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
    gates_full_section = reading.sections[7]

    assert "投射者" in reading.headline
    assert len(reading.sections) == 9
    assert core_section.title == "核心身份"
    assert any(source.kind == "type" for source in core_section.sources)
    assert any("25-51" in bullet for bullet in channels_section.bullets)
    assert any("57 号闸门" in bullet for bullet in gates_section.bullets)
    assert any("唤醒" in bullet for bullet in channels_section.bullets)
    assert any("直觉清醒" in bullet for bullet in gates_section.bullets)
    assert any(source.code == "25-51" for source in channels_section.sources)
    assert any(source.code == "57" for source in gates_section.sources)
    assert any(fact.startswith("输入精度：") for fact in reading.quick_facts)
    # V0.6：关键闸门只取 top-6，其余只保留在按需专业数据中。
    assert len(gates_section.bullets) <= 6
    assert gates_full_section.key == "gates-full"
    assert len(gates_full_section.bullets) == len(chart.activated_gates)


def test_render_reading_markdown_contains_key_blocks() -> None:
    chart = calculate_chart(datetime(1988, 10, 9, 12, 30, tzinfo=UTC))
    reading = generate_reading(chart)
    markdown = render_reading_markdown(reading)

    assert "# 人类图完整解读" in markdown
    assert "## 决策与行动方式" in markdown
    assert "## 九大中心" in markdown
    assert "## 通道主题" in markdown
    assert "## 关键闸门" in markdown
    assert "## 完整闸门清单" in markdown


def test_generate_reading_surfaces_precision_warnings() -> None:
    chart = calculate_chart(normalize_birth_input("1999-03-14T08:05:00"))
    reading = generate_reading(chart)

    assert any("按世界时处理" in fact for fact in reading.quick_facts)
    assert any("影响人类图结果精度" in fact for fact in reading.quick_facts)


def test_reading_markdown_has_no_english_symbols_or_developer_voice() -> None:
    """V0.6 硬红线：除精确 Authority 名称外，零英文、符号、开发者口吻和模板套话。"""
    import re

    from human_design.labels import AUTHORITY_PROFESSIONAL_LABELS

    chart = calculate_chart(normalize_birth_input("1988-10-09T20:30:00+08:00"))
    reading = generate_reading(chart)
    markdown = render_reading_markdown(reading)

    english_check = markdown
    for term in set(AUTHORITY_PROFESSIONAL_LABELS.values()):
        english_check = english_check.replace(term, "")
    assert not re.search(r"[A-Za-z]{3,}", english_check), re.search(r"[A-Za-z]{3,}", english_check).group()
    assert not re.search(r"[♃♄⛢♅⊕☊☋☉☽☿♀♂♆♇]", markdown)
    for banned in ("方便后续", "门线解读", "产品价值", "chart facts", "回到图表事实", "系统有没有编造"):
        assert banned not in markdown
    for template in ("当这股能量运作成熟时", "形成稳定贡献", "活成过度反应或反复内耗"):
        assert template not in markdown
    for fatalism in ("你注定", "你必然", "命中注定"):
        assert fatalism not in markdown


def test_variable_orientation_counts_only_l_r_tokens() -> None:
    chart = calculate_chart(normalize_birth_input("1970-02-04T12:00:00+08:00"))
    reading = generate_reading(chart)
    cross_section = next(section for section in reading.sections if section.key == "cross-variables")

    assert any("0 左 / 4 右" in bullet for bullet in cross_section.bullets)
