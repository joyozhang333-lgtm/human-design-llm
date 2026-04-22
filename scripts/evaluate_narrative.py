#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.evals import run_narrative_eval_suite


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run narrative quality checks against focus/question cases."
    )
    parser.add_argument(
        "--cases",
        default=str(ROOT / "tests" / "fixtures" / "narrative_cases.json"),
        help="Path to narrative eval cases JSON.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_narrative_eval_suite(args.cases)
    if args.format == "json":
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"narrative-eval: {report.passed}/{report.total} passed")
        for result in report.results:
            status = "PASS" if result.passed else "FAIL"
            print(f"- {result.case_id}: {status}")
    return 0 if report.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
