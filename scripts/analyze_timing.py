#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.input import InputNormalizationError, normalize_birth_input
from human_design.timing import analyze_timing


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze current transit timing against a natal Human Design chart."
    )
    parser.add_argument("birth_time", help="Natal birth datetime in ISO format.")
    parser.add_argument("transit_time", help="Transit datetime in ISO format.")
    parser.add_argument("--timezone", dest="timezone_name", help="Optional natal IANA timezone.")
    parser.add_argument("--transit-timezone", dest="transit_timezone_name", help="Optional transit IANA timezone.")
    parser.add_argument("--label", default="current", help="Timing label, e.g. current / week / launch-day.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        natal = normalize_birth_input(args.birth_time, timezone_name=args.timezone_name)
        transit = normalize_birth_input(
            args.transit_time,
            timezone_name=args.transit_timezone_name,
        )
    except InputNormalizationError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2

    result = analyze_timing(natal, transit, timing_label=args.label)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
