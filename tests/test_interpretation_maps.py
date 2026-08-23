from __future__ import annotations

from human_design.engine import calculate_chart
from human_design.content_audit import audit_report_content
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

    assert package.product_version == "0.5.3"
    assert package.map_type == "talent"
    assert package.title == "天赋报告"
    assert "人生角色：2/4" in package.professional_facts
    assert "已定义通道：02-14" in "\n".join(package.professional_facts)
    assert "2/4：你的天赋怎样成熟" in text
    assert "轮回交叉与人生使命：斯芬克斯右角度交叉" in "\n".join(package.professional_facts)
    assert "天然八十分" in text
    assert "当前聚焦" not in text
    assert "焦点提示" not in text


def test_wealth_map_surfaces_money_source_and_promise_boundary() -> None:
    package = build_interpretation_map(_anonymous_0214_chart(), map_type="wealth")
    titles = [item.title for section in package.sections for item in section.items]
    wealth_item = next(item for section in package.sections for item in section.items if item.key == "wealth.02-14-main-track")

    assert any("02-14" in title and "形成价值" in title for title in titles)
    assert any("02-14" in "；".join(item.chart_basis) for section in package.sections for item in section.items)
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

    assert any("身体怎样告诉你“要”还是“不要”" == item.title for section in body.sections for item in section.items)
    assert mission.professional_facts
    assert "纯生产者" in "\n".join(mission.professional_facts)
    assert "Authority：Sacral Authority" in "\n".join(mission.professional_facts)
    assert any(item.key == "mission.generator-cross" for section in mission.sections for item in section.items)


def test_every_user_map_is_a_complete_four_chapter_report() -> None:
    chart = _anonymous_0214_chart()
    for map_type in ("body", "wealth", "talent", "relationship", "mission"):
        package = build_interpretation_map(chart, map_type=map_type)
        items = [item for section in package.sections for item in section.items]
        assert len(package.sections) >= 4
        assert all(section.items for section in package.sections)
        assert all(item.user_language and item.chart_basis for item in items)
        assert any(item.life_scenes for item in items)
        assert any(item.embodied_expression for item in items)
        assert any(item.blind_spots for item in items)
        assert any(item.stuck_patterns for item in items)
        assert any(item.stuck_causes for item in items)
        assert any(item.practices for item in items)


def test_user_reports_are_compact_distinct_and_auditable() -> None:
    chart = _anonymous_0214_chart()
    for map_type in ("body", "wealth", "talent", "relationship", "mission"):
        package = build_interpretation_map(chart, map_type=map_type)
        assert len(package.sections) == 4
        assert all(len(section.items) == 1 for section in package.sections)

    audit = audit_report_content(chart)
    assert audit.score >= 90, audit.issues
    assert all(audit.checks.values()), audit.issues


def test_talent_wealth_and_mission_cover_every_defined_channel() -> None:
    chart = _anonymous_0214_chart()
    for map_type in ("talent", "wealth", "mission"):
        package = build_interpretation_map(chart, map_type=map_type)
        text = map_context_text(package)
        for channel in chart.channels:
            assert channel.code in text


def test_body_report_covers_every_center_state() -> None:
    chart = _anonymous_0214_chart()
    package = build_interpretation_map(chart, map_type="body")
    items = [item for section in package.sections for item in section.items]
    stable = next(item for item in items if item.key == "body.stable-resources")
    pressure = next(item for item in items if item.key == "body.open-pressure-chain")
    assert len(stable.chart_basis) == sum(center.defined for center in chart.centers)
    assert len(pressure.chart_basis) == sum(not center.defined for center in chart.centers)


def test_suggested_questions_only_reference_the_current_chart() -> None:
    chart = calculate_chart(normalize_birth_input("1991-07-12T09:40:00+08:00"))
    package = build_interpretation_map(chart, map_type="talent")
    questions = "\n".join(package.suggested_questions)

    assert "5/1" in questions
    assert "2/4" not in questions
    assert "02-14" not in questions


def test_mission_report_names_cross_and_four_core_activations() -> None:
    package = build_interpretation_map(_anonymous_0214_chart(), map_type="mission")
    theme = next(item for section in package.sections for item in section.items if item.key == "mission.cross-theme")

    assert theme.title.startswith("你的使命主题：")
    assert any(line.startswith("使命名称：") for line in theme.chart_basis)
    assert sum(any(label in line for label in ("人格太阳", "人格地球", "设计太阳", "设计地球")) for line in theme.chart_basis) == 4


def test_professional_map_uses_trace_diagnosis_without_long_sections() -> None:
    package = build_interpretation_map(_anonymous_0214_chart(), map_type="professional")
    items = [item for section in package.sections for item in section.items]

    assert items
    assert all(item.diagnosis_depth == "trace" for item in items)
    assert all(not item.embodied_expression for item in items)
    assert all(not item.stuck_causes for item in items)
    assert any(item.blind_spots for item in items)
    assert any(item.stuck_patterns for item in items)
