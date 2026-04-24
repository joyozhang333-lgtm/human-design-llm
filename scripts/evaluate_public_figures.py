#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.evals import run_public_figure_accuracy_suite, score_eval_checks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run public-figure accuracy checks against Astro-Databank fixtures."
    )
    parser.add_argument(
        "--fixtures",
        default=str(ROOT / "tests" / "fixtures" / "public_figures.json"),
        help="Path to public figure fixture JSON.",
    )
    parser.add_argument(
        "--target",
        type=int,
        default=90,
        help="Minimum check-level score required to pass.",
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
    report = run_public_figure_accuracy_suite(args.fixtures)
    score = score_eval_checks(report)
    passed = report.failed == 0 and score >= args.target
    result = {
        "score": score,
        "target": args.target,
        "passed": passed,
        "report": report.to_dict(),
    }

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"public-figure-accuracy: score={score}/{args.target}, cases={report.passed}/{report.total}")
        for case in report.results:
            status = "PASS" if case.passed else "FAIL"
            failed_checks = [check.name for check in case.checks if not check.passed]
            suffix = "" if not failed_checks else f" failed={failed_checks}"
            print(f"- {case.case_id}: {status}{suffix}")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
