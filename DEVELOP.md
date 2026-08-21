# Development Guide

## CLI Rules

- Keep the real console script on `chatstyle>=0.2.0,<0.3.0`, with an explicit `chatnpm` Click root.
- Use ChatStyle `add_tree_option()` for registered `--tree` and `--tree-brief` output; do not add a package-local tree renderer.
- Keep the public command surface aligned with the real Click registry; full and brief trees are the source of truth for docs, README snippets, and CLI tests.
- ChatNPM has no env/profile/config behavior, so it does not require ChatEnv. Add typed ChatEnv registration and storage only if such behavior is introduced.
- Do not keep scaffold-only commands in the public CLI.
- Add new runtime dependencies only when the command implementation actually imports and uses them.
- Missing required arguments should fail clearly in non-interactive CLI usage unless the command explicitly implements an interactive flow.
- Sensitive values must stay masked in prompts, summaries, logs, and tests.
- Prefer lazy imports in CLI wiring and keep implementation imports local when possible.

## Docs and Tests

- Lock the public CLI surface with `tests/test_cli.py` and both ChatStyle tree views.
- Keep README, bilingual MkDocs docs, and CHANGELOG in sync with user-facing changes.
- Keep MkDocs Material configured with `pymdownx.emoji` and Material `twemoji` / `to_svg` renderers.
- Keep source docs and generated HTML/search output free of literal Material shorthand tokens.
- Keep docs on the ChatArch public docs domain: `https://arch.gh.wzhecnu.cn/ChatNPM/`.

## Packaging and Release

- Use PyPI Trusted Publishing / OIDC for releases; do not add legacy PyPI token secrets.
- Tag-triggered publish workflows must verify the tag matches the package version and that the tagged commit is reachable from the default branch.
- Local release gates should run source tests, installed CLI smoke, `python -m build`, `twine check`, `mkdocs build --strict`, and the Material literal-token checker.

## Automation

- Keep automation small and reviewable.
- Prefer commands that can run in CI without interactive prompts.
- Ensure generated defaults are safe for local development.
