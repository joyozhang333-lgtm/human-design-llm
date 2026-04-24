# Human Design LLM | 人类图 AI 解读引擎

LLM-native Human Design BodyGraph toolkit for chart calculation, structured readings, career analysis, relationship comparison, timing/transit context, source-traceable prompts, and installable AI skills.

人类图 LLM 是一个面向 AI Agent / LLM Runtime 的开源人类图产品层：它不是网页应用，而是把 **人类图排盘、BodyGraph 图像、结构化解读、知识卡、引用追踪、会话协议和评测工具链** 打包成可直接被大模型消费的 Python 工具库与 skill。

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-2.2.0-black)](./CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Tests](https://img.shields.io/badge/tests-65%20passing-brightgreen)](./tests)
[![LLM Native](https://img.shields.io/badge/LLM-native-orange)](./docs/contracts/llm-package.md)

## SEO Keywords

Human Design LLM, Human Design AI, Human Design chart calculator, BodyGraph Python, BodyGraph SVG, Human Design reading generator, Human Design career reading, Human Design relationship chart, Human Design transit analysis, AI astrology toolkit, Codex skill, LLM prompt package, 人类图, 人类图排盘, 人类图解读, 人类图职业解读, 人类图合盘, 人类图流年, 人类图 AI, 大模型技能, AI 命理工具。

## English Introduction

Human Design LLM is an open-source Python toolkit for building AI-native Human Design products. It wraps the `ppo/pyhd` calculation engine with a stable local schema, then adds interpretation layers that are designed for LLMs rather than static websites.

The project produces:

- A JSON-friendly Human Design chart schema with type, strategy, authority, profile, definition, incarnation cross, variables, centers, channels, gates, and planetary activations.
- Source-traceable reading sections backed by local markdown reference cards for types, authorities, profiles, centers, definitions, gates, and channels.
- LLM product packages containing system prompts, assistant instructions, focus-aware context blocks, answer citations, suggested follow-ups, delivery depth, and session state.
- Focused product lines for single-chart readings, career readings, relationship comparison, timing/transit context, and birth-time uncertainty analysis.
- Template-driven BodyGraph SVG rendering for repeatable chart images and reading-booklet output.
- Regression tests and narrative evaluation scripts so product quality can be checked before release.

This repository is useful if you are building a Human Design AI assistant, a BodyGraph interpretation agent, a Human Design API backend, a Codex/OpenAI skill, or an LLM workflow that needs structured chart facts instead of prompt-only guessing.

## 中文介绍

Human Design LLM 是一个开源的人类图 AI 产品底座，重点解决三件事：

- **先算准**：用本地 Python 链路计算人类图，把上游 `pyhd` 的原始对象转换成稳定、可测试、可序列化的统一 chart schema。
- **再解读**：把类型、策略、权威、人生角色、九大中心、通道、闸门、变量、合盘和时机分析整理成结构化阅读对象。
- **给 LLM 用**：直接生成大模型可以消费的产品包，包括上下文块、引用来源、回答草稿、后续追问、输出深度和会话状态。

它适合做：

- 人类图 AI 解读助手
- 人类图排盘 API
- 人类图职业解读产品
- 人类图合盘 / 关系分析工具
- 人类图流年 / transit / timing 辅助分析
- Codex / OpenAI / Hermes / OpenClaw 等 runtime 的本地 skill

## Highlights

- **LLM-native product package**: `build_llm_product()` returns prompts, context blocks, citations, answer markdown, session state, and structured reading data.
- **Career deep reading**: `focus="career"` injects career thesis, money engine, opportunity entry, career role, distortion loop, and direction filters.
- **Chinese terminology layer**: Simplified-Chinese output uses terms such as `荐骨中心`, `荐骨权威`, `阿姬娜中心`, and `人生角色`.
- **Source traceability**: reading sections and answer citations point back to markdown reference cards under `references/`.
- **BodyGraph rendering**: `render_bodygraph_svg()` uses a stable SVG template rather than drawing a chart from scratch each time.
- **Evaluation-first release loop**: `pytest`, smoke tests, narrative evals, and `evaluate_v2.py` protect the product from shallow or generic output.

## Current Version

`2.2.0` is the open-source closing release for the current development cycle.

This release includes:

- Single-chart Human Design reading.
- Career deep reading for work, money, positioning, and direction.
- Relationship chart comparison and relationship LLM packages.
- Timing/transit comparison and timing LLM packages.
- Birth-time uncertainty sampling.
- BodyGraph SVG/PNG rendering scripts.
- Codex-compatible skill metadata and runtime prompt adapters.
- SEO-ready bilingual README, MIT license, package metadata, and release documentation.

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

Run the release checks:

```bash
python -m pytest -q
python scripts/evaluate_v2.py
```

## Python API

```python
from human_design import build_llm_product, calculate_chart, normalize_birth_input

chart = calculate_chart(normalize_birth_input("1988-10-09T20:30:00+08:00"))
package = build_llm_product(
    chart,
    focus="career",
    question="我最适合怎么工作、赚钱、选方向？",
    depth="deep",
    citation_mode="sources",
)

print(package.answer_markdown)
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
| Career | `generate_career_report()` | `scripts/generate_career_reading.py` | career deep reading |
| LLM package | `build_llm_product()` | `scripts/generate_llm_product.py` | LLM-ready context and answer |
| Relationship | `compare_relationship()` | `scripts/compare_relationship.py` | dual-chart comparison |
| Timing | `analyze_timing()` | `scripts/analyze_timing.py` | natal/transit comparison |
| Uncertainty | `analyze_birth_time_range()` | `scripts/analyze_uncertainty.py` | birth-time range sampling |
| BodyGraph | `render_bodygraph_svg()` | `scripts/render_bodygraph.py` | template-based SVG |

## Repository Structure

```text
human-design-llm/
├── human_design/          # Python package: engine, schema, readings, LLM products
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

- `65` pytest cases passing.
- `evaluate_v2.py` product score: `100/100`.
- Smoke tests for chart, reading, relationship, timing, citations, context blocks, delivery depth, and session state.
- Narrative evals for focused answers and source rendering.

## Documentation

- [Changelog](./CHANGELOG.md)
- [Install guide](./docs/install.md)
- [Versioning policy](./docs/versioning.md)
- [Release checklist](./docs/release-checklist.md)
- [Chart contract](./docs/contracts/chart.md)
- [Reading contract](./docs/contracts/reading.md)
- [LLM package contract](./docs/contracts/llm-package.md)
- [Relationship contracts](./docs/contracts/relationship.md)
- [Timing contracts](./docs/contracts/timing.md)
- [Output depth contract](./docs/contracts/output-depth.md)
- [Session contract](./docs/contracts/session.md)
- [SEO documentation](./docs/SEO.md)

## Important Notes

Human Design is used here as a reflective and interpretive framework. This project does not provide medical, legal, financial, psychological, or guaranteed life advice.

人类图在本项目中被视为自我观察和反思工具，不应替代医学、法律、财务、心理咨询或任何现实专业建议。

## License

MIT License. See [LICENSE](./LICENSE).
