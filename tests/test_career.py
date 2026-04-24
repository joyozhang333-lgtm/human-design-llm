from __future__ import annotations

from human_design.career import generate_career_report, render_career_report_markdown
from human_design.engine import calculate_chart
from human_design.input import normalize_birth_input


def _build_chart():
    return calculate_chart(normalize_birth_input("1995-03-03T18:30:00+08:00"))


def _build_non_0214_chart():
    return calculate_chart(normalize_birth_input("1988-10-09T20:30:00+08:00"))


def test_generate_career_report_contains_deep_structure() -> None:
    report = generate_career_report(_build_chart())

    section_titles = {section.title for section in report.sections}
    assert "职业命题" in section_titles
    assert "赚钱结构" in section_titles
    assert "职业误判环路" in section_titles
    assert "方向筛选门槛" in section_titles
    assert "02-14" in report.thesis


def test_render_career_report_markdown_is_actionable() -> None:
    markdown = render_career_report_markdown(generate_career_report(_build_chart()))

    assert "# 人类图职业深读" in markdown
    assert "错误承诺" in markdown
    assert "资产门槛" in markdown
    assert "14 天实验" in markdown


def test_career_report_does_not_invent_absent_channel_or_gates() -> None:
    report = generate_career_report(_build_non_0214_chart())
    section_text = "\n".join(
        (section.summary + "\n" + "\n".join(section.bullets))
        for section in report.sections
    )

    assert "02-14" not in section_text
    assert "14 号闸门" not in section_text
    assert "29 号闸门" not in section_text
    assert "5 号闸门" not in section_text
    assert "25-51" in section_text
    assert "荐骨回应" not in section_text
