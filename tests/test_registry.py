from chatnpm.registry import fetch_packument, summarize_packument


def test_summarize_packument_reports_publisher_and_provenance_metadata():
    packument = {
        "name": "@chatarch/example",
        "dist-tags": {"latest": "1.2.3"},
        "maintainers": [
            {"name": "rexwzh", "email": "rex@example.com"},
            {"name": "bot"},
        ],
        "time": {"1.2.3": "2026-08-12T00:00:00.000Z"},
        "repository": {"type": "git", "url": "git+https://github.com/ChatArch/Example.git"},
        "versions": {
            "1.2.3": {
                "name": "@chatarch/example",
                "version": "1.2.3",
                "license": "MIT",
                "repository": {"type": "git", "url": "git+https://github.com/ChatArch/Example.git"},
                "publishConfig": {"access": "public", "provenance": True},
                "dist": {
                    "tarball": "https://registry.npmjs.org/@chatarch/example/-/example-1.2.3.tgz",
                    "integrity": "sha512-fixture",
                    "signatures": [
                        {"keyid": "SHA256:fixture", "sig": "fixture-signature"}
                    ],
                    "attestations": {
                        "url": "https://registry.npmjs.org/-/npm/v1/attestations/@chatarch%2fexample@1.2.3",
                        "provenance": {"predicateType": "https://slsa.dev/provenance/v1"},
                    },
                },
            }
        },
    }

    summary = summarize_packument(packument, version=None, registry="https://registry.npmjs.org/")

    assert summary["package"] == "@chatarch/example"
    assert summary["version"] == "1.2.3"
    assert summary["latest"] == "1.2.3"
    assert summary["scope"] == "chatarch"
    assert summary["maintainers"] == [
        {"name": "rexwzh", "email": "rex@example.com"},
        {"name": "bot"},
    ]
    assert summary["repository"] == {
        "type": "git",
        "url": "git+https://github.com/ChatArch/Example.git",
    }
    assert summary["publish_config"] == {
        "present": True,
        "access": "public",
        "provenance": True,
        "redacted_key_count": 0,
        "unsupported_key_count": 0,
    }
    assert summary["dist"]["tarball_present"] is True
    assert summary["dist"]["integrity_present"] is True
    assert summary["dist"]["signature_count"] == 1
    assert summary["dist"]["attestation_present"] is True
    assert summary["provenance"]["present"] is True
    assert summary["provenance"]["source"] == "dist.attestations"
    assert summary["trusted_publishing"]["public_registry_readback"] == "not_exposed"


def test_summarize_packument_marks_missing_provenance_without_guessing():
    packument = {
        "name": "plain-package",
        "dist-tags": {"latest": "0.1.0"},
        "versions": {
            "0.1.0": {
                "name": "plain-package",
                "version": "0.1.0",
                "dist": {"shasum": "abc"},
            }
        },
    }

    summary = summarize_packument(packument, version="0.1.0", registry="https://registry.npmjs.org/")

    assert summary["package"] == "plain-package"
    assert summary["scope"] is None
    assert summary["dist"]["signature_count"] == 0
    assert summary["dist"]["attestation_present"] is False
    assert summary["provenance"] == {"present": False, "source": None}
    assert summary["trusted_publishing"]["public_registry_readback"] == "not_exposed"


def test_summarize_packument_rejects_unknown_version():
    packument = {"name": "pkg", "dist-tags": {"latest": "1.0.0"}, "versions": {"1.0.0": {}}}

    try:
        summarize_packument(packument, version="2.0.0", registry="https://registry.npmjs.org/")
    except ValueError as exc:
        assert "version not found" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_summarize_packument_redacts_publish_config_auth_material():
    raw_key = "NODE" + "_AUTH" + "_TOKEN"
    auth_property = "_" + "auth" + "Token"
    secret_value = "fixture-secret-value"
    packument = {
        "name": "pkg",
        "dist-tags": {"latest": "1.0.0"},
        "versions": {
            "1.0.0": {
                "publishConfig": {
                    "access": "public",
                    "registry": f"https://user:{secret_value}@registry.npmjs.org/?{raw_key}={secret_value}",
                    raw_key: secret_value,
                    auth_property: secret_value,
                    "customField": "harmless-but-unsupported",
                },
                "dist": {"shasum": "abc"},
            }
        },
    }

    summary = summarize_packument(packument, version="1.0.0", registry=f"https://user:{secret_value}@registry.npmjs.org/?x={secret_value}")
    rendered = __import__("json").dumps(summary)

    assert summary["registry"] == "https://registry.npmjs.org/"
    assert summary["publish_config"] == {
        "present": True,
        "access": "public",
        "registry": "https://registry.npmjs.org/",
        "redacted_key_count": 2,
        "unsupported_key_count": 1,
    }
    assert raw_key not in rendered
    assert auth_property not in rendered
    assert secret_value not in rendered


def test_summarize_packument_drops_malformed_secret_bearing_repository_url():
    secret_value = "fixture-secret-value"
    packument = {
        "name": "pkg",
        "dist-tags": {"latest": "1.0.0"},
        "versions": {
            "1.0.0": {
                "repository": f"https://registry.npmjs.org:{secret_value}/repo.git",
                "dist": {"shasum": "abc"},
            }
        },
    }

    summary = summarize_packument(packument, version="1.0.0", registry="https://registry.npmjs.org/")
    rendered = __import__("json").dumps(summary)

    assert summary["repository"] is None
    assert secret_value not in rendered


def test_summarize_packument_drops_malformed_secret_bearing_publish_config_registry():
    secret_value = "fixture-secret-value"
    packument = {
        "name": "pkg",
        "dist-tags": {"latest": "1.0.0"},
        "versions": {
            "1.0.0": {
                "publishConfig": {
                    "access": "public",
                    "registry": f"https://registry.npmjs.org:{secret_value}/",
                },
                "dist": {"shasum": "abc"},
            }
        },
    }

    summary = summarize_packument(packument, version="1.0.0", registry="https://registry.npmjs.org/")
    rendered = __import__("json").dumps(summary)

    assert summary["publish_config"] == {
        "present": True,
        "access": "public",
        "redacted_key_count": 0,
        "unsupported_key_count": 1,
    }
    assert secret_value not in rendered


def test_fetch_packument_reports_invalid_registry_without_echoing_value():
    secret_value = "fixture-secret-value"

    try:
        fetch_packument("pkg", registry=f"https://registry.npmjs.org:{secret_value}/")
    except ValueError as exc:
        message = str(exc)
        assert "invalid npm registry URL" in message
        assert secret_value not in message
    else:
        raise AssertionError("expected ValueError")


def test_fetch_packument_reports_invalid_json_cleanly(monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self):
            return b"not-json"

    monkeypatch.setattr("urllib.request.urlopen", lambda *args, **kwargs: Response())

    try:
        fetch_packument("pkg")
    except ValueError as exc:
        assert "invalid npm registry response for pkg" in str(exc)
    else:
        raise AssertionError("expected ValueError")
