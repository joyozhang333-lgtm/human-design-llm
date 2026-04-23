# Relationship Reading Contract

更新时间：2026-04-23

这份文档定义 `RelationshipReading` 的结构契约。

目标：

- 把双人盘结构差异翻译成可读的关系解读
- 为 relationship product package 提供统一 reading 层
- 保持 section/source 结构与单人 reading 兼容

## 顶层字段

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `generated_at_utc` | `string` | 稳定 | 生成时间，ISO 8601 UTC |
| `headline` | `string` | 稳定 | 双人关系解读标题 |
| `quick_facts` | `array[string]` | 稳定 | 双方关键信息和结构摘要 |
| `sections` | `array` | 稳定 | 关系章节列表 |
| `suggested_questions` | `array[string]` | 稳定 | 继续追问建议 |
| `comparison` | `object` | 稳定 | 原始 `RelationshipComparisonResult` |

## `sections`

每项结构沿用通用 `ReadingSection`：

```json
{
  "key": "decision-sync",
  "title": "共同决策",
  "summary": "双人关系里最容易出问题的，不是意见不同，而是两个人把确认方式混成一种。",
  "bullets": [
    "A 先按自己的策略与权威确认。",
    "B 先按自己的策略与权威确认。"
  ],
  "sources": [
    {
      "kind": "authority",
      "code": "ego-projected",
      "title": "Ego Projected Authority",
      "path": "/abs/path/to/file.md"
    }
  ]
}
```

规则：

1. 当前至少包含：
   - `relationship-skeleton`
   - `resonance`
   - `friction`
   - `decision-sync`
   - `relationship-practice`
2. `sources` 用于把关系章节追溯回双人比较实际命中的知识卡。
3. 后续可新增章节，但不要改变现有 key 的语义。

## 兼容性规则

1. `quick_facts / sections / suggested_questions / comparison` 是上层 runtime 可依赖字段。
2. 后续如果加入合盘专属指标，应以新增字段或新增 section 的方式引入。
3. 关系 reading 允许比单人 reading 更强调比较和规则，但不能脱离 `comparison` 的真实结构。
