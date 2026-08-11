<div align="center">
    <a href="https://pypi.python.org/pypi/ChatNPM">
        <img src="https://img.shields.io/pypi/v/ChatNPM.svg" alt="PyPI version" />
    </a>
    <a href="https://github.com/ChatArch/ChatNPM/actions/workflows/ci.yml">
        <img src="https://github.com/ChatArch/ChatNPM/actions/workflows/ci.yml/badge.svg" alt="Tests" />
    </a>
    <a href="https://chatarch.github.io/ChatNPM">
        <img src="https://img.shields.io/badge/docs-mkdocs-blue.svg" alt="Documentation" />
    </a>
</div>

<div align="center">

[English](README.en.md) | [简体中文](README.md)
</div>

# ChatNPM

ChatNPM: ChatArch npm registry and package maintenance helper

## Quick Start

```bash
pip install -e ".[dev]"
chatnpm hello ChatArch
chatnpm --tree
chatnpm package inspect npm --format json
chatnpm trusted audit . --format json
python -m pytest -q
python -m build
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

This package currently depends on `chatstyle>=0.1.0,<0.2.0`; it does not keep a `chatenv` runtime dependency until ChatEnv integration is actually used. New commands should prefer:

- `CommandSchema` / `CommandField` for inputs.
- `add_interactive_option()` for the shared `-i/-I` switch.
- `resolve_command_inputs()` for missing args, defaults, TTY behavior, and validation.

## Layout

- `src/`: package source code
- `tests/code-tests/`: code tests and migrated historical tests
- `tests/cli-tests/`: real CLI tests, doc-first
- `tests/mock-cli-tests/`: mock/fake CLI tests, doc-first
- `docs/`: long-lived project docs built by mkdocs

## Development Notes

See `DEVELOP.md` and `AGENTS.md` before expanding the scaffold.
