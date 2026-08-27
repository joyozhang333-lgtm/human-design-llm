# Install Guide

更新时间：2026-08-27

## 目标

把这个仓库安装成一个可直接被 Codex 发现和调用的 skill。

## 安装前提

- 已安装 Python 3.11+
- 仓库根目录包含：
  - `SKILL.md`
  - `agents/openai.yaml`

## 推荐安装方式

本仓库已经包含 `.agents/skills/human-design` 入口，在仓库内开发时不需要再次安装。要把 Skill 接入另一个项目，可从仓库执行安装器，并把目标明确指向消费项目：

```bash
cd /path/to/human-design-llm
. .venv/bin/activate
python scripts/install_skill.py \
  --target codex \
  --scope project \
  --project-dir /path/to/consumer-project \
  --mode link \
  --force
```

Codex 项目级入口会安装到消费项目的：

```text
.agents/skills/human-design
```

## 复制安装

如果不想保留软链接，可以复制一份：

```bash
python scripts/install_skill.py --target codex --scope user --mode copy --force
```

用户级 Codex Skill 默认安装到 `~/.codex/skills/human-design`。

## 自定义项目或用户目录

```bash
python scripts/install_skill.py --target codex --scope project --project-dir /path/to/project --force
python scripts/install_skill.py --target codex --scope user --home-dir /path/to/home --force
```

## 安装后验证

1. 确认目标目录存在 `SKILL.md`
2. 确认目标目录存在 `agents/openai.yaml`
3. 在 Codex 里用 `$human-design` 或相关触发词调用

Claude Code、DeepSeek Harness、Hugging Face / OpenClaw 和腾讯 WorkBuddy 的目标路径与安装命令见 [ai-agent-setup.md](./ai-agent-setup.md)。

## 注意事项

- `link` 模式适合开发；`copy` 模式适合固定快照。
- 如果目标已存在，必须显式传 `--force`。
