# Web/App API Contract

更新时间：2026-08-18

## `POST /api/readings/main`

生成 V0.5 主报告，响应包括一句核心定位、四段式全盘叙事、活对/活拧体感、可展开专业目录和主题地图入口。配置模型后走 LLM；无 Key、调用失败或护栏不通过时使用结构化回退。

## `POST /api/readings/detail`

按需生成中心、通道、闸门、变量或人生主轴细读。所有结构必须来自当前盘面白名单。

## `POST /api/charts`

创建正式人类图。

请求：

```json
{
  "user_name": "可选昵称",
  "gender": "female",
  "birth_date": "1970-02-04",
  "birth_time": "12:00",
  "city": "杭州",
  "region": "浙江"
}
```

规则：

- `birth_date` 和 `birth_time` 必填。
- 中文用户表单只展示 `city/region`，不展示国家和时区；后端仍兼容 `country` 和 `timezone_name`。
- `timezone_name` 或 `city/region/country` 至少提供一组；中文前端默认内部传入 `Asia/Shanghai`。
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
- `talent`
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
  "deep_synthesis": {},
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
  "session_id": "可选",
  "map_type": "body",
  "map_item_key": "可选",
  "entry_source": "followup_button",
  "synthesis_mode": "full_chart"
}
```

响应重点字段：

```json
{
  "session_id": "session_xxx",
  "focus": "growth",
  "answer_markdown": "...",
  "answer_provider": "deepseek",
  "answer_model": "deepseek-chat",
  "provider_configured": true,
  "entry_source": "followup_button",
  "synthesis_mode": "full_chart",
  "citations": [],
  "map_context": {
    "map_type": "body",
    "title": "身体地图",
    "sections": [],
    "retrieved_knowledge": []
  },
  "suggested_followups": [],
  "session": {
    "messages": []
  }
}
```

说明：

- 配置 `DEEPSEEK_API_KEY` 后使用 DeepSeek 生成回答。
- 未配置或外部服务不可用时，接口回退到本地结构化解读引擎。
- 无论使用哪个 provider，回答都必须基于当前 `chart`、`context_blocks`、`map_context` 和引用，不允许编造图表事实。
- 当问题包含“天赋、优势、潜能、使命、主航道、深挖”等意图时，默认进入 `focus: talent`，回答必须引用真实结构并输出具体天赋模块、误用方式和可观察练习。

## `POST /api/interpretation-maps`

生成 V0.5 全盘综合解读地图。前端展示独立的长解读，并保留结构化诊断条目和追问入口。

请求：

```json
{
  "chart_id": "chart_xxx",
  "map_type": "wealth",
  "depth": "deep"
}
```

`map_type` 可选：

- `body`
- `wealth`
- `talent`
- `relationship`
- `mission`
- `professional`

响应重点字段：

```json
{
  "product_version": "0.5.0",
  "map_type": "wealth",
  "title": "财富地图",
  "description": "...",
  "overview": "基于整张盘生成的独立长解读",
  "generation_mode": "llm",
  "professional_facts": ["类型：纯生产者"],
  "sections": [
    {
      "key": "wealth-core",
      "title": "财富从哪里来",
      "items": [
        {
          "key": "wealth.02-14-main-track",
          "title": "财富来源：方向感加资源配置",
          "diagnosis_depth": "deep",
          "chart_basis": ["通道：02-14"],
          "professional_basis": "...",
          "user_language": "...",
          "life_scenes": [],
          "embodied_expression": [],
          "blind_spots": [],
          "stuck_patterns": [],
          "stuck_causes": [],
          "common_blocks": [],
          "practices": [],
          "followup_questions": []
        }
      ]
    }
  ],
  "prompt_pack": {},
  "retrieved_knowledge": [],
  "sources": [],
  "suggested_questions": []
}
```

说明：

- 地图条目必须能追溯到真实图表事实：类型、策略、权威、中心、通道、闸门或行星激活。
- `overview` 必须是给用户看的全盘综合解读，不得包含提示词、模型要求、思考过程或开发者语言。
- V0.5 延续 `diagnosis_depth`：`deep` 输出完整特质诊断层；`standard` 输出简版盲区和卡住状态；`trace` 只做事实核验和防误读。
- `deep` 条目必须返回 `embodied_expression`、`blind_spots`、`stuck_patterns`、`stuck_causes`，并且 `stuck_causes` 同时说明盘面机制和现实场景。
- `retrieved_knowledge` 来自 `references/research-corpus/v0.3/knowledge_atoms.json`。
- `sources` 来自 `references/research-corpus/v0.3/sources.json`，只暴露来源元信息，不复制版权正文。

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
    "model": "deepseek-chat",
    "base_url": "https://api.deepseek.com"
  },
  "claude": {
    "configured": false,
    "model": "claude-opus-4-8",
    "base_url": "https://api.anthropic.com"
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
- `deep_synthesis` 是 Web/App 上层报告包装字段，包含 `headline`、`thesis`、`structure_formula`、`research_method_notes`、`non_genericity_checks`、`suggested_experiments` 和 `research_sources`。
- Web/App 新增字段只作为上层产品包装，不改变底层 chart 和 LLM package 字段语义。
