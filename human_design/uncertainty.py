from __future__ import annotations

from datetime import UTC, datetime

from .engine import calculate_chart
from .input import (
    LocationResolver,
    normalize_birth_time_range,
)
from .schema import (
    ChartRangeSample,
    ChartSummary,
    ChartUncertaintyResult,
    HumanDesignChart,
    LabeledValue,
    UncertaintyFacet,
)

SUMMARY_KEYS = (
    "type",
    "strategy",
    "authority",
    "profile",
    "definition",
    "signature",
    "not_self_theme",
    "incarnation_cross",
)


def analyze_birth_time_range(
    start_birth_time: str | datetime,
    end_birth_time: str | datetime,
    *,
    timezone_name: str | None = None,
    city: str | None = None,
    region: str | None = None,
    country: str | None = None,
    interval_minutes: int = 30,
    location_resolver: LocationResolver | None = None,
) -> ChartUncertaintyResult:
    normalized_range = normalize_birth_time_range(
        start_birth_time,
        end_birth_time,
        timezone_name=timezone_name,
        city=city,
        region=region,
        country=country,
        interval_minutes=interval_minutes,
        location_resolver=location_resolver,
    )
    charts = tuple(calculate_chart(sample) for sample in normalized_range.samples)
    if not charts:
        raise ValueError("至少需要一个区间样本来分析人类图不确定性。")

    samples = tuple(_build_sample(chart) for chart in charts)
    return ChartUncertaintyResult(
        generated_at_utc=datetime.now(UTC).isoformat(),
        interval_minutes=normalized_range.interval_minutes,
        sample_count=len(charts),
        range_start_local=charts[0].input.birth_datetime_local,
        range_end_local=charts[-1].input.birth_datetime_local,
        range_start_utc=charts[0].birth_datetime_utc,
        range_end_utc=charts[-1].birth_datetime_utc,
        summary_facets=_build_summary_facets(tuple(chart.summary for chart in charts)),
        stable_centers=_stable_codes(tuple(_defined_centers(chart) for chart in charts)),
        variable_centers=_variable_codes(tuple(_defined_centers(chart) for chart in charts)),
        stable_channels=_stable_codes(tuple(_channel_codes(chart) for chart in charts)),
        variable_channels=_variable_codes(tuple(_channel_codes(chart) for chart in charts)),
        stable_gates=_stable_ints(tuple(_gate_numbers(chart) for chart in charts)),
        variable_gates=_variable_ints(tuple(_gate_numbers(chart) for chart in charts)),
        samples=samples,
    )


def _build_sample(chart: HumanDesignChart) -> ChartRangeSample:
    return ChartRangeSample(
        birth_datetime_local=chart.input.birth_datetime_local,
        birth_datetime_utc=chart.birth_datetime_utc,
        summary=chart.summary,
        defined_centers=_defined_centers(chart),
        channels=_channel_codes(chart),
        activated_gates=_gate_numbers(chart),
    )


def _build_summary_facets(summaries: tuple[ChartSummary, ...]) -> tuple[UncertaintyFacet, ...]:
    facets: list[UncertaintyFacet] = []
    for key in SUMMARY_KEYS:
        values = _unique_labeled_values(tuple(getattr(summary, key) for summary in summaries))
        facets.append(
            UncertaintyFacet(
                key=key,
                values=values,
                stable=len(values) == 1,
            )
        )
    return tuple(facets)


def _unique_labeled_values(values: tuple[LabeledValue, ...]) -> tuple[LabeledValue, ...]:
    seen: set[str] = set()
    unique: list[LabeledValue] = []
    for value in values:
        if value.code in seen:
            continue
        seen.add(value.code)
        unique.append(value)
    return tuple(unique)


def _defined_centers(chart: HumanDesignChart) -> tuple[str, ...]:
    return tuple(center.code for center in chart.centers if center.defined)


def _channel_codes(chart: HumanDesignChart) -> tuple[str, ...]:
    return tuple(channel.code for channel in chart.channels)


def _gate_numbers(chart: HumanDesignChart) -> tuple[int, ...]:
    return tuple(gate.gate for gate in chart.activated_gates)


def _stable_codes(samples: tuple[tuple[str, ...], ...]) -> tuple[str, ...]:
    if not samples:
        return ()
    stable = set(samples[0])
    for sample in samples[1:]:
        stable &= set(sample)
    return tuple(item for item in samples[0] if item in stable)


def _variable_codes(samples: tuple[tuple[str, ...], ...]) -> tuple[str, ...]:
    if not samples:
        return ()
    stable = set(_stable_codes(samples))
    union: list[str] = []
    seen: set[str] = set()
    for sample in samples:
        for item in sample:
            if item in seen or item in stable:
                continue
            seen.add(item)
            union.append(item)
    return tuple(union)


def _stable_ints(samples: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    if not samples:
        return ()
    stable = set(samples[0])
    for sample in samples[1:]:
        stable &= set(sample)
    return tuple(item for item in samples[0] if item in stable)


def _variable_ints(samples: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    if not samples:
        return ()
    stable = set(_stable_ints(samples))
    union: list[int] = []
    seen: set[int] = set()
    for sample in samples:
        for item in sample:
            if item in seen or item in stable:
                continue
            seen.add(item)
            union.append(item)
    return tuple(union)
