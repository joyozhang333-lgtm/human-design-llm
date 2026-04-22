from __future__ import annotations

from datetime import UTC, datetime

from .knowledge import (
    AUTHORITY_GUIDES,
    CENTER_GUIDES,
    CHANNEL_TYPE_GUIDES,
    CIRCUIT_GROUP_GUIDES,
    DEFINITION_GUIDES,
    get_authority_card,
    get_channel_card,
    get_center_card,
    get_definition_card,
    get_gate_card,
    get_profile_card,
    get_type_card,
    LINE_GUIDES,
    PLANET_GUIDES,
    PROFILE_GUIDES,
    TYPE_GUIDES,
    VARIABLE_ORIENTATION_GUIDES,
    to_source_reference,
)
from .schema import HumanDesignChart, HumanDesignReading, ReadingSection, SourceReference

PRECISION_LABELS = {
    "explicit-offset": "显式 UTC offset",
    "timezone-name": "显式 IANA 时区",
    "city-resolved": "城市解析时区",
    "assumed-utc": "默认按 UTC",
}


def generate_reading(chart: HumanDesignChart) -> HumanDesignReading:
    precision_facts = (
        f"输入精度：{PRECISION_LABELS.get(chart.input.source_precision, chart.input.source_precision)}",
        *tuple(f"精度提示：{warning}" for warning in chart.input.warnings),
    )
    sections = (
        _core_section(chart),
        _decision_section(chart),
        _profile_definition_section(chart),
        _cross_and_variables_section(chart),
        _centers_section(chart),
        _channels_section(chart),
        _gates_section(chart),
        _integration_section(chart),
    )
    headline = (
        f"{chart.summary.profile.label} | "
        f"{chart.summary.authority.label} {chart.summary.type.label}"
    )
    quick_facts = (
        f"类型：{chart.summary.type.label}",
        f"策略：{chart.summary.strategy.label}",
        f"权威：{chart.summary.authority.label}",
        f"Profile：{chart.summary.profile.label}",
        f"定义：{chart.summary.definition.label}",
        f"轮回交叉：{chart.summary.incarnation_cross.label}",
        *precision_facts,
    )
    suggested_questions = (
        "当我最近在做重大决定时，我有没有先回到自己的权威，而不是急着找标准答案？",
        "我最常被哪一种中心或通道主题牵动，它在工作和关系里具体怎么表现？",
        "如果我要把这张图真正活出来，接下来 30 天最值得实验的一条行为调整是什么？",
    )
    return HumanDesignReading(
        generated_at_utc=datetime.now(UTC).isoformat(),
        headline=headline,
        quick_facts=quick_facts,
        sections=sections,
        suggested_questions=suggested_questions,
        chart=chart,
    )


def render_reading_markdown(reading: HumanDesignReading) -> str:
    lines: list[str] = []
    lines.append("# 人类图完整解读")
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


def _core_section(chart: HumanDesignChart) -> ReadingSection:
    type_card = get_type_card(chart.summary.type.code)
    type_guide = TYPE_GUIDES.get(chart.summary.type.code, {})
    summary_text = type_card.summary if type_card and type_card.summary else type_guide.get(
        "summary",
        "这张图的重点，是先尊重你的能量运作方式，再谈效率和结果。",
    )
    gifts = type_card.gifts if type_card and type_card.gifts else type_guide.get("gifts", ())
    shadows = (
        type_card.shadows if type_card and type_card.shadows else type_guide.get("shadows", ())
    )
    summary = (
        f"你的基础配置是「{chart.summary.type.label} + {chart.summary.profile.label} + "
        f"{chart.summary.authority.label}」。"
        f"{summary_text}"
    )
    bullets = (
        *gifts,
        *shadows,
        f"签名主题是「{chart.summary.signature.label}」，不对位时更容易落入「{chart.summary.not_self_theme.label}」。",
    )
    return ReadingSection(
        key="core",
        title="核心身份",
        summary=summary,
        bullets=tuple(bullets),
        sources=_unique_sources(
            (
                _source_from_card("type", type_card),
            )
        ),
    )


def _decision_section(chart: HumanDesignChart) -> ReadingSection:
    authority_card = get_authority_card(chart.summary.authority.code)
    authority = (
        authority_card.summary
        if authority_card and authority_card.summary
        else AUTHORITY_GUIDES.get(
            chart.summary.authority.code,
            "你的决定方式要尽量回到身体和真实当下，而不是只靠头脑推理。",
        )
    )
    summary = (
        f"行动上，你的策略是「{chart.summary.strategy.label}」；决定上，你的权威是「{chart.summary.authority.label}」。"
        "策略决定你如何进入机会，权威决定你如何在机会里做选择。"
    )
    bullets = (
        authority,
        f"如果你跳过「{chart.summary.strategy.label}」这一步，常会更快撞上 {chart.summary.not_self_theme.label}。",
        "真正的稳定不是更快，而是更对位。先让身体、情绪或表达出现真实信号，再推进动作。",
    )
    return ReadingSection(
        key="decision",
        title="决策与行动方式",
        summary=summary,
        bullets=bullets,
        sources=_unique_sources(
            (
                _source_from_card("authority", authority_card),
            )
        ),
    )


def _profile_definition_section(chart: HumanDesignChart) -> ReadingSection:
    profile_card = get_profile_card(chart.summary.profile.code)
    profile = (
        profile_card.summary
        if profile_card and profile_card.summary
        else PROFILE_GUIDES.get(
            chart.summary.profile.code,
            "你的 Profile 提示你在人生里既有天赋表达，也有必须亲自走过的成长路径。",
        )
    )
    definition_card = get_definition_card(chart.summary.definition.code)
    definition = (
        definition_card.summary
        if definition_card and definition_card.summary
        else DEFINITION_GUIDES.get(
            chart.summary.definition.code,
            "你的定义方式决定了你是更偏内部整合，还是更需要关系和环境来帮助连接。",
        )
    )
    summary = (
        f"Profile「{chart.summary.profile.label}」更多讲的是你学习、关系和角色展开的方式；"
        f"定义「{chart.summary.definition.label}」讲的是你内部系统如何连线。"
    )
    bullets = (
        profile,
        definition,
        "这两个维度一起看时，你会更清楚：你是靠独自消化形成清晰，还是更需要人在场、关系回声与场域流动。",
    )
    return ReadingSection(
        key="profile-definition",
        title="角色路径与内在线路",
        summary=summary,
        bullets=bullets,
        sources=_unique_sources(
            (
                _source_from_card("profile", profile_card),
                _source_from_card("definition", definition_card),
            )
        ),
    )


def _cross_and_variables_section(chart: HumanDesignChart) -> ReadingSection:
    p_sun = _find_activation(chart, "personality", "sun")
    p_earth = _find_activation(chart, "personality", "earth")
    d_sun = _find_activation(chart, "design", "sun")
    d_earth = _find_activation(chart, "design", "earth")
    summary = (
        f"你的轮回交叉是「{chart.summary.incarnation_cross.label}」。"
        "它更像一条人生主轴：不是职业名称，而是你反复会遇到、也会反复贡献出去的主题。"
    )
    bullets = (
        f"人格太阳/地球：{p_sun.gate} / {p_earth.gate}。它们描述你较显性的驱动力与平衡点。",
        f"设计太阳/地球：{d_sun.gate} / {d_earth.gate}。它们描述更底层、身体化、未必总被头脑意识到的驱动。",
        f"变量方向是「{chart.variables.orientation.label}」。"
        f"其中 Motivation = {chart.variables.motivation.label}，Perspective = {chart.variables.perspective.label}，"
        f"Determination = {chart.variables.determination.label}，Environment = {chart.variables.environment.label}。",
        _describe_variable_orientations(chart.variables.orientation.label),
    )
    return ReadingSection(
        key="cross-variables",
        title="人生主轴与变量",
        summary=summary,
        bullets=bullets,
    )


def _centers_section(chart: HumanDesignChart) -> ReadingSection:
    defined = [center for center in chart.centers if center.defined]
    undefined = [center for center in chart.centers if not center.defined]
    summary = (
        f"你有 {len(defined)} 个已定义中心、{len(undefined)} 个开放中心。"
        "已定义中心是你相对稳定的发力方式，开放中心是你最容易放大外界、同时也最有学习空间的地方。"
    )
    bullets: list[str] = []
    sources: list[SourceReference | None] = []
    for center in chart.centers:
        center_card = get_center_card(center.code)
        guide = CENTER_GUIDES.get(center.code)
        if not guide and not center_card:
            continue
        state = "已定义" if center.defined else "开放"
        if center_card:
            label = center_card.title
            explanation = center_card.defined if center.defined else center_card.undefined
        else:
            label = guide["label"]
            explanation = guide["defined"] if center.defined else guide["undefined"]
        bullets.append(f"{label}：{state}。{explanation}")
        sources.append(_source_from_card("center", center_card))
    return ReadingSection(
        key="centers",
        title="九大中心",
        summary=summary,
        bullets=tuple(bullets),
        sources=_unique_sources(tuple(sources)),
    )


def _channels_section(chart: HumanDesignChart) -> ReadingSection:
    summary = (
        f"你当前有 {len(chart.channels)} 条已定义通道。通道代表固定回路：它们会把两个中心之间的能量流变成更稳定的表达方式。"
    )
    channel_cards = [get_channel_card(channel.code) for channel in chart.channels]
    bullets = tuple(
        _describe_channel(channel, channel_card)
        for channel, channel_card in zip(chart.channels, channel_cards, strict=True)
    ) or (
        "这张图当前没有已定义通道，说明你的很多体验更依赖具体环境和互动来被激活。",
    )
    return ReadingSection(
        key="channels",
        title="通道主题",
        summary=summary,
        bullets=bullets,
        sources=_unique_sources(
            tuple(_source_from_card("channel", channel_card) for channel_card in channel_cards)
        ),
    )


def _gates_section(chart: HumanDesignChart) -> ReadingSection:
    summary = (
        f"你当前有 {len(chart.activated_gates)} 个被激活的闸门。下面优先列出完整激活清单，方便后续继续做更细的门线解读。"
    )
    gate_cards = [get_gate_card(gate.gate) for gate in chart.activated_gates]
    bullets = tuple(
        _describe_gate(gate, gate_card)
        for gate, gate_card in zip(chart.activated_gates, gate_cards, strict=True)
    )
    return ReadingSection(
        key="gates",
        title="闸门与行星激活",
        summary=summary,
        bullets=bullets,
        sources=_unique_sources(tuple(_source_from_card("gate", gate_card) for gate_card in gate_cards)),
    )


def _integration_section(chart: HumanDesignChart) -> ReadingSection:
    defined_centers = [center.label for center in chart.centers if center.defined]
    type_card = get_type_card(chart.summary.type.code)
    authority_card = get_authority_card(chart.summary.authority.code)
    summary = (
        "真正让人类图变成产品价值的，不是知道术语，而是把它变成可执行的自我观察。"
        "你现在最需要的不是再多看一堆标签，而是把图里最关键的 2 到 3 个机制活到日常里。"
    )
    bullets = (
        f"先从「{chart.summary.authority.label}」练起：未来两周，把所有重要决定都延后到你的权威真正有回应时再定。",
        f"再从「{chart.summary.strategy.label}」练起：观察自己什么时候顺着策略进入事情，什么时候在逆着自己的方式硬推。",
        f"最后盯住最关键的结构：当前定义中心 {', '.join(defined_centers) or '无'}，以及通道 {', '.join(channel.code for channel in chart.channels) or '无'}。",
    )
    return ReadingSection(
        key="integration",
        title="30 天整合建议",
        summary=summary,
        bullets=bullets,
        sources=_unique_sources(
            (
                _source_from_card("type", type_card),
                _source_from_card("authority", authority_card),
            )
        ),
    )


def _describe_channel(channel, card=None) -> str:
    if card is None:
        card = get_channel_card(channel.code)
    channel_type = CHANNEL_TYPE_GUIDES.get(channel.channel_type.code, "")
    circuit_group = CIRCUIT_GROUP_GUIDES.get(channel.circuit_group.code, "")
    center_names = " 与 ".join(_center_label(code) for code in channel.centers)
    details = ""
    if card:
        detail_parts = [card.summary, *_limit_bullets(card.gifts, 2), *_limit_bullets(card.shadows, 1)]
        details = " ".join(part for part in detail_parts if part).strip()
    return (
        f"{channel.label}：连接 {center_names}，属于 {channel.circuit_group.label} 回路中的 "
        f"{channel.channel_type.label} 通道。{channel_type} {circuit_group}"
        f"{(' ' + details) if details else ''}"
    ).strip()


def _describe_gate(gate, card=None) -> str:
    if card is None:
        card = get_gate_card(gate.gate)
    planet_bits = []
    for activation in gate.activations:
        planet_meaning = PLANET_GUIDES.get(
            activation.planet_code, "这个行星会把该主题带进你的生命经验。"
        )
        line_guide = LINE_GUIDES.get(activation.line, "")
        planet_bits.append(
            f"{activation.imprint} {activation.planet_label} 激活 {activation.line} 线：{planet_meaning} {line_guide}".strip()
        )

    card_summary = ""
    if card:
        detail_parts = [card.summary, *_limit_bullets(card.gifts, 1), *_limit_bullets(card.shadows, 1)]
        card_summary = " ".join(part for part in detail_parts if part).strip()

    return (
        f"{gate.gate} 号闸门《{gate.title}》位于 {_center_label(gate.center)}，主题是「{gate.theme}」。"
        f"相关通道：{', '.join(gate.channels) or '无'}。"
        f"{(card_summary + ' ') if card_summary else ''}"
        f"{' '.join(planet_bits)}"
    )


def _describe_variable_orientations(label: str) -> str:
    parts = []
    mapping = (
        ("P-top", label[0:1]),
        ("P-bottom", label[1:2]),
        ("D-top", label[3:4]),
        ("D-bottom", label[4:5]),
    )
    for _, token in mapping:
        orientation = "left" if token == "L" else "right"
        parts.append(VARIABLE_ORIENTATION_GUIDES[orientation])
    return "变量方向的整体提醒：" + " ".join(parts)


def _find_activation(chart: HumanDesignChart, imprint: str, planet_code: str):
    bucket = chart.personality if imprint == "personality" else chart.design
    return next(
        activation for activation in bucket.activations if activation.planet_code == planet_code
    )


def _center_label(code: str) -> str:
    center_card = get_center_card(code)
    if center_card:
        return center_card.title
    guide = CENTER_GUIDES.get(code)
    return guide["label"] if guide else code


def _limit_bullets(items: tuple[str, ...], limit: int) -> tuple[str, ...]:
    return tuple(item for item in items[:limit] if item)


def _source_from_card(kind: str, card) -> SourceReference | None:
    if card is None:
        return None
    return to_source_reference(kind, card)


def _unique_sources(sources: tuple[SourceReference | None, ...]) -> tuple[SourceReference, ...]:
    items = [source for source in sources if source is not None]
    seen: set[tuple[str, str, str]] = set()
    unique: list[SourceReference] = []
    for source in items:
        key = (source.kind, source.code, source.path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(source)
    return tuple(unique)
