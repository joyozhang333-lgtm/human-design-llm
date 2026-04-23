# LLM Package Contract

更新时间：2026-04-23

这份文档定义 `LLMProductPackage` 的结构契约。目标是让 runtime 直接消费产品包，而不是现场重拼 prompt。

## 顶层字段

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `generated_at_utc` | `string` | 稳定 | 生成时间，ISO 8601 UTC |
| `product_name` | `string` | 稳定 | 当前固定为 `human-design-llm` |
| `product_version` | `string` | 稳定 | 产品包版本 |
| `focus` | `string` | 稳定 | `overview / career / relationship / decision / growth` |
| `delivery_depth` | `string` | 稳定 | `brief / standard / deep` |
| `question` | `string|null` | 稳定 | 用户原始问题 |
| `system_prompt` | `string` | 稳定 | runtime 可直接使用的系统提示 |
| `assistant_instructions` | `array[string]` | 稳定 | 执行约束 |
| `context_blocks` | `array` | 稳定 | 按 focus 选出的上下文块 |
| `answer_citation_mode` | `string` | 稳定 | `none / sources` |
| `answer_citations` | `array` | 稳定 | 最终回答段落到知识卡来源的结构化映射 |
| `answer_markdown` | `string` | 稳定 | 直接可展示的回答草稿 |
| `suggested_followups` | `array[string]` | 稳定 | 推荐继续追问 |
| `session_state` | `object` | 稳定 | 下一轮会话可直接复用的状态摘要 |
| `reading` | `object` | 稳定 | 完整 `HumanDesignReading` |

## `context_blocks`

每个 block 结构：

```json
{
  "key": "channels",
  "title": "通道主题",
  "content": "你当前有 1 条已定义通道……",
  "sources": [
    {
      "kind": "channel",
      "code": "25-51",
      "title": "25-51 Channel of Initiation",
      "path": "/abs/path/to/references/channels/25-51.md"
    }
  ]
}
```

稳定字段：

- `key`
- `title`
- `content`
- `sources`

`sources` 规则：

1. `context_blocks[*].sources` 用来给 runtime、评测器或上层应用做可解释性追踪。
2. 每个来源对象固定包含 `kind / code / title / path`。
3. 基础 block（如 `focus`、`quick-facts`）允许为空数组。

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

当 `answer_citation_mode = "sources"` 时，允许在 `焦点提示` 和各 section 后附加 `来源：...` 行，把回答直接映射回知识卡。

## `answer_citations`

每个 citation 结构：

```json
{
  "key": "channels",
  "title": "通道主题",
  "sources": [
    {
      "kind": "channel",
      "code": "25-51",
      "title": "25-51 Channel of Initiation",
      "path": "/abs/path/to/references/channels/25-51.md"
    }
  ]
}
```

规则：

1. `answer_citations` 是最终回答层的结构化 trace，不依赖 markdown 是否显示来源。
2. `key` 默认对应 `focus-highlights` 或 section key。
3. `sources` 的对象结构与 `context_blocks[*].sources` 相同。

## `delivery_depth`

统一规则见 [output-depth.md](/Users/zhangzhaoyang/Desktop/禅拍课程/human-design-product/docs/contracts/output-depth.md)。

当前要求：

1. `brief` 必须比 `deep` 更短，而不是只改一个标签。
2. `delivery_depth` 应同时影响 section 数量、高亮数量和 followup 数量。

## `session_state`

统一规则见 [session.md](/Users/zhangzhaoyang/Desktop/禅拍课程/human-design-product/docs/contracts/session.md)。

当前要求：

1. `session_state.product_line` 对单人产品固定为 `single`。
2. `carry_block_keys` 正常情况下不应为空。
3. `suggested_next_questions` 应与 `suggested_followups` 保持同向。

## 兼容性规则

1. `product_name`、`focus`、`context_blocks[*].key` 视为上层 runtime 契约。
2. 可以扩展 block，但不要删除已有基础 block。
3. prompt 文案可以演进，但字段名称和对象层级不要随意漂移。
4. `context_blocks[*].sources` 是新增稳定字段；消费方应兼容空数组和多来源场景。
5. `answer_citation_mode` 与 `answer_citations` 是新增稳定字段；消费方不应假设最终回答只有纯文本。
