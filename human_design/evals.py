from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .engine import calculate_chart
from .input import normalize_birth_input
from .product import build_llm_product
from .reading import generate_reading
from .schema import AnswerCitation, LLMContextBlock, ReadingSection, SourceReference

FOCUSES = ("overview", "career", "relationship", "decision", "growth")
VALID_SOURCE_KINDS = frozenset(
    ("type", "authority", "profile", "definition", "center", "channel", "gate")
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
                    name=f"product-{focus}-answer-citation-integrity",
                    passed=_answer_citations_are_valid(package.answer_citations),
                    detail=_answer_citation_detail(package.answer_citations),
                )
            )
            checks.append(
                EvalCheck(
                    name=f"product-{focus}-answer-citation-sync",
                    passed=_answer_citations_match_sections(package.answer_citations, package.reading.sections),
                    detail=_answer_citation_sync_detail(package.answer_citations, package.reading.sections),
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


def _find_block(blocks: tuple[LLMContextBlock, ...], key: str) -> LLMContextBlock | None:
    return next((block for block in blocks if block.key == key), None)


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


def _answer_citations_match_sections(
    citations: tuple[AnswerCitation, ...],
    sections: tuple[ReadingSection, ...],
) -> bool:
    return not _answer_citation_mismatches(citations, sections)


def _answer_citation_sync_detail(
    citations: tuple[AnswerCitation, ...],
    sections: tuple[ReadingSection, ...],
) -> str:
    return f"mismatches={_answer_citation_mismatches(citations, sections)}"


def _answer_citation_mismatches(
    citations: tuple[AnswerCitation, ...],
    sections: tuple[ReadingSection, ...],
) -> list[str]:
    citation_map = {citation.key: citation for citation in citations}
    mismatches: list[str] = []
    for section in sections:
        citation = citation_map.get(section.key)
        if citation is None:
            continue
        if _source_signature(citation.sources) != _source_signature(section.sources):
            mismatches.append(section.key)
    return mismatches
