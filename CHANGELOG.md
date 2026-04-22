# Changelog

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
