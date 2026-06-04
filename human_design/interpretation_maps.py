from __future__ import annotations

from datetime import UTC, datetime

from .labels import (
    CENTER_LABELS,
    display_authority,
    display_definition,
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
    "body": ("身体怎么运作", "先看身体资源和压力链，不急着把专业术语当结论。"),
    "wealth": ("财富从哪里来", "先看资源、承诺和主航道，再谈行业、职位或商业模式。"),
    "talent": ("天赋怎么形成", "先看爻位、通道和关键闸门如何叠加，而不是给单一标签。"),
    "relationship": ("关系怎么对位", "先看你怎样连接、怎样被影响，以及什么关系让你更像自己。"),
    "mission": ("人生主线怎么走", "先看你如何进入正确事情，再看长期使命如何被做深。"),
    "professional": ("图表事实", "这里用于核验每段解读到底来自哪个图表结构。"),
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
        lines.append("")
    for section in package.sections:
        lines.append(f"## {section.title}")
        for item in section.items:
            lines.append(f"### {item.title}")
            lines.append("依据：" + "；".join(item.chart_basis))
            lines.append(item.user_language)
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
        chart_basis=chart_basis,
        professional_basis=rule.professional_basis,
        user_language=_expanded_user_language(rule, chart, atoms, depth),
        life_scenes=_life_scenes(rule, chart),
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
        "这张图的专业信息不是给你背术语用的，而是用来校验解读是否真实。"
        f"你的类型是{summary['type']}，策略是{summary['strategy']}，权威是{summary['authority']}，"
        f"人生角色是{summary['profile']}。任何关于工作、财富、关系或使命的判断，都必须能回到这些事实，"
        "再进一步落到已定义中心、开放中心、通道、闸门和行星激活。"
    )
    return InterpretationMapItem(
        key="professional.chart-facts",
        title="这张图的事实清单",
        subtitle="用来防止泛泛解读和编造图表事实",
        chart_basis=chart_basis,
        professional_basis="人类图解读必须先有图表事实，再从事实进入解释。",
        user_language=user_language,
        life_scenes=("当你读到一段解读时，可以回到这里检查依据。", "当聊天回答变得泛时，可以要求系统指出对应中心、通道或闸门。"),
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
    channels = [f"{channel.code}「{channel.label}」" for channel in chart.channels]
    gates = [str(gate.gate) for gate in chart.activated_gates]
    return (
        f"类型：{summary['type']}",
        f"策略：{summary['strategy']}",
        f"权威：{summary['authority']}",
        f"人生角色：{summary['profile']}",
        f"定义：{summary['definition']}",
        f"签名/非自己主题：{summary['signature']} / {summary['not_self_theme']}",
        f"轮回交叉：{summary['incarnation_cross']}",
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
        "incarnation_cross": chart.summary.incarnation_cross.label,
    }


def _center_labels(chart: HumanDesignChart, *, defined: bool) -> list[str]:
    return [
        normalize_center_title(CENTER_LABELS.get(center.code, center.label))
        for center in chart.centers
        if center.defined is defined
    ]


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
            basis.append(f"通道：{code}" + (f"「{channel.label}」" if channel else ""))
        elif key.startswith("gate:"):
            gate = int(key.split(":", 1)[1])
            gate_state = next((item for item in chart.activated_gates if item.gate == gate), None)
            basis.append(f"闸门：{gate}" + (f"「{gate_state.theme}」" if gate_state else ""))
        elif key.startswith("cross:"):
            basis.append(f"轮回交叉：{summary['incarnation_cross']}")
    for atom in atoms:
        if atom.topic not in "；".join(basis):
            basis.append(f"资料主题：{atom.topic}")
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
    summary = _summary(chart)
    atom_text = " ".join(atom.user_translation for atom in atoms[:4])
    specific = _specific_expansion(rule, chart)
    text = (
        f"{rule.user_language_template} {specific} "
        f"放回你的盘面看，这不是泛泛的性格描述：你的{summary['type']}、{summary['authority']}、"
        f"{summary['profile']}和实际激活结构共同指向这个主题。"
    )
    if depth != "brief" and atom_text:
        text += f" 资料库把这个主题翻译成一句更接近日常的话：{atom_text}"
    return text.strip()


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
            "2/4 的误区是要么躲太久，要么为了关系过早出来。你的更优节奏是先把能力养到能被信任的人识别，"
            "再让关系网络成为入口。"
        )
    if rule.rule_id == "talent.consciousness-cross":
        return (
            f"你的轮回交叉是{summary['incarnation_cross']}，它不适合被解释成命定剧本，"
            "更适合被看作你反复遇到的问题类型：怀疑、混乱、节律、经验和清晰。"
        )
    if rule.rule_id == "body.open-pressure-chain":
        return f"你的已定义中心是{defined_centers}；开放中心是{open_centers}。开放中心越多，越要先分清外界压力和自己的真实回应。"
    if rule.rule_id == "mission.generator-cross":
        return f"你的主通道是{channels}，它要求你把生命力投到有方向感的事情里，而不是靠证明自己进入使命。"
    return "这个条目要和你的真实图表一起看，而不是单独拿出来当标签。"


def _life_scenes(rule: InterpretationRule, chart: HumanDesignChart) -> tuple[str, ...]:
    return {
        "body.sacral-response-training": (
            "别人问你一个具体机会时，身体先有反应，头脑后来才解释。",
            "你嘴上说可以，但身体沉下去、拖延、没有劲，这通常不是懒。",
            "当你回应正确，一件事会越做越进入状态，而不是越做越想逃。",
        ),
        "body.open-pressure-chain": (
            "早上刷到很多信息后，突然觉得自己必须马上换方向。",
            "会议里没有人要求你发言，但你感觉必须说点什么证明自己。",
            "别人急，你也跟着急，最后替别人的压力加班。",
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
            "你一个人做东西时能力很自然，但被突然推到台前会失真。",
            "机会常来自熟人、朋友、长期关系，而不是陌生平台硬抢。",
            "当关系真正信任你，你的天然能力更容易被叫出来。",
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
        return ("把一个天然能力写成作品、方法或案例，而不是只在脑子里认可。", "每周复盘一次：这个能力在哪里被正确召唤，在哪里被误用。")
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
