from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import random
from typing import Any

from .empirical_dataset import load_manifest


def build_holdout_forced_choice_trials(
    manifest_path: str | Path,
    blind_trials_path: str | Path,
    answer_key_path: str | Path,
    *,
    seed: str = "human-design-accuracy-v1-holdout",
    options_per_trial: int = 4,
    max_trials: int | None = 1000,
) -> dict[str, Any]:
    records = [record for record in load_manifest(manifest_path) if record["split"] == "holdout"]
    if len(records) < 1000:
        raise ValueError(f"holdout split must contain at least 1000 records, got {len(records)}")
    selected = records[:max_trials] if max_trials else records
    rng = random.Random(seed)
    blind_trials: list[dict[str, Any]] = []
    answer_key: list[dict[str, str]] = []

    for record in selected:
        decoys = _choose_decoys(record, records, rng, options_per_trial - 1)
        option_records = [record, *decoys]
        rng.shuffle(option_records)
        option_ids = [item["sample_id"] for item in option_records]
        trial_id = f"trial-{record['sample_id']}"
        blind_trials.append(
            {
                "trial_id": trial_id,
                "option_ids": option_ids,
                "prompt_profile": _blind_prompt_profile(record),
                "decoy_policy": "same-gender-nearest-birth-year-holdout",
                "seed_hash": sha256(f"{seed}:{trial_id}".encode("utf-8")).hexdigest(),
            }
        )
        answer_key.append({"trial_id": trial_id, "correct_option_id": record["sample_id"]})

    _write_jsonl(blind_trials_path, blind_trials)
    _write_jsonl(answer_key_path, answer_key)
    return {
        "manifest_path": str(manifest_path),
        "blind_trials_path": str(blind_trials_path),
        "answer_key_path": str(answer_key_path),
        "trials": len(blind_trials),
        "options_per_trial": options_per_trial,
        "seed": seed,
    }


def _choose_decoys(
    target: dict[str, Any],
    records: list[dict[str, Any]],
    rng: random.Random,
    count: int,
) -> list[dict[str, Any]]:
    target_year = target["birth"]["year"]
    same_gender = [
        record
        for record in records
        if record["sample_id"] != target["sample_id"] and record["gender"] == target["gender"]
    ]
    candidates = sorted(
        same_gender or [record for record in records if record["sample_id"] != target["sample_id"]],
        key=lambda item: (abs(item["birth"]["year"] - target_year), item["sample_id"]),
    )
    if len(candidates) < count:
        candidates = sorted(
            [record for record in records if record["sample_id"] != target["sample_id"]],
            key=lambda item: (abs(item["birth"]["year"] - target_year), item["sample_id"]),
        )
    nearest_pool = candidates[: max(50, count * 8)]
    if len(nearest_pool) < count:
        raise ValueError(f"not enough decoys for {target['sample_id']}: needed={count} available={len(nearest_pool)}")
    return rng.sample(nearest_pool, count)


def _blind_prompt_profile(record: dict[str, Any]) -> dict[str, Any]:
    labels = record.get("labels", {})
    return {
        "gender": record.get("gender"),
        "birth_year_bucket": _year_bucket(record["birth"]["year"]),
        "target_label_counts": {
            "vocation": len(labels.get("vocation", [])),
            "traits": len(labels.get("traits", [])),
            "life_events": len(labels.get("life_events", [])),
        },
    }


def _year_bucket(year: int) -> str:
    if year <= 0:
        return "unknown"
    return f"{year // 10 * 10}s"


def _write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
