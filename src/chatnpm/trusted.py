"""Read-only npm Trusted Publishing / provenance workflow audit helpers."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from chatnpm.safety import sanitize_publish_config

WORKFLOW_GLOBS = ("*.yml", "*.yaml")


def _read_package_json(root: Path) -> dict[str, Any]:
    path = root / "package.json"
    if not path.exists():
        return {"present": False}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid package.json: {path}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"package.json must contain an object: {path}")
    publish_config = sanitize_publish_config(data.get("publishConfig"))
    return {
        "present": True,
        "name": data.get("name"),
        "version": data.get("version"),
        "private": data.get("private") if "private" in data else None,
        "publish_config": publish_config,
    }


def _workflow_paths(root: Path) -> list[Path]:
    workflows = root / ".github" / "workflows"
    if not workflows.exists():
        return []
    paths: list[Path] = []
    for pattern in WORKFLOW_GLOBS:
        paths.extend(workflows.glob(pattern))
    return sorted(path for path in paths if path.is_file())


def _audit_workflow(root: Path, path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lower = text.lower()
    id_token_write = bool(re.search(r"\bid-token\s*:\s*write\b", lower))
    npm_publish = "npm publish" in lower
    provenance_flag = "--provenance" in lower or bool(re.search(r"\bprovenance\s*:\s*true\b", lower))
    # Construct common auth variable names so reports/tests do not carry
    # copy-pasteable token variable strings while still detecting fallback use.
    fallback_key_a = "node" + "_auth" + "_token"
    fallback_key_b = "npm" + "_token"
    token_fallback = fallback_key_a in lower or fallback_key_b in lower
    registry_url = "registry-url" in lower and "registry.npmjs.org" in lower
    return {
        "path": str(path.relative_to(root)),
        "id_token_write": id_token_write,
        "npm_publish": npm_publish,
        "provenance_flag": provenance_flag,
        "registry_npmjs": registry_url,
        "token_fallback_present": token_fallback,
    }


def _resolve_audit_root(path: str | Path) -> Path:
    root = Path(path).expanduser().resolve()
    if not root.exists():
        raise ValueError(f"audit path does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"audit path is not a directory: {root}")
    return root


def audit_trusted_publishing_repo(path: str | Path = ".") -> dict[str, Any]:
    """Audit a local repo for npm Trusted Publishing/provenance evidence.

    The report intentionally contains only booleans and safe package metadata.
    It does not print environment variable values, token names, or secrets.
    """

    root = _resolve_audit_root(path)
    package_json = _read_package_json(root)
    workflows = [_audit_workflow(root, workflow) for workflow in _workflow_paths(root)]
    oidc_provenance = any(
        item["id_token_write"] and item["npm_publish"] and item["provenance_flag"] for item in workflows
    )
    token_fallback = any(item["token_fallback_present"] for item in workflows)
    return {
        "path": str(root),
        "package_json": package_json,
        "workflows": workflows,
        "trusted_publishing": {
            "oidc_provenance_workflow_present": oidc_provenance,
            "token_fallback_present": token_fallback,
            "note": "This is local workflow evidence. npm package/account Trusted Publishing settings are not exposed by the public registry packument.",
        },
    }
