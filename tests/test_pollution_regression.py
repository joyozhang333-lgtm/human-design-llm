"""V0.5 P0 污染回归：fallback-to-professional 已从根删除，永不复发。

样本盘 = 真实取证盘（投射者 / 2-4 / 意志力权威 / 一分人）：
wealth/mission 无规则匹配时，绝不能再把开发者方法论当用户内容渲染。
"""
from __future__ import annotations

import pytest

from human_design.engine import calculate_chart
from human_design.input import normalize_birth_input
from human_design.interpretation_maps import build_interpretation_map

POLLUTION_BLACKLIST = (
    "chart facts",
    "专业信息必须",
    "专业依据必须",
    "方便后续",
    "回到图表事实",
    "知识原子",
    "产品价值",
    "门线解读",
    "系统有没有编造",
    "盘面机制：这个条目必须",
)


@pytest.fixture(scope="module")
def cold_config_chart():
    # 该盘在 wealth/mission 下没有任何匹配规则（历史上正是它触发污染）。
    return calculate_chart(normalize_birth_input("1988-10-09T20:30:00+08:00", timezone_name="Asia/Shanghai"))


def _all_item_text(package) -> str:
    chunks: list[str] = []
    for section in package.sections:
        chunks.append(section.title)
        chunks.append(section.intro)
        for item in section.items:
            chunks.extend(
                (
                    item.key,
                    item.title,
                    item.subtitle,
                    item.professional_basis,
                    item.user_language,
                    *item.chart_basis,
                    *item.life_scenes,
                    *item.embodied_expression,
                    *item.blind_spots,
                    *item.stuck_patterns,
                    *item.stuck_causes,
                    *item.common_blocks,
                    *item.practices,
                    *item.followup_questions,
                )
            )
    return "\n".join(chunks)


@pytest.mark.parametrize("map_type", ["wealth", "mission", "body", "talent", "relationship"])
def test_cold_config_maps_never_fall_back_to_professional(cold_config_chart, map_type) -> None:
    package = build_interpretation_map(cold_config_chart, map_type=map_type)
    for section in package.sections:
        for item in section.items:
            assert not item.key.startswith("professional."), item.key
    text = _all_item_text(package).lower()
    for banned in POLLUTION_BLACKLIST:
        assert banned.lower() not in text, banned


def test_cold_config_wealth_mission_have_grounded_reports(cold_config_chart) -> None:
    for map_type in ("wealth", "mission"):
        package = build_interpretation_map(cold_config_chart, map_type=map_type)
        items = [item for section in package.sections for item in section.items]
        assert items, f"{map_type} 必须有完整解读"
        assert len(package.sections) >= 4
        assert items[0].key.startswith(f"{map_type}.")
        assert items[0].chart_basis
        assert items[0].user_language
        assert all("宁可先空着" not in section.intro for section in package.sections)


def test_professional_map_has_no_methodology_in_user_fields(cold_config_chart) -> None:
    package = build_interpretation_map(cold_config_chart, map_type="professional")
    for section in package.sections:
        for item in section.items:
            assert item.professional_basis == "", item.key
            lowered = (item.subtitle + item.user_language).lower()
            for banned in ("chart facts", "专业依据必须", "回到图表事实"):
                assert banned not in lowered


def test_matched_rules_still_produce_content_for_known_chart() -> None:
    chart = calculate_chart(normalize_birth_input("1970-02-04T12:00:00+08:00"))
    package = build_interpretation_map(chart, map_type="wealth")
    items = [item for section in package.sections for item in section.items]
    assert items, "有规则匹配的盘不应为空"
    assert all(item.key.startswith("wealth.") for item in items)
