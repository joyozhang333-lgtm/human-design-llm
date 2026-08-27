# Host Installation

Run these commands from the cloned repository. `--scope project` installs into the current project; `--scope user` installs for the current user.

## Codex

```bash
python scripts/install_skill.py --target codex --scope user --force
```

Targets `~/.codex/skills/human-design` for user scope and `.agents/skills/human-design` for project scope.

## Claude Code

```bash
python scripts/install_skill.py --target claude-code --scope user --force
```

Targets `~/.claude/skills/human-design` or `.claude/skills/human-design`.

## DeepSeek Harness

```bash
python scripts/install_skill.py --target deepseek-harness --scope user --force
```

Targets `~/.dsh/skills/human-design` or `.dsh/skills/human-design`. DeepSeek Harness also discovers project `.agents/skills` bundles.

## Hugging Face / Shared Agent Skills

```bash
python scripts/install_skill.py --target huggingface --scope user --force
```

Targets `~/.agents/skills/human-design` or `.agents/skills/human-design`, the shared Agent Skills location used by multiple coding agents.

## OpenClaw

```bash
python scripts/install_skill.py --target openclaw --scope user --force
```

This uses the shared Agent Skills location so the same audited bundle can be loaded without a separate prompt copy.

## Tencent WorkBuddy / CodeBuddy

WorkBuddy user install:

```bash
python scripts/install_skill.py --target workbuddy --scope user --force
```

This targets `~/.workbuddy/skills/human-design`.

CodeBuddy project install:

```bash
python scripts/install_skill.py --target workbuddy --scope project --force
```

This targets `.codebuddy/skills/human-design`. To use WorkBuddy's local-package upload flow, create the deterministic ZIP without changing either installation:

```bash
python scripts/install_skill.py --target workbuddy --package dist/human-design-workbuddy.zip --package-only
```

Upload the ZIP from WorkBuddy's Skills panel. Review the package before enabling it; the bundle performs local calculation and does not contain credentials.
