# ChatNPM 文档

这里收纳 `ChatNPM` 的长期维护文档。

## npm 发布元数据检查

```bash
chatnpm package inspect npm
chatnpm package inspect npm --version 12.0.2 --format json
chatnpm trusted audit . --format json
```

该命令只读取公开 npm registry metadata，输出 package、version、scope、maintainers、repository、安全 `publishConfig` 摘要、dist integrity/signature/attestation 和 provenance evidence。`chatnpm trusted audit` 则只读本地 `package.json` 与 `.github/workflows/*.yml`，回报是否存在 `id-token: write`、`npm publish --provenance`、npm registry 设置与 token fallback 迹象；本地 `publishConfig` 同样只输出安全摘要，不原样回显未知或 auth-like 字段。

注意：npm public registry 不公开 PyPI-style Trusted Publisher settings 表。ChatNPM 会把该项读回为 `not_exposed`，避免把“公开 API 不可读”误报为“没有 Trusted Publishing”。

## 本地预览

```bash
pip install -e ".[docs]"
mkdocs serve
```

英文版见：[index.en.md](index.en.md)。
