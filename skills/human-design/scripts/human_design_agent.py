#!/usr/bin/env python3

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys


# A cloned repository should work before editable installation. Installed skill
# copies still require the Python package, which keeps the bundle small.
for parent in Path(__file__).resolve().parents:
    if (parent / "human_design" / "__init__.py").is_file():
        sys.path.insert(0, str(parent))
        break


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local Human Design Agent Skill adapter.")
    parser.add_argument("command", choices=("chart", "report", "context"))
    parser.add_argument("birth_time", help="ISO local birth datetime, with offset when available.")
    parser.add_argument("--timezone", dest="timezone_name", default=None, help="IANA timezone, e.g. Asia/Shanghai.")
    parser.add_argument("--city", default=None)
    parser.add_argument("--region", default=None)
    parser.add_argument("--country", default=None)
    parser.add_argument(
        "--allow-location-lookup",
        action="store_true",
        help="Consent to external geocoding/timezone lookup when place is provided without --timezone.",
    )
    parser.add_argument(
        "--map-type",
        choices=("body", "channels", "wealth", "talent", "relationship", "mission", "professional"),
        default="talent",
    )
    parser.add_argument(
        "--focus",
        choices=("overview", "talent", "career", "relationship", "decision", "growth"),
        default="overview",
    )
    parser.add_argument("--question", default=None)
    parser.add_argument("--depth", choices=("brief", "standard", "deep"), default="deep")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", default=None, help="Optional local output file. Defaults to stdout.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        parsed_birth_time = datetime.fromisoformat(args.birth_time.replace("Z", "+00:00"))
    except ValueError:
        print("input error: birth_time must be a valid ISO datetime.", file=sys.stderr)
        return 2
    has_offset = parsed_birth_time.utcoffset() is not None
    has_place = any((args.city, args.region, args.country))
    if not has_offset and not args.timezone_name and not has_place:
        print(
            "input error: provide an explicit UTC offset, --timezone, or a birth place.",
            file=sys.stderr,
        )
        return 2
    if not has_offset and not args.timezone_name and has_place and not args.allow_location_lookup:
        print(
            "input error: place-only timezone resolution contacts external services; pass "
            "--allow-location-lookup after consent, or provide --timezone.",
            file=sys.stderr,
        )
        return 2
    try:
        from human_design.engine import calculate_chart
        from human_design.input import InputNormalizationError, normalize_birth_input
        from human_design.interpretation_maps import build_interpretation_map
        from human_design.product import build_llm_product
    except ModuleNotFoundError:
        print(
            "human-design-llm is not installed. Install the repository in a virtual environment first.",
            file=sys.stderr,
        )
        return 3

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
    if args.command == "chart":
        payload = chart.to_dict()
        rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    elif args.command == "report":
        payload = build_interpretation_map(chart, map_type=args.map_type, depth=args.depth).to_dict()
        rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    else:
        package = build_llm_product(
            chart,
            focus=args.focus,
            question=args.question,
            depth=args.depth,
        )
        rendered = package.answer_markdown if args.format == "markdown" else json.dumps(package.to_dict(), ensure_ascii=False, indent=2)

    if args.output:
        output = Path(args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + ("" if rendered.endswith("\n") else "\n"), encoding="utf-8")
        print(str(output))
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
