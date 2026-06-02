# Human Design LLM - Human Design AI Toolkit | 人类图 AI 解读引擎

**Human Design LLM** is an open-source Human Design AI toolkit and Web/App product foundation for **BodyGraph chart calculation, Human Design reading generation, body-energy interpretation, career analysis, relationship comparison, timing/transit context, source-traceable LLM prompts, installable AI skills, and a Chinese-first user-facing app**.

**人类图 LLM** 是一个面向 AI Agent / LLM Runtime 与 Web/App 的开源人类图产品底座，覆盖 **人类图排盘、BodyGraph 出图、身体能量解读、人类图职业解读、人类图合盘、时机分析、知识卡引用追踪、会话协议、Web API、React 前端和 Codex skill**。

It is not a static Human Design website. It is a Python product layer that turns birth data into structured chart facts, then packages those facts into LLM-ready context blocks and grounded interpretation workflows.

它不是一个静态网页，也不是单纯 prompt 模板，而是把出生资料转成结构化人类图事实，再把这些事实封装成大模型可直接使用的产品包。

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-2.5.0-black)](./CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Tests](https://img.shields.io/badge/tests-90%20passing-brightgreen)](./tests)
[![LLM Native](https://img.shields.io/badge/LLM-native-orange)](./docs/contracts/llm-package.md)

## What It Does

Human Design LLM turns a birth time into reusable product layers:

| Layer | English | 中文 |
| --- | --- | --- |
| Chart | Human Design chart calculator and BodyGraph schema | 人类图排盘与 BodyGraph 结构化数据 |
| Reading | Source-backed Human Design reading generator | 带知识卡来源的人类图解读生成器 |
| Body Energy | Center/channel/gate interpretation for body resources and energy management | 身体资源、九大中心、通道、闸门与能量管理解读 |
| Product Package | LLM-ready prompts, context blocks, citations, follow-ups, session state | 大模型可直接消费的 prompts、上下文块、引用、追问和会话状态 |
| Visuals | Template-based BodyGraph SVG rendering | 模板驱动的人类图 BodyGraph 出图 |
| Web/App | FastAPI endpoints and React/Vite user interface | FastAPI 接口与 React/Vite 用户界面 |

## Who It Is For

This repository is designed for developers and AI builders who want to create:

- Human Design AI assistants.
- Human Design chart calculator APIs.
- BodyGraph interpretation agents.
- Human Design career reading products.
- Human Design talent and deep-reading products.
- Human Design relationship chart and compatibility tools.
- Human Design timing, transit, and cycle analysis workflows.
- Chinese Human Design Web/App products with chart, report, and chat flows.
- Codex / OpenAI / Hermes / OpenClaw skills that need structured chart facts.

这个项目适合用来搭建：

- 人类图 AI 解读助手
- 人类图排盘 API
- BodyGraph 自动出图工具
- 人类图职业解读产品
- 人类图天赋深挖 / 深度解读产品
- 人类图合盘 / 关系分析工具
- 人类图流年 / transit / timing 分析流程
- 中文人类图 Web/App 产品：排盘、报告、出图和聊天问答
- 面向 Codex / OpenAI / Hermes / OpenClaw 的本地 skill

## Why This Project Is Different

- **Chart facts before interpretation**: every answer starts from calculated chart data, not prompt-only guessing.
- **LLM-native contract**: `build_llm_product()` returns system prompts, assistant instructions, focus-aware context blocks, answer citations, suggested follow-ups, delivery depth, and session state.
- **Career reading that is not generic**: `focus="career"` adds career thesis, money engine, opportunity entry, role architecture, distortion loop, and direction filters while guarding against invented gates or channels.
- **Talent reading that is not generic**: `focus="talent"` adds research method context, structure stacking, talent modules, non-genericity checks, consumption loops, and 30-day experiments.
- **Source traceability**: output sections point back to local markdown reference cards under `references/`.
- **Research-grounded deep synthesis**: `human_design.deep_synthesis` connects official/classic source digestion, YouTube/podcast practice language, Chinese terminology, and anthropological thick-description methods without copying copyrighted texts.
- **Chinese-first reading quality**: Simplified-Chinese output uses terms such as `荐骨中心`, `荐骨权威`, `阿姬娜中心`, and `人生角色`.
- **Template-driven BodyGraph**: SVG rendering uses a stable bodygraph template, not ad-hoc drawing from scratch.
- **User-facing Web/App layer**: FastAPI wraps the Python product core, while `web/` provides a real chart/report/chat interface.
- **Body resource and energy interpretation**: `build_body_energy_profile()` explains defined/open centers, channels, gates, consumption patterns, and practices.
- **Evaluation-first release loop**: `pytest`, smoke tests, narrative evals, public-figure accuracy checks, empirical-readiness checks, and `evaluate_v2.py` protect the product from shallow or generic output.

## Search Phrases This Repository Targets

English search intent:

- Human Design LLM
- Human Design AI
- Human Design chart calculator
- BodyGraph Python
- BodyGraph SVG generator
- Human Design reading generator
- Human Design career reading
- Human Design talent reading
- Human Design deep reading
- Human Design relationship chart
- Human Design transit analysis
- Human Design empirical validation
- Human Design blind test
- Human Design holdout benchmark
- Human Design prospective prediction
- AI astrology toolkit
- Codex skill for Human Design

中文搜索意图：

- 人类图
- 人类图排盘
- 人类图解读
- 人类图 AI
- 人类图职业解读
- 人类图天赋解读
- 人类图深度解读
- 人类图合盘
- 人类图关系分析
- 人类图流年
- 人类图 BodyGraph
- 人类图客观准确性
- 人类图盲测
- 人类图前瞻预测
- 人类图 holdout
- 大模型命理工具

## Current Release

`2.5.0` is the open-source release for the current development cycle.

Release scope:

- Single-chart Human Design reading.
- Career deep reading for work, money, positioning, and direction.
- Talent deep synthesis with research method context, structure stacking, non-genericity checks, and 30-day experiments.
- Relationship chart comparison and relationship LLM packages.
- Timing/transit comparison and timing LLM packages.
- Birth-time uncertainty sampling.
- BodyGraph SVG/PNG rendering scripts.
- Codex-compatible skill metadata and runtime prompt adapters.
- SEO-ready bilingual README, MIT license, package metadata, and release documentation.
- Public-figure accuracy suite with 10 Astro-Databank AA/A-rated fixtures.
- Empirical validation protocol, blinded forced-choice statistics script, and no-proof-without-data guardrails.
- 4834-record public-figure benchmark manifest, 1000 blinded holdout trials, frozen protocol hash, and prospective prediction registry.
- Chinese Web/App report tab for `天赋深挖版`, plus API response field `deep_synthesis`.

## Installation

```bash
git clone https://github.com/joyozhang333-lgtm/human-design-llm.git
cd human-design-llm

python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

If editable install is not needed, the legacy requirements path also works:

```bash
python -m pip install -r requirements-dev.txt
```

## Quick Start

Calculate a chart:

```bash
python scripts/calculate_chart.py '1988-10-09T20:30:00+08:00'
```

Generate a Chinese reading:

```bash
python scripts/generate_reading.py '1988-10-09T20:30:00+08:00'
```

Generate a career deep reading:

```bash
python scripts/generate_career_reading.py '1988-10-09T20:30:00+08:00'
```

Generate an LLM-ready career answer:

```bash
python scripts/generate_llm_product.py '1988-10-09T20:30:00+08:00' \
  --focus career \
  --question '我最适合怎么工作、赚钱、选方向？' \
  --format markdown \
  --depth deep
```

Render a BodyGraph SVG:

```bash
python scripts/render_bodygraph.py '1988-10-09T20:30:00+08:00' \
  --output outputs/bodygraphs/example.svg
```

Run the Web/App product locally:

```bash
python -m pip install -r requirements-web.txt
cp .env.example .env
uvicorn human_design.web_api:app --reload

cd web
npm install
npm run dev
```

Then open `http://127.0.0.1:5173`.

Optional AI providers:

- `DEEPSEEK_API_KEY` enables live personalized chat through DeepSeek Chat Completions. Without it, `/api/chat` falls back to the local grounded reading engine.
- `MINIMAX_API_KEY` enables report visual cover generation through MiniMax Image Generation. The formal BodyGraph remains template-rendered SVG for chart accuracy.
- `.env` is ignored by git; keep real keys local and use `.env.example` only as a template.

Run the release checks:

```bash
python -m pytest -q
python scripts/evaluate_v2.py
```

## Python API

```python
from human_design import (
    build_body_energy_profile,
    build_llm_product,
    calculate_chart,
    normalize_birth_input,
)

chart = calculate_chart(normalize_birth_input("1988-10-09T20:30:00+08:00"))
package = build_llm_product(
    chart,
    focus="career",
    question="我最适合怎么工作、赚钱、选方向？",
    depth="deep",
    citation_mode="sources",
)
body_energy = build_body_energy_profile(chart)

print(package.answer_markdown)
print(body_energy.headline)
```

## Supported Input

- ISO datetime with explicit UTC offset, such as `1988-10-09T20:30:00+08:00`.
- Naive datetime plus `--timezone`, such as `--timezone Asia/Shanghai`.
- Naive datetime plus location fields, such as `--city Shanghai --country China`.
- If timezone and location are missing, the system falls back to UTC and returns explicit precision warnings.

## Product Lines

| Product line | Main API | CLI | Output |
| --- | --- | --- | --- |
| Chart | `calculate_chart()` | `scripts/calculate_chart.py` | structured chart JSON |
| Reading | `generate_reading()` | `scripts/generate_reading.py` | markdown / JSON reading |
| Body Energy | `build_body_energy_profile()` | Web/API layer | center/channel/gate energy profile |
| Career | `generate_career_report()` | `scripts/generate_career_reading.py` | career deep reading |
| LLM package | `build_llm_product()` | `scripts/generate_llm_product.py` | LLM-ready context and answer |
| Relationship | `compare_relationship()` | `scripts/compare_relationship.py` | dual-chart comparison |
| Timing | `analyze_timing()` | `scripts/analyze_timing.py` | natal/transit comparison |
| Uncertainty | `analyze_birth_time_range()` | `scripts/analyze_uncertainty.py` | birth-time range sampling |
| BodyGraph | `render_bodygraph_svg()` | `scripts/render_bodygraph.py` | template-based SVG |
| Web/App API | `human_design.web_api:app` | `uvicorn human_design.web_api:app` | chart/report/chat HTTP API |

## Repository Structure

```text
human-design-llm/
├── human_design/          # Python package: engine, schema, readings, LLM products
├── web/                   # React/Vite user-facing Web/App
├── references/            # Markdown knowledge cards for HD types, centers, gates, channels
├── scripts/               # CLI tools for chart, reading, career, relationship, timing, evals
├── tests/                 # pytest regression suite
├── docs/                  # contracts, roadmap, release notes, SEO documentation
├── runtimes/              # Codex / Hermes / OpenClaw prompt adapters
├── agents/openai.yaml     # installable skill metadata
├── SKILL.md               # Codex skill instructions
├── pyproject.toml         # package metadata and SEO keywords
└── CHANGELOG.md
```

## Web/App Product

The Web/App layer turns the existing LLM-native toolkit into a user-facing product:

- `POST /api/charts` creates a formal chart from precise birth data.
- `POST /api/reports` generates overview, body-energy, career, relationship, or deep reports.
- `POST /api/chat` answers personalized follow-up questions grounded in chart facts and citations, using DeepSeek when configured.
- `POST /api/images/reading-visual` generates a MiniMax-powered report cover/energy visual when configured.
- `web/` renders the birth form, fixed-template BodyGraph, report reader, and chat dock.

Product requirements are documented in [docs/product-requirements-web-app.md](./docs/product-requirements-web-app.md), and the HTTP contract is documented in [docs/contracts/web-api.md](./docs/contracts/web-api.md).

## Reference Coverage

The local knowledge base currently includes:

- Human Design types.
- Authorities.
- Profiles / 人生角色.
- Centers.
- Definitions.
- 64 gates.
- 36 channels.

These files are intentionally local and source-traceable so that LLM output can cite where each interpretation block came from.

## Quality Gates

Current local release validation:

- `85` pytest cases passing.
- `evaluate_v2.py` product score: `100/100`.
- `evaluate_public_figures.py` public-figure accuracy score: `100/90`.
- `evaluate_empirical_readiness.py` scientific validation readiness score: `100/90`.
- `evaluate_accuracy_benchmark.py` 1000+ benchmark infrastructure score: `100/90`.
- 4834 public-figure records collected from Astro-Databank `c_sample`; holdout split contains 1073 records and 1000 blinded forced-choice trials.
- Smoke tests for chart, reading, relationship, timing, citations, context blocks, delivery depth, and session state.
- Narrative evals for focused answers and source rendering.
- Public-figure evals for source rating, UTC conversion, chart structure, Chinese term quality, citation rendering, no invented gates/channels, and BodyGraph SVG rendering.
- Empirical-readiness evals for falsifiable claims, blinded design, randomization, controls, chance baseline, p value, confidence interval, and truth-claim discipline.

## Documentation

- [Changelog](./CHANGELOG.md)
- [Install guide](./docs/install.md)
- [Versioning policy](./docs/versioning.md)
- [Release checklist](./docs/release-checklist.md)
- [Introduction pack](./docs/INTRODUCTION.md)
- [Web/App product requirements](./docs/product-requirements-web-app.md)
- [Chart contract](./docs/contracts/chart.md)
- [Web/App API contract](./docs/contracts/web-api.md)
- [Reading contract](./docs/contracts/reading.md)
- [LLM package contract](./docs/contracts/llm-package.md)
- [Relationship contracts](./docs/contracts/relationship.md)
- [Timing contracts](./docs/contracts/timing.md)
- [Output depth contract](./docs/contracts/output-depth.md)
- [Session contract](./docs/contracts/session.md)
- [Empirical validation protocol](./docs/empirical-validation-protocol.md)
- [Empirical trial contract](./docs/contracts/empirical-trial.md)
- [Public figure manifest contract](./docs/contracts/public-figure-manifest.md)
- [Prospective prediction contract](./docs/contracts/prospective-prediction.md)
- [Label prediction contract](./docs/contracts/label-predictions.md)
- [SEO documentation](./docs/SEO.md)

## Important Notes

Human Design is used here as a reflective and interpretive framework. This project does not provide medical, legal, financial, psychological, or guaranteed life advice.

人类图在本项目中被视为自我观察和反思工具，不应替代医学、法律、财务、心理咨询或任何现实专业建议。

The empirical validation tooling is for falsifiable testing. Demo fixtures are not evidence, and the project should not claim Human Design is scientifically proven without real preregistered blinded trials and independent replication.

本项目的实验评估工具用于可证伪测试。Demo fixture 不是科学证据；没有真实预注册盲测数据和独立复现前，不能宣称人类图已被科学证明。

## License

MIT License. See [LICENSE](./LICENSE).
