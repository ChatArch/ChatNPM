# ChatNPM Docs

Long-lived documentation for `ChatNPM` lives here.

## npm publishing metadata inspection

```bash
chatnpm package inspect npm
chatnpm package inspect npm --version 12.0.2 --format json
chatnpm trusted audit . --format json
```

The command reads only public npm registry metadata and reports package, version, scope, maintainers, repository, a safe `publishConfig` summary, dist integrity/signature/attestation, and provenance evidence. `chatnpm trusted audit` reads only local `package.json` and `.github/workflows/*.yml` files to report `id-token: write`, `npm publish --provenance`, npm registry setup, and token-fallback evidence; local `publishConfig` is also summarized safely instead of echoing unknown or auth-like fields.

Note: the public npm registry does not expose a PyPI-style Trusted Publisher settings table. ChatNPM reports that field as `not_exposed` so “not publicly readable” is not confused with “Trusted Publishing is absent”.

## Local Preview

```bash
pip install -e ".[docs]"
mkdocs serve
```

Chinese version: [index.md](index.md).
