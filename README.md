<div align="center">
    <a href="https://pypi.python.org/pypi/ChatNPM">
        <img src="https://img.shields.io/pypi/v/ChatNPM.svg" alt="PyPI version" />
    </a>
    <a href="https://github.com/ChatArch/ChatNPM/actions/workflows/ci.yml">
        <img src="https://github.com/ChatArch/ChatNPM/actions/workflows/ci.yml/badge.svg" alt="Tests" />
    </a>
    <a href="https://arch.gh.wzhecnu.cn/ChatNPM/">
        <img src="https://img.shields.io/badge/docs-mkdocs-blue.svg" alt="Documentation" />
    </a>
</div>

<div align="center">

[英文版](README.en.md) | [简体中文](README.md)
</div>

# ChatNPM

ChatNPM: ChatArch npm registry and package maintenance helper

文档：<https://arch.gh.wzhecnu.cn/ChatNPM/>

## 快速开始

```bash
pip install chatnpm
chatnpm --tree
chatnpm --tree-brief
chatnpm package inspect npm --format json
chatnpm trusted audit . --format json
printf '%s\n' 'Open https://www.npmjs.com/login/abc to use your security key' | chatnpm auth parse-output --format json
python -m pytest -q
python -m build
```

## 真实 CLI 树

`chatnpm --tree` 显示参数签名；`chatnpm --tree-brief` 保留相同节点和用途说明，但省略参数签名。两者均由 ChatStyle 从真实 Click 注册面生成。

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

## npm 发布元数据只读检查

`chatnpm package inspect <package>` 会读取公开 npm registry packument，输出安全摘要：

- package / version / scope
- public maintainers count and names from registry metadata
- repository and safe `publishConfig` summary
- dist integrity/signature/attestation presence
- provenance evidence when `dist.attestations` is present
- local GitHub Actions evidence for npm OIDC / `npm publish --provenance` through `chatnpm trusted audit`

npm 的公开 registry 不提供类似 PyPI 项目设置页的 Trusted Publisher 表格，因此 ChatNPM 会明确报告：

```text
Trusted Publishing settings: not exposed by public npm registry
```

这不是失败，也不是推断没有 Trusted Publishing；它只表示公开读回只能验证 registry provenance/attestation evidence，不能读取 npm 账号/包设置里的 trusted-publishing 配置。

## CLI 规范

这个包使用 `chatstyle>=0.2.0,<0.3.0` 的 `add_tree_option()` 生成完整和简洁命令树，不维护包内 renderer。ChatNPM 没有 env/profile/config 行为，因此不依赖 ChatEnv。

## 目录结构

- `src/`：包源码
- `tests/`：CLI、registry、trusted publishing、docs/workflow contract 测试
- `docs/`：长期维护文档，由 MkDocs Material + i18n 构建

## 开发说明

扩展前先阅读 `DEVELOP.md` 和 `AGENTS.md`。
