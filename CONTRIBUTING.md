# Contributing

Contributions in Chinese and English are welcome: chart calculation fixes, BodyGraph rendering, terminology, knowledge cards, interpretation quality, accessibility, tests, API adapters, and documentation.

## Before Opening A Pull Request

```bash
python -m pytest -q
cd web
npm ci
npm run build
```

Keep changes focused and explain the user-facing behavior. Add regression tests for chart facts, rendering, prompts, validators, or API contracts when relevant.

## Accuracy Rules

- Interpretation output must only mention centers, channels, gates, lines, and authorities present in the chart context.
- Do not turn Human Design into medical, psychological, legal, financial, or deterministic fate advice.
- Distinguish engineering tests from scientific evidence. A passing scorecard does not prove personality or destiny accuracy.
- Copyrighted books may be summarized and cited; do not submit long copied passages.

## Privacy And Secrets

Never commit real user names, birth details, conversations, private screenshots, server credentials, database passwords, or API keys. Use synthetic fixtures and `.env.example` placeholders. If a secret appears in a commit, rotate it before requesting review.

## 中文贡献说明

欢迎改进简体中文术语、全盘综合解读、知识卡、排盘与出图、移动端体验和 Agent 适配。提交前请确认文案是用户能理解的语言，不包含提示词、开发者要求或模型思考过程；测试数据必须是虚构样本。
