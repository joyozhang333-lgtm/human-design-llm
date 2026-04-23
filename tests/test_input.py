from __future__ import annotations

from datetime import UTC, datetime

import pytest

from human_design.input import (
    InputNormalizationError,
    NominatimLocationResolver,
    normalize_birth_input,
    normalize_birth_time_range,
)
from human_design.schema import InputLocation


class FakeLocationResolver(NominatimLocationResolver):
    def __init__(self, location: InputLocation) -> None:
        self._location = location

    def resolve(self, city: str, region: str | None, country: str | None) -> InputLocation:
        return self._location


def test_normalize_birth_input_uses_explicit_offset() -> None:
    normalized = normalize_birth_input("1988-10-09T20:30:00+08:00")

    assert normalized.birth_datetime_utc == datetime(1988, 10, 9, 12, 30, tzinfo=UTC)
    assert normalized.chart_input.birth_datetime_local == "1988-10-09T20:30:00+08:00"
    assert normalized.chart_input.timezone_name == "UTC+08:00"
    assert normalized.chart_input.source_precision == "explicit-offset"
    assert normalized.chart_input.warnings == ()


def test_normalize_birth_input_uses_timezone_name() -> None:
    normalized = normalize_birth_input(
        "1988-10-09T20:30:00",
        timezone_name="Asia/Shanghai",
    )

    assert normalized.birth_datetime_utc == datetime(1988, 10, 9, 12, 30, tzinfo=UTC)
    assert normalized.chart_input.birth_datetime_local == "1988-10-09T20:30:00+08:00"
    assert normalized.chart_input.timezone_name == "Asia/Shanghai"
    assert normalized.chart_input.source_precision == "timezone-name"


def test_normalize_birth_input_resolves_city_timezone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    location = InputLocation(
        query="Shanghai, China",
        name="Shanghai, China",
        latitude=31.2304,
        longitude=121.4737,
    )
    resolver = FakeLocationResolver(location)
    monkeypatch.setattr(
        "human_design.input._resolve_timezone_from_coordinates",
        lambda resolved: "Asia/Shanghai",
    )

    normalized = normalize_birth_input(
        "1988-10-09T20:30:00",
        city="Shanghai",
        country="China",
        location_resolver=resolver,
    )

    assert normalized.birth_datetime_utc == datetime(1988, 10, 9, 12, 30, tzinfo=UTC)
    assert normalized.chart_input.source_precision == "city-resolved"
    assert normalized.chart_input.location == location
    assert normalized.chart_input.timezone_name == "Asia/Shanghai"
    assert any("IANA 时区" in warning for warning in normalized.chart_input.warnings)


def test_normalize_birth_input_warns_when_timezone_missing() -> None:
    normalized = normalize_birth_input("1988-10-09T12:30:00")

    assert normalized.birth_datetime_utc == datetime(1988, 10, 9, 12, 30, tzinfo=UTC)
    assert normalized.chart_input.source_precision == "assumed-utc"
    assert normalized.chart_input.timezone_name == "UTC"
    assert normalized.chart_input.warnings == (
        "出生时间未提供时区，当前按 UTC 处理；这会影响人类图结果精度。",
    )


def test_normalize_birth_input_rejects_unknown_timezone() -> None:
    with pytest.raises(InputNormalizationError):
        normalize_birth_input("1988-10-09T20:30:00", timezone_name="Mars/Base")


def test_normalize_birth_time_range_builds_multiple_samples() -> None:
    normalized = normalize_birth_time_range(
        "1988-10-09T20:00:00",
        "1988-10-09T21:00:00",
        timezone_name="Asia/Shanghai",
        interval_minutes=30,
    )

    assert normalized.interval_minutes == 30
    assert len(normalized.samples) == 3
    assert normalized.samples[0].chart_input.birth_datetime_local == "1988-10-09T20:00:00+08:00"
    assert normalized.samples[-1].chart_input.birth_datetime_local == "1988-10-09T21:00:00+08:00"


def test_normalize_birth_time_range_rejects_mixed_timezone_awareness() -> None:
    with pytest.raises(InputNormalizationError):
        normalize_birth_time_range(
            "1988-10-09T20:00:00+08:00",
            "1988-10-09T21:00:00",
        )
