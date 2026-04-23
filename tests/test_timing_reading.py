from __future__ import annotations

from human_design.input import normalize_birth_input
from human_design.timing import analyze_timing
from human_design.timing_reading import generate_timing_reading, render_timing_reading_markdown


def _build_timing():
    natal = normalize_birth_input("1988-10-09T20:30:00+08:00")
    transit = normalize_birth_input("2026-04-23T10:00:00+08:00")
    return analyze_timing(natal, transit, timing_label="today")


def test_generate_timing_reading_has_sections_and_sources() -> None:
    reading = generate_timing_reading(_build_timing())

    assert reading.headline
    assert len(reading.sections) == 4
    assert any(section.key == "decision-window" for section in reading.sections)
    assert sum(1 for section in reading.sections if section.sources) >= 4


def test_render_timing_reading_markdown_contains_expected_sections() -> None:
    markdown = render_timing_reading_markdown(generate_timing_reading(_build_timing()))

    assert "# 人类图 Timing 解读" in markdown
    assert "## 当前气候" in markdown
    assert "## 决策窗口" in markdown
    assert "## 建议继续追问" in markdown
