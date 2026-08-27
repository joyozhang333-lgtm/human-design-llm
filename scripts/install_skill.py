#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.installer import (
    SUPPORTED_AGENT_HOSTS,
    SkillInstallError,
    install_agent_skill,
    package_skill_bundle,
    resolve_agent_skill_target,
)

SKILL_SOURCE = ROOT / "skills" / "human-design"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install Human Design into a supported Agent Skill host.")
    parser.add_argument(
        "--target",
        choices=(*SUPPORTED_AGENT_HOSTS, "all"),
        default="codex",
        help="Agent host. Use all to install every host path for the selected scope.",
    )
    parser.add_argument("--scope", choices=("project", "user"), default="project")
    parser.add_argument("--project-dir", default=None, help="Project root for project scope. Defaults to current directory.")
    parser.add_argument("--home-dir", default=None, help="Home override for tests or managed environments.")
    parser.add_argument("--mode", choices=("copy", "link"), default="copy")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--package",
        dest="package_path",
        default=None,
        help="Also create a deterministic ZIP for WorkBuddy local upload.",
    )
    parser.add_argument(
        "--package-only",
        action="store_true",
        help="Create --package without installing into a host directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    targets = SUPPORTED_AGENT_HOSTS if args.target == "all" else (args.target,)
    try:
        if args.package_only and not args.package_path:
            raise SkillInstallError("--package-only 必须与 --package 一起使用。")
        if not args.package_only:
            seen_targets: set[str] = set()
            for host in targets:
                planned_target = str(resolve_agent_skill_target(
                    host,
                    scope=args.scope,
                    project_dir=args.project_dir,
                    home_dir=args.home_dir,
                ))
                if planned_target in seen_targets:
                    print(f"{host}: shared with {planned_target}")
                    continue
                result = install_agent_skill(
                    SKILL_SOURCE,
                    host=host,
                    scope=args.scope,
                    project_dir=args.project_dir,
                    home_dir=args.home_dir,
                    mode=args.mode,
                    force=args.force,
                )
                print(f"{host}: {result.target_dir}")
                seen_targets.add(result.target_dir)
        if args.package_path:
            output = package_skill_bundle(SKILL_SOURCE, args.package_path)
            print(f"workbuddy-package: {output}")
    except SkillInstallError as exc:
        print(f"install error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
