# Human Design LLM | 开源人类图 AI、BodyGraph 与 Agent Skill

> 把 Human Design（人类图）从昂贵、封闭的一次性报告，变成人人可以运行、验证、扩展和自托管的开源产品。

[![Live Demo](https://img.shields.io/badge/Live_Demo-humandesign.guichu.chat-c46f55)](https://humandesign.guichu.chat)
[![Version](https://img.shields.io/badge/version-0.5.0-222222)](./CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-177_passing-2E8B57)](./tests)
[![License](https://img.shields.io/badge/license-MIT-2E8B57)](./LICENSE)

**在线体验 / Live Demo：<https://humandesign.guichu.chat>**

**Human Design LLM** 是 [HumanDesign.guichu.chat](https://humandesign.guichu.chat) 的完整开源代码。它既是一个可直接使用的人类图 Web 产品，也是一个可安装到 Codex、Claude Code、Hermes、OpenClaw 或其他 AI Agent 的 Skill，同时提供 Python API、FastAPI 服务和 React 前端，方便开发者构建自己的 Human Design 产品。

The repository contains the complete open-source product behind [HumanDesign.guichu.chat](https://humandesign.guichu.chat). Use it as a standalone Web app, a Human Design skill for AI agents, a Python library, or a backend/frontend foundation for your own product.

## 为什么开源

认识自己的身体节奏、决策方式和天赋，不应该只能依赖高昂的一次性解读费用。本项目希望让更多人能够：

- 免费运行或自托管一套完整的人类图产品。
- 在自己的 AI 中调用结构化盘面，而不是让模型凭空猜测。
- 看懂类型、策略、权威、人生角色、中心、通道、闸门与人生主轴如何共同作用。
- 用清晰、非决定论的语言观察自己的生命，而不是被术语或标签限制。
- 共同改进中文术语、解释质量、产品体验与工程可靠性。

仓库使用 MIT License。你可以学习、修改、部署和用于自己的产品；外部模型 API 与服务器费用仍由使用者自行承担。

## V0.5 更新了什么

V0.5 的关键词是 **从术语墙到完整阅读体验**。本版本不再只把固定模板拼成报告，而是引入新的内容生成链路：

```text
出生信息
  -> HumanDesignChart 结构化排盘
  -> 中文 ChartFacts 与事实白名单
  -> 分层解读 Prompt
  -> DeepSeek / Claude 综合生成
  -> 闸门、通道、中心与术语护栏校验
  -> SQLite 缓存
  -> 无模型或校验失败时安全回退
```

主要变化：

- **主线叙事**：先讲“这张图对你意味着什么”，再按需展开中心、通道、闸门、变量与人生主轴。
- **全盘综合解读**：类型、策略、权威、人生角色、通道与开放中心在同一条叙事中联动，不再只做单个术语查询。
- **真实 AI 生成**：主阅读与细读可以调用 DeepSeek 或 Claude；没有 API Key 时自动使用结构化中文回退内容。
- **事实护栏**：输出中的闸门、通道、中心和爻线必须来自当前盘面；违规文本会被重写或拦截。
- **中文化层**：行星、变量、回路、通道类型和常见 Human Design 术语统一转成简体中文。
- **隐私缓存**：生成缓存只保存盘面事实哈希与文本，不保存昵称、生日、出生时间、性别或出生地。
- **阅读式界面**：BodyGraph 置顶，其后依次展示核心配置、四段式报告、主题地图与咨询对话；桌面和移动端使用同一套阅读流。
- **深度探索与对话**：身体、财富、关系等主题可以继续展开，并把问题带入基于当前全盘的 AI 对话。
- **污染回归保护**：模型输出若泄露提示词、编造结构或混入开发者语言会被重写或拦截，并回退到基于真实盘面的结构化解读。

完整发布记录见 [CHANGELOG.md](./CHANGELOG.md)。

## 核心能力

| 能力 | 说明 |
| --- | --- |
| 人类图排盘 | 输入出生日期、准确时间和出生地，生成稳定的 `HumanDesignChart` JSON |
| BodyGraph | 固定模板渲染九大中心、红黑激活、闸门、通道和人格/设计侧栏 |
| 核心解读 | 类型、策略、权威、人生角色、定义、签名、非自己主题与轮回交叉 |
| 主线阅读 | L1 高密度定位、L2 全盘叙事、L3 中心/通道/闸门/变量/使命细读 |
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

仓库根目录的 [SKILL.md](./SKILL.md) 是 Skill 入口，`runtimes/` 提供不同 Agent 的运行时适配。

#### Codex

推荐安装到当前共享 Skill 目录：

```bash
python scripts/install_skill.py --mode link --force
```

默认目标为 `~/.agents/skills/human-design`。如果你的 Codex 仍使用 `CODEX_HOME`，脚本会兼容 `$CODEX_HOME/skills/human-design`。安装后可用 `$human-design` 显式调用。

#### Claude Code

项目级安装：

```bash
mkdir -p .claude/skills
ln -s "$(pwd)" .claude/skills/human-design
```

个人级安装：

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)" ~/.claude/skills/human-design
```

#### Hermes、OpenClaw、Harness 与其他 AI

- Hermes：加载 [runtimes/hermes/SYSTEM_PROMPT.md](./runtimes/hermes/SYSTEM_PROMPT.md)。
- OpenClaw：加载 [runtimes/openclaw/SYSTEM_PROMPT.md](./runtimes/openclaw/SYSTEM_PROMPT.md)。
- Codex：可直接安装 Skill，也可加载 [runtimes/codex/SYSTEM_PROMPT.md](./runtimes/codex/SYSTEM_PROMPT.md)。
- Harness 或其他 Agent 框架：加载 [runtimes/generic/SYSTEM_PROMPT.md](./runtimes/generic/SYSTEM_PROMPT.md)，并把 `build_llm_product()` 生成的 JSON 作为上下文。

详细配置与工作原理见 [AI Agent / Skill 安装指南](./docs/ai-agent-setup.md)。

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
| `POST /api/readings/main` | 生成 V0.5 主线综合解读 |
| `POST /api/readings/detail` | 按需生成中心、通道、闸门、变量或人生主轴细读 |
| `GET /api/charts/{id}/bodygraph.svg` | 获取固定模板 BodyGraph SVG |
| `GET /api/charts/{id}/reading-book` | 获取结构化阅读本 |
| `POST /api/interpretation-maps` | 获取身体、财富、天赋、关系、使命或专业信息地图 |
| `POST /api/reports` | 生成总览、身体、天赋、职业或深度报告包 |
| `POST /api/chat` | 基于当前盘面、地图上下文和会话历史继续对话 |
| `GET /api/product/providers` | 查看模型是否已配置，不返回任何 Key |

接口契约见 [docs/contracts/web-api.md](./docs/contracts/web-api.md)。

## 项目结构

```text
human-design-llm/
├── human_design/          # 排盘、schema、解读、LLM 产品与 Web API
│   └── generation/        # V0.5 facts / prompt / LLM / validator / cache / fallback
├── web/                   # React 19 + TypeScript + Vite 用户界面
├── references/            # 类型、中心、闸门、通道和研究知识卡
├── scripts/               # CLI、安装、评估和实验工具
├── tests/                 # 177 个自动化回归测试
├── runtimes/              # Codex / Claude-compatible / Hermes / OpenClaw / 通用适配
├── agents/openai.yaml     # Agent 元数据
├── SKILL.md               # Skill 入口
└── docs/                  # API、安装、版本、研究和发布文档
```

## 质量与边界

当前发布已通过：

- `177` 个 pytest 测试。
- React/TypeScript 生产构建。
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
- Human Design skills for Codex, Claude Code, Hermes, OpenClaw, Harness, and generic agents.
- FastAPI endpoints and a responsive React reading experience.
- Career, talent, relationship, timing, uncertainty, citation, and evaluation workflows.

Start with the [live demo](https://humandesign.guichu.chat), read the [AI skill setup guide](./docs/ai-agent-setup.md), or clone the repository to build your own Human Design product. Contributions in Chinese or English are welcome.

## 参与贡献

欢迎提交中文/英文术语改进、知识卡、排盘或渲染修复、无障碍优化、测试、Agent 适配和产品体验改进。请先阅读 [CONTRIBUTING.md](./CONTRIBUTING.md)。

如果你基于本仓库做了新产品，也欢迎在 Discussion 中分享。请不要在 issue、fixture、截图或 PR 中提交真实用户的姓名、出生资料或 API Key。

## License

[MIT License](./LICENSE) © Human Design LLM contributors.
