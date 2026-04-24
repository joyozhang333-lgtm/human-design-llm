# Reading Contract

更新时间：2026-04-22

这份文档定义 `HumanDesignReading` 的结构契约。

## 顶层字段

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `generated_at_utc` | `string` | 稳定 | 生成时间，ISO 8601 UTC |
| `headline` | `string` | 稳定 | 高密度阅读标题 |
| `quick_facts` | `array[string]` | 稳定 | 快速摘要；允许扩展新条目 |
| `sections` | `array` | 稳定 | 阅读章节 |
| `suggested_questions` | `array[string]` | 稳定 | 建议继续追问 |
| `chart` | `object` | 稳定 | 完整 `HumanDesignChart` 对象 |

## `sections`

每个 section 结构：

```json
{
  "key": "decision",
  "title": "决策与行动方式",
  "summary": "行动上，你的策略是……",
  "bullets": [
    "具体建议 1",
    "具体建议 2"
  ],
  "sources": [
    {
      "kind": "authority",
      "code": "ego-projected",
      "title": "Ego Projected Authority",
      "path": "/abs/path/to/references/authorities/ego-projected.md"
    }
  ]
}
```

稳定字段：

- `key`
- `title`
- `summary`
- `bullets`
- `sources`

`sources` 规则：

1. 这是结构化来源追踪字段，用来标记该 section 主要基于哪些知识卡。
2. 每个来源对象固定包含 `kind / code / title / path`。
3. 允许为空数组；当 section 主要由 chart 原始结构拼装、没有明确知识卡支撑时，可以不附来源。

## 当前默认章节 key

这些 key 可被产品层直接引用：

- `core`
- `decision`
- `profile-definition`
- `cross-variables`
- `centers`
- `channels`
- `gates`
- `integration`

规则：

1. 这些 key 视为稳定接口，不要轻易改名。
2. 可新增新 section，但不要删除已有默认 key，除非同步调整 product 层与 tests。

## quick_facts 规则

当前 quick facts 至少覆盖：

- 类型
- 策略
- 权威
- 人生角色
- 定义
- 轮回交叉
- 输入精度
- 输入警告（若存在）

说明：

1. `quick_facts` 的顺序可微调，但不应删除这些核心信息。
2. 如果输入精度存在警告，必须显式体现在 `quick_facts`。

## 兼容性规则

1. `headline` 和 `summary` 的文案可演进，但结构必须保持稳定。
2. `sections[*].key` 是产品层选段逻辑的契约，不要在未同步上层代码时改动。
3. `chart` 必须保持原样附带，不能在阅读对象里裁剪成不完整版本。
4. `sections[*].sources` 是新增稳定字段；上层消费方应允许它为空，但不应假设该字段不存在。
