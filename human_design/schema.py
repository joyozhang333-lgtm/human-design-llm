from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class JsonMixin:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LabeledValue(JsonMixin):
    code: str
    label: str


@dataclass(frozen=True)
class EngineInfo(JsonMixin):
    name: str
    version: str | None
    upstream: str
    notes: tuple[str, ...]


@dataclass(frozen=True)
class InputLocation(JsonMixin):
    query: str
    name: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class ChartInput(JsonMixin):
    raw_birth_time: str
    birth_datetime_local: str
    timezone_name: str
    source_precision: str
    warnings: tuple[str, ...]
    location: InputLocation | None


@dataclass(frozen=True)
class ActivationRecord(JsonMixin):
    imprint: str
    planet_code: str
    planet_label: str
    planet_symbol: str | None
    longitude: float
    gate: int
    gate_label: str
    gate_theme: str
    gate_title: str
    line: int
    color: int
    tone: int
    base: int


@dataclass(frozen=True)
class ImprintData(JsonMixin):
    datetime_utc: str
    activations: tuple[ActivationRecord, ...]


@dataclass(frozen=True)
class CenterState(JsonMixin):
    code: str
    label: str
    defined: bool


@dataclass(frozen=True)
class DefinitionGroup(JsonMixin):
    centers: tuple[str, ...]


@dataclass(frozen=True)
class ChannelState(JsonMixin):
    code: str
    label: str
    gates: tuple[int, int]
    centers: tuple[str, str]
    channel_type: LabeledValue
    circuit: LabeledValue
    circuit_group: LabeledValue
    is_creative: bool


@dataclass(frozen=True)
class GateActivationRef(JsonMixin):
    imprint: str
    planet_code: str
    planet_label: str
    line: int
    color: int
    tone: int
    base: int


@dataclass(frozen=True)
class GateState(JsonMixin):
    gate: int
    label: str
    theme: str
    title: str
    center: str
    quarter: str
    channels: tuple[str, ...]
    harmonic_gates: tuple[int, ...]
    activations: tuple[GateActivationRef, ...]


@dataclass(frozen=True)
class ChartSummary(JsonMixin):
    type: LabeledValue
    strategy: LabeledValue
    authority: LabeledValue
    profile: LabeledValue
    definition: LabeledValue
    signature: LabeledValue
    not_self_theme: LabeledValue
    incarnation_cross: LabeledValue


@dataclass(frozen=True)
class VariableSet(JsonMixin):
    orientation: LabeledValue
    determination: LabeledValue
    cognition: LabeledValue
    environment: LabeledValue
    perspective: LabeledValue
    motivation: LabeledValue
    sense: LabeledValue


@dataclass(frozen=True)
class UncertaintyFacet(JsonMixin):
    key: str
    values: tuple[LabeledValue, ...]
    stable: bool


@dataclass(frozen=True)
class HumanDesignChart(JsonMixin):
    generated_at_utc: str
    birth_datetime_utc: str
    design_datetime_utc: str
    input: ChartInput
    engine: EngineInfo
    summary: ChartSummary
    variables: VariableSet
    definitions: tuple[DefinitionGroup, ...]
    centers: tuple[CenterState, ...]
    channels: tuple[ChannelState, ...]
    activated_gates: tuple[GateState, ...]
    personality: ImprintData
    design: ImprintData


@dataclass(frozen=True)
class ChartRangeSample(JsonMixin):
    birth_datetime_local: str
    birth_datetime_utc: str
    summary: ChartSummary
    defined_centers: tuple[str, ...]
    channels: tuple[str, ...]
    activated_gates: tuple[int, ...]


@dataclass(frozen=True)
class ChartUncertaintyResult(JsonMixin):
    generated_at_utc: str
    interval_minutes: int
    sample_count: int
    range_start_local: str
    range_end_local: str
    range_start_utc: str
    range_end_utc: str
    summary_facets: tuple[UncertaintyFacet, ...]
    stable_centers: tuple[str, ...]
    variable_centers: tuple[str, ...]
    stable_channels: tuple[str, ...]
    variable_channels: tuple[str, ...]
    stable_gates: tuple[int, ...]
    variable_gates: tuple[int, ...]
    samples: tuple[ChartRangeSample, ...]


@dataclass(frozen=True)
class RelationshipFacetComparison(JsonMixin):
    key: str
    left: LabeledValue
    right: LabeledValue
    same: bool


@dataclass(frozen=True)
class RelationshipCodeDelta(JsonMixin):
    shared: tuple[str, ...]
    left_only: tuple[str, ...]
    right_only: tuple[str, ...]


@dataclass(frozen=True)
class RelationshipIntDelta(JsonMixin):
    shared: tuple[int, ...]
    left_only: tuple[int, ...]
    right_only: tuple[int, ...]


@dataclass(frozen=True)
class RelationshipComparisonResult(JsonMixin):
    generated_at_utc: str
    left_label: str
    right_label: str
    summary_facets: tuple[RelationshipFacetComparison, ...]
    centers: RelationshipCodeDelta
    channels: RelationshipCodeDelta
    gates: RelationshipIntDelta
    left_chart: HumanDesignChart
    right_chart: HumanDesignChart


@dataclass(frozen=True)
class SourceReference(JsonMixin):
    kind: str
    code: str
    title: str
    path: str


@dataclass(frozen=True)
class ReadingSection(JsonMixin):
    key: str
    title: str
    summary: str
    bullets: tuple[str, ...]
    sources: tuple[SourceReference, ...] = ()


@dataclass(frozen=True)
class HumanDesignReading(JsonMixin):
    generated_at_utc: str
    headline: str
    quick_facts: tuple[str, ...]
    sections: tuple[ReadingSection, ...]
    suggested_questions: tuple[str, ...]
    chart: HumanDesignChart


@dataclass(frozen=True)
class LLMContextBlock(JsonMixin):
    key: str
    title: str
    content: str
    sources: tuple[SourceReference, ...] = ()


@dataclass(frozen=True)
class AnswerCitation(JsonMixin):
    key: str
    title: str
    sources: tuple[SourceReference, ...]


@dataclass(frozen=True)
class LLMProductPackage(JsonMixin):
    generated_at_utc: str
    product_name: str
    product_version: str
    focus: str
    question: str | None
    system_prompt: str
    assistant_instructions: tuple[str, ...]
    context_blocks: tuple[LLMContextBlock, ...]
    answer_citation_mode: str
    answer_citations: tuple[AnswerCitation, ...]
    answer_markdown: str
    suggested_followups: tuple[str, ...]
    reading: HumanDesignReading
