from __future__ import annotations

from datetime import UTC, datetime

from human_design import __version__
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
    assert package.product_version == __version__ == "2.2.0"
    assert package.focus == "career"
    assert package.question == "我在工作里最该怎么用这张图？"
    assert package.answer_citation_mode == "none"
    assert "structured chart data" in package.system_prompt
    assert any(block.key == "channels" for block in package.context_blocks)
    assert any(block.key == "question-lens" for block in package.context_blocks)
    assert any(block.key == "focus-highlights" for block in package.context_blocks)
    assert any(citation.key == "focus-highlights" for citation in package.answer_citations)
    channels_block = next(block for block in package.context_blocks if block.key == "channels")
    highlight_block = next(block for block in package.context_blocks if block.key == "focus-highlights")
    assert any(source.kind == "channel" for source in channels_block.sources)
    assert len(highlight_block.sources) >= 1
    assert "当前聚焦：career" in package.answer_markdown
    assert "当前问题：我在工作里最该怎么用这张图？" in package.answer_markdown
    assert "## 问题切口" in package.answer_markdown
    assert "## 焦点提示" in package.answer_markdown
    assert "## 职业命题" in package.answer_markdown
    assert "## 赚钱结构" in package.answer_markdown
    assert "## 职业误判环路" in package.answer_markdown
    assert "## 方向筛选门槛" in package.answer_markdown
    assert len(package.suggested_followups) == 2


def test_build_llm_product_can_render_answer_sources() -> None:
    chart = calculate_chart(datetime(1988, 10, 9, 12, 30, tzinfo=UTC))
    package = build_llm_product(
        chart,
        focus="career",
        question="我在工作里最该怎么用这张图？",
        citation_mode="sources",
    )

    assert package.answer_citation_mode == "sources"
    assert "来源：" in package.answer_markdown
    assert "[authority:" in package.answer_markdown or "[channel:" in package.answer_markdown
    assert any(citation.key == "channels" for citation in package.answer_citations)


def test_build_llm_product_surfaces_precision_context_when_needed() -> None:
    chart = calculate_chart(normalize_birth_input("1999-03-14T08:05:00"))
    package = build_llm_product(chart, focus="decision")

    assert any(block.key == "input-precision" for block in package.context_blocks)
    assert "输入精度提示" in package.answer_markdown


def test_build_llm_product_focuses_diverge_for_same_chart() -> None:
    chart = calculate_chart(datetime(1988, 10, 9, 12, 30, tzinfo=UTC))
    career = build_llm_product(chart, focus="career", question="我适合换工作吗？")
    relationship = build_llm_product(chart, focus="relationship", question="我在关系里最该注意什么？")

    assert career.answer_markdown != relationship.answer_markdown
    assert career.context_blocks != relationship.context_blocks
    assert "职业转向场景" in career.answer_markdown
    assert "亲密关系场景" in relationship.answer_markdown


def test_build_llm_product_question_changes_highlight_priority() -> None:
    chart = calculate_chart(normalize_birth_input("1999-03-14T08:05:00"))
    package = build_llm_product(
        chart,
        focus="decision",
        question="我现在要不要换工作？",
    )

    focus_block = next(block for block in package.context_blocks if block.key == "focus-highlights")
    assert "权威" in focus_block.content or "定义" in focus_block.content
    assert "现实决策压力" in package.answer_markdown


def test_career_money_direction_question_gets_deep_lens() -> None:
    chart = calculate_chart(normalize_birth_input("1995-03-03T18:30:00+08:00"))
    package = build_llm_product(
        chart,
        focus="career",
        question="我最适合怎么工作、赚钱、选方向？",
        depth="deep",
    )

    focus_block = next(block for block in package.context_blocks if block.key == "focus-highlights")
    assert "职业方向与赚钱结构场景" in package.answer_markdown
    assert "职业主轴 02-14" in focus_block.content
    assert "赚钱误判点" in focus_block.content
    assert "承诺风险" in focus_block.content


def test_career_focus_uses_type_specific_decision_language() -> None:
    chart = calculate_chart(normalize_birth_input("1988-10-09T20:30:00+08:00"))
    package = build_llm_product(
        chart,
        focus="career",
        question="我最适合怎么工作、赚钱、选方向？",
        depth="deep",
    )
    focus_block = next(block for block in package.context_blocks if block.key == "focus-highlights")

    assert "被正确看见" in focus_block.content
    assert "身体真正有回应" not in focus_block.content
    assert "Energy Projector" not in focus_block.content
    assert "Ego Projected" not in focus_block.content
