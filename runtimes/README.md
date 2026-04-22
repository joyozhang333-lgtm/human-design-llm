# Runtimes

这个目录放给不同 LLM runtime 使用的适配提示。

当前已提供：

- `codex/SYSTEM_PROMPT.md`
- `hermes/SYSTEM_PROMPT.md`
- `openclaw/SYSTEM_PROMPT.md`

目标不是重复知识库，而是把本仓库的结构化 chart / reading / product package 接到具体 runtime 的回答行为上。

## 当前约定

所有 runtime adapter 都应该基于同一份 `LLMProductPackage` 工作，优先消费：

1. `system_prompt`
2. `assistant_instructions`
3. `question-lens`
4. `focus-highlights`
5. `reading.sections`

## 最小接入方式

如果 runtime 允许自定义 system prompt，可以直接把对应 `SYSTEM_PROMPT.md` 的内容作为运行时提示，再把产品包 JSON 作为上下文喂给模型。
