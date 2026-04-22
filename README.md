# human-design-product

独立的人类图产品工作目录。这个仓库只服务于人类图相关能力，不复用也不混入 `mayan-kin` 的代码、目录或 Git 历史。

当前定位不是 web 应用，而是 **LLM 原生产品**：把排盘、知识、解读和会话协议包装成可直接给模型消费的产品层。

当前阶段先做五件事：

1. 选定一个可控的人类图计算底座
2. 搭建适合 Codex skill 的解释层结构
3. 定义统一的 chart 数据结构和本地排盘入口
4. 生成完整的人类图解读成稿
5. 生成给 LLM 直接消费的产品包

## 当前判断

- 计算引擎优先看 Python 方案，便于后续把排盘和 skill 集成在同一个仓库里
- 解读知识库大概率需要我们自己建设，因为 GitHub 上暂时没看到成熟、可直接复用的人类图解释数据仓库
- 产品路线拆成三层：`calculation engine`、`reading layer`、`llm product layer`
- 第一版计算底座已接到 `ppo/pyhd`
- 当前上游 `pyhd` 在 Python 3.11 下需要一个 runtime 兼容补丁，而且它自己的 `Chart.to_model()` 导出当前主线是坏的；本仓库已经绕开这两个问题，直接输出自己的统一 schema

## 仓库结构

```text
human-design-product/
├── SKILL.md
├── docs/
│   ├── contracts/
│   ├── github-research.md
│   ├── execution-plan.md
│   └── roadmap.md
├── human_design/
│   ├── engine.py
│   ├── knowledge.py
│   ├── product.py
│   ├── pyhd_adapter.py
│   ├── reading.py
│   └── schema.py
├── requirements.txt
├── requirements-dev.txt
├── scripts/
│   ├── calculate_chart.py
│   ├── generate_llm_product.py
│   └── generate_reading.py
├── runtimes/
│   ├── README.md
│   └── hermes/SYSTEM_PROMPT.md
└── tests/
    ├── test_engine.py
    ├── test_product.py
    └── test_reading.py
├── references/
```

## 本地使用

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/calculate_chart.py '1988-10-09T20:30:00+08:00'
python scripts/calculate_chart.py '1988-10-09T20:30:00' --timezone Asia/Shanghai
python scripts/calculate_chart.py '1988-10-09T20:30:00' --city Shanghai --country China
python scripts/generate_reading.py '1988-10-09T20:30:00+08:00'
python scripts/generate_llm_product.py '1988-10-09T20:30:00+08:00' --focus career --question '我在工作里最该怎么用这张图？'
```

输入支持四种方式：

- 带显式 UTC offset 的 ISO 时间
- 不带 offset，但显式传 `--timezone`
- 不带 offset，但传 `--city` + `--country`（可选 `--region`）
- 什么都不补时，默认按 UTC 处理，并在结果里带精度 warning

## 当前输出

第一版统一 chart schema 已包含：

- 摘要字段：类型、策略、权威、Profile、Definition、Signature、Not-Self Theme、Incarnation Cross
- Variables：orientation、determination、cognition、environment、perspective、motivation、sense
- 结构字段：definitions、centers、channels、activated_gates
- 原始激活：personality/design 两套 planetary activations

输出目标是“JSON 友好、可复用、与上游内部实现解耦”，方便后续同时服务脚本、skill、API 和解释模板。

`chart.input` 现在会保留：

- `raw_birth_time`
- `birth_datetime_local`
- `timezone_name`
- `source_precision`
- `warnings`
- `location`

## 当前 LLM 产品输出

除了 chart schema 和阅读对象，现在这个仓库还会生成一层 LLM 产品包，包含：

- `system_prompt`
- `assistant_instructions`
- `focus-aware context_blocks`
- `answer_markdown`
- `suggested_followups`
- 完整 `reading`

这层的目标是：让任何 LLM runtime 不需要再现场拼 prompt，而是直接消费本仓库产出的产品包。

## 当前知识库状态

`references/` 已经开始承载运行时知识，而不再只是预留目录。当前已经落地：

- `types / authorities / profiles / centers / definitions`
- `64 gates` draft 覆盖
- `36 channels` draft 覆盖

`reading.py` 和 `product.py` 现在会优先读取这些引用卡；`knowledge.py` 中的硬编码 guide 仍作为 fallback 存在。

## 当前完整产品能力

现在这个 repo 已经具备一条完整本地链路：

1. 输入出生时间
2. 计算 BodyGraph
3. 生成统一 chart schema
4. 输出完整解读
5. 输出 LLM 会话产品包

`generate_reading.py` 默认输出 Markdown 成稿，也支持 `--format json` 输出完整结构化阅读对象。
`generate_llm_product.py` 默认输出完整 JSON 产品包，也支持 `--format markdown` 只输出最终回答成稿。

## 下一步

1. 细化 64 闸门与 36 通道的专属知识卡
2. 继续扩充 fixtures 和线上计算器一致性验证
3. 细化不同 runtime 的 prompt adapter
4. 在 skill / API / 其他 LLM runtime 中消费这套 chart + reading + product package

详细版本路线见 [docs/roadmap.md](/Users/zhangzhaoyang/Desktop/禅拍课程/human-design-product/docs/roadmap.md)。
详细开发、评审、提交节奏见 [docs/execution-plan.md](/Users/zhangzhaoyang/Desktop/禅拍课程/human-design-product/docs/execution-plan.md)。
结构契约见：

- [docs/contracts/chart.md](/Users/zhangzhaoyang/Desktop/禅拍课程/human-design-product/docs/contracts/chart.md)
- [docs/contracts/reading.md](/Users/zhangzhaoyang/Desktop/禅拍课程/human-design-product/docs/contracts/reading.md)
- [docs/contracts/llm-package.md](/Users/zhangzhaoyang/Desktop/禅拍课程/human-design-product/docs/contracts/llm-package.md)
