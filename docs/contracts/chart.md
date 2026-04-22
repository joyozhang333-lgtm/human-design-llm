# Chart Contract

更新时间：2026-04-22

这份文档定义 `HumanDesignChart` 的结构契约。目标不是解释所有命理术语，而是冻结产品层可依赖的数据形状。

## 顶层字段

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `generated_at_utc` | `string` | 稳定 | 生成时间，ISO 8601 UTC |
| `birth_datetime_utc` | `string` | 稳定 | 参与排盘的 UTC 出生时间 |
| `design_datetime_utc` | `string` | 稳定 | design imprint 对应 UTC 时间 |
| `input` | `object` | 稳定 | 输入归一化结果与精度提示 |
| `engine` | `object` | 稳定 | 计算引擎信息 |
| `summary` | `object` | 稳定 | 类型、策略、权威等核心摘要 |
| `variables` | `object` | 稳定 | variables 信息 |
| `definitions` | `array` | 稳定 | 定义分组 |
| `centers` | `array` | 稳定 | 九大中心状态 |
| `channels` | `array` | 稳定 | 已定义通道 |
| `activated_gates` | `array` | 稳定 | 激活闸门与引用激活 |
| `personality` | `object` | 稳定 | personality imprint 原始激活 |
| `design` | `object` | 稳定 | design imprint 原始激活 |

## `input`

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `raw_birth_time` | `string` | 稳定 | 原始输入时间字符串或 `datetime.isoformat()` |
| `birth_datetime_local` | `string` | 稳定 | 用于解释的本地时间，带 offset |
| `timezone_name` | `string` | 稳定 | IANA 时区或显式 offset 名称 |
| `source_precision` | `string` | 稳定 | `explicit-offset` / `timezone-name` / `city-resolved` / `assumed-utc` |
| `warnings` | `array[string]` | 稳定 | 精度和解析警告 |
| `location` | `object|null` | 稳定 | 地点解析结果；无地点时为 `null` |

### `input.location`

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `query` | `string` | 稳定 | 解析时使用的地点查询串 |
| `name` | `string` | 稳定 | geocoder 返回的展示名称 |
| `latitude` | `number` | 稳定 | 纬度 |
| `longitude` | `number` | 稳定 | 经度 |

## `engine`

| 字段 | 类型 | 稳定性 | 说明 |
| --- | --- | --- | --- |
| `name` | `string` | 稳定 | 当前为 `pyhd` |
| `version` | `string|null` | 稳定 | 上游版本号，未知时可为空 |
| `upstream` | `string` | 稳定 | 上游仓库链接 |
| `notes` | `array[string]` | 可扩展 | runtime patch、兼容性说明 |

## `summary`

这些字段统一为 `LabeledValue` 结构：

```json
{
  "code": "energy-projector",
  "label": "Energy Projector"
}
```

稳定字段：

- `type`
- `strategy`
- `authority`
- `profile`
- `definition`
- `signature`
- `not_self_theme`
- `incarnation_cross`

## 结构字段

### `definitions`

每项结构：

```json
{
  "centers": ["g", "heart"]
}
```

### `centers`

每项结构：

```json
{
  "code": "throat",
  "label": "Throat",
  "defined": true
}
```

### `channels`

每项结构：

```json
{
  "code": "25-51",
  "label": "Initiation",
  "gates": [25, 51],
  "centers": ["g", "heart"],
  "channel_type": {"code": "individual", "label": "Individual"},
  "circuit": {"code": "knowing", "label": "Knowing"},
  "circuit_group": {"code": "individual", "label": "Individual"},
  "is_creative": true
}
```

### `activated_gates`

每项结构：

```json
{
  "gate": 57,
  "label": "57",
  "theme": "Intuitive Insight",
  "title": "The Gentle",
  "center": "spleen",
  "quarter": "Duality",
  "channels": ["10-57", "20-57", "34-57"],
  "harmonic_gates": [10, 20, 34],
  "activations": [
    {
      "imprint": "personality",
      "planet_code": "sun",
      "planet_label": "Sun",
      "line": 2,
      "color": 1,
      "tone": 3,
      "base": 5
    }
  ]
}
```

## Imprint 数据

`personality` 与 `design` 结构一致：

- `datetime_utc`
- `activations`

每个 activation 稳定字段：

- `imprint`
- `planet_code`
- `planet_label`
- `planet_symbol`
- `longitude`
- `gate`
- `gate_label`
- `gate_theme`
- `gate_title`
- `line`
- `color`
- `tone`
- `base`

## 兼容性规则

1. 可以新增字段，但不要改已有稳定字段的语义。
2. `code` 应继续保持 JSON 友好的 slug 风格。
3. `label` 可以随着上游库变化而微调，但 `code` 不应随意漂移。
4. 若必须调整稳定字段，先更新本文档，再更新 fixtures 和 tests。
