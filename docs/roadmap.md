# Human Design LLM Product Roadmap

更新时间：2026-04-22

## 产品目标

把当前仓库发展成一个 **LLM 原生的人类图 skill 产品**，而不是单纯的排盘脚本。

最终目标：

- 能接收真实用户输入：出生日期、出生时间、出生地点、用户问题、解读 focus
- 能稳定生成结构化 `chart`
- 能稳定生成结构化 `reading`
- 能稳定生成结构化 `llm product package`
- 能作为正式 skill 安装和复用
- 能通过回归样本和评测来保证质量

## 当前基线

当前仓库已经有：

- `calculation engine`
- `reading layer`
- `llm product layer`
- CLI 脚本入口
- 基础测试

当前还缺：

- 城市名 / 历史时区解析
- 64 闸门 / 36 通道的完整专属知识卡
- 更完整的 runtime adapter
- 更成体系的 eval / golden tests
- 更明确的 skill 安装与发布结构

## 版本路线图

### v0.3 Foundation Beta

目标：把产品底座做稳，重点解决输入、契约和精度边界。

必须完成：

- 输入归一化层
- 时间与时区解析层
- 历史时区/地点精度提示
- `chart / reading / llm package` 契约文档
- 样本 fixtures 和基础 golden tests
- skill 目录结构定稿

发布标准：

- 用户输入城市名时可以转成 UTC，或给出明确失败信息
- 所有脚本入口都走同一输入归一化链路
- `chart / reading / llm package` schema 定稿并文档化
- 基础测试能稳定通过

### v0.6 Knowledge Beta

目标：把“能算”升级成“能讲透”，重点补全知识系统。

必须完成：

- `references/` 知识体系目录
- 64 gates 知识卡
- 36 channels 知识卡
- 类型 / 权威 / 人生角色 / 中心知识卡外置
- `reading.py` 改为“知识驱动”而不是“主要依赖硬编码模板”
- 五种 focus 的差异化输出提升

发布标准：

- 任意一张盘里的已激活 gate/channel 都能命中专属知识
- `overview / career / relationship / decision / growth` 输出不再高度重复
- 同一张盘面对不同问题，context block 选择和答案内容会发生可解释变化

### v1.0 Release

目标：把仓库做成一个可安装、可复用、可验证的正式 skill 产品。

必须完成：

- 正式 skill 安装结构
- `agents/openai.yaml` 或等价 runtime 元数据
- 多 runtime adapter
- 更完整的 narrative eval
- 发布文档、版本号策略、smoke 脚本
- 回归样本覆盖主要 focus 模式

发布标准：

- 可直接作为 skill 安装到目标环境
- 至少 2 到 3 个 runtime 可以直接消费同一产品包
- 回归测试和 narrative eval 可稳定运行
- 文档完整到足以让别人接手继续开发

## 工作流拆分

建议把开发拆成 6 条长期工作流。

### A. Input & Time

职责：

- 输入解析
- 地点到时区
- 历史时间精度
- precision warning

主要文件：

- `human_design/input.py` 未来新增
- `human_design/engine.py`
- `scripts/*`
- `tests/test_input*.py`

### B. Contracts & Data Model

职责：

- `chart / reading / llm package` schema 演进
- 契约文档
- JSON 兼容性

主要文件：

- `human_design/schema.py`
- `docs/contracts/*.md` 未来新增
- `tests/test_schema*.py` 未来新增

### C. Knowledge System

职责：

- 64 gates
- 36 channels
- 类型 / 权威 / 人生角色 / 中心知识
- 知识索引和检索规则

主要文件：

- `references/`
- `human_design/knowledge.py`
- 后续知识索引文件

### D. Reading & Product Logic

职责：

- `reading.py`
- `product.py`
- focus-aware answer planning
- answer markdown 组织

主要文件：

- `human_design/reading.py`
- `human_design/product.py`
- `tests/test_reading.py`
- `tests/test_product.py`

### E. Runtime & Packaging

职责：

- `SKILL.md`
- runtime prompts
- skill 安装结构
- `agents/` 元数据

主要文件：

- `SKILL.md`
- `runtimes/`
- `agents/` 未来新增
- README 中的安装部分

### F. QA & Eval

职责：

- golden tests
- narrative eval
- smoke
- 样本库

主要文件：

- `tests/`
- `tests/fixtures/` 未来新增
- `scripts/smoke_*.py` 未来新增

## 详细开发计划

## Phase 1
目标版本：v0.3

### 1. 输入层

任务：

- 新增 `human_design/input.py`
- 支持：
  - ISO datetime
  - UTC offset
  - `city + country`
  - `city + region + country`
- 统一输出：
  - `birth_datetime_utc`
  - `timezone_name`
  - `source_precision`
  - `warnings`

验收：

- 所有脚本入口不再各自解析输入
- 无时区输入会给出明示 warning
- 城市查不到时不 silent fallback

### 2. 契约文档

任务：

- 新建：
  - `docs/contracts/chart.md`
  - `docs/contracts/reading.md`
  - `docs/contracts/llm-package.md`
- 标明必填字段、稳定字段、未来可扩字段

验收：

- 任何后续改 schema 的 PR 都能对照文档

### 3. 基础样本和回归

任务：

- 新建 `tests/fixtures/`
- 放入 5 到 10 组真实样本盘
- 锁定关键字段：
  - type
  - authority
  - profile
  - definition
  - channels
  - personality/design sun-earth

验收：

- 改输入层或 engine 时不会悄悄打坏已有盘

## Phase 2
目标版本：v0.6

### 4. 知识体系重构

任务：

- 新建 `references/index.json`
- 新建目录：
  - `references/types/`
  - `references/authorities/`
  - `references/profiles/`
  - `references/centers/`
  - `references/channels/`
  - `references/gates/`
- 先完成结构，再逐步填满内容

验收：

- 所有已激活 gates/channels 都可从知识卡命中解释

### 5. 阅读逻辑升级

任务：

- 把 `reading.py` 改造成“知识卡驱动渲染器”
- 区分：
  - 总览解释
  - 结构解释
  - 问题导向解释
- 降低重复模板感

验收：

- 同一张盘不同 focus 输出有明显差异
- 不是每次都把整份盘重讲一遍

### 6. 产品包升级

任务：

- 让 `product.py` 支持：
  - `focus planning`
  - `question-aware context selection`
  - 更细的 followups
  - per-runtime prompt shaping

验收：

- `llm package` 不再只是 reading 的简单包装

## Phase 3
目标版本：v1.0

### 7. Skill 安装与分发

任务：

- 定稿 skill 目录结构
- 增加 `agents/openai.yaml`
- 明确安装方式
- 明确 runtime 对接方式

验收：

- 仓库可以直接被当作 skill 产品使用

### 8. 多 runtime adapter

任务：

- 先支持：
  - Codex
  - Hermes
  - OpenClaw 或兼容 skill runtime

验收：

- 同一产品包可以被多个 runtime 直接消费

### 9. 评测与发布

任务：

- 增加 narrative eval 集
- 增加 smoke runner
- 增加 release checklist
- 明确版本号和变更说明策略

验收：

- 每次改 prompt、知识卡、reading planner 都可做自动回归

## 多线程开发建议

结论先行：

- **现在不建议立刻开很多线程**
- **建议先单线程把 v0.3 的输入层和契约层做稳**
- **从 v0.6 开始，最多开 3 条并行线程**

原因：

- 当前仓库还在定基础协议阶段
- `input / schema / engine / scripts` 强耦合
- 如果太早并行，后面会因为 schema 变动频繁互相踩

### 当前阶段建议

建议线程数：`1`

先做：

- input normalization
- timezone handling
- contracts
- fixtures

这是主干，别并行拆。

### 进入 v0.6 后建议

建议线程数：`3`

推荐拆法：

#### 线程 A：Input & Eval

负责：

- `input.py`
- `engine.py`
- fixtures
- golden tests

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

#### 线程 C：Packaging & Runtime

负责：

- `SKILL.md`
- `runtimes/`
- `agents/`
- packaging docs

写入范围：

- `SKILL.md`
- `runtimes/`
- `agents/`
- README 安装部分

### 不建议超过 3 条线程

原因：

- 仓库体量还小
- 中心共享文件太多：`schema.py`、`product.py`、`README.md`
- 第 4 条线程开始，协调成本会高于产出

## 推荐实施顺序

1. 先完成 `v0.3`
2. `v0.3` 契约冻结后，再并行启动 `v0.6` 的 3 条线程
3. `v0.6` 收口后，再做 `v1.0` 的安装、runtime 和发布

## 完成定义

这条 roadmap 的终点不是“代码更多”，而是下面 5 件事同时成立：

- 输入真实用户资料时可稳定处理
- 输出对 LLM 可直接消费
- 输出对真人阅读也成立
- skill 可以正式安装
- 每次升级都能被评测体系验证
