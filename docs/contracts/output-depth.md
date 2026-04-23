# Output Depth Contract

更新时间：2026-04-23

这份文档定义 `delivery_depth` 的统一契约。目标是让 single / relationship / timing 三条产品线在输出深度上行为一致，而不是每条链各自发散。

## 顶层字段

以下 package 都必须带 `delivery_depth`：

- `LLMProductPackage`
- `RelationshipProductPackage`
- `TimingProductPackage`

字段定义：

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `delivery_depth` | `string` | 稳定 | 输出深度模式 |

## 支持的值

- `brief`
- `standard`
- `deep`

规则：

1. 传入未知值时必须安全回落到 `standard`。
2. `brief` 用于快速读一遍骨架，不追求全量展开。
3. `deep` 用于更完整的解释、更多高亮和更长的上下文。

## 行为约束

`delivery_depth` 不能只是标签，至少要改变三件事：

1. section 选择数量
2. `focus-highlights` 的条数上限
3. `suggested_followups` 的保留数量

当前基线：

- `brief`
  - 只保留前 2 个 focus section
  - `focus-highlights` 上限 `3`
  - `suggested_followups` 保留前 `2`
- `standard`
  - 保留默认 focus section
  - `focus-highlights` 上限 `5`
- `deep`
  - 保留默认 focus section
  - `focus-highlights` 上限 `7`

## 兼容性规则

1. `delivery_depth` 是 `V2.0` 稳定契约，上层 runtime 可以直接依赖。
2. 允许后续继续细化每个深度的细节，但不要删除现有取值。
3. 如果未来新增深度模式，应以向后兼容方式扩展，不要重命名现有值。
