from __future__ import annotations

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
from .schema import (
    ReadingSection,
    RelationshipComparisonResult,
    RelationshipReading,
    SourceReference,
)


def generate_relationship_reading(
    comparison: RelationshipComparisonResult,
) -> RelationshipReading:
    left = comparison.left_chart
    right = comparison.right_chart
    headline = (
        f"{comparison.left_label} x {comparison.right_label} | "
        f"{left.summary.type.label} + {right.summary.type.label}"
    )
    quick_facts = (
        _person_summary(comparison.left_label, left),
        _person_summary(comparison.right_label, right),
        f"共享定义中心：{_format_codes(comparison.centers.shared) or '无'}",
        f"共享通道：{_format_codes(comparison.channels.shared) or '无'}",
        f"共享闸门数量：{len(comparison.gates.shared)}",
        *tuple(_precision_facts(comparison)),
    )
    sections = (
        _relationship_skeleton_section(comparison),
        _resonance_section(comparison),
        _friction_section(comparison),
        _decision_section(comparison),
        _practice_section(comparison),
    )
    suggested_questions = (
        "这段关系里，什么场景最容易让我们各自掉回不对位的决策方式？",
        "我们最值得有意识练习的一条沟通或协作规则是什么？",
        "如果把这段关系拉到未来 30 天，最值得观察的重复模式是什么？",
    )
    return RelationshipReading(
        generated_at_utc=datetime.now(UTC).isoformat(),
        headline=headline,
        quick_facts=quick_facts,
        sections=sections,
        suggested_questions=suggested_questions,
        comparison=comparison,
    )


def render_relationship_reading_markdown(reading: RelationshipReading) -> str:
    lines: list[str] = []
    lines.append("# 人类图关系解读")
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


def _relationship_skeleton_section(
    comparison: RelationshipComparisonResult,
) -> ReadingSection:
    left = comparison.left_chart.summary
    right = comparison.right_chart.summary
    same_authority = _facet_same(comparison, "authority")
    summary = (
        "关系骨架先看两个人是同频展开，还是异质互补。"
        f"{comparison.left_label} 更像 {left.type.label}，{comparison.right_label} 更像 {right.type.label}；"
        "这会直接决定彼此进入关系、被看见和推进事情的节奏。"
    )
    bullets = (
        f"类型层：{comparison.left_label} 是「{left.type.label}」，{comparison.right_label} 是「{right.type.label}」。"
        + (" 两人的基础节奏相近，比较容易用相似方式理解彼此。"
           if _facet_same(comparison, 'type')
           else " 两人的能量节奏不同，关键不是谁更对，而是不要逼彼此用同一种启动方式。"),
        f"权威层：{comparison.left_label} 用「{left.authority.label}」做决定，{comparison.right_label} 用「{right.authority.label}」。"
        + (" 决策速度和确认方式相近，比较容易形成共同步调。"
           if same_authority
           else " 做决定时很容易一个人觉得该快，一个人觉得还没到点，这本身不是不合，而是机制不同。"),
        f"Profile 层：{comparison.left_label} 是「{left.profile.label}」，{comparison.right_label} 是「{right.profile.label}」。"
        " 这会影响彼此需要多少独处、多少试错、多少关系回声。",
        f"定义层：两侧都是「{left.definition.label}」。"
        if _facet_same(comparison, "definition")
        else (
            f"定义层：{comparison.left_label} 是「{left.definition.label}」，"
            f"{comparison.right_label} 是「{right.definition.label}」。"
            " 一个人更容易内部自我整合，另一个人可能更需要关系和场域帮助连线。"
        ),
    )
    return ReadingSection(
        key="relationship-skeleton",
        title="关系骨架",
        summary=summary,
        bullets=bullets,
        sources=_unique_sources(
            (
                _summary_source("type", left.type.code),
                _summary_source("type", right.type.code),
                _summary_source("authority", left.authority.code),
                _summary_source("authority", right.authority.code),
                _summary_source("profile", left.profile.code),
                _summary_source("profile", right.profile.code),
                _summary_source("definition", left.definition.code),
                _summary_source("definition", right.definition.code),
            )
        ),
    )


def _resonance_section(comparison: RelationshipComparisonResult) -> ReadingSection:
    shared_centers = comparison.centers.shared
    shared_channels = comparison.channels.shared
    shared_gates = comparison.gates.shared
    summary = (
        f"这段关系当前最自然的连接面，来自 {len(shared_centers)} 个共享定义中心、"
        f"{len(shared_channels)} 条共享通道和 {len(shared_gates)} 个共享闸门。"
        "共享结构越多，越容易觉得“某些地方我们天生就懂彼此”。"
    )
    bullets = (
        (
            f"共享中心：{_format_center_codes(shared_centers)}。这意味着在这些议题上，你们更容易感到彼此稳定、好理解。"
            if shared_centers
            else "共享中心：当前没有重合的定义中心，关系中的稳定感更依赖清晰沟通和现实规则，而不是自然同频。"
        ),
        (
            "共享通道："
            + "；".join(_channel_bullet(code) for code in shared_channels[:3])
            if shared_channels
            else "共享通道：当前没有完全重合的通道，因此连接感更多来自局部共鸣，而不是整条能量回路的一致。"
        ),
        (
            f"共享闸门：{_format_ints(shared_gates[:6])}。这些重复主题是你们最容易彼此认出、也最容易共同放大的地方。"
            if shared_gates
            else "共享闸门：当前没有重合的激活闸门，关系更偏差异互补型，而不是镜像同频型。"
        ),
    )
    return ReadingSection(
        key="resonance",
        title="共同连接面",
        summary=summary,
        bullets=bullets,
        sources=_unique_sources(
            (
                *tuple(_center_source(code) for code in shared_centers[:3]),
                *tuple(_channel_source(code) for code in shared_channels[:3]),
                *tuple(_gate_source(code) for code in shared_gates[:3]),
            )
        ),
    )


def _friction_section(comparison: RelationshipComparisonResult) -> ReadingSection:
    left_label = comparison.left_label
    right_label = comparison.right_label
    summary = (
        "差异不是坏事，但它通常决定了摩擦会从哪里冒出来。"
        "关系里的冲突点，很多时候不是价值观冲突，而是节奏、边界和处理压力的方式不同。"
    )
    bullets = (
        _difference_bullet(left_label, "中心", comparison.centers.left_only, _format_center_codes),
        _difference_bullet(right_label, "中心", comparison.centers.right_only, _format_center_codes),
        _difference_bullet(left_label, "通道", comparison.channels.left_only, _format_codes),
        _difference_bullet(right_label, "通道", comparison.channels.right_only, _format_codes),
        (
            f"如果一方带有更多独有结构，另一方常会在这些议题上感觉“被带节奏”或“需要适应”。"
            " 真正有用的做法不是争输赢，而是先识别是谁在主导哪一类议题。"
        ),
    )
    return ReadingSection(
        key="friction",
        title="摩擦与互补",
        summary=summary,
        bullets=bullets,
        sources=_unique_sources(
            (
                *tuple(_center_source(code) for code in comparison.centers.left_only[:2]),
                *tuple(_center_source(code) for code in comparison.centers.right_only[:2]),
                *tuple(_channel_source(code) for code in comparison.channels.left_only[:2]),
                *tuple(_channel_source(code) for code in comparison.channels.right_only[:2]),
            )
        ),
    )


def _decision_section(comparison: RelationshipComparisonResult) -> ReadingSection:
    left = comparison.left_chart.summary
    right = comparison.right_chart.summary
    summary = (
        "双人关系里最容易出问题的，不是意见不同，而是两个人把“确认方式”混成一种。"
        "联合决策要先保留各自权威，再讨论共同现实。"
    )
    bullets = (
        f"{comparison.left_label}：优先按「{left.strategy.label} + {left.authority.label}」确认自己的真实回应，再表达给对方。",
        f"{comparison.right_label}：优先按「{right.strategy.label} + {right.authority.label}」确认自己的真实回应，再表达给对方。",
        (
            "联合决策规则：先各自完成自己的确认，再进入讨论；不要用说服替代清晰。"
            if not _facet_same(comparison, "authority")
            else "联合决策规则：两人的权威机制相近，可以用相似节奏推进，但仍然要避免互相替对方确认。"
        ),
        "如果问题牵涉承诺、搬家、合作、结婚或分开，至少让双方都完整走完自己的权威流程后再定。"
    )
    return ReadingSection(
        key="decision-sync",
        title="共同决策",
        summary=summary,
        bullets=bullets,
        sources=_unique_sources(
            (
                _summary_source("authority", left.authority.code),
                _summary_source("authority", right.authority.code),
                _summary_source("type", left.type.code),
                _summary_source("type", right.type.code),
            )
        ),
    )


def _practice_section(comparison: RelationshipComparisonResult) -> ReadingSection:
    summary = (
        "关系真正能落地，不靠“分析得很对”，而靠你们有没有把差异翻译成规则。"
        "最有效的练习通常都很具体。"
    )
    shared_center = comparison.centers.shared[0] if comparison.centers.shared else None
    left_only_center = comparison.centers.left_only[0] if comparison.centers.left_only else None
    right_only_center = comparison.centers.right_only[0] if comparison.centers.right_only else None
    bullets = (
        "先建立一个固定决策协议：重大决定先各自消化，再约一个明确时间回到同一张桌子上讨论。",
        (
            f"把「{_center_label(shared_center)}」当作共同落点：每次关系拉扯时，先回到这个主题上确认彼此真正要守护的是什么。"
            if shared_center
            else "如果缺少明显共享中心，就更要用明确规则、时间窗口和现实边界代替“你应该懂我”。"
        ),
        (
            f"留意 {comparison.left_label} 在「{_center_label(left_only_center)}」议题上的稳定带动力，"
            f"以及 {comparison.right_label} 在「{_center_label(right_only_center)}」议题上的主导倾向。"
            if left_only_center and right_only_center
            else "把最常重复出现的拉扯场景记录下来，观察到底是节奏差异、边界差异，还是情绪处理差异。"
        ),
    )
    return ReadingSection(
        key="relationship-practice",
        title="实践建议",
        summary=summary,
        bullets=bullets,
        sources=_unique_sources(
            (
                *tuple(_center_source(code) for code in comparison.centers.shared[:1]),
                *tuple(_center_source(code) for code in comparison.centers.left_only[:1]),
                *tuple(_center_source(code) for code in comparison.centers.right_only[:1]),
                _summary_source("authority", comparison.left_chart.summary.authority.code),
                _summary_source("authority", comparison.right_chart.summary.authority.code),
            )
        ),
    )


def _person_summary(label: str, chart) -> str:
    return (
        f"{label}：{chart.summary.type.label} / {chart.summary.authority.label} / "
        f"{chart.summary.profile.label} / {chart.summary.definition.label}"
    )


def _precision_facts(comparison: RelationshipComparisonResult) -> tuple[str, ...]:
    facts: list[str] = []
    if comparison.left_chart.input.warnings:
        facts.append(
            f"{comparison.left_label} 输入精度提示：{'；'.join(comparison.left_chart.input.warnings)}"
        )
    if comparison.right_chart.input.warnings:
        facts.append(
            f"{comparison.right_label} 输入精度提示：{'；'.join(comparison.right_chart.input.warnings)}"
        )
    return tuple(facts)


def _facet_same(comparison: RelationshipComparisonResult, key: str) -> bool:
    facet = next(item for item in comparison.summary_facets if item.key == key)
    return facet.same


def _difference_bullet(label: str, kind: str, values, formatter) -> str:
    if not values:
        return f"{label} 的独有{kind}：当前不明显，说明在这层结构上不会总是由一方单边主导。"
    return f"{label} 的独有{kind}：{formatter(values)}。这些议题更容易由 {label} 先带出节奏或先感到在意。"


def _channel_bullet(code: str) -> str:
    card = get_channel_card(code)
    if card is not None and card.summary:
        return f"{code} {card.summary}"
    return code


def _summary_source(kind: str, code: str) -> SourceReference | None:
    if kind == "type":
        card = get_type_card(code)
    elif kind == "authority":
        card = get_authority_card(code)
    elif kind == "profile":
        card = get_profile_card(code)
    elif kind == "definition":
        card = get_definition_card(code)
    else:
        return None
    return to_source_reference(kind, card) if card is not None else None


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
    return card.title if card is not None else code


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
