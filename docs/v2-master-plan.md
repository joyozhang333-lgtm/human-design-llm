# Human Design V2.0 Master Plan

更新时间：2026-04-23

这份文档是 `V2.0` 的总规划，不是单次 sprint 表。

目标：

- 定义 `V2.0` 的完整产品范围
- 定义连续开发循环
- 定义停止条件：**评估分 >= 90/100**

## 完整范围

### 1. Single

- 单人盘输入
- 时区/城市解析
- 出生时间区间
- uncertainty
- single reading
- single LLM package
- sources / citations

### 2. Relationship

- 双人 comparison
- relationship reading
- relationship LLM package
- relationship smoke / narrative eval

### 3. Timing

- transit/timing input
- timing analysis
- timing reading
- timing LLM package
- timing smoke / narrative eval

### 4. Output & Session

- `brief / standard / deep`
- session memory structure
- 多轮追问 continuity
- output consistency eval

### 5. Quality & Release

- full regression
- release docs
- contracts completeness
- install/runtime compatibility
- readiness scoring

## 连续循环

每个阶段都必须经过：

1. 协议
2. 实现
3. 测试
4. 评估
5. 修评估失败
6. 更新文档
7. 提交

## 停止条件

只有同时满足下面条件，才算任务完成：

1. `single / relationship / timing / output-session / release` 五个维度全部有实现
2. `scripts/evaluate_v2.py` 输出总分 `>= 90`
3. 关键回归全部通过
4. README / contracts / release docs 已同步

## 当前节奏

- 已完成：`Phase 1 Uncertainty`
- 已完成：`Phase 2 Relationship`
- 已完成：`Phase 3 Timing`
- 已完成：`Phase 4 Output & Session`
- 已完成：`Phase 5 Full Release`

## 当前真实状态

当前已经达到停止条件。

当前基线：

- `scripts/evaluate_v2.py`：`100/100`
- `pytest`：`57 passed`
- `smoke_all.py`：`5/5 passed`
- `evaluate_relationship.py`：`6/6 passed`
- `evaluate_timing.py`：`6/6 passed`

当前得分仍以 `scripts/evaluate_v2.py` 的实时输出为准，但以当前基线来看，`V2.0` 已经完成主开发闭环。
