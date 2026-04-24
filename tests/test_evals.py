from __future__ import annotations

from pathlib import Path

from human_design.evals import (
    run_narrative_eval_suite,
    run_empirical_readiness_suite,
    run_public_figure_accuracy_suite,
    run_relationship_narrative_eval_suite,
    run_relationship_smoke_suite,
    run_smoke_suite,
    run_timing_narrative_eval_suite,
    run_timing_smoke_suite,
    score_eval_checks,
)


ROOT = Path(__file__).parent


def test_run_smoke_suite_passes_fixture_set() -> None:
    report = run_smoke_suite(ROOT / "fixtures" / "chart_cases.json")

    assert report.failed == 0
    assert report.total == 5
    assert report.passed == 5
    first_result = report.results[0]
    assert any(check.name == "reading-source-coverage" for check in first_result.checks)
    assert any(check.name.endswith("highlight-sources") for check in first_result.checks)
    assert any(check.name.endswith("answer-citation-integrity") for check in first_result.checks)
    assert any(check.name.endswith("answer-markdown-citation-render") for check in first_result.checks)


def test_run_narrative_eval_suite_passes_case_set() -> None:
    report = run_narrative_eval_suite(ROOT / "fixtures" / "narrative_cases.json")

    assert report.failed == 0
    assert report.total == 5
    assert report.passed == 5
    first_result = report.results[0]
    assert any(check.name == "source-block:focus-highlights" for check in first_result.checks)
    assert any(check.name == "source-kinds:channels" for check in first_result.checks)
    assert any(check.name == "citation-mode" and check.detail == "sources" for check in first_result.checks)
    assert any(check.name == "answer-citation:channels" for check in first_result.checks)


def test_run_relationship_smoke_suite_passes_fixture_set() -> None:
    report = run_relationship_smoke_suite(ROOT / "fixtures" / "relationship_cases.json")

    assert report.failed == 0
    assert report.total == 3
    assert report.passed == 3
    first_result = report.results[0]
    assert any(check.name == "relationship-reading-source-coverage" for check in first_result.checks)
    assert any(check.name.endswith("highlight-sources") for check in first_result.checks)
    assert any(check.name.endswith("answer-citation-integrity") for check in first_result.checks)


def test_run_relationship_narrative_eval_suite_passes_case_set() -> None:
    report = run_relationship_narrative_eval_suite(
        ROOT / "fixtures" / "relationship_narrative_cases.json"
    )

    assert report.failed == 0
    assert report.total == 3
    assert report.passed == 3
    first_result = report.results[0]
    assert any(check.name == "source-block:friction" for check in first_result.checks)
    assert any(check.name == "source-kinds:relationship-practice" for check in first_result.checks)
    assert any(check.name == "citation-mode" and check.detail == "sources" for check in first_result.checks)
    assert any(check.name == "answer-citation:focus-highlights" for check in first_result.checks)


def test_run_timing_smoke_suite_passes_fixture_set() -> None:
    report = run_timing_smoke_suite(ROOT / "fixtures" / "timing_cases.json")

    assert report.failed == 0
    assert report.total == 3
    assert report.passed == 3
    first_result = report.results[0]
    assert any(check.name == "timing-reading-source-coverage" for check in first_result.checks)
    assert any(check.name.endswith("highlight-sources") for check in first_result.checks)
    assert any(check.name.endswith("answer-citation-integrity") for check in first_result.checks)


def test_run_timing_narrative_eval_suite_passes_case_set() -> None:
    report = run_timing_narrative_eval_suite(ROOT / "fixtures" / "timing_narrative_cases.json")

    assert report.failed == 0
    assert report.total == 3
    assert report.passed == 3
    first_result = report.results[0]
    assert any(check.name == "source-block:pressure-points" for check in first_result.checks)
    assert any(check.name == "source-kinds:decision-window" for check in first_result.checks)
    assert any(check.name == "citation-mode" and check.detail == "sources" for check in first_result.checks)
    assert any(check.name == "answer-citation:decision-window" for check in first_result.checks)


def test_run_public_figure_accuracy_suite_scores_above_90() -> None:
    report = run_public_figure_accuracy_suite(ROOT / "fixtures" / "public_figures.json")

    assert report.failed == 0
    assert report.total == 11
    assert report.passed == 11
    assert score_eval_checks(report) >= 90
    first_public_result = report.results[1]
    assert any(check.name == "utc-conversion" for check in first_public_result.checks)
    assert any(check.name == "career-no-invented-channels" for check in first_public_result.checks)
    assert any(check.name == "bodygraph-svg-render" for check in first_public_result.checks)


def test_run_empirical_readiness_suite_scores_above_90() -> None:
    report = run_empirical_readiness_suite(
        ROOT.parent / "docs" / "empirical-validation-protocol.md",
        ROOT.parent / "docs" / "contracts" / "empirical-trial.md",
        ROOT / "fixtures" / "empirical_forced_choice_demo.json",
    )

    assert report.failed == 0
    assert report.total == 1
    assert report.passed == 1
    assert score_eval_checks(report) >= 90
    checks = report.results[0].checks
    assert any(check.name == "protocol-scientific-controls" for check in checks)
    assert any(check.name == "demo-not-misrepresented-as-proof" for check in checks)
    assert any(check.name == "truth-claim-discipline" for check in checks)
