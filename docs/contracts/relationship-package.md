# Relationship Package Contract

更新时间：2026-04-23

这份文档定义 `RelationshipProductPackage` 的结构契约。

目标：

- 为 LLM runtime 提供可直接消费的双人关系产品包
- 保持和单人 `LLMProductPackage` 类似的上下文、引用和回答结构
- 支持 relationship focus、question lens 和 citation mode

## 顶层字段

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `generated_at_utc` | `string` | 稳定 | 生成时间 |
| `product_name` | `string` | 稳定 | 当前为 relationship 产品名 |
| `product_version` | `string` | 稳定 | 版本号 |
| `focus` | `string` | 稳定 | 当前关系焦点 |
| `question` | `string|null` | 稳定 | 用户问题 |
| `system_prompt` | `string` | 稳定 | runtime 系统提示 |
| `assistant_instructions` | `array[string]` | 稳定 | 回答规约 |
| `context_blocks` | `array` | 稳定 | LLM 消费上下文块 |
| `answer_citation_mode` | `string` | 稳定 | `none` 或 `sources` |
| `answer_citations` | `array` | 稳定 | 最终回答引用映射 |
| `answer_markdown` | `string` | 稳定 | 最终回答 |
| `suggested_followups` | `array[string]` | 稳定 | 继续追问建议 |
| `comparison` | `object` | 稳定 | 原始比较结果 |
| `reading` | `object` | 稳定 | `RelationshipReading` |

## `focus`

当前支持：

- `overview`
- `intimacy`
- `partnership`
- `decision`
- `communication`

规则：

1. `focus` 影响 sections 选择、焦点高亮和 followups。
2. 未识别 focus 时必须安全回落到 `overview`。

## `context_blocks`

当前至少可能出现：

- `focus`
- `question-lens`
- `input-precision`
- `quick-facts`
- `focus-highlights`
- 各 relationship section key

规则：

1. `focus-highlights` 如果存在，应同时出现在 `answer_citations` 中。
2. section block 的 `sources` 应与 `reading.sections[*].sources` 保持一致。

## 兼容性规则

1. relationship package 和单人 package 可以并存，不要让两者互相污染接口。
2. 后续若加入 relationship narrative eval 或 session memory，应以新增字段方式扩展。
3. `comparison / reading / context_blocks / answer_citations` 是 V2.0 relationship 层的稳定基线。
