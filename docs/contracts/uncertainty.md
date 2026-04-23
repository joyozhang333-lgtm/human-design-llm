# Uncertainty Contract

更新时间：2026-04-23

这份文档定义 `ChartUncertaintyResult` 的结构契约。

目标：

- 支持出生时间区间分析
- 明确哪些结构稳定，哪些结构会漂移
- 为后续 relationship / timing 层提供统一不确定性接口

## 顶层字段

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `generated_at_utc` | `string` | 稳定 | 生成时间，ISO 8601 UTC |
| `interval_minutes` | `number` | 稳定 | 采样步长 |
| `sample_count` | `number` | 稳定 | 采样数量 |
| `range_start_local` | `string` | 稳定 | 本地区间起点 |
| `range_end_local` | `string` | 稳定 | 本地区间终点 |
| `range_start_utc` | `string` | 稳定 | UTC 区间起点 |
| `range_end_utc` | `string` | 稳定 | UTC 区间终点 |
| `summary_facets` | `array` | 稳定 | 核心摘要字段的稳定性 |
| `stable_centers` | `array[string]` | 稳定 | 在所有样本中都定义的中心 |
| `variable_centers` | `array[string]` | 稳定 | 仅在部分样本中定义的中心 |
| `stable_channels` | `array[string]` | 稳定 | 在所有样本中都存在的通道 |
| `variable_channels` | `array[string]` | 稳定 | 仅在部分样本中出现的通道 |
| `stable_gates` | `array[number]` | 稳定 | 在所有样本中都激活的闸门 |
| `variable_gates` | `array[number]` | 稳定 | 仅在部分样本中激活的闸门 |
| `samples` | `array` | 稳定 | 各采样点的轻量结果 |

## `summary_facets`

每项结构：

```json
{
  "key": "type",
  "values": [
    {"code": "energy-projector", "label": "Energy Projector"}
  ],
  "stable": true
}
```

规则：

1. `key` 当前至少覆盖：
   - `type`
   - `strategy`
   - `authority`
   - `profile`
   - `definition`
   - `signature`
   - `not_self_theme`
   - `incarnation_cross`
2. `stable=true` 表示该 facet 在所有样本中只出现一个值。
3. `values` 顺序按首次出现顺序保留。

## `samples`

每项结构：

```json
{
  "birth_datetime_local": "1988-10-09T20:00:00+08:00",
  "birth_datetime_utc": "1988-10-09T12:00:00+00:00",
  "summary": {
    "type": {"code": "energy-projector", "label": "Energy Projector"}
  },
  "defined_centers": ["g", "heart"],
  "channels": ["25-51"],
  "activated_gates": [8, 18, 25]
}
```

规则：

1. `samples` 是轻量视图，不要求包含完整 chart。
2. `summary` 结构与 `HumanDesignChart.summary` 一致。
3. `defined_centers / channels / activated_gates` 用于快速比对变化。

## 兼容性规则

1. 可以新增更细的不确定性字段，但不要改现有字段语义。
2. `stable_* / variable_*` 是上层产品层可依赖接口。
3. 如果后续加入“影响等级”或“变化原因”，应作为新增字段，而不是重写当前结构。
