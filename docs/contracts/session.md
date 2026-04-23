# Session Contract

更新时间：2026-04-23

这份文档定义 `session_state` 的统一契约。目标是让 single / relationship / timing 三条产品线都能把“本轮最值得带进下一轮”的上下文显式暴露出来，而不是把多轮连续性藏在 markdown 里。

## 顶层字段

以下 package 都必须带 `session_state`：

- `LLMProductPackage`
- `RelationshipProductPackage`
- `TimingProductPackage`

`session_state` 结构：

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `product_line` | `string` | 稳定 | `single / relationship / timing` |
| `focus` | `string` | 稳定 | 当前会话焦点 |
| `headline` | `string` | 稳定 | 本轮最高密度结论 |
| `carry_facts` | `array[string]` | 稳定 | 下一轮可直接复用的核心事实 |
| `carry_block_keys` | `array[string]` | 稳定 | 建议下一轮继续携带的 block key |
| `suggested_next_questions` | `array[string]` | 稳定 | 适合进入下一轮的追问 |

## 当前基线规则

1. `headline` 必须来自本轮 reading headline，而不是重新拼一个新标题。
2. `carry_facts` 默认来自 `quick_facts` 的前几条，当前基线最多保留 `4` 条。
3. `carry_block_keys` 默认排除 `focus` 和 `quick-facts`，因为这两类信息重复价值较低。
4. `suggested_next_questions` 应与 `suggested_followups` 对齐，不要出现两套互相矛盾的问题建议。

## 用途

`session_state` 主要给三类消费者使用：

1. runtime：决定下一轮继续带哪些上下文块
2. eval：检查多轮连续性不是口头宣称，而是有结构化状态
3. 上层产品：把“推荐继续问什么”显式展示给用户

## 兼容性规则

1. `session_state` 是 `V2.0` 输出层稳定字段，消费方可以直接依赖。
2. 后续新增字段时只能追加，不要移除当前字段。
3. `carry_block_keys` 允许为空，但正常产品输出不应长期为空。
