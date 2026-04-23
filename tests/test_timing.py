from __future__ import annotations

from human_design.input import normalize_birth_input
from human_design.timing import analyze_timing


def test_analyze_timing_returns_structured_result() -> None:
    natal = normalize_birth_input("1988-10-09T20:30:00+08:00")
    transit = normalize_birth_input("2026-04-23T10:00:00+08:00")
    result = analyze_timing(natal, transit, timing_label="today")

    assert result.timing_label == "today"
    assert result.transit_datetime_local.endswith("+08:00")
    assert isinstance(result.centers.shared, tuple)
    assert isinstance(result.channels.transit_only, tuple)
    assert isinstance(result.gates.natal_only, tuple)
    assert result.natal_chart.summary.type.code
    assert result.transit_chart.channels is not None


def test_analyze_timing_is_json_friendly() -> None:
    natal = normalize_birth_input("1992-01-03T06:15:00-05:00")
    transit = normalize_birth_input("2026-04-23T09:00:00", timezone_name="Asia/Shanghai")
    payload = analyze_timing(natal, transit).to_dict()

    assert payload["timing_label"] == "current"
    assert "centers" in payload
    assert "channels" in payload
    assert "gates" in payload
