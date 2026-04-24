from __future__ import annotations

from dataclasses import dataclass

from .knowledge import (
    get_authority_card,
    get_center_card,
    get_channel_card,
    get_gate_card,
    get_profile_card,
    get_type_card,
    to_source_reference,
)
from .labels import display_authority, display_profile, display_type, normalize_center_title
from .schema import HumanDesignChart, JsonMixin, ReadingSection, SourceReference


@dataclass(frozen=True)
class CareerReport(JsonMixin):
    headline: str
    thesis: str
    sections: tuple[ReadingSection, ...]
    suggested_experiments: tuple[str, ...]
    chart: HumanDesignChart


def generate_career_report(chart: HumanDesignChart) -> CareerReport:
    type_label = display_type(chart.summary.type.code, chart.summary.type.label)
    authority_label = display_authority(chart.summary.authority.code, chart.summary.authority.label)
    profile_label = display_profile(chart.summary.profile.code, chart.summary.profile.label)
    thesis = _career_thesis(chart, type_label, authority_label, profile_label)
    sections = (
        _thesis_section(chart, thesis),
        _money_engine_section(chart),
        _market_entry_section(chart),
        _role_section(chart),
        _distortion_loop_section(chart),
        _direction_filter_section(chart),
    )
    return CareerReport(
        headline=f"{profile_label} | {authority_label} {type_label} 职业深读",
        thesis=thesis,
        sections=sections,
        suggested_experiments=(
            f"未来 14 天只记录一件事：哪些工作能通过「{authority_label}」确认，哪些只是头脑觉得应该做。",
            "把当前所有项目分成三类：值得长期投、短期现金流、纯消耗；先砍纯消耗。",
            "任何新合作先过 48 小时，不用当场证明价值，也不要当场给长期承诺。",
        ),
        chart=chart,
    )


def render_career_report_markdown(report: CareerReport) -> str:
    lines = ["# 人类图职业深读", "", report.headline, "", report.thesis]
    for section in report.sections:
        lines.extend(("", f"## {section.title}", section.summary))
        for bullet in section.bullets:
            lines.append(f"- {bullet}")
    lines.extend(("", "## 14 天实验"))
    for item in report.suggested_experiments:
        lines.append(f"- {item}")
    return "\n".join(lines).strip() + "\n"


def career_report_sections(chart: HumanDesignChart) -> tuple[ReadingSection, ...]:
    return generate_career_report(chart).sections


def _career_thesis(
    chart: HumanDesignChart,
    type_label: str,
    authority_label: str,
    profile_label: str,
) -> str:
    defined_centers = tuple(center.code for center in chart.centers if center.defined)
    channel_codes = tuple(channel.code for channel in chart.channels)
    if defined_centers == ("g", "sacral") and channel_codes == ("02-14",):
        return (
            f"你的职业核心不是找一个更响亮的身份，而是让「{type_label}」的持续生命力、"
            f"「{authority_label}」的身体回应、以及「{profile_label}」的关系展开，全部服务同一条主航道。"
            "02-14 这条通道把方向感和资源投放绑在一起；你真正的职业优势，是持续给正确方向供能，"
            "真正的职业风险，是把这股持续供能交给错误方向。"
        )
    return (
        f"你的职业判断要先回到「{type_label} + {authority_label} + {profile_label}」这组基础机制，"
        f"再看已定义中心和实际通道（{_channel_summary(chart)}）。方向、能量和关系展开方式对齐以后，职业选择才会稳定。"
    )


def _thesis_section(chart: HumanDesignChart, thesis: str) -> ReadingSection:
    authority_label = display_authority(chart.summary.authority.code, chart.summary.authority.label)
    bullets = [
        "这张盘的职业问题不是先套行业标签，而是让类型、权威、人生角色和已定义结构共同决定工作方式。",
    ]
    if _has_channel(chart, "02-14"):
        bullets.append("G中心与荐骨中心被 02-14 直接连起来，说明方向感和可持续供能必须绑在一起看。")
        bullets.append("你不是靠临场证明赢，而是靠长期把资源、时间和注意力投进同一条对的路。")
    elif chart.channels:
        bullets.append(
            f"当前已定义通道是 {_channel_summary(chart)}；职业定位必须从这些真实稳定回路出发，不能套用不存在的通道模板。"
        )
        bullets.append(f"任何长期方向都先经过「{authority_label}」确认，再考虑市场前景、关系机会和商业包装。")
    else:
        bullets.append("当前没有固定通道，职业稳定感更依赖正确环境、正确关系和对开放中心压力的识别。")
        bullets.append(f"越是外界声音很多，越要让「{authority_label}」成为进入机会和长期承诺的阀门。")
    sources = _sources(
        ("type", get_type_card(chart.summary.type.code)),
        ("authority", get_authority_card(chart.summary.authority.code)),
        ("profile", get_profile_card(chart.summary.profile.code)),
        *_channel_source_items(chart),
    )
    return ReadingSection(
        key="career-thesis",
        title="职业命题",
        summary=thesis,
        bullets=tuple(bullets),
        sources=sources,
    )


def _money_engine_section(chart: HumanDesignChart) -> ReadingSection:
    authority_label = display_authority(chart.summary.authority.code, chart.summary.authority.label)
    profile_label = display_profile(chart.summary.profile.code, chart.summary.profile.label)
    bullets = [
        f"赚钱入口先过「{authority_label}」：不是每个看起来赚钱的机会都值得长期投入。",
        f"{profile_label} 人生角色会影响你被市场看见的方式；收入结构要顺着你的学习、关系和角色展开方式设计。",
    ]
    if chart.channels:
        bullets.append(f"把已定义通道（{_channel_summary(chart)}）转成可复用资产：产品、方法、案例、内容、服务流程或客户信任。")
    else:
        bullets.append("没有固定通道时，不要用高强度硬撑来制造稳定感；更适合用清晰边界、正确场域和可复制流程来承接机会。")
    if _has_gate(chart, 14):
        bullets.append("14 号闸门强调资源投放：钱不是单纯来自忙，而是来自把资源集中给真正值得的方向。")
    if _has_gate(chart, 29):
        bullets.append("29 号闸门强调承诺深度：一旦答应就容易整个人进去，所以错误承诺会直接吞掉赚钱能力。")
    if _has_gate(chart, 5):
        bullets.append("5 号闸门强调节律：你的收入结构更适合稳定复利，而不是长期靠临场爆发和高频接活。")
    if _has_open_center(chart, "heart"):
        bullets.append("开放意志中心会让你想用成果证明价值；这会诱导你低价多接、过度承诺、用忙碌补价值感。")
    elif _has_defined_center(chart, "heart"):
        bullets.append("已定义意志中心适合把承诺、定价和资源交换说清楚；关键是只承诺真正愿意承担的事情。")
    return ReadingSection(
        key="career-money-engine",
        title="赚钱结构",
        summary=(
            "你的赚钱结构不是高频换机会，而是把一个能长期生长的能力、产品或方法论做成资产。"
            "对你来说，最贵的不是能力不足，而是把能力投给了不值得长期供能的方向。"
        ),
        bullets=tuple(bullets),
        sources=_sources(
            ("profile", get_profile_card(chart.summary.profile.code)),
            ("center", get_center_card("heart")),
            *_active_gate_source_items(chart, (14, 29, 5)),
            *_channel_source_items(chart),
        ),
    )


def _market_entry_section(chart: HumanDesignChart) -> ReadingSection:
    profile_label = display_profile(chart.summary.profile.code, chart.summary.profile.label)
    bullets = [
        f"{profile_label} 的市场入口要顺着人生角色来设计：你不需要模仿所有人的获客方式。",
    ]
    if _profile_has_line(chart, 2):
        bullets.append("2线需要独处熟成：真正值钱的东西常常先在你自己的空间里长出来，不适合一开始就被外界需求撕碎。")
    if _profile_has_line(chart, 4):
        bullets.append("4线通过关系展开：机会更适合从熟人网络、口碑、信任场、长期合作中放大。")
    if _has_open_center(chart, "throat"):
        bullets.append("开放喉中心不适合长期靠抢话语权生存；你更适合用作品、产品、方法和结果替你说话。")
    elif _has_defined_center(chart, "throat"):
        bullets.append("已定义喉中心适合把表达做成稳定出口；关键是让表达服务定位，而不是被外界节奏牵走。")
    if _has_gate(chart, 13):
        bullets.append("13 号闸门适合用户研究、访谈、咨询、社群、教育与内容沉淀，因为你能听见经验背后的脉络。")
    if _has_gate(chart, 17):
        bullets.append("17 号闸门适合策略、分析、教学和框架输出，但它必须接受验证，不能把观点当成最终真理。")
    return ReadingSection(
        key="career-market-entry",
        title="机会入口",
        summary=(
            "你不是陌生市场硬推型，更像先把能力养熟，再通过正确关系网络被看见。"
            "你的市场入口不是更吵，而是更可信。"
        ),
        bullets=tuple(bullets),
        sources=_sources(
            ("profile", get_profile_card(chart.summary.profile.code)),
            ("center", get_center_card("throat")),
            *_active_gate_source_items(chart, (13, 17)),
        ),
    )


def _role_section(chart: HumanDesignChart) -> ReadingSection:
    type_label = display_type(chart.summary.type.code, chart.summary.type.label)
    role_fragments = [
        f"工作方式：先按「{type_label}」的能量机制选环境和节奏，不要只按岗位名称判断适不适合。",
        "方法提炼者：从用户故事、现场经验和复杂信息里提炼可复用结构。",
        "长期建设者：围绕同一主题持续打磨产品、内容、服务或体系。",
    ]
    for channel in chart.channels[:3]:
        card = get_channel_card(channel.code)
        if card and card.focus.get("career"):
            role_fragments.append(f"通道 {channel.code}：{card.focus['career']}")
        else:
            role_fragments.append(f"通道 {channel.code}：这是你能稳定调用的职业回路，适合沉淀成角色优势。")
    if not chart.channels:
        role_fragments.append("没有固定通道时，职业位置不宜靠硬标签锁死，更要靠场域匹配、项目筛选和边界管理来稳定。")
    if _has_gate(chart, 7):
        role_fragments.append("集体方向感：7 号闸门让你天然会观察团队或群体该往哪里走。")
    if _has_gate(chart, 13):
        role_fragments.append("经验倾听者：13 号闸门让你适合吸收故事、理解脉络，并把经验沉淀成洞察。")
    if _has_gate(chart, 17):
        role_fragments.append("观点结构者：17 号闸门让你适合做框架、分析和策略输出，但需要现实验证。")
    return ReadingSection(
        key="career-role-architecture",
        title="职业位置",
        summary=(
            "你的职业位置要从真实已定义结构出发。"
            "如果把自己放到长期违背类型、权威和通道的位置，盘里的核心能力会被压扁。"
        ),
        bullets=tuple(role_fragments),
        sources=_sources(
            ("type", get_type_card(chart.summary.type.code)),
            *_channel_source_items(chart),
            *_active_gate_source_items(chart, (7, 13, 17)),
        ),
    )


def _distortion_loop_section(chart: HumanDesignChart) -> ReadingSection:
    authority_label = display_authority(chart.summary.authority.code, chart.summary.authority.label)
    loop_parts: list[str] = []
    if _has_open_center(chart, "head") or _has_open_center(chart, "ajna"):
        loop_parts.append("开放头顶/阿姬娜容易把焦虑包装成必须立刻想清楚")
    if _has_open_center(chart, "root"):
        loop_parts.append("开放根部容易把外界压力放大成马上解决")
    if _has_open_center(chart, "heart"):
        loop_parts.append("开放意志容易用成果、价格或承诺证明自己值钱")
    if _has_open_center(chart, "throat"):
        loop_parts.append("开放喉中心容易为了被看见而抢表达、抢机会")
    if _has_gate(chart, 29):
        loop_parts.append("29 号闸门会让你在错误时机答应到底")
    if _has_gate(chart, 63) or _has_gate(chart, 64):
        loop_parts.append("63/64 的压力会把怀疑和混乱推成过度分析")
    loop = "，".join(loop_parts) if loop_parts else "这张盘的职业误判更可能来自跳过自己的权威、被外界节奏带走，或把短期机会误当长期方向"
    bullets = [
        f"第一步：先分辨当前决定是来自「{authority_label}」，还是来自焦虑、证明、怕错过和外界催促。",
        "第二步：任何会影响长期方向、定价、合作关系的决定，都不要在压力最高的时候当场定。",
        "第三步：把承诺写成边界清楚的范围、周期、交付物和退出条件，而不是一句模糊的“我可以”。",
    ]
    if _has_gate(chart, 29):
        bullets.append("如果 29 号闸门被激活，尤其要防止一时答应后长期被错误项目绑定。")
    else:
        bullets.append("即使没有强承诺主题被激活，也要避免用短期热度替代长期方向判断。")
    bullets.append("真正要练的不是更努力，而是在承诺前识别误判链有没有启动。")
    return ReadingSection(
        key="career-distortion-loop",
        title="职业误判环路",
        summary=(
            f"{loop}。这会形成一个很隐蔽的职业陷阱：你不是做不成，而是可能把不属于你的事也做得很认真。"
        ),
        bullets=tuple(bullets),
        sources=_sources(
            *_open_center_source_items(chart, ("head", "ajna", "root", "heart", "throat")),
            *_active_gate_source_items(chart, (29, 63, 64)),
            ("authority", get_authority_card(chart.summary.authority.code)),
        ),
    )


def _direction_filter_section(chart: HumanDesignChart) -> ReadingSection:
    authority_label = display_authority(chart.summary.authority.code, chart.summary.authority.label)
    bullets = [
        f"权威门槛：这件事能不能通过「{authority_label}」确认，而不是头脑觉得应该。",
        "承诺门槛：如果它要你持续做两三年，你是否仍然愿意把生命力投进去。",
        "资产门槛：它能不能沉淀成产品、内容、方法、客户信任、数据或系统。",
        "表达门槛：它是否允许你用作品和结构说话，而不是长期逼你临场表演。",
        "关系门槛：它能不能进入你的信任网络，让机会通过正确的人和场域放大。",
        "代价门槛：它是否长期触发证明、赶快、怕错过和过度承诺。",
    ]
    if _has_channel(chart, "02-14"):
        summary = (
            "你选方向不能只看前景和收入，要先看它是否配得上 02-14 的长期资源投放。"
            "对你来说，错误方向的机会越大，损耗越大。"
        )
        bullets.insert(1, "资源门槛：它是否值得 02-14 持续投放时间、钱、人、注意力和执行力。")
    else:
        summary = (
            "你选方向不能只看前景和收入，要先看它是否符合你的权威、人生角色、已定义中心和真实通道。"
            "对你来说，错误方向的机会越大，后续修正成本越高。"
        )
    return ReadingSection(
        key="career-direction-filter",
        title="方向筛选门槛",
        summary=summary,
        bullets=tuple(bullets),
        sources=_sources(
            ("authority", get_authority_card(chart.summary.authority.code)),
            ("profile", get_profile_card(chart.summary.profile.code)),
            *_channel_source_items(chart),
            *_active_gate_source_items(chart, (14, 29)),
        ),
    )


def _has_channel(chart: HumanDesignChart, code: str) -> bool:
    return any(channel.code == code for channel in chart.channels)


def _has_gate(chart: HumanDesignChart, gate: int) -> bool:
    return any(item.gate == gate for item in chart.activated_gates)


def _has_open_center(chart: HumanDesignChart, code: str) -> bool:
    return any(center.code == code and not center.defined for center in chart.centers)


def _has_defined_center(chart: HumanDesignChart, code: str) -> bool:
    return any(center.code == code and center.defined for center in chart.centers)


def _profile_has_line(chart: HumanDesignChart, line: int) -> bool:
    return str(line) in chart.summary.profile.code.split("-")


def _channel_summary(chart: HumanDesignChart) -> str:
    return ", ".join(channel.code for channel in chart.channels) or "无固定通道"


def _channel_source_items(chart: HumanDesignChart) -> tuple[tuple[str, object], ...]:
    return tuple(("channel", get_channel_card(channel.code)) for channel in chart.channels)


def _active_gate_source_items(
    chart: HumanDesignChart,
    gates: tuple[int, ...],
) -> tuple[tuple[str, object], ...]:
    return tuple(("gate", get_gate_card(gate)) for gate in gates if _has_gate(chart, gate))


def _open_center_source_items(
    chart: HumanDesignChart,
    center_codes: tuple[str, ...],
) -> tuple[tuple[str, object], ...]:
    return tuple(("center", get_center_card(code)) for code in center_codes if _has_open_center(chart, code))


def _sources(*items) -> tuple[SourceReference, ...]:
    seen: set[tuple[str, str, str]] = set()
    sources: list[SourceReference] = []
    for kind, card in items:
        if card is None:
            continue
        source = to_source_reference(kind, card)
        key = (source.kind, source.code, source.path)
        if key in seen:
            continue
        seen.add(key)
        title = normalize_center_title(source.title) if kind == "center" else source.title
        sources.append(
            SourceReference(
                kind=source.kind,
                code=source.code,
                title=title,
                path=source.path,
            )
        )
    return tuple(sources)
