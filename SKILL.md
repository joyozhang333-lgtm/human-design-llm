---
name: human-design
description: "人类图 (Human Design) 解读技能。根据阳历出生日期、准确出生时间和出生地点，输出 BodyGraph 相关核心结论与解释，包括类型、策略、权威、Profile、定义、中心、通道、闸门与基础解读。触发词: 人类图, Human Design, bodygraph, 类型, 策略, 权威, profile, 通道, 闸门, 轮回交叉."
---

# Human Design Skill

这是人类图产品的技能入口。当前仓库已经不是单纯的排盘脚本，而是一个可安装的 LLM 原生 skill 产品：排盘、阅读对象、会话产品包、runtime adapter、安装与评测工具链都在仓库内生成。

## 使用时机

- 用户要查自己的人类图
- 用户问类型、策略、权威、Profile、中心、通道、闸门
- 用户要把出生资料转成可解释的 BodyGraph 结构

## 必要输入

- 阳历出生日期
- 尽量精确到分钟的出生时间
- 出生地点，或至少给出时区/UTC offset

如果缺少出生时间或出生地点，必须先说明精度会明显下降，不能假装能给出精确排盘。

## 工作原则

1. 先算，再解读。不要在没有结构化盘面数据时直接输出完整人类图结论。
2. 计算层与解释层分开维护。计算结果应当可以被 CLI、脚本、API、skill 共用。
3. 对 GitHub 候选项目先看许可证、活跃度、语言栈、可嵌入性，不只看功能截图。
4. 当前本仓库已经有完整本地排盘、报告生成和 LLM 产品包链路，优先调用本仓库自己的产品层，而不是把解读外包给 prompt 硬写。

## 当前仓库导航

- GitHub 调研：`docs/github-research.md`
- 契约文档：`docs/contracts/`
- 安装文档：`docs/install.md`
- 排盘引擎：`human_design/engine.py`
- 输入归一化：`human_design/input.py`
- 解读生成器：`human_design/reading.py`
- 解读知识：`human_design/knowledge.py`
- LLM 产品层：`human_design/product.py`
- Runtime 提示：`runtimes/`（当前已提供 Codex / Hermes / OpenClaw）
- Agent 元数据：`agents/openai.yaml`
- 知识卡目录：`references/`（当前已包含 types / authorities / profiles / centers / definitions，以及 `64 gates / 36 channels` draft 覆盖）
- 脚本目录：`scripts/`
- 测试目录：`tests/`

## 当前执行方式

1. 先用 `human_design.engine.calculate_chart()` 生成结构化盘面
2. 再用 `human_design.reading.generate_reading()` 生成完整阅读对象
3. 需要文本成稿时，用 `human_design.reading.render_reading_markdown()`
4. 需要 LLM 会话产品时，用 `human_design.product.build_llm_product()`
5. 需要脚本入口时，优先使用：
   - `scripts/calculate_chart.py`
   - `scripts/generate_reading.py`
   - `scripts/generate_llm_product.py`

## 输入要求

- 最好给带时区的 ISO 时间，例如 `1988-10-09T20:30:00+08:00`
- 如果没有 offset，优先传 `--timezone`，例如 `Asia/Shanghai`
- 也支持 `--city` + `--country`，必要时补 `--region`
- 如果什么都不补，当前默认按 UTC 处理，而且结果里会显式带精度 warning
- 城市解析当前通过 geocoder + IANA timezone 解析；若解析失败，必须明确报错，不能假装成功

## LLM 产品要求

- 默认输出必须建立在结构化 chart 事实上
- 用户若提出职业、关系、成长、决策等焦点问题，应优先走 focus-aware 的产品包，而不是全文照抄总报告
- 若接到其他 runtime，应优先复用 `runtimes/` 下的适配提示，而不是现场重写 system prompt
- 当前 `reading.sections[*]` 与 `product.context_blocks[*]` 已支持 `sources` 来源追踪；如果上层 runtime 需要解释“这段话基于什么”，优先使用这些结构化来源，而不是自行猜测
- 如果上层 runtime 需要把最终回答直接映射回知识卡，优先使用 `answer_citations`；需要展示型引用时，再开启 `citation_mode=sources`
