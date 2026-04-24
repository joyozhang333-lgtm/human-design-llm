#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.protocol_freeze import freeze_protocol


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Freeze empirical protocol files with SHA-256 hashes.")
    parser.add_argument("--protocol-id", default="human-design-accuracy-v1")
    parser.add_argument(
        "--output",
        default=str(ROOT / "docs" / "protocol-freezes" / "human-design-accuracy-v1.freeze.json"),
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=[
            "docs/empirical-validation-protocol.md",
            "docs/contracts/empirical-trial.md",
        ],
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    freeze = freeze_protocol(args.protocol_id, args.paths, args.output)
    print(json.dumps(freeze.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
