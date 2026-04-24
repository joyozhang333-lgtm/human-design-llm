# Timing Package Contract

更新时间：2026-04-23

这份文档定义 `TimingProductPackage` 的结构契约。

目标：

- 让 LLM runtime 直接消费 timing 产品包
- 保持和单人 / relationship package 一致的 context、citation 和 answer 结构
- 支持 timing focus 与 timing narrative eval

## 顶层字段

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `generated_at_utc` | `string` | 稳定 | 生成时间 |
| `product_name` | `string` | 稳定 | timing 产品名 |
| `product_version` | `string` | 稳定 | 版本号 |
| `focus` | `string` | 稳定 | timing 焦点 |
| `delivery_depth` | `string` | 稳定 | `brief / standard / deep` |
| `question` | `string|null` | 稳定 | 用户问题 |
| `context_blocks` | `array` | 稳定 | LLM 消费上下文块 |
| `answer_citation_mode` | `string` | 稳定 | `none` 或 `sources` |
| `answer_citations` | `array` | 稳定 | 回答引用映射 |
| `answer_markdown` | `string` | 稳定 | 最终回答 |
| `suggested_followups` | `array[string]` | 稳定 | 继续追问建议 |
| `session_state` | `object` | 稳定 | 下一轮 timing 会话状态摘要 |
| `timing` | `object` | 稳定 | `TimingAnalysisResult` |
| `reading` | `object` | 稳定 | `TimingReading` |

## `focus`

当前支持：

- `overview`
- `decision`
- `timing`
- `energy`
- `growth`

规则：

1. `focus` 影响 sections 选择、焦点高亮和 followups。
2. 未识别 focus 时必须回落到 `overview`。

## `delivery_depth`

统一规则见 [output-depth.md](docs/contracts/output-depth.md)。

timing 基线要求：

1. `brief` 更适合快速判断“现在是什么天气”。
2. `deep` 应保留更多时机解释与练习建议。

## `session_state`

统一规则见 [session.md](docs/contracts/session.md)。

timing 基线要求：

1. `session_state.product_line` 固定为 `timing`。
2. `carry_facts` 应优先保留当前时机最重要的压力点与锚定点。
