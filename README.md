# Human Design LLM | 开源人类图 AI、BodyGraph 与 Agent Skill

> 把 Human Design（人类图）从昂贵、封闭的一次性报告，变成人人可以运行、验证、扩展和自托管的开源产品。

[![Live Demo](https://img.shields.io/badge/Live_Demo-humandesign.guichu.chat-c46f55)](https://humandesign.guichu.chat)
[![Version](https://img.shields.io/badge/version-0.6.2-1f4d3a)](./CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)](https://www.python.org/)
[![CI](https://github.com/joyozhang333-lgtm/human-design-llm/actions/workflows/ci.yml/badge.svg)](https://github.com/joyozhang333-lgtm/human-design-llm/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-2E8B57)](./LICENSE)

**在线体验 / Live Demo：<https://humandesign.guichu.chat>**

**Human Design LLM** 是 [HumanDesign.guichu.chat](https://humandesign.guichu.chat) 的完整开源代码。它既是一个可直接使用和自托管的人类图 Web 产品，也是一个可安装到 **Codex、Claude Code、DeepSeek Harness、Hugging Face / OpenClaw 和腾讯 WorkBuddy** 的标准 Agent Skill，同时提供 Python API、FastAPI 服务和 React 前端。

The repository contains the complete open-source product behind [HumanDesign.guichu.chat](https://humandesign.guichu.chat). Use it as a standalone Web app, a Human Design skill for AI agents, a Python library, or a backend/frontend foundation for your own product.

## 为什么开源

认识自己的身体节奏、决策方式和天赋，不应该只能依赖高昂的一次性解读费用。本项目希望让更多人能够：

- 免费运行或自托管一套完整的人类图产品。
- 在自己的 AI 中调用结构化盘面，而不是让模型凭空猜测。
- 看懂类型、策略、权威、人生角色、中心、通道、闸门与人生主轴如何共同作用。
- 用清晰、非决定论的语言观察自己的生命，而不是被术语或标签限制。
- 共同改进中文术语、解释质量、产品体验与工程可靠性。

仓库使用 MIT License。你可以学习、修改、部署和用于自己的产品；外部模型 API 与服务器费用仍由使用者自行承担。

## V0.6 更新了什么

V0.6 的关键词是 **一张图、一条阅读主线、五份真正能读的报告**。它不是在旧页面上继续删卡片，而是重新设计整个结果页和报告阅读模型：

```text
出生信息
  -> HumanDesignChart 结构化排盘
  -> 中文 ChartFacts 与事实白名单
  -> 全盘报告与通道诊断
  -> DeepSeek 连续咨询
  -> 闸门、通道、中心与术语护栏校验
  -> SQLite 缓存
  -> 无模型或校验失败时安全回退
```

主要变化：

- **BodyGraph 真正置顶**：图是结果页的第一内容，图后只保留类型、行动方式、Authority、人生角色、定义和人生主轴六项配置。
- **删除顶层术语清单**：结果页不再展示“已定义中心”“开放中心”和闸门目录；这些事实只在相关报告中按需解释。
- **通道单独成篇**：逐条解释当前盘面真实接通的能力线路，并讲清多条通道组合后的成熟表达、误用方式和现实练习。
- **五份可读报告**：身体、天赋、财富、关系、使命采用单栏文章和渐进展开，不再把目录、标签、诊断字段一次性堆满屏幕。
- **全盘综合解读**：任何天赋和人生角色都必须与真实通道、决策方式和现实场景联动，而不是给一段可套在所有人身上的定义。
- **真实连续咨询**：点击报告问题会携带当前盘面和章节上下文进入 DeepSeek 对话，回答继续推进，不复制报告原文。
- **即时打开**：主题报告由本地确定性引擎先生成，不等待外部模型；模型只在用户主动深聊时参与。
- **事实护栏**：输出中的闸门、通道、中心和爻线必须来自当前盘面；违规文本会被重写或拦截。
- **隐私缓存**：生成缓存只保存盘面事实哈希与文本，不保存昵称、生日、出生时间、性别或出生地。
- **六宿主 Agent Skill**：同一份经过审计的 Skill 可安装到 Codex、Claude Code、DeepSeek Harness、Hugging Face / OpenClaw 和腾讯 WorkBuddy；CI 验证宿主路径、元数据、执行入口和无密钥发布包。

完整发布记录见 [CHANGELOG.md](./CHANGELOG.md)。

## 核心能力

| 能力 | 说明 |
| --- | --- |
| 人类图排盘 | 输入出生日期、准确时间和出生地，生成稳定的 `HumanDesignChart` JSON |
| BodyGraph | 固定模板渲染九大中心、红黑激活、闸门、通道和人格/设计侧栏 |
| 核心解读 | 类型、Strategy、Authority、人生角色、定义、签名、非自己主题与轮回交叉 |
| 主线阅读 | L1 高密度定位、L2 全盘叙事、L3 中心/通道/变量/使命细读 |
| 身体与能量 | 已定义/开放中心、压力链、身体资源、消耗模式与观察练习 |
| 天赋与职业 | 天赋结构、角色爻线、职业位置、赚钱方式、机会入口与方向筛选 |
| 关系与合盘 | 单盘关系模式、双人盘比较和关系 LLM 产品包 |
| 时机与不确定性 | transit/timing 对照与出生时间区间采样 |
| AI 对话 | 基于盘面事实、地图上下文和会话历史继续追问，不只重复报告 |
| LLM 产品包 | Prompt、上下文块、来源、引用、追问、输出深度与会话状态 |
| 资料库 | 类型、权威、人生角色、中心、64 闸门、36 通道与研究知识卡 |
| 评估工具 | pytest、叙事评估、公开人物盘面回归、盲测与前瞻实验基础设施 |

## 两种使用方式

### 1. 作为完整产品运行

```bash
git clone https://github.com/joyozhang333-lgtm/human-design-llm.git
cd human-design-llm

python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[web,dev]"

cp .env.example .env
uvicorn human_design.web_api:app --reload --port 8000
```

另开一个终端启动前端：

```bash
cd web
npm install
npm run dev
```

打开 <http://127.0.0.1:5173>。生产部署说明见 [docs/deployment.md](./docs/deployment.md)。

可选模型配置：

```dotenv
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=deepseek-chat

# 也可以切到 Claude
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-opus-4-8
HD_LLM_PROVIDER=deepseek
```

不要把真实 Key 写入代码、截图或 Git 提交。`.env` 已被忽略；仓库只提交空值模板 `.env.example`。

### 2. 作为 AI Skill 使用

标准 Skill 包位于 [skills/human-design](./skills/human-design)。提供 UTC offset 或 IANA 时区时会完全在本地计算，不会把出生资料自动发送到公开网站；仅在用户明确允许地点查时区时才访问外部解析服务。需要 AI 深聊时，由宿主自己的模型继续解释结构化上下文。

先克隆仓库，然后使用一个安装命令：

```bash
git clone https://github.com/joyozhang333-lgtm/human-design-llm.git
cd human-design-llm
python scripts/install_skill.py --target <host> --scope user --force
```

| 宿主 | `<host>` | 用户级安装位置 | 仓库级自动发现位置 |
| --- | --- | --- | --- |
| OpenAI Codex | `codex` | `~/.codex/skills/human-design` | `.agents/skills/human-design` |
| Claude Code | `claude-code` | `~/.claude/skills/human-design` | `.claude/skills/human-design` |
| DeepSeek Harness | `deepseek-harness` | `~/.dsh/skills/human-design` | `.dsh/skills/human-design` |
| Hugging Face Agent Skills | `huggingface` | `~/.agents/skills/human-design` | `.agents/skills/human-design` |
| OpenClaw / 小龙虾 | `openclaw` | `~/.agents/skills/human-design` | `.agents/skills/human-design` |
| 腾讯 WorkBuddy / CodeBuddy | `workbuddy` | `~/.workbuddy/skills/human-design` | `.codebuddy/skills/human-design` |

一次安装所有宿主位置：

```bash
python scripts/install_skill.py --target all --scope project --force
```

为腾讯 WorkBuddy 生成可直接上传的、内容确定且不含 `.env`/缓存/密钥的 ZIP：

```bash
python scripts/install_skill.py --target workbuddy --package dist/human-design-workbuddy.zip --package-only
```

每个 `v*` 标签的 [GitHub Release](https://github.com/joyozhang333-lgtm/human-design-llm/releases) 同时提供 Python wheel、WorkBuddy ZIP 和 `SHA256SUMS`，可先校验再安装。Skill 负责 Agent 发现与工作流，Python wheel 提供本地排盘与解读引擎。

Skill 的本地执行入口：

```bash
python skills/human-design/scripts/human_design_agent.py chart '1988-10-09T20:30:00+08:00'
python skills/human-design/scripts/human_design_agent.py report '1988-10-09T20:30:00+08:00' --map-type talent
python skills/human-design/scripts/human_design_agent.py context '1988-10-09T20:30:00+08:00' --focus talent --question '我的天然优势怎样形成代表作？' --format markdown
```

详细配置、隐私边界和宿主验证方式见 [AI Agent / Skill 安装指南](./docs/ai-agent-setup.md)。

## Python 快速开始

```python
from human_design import calculate_chart, normalize_birth_input
from human_design.generation import generate_main_reading

birth = normalize_birth_input("1988-10-09T20:30:00+08:00")
chart = calculate_chart(birth)
reading = generate_main_reading(chart)

print(chart.summary.type)
print(reading.l1)
print(reading.l2)
```

常用 CLI：

```bash
python scripts/calculate_chart.py '1988-10-09T20:30:00+08:00'
python scripts/generate_reading.py '1988-10-09T20:30:00+08:00'
python scripts/generate_career_reading.py '1988-10-09T20:30:00+08:00'
python scripts/render_bodygraph.py '1988-10-09T20:30:00+08:00' --output outputs/example.svg
```

## Web API

| Endpoint | 用途 |
| --- | --- |
| `POST /api/charts` | 排盘并返回 chart、中文摘要、精度提醒与 BodyGraph URL |
| `POST /api/readings/main` | 生成 V0.6 主线综合解读 |
| `POST /api/readings/detail` | 按需生成中心、通道、闸门、变量或人生主轴细读 |
| `GET /api/charts/{id}/bodygraph.svg` | 获取固定模板 BodyGraph SVG |
| `GET /api/charts/{id}/reading-book` | 获取结构化阅读本 |
| `POST /api/interpretation-maps` | 即时获取身体、通道、财富、天赋、关系、使命或专业信息报告，不等待模型 |
| `POST /api/reports` | 生成总览、身体、天赋、职业或深度报告包 |
| `POST /api/chat` | 基于当前盘面、地图上下文和会话历史继续对话 |
| `GET /api/product/providers` | 查看模型是否已配置，不返回任何 Key |

接口契约见 [docs/contracts/web-api.md](./docs/contracts/web-api.md)。

## 项目结构

```text
human-design-llm/
├── human_design/          # 排盘、schema、解读、LLM 产品与 Web API
│   └── generation/        # V0.6 facts / prompt / LLM / validator / cache / fallback
├── web/                   # React 19 + TypeScript + Vite 用户界面
├── skills/human-design/   # 六类 Agent 共用的标准 Skill 包与本地执行器
├── .agents/               # Codex / Hugging Face / OpenClaw 仓库级发现入口
├── .claude/               # Claude Code 仓库级发现入口
├── .dsh/                  # DeepSeek Harness 仓库级发现入口
├── .codebuddy/            # 腾讯 WorkBuddy 仓库级发现入口
├── references/            # 类型、中心、闸门、通道和研究知识卡
├── scripts/               # CLI、安装、评估和实验工具
├── tests/                 # 排盘、报告、隐私、安装与 API 自动化回归
├── runtimes/              # Codex / Claude-compatible / Hermes / OpenClaw / 通用适配
├── agents/openai.yaml     # Agent 元数据
├── SKILL.md               # Skill 入口
└── docs/                  # API、安装、版本、研究和发布文档
```

## 质量与边界

每次发布必须通过：

- 全量 pytest 与内容审计。
- React/TypeScript 生产构建。
- 六类 Agent 发现路径、安装结果和本地执行入口验证。
- WorkBuddy ZIP 可重复构建与密钥排除检查。
- 闸门、通道、中心和爻线防编造校验。
- 中文术语、开发者语言污染和决定论表达回归测试。
- 公开人物排盘结构、时区转换与 BodyGraph 渲染回归。
- 盲测、holdout 和前瞻登记的评估基础设施检查。

这些是**工程质量门槛**，不是人类图“科学准确率”的证明。人类图在本项目中被定位为自我观察与反思框架，不替代医学、心理、法律、财务或其他专业意见，也不做确定性命运承诺。

## English Overview

Human Design LLM is an open-source, Chinese-first Human Design AI toolkit and production-ready foundation for:

- Structured Human Design chart calculation and BodyGraph SVG rendering.
- LLM-generated whole-chart readings with deterministic fact guardrails.
- DeepSeek and Claude provider support with safe local fallback.
- One audited Agent Skill for Codex, Claude Code, DeepSeek Harness, Hugging Face / OpenClaw, Tencent WorkBuddy, and compatible Agent Skills hosts.
- FastAPI endpoints and a responsive React reading experience.
- Career, talent, relationship, timing, uncertainty, citation, and evaluation workflows.

Start with the [live demo](https://humandesign.guichu.chat), read the [AI skill setup guide](./docs/ai-agent-setup.md), or clone the repository to build your own Human Design product. Contributions in Chinese or English are welcome.

## 参与贡献

欢迎提交中文/英文术语改进、知识卡、排盘或渲染修复、无障碍优化、测试、Agent 适配和产品体验改进。请先阅读 [CONTRIBUTING.md](./CONTRIBUTING.md)。

如果你基于本仓库做了新产品，也欢迎在 Discussion 中分享。请不要在 issue、fixture、截图或 PR 中提交真实用户的姓名、出生资料或 API Key。

## License

[MIT License](./LICENSE) © Human Design LLM contributors.
