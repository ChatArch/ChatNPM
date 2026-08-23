<div align="center">
    <a href="https://pypi.python.org/pypi/ChatNPM">
        <img src="https://img.shields.io/pypi/v/ChatNPM.svg" alt="PyPI version" />
    </a>
    <a href="https://github.com/ChatArch/ChatNPM/actions/workflows/ci.yml">
        <img src="https://github.com/ChatArch/ChatNPM/actions/workflows/ci.yml/badge.svg" alt="Tests" />
    </a>
    <a href="https://arch.gh.wzhecnu.cn/ChatNPM/">
        <img src="https://img.shields.io/badge/docs-mkdocs-blue.svg" alt="Documentation" />
    </a>
</div>

<div align="center">

[English](README.en.md) | [简体中文](README.md)
</div>

# ChatNPM

ChatNPM: ChatArch npm registry and package maintenance helper

Documentation: <https://arch.gh.wzhecnu.cn/ChatNPM/>

## Quick Start

```bash
pip install chatnpm
chatnpm --tree
chatnpm --tree-brief
chatnpm package inspect npm --format json
chatnpm trusted audit . --format json
printf '%s\n' 'Open https://www.npmjs.com/login/abc to use your security key' | chatnpm auth parse-output --format json
python -m pytest -q
python -m build
```

## Real CLI tree

`chatnpm --tree` includes parameter signatures. `chatnpm --tree-brief` preserves the same nodes and purposes without signatures. ChatStyle generates both views from the real Click registry.

```text
chatnpm
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
├── auth  # Parse npm authentication handoff prompts.
│   └── parse-output [--format OUTPUT-FORMAT]  # Parse npm CLI output from stdin into a card-handoff payload.
├── package  # Inspect public npm registry metadata; read-only network access.
│   └── inspect <PACKAGE> [--version PACKAGE-VERSION] [--registry REGISTRY] [--format OUTPUT-FORMAT]  # Read public package metadata; sends one request and never outputs auth values.
└── trusted  # Audit npm Trusted Publishing evidence; read-only filesystem access.
    └── audit [PATH] [--format OUTPUT-FORMAT]  # Read package/workflow evidence under PATH; no account access or secret output.
```

## Read-only npm publishing metadata inspection

`chatnpm package inspect <package>` reads the public npm registry packument and prints a safe summary:

- package / version / scope
- public maintainer count and names from registry metadata
- repository and safe `publishConfig` summary
- dist integrity/signature/attestation presence
- provenance evidence when `dist.attestations` is present
- local GitHub Actions evidence for npm OIDC / `npm publish --provenance` through `chatnpm trusted audit`

The public npm registry does not expose a PyPI-style Trusted Publisher settings table. ChatNPM therefore reports:

```text
Trusted Publishing settings: not exposed by public npm registry
```

That is not a failure and it is not a claim that Trusted Publishing is absent. It means public readback can verify registry provenance/attestation evidence, but cannot read npm account/package trusted-publishing settings.

## CLI Contract

This package uses `add_tree_option()` from `chatstyle>=0.2.0,<0.3.0` for full and brief registered trees instead of a package-local renderer. ChatNPM has no env/profile/config behavior, so it does not depend on ChatEnv.

## Layout

- `src/`: package source code
- `tests/`: CLI, registry, trusted publishing, docs/workflow contract tests
- `docs/`: long-lived project docs built by MkDocs Material + i18n

## Development Notes

See `DEVELOP.md` and `AGENTS.md` before expanding the package.
