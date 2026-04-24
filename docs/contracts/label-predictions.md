# Label Prediction Contract

更新时间：2026-04-24

该契约用于人格 / 天赋 / 职业标签准确率评分。预测必须先锁定，再对 holdout manifest 评分。

## JSONL 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `sample_id` | `string` | holdout 样本 ID |
| `label_group` | `string` | `vocation`、`traits`、`life_events` |
| `predicted_labels` | `string[]` | 预测标签，必须来自冻结 label universe |
| `locked_at` | `string` | 预测锁定时间 |
| `prediction_hash` | `string` | 预测内容 hash |

## 当前评分

`scripts/analyze_label_predictions.py` 会按 label group 计算：

- scored predictions
- correct predictions
- observed accuracy
- 是否达到 `>= 90%`

没有预测文件、样本量不足、或准确率不足时，一律不得宣称性格 / 天赋准确率达到 90%。
