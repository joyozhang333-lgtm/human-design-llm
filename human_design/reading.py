from __future__ import annotations

import re
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
from .glossary import (
    display_circuit_group,
    display_channel_type,
    display_imprint,
    display_planet,
    display_variables,
    scrub_technical_terms,
)
from .labels import (
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
from .schema import HumanDesignChart, HumanDesignReading, ReadingSection, SourceReference

PRECISION_LABELS = {
    "explicit-offset": "出生时间自带精确时区偏移",
    "timezone-name": "使用了明确指定的时区",
    "city-resolved": "时区由出生城市解析",
    "assumed-utc": "未提供时区，按世界时处理",
}

# 手写优质卡片的确定性识别：命中模板指纹或含英文的填空版卡片不进入用户文本。
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


def _clean_card_text(text: str) -> str:
    """只放行手写优质文案：模板指纹或英文命中即整句弃用（宁缺毋滥）。"""
    candidate = (text or "").strip()
    if not candidate:
        return ""
    if _ENGLISH_RE.search(candidate):
        return ""
    if any(regex.search(candidate) for regex in _TEMPLATE_FINGERPRINT_RES):
        return ""
    return candidate


def generate_reading(chart: HumanDesignChart) -> HumanDesignReading:
    type_label = display_type(chart.summary.type.code, chart.summary.type.label)
    strategy_label = display_strategy(chart.summary.strategy.code, chart.summary.strategy.label)
    authority_label = display_authority(chart.summary.authority.code, chart.summary.authority.label)
    profile_label = display_profile(chart.summary.profile.code, chart.summary.profile.label)
    definition_label = display_definition(chart.summary.definition.code, chart.summary.definition.label)
    precision_facts = (
        f"输入精度：{scrub_technical_terms(PRECISION_LABELS.get(chart.input.source_precision, '见录入信息'))}",
        *tuple(f"精度提示：{scrub_technical_terms(warning)}" for warning in chart.input.warnings),
    )
    sections = (
        _core_section(chart),
        _decision_section(chart),
        _profile_definition_section(chart),
        _cross_and_variables_section(chart),
        _centers_section(chart),
        _channels_section(chart),
        _gates_section(chart),
        _gates_full_section(chart),
        _integration_section(chart),
    )
    headline = (
        f"{profile_label} | "
        f"{authority_label} {type_label}"
    )
    quick_facts = (
        f"类型：{type_label}",
        f"策略：{strategy_label}",
        f"权威：{authority_label}",
        f"人生角色：{profile_label}",
        f"定义：{definition_label}",
        f"轮回交叉：{display_incarnation_cross(chart.summary.incarnation_cross.code, chart.summary.incarnation_cross.label)}",
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
    type_label = display_type(chart.summary.type.code, chart.summary.type.label)
    profile_label = display_profile(chart.summary.profile.code, chart.summary.profile.label)
    authority_label = display_authority(chart.summary.authority.code, chart.summary.authority.label)
    signature_label = display_signature(chart.summary.signature.code, chart.summary.signature.label)
    not_self_label = display_not_self(chart.summary.not_self_theme.code, chart.summary.not_self_theme.label)
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
        f"你的基础配置是「{type_label} + {profile_label} + "
        f"{authority_label}」。"
        f"{summary_text}"
    )
    bullets = (
        *gifts,
        *shadows,
        f"签名主题是「{signature_label}」，不对位时更容易落入「{not_self_label}」。",
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
    strategy_label = display_strategy(chart.summary.strategy.code, chart.summary.strategy.label)
    authority_label = display_authority(chart.summary.authority.code, chart.summary.authority.label)
    not_self_label = display_not_self(chart.summary.not_self_theme.code, chart.summary.not_self_theme.label)
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
        f"行动上，你的策略是「{strategy_label}」；决定上，你的权威是「{authority_label}」。"
        "策略决定你如何进入机会，权威决定你如何在机会里做选择。"
    )
    bullets = (
        authority,
        f"如果你跳过「{strategy_label}」这一步，常会更快撞上 {not_self_label}。",
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
    profile_label = display_profile(chart.summary.profile.code, chart.summary.profile.label)
    definition_label = display_definition(chart.summary.definition.code, chart.summary.definition.label)
    profile_card = get_profile_card(chart.summary.profile.code)
    profile = (
        profile_card.summary
        if profile_card and profile_card.summary
        else PROFILE_GUIDES.get(
            chart.summary.profile.code,
            "你的人生角色提示你在人生里既有天赋表达，也有必须亲自走过的成长路径。",
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
        f"人生角色「{profile_label}」更多讲的是你学习、关系和角色展开的方式；"
        f"定义「{definition_label}」讲的是你内部系统如何连线。"
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
    cross_label = display_incarnation_cross(
        chart.summary.incarnation_cross.code, chart.summary.incarnation_cross.label
    )
    summary = (
        f"你的人生主轴（轮回交叉）是「{cross_label}」。"
        "它不是职业名称，而是你一生反复会遇到、也会反复贡献出去的主题。"
    )
    bullets = (
        f"人格面（意识层）太阳/地球落在 {p_sun.gate} 号与 {p_earth.gate} 号闸门，描述你较显性的驱动力与平衡点。",
        f"设计面（身体层）太阳/地球落在 {d_sun.gate} 号与 {d_earth.gate} 号闸门，描述更底层、身体化、未必总被头脑意识到的驱动。",
        *display_variables(chart.variables),
        _describe_variable_orientations(chart.variables.orientation.label),
        "这一小节看看就好，不必当规定：它描述的是让你更省力的倾向，不是必须执行的清单。",
    )
    return ReadingSection(
        key="cross-variables",
        title="人生主轴与运作微调",
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
            label = normalize_center_title(center_card.title)
            explanation = center_card.defined if center.defined else center_card.undefined
        else:
            label = normalize_center_title(guide["label"])
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


GATE_PRIORITY = (2, 14, 63, 64, 5, 35, 13, 17, 27, 28, 29, 34, 60, 61)


def _cross_axis_gate_numbers(chart: HumanDesignChart) -> list[int]:
    numbers: list[int] = []
    for imprint, planet in (("personality", "sun"), ("personality", "earth"), ("design", "sun"), ("design", "earth")):
        bucket = chart.personality if imprint == "personality" else chart.design
        for activation in bucket.activations:
            if activation.planet_code == planet:
                numbers.append(activation.gate)
                break
    return numbers


def _prioritized_gates(chart: HumanDesignChart) -> list:
    """按主轴 + 天赋优先级排序激活闸门（复用 deep_synthesis 的优先级表）。"""
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


def _gates_section(chart: HumanDesignChart) -> ReadingSection:
    top_gates = _prioritized_gates(chart)[:6]
    summary = (
        f"你当前有 {len(chart.activated_gates)} 个被激活的闸门。"
        "下面先看和你的主线最相关的几个，其余收在后面的完整清单里，想细看时再展开。"
    )
    gate_cards = [get_gate_card(gate.gate) for gate in top_gates]
    bullets = tuple(
        _describe_gate(gate, gate_card)
        for gate, gate_card in zip(top_gates, gate_cards, strict=True)
    )
    return ReadingSection(
        key="gates",
        title="关键闸门",
        summary=summary,
        bullets=bullets,
        sources=_unique_sources(tuple(_source_from_card("gate", gate_card) for gate_card in gate_cards)),
    )


def _gates_full_section(chart: HumanDesignChart) -> ReadingSection:
    bullets = tuple(
        f"{gate.gate} 号闸门·{display_gate_theme(gate.gate) or '主题见专业信息'}（位于{_center_label(gate.center)}）"
        for gate in _prioritized_gates(chart)
    )
    return ReadingSection(
        key="gates-full",
        title="完整闸门清单",
        summary="这是你全部被激活的闸门，每个只给名字，供想细看的时候核对。",
        bullets=bullets,
    )


def _integration_section(chart: HumanDesignChart) -> ReadingSection:
    authority_label = display_authority(chart.summary.authority.code, chart.summary.authority.label)
    strategy_label = display_strategy(chart.summary.strategy.code, chart.summary.strategy.label)
    defined_centers = [_center_label(center.code) for center in chart.centers if center.defined]
    type_card = get_type_card(chart.summary.type.code)
    authority_card = get_authority_card(chart.summary.authority.code)
    summary = (
        "读完这张图，最有用的不是记住术语，而是把里面最关键的两三个机制放进日常里观察。"
        "答案不在图里，在你接下来怎么观察自己。"
    )
    bullets = (
        f"先从「{authority_label}」练起：未来两周，把所有重要决定都延后到你的权威真正有回应时再定。",
        f"再从「{strategy_label}」练起：观察自己什么时候顺着策略进入事情，什么时候在逆着自己的方式硬推。",
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
        detail_parts = [
            _clean_card_text(card.summary),
            *(_clean_card_text(item) for item in _limit_bullets(card.gifts, 2)),
            *(_clean_card_text(item) for item in _limit_bullets(card.shadows, 1)),
        ]
        details = " ".join(part for part in detail_parts if part).strip()
    channel_name = display_channel_label(channel.code) or f"{channel.code} 通道"
    return (
        f"{channel.code}「{channel_name}」：连接{center_names}，"
        f"属于{display_circuit_group(channel.circuit_group.code)}的{display_channel_type(channel.channel_type.code)}通道。"
        f"{channel_type} {circuit_group}"
        f"{(' ' + details) if details else ''}"
    ).strip()


def _describe_gate(gate, card=None) -> str:
    if card is None:
        card = get_gate_card(gate.gate)
    planet_bits = []
    for activation in gate.activations[:2]:
        planet_meaning = PLANET_GUIDES.get(
            activation.planet_code, "这个行星会把该主题带进你的生命经验。"
        )
        line_guide = LINE_GUIDES.get(activation.line, "")
        planet_bits.append(
            f"{display_imprint(activation.imprint, short=True)}·{display_planet(activation.planet_code, activation.planet_label)}"
            f" 激活 {activation.line} 线：{planet_meaning} {line_guide}".strip()
        )

    # 只用手写优质卡片的一句具体白话；填空模板卡片不进入用户文本。
    card_summary = ""
    if card:
        card_summary = _clean_card_text(card.summary)
        if not card_summary:
            gift = _clean_card_text(card.gifts[0]) if card.gifts else ""
            card_summary = gift

    theme_cn = display_gate_theme(gate.gate) or "主题见专业信息"
    return (
        f"{gate.gate} 号闸门·{theme_cn}，位于{_center_label(gate.center)}。"
        f"{(card_summary + ' ') if card_summary else ''}"
        f"{' '.join(planet_bits)}"
    ).strip()


def _describe_variable_orientations(label: str) -> str:
    tokens = tuple(token for token in label if token in {"L", "R"})
    left_count = sum(1 for token in tokens if token == "L")
    right_count = sum(1 for token in tokens if token == "R")
    if left_count > right_count:
        leading = VARIABLE_ORIENTATION_GUIDES["left"]
    elif right_count > left_count:
        leading = VARIABLE_ORIENTATION_GUIDES["right"]
    else:
        leading = "左右变量数量接近，既需要结构节奏，也需要给感知和环境读取留空间。"

    if left_count and right_count:
        balance = "同时保留另一侧能力，不要把自己固定成单一工作方式。"
    elif left_count:
        balance = "重点是建立可重复节奏，但也要避免过度控制现场变化。"
    else:
        balance = "重点是保护接收和观察能力，但也要给行动留出最低限度结构。"
    return f"变量方向的整体提醒：{left_count} 左 / {right_count} 右。{leading}{balance}"


def _find_activation(chart: HumanDesignChart, imprint: str, planet_code: str):
    bucket = chart.personality if imprint == "personality" else chart.design
    return next(
        activation for activation in bucket.activations if activation.planet_code == planet_code
    )


def _center_label(code: str) -> str:
    center_card = get_center_card(code)
    if center_card:
        return normalize_center_title(center_card.title)
    guide = CENTER_GUIDES.get(code)
    return normalize_center_title(guide["label"]) if guide else code


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
