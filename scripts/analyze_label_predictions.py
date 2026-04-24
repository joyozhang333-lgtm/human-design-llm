#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.empirical import analyze_label_prediction_experiment
from human_design.empirical_dataset import load_manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score locked personality/talent label predictions against holdout labels.")
    parser.add_argument("predictions", help="JSONL file with sample_id and predicted_labels.")
    parser.add_argument("--manifest", default=str(ROOT / "data" / "empirical" / "public_figure_manifest.jsonl"))
    parser.add_argument("--label-group", choices=("vocation", "traits", "life_events"), default="vocation")
    parser.add_argument("--split", default="holdout")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = load_manifest(args.manifest)
    predictions = [
        json.loads(line)
        for line in Path(args.predictions).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    result = analyze_label_prediction_experiment(
        manifest,
        predictions,
        label_group=args.label_group,
        split=args.split,
    )
    if args.format == "json":
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"label-prediction: {result.evidence_status}")
        print(f"group={result.label_group} split={result.split}")
        print(f"scored={result.scored_predictions}/{result.total_predictions} correct={result.correct_predictions}")
        print(f"accuracy={result.observed_accuracy}")
    return 0 if result.passed_accuracy_threshold else 1


if __name__ == "__main__":
    raise SystemExit(main())
