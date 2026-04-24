# Public Figure Manifest Contract

更新时间：2026-04-24

该契约描述 `data/empirical/public_figure_manifest.jsonl`。它用于 1000+ 公开人物 blind / holdout benchmark，不等于准确率结论。

## 来源

- Source: Astro-Databank `c_sample.zip`
- URL: `https://www.astro.com/adbexport/c_sample.zip`
- 当前构建：4834 条 timed Public Figure，Rodden `AA/A/B`
- Split seed: `human-design-accuracy-v1`

## JSONL 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `sample_id` | `string` | 内部样本 ID，例如 `adb-33` |
| `adb_id` | `string` | Astro-Databank record id |
| `name` | `string` | 公开人物姓名，仅用于 source manifest，不进入 blind prompt |
| `source_export` | `string` | export URL |
| `data_type` | `string` | 必须为 `Public Figure` |
| `rodden_rating` | `string` | `AA/A/B` |
| `gender` | `string` | ADB 性别字段 |
| `birth` | `object` | 日期、时间、地点、JD UT、经纬度原始字段 |
| `labels` | `object` | ADB categories 拆分后的标签 |
| `split` | `string` | `train/validation/holdout` |
| `blind_safe` | `object` | 盲测时必须剥离的信息 |
| `record_hash` | `string` | 样本稳定 hash |

## 盲测限制

- blind prompt 不得暴露 `name`
- blind prompt 不得暴露 birthplace / country
- blind prompt 不得暴露 `vocation` / identifying biography
- answer key 必须和 blind trials 分文件存放

## 当前规模

```json
{
  "included_records": 4834,
  "split_counts": {
    "train": 2801,
    "validation": 960,
    "holdout": 1073
  }
}
```
