#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.evals import run_empirical_readiness_suite, score_eval_checks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate whether the project is ready for falsifiable empirical validation."
    )
    parser.add_argument(
        "--protocol",
        default=str(ROOT / "docs" / "empirical-validation-protocol.md"),
        help="Path to the empirical validation protocol.",
    )
    parser.add_argument(
        "--contract",
        default=str(ROOT / "docs" / "contracts" / "empirical-trial.md"),
        help="Path to the empirical trial data contract.",
    )
    parser.add_argument(
        "--demo",
        default=str(ROOT / "tests" / "fixtures" / "empirical_forced_choice_demo.json"),
        help="Path to a demo experiment JSON used to verify the statistics pipeline.",
    )
    parser.add_argument("--target", type=int, default=90)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_empirical_readiness_suite(args.protocol, args.contract, args.demo)
    score = score_eval_checks(report)
    passed = report.failed == 0 and score >= args.target
    result = {
        "score": score,
        "target": args.target,
        "passed": passed,
        "truth_claim_status": "not-established-without-real-preregistered-trial-data",
        "report": report.to_dict(),
    }

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"empirical-readiness: score={score}/{args.target}, cases={report.passed}/{report.total}")
        print("truth-claim-status: not-established-without-real-preregistered-trial-data")
        for case in report.results:
            status = "PASS" if case.passed else "FAIL"
            failed_checks = [check.name for check in case.checks if not check.passed]
            suffix = "" if not failed_checks else f" failed={failed_checks}"
            print(f"- {case.case_id}: {status}{suffix}")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
