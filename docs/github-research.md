# GitHub 开源调研

调研日期：2026-04-22

目标：筛出适合给本仓库复用或参考的人类图开源项目，重点看三类能力：

1. 排盘和计算
2. BodyGraph / SVG 可视化
3. 解释层知识是否可复用

## 结论先行

- 当前最值得优先验证的本地计算基座是 [ppo/pyhd](https://github.com/ppo/pyhd)。
- 当前最完整的规则参考实现是 [CReizner/SharpAstrology.HumanDesign](https://github.com/CReizner/SharpAstrology.HumanDesign)。
- [jdempcy/hdkit](https://github.com/jdempcy/hdkit) 仍然很适合拿来参考 BodyGraph 和旧版数据流，但它已经归档，不适合作为主依赖。
- GitHub 上暂时没有看到成熟、开箱即用、许可证清晰的人类图“解释知识库”仓库，解释层大概率要自己建设。

## 候选仓库

| 仓库 | 语言/栈 | Stars | 许可证 | 最近推送 | 适合拿来做什么 | 判断 |
| --- | --- | ---: | --- | --- | --- | --- |
| [ppo/pyhd](https://github.com/ppo/pyhd) | Python + pyswisseph | 0 | MIT | 2026-01-31 | 本地 Python 计算引擎 | 第一优先验证 |
| [CReizner/SharpAstrology.HumanDesign](https://github.com/CReizner/SharpAstrology.HumanDesign) | C# + SwissEph | 63 | MIT | 2025-02-07 | 完整规则参考、Chart 结构参考 | 强参考，不直接嵌入 |
| [jdempcy/hdkit](https://github.com/jdempcy/hdkit) | JS / Rails / SVG | 159 | MIT | 2026-02-24 | BodyGraph、SVG、旧版工具链参考 | 归档仓库，只参考 |
| [reffan/bodygraph-api-php](https://github.com/reffan/bodygraph-api-php) | PHP | 12 | 未声明 | 2024-11-20 | 图表计算逻辑参考 | 可参考，不建议依赖 |
| [geodetheseeker/human-design-py](https://github.com/geodetheseeker/human-design-py) | Python | 2 | 仓库元数据未识别 | 2026-04-20 | 单文件 Python 原型 | 可读源码，不建议直接接入 |
| [eCarlsson-r/HumanDesign-API](https://github.com/eCarlsson-r/HumanDesign-API) | .NET 10 + SVG + AI | 1 | 仓库元数据未识别 | 2026-03-09 | 全栈后端架构参考 | 可参考架构，不建议依赖 |
| [VasVV/HumanDesignApp](https://github.com/VasVV/HumanDesignApp) | JavaScript | 8 | 未声明 | 2021-07-17 | 老前端 Demo | 不建议作为底座 |

## 逐项备注

### 1. ppo/pyhd

链接：[https://github.com/ppo/pyhd](https://github.com/ppo/pyhd)

优点：

- Python 栈，和本仓库未来最容易对齐
- 明确声明基于 `pyswisseph`
- 不是单文件脚本，已经有 `src/pyhd` 包结构
- README 明确提到 Personality / Design 两套 imprint、88° solar arc、完整 BodyGraph 计算
- MIT 许可证明确

风险：

- Star 很少，社区验证还不强
- 需要自己实测和线上计算器的对齐程度

结论：

- 最值得先做 PoC 的本地计算基座

### 2. CReizner/SharpAstrology.HumanDesign

链接：[https://github.com/CReizner/SharpAstrology.HumanDesign](https://github.com/CReizner/SharpAstrology.HumanDesign)

优点：

- 功能覆盖很完整：type、profile、authority、channels、gates、cross、variables、transit、composite
- README 清楚说明了依赖和用法
- 作为规则实现参考价值很高

风险：

- 主栈是 C#，并且依赖 `SharpAstrology.SwissEph`
- 适合拿来对照规则，不适合直接并入当前 Python 优先路线

结论：

- 作为规则和数据结构参考，优先级很高

### 3. jdempcy/hdkit

链接：[https://github.com/jdempcy/hdkit](https://github.com/jdempcy/hdkit)

优点：

- 历史最久，社区认知度最高
- 明确包含 bodygraph、planetary position、PDF、SVG、sample apps
- 很适合参考“人类图产品怎么拆模块”

风险：

- 仓库已归档
- 技术栈较旧，包含 Rails/React/Node 多套样例，直接接入成本高

结论：

- 适合参考 SVG / BodyGraph / sample app 结构，不适合作为主基座

### 4. geodetheseeker/human-design-py

链接：[https://github.com/geodetheseeker/human-design-py](https://github.com/geodetheseeker/human-design-py)

优点：

- Python 原型直接，便于快速读懂
- README 明确写了 gates、centers、correct design date、accuracy 对照
- 还额外接了地点到时区换算

风险：

- 当前更像单文件原型
- GitHub 仓库元数据没有识别到许可证，虽然 README 写了 MIT，但复用前必须核实

结论：

- 可以读源码，但暂不作为主依赖

### 5. eCarlsson-r/HumanDesign-API

链接：[https://github.com/eCarlsson-r/HumanDesign-API](https://github.com/eCarlsson-r/HumanDesign-API)

优点：

- 方向完整：计算、SVG、AI 解读、地理与时区、数据库
- 架构表达清楚，适合参考“产品化后端怎么分层”

风险：

- 仓库很新，社区验证很弱
- GitHub 仓库元数据没有识别到许可证，不能直接默认可复用
- 强绑定 .NET 后端，不适合现在的轻量 skill 起步阶段

结论：

- 可参考架构，不建议当前直接接入

## 当前技术路线建议

### 计算层

- 先以 `ppo/pyhd` 为第一验证对象
- 再用 `SharpAstrology.HumanDesign` 对照关键规则和边界情况

### 解释层

- 自建 `references/` 知识卡
- 先覆盖：类型、策略、权威、人生角色、中心、通道、闸门
- 不依赖 GitHub 上零散的解释文案，避免版权和质量不稳定问题

### 产品层

- 先做本地 skill + 脚本
- 等 chart 数据结构稳定后，再决定是否要扩成 API 或前端可视化

## 当前未发现的东西

- 没找到成熟、可直接复用的人类图解释知识库仓库
- 没找到明显领先、社区共识很强的 Python 全功能开源项目
- 没看到一个同时满足“活跃 + 许可证清晰 + 解释层完整 + 可直接嵌入”的现成底座
