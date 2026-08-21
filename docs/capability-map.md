# 能力地图

## `chatnpm package inspect`

读取公开 npm registry packument，并输出安全摘要：

- package、version、scope
- public maintainers count
- repository
- safe `publishConfig` summary
- dist integrity/signature/attestation presence
- provenance evidence

## `chatnpm trusted audit`

读取本地项目，不访问 npm 账号设置页，不输出 token 值：

- `package.json` 基础信息
- `.github/workflows/*.yml` 发布证据
- `id-token: write`
- `npm publish --provenance`
- token fallback evidence

## 验收

```bash
chatnpm --tree
chatnpm --tree-brief
chatnpm package inspect npm --format json
chatnpm trusted audit . --format json
```
