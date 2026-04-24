#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.evals import (
    run_accuracy_benchmark_readiness_suite,
    run_empirical_readiness_suite,
    run_narrative_eval_suite,
    run_public_figure_accuracy_suite,
    run_relationship_narrative_eval_suite,
    run_relationship_smoke_suite,
    run_smoke_suite,
    run_timing_narrative_eval_suite,
    run_timing_smoke_suite,
    score_eval_checks,
)
from human_design.engine import calculate_chart
from human_design.input import normalize_birth_time_range
from human_design.input import normalize_birth_input
from human_design.product import build_llm_product
from human_design.relationship import compare_relationship
from human_design.relationship_product import build_relationship_product
from human_design.timing import analyze_timing
from human_design.timing_product import build_timing_product
from human_design.uncertainty import analyze_birth_time_range


def _full_or_zero(report, points: int) -> int:
    return points if report.failed == 0 else 0


def _file_points(paths: list[Path], points: int) -> int:
    return points if all(path.exists() for path in paths) else 0


def _build_output_session_checks() -> dict[str, bool]:
    natal = normalize_birth_input("1988-10-09T20:30:00+08:00")
    chart = calculate_chart(natal)
    single_brief = build_llm_product(chart=chart, focus="career", question="我适合怎么工作？", depth="brief")
    single_deep = build_llm_product(chart=chart, focus="career", question="我适合怎么工作？", depth="deep")

    left = normalize_birth_input("1988-10-09T20:30:00+08:00")
    right = normalize_birth_input("1992-01-03T06:15:00-05:00")
    comparison = compare_relationship(left, right, left_label="我", right_label="对方")
    relationship_brief = build_relationship_product(comparison, focus="communication", depth="brief")
    relationship_deep = build_relationship_product(comparison, focus="communication", depth="deep")

    transit = normalize_birth_input("2026-04-23T10:00:00+08:00")
    timing = analyze_timing(natal, transit, timing_label="today")
    timing_brief = build_timing_product(timing, focus="decision", depth="brief")
    timing_deep = build_timing_product(timing, focus="decision", depth="deep")

    return {
        "docs": all(
            path.exists()
            for path in (
                ROOT / "docs" / "contracts" / "output-depth.md",
                ROOT / "docs" / "contracts" / "session.md",
            )
        ),
        "single_depth": (
            single_brief.delivery_depth == "brief"
            and single_deep.delivery_depth == "deep"
            and len(single_deep.answer_markdown) > len(single_brief.answer_markdown)
            and len(single_deep.context_blocks) >= len(single_brief.context_blocks)
        ),
        "relationship_depth": (
            relationship_brief.delivery_depth == "brief"
            and relationship_deep.delivery_depth == "deep"
            and len(relationship_deep.answer_markdown) > len(relationship_brief.answer_markdown)
            and len(relationship_deep.context_blocks) >= len(relationship_brief.context_blocks)
        ),
        "timing_depth": (
            timing_brief.delivery_depth == "brief"
            and timing_deep.delivery_depth == "deep"
            and len(timing_deep.answer_markdown) > len(timing_brief.answer_markdown)
            and len(timing_deep.context_blocks) >= len(timing_brief.context_blocks)
        ),
        "session_state": all(
            package.session_state.headline
            and package.session_state.carry_facts
            and package.session_state.carry_block_keys
            and package.session_state.suggested_next_questions
            for package in (
                single_brief,
                relationship_brief,
                timing_brief,
            )
        ),
    }


def evaluate_v2() -> dict:
    single_smoke = run_smoke_suite(ROOT / "tests" / "fixtures" / "chart_cases.json")
    single_narrative = run_narrative_eval_suite(ROOT / "tests" / "fixtures" / "narrative_cases.json")
    relationship_smoke = run_relationship_smoke_suite(ROOT / "tests" / "fixtures" / "relationship_cases.json")
    relationship_narrative = run_relationship_narrative_eval_suite(
        ROOT / "tests" / "fixtures" / "relationship_narrative_cases.json"
    )
    timing_smoke = run_timing_smoke_suite(ROOT / "tests" / "fixtures" / "timing_cases.json")
    timing_narrative = run_timing_narrative_eval_suite(
        ROOT / "tests" / "fixtures" / "timing_narrative_cases.json"
    )
    public_figure_accuracy = run_public_figure_accuracy_suite(
        ROOT / "tests" / "fixtures" / "public_figures.json"
    )
    public_figure_score = score_eval_checks(public_figure_accuracy)
    empirical_readiness = run_empirical_readiness_suite(
        ROOT / "docs" / "empirical-validation-protocol.md",
        ROOT / "docs" / "contracts" / "empirical-trial.md",
        ROOT / "tests" / "fixtures" / "empirical_forced_choice_demo.json",
    )
    empirical_readiness_score = score_eval_checks(empirical_readiness)
    accuracy_benchmark = run_accuracy_benchmark_readiness_suite(
        ROOT / "data" / "empirical" / "public_figure_manifest.jsonl",
        ROOT / "data" / "empirical" / "holdout_trials_blinded.jsonl",
        ROOT / "data" / "empirical" / "holdout_trials_answer_key.jsonl",
        ROOT / "docs" / "protocol-freezes" / "human-design-accuracy-v1.freeze.json",
        ROOT / "data" / "empirical" / "prospective_prediction_registry.jsonl",
    )
    accuracy_benchmark_score = score_eval_checks(accuracy_benchmark)

    uncertainty = analyze_birth_time_range(
        "1988-10-09T20:00:00",
        "1988-10-09T21:00:00",
        timezone_name="Asia/Shanghai",
        interval_minutes=30,
    )
    uncertainty_score = 10 if uncertainty.sample_count >= 3 and (
        uncertainty.variable_centers or uncertainty.variable_channels or uncertainty.variable_gates
    ) else 0

    single_score = (
        _full_or_zero(single_smoke, 10)
        + _full_or_zero(single_narrative, 10)
        + uncertainty_score
    )
    relationship_score = _full_or_zero(relationship_smoke, 10) + _full_or_zero(relationship_narrative, 10)
    timing_score = _full_or_zero(timing_smoke, 10) + _full_or_zero(timing_narrative, 10)

    output_session_checks = _build_output_session_checks()
    output_session_score = 0
    output_session_score += 3 if output_session_checks["docs"] else 0
    output_session_score += 4 if output_session_checks["single_depth"] else 0
    output_session_score += 3 if output_session_checks["relationship_depth"] else 0
    output_session_score += 3 if output_session_checks["timing_depth"] else 0
    output_session_score += 2 if output_session_checks["session_state"] else 0

    release_score = (
        _file_points(
            [
                ROOT / "docs" / "release-checklist.md",
                ROOT / "docs" / "versioning.md",
                ROOT / "docs" / "install.md",
                ROOT / "docs" / "contracts" / "chart.md",
                ROOT / "docs" / "contracts" / "reading.md",
                ROOT / "docs" / "contracts" / "llm-package.md",
                ROOT / "docs" / "contracts" / "uncertainty.md",
                ROOT / "docs" / "contracts" / "relationship.md",
                ROOT / "docs" / "contracts" / "relationship-reading.md",
                ROOT / "docs" / "contracts" / "relationship-package.md",
                ROOT / "docs" / "contracts" / "timing.md",
                ROOT / "docs" / "contracts" / "timing-reading.md",
                ROOT / "docs" / "contracts" / "timing-package.md",
                ROOT / "docs" / "contracts" / "output-depth.md",
                ROOT / "docs" / "contracts" / "session.md",
            ],
            10,
        )
        + (5 if single_smoke.failed == relationship_smoke.failed == timing_smoke.failed == 0 else 0)
    )

    public_figure_passed = public_figure_accuracy.failed == 0 and public_figure_score >= 90
    empirical_readiness_passed = empirical_readiness.failed == 0 and empirical_readiness_score >= 90
    accuracy_benchmark_passed = accuracy_benchmark.failed == 0 and accuracy_benchmark_score >= 90
    total = single_score + relationship_score + timing_score + output_session_score + release_score
    return {
        "score": total,
        "target": 90,
        "passed": total >= 90 and public_figure_passed and empirical_readiness_passed and accuracy_benchmark_passed,
        "public_figure_accuracy": {
            "score": public_figure_score,
            "target": 90,
            "passed": public_figure_passed,
        },
        "empirical_readiness": {
            "score": empirical_readiness_score,
            "target": 90,
            "passed": empirical_readiness_passed,
            "truth_claim_status": "not-established-without-real-preregistered-trial-data",
        },
        "accuracy_benchmark": {
            "infrastructure_score": accuracy_benchmark_score,
            "target": 90,
            "passed": accuracy_benchmark_passed,
            "actual_accuracy_score": None,
            "actual_accuracy_status": "not-established-until-blind-and-prospective-outcomes-are-scored",
        },
        "breakdown": {
            "single": single_score,
            "relationship": relationship_score,
            "timing": timing_score,
            "output_session": output_session_score,
            "release": release_score,
        },
        "output_session_checks": output_session_checks,
        "reports": {
            "single_smoke": single_smoke.to_dict(),
            "single_narrative": single_narrative.to_dict(),
            "relationship_smoke": relationship_smoke.to_dict(),
            "relationship_narrative": relationship_narrative.to_dict(),
            "timing_smoke": timing_smoke.to_dict(),
            "timing_narrative": timing_narrative.to_dict(),
            "public_figure_accuracy": public_figure_accuracy.to_dict(),
            "empirical_readiness": empirical_readiness.to_dict(),
            "accuracy_benchmark": accuracy_benchmark.to_dict(),
        },
    }


def main() -> int:
    result = evaluate_v2()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
