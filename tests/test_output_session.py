from __future__ import annotations

from human_design.engine import calculate_chart
from human_design.input import normalize_birth_input
from human_design.product import build_llm_product
from human_design.relationship import compare_relationship
from human_design.relationship_product import build_relationship_product
from human_design.timing import analyze_timing
from human_design.timing_product import build_timing_product


def test_single_depth_modes_change_answer_size_and_session_state() -> None:
    normalized = normalize_birth_input("1988-10-09T20:30:00+08:00")
    chart = calculate_chart(normalized)
    brief = build_llm_product(chart=chart, focus="career", depth="brief")
    deep = build_llm_product(chart=chart, focus="career", depth="deep")

    assert brief.delivery_depth == "brief"
    assert deep.delivery_depth == "deep"
    assert len(deep.answer_markdown) > len(brief.answer_markdown)
    assert brief.session_state.product_line == "single"
    assert brief.session_state.carry_block_keys


def test_relationship_and_timing_packages_expose_session_state() -> None:
    left = normalize_birth_input("1988-10-09T20:30:00+08:00")
    right = normalize_birth_input("1992-01-03T06:15:00-05:00")
    relationship_brief = build_relationship_product(
        compare_relationship(left, right, left_label="我", right_label="对方"),
        focus="communication",
        depth="brief",
    )
    relationship_deep = build_relationship_product(
        compare_relationship(left, right, left_label="我", right_label="对方"),
        focus="communication",
        depth="deep",
    )

    natal = normalize_birth_input("1988-10-09T20:30:00+08:00")
    transit = normalize_birth_input("2026-04-23T10:00:00+08:00")
    timing_brief = build_timing_product(
        analyze_timing(natal, transit, timing_label="today"),
        focus="decision",
        depth="brief",
    )
    timing_deep = build_timing_product(
        analyze_timing(natal, transit, timing_label="today"),
        focus="decision",
        depth="deep",
    )

    assert relationship_brief.session_state.product_line == "relationship"
    assert relationship_brief.delivery_depth == "brief"
    assert relationship_brief.session_state.suggested_next_questions
    assert len(relationship_deep.answer_markdown) > len(relationship_brief.answer_markdown)
    assert len(relationship_deep.suggested_followups) >= len(relationship_brief.suggested_followups)

    assert timing_brief.session_state.product_line == "timing"
    assert timing_deep.delivery_depth == "deep"
    assert timing_deep.session_state.carry_facts
    assert len(timing_deep.answer_markdown) > len(timing_brief.answer_markdown)
    assert len(timing_deep.suggested_followups) >= len(timing_brief.suggested_followups)
