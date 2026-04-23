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
from human_design.timing_reading import generate_timing_reading, render_timing_reading_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Human Design timing reading.")
    parser.add_argument("birth_time", help="Natal birth datetime in ISO format.")
    parser.add_argument("transit_time", help="Transit datetime in ISO format.")
    parser.add_argument("--timezone", dest="timezone_name", help="Optional natal IANA timezone.")
    parser.add_argument("--transit-timezone", dest="transit_timezone_name", help="Optional transit IANA timezone.")
    parser.add_argument("--label", default="current", help="Timing label.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        natal = normalize_birth_input(args.birth_time, timezone_name=args.timezone_name)
        transit = normalize_birth_input(args.transit_time, timezone_name=args.transit_timezone_name)
    except InputNormalizationError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2

    timing = analyze_timing(natal, transit, timing_label=args.label)
    reading = generate_timing_reading(timing)
    if args.format == "json":
        print(json.dumps(reading.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_timing_reading_markdown(reading), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
