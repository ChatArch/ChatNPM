# CLI 树

ChatNPM 使用共享的 `chatstyle.add_tree_option()` 从真实 Click 注册面生成命令树。`chatnpm --tree` 包含参数签名，`chatnpm --tree-brief` 保留相同节点和用途说明但省略签名。

## 完整树

```text
chatnpm
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
├── auth  # Parse npm authentication handoff prompts.
│   └── parse-output [--format OUTPUT-FORMAT]  # Parse npm CLI output from stdin into a card-handoff payload.
├── package  # Inspect public npm registry metadata; read-only network access.
│   └── inspect <PACKAGE> [--version PACKAGE-VERSION] [--registry REGISTRY] [--format OUTPUT-FORMAT]  # Read public package metadata; sends one request and never outputs auth values.
└── trusted  # Audit npm Trusted Publishing evidence; read-only filesystem access.
    └── audit [PATH] [--format OUTPUT-FORMAT]  # Read package/workflow evidence under PATH; no account access or secret output.
```

## 简版树

```text
chatnpm
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
├── auth  # Parse npm authentication handoff prompts.
│   └── parse-output  # Parse npm CLI output from stdin into a card-handoff payload.
├── package  # Inspect public npm registry metadata; read-only network access.
│   └── inspect  # Read public package metadata; sends one request and never outputs auth values.
└── trusted  # Audit npm Trusted Publishing evidence; read-only filesystem access.
    └── audit  # Read package/workflow evidence under PATH; no account access or secret output.
```

## 验收命令

```bash
chatnpm --version
chatnpm --tree
chatnpm --tree-brief
chatnpm package inspect npm --format json
chatnpm trusted audit . --format json
printf '%s\n' 'Open https://www.npmjs.com/login/abc to use your security key' | chatnpm auth parse-output --format json
```
