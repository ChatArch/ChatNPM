# CLI 树

`chatnpm --tree` 从真实 Click 注册命令面生成，用来在本地 gate、CI 和发布 readback 中锁定公开接口。

```text
chatnpm  # ChatArch npm registry and publishing-evidence helper.
├── --help  # Show this help message.
├── --version  # Show the installed package version.
├── --tree  # Print the registered command tree.
├── package  # Inspect npm package registry metadata.
│   └── inspect PACKAGE [--version PACKAGE-VERSION] [--registry REGISTRY] [--format text|json]  # Read npm registry publisher/provenance metadata for PACKAGE.
└── trusted  # Audit npm Trusted Publishing evidence.
    └── audit [PATH] [--format text|json]  # Read local package/workflow evidence for npm Trusted Publishing.
```

## 验收命令

```bash
chatnpm --version
chatnpm --tree
chatnpm package inspect npm --format json
chatnpm trusted audit . --format json
```
