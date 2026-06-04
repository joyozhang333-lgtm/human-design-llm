from __future__ import annotations

from human_design.engine import calculate_chart
from human_design.input import normalize_birth_input
from human_design.interpretation_maps import build_interpretation_map, map_context_text
from human_design.research_corpus import load_interpretation_rules, load_knowledge_atoms, load_source_cards


def _zhang_chart():
    return calculate_chart(normalize_birth_input("1995-03-03T18:30:00+08:00"))


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
    package = build_interpretation_map(_zhang_chart(), map_type="talent", chart_id="chart_test")
    text = map_context_text(package)

    assert package.product_version == "0.3.0"
    assert package.map_type == "talent"
    assert package.title == "天赋地图"
    assert "人生角色：2/4" in package.professional_facts
    assert "已定义通道：02-14" in "\n".join(package.professional_facts)
    assert "2/4 天赋" in text
    assert "意识交叉" in text
    assert "独处养熟" in text
    assert "当前聚焦" not in text
    assert "焦点提示" not in text


def test_wealth_map_surfaces_money_source_and_promise_boundary() -> None:
    package = build_interpretation_map(_zhang_chart(), map_type="wealth")
    titles = [item.title for section in package.sections for item in section.items]

    assert "财富来源：方向感加资源配置" in titles
    assert "保财风险：错误承诺会吞掉生命力" in titles
    assert any("14号闸门" in "；".join(item.chart_basis) for section in package.sections for item in section.items)
    assert any("开放" in "；".join(item.chart_basis) and "意志" in "；".join(item.chart_basis) for section in package.sections for item in section.items)


def test_body_and_mission_maps_are_grounded_in_real_chart_facts() -> None:
    body = build_interpretation_map(_zhang_chart(), map_type="body")
    mission = build_interpretation_map(_zhang_chart(), map_type="mission")

    assert any("荐骨怎么真正参与选择" == item.title for section in body.sections for item in section.items)
    assert any("能量卡点从哪里开始" == item.title for section in body.sections for item in section.items)
    assert any("人生使命不是主动证明" in item.title for section in mission.sections for item in section.items)
    assert "纯生产者" in "\n".join(mission.professional_facts)
    assert "荐骨权威" in "\n".join(mission.professional_facts)
