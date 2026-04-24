#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.evals import run_accuracy_benchmark_readiness_suite, score_eval_checks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate 1000+ sample benchmark and holdout readiness.")
    parser.add_argument("--target", type=int, default=90)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--manifest", default=str(ROOT / "data" / "empirical" / "public_figure_manifest.jsonl"))
    parser.add_argument("--blind-trials", default=str(ROOT / "data" / "empirical" / "holdout_trials_blinded.jsonl"))
    parser.add_argument("--answer-key", default=str(ROOT / "data" / "empirical" / "holdout_trials_answer_key.jsonl"))
    parser.add_argument("--freeze", default=str(ROOT / "docs" / "protocol-freezes" / "human-design-accuracy-v1.freeze.json"))
    parser.add_argument("--registry", default=str(ROOT / "data" / "empirical" / "prospective_prediction_registry.jsonl"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_accuracy_benchmark_readiness_suite(
        args.manifest,
        args.blind_trials,
        args.answer_key,
        args.freeze,
        args.registry,
    )
    score = score_eval_checks(report)
    passed = report.failed == 0 and score >= args.target
    result = {
        "infrastructure_score": score,
        "target": args.target,
        "passed": passed,
        "actual_accuracy_score": None,
        "actual_accuracy_status": "not-established-until-blind-and-prospective-outcomes-are-scored",
        "report": report.to_dict(),
    }
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"accuracy-benchmark-readiness: infrastructure_score={score}/{args.target}, cases={report.passed}/{report.total}")
        print("actual_accuracy_status: not-established-until-blind-and-prospective-outcomes-are-scored")
        for case in report.results:
            status = "PASS" if case.passed else "FAIL"
            failed_checks = [check.name for check in case.checks if not check.passed]
            suffix = "" if not failed_checks else f" failed={failed_checks}"
            print(f"- {case.case_id}: {status}{suffix}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
