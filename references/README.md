# Reference Cards

v0.6 开始把知识从 `human_design/knowledge.py` 拆到 `references/`。

当前约定：

- `references/index.json` 是索引入口
- `references/gates/*.md` 存 gate 卡
- `references/channels/*.md` 存 channel 卡
- 未来再补 `types / authorities / profiles / centers`

Markdown 卡片格式：

```md
# 57 The Gentle

## 核心主题
一段 1-3 句总结。

## 礼物
- ...
- ...

## 失衡表现
- ...
- ...

## Career
一段。

## Relationship
一段。

## Decision
一段。

## Growth
一段。
```

要求：

1. 不要加 YAML front matter。
2. 标题与 section 名保持稳定，方便程序解析。
3. 中文内容为主，英文名只做辅助识别。
