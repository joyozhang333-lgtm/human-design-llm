from __future__ import annotations

from pathlib import Path

from human_design.evals import (
    run_narrative_eval_suite,
    run_relationship_narrative_eval_suite,
    run_relationship_smoke_suite,
    run_smoke_suite,
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
