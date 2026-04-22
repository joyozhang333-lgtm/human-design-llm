# Human Design LLM Product Execution Plan

更新时间：2026-04-22

这份文档不是 roadmap 的重复版，而是把 roadmap 变成可执行开发计划。

对应关系：

- `docs/roadmap.md` 说明版本目标与阶段边界
- 本文档说明每个版本怎么做、怎么评审、怎么提交、何时适合并行

## 总执行原则

1. 先做基础协议，再扩知识系统。
2. 所有新能力必须优先沉到结构化层，而不是只沉到 prompt。
3. 每个版本都要同时收口三件事：
   - 功能
   - 评审
   - 提交
4. 未通过版本 gate 时，不进入下一个版本。

## 版本总览

| 版本 | 核心目标 | 主工作流 | 是否建议并行 | 完成信号 |
| --- | --- | --- | --- | --- |
| v0.3 | 把输入、时区、契约和基础回归做稳 | Input / Contracts / Eval | 不建议 | 输入稳定，schema 定稿，fixtures 可回归 |
| v0.6 | 把知识系统与阅读逻辑做深 | Knowledge / Reading / Product | 可，最多 3 线程 | 64 门/36 通道可命中，focus 输出显著分化 |
| v1.0 | 把 skill 做成可安装、可发布产品 | Runtime / Packaging / Release QA | 可，2-3 线程 | 可安装、可复用、可评测、可交接 |

## v0.3 开发计划

目标：Foundation Beta

### 开发任务

#### A1 输入归一化

- 新增 `human_design/input.py`
- 统一处理：
  - ISO datetime
  - UTC offset
  - `city + country`
  - `city + region + country`
- 统一输出：
  - `birth_datetime_utc`
  - `timezone_name`
  - `source_precision`
  - `warnings`

完成标准：

- 所有脚本入口统一走 `input.py`
- 无时区输入不会 silent assume，必须带 warning
- 城市解析失败不会悄悄 fallback

#### A2 契约冻结

- 新建：
  - `docs/contracts/chart.md`
  - `docs/contracts/reading.md`
  - `docs/contracts/llm-package.md`
- 把当前稳定字段和可变字段分开写清楚
- 为 schema 增加必要注释与测试

完成标准：

- 后续改字段时有明确定义可以对照
- 不再靠 README 口头描述 schema

#### A3 样本回归

- 新建 `tests/fixtures/`
- 建 5-10 组真实样本
- 锁住关键字段：
  - type
  - authority
  - profile
  - definition
  - channels
  - personality/design sun-earth

完成标准：

- 改 engine/input 后，主要盘面不会悄悄漂移

### 评审 gate

进入 v0.3 收口前，必须逐条满足：

- 输入层所有入口统一
- 契约文档齐全
- fixtures 可跑
- `pytest` 全绿
- README 与 SKILL 对当前行为描述一致

### 提交策略

建议拆成 3 到 4 个 commit：

1. `feat(input): unify birth time and timezone normalization`
2. `docs(contracts): define chart reading and llm package contracts`
3. `test(fixtures): add golden chart fixtures and regression coverage`
4. `chore(v0.3): finalize foundation beta docs`

### 是否建议多线程

不建议。

原因：

- `input / engine / schema / scripts` 强耦合
- 现在并行会导致反复改协议
- 这个版本是基础设施，先单线程定稳更划算

建议线程数：`1`

## v0.6 开发计划

目标：Knowledge Beta

### 开发任务

#### B1 知识目录重构

- 新建：
  - `references/index.json`
  - `references/types/`
  - `references/authorities/`
  - `references/profiles/`
  - `references/centers/`
  - `references/channels/`
  - `references/gates/`
- 先定结构，再逐步填内容

完成标准：

- 知识已经不依赖单一 `knowledge.py`
- 仓库内的知识组织符合 skill 的 progressive disclosure 结构

#### B2 闸门与通道知识落地

- 64 gates 全量知识卡
- 36 channels 全量知识卡
- 对每个 focus 标出适合读取的解释角度

完成标准：

- 任意一张盘的激活 gate/channel 都能命中专属知识

#### B3 阅读逻辑升级

- `reading.py` 从“模板驱动”改成“知识卡驱动”
- 降低重复度
- 强化 focus 差异：
  - overview
  - career
  - relationship
  - decision
  - growth

完成标准：

- 同一张盘面对不同问题，不再只是换标题

#### B4 产品包升级

- `product.py` 做 question-aware selection
- context block 选择变得可解释
- followups 更聚焦

完成标准：

- LLM 产品包不再只是 reading 的简单包装

### 评审 gate

- 64 gates / 36 channels 覆盖度达标
- 至少 5 张样本盘在不同 focus 下输出有清晰差异
- `pytest` 全绿
- 抽样阅读输出没有明显术语堆砌和整段重复

### 提交策略

建议拆成 4 到 6 个 commit：

1. `feat(knowledge): scaffold structured reference library`
2. `feat(gates): add gate knowledge cards`
3. `feat(channels): add channel knowledge cards`
4. `feat(reading): migrate reading layer to reference-driven rendering`
5. `feat(product): improve focus-aware llm package planning`
6. `chore(v0.6): finalize knowledge beta docs`

### 是否建议多线程

建议，但最多 `3` 条线程。

推荐拆法：

#### 线程 A：Input & Eval

负责：

- `input.py`
- `engine.py`
- fixtures
- regression tests

写入范围：

- `human_design/input.py`
- `human_design/engine.py`
- `tests/test_engine*.py`
- `tests/fixtures/`

#### 线程 B：Knowledge & Reading

负责：

- `references/`
- `knowledge.py`
- `reading.py`

写入范围：

- `references/`
- `human_design/knowledge.py`
- `human_design/reading.py`
- `tests/test_reading*.py`

#### 线程 C：Product & Runtime

负责：

- `product.py`
- `runtimes/`
- `SKILL.md`
- 安装/使用文档

写入范围：

- `human_design/product.py`
- `runtimes/`
- `SKILL.md`
- README 中的产品层说明

## v1.0 开发计划

目标：Release

### 开发任务

#### C1 Skill 安装与元数据

- 定稿 skill 目录结构
- 新增 `agents/openai.yaml`
- 完成安装说明

完成标准：

- 仓库可直接作为 skill 被安装和调用

#### C2 Runtime 适配

- 至少支持：
  - Codex
  - Hermes
  - OpenClaw 或兼容 runtime
- 每个 runtime 有最小适配提示和使用方式

完成标准：

- 同一产品包可被多个 runtime 直接消费

#### C3 评测与发布

- narrative eval
- smoke runner
- release checklist
- 版本号策略
- 更新日志策略

完成标准：

- 改 prompt / reading / 知识卡后可自动回归

### 评审 gate

- skill 可以安装
- 至少 2-3 个 runtime 可用
- narrative eval 与 smoke 可跑
- 文档完整到足以交接

### 提交策略

建议拆成 4 到 5 个 commit：

1. `feat(skill): finalize installable skill packaging`
2. `feat(runtime): add runtime adapters and metadata`
3. `feat(eval): add narrative eval and smoke runner`
4. `docs(release): add release checklist and versioning policy`
5. `chore(v1.0): release candidate baseline`

### 是否建议多线程

可以，建议 `2-3` 条线程。

但不建议超过 3 条。

原因：

- 共享文件已经很多：`schema.py`、`product.py`、`README.md`、`SKILL.md`
- 第 4 条线程开始，协调成本明显上升

## 自动推进规则

如果按自动推进工作流执行，每一轮循环都按下面顺序走：

1. 识别当前目标版本
2. 选当前版本里最高优先级且未完成的任务
3. 开发
4. 本地评审
5. 运行相关测试
6. 更新文档
7. 满足 gate 后提交 commit
8. 若版本完成，切换到下一个版本

## 自动评审清单

每次提交前至少检查：

- 功能是否落在当前版本范围内，没有越界扩张
- 是否更新了对应文档
- 是否补了或更新了测试
- 是否破坏现有 schema
- 是否引入了重复知识或 prompt duplication
- 是否把本该结构化的内容偷懒写死在 prompt 里

## 自动提交规则

- 只在当前任务完成并通过对应 gate 时提交
- 提交粒度按“一个可解释的能力增量”拆
- 不把多个工作流混成一个巨型 commit
- 若只是探索或半成品，不提交

## 结论：是否需要开多个线程

结论如下：

- `v0.3`：**不需要**
- `v0.6`：**需要，但最多 3 条**
- `v1.0`：**可以开 2-3 条**

当前建议：

- 先单线程打完 `v0.3`
- 再在 `v0.6` 启动最多 3 条工作线程
- `v1.0` 沿用 2-3 条线程收口
