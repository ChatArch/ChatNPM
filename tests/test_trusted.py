import json
from pathlib import Path

from chatnpm.trusted import audit_trusted_publishing_repo


def test_audit_trusted_publishing_repo_reports_oidc_provenance(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "@chatarch/example",
                "version": "1.2.3",
                "publishConfig": {"access": "public", "provenance": True},
            }
        ),
        encoding="utf-8",
    )
    workflow = tmp_path / ".github" / "workflows" / "publish.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        """
name: Publish npm
permissions:
  contents: read
  id-token: write
jobs:
  publish:
    steps:
      - uses: actions/setup-node@v4
        with:
          registry-url: https://registry.npmjs.org/
      - run: npm publish --access public --provenance
""".strip(),
        encoding="utf-8",
    )

    report = audit_trusted_publishing_repo(tmp_path)

    assert report["package_json"] == {
        "present": True,
        "name": "@chatarch/example",
        "version": "1.2.3",
        "private": None,
        "publish_config": {
            "present": True,
            "access": "public",
            "provenance": True,
            "redacted_key_count": 0,
            "unsupported_key_count": 0,
        },
    }
    assert report["trusted_publishing"]["oidc_provenance_workflow_present"] is True
    assert report["trusted_publishing"]["token_fallback_present"] is False
    assert report["workflows"][0]["id_token_write"] is True
    assert report["workflows"][0]["npm_publish"] is True
    assert report["workflows"][0]["provenance_flag"] is True


def test_audit_trusted_publishing_repo_reports_token_fallback_without_values(tmp_path: Path) -> None:
    workflow = tmp_path / ".github" / "workflows" / "publish.yml"
    workflow.parent.mkdir(parents=True)
    fallback_key_a = "NODE" + "_AUTH" + "_TOKEN"
    fallback_key_b = "NPM" + "_TOKEN"
    workflow.write_text(
        f"""
name: Publish npm
jobs:
  publish:
    steps:
      - run: npm publish --access public
        env:
          {fallback_key_a}: ${{{{ secrets.{fallback_key_b} }}}}
""".strip(),
        encoding="utf-8",
    )

    report = audit_trusted_publishing_repo(tmp_path)

    assert report["package_json"] == {"present": False}
    assert report["trusted_publishing"]["oidc_provenance_workflow_present"] is False
    assert report["trusted_publishing"]["token_fallback_present"] is True
    rendered = json.dumps(report)
    assert "${{ secrets." + ("NPM" + "_TOKEN") + " }}" not in rendered
    assert ("NODE" + "_AUTH" + "_TOKEN") not in rendered


def test_audit_trusted_publishing_repo_rejects_missing_path(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    try:
        audit_trusted_publishing_repo(missing)
    except ValueError as exc:
        assert "audit path does not exist" in str(exc)
        assert str(missing.resolve()) in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_audit_trusted_publishing_repo_rejects_file_path(tmp_path: Path) -> None:
    not_dir = tmp_path / "package.json"
    not_dir.write_text("{}", encoding="utf-8")

    try:
        audit_trusted_publishing_repo(not_dir)
    except ValueError as exc:
        assert "audit path is not a directory" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_audit_trusted_publishing_repo_rejects_invalid_package_json(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("not-json", encoding="utf-8")

    try:
        audit_trusted_publishing_repo(tmp_path)
    except ValueError as exc:
        assert "invalid package.json" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_audit_trusted_publishing_repo_drops_malformed_publish_config_registry(tmp_path: Path) -> None:
    secret_value = "fixture-secret-value"
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "pkg",
                "version": "1.0.0",
                "publishConfig": {
                    "access": "public",
                    "registry": f"https://registry.npmjs.org:{secret_value}/",
                },
            }
        ),
        encoding="utf-8",
    )

    report = audit_trusted_publishing_repo(tmp_path)
    rendered = json.dumps(report)

    assert report["package_json"]["publish_config"] == {
        "present": True,
        "access": "public",
        "redacted_key_count": 0,
        "unsupported_key_count": 1,
    }
    assert secret_value not in rendered


def test_audit_trusted_publishing_repo_redacts_package_json_publish_config(tmp_path: Path) -> None:
    raw_key = "NODE" + "_AUTH" + "_TOKEN"
    auth_property = "_" + "auth" + "Token"
    secret_value = "fixture-secret-value"
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "pkg",
                "version": "1.0.0",
                "publishConfig": {
                    "access": "public",
                    "registry": f"https://user:{secret_value}@registry.npmjs.org/?{raw_key}={secret_value}",
                    raw_key: secret_value,
                    auth_property: secret_value,
                    "customField": "harmless-but-unsupported",
                },
            }
        ),
        encoding="utf-8",
    )

    report = audit_trusted_publishing_repo(tmp_path)
    rendered = json.dumps(report)

    assert report["package_json"]["publish_config"] == {
        "present": True,
        "access": "public",
        "registry": "https://registry.npmjs.org/",
        "redacted_key_count": 2,
        "unsupported_key_count": 1,
    }
    assert raw_key not in rendered
    assert auth_property not in rendered
    assert secret_value not in rendered
