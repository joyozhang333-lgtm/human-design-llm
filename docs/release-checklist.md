# Release Checklist

## 发布前

- 检查 `git status --short --branch`，确认只包含本次发布改动。
- 运行 `python -m pytest -q`、前端 TypeScript 检查与生产构建。
- 用 npm 官方 registry 完成生产依赖审计。
- 运行多盘面内容审计，覆盖反映者、无通道和九个中心全定义等边界。
- 在桌面端与移动端完成 BodyGraph、六项核心配置、通道、五份主题报告和咨询对话验收。
- 确认主页不展示已定义中心、开放中心或闸门目录，用户可见版本与 `/api/product/config` 一致。
- 确认未明确同意时不调用 DeepSeek，且远程上下文不包含昵称、出生日期、出生时间和出生地。
- 运行仓库密钥与个人资料扫描；公开样例只使用匿名合成数据。
- 验证 Codex、Claude Code、DeepSeek Harness、Hugging Face / OpenClaw 和 WorkBuddy 的发现路径与执行入口。
- 构建 Python wheel 和确定性 WorkBuddy ZIP，确认包内无 `.env`、密钥、缓存和个人出生资料。
- 完成独立 review，修复所有 P0/P1 问题，并在 PR 中记录验证结果。

## GitHub 发布

- 更新 `CHANGELOG.md`、`human_design/version.py`、`pyproject.toml`、`web/package.json` 和前端公开版本。
- 提交功能分支、创建 PR，等待 backend、frontend 和 agent-skill CI 通过后合并。
- 在合并提交上创建 `v*` 标签，确认 GitHub Release 含 wheel、WorkBuddy ZIP 和 `SHA256SUMS`。

## 生产上线

- 上传后先比较本地与远端 SHA-256，一致后再解压。
- 发布到新的版本目录，保留现有 `.env`，通过符号链接原子切换。
- 重启后端服务，验证 Nginx 配置与 HTTPS。
- 验证 `/api/health`、`/api/product/config`、匿名排盘、主报告、六份即时报告和 DeepSeek 同意/不同意两条路径。
- 在正式域名上复核 V0.7、BodyGraph 首屏、连续报告、独立咨询页和无顶层中心/闸门目录。
