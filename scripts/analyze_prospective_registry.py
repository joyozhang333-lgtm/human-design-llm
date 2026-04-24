#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.prediction_registry import analyze_prospective_registry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze locked prospective prediction registry outcomes.")
    parser.add_argument(
        "registry",
        nargs="?",
        default=str(ROOT / "data" / "empirical" / "prospective_prediction_registry.jsonl"),
    )
    parser.add_argument("--format", choices=("json", "text"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = analyze_prospective_registry(args.registry)
    if args.format == "json":
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"prospective-registry: {result.status}")
        print(f"locked={result.locked_predictions} resolved={result.resolved_predictions} scorable={result.scorable_predictions}")
        print(f"accuracy={result.observed_accuracy}")
    return 0 if result.status == "passed-90" else 1


if __name__ == "__main__":
    raise SystemExit(main())
