#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.engine import calculate_chart
from human_design.input import InputNormalizationError, normalize_birth_input
from human_design.reading import generate_reading, render_reading_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a complete Human Design reading."
    )
    parser.add_argument(
        "birth_time",
        help="Birth date/time in ISO format. Example: 1988-10-09T20:30:00+08:00",
    )
    parser.add_argument(
        "--timezone",
        dest="timezone_name",
        help="Optional IANA timezone, e.g. Asia/Shanghai.",
    )
    parser.add_argument(
        "--city",
        help="Optional birth city used to resolve timezone.",
    )
    parser.add_argument(
        "--region",
        help="Optional birth region / state used to resolve timezone.",
    )
    parser.add_argument(
        "--country",
        help="Optional birth country used to resolve timezone.",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        normalized = normalize_birth_input(
            args.birth_time,
            timezone_name=args.timezone_name,
            city=args.city,
            region=args.region,
            country=args.country,
        )
    except InputNormalizationError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2

    chart = calculate_chart(normalized)
    reading = generate_reading(chart)
    if args.format == "json":
        print(json.dumps(reading.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_reading_markdown(reading), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
