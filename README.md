<div align="center">
    <a href="https://pypi.python.org/pypi/ChatNPM">
        <img src="https://img.shields.io/pypi/v/ChatNPM.svg" alt="PyPI version" />
    </a>
    <a href="https://github.com/ChatArch/ChatNPM/actions/workflows/ci.yml">
        <img src="https://github.com/ChatArch/ChatNPM/actions/workflows/ci.yml/badge.svg" alt="Tests" />
    </a>
    <a href="https://chatarch.github.io/ChatNPM">
        <img src="https://img.shields.io/badge/docs-mkdocs-blue.svg" alt="Documentation" />
    </a>
</div>

<div align="center">

[English](README.en.md) | [简体中文](README.md)
</div>

# ChatNPM

ChatNPM: ChatArch npm registry and package maintenance helper

## 快速开始

```bash
pip install -e ".[dev]"
chatnpm hello ChatArch
chatnpm --tree
chatnpm package inspect npm --format json
chatnpm trusted audit . --format json
python -m pytest -q
python -m build
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

这个包当前运行时依赖 `chatstyle>=0.1.0,<0.2.0`；未使用 ChatEnv 时不引入 `chatenv` 运行时依赖。新的命令应优先使用：

- `CommandSchema` / `CommandField` 描述输入。
- `add_interactive_option()` 提供统一 `-i/-I`。
- `resolve_command_inputs()` 统一缺参补问、默认值、TTY 与校验。

## 目录结构

- `src/`：包源码
- `tests/code-tests/`：代码测试和历史测试迁移
- `tests/cli-tests/`：真实 CLI 测试，doc-first
- `tests/mock-cli-tests/`：mock/fake CLI 测试，doc-first
- `docs/`：长期维护文档，由 mkdocs 构建

## 开发说明

扩展脚手架前，先阅读 `DEVELOP.md` 和 `AGENTS.md`。
