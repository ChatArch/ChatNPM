# Home

ChatNPM is ChatArch's read-only helper for npm registry metadata and npm publishing evidence.

- Production docs: <https://arch.gh.wzhecnu.cn/ChatNPM/>
- GitHub: <https://github.com/ChatArch/ChatNPM>
- PyPI: <https://pypi.org/project/ChatNPM/>

## Quick start

```bash
pip install chatnpm
chatnpm --tree
chatnpm package inspect npm --format json
chatnpm trusted audit . --format json
```

## Capabilities

`chatnpm package inspect <package>` reads only public npm registry metadata and reports package, version, scope, maintainers, repository, a safe `publishConfig` summary, dist integrity/signature/attestation, and provenance evidence. `chatnpm trusted audit` reads only local `package.json` and `.github/workflows/*.yml` files to report `id-token: write`, `npm publish --provenance`, npm registry setup, and token-fallback evidence; local `publishConfig` is also summarized safely instead of echoing unknown or auth-like fields.

## CLI tree

```bash
chatnpm --tree
```

See [CLI Tree](cli-tree.md).

Chinese version: <https://arch.gh.wzhecnu.cn/ChatNPM/>.
