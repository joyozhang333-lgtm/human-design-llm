from __future__ import annotations

import re

from human_design.glossary import (
    CROSS_ANGLE_LABELS,
    DETERMINATION_LABELS,
    ENVIRONMENT_LABELS,
    MOTIVATION_LABELS,
    PERSPECTIVE_LABELS,
    PLANET_LABELS,
    PLANET_SYMBOLS,
    SENSE_LABELS,
    build_glossary_entries,
    display_channel_type,
    display_circuit_group,
    display_determination,
    display_environment,
    display_imprint,
    display_incarnation_cross_theme,
    display_motivation,
    display_perspective,
    display_planet,
    scrub_technical_terms,
)
from human_design.labels import (
    CENTER_LABELS,
    CHANNEL_LABELS,
    GATE_THEME_LABELS,
    display_channel_label,
    display_gate_theme,
    display_incarnation_cross,
)

ENGLISH_RE = re.compile(r"[A-Za-z]")
SYMBOL_RE = re.compile(r"[♃♄⛢♅⊕☊☋☉☽☿♀♂♆♇]")


def _assert_chinese(text: str) -> None:
    assert text, "translation must not be empty"
    assert not ENGLISH_RE.search(text), text
    assert not SYMBOL_RE.search(text), text


def test_all_64_gates_have_chinese_themes() -> None:
    for gate in range(1, 65):
        _assert_chinese(display_gate_theme(gate))
    assert len(GATE_THEME_LABELS) == 64


def test_all_36_channels_have_chinese_labels() -> None:
    assert len(CHANNEL_LABELS) == 36
    for code in CHANNEL_LABELS:
        _assert_chinese(display_channel_label(code))


def test_all_9_centers_have_chinese_labels() -> None:
    assert len(CENTER_LABELS) == 9
    for label in CENTER_LABELS.values():
        assert not SYMBOL_RE.search(label)
        # G中心 允许字母 G，其余必须无英文
        assert label == "G中心" or not ENGLISH_RE.search(label)


def test_all_planets_translate_from_code_symbol_and_mixed_labels() -> None:
    for code in PLANET_LABELS:
        _assert_chinese(display_planet(code))
    for symbol in PLANET_SYMBOLS:
        _assert_chinese(display_planet(symbol))
    _assert_chinese(display_planet("sun", "☉ Sun"))
    _assert_chinese(display_planet("", "☉ Sun"))
    _assert_chinese(display_planet("north-node", "North Node"))


def test_all_variable_values_translate_to_chinese() -> None:
    for value in MOTIVATION_LABELS:
        _assert_chinese(display_motivation(value))
    for value in PERSPECTIVE_LABELS:
        _assert_chinese(display_perspective(value))
    for value in DETERMINATION_LABELS:
        _assert_chinese(display_determination(value))
    for value in ENVIRONMENT_LABELS:
        _assert_chinese(display_environment(value))
    assert len(DETERMINATION_LABELS) == 12
    assert len(ENVIRONMENT_LABELS) == 12
    assert len(MOTIVATION_LABELS) == 6
    assert len(SENSE_LABELS) == 6


def test_variable_miss_never_falls_back_to_english() -> None:
    _assert_chinese(display_motivation("Nonexistent"))
    _assert_chinese(display_determination("Weird, Value"))


def test_circuit_channel_type_imprint_translate() -> None:
    for code in ("individual", "tribal", "collective", "integration"):
        _assert_chinese(display_circuit_group(code))
    for code in ("projected", "generated", "manifested", "manifesting-generated"):
        _assert_chinese(display_channel_type(code))
    for code in ("design", "personality"):
        _assert_chinese(display_imprint(code))
        _assert_chinese(display_imprint(code, short=True))


def test_incarnation_cross_degrade_template_covers_all_angles() -> None:
    assert display_incarnation_cross_theme("57-51-53-54-r", "", GATE_THEME_LABELS) == "右角度交叉·直觉清明"
    assert display_incarnation_cross_theme("10-15-18-17-l", "", GATE_THEME_LABELS).startswith("左角度交叉·")
    assert display_incarnation_cross_theme("1-2-7-13-j", "", GATE_THEME_LABELS).startswith("并列交叉·")
    for code in CROSS_ANGLE_LABELS:
        result = display_incarnation_cross_theme(f"8-14-59-55-{code}", "", GATE_THEME_LABELS)
        _assert_chinese(result)


def test_incarnation_cross_display_never_returns_english() -> None:
    # 未收录的交叉：降级模板，不回落英文全名。
    result = display_incarnation_cross("57-51-53-54-r", "Right Angle Cross of Penetration 3 (57/51 | 53/54)")
    _assert_chinese(result)
    # code 解析失败时也回落中文占位。
    result = display_incarnation_cross("", "Left Angle Cross of Something")
    _assert_chinese(result)


def test_scrub_technical_terms_removes_utc_iana() -> None:
    scrubbed = scrub_technical_terms("出生时间未提供时区，当前按 UTC 处理；IANA 时区规则已应用。")
    assert "UTC" not in scrubbed
    assert "IANA" not in scrubbed


def test_glossary_entries_export_shape() -> None:
    entries = build_glossary_entries()
    assert len(entries) > 50
    for entry in entries:
        assert entry["key"]
        assert entry["zh"]
        assert entry["tier"] in {"translate", "hide", "first-hint"}
        assert not SYMBOL_RE.search(entry["zh"])
