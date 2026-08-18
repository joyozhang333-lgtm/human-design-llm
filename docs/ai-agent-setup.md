# AI Agent / Skill Setup

Human Design LLM can run as a repository-level Skill or as a structured context provider for any agent that supports system prompts and tool execution.

## Codex

Install a personal Skill with the bundled installer:

```bash
python scripts/install_skill.py --mode link --force
```

The default target is `~/.agents/skills/human-design`. If `CODEX_HOME` is set, the installer uses `$CODEX_HOME/skills/human-design`. Invoke it explicitly with `$human-design`, or ask for a Human Design chart in natural language.

## Claude Code

Project-level Skill:

```bash
mkdir -p .claude/skills
ln -s "$(pwd)" .claude/skills/human-design
```

Personal Skill:

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)" ~/.claude/skills/human-design
```

Claude Code reads the root `SKILL.md`. Keep the repository available at the symlink target.

## Hermes And OpenClaw

- Hermes: load `runtimes/hermes/SYSTEM_PROMPT.md`.
- OpenClaw: load `runtimes/openclaw/SYSTEM_PROMPT.md`.
- Codex without Skill discovery: load `runtimes/codex/SYSTEM_PROMPT.md`.

## Harness And Generic Agents

Load `runtimes/generic/SYSTEM_PROMPT.md` as the system instruction. Give the model a `HumanDesignChart`, `LLMProductPackage`, or API response as context. For a full product integration, call:

```text
POST /api/charts
POST /api/readings/main
POST /api/interpretation-maps
POST /api/chat
```

The agent must calculate first, use only structures present in the chart, and keep Human Design framed as a reflective tool rather than deterministic advice.

## 中文说明

本仓库既可以作为完整 Web 产品运行，也可以安装到 Codex、Claude Code、Hermes、OpenClaw、Harness 或其他 AI Agent。核心原则是“先排盘，再解读”：模型只能使用当前用户真实盘面中的类型、权威、人生角色、中心、通道和闸门，不得凭空补全。

生产环境请把模型密钥放进未提交的 `.env` 或密钥管理服务。不要把真实姓名、出生资料、对话、API Key 写进公开 fixture、截图、Issue 或日志。
