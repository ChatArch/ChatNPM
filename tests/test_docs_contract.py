from pathlib import Path

from chatstyle import render_click_tree

from chatnpm.cli import main

ROOT = Path(__file__).resolve().parents[1]


def _text_blocks(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [chunk.split("```", 1)[0].rstrip() for chunk in text.split("```text\n")[1:]]


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


def test_public_docs_surfaces_link_to_canonical_domain_and_both_cli_trees():
    for relative in ["README.md", "README.en.md", "docs/index.md", "docs/index.en.md"]:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "https://arch.gh.wzhecnu.cn/ChatNPM/" in text, relative
        old_domain = "chatarch" + ".github" + ".io"
        assert old_domain not in text, relative
        assert "chatnpm --tree" in text, relative
        assert "chatnpm --tree-brief" in text, relative


def test_cli_tree_docs_exist_in_both_languages():
    expected = [
        render_click_tree(main, root_name="chatnpm"),
        render_click_tree(main, root_name="chatnpm", brief=True),
    ]

    for path in [ROOT / "docs/cli-tree.md", ROOT / "docs/cli-tree.en.md"]:
        text = path.read_text(encoding="utf-8")
        assert "chatstyle.add_tree_option()" in text
        assert "chatnpm" in text
        assert "auth" in text
        assert "parse-output" in text
        assert "package inspect" in text
        assert "trusted audit" in text
        assert "hello" not in text.lower()
        assert _text_blocks(path)[:2] == expected


def test_material_icon_literals_are_not_in_source_docs():
    for path in [*ROOT.glob("README*.md"), *ROOT.glob("docs/**/*.md")]:
        literal_icon_prefix = ":" + "material-"
        assert literal_icon_prefix not in path.read_text(encoding="utf-8"), path
