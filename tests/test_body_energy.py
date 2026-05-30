from __future__ import annotations

from human_design.body_energy import build_body_energy_profile
from human_design.engine import calculate_chart
from human_design.input import normalize_birth_input


def test_body_energy_profile_uses_simplified_chinese_terms() -> None:
    chart = calculate_chart(normalize_birth_input("1995-03-03T18:30:00+08:00"))
    profile = build_body_energy_profile(chart)
    payload = str(profile.to_dict())

    assert profile.headline == "身体资源与灵性能量地图"
    assert "荐骨中心" in payload
    assert "阿姬娜中心" in payload
    assert "喉咙中心" in payload
    assert "骶骨" not in payload
    assert "阿扎那" not in payload
    assert "额骨" not in payload
    assert "Pure Generator" not in payload
    assert "Sacral" not in payload
    assert len(profile.center_notes) == 9
    assert profile.energy_management


def test_body_energy_profile_surfaces_channels_and_observation_practices() -> None:
    chart = calculate_chart(normalize_birth_input("1995-03-03T18:30:00+08:00"))
    profile = build_body_energy_profile(chart)

    assert any(note.practice for note in profile.center_notes)
    assert any("消耗" in note.consumption_pattern or "卡点" in note.consumption_pattern for note in profile.center_notes)
    assert any(note.code == "02-14" for note in profile.channel_notes)
    assert profile.gate_notes
