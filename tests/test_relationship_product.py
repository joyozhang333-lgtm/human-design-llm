from __future__ import annotations

from human_design import __version__
from human_design.input import normalize_birth_input
from human_design.relationship import compare_relationship
from human_design.relationship_product import build_relationship_product


def _build_comparison():
    left = normalize_birth_input("1988-10-09T20:30:00+08:00")
    right = normalize_birth_input("1992-01-03T06:15:00-05:00")
    return compare_relationship(left, right, left_label="我", right_label="对方")


def test_build_relationship_product_returns_cited_package() -> None:
    package = build_relationship_product(
        _build_comparison(),
        focus="communication",
        question="我们为什么一沟通就容易拉扯？",
        citation_mode="sources",
    )

    assert package.product_version == __version__ == "2.2.1"
    assert package.focus == "communication"
    assert any(block.key == "focus-highlights" for block in package.context_blocks)
    assert any(citation.key == "focus-highlights" for citation in package.answer_citations)
    assert "## 焦点提示" in package.answer_markdown
    assert "来源：" in package.answer_markdown


def test_build_relationship_product_changes_by_focus() -> None:
    comparison = _build_comparison()
    overview = build_relationship_product(comparison, focus="overview")
    decision = build_relationship_product(comparison, focus="decision")

    assert overview.answer_markdown != decision.answer_markdown
    assert any(block.key == "decision-sync" for block in decision.context_blocks)
    assert overview.reading.sections[0].key == "relationship-skeleton"
