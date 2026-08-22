# Capability Map

## `chatnpm auth parse-output`

Parses npm CLI output for one-time login / security-key / OTP handoff state and emits platform-neutral JSON: `status`, `login_url`, and `otp_required`. Hosts such as Hermes/Feishu can render `login_url` as a card button, wait for user confirmation, and then resume the npm operation.

## `chatnpm package inspect`

Reads public npm registry packuments and returns a safe summary:

- package, version, scope
- public maintainer count
- repository
- safe `publishConfig` summary
- dist integrity/signature/attestation presence
- provenance evidence

## `chatnpm trusted audit`

Reads a local project without accessing npm account settings or printing token values:

- `package.json` basics
- `.github/workflows/*.yml` publishing evidence
- `id-token: write`
- `npm publish --provenance`
- token fallback evidence

## Acceptance

```bash
chatnpm --tree
chatnpm --tree-brief
chatnpm package inspect npm --format json
chatnpm trusted audit . --format json
printf '%s\n' 'Open https://www.npmjs.com/login/abc to use your security key' | chatnpm auth parse-output --format json
```
