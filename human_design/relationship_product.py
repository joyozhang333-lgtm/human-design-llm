from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from .knowledge import get_authority_card, get_center_card, get_channel_card, get_profile_card, to_source_reference
from .relationship_reading import generate_relationship_reading
from .schema import (
    AnswerCitation,
    LLMContextBlock,
    ReadingSection,
    RelationshipComparisonResult,
    RelationshipProductPackage,
    SourceReference,
)
from .version import VERSION

PRODUCT_NAME = "human-design-relationship-llm"
PRODUCT_VERSION = VERSION
CITATION_MODES = ("none", "sources")
RELATIONSHIP_FOCUSES = ("overview", "intimacy", "partnership", "decision", "communication")

FOCUS_SECTIONS = {
    "overview": (
        "relationship-skeleton",
        "resonance",
        "friction",
        "decision-sync",
        "relationship-practice",
    ),
    "intimacy": (
        "relationship-skeleton",
        "resonance",
        "friction",
        "relationship-practice",
    ),
    "partnership": (
        "relationship-skeleton",
        "resonance",
        "decision-sync",
        "relationship-practice",
    ),
    "decision": (
        "decision-sync",
        "friction",
        "relationship-practice",
    ),
    "communication": (
        "relationship-skeleton",
        "friction",
        "relationship-practice",
    ),
}

FOCUS_GUIDANCE = {
    "overview": "输出这段关系的整体骨架，说明自然连接点、摩擦点和最值得建立的规则。",
    "intimacy": "重点看亲密关系中的被看见、情绪处理、节奏差异和靠近方式。",
    "partnership": "重点把差异翻译成协作、分工、承诺和资源交换规则。",
    "decision": "重点帮助双方建立共同决策流程，不替任何一方做宿命式判断。",
    "communication": "重点看沟通、边界、情绪与冲突修复方式。",
}

FOCUS_FOLLOWUPS = {
    "overview": (
        "这段关系里最值得先建立的一条规则是什么？",
        "我们最容易在哪种场景里误把差异当成问题？",
    ),
    "intimacy": (
        "我们各自最需要怎样被理解和被接住？",
        "什么情境最容易触发彼此的不安全感或误读？",
    ),
    "partnership": (
        "如果一起做项目，最适合怎样分工和定节奏？",
        "我们各自最不适合被对方催促或代替决定的点是什么？",
    ),
    "decision": (
        "下一次重大决定时，我们应该按什么顺序来确认？",
        "我们过去做错决定时，通常是谁跳过了自己的权威流程？",
    ),
    "communication": (
        "争执开始升级前，最早出现的信号通常是什么？",
        "我们该怎样区分真实情绪和被放大的场域反应？",
    ),
}

QUESTION_PATTERNS = {
    "intimacy": ("亲密", "恋爱", "伴侣", "婚姻", "吸引", "喜欢"),
    "partnership": ("合作", "创业", "搭档", "团队", "项目", "一起做"),
    "decision": ("要不要", "该不该", "是否", "决定", "结婚", "分开", "复合"),
    "communication": ("沟通", "边界", "冲突", "争吵", "拉扯", "冷战", "情绪"),
}

SYSTEM_PROMPT = """You are `human-design-relationship-llm`, a Human Design relationship interpretation layer.

Your job is to translate a structured dual-chart comparison into grounded relationship guidance.

Operating rules:
- Always start from the provided comparison and reading objects. Do not invent chart facts.
- Treat Human Design as a reflective framework, not a verdict about compatibility.
- Talk about rhythm, decision process, boundaries, and interaction patterns rather than fate.
- If either side has uncertain input precision, explicitly note the relationship reading may shift.
- Prefer practical rules and experiments over abstract judgments.
"""

ASSISTANT_INSTRUCTIONS = (
    "先给出这段关系最重要的结构结论，再展开，不要先堆术语。",
    "先说共鸣点和摩擦点，再说建议，不要只讲其中一边。",
    "涉及重大关系决定时，只提供观察框架和流程建议，不替用户下命令。",
    "结尾给 2 个可继续追问的问题。",
)


@dataclass(frozen=True)
class RelationshipHighlight:
    key: str
    label: str
    text: str
    priority: int
    source: SourceReference | None = None


def build_relationship_product(
    comparison: RelationshipComparisonResult,
    *,
    focus: str = "overview",
    question: str | None = None,
    citation_mode: str = "none",
) -> RelationshipProductPackage:
    focus_key = focus if focus in RELATIONSHIP_FOCUSES else "overview"
    citation_mode_key = citation_mode if citation_mode in CITATION_MODES else "none"
    reading = generate_relationship_reading(comparison)
    selected_keys = set(FOCUS_SECTIONS[focus_key])
    selected_sections = tuple(
        section for section in reading.sections if section.key in selected_keys
    )
    question_lens = _build_question_lens(focus_key, question)
    focus_highlights, focus_highlight_sources = _build_focus_highlights(comparison, focus_key, question)
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
                    content=_precision_note(comparison),
                ),
            )
            if _precision_note(comparison)
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
        comparison,
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
    return RelationshipProductPackage(
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
        comparison=comparison,
        reading=reading,
    )


def _render_answer(
    comparison: RelationshipComparisonResult,
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
    lines.append("# Human Design Relationship Session")
    lines.append("")
    lines.append(headline)
    lines.append("")
    lines.append(f"当前聚焦：{focus}")
    if question:
        lines.append(f"当前问题：{question}")
    precision_note = _precision_note(comparison)
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


def _build_question_lens(focus: str, question: str | None) -> str | None:
    if not question:
        return None
    if any(token in question for token in QUESTION_PATTERNS["decision"]) or focus == "decision":
        return "这个问题带有明确的关系决策压力。回答时要优先把双方权威流程拆开，再看能否形成共同结论。"
    if any(token in question for token in QUESTION_PATTERNS["communication"]) or focus == "communication":
        return "这个问题更像沟通和边界场景。回答时要优先看谁在放大情绪、谁在主导节奏，以及冲突是怎么升级的。"
    if any(token in question for token in QUESTION_PATTERNS["partnership"]) or focus == "partnership":
        return "这个问题更像协作场景。回答时要优先看双方节奏、承诺方式和资源交换规则是否一致。"
    if any(token in question for token in QUESTION_PATTERNS["intimacy"]) or focus == "intimacy":
        return "这个问题更像亲密关系场景。回答时要优先看被看见的需求、靠近节奏和情绪承接方式。"
    return None


def _build_focus_highlights(
    comparison: RelationshipComparisonResult,
    focus: str,
    question: str | None,
) -> tuple[str | None, tuple[SourceReference, ...]]:
    candidates: list[RelationshipHighlight] = []
    candidates.extend(_summary_highlights(comparison, focus))
    candidates.extend(_center_highlights(comparison, focus))
    candidates.extend(_channel_highlights(comparison, focus))
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
        if len(selected) >= 5:
            break
    return ("\n".join(selected) if selected else None, _unique_sources(tuple(sources)))


def _summary_highlights(
    comparison: RelationshipComparisonResult,
    focus: str,
) -> list[RelationshipHighlight]:
    left = comparison.left_chart.summary
    right = comparison.right_chart.summary
    highlights: list[RelationshipHighlight] = []
    if comparison.left_chart.summary.authority.code == comparison.right_chart.summary.authority.code:
        text = "两人的权威机制相近，容易理解彼此如何确认事情，但也要避免互相替对方确认。"
    else:
        text = "两人的权威机制不同，关系里的关键不是谁说服谁，而是各自完成自己的确认流程。"
    highlights.append(
        RelationshipHighlight(
            key="authority",
            label="权威差异",
            text=text,
            priority=100 if focus in {"decision", "communication"} else 92,
            source=_authority_source(left.authority.code),
        )
    )
    profile_text = (
        "双方的 Profile 节奏相近，比较容易理解彼此的角色展开方式。"
        if comparison.left_chart.summary.profile.code == comparison.right_chart.summary.profile.code
        else "双方的 Profile 不同，意味着一个人要的独处、试错或关系支持，未必和另一方一样。"
    )
    highlights.append(
        RelationshipHighlight(
            key="profile",
            label="Profile 节奏",
            text=profile_text,
            priority=96 if focus == "intimacy" else 84,
            source=_profile_source(left.profile.code),
        )
    )
    return highlights


def _center_highlights(
    comparison: RelationshipComparisonResult,
    focus: str,
) -> list[RelationshipHighlight]:
    highlights: list[RelationshipHighlight] = []
    if comparison.centers.shared:
        code = comparison.centers.shared[0]
        card = get_center_card(code)
        if card is not None:
            text = (
                f"共享「{card.title}」说明你们在这个主题上更容易觉得彼此懂、也更容易在这里形成稳定感。"
            )
            highlights.append(
                RelationshipHighlight(
                    key=f"shared-center:{code}",
                    label=f"共享中心 {card.title}",
                    text=text,
                    priority=94 if focus in {"intimacy", "communication"} else 82,
                    source=to_source_reference("center", card),
                )
            )
    if comparison.centers.left_only:
        code = comparison.centers.left_only[0]
        card = get_center_card(code)
        if card is not None:
            highlights.append(
                RelationshipHighlight(
                    key=f"left-center:{code}",
                    label=f"{comparison.left_label} 的独有中心",
                    text=f"{comparison.left_label} 在「{card.title}」议题上更可能自然地主导节奏，另一方未必同步。",
                    priority=92 if focus in {"communication", "partnership"} else 78,
                    source=to_source_reference("center", card),
                )
            )
    if comparison.centers.right_only:
        code = comparison.centers.right_only[0]
        card = get_center_card(code)
        if card is not None:
            highlights.append(
                RelationshipHighlight(
                    key=f"right-center:{code}",
                    label=f"{comparison.right_label} 的独有中心",
                    text=f"{comparison.right_label} 在「{card.title}」议题上更可能自然地主导节奏，另一方未必同步。",
                    priority=92 if focus in {"communication", "partnership"} else 78,
                    source=to_source_reference("center", card),
                )
            )
    return highlights


def _channel_highlights(
    comparison: RelationshipComparisonResult,
    focus: str,
) -> list[RelationshipHighlight]:
    highlights: list[RelationshipHighlight] = []
    if comparison.channels.shared:
        code = comparison.channels.shared[0]
        card = get_channel_card(code)
        if card is not None:
            text = card.focus.get("relationship") or card.summary
            highlights.append(
                RelationshipHighlight(
                    key=f"shared-channel:{code}",
                    label=f"共享通道 {code}",
                    text=text,
                    priority=88 if focus in {"intimacy", "partnership"} else 76,
                    source=to_source_reference("channel", card),
                )
            )
    return highlights


def _question_bonus(question: str) -> int:
    if not question:
        return 0
    if any(token in question for token in QUESTION_PATTERNS["decision"]):
        return 8
    if any(token in question for token in QUESTION_PATTERNS["communication"]):
        return 7
    if any(token in question for token in QUESTION_PATTERNS["partnership"]):
        return 6
    if any(token in question for token in QUESTION_PATTERNS["intimacy"]):
        return 5
    return 0


def _section_to_text(section: ReadingSection) -> str:
    lines = [section.summary]
    for bullet in section.bullets:
        lines.append(f"- {bullet}")
    return "\n".join(lines)


def _precision_note(comparison: RelationshipComparisonResult) -> str | None:
    notes: list[str] = []
    if comparison.left_chart.input.warnings:
        notes.append(
            f"{comparison.left_label}：{'；'.join(comparison.left_chart.input.warnings)}"
        )
    if comparison.right_chart.input.warnings:
        notes.append(
            f"{comparison.right_label}：{'；'.join(comparison.right_chart.input.warnings)}"
        )
    return "；".join(notes) if notes else None


def _authority_source(code: str) -> SourceReference | None:
    card = get_authority_card(code)
    return to_source_reference("authority", card) if card is not None else None


def _profile_source(code: str) -> SourceReference | None:
    card = get_profile_card(code)
    return to_source_reference("profile", card) if card is not None else None


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
