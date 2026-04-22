from __future__ import annotations

from human_design.knowledge import get_channel_card, get_gate_card, load_reference_index


def test_reference_index_has_gate_and_channel_collections() -> None:
    index = load_reference_index()

    assert "channels" in index["collections"]
    assert "gates" in index["collections"]


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
