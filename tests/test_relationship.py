from __future__ import annotations

from human_design.input import normalize_birth_input
from human_design.relationship import compare_relationship


def test_compare_relationship_returns_structured_deltas() -> None:
    left = normalize_birth_input("1988-10-09T20:30:00+08:00")
    right = normalize_birth_input("1992-01-03T06:15:00-05:00")
    result = compare_relationship(left, right, left_label="Left", right_label="Right")

    assert result.left_label == "Left"
    assert result.right_label == "Right"
    assert len(result.summary_facets) == 5
    assert any(facet.key == "authority" for facet in result.summary_facets)
    assert isinstance(result.centers.shared, tuple)
    assert isinstance(result.channels.left_only, tuple)
    assert isinstance(result.gates.right_only, tuple)
    assert result.left_chart.summary.type.code
    assert result.right_chart.summary.type.code


def test_compare_relationship_is_json_friendly() -> None:
    left = normalize_birth_input("1988-10-09T20:30:00+08:00")
    right = normalize_birth_input("2001-06-21T14:45:00", timezone_name="Europe/London")
    payload = compare_relationship(left, right).to_dict()

    assert payload["summary_facets"][0]["key"] == "type"
    assert "centers" in payload
    assert "channels" in payload
    assert "gates" in payload
