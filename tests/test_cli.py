import json

from click.testing import CliRunner
from chatstyle import render_click_tree

from chatnpm import __version__
from chatnpm.cli import main


def test_scaffold_hello_command_is_not_public():
    help_result = CliRunner().invoke(main, ["--help"])
    tree_result = CliRunner().invoke(main, ["--tree"])
    brief_result = CliRunner().invoke(main, ["--tree-brief"])
    hello_result = CliRunner().invoke(main, ["hello", "ChatArch"])

    assert help_result.exit_code == 0, help_result.output
    assert tree_result.exit_code == 0, tree_result.output
    assert brief_result.exit_code == 0, brief_result.output
    assert "--tree" in help_result.output
    assert "--tree-brief" in help_result.output
    assert "hello" not in help_result.output.lower()
    assert "hello" not in tree_result.output.lower()
    assert "hello" not in brief_result.output.lower()
    assert hello_result.exit_code != 0


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


def test_tree_lists_registered_public_commands_with_signatures_and_purposes():
    result = CliRunner().invoke(main, ["--tree"])

    assert result.exit_code == 0, result.output
    assert result.output == render_click_tree(main, root_name="chatnpm") + "\n"
    assert result.output.splitlines().count("chatnpm") == 1
    assert "├── --tree-brief" in result.output
    assert "package  # Inspect public npm registry metadata; read-only network access." in result.output
    assert "inspect <PACKAGE>" in result.output
    assert "sends one request and never outputs auth values" in result.output
    assert "trusted  # Audit npm Trusted Publishing evidence; read-only filesystem access." in result.output
    assert "audit [PATH]" in result.output
    assert "no account access or secret output" in result.output
    assert "hello" not in result.output.lower()


def test_tree_brief_keeps_nodes_and_purposes_but_omits_signatures():
    result = CliRunner().invoke(main, ["--tree-brief"])

    assert result.exit_code == 0, result.output
    assert result.output == render_click_tree(main, root_name="chatnpm", brief=True) + "\n"
    assert result.output.splitlines().count("chatnpm") == 1
    assert "├── --tree-brief" in result.output
    assert "│   └── inspect  # Read public package metadata" in result.output
    assert "    └── audit  # Read package/workflow evidence" in result.output
    assert "inspect <PACKAGE>" not in result.output
    assert "audit [PATH]" not in result.output
    assert "--registry" not in result.output


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
    assert result.output == f"chatnpm, version {__version__}\n"
