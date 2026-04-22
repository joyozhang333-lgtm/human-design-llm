from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from .knowledge import (
    get_authority_card,
    get_center_card,
    get_channel_card,
    get_definition_card,
    get_gate_card,
    get_profile_card,
    get_type_card,
    to_source_reference,
)
from .reading import generate_reading
from .schema import (
    AnswerCitation,
    HumanDesignChart,
    LLMContextBlock,
    LLMProductPackage,
    ReadingSection,
    SourceReference,
)
from .version import VERSION

PRODUCT_NAME = "human-design-llm"
PRODUCT_VERSION = VERSION
CITATION_MODES = ("none", "sources")

FOCUS_SECTIONS = {
    "overview": (
        "core",
        "decision",
        "profile-definition",
        "cross-variables",
        "centers",
        "channels",
        "gates",
        "integration",
    ),
    "career": (
        "core",
        "decision",
        "profile-definition",
        "cross-variables",
        "channels",
        "integration",
    ),
    "relationship": (
        "core",
        "decision",
        "profile-definition",
        "centers",
        "channels",
        "integration",
    ),
    "decision": (
        "decision",
        "profile-definition",
        "cross-variables",
        "integration",
    ),
    "growth": (
        "core",
        "profile-definition",
        "centers",
        "channels",
        "gates",
        "integration",
    ),
}

FOCUS_GUIDANCE = {
    "overview": "输出一份完整总览，帮助用户先看懂自己的人类图骨架。",
    "career": "重点把图里的能量配置翻译成工作方式、协作方式、职业选择和资源配置建议。",
    "relationship": "重点把图里的决策、边界、情绪、互动模式翻译成关系建议。",
    "decision": "重点帮助用户用策略与权威做现实决策，不要把结果写成玄学断言。",
    "growth": "重点把图里的卡点、练习方向和 30 天实验建议说清楚。",
}

FOCUS_FOLLOWUPS = {
    "overview": (
        "如果只先抓一件事开始练，我最该先练策略还是权威？",
        "我这张图里最值得继续深挖的中心、通道或闸门是哪几个？",
    ),
    "career": (
        "这张图更适合什么样的工作环境、合作关系和节奏？",
        "如果我现在正处在职业转向期，这张图最该提醒我的风险是什么？",
    ),
    "relationship": (
        "我在亲密关系或合作关系里最容易重复的模式是什么？",
        "什么样的人和互动方式最容易把我带回对位状态？",
    ),
    "decision": (
        "如果我现在要做一个重要决定，这张图要求我先停下来观察什么？",
        "我过去做错决定时，通常是跳过了哪一步？",
    ),
    "growth": (
        "接下来 30 天最值得做的一个具体实验是什么？",
        "我最该从哪个开放中心或已定义结构开始练习？",
    ),
}

SYSTEM_PROMPT = """You are `human-design-llm`, a Human Design interpretation product layer.

Your job is to transform structured chart data into clear, grounded, non-fatalistic guidance.

Operating rules:
- Always start from the provided chart and reading objects. Do not invent chart facts.
- Use Human Design as a reflective framework, not as deterministic truth.
- Prefer language such as "更可能", "更适合", "容易", "需要留意".
- Never present the reading as medical, legal, financial, or guaranteed advice.
- When the user asks a focused question, answer it through strategy, authority, profile, centers, channels, and gates that are actually present in the chart.
- If birth time or timezone is uncertain, explicitly say precision may be affected.
- Keep the answer practical: insight first, then concrete application, then follow-up questions.
"""

ASSISTANT_INSTRUCTIONS = (
    "先给一句高密度结论，再展开，不要一上来铺术语。",
    "先引用 chart 中真实存在的类型、权威、Profile、定义、中心和通道，再解释。",
    "当用户问题有明确焦点时，只展开和焦点最相关的 3 到 5 个结构，不要把整份盘重讲一遍。",
    "结尾给 2 个可以继续追问的问题。",
)

QUESTION_PATTERNS = {
    "career_transition": ("换工作", "转岗", "跳槽", "辞职", "创业", "副业", "职业"),
    "career_team": ("工作", "事业", "团队", "合作", "老板", "管理", "带人", "同事"),
    "relationship_intimacy": ("关系", "亲密", "伴侣", "婚姻", "恋爱", "相处"),
    "relationship_boundary": ("边界", "沟通", "争吵", "情绪", "拉扯"),
    "decision_timing": ("要不要", "是否", "该不该", "什么时候", "现在", "时机"),
    "growth_pattern": ("成长", "卡点", "内耗", "练习", "课题", "天赋", "状态"),
}

CENTER_PRIORITY = {
    "career": ("throat", "sacral", "heart", "g", "ajna", "root"),
    "relationship": ("g", "solar-plexus", "heart", "sacral", "throat", "spleen"),
    "decision": ("solar-plexus", "spleen", "sacral", "heart", "g"),
    "growth": ("root", "head", "ajna", "g", "spleen", "solar-plexus", "heart"),
}

SOURCE_PRIORITY = {
    "career": {
        "type": 100,
        "authority": 95,
        "profile": 90,
        "channel": 80,
        "center": 72,
        "gate": 60,
        "definition": 55,
    },
    "relationship": {
        "authority": 100,
        "profile": 95,
        "center": 88,
        "channel": 80,
        "type": 72,
        "gate": 62,
        "definition": 50,
    },
    "decision": {
        "authority": 100,
        "definition": 88,
        "center": 84,
        "channel": 76,
        "gate": 66,
        "type": 62,
        "profile": 58,
    },
    "growth": {
        "profile": 96,
        "center": 90,
        "definition": 84,
        "channel": 78,
        "gate": 70,
        "type": 66,
        "authority": 62,
    },
}


@dataclass(frozen=True)
class HighlightCandidate:
    key: str
    source_type: str
    label: str
    text: str
    priority: int
    source: SourceReference | None = None


def build_llm_product(
    chart: HumanDesignChart,
    focus: str = "overview",
    question: str | None = None,
    citation_mode: str = "none",
) -> LLMProductPackage:
    focus_key = focus if focus in FOCUS_SECTIONS else "overview"
    citation_mode_key = citation_mode if citation_mode in CITATION_MODES else "none"
    reading = generate_reading(chart)
    selected_keys = set(FOCUS_SECTIONS[focus_key])
    selected_sections = tuple(
        section for section in reading.sections if section.key in selected_keys
    )
    question_lens = _build_question_lens(focus_key, question)
    focus_highlights, focus_highlight_sources = _build_focus_highlights(chart, focus_key, question)
    answer_citations = _build_answer_citations(
        selected_sections=selected_sections,
        focus_highlight_sources=focus_highlight_sources,
    )

    context_blocks = (
        LLMContextBlock(
            key="focus",
            title="Focus",
            content=FOCUS_GUIDANCE[focus_key],
        ),
        *(
            (
                LLMContextBlock(
                    key="question-lens",
                    title="Question Lens",
                    content=question_lens,
                ),
            )
            if question_lens
            else ()
        ),
        *(
            (
                LLMContextBlock(
                    key="input-precision",
                    title="Input Precision",
                    content="\n".join(chart.input.warnings),
                ),
            )
            if chart.input.warnings
            else ()
        ),
        LLMContextBlock(
            key="quick-facts",
            title="Quick Facts",
            content="\n".join(reading.quick_facts),
        ),
        *(
            (
                LLMContextBlock(
                    key="focus-highlights",
                    title="Focus Highlights",
                    content=focus_highlights,
                    sources=focus_highlight_sources,
                ),
            )
            if focus_highlights
            else ()
        ),
        *tuple(
            LLMContextBlock(
                key=section.key,
                title=section.title,
                content=_section_to_text(section.summary, section.bullets),
                sources=section.sources,
            )
            for section in selected_sections
        ),
    )

    answer_markdown = _render_focus_answer(
        chart,
        reading.headline,
        focus_key,
        question,
        question_lens,
        focus_highlights,
        selected_sections,
        FOCUS_FOLLOWUPS[focus_key],
        answer_citations,
        citation_mode_key,
    )

    return LLMProductPackage(
        generated_at_utc=datetime.now(UTC).isoformat(),
        product_name=PRODUCT_NAME,
        product_version=PRODUCT_VERSION,
        focus=focus_key,
        question=question,
        system_prompt=SYSTEM_PROMPT,
        assistant_instructions=ASSISTANT_INSTRUCTIONS,
        context_blocks=context_blocks,
        answer_citation_mode=citation_mode_key,
        answer_citations=answer_citations,
        answer_markdown=answer_markdown,
        suggested_followups=FOCUS_FOLLOWUPS[focus_key],
        reading=reading,
    )


def _render_focus_answer(
    chart: HumanDesignChart,
    headline: str,
    focus: str,
    question: str | None,
    question_lens: str | None,
    focus_highlights: str | None,
    sections: tuple[ReadingSection, ...],
    followups: tuple[str, ...],
    answer_citations: tuple[AnswerCitation, ...],
    citation_mode: str,
) -> str:
    citation_map = {citation.key: citation for citation in answer_citations}
    lines: list[str] = []
    lines.append("# Human Design LLM Session")
    lines.append("")
    lines.append(headline)
    lines.append("")
    lines.append(f"当前聚焦：{focus}")
    if question:
        lines.append(f"当前问题：{question}")
    precision_note = _precision_note(chart)
    if precision_note:
        lines.append(f"输入精度提示：{precision_note}")
    if question_lens:
        lines.append("")
        lines.append("## 问题切口")
        lines.append(question_lens)
    if focus_highlights:
        lines.append("")
        lines.append("## 焦点提示")
        lines.append(focus_highlights)
        citation = citation_map.get("focus-highlights")
        if citation_mode == "sources" and citation is not None:
            lines.append("")
            lines.append(_render_source_line(citation.sources))

    for section in sections:
        lines.append("")
        lines.append(f"## {section.title}")
        lines.append(section.summary)
        if section.bullets:
            lines.append("")
            for bullet in section.bullets:
                lines.append(f"- {bullet}")
        citation = citation_map.get(section.key)
        if citation_mode == "sources" and citation is not None:
            lines.append("")
            lines.append(_render_source_line(citation.sources))

    lines.append("")
    lines.append("## 建议继续追问")
    for item in followups:
        lines.append(f"- {item}")

    return "\n".join(lines).strip() + "\n"


def _section_to_text(summary: str, bullets: tuple[str, ...]) -> str:
    lines = [summary]
    for bullet in bullets:
        lines.append(f"- {bullet}")
    return "\n".join(lines)


def _build_answer_citations(
    selected_sections: tuple[ReadingSection, ...],
    focus_highlight_sources: tuple[SourceReference, ...],
) -> tuple[AnswerCitation, ...]:
    citations: list[AnswerCitation] = []
    if focus_highlight_sources:
        citations.append(
            AnswerCitation(
                key="focus-highlights",
                title="焦点提示",
                sources=focus_highlight_sources,
            )
        )
    citations.extend(
        AnswerCitation(
            key=section.key,
            title=section.title,
            sources=section.sources,
        )
        for section in selected_sections
        if section.sources
    )
    return tuple(citations)


def _precision_note(chart: HumanDesignChart | None) -> str | None:
    if chart is None or not chart.input.warnings:
        return None
    return "；".join(chart.input.warnings)


def _build_question_lens(focus: str, question: str | None) -> str | None:
    if not question:
        return None

    hits = [
        name
        for name, keywords in QUESTION_PATTERNS.items()
        if any(keyword in question for keyword in keywords)
    ]
    if not hits:
        return None

    if focus == "career":
        if "career_transition" in hits:
            return "这个问题更像职业转向场景。回答时要优先看邀请/回应是否对位、合作关系是否支持你，以及资源承诺能否长期承接。"
        if "career_team" in hits:
            return "这个问题更像团队与协作场景。回答时要优先看你在组织中的角色定位、表达方式、边界感和资源交换模式。"
    if focus == "relationship":
        if "relationship_boundary" in hits:
            return "这个问题更像关系边界与沟通场景。回答时要优先看情绪、表达时机、角色投射和彼此边界，而不是只判断对错。"
        if "relationship_intimacy" in hits:
            return "这个问题更像亲密关系场景。回答时要优先看连接方式、情绪处理、被看见的需求，以及相处节奏是否对位。"
    if focus == "decision":
        if "decision_timing" in hits or "career_transition" in hits:
            return "这个问题带有明确的现实决策压力。回答时要优先帮助用户放慢、识别权威信号，并区分真实清晰和短期焦虑。"
    if focus == "growth":
        if "growth_pattern" in hits:
            return "这个问题更像自我成长场景。回答时要优先指出重复模式、练习路径和可执行的小实验，而不是给抽象评价。"
    return None


def _build_focus_highlights(
    chart: HumanDesignChart,
    focus: str,
    question: str | None,
) -> tuple[str | None, tuple[SourceReference, ...]]:
    if focus == "overview":
        return None, ()

    candidates: list[HighlightCandidate] = []
    candidates.extend(_build_core_candidates(chart, focus))
    candidates.extend(_build_center_candidates(chart, focus))
    candidates.extend(_build_channel_candidates(chart, focus))
    candidates.extend(_build_gate_candidates(chart, focus))

    if not candidates:
        return None, ()

    question_bonus = _question_bonus_map(question or "")
    selected: list[str] = []
    sources: list[SourceReference] = []
    seen: set[str] = set()
    ranked = sorted(
        candidates,
        key=lambda candidate: candidate.priority + question_bonus.get(candidate.source_type, 0),
        reverse=True,
    )
    for candidate in ranked:
        if candidate.key in seen:
            continue
        selected.append(f"- {candidate.label}：{candidate.text}")
        if candidate.source is not None:
            sources.append(candidate.source)
        seen.add(candidate.key)
        if len(selected) >= 5:
            break
    content = "\n".join(selected) if selected else None
    return content, _unique_sources(tuple(sources))


def _build_core_candidates(chart: HumanDesignChart, focus: str) -> list[HighlightCandidate]:
    priority = SOURCE_PRIORITY[focus]
    candidates: list[HighlightCandidate] = []

    type_card = get_type_card(chart.summary.type.code)
    if type_card and type_card.focus.get(focus):
        candidates.append(
            HighlightCandidate(
                key=f"type:{chart.summary.type.code}",
                source_type="type",
                label=f"类型 {chart.summary.type.label}",
                text=type_card.focus[focus],
                priority=priority["type"],
                source=_source_from_card("type", type_card),
            )
        )

    authority_card = get_authority_card(chart.summary.authority.code)
    if authority_card and authority_card.focus.get(focus):
        candidates.append(
            HighlightCandidate(
                key=f"authority:{chart.summary.authority.code}",
                source_type="authority",
                label=f"权威 {chart.summary.authority.label}",
                text=authority_card.focus[focus],
                priority=priority["authority"],
                source=_source_from_card("authority", authority_card),
            )
        )

    profile_card = get_profile_card(chart.summary.profile.code)
    if profile_card and profile_card.focus.get(focus):
        candidates.append(
            HighlightCandidate(
                key=f"profile:{chart.summary.profile.code}",
                source_type="profile",
                label=f"Profile {chart.summary.profile.label}",
                text=profile_card.focus[focus],
                priority=priority["profile"],
                source=_source_from_card("profile", profile_card),
            )
        )

    definition_card = get_definition_card(chart.summary.definition.code)
    if definition_card and definition_card.focus.get(focus):
        candidates.append(
            HighlightCandidate(
                key=f"definition:{chart.summary.definition.code}",
                source_type="definition",
                label=f"定义 {chart.summary.definition.label}",
                text=definition_card.focus[focus],
                priority=priority["definition"],
                source=_source_from_card("definition", definition_card),
            )
        )
    return candidates


def _build_center_candidates(chart: HumanDesignChart, focus: str) -> list[HighlightCandidate]:
    priorities = CENTER_PRIORITY.get(focus, ())
    base_priority = SOURCE_PRIORITY[focus]["center"]
    candidates: list[HighlightCandidate] = []
    for rank, center_code in enumerate(priorities):
        center_state = next((center for center in chart.centers if center.code == center_code), None)
        if center_state is None:
            continue
        center_card = get_center_card(center_code)
        if center_card is None or not center_card.focus.get(focus):
            continue
        state_label = "已定义" if center_state.defined else "开放"
        candidates.append(
            HighlightCandidate(
                key=f"center:{center_code}",
                source_type="center",
                label=f"{center_card.title}（{state_label}）",
                text=center_card.focus[focus],
                priority=base_priority - rank,
                source=_source_from_card("center", center_card),
            )
        )
    return candidates


def _build_channel_candidates(chart: HumanDesignChart, focus: str) -> list[HighlightCandidate]:
    priority = SOURCE_PRIORITY[focus]["channel"]
    candidates: list[HighlightCandidate] = []
    for rank, channel in enumerate(chart.channels):
        card = get_channel_card(channel.code)
        if card is None or not card.focus.get(focus):
            continue
        candidates.append(
            HighlightCandidate(
                key=f"channel:{channel.code}",
                source_type="channel",
                label=f"通道 {channel.code}",
                text=card.focus[focus],
                priority=priority - rank,
                source=_source_from_card("channel", card),
            )
        )
    return candidates


def _build_gate_candidates(chart: HumanDesignChart, focus: str) -> list[HighlightCandidate]:
    priority = SOURCE_PRIORITY[focus]["gate"]
    candidates: list[HighlightCandidate] = []
    for rank, gate in enumerate(chart.activated_gates):
        card = get_gate_card(gate.gate)
        if card is None or not card.focus.get(focus):
            continue
        candidates.append(
            HighlightCandidate(
                key=f"gate:{gate.gate}",
                source_type="gate",
                label=f"{gate.gate} 号闸门",
                text=card.focus[focus],
                priority=priority - rank,
                source=_source_from_card("gate", card),
            )
        )
    return candidates


def _question_bonus_map(question: str) -> dict[str, int]:
    if not question:
        return {}
    bonus = {
        "type": 0,
        "authority": 0,
        "profile": 0,
        "definition": 0,
        "center": 0,
        "channel": 0,
        "gate": 0,
    }
    if any(token in question for token in QUESTION_PATTERNS["career_transition"]):
        bonus["authority"] += 6
        bonus["channel"] += 5
        bonus["definition"] += 4
    if any(token in question for token in QUESTION_PATTERNS["career_team"]):
        bonus["type"] += 4
        bonus["center"] += 5
        bonus["channel"] += 4
    if any(token in question for token in QUESTION_PATTERNS["relationship_intimacy"]):
        bonus["center"] += 6
        bonus["authority"] += 4
        bonus["profile"] += 4
    if any(token in question for token in QUESTION_PATTERNS["relationship_boundary"]):
        bonus["center"] += 7
        bonus["gate"] += 4
    if any(token in question for token in QUESTION_PATTERNS["decision_timing"]):
        bonus["authority"] += 8
        bonus["definition"] += 4
        bonus["gate"] += 3
    if any(token in question for token in QUESTION_PATTERNS["growth_pattern"]):
        bonus["profile"] += 6
        bonus["center"] += 5
        bonus["gate"] += 4
    return bonus


def _source_from_card(kind: str, card) -> SourceReference | None:
    if card is None:
        return None
    return to_source_reference(kind, card)


def _unique_sources(sources: tuple[SourceReference, ...]) -> tuple[SourceReference, ...]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[SourceReference] = []
    for source in sources:
        key = (source.kind, source.code, source.path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(source)
    return tuple(unique)


def _render_source_line(sources: tuple[SourceReference, ...]) -> str:
    items = [
        f"[{source.kind}:{source.code}]({source.path})"
        for source in sources
    ]
    return "来源：" + "；".join(items)
