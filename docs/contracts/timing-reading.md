# Timing Reading Contract

更新时间：2026-04-23

这份文档定义 `TimingReading` 的结构契约。

目标：

- 把 `TimingAnalysisResult` 翻译成可读的阶段解读
- 明确区分长期本命结构和短期天气
- 为 timing LLM package 提供统一 reading 层

## 顶层字段

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `generated_at_utc` | `string` | 稳定 | 生成时间 |
| `headline` | `string` | 稳定 | timing 解读标题 |
| `quick_facts` | `array[string]` | 稳定 | 当前时点、权威、放大点等摘要 |
| `sections` | `array` | 稳定 | timing 章节 |
| `suggested_questions` | `array[string]` | 稳定 | 继续追问建议 |
| `timing` | `object` | 稳定 | 原始 `TimingAnalysisResult` |

## `sections`

当前至少包含：

- `current-atmosphere`
- `pressure-points`
- `decision-window`
- `timing-practice`

规则：

1. `sources` 用于把 timing 解读追溯到真实命中的 authority / center / channel / gate 卡。
2. `sections` 可以扩展，但不要更改现有 key 的核心语义。
