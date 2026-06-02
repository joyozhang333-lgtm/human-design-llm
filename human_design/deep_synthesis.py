from __future__ import annotations

from dataclasses import asdict, dataclass

from .knowledge import (
    get_authority_card,
    get_channel_card,
    get_center_card,
    get_gate_card,
    get_profile_card,
    get_type_card,
    to_source_reference,
)
from .labels import (
    CENTER_LABELS,
    display_authority,
    display_profile,
    display_strategy,
    display_type,
    normalize_center_title,
)
from .schema import HumanDesignChart, ReadingSection, SourceReference


RESEARCH_DIGEST_PATH = "docs/research/human-design-source-digest-2026-06.md"

RESEARCH_METHOD_NOTES = (
    "先读盘面事实，再读解释：类型、策略、权威、人生角色、定义、中心、通道、闸门和轮回交叉必须同时进入判断。",
    "优先使用官方源头、经典书籍结构和本地知识卡；公开视频、播客和中文资料只用于表达语感和练习设计。",
    "不把单一标签当结论：不能只因为某人是 2/4、生产者或某个闸门，就给出可套给所有人的性格话术。",
    "把开放中心视为学习场和条件化入口，不把它写成缺陷；把“淤堵”解释为可观察的消耗模式。",
    "每个深度结论都要落到具体生活实验：身体回应、关系召唤、资源投放、边界、表达、复盘。",
)

RESEARCH_SOURCES = (
    SourceReference(
        kind="research",
        code="official-foundation",
        title="Jovian Archive / Ra.TV / Ra Uru Hu 官方源头资料",
        path=RESEARCH_DIGEST_PATH,
    ),
    SourceReference(
        kind="research",
        code="classic-books",
        title="The Definitive Book of Human Design 等经典书籍结构",
        path=RESEARCH_DIGEST_PATH,
    ),
    SourceReference(
        kind="research",
        code="practice-voices",
        title="YouTube / podcast / 中文世界实践表达吸收",
        path=RESEARCH_DIGEST_PATH,
    ),
    SourceReference(
        kind="research",
        code="anthropology",
        title="厚描、礼物交换、阈限与共同体的人类学补充视角",
        path=RESEARCH_DIGEST_PATH,
    ),
)

GATE_TALENT_MODULES: dict[int, tuple[str, str, str]] = {
    2: (
        "方向接收",
        "能在复杂场域里感到哪条路更有生命力，适合做方向校准、路线选择和承接型主理。",
        "不要把顺势误读成被动，也不要为了控制感强行主导一切。",
    ),
    5: (
        "节律建设",
        "擅长把长期任务放进稳定节奏，让产品、内容、关系和身体状态形成复利。",
        "不要因为怕错过而打乱节律，也不要把等待变成逃避推进。",
    ),
    13: (
        "厚描倾听",
        "能听见故事背后的关系、历史和未说完的情绪，适合访谈、咨询、用户研究和生命叙事整理。",
        "不要把别人的故事全部背到自己身上，倾听之后必须有清理和边界。",
    ),
    14: (
        "资源配置",
        "能感到时间、钱、人、注意力和执行力该投向哪里，适合把能力沉淀成资产和主航道。",
        "不要用资源证明价值；错误方向越大，生命力损耗越大。",
    ),
    17: (
        "框架化表达",
        "能从事实和模式里提炼观点、结构和方法论，适合策略、研究、教学、产品文档和 AI workflow。",
        "不要过早把观点当真理；观点必须接受现实验证。",
    ),
    27: (
        "有边界的滋养",
        "能设计持续支持人的产品、关系或服务，让照顾从临时情绪变成稳定供养。",
        "不要把照顾活成牺牲，也不要让用户、朋友或客户吞掉你的身体资源。",
    ),
    28: (
        "意义攻坚",
        "不怕难，适合处理真正值得的复杂课题，把挑战转成存在感和长期贡献。",
        "不要为了证明自己活着而抓错战场；刺激不等于意义。",
    ),
    29: (
        "深度承诺",
        "一旦答应就能深度进入经验，适合长期项目、陪跑、产品打磨和需要可信度的承诺。",
        "你的 yes 很贵；错误承诺会把能力、时间和身体状态一起拖走。",
    ),
    34: (
        "原始生命力",
        "身体里有强劲行动能量，适合把真实回应快速转成具体推进。",
        "不要把力量用在没有回应的事情上，否则强能量会变成强消耗。",
    ),
    35: (
        "经验转译",
        "能从经历、变化和阶段推进里提炼故事与方法，把走过的路讲成别人能用的经验。",
        "不要为了新鲜感一直换场；经历必须沉淀，不然只剩消耗。",
    ),
    60: (
        "限制转化",
        "能在现实限制里找到可执行边界，把混乱愿景压成可落地版本。",
        "不要把限制当失败；真正的创造经常从边界开始。",
    ),
    61: (
        "内在真理压力",
        "对深层答案、根本问题和不可见逻辑有持续追问，适合研究本质与精神性议题。",
        "不要把每个问题都逼成立刻答案；压力需要容器和节律。",
    ),
    63: (
        "问题定位",
        "能敏感发现逻辑漏洞、证据不足和系统没说透的地方，适合评审、研究、诊断和产品校准。",
        "不要让怀疑变成焦虑循环；成熟的怀疑要导向验证问题。",
    ),
    64: (
        "混乱整合",
        "能把碎片、经历和信息雾团慢慢拼成结构，适合资料整理、体系化和复杂叙事重建。",
        "不要急着在混乱里抢答案；先允许材料沉淀，再形成线索。",
    ),
}

GATE_TALENT_PRIORITY = (2, 14, 63, 64, 5, 35, 13, 17, 27, 28, 29, 34, 60, 61)


@dataclass(frozen=True)
class DeepSynthesisProfile:
    headline: str
    thesis: str
    structure_formula: str
    research_method_notes: tuple[str, ...]
    sections: tuple[ReadingSection, ...]
    non_genericity_checks: tuple[str, ...]
    suggested_experiments: tuple[str, ...]
    research_sources: tuple[SourceReference, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_deep_synthesis_profile(
    chart: HumanDesignChart,
    *,
    focus: str = "talent",
    question: str | None = None,
) -> DeepSynthesisProfile:
    type_label = display_type(chart.summary.type.code, chart.summary.type.label)
    authority_label = display_authority(chart.summary.authority.code, chart.summary.authority.label)
    profile_label = display_profile(chart.summary.profile.code, chart.summary.profile.label)
    formula = build_structure_formula(chart)
    thesis = _build_thesis(chart, type_label, authority_label, profile_label)
    sections = build_deep_synthesis_sections(chart, focus=focus, question=question)
    return DeepSynthesisProfile(
        headline=f"{profile_label} | {authority_label} {type_label} 天赋深挖",
        thesis=thesis,
        structure_formula=formula,
        research_method_notes=RESEARCH_METHOD_NOTES,
        sections=sections,
        non_genericity_checks=_build_non_genericity_checks(chart),
        suggested_experiments=_build_suggested_experiments(chart),
        research_sources=RESEARCH_SOURCES,
    )


def build_deep_synthesis_sections(
    chart: HumanDesignChart,
    *,
    focus: str = "talent",
    question: str | None = None,
) -> tuple[ReadingSection, ...]:
    return (
        _method_section(chart, focus, question),
        _structure_section(chart),
        _talent_axis_section(chart),
        _cross_pressure_section(chart),
        _talent_modules_section(chart),
        _consumption_loop_section(chart),
        _experiments_section(chart),
    )


def render_deep_synthesis_markdown(profile: DeepSynthesisProfile) -> str:
    lines = [
        "# 人类图天赋深挖",
        "",
        profile.headline,
        "",
        profile.thesis,
        "",
        f"结构公式：{profile.structure_formula}",
        "",
        "## 研究方法",
    ]
    for note in profile.research_method_notes:
        lines.append(f"- {note}")
    for section in profile.sections:
        lines.extend(("", f"## {section.title}", section.summary))
        for bullet in section.bullets:
            lines.append(f"- {bullet}")
    lines.extend(("", "## 非泛化检查"))
    for item in profile.non_genericity_checks:
        lines.append(f"- {item}")
    lines.extend(("", "## 30 天实验"))
    for item in profile.suggested_experiments:
        lines.append(f"- {item}")
    return "\n".join(lines).strip() + "\n"


def research_context_text() -> str:
    lines = ["本轮深度解读采用以下资料吸收和输出约束："]
    lines.extend(f"- {note}" for note in RESEARCH_METHOD_NOTES)
    lines.append("- 资料底稿见 docs/research/human-design-source-digest-2026-06.md。")
    return "\n".join(lines)


def research_source_references() -> tuple[SourceReference, ...]:
    return RESEARCH_SOURCES


def build_structure_formula(chart: HumanDesignChart) -> str:
    defined_centers = "、".join(_center_labels(chart, defined=True)) or "无已定义中心"
    channels = "、".join(f"{channel.code}「{channel.label}」" for channel in chart.channels) or "无固定通道"
    p_sun = _activation_gate(chart, "personality", "sun")
    p_earth = _activation_gate(chart, "personality", "earth")
    d_sun = _activation_gate(chart, "design", "sun")
    d_earth = _activation_gate(chart, "design", "earth")
    cross = f"{p_sun}/{p_earth} | {d_sun}/{d_earth}" if all((p_sun, p_earth, d_sun, d_earth)) else chart.summary.incarnation_cross.label
    return (
        f"{display_type(chart.summary.type.code, chart.summary.type.label)} + "
        f"{display_authority(chart.summary.authority.code, chart.summary.authority.label)} + "
        f"{display_profile(chart.summary.profile.code, chart.summary.profile.label)} + "
        f"{defined_centers} + {channels} + {cross}"
    )


def _method_section(chart: HumanDesignChart, focus: str, question: str | None) -> ReadingSection:
    question_line = f"本轮问题是「{question}」，所以会优先从这个切口筛选结构。" if question else "本轮先做完整天赋深挖，不只回应某一个表层标签。"
    bullets = (
        "不是只按人生角色、类型或某个闸门单点判断；必须把核心机制、稳定定义、开放消耗和具体生活场景叠加。",
        "官方源头用于确定读图顺序：策略与权威是实验入口，中心/通道/闸门是身体结构语言。",
        "人类学视角用于防泛化：先看具体关系、具体场域、具体故事，再把天赋翻译成可验证实践。",
        question_line,
    )
    return ReadingSection(
        key="deep-method",
        title="深读方法",
        summary=(
            "这份报告采用“盘面事实先行 + 资料来源约束 + 结构叠加 + 生活实验”的方法。"
            "目标不是把你写成一个标签，而是找出这张图如何在身体、关系和产品/工作里实际运作。"
        ),
        bullets=bullets,
        sources=RESEARCH_SOURCES,
    )


def _structure_section(chart: HumanDesignChart) -> ReadingSection:
    formula = build_structure_formula(chart)
    profile_label = display_profile(chart.summary.profile.code, chart.summary.profile.label)
    bullets = [
        f"结构公式：{formula}。",
        f"「{profile_label}」只说明你的角色展开方式，不能单独推出职业、性格或天赋结论。",
        f"策略「{display_strategy(chart.summary.strategy.code, chart.summary.strategy.label)}」和权威「{display_authority(chart.summary.authority.code, chart.summary.authority.label)}」决定你如何进入机会与确认选择。",
    ]
    if chart.channels:
        bullets.append(f"已定义通道是 {_channel_summary(chart)}；这些才是身体里稳定重复出现的天赋回路。")
    else:
        bullets.append("当前没有固定通道，稳定感更依赖正确环境、关系和对开放中心条件化的识别。")
    return ReadingSection(
        key="deep-structure",
        title="结构叠加",
        summary=(
            "真正的深读从完整结构开始。"
            "同一个人生角色，放在不同类型、权威、中心、通道和轮回交叉里，会长成完全不同的生命形态。"
        ),
        bullets=tuple(bullets),
        sources=_sources(
            ("type", get_type_card(chart.summary.type.code)),
            ("authority", get_authority_card(chart.summary.authority.code)),
            ("profile", get_profile_card(chart.summary.profile.code)),
            *_channel_source_items(chart),
        ),
    )


def _talent_axis_section(chart: HumanDesignChart) -> ReadingSection:
    if _has_channel(chart, "02-14"):
        summary = (
            "这张图的核心天赋轴不是“表达得多漂亮”，而是“方向化”："
            "把生命力、资源、注意力和机会放进真正值得长期供能的主航道。"
        )
        bullets = (
            "2 号闸门提供方向接收：不是靠硬推控制一切，而是在对的场域里感到路该往哪里走。",
            "14 号闸门提供资源与生命力调度：钱、时间、技术、人和注意力要集中到对的方向。",
            "02-14 连通 G中心与荐骨中心，所以方向感和持续供能必须绑在一起；方向不对时，越努力越挫败。",
            "成熟用法是先让身体确认，再把资源投进去；不要先用头脑证明这个方向“应该正确”。",
        )
        sources = _sources(
            ("channel", get_channel_card("02-14")),
            ("gate", get_gate_card(2)),
            ("gate", get_gate_card(14)),
            ("center", get_center_card("g")),
            ("center", get_center_card("sacral")),
        )
    elif chart.channels:
        first = chart.channels[0]
        card = get_channel_card(first.code)
        summary = (
            f"你的第一条稳定通道是 {first.code}「{first.label}」。"
            "深读时先看这条通道如何把两个中心接成固定回路，再看它如何服务现实场景。"
        )
        bullets = tuple(
            f"通道 {channel.code}「{channel.label}」：{_channel_focus_text(channel.code)}"
            for channel in chart.channels[:4]
        )
        sources = _sources(*_channel_source_items(chart))
        if card is not None:
            sources = _unique_sources((to_source_reference("channel", card), *sources))
    else:
        summary = "这张图没有固定通道，天赋更像环境和关系中被点亮的流动能力，而不是一个固定输出管道。"
        bullets = (
            "不要用“我必须一直稳定输出”要求自己；重点是找到对的场域、对的人和对的提问。",
            "开放中心会带来很强的学习能力，但也更需要过滤外界压力。",
            "决策仍然要回到类型、策略和权威，而不是临场被环境推着走。",
        )
        sources = _sources(
            ("type", get_type_card(chart.summary.type.code)),
            ("authority", get_authority_card(chart.summary.authority.code)),
        )
    return ReadingSection(
        key="deep-talent-axis",
        title="核心天赋轴",
        summary=summary,
        bullets=bullets,
        sources=sources,
    )


def _cross_pressure_section(chart: HumanDesignChart) -> ReadingSection:
    p_sun = _activation_gate(chart, "personality", "sun")
    p_earth = _activation_gate(chart, "personality", "earth")
    d_sun = _activation_gate(chart, "design", "sun")
    d_earth = _activation_gate(chart, "design", "earth")
    cross_label = chart.summary.incarnation_cross.label
    bullets: list[str] = []
    if p_sun and p_earth:
        bullets.append(f"人格太阳/地球 {p_sun}/{p_earth}：这是你更显性、更容易被自己意识到的驱动力和平衡点。")
    if d_sun and d_earth:
        bullets.append(f"设计太阳/地球 {d_sun}/{d_earth}：这是更身体化、未必总能被头脑解释清楚的底层驱动。")
    if {p_sun, p_earth, d_sun, d_earth} >= {63, 64, 5, 35}:
        summary = (
            "你的主轴很适合把“怀疑、混乱、节律、经验”串起来："
            "先发现问题和碎片，再用稳定节奏把经历转成可讲、可用、可产品化的方法。"
        )
        bullets.extend(
            (
                "63 号闸门让你对“这是真的吗、哪里没说透”很敏感；成熟时是问题定位，不成熟时是焦虑怀疑。",
                "64 号闸门让你面对大量碎片和未完成线索；成熟时是整合能力，不成熟时是想马上摆脱混乱。",
                "5 号闸门要求节律；35 号闸门要求把经验讲成进步。两者合起来，是把混乱研究变成可用产品的关键。",
            )
        )
    else:
        summary = (
            f"你的轮回交叉「{cross_label}」更像人生反复会遇到、也会反复贡献出去的主题。"
            "它不是职业名称，也不是命定剧本，而是要通过策略与权威活成的主轴。"
        )
        for gate in (p_sun, p_earth, d_sun, d_earth):
            if gate:
                bullets.append(_gate_theme_sentence(gate))
    return ReadingSection(
        key="deep-cross-pressure",
        title="轮回交叉与意识压力",
        summary=summary,
        bullets=tuple(bullets),
        sources=_sources(*_active_gate_source_items(chart, (p_sun, p_earth, d_sun, d_earth))),
    )


def _talent_modules_section(chart: HumanDesignChart) -> ReadingSection:
    selected = _selected_talent_gates(chart)
    bullets: list[str] = []
    for gate in selected:
        title, gift, risk = GATE_TALENT_MODULES.get(gate, _fallback_gate_module(gate))
        bullets.append(f"{title}（{gate}号闸门）：{gift} 留意：{risk}")
    if not bullets:
        bullets.append("当前可用的天赋模块需要从已激活闸门继续扩展知识卡；本轮先以类型、权威、中心和通道为主。")
    return ReadingSection(
        key="deep-talent-modules",
        title="具体天赋模块",
        summary=(
            "下面只列这张图实际激活的闸门，不补不存在的能力。"
            "每个模块都同时包含礼物和风险，因为天赋一旦脱离策略、权威和边界，就会变成消耗。"
        ),
        bullets=tuple(bullets),
        sources=_sources(*_active_gate_source_items(chart, tuple(selected))),
    )


def _consumption_loop_section(chart: HumanDesignChart) -> ReadingSection:
    open_centers = tuple(center.code for center in chart.centers if not center.defined)
    chain = _open_center_chain(open_centers)
    bullets = [
        f"开放中心：{'、'.join(_center_labels(chart, defined=False)) or '无'}。",
        "开放中心不是缺陷，而是你最容易被外界条件化、也最能学习场域的地方。",
        "一旦发现自己开始急、硬撑、过度解释、证明价值或替别人消化情绪，就要回到策略与权威。",
    ]
    if _has_gate(chart, 29):
        bullets.append("29 号闸门会放大“答应后走到底”的惯性；开放中心被触发时尤其不要马上长期承诺。")
    if _has_channel(chart, "02-14"):
        bullets.append("02-14 的修复方式不是更努力，而是问：这件事到底是不是我的主航道，是否值得继续投资源？")
    return ReadingSection(
        key="deep-consumption-loop",
        title="消耗链与能量卡点",
        summary=chain,
        bullets=tuple(bullets),
        sources=_sources(
            *_open_center_source_items(chart),
            *_active_gate_source_items(chart, (29, 14, 2)),
            ("authority", get_authority_card(chart.summary.authority.code)),
        ),
    )


def _experiments_section(chart: HumanDesignChart) -> ReadingSection:
    return ReadingSection(
        key="deep-experiments",
        title="30 天验证实验",
        summary=(
            "深读必须能被生活验证。下面的实验不是为了证明人类图绝对正确，"
            "而是让你观察：哪些结构真的能解释你的身体、关系、工作和能量变化。"
        ),
        bullets=_build_suggested_experiments(chart),
        sources=_sources(
            ("authority", get_authority_card(chart.summary.authority.code)),
            ("profile", get_profile_card(chart.summary.profile.code)),
            *_channel_source_items(chart),
            *tuple(("gate", get_gate_card(gate)) for gate in _selected_talent_gates(chart)[:6]),
        ),
    )


def _build_thesis(
    chart: HumanDesignChart,
    type_label: str,
    authority_label: str,
    profile_label: str,
) -> str:
    if chart.summary.type.code == "pure-generator" and chart.summary.authority.code == "sacral" and _has_channel(chart, "02-14"):
        return (
            f"这张图的核心不是单纯“{profile_label} 会关系”或“{type_label} 能做事”，"
            f"而是用「{authority_label}」确认身体回应后，把 02-14 的方向感与资源投放放进一个长期主航道。"
            "你的天赋更像把混乱经验、真实故事、身体回应和资源方向整理成可持续产品或方法。"
        )
    if chart.channels:
        return (
            f"这张图要从「{type_label} + {authority_label} + {profile_label}」开始，"
            f"再落到已定义通道 {_channel_summary(chart)}。你的深层天赋不在标签本身，"
            "而在这些结构如何共同决定你该怎样进入机会、供能、表达和建立关系。"
        )
    return (
        f"这张图要从「{type_label} + {authority_label} + {profile_label}」开始，"
        "再观察开放中心如何读取环境。你的天赋更依赖正确场域和正确关系被点亮，不能用固定输出型模板理解。"
    )


def _build_non_genericity_checks(chart: HumanDesignChart) -> tuple[str, ...]:
    checks = [
        f"必须引用真实类型：{display_type(chart.summary.type.code, chart.summary.type.label)}。",
        f"必须引用真实权威：{display_authority(chart.summary.authority.code, chart.summary.authority.label)}。",
        f"必须引用真实人生角色：{display_profile(chart.summary.profile.code, chart.summary.profile.label)}。",
        f"必须引用真实已定义中心：{'、'.join(_center_labels(chart, defined=True)) or '无'}。",
        f"只能引用真实通道：{_channel_summary(chart) if chart.channels else '无固定通道'}。",
        "闸门解读只能来自 activated_gates，不得补不存在的通道或闸门。",
    ]
    if _has_channel(chart, "02-14"):
        checks.append("如果讨论赚钱、方向或天赋，必须解释 02-14 的方向/资源轴，而不是只讲性格。")
    if _has_gate(chart, 29):
        checks.append("如果讨论承诺、合作或项目，必须提示 29 号闸门的高质量说“是”与过度承诺风险。")
    return tuple(checks)


def _build_suggested_experiments(chart: HumanDesignChart) -> tuple[str, ...]:
    authority = display_authority(chart.summary.authority.code, chart.summary.authority.label)
    experiments = [
        f"身体权威日志：连续 30 天记录 10 个小决定，写下当时的「{authority}」信号、实际选择和 24 小时后的身体反馈。",
        "非泛化复盘：每周选一个具体场景，写出它对应的类型、权威、中心、通道或闸门，不用抽象性格词概括自己。",
    ]
    if chart.summary.profile.code == "2-4":
        experiments.append("2/4 召唤日志：记录哪些机会来自真实作品和信任关系，哪些只是别人临时投射给你的期待。")
    if _has_channel(chart, "02-14"):
        experiments.append("02-14 资源投放表：把项目按“身体回应、长期方向、资产沉淀、资源代价”各打 1-5 分，低分项目先暂停扩张。")
    if _has_gate(chart, 13):
        experiments.append("13 号厚描访谈：每周做 2 次深度倾听，只记录对方故事背后的重复模式、关系背景和真正需求。")
    if _has_gate(chart, 17):
        experiments.append("17 号观点验证：任何新观点先写成假设、证据、反例和下一步验证，不要直接当最终判断发布。")
    if _has_gate(chart, 29):
        experiments.append("29 号承诺冷却：所有超过 2 周的新合作都延迟 24 小时答复，并写清交付范围、退出条件和资源代价。")
    if not any(_has_gate(chart, gate) for gate in (13, 17, 29)) and chart.activated_gates:
        gate = chart.activated_gates[0].gate
        experiments.append(f"{gate} 号闸门观察：每天记录它什么时候让你更有生命力，什么时候变成执念或消耗。")
    return tuple(experiments[:7])


def _selected_talent_gates(chart: HumanDesignChart) -> tuple[int, ...]:
    active = {gate.gate for gate in chart.activated_gates}
    selected = [gate for gate in GATE_TALENT_PRIORITY if gate in active]
    for gate in sorted(active):
        if gate not in selected:
            selected.append(gate)
        if len(selected) >= 8:
            break
    return tuple(selected[:8])


def _fallback_gate_module(gate: int) -> tuple[str, str, str]:
    card = get_gate_card(gate)
    if card is None:
        return ("天赋入口", "这是当前图中实际激活的闸门，适合作为生活观察入口。", "不要脱离类型、权威和具体场景单独断言。")
    gift = card.gifts[0] if card.gifts else f"能在「{card.title}」主题上形成稳定贡献。"
    shadow = card.shadows[0] if card.shadows else "失衡时会被焦虑、证明或外界压力带偏。"
    return (card.title, gift, shadow)


def _open_center_chain(open_centers: tuple[str, ...]) -> str:
    parts: list[str] = []
    if "head" in open_centers or "ajna" in open_centers:
        parts.append("开放头顶/阿姬娜把外界问题放大成“我必须马上想清楚”")
    if "root" in open_centers:
        parts.append("开放根部把外界压力放大成“我必须马上做完”")
    if "heart" in open_centers:
        parts.append("开放意志把价值感压力放大成“我必须证明自己”")
    if "throat" in open_centers:
        parts.append("开放喉咙把被看见压力放大成“我必须马上表达”")
    if "solar-plexus" in open_centers:
        parts.append("开放情绪把别人的波动放大成“我必须让场面稳定”")
    if "spleen" in open_centers:
        parts.append("开放脾把熟悉感误读成安全")
    if "g" in open_centers:
        parts.append("开放 G中心让环境和关系强烈影响方向感")
    if "sacral" in open_centers:
        parts.append("开放荐骨容易把别人的工作节奏误当成自己的持续力")
    if not parts:
        return "这张图开放中心较少，消耗链更可能来自跳过自己的策略与权威，或把稳定定义用在错误场景。"
    return " → ".join(parts) + "。这条链一旦启动，先暂停承诺，再回到身体权威和真实场景。"


def _channel_focus_text(code: str) -> str:
    card = get_channel_card(code)
    if card is None:
        return "这是你身体里稳定重复出现的能量路径，适合观察它在哪些场景自然启动。"
    return card.focus.get("growth") or card.summary


def _gate_theme_sentence(gate: int) -> str:
    card = get_gate_card(gate)
    if card is None:
        return f"{gate} 号闸门是当前轮回交叉的一部分，需要结合实际激活和生活场景观察。"
    return f"{gate} 号闸门「{card.title}」：{card.summary}"


def _activation_gate(chart: HumanDesignChart, imprint: str, planet_code: str) -> int | None:
    data = chart.personality if imprint == "personality" else chart.design
    for activation in data.activations:
        if activation.planet_code == planet_code:
            return activation.gate
    return None


def _center_labels(chart: HumanDesignChart, *, defined: bool) -> tuple[str, ...]:
    return tuple(
        normalize_center_title(CENTER_LABELS.get(center.code, center.label))
        for center in chart.centers
        if center.defined is defined
    )


def _channel_summary(chart: HumanDesignChart) -> str:
    return "、".join(f"{channel.code}「{channel.label}」" for channel in chart.channels)


def _has_channel(chart: HumanDesignChart, code: str) -> bool:
    return any(channel.code == code for channel in chart.channels)


def _has_gate(chart: HumanDesignChart, gate: int) -> bool:
    return any(item.gate == gate for item in chart.activated_gates)


def _active_gate_source_items(chart: HumanDesignChart, gates: tuple[int | None, ...]) -> tuple[tuple[str, object | None], ...]:
    active = {gate.gate for gate in chart.activated_gates}
    items: list[tuple[str, object | None]] = []
    seen: set[int] = set()
    for gate in gates:
        if gate is None or gate not in active or gate in seen:
            continue
        seen.add(gate)
        items.append(("gate", get_gate_card(gate)))
    return tuple(items)


def _channel_source_items(chart: HumanDesignChart) -> tuple[tuple[str, object | None], ...]:
    return tuple(("channel", get_channel_card(channel.code)) for channel in chart.channels)


def _open_center_source_items(chart: HumanDesignChart) -> tuple[tuple[str, object | None], ...]:
    return tuple(
        ("center", get_center_card(center.code))
        for center in chart.centers
        if not center.defined
    )


def _sources(*items: tuple[str, object | None]) -> tuple[SourceReference, ...]:
    sources: list[SourceReference] = []
    for kind, card in items:
        if card is None:
            continue
        sources.append(to_source_reference(kind, card))  # type: ignore[arg-type]
    return _unique_sources(tuple(sources))


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
