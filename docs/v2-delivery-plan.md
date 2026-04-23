# Human Design V2.0 Delivery Plan

更新时间：2026-04-23

这份文档不是冲刺表，而是 **完整交付规划 + 连续开发循环**。

目标不是“今天冲完”，而是：

- 先把 `V2.0` 的完整范围定义清楚
- 再按固定顺序进入
  - 开发
  - 评审
  - 迭代
  - 再开发
  - 再评审
- 在 `V2.0` 完成前，不再回到“先问用户要不要做这一步”的模式

## V2.0 的完整范围

`V2.0` 不是单一功能，而是 5 条产品线一起完成。

### 1. Single

- 单人盘输入
- 时区/城市解析
- 区间时间输入
- 不确定性分析
- 总览 / 职业 / 关系 / 决策 / 成长
- 简版 / 标准版 / 深度版
- source trace
- answer citations

### 2. Relationship

- 双人输入
- 双人 chart 对照
- 关系 reading
- 决策差异
- 边界 / 情绪 / 协作差异
- relationship package
- relationship citations

### 3. Timing

- transit / timing 输入
- 当前阶段解释
- 决策时机
- 时间窗口提醒
- timing package
- timing citations

### 4. Product

- 统一 schema
- 统一 package
- 多 runtime 消费
- 多输出深度
- 多轮追问上下文结构

### 5. QA & Release

- smoke
- narrative eval
- source trace eval
- answer citation eval
- release docs
- versioning

## V2.0 完成标准

只有同时满足下面条件，才算 `V2.0 完成`：

- `single / relationship / timing` 三条主链都能独立跑通
- 三条主链都落到结构化 schema
- 三条主链都能生成 LLM product package
- 三条主链都能通过 smoke / narrative / citation 相关评测
- README / contracts / release docs 全部同步

## 开发总原则

### 1. 先协议，后扩展

每进入一个新模块，先定：

- schema
- script entry
- eval gate

再写业务逻辑。

### 2. 一次只推进一个主阶段

今天起不再“这里补一点、那里补一点”。

顺序固定为：

1. `uncertainty`
2. `relationship`
3. `timing`
4. `output depth / session layer`
5. `full eval / release`

### 3. 每一阶段都必须过一次“开发 -> 评审 -> 迭代”

每一阶段的闭环固定是：

1. 定协议
2. 实现最小可运行链路
3. 写测试
4. 跑评测
5. 修评测失败
6. 更新文档
7. 提交

没有这七步，不进入下一阶段。

## V2.0 分阶段交付

## Phase 1: Uncertainty

目标：

- 支持出生时间区间输入
- 生成多个候选 chart
- 输出稳定结构 / 漂移结构
- 把不确定性写进结构化结果

必须交付：

- `normalize_birth_time_range()`
- `ChartUncertaintyResult`
- `scripts/analyze_uncertainty.py`
- uncertainty tests
- uncertainty contract

评审 gate：

- 区间输入可跑
- sample count 正确
- stable / variable 结果可序列化
- tests 通过

## Phase 2: Relationship

目标：

- 支持双人输入与结构化对照
- 输出关系 reading 与 relationship package

必须交付：

- relationship schema
- relationship comparison logic
- relationship reading
- relationship product package
- relationship tests

评审 gate：

- 双人 package 可跑
- 至少有 3 类关系问题 narrative case
- sources / citations 可追踪

## Phase 3: Timing

目标：

- 支持时间层产品线
- 回答“现在是什么阶段”“当前更适合怎么决策”

必须交付：

- timing schema
- transit/timing input
- timing reading
- timing product package
- timing eval

评审 gate：

- timing questions 可跑
- 不宿命化
- 引用与 sources 完整

## Phase 4: Output & Session

目标：

- 从“会回答”升级成“会持续回答”

必须交付：

- 简版 / 标准版 / 深度版
- 多轮追问上下文结构
- answer mode 一致性
- mode eval

评审 gate：

- 不同深度输出差异明显
- 深度变化不破坏引用结构

## Phase 5: Full Release

目标：

- 把 V2.0 收成正式版本

必须交付：

- 全量 smoke
- narrative eval
- source trace eval
- answer citation eval
- release checklist
- changelog / version

评审 gate：

- 全量回归通过
- release docs 完整
- 仓库处于可交付状态

## 当前循环起点

从现在开始，默认按这个顺序推进：

1. 先完成 `Phase 1: Uncertainty`
2. 评审并提交
3. 再进入 `Phase 2: Relationship`
4. 再评审并提交
5. 再进入 `Phase 3: Timing`
6. 再评审并提交
7. 最后统一收口 `Phase 4 / Phase 5`

## 当前阶段

当前已进入：

- `Phase 2: Relationship`

当前动作：

- 冻结 relationship comparison schema
- 落地双人盘对照逻辑
- 增加 comparison script 和 tests
- 下一轮把 relationship reading / product package 接进来

这一轮完成前，不切去 timing。
