from __future__ import annotations

from pathlib import Path

from human_design.engine import calculate_chart
from human_design.content_audit import audit_report_content
from human_design.input import normalize_birth_input
from human_design.interpretation_maps import build_interpretation_map, map_context_text
from human_design.research_corpus import load_interpretation_rules, load_knowledge_atoms, load_source_cards


def _anonymous_0214_chart():
    return calculate_chart(normalize_birth_input("1970-02-04T12:00:00+08:00"))


def _anonymous_reflector_chart():
    return calculate_chart(normalize_birth_input("1980-11-18T00:00:00+08:00"))


def _anonymous_fully_defined_chart():
    return calculate_chart(normalize_birth_input("2007-10-05T04:28:00+08:00"))


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


def test_packaged_research_corpus_matches_the_maintained_reference_copy() -> None:
    root = Path(__file__).resolve().parents[1]
    maintained = root / "references" / "research-corpus" / "v0.3"
    packaged = root / "human_design" / "assets" / "research-corpus" / "v0.3"

    for filename in ("sources.json", "knowledge_atoms.json", "interpretation_rules.json"):
        assert (packaged / filename).read_bytes() == (maintained / filename).read_bytes()


def test_talent_map_uses_profile_channel_cross_and_user_language() -> None:
    package = build_interpretation_map(_anonymous_0214_chart(), map_type="talent", chart_id="chart_test")
    text = map_context_text(package)

    assert package.product_version == "0.7.0"
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


def test_every_user_map_is_a_complete_readable_report() -> None:
    chart = _anonymous_0214_chart()
    for map_type in ("body", "channels", "wealth", "talent", "relationship", "mission"):
        package = build_interpretation_map(chart, map_type=map_type)
        items = [item for section in package.sections for item in section.items]
        assert 1 <= len(package.sections) <= 5
        assert all(section.items for section in package.sections)
        assert all(item.user_language and item.chart_basis for item in items)
        assert any(item.life_scenes for item in items)
        assert any(item.embodied_expression for item in items)
        assert any(item.blind_spots for item in items)
        assert any(item.stuck_patterns for item in items)
        assert any(item.stuck_causes for item in items)
        assert any(item.practices for item in items)


def test_report_depth_changes_the_diagnostic_payload() -> None:
    chart = _anonymous_0214_chart()
    brief = build_interpretation_map(chart, map_type="wealth", depth="brief")
    standard = build_interpretation_map(chart, map_type="wealth", depth="standard")
    deep = build_interpretation_map(chart, map_type="wealth", depth="deep")

    brief_items = [item for section in brief.sections for item in section.items]
    standard_items = [item for section in standard.sections for item in section.items]
    deep_items = [item for section in deep.sections for item in section.items]

    assert len(brief.suggested_questions) < len(deep.suggested_questions)
    assert all(item.diagnosis_depth == "trace" for item in brief_items)
    assert all(not item.blind_spots and not item.stuck_causes for item in brief_items)
    assert any(item.blind_spots for item in standard_items)
    assert all(not item.stuck_causes for item in standard_items)
    assert any(item.diagnosis_depth == "deep" and item.stuck_causes for item in deep_items)


def test_user_reports_are_compact_distinct_and_auditable() -> None:
    chart = _anonymous_0214_chart()
    for map_type in ("body", "channels", "wealth", "talent", "relationship", "mission"):
        package = build_interpretation_map(chart, map_type=map_type)
        assert package.sections
        assert all(section.items for section in package.sections)

    audit = audit_report_content(chart)
    assert audit.score >= 90, audit.issues
    assert all(audit.checks.values()), audit.issues


def test_reflector_reports_explain_environment_without_empty_facts() -> None:
    chart = _anonymous_reflector_chart()
    assert chart.summary.type.code == "reflector"
    assert not chart.channels
    assert not any(center.defined for center in chart.centers)

    packages = {
        map_type: build_interpretation_map(chart, map_type=map_type)
        for map_type in ("body", "channels", "wealth", "talent", "relationship", "mission")
    }
    all_items = [
        item
        for package in packages.values()
        for section in package.sections
        for item in section.items
    ]
    assert all(item.chart_basis for item in all_items)
    assert "九个中心均开放" in map_context_text(packages["body"])
    assert "能力成熟" in map_context_text(packages["channels"])
    assert "先选对场域" in map_context_text(packages["mission"])

    audit = audit_report_content(chart)
    assert audit.score == 100, audit.issues
    assert all(audit.checks.values()), audit.issues


def test_fully_defined_chart_reports_explain_overuse_without_open_center_placeholders() -> None:
    chart = _anonymous_fully_defined_chart()
    assert all(center.defined for center in chart.centers)

    packages = {
        map_type: build_interpretation_map(chart, map_type=map_type)
        for map_type in ("body", "wealth", "relationship")
    }
    items = [
        item
        for package in packages.values()
        for section in package.sections
        for item in section.items
    ]
    assert all(item.chart_basis for item in items)
    assert "全天候有责任" in map_context_text(packages["body"])
    assert "九个中心均已定义" in map_context_text(packages["wealth"])
    assert "各自完整" in map_context_text(packages["relationship"])

    audit = audit_report_content(chart)
    assert audit.score == 100, audit.issues
    assert all(audit.checks.values()), audit.issues


def test_channel_report_explains_every_actual_channel() -> None:
    chart = _anonymous_0214_chart()
    package = build_interpretation_map(chart, map_type="channels")
    items = {item.key: item for section in package.sections for item in section.items}

    assert package.title == "通道报告"
    for channel in chart.channels:
        item = items[f"channels.{channel.code}"]
        assert channel.code in "\n".join(item.chart_basis)
        assert item.embodied_expression
        assert item.blind_spots
        assert item.stuck_patterns
        assert item.stuck_causes


def test_single_channel_reports_use_singular_language_and_exact_authority() -> None:
    chart = calculate_chart(normalize_birth_input("1988-10-09T20:30:00+08:00"))
    assert len(chart.channels) == 1
    packages = {
        map_type: build_interpretation_map(chart, map_type=map_type)
        for map_type in ("body", "channels", "talent", "wealth", "mission")
    }
    text = "\n".join(map_context_text(package) for package in packages.values())

    assert "talent.channel-25-51" in {
        item.key for section in packages["talent"].sections for item in section.items
    }
    assert "它们不会一条一条" not in text
    assert "分别卖一次" not in text
    assert "一部分能力" not in text
    assert "有的负责看见" not in text
    assert "自我投射的Ego Authority" not in text
    assert "Ego Projected Authority" in text
    assert "先先" not in text
    assert "它们" not in packages["channels"].description
    assert all("多条通道" not in question for question in packages["channels"].suggested_questions)
    assert any("这条通道" in question for question in packages["channels"].suggested_questions)
    assert audit_report_content(chart).score >= 90


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
