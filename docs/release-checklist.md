# Release Checklist

更新时间：2026-04-23

## 发布前

- `pytest` 全绿
- `python scripts/smoke_all.py`
- `python scripts/evaluate_narrative.py`
- `python scripts/evaluate_public_figures.py`
- 抽样检查 `career / relationship / decision / growth / overview` 五个 focus
- 抽样检查至少一例 `input.warnings` 场景
- 确认 narrative eval 已覆盖关键 block 的 `sources` 与 source kind 校验
- 抽样运行一例 `python scripts/generate_llm_product.py ... --format markdown --citation-mode sources`
- 确认 answer-level `answer_citations` 与 `citation_mode=sources` 的 markdown 渲染一致
- 确认公开人物校验集达到 `>= 90`，并且没有虚构通道 / 闸门、中文术语回退或 SVG 渲染失败
- `README.md`、`SKILL.md`、`docs/install.md` 已同步当前行为
- `agents/openai.yaml` 存在且描述未过时
- `runtimes/` 至少包含 `codex / hermes / openclaw`

## 发布时

- 更新 `CHANGELOG.md`
- 检查 `human_design/version.py`
- 如需安装验证，执行：
  - `python scripts/install_skill.py --mode link --force`
- 保留最近一次 smoke 和 narrative eval 结果

## 发布后

- 用至少一个真实问题做 smoke：
  - `career`
  - `decision`
  - `relationship`
- 确认 skill 可以被目标环境正常发现
