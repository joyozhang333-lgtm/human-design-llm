from __future__ import annotations

from datetime import UTC, datetime

from human_design.engine import calculate_chart
from human_design.input import normalize_birth_input
from human_design.reading import generate_reading, render_reading_markdown


def test_generate_reading_produces_complete_sections() -> None:
    chart = calculate_chart(datetime(1988, 10, 9, 12, 30, tzinfo=UTC))
    reading = generate_reading(chart)
    core_section = reading.sections[0]
    channels_section = reading.sections[5]
    gates_section = reading.sections[6]

    assert "投射者" in reading.headline
    assert len(reading.sections) == 8
    assert core_section.title == "核心身份"
    assert any(source.kind == "type" for source in core_section.sources)
    assert any("25-51" in bullet for bullet in channels_section.bullets)
    assert any("57 号闸门" in bullet for bullet in gates_section.bullets)
    assert any("唤醒" in bullet for bullet in channels_section.bullets)
    assert any("直觉清醒" in bullet for bullet in gates_section.bullets)
    assert any(source.code == "25-51" for source in channels_section.sources)
    assert any(source.code == "57" for source in gates_section.sources)
    assert any(fact.startswith("输入精度：") for fact in reading.quick_facts)


def test_render_reading_markdown_contains_key_blocks() -> None:
    chart = calculate_chart(datetime(1988, 10, 9, 12, 30, tzinfo=UTC))
    reading = generate_reading(chart)
    markdown = render_reading_markdown(reading)

    assert "# 人类图完整解读" in markdown
    assert "## 决策与行动方式" in markdown
    assert "## 九大中心" in markdown
    assert "## 通道主题" in markdown
    assert "## 闸门与行星激活" in markdown


def test_generate_reading_surfaces_precision_warnings() -> None:
    chart = calculate_chart(normalize_birth_input("1999-03-14T08:05:00"))
    reading = generate_reading(chart)

    assert any("默认按 UTC" in fact for fact in reading.quick_facts)
    assert any("影响人类图结果精度" in fact for fact in reading.quick_facts)


def test_variable_orientation_counts_only_l_r_tokens() -> None:
    chart = calculate_chart(normalize_birth_input("1995-03-03T18:30:00+08:00"))
    reading = generate_reading(chart)
    cross_section = next(section for section in reading.sections if section.key == "cross-variables")

    assert any("3 左 / 1 右" in bullet for bullet in cross_section.bullets)
