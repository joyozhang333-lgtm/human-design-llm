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
from human_design.product import build_llm_product


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an LLM-native Human Design product package."
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
        "--focus",
        choices=("overview", "career", "relationship", "decision", "growth"),
        default="overview",
        help="Session focus.",
    )
    parser.add_argument(
        "--question",
        default=None,
        help="Optional user question to attach to the package.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output full package as JSON, or only answer markdown.",
    )
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
    package = build_llm_product(
        chart,
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
