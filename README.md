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
chatnpm package inspect npm --format json
chatnpm trusted audit . --format json
python -m pytest -q
python -m build
```

## 真实 CLI 树

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

这个包当前运行时只依赖 Click；新的命令应优先使用真实注册命令生成的 `chatnpm --tree` 作为文档与测试来源。

## 目录结构

- `src/`：包源码
- `tests/`：CLI、registry、trusted publishing、docs/workflow contract 测试
- `docs/`：长期维护文档，由 MkDocs Material + i18n 构建

## 开发说明

扩展前先阅读 `DEVELOP.md` 和 `AGENTS.md`。
