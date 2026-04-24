#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.empirical import analyze_forced_choice_experiment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze blinded forced-choice experiment data for Human Design claims."
    )
    parser.add_argument("experiment_json", help="Path to an empirical experiment JSON file.")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = analyze_forced_choice_experiment(args.experiment_json)
    if args.format == "json":
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"experiment: {result.experiment_id}")
        print(f"status: {result.evidence_status}")
        print(
            f"accuracy: {result.correct_trials}/{result.total_trials} "
            f"({result.observed_accuracy:.3f}, chance={result.chance_accuracy:.3f})"
        )
        print(f"95% Wilson CI: [{result.wilson_ci_low:.3f}, {result.wilson_ci_high:.3f}]")
        print(f"exact one-sided binomial p-value: {result.exact_p_value:.6g}")
        print(f"passed threshold: {result.passed_statistical_threshold}")
    return 0 if result.passed_statistical_threshold else 1


if __name__ == "__main__":
    raise SystemExit(main())
