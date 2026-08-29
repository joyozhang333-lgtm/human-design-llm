# AI Agent / Skill 安装指南

Human Design LLM V0.7 使用一份标准 `skills/human-design/SKILL.md` 服务多个 Agent。所有宿主共享同一套计算入口、隐私边界和全盘解读规则，避免分别维护多份 Prompt 后内容漂移。

## 安装前准备

```bash
git clone https://github.com/joyozhang333-lgtm/human-design-llm.git
cd human-design-llm
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

安装器默认复制 `skills/human-design/`，不会复制 `.env`、缓存、构建目录或密钥。`--scope project` 安装到指定项目，`--scope user` 安装到当前用户目录。

## OpenAI Codex

```bash
python scripts/install_skill.py --target codex --scope user --force
```

- 用户级：`~/.codex/skills/human-design`
- 项目级：`.agents/skills/human-design`
- 调用：在 Codex 中直接提出人类图问题，或显式使用 `$human-design`

仓库本身已提交 `.agents/skills/human-design/SKILL.md`，因此用 Codex 打开本仓库时无需再次复制。

## Claude Code

```bash
python scripts/install_skill.py --target claude-code --scope user --force
```

- 用户级：`~/.claude/skills/human-design`
- 项目级：`.claude/skills/human-design`

Claude Code 会从对应目录发现带 YAML frontmatter 的 `SKILL.md`。

## DeepSeek Harness

```bash
python scripts/install_skill.py --target deepseek-harness --scope user --force
```

- 用户级：`~/.dsh/skills/human-design`
- 项目级：`.dsh/skills/human-design`
- 兼容发现：DeepSeek Harness 也可读取项目 `.agents/skills`

仓库同时提交 `.dsh/skills/human-design/SKILL.md`，克隆后即可被项目级 Harness 发现。

## Hugging Face / 小龙虾兼容宿主

支持 Agent Skills 规范的 Hugging Face 工具或本地 Agent 可使用共享目录：

```bash
python scripts/install_skill.py --target huggingface --scope user --force
```

- 用户级：`~/.agents/skills/human-design`
- 项目级：`.agents/skills/human-design`

如果“小龙虾”运行时本身支持标准 `SKILL.md`，直接选择此目录；如果它只支持 system prompt，则加载 `runtimes/generic/SYSTEM_PROMPT.md`，并把本地脚本生成的 JSON 作为上下文。不要把“可加载通用 Prompt”误写成已验证的原生插件。

## OpenClaw

```bash
python scripts/install_skill.py --target openclaw --scope user --force
```

OpenClaw 使用共享 `.agents/skills/human-design`。对不带 Skill discovery 的旧运行时，可加载 `runtimes/openclaw/SYSTEM_PROMPT.md`。

## 腾讯 WorkBuddy / CodeBuddy

仓库级安装：

```bash
python scripts/install_skill.py --target workbuddy --scope project --force
```

目标为 `.codebuddy/skills/human-design`。如果 WorkBuddy 使用“上传本地 Skill 包”的界面，生成可重复构建的 ZIP：

```bash
python scripts/install_skill.py \
  --target workbuddy \
  --package dist/human-design-workbuddy.zip \
  --package-only
```

随后在 WorkBuddy 的 Skills 面板上传 `dist/human-design-workbuddy.zip`。发布工作流会为 `v*` 标签自动构建同样的包，并在 GitHub Release 中同时提供 Python wheel 和 `SHA256SUMS`。WorkBuddy ZIP 提供 Skill 指令与本地入口，wheel 提供它调用的排盘与解读引擎。

## 一次安装全部项目入口

```bash
python scripts/install_skill.py --target all --scope project --force
```

Codex、Hugging Face 与 OpenClaw 共用 `.agents/skills`，安装器会自动去重，不会复制三份内容。

## 本地执行契约

Skill 通过同一个本地适配器调用产品层：

```bash
python skills/human-design/scripts/human_design_agent.py \
  chart '1988-10-09T20:30:00+08:00'

python skills/human-design/scripts/human_design_agent.py \
  report '1988-10-09T20:30:00+08:00' \
  --map-type channels

python skills/human-design/scripts/human_design_agent.py \
  context '1988-10-09T20:30:00+08:00' \
  --focus talent \
  --question '我的天然优势怎样形成代表作？' \
  --format markdown
```

`chart` 返回标准盘面 JSON，`report` 返回结构化主题报告，`context` 返回适合宿主继续对话的上下文或 Markdown。脚本本身不发网络请求。

## 隐私与模型

- 本地排盘和报告无需 API Key。
- Skill 不会自动把出生信息发送到 `humandesign.guichu.chat`。
- 如果宿主使用自己的远程模型，出生资料会受该宿主的数据策略约束，使用者应自行确认。
- 不要把真实姓名、出生日期、出生时间、出生地、会话内容或 API Key 写进公开示例、Issue、截图、fixture 或 Git 提交。
- 人类图在本项目中是自我观察框架，不是医学或心理诊断，也不提供确定性财富、关系或命运预测。

## 发布前验证

```bash
python -m pytest -q tests/test_installer.py
python scripts/install_skill.py --target all --scope project --project-dir /tmp/hd-agent-check --force
python scripts/install_skill.py --target workbuddy --package /tmp/human-design-workbuddy.zip --package-only
python skills/human-design/scripts/human_design_agent.py report \
  '1988-10-09T20:30:00+08:00' --map-type talent
```

CI 还会校验四类仓库发现入口、Skill frontmatter、确定性 ZIP、密钥排除以及本地报告执行。
