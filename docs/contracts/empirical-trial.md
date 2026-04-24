# Empirical Trial Contract

更新时间：2026-04-24

该契约用于 `scripts/analyze_empirical_trial.py` 分析真实盲测数据。它只描述数据格式，不代表实验已经证明人类图准确。

## 顶层字段

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 | 实验 ID |
| `experiment_type` | `string` | 是 | 例如 `forced-choice-self-identification` |
| `status` | `string` | 是 | `demo-format-only-not-evidence`、`preregistered-pilot`、`preregistered-main` |
| `claim` | `string` | 是 | 可证伪命题 |
| `preregistered` | `boolean` | 是 | 是否预注册 |
| `blinded` | `boolean` | 是 | 是否盲测 |
| `randomized` | `boolean` | 是 | 是否随机 |
| `control_conditions` | `string[]` | 是 | 对照条件 |
| `options_per_trial` | `integer` | 是 | 每题候选数量 |
| `minimum_sample_size` | `integer` | 是 | 预注册最小样本量 |
| `alpha` | `number` | 是 | 显著性阈值 |
| `success_threshold` | `object` | 是 | 成功门槛 |
| `trials` | `object[]` | 条件 | 原始试次数据 |
| `summary` | `object` | 条件 | 聚合数据；只能用于公开报告的摘要或测试 fixture |

`trials` 和 `summary` 至少提供一个。正式实验归档必须保存 `trials` 原始匿名数据；`summary` 不能替代原始数据审计。

## success_threshold

```json
{
  "accuracy": 0.45,
  "ci_lower_above_chance": true
}
```

## trials[]

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `participant_id` | `string` | 是 | 匿名参与者 ID |
| `correct_option_id` | `string` | 是 | 正确报告选项 |
| `selected_option_id` | `string` | 是 | 参与者选择 |
| `option_ids` | `string[]` | 是 | 本题全部候选 |
| `response_seconds` | `number` | 否 | 作答耗时 |

## summary

```json
{
  "trials": 120,
  "correct": 66
}
```

`summary` 可用于 demo、论文摘要复算或单元测试，但正式结论必须能追溯到原始匿名 `trials[]`。

## 输出指标

`analyze_empirical_trial.py` 输出：

- `total_trials`
- `correct_trials`
- `options_per_trial`
- `chance_accuracy`
- `observed_accuracy`
- `wilson_ci_low`
- `wilson_ci_high`
- `exact_p_value`
- `passed_statistical_threshold`
- `evidence_status`

## 结论边界

- `demo-only-not-evidence`：格式演示，不是科学证据。
- `not-supported-by-current-data`：当前数据未支持命题。
- `passed-preregistered-threshold`：当前数据超过预注册统计门槛，但仍需独立复现实验。
