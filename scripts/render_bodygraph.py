#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.bodygraph import write_bodygraph_svg
from human_design.engine import calculate_chart
from human_design.input import InputNormalizationError, normalize_birth_input


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a Human Design bodygraph SVG.")
    parser.add_argument("birth_time", help="Birth date/time in ISO format.")
    parser.add_argument("--timezone", dest="timezone_name", help="Optional IANA timezone.")
    parser.add_argument("--city", help="Optional birth city.")
    parser.add_argument("--region", help="Optional birth region / state.")
    parser.add_argument("--country", help="Optional birth country.")
    parser.add_argument("--title", default="人类图", help="Chart title.")
    parser.add_argument(
        "--output",
        default=str(ROOT / "outputs" / "bodygraphs" / "bodygraph.svg"),
        help="Output SVG path.",
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
    path = write_bodygraph_svg(chart, args.output, title=args.title)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
