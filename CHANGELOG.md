# Changelog

## 2026-08-12 - 0.1.2

### Added

- Add `chatnpm package inspect <package>` for read-only npm registry publisher/provenance metadata readback with safe `publishConfig` summaries.
- Add `chatnpm trusted audit [PATH]` for local GitHub Actions OIDC/provenance workflow evidence without printing token variables or values.
- Report npm dist integrity/signature/attestation presence and provenance evidence without reading or writing npm tokens.
- Add `chatnpm --tree` so the real CLI command surface can be verified during release checks.
- Remove unused `chatenv` runtime dependency, bound `chatstyle` to the current compatible `0.1.x` line, and bound MkDocs docs extras.

### Changed

- Document that npm public registry metadata does not expose a PyPI-style Trusted Publisher settings table; ChatNPM reports this as `not_exposed` instead of guessing.

## 2026-06-23

### Added

### Changed

- 准备 `0.1.1` 发版，用于验证 PyPI Trusted Publishing 免 token 发布流程。

- 发布 workflow 改为显式 `v*` tag / `workflow_dispatch` 触发，使用 PyPI Trusted Publishing（`id-token: write` + `environment: pypi`），不再依赖仓库级 PyPI token secret。

### Fixed
