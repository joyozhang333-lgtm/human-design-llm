from __future__ import annotations

from human_design.uncertainty import analyze_birth_time_range


def test_analyze_birth_time_range_returns_structured_result() -> None:
    result = analyze_birth_time_range(
        "1988-10-09T20:00:00",
        "1988-10-09T21:00:00",
        timezone_name="Asia/Shanghai",
        interval_minutes=30,
    )

    assert result.interval_minutes == 30
    assert result.sample_count == 3
    assert result.range_start_local == "1988-10-09T20:00:00+08:00"
    assert result.range_end_local == "1988-10-09T21:00:00+08:00"
    assert any(facet.key == "type" for facet in result.summary_facets)
    assert len(result.samples) == 3
    assert result.samples[0].birth_datetime_local == "1988-10-09T20:00:00+08:00"
    assert isinstance(result.variable_channels, tuple)
    assert isinstance(result.variable_gates, tuple)


def test_analyze_birth_time_range_serializes_to_json_friendly_payload() -> None:
    result = analyze_birth_time_range(
        "1988-10-09T20:00:00",
        "1988-10-09T20:30:00",
        timezone_name="Asia/Shanghai",
        interval_minutes=30,
    )
    payload = result.to_dict()

    assert payload["sample_count"] == 2
    assert payload["summary_facets"][0]["key"] == "type"
    assert "samples" in payload
