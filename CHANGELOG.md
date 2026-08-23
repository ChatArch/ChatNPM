# Changelog

## 2026-08-22 - 0.1.5

### Added

- Add `chatnpm auth parse-output` to parse npm CLI login/security-key/OTP prompts into a platform-neutral handoff payload (`status`, `login_url`, `otp_required`).
- Document the Hermes/Feishu card-handoff pattern: ChatNPM emits structured auth state; the host platform renders the card and resumes npm publish after user confirmation.


## 2026-08-22 - 0.1.4

### Added

- Add `chatnpm --tree-brief` for the registered CLI surface without parameter signatures.
- Add installed editable and built-wheel CLI readbacks, distribution checks, and documentation drift tests to CI.

### Changed

- Replace the package-local tree renderer with ChatStyle `add_tree_option()` on the explicit `chatnpm` root.
- Align runtime and documentation dependency bounds with the current ChatArch CLI package standard.
- Document command side effects and secret-output boundaries in both registered tree views.

## 2026-08-12 - 0.1.3

### Added

- Add bilingual MkDocs Material + i18n docs on the ChatArch production docs domain.
- Add CLI tree docs generated from the real Click command surface with purpose comments.
- Add docs and workflow contract tests for ChatArch release gates.

### Changed

- Remove the public scaffold `hello` command from the runtime CLI surface and drop the now-unused ChatStyle runtime dependency.
- Generate `chatnpm --tree` from the registered Click commands instead of maintaining a handwritten tree string.
- Align CI with Python 3.10/3.11/3.12, installed CLI smoke checks, strict MkDocs build, and source tests.
- Harden PyPI Trusted Publishing workflow with a tag/version check and default-branch ancestry guard without legacy PyPI token secrets.
- Point README, package metadata, and docs to `https://arch.gh.wzhecnu.cn/ChatNPM/`.

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

- 发布 workflow 改为显式 `v*` tag / `workflow_dispatch` 触发，使用 PyPI Trusted Publishing（`id-token: write`），不再依赖仓库级 PyPI token secret。

### Fixed
