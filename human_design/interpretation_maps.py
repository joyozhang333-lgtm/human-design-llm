from __future__ import annotations

from datetime import UTC, datetime

from .labels import (
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
from .research_corpus import (
    atoms_by_id,
    build_prompt_pack,
    load_interpretation_rules,
    normalize_map_type,
    sources_by_id,
)
from .schema import (
    HumanDesignChart,
    InterpretationMapItem,
    InterpretationMapPackage,
    InterpretationMapSection,
    InterpretationRule,
    KnowledgeAtom,
    SourceCard,
    SourceReference,
)
from .version import VERSION

MAP_TITLES = {
    "body": ("身体地图", "看身体怎么回应、哪里容易被外界压力带走，以及能量要怎么回到自己身上。"),
    "wealth": ("财富地图", "看钱从哪里来、资源怎么配置、什么承诺会损耗你，以及该怎么形成长期资产。"),
    "talent": ("天赋地图", "看你的爻位、主通道、关键闸门和意识主题如何组合成可被使用的能力。"),
    "relationship": ("关系地图", "看你适合什么样的关系、边界如何设定，以及情绪和表达如何不失真。"),
    "mission": ("使命地图", "看策略、权威、主通道和轮回交叉如何落成长期人生主线。"),
    "professional": ("专业信息地图", "把专业配置、中心、通道、闸门和行星激活列清楚，作为所有解读的依据。"),
}

SECTION_TITLES = {
    "body": ("身体怎么运作", "看你什么时候有力、什么时候被外界带走，以及身体怎样回到稳定。"),
    "wealth": ("财富从哪里来", "看资源、承诺和主航道如何连成赚钱方式，而不是只给行业标签。"),
    "talent": ("天赋怎么形成", "看爻位、通道和关键闸门如何叠加成可以被练出来的能力。"),
    "relationship": ("关系怎么对位", "看你怎样连接、怎样被影响，以及什么关系会让你更像自己。"),
    "mission": ("人生主线怎么走", "看你如何进入正确事情，再让长期使命从行动里长出来。"),
    "professional": ("个人人类图简要", "这里列出你的核心配置，方便你核对每段解读来自哪里。"),
}

MAP_FOLLOWUPS = {
    "body": (
        "我怎么训练荐骨回应？",
        "我最容易在哪个开放中心被带跑？",
        "我现在能量低落时应该先检查什么？",
    ),
    "wealth": (
        "我最适合靠什么方式赚钱？",
        "哪些合作或客户最容易消耗我？",
        "我的定价和承诺边界应该怎么设？",
    ),
    "talent": (
        "我的 2/4 爻位怎么变成真实优势？",
        "02-14 通道如何变成事业主航道？",
        "63/64 和 5/35 怎么组合成判断力？",
    ),
    "relationship": (
        "什么样的人最适合我？",
        "我在关系里最容易被什么情绪带走？",
        "亲密关系里我该怎么表达边界？",
    ),
    "mission": (
        "我的人生使命怎么落地成具体方向？",
        "挫败感在提醒我偏离了哪里？",
        "我怎么判断一个机会是不是主线？",
    ),
    "professional": (
        "这些专业配置各自代表什么？",
        "哪几个结构最值得优先解读？",
        "这张图里有哪些事实不能被编造？",
    ),
}

DEEP_DIAGNOSIS_RULE_IDS = {
    "body.sacral-response-training",
    "body.open-pressure-chain",
    "wealth.02-14-main-track",
    "wealth.promise-boundary",
    "talent.profile-24",
    "talent.consciousness-cross",
    "relationship.emotional-boundary",
    "relationship.network-fit",
    "mission.generator-cross",
}


def build_interpretation_map(
    chart: HumanDesignChart,
    *,
    map_type: str = "talent",
    depth: str = "deep",
    chart_id: str | None = None,
) -> InterpretationMapPackage:
    map_key = normalize_map_type(map_type)
    chart_keys = _chart_keys(chart)
    selected_rules = tuple(
        rule
        for rule in load_interpretation_rules()
        if rule.map_type == map_key and _rule_matches(rule, chart_keys)
    )
    if not selected_rules:
        selected_rules = tuple(
            rule
            for rule in load_interpretation_rules()
            if rule.map_type == "professional" and _rule_matches(rule, chart_keys)
        )

    atom_lookup = atoms_by_id()
    source_lookup = sources_by_id()
    atom_ids = _unique(
        atom_id
        for rule in selected_rules
        for atom_id in rule.source_atom_ids
        if atom_id in atom_lookup
    )
    retrieved_atoms = tuple(atom_lookup[atom_id] for atom_id in atom_ids)
    source_cards = _source_cards_for_atoms(retrieved_atoms, source_lookup)
    prompt_pack = build_prompt_pack(
        map_key,
        atom_ids=tuple(atom.atom_id for atom in retrieved_atoms),
        rule_ids=tuple(rule.rule_id for rule in selected_rules),
    )
    title, description = MAP_TITLES[map_key]

    return InterpretationMapPackage(
        generated_at_utc=datetime.now(UTC).isoformat(),
        product_version=VERSION,
        map_type=map_key,
        title=title,
        description=description,
        chart_id=chart_id,
        professional_facts=_professional_facts(chart),
        sections=_build_sections(map_key, chart, selected_rules, atom_lookup, source_lookup, depth),
        prompt_pack=prompt_pack,
        retrieved_knowledge=retrieved_atoms,
        sources=source_cards,
        suggested_questions=MAP_FOLLOWUPS[map_key],
        chart=chart,
    )


def map_type_from_focus(focus: str | None) -> str:
    return {
        "growth": "body",
        "career": "wealth",
        "talent": "talent",
        "relationship": "relationship",
        "decision": "mission",
        "overview": "professional",
    }.get(focus or "", "talent")


def map_context_text(
    package: InterpretationMapPackage,
    *,
    selected_item_key: str | None = None,
    max_chars: int = 9000,
) -> str:
    lines = [
        f"地图：{package.title}",
        package.description,
        "",
        "专业事实：",
        *[f"- {fact}" for fact in package.professional_facts],
        "",
        "可引用地图条目：",
    ]
    selected_item = _find_item(package, selected_item_key)
    if selected_item is not None:
        lines.append("## 用户当前展开的条目")
        lines.append(f"### {selected_item.title}")
        lines.append("依据：" + "；".join(selected_item.chart_basis))
        lines.append(selected_item.user_language)
        _append_diagnosis_context(lines, selected_item)
        lines.append("")
    for section in package.sections:
        lines.append(f"## {section.title}")
        for item in section.items:
            lines.append(f"### {item.title}")
            lines.append("依据：" + "；".join(item.chart_basis))
            lines.append(item.user_language)
            _append_diagnosis_context(lines, item)
            if item.common_blocks:
                lines.append("常见卡点：" + "；".join(item.common_blocks))
            if item.practices:
                lines.append("练习：" + "；".join(item.practices))
    text = "\n".join(lines).strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n\n[地图上下文已截断]"


def _find_item(package: InterpretationMapPackage, item_key: str | None) -> InterpretationMapItem | None:
    if not item_key:
        return None
    for section in package.sections:
        for item in section.items:
            if item.key == item_key:
                return item
    return None


def _append_diagnosis_context(lines: list[str], item: InterpretationMapItem) -> None:
    lines.append(f"诊断深度：{item.diagnosis_depth}")
    if item.embodied_expression:
        lines.append("活出来：" + "；".join(item.embodied_expression))
    if item.blind_spots:
        lines.append("盲区：" + "；".join(item.blind_spots))
    if item.stuck_patterns:
        lines.append("卡住状态：" + "；".join(item.stuck_patterns))
    if item.stuck_causes:
        lines.append("卡住原因：" + "；".join(item.stuck_causes))


def _build_sections(
    map_key: str,
    chart: HumanDesignChart,
    selected_rules: tuple[InterpretationRule, ...],
    atom_lookup: dict[str, KnowledgeAtom],
    source_lookup: dict[str, SourceCard],
    depth: str,
) -> tuple[InterpretationMapSection, ...]:
    section_title, intro = SECTION_TITLES[map_key]
    items = [
        _rule_to_item(rule, chart, atom_lookup, source_lookup, depth)
        for rule in selected_rules
    ]
    if map_key == "professional":
        items.append(_professional_detail_item(chart))
    return (
        InterpretationMapSection(
            key=f"{map_key}-core",
            title=section_title,
            intro=intro,
            items=tuple(items),
        ),
    )


def _rule_to_item(
    rule: InterpretationRule,
    chart: HumanDesignChart,
    atom_lookup: dict[str, KnowledgeAtom],
    source_lookup: dict[str, SourceCard],
    depth: str,
) -> InterpretationMapItem:
    atoms = tuple(atom_lookup[atom_id] for atom_id in rule.source_atom_ids if atom_id in atom_lookup)
    chart_basis = _basis_for_rule(rule, chart, atoms)
    sources = _source_references_for_atoms(atoms, source_lookup)
    return InterpretationMapItem(
        key=rule.rule_id,
        title=rule.title,
        subtitle=_subtitle_for_rule(rule, chart),
        diagnosis_depth=_diagnosis_depth(rule),
        chart_basis=chart_basis,
        professional_basis=rule.professional_basis,
        user_language=_expanded_user_language(rule, chart, atoms, depth),
        life_scenes=_life_scenes(rule, chart),
        embodied_expression=_embodied_expression(rule, chart),
        blind_spots=_blind_spots(rule, chart),
        stuck_patterns=_stuck_patterns(rule, chart),
        stuck_causes=_stuck_causes(rule, chart),
        common_blocks=_common_blocks(rule, chart),
        practices=(rule.practice_template, *_extra_practices(rule, chart)),
        followup_questions=_item_followups(rule),
        source_atom_ids=rule.source_atom_ids,
        sources=sources,
    )


def _professional_detail_item(chart: HumanDesignChart) -> InterpretationMapItem:
    summary = _summary(chart)
    personality_sun = next((item for item in chart.personality.activations if item.planet_code == "sun"), None)
    design_sun = next((item for item in chart.design.activations if item.planet_code == "sun"), None)
    chart_basis = _professional_facts(chart)
    if personality_sun and design_sun:
        chart_basis = (
            *chart_basis,
            f"人格太阳：{personality_sun.gate}.{personality_sun.line}",
            f"设计太阳：{design_sun.gate}.{design_sun.line}",
        )
    user_language = (
        "这张图的简要信息，是你阅读所有解读时的底盘。"
        f"你的类型是{summary['type']}，策略是{summary['strategy']}，权威是{summary['authority']}，"
        f"人生角色是{summary['profile']}。关于工作、财富、关系或使命的判断，都要能回到这些事实，"
        "再落到已定义中心、开放中心、通道、闸门和行星激活。"
    )
    return InterpretationMapItem(
        key="professional.chart-facts",
        title="这张图的事实清单",
        subtitle="用来防止泛泛解读和编造图表事实",
        diagnosis_depth="trace",
        chart_basis=chart_basis,
        professional_basis="人类图解读必须先有图表事实，再从事实进入解释。",
        user_language=user_language,
        life_scenes=("当你读到一段解读时，可以回到这里检查依据。", "当聊天回答变得泛时，可以要求系统指出对应中心、通道或闸门。"),
        embodied_expression=(),
        blind_spots=("只看结论、不查图表依据时，很容易把一段听起来舒服的话误当成自己的真实结构。",),
        stuck_patterns=("读完很多术语但不知道怎么用，或者把不存在的中心、通道、闸门也当成自己的特质。",),
        stuck_causes=(),
        common_blocks=("只听结论，不检查依据。", "把术语当命运标签，而不是观察工具。"),
        practices=("每次读完一个地图条目，至少确认一个图表依据。",),
        followup_questions=("我这张图最核心的三个事实是什么？", "这段解读分别对应哪些中心、通道和闸门？"),
        source_atom_ids=("chart.fact-first",),
        sources=(
            SourceReference(
                kind="research",
                code="jovian-chart-kb",
                title="What is a Human Design Chart?",
                path="https://support.jovianarchive.com/hc/en-us/articles/15883298680465-What-is-a-Human-Design-Chart",
            ),
        ),
    )


def _diagnosis_depth(rule: InterpretationRule) -> str:
    if rule.rule_id in DEEP_DIAGNOSIS_RULE_IDS:
        return "deep"
    if rule.map_type == "professional":
        return "trace"
    return "standard"


def _chart_keys(chart: HumanDesignChart) -> set[str]:
    keys = {
        "chart",
        "all",
        f"type:{chart.summary.type.code}",
        f"strategy:{chart.summary.strategy.code}",
        f"authority:{chart.summary.authority.code}",
        f"profile:{chart.summary.profile.code}",
        f"definition:{chart.summary.definition.code}",
    }
    if "Consciousness" in chart.summary.incarnation_cross.label or "意识" in chart.summary.incarnation_cross.label:
        keys.add("cross:Right Angle Cross of Consciousness")
    for center in chart.centers:
        state = "defined" if center.defined else "open"
        keys.add(f"center:{center.code}:{state}")
    for channel in chart.channels:
        keys.add(f"channel:{channel.code}")
    for gate in chart.activated_gates:
        keys.add(f"gate:{gate.gate}")
    return keys


def _rule_matches(rule: InterpretationRule, chart_keys: set[str]) -> bool:
    if "all" in rule.applies_to:
        return True
    return all(key in chart_keys for key in rule.applies_to)


def _professional_facts(chart: HumanDesignChart) -> tuple[str, ...]:
    summary = _summary(chart)
    defined_centers = _center_labels(chart, defined=True)
    open_centers = _center_labels(chart, defined=False)
    channels = [f"{channel.code}「{display_channel_label(channel.code, channel.label)}」" for channel in chart.channels]
    gates = [f"{gate.gate}号「{display_gate_theme(gate.gate, gate.theme)}」" for gate in chart.activated_gates]
    return (
        f"类型：{summary['type']}",
        f"策略：{summary['strategy']}",
        f"权威：{summary['authority']}",
        f"人生角色：{summary['profile']}",
        f"定义：{summary['definition']}",
        f"签名/非自己主题：{summary['signature']} / {summary['not_self_theme']}",
        f"使命名称：{summary['incarnation_cross']}",
        "已定义中心：" + ("、".join(defined_centers) if defined_centers else "无"),
        "开放中心：" + ("、".join(open_centers) if open_centers else "无"),
        "已定义通道：" + ("、".join(channels) if channels else "无"),
        "已激活闸门：" + "、".join(gates),
    )


def _summary(chart: HumanDesignChart) -> dict[str, str]:
    return {
        "type": display_type(chart.summary.type.code, chart.summary.type.label),
        "strategy": display_strategy(chart.summary.strategy.code, chart.summary.strategy.label),
        "authority": display_authority(chart.summary.authority.code, chart.summary.authority.label),
        "profile": display_profile(chart.summary.profile.code, chart.summary.profile.label),
        "definition": display_definition(chart.summary.definition.code, chart.summary.definition.label),
        "signature": display_signature(chart.summary.signature.code, chart.summary.signature.label),
        "not_self_theme": display_not_self(chart.summary.not_self_theme.code, chart.summary.not_self_theme.label),
        "incarnation_cross": display_incarnation_cross(chart.summary.incarnation_cross.code, chart.summary.incarnation_cross.label),
    }


def _center_labels(chart: HumanDesignChart, *, defined: bool) -> list[str]:
    return [
        normalize_center_title(CENTER_LABELS.get(center.code, center.label))
        for center in chart.centers
        if center.defined is defined
    ]


def _open_center_pressure_detail(chart: HumanDesignChart) -> tuple[str, ...]:
    labels = {
        "head": "头顶中心开放：容易焦虑“我是不是还没想明白”，不断替外界问题找答案。",
        "ajna": "阿姬娜中心开放：容易焦虑“我必须确定、必须有观点”，于是过早下结论。",
        "throat": "喉咙中心开放：容易焦虑“我不说点什么就没人看见”，表达会变急。",
        "g": "G中心开放：容易焦虑“我到底是谁、方向在哪”，被环境和关系牵着换身份。",
        "heart": "意志力中心开放：容易焦虑“我不够值钱”，用承诺、低价、多做来证明价值。",
        "solar-plexus": "情绪中心开放：容易焦虑“别人生气是不是我的错”，在强情绪里急着安抚。",
        "spleen": "脾中心开放：容易抓住熟悉但消耗的关系或工作，因为离开会不安全。",
        "sacral": "荐骨中心开放：容易不知道什么时候停，把别人的持续力误当成自己的电量。",
        "root": "根部中心开放：容易焦虑“必须马上完成”，把他人的紧迫感接成自己的任务。",
    }
    details = [
        labels[center.code]
        for center in chart.centers
        if not center.defined and center.code in labels
    ]
    return tuple(details[:4] or ("开放中心会放大外界信号，所以先退回身体，再判断这是不是自己的事。",))


def _basis_for_rule(
    rule: InterpretationRule,
    chart: HumanDesignChart,
    atoms: tuple[KnowledgeAtom, ...],
) -> tuple[str, ...]:
    basis: list[str] = []
    summary = _summary(chart)
    for key in rule.applies_to:
        if key.startswith("type:"):
            basis.append(f"类型：{summary['type']}")
        elif key.startswith("authority:"):
            basis.append(f"权威：{summary['authority']}")
        elif key.startswith("profile:"):
            basis.append(f"人生角色：{summary['profile']}")
        elif key.startswith("definition:"):
            basis.append(f"定义：{summary['definition']}")
        elif key.startswith("center:"):
            _, code, state = key.split(":")
            label = normalize_center_title(CENTER_LABELS.get(code, code))
            basis.append(f"{label}：{'已定义' if state == 'defined' else '开放'}")
        elif key.startswith("channel:"):
            code = key.split(":", 1)[1]
            channel = next((item for item in chart.channels if item.code == code), None)
            basis.append(f"通道：{code}" + (f"「{display_channel_label(channel.code, channel.label)}」" if channel else ""))
        elif key.startswith("gate:"):
            gate = int(key.split(":", 1)[1])
            gate_state = next((item for item in chart.activated_gates if item.gate == gate), None)
            basis.append(f"闸门：{gate}" + (f"「{display_gate_theme(gate, gate_state.theme)}」" if gate_state else ""))
        elif key.startswith("cross:"):
            basis.append(f"使命名称：{summary['incarnation_cross']}")
    for atom in atoms:
        if atom.topic not in "；".join(basis):
            basis.append(f"解读主题：{atom.topic}")
    return tuple(_unique(basis))


def _subtitle_for_rule(rule: InterpretationRule, chart: HumanDesignChart) -> str:
    summary = _summary(chart)
    if rule.map_type == "body":
        return f"{summary['authority']}不是想法结论，而是身体反应。"
    if rule.map_type == "wealth":
        return "先看资源投向和承诺边界，再看赚钱形式。"
    if rule.map_type == "talent":
        return f"{summary['profile']}要和通道、闸门一起看。"
    if rule.map_type == "relationship":
        return "关系是否对位，要看身体、边界和方向是否同时稳定。"
    if rule.map_type == "mission":
        return "使命不是一句标签，而是长期回应出来的主线。"
    return "专业依据必须能回到图表事实。"


def _expanded_user_language(
    rule: InterpretationRule,
    chart: HumanDesignChart,
    atoms: tuple[KnowledgeAtom, ...],
    depth: str,
) -> str:
    atom_text = _shorten_text(" ".join(atom.user_translation for atom in atoms[:3]), 150)
    specific = _specific_expansion(rule, chart)
    lens = _full_chart_lens(rule, chart)
    text = f"{rule.user_language_template} {specific} {lens}"
    if depth != "brief" and atom_text:
        text += f" {atom_text}"
    return text.strip()


def _full_chart_lens(rule: InterpretationRule, chart: HumanDesignChart) -> str:
    summary = _summary(chart)
    channels = "、".join(
        f"{channel.code}「{display_channel_label(channel.code, channel.label)}」"
        for channel in chart.channels[:3]
    )
    open_centers = "、".join(_center_labels(chart, defined=False)[:3])
    if rule.rule_id == "body.sacral-response-training":
        return "判断标准很简单：身体先亮起来，再谈计划；身体先沉下去，再合理的机会也先别急着答应。"
    if rule.rule_id == "body.open-pressure-chain":
        return f"你要先查最容易被带跑的入口：{open_centers or '开放中心'}。焦虑不是结论，它只是提醒你先把别人的压力放回别人那里。"
    if rule.rule_id == "wealth.02-14-main-track":
        return f"财富判断不看热闹，看三件事：身体有没有回应，资源会不会集中，最后能不能沉淀成作品、方法、客户信任或资产。"
    if rule.rule_id == "wealth.promise-boundary":
        return "钱留不住时，先别问自己够不够努力，先查你有没有在被夸、被催、被需要的时候答应过头。"
    if rule.rule_id == "talent.profile-24":
        return f"因为你同时有{summary['authority']}和{channels or '当前通道'}，天赋不能只停在别人夸你，它要被练成稳定交付。"
    if rule.rule_id == "talent.consciousness-cross":
        return "你的问题意识要有出口：提出一个好问题，拆掉一个假答案，做一个小实验，比在脑子里绕一百遍更有用。"
    if rule.rule_id == "relationship.emotional-boundary":
        return "关系里最关键的不是马上讲清楚，而是先让身体从对方情绪里退出来；退出来之后还想靠近，才值得继续谈。"
    if rule.rule_id == "relationship.network-fit":
        return "对的人不会一直消耗你的独处，也不会让你为了关系丢掉方向；他会让你更稳定地成为自己。"
    if rule.rule_id == "mission.generator-cross":
        return "使命不是一句宏大口号，而是你反复回应后仍愿意做深的那条线；越做越有力，才说明方向对。"
    return "这条解读只在能回到你的类型、权威、中心、通道和现实选择时才有意义。"


def _specific_expansion(rule: InterpretationRule, chart: HumanDesignChart) -> str:
    summary = _summary(chart)
    channels = ", ".join(channel.code for channel in chart.channels) or "没有已定义通道"
    defined_centers = "、".join(_center_labels(chart, defined=True))
    open_centers = "、".join(_center_labels(chart, defined=False))
    if rule.rule_id == "wealth.02-14-main-track":
        return (
            "你这张图只有少数稳定主轴时，02-14 会变得尤其关键。它把方向和资源连起来，"
            "所以财富不是靠不断换赛道，而是靠选定真正有回应的方向后持续加码。"
        )
    if rule.rule_id == "talent.profile-24":
        return (
            "2爻要找到自己某个已经能做到80分的天赋，但它常常会被你忽视，因为你觉得这件事太容易、太自然，"
            "甚至身边人越说你这里有天赋，你越会轻轻带过。4爻又会让机会从信任关系里来，所以你不是靠陌生人硬推自己，"
            "而是先在独处里把80分能力练到100分，再让熟人、作品、案例和口碑把你带到合适场域。"
        )
    if rule.rule_id == "talent.consciousness-cross":
        return (
            f"你的轮回交叉是{summary['incarnation_cross']}，它不适合被解释成命定剧本，"
            "更适合被看作你反复遇到的问题类型：怀疑、混乱、节律、经验和清晰。"
        )
    if rule.rule_id == "body.open-pressure-chain":
        pressure_detail = "；".join(_open_center_pressure_detail(chart))
        return (
            f"你的已定义中心是{defined_centers}；开放中心是{open_centers}。开放中心不是缺陷，而是会放大场域。"
            f"具体到生活里，最容易出现的是：{pressure_detail}"
        )
    if rule.rule_id == "mission.generator-cross":
        return f"你的主通道是{channels}，它要求你把生命力投到有方向感的事情里，而不是靠证明自己进入使命。"
    return "这个条目要和你的真实图表一起看，而不是单独拿出来当标签。"


def _shorten_text(text: str, limit: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[:limit].rstrip("，。；、 ") + "。"


def _life_scenes(rule: InterpretationRule, chart: HumanDesignChart) -> tuple[str, ...]:
    return {
        "body.sacral-response-training": (
            "别人问你一个具体机会时，身体先有反应，头脑后来才解释。",
            "你嘴上说可以，但身体沉下去、拖延、没有劲，这通常不是懒。",
            "当你回应正确，一件事会越做越进入状态，而不是越做越想逃。",
        ),
        "body.open-pressure-chain": (
            *_open_center_pressure_detail(chart),
            "别人一急，你也跟着急，最后替别人的压力加班、解释或兜底。",
        ),
        "wealth.02-14-main-track": (
            "你把一个方法反复打磨后，它开始带来客户、作品和资产。",
            "你一分散去做很多不相关项目，钱看似进来，身体却越来越空。",
            "当方向对时，你会愿意为它长期配置时间、资源和学习。",
        ),
        "wealth.promise-boundary": (
            "客户一催你就降价或多送服务。",
            "合作方夸你靠谱，你立刻答应超出范围的事情。",
            "一个项目的钱不差，但它持续占用你的身体和主航道。",
        ),
        "talent.profile-24": (
            "你一个人做东西时，某些能力已经能做到80分，但你会觉得这只是普通操作，不把它当成天赋。",
            "身边人越说你这里很有天赋、应该再精进，你反而越容易忽视，转头去学别人擅长的东西。",
            "真正合适的机会常来自熟人、朋友、长期关系，而不是陌生平台硬抢；关系看见你，是为了把已经熟成的能力叫出来。",
        ),
        "talent.consciousness-cross": (
            "你对一个答案不满意，会继续追问它是否真的成立。",
            "你能把别人觉得混乱的问题整理出几个关键判断点。",
            "你经历过的变化会慢慢变成你讲给别人的方法。",
        ),
        "relationship.emotional-boundary": (
            "对方情绪一强，你立刻想解释、安抚或妥协。",
            "冲突后离开现场，你才发现刚才很多感受不是自己的。",
            "真正对的关系会让你的身体慢慢安静，而不是一直紧绷。",
        ),
        "relationship.network-fit": (
            "对方既尊重你的独处，也知道什么时候邀请你出来。",
            "关系让你更稳定地走自己的方向，而不是越来越怀疑自己。",
            "朋友和合作伙伴通过信任把你带到合适场域。",
        ),
        "mission.generator-cross": (
            "机会来了以后，身体先回应，再慢慢长出长期方向。",
            "挫败感出现时，它常提醒你正在做不属于主线的事。",
            "你把一个反复怀疑的问题做成方法，别人因此少走弯路。",
        ),
    }.get(rule.rule_id, ("在现实选择、合作、表达和长期投入里观察这个主题。",))


def _embodied_expression(rule: InterpretationRule, chart: HumanDesignChart) -> tuple[str, ...]:
    if rule.map_type == "professional":
        return ()
    return {
        "body.sacral-response-training": (
            "真正活出来时，你不会靠头脑硬判断每个机会，而是让具体问题落到身体反应上：有回应就有持续力，没回应就不再逼自己。",
            "别人会感到你做对的事时很稳，不是靠兴奋冲刺，而是越做越进入状态。",
            "你的身体会成为筛选器：该投入的事情让你更有生命力，不该接的事情会很快显出沉、拖、空。",
        ),
        "body.open-pressure-chain": (
            "真正活出来时，你能分清外界压力和自己的回应，不再替每个人的焦虑找答案。",
            "你会允许自己先退开、先观察，再决定是否表达或行动。",
            "你的清晰感来自身体回到自己，而不是把所有问题都立刻想明白。",
        ),
        "wealth.02-14-main-track": (
            "真正活出来时，你像一个能把方向感变成资源配置的人：知道钱、时间、人脉和注意力该投向哪里。",
            "你不是靠到处接活赚钱，而是围绕有回应的主航道持续打磨资产、产品、方法或服务。",
            "别人会在你身上看到一种稳定的推进力：不是乱冲，而是能把资源推到对的位置。",
        ),
        "wealth.promise-boundary": (
            "真正活出来时，你会先确认身体是否有回应，再决定价格、范围、周期和承诺。",
            "你能把边界说清楚，不再用多做、低价、硬扛来证明自己值钱。",
            "你的财富会更像可持续交换，而不是靠消耗生命力换短期现金流。",
        ),
        "talent.profile-24": (
            "真正活出来时，你会允许天赋先在独处中熟成，再通过信任关系被看见。",
            "你会把自己已经能做到80分、但曾经觉得太容易的能力，通过练习、作品、案例和复盘推到100分。",
            "你不会急着把半熟的能力推到所有人面前，而是让小范围验证慢慢形成口碑；别人觉得你像天然会的，你知道那是安静空间和正确召唤共同养出来的。",
        ),
        "talent.consciousness-cross": (
            "真正活出来时，你能把怀疑、混乱和经验整理成判断力，让别人少走弯路。",
            "你不是为了否定而怀疑，而是能追问一个结论是否真的成立，并把问题拆到更清楚。",
            "你的经历会沉淀成方法：你走过的变化越多，越能帮助别人理解复杂局面。",
        ),
        "relationship.emotional-boundary": (
            "真正活出来时，你不会把对方强烈情绪立刻当成自己的答案，而是能先退回身体再回应。",
            "你在关系里会更稳定：既能感受别人，也不让别人的情绪替你做决定。",
            "对的人会尊重你的等待和分辨，而不是逼你在情绪场里立刻表态。",
        ),
        "relationship.network-fit": (
            "真正活出来时，你的关系会成为正确召唤，而不是持续打扰。",
            "你能在独处和关系之间形成节奏：先养熟自己，再让信任网络把你带到合适场域。",
            "适合你的人会看见你的方向感，也尊重你不随时在线、不随叫随到。",
        ),
        "mission.generator-cross": (
            "真正活出来时，你的人生主线不是靠宣言喊出来，而是靠一次次正确回应累积出来。",
            "你会把生命力投到能持续做深的方向，慢慢形成别人能识别的能力、作品或体系。",
            "使命感会从满足感里长出来：越做越有力，而不是越证明越空。",
        ),
    }.get(rule.rule_id, ("这个特质活出来时，不是停留在术语里，而是能在真实选择、合作节奏和身体状态里被看见。",))


def _blind_spots(rule: InterpretationRule, chart: HumanDesignChart) -> tuple[str, ...]:
    if rule.map_type == "professional":
        return ("只看结论、不查图表依据时，很容易把一段听起来舒服的话误当成自己的真实结构。",)
    return {
        "body.sacral-response-training": (
            "你最大的盲区是把头脑里的合理、应该、看起来有机会，误判成身体真的想做。",
            "别人越期待你，你越容易把对方的期待当成自己的回应。",
        ),
        "body.open-pressure-chain": (
            "你容易把外界的压力、问题和紧迫感吸进来，以为那都是你必须立刻解决的事。",
            "你会为了显得确定、显得有表达、显得跟得上，而过早给出不是自己的答案。",
        ),
        "wealth.02-14-main-track": (
            "你的盲区是以为机会越多越安全，结果资源被分散到太多不成系统的事情上。",
            "你容易把短期现金流误当成长期财富，忽略它有没有沉淀成资产。",
        ),
        "wealth.promise-boundary": (
            "你的盲区是用承诺换安全感，用低价、多做、硬扛来证明自己值得被选择。",
            "当别人认可你、需要你、催你时，你可能还没等身体回应就先答应了。",
        ),
        "talent.profile-24": (
            "你的盲区是低估天然能力，以为不费力、容易上手、别人一夸就能做好的东西不值钱。",
            "别人越说你这里有天赋，你越可能轻轻带过，反而去学习很多别人擅长、但不一定属于你的能力。",
            "你也容易在两个极端之间摇摆：要么躲太久不出来，要么被关系一叫就把半熟能力过早拿出去消耗。",
        ),
        "talent.consciousness-cross": (
            "你的盲区是把怀疑留在脑子里打转，没有把它变成可验证的问题和方法。",
            "混乱出现时，你可能急着定论，反而跳过了真正整理经验的过程。",
        ),
        "relationship.emotional-boundary": (
            "你的盲区是以为关系里的强情绪就代表真实答案，尤其容易把对方的急迫当成自己的责任。",
            "你可能为了避免冲突而答应，事后身体才开始抗拒。",
        ),
        "relationship.network-fit": (
            "你的盲区是把频繁打扰、持续索取误认为亲密或重视。",
            "你可能为了维持关系而牺牲独处节奏和方向感。",
        ),
        "mission.generator-cross": (
            "你的盲区是想先证明自己有使命，再允许自己行动；这会让使命变成压力。",
            "你容易把没有回应的规划包装成人生方向，越执行越挫败。",
        ),
    }.get(rule.rule_id, ("盲区是只理解术语，却没有观察它在自己现实选择里的具体表现。",))


def _stuck_patterns(rule: InterpretationRule, chart: HumanDesignChart) -> tuple[str, ...]:
    if rule.map_type == "professional":
        return ("读完很多术语但不知道怎么用，或者把不存在的中心、通道、闸门也当成自己的特质。",)
    return {
        "body.sacral-response-training": (
            "卡住时会表现为答应了但拖延、身体沉、越做越没劲，最后用自责解释自己不够努力。",
            "你会反复问别人该不该做，却没有把问题拆成身体能回应的具体选项。",
        ),
        "body.open-pressure-chain": (
            "卡住时会像被很多问题同时追着跑，脑子停不下来，表达也变急。",
            "你可能忙着处理别人的压力，自己的身体却越来越空。",
        ),
        "wealth.02-14-main-track": (
            "卡住时会不断接项目、换方向、追机会，钱可能进来，但主航道越来越模糊。",
            "你会觉得自己很忙，却没有形成可复用资产。",
        ),
        "wealth.promise-boundary": (
            "卡住时会低价多接、范围失控、答应太多，最后对客户、合作和钱都产生怨气。",
            "你会把原本该谈清楚的边界，拖到身体被耗尽后才爆发。",
        ),
        "talent.profile-24": (
            "卡住时会一直学别人擅长的东西，却迟迟不把自己已经有80分基础的能力做成作品、方法、案例或真实服务。",
            "你会在独处里怀疑自己，出来后又被关系消耗，形成躲起来和过度回应的循环。",
            "你可能被夸很多次，却没有建立训练路径，所以天赋停留在“别人觉得你会”，没有变成你自己能稳定交付的能力。",
        ),
        "talent.consciousness-cross": (
            "卡住时会不断怀疑、不断收集信息，但迟迟不形成判断。",
            "你也可能经历很多，却没有复盘成结构，导致经验无法变成能力。",
        ),
        "relationship.emotional-boundary": (
            "卡住时会在关系里过度解释、安抚、妥协，离开现场后才发现自己并不想答应。",
            "你会被对方情绪牵着走，身体越来越紧，关系越来越累。",
        ),
        "relationship.network-fit": (
            "卡住时会进入被关系拉扯的状态：不见人会内疚，见了又被消耗。",
            "你会让不适合的人占用你的节奏，导致方向感下降。",
        ),
        "mission.generator-cross": (
            "卡住时会把人生规划写得很完整，但身体没有回应，执行起来只有挫败。",
            "你会把挫败感压下去继续硬做，直到对整条路都失去兴趣。",
        ),
    }.get(rule.rule_id, ("卡住时会变成知道很多名词，但无法判断下一步该怎么观察和行动。",))


def _stuck_causes(rule: InterpretationRule, chart: HumanDesignChart) -> tuple[str, ...]:
    if rule.map_type == "professional":
        return ()
    summary = _summary(chart)
    channels = "、".join(channel.code for channel in chart.channels) or "没有已定义通道"
    open_centers = "、".join(_center_labels(chart, defined=False)) or "开放中心较少"
    return {
        "body.sacral-response-training": (
            f"盘面机制：你的决策核心是{summary['authority']}，它需要具体选项和身体回应；现实场景：当机会只停留在头脑想象或别人期待里，你就会用理性替身体做决定。",
            f"盘面机制：{summary['type']}的生命力适合回应后持续投入；现实场景：你若先承诺再找感觉，身体会用拖延和没劲来提醒你不对。",
        ),
        "body.open-pressure-chain": (
            f"盘面机制：开放中心包括{open_centers}，容易放大外界压力；现实场景：信息、人群和他人焦虑一多，你会误以为所有问题都必须现在解决。",
            "盘面机制：开放中心不是缺陷，而是放大器；现实场景：你没有先退回身体，就会把别人的节奏当成自己的节奏。",
        ),
        "wealth.02-14-main-track": (
            "盘面机制：02-14 把 G中心方向感和荐骨资源连起来；现实场景：如果项目不在主航道上，再赚钱也会分散你的资源配置能力。",
            f"盘面机制：{summary['authority']}需要先确认身体回应；现实场景：看到现金流就接，会让钱变成忙乱，而不是资产。",
        ),
        "wealth.promise-boundary": (
            f"盘面机制：开放意志力中心容易用承诺证明价值，{summary['authority']}又需要等身体回应；现实场景：客户一催、关系一热，你就可能先答应再透支。",
            "盘面机制：承诺边界不是道德问题，而是能量配置问题；现实场景：范围、价格、退出机制没谈清楚，财富会变成消耗。",
        ),
        "talent.profile-24": (
            f"盘面机制：{summary['profile']}需要独处熟成和关系召唤同时存在；现实场景：只独处会看不见市场，只回应关系会过早把半熟能力拿出去消耗。",
            "盘面机制：2线的天然感容易让你低估自己，4线又通过关系展开；现实场景：你需要把80分天然能力用训练、作品和案例推到100分，否则天赋会停在别人一句夸奖里。",
            "盘面机制：你的能力要被正确场域召唤才稳定；现实场景：如果你总在模仿别人擅长的路，就会错过自己已经显露出来的那条线。",
        ),
        "talent.consciousness-cross": (
            f"盘面机制：你的轮回交叉主题会把怀疑、混乱、节律和经验推到前台；现实场景：如果没有复盘和验证，怀疑只会变成内耗。",
            f"盘面机制：图里通道包括{channels}，需要把能量落到可持续结构；现实场景：只思考不整理，判断力就无法变成别人能使用的方法。",
        ),
        "relationship.emotional-boundary": (
            "盘面机制：你不是情绪权威时，强情绪场不适合作最终决定；现实场景：对方一激动你就解释或答应，会把关系压力误认为自己的选择。",
            f"盘面机制：{summary['authority']}需要身体回应；现实场景：冲突现场太吵时，身体信号会被对方情绪盖住。",
        ),
        "relationship.network-fit": (
            f"盘面机制：{summary['profile']}通过关系被看见，但也需要独处恢复；现实场景：不尊重你独处节奏的人，会把关系入口变成消耗入口。",
            "盘面机制：G中心方向感需要稳定环境支持；现实场景：关系如果不断打断你的方向，你会越来越不像自己。",
        ),
        "mission.generator-cross": (
            f"盘面机制：{summary['type']}的主线来自回应后持续做深，不来自头脑先定义使命；现实场景：你越急着证明人生方向，越容易选到没有身体回应的路。",
            f"盘面机制：你的已定义通道是{channels}，使命要落在可持续能量流里；现实场景：只靠计划和口号推进，会很快撞上挫败感。",
        ),
    }.get(rule.rule_id, ("盘面机制：这个条目必须回到真实图表事实；现实场景：如果只背术语，就无法知道它在生活中如何发生。",))


def _common_blocks(rule: InterpretationRule, chart: HumanDesignChart) -> tuple[str, ...]:
    return {
        "body.sacral-response-training": ("用头脑替身体决定。", "把别人期待当成自己的回应。", "没有具体选项时逼自己给答案。"),
        "body.open-pressure-chain": ("替别人回答问题。", "为了显得确定而过早下结论。", "为了被看见而急着表达。"),
        "wealth.02-14-main-track": ("到处接活导致资源分散。", "把短期现金流误当长期财富。", "没有主航道就扩大投入。"),
        "wealth.promise-boundary": ("用低价证明价值。", "答应前不等身体回应。", "把承诺当成关系安全感。"),
        "talent.profile-24": ("独处太久不让作品被看见。", "关系一召唤就过早消耗。", "把天然能力误以为不值钱。"),
        "talent.consciousness-cross": ("怀疑没有出口。", "混乱时强行定论。", "经历很多但不复盘。"),
        "relationship.emotional-boundary": ("把对方情绪当自己的答案。", "为了避免冲突而答应。", "在情绪场里做决定。"),
        "relationship.network-fit": ("为了关系牺牲方向感。", "把持续打扰误认为亲密。", "被不尊重独处的人消耗。"),
        "mission.generator-cross": ("主动证明自己有使命。", "把挫败感压下去继续硬做。", "没有回应就强行规划人生。"),
    }.get(rule.rule_id, ("术语化理解，不回到身体和现实场景。",))


def _extra_practices(rule: InterpretationRule, chart: HumanDesignChart) -> tuple[str, ...]:
    if rule.map_type == "wealth":
        return ("给每个项目标注：有回应、能沉淀资产、是否过度承诺。", "报价前先确认范围、退出机制和身体反应。")
    if rule.map_type == "talent":
        return (
            "列出三件别人常夸、你却觉得太容易的事，选一件当作80分天赋来训练。",
            "把一个天然能力写成作品、方法或案例，而不是只在脑子里认可。",
            "每周复盘一次：这个能力在哪里被正确召唤，在哪里被误用。",
        )
    if rule.map_type == "relationship":
        return ("关系冲突时先离开强情绪场，再听身体是否还想靠近。", "把独处需求提前说清楚，不等到被耗尽才爆发。")
    if rule.map_type == "mission":
        return ("用 30/60/90 天观察主线，不用一天给自己定终身使命。",)
    if rule.map_type == "body":
        return ("用睡眠、拖延、身体紧绷和满足感记录回应是否正确。",)
    return ()


def _item_followups(rule: InterpretationRule) -> tuple[str, ...]:
    return {
        "body.sacral-response-training": ("我怎么区分真实荐骨回应和头脑兴奋？", "我可以用哪些日常练习训练身体回答？"),
        "body.open-pressure-chain": ("我的开放中心里哪个最容易带来内耗？", "我怎么判断压力是不是别人的？"),
        "wealth.02-14-main-track": ("我的财富主航道具体适合怎么设计？", "哪些项目应该砍掉？"),
        "wealth.promise-boundary": ("我的定价边界应该怎么设？", "什么客户最容易让我过度承诺？"),
        "talent.profile-24": ("我的 2/4 天赋怎样被正确看见？", "我应该怎么经营熟人信任网络？"),
        "talent.consciousness-cross": ("63/64 的怀疑怎样变成判断力？", "5/35 对我的经验和节律有什么要求？"),
        "relationship.emotional-boundary": ("我在关系里怎么不被情绪带跑？", "我适合怎样处理冲突？"),
        "relationship.network-fit": ("什么样的人最适合我？", "哪些关系会消耗我的方向感？"),
        "mission.generator-cross": ("我怎么判断自己正在主线里？", "挫败感具体在提醒我什么？"),
    }.get(rule.rule_id, ("这条解读的图表依据是什么？", "我可以怎么在生活里观察它？"))


def _source_cards_for_atoms(
    atoms: tuple[KnowledgeAtom, ...],
    source_lookup: dict[str, SourceCard],
) -> tuple[SourceCard, ...]:
    return tuple(source_lookup[source_id] for source_id in _unique(
        source_id for atom in atoms for source_id in atom.source_ids if source_id in source_lookup
    ))


def _source_references_for_atoms(
    atoms: tuple[KnowledgeAtom, ...],
    source_lookup: dict[str, SourceCard],
) -> tuple[SourceReference, ...]:
    refs = []
    for source in _source_cards_for_atoms(atoms, source_lookup):
        refs.append(
            SourceReference(
                kind="research",
                code=source.source_id,
                title=source.title,
                path=source.url or f"references/research-corpus/v0.3/sources.json#{source.source_id}",
            )
        )
    return tuple(refs)


def _unique(values) -> tuple:
    seen = set()
    result = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return tuple(result)
