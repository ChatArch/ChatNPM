import json

from click.testing import CliRunner

from chatnpm.cli import main


def test_hello_command_accepts_explicit_name():
    result = CliRunner().invoke(main, ["hello", "ChatArch"])

    assert result.exit_code == 0
    assert "Hello, ChatArch!" in result.output


def test_package_inspect_outputs_safe_json(monkeypatch):
    def fake_inspect_package(package, *, version=None, registry, timeout=30):
        assert package == "@chatarch/example"
        assert version == "1.2.3"
        assert registry == "https://registry.npmjs.org/"
        return {
            "registry": registry,
            "package": package,
            "scope": "chatarch",
            "version": version,
            "latest": "1.2.3",
            "maintainers": [{"name": "rexwzh"}],
            "repository": {"type": "git", "url": "git+https://github.com/ChatArch/Example.git"},
            "dist": {
                "tarball_present": True,
                "integrity_present": True,
                "signature_count": 1,
                "attestation_present": True,
            },
            "provenance": {"present": True, "source": "dist.attestations"},
            "trusted_publishing": {"public_registry_readback": "not_exposed"},
        }

    monkeypatch.setattr("chatnpm.cli.inspect_package", fake_inspect_package)

    result = CliRunner().invoke(
        main,
        ["package", "inspect", "@chatarch/example", "--version", "1.2.3", "--format", "json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["package"] == "@chatarch/example"
    assert payload["provenance"] == {"present": True, "source": "dist.attestations"}
    assert "token" not in result.output.lower()
    assert "password" not in result.output.lower()


def test_package_inspect_text_mentions_no_public_trusted_publisher_table(monkeypatch):
    monkeypatch.setattr(
        "chatnpm.cli.inspect_package",
        lambda package, **kwargs: {
            "package": package,
            "version": "1.0.0",
            "scope": None,
            "maintainers": [],
            "repository": None,
            "dist": {"signature_count": 0, "attestation_present": False},
            "provenance": {"present": False, "source": None},
            "trusted_publishing": {"public_registry_readback": "not_exposed"},
        },
    )

    result = CliRunner().invoke(main, ["package", "inspect", "plain-package"])

    assert result.exit_code == 0, result.output
    assert "plain-package@1.0.0" in result.output
    assert "Trusted Publishing settings: not exposed by public npm registry" in result.output


def test_package_inspect_reports_clean_registry_errors(monkeypatch):
    def fail_inspect(*args, **kwargs):
        raise ValueError("npm registry request failed for pkg: HTTP 500")

    monkeypatch.setattr("chatnpm.cli.inspect_package", fail_inspect)

    result = CliRunner().invoke(main, ["package", "inspect", "pkg"])

    assert result.exit_code != 0
    assert "Error: npm registry request failed for pkg: HTTP 500" in result.output
    assert "Traceback" not in result.output


def test_package_inspect_reports_invalid_registry_without_echoing_value():
    secret_value = "fixture-secret-value"

    result = CliRunner().invoke(
        main,
        ["package", "inspect", "pkg", "--registry", f"https://registry.npmjs.org:{secret_value}/"],
    )

    assert result.exit_code != 0
    assert "Error: invalid npm registry URL" in result.output
    assert secret_value not in result.output
    assert "Traceback" not in result.output


def test_tree_lists_package_inspect_command():
    result = CliRunner().invoke(main, ["--tree"])

    assert result.exit_code == 0, result.output
    assert "chatnpm" in result.output
    assert "package" in result.output
    assert "inspect" in result.output
    assert "trusted" in result.output
    assert "audit" in result.output
    assert "hello" in result.output


def test_trusted_audit_outputs_safe_json(monkeypatch, tmp_path):
    def fake_audit(path):
        assert path == tmp_path
        return {
            "path": str(path),
            "package_json": {"present": True, "name": "@chatarch/example", "version": "1.2.3"},
            "workflows": [{"path": ".github/workflows/publish.yml", "id_token_write": True}],
            "trusted_publishing": {
                "oidc_provenance_workflow_present": True,
                "token_fallback_present": False,
            },
        }

    monkeypatch.setattr("chatnpm.cli.audit_trusted_publishing_repo", fake_audit)

    result = CliRunner().invoke(main, ["trusted", "audit", str(tmp_path), "--format", "json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["trusted_publishing"]["oidc_provenance_workflow_present"] is True
    assert ("NODE" + "_AUTH" + "_TOKEN") not in result.output
    assert ("NPM" + "_TOKEN") not in result.output


def test_trusted_audit_reports_clean_missing_path_errors(tmp_path):
    missing = tmp_path / "missing"

    result = CliRunner().invoke(main, ["trusted", "audit", str(missing), "--format", "json"])

    assert result.exit_code != 0
    assert "Error: audit path does not exist" in result.output
    assert "Traceback" not in result.output


def test_trusted_audit_reports_clean_package_json_errors(tmp_path):
    (tmp_path / "package.json").write_text("not-json", encoding="utf-8")

    result = CliRunner().invoke(main, ["trusted", "audit", str(tmp_path)])

    assert result.exit_code != 0
    assert "Error: invalid package.json" in result.output
    assert "Traceback" not in result.output


def test_version_option_reports_package_version():
    result = CliRunner().invoke(main, ["--version"])

    assert result.exit_code == 0, result.output
    assert "0.1.2" in result.output
