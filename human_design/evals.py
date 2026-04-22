from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .engine import calculate_chart
from .input import normalize_birth_input
from .product import build_llm_product
from .reading import generate_reading

FOCUSES = ("overview", "career", "relationship", "decision", "growth")


@dataclass(frozen=True)
class EvalCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class EvalCaseResult:
    case_id: str
    passed: bool
    checks: tuple[EvalCheck, ...]


@dataclass(frozen=True)
class EvalSuiteResult:
    name: str
    total: int
    passed: int
    failed: int
    results: tuple[EvalCaseResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "results": [
                {
                    "case_id": result.case_id,
                    "passed": result.passed,
                    "checks": [
                        {
                            "name": check.name,
                            "passed": check.passed,
                            "detail": check.detail,
                        }
                        for check in result.checks
                    ],
                }
                for result in self.results
            ],
        }


def run_smoke_suite(fixtures_path: str | Path) -> EvalSuiteResult:
    fixtures = json.loads(Path(fixtures_path).read_text(encoding="utf-8"))
    results: list[EvalCaseResult] = []

    for fixture in fixtures:
        checks: list[EvalCheck] = []
        normalized = normalize_birth_input(**fixture["input"])
        chart = calculate_chart(normalized)
        reading = generate_reading(chart)

        checks.append(
            EvalCheck(
                name="reading-sections",
                passed=len(reading.sections) >= 8,
                detail=f"sections={len(reading.sections)}",
            )
        )

        focus_outputs: dict[str, str] = {}
        for focus in FOCUSES:
            package = build_llm_product(chart, focus=focus)
            focus_outputs[focus] = package.answer_markdown
            checks.append(
                EvalCheck(
                    name=f"product-{focus}",
                    passed=bool(package.answer_markdown.strip())
                    and package.focus == focus
                    and bool(package.context_blocks),
                    detail=f"context_blocks={len(package.context_blocks)}",
                )
            )

        unique_outputs = len(set(focus_outputs.values()))
        checks.append(
            EvalCheck(
                name="focus-diversity",
                passed=unique_outputs >= 4,
                detail=f"unique_outputs={unique_outputs}",
            )
        )

        results.append(
            EvalCaseResult(
                case_id=fixture["id"],
                passed=all(check.passed for check in checks),
                checks=tuple(checks),
            )
        )

    return _suite_from_results("smoke", results)


def run_narrative_eval_suite(cases_path: str | Path) -> EvalSuiteResult:
    cases = json.loads(Path(cases_path).read_text(encoding="utf-8"))
    results: list[EvalCaseResult] = []

    for case in cases:
        normalized = normalize_birth_input(**case["input"])
        chart = calculate_chart(normalized)
        package = build_llm_product(
            chart,
            focus=case["focus"],
            question=case.get("question"),
        )
        text = package.answer_markdown
        checks: list[EvalCheck] = []

        checks.append(
            EvalCheck(
                name="has-focus",
                passed=f"当前聚焦：{case['focus']}" in text,
                detail=case["focus"],
            )
        )

        for pattern in case.get("required_substrings", []):
            checks.append(
                EvalCheck(
                    name=f"required:{pattern}",
                    passed=pattern in text,
                    detail=pattern,
                )
            )

        for pattern in case.get("forbidden_substrings", []):
            checks.append(
                EvalCheck(
                    name=f"forbidden:{pattern}",
                    passed=pattern not in text,
                    detail=pattern,
                )
            )

        for key in case.get("required_block_keys", []):
            checks.append(
                EvalCheck(
                    name=f"block:{key}",
                    passed=any(block.key == key for block in package.context_blocks),
                    detail=key,
                )
            )

        results.append(
            EvalCaseResult(
                case_id=case["id"],
                passed=all(check.passed for check in checks),
                checks=tuple(checks),
            )
        )

    return _suite_from_results("narrative", results)


def _suite_from_results(name: str, results: list[EvalCaseResult]) -> EvalSuiteResult:
    passed = sum(1 for result in results if result.passed)
    total = len(results)
    return EvalSuiteResult(
        name=name,
        total=total,
        passed=passed,
        failed=total - passed,
        results=tuple(results),
    )
