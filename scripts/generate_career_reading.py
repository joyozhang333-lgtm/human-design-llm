#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.career import generate_career_report, render_career_report_markdown
from human_design.engine import calculate_chart
from human_design.input import InputNormalizationError, normalize_birth_input


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a deep Human Design career report.")
    parser.add_argument("birth_time", help="Birth date/time in ISO format.")
    parser.add_argument("--timezone", dest="timezone_name", help="Optional IANA timezone.")
    parser.add_argument("--city", help="Optional birth city.")
    parser.add_argument("--region", help="Optional birth region / state.")
    parser.add_argument("--country", help="Optional birth country.")
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
    report = generate_career_report(chart)
    if args.format == "json":
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_career_report_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
