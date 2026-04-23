#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.evals import (
    run_relationship_narrative_eval_suite,
    run_relationship_smoke_suite,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run relationship smoke and narrative checks.")
    parser.add_argument(
        "--suite",
        choices=("smoke", "narrative", "all"),
        default="all",
        help="Which relationship suite to run.",
    )
    parser.add_argument(
        "--smoke-fixtures",
        default=str(ROOT / "tests" / "fixtures" / "relationship_cases.json"),
        help="Path to relationship smoke fixture JSON.",
    )
    parser.add_argument(
        "--narrative-fixtures",
        default=str(ROOT / "tests" / "fixtures" / "relationship_narrative_cases.json"),
        help="Path to relationship narrative fixture JSON.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def _suite_to_text(report) -> str:
    lines = [f"{report.name}: {report.passed}/{report.total} passed"]
    for result in report.results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(f"- {result.case_id}: {status}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    reports = []
    if args.suite in ("smoke", "all"):
        reports.append(run_relationship_smoke_suite(args.smoke_fixtures))
    if args.suite in ("narrative", "all"):
        reports.append(run_relationship_narrative_eval_suite(args.narrative_fixtures))

    failed = sum(report.failed for report in reports)
    if args.format == "json":
        print(json.dumps([report.to_dict() for report in reports], ensure_ascii=False, indent=2))
    else:
        print("\n\n".join(_suite_to_text(report) for report in reports))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
