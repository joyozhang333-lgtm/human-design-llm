from __future__ import annotations

from pathlib import Path

from human_design.bodygraph import render_bodygraph_svg, write_bodygraph_svg
from human_design.engine import calculate_chart
from human_design.input import normalize_birth_input


def _build_chart():
    return calculate_chart(normalize_birth_input("1995-03-03T18:30:00+08:00"))


def test_render_bodygraph_svg_contains_expected_labels() -> None:
    svg = render_bodygraph_svg(_build_chart(), title="测试人类图")

    assert "<svg" in svg
    assert "测试人类图" in svg
    assert "纯生产者" in svg
    assert "荐骨权威" in svg
    assert "荐骨中心" in svg
    assert "阿姬娜中心" in svg
    assert "设计面" in svg
    assert "人格面" in svg
    assert "63.2" in svg
    assert "5.4" in svg
    assert "人类图解读本" in svg
    assert "核心身份" in svg
    assert "决策与行动方式" in svg
    assert "建议继续追问" in svg
    assert ">2<" in svg
    assert ">14<" in svg


def test_write_bodygraph_svg_creates_file(tmp_path: Path) -> None:
    output = tmp_path / "chart.svg"
    path = write_bodygraph_svg(_build_chart(), output)

    assert path.exists()
    assert path.read_text(encoding="utf-8").startswith("<svg")
