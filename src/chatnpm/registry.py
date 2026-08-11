"""Read-only npm registry metadata helpers."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from chatnpm.safety import sanitize_publish_config, sanitize_repository, sanitize_url

DEFAULT_REGISTRY = "https://registry.npmjs.org/"


def _normalize_registry(registry: str) -> str:
    value = registry.strip() or DEFAULT_REGISTRY
    safe = sanitize_url(value)
    if not safe:
        raise ValueError("invalid npm registry URL")
    return safe if safe.endswith("/") else safe + "/"


def package_scope(package: str) -> str | None:
    """Return the npm scope without '@', if any."""

    if package.startswith("@") and "/" in package:
        return package[1:].split("/", 1)[0]
    return None


def package_url(package: str, registry: str = DEFAULT_REGISTRY) -> str:
    """Build the npm registry packument URL for a package name."""

    base = _normalize_registry(registry)
    encoded = urllib.parse.quote(package, safe="")
    return urllib.parse.urljoin(base, encoded)


def fetch_packument(package: str, registry: str = DEFAULT_REGISTRY, timeout: float = 30) -> dict[str, Any]:
    """Fetch a package packument from an npm-compatible registry."""

    url = package_url(package, registry)
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise ValueError(f"npm package not found: {package}") from exc
        raise ValueError(f"npm registry request failed for {package}: HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ValueError(f"npm registry request failed for {package}: {exc.__class__.__name__}") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"invalid npm registry response for {package}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"unexpected npm registry response for {package}")
    return payload


def _safe_maintainers(packument: dict[str, Any]) -> list[dict[str, str]]:
    maintainers = packument.get("maintainers") or []
    safe: list[dict[str, str]] = []
    for item in maintainers:
        if not isinstance(item, dict):
            continue
        entry: dict[str, str] = {}
        name = item.get("name")
        email = item.get("email")
        if isinstance(name, str) and name:
            entry["name"] = name
        if isinstance(email, str) and email:
            entry["email"] = email
        if entry:
            safe.append(entry)
    return safe


def _dist_summary(dist: dict[str, Any]) -> dict[str, Any]:
    signatures = dist.get("signatures") or []
    attestations = dist.get("attestations")
    return {
        "tarball_present": bool(dist.get("tarball")),
        "integrity_present": bool(dist.get("integrity")),
        "shasum_present": bool(dist.get("shasum")),
        "signature_count": len(signatures) if isinstance(signatures, list) else 0,
        "attestation_present": bool(attestations),
        "file_count": dist.get("fileCount") if isinstance(dist.get("fileCount"), int) else None,
        "unpacked_size": dist.get("unpackedSize") if isinstance(dist.get("unpackedSize"), int) else None,
    }


def _provenance_summary(dist: dict[str, Any], safe_publish_config: dict[str, Any]) -> dict[str, Any]:
    attestations = dist.get("attestations")
    if attestations:
        return {"present": True, "source": "dist.attestations"}
    if safe_publish_config.get("provenance") is True:
        return {"present": "declared", "source": "publishConfig.provenance"}
    return {"present": False, "source": None}


def summarize_packument(
    packument: dict[str, Any],
    *,
    version: str | None = None,
    registry: str = DEFAULT_REGISTRY,
) -> dict[str, Any]:
    """Summarize npm package publisher/provenance metadata without secrets.

    npm's public registry exposes package/version publisher evidence such as
    maintainers, repository, dist signatures, and attestation metadata when it
    exists. It does not expose a PyPI-like Trusted Publisher settings table, so
    that field is reported as not exposed instead of guessed.
    """

    package = packument.get("name")
    if not isinstance(package, str) or not package:
        raise ValueError("npm packument missing package name")

    versions = packument.get("versions") or {}
    if not isinstance(versions, dict) or not versions:
        raise ValueError(f"npm package has no versions: {package}")

    latest = (packument.get("dist-tags") or {}).get("latest")
    selected_version = version or latest
    if not isinstance(selected_version, str) or not selected_version:
        raise ValueError(f"npm package has no selectable version: {package}")
    version_data = versions.get(selected_version)
    if not isinstance(version_data, dict):
        raise ValueError(f"npm package version not found: {package}@{selected_version}")

    dist = version_data.get("dist") or {}
    if not isinstance(dist, dict):
        dist = {}
    publish_config = version_data.get("publishConfig") or {}
    safe_publish_config = sanitize_publish_config(publish_config)

    repository = sanitize_repository(version_data.get("repository") or packument.get("repository"))

    npm_user = version_data.get("_npmUser") or version_data.get("npmUser")
    if isinstance(npm_user, dict):
        npm_user = {key: value for key, value in npm_user.items() if key in {"name", "email"}}
    elif not isinstance(npm_user, str):
        npm_user = None

    return {
        "registry": sanitize_url(_normalize_registry(registry)) or DEFAULT_REGISTRY,
        "package": package,
        "scope": package_scope(package),
        "version": selected_version,
        "latest": latest,
        "published_at": (packument.get("time") or {}).get(selected_version),
        "license": version_data.get("license"),
        "maintainers": _safe_maintainers(packument),
        "npm_user": npm_user,
        "repository": repository,
        "publish_config": safe_publish_config,
        "dist": _dist_summary(dist),
        "provenance": _provenance_summary(dist, safe_publish_config),
        "trusted_publishing": {
            "public_registry_readback": "not_exposed",
            "note": "npm public packuments expose signatures/attestations, not a PyPI-style Trusted Publisher settings table.",
        },
    }


def inspect_package(
    package: str,
    *,
    version: str | None = None,
    registry: str = DEFAULT_REGISTRY,
    timeout: float = 30,
) -> dict[str, Any]:
    """Fetch and summarize a package from the npm registry."""

    packument = fetch_packument(package, registry=registry, timeout=timeout)
    return summarize_packument(packument, version=version, registry=registry)
