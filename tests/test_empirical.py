from __future__ import annotations

from pathlib import Path

from human_design.empirical import analyze_forced_choice_experiment


ROOT = Path(__file__).parent


def test_analyze_forced_choice_experiment_scores_demo_fixture() -> None:
    result = analyze_forced_choice_experiment(ROOT / "fixtures" / "empirical_forced_choice_demo.json")

    assert result.total_trials == 120
    assert result.correct_trials == 66
    assert result.options_per_trial == 4
    assert result.observed_accuracy == 0.55
    assert result.chance_accuracy == 0.25
    assert result.exact_p_value < 0.01
    assert result.ci_lower_above_chance
    assert result.passed_statistical_threshold
    assert result.evidence_status == "demo-only-not-evidence"


def test_analyze_forced_choice_experiment_rejects_null_result() -> None:
    result = analyze_forced_choice_experiment(
        {
            "id": "null-result",
            "experiment_type": "forced-choice-self-identification",
            "status": "preregistered-pilot",
            "options_per_trial": 4,
            "minimum_sample_size": 120,
            "alpha": 0.01,
            "success_threshold": {"accuracy": 0.45, "ci_lower_above_chance": True},
            "summary": {"trials": 120, "correct": 34},
        }
    )

    assert result.observed_accuracy < result.accuracy_threshold
    assert not result.passed_statistical_threshold
    assert result.evidence_status == "not-supported-by-current-data"
