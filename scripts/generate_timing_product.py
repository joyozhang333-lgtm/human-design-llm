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
from human_design.timing_product import build_timing_product


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an LLM-native Human Design timing product package."
    )
    parser.add_argument("birth_time", help="Natal birth datetime in ISO format.")
    parser.add_argument("transit_time", help="Transit datetime in ISO format.")
    parser.add_argument("--timezone", dest="timezone_name", help="Optional natal IANA timezone.")
    parser.add_argument("--transit-timezone", dest="transit_timezone_name", help="Optional transit IANA timezone.")
    parser.add_argument("--label", default="current", help="Timing label.")
    parser.add_argument(
        "--focus",
        choices=("overview", "decision", "timing", "energy", "growth"),
        default="overview",
        help="Timing session focus.",
    )
    parser.add_argument("--question", default=None, help="Optional user question.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Output format.")
    parser.add_argument(
        "--citation-mode",
        choices=("none", "sources"),
        default="none",
        help="Optional citation rendering mode for answer_markdown.",
    )
    parser.add_argument(
        "--depth",
        choices=("brief", "standard", "deep"),
        default="standard",
        help="Answer depth mode.",
    )
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
    package = build_timing_product(
        timing,
        focus=args.focus,
        question=args.question,
        citation_mode=args.citation_mode,
        depth=args.depth,
    )
    if args.format == "markdown":
        print(package.answer_markdown, end="")
    else:
        print(json.dumps(package.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
