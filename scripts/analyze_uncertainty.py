#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.input import InputNormalizationError
from human_design.uncertainty import analyze_birth_time_range


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze Human Design uncertainty across a birth time range."
    )
    parser.add_argument(
        "start_birth_time",
        help="Range start in ISO format. Example: 1988-10-09T20:00:00",
    )
    parser.add_argument(
        "end_birth_time",
        help="Range end in ISO format. Example: 1988-10-09T21:00:00",
    )
    parser.add_argument(
        "--timezone",
        dest="timezone_name",
        help="Optional IANA timezone, e.g. Asia/Shanghai.",
    )
    parser.add_argument("--city", help="Optional birth city used to resolve timezone.")
    parser.add_argument("--region", help="Optional birth region / state used to resolve timezone.")
    parser.add_argument("--country", help="Optional birth country used to resolve timezone.")
    parser.add_argument(
        "--interval-minutes",
        type=int,
        default=30,
        help="Sampling interval in minutes.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = analyze_birth_time_range(
            args.start_birth_time,
            args.end_birth_time,
            timezone_name=args.timezone_name,
            city=args.city,
            region=args.region,
            country=args.country,
            interval_minutes=args.interval_minutes,
        )
    except InputNormalizationError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
