# Install Guide

更新时间：2026-08-18

## 目标

把这个仓库安装成一个可直接被 Codex 发现和调用的 skill。

## 安装前提

- 已安装 Python 3.11+
- 仓库根目录包含：
  - `SKILL.md`
  - `agents/openai.yaml`

## 推荐安装方式

开发期建议用软链接，更新仓库后不需要重复复制。

```bash
cd human-design-llm
. .venv/bin/activate
python scripts/install_skill.py --mode link --force
```

默认会安装到：

```text
~/.agents/skills/human-design
```

## 复制安装

如果不想保留软链接，可以复制一份：

```bash
python scripts/install_skill.py --mode copy --force
```

## 自定义安装目录

```bash
python scripts/install_skill.py --codex-home /path/to/codex-home --mode link --force
```

## 安装后验证

1. 确认目标目录存在 `SKILL.md`
2. 确认目标目录存在 `agents/openai.yaml`
3. 在 Codex 里用 `$human-design` 或相关触发词调用

如果已设置 `CODEX_HOME`，安装器会兼容 `$CODEX_HOME/skills/human-design`。Claude Code、Hermes、OpenClaw 和通用 Agent 的安装方式见 [ai-agent-setup.md](./ai-agent-setup.md)。

## 注意事项

- `link` 模式适合开发；`copy` 模式适合固定快照。
- 如果目标已存在，必须显式传 `--force`。
