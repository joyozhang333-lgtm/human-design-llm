from __future__ import annotations

from pathlib import Path

from human_design.empirical_dataset import deterministic_split, load_manifest
from human_design.prediction_registry import analyze_prospective_registry


ROOT = Path(__file__).parent


def test_public_figure_manifest_contains_1000_plus_holdout_records() -> None:
    records = load_manifest(ROOT.parent / "data" / "empirical" / "public_figure_manifest.jsonl")
    holdout = [record for record in records if record["split"] == "holdout"]

    assert len(records) == 4834
    assert len(holdout) >= 1000
    assert {record["rodden_rating"] for record in records}.issubset({"AA", "A", "B"})
    assert deterministic_split(records[0]["adb_id"]) == records[0]["split"]
    assert all(record["blind_safe"]["strip_identifying_biography"] for record in records)


def test_holdout_trials_keep_answer_key_separate() -> None:
    blind_trials = (ROOT.parent / "data" / "empirical" / "holdout_trials_blinded.jsonl").read_text(
        encoding="utf-8"
    ).splitlines()
    answer_key = (ROOT.parent / "data" / "empirical" / "holdout_trials_answer_key.jsonl").read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(blind_trials) == 1000
    assert len(answer_key) == 1000
    assert all("correct_option_id" not in line for line in blind_trials)
    assert all("correct_option_id" in line for line in answer_key)


def test_prospective_registry_template_is_unresolved_not_success() -> None:
    result = analyze_prospective_registry(
        ROOT.parent / "data" / "empirical" / "prospective_prediction_registry.jsonl"
    )

    assert result.total_predictions == 1
    assert result.status == "unresolved"
    assert result.observed_accuracy is None
