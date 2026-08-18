from __future__ import annotations

from human_design.engine import calculate_chart
from human_design.input import normalize_birth_input
from human_design.interpretation_maps import build_interpretation_map, map_context_text
from human_design.research_corpus import load_interpretation_rules, load_knowledge_atoms, load_source_cards


def _anonymous_0214_chart():
    return calculate_chart(normalize_birth_input("1970-02-04T12:00:00+08:00"))


def test_v03_research_corpus_loads_source_atom_rule_layers() -> None:
    sources = load_source_cards()
    atoms = load_knowledge_atoms()
    rules = load_interpretation_rules()

    assert len(sources) >= 8
    assert len(atoms) >= 20
    assert {source.source_id for source in sources} >= {
        "jovian-dictionary",
        "ihds-definitive-book",
        "zh-authorized-science-of-differentiation",
    }
    assert any(atom.atom_id == "channel.02-14.direction-resources" for atom in atoms)
    assert any(rule.rule_id == "wealth.02-14-main-track" for rule in rules)


def test_talent_map_uses_profile_channel_cross_and_user_language() -> None:
    package = build_interpretation_map(_anonymous_0214_chart(), map_type="talent", chart_id="chart_test")
    text = map_context_text(package)

    assert package.product_version == "0.5.1"
    assert package.map_type == "talent"
    assert package.title == "天赋地图"
    assert "人生角色：2/4" in package.professional_facts
    assert "已定义通道：02-14" in "\n".join(package.professional_facts)
    assert "2/4 天赋" in text
    assert "轮回交叉与人生使命：斯芬克斯右角度交叉" in "\n".join(package.professional_facts)
    assert "独处养熟" in text
    assert "当前聚焦" not in text
    assert "焦点提示" not in text


def test_wealth_map_surfaces_money_source_and_promise_boundary() -> None:
    package = build_interpretation_map(_anonymous_0214_chart(), map_type="wealth")
    titles = [item.title for section in package.sections for item in section.items]
    wealth_item = next(item for section in package.sections for item in section.items if item.key == "wealth.02-14-main-track")

    assert "财富来源：方向感加资源配置" in titles
    assert any("14号闸门" in "；".join(item.chart_basis) for section in package.sections for item in section.items)
    assert "02-14" in map_context_text(package)
    assert wealth_item.diagnosis_depth == "deep"
    assert wealth_item.embodied_expression
    assert wealth_item.blind_spots
    assert wealth_item.stuck_patterns
    assert wealth_item.stuck_causes
    assert all("多觉察" not in " ".join(values) for values in (wealth_item.embodied_expression, wealth_item.blind_spots, wealth_item.stuck_patterns, wealth_item.stuck_causes))
    assert any("盘面机制" in cause and "现实场景" in cause for cause in wealth_item.stuck_causes)


def test_body_and_mission_maps_are_grounded_in_real_chart_facts() -> None:
    body = build_interpretation_map(_anonymous_0214_chart(), map_type="body")
    mission = build_interpretation_map(_anonymous_0214_chart(), map_type="mission")

    assert any("荐骨怎么真正参与选择" == item.title for section in body.sections for item in section.items)
    assert mission.professional_facts
    assert "纯生产者" in "\n".join(mission.professional_facts)
    assert "Authority：Sacral Authority" in "\n".join(mission.professional_facts)
    assert any(item.key == "mission.whole-chart" for section in mission.sections for item in section.items)


def test_every_user_map_has_a_complete_whole_chart_reading() -> None:
    chart = _anonymous_0214_chart()
    for map_type in ("body", "wealth", "talent", "relationship", "mission"):
        package = build_interpretation_map(chart, map_type=map_type)
        items = [item for section in package.sections for item in section.items]
        whole_chart = next(item for item in items if item.key == f"{map_type}.whole-chart")
        assert whole_chart.user_language
        assert whole_chart.life_scenes
        assert whole_chart.embodied_expression
        assert whole_chart.blind_spots
        assert whole_chart.stuck_patterns
        assert whole_chart.stuck_causes
        assert whole_chart.practices


def test_professional_map_uses_trace_diagnosis_without_long_sections() -> None:
    package = build_interpretation_map(_anonymous_0214_chart(), map_type="professional")
    items = [item for section in package.sections for item in section.items]

    assert items
    assert all(item.diagnosis_depth == "trace" for item in items)
    assert all(not item.embodied_expression for item in items)
    assert all(not item.stuck_causes for item in items)
    assert any(item.blind_spots for item in items)
    assert any(item.stuck_patterns for item in items)
