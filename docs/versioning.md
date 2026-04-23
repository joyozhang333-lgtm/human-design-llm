# Versioning Policy

更新时间：2026-04-23

## 当前版本

- `1.4.0`

## 规则

采用语义化版本：

- `MAJOR`：契约级破坏性变更
- `MINOR`：新增能力，但不破坏既有接口
- `PATCH`：修复、文案优化、知识卡精修、评测增强

## 何时升版本

### MAJOR

- `chart / reading / llm package` 稳定字段发生破坏性变化
- skill 安装结构发生不兼容变化

### MINOR

- 新增 runtime adapter
- 新增产品层能力
- 新增知识卡结构但不破坏已有读取方式

### PATCH

- 精修 gate/channel/type/profile 等卡片内容
- 优化 question-aware planner
- 增加测试、smoke、narrative eval
- 修复输入解析或文档问题

## 发布要求

每次发布都要同步：

- `human_design/version.py`
- `CHANGELOG.md`
- 相关安装 / runtime / release 文档
