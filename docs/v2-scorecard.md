# V2.0 Scorecard

更新时间：2026-04-23

`V2.0` 的停止条件不是“感觉差不多”，而是 **客观评分 >= 90/100**。

评分结构：

| 维度 | 满分 | 说明 |
| --- | --- | --- |
| `single` | 30 | single smoke / narrative / uncertainty |
| `relationship` | 20 | relationship smoke / narrative |
| `timing` | 20 | timing smoke / narrative |
| `output_session` | 15 | depth mode / session continuity |
| `release` | 15 | contracts / docs / regression / runtime readiness |

附加硬门槛：

- `scripts/evaluate_public_figures.py` 必须达到 `>= 90`
- 10 位公开人物样本必须全部通过来源、UTC、盘面结构、术语、引用、通道 / 闸门防幻觉和 SVG 出图检查
- `scripts/evaluate_empirical_readiness.py` 必须达到 `>= 90`
- 经验验证层必须明确区分“科学评估准备度”和“客观准确性已被证明”

## 当前门槛

- `< 70`：远未完成
- `70-89`：主链路已成型，但未成熟
- `>= 90`：可以停止主开发循环，转入维护/精修

## 使用方式

运行：

```bash
./.venv/bin/python scripts/evaluate_v2.py
```

它会输出：

- 分项得分
- 总分
- 是否达到 `>= 90`
- 公开人物准确度附加门槛

当前基线：

- `score = 100`
- `passed = true`
- `public_figure_accuracy.score = 100`
- `empirical_readiness.score = 100`
