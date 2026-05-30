# Web/App API Contract

更新时间：2026-05-30

## `POST /api/charts`

创建正式人类图。

请求：

```json
{
  "user_name": "可选昵称",
  "birth_date": "1995-03-03",
  "birth_time": "18:30",
  "city": "邢台",
  "region": "河北",
  "country": "中国",
  "timezone_name": "Asia/Shanghai"
}
```

规则：

- `birth_date` 和 `birth_time` 必填。
- `timezone_name` 或 `city/region/country` 至少提供一组。
- 仅生日会返回 `422 birth_time_required`，不生成正式图表。

响应重点字段：

```json
{
  "chart_id": "chart_xxx",
  "chart": {},
  "bodygraph_svg_url": "/api/charts/chart_xxx/bodygraph.svg",
  "bodygraph_svg": "<svg ...",
  "precision_warnings": []
}
```

## `POST /api/reports`

生成报告。

请求：

```json
{
  "chart_id": "chart_xxx",
  "report_type": "body-energy",
  "question": "可选覆盖问题"
}
```

`report_type` 可选：

- `overview`
- `body-energy`
- `career`
- `relationship`
- `deep`

响应重点字段：

```json
{
  "report_id": "report_xxx",
  "report_type": "body-energy",
  "focus": "growth",
  "answer_markdown": "...",
  "body_energy": {},
  "citations": [],
  "suggested_followups": [],
  "export_markdown": "..."
}
```

## `POST /api/chat`

围绕当前图表追问。

请求：

```json
{
  "chart_id": "chart_xxx",
  "question": "我的喉咙中心和表达方式应该怎么用？",
  "session_id": "可选"
}
```

响应重点字段：

```json
{
  "session_id": "session_xxx",
  "focus": "growth",
  "answer_markdown": "...",
  "answer_provider": "deepseek",
  "answer_model": "deepseek-v4-pro",
  "provider_configured": true,
  "citations": [],
  "suggested_followups": [],
  "session": {
    "messages": []
  }
}
```

说明：

- 配置 `DEEPSEEK_API_KEY` 后使用 DeepSeek 生成回答。
- 未配置或外部服务不可用时，接口回退到本地结构化解读引擎。
- 无论使用哪个 provider，回答都必须基于当前 `chart`、`context_blocks` 和引用，不允许编造图表事实。

## `POST /api/images/reading-visual`

生成报告视觉封面/能量图。正式 BodyGraph 仍由 `/api/charts/{chart_id}/bodygraph.svg` 提供，避免图片模型画错通道、闸门或左右行星列表。

请求：

```json
{
  "chart_id": "chart_xxx",
  "prompt": "身体能量解读视觉封面",
  "aspect_ratio": "3:4"
}
```

响应重点字段：

```json
{
  "image_id": "image_xxx",
  "chart_id": "chart_xxx",
  "provider": "minimax",
  "model": "image-01",
  "prompt": "...",
  "image_url": "data:image/jpeg;base64,...",
  "fallback_bodygraph_svg_url": "/api/charts/chart_xxx/bodygraph.svg",
  "provider_configured": true
}
```

说明：

- 配置 `MINIMAX_API_KEY` 后调用 MiniMax Image Generation。
- 未配置时返回 `provider_configured: false` 和标准 BodyGraph fallback，不报错。
- 默认返回 base64 data URL；也兼容 provider 返回的 URL。

## `GET /api/product/providers`

返回外部 AI provider 的非敏感配置状态，不包含密钥。

```json
{
  "deepseek": {
    "configured": true,
    "model": "deepseek-v4-pro",
    "base_url": "https://api.deepseek.com"
  },
  "minimax": {
    "configured": true,
    "model": "image-01",
    "endpoint": "https://api.minimax.io/v1/image_generation",
    "response_format": "base64"
  }
}
```

## 兼容性

- `chart` 继续使用 `HumanDesignChart` 契约。
- `answer_markdown`、`context_blocks`、`citations` 继续来自 `LLMProductPackage`。
- Web/App 新增字段只作为上层产品包装，不改变底层 chart 和 LLM package 字段语义。
