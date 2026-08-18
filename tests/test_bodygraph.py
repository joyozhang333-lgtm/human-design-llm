from __future__ import annotations

from pathlib import Path

from human_design.bodygraph import render_bodygraph_svg, write_bodygraph_svg
from human_design.engine import calculate_chart
from human_design.input import normalize_birth_input


def _build_chart():
    return calculate_chart(normalize_birth_input("1970-02-04T12:00:00+08:00"))


def test_render_bodygraph_svg_contains_expected_labels() -> None:
    svg = render_bodygraph_svg(_build_chart(), title="测试人类图")

    assert "<svg" in svg
    assert "测试人类图" in svg
    assert "纯生产者" in svg
    assert "Sacral Authority" in svg
    assert "荐骨中心" in svg
    assert "阿姬娜中心" in svg
    assert "设计面" in svg
    assert "人格面" in svg
    assert "13.2" in svg
    assert "1.4" in svg
    assert "人类图解读本" in svg
    assert "核心身份" in svg
    assert "决策与行动方式" in svg
    assert "建议继续追问" in svg
    assert ">2<" in svg
    assert ">14<" in svg


def test_render_bodygraph_svg_without_booklet_is_graphic_only() -> None:
    svg = render_bodygraph_svg(_build_chart(), title="测试人类图", include_booklet=False)

    assert "<svg" in svg
    assert "测试人类图" in svg
    # Chart graphic, activation panels and 盘面摘要 stay.
    assert "Sacral Authority" in svg
    assert "阿姬娜中心" in svg
    assert "盘面摘要" in svg
    assert "设计面" in svg
    assert "人格面" in svg
    # The long in-SVG booklet is dropped (ships via the reading-book endpoint instead).
    assert "人类图解读本" not in svg
    assert "建议继续追问" not in svg


def test_write_bodygraph_svg_creates_file(tmp_path: Path) -> None:
    output = tmp_path / "chart.svg"
    path = write_bodygraph_svg(_build_chart(), output)

    assert path.exists()
    assert path.read_text(encoding="utf-8").startswith("<svg")
