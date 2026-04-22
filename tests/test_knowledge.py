from __future__ import annotations

from human_design.knowledge import (
    get_authority_card,
    get_center_card,
    get_channel_card,
    get_definition_card,
    get_gate_card,
    get_profile_card,
    get_type_card,
    load_reference_index,
)


def test_reference_index_has_core_collections() -> None:
    index = load_reference_index()

    assert "types" in index["collections"]
    assert "authorities" in index["collections"]
    assert "profiles" in index["collections"]
    assert "centers" in index["collections"]
    assert "definitions" in index["collections"]
    assert "channels" in index["collections"]
    assert "gates" in index["collections"]


def test_load_type_card() -> None:
    card = get_type_card("energy-projector")

    assert card is not None
    assert "精准引导能量" in card.summary
    assert len(card.gifts) >= 2


def test_load_authority_card() -> None:
    card = get_authority_card("ego-projected")

    assert card is not None
    assert "被看见的关系里说出来" in card.summary
    assert card.focus["decision"]


def test_load_profile_card() -> None:
    card = get_profile_card("2-4")

    assert card is not None
    assert "独处与被看见之间找到平衡" in card.summary


def test_load_definition_card() -> None:
    card = get_definition_card("single")

    assert card is not None
    assert "内部处理链路相对连贯" in card.summary


def test_load_center_card() -> None:
    card = get_center_card("g")

    assert card is not None
    assert card.title == "G 中心"
    assert "身份感" in card.defined
    assert "环境与关系来映照方向" in card.undefined


def test_load_channel_card() -> None:
    card = get_channel_card("25-51")

    assert card is not None
    assert "唤醒" in card.summary
    assert len(card.gifts) >= 2
    assert card.focus["career"]


def test_load_gate_card() -> None:
    card = get_gate_card(57)

    assert card is not None
    assert "直觉" in card.summary
    assert len(card.shadows) >= 2
    assert card.focus["decision"]
