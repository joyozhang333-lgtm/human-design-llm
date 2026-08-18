"""ChartFacts：HumanDesignChart → 扁平、已中文化、自带白名单的结构化事实。

这是 LLM 的唯一事实来源，也是护栏校验的依据（二者同源）。
所有字段在这里就完成中文化——LLM 看不到英文，比要求它翻译可靠得多。
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field

from ..glossary import display_variables
from ..knowledge import get_gate_card
from ..labels import (
    CENTER_LABELS,
    display_authority,
    display_channel_label,
    display_definition,
    display_gate_theme,
    display_incarnation_cross,
    display_not_self,
    display_profile,
    display_signature,
    display_strategy,
    display_type,
    normalize_center_title,
)
from ..schema import HumanDesignChart

# 与 deep_synthesis.GATE_TALENT_PRIORITY 保持一致的天赋优先级。
GATE_PRIORITY = (2, 14, 63, 64, 5, 35, 13, 17, 27, 28, 29, 34, 60, 61)

L2_TOP_GATES = 6

_TEMPLATE_FINGERPRINT_RES = tuple(
    re.compile(pattern)
    for pattern in (
        r"把与「?.+?」?相关的体验持续带进你的生命结构",
        r"当这股能量运作成熟时",
        r"形成稳定贡献",
        r"如果.{0,6}被焦虑或外界压力带偏",
        r"活成过度反应或反复内耗",
    )
)
_ENGLISH_RE = re.compile(r"[A-Za-z]{3,}")


def clean_card_sentence(text: str) -> str:
    """手写优质卡片的确定性识别：含英文或模板指纹的填空卡文案不放行。"""
    candidate = " ".join((text or "").split())
    if not candidate:
        return ""
    if _ENGLISH_RE.search(candidate):
        return ""
    if any(regex.search(candidate) for regex in _TEMPLATE_FINGERPRINT_RES):
        return ""
    return candidate


@dataclass(frozen=True)
class Whitelist:
    gate_nums: frozenset[int]
    channel_codes: frozenset[str]
    center_codes: frozenset[str]
    line_nums: frozenset[int]


@dataclass(frozen=True)
class GateFact:
    gate: int
    theme_cn: str
    center_cn: str
    sentence: str  # 手写优质卡片的一句具体白话；写不具体就为空


@dataclass(frozen=True)
class ChartFacts:
    layer: str
    focus: str
    type_cn: str
    strategy_cn: str
    authority_cn: str
    profile_cn: str
    definition_cn: str
    signature_cn: str
    not_self_cn: str
    cross_cn: str
    defined_centers_cn: tuple[str, ...]
    open_centers_cn: tuple[str, ...]
    channels_cn: tuple[str, ...]
    top_gates: tuple[GateFact, ...]
    all_gates: tuple[GateFact, ...]
    variables_cn: tuple[str, ...]
    precision_cn: tuple[str, ...]
    whitelist: Whitelist
    # 昵称/出生地拼音/用户问题原词：只用于英文检测排除，绝不进入 L3 prompt、缓存键或落盘。
    user_term_whitelist: tuple[str, ...] = field(default=())
    # 内部选择用代码（不出现在用户文本里）
    type_code: str = ""
    strategy_code: str = ""
    authority_code: str = ""
    profile_code: str = ""
    definition_code: str = ""
    signature_code: str = ""
    not_self_code: str = ""
    channel_codes: tuple[str, ...] = ()
    open_center_codes: tuple[str, ...] = ()
    defined_center_codes: tuple[str, ...] = ()

    @property
    def facts_hash(self) -> str:
        """仅图表事实的哈希：不含昵称、问题等任何个人输入。"""
        payload = {
            "type": self.type_code,
            "strategy": self.strategy_code,
            "authority": self.authority_code,
            "profile": self.profile_code,
            "definition": self.definition_code,
            "cross": self.cross_cn,
            "channels": sorted(self.channel_codes),
            "gates": sorted(g.gate for g in self.all_gates),
            "open_centers": sorted(self.open_center_codes),
            "variables": list(self.variables_cn),
        }
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _center_label(code: str, fallback: str = "") -> str:
    return normalize_center_title(CENTER_LABELS.get(code, fallback or code))


def _cross_axis_gate_numbers(chart: HumanDesignChart) -> list[int]:
    numbers: list[int] = []
    for imprint, planet in (("personality", "sun"), ("personality", "earth"), ("design", "sun"), ("design", "earth")):
        bucket = chart.personality if imprint == "personality" else chart.design
        for activation in bucket.activations:
            if activation.planet_code == planet:
                numbers.append(activation.gate)
                break
    return numbers


def _gate_fact(gate_state) -> GateFact:
    card = get_gate_card(gate_state.gate)
    sentence = clean_card_sentence(card.summary) if card else ""
    return GateFact(
        gate=gate_state.gate,
        theme_cn=display_gate_theme(gate_state.gate) or f"第{gate_state.gate}号闸门",
        center_cn=_center_label(gate_state.center),
        sentence=sentence,
    )


def _prioritized_gate_states(chart: HumanDesignChart) -> list:
    by_number = {gate.gate: gate for gate in chart.activated_gates}
    ordered = []
    for num in (*_cross_axis_gate_numbers(chart), *GATE_PRIORITY):
        gate = by_number.get(num)
        if gate is not None and gate not in ordered:
            ordered.append(gate)
    for gate in chart.activated_gates:
        if gate not in ordered:
            ordered.append(gate)
    return ordered


def extract_chart_facts(
    chart: HumanDesignChart,
    layer: str = "L2",
    focus: str | None = None,
    *,
    user_terms: tuple[str, ...] = (),
) -> ChartFacts:
    summary = chart.summary
    all_gates = tuple(_gate_fact(gate) for gate in _prioritized_gate_states(chart))
    top_gates = all_gates[:L2_TOP_GATES]

    whitelist = Whitelist(
        gate_nums=frozenset(gate.gate for gate in chart.activated_gates),
        channel_codes=frozenset(channel.code for channel in chart.channels),
        center_codes=frozenset(center.code for center in chart.centers),
        line_nums=frozenset(
            activation.line
            for bucket in (chart.personality, chart.design)
            for activation in bucket.activations
        ),
    )

    from ..reading import PRECISION_LABELS  # 复用同一份中文精度标签，避免两处漂移
    from ..glossary import scrub_technical_terms

    precision = (
        scrub_technical_terms(PRECISION_LABELS.get(chart.input.source_precision, "见录入信息")),
        *(scrub_technical_terms(warning) for warning in chart.input.warnings),
    )

    return ChartFacts(
        layer=layer,
        focus=focus or "",
        type_cn=display_type(summary.type.code, summary.type.label),
        strategy_cn=display_strategy(summary.strategy.code, summary.strategy.label),
        authority_cn=display_authority(summary.authority.code, summary.authority.label),
        profile_cn=display_profile(summary.profile.code, summary.profile.label),
        definition_cn=display_definition(summary.definition.code, summary.definition.label),
        signature_cn=display_signature(summary.signature.code, summary.signature.label),
        not_self_cn=display_not_self(summary.not_self_theme.code, summary.not_self_theme.label),
        cross_cn=display_incarnation_cross(summary.incarnation_cross.code, summary.incarnation_cross.label),
        defined_centers_cn=tuple(
            _center_label(center.code, center.label) for center in chart.centers if center.defined
        ),
        open_centers_cn=tuple(
            _center_label(center.code, center.label) for center in chart.centers if not center.defined
        ),
        channels_cn=tuple(
            f"{channel.code}「{display_channel_label(channel.code) or '通道'}」" for channel in chart.channels
        ),
        top_gates=top_gates,
        all_gates=all_gates,
        variables_cn=display_variables(chart.variables),
        precision_cn=precision,
        whitelist=whitelist,
        user_term_whitelist=tuple(term for term in user_terms if term),
        type_code=summary.type.code,
        strategy_code=summary.strategy.code,
        authority_code=summary.authority.code,
        profile_code=summary.profile.code,
        definition_code=summary.definition.code,
        signature_code=summary.signature.code,
        not_self_code=summary.not_self_theme.code,
        channel_codes=tuple(channel.code for channel in chart.channels),
        open_center_codes=tuple(center.code for center in chart.centers if not center.defined),
        defined_center_codes=tuple(center.code for center in chart.centers if center.defined),
    )
