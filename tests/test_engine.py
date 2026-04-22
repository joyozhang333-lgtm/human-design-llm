from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from human_design.engine import calculate_chart, parse_birth_datetime
from human_design.input import normalize_birth_input

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "chart_cases.json"


def test_parse_birth_datetime_assumes_utc_for_naive_values() -> None:
    parsed = parse_birth_datetime("1988-10-09T12:30:00")

    assert parsed == datetime(1988, 10, 9, 12, 30, tzinfo=UTC)


def test_calculate_chart_returns_unified_schema() -> None:
    chart = calculate_chart(datetime(1988, 10, 9, 12, 30, tzinfo=UTC))

    assert chart.engine.name == "pyhd"
    assert chart.summary.type.code == "energy-projector"
    assert chart.summary.authority.code == "ego-projected"
    assert chart.summary.profile.code == "2-4"
    assert chart.summary.definition.code == "single"
    assert [channel.code for channel in chart.channels] == ["25-51"]
    assert [center.code for center in chart.centers if center.defined] == ["g", "heart"]
    assert chart.variables.orientation.label == "PLR DRR"

    personality_sun = next(
        activation
        for activation in chart.personality.activations
        if activation.planet_code == "sun"
    )
    design_sun = next(
        activation
        for activation in chart.design.activations
        if activation.planet_code == "sun"
    )

    assert personality_sun.gate == 57
    assert personality_sun.line == 2
    assert design_sun.gate == 53
    assert design_sun.line == 4

    payload = chart.to_dict()
    assert payload["summary"]["type"]["label"] == "Energy Projector"
    assert payload["activated_gates"][0]["gate"] == 8
    assert payload["input"]["source_precision"] == "explicit-offset"
    json.dumps(payload, ensure_ascii=False)


@pytest.mark.parametrize("fixture", json.loads(FIXTURE_PATH.read_text(encoding="utf-8")))
def test_chart_golden_fixtures(fixture: dict) -> None:
    normalized = normalize_birth_input(**fixture["input"])
    chart = calculate_chart(normalized)
    expected = fixture["expected"]

    personality_sun = next(
        activation
        for activation in chart.personality.activations
        if activation.planet_code == "sun"
    )
    personality_earth = next(
        activation
        for activation in chart.personality.activations
        if activation.planet_code == "earth"
    )
    design_sun = next(
        activation
        for activation in chart.design.activations
        if activation.planet_code == "sun"
    )
    design_earth = next(
        activation
        for activation in chart.design.activations
        if activation.planet_code == "earth"
    )

    assert chart.input.source_precision == expected["source_precision"], fixture["id"]
    assert chart.summary.type.code == expected["type"], fixture["id"]
    assert chart.summary.authority.code == expected["authority"], fixture["id"]
    assert chart.summary.profile.code == expected["profile"], fixture["id"]
    assert chart.summary.definition.code == expected["definition"], fixture["id"]
    assert [channel.code for channel in chart.channels] == expected["channels"], fixture["id"]
    assert (
        personality_sun.gate,
        personality_sun.line,
    ) == (
        expected["personality_sun"]["gate"],
        expected["personality_sun"]["line"],
    ), fixture["id"]
    assert (
        personality_earth.gate,
        personality_earth.line,
    ) == (
        expected["personality_earth"]["gate"],
        expected["personality_earth"]["line"],
    ), fixture["id"]
    assert (
        design_sun.gate,
        design_sun.line,
    ) == (
        expected["design_sun"]["gate"],
        expected["design_sun"]["line"],
    ), fixture["id"]
    assert (
        design_earth.gate,
        design_earth.line,
    ) == (
        expected["design_earth"]["gate"],
        expected["design_earth"]["line"],
    ), fixture["id"]
