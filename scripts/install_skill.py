#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.installer import SkillInstallError, install_skill


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install this repository as a Codex skill."
    )
    parser.add_argument(
        "--name",
        default="human-design",
        help="Skill directory name under ~/.codex/skills/.",
    )
    parser.add_argument(
        "--codex-home",
        default=None,
        help="Optional Codex home directory. Defaults to ~/.codex.",
    )
    parser.add_argument(
        "--mode",
        choices=("link", "copy"),
        default="link",
        help="Install mode. `link` is recommended during development.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace the existing installed skill if present.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = install_skill(
            ROOT,
            skill_name=args.name,
            codex_home=args.codex_home,
            mode=args.mode,
            force=args.force,
        )
    except SkillInstallError as exc:
        print(f"install error: {exc}", file=sys.stderr)
        return 2

    print(f"installed {result.skill_name}")
    print(f"mode: {result.mode}")
    print(f"target: {result.target_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
