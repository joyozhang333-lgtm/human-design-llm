#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.empirical_trials import build_holdout_forced_choice_trials


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build blinded holdout forced-choice trials from a manifest.")
    parser.add_argument(
        "--manifest",
        default=str(ROOT / "data" / "empirical" / "public_figure_manifest.jsonl"),
    )
    parser.add_argument(
        "--blind-output",
        default=str(ROOT / "data" / "empirical" / "holdout_trials_blinded.jsonl"),
    )
    parser.add_argument(
        "--answer-key-output",
        default=str(ROOT / "data" / "empirical" / "holdout_trials_answer_key.jsonl"),
    )
    parser.add_argument("--max-trials", type=int, default=1000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_holdout_forced_choice_trials(
        args.manifest,
        args.blind_output,
        args.answer_key_output,
        max_trials=args.max_trials,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["trials"] >= 1000 else 1


if __name__ == "__main__":
    raise SystemExit(main())
