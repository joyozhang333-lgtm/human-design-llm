from __future__ import annotations

from datetime import UTC, datetime

from .labels import display_authority, display_type, normalize_center_title
from .knowledge import (
    get_authority_card,
    get_center_card,
    get_channel_card,
    get_gate_card,
    to_source_reference,
)
from .schema import ReadingSection, SourceReference, TimingAnalysisResult, TimingReading


def generate_timing_reading(timing: TimingAnalysisResult) -> TimingReading:
    natal = timing.natal_chart
    authority_label = display_authority(natal.summary.authority.code, natal.summary.authority.label)
    type_label = display_type(natal.summary.type.code, natal.summary.type.label)
    headline = (
        f"{timing.timing_label} | {authority_label} "
        f"{type_label} 当前时机解读"
    )
    quick_facts = (
        f"当前时点：{timing.transit_datetime_local}",
        f"你的权威：{authority_label}",
        f"锚定中心：{_format_center_codes(timing.anchored_defined_centers) or '无'}",
        f"被当前时机放大的开放中心：{_format_center_codes(timing.pressured_open_centers) or '无'}",
        f"当前新增通道：{_format_codes(timing.channels.transit_only) or '无'}",
        f"当前新增闸门：{_format_ints(timing.gates.transit_only[:6]) or '无'}",
        *tuple(f"输入精度提示：{warning}" for warning in natal.input.warnings),
    )
    sections = (
        _atmosphere_section(timing),
        _pressure_section(timing),
        _decision_section(timing),
        _practice_section(timing),
    )
    suggested_questions = (
        "这个阶段我最该顺着什么推进，而最不该因为焦虑去硬推什么？",
        "如果我现在有一个现实决定，怎样区分当前时机压力和我自己的真实权威？",
        "接下来 7 天最值得观察的一个重复信号是什么？",
    )
    return TimingReading(
        generated_at_utc=datetime.now(UTC).isoformat(),
        headline=headline,
        quick_facts=quick_facts,
        sections=sections,
        suggested_questions=suggested_questions,
        timing=timing,
    )


def render_timing_reading_markdown(reading: TimingReading) -> str:
    lines: list[str] = []
    lines.append("# 人类图 Timing 解读")
    lines.append("")
    lines.append(reading.headline)
    lines.append("")
    lines.append("## 快速摘要")
    for fact in reading.quick_facts:
        lines.append(f"- {fact}")

    for section in reading.sections:
        lines.append("")
        lines.append(f"## {section.title}")
        lines.append(section.summary)
        if section.bullets:
            lines.append("")
            for bullet in section.bullets:
                lines.append(f"- {bullet}")

    lines.append("")
    lines.append("## 建议继续追问")
    for question in reading.suggested_questions:
        lines.append(f"- {question}")
    return "\n".join(lines).strip() + "\n"


def _atmosphere_section(timing: TimingAnalysisResult) -> ReadingSection:
    summary = (
        f"这个 `{timing.timing_label}` 时点更像一层短期天气，不会改变你的底层配置，"
        "但会放大某些中心、通道和闸门，让某些议题在这段时间更有存在感。"
    )
    bullets = (
        (
            f"锚定中心：{_format_center_codes(timing.anchored_defined_centers)}。这些主题既是你的长期稳定区，也是当前仍然能站得住的地方。"
            if timing.anchored_defined_centers
            else "锚定中心：当前没有额外被重复强化的定义中心，所以这段时机更像变化型天气，而不是稳定放大型天气。"
        ),
        (
            "当前新增通道："
            + "；".join(_channel_bullet(code) for code in timing.channels.transit_only[:3])
            if timing.channels.transit_only
            else "当前新增通道：没有特别突出的临时通道主题，这个时机更偏闸门级和中心级波动。"
        ),
        (
            f"当前新增闸门：{_format_ints(timing.gates.transit_only[:6])}。这些短期主题更容易成为最近几天的触发点。"
            if timing.gates.transit_only
            else "当前新增闸门：这段时间和你的本命主题重合度更高，短期噪音相对没那么强。"
        ),
    )
    return ReadingSection(
        key="current-atmosphere",
        title="当前气候",
        summary=summary,
        bullets=bullets,
        sources=_unique_sources(
            (
                *tuple(_center_source(code) for code in timing.anchored_defined_centers[:2]),
                *tuple(_channel_source(code) for code in timing.channels.transit_only[:2]),
                *tuple(_gate_source(code) for code in timing.gates.transit_only[:2]),
            )
        ),
    )


def _pressure_section(timing: TimingAnalysisResult) -> ReadingSection:
    summary = (
        "真正需要留意的不是“今天适不适合做事”，而是哪些本来不是你稳定发力点的地方，"
        "现在被外界时机短暂放大了。"
    )
    bullets = (
        (
            "被放大的开放中心："
            + "；".join(_pressured_center_bullet(code) for code in timing.pressured_open_centers[:3])
            if timing.pressured_open_centers
            else "被放大的开放中心：当前没有特别突出的外界中心压力，这个阶段更适合靠自己的稳定结构做推进。"
        ),
        (
            f"共享闸门：{_format_ints(timing.gates.shared[:6])}。这些主题会让你觉得“最近这个议题特别熟”，因为它本来就在你的盘里。"
            if timing.gates.shared
            else "共享闸门：当前和你本命没有太多重合，所以更要区分什么是短期天气，什么是你的长期方向。"
        ),
        "当你突然想加速、证明、承诺或情绪反应变大时，先问一句：这真是我的长期节奏，还是当下天气在放大我？",
    )
    return ReadingSection(
        key="pressure-points",
        title="压力与放大点",
        summary=summary,
        bullets=bullets,
        sources=_unique_sources(
            (
                *tuple(_center_source(code) for code in timing.pressured_open_centers[:3]),
                *tuple(_gate_source(code) for code in timing.gates.shared[:2]),
            )
        ),
    )


def _decision_section(timing: TimingAnalysisResult) -> ReadingSection:
    authority_label = display_authority(
        timing.natal_chart.summary.authority.code,
        timing.natal_chart.summary.authority.label,
    )
    authority_card = get_authority_card(timing.natal_chart.summary.authority.code)
    authority_summary = (
        authority_card.summary
        if authority_card is not None
        else "当前决策仍然要回到你的身体权威，而不是回到外界节奏。"
    )
    summary = (
        "Timing 的价值不是替你下结论，而是提醒你：在这个阶段，什么会扰动你的判断，什么又能帮你回到自己的权威。"
    )
    bullets = (
        f"你的主决策方式仍然是「{authority_label}」。{authority_summary}",
        (
            f"如果最近最强的是「{_format_center_codes(timing.pressured_open_centers[:1])}」压力，做重大决定时更要避免被一时情绪或场域节奏推着走。"
            if timing.pressured_open_centers
            else "当前外界中心压力不算特别重，反而更适合把注意力放回你自己原本的决策节奏。"
        ),
        (
            f"如果短期新增了通道 {timing.channels.transit_only[0]}，这几天更容易在这个主题上感到“事情非处理不可”。先辨别这是时机提醒，还是你真的要现在拍板。"
            if timing.channels.transit_only
            else "如果没有明显的临时通道驱动，就不要为了制造确定感而强行定一个结果。"
        ),
    )
    return ReadingSection(
        key="decision-window",
        title="决策窗口",
        summary=summary,
        bullets=bullets,
        sources=_unique_sources(
            (
                _authority_source(timing.natal_chart.summary.authority.code),
                *tuple(_center_source(code) for code in timing.pressured_open_centers[:1]),
                *tuple(_channel_source(code) for code in timing.channels.transit_only[:1]),
            )
        ),
    )


def _practice_section(timing: TimingAnalysisResult) -> ReadingSection:
    summary = (
        "这个阶段最有价值的不是“抓住所有机会”，而是做几条足够小、能验证时机感的实验。"
    )
    bullets = (
        "把接下来 7 天最重要的决定都拆成两步：先记录第一反应，再等你的权威真正给出确认。",
        (
            f"如果「{_format_center_codes(timing.pressured_open_centers[:1])}」被放大，遇到强烈波动时先不要立刻解释、承诺或翻盘，先让波过去。"
            if timing.pressured_open_centers
            else "如果当前没有明显的外界中心放大，就更适合测试稳定推进而不是频繁改方向。"
        ),
        (
            f"把新增闸门 {timing.gates.transit_only[0]} 当成观察点：最近几天，相关主题会怎样在工作、关系或情绪里反复出现？"
            if timing.gates.transit_only
            else "把最近最重复出现的现实场景记下来，区分它是长期课题，还是短期天气。"
        ),
    )
    return ReadingSection(
        key="timing-practice",
        title="阶段练习",
        summary=summary,
        bullets=bullets,
        sources=_unique_sources(
            (
                _authority_source(timing.natal_chart.summary.authority.code),
                *tuple(_center_source(code) for code in timing.pressured_open_centers[:1]),
                *tuple(_gate_source(code) for code in timing.gates.transit_only[:1]),
            )
        ),
    )


def _channel_bullet(code: str) -> str:
    card = get_channel_card(code)
    if card is not None and card.summary:
        return f"{code} {card.summary}"
    return code


def _pressured_center_bullet(code: str) -> str:
    card = get_center_card(code)
    if card is None:
        return code
    return f"{normalize_center_title(card.title)}：{card.undefined}"


def _authority_source(code: str) -> SourceReference | None:
    card = get_authority_card(code)
    return to_source_reference("authority", card) if card is not None else None


def _center_source(code: str) -> SourceReference | None:
    card = get_center_card(code)
    return to_source_reference("center", card) if card is not None else None


def _channel_source(code: str) -> SourceReference | None:
    card = get_channel_card(code)
    return to_source_reference("channel", card) if card is not None else None


def _gate_source(code: int) -> SourceReference | None:
    card = get_gate_card(code)
    return to_source_reference("gate", card) if card is not None else None


def _center_label(code: str | None) -> str:
    if code is None:
        return "该中心"
    card = get_center_card(code)
    return normalize_center_title(card.title) if card is not None else code


def _format_codes(values) -> str:
    return "、".join(values)


def _format_ints(values) -> str:
    return "、".join(str(value) for value in values)


def _format_center_codes(values) -> str:
    return "、".join(_center_label(value) for value in values)


def _unique_sources(sources: tuple[SourceReference | None, ...]) -> tuple[SourceReference, ...]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[SourceReference] = []
    for source in sources:
        if source is None:
            continue
        key = (source.kind, source.code, source.path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(source)
    return tuple(unique)
