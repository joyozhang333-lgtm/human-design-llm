from __future__ import annotations

from human_design import __version__
from human_design.input import normalize_birth_input
from human_design.timing import analyze_timing
from human_design.timing_product import build_timing_product


def _build_timing():
    natal = normalize_birth_input("1988-10-09T20:30:00+08:00")
    transit = normalize_birth_input("2026-04-23T10:00:00+08:00")
    return analyze_timing(natal, transit, timing_label="today")


def test_build_timing_product_returns_cited_package() -> None:
    package = build_timing_product(
        _build_timing(),
        focus="decision",
        question="我现在要不要推进这个决定？",
        citation_mode="sources",
    )

    assert package.product_version == __version__
    assert package.focus == "decision"
    assert any(block.key == "focus-highlights" for block in package.context_blocks)
    assert any(citation.key == "focus-highlights" for citation in package.answer_citations)
    assert "## 焦点提示" in package.answer_markdown
    assert "来源：" in package.answer_markdown


def test_build_timing_product_changes_by_focus() -> None:
    timing = _build_timing()
    overview = build_timing_product(timing, focus="overview")
    decision = build_timing_product(timing, focus="decision")

    assert overview.answer_markdown != decision.answer_markdown
    assert any(block.key == "decision-window" for block in decision.context_blocks)
