from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_mkdocs_uses_chatarch_public_domain_and_i18n():
    text = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "site_url: https://arch.gh.wzhecnu.cn/ChatNPM/" in text
    assert "mkdocs-static-i18n" not in text  # package name belongs in pyproject, not config key
    assert "- i18n:" in text
    assert "docs_structure: suffix" in text
    assert "locale: en" in text
    assert "pymdownx.emoji" in text
    assert "!!python/name:material.extensions.emoji.twemoji" in text
    assert "!!python/name:material.extensions.emoji.to_svg" in text
    old_domain = "chatarch" + ".github" + ".io"
    assert old_domain not in text


def test_public_docs_surfaces_link_to_canonical_domain_and_cli_tree():
    for relative in ["README.md", "README.en.md", "docs/index.md", "docs/index.en.md"]:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "https://arch.gh.wzhecnu.cn/ChatNPM/" in text, relative
        old_domain = "chatarch" + ".github" + ".io"
        assert old_domain not in text, relative
        assert "chatnpm --tree" in text or "cli-tree" in text, relative


def test_cli_tree_docs_exist_in_both_languages():
    zh = (ROOT / "docs/cli-tree.md").read_text(encoding="utf-8")
    en = (ROOT / "docs/cli-tree.en.md").read_text(encoding="utf-8")

    for text in [zh, en]:
        assert "chatnpm" in text
        assert "package inspect" in text
        assert "trusted audit" in text
        assert "hello" not in text.lower()


def test_material_icon_literals_are_not_in_source_docs():
    for path in [*ROOT.glob("README*.md"), *ROOT.glob("docs/**/*.md")]:
        literal_icon_prefix = ":" + "material-"
        assert literal_icon_prefix not in path.read_text(encoding="utf-8"), path
