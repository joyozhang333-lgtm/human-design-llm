from __future__ import annotations

from datetime import UTC, datetime

from human_design.engine import calculate_chart
from human_design.input import normalize_birth_input
from human_design.product import build_llm_product


def test_build_llm_product_generates_session_package() -> None:
    chart = calculate_chart(datetime(1988, 10, 9, 12, 30, tzinfo=UTC))
    package = build_llm_product(
        chart,
        focus="career",
        question="我在工作里最该怎么用这张图？",
    )

    assert package.product_name == "human-design-llm"
    assert package.focus == "career"
    assert package.question == "我在工作里最该怎么用这张图？"
    assert "structured chart data" in package.system_prompt
    assert any(block.key == "channels" for block in package.context_blocks)
    assert "当前聚焦：career" in package.answer_markdown
    assert "当前问题：我在工作里最该怎么用这张图？" in package.answer_markdown
    assert len(package.suggested_followups) == 2


def test_build_llm_product_surfaces_precision_context_when_needed() -> None:
    chart = calculate_chart(normalize_birth_input("1999-03-14T08:05:00"))
    package = build_llm_product(chart, focus="decision")

    assert any(block.key == "input-precision" for block in package.context_blocks)
    assert "输入精度提示" in package.answer_markdown
