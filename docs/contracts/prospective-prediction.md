# Prospective Prediction Registry Contract

更新时间：2026-04-24

该契约描述 `data/empirical/prospective_prediction_registry.jsonl`。前瞻预测只有在预测被锁定后、结果窗口结束后、 outcome 被独立评分后，才可进入准确率统计。

## JSONL 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `prediction_id` | `string` | 唯一预测 ID |
| `subject_ref` | `string` | 样本或公开人物 ID |
| `locked_at` | `string` | ISO 时间；为空表示未锁定 |
| `prediction_hash` | `string` | 预测正文 hash；为空表示未锁定 |
| `prediction_text` | `string` | 可公开时可填明文；私有实验可只保留 hash |
| `horizon_start` | `string` | 预测期开始 |
| `horizon_end` | `string` | 预测期结束 |
| `outcome_metric` | `string` | 预注册 outcome 指标 |
| `outcome_status` | `string` | `unresolved/hit/miss/void` |
| `outcome_notes` | `string` | 评分说明 |

## 评分规则

- `unresolved` 不得计为成功。
- `void` 从 scorable denominator 中移除，但必须保留原因。
- 只有 `hit/miss` 进入准确率。
- `>=90%` 只有在 scorable 样本量满足预注册门槛时才可宣称。
