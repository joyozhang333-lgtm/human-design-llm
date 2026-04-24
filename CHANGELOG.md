# Changelog

## 2.4.0 - 2026-04-24

- 从 Astro-Databank `c_sample` export 生成 4834 条 AA/A/B timed Public Figure benchmark manifest
- 固定 `human-design-accuracy-v1` split：train 2801 / validation 960 / holdout 1073
- 新增 1000 条 blinded forced-choice holdout trials，并将 answer key 分离保存
- 新增 protocol freeze hash、prospective prediction registry、benchmark readiness evaluator
- 新增 `scripts/build_public_figure_manifest.py`、`scripts/build_holdout_trials.py`、`scripts/freeze_empirical_protocol.py`、`scripts/evaluate_accuracy_benchmark.py`、`scripts/analyze_prospective_registry.py`
- 新增 `scripts/analyze_label_predictions.py` 和 label prediction contract，用于性格 / 天赋 / 职业标签 holdout 准确率评分
- 将 `evaluate_v2.py` 接入 1000+ benchmark infrastructure gate
- 明确区分 `infrastructure_score=100/90` 与真实 `actual_accuracy_score`；没有盲评和前瞻 outcome 前不能宣称 90% 命运 / 性格 / 天赋准确率
- 将产品版本切到 `2.4.0`

## 2.3.0 - 2026-04-24

- 新增 `docs/empirical-validation-protocol.md`，把“人类图是否客观准确”拆成可证伪盲测命题、对照组、机会基线、p 值、置信区间和独立复现门槛
- 新增 `docs/contracts/empirical-trial.md`，定义真实实验数据格式
- 新增 `human_design.empirical.analyze_forced_choice_experiment()` 与 `scripts/analyze_empirical_trial.py`，支持分析 4 选 1 盲测数据、Wilson 置信区间和精确二项检验
- 新增 `scripts/evaluate_empirical_readiness.py` 与 readiness suite，确保产品达到科学评估准备度 `>= 90`，同时防止把 demo fixture 误表述为科学证据
- 将 `evaluate_v2.py` 接入经验验证准备度硬门槛
- 将产品版本切到 `2.3.0`

## 2.2.1 - 2026-04-24

- 新增 10 位公开人物 Astro-Databank AA/A 评级 fixture，用于真实样本回归
- 新增 `run_public_figure_accuracy_suite()` 与 `scripts/evaluate_public_figures.py`
- 将公开人物准确度纳入质量门槛，覆盖来源、UTC 换算、盘面结构、中文术语、引用、通道 / 闸门防幻觉和 BodyGraph SVG 渲染
- 修复职业深读在只有 63 或 64 单闸门激活时仍写成 `63/64` 的问题，避免出现非本盘闸门
- 补齐 `等待邀请` 策略的中文本地化，避免投射者输出回退到英文
- 将产品版本切到 `2.2.1`

## 2.2.0 - 2026-04-24

- 将项目正式命名为 `human-design-llm`，定位为 LLM-native Human Design / 人类图 AI 解读引擎
- 重写 README 为中英文开源介绍，加入 Human Design / BodyGraph / AI / LLM / 人类图排盘 / 职业解读等 SEO 关键词
- 新增 `pyproject.toml`，补齐 Python 包元数据、依赖、关键词、GitHub URL 和测试配置
- 新增 MIT `LICENSE`
- 新增 `docs/SEO.md`，记录 GitHub description、topics、英文关键词、中文关键词和公开定位
- 将 `outputs/` 标记为本地生成物，避免把真实用户样例图提交到开源仓库
- 更新 Nominatim User-Agent，指向公开仓库名称与地址
- 修复职业深读的图谱安全问题，确保不同盘只引用实际存在的通道、闸门、中心和权威
- 本地化 career focus 高亮，避免中文回答混入 `Energy Projector` / `Ego Projected` 等英文标签
- 将产品版本切到 `2.2.0`

## 2.1.0 - 2026-04-24

- 新增 `human_design/career.py`，把职业解读升级为独立的深读产品层
- 新增 `scripts/generate_career_reading.py`，支持直接输出职业深读 Markdown / JSON
- `build_llm_product(..., focus="career")` 现在会自动注入职业命题、赚钱结构、机会入口、职业位置、误判环路和方向筛选门槛
- `career` focus 现在会识别“赚钱/方向”类问题，并生成职业主轴、职业决策阀门、市场入口、赚钱误判点和承诺风险等高密度焦点提示
- 修复变量方向摘要重复和 L/R 统计错误，避免 `PLL DLR` 这类标签被误读
- 新增 career report 回归测试，避免职业输出退回泛化建议
- 将产品版本切到 `2.1.0`

## 2.0.0 - 2026-04-23

- 为 single / relationship / timing 三条产品线统一加入 `delivery_depth`
- 为三条产品线统一加入 `session_state`
- 新增 `human_design/session.py`，把输出深度与会话连续性收口成统一协议
- 新增 `docs/contracts/output-depth.md` 与 `docs/contracts/session.md`
- 将 `scripts/evaluate_v2.py` 改成按真实产品行为评分，而不是只检查文件存在
- 完成 `Phase 4: Output & Session` 与 `Phase 5: Full Release`
- 将 `V2.0` 收口到真实评测 `100/100`
- 将产品版本切到 `2.0.0`

## 1.6.0 - 2026-04-23

- 新增 `TimingAnalysisResult`、`TimingReading`、`TimingProductPackage`
- 新增 `analyze_timing.py`、`generate_timing_reading.py`、`generate_timing_product.py`
- 新增 timing smoke / narrative eval 与 `scripts/evaluate_timing.py`
- 新增 V2.0 总规划、评分标准和 `scripts/evaluate_v2.py`
- 将 `V2.0` 当前阶段推进到 `Phase 4: Output & Session`
- 将产品版本切到 `1.6.0`

## 1.5.1 - 2026-04-23

- 新增 `run_relationship_smoke_suite()` 与 `run_relationship_narrative_eval_suite()`
- 新增 `scripts/evaluate_relationship.py`
- 新增 3 组 relationship smoke fixture 与 3 组 narrative case
- 让 `Phase 2: Relationship` 的 sources / citations / narrative gate 可验证
- 将产品版本切到 `1.5.1`

## 1.5.0 - 2026-04-23

- 新增 `RelationshipReading` 与 `RelationshipProductPackage`
- 新增 `generate_relationship_reading.py` 与 `generate_relationship_product.py`
- 新增 relationship reading / package contract 与测试覆盖
- 将双人盘能力从结构比较推进到可被 LLM 直接消费的关系产品层
- 将产品版本切到 `1.5.0`

## 1.4.0 - 2026-04-23

- 新增 `RelationshipComparisonResult` 与 `compare_relationship()`
- 新增双人盘 CLI `scripts/compare_relationship.py`
- 新增 relationship contract 与测试覆盖
- 将 `V2.0` 当前阶段推进到 `Phase 2: Relationship`
- 将产品版本切到 `1.4.0`

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
