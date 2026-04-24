from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from .bodygraph import render_bodygraph_svg
from .empirical import analyze_forced_choice_experiment
from .empirical_dataset import load_manifest
from .engine import calculate_chart
from .input import normalize_birth_input
from .prediction_registry import analyze_prospective_registry
from .product import build_llm_product
from .reading import generate_reading
from .relationship import compare_relationship
from .relationship_product import build_relationship_product
from .relationship_reading import generate_relationship_reading
from .schema import AnswerCitation, LLMContextBlock, ReadingSection, SourceReference
from .timing import analyze_timing
from .timing_product import build_timing_product
from .timing_reading import generate_timing_reading

FOCUSES = ("overview", "career", "relationship", "decision", "growth")
RELATIONSHIP_FOCUSES = ("overview", "intimacy", "partnership", "decision", "communication")
TIMING_FOCUSES = ("overview", "decision", "timing", "energy", "growth")
VALID_SOURCE_KINDS = frozenset(
    ("type", "authority", "profile", "definition", "center", "channel", "gate")
)
PUBLIC_FIGURE_ALLOWED_RATINGS = frozenset(("AA", "A"))
PUBLIC_FIGURE_BANNED_TERMS = (
    "骶骨",
    "额骨",
    "阿扎那",
    "阿基那",
    "Energy Projector",
    "Classic Projector",
    "Mental Projector",
    "Ego Projected",
    "Wait for the Invitation",
)
EMPIRICAL_PROTOCOL_REQUIRED_TERMS = (
    "可证伪",
    "盲测",
    "随机",
    "对照",
    "机会基线",
    "p 值",
    "置信区间",
    "不能宣称",
)


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
        sourced_sections = sum(1 for section in reading.sections if section.sources)
        checks.append(
            EvalCheck(
                name="reading-source-coverage",
                passed=sourced_sections >= 6,
                detail=f"sourced_sections={sourced_sections}",
            )
        )
        checks.append(
            EvalCheck(
                name="reading-source-integrity",
                passed=_sources_are_valid(_collect_reading_sources(reading.sections)),
                detail=_source_integrity_detail(_collect_reading_sources(reading.sections)),
            )
        )

        focus_outputs: dict[str, str] = {}
        for focus in FOCUSES:
            package = build_llm_product(chart, focus=focus)
            cited_package = build_llm_product(chart, focus=focus, citation_mode="sources")
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
            checks.append(
                EvalCheck(
                    name=f"product-{focus}-answer-citation-mode-stable",
                    passed=package.answer_citations == cited_package.answer_citations,
                    detail=f"citations={len(package.answer_citations)}",
                )
            )
            checks.append(
                EvalCheck(
                    name=f"product-{focus}-answer-citation-integrity",
                    passed=_answer_citations_are_valid(package.answer_citations),
                    detail=_answer_citation_detail(package.answer_citations),
                )
            )
            checks.append(
                EvalCheck(
                    name=f"product-{focus}-answer-citation-scope-sync",
                    passed=_answer_citations_match_scope(
                        package.answer_citations,
                        package.context_blocks,
                        package.reading.sections,
                    ),
                    detail=_answer_citation_scope_detail(
                        package.answer_citations,
                        package.context_blocks,
                        package.reading.sections,
                    ),
                )
            )
            checks.append(
                EvalCheck(
                    name=f"product-{focus}-answer-markdown-citation-render",
                    passed=_answer_markdown_renders_citations(cited_package),
                    detail=_answer_markdown_citation_detail(cited_package),
                )
            )
            checks.append(
                EvalCheck(
                    name=f"product-{focus}-block-source-integrity",
                    passed=_sources_are_valid(_collect_block_sources(package.context_blocks)),
                    detail=_source_integrity_detail(_collect_block_sources(package.context_blocks)),
                )
            )
            checks.append(
                EvalCheck(
                    name=f"product-{focus}-section-source-sync",
                    passed=_context_sources_match_reading(package.context_blocks, package.reading.sections),
                    detail=_section_sync_detail(package.context_blocks, package.reading.sections),
                )
            )
            if focus != "overview":
                highlight_block = _find_block(package.context_blocks, "focus-highlights")
                checks.append(
                    EvalCheck(
                        name=f"product-{focus}-highlight-sources",
                        passed=highlight_block is not None and bool(highlight_block.sources),
                        detail=f"sources={len(highlight_block.sources) if highlight_block else 0}",
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
            citation_mode=case.get("citation_mode", "none"),
        )
        text = package.answer_markdown
        checks: list[EvalCheck] = []

        checks.append(
            EvalCheck(
                name="citation-mode",
                passed=package.answer_citation_mode == case.get("citation_mode", "none"),
                detail=package.answer_citation_mode,
            )
        )

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

        for key in case.get("required_source_blocks", []):
            block = _find_block(package.context_blocks, key)
            checks.append(
                EvalCheck(
                    name=f"source-block:{key}",
                    passed=block is not None and bool(block.sources),
                    detail=f"sources={len(block.sources) if block else 0}",
                )
            )
            if block is not None and block.sources:
                checks.append(
                    EvalCheck(
                        name=f"source-block-integrity:{key}",
                        passed=_sources_are_valid(block.sources),
                        detail=_source_integrity_detail(block.sources),
                    )
                )

        for key, expected_kinds in case.get("required_block_source_kinds", {}).items():
            block = _find_block(package.context_blocks, key)
            present_kinds = {source.kind for source in block.sources} if block is not None else set()
            missing = [kind for kind in expected_kinds if kind not in present_kinds]
            checks.append(
                EvalCheck(
                    name=f"source-kinds:{key}",
                    passed=not missing,
                    detail=f"present={sorted(present_kinds)} missing={missing}",
                )
            )

        for key in case.get("required_citation_keys", []):
            citation = _find_answer_citation(package.answer_citations, key)
            checks.append(
                EvalCheck(
                    name=f"answer-citation:{key}",
                    passed=citation is not None and bool(citation.sources),
                    detail=f"sources={len(citation.sources) if citation else 0}",
                )
            )
            if citation is not None and case.get("citation_mode", "none") == "sources":
                rendered_line = _render_expected_source_line(citation.sources)
                checks.append(
                    EvalCheck(
                        name=f"answer-citation-render:{key}",
                        passed=rendered_line in text,
                        detail=rendered_line,
                    )
                )

        for key, expected_kinds in case.get("required_citation_source_kinds", {}).items():
            citation = _find_answer_citation(package.answer_citations, key)
            present_kinds = {source.kind for source in citation.sources} if citation is not None else set()
            missing = [kind for kind in expected_kinds if kind not in present_kinds]
            checks.append(
                EvalCheck(
                    name=f"answer-citation-kinds:{key}",
                    passed=not missing,
                    detail=f"present={sorted(present_kinds)} missing={missing}",
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


def run_public_figure_accuracy_suite(fixtures_path: str | Path) -> EvalSuiteResult:
    fixtures = json.loads(Path(fixtures_path).read_text(encoding="utf-8"))
    results: list[EvalCaseResult] = []

    for fixture in fixtures:
        checks: list[EvalCheck] = []
        source = fixture.get("source", {})

        checks.append(
            EvalCheck(
                name="public-source-present",
                passed=bool(source.get("url")) and "astro.com" in source.get("url", ""),
                detail=source.get("url", ""),
            )
        )
        checks.append(
            EvalCheck(
                name="public-source-rating",
                passed=source.get("rodden_rating") in PUBLIC_FIGURE_ALLOWED_RATINGS,
                detail=f"rating={source.get('rodden_rating')}",
            )
        )
        checks.append(
            EvalCheck(
                name="public-birth-data-present",
                passed=bool(source.get("birth_data")) and bool(fixture.get("name")),
                detail=source.get("birth_data", ""),
            )
        )

        normalized = normalize_birth_input(**fixture["input"])
        chart = calculate_chart(normalized)
        reading = generate_reading(chart)
        career_package = build_llm_product(
            chart,
            focus="career",
            question="我最适合怎么工作、赚钱、选方向？",
            citation_mode="sources",
            depth="deep",
        )
        overview_package = build_llm_product(chart, focus="overview", citation_mode="sources")

        checks.append(
            EvalCheck(
                name="utc-conversion",
                passed=normalized.birth_datetime_utc.isoformat() == fixture["expected_utc"],
                detail=f"{normalized.birth_datetime_utc.isoformat()} expected={fixture['expected_utc']}",
            )
        )
        checks.append(
            EvalCheck(
                name="input-precision",
                passed=not chart.input.warnings and chart.input.source_precision == "explicit-offset",
                detail=f"precision={chart.input.source_precision} warnings={chart.input.warnings}",
            )
        )
        checks.append(
            EvalCheck(
                name="chart-core-fields",
                passed=all(
                    (
                        chart.summary.type.code,
                        chart.summary.strategy.code,
                        chart.summary.authority.code,
                        chart.summary.profile.code,
                        chart.summary.definition.code,
                        chart.summary.incarnation_cross.label,
                    )
                ),
                detail=(
                    f"type={chart.summary.type.code} authority={chart.summary.authority.code} "
                    f"profile={chart.summary.profile.code} definition={chart.summary.definition.code}"
                ),
            )
        )
        checks.append(
            EvalCheck(
                name="chart-structure-fields",
                passed=(
                    len(chart.centers) == 9
                    and len(chart.personality.activations) >= 13
                    and len(chart.design.activations) >= 13
                    and bool(chart.activated_gates)
                ),
                detail=(
                    f"centers={len(chart.centers)} personality={len(chart.personality.activations)} "
                    f"design={len(chart.design.activations)} gates={len(chart.activated_gates)}"
                ),
            )
        )
        checks.append(
            EvalCheck(
                name="reading-completeness",
                passed=len(reading.sections) >= 8 and bool(reading.quick_facts) and fixture["name"].split()[0] not in reading.headline,
                detail=f"sections={len(reading.sections)} quick_facts={len(reading.quick_facts)}",
            )
        )

        for focus, package in (("career", career_package), ("overview", overview_package)):
            checks.append(
                EvalCheck(
                    name=f"{focus}-product-package",
                    passed=bool(package.answer_markdown.strip())
                    and bool(package.context_blocks)
                    and bool(package.answer_citations),
                    detail=f"context_blocks={len(package.context_blocks)} citations={len(package.answer_citations)}",
                )
            )
            checks.append(
                EvalCheck(
                    name=f"{focus}-citation-integrity",
                    passed=_answer_citations_are_valid(package.answer_citations)
                    and _answer_citations_match_scope(
                        package.answer_citations,
                        package.context_blocks,
                        package.reading.sections,
                    )
                    and _answer_markdown_renders_citations(package),
                    detail=(
                        f"valid={_answer_citation_detail(package.answer_citations)} "
                        f"scope={_answer_citation_scope_detail(package.answer_citations, package.context_blocks, package.reading.sections)} "
                        f"markdown={_answer_markdown_citation_detail(package)}"
                    ),
                )
            )

        checks.append(
            EvalCheck(
                name="career-no-invented-channels",
                passed=_mentioned_channels(career_package.answer_markdown).issubset(
                    {channel.code for channel in chart.channels}
                ),
                detail=(
                    f"mentioned={sorted(_mentioned_channels(career_package.answer_markdown))} "
                    f"actual={sorted(channel.code for channel in chart.channels)}"
                ),
            )
        )
        checks.append(
            EvalCheck(
                name="career-no-invented-gates",
                passed=_mentioned_gate_numbers(career_package.answer_markdown).issubset(
                    {gate.gate for gate in chart.activated_gates}
                ),
                detail=(
                    f"mentioned={sorted(_mentioned_gate_numbers(career_package.answer_markdown))} "
                    f"actual={sorted(gate.gate for gate in chart.activated_gates)}"
                ),
            )
        )
        checks.append(
            EvalCheck(
                name="zh-term-quality",
                passed=not _banned_terms(career_package.answer_markdown),
                detail=f"banned={_banned_terms(career_package.answer_markdown)}",
            )
        )
        svg = render_bodygraph_svg(chart, title=fixture["name"])
        checks.append(
            EvalCheck(
                name="bodygraph-svg-render",
                passed=svg.startswith("<svg") and fixture["name"] in svg and len(svg) > 1000,
                detail=f"svg_bytes={len(svg)}",
            )
        )

        results.append(
            EvalCaseResult(
                case_id=fixture["id"],
                passed=all(check.passed for check in checks),
                checks=tuple(checks),
            )
        )

    suite_checks: list[EvalCheck] = [
        EvalCheck(
            name="fixture-count",
            passed=len(fixtures) >= 10,
            detail=f"fixtures={len(fixtures)}",
        )
    ]
    if suite_checks:
        results.insert(
            0,
            EvalCaseResult(
                case_id="suite",
                passed=all(check.passed for check in suite_checks),
                checks=tuple(suite_checks),
            ),
        )

    return _suite_from_results("public-figure-accuracy", results)


def score_eval_checks(report: EvalSuiteResult) -> int:
    checks = [check for result in report.results for check in result.checks]
    if not checks:
        return 0
    passed = sum(1 for check in checks if check.passed)
    return round(passed / len(checks) * 100)


def run_empirical_readiness_suite(
    protocol_path: str | Path,
    contract_path: str | Path,
    demo_experiment_path: str | Path,
) -> EvalSuiteResult:
    protocol = Path(protocol_path)
    contract = Path(contract_path)
    demo = Path(demo_experiment_path)
    checks: list[EvalCheck] = []

    protocol_text = protocol.read_text(encoding="utf-8") if protocol.exists() else ""
    contract_text = contract.read_text(encoding="utf-8") if contract.exists() else ""

    checks.append(
        EvalCheck(
            name="protocol-exists",
            passed=protocol.exists() and len(protocol_text) > 2000,
            detail=f"path={protocol} chars={len(protocol_text)}",
        )
    )
    missing_terms = [term for term in EMPIRICAL_PROTOCOL_REQUIRED_TERMS if term not in protocol_text]
    checks.append(
        EvalCheck(
            name="protocol-scientific-controls",
            passed=not missing_terms,
            detail=f"missing={missing_terms}",
        )
    )
    checks.append(
        EvalCheck(
            name="contract-exists",
            passed=contract.exists() and "experiment_type" in contract_text and "summary" in contract_text,
            detail=f"path={contract} chars={len(contract_text)}",
        )
    )

    result = analyze_forced_choice_experiment(demo)
    checks.append(
        EvalCheck(
            name="demo-experiment-analyzes",
            passed=(
                result.total_trials >= 120
                and result.options_per_trial >= 4
                and result.exact_p_value <= result.alpha
                and result.ci_lower_above_chance
            ),
            detail=(
                f"trials={result.total_trials} options={result.options_per_trial} "
                f"accuracy={result.observed_accuracy:.3f} p={result.exact_p_value:.6g}"
            ),
        )
    )
    checks.append(
        EvalCheck(
            name="demo-not-misrepresented-as-proof",
            passed=result.evidence_status == "demo-only-not-evidence",
            detail=f"evidence_status={result.evidence_status}",
        )
    )
    checks.append(
        EvalCheck(
            name="truth-claim-discipline",
            passed=(
                "不能宣称人类图已经被科学证明" in protocol_text
                and "独立复现实验" in protocol_text
            ),
            detail="requires explicit no-proof-without-real-data language",
        )
    )

    return _suite_from_results(
        "empirical-validation-readiness",
        [
            EvalCaseResult(
                case_id="empirical-readiness",
                passed=all(check.passed for check in checks),
                checks=tuple(checks),
            )
        ],
    )


def run_accuracy_benchmark_readiness_suite(
    manifest_path: str | Path,
    blind_trials_path: str | Path,
    answer_key_path: str | Path,
    freeze_path: str | Path,
    prospective_registry_path: str | Path,
) -> EvalSuiteResult:
    manifest = load_manifest(manifest_path)
    blind_trials = _load_jsonl(blind_trials_path)
    answer_key = _load_jsonl(answer_key_path)
    freeze = json.loads(Path(freeze_path).read_text(encoding="utf-8")) if Path(freeze_path).exists() else {}
    prospective = analyze_prospective_registry(prospective_registry_path)
    checks: list[EvalCheck] = []

    holdout_records = [record for record in manifest if record.get("split") == "holdout"]
    checks.append(
        EvalCheck(
            name="manifest-1000-plus",
            passed=len(manifest) >= 1000 and len(holdout_records) >= 1000,
            detail=f"manifest={len(manifest)} holdout={len(holdout_records)}",
        )
    )
    rating_set = {record.get("rodden_rating") for record in manifest}
    checks.append(
        EvalCheck(
            name="manifest-rating-quality",
            passed=rating_set.issubset({"AA", "A", "B"}),
            detail=f"ratings={sorted(rating_set)}",
        )
    )
    split_counts = {split: sum(1 for record in manifest if record.get("split") == split) for split in ("train", "validation", "holdout")}
    checks.append(
        EvalCheck(
            name="deterministic-splits-present",
            passed=all(count > 0 for count in split_counts.values()),
            detail=f"splits={split_counts}",
        )
    )
    answer_ids = {row.get("trial_id") for row in answer_key}
    blind_ids = {row.get("trial_id") for row in blind_trials}
    checks.append(
        EvalCheck(
            name="blind-holdout-trials-1000",
            passed=len(blind_trials) >= 1000 and blind_ids == answer_ids,
            detail=f"blind_trials={len(blind_trials)} answer_key={len(answer_key)}",
        )
    )
    leaked_answer_trials = [row.get("trial_id") for row in blind_trials if "correct_option_id" in row]
    checks.append(
        EvalCheck(
            name="blind-answer-key-separated",
            passed=not leaked_answer_trials,
            detail=f"leaked={leaked_answer_trials[:5]}",
        )
    )
    checks.append(
        EvalCheck(
            name="frozen-protocol-present",
            passed=freeze.get("status") == "frozen" and bool(freeze.get("combined_sha256")),
            detail=f"protocol_id={freeze.get('protocol_id')} hash={freeze.get('combined_sha256')}",
        )
    )
    checks.append(
        EvalCheck(
            name="prospective-registry-present",
            passed=prospective.total_predictions >= 1 and prospective.status == "unresolved",
            detail=f"total={prospective.total_predictions} status={prospective.status}",
        )
    )
    checks.append(
        EvalCheck(
            name="actual-accuracy-not-overclaimed",
            passed=prospective.status != "passed-90",
            detail="actual 90% destiny/personality/talent accuracy requires scored blind/prospective outcomes",
        )
    )

    return _suite_from_results(
        "accuracy-benchmark-readiness",
        [
            EvalCaseResult(
                case_id="accuracy-benchmark",
                passed=all(check.passed for check in checks),
                checks=tuple(checks),
            )
        ],
    )


def run_relationship_smoke_suite(fixtures_path: str | Path) -> EvalSuiteResult:
    fixtures = json.loads(Path(fixtures_path).read_text(encoding="utf-8"))
    results: list[EvalCaseResult] = []

    for fixture in fixtures:
        checks: list[EvalCheck] = []
        comparison = _build_relationship_comparison_from_fixture(fixture)
        reading = generate_relationship_reading(comparison)

        checks.append(
            EvalCheck(
                name="relationship-reading-sections",
                passed=len(reading.sections) >= 5,
                detail=f"sections={len(reading.sections)}",
            )
        )
        sourced_sections = sum(1 for section in reading.sections if section.sources)
        checks.append(
            EvalCheck(
                name="relationship-reading-source-coverage",
                passed=sourced_sections >= 4,
                detail=f"sourced_sections={sourced_sections}",
            )
        )
        checks.append(
            EvalCheck(
                name="relationship-reading-source-integrity",
                passed=_sources_are_valid(_collect_reading_sources(reading.sections)),
                detail=_source_integrity_detail(_collect_reading_sources(reading.sections)),
            )
        )

        focus_outputs: dict[str, str] = {}
        for focus in RELATIONSHIP_FOCUSES:
            package = build_relationship_product(comparison, focus=focus)
            cited_package = build_relationship_product(comparison, focus=focus, citation_mode="sources")
            focus_outputs[focus] = package.answer_markdown
            checks.append(
                EvalCheck(
                    name=f"relationship-product-{focus}",
                    passed=bool(package.answer_markdown.strip())
                    and package.focus == focus
                    and bool(package.context_blocks),
                    detail=f"context_blocks={len(package.context_blocks)}",
                )
            )
            checks.append(
                EvalCheck(
                    name=f"relationship-product-{focus}-answer-citation-mode-stable",
                    passed=package.answer_citations == cited_package.answer_citations,
                    detail=f"citations={len(package.answer_citations)}",
                )
            )
            checks.append(
                EvalCheck(
                    name=f"relationship-product-{focus}-answer-citation-integrity",
                    passed=_answer_citations_are_valid(package.answer_citations),
                    detail=_answer_citation_detail(package.answer_citations),
                )
            )
            checks.append(
                EvalCheck(
                    name=f"relationship-product-{focus}-answer-citation-scope-sync",
                    passed=_answer_citations_match_scope(
                        package.answer_citations,
                        package.context_blocks,
                        package.reading.sections,
                    ),
                    detail=_answer_citation_scope_detail(
                        package.answer_citations,
                        package.context_blocks,
                        package.reading.sections,
                    ),
                )
            )
            checks.append(
                EvalCheck(
                    name=f"relationship-product-{focus}-answer-markdown-citation-render",
                    passed=_answer_markdown_renders_citations(cited_package),
                    detail=_answer_markdown_citation_detail(cited_package),
                )
            )
            checks.append(
                EvalCheck(
                    name=f"relationship-product-{focus}-block-source-integrity",
                    passed=_sources_are_valid(_collect_block_sources(package.context_blocks)),
                    detail=_source_integrity_detail(_collect_block_sources(package.context_blocks)),
                )
            )
            checks.append(
                EvalCheck(
                    name=f"relationship-product-{focus}-section-source-sync",
                    passed=_context_sources_match_reading(package.context_blocks, package.reading.sections),
                    detail=_section_sync_detail(package.context_blocks, package.reading.sections),
                )
            )
            if focus != "overview":
                highlight_block = _find_block(package.context_blocks, "focus-highlights")
                checks.append(
                    EvalCheck(
                        name=f"relationship-product-{focus}-highlight-sources",
                        passed=highlight_block is not None and bool(highlight_block.sources),
                        detail=f"sources={len(highlight_block.sources) if highlight_block else 0}",
                    )
                )

        unique_outputs = len(set(focus_outputs.values()))
        checks.append(
            EvalCheck(
                name="relationship-focus-diversity",
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

    return _suite_from_results("relationship-smoke", results)


def run_relationship_narrative_eval_suite(cases_path: str | Path) -> EvalSuiteResult:
    cases = json.loads(Path(cases_path).read_text(encoding="utf-8"))
    results: list[EvalCaseResult] = []

    for case in cases:
        comparison = _build_relationship_comparison_from_fixture(case)
        package = build_relationship_product(
            comparison,
            focus=case["focus"],
            question=case.get("question"),
            citation_mode=case.get("citation_mode", "none"),
        )
        text = package.answer_markdown
        checks: list[EvalCheck] = []

        checks.append(
            EvalCheck(
                name="citation-mode",
                passed=package.answer_citation_mode == case.get("citation_mode", "none"),
                detail=package.answer_citation_mode,
            )
        )
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

        for key in case.get("required_source_blocks", []):
            block = _find_block(package.context_blocks, key)
            checks.append(
                EvalCheck(
                    name=f"source-block:{key}",
                    passed=block is not None and bool(block.sources),
                    detail=f"sources={len(block.sources) if block else 0}",
                )
            )
            if block is not None and block.sources:
                checks.append(
                    EvalCheck(
                        name=f"source-block-integrity:{key}",
                        passed=_sources_are_valid(block.sources),
                        detail=_source_integrity_detail(block.sources),
                    )
                )

        for key, expected_kinds in case.get("required_block_source_kinds", {}).items():
            block = _find_block(package.context_blocks, key)
            present_kinds = {source.kind for source in block.sources} if block is not None else set()
            missing = [kind for kind in expected_kinds if kind not in present_kinds]
            checks.append(
                EvalCheck(
                    name=f"source-kinds:{key}",
                    passed=not missing,
                    detail=f"present={sorted(present_kinds)} missing={missing}",
                )
            )

        for key in case.get("required_citation_keys", []):
            citation = _find_answer_citation(package.answer_citations, key)
            checks.append(
                EvalCheck(
                    name=f"answer-citation:{key}",
                    passed=citation is not None and bool(citation.sources),
                    detail=f"sources={len(citation.sources) if citation else 0}",
                )
            )
            if citation is not None and case.get("citation_mode", "none") == "sources":
                rendered_line = _render_expected_source_line(citation.sources)
                checks.append(
                    EvalCheck(
                        name=f"answer-citation-render:{key}",
                        passed=rendered_line in text,
                        detail=rendered_line,
                    )
                )

        for key, expected_kinds in case.get("required_citation_source_kinds", {}).items():
            citation = _find_answer_citation(package.answer_citations, key)
            present_kinds = {source.kind for source in citation.sources} if citation is not None else set()
            missing = [kind for kind in expected_kinds if kind not in present_kinds]
            checks.append(
                EvalCheck(
                    name=f"answer-citation-kinds:{key}",
                    passed=not missing,
                    detail=f"present={sorted(present_kinds)} missing={missing}",
                )
            )

        results.append(
            EvalCaseResult(
                case_id=case["id"],
                passed=all(check.passed for check in checks),
                checks=tuple(checks),
            )
        )

    return _suite_from_results("relationship-narrative", results)


def run_timing_smoke_suite(fixtures_path: str | Path) -> EvalSuiteResult:
    fixtures = json.loads(Path(fixtures_path).read_text(encoding="utf-8"))
    results: list[EvalCaseResult] = []

    for fixture in fixtures:
        checks: list[EvalCheck] = []
        timing = _build_timing_from_fixture(fixture)
        reading = generate_timing_reading(timing)

        checks.append(
            EvalCheck(
                name="timing-reading-sections",
                passed=len(reading.sections) >= 4,
                detail=f"sections={len(reading.sections)}",
            )
        )
        sourced_sections = sum(1 for section in reading.sections if section.sources)
        checks.append(
            EvalCheck(
                name="timing-reading-source-coverage",
                passed=sourced_sections >= 4,
                detail=f"sourced_sections={sourced_sections}",
            )
        )
        checks.append(
            EvalCheck(
                name="timing-reading-source-integrity",
                passed=_sources_are_valid(_collect_reading_sources(reading.sections)),
                detail=_source_integrity_detail(_collect_reading_sources(reading.sections)),
            )
        )

        focus_outputs: dict[str, str] = {}
        for focus in TIMING_FOCUSES:
            package = build_timing_product(timing, focus=focus)
            cited_package = build_timing_product(timing, focus=focus, citation_mode="sources")
            focus_outputs[focus] = package.answer_markdown
            checks.append(
                EvalCheck(
                    name=f"timing-product-{focus}",
                    passed=bool(package.answer_markdown.strip())
                    and package.focus == focus
                    and bool(package.context_blocks),
                    detail=f"context_blocks={len(package.context_blocks)}",
                )
            )
            checks.append(
                EvalCheck(
                    name=f"timing-product-{focus}-answer-citation-mode-stable",
                    passed=package.answer_citations == cited_package.answer_citations,
                    detail=f"citations={len(package.answer_citations)}",
                )
            )
            checks.append(
                EvalCheck(
                    name=f"timing-product-{focus}-answer-citation-integrity",
                    passed=_answer_citations_are_valid(package.answer_citations),
                    detail=_answer_citation_detail(package.answer_citations),
                )
            )
            checks.append(
                EvalCheck(
                    name=f"timing-product-{focus}-answer-citation-scope-sync",
                    passed=_answer_citations_match_scope(
                        package.answer_citations,
                        package.context_blocks,
                        package.reading.sections,
                    ),
                    detail=_answer_citation_scope_detail(
                        package.answer_citations,
                        package.context_blocks,
                        package.reading.sections,
                    ),
                )
            )
            checks.append(
                EvalCheck(
                    name=f"timing-product-{focus}-answer-markdown-citation-render",
                    passed=_answer_markdown_renders_citations(cited_package),
                    detail=_answer_markdown_citation_detail(cited_package),
                )
            )
            checks.append(
                EvalCheck(
                    name=f"timing-product-{focus}-block-source-integrity",
                    passed=_sources_are_valid(_collect_block_sources(package.context_blocks)),
                    detail=_source_integrity_detail(_collect_block_sources(package.context_blocks)),
                )
            )
            checks.append(
                EvalCheck(
                    name=f"timing-product-{focus}-section-source-sync",
                    passed=_context_sources_match_reading(package.context_blocks, package.reading.sections),
                    detail=_section_sync_detail(package.context_blocks, package.reading.sections),
                )
            )
            if focus != "overview":
                highlight_block = _find_block(package.context_blocks, "focus-highlights")
                checks.append(
                    EvalCheck(
                        name=f"timing-product-{focus}-highlight-sources",
                        passed=highlight_block is not None and bool(highlight_block.sources),
                        detail=f"sources={len(highlight_block.sources) if highlight_block else 0}",
                    )
                )

        unique_outputs = len(set(focus_outputs.values()))
        checks.append(
            EvalCheck(
                name="timing-focus-diversity",
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

    return _suite_from_results("timing-smoke", results)


def run_timing_narrative_eval_suite(cases_path: str | Path) -> EvalSuiteResult:
    cases = json.loads(Path(cases_path).read_text(encoding="utf-8"))
    results: list[EvalCaseResult] = []

    for case in cases:
        timing = _build_timing_from_fixture(case)
        package = build_timing_product(
            timing,
            focus=case["focus"],
            question=case.get("question"),
            citation_mode=case.get("citation_mode", "none"),
        )
        text = package.answer_markdown
        checks: list[EvalCheck] = []

        checks.append(
            EvalCheck(
                name="citation-mode",
                passed=package.answer_citation_mode == case.get("citation_mode", "none"),
                detail=package.answer_citation_mode,
            )
        )
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

        for key in case.get("required_source_blocks", []):
            block = _find_block(package.context_blocks, key)
            checks.append(
                EvalCheck(
                    name=f"source-block:{key}",
                    passed=block is not None and bool(block.sources),
                    detail=f"sources={len(block.sources) if block else 0}",
                )
            )
            if block is not None and block.sources:
                checks.append(
                    EvalCheck(
                        name=f"source-block-integrity:{key}",
                        passed=_sources_are_valid(block.sources),
                        detail=_source_integrity_detail(block.sources),
                    )
                )

        for key, expected_kinds in case.get("required_block_source_kinds", {}).items():
            block = _find_block(package.context_blocks, key)
            present_kinds = {source.kind for source in block.sources} if block is not None else set()
            missing = [kind for kind in expected_kinds if kind not in present_kinds]
            checks.append(
                EvalCheck(
                    name=f"source-kinds:{key}",
                    passed=not missing,
                    detail=f"present={sorted(present_kinds)} missing={missing}",
                )
            )

        for key in case.get("required_citation_keys", []):
            citation = _find_answer_citation(package.answer_citations, key)
            checks.append(
                EvalCheck(
                    name=f"answer-citation:{key}",
                    passed=citation is not None and bool(citation.sources),
                    detail=f"sources={len(citation.sources) if citation else 0}",
                )
            )
            if citation is not None and case.get("citation_mode", "none") == "sources":
                rendered_line = _render_expected_source_line(citation.sources)
                checks.append(
                    EvalCheck(
                        name=f"answer-citation-render:{key}",
                        passed=rendered_line in text,
                        detail=rendered_line,
                    )
                )

        for key, expected_kinds in case.get("required_citation_source_kinds", {}).items():
            citation = _find_answer_citation(package.answer_citations, key)
            present_kinds = {source.kind for source in citation.sources} if citation is not None else set()
            missing = [kind for kind in expected_kinds if kind not in present_kinds]
            checks.append(
                EvalCheck(
                    name=f"answer-citation-kinds:{key}",
                    passed=not missing,
                    detail=f"present={sorted(present_kinds)} missing={missing}",
                )
            )

        results.append(
            EvalCaseResult(
                case_id=case["id"],
                passed=all(check.passed for check in checks),
                checks=tuple(checks),
            )
        )

    return _suite_from_results("timing-narrative", results)


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


def _build_relationship_comparison_from_fixture(fixture: dict[str, Any]):
    left = normalize_birth_input(**fixture["left_input"])
    right = normalize_birth_input(**fixture["right_input"])
    return compare_relationship(
        left,
        right,
        left_label=fixture.get("left_label", "A"),
        right_label=fixture.get("right_label", "B"),
    )


def _build_timing_from_fixture(fixture: dict[str, Any]):
    natal = normalize_birth_input(**fixture["natal_input"])
    transit = normalize_birth_input(**fixture["transit_input"])
    return analyze_timing(
        natal,
        transit,
        timing_label=fixture.get("timing_label", "current"),
    )


def _find_block(blocks: tuple[LLMContextBlock, ...], key: str) -> LLMContextBlock | None:
    return next((block for block in blocks if block.key == key), None)


def _find_answer_citation(
    citations: tuple[AnswerCitation, ...],
    key: str,
) -> AnswerCitation | None:
    return next((citation for citation in citations if citation.key == key), None)


def _collect_reading_sources(sections: tuple[ReadingSection, ...]) -> tuple[SourceReference, ...]:
    return tuple(source for section in sections for source in section.sources)


def _collect_block_sources(blocks: tuple[LLMContextBlock, ...]) -> tuple[SourceReference, ...]:
    return tuple(source for block in blocks for source in block.sources)


def _sources_are_valid(sources: tuple[SourceReference, ...]) -> bool:
    return all(source.kind in VALID_SOURCE_KINDS and Path(source.path).exists() for source in sources)


def _source_integrity_detail(sources: tuple[SourceReference, ...]) -> str:
    invalid = [
        f"{source.kind}:{source.code}"
        for source in sources
        if source.kind not in VALID_SOURCE_KINDS or not Path(source.path).exists()
    ]
    return f"sources={len(sources)} invalid={invalid}"


def _context_sources_match_reading(
    blocks: tuple[LLMContextBlock, ...],
    sections: tuple[ReadingSection, ...],
) -> bool:
    return not _mismatched_section_keys(blocks, sections)


def _section_sync_detail(
    blocks: tuple[LLMContextBlock, ...],
    sections: tuple[ReadingSection, ...],
) -> str:
    mismatches = _mismatched_section_keys(blocks, sections)
    return f"mismatches={mismatches}"


def _mismatched_section_keys(
    blocks: tuple[LLMContextBlock, ...],
    sections: tuple[ReadingSection, ...],
) -> list[str]:
    mismatches: list[str] = []
    for section in sections:
        block = _find_block(blocks, section.key)
        if block is None:
            continue
        if _source_signature(block.sources) != _source_signature(section.sources):
            mismatches.append(section.key)
    return mismatches


def _source_signature(sources: tuple[SourceReference, ...]) -> tuple[tuple[str, str, str], ...]:
    return tuple((source.kind, source.code, source.path) for source in sources)


def _answer_citations_are_valid(citations: tuple[AnswerCitation, ...]) -> bool:
    return all(_sources_are_valid(citation.sources) for citation in citations)


def _answer_citation_detail(citations: tuple[AnswerCitation, ...]) -> str:
    invalid = [
        citation.key
        for citation in citations
        if not _sources_are_valid(citation.sources)
    ]
    return f"citations={len(citations)} invalid={invalid}"


def _answer_citations_match_scope(
    citations: tuple[AnswerCitation, ...],
    blocks: tuple[LLMContextBlock, ...],
    sections: tuple[ReadingSection, ...],
) -> bool:
    return not _answer_citation_mismatches(citations, blocks, sections)


def _answer_citation_scope_detail(
    citations: tuple[AnswerCitation, ...],
    blocks: tuple[LLMContextBlock, ...],
    sections: tuple[ReadingSection, ...],
) -> str:
    return f"mismatches={_answer_citation_mismatches(citations, blocks, sections)}"


def _answer_citation_mismatches(
    citations: tuple[AnswerCitation, ...],
    blocks: tuple[LLMContextBlock, ...],
    sections: tuple[ReadingSection, ...],
) -> list[str]:
    citation_map = {citation.key: citation for citation in citations}
    block_map = {block.key: block for block in blocks}
    selected_section_keys = {section.key for section in sections if section.key in block_map}
    allowed_keys = set(selected_section_keys)
    if "focus-highlights" in block_map:
        allowed_keys.add("focus-highlights")
    mismatches: list[str] = []
    for citation in citations:
        if citation.key not in allowed_keys:
            mismatches.append(citation.key)
            continue
        if citation.key == "focus-highlights":
            block = block_map.get("focus-highlights")
            if block is None or _source_signature(citation.sources) != _source_signature(block.sources):
                mismatches.append(citation.key)
    highlight_block = block_map.get("focus-highlights")
    if highlight_block is not None and highlight_block.sources and "focus-highlights" not in citation_map:
        mismatches.append("focus-highlights")
    for section in sections:
        if section.key not in selected_section_keys:
            continue
        citation = citation_map.get(section.key)
        if section.sources and citation is None:
            mismatches.append(section.key)
            continue
        if citation is None:
            continue
        if _source_signature(citation.sources) != _source_signature(section.sources):
            mismatches.append(section.key)
    return mismatches


def _answer_markdown_renders_citations(package) -> bool:
    if package.answer_citation_mode != "sources":
        return False
    return not _answer_markdown_citation_mismatches(package)


def _answer_markdown_citation_detail(package) -> str:
    return f"mismatches={_answer_markdown_citation_mismatches(package)}"


def _answer_markdown_citation_mismatches(package) -> list[str]:
    mismatches: list[str] = []
    for citation in package.answer_citations:
        rendered_line = _render_expected_source_line(citation.sources)
        if rendered_line not in package.answer_markdown:
            mismatches.append(citation.key)
    return mismatches


def _render_expected_source_line(sources: tuple[SourceReference, ...]) -> str:
    items = [f"[{source.kind}:{source.code}]({source.path})" for source in sources]
    return "来源：" + "；".join(items)


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _mentioned_channels(text: str) -> set[str]:
    channels: set[str] = set()
    channel_patterns = (
        r"通道\s*(\d{1,2})-(\d{1,2})",
        r"\[channel:(\d{1,2})-(\d{1,2})\]",
        r"/channels/(\d{1,2})-(\d{1,2})\.md",
    )
    for pattern in channel_patterns:
        for left, right in re.findall(pattern, text):
            channels.add(f"{int(left):02d}-{int(right):02d}")
    return channels


def _mentioned_gate_numbers(text: str) -> set[int]:
    gates: set[int] = set()
    for match in re.finditer(r"(?<!\d)(\d{1,2})\s*号闸门", text):
        gates.add(int(match.group(1)))
    for match in re.finditer(r"\[gate:(\d{1,2})\]", text):
        gates.add(int(match.group(1)))
    for match in re.finditer(r"/gates/(\d{1,2})\.md", text):
        gates.add(int(match.group(1)))
    for match in re.finditer(r"(?<!\d)(\d{1,2})/(\d{1,2})(?:\s*(?:号闸门|闸门|主题|压力)|\s*的压力)", text):
        gates.add(int(match.group(1)))
        gates.add(int(match.group(2)))
    return gates


def _banned_terms(text: str) -> tuple[str, ...]:
    return tuple(term for term in PUBLIC_FIGURE_BANNED_TERMS if term in text)
