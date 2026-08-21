# Capability Map

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
```
