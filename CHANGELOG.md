# Changelog

## 1.3.0 - 2026-04-23

- 新增 `normalize_birth_time_range()`，支持出生时间区间归一化
- 新增 `ChartUncertaintyResult` 与 `scripts/analyze_uncertainty.py`
- 新增 uncertainty contract 与测试覆盖
- 新增 `docs/v2-delivery-plan.md`，把 V2.0 改成阶段式持续交付循环
- 将产品版本切到 `1.3.0`

## 1.2.1 - 2026-04-23

- 扩展 smoke，增加 `answer_citations` scope/sync 与 markdown 渲染检查
- 扩展 narrative eval，支持 case 级 `citation_mode` 与 answer citation 校验
- 把 `citation_mode=sources` 正式纳入 narrative fixture 回归
- 将产品版本切到 `1.2.1`

## 1.2.0 - 2026-04-23

- 为 `llm_package` 增加 `answer_citation_mode` 与 `answer_citations`
- `build_llm_product()` 支持 `citation_mode`，可选把最终回答直接渲染为带来源的 markdown
- `scripts/generate_llm_product.py` 增加 `--citation-mode`
- 同步更新产品契约、README 和 skill 说明
- 将产品版本切到 `1.2.0`

## 1.1.1 - 2026-04-23

- 扩展 `smoke` 与 `narrative eval`，把 `sources` 来源完整性纳入回归检查
- 支持在 narrative fixture 中声明 `required_source_blocks` 与 `required_block_source_kinds`
- 增加 context block 与 reading section 的 source sync 校验，避免产品包和阅读对象脱钩
- 将产品版本切到 `1.1.1`

## 1.1.0 - 2026-04-23

- 为 `reading.sections[*]` 增加结构化 `sources`，把章节输出关联到具体知识卡
- 为 `llm_package.context_blocks[*]` 增加结构化 `sources`，让 runtime 和评测层可以直接做来源追踪
- 为 `focus-highlights` 增加来源保留，避免高亮内容和知识卡脱钩
- 补充 reading / product 契约文档与测试覆盖
- 将产品版本切到 `1.1.0`

## 1.0.0 - 2026-04-22

- 增加 `agents/openai.yaml` 和可安装 skill 结构
- 增加 `scripts/install_skill.py` 与安装文档
- 增加 `Codex / Hermes / OpenClaw` runtime adapters
- 完成 `types / authorities / profiles / centers / definitions / 64 gates / 36 channels` 引用卡覆盖
- 增加 question-aware product planner
- 增加 smoke runner 与 narrative eval
- 将产品版本切到 `1.0.0`
