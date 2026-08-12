from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_publish_workflow_uses_oidc_without_legacy_pypi_tokens():
    text = (ROOT / ".github/workflows/publish.yml").read_text(encoding="utf-8")

    assert "id-token: write" in text
    assert "pypa/gh-action-pypi-publish@release/v1" in text
    assert ("PYPI" + "_API" + "_TOKEN") not in text
    assert ("TWINE" + "_PASSWORD") not in text
    assert ("secrets" + ".PYPI") not in text
    assert ("environment" + ": pypi") not in text


def test_publish_workflow_has_tag_version_and_default_branch_guard():
    text = (ROOT / ".github/workflows/publish.yml").read_text(encoding="utf-8")

    assert "tags:" in text
    assert "v*" in text
    assert "Check tag matches package version" in text
    assert "git fetch --no-tags origin main:refs/remotes/origin/main" in text
    assert "git merge-base --is-ancestor" in text
    assert ("git fetch origin main " + "--tags") not in text
    assert ("git fetch origin master " + "--tags") not in text


def test_ci_runs_python_matrix_and_installed_cli_smoke():
    text = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "python-version: [\"3.10\", \"3.11\", \"3.12\"]" in text
    assert "python -m pytest -q" in text
    assert "chatnpm --version" in text
    assert "chatnpm --tree" in text
    assert "mkdocs build --strict" in text


def test_preview_docs_uses_mkdocs_site_url_not_github_io():
    text = (ROOT / ".github/workflows/preview.yaml").read_text(encoding="utf-8")

    assert "CHATARCH_PREVIEW_URL" in text
    assert "mkdocs.yml" in text
    assert ("github" + ".io") not in text
