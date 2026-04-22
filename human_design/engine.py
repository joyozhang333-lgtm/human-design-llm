from __future__ import annotations

import re
from collections import defaultdict
from datetime import UTC, datetime
from importlib import import_module
from typing import Any

from .input import (
    NormalizedBirthInput,
    normalize_birth_input,
    normalize_datetime,
    parse_birth_datetime,
)
from .pyhd_adapter import PYHD_UPSTREAM, load_pyhd_chart
from .schema import (
    ActivationRecord,
    CenterState,
    ChannelState,
    ChartSummary,
    DefinitionGroup,
    EngineInfo,
    GateActivationRef,
    GateState,
    HumanDesignChart,
    ImprintData,
    LabeledValue,
    VariableSet,
)

CENTER_DISPLAY_ORDER = {
    "head": 0,
    "ajna": 1,
    "throat": 2,
    "g": 3,
    "heart": 4,
    "spleen": 5,
    "solar-plexus": 6,
    "sacral": 7,
    "root": 8,
}

CODE_ALIASES = {
    "splenic": "spleen",
}


def calculate_chart(
    birth_datetime: datetime | NormalizedBirthInput,
) -> HumanDesignChart:
    chart_cls, pyhd_version, engine_notes = load_pyhd_chart()
    if isinstance(birth_datetime, NormalizedBirthInput):
        normalized = birth_datetime
    else:
        normalized = normalize_birth_input(birth_datetime)
    birth_utc = normalize_datetime(normalized.birth_datetime_utc)
    raw_chart = chart_cls(birth_utc)
    centers_enum = import_module("pyhd.constants").Centers

    personality = _build_imprint("personality", raw_chart.personality)
    design = _build_imprint("design", raw_chart.design)
    centers = tuple(
        sorted(
            (
                CenterState(
                    code=_enum_code(center),
                    label=_enum_label(center),
                    defined=center in raw_chart.centers,
                )
                for center in centers_enum
            ),
            key=lambda center: CENTER_DISPLAY_ORDER.get(center.code, 999),
        )
    )

    activations_by_gate: dict[int, list[ActivationRecord]] = defaultdict(list)
    for activation in personality.activations + design.activations:
        activations_by_gate[activation.gate].append(activation)

    return HumanDesignChart(
        generated_at_utc=datetime.now(UTC).isoformat(),
        birth_datetime_utc=personality.datetime_utc,
        design_datetime_utc=design.datetime_utc,
        input=normalized.chart_input,
        engine=EngineInfo(
            name="pyhd",
            version=pyhd_version,
            upstream=PYHD_UPSTREAM,
            notes=engine_notes,
        ),
        summary=ChartSummary(
            type=_enum_value(raw_chart.type),
            strategy=_enum_value(raw_chart.strategy),
            authority=_enum_value(raw_chart.authority),
            profile=_enum_value(raw_chart.profile),
            definition=_enum_value(raw_chart.definition_type),
            signature=_enum_value(raw_chart.signature),
            not_self_theme=_enum_value(raw_chart.not_self_theme),
            incarnation_cross=_enum_value(raw_chart.cross),
        ),
        variables=VariableSet(
            orientation=LabeledValue(
                code=_slug(str(raw_chart.variable_orientations)),
                label=str(raw_chart.variable_orientations),
            ),
            determination=_enum_value(raw_chart.determination),
            cognition=_enum_value(raw_chart.cognition),
            environment=_enum_value(raw_chart.environment),
            perspective=_enum_value(raw_chart.perspective),
            motivation=_enum_value(raw_chart.motivation),
            sense=_enum_value(raw_chart.sense),
        ),
        definitions=tuple(
            DefinitionGroup(centers=tuple(_enum_code(center) for center in group))
            for group in raw_chart.definitions
        ),
        centers=centers,
        channels=tuple(
            ChannelState(
                code=channel.name,
                label=_enum_label(channel),
                gates=tuple(gate.num for gate in channel.gates),
                centers=tuple(_enum_code(center) for center in channel.centers),
                channel_type=_enum_value(channel.channel_type),
                circuit=_enum_value(channel.circuit),
                circuit_group=_enum_value(channel.circuit_group),
                is_creative=bool(channel.is_creative),
            )
            for channel in raw_chart.channels
        ),
        activated_gates=tuple(
            GateState(
                gate=gate.num,
                label=str(gate.num),
                theme=gate.gate_of,
                title=gate.title,
                center=_enum_code(gate.center),
                quarter=_enum_label(gate.quarter),
                channels=tuple(channel.name for channel in gate.channels),
                harmonic_gates=tuple(
                    sorted({channel.harmonic_gate(gate).num for channel in gate.channels})
                ),
                activations=tuple(
                    GateActivationRef(
                        imprint=activation.imprint,
                        planet_code=activation.planet_code,
                        planet_label=activation.planet_label,
                        line=activation.line,
                        color=activation.color,
                        tone=activation.tone,
                        base=activation.base,
                    )
                    for activation in activations_by_gate[gate.num]
                ),
            )
            for gate in raw_chart.gates
        ),
        personality=personality,
        design=design,
    )


def _build_imprint(imprint_name: str, imprint: Any) -> ImprintData:
    return ImprintData(
        datetime_utc=normalize_datetime(imprint.dt).isoformat(),
        activations=tuple(
            ActivationRecord(
                imprint=imprint_name,
                planet_code=_enum_code(planet),
                planet_label=_enum_label(planet),
                planet_symbol=getattr(planet, "symbol", None),
                longitude=round(activation.longitude, 6),
                gate=activation.gate.num,
                gate_label=str(activation.gate.num),
                gate_theme=activation.gate.gate_of,
                gate_title=activation.gate.title,
                line=activation.line.num,
                color=activation.color.num,
                tone=activation.tone.num,
                base=activation.base.num,
            )
            for planet, activation in imprint.items()
        ),
    )


def _enum_value(value: Any) -> LabeledValue:
    return LabeledValue(code=_enum_code(value), label=_enum_label(value))


def _enum_code(value: Any) -> str:
    raw = getattr(value, "_key", None)
    if raw is None:
        raw = str(value)
    code = _slug(str(raw).strip("_"))
    return CODE_ALIASES.get(code, code)


def _enum_label(value: Any) -> str:
    return getattr(value, "full_name", str(value))
def _slug(raw: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
