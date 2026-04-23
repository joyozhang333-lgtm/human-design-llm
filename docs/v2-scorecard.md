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

当前基线：

- `score = 100`
- `passed = true`
