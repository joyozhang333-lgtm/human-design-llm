# LLM Package Contract

更新时间：2026-04-22

这份文档定义 `LLMProductPackage` 的结构契约。目标是让 runtime 直接消费产品包，而不是现场重拼 prompt。

## 顶层字段

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `generated_at_utc` | `string` | 稳定 | 生成时间，ISO 8601 UTC |
| `product_name` | `string` | 稳定 | 当前固定为 `human-design-llm` |
| `product_version` | `string` | 稳定 | 产品包版本 |
| `focus` | `string` | 稳定 | `overview / career / relationship / decision / growth` |
| `question` | `string|null` | 稳定 | 用户原始问题 |
| `system_prompt` | `string` | 稳定 | runtime 可直接使用的系统提示 |
| `assistant_instructions` | `array[string]` | 稳定 | 执行约束 |
| `context_blocks` | `array` | 稳定 | 按 focus 选出的上下文块 |
| `answer_markdown` | `string` | 稳定 | 直接可展示的回答草稿 |
| `suggested_followups` | `array[string]` | 稳定 | 推荐继续追问 |
| `reading` | `object` | 稳定 | 完整 `HumanDesignReading` |

## `context_blocks`

每个 block 结构：

```json
{
  "key": "channels",
  "title": "通道主题",
  "content": "你当前有 1 条已定义通道……"
}
```

稳定字段：

- `key`
- `title`
- `content`

## 当前约定的 block key

基础 block：

- `focus`
- `quick-facts`

条件 block：

- `input-precision`

章节 block：

- `core`
- `decision`
- `profile-definition`
- `cross-variables`
- `centers`
- `channels`
- `gates`
- `integration`

规则：

1. `focus` 与 `quick-facts` 默认必须存在。
2. 当 `chart.input.warnings` 非空时，`input-precision` 必须存在。
3. 章节 block 由 focus 选择器决定，不要求每次全量输出。

## focus 规则

| focus | 默认 section keys |
| --- | --- |
| `overview` | `core`, `decision`, `profile-definition`, `cross-variables`, `centers`, `channels`, `gates`, `integration` |
| `career` | `core`, `decision`, `profile-definition`, `cross-variables`, `channels`, `integration` |
| `relationship` | `core`, `decision`, `profile-definition`, `centers`, `channels`, `integration` |
| `decision` | `decision`, `profile-definition`, `cross-variables`, `integration` |
| `growth` | `core`, `profile-definition`, `centers`, `channels`, `gates`, `integration` |

## `answer_markdown` 规则

当前回答草稿至少包含：

- 标题
- `headline`
- `当前聚焦`
- `当前问题`（如果有）
- `输入精度提示`（如果有 warning）
- 选中 sections
- `建议继续追问`

## 兼容性规则

1. `product_name`、`focus`、`context_blocks[*].key` 视为上层 runtime 契约。
2. 可以扩展 block，但不要删除已有基础 block。
3. prompt 文案可以演进，但字段名称和对象层级不要随意漂移。
