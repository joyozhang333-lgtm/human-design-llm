from __future__ import annotations

from datetime import UTC, datetime

from .engine import calculate_chart
from .input import NormalizedBirthInput
from .schema import (
    HumanDesignChart,
    LabeledValue,
    RelationshipCodeDelta,
    RelationshipComparisonResult,
    RelationshipFacetComparison,
    RelationshipIntDelta,
)

SUMMARY_KEYS = ("type", "strategy", "authority", "profile", "definition")


def compare_relationship(
    left: HumanDesignChart | NormalizedBirthInput,
    right: HumanDesignChart | NormalizedBirthInput,
    *,
    left_label: str = "A",
    right_label: str = "B",
) -> RelationshipComparisonResult:
    left_chart = left if isinstance(left, HumanDesignChart) else calculate_chart(left)
    right_chart = right if isinstance(right, HumanDesignChart) else calculate_chart(right)
    return RelationshipComparisonResult(
        generated_at_utc=datetime.now(UTC).isoformat(),
        left_label=left_label,
        right_label=right_label,
        summary_facets=_build_summary_facets(left_chart, right_chart),
        centers=_code_delta(_defined_centers(left_chart), _defined_centers(right_chart)),
        channels=_code_delta(_channel_codes(left_chart), _channel_codes(right_chart)),
        gates=_int_delta(_gate_numbers(left_chart), _gate_numbers(right_chart)),
        left_chart=left_chart,
        right_chart=right_chart,
    )


def _build_summary_facets(
    left_chart: HumanDesignChart,
    right_chart: HumanDesignChart,
) -> tuple[RelationshipFacetComparison, ...]:
    facets: list[RelationshipFacetComparison] = []
    for key in SUMMARY_KEYS:
        left_value = getattr(left_chart.summary, key)
        right_value = getattr(right_chart.summary, key)
        facets.append(
            RelationshipFacetComparison(
                key=key,
                left=left_value,
                right=right_value,
                same=left_value.code == right_value.code,
            )
        )
    return tuple(facets)


def _defined_centers(chart: HumanDesignChart) -> tuple[str, ...]:
    return tuple(center.code for center in chart.centers if center.defined)


def _channel_codes(chart: HumanDesignChart) -> tuple[str, ...]:
    return tuple(channel.code for channel in chart.channels)


def _gate_numbers(chart: HumanDesignChart) -> tuple[int, ...]:
    return tuple(gate.gate for gate in chart.activated_gates)


def _code_delta(left: tuple[str, ...], right: tuple[str, ...]) -> RelationshipCodeDelta:
    left_set = set(left)
    right_set = set(right)
    return RelationshipCodeDelta(
        shared=tuple(item for item in left if item in right_set),
        left_only=tuple(item for item in left if item not in right_set),
        right_only=tuple(item for item in right if item not in left_set),
    )


def _int_delta(left: tuple[int, ...], right: tuple[int, ...]) -> RelationshipIntDelta:
    left_set = set(left)
    right_set = set(right)
    return RelationshipIntDelta(
        shared=tuple(item for item in left if item in right_set),
        left_only=tuple(item for item in left if item not in right_set),
        right_only=tuple(item for item in right if item not in left_set),
    )
