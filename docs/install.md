# Install Guide

更新时间：2026-04-22

## 目标

把这个仓库安装成一个可直接被 Codex 发现和调用的 skill。

## 安装前提

- 本机已有 `~/.codex/`
- 仓库根目录包含：
  - `SKILL.md`
  - `agents/openai.yaml`

## 推荐安装方式

开发期建议用软链接，更新仓库后不需要重复复制。

```bash
cd /Users/zhangzhaoyang/Desktop/禅拍课程/human-design-product
. .venv/bin/activate
python scripts/install_skill.py --mode link --force
```

默认会安装到：

```text
~/.codex/skills/human-design
```

## 复制安装

如果不想保留软链接，可以复制一份：

```bash
python scripts/install_skill.py --mode copy --force
```

## 自定义安装目录

```bash
python scripts/install_skill.py --codex-home /path/to/codex-home --mode link --force
```

## 安装后验证

1. 确认目标目录存在 `SKILL.md`
2. 确认目标目录存在 `agents/openai.yaml`
3. 在 Codex 里用 `$human-design` 或相关触发词调用

## 注意事项

- `link` 模式适合开发；`copy` 模式适合固定快照。
- 如果目标已存在，必须显式传 `--force`。
