from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from .knowledge import get_authority_card, get_center_card, get_channel_card, get_gate_card, to_source_reference
from .schema import (
    AnswerCitation,
    LLMContextBlock,
    ReadingSection,
    SourceReference,
    TimingAnalysisResult,
    TimingProductPackage,
)
from .session import build_session_state, followups_by_depth, highlight_limit, normalize_depth, select_sections_by_depth
from .timing_reading import generate_timing_reading
from .version import VERSION

PRODUCT_NAME = "human-design-timing-llm"
PRODUCT_VERSION = VERSION
CITATION_MODES = ("none", "sources")
TIMING_FOCUSES = ("overview", "decision", "timing", "energy", "growth")

FOCUS_SECTIONS = {
    "overview": ("current-atmosphere", "pressure-points", "decision-window", "timing-practice"),
    "decision": ("pressure-points", "decision-window", "timing-practice"),
    "timing": ("current-atmosphere", "pressure-points", "timing-practice"),
    "energy": ("current-atmosphere", "pressure-points", "timing-practice"),
    "growth": ("pressure-points", "decision-window", "timing-practice"),
}

FOCUS_GUIDANCE = {
    "overview": "解释当前时机的整体天气：哪些主题被放大、哪些结构能让你站稳。",
    "decision": "重点帮助用户在当前阶段做现实决策，不把短期天气误当长期命运。",
    "timing": "重点解释现在是什么阶段、什么主题正在浮上来，以及近期窗口感在哪里。",
    "energy": "重点看当前能量起伏、被放大的开放中心和节奏管理。",
    "growth": "重点把当前天气翻译成最近 7 到 14 天最值得做的观察与练习。",
}

FOCUS_FOLLOWUPS = {
    "overview": (
        "这段时间我最该顺着哪个主题推进？",
        "哪些反应更像短期天气，而不是我的长期方向？",
    ),
    "decision": (
        "如果我现在必须做决定，怎样避免被当下气候推着走？",
        "哪些信号说明这不是时候，而不是我不行？",
    ),
    "timing": (
        "这个阶段最重要的窗口在哪里？",
        "最近几天什么主题最值得持续观察？",
    ),
    "energy": (
        "我最近最容易在哪种压力里失真？",
        "现在更适合扩张，还是适合稳住节奏？",
    ),
    "growth": (
        "接下来 7 天最值得做的一个小实验是什么？",
        "当前时机最想让我看到的重复模式是什么？",
    ),
}

QUESTION_PATTERNS = {
    "decision": ("要不要", "该不该", "是否", "决定", "现在", "时机"),
    "energy": ("状态", "累", "能量", "节奏", "压力", "内耗"),
    "growth": ("成长", "课题", "练习", "最近", "卡点"),
}

SYSTEM_PROMPT = """You are `human-design-timing-llm`, a Human Design timing interpretation layer.

Your job is to translate a natal chart plus a transit timing comparison into grounded short-term guidance.

Operating rules:
- Always separate natal structure from temporary timing weather.
- Never describe timing as fate. Treat it as a temporary amplification field.
- Prioritize practical decisions, timing windows, and pressure management.
- If natal or transit input precision is uncertain, explicitly say the timing reading may shift.
"""

ASSISTANT_INSTRUCTIONS = (
    "先说当前天气的高密度结论，再说决策和练习，不要一开始就堆技术术语。",
    "必须清楚区分：什么是你的长期结构，什么只是当前阶段被放大的主题。",
    "不要把 timing 说成宿命论，只能说趋势、放大点和更适合的动作。",
    "结尾给 2 个继续追问的问题。",
)


@dataclass(frozen=True)
class TimingHighlight:
    key: str
    label: str
    text: str
    priority: int
    source: SourceReference | None = None


def build_timing_product(
    timing: TimingAnalysisResult,
    *,
    focus: str = "overview",
    question: str | None = None,
    citation_mode: str = "none",
    depth: str = "standard",
) -> TimingProductPackage:
    focus_key = focus if focus in TIMING_FOCUSES else "overview"
    citation_mode_key = citation_mode if citation_mode in CITATION_MODES else "none"
    depth_key = normalize_depth(depth)
    reading = generate_timing_reading(timing)
    selected_keys = set(FOCUS_SECTIONS[focus_key])
    selected_sections = select_sections_by_depth(
        tuple(section for section in reading.sections if section.key in selected_keys),
        depth_key,
    )
    question_lens = _build_question_lens(focus_key, question)
    focus_highlights, focus_highlight_sources = _build_focus_highlights(timing, focus_key, question, depth_key)
    answer_citations = _build_answer_citations(selected_sections, focus_highlight_sources)
    context_blocks = (
        LLMContextBlock(key="focus", title="Focus", content=FOCUS_GUIDANCE[focus_key]),
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
                    content=_precision_note(timing),
                ),
            )
            if _precision_note(timing)
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
                content=_section_to_text(section),
                sources=section.sources,
            )
            for section in selected_sections
        ),
    )
    answer_markdown = _render_answer(
        timing,
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
    suggested_followups = followups_by_depth(FOCUS_FOLLOWUPS[focus_key], depth_key)
    session_state = build_session_state(
        product_line="timing",
        focus=focus_key,
        headline=reading.headline,
        quick_facts=reading.quick_facts,
        context_blocks=context_blocks,
        suggested_followups=suggested_followups,
    )
    return TimingProductPackage(
        generated_at_utc=datetime.now(UTC).isoformat(),
        product_name=PRODUCT_NAME,
        product_version=PRODUCT_VERSION,
        focus=focus_key,
        delivery_depth=depth_key,
        question=question,
        system_prompt=SYSTEM_PROMPT,
        assistant_instructions=ASSISTANT_INSTRUCTIONS,
        context_blocks=context_blocks,
        answer_citation_mode=citation_mode_key,
        answer_citations=answer_citations,
        answer_markdown=answer_markdown,
        suggested_followups=suggested_followups,
        session_state=session_state,
        timing=timing,
        reading=reading,
    )


def _render_answer(
    timing: TimingAnalysisResult,
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
    lines.append("# Human Design Timing Session")
    lines.append("")
    lines.append(headline)
    lines.append("")
    lines.append(f"当前聚焦：{focus}")
    if question:
        lines.append(f"当前问题：{question}")
    precision_note = _precision_note(timing)
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


def _build_question_lens(focus: str, question: str | None) -> str | None:
    if not question:
        return None
    if focus == "decision" or any(token in question for token in QUESTION_PATTERNS["decision"]):
        return "这个问题带有明确的现实决策压力。回答时要优先区分：什么是当前天气在催，什么是你自己的权威真的清晰。"
    if focus == "energy" or any(token in question for token in QUESTION_PATTERNS["energy"]):
        return "这个问题更像能量与压力场景。回答时要优先看哪些开放中心正在被外界放大，以及你该如何稳住节奏。"
    if focus == "growth" or any(token in question for token in QUESTION_PATTERNS["growth"]):
        return "这个问题更像阶段成长场景。回答时要优先指出最近反复出现的主题，以及最值得做的短期实验。"
    return None


def _build_focus_highlights(
    timing: TimingAnalysisResult,
    focus: str,
    question: str | None,
    depth: str,
) -> tuple[str | None, tuple[SourceReference, ...]]:
    candidates: list[TimingHighlight] = []
    candidates.extend(_authority_highlights(timing, focus))
    candidates.extend(_center_highlights(timing, focus))
    candidates.extend(_channel_highlights(timing, focus))
    candidates.extend(_gate_highlights(timing, focus))
    if not candidates:
        return None, ()
    bonus = _question_bonus(question or "")
    selected: list[str] = []
    sources: list[SourceReference] = []
    seen: set[str] = set()
    ranked = sorted(candidates, key=lambda item: item.priority + bonus, reverse=True)
    for candidate in ranked:
        if candidate.key in seen:
            continue
        selected.append(f"- {candidate.label}：{candidate.text}")
        if candidate.source is not None:
            sources.append(candidate.source)
        seen.add(candidate.key)
        if len(selected) >= highlight_limit(depth):
            break
    return ("\n".join(selected) if selected else None, _unique_sources(tuple(sources)))


def _authority_highlights(timing: TimingAnalysisResult, focus: str) -> list[TimingHighlight]:
    card = get_authority_card(timing.natal_chart.summary.authority.code)
    if card is None:
        return []
    text = (
        f"无论当前天气如何变化，你的最终决策仍然要回到「{timing.natal_chart.summary.authority.label}」。"
    )
    return [
        TimingHighlight(
            key=f"authority:{timing.natal_chart.summary.authority.code}",
            label=f"权威 {timing.natal_chart.summary.authority.label}",
            text=text,
            priority=100 if focus == "decision" else 88,
            source=to_source_reference("authority", card),
        )
    ]


def _center_highlights(timing: TimingAnalysisResult, focus: str) -> list[TimingHighlight]:
    highlights: list[TimingHighlight] = []
    for rank, code in enumerate(timing.pressured_open_centers[:2]):
        card = get_center_card(code)
        if card is None:
            continue
        highlights.append(
            TimingHighlight(
                key=f"pressure-center:{code}",
                label=f"被放大的开放中心 {card.title}",
                text=f"这个中心当前被短期天气点亮，更容易出现放大、着急或过度解释的反应。",
                priority=96 - rank if focus in {"decision", "energy"} else 84 - rank,
                source=to_source_reference("center", card),
            )
        )
    for rank, code in enumerate(timing.anchored_defined_centers[:1]):
        card = get_center_card(code)
        if card is None:
            continue
        highlights.append(
            TimingHighlight(
                key=f"anchor-center:{code}",
                label=f"锚定中心 {card.title}",
                text="这个中心是你当前最适合回去站稳的位置，天气再变，这里仍然更能给你稳定感。",
                priority=82 - rank,
                source=to_source_reference("center", card),
            )
        )
    return highlights


def _channel_highlights(timing: TimingAnalysisResult, focus: str) -> list[TimingHighlight]:
    highlights: list[TimingHighlight] = []
    for rank, code in enumerate(timing.channels.transit_only[:2]):
        card = get_channel_card(code)
        if card is None:
            continue
        text = card.summary or f"{code} 这条通道是当前时机新带进来的临时主题。"
        highlights.append(
            TimingHighlight(
                key=f"channel:{code}",
                label=f"当前新增通道 {code}",
                text=text,
                priority=90 - rank if focus in {"timing", "energy"} else 76 - rank,
                source=to_source_reference("channel", card),
            )
        )
    return highlights


def _gate_highlights(timing: TimingAnalysisResult, focus: str) -> list[TimingHighlight]:
    highlights: list[TimingHighlight] = []
    for rank, code in enumerate(timing.gates.transit_only[:2]):
        card = get_gate_card(code)
        if card is None:
            continue
        highlights.append(
            TimingHighlight(
                key=f"gate:{code}",
                label=f"当前新增闸门 {code}",
                text=f"{card.summary or card.title} 这个主题最近更容易被触发，但它是阶段性天气，不一定是长期答案。",
                priority=74 - rank,
                source=to_source_reference("gate", card),
            )
        )
    return highlights


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


def _question_bonus(question: str) -> int:
    if any(token in question for token in QUESTION_PATTERNS["decision"]):
        return 8
    if any(token in question for token in QUESTION_PATTERNS["energy"]):
        return 6
    if any(token in question for token in QUESTION_PATTERNS["growth"]):
        return 5
    return 0


def _section_to_text(section: ReadingSection) -> str:
    lines = [section.summary]
    for bullet in section.bullets:
        lines.append(f"- {bullet}")
    return "\n".join(lines)


def _precision_note(timing: TimingAnalysisResult) -> str | None:
    notes = list(timing.natal_chart.input.warnings)
    notes.extend(
        f"当前时点：{warning}" for warning in timing.transit_chart.input.warnings
    )
    return "；".join(notes) if notes else None


def _render_source_line(sources: tuple[SourceReference, ...]) -> str:
    items = [f"[{source.kind}:{source.code}]({source.path})" for source in sources]
    return "来源：" + "；".join(items)


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
