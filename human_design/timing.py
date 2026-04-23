from __future__ import annotations

from datetime import UTC, datetime

from .engine import calculate_chart
from .input import NormalizedBirthInput
from .schema import (
    HumanDesignChart,
    TimingAnalysisResult,
    TimingCodeDelta,
    TimingIntDelta,
)


def analyze_timing(
    natal: HumanDesignChart | NormalizedBirthInput,
    transit: HumanDesignChart | NormalizedBirthInput,
    *,
    timing_label: str = "current",
) -> TimingAnalysisResult:
    natal_chart = natal if isinstance(natal, HumanDesignChart) else calculate_chart(natal)
    transit_chart = transit if isinstance(transit, HumanDesignChart) else calculate_chart(transit)
    natal_defined_centers = _defined_centers(natal_chart)
    transit_defined_centers = _defined_centers(transit_chart)

    centers = _code_delta(natal_defined_centers, transit_defined_centers)
    channels = _code_delta(_channel_codes(natal_chart), _channel_codes(transit_chart))
    gates = _int_delta(_gate_numbers(natal_chart), _gate_numbers(transit_chart))

    return TimingAnalysisResult(
        generated_at_utc=datetime.now(UTC).isoformat(),
        timing_label=timing_label,
        transit_datetime_local=transit_chart.input.birth_datetime_local,
        transit_datetime_utc=transit_chart.birth_datetime_utc,
        pressured_open_centers=centers.transit_only,
        anchored_defined_centers=centers.shared,
        centers=centers,
        channels=channels,
        gates=gates,
        natal_chart=natal_chart,
        transit_chart=transit_chart,
    )


def _defined_centers(chart: HumanDesignChart) -> tuple[str, ...]:
    return tuple(center.code for center in chart.centers if center.defined)


def _channel_codes(chart: HumanDesignChart) -> tuple[str, ...]:
    return tuple(channel.code for channel in chart.channels)


def _gate_numbers(chart: HumanDesignChart) -> tuple[int, ...]:
    return tuple(gate.gate for gate in chart.activated_gates)


def _code_delta(natal: tuple[str, ...], transit: tuple[str, ...]) -> TimingCodeDelta:
    natal_set = set(natal)
    transit_set = set(transit)
    return TimingCodeDelta(
        shared=tuple(item for item in natal if item in transit_set),
        natal_only=tuple(item for item in natal if item not in transit_set),
        transit_only=tuple(item for item in transit if item not in natal_set),
    )


def _int_delta(natal: tuple[int, ...], transit: tuple[int, ...]) -> TimingIntDelta:
    natal_set = set(natal)
    transit_set = set(transit)
    return TimingIntDelta(
        shared=tuple(item for item in natal if item in transit_set),
        natal_only=tuple(item for item in natal if item not in transit_set),
        transit_only=tuple(item for item in transit if item not in natal_set),
    )
