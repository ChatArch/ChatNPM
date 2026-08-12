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
chatnpm package inspect npm --format json
chatnpm trusted audit . --format json
python -m pytest -q
python -m build
```

## Real CLI tree

```text
chatnpm  # ChatArch npm registry and publishing-evidence helper.
├── --help  # Show this help message.
├── --version  # Show the installed package version.
├── --tree  # Print the registered command tree.
├── package  # Inspect npm package registry metadata.
│   └── inspect PACKAGE [--version PACKAGE-VERSION] [--registry REGISTRY] [--format text|json]  # Read npm registry publisher/provenance metadata for PACKAGE.
└── trusted  # Audit npm Trusted Publishing evidence.
    └── audit [PATH] [--format text|json]  # Read local package/workflow evidence for npm Trusted Publishing.
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

This package currently depends on Click only. New commands should treat the registered `chatnpm --tree` output as the source for docs and tests.

## Layout

- `src/`: package source code
- `tests/`: CLI, registry, trusted publishing, docs/workflow contract tests
- `docs/`: long-lived project docs built by MkDocs Material + i18n

## Development Notes

See `DEVELOP.md` and `AGENTS.md` before expanding the package.
