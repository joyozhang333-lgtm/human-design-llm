from __future__ import annotations

from dataclasses import dataclass
import json
from math import comb, sqrt
from pathlib import Path
from typing import Any

from .schema import JsonMixin


@dataclass(frozen=True)
class ForcedChoiceExperimentResult(JsonMixin):
    experiment_id: str
    experiment_type: str
    status: str
    total_trials: int
    correct_trials: int
    options_per_trial: int
    chance_accuracy: float
    observed_accuracy: float
    wilson_ci_low: float
    wilson_ci_high: float
    exact_p_value: float
    alpha: float
    minimum_sample_size: int
    accuracy_threshold: float
    ci_lower_above_chance: bool
    passed_statistical_threshold: bool
    evidence_status: str


def analyze_forced_choice_experiment(payload: dict[str, Any] | str | Path) -> ForcedChoiceExperimentResult:
    data = _load_payload(payload)
    total_trials, correct_trials = _extract_counts(data)
    options_per_trial = int(data.get("options_per_trial") or _infer_options_per_trial(data))
    if options_per_trial < 2:
        raise ValueError("options_per_trial must be >= 2")
    if total_trials <= 0:
        raise ValueError("experiment must contain at least one trial")
    if correct_trials < 0 or correct_trials > total_trials:
        raise ValueError("correct trial count is outside valid range")

    alpha = float(data.get("alpha", 0.01))
    minimum_sample_size = int(data.get("minimum_sample_size", 120))
    success_threshold = data.get("success_threshold", {})
    chance_accuracy = 1 / options_per_trial
    observed_accuracy = correct_trials / total_trials
    ci_low, ci_high = _wilson_interval(correct_trials, total_trials)
    exact_p_value = _binomial_survival(correct_trials, total_trials, chance_accuracy)
    accuracy_threshold = float(
        success_threshold.get("accuracy", max(chance_accuracy + 0.10, chance_accuracy * 1.5))
    )
    require_ci_lower_above_chance = bool(success_threshold.get("ci_lower_above_chance", True))
    ci_lower_above_chance = ci_low > chance_accuracy
    passed_statistical_threshold = (
        total_trials >= minimum_sample_size
        and observed_accuracy >= accuracy_threshold
        and exact_p_value <= alpha
        and (ci_lower_above_chance or not require_ci_lower_above_chance)
    )
    status = str(data.get("status", "unknown"))
    evidence_status = _evidence_status(status, passed_statistical_threshold)

    return ForcedChoiceExperimentResult(
        experiment_id=str(data.get("id", "unknown")),
        experiment_type=str(data.get("experiment_type", "forced-choice")),
        status=status,
        total_trials=total_trials,
        correct_trials=correct_trials,
        options_per_trial=options_per_trial,
        chance_accuracy=chance_accuracy,
        observed_accuracy=observed_accuracy,
        wilson_ci_low=ci_low,
        wilson_ci_high=ci_high,
        exact_p_value=exact_p_value,
        alpha=alpha,
        minimum_sample_size=minimum_sample_size,
        accuracy_threshold=accuracy_threshold,
        ci_lower_above_chance=ci_lower_above_chance,
        passed_statistical_threshold=passed_statistical_threshold,
        evidence_status=evidence_status,
    )


def _load_payload(payload: dict[str, Any] | str | Path) -> dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    return json.loads(Path(payload).read_text(encoding="utf-8"))


def _extract_counts(data: dict[str, Any]) -> tuple[int, int]:
    trials = data.get("trials")
    if trials:
        total = len(trials)
        correct = sum(1 for trial in trials if trial.get("selected_option_id") == trial.get("correct_option_id"))
        return total, correct
    summary = data.get("summary")
    if summary:
        return int(summary["trials"]), int(summary["correct"])
    raise ValueError("experiment data must include either trials[] or summary")


def _infer_options_per_trial(data: dict[str, Any]) -> int:
    trials = data.get("trials") or []
    option_counts = [len(trial.get("option_ids", ())) for trial in trials if trial.get("option_ids")]
    if not option_counts:
        raise ValueError("options_per_trial is required when raw trials do not include option_ids")
    first = option_counts[0]
    if any(count != first for count in option_counts):
        raise ValueError("all trials must use the same number of options")
    return first


def _wilson_interval(correct: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    proportion = correct / total
    denominator = 1 + z**2 / total
    center = (proportion + z**2 / (2 * total)) / denominator
    margin = z * sqrt((proportion * (1 - proportion) + z**2 / (4 * total)) / total) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def _binomial_survival(k: int, n: int, p: float) -> float:
    probability = 0.0
    for successes in range(k, n + 1):
        probability += comb(n, successes) * (p**successes) * ((1 - p) ** (n - successes))
    return min(1.0, probability)


def _evidence_status(status: str, passed_statistical_threshold: bool) -> str:
    normalized = status.lower()
    if "demo" in normalized or "fixture" in normalized or "format" in normalized:
        return "demo-only-not-evidence"
    if passed_statistical_threshold:
        return "passed-preregistered-threshold"
    return "not-supported-by-current-data"
