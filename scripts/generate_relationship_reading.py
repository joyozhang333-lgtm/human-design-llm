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
from human_design.relationship import compare_relationship
from human_design.relationship_reading import (
    generate_relationship_reading,
    render_relationship_reading_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Human Design relationship reading.")
    parser.add_argument("left_birth_time", help="Left side birth datetime in ISO format.")
    parser.add_argument("right_birth_time", help="Right side birth datetime in ISO format.")
    parser.add_argument("--left-label", default="A", help="Display label for the left chart.")
    parser.add_argument("--right-label", default="B", help="Display label for the right chart.")
    parser.add_argument("--left-timezone", dest="left_timezone_name", help="Optional left IANA timezone.")
    parser.add_argument("--right-timezone", dest="right_timezone_name", help="Optional right IANA timezone.")
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
        left = normalize_birth_input(args.left_birth_time, timezone_name=args.left_timezone_name)
        right = normalize_birth_input(args.right_birth_time, timezone_name=args.right_timezone_name)
    except InputNormalizationError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2

    comparison = compare_relationship(
        left,
        right,
        left_label=args.left_label,
        right_label=args.right_label,
    )
    reading = generate_relationship_reading(comparison)
    if args.format == "json":
        print(json.dumps(reading.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_relationship_reading_markdown(reading), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
