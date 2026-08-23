# 首页

ChatNPM 是 ChatArch 的 npm registry 与 npm 发布证据只读检查工具。

- 生产文档：<https://arch.gh.wzhecnu.cn/ChatNPM/>
- GitHub：<https://github.com/ChatArch/ChatNPM>
- PyPI：<https://pypi.org/project/ChatNPM/>

## 快速开始

```bash
pip install chatnpm
chatnpm --tree
chatnpm --tree-brief
chatnpm package inspect npm --format json
chatnpm trusted audit . --format json
printf '%s\n' 'Open https://www.npmjs.com/login/abc to use your security key' | chatnpm auth parse-output --format json
```

## 能力

`chatnpm package inspect <package>` 只读取公开 npm registry metadata，输出 package、version、scope、maintainers、repository、安全 `publishConfig` 摘要、dist integrity/signature/attestation 和 provenance evidence。`chatnpm trusted audit` 只读本地 `package.json` 与 `.github/workflows/*.yml`，回报是否存在 `id-token: write`、`npm publish --provenance`、npm registry 设置与 token fallback 迹象；本地 `publishConfig` 同样只输出安全摘要，不原样回显未知或 auth-like 字段。

`chatnpm auth parse-output` 从 npm CLI 输出里解析登录 URL 与 OTP 需求，输出结构化 JSON，供 Hermes/Feishu 等平台发认证卡片并等待用户点击完成。

## CLI 树

```bash
chatnpm --tree
chatnpm --tree-brief
```

详见 [CLI 树](cli-tree.md)。

英文版：<https://arch.gh.wzhecnu.cn/ChatNPM/en/>。
