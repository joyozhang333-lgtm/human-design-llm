# Relationship Contract

更新时间：2026-04-23

这份文档定义 `RelationshipComparisonResult` 的结构契约。

目标：

- 支持双人盘的结构化对照
- 为 relationship reading / product package 提供统一输入
- 让后续 narrative / citation 层能直接复用同一份比较结果

## 顶层字段

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `generated_at_utc` | `string` | 稳定 | 生成时间，ISO 8601 UTC |
| `left_label` | `string` | 稳定 | 左侧显示标签 |
| `right_label` | `string` | 稳定 | 右侧显示标签 |
| `summary_facets` | `array` | 稳定 | 核心摘要字段的左右对照 |
| `centers` | `object` | 稳定 | 定义中心的共享/差异结果 |
| `channels` | `object` | 稳定 | 通道的共享/差异结果 |
| `gates` | `object` | 稳定 | 激活闸门的共享/差异结果 |
| `left_chart` | `object` | 稳定 | 左侧完整单人盘 |
| `right_chart` | `object` | 稳定 | 右侧完整单人盘 |

## `summary_facets`

每项结构：

```json
{
  "key": "authority",
  "left": {"code": "ego-projected", "label": "Ego Projected"},
  "right": {"code": "sacral", "label": "Sacral"},
  "same": false
}
```

规则：

1. 当前至少覆盖：
   - `type`
   - `strategy`
   - `authority`
   - `profile`
   - `definition`
2. `same=true` 表示左右两侧该 facet 的 `code` 一致。
3. 顺序按固定摘要顺序输出，方便前端或 LLM runtime 稳定消费。

## `centers / channels / gates`

这三类差异结果都遵循同一种三段结构。

字符串集合示例：

```json
{
  "shared": ["25-51"],
  "left_only": ["10-57"],
  "right_only": ["32-54"]
}
```

数字集合示例：

```json
{
  "shared": [11, 54],
  "left_only": [25, 51],
  "right_only": [32, 59]
}
```

规则：

1. `shared` 表示两侧都存在。
2. `left_only` 表示仅左侧存在。
3. `right_only` 表示仅右侧存在。
4. 当前顺序保留原始 chart 的首次出现顺序，不额外重排。

## `left_chart / right_chart`

1. 结构与 `HumanDesignChart` 完全一致。
2. relationship 层当前不改写单人盘，只做对照。
3. 后续 relationship reading / package 应直接复用这两个完整 chart，而不是重新计算。

## 兼容性规则

1. 后续可以新增：
   - 关系主题标签
   - 决策差异
   - 沟通/边界/情绪对照
   - relationship sources / citations
2. 这些新增字段必须以附加方式引入，不要破坏当前顶层字段语义。
3. `summary_facets / centers / channels / gates / left_chart / right_chart` 这几项可以被上层产品层视为稳定基线。
