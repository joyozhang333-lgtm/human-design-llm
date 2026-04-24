from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .schema import JsonMixin


@dataclass(frozen=True)
class ProspectiveRegistryResult(JsonMixin):
    registry_path: str
    total_predictions: int
    locked_predictions: int
    resolved_predictions: int
    scorable_predictions: int
    correct_predictions: int
    observed_accuracy: float | None
    status: str


def analyze_prospective_registry(path: str | Path) -> ProspectiveRegistryResult:
    registry_path = Path(path)
    rows = [
        json.loads(line)
        for line in registry_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ] if registry_path.exists() else []
    locked = [row for row in rows if row.get("locked_at") and row.get("prediction_hash")]
    resolved = [row for row in locked if row.get("outcome_status") in {"hit", "miss", "void"}]
    scorable = [row for row in resolved if row.get("outcome_status") in {"hit", "miss"}]
    correct = [row for row in scorable if row.get("outcome_status") == "hit"]
    accuracy = (len(correct) / len(scorable)) if scorable else None
    status = "unresolved"
    if scorable:
        status = "passed-90" if accuracy is not None and accuracy >= 0.90 else "below-90"
    return ProspectiveRegistryResult(
        registry_path=str(registry_path),
        total_predictions=len(rows),
        locked_predictions=len(locked),
        resolved_predictions=len(resolved),
        scorable_predictions=len(scorable),
        correct_predictions=len(correct),
        observed_accuracy=accuracy,
        status=status,
    )
