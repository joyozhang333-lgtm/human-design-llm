# Timing Contract

更新时间：2026-04-23

这份文档定义 `TimingAnalysisResult` 的结构契约。

目标：

- 支持把单人本命盘和一个指定时点的 transit/timing 场做结构化比对
- 输出当前被放大的开放中心、共享结构和短期新增主题
- 为 timing reading / timing product package 提供统一输入

## 顶层字段

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `generated_at_utc` | `string` | 稳定 | 生成时间，ISO 8601 UTC |
| `timing_label` | `string` | 稳定 | 当前时机标签，如 `current` / `today` / `launch-week` |
| `transit_datetime_local` | `string` | 稳定 | 当前时机的本地时间 |
| `transit_datetime_utc` | `string` | 稳定 | 当前时机的 UTC 时间 |
| `pressured_open_centers` | `array[string]` | 稳定 | 本命开放、当前被时机定义的中心 |
| `anchored_defined_centers` | `array[string]` | 稳定 | 本命与当前时机都定义的中心 |
| `centers` | `object` | 稳定 | 本命和当前时机中心差异 |
| `channels` | `object` | 稳定 | 本命和当前时机通道差异 |
| `gates` | `object` | 稳定 | 本命和当前时机闸门差异 |
| `natal_chart` | `object` | 稳定 | 本命完整 chart |
| `transit_chart` | `object` | 稳定 | 当前时机完整 chart |

## `centers / channels / gates`

结构：

```json
{
  "shared": ["25-51"],
  "natal_only": [],
  "transit_only": ["37-40"]
}
```

规则：

1. `shared` 表示本命和当前时机都存在。
2. `natal_only` 表示只有本命存在。
3. `transit_only` 表示只有当前时机存在，通常代表短期天气主题。

## 兼容性规则

1. timing 层允许后续增加“窗口级别”“提醒等级”等字段，但不要重写当前 delta 语义。
2. `pressured_open_centers / anchored_defined_centers / centers / channels / gates` 是上层 runtime 可依赖的稳定基线。
3. timing 结果的职责是描述“当前天气”，不是替代本命盘。
