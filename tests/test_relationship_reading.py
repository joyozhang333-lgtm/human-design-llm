from __future__ import annotations

from human_design.input import normalize_birth_input
from human_design.relationship import compare_relationship
from human_design.relationship_reading import (
    generate_relationship_reading,
    render_relationship_reading_markdown,
)


def _build_comparison():
    left = normalize_birth_input("1988-10-09T20:30:00+08:00")
    right = normalize_birth_input("1992-01-03T06:15:00-05:00")
    return compare_relationship(left, right, left_label="我", right_label="对方")


def test_generate_relationship_reading_has_sections_and_sources() -> None:
    reading = generate_relationship_reading(_build_comparison())

    assert reading.headline
    assert len(reading.sections) == 5
    assert any(section.key == "decision-sync" for section in reading.sections)
    assert sum(1 for section in reading.sections if section.sources) >= 4
    assert reading.quick_facts[0].startswith("我：")


def test_render_relationship_reading_markdown_contains_expected_sections() -> None:
    markdown = render_relationship_reading_markdown(generate_relationship_reading(_build_comparison()))

    assert "# 人类图关系解读" in markdown
    assert "## 关系骨架" in markdown
    assert "## 共同决策" in markdown
    assert "## 建议继续追问" in markdown
