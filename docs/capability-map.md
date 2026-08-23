# 能力地图

## `chatnpm auth parse-output`

从 npm CLI 输出中解析一次性登录 / security-key / OTP handoff 状态，并输出平台中立 JSON：`status`、`login_url`、`otp_required`。Hermes/Feishu 这类宿主可以把 `login_url` 渲染成卡片按钮，等用户完成认证后继续原 npm 操作。

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
printf '%s\n' 'Open https://www.npmjs.com/login/abc to use your security key' | chatnpm auth parse-output --format json
```
