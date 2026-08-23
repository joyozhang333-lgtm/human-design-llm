from __future__ import annotations

from collections.abc import Iterable

from .body_energy import CENTER_ENERGY_GUIDES
from .generation.fallback import CHANNEL_LINES
from .knowledge import AUTHORITY_GUIDES, DEFINITION_GUIDES, PROFILE_GUIDES
from .labels import (
    CENTER_LABELS,
    display_authority,
    display_authority_professional,
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
from .schema import HumanDesignChart, InterpretationMapItem, InterpretationMapSection


LINE_TALENTS = {
    1: "先研究到底、建立可靠地基，再愿意把判断交给现实验证",
    2: "先在独处里发现天然会的能力，再等真正看见你的人把它叫出来",
    3: "通过亲自试错分辨什么可行，最后把踩过的坑变成别人能用的经验",
    4: "通过长期信任关系获得机会，也通过关系网络放大影响力",
    5: "把复杂问题变成可落地方案，同时管理别人对你过高的期待",
    6: "用时间把经历沉淀成示范，不靠说服，而靠自己怎样活",
}

AUTHORITY_PRACTICES = {
    "sacral": "把问题改成可以回答“想不想、要不要”的小问题，记录身体第一秒是有劲还是没劲。",
    "solar-plexus": "重要决定至少隔一晚，情绪高点和低点都不签下最终答案。",
    "emotional": "重要决定至少隔一晚，情绪高点和低点都不签下最终答案。",
    "splenic": "先记下第一秒的放松或收紧，再看后来的分析有没有覆盖它。",
    "ego": "答应之前问：这是我真想要，还是我想证明自己值得？",
    "ego-manifested": "答应之前问：这是我真想要，还是我想证明自己值得？",
    "ego-projected": "把愿望说出来，听自己究竟愿不愿意为它作出承诺。",
    "self-projected": "找一个不替你做决定的人，把选择说出来，听哪句话最像自己。",
    "mental": "换两个环境、找两个可信的人分别谈一次，再比较自己在哪个场域更清楚。",
    "outer-authority": "换两个环境、找两个可信的人分别谈一次，再比较自己在哪个场域更清楚。",
    "lunar": "重大决定跨越完整月亮周期观察，不把某一天的状态当最终结论。",
}


def build_report_sections(map_type: str, chart: HumanDesignChart) -> tuple[InterpretationMapSection, ...]:
    builders = {
        "body": _body_report,
        "wealth": _wealth_report,
        "talent": _talent_report,
        "relationship": _relationship_report,
        "mission": _mission_report,
    }
    builder = builders.get(map_type)
    return builder(chart) if builder else ()


def build_report_overview(map_type: str, chart: HumanDesignChart) -> str:
    summary = _summary(chart)
    channels = _channel_names(chart)
    profile = summary["profile"]
    overview = {
        "body": (
            f"你的身体先用「{summary['strategy']}」进入事情，再用 {summary['authority_professional']} 确认是否继续。"
            "真正要练的不是更会分析，而是在压力出现时仍能认出自己的节奏。"
        ),
        "wealth": (
            "你的财富不由一个行业标签决定，而取决于三件事：机会是不是对的、能力能不能重复交付、承诺有没有吞掉利润。"
            f"你可以长期使用的能力组合来自{'、'.join(channels) or '合适的人与环境'}。"
        ),
        "talent": (
            f"你的天赋不能只看一个标签。{profile}说明能力怎样成熟，"
            f"{'、'.join(channels) or '合适的环境'}说明哪些能力会自然连在一起。重点不是证明你会什么，而是找到那项已经反复有效、值得练成代表作的能力。"
        ),
        "relationship": (
            f"关系合不合适，不看一个抽象的“最配类型”，而看对方是否尊重你的决定节奏和{profile}的连接方式，"
            "以及你能否在靠近一个人时仍然保留自己的感受和边界。"
        ),
        "mission": (
            f"你的人生使命主题叫「{summary['cross']}」。它不是职业答案，而是一个会在不同阶段反复出现的人生问题。"
            "使命是否真实，要看你长期投入后有没有更有生命力、能力有没有积累、别人有没有因此真正受益。"
        ),
    }
    return overview.get(map_type, "")


def _body_report(chart: HumanDesignChart) -> tuple[InterpretationMapSection, ...]:
    summary = _summary(chart)
    authority_code = chart.summary.authority.code
    defined = _centers(chart, True)
    open_centers = _centers(chart, False)
    decision_key = "body.sacral-response-training" if authority_code == "sacral" else "body.decision-signal"
    decision = _item(
        key=decision_key,
        title="身体怎样告诉你“要”还是“不要”",
        subtitle=f"{summary['type']} · {summary['strategy']} · {summary['authority_professional']}",
        basis=_core_basis(chart),
        user=(
            f"你不是先想出一个完美答案再行动。对你更有效的顺序是：现实先出现一个具体的人、事或选项，"
            f"你按「{summary['strategy']}」进入，再让 {summary['authority_professional']} 给出最终确认。"
            f"{_authority_guide(authority_code)}"
        ),
        scenes=("接项目、答应见面、决定继续一段关系、买下重要东西时，都用同一套顺序。",),
        embodied=(f"顺着使用时，行动之后更接近「{summary['signature']}」：身体可能累，但不会越来越拧。",),
        blind=("头脑会把“看起来合理、别人都说好、现在不答应就会错过”误当成身体答案。",),
        stuck=(f"跳过自己的决定方式时，最早出现的信号通常是「{summary['not_self']}」、拖延或越做越没劲。",),
        causes=("盘面机制：机会入口和决定方式是两步；现实场景：对方催你表态时，你容易把赶快回答误当成清晰。",),
        practices=(AUTHORITY_PRACTICES.get(authority_code, "给重要选择留出空间，记录第一反应和事后体感。"),),
        followups=("拿我最近一个真实选择，带我做一次身体判断。",),
    )
    stable = _item(
        key="body.stable-resources",
        title="你身体里相对稳定的资源",
        subtitle="这些中心不需要从别人那里借来",
        basis=tuple(f"{_center_name(center.code)}：已定义" for center in defined),
        user=(
            f"你的{'、'.join(_center_name(center.code) for center in defined) or '中心定义会随环境呈现'}是较稳定的资源。"
            "稳定不等于每时每刻都强，而是状态合适时，你更容易重复调用这些能力。"
        ),
        scenes=tuple(
            f"{_center_name(center.code)}：{CENTER_ENERGY_GUIDES[center.code]['body']}"
            for center in defined
        ) or ("你的稳定感更依赖正确环境，因此选地方和人比逼自己固定更重要。",),
        embodied=("真正用对这些资源时，你不需要向别人证明；它们会自然进入做事、表达和关系。",),
        blind=("稳定资源也会被过度使用：会做不等于每次都该由你做。",),
        stuck=("长期把稳定能力拿去救火，会出现“别人越来越依赖你，你却越来越没有自己的主线”。",),
        practices=("圈出最近一周最耗能的三件事，分辨哪一件只是因为你能做，而不是因为它值得你做。",),
    )
    pressure = _item(
        key="body.open-pressure-chain",
        title="压力最容易从哪里进入",
        subtitle="开放中心不是缺陷，是最容易受环境影响的位置",
        basis=tuple(f"{_center_name(center.code)}：开放" for center in open_centers),
        user=(
            f"你开放的是{'、'.join(_center_name(center.code) for center in open_centers) or '没有明显开放中心'}。"
            "压力通常不是一下子把你压垮，而是先在其中一个位置出现，再带着你加速、证明、安抚或硬撑。"
        ),
        scenes=tuple(
            f"{_center_name(center.code)}：{CENTER_ENERGY_GUIDES[center.code]['open_body']}"
            for center in open_centers
        ) or ("你的中心大多稳定，仍要留意自己是否把稳定误用成必须一直扛。",),
        blind=tuple(CENTER_ENERGY_GUIDES[center.code]["consumption"] for center in open_centers),
        stuck=tuple(
            f"{_center_name(center.code)}被带走时：{CENTER_ENERGY_GUIDES[center.code]['consumption']}"
            for center in open_centers
        ),
        causes=("盘面机制：开放中心会放大现场信号；现实场景：催促、冲突或比较一出现，你会暂时把别人的状态当成自己的任务。",),
        practices=tuple(CENTER_ENERGY_GUIDES[center.code]["practice"] for center in open_centers[:3]),
        followups=("按我最常见的生活场景，判断压力链通常从哪个中心开始。",),
    )
    recovery = _item(
        key="body.recovery-order",
        title="能量乱掉以后，按什么顺序回来",
        subtitle="先退出放大场，再做决定",
        basis=(f"Strategy：{summary['strategy']}", f"Authority：{summary['authority_professional']}", f"开放中心数量：{len(open_centers)}"),
        user="恢复不是再逼自己做一套正确方法，而是先停止继续接收现场压力，让身体重新听得见自己。",
        scenes=("第一步离开高压现场；第二步把问题缩小；第三步按自己的决定方式确认；第四步只处理下一件事。",),
        embodied=("恢复之后，你会重新知道什么值得做、什么可以晚一点、什么根本不是你的责任。",),
        stuck=("如果休息时还在反复想怎样让所有人满意，身体虽然停了，压力链并没有停。",),
        practices=("今天只做一次：感到急时离开现场十分钟，不解决问题，只记录身体哪里紧、哪里松。",),
    )
    return (
        _section("body-decision", "你的决定系统", "先弄清身体怎样参与选择。", decision),
        _section("body-resources", "稳定能量", "哪些力量属于你，怎样避免把强项用成负担。", stable),
        _section("body-pressure", "压力入口", "逐个看开放中心会把什么放大。", pressure),
        _section("body-recovery", "恢复顺序", "能量乱掉以后，不靠硬撑把自己拉回来。", recovery),
    )


def _wealth_report(chart: HumanDesignChart) -> tuple[InterpretationMapSection, ...]:
    summary = _summary(chart)
    channels = tuple(chart.channels)
    route = _item(
        key="wealth.income-route",
        title="钱更可能从哪里来",
        subtitle="机会入口 × 稳定能力 × 可重复交付",
        basis=_core_basis(chart) + tuple(f"通道：{_channel_name(channel)}" for channel in channels),
        user=(
            f"你的财富入口要先服从「{summary['strategy']}」，不是看到市场热点就把全部资源压上去。"
            f"{summary['profile']}决定别人怎样认识和选择你；"
            f"{'已定义通道决定你能反复交付什么。' if channels else '你的能力更容易在对的人和环境中被点亮，合作场域比固定职业标签更重要。'}"
        ),
        scenes=("判断一个收入机会时，同时看三件事：身体是否愿意、能力能否重复、做完能否留下案例或资产。",),
        embodied=("顺的时候，收入增长和能力积累发生在同一条线上；你不是只换到现金，也在变得更不可替代。",),
        blind=("只看单次价格，会忽略项目是否切碎注意力、破坏口碑或占掉真正主线的资源。",),
        stuck=("很忙、项目不少、回款也有，但每个项目都从零开始，半年后仍说不清自己积累了什么。",),
        practices=("把现有收入逐项标记为现金流、案例、方法、关系、可复用资产；只有现金流的一项必须重新评估。",),
    )
    channel_items = (_wealth_channels_item(channels),) if channels else (
        _item(
            key="wealth.environmental-value",
            title="你的价值更依赖场域被接通",
            subtitle="没有固定通道不等于没有天赋",
            basis=("已定义通道：无",),
            user="你的能力组合更流动。同一个人在不同团队、客户和搭档身边，能被点亮的部分会不同。因此财富策略不是逼自己永远稳定，而是筛选能让你自然发挥的场域。",
            scenes=("先做小范围合作测试，比一开始签长期绑定更适合你。",),
            blind=("为了证明自己稳定而长期留在错误环境，反而会让能力越来越钝。",),
            practices=("记录三类让你明显变聪明、变有力的合作对象，提炼共同条件。",),
        ),
    )
    promise = _wealth_boundary_item(chart)
    plan = _item(
        key="wealth.asset-plan",
        title="把收入变成长期资产",
        subtitle="未来 30 天只验证一条主线",
        basis=(f"人生角色：{summary['profile']}", f"定义：{summary['definition']}", *tuple(f"通道：{_channel_name(channel)}" for channel in channels)),
        user="财富稳定的关键不是同时开发更多方向，而是选一条身体愿意投入、能力可以重复、市场已经给出反馈的路径，连续做够一个周期。",
        scenes=("把一次服务变成流程，把一个案例变成公开证据，把重复问题变成产品，把信任关系变成稳定转介绍。",),
        embodied=("你会逐渐减少临时救火型收入，增加能复用、能提价、能被转介绍的收入。",),
        stuck=("每周都在尝试新方向，短期兴奋很多，却没有任何一项走到可以定价和复购。",),
        practices=("选一个已有真实反馈的能力，连续四周只优化同一种交付；每周记录需求、结果、客户原话和可复用步骤。",),
        followups=("结合我的真实工作，帮我选一条最值得做 30 天验证的财富主线。",),
    )
    return (
        _section("wealth-route", "财富主线", "不是先猜行业，而是先看钱怎样沿着你的盘面进入。", route),
        _section("wealth-assets", "可变现的能力", "逐条看你的稳定通道能解决什么问题。", *channel_items),
        _section("wealth-boundaries", "定价与承诺", "哪些压力会让你低价、多做或答应过头。", promise),
        _section("wealth-plan", "资产化路径", "把天然能力变成案例、方法和长期复利。", plan),
    )


def _talent_report(chart: HumanDesignChart) -> tuple[InterpretationMapSection, ...]:
    summary = _summary(chart)
    profile_code = chart.summary.profile.code
    profile = _profile_item(chart)
    channels = tuple(chart.channels)
    channel_items = (_talent_channels_item(channels),) if channels else (
        _item(
            key="talent.environmental-combination",
            title="你的天赋在关系和环境里组合",
            subtitle="流动不是缺点，而是高环境敏感度",
            basis=("已定义通道：无",),
            user="你没有一条永远固定接通的能力线路，因此不要用“我为什么不能一直稳定输出”否定自己。你更像组合型人才：遇到不同的人和场，能调用不同部分。",
            scenes=("短项目、跨团队、顾问式合作或多样场域，常比长期锁死在单一角色里更容易看见你的能力。",),
            blind=("把某个环境里被点亮的能力，当成离开那个环境后也必须一直维持。",),
            practices=("比较三个你发挥特别好的场景，先找环境共同点，再找能力共同点。",),
        ),
    )
    defined = _centers(chart, True)
    combination = _item(
        key="talent.center-combination",
        title="这些能力为什么能连在一起",
        subtitle="稳定中心是天赋的供能系统",
        basis=tuple(f"{_center_name(center.code)}：已定义" for center in defined),
        user=(
            f"你的{'、'.join(_center_name(center.code) for center in defined) or '能力'}不是几个孤立标签。"
            "中心提供资源，通道把资源接成能力线路，人生角色决定能力怎样成熟和被别人看见。"
        ),
        scenes=tuple(f"{_center_name(center.code)}提供：{CENTER_ENERGY_GUIDES[center.code]['body']}" for center in defined),
        embodied=("真正成熟时，你不会只展示一个技巧，而会把判断、节奏、表达和交付连成别人可以依赖的整体能力。",),
        blind=("容易把最自然的那一段当成“谁都会”，转而追逐别人看起来更厉害的能力。",),
        practices=("问三位长期认识你的人：我处理哪类问题时最自然、最有效、最像我自己？只记录重复出现的答案。",),
    )
    maturation = _item(
        key="talent.maturation-plan",
        title="把天然八十分练到一百分",
        subtitle=f"按{summary['profile']}的方式形成代表作",
        basis=(f"人生角色：{summary['profile']}", f"Strategy：{summary['strategy']}", *tuple(f"通道：{_channel_name(channel)}" for channel in channels)),
        user=(
            "天赋成熟不是再学更多，而是对一个已经反复出现的强项进行刻意练习、真实交付和证据积累。"
            f"对{summary['profile']}来说，正确的成熟路径是：{PROFILE_GUIDES.get(profile_code, '按自己的角色节奏在真实关系和实践中成熟。')}"
        ),
        scenes=("一项能力至少走完“自然会做—持续练习—真实交付—得到反馈—形成方法—被稳定选择”六步。",),
        embodied=("别人不只会说你“有感觉、有天赋”，而会清楚知道在什么问题上应该找你。",),
        stuck=("会很多、学很多、灵感很多，却没有作品、案例和可复述的方法。",),
        practices=("从通道能力里选一项，做四周同题训练：每周一个作品、一次真实反馈、一次方法修订。",),
        followups=("根据我的盘和现实经历，帮我找出最可能已经有八十分基础的那项天赋。",),
    )
    return (
        _section("talent-profile", "天赋怎样被发现", "先看你为什么会忽视天赋，以及别人怎样看见它。", profile),
        _section("talent-channels", "你的稳定天赋", "每条通道都是一条可以反复调用的完整能力。", *channel_items),
        _section("talent-system", "天赋怎样组合", "把人生角色、中心和通道放在一起看。", combination),
        _section("talent-maturation", "从天赋到代表作", "不给标签收尾，给出一条能验证的成熟路径。", maturation),
    )


def _relationship_report(chart: HumanDesignChart) -> tuple[InterpretationMapSection, ...]:
    summary = _summary(chart)
    profile_code = chart.summary.profile.code
    definition_code = chart.summary.definition.code
    connection = _item(
        key="relationship.network-fit",
        title="你怎样进入一段真正适合的关系",
        subtitle=f"{summary['profile']} · {summary['definition']}",
        basis=(f"人生角色：{summary['profile']}", f"定义：{summary['definition']}", f"Strategy：{summary['strategy']}"),
        user=(
            f"{PROFILE_GUIDES.get(profile_code, '你需要按自己的人生角色节奏建立连接。')}"
            f"{DEFINITION_GUIDES.get(definition_code, '')} 对你来说，强烈吸引不等于适合；"
            f"关系仍要经过「{summary['strategy']}」和 {summary['authority_professional']} 的确认。"
        ),
        scenes=("重要关系先看对方是否尊重你的节奏、边界和独处需求，再看一时感觉有多强。",),
        embodied=("适合的关系会让你更容易说真话、做真实选择，并且不需要靠过度付出来换稳定。",),
        blind=("把“他让我感觉被接通、被补全”误认为“我必须留在这段关系”。",),
        stuck=("为了维持连接，长期调成对方需要的样子，最后突然想逃开。",),
        practices=("回看一段最舒服的关系：对方做了什么，让你不需要证明、赶快回答或压住自己？",),
    )
    emotional = _relationship_emotion_item(chart)
    open_centers = _centers(chart, False)
    attraction = _item(
        key="relationship.attraction-traps",
        title="你最容易把什么误认为爱",
        subtitle="开放中心会放大吸引，也会放大代价",
        basis=tuple(f"{_center_name(center.code)}：开放" for center in open_centers),
        user=(
            f"你开放的{'、'.join(_center_name(center.code) for center in open_centers) or '中心较少'}会让某些人显得格外有吸引力。"
            "这种吸引是真实体验，但不能代替你的决定方式。"
        ),
        scenes=tuple(_relationship_open_center_line(center.code) for center in open_centers),
        blind=("最容易被吸引的地方，往往也是最容易失去边界的地方。",),
        stuck=("一开始觉得对方补足了自己，后来却发现自己越来越依赖对方的情绪、方向、肯定或节奏。",),
        causes=("盘面机制：开放中心会放大对方的稳定信号；现实场景：在关系热度最高时，你容易把放大后的感觉当成永久答案。",),
        practices=("关系中的重大承诺不要只在见面现场决定；离开对方的能量场后，再看答案是否还在。",),
    )
    fit = _item(
        key="relationship.fit-conditions",
        title="什么样的关系更适合你",
        subtitle="不是找一个标签，而是确认四个相处条件",
        basis=_core_basis(chart),
        user="适合你的关系至少要满足四件事：尊重你的决定节奏、允许你保持真实角色、能谈清承诺边界、冲突后仍能回到事实和身体感受。",
        scenes=("对方可以表达失望，但不逼你当场答应；可以亲近，也允许你独处；可以需要你，但不把你的天赋当成无限义务。",),
        embodied=("你会感觉自己在关系里更完整地活着，而不是更熟练地扮演一个好伴侣、好朋友或好合作者。",),
        stuck=("关系表面稳定，身体却长期紧、累、想躲，真实需要只能靠冷淡或爆发才能出现。",),
        practices=("和重要的人谈清三句话：我做决定需要什么节奏；我不能长期承担什么；出现冲突时我们怎样暂停和回来。",),
        followups=("根据我的盘，帮我分析一段具体关系里我正在替对方承担什么。",),
    )
    return (
        _section("relationship-entry", "连接方式", "你怎样靠近别人，也怎样保留自己。", connection),
        _section("relationship-emotion", "情绪与冲突", "分清自己的感受和现场被放大的感受。", emotional),
        _section("relationship-attraction", "吸引与盲区", "最强的吸引不一定是最稳的关系。", attraction),
        _section("relationship-fit", "适合你的关系", "把“合不合适”落到可以观察的相处条件。", fit),
    )


def _mission_report(chart: HumanDesignChart) -> tuple[InterpretationMapSection, ...]:
    summary = _summary(chart)
    personality_sun = _activation(chart, "personality", "sun")
    personality_earth = _activation(chart, "personality", "earth")
    design_sun = _activation(chart, "design", "sun")
    design_earth = _activation(chart, "design", "earth")
    cross_basis = [f"使命名称：{summary['cross']}"]
    for label, activation in (
        ("人格太阳", personality_sun),
        ("人格地球", personality_earth),
        ("设计太阳", design_sun),
        ("设计地球", design_earth),
    ):
        if activation:
            cross_basis.append(f"{label}：{activation.gate}.{activation.line}「{display_gate_theme(activation.gate, activation.gate_theme)}」")
    theme = _item(
        key="mission.cross-theme",
        title=f"你的使命主题：{summary['cross']}",
        subtitle="使命不是职业名称，而是反复出现的人生主轴",
        basis=tuple(cross_basis),
        user=(
            f"你的轮回交叉名称是「{summary['cross']}」。这四个太阳与地球位置共同构成你反复会遇见的主题。"
            "它不会直接告诉你该做哪份工作，而会告诉你：无论在哪个行业，什么问题总会把你叫到场。"
        ),
        scenes=tuple(_activation_sentence(label, activation) for label, activation in (
            ("你主动认得的主轴", personality_sun),
            ("让主轴站稳的现实课题", personality_earth),
            ("别人先从你身上感到的力量", design_sun),
            ("身体必须学会的落地方式", design_earth),
        ) if activation),
        embodied=("使命活出来时，同一种价值会在不同项目、关系和人生阶段反复出现，形式会变，主轴不会轻易消失。",),
        blind=("把使命误认成一个头衔，会逼自己守住形式，却错过真正反复出现的问题。",),
        practices=("列出过去三年最有生命力的五件事，只写它们服务了谁、解决了什么，不写职位名称，再找共同主题。",),
    )
    role = _item(
        key="mission.role-path",
        title="你用什么方式承担这条使命",
        subtitle=f"{summary['type']} · {summary['profile']}",
        basis=_core_basis(chart),
        user=(
            f"使命必须通过你的实际运作方式发生：用「{summary['strategy']}」进入正确事情，"
            f"用 {summary['authority_professional']} 决定是否投入，再用{summary['profile']}的角色路径让贡献成熟。"
        ),
        scenes=(PROFILE_GUIDES.get(chart.summary.profile.code, "你的人生角色决定经验怎样沉淀成影响力。"),),
        embodied=("你不再追问“我最终应该成为什么”，而是越来越清楚“什么事情值得我用这种方式持续承担”。",),
        stuck=(f"一旦跳过身体和角色路径，使命感会变成焦虑，日常则反复出现「{summary['not_self']}」。",),
        causes=("盘面机制：轮回交叉只能通过类型、决定方式和人生角色被活出来；现实场景：先定宏大身份再逼身体配合，会让意义感和生命力分离。",),
        practices=("回看最近一个重要选择：它是否按你的行动方式进入、经过你的决定方式确认，并允许你用自己的人生角色逐步成熟？",),
    )
    channels = tuple(chart.channels)
    channel_items = (_mission_channels_item(channels),) if channels else (
        _item(
            key="mission.environmental-path",
            title="使命通过正确环境和关系显现",
            subtitle="能力流动时，场域选择就是主线选择",
            basis=("已定义通道：无",),
            user="你的使命落地方式不是固定输出同一种能力，而是在正确的人和环境里映照、连接和整合。先选场域，再谈长期角色。",
            practices=("比较过去三个让你明显有生命力的环境，找出它们允许你成为什么样的人。",),
        ),
    )
    experiment = _item(
        key="mission.generator-cross" if "generator" in chart.summary.type.code else "mission.ninety-day-experiment",
        title="怎样验证自己正在活出使命",
        subtitle="不用给一生定案，先看 90 天证据",
        basis=(f"签名：{summary['signature']}", f"非自己主题：{summary['not_self']}", f"Strategy：{summary['strategy']}"),
        user="判断一条路是不是使命主线，不看它听起来多伟大，而看连续投入后是否同时出现三类证据：身体更有生命力、能力在积累、真实的人因为你的贡献发生变化。",
        scenes=("每两周记录一次：我解决了什么真实问题；哪项能力变强；身体更接近满足、成功、平和或惊喜，还是更接近挫败、苦涩、愤怒或失望。",),
        embodied=("方向会越来越具体，行动会越来越朴素；你不需要天天感到神圣，却会知道自己为什么继续。",),
        blind=("短期兴奋、外界掌声和宏大叙事都可能伪装成使命感。",),
        stuck=("频繁换方向、收集越来越多体系，却很少把一条真实主线做完一个周期。",),
        practices=("选一个已经有现实回应的主题做 90 天；每周固定一次交付，每两周按生命力、能力积累、真实影响各打 1-5 分。",),
        followups=("结合我最近三年的经历，帮我找使命主线的重复证据。",),
    )
    return (
        _section("mission-theme", "使命主题", "先讲清轮回交叉的名字和四个核心位置。", theme),
        _section("mission-role", "你怎样承担使命", "使命必须通过你的类型、决定方式和人生角色发生。", role),
        _section("mission-capabilities", "使命靠什么能力落地", "稳定通道是你长期贡献时可以反复调用的能力。", *channel_items),
        _section("mission-proof", "用现实验证使命", "看 90 天证据，不靠一句宏大结论。", experiment),
    )


def _profile_item(chart: HumanDesignChart) -> InterpretationMapItem:
    summary = _summary(chart)
    code = chart.summary.profile.code
    lines = [int(value) for value in code.split("-") if value.isdigit()]
    line_text = tuple(f"{line}爻：{LINE_TALENTS.get(line, '通过自己的角色路径让能力成熟')}。" for line in lines)
    if code == "2-4":
        user = (
            "2/4 的天赋常有一个反常点：你本来已经能做到八十分，因为做起来太容易，反而最容易忽视。"
            "身边人越说你在某件事上有天赋，你越可能觉得“这有什么”，然后去学习别人擅长的东西。"
            "真正的成长不是再找一个新天赋，而是把这个天然八十分的能力放回独处中精进，再通过信任关系、作品和小范围验证推到一百分。"
        )
        embodied = ("你允许天赋先在独处中熟成，不急着把半熟能力推到所有人面前；被正确的人看见后，再用作品和案例形成口碑。",)
        blind = ("把别人反复认可的能力当成“太普通”，把主要时间用来追赶别人已经擅长的事。",)
        stuck = ("学了很多、认识很多人，却没有一项能力被持续打磨到能代表你。",)
        causes = ("盘面机制：2爻会低估天然能力，4爻通过信任网络获得机会；现实场景：陌生市场的噪音很大时，你容易离开自己的强项去模仿热门能力。",)
        key = "talent.profile-24"
    else:
        user = PROFILE_GUIDES.get(code, f"{summary['profile']}说明天赋怎样成熟、怎样被看见，也说明你需要怎样的学习和关系节奏。")
        embodied = ("你按自己的角色节奏积累能力，不再用别人的成长路径催促自己。",)
        blind = ("只看到人生角色的优点，却没有接受它必须经历的学习方式。",)
        stuck = ("模仿别人的曝光、学习或获客方式，越努力越觉得自己不自然。",)
        causes = ("盘面机制：两条爻线共同决定天赋成熟和社会互动方式；现实场景：用热门成功模板替代自己的角色节奏，会让能力和被看见的方式错位。",)
        key = f"talent.profile-{code.replace('-', '')}"
    return _item(
        key=key,
        title=f"{summary['profile']}：你的天赋怎样成熟",
        subtitle="不是性格标签，是能力从潜力到被看见的路径",
        basis=(f"人生角色：{summary['profile']}", *line_text),
        user=user,
        scenes=line_text,
        embodied=embodied,
        blind=blind,
        stuck=stuck,
        causes=causes,
        practices=("列出三件别人反复找你做、你却觉得不难的事；只选重复出现两次以上的能力。",),
        followups=(f"结合我的完整盘面，{summary['profile']}最可能让我忽视哪一种天赋？",),
    )


def _talent_channels_item(channels) -> InterpretationMapItem:
    names = tuple(_channel_name(channel) for channel in channels)
    expressions = tuple(
        f"{_channel_name(channel)}：{CHANNEL_LINES.get(channel.code, '这条线路会把两种资源合成一种可重复使用的能力。')}"
        for channel in channels
    )
    return _item(
        key="talent.channel-combination",
        title="这些能力怎样在你身上连成一体",
        subtitle="通道不是分散标签，而是一组会共同出现的能力",
        basis=tuple(f"已定义通道：{name}" for name in names),
        user=(
            f"你有{'、'.join(names)}。现实里它们不会一条一条排队出现，而会在同一件事里彼此配合。"
            "真正值得发展的天赋，是你在处理某类问题时自然形成的一整套动作：你先看见什么、怎样判断、怎样推进，最后留下什么结果。"
        ),
        scenes=expressions,
        embodied=("活出来时，别人会因为一类明确的问题持续找到你，而不是只笼统地说你很有天赋。",),
        blind=("把每条通道拆成一个新方向，会让精力越来越散；它们更可能共同服务同一种核心问题。",),
        stuck=("学了很多能力名称，却没有回到真实案例里判断：哪几种能力总是一起出现、共同产生结果。",),
        practices=("找出三个你真正解决过的问题，逐个写下自己看见了什么、做了什么、结果是什么，再圈出重复动作。",),
        followups=("结合我的经历，帮我判断这些通道最可能共同解决哪一类问题。",),
    )


def _wealth_channels_item(channels) -> InterpretationMapItem:
    names = tuple(_channel_name(channel) for channel in channels)
    has_0214 = any(channel.code == "02-14" for channel in channels)
    value_lines = []
    for channel in channels:
        projected = "project" in channel.channel_type.code.lower()
        value_path = "适合用判断、引导和方法形成价值" if projected else "适合做成持续交付或可重复产出"
        value_lines.append(
            f"{_channel_name(channel)}：{CHANNEL_LINES.get(channel.code, '这是一条可以反复调用的能力线路')}；{value_path}。"
        )
    key = "wealth.02-14-main-track" if has_0214 else "wealth.channel-combination"
    title = "02-14 等能力怎样共同形成价值" if has_0214 else "你的能力组合怎样形成价值"
    return _item(
        key=key,
        title=title,
        subtitle="把完整能力组合变成一项清楚、可重复、能定价的交付",
        basis=tuple(f"已定义通道：{name}" for name in names),
        user=(
            f"你的收入能力不是把{'、'.join(names)}分别卖一次，而是让它们共同解决一个客户真正愿意付费的问题。"
            "一部分能力负责看见方向或判断问题，另一部分负责推进、保护质量或走完过程。组合后的结果，比单卖一个技巧更有价值。"
        ),
        scenes=tuple(value_lines),
        embodied=("客户能说清你解决了什么问题，你也能用相似步骤再次交付，而不是每次靠临场救火。",),
        blind=("天然能力常被免费用来帮忙；如果不记录过程和结果，别人只能觉得你人很好，却不知道该购买什么。",),
        stuck=("事情做了很多，口碑也不差，但每次都从零开始，收入无法随着经验积累而提高。",),
        causes=("盘面机制：稳定通道会重复出现，却不会自动变成产品；现实场景：只临时救场、不提炼共同问题，市场就看不见这套能力组合。",),
        practices=("选一次最有效的帮助，写清客户原来的问题、你的三个关键动作和最后结果，再用同一结构验证第二次。",),
        followups=("结合我的现实工作，这组能力最适合形成哪一种产品、服务或职责？",),
    )


def _wealth_boundary_item(chart: HumanDesignChart) -> InterpretationMapItem:
    open_centers = _centers(chart, False)
    open_codes = {center.code for center in open_centers}
    risks = []
    practices = []
    if "heart" in open_codes:
        risks.append("意志力中心开放：为了证明自己值钱，容易低价、多送、先承诺后计算成本。")
        practices.append("报价前先写清交付范围、修改次数和不包含事项，不用多做证明价值。")
    if "root" in open_codes:
        risks.append("根部中心开放：客户一催就把对方的紧急程度当成自己的优先级。")
        practices.append("所有“很急”的需求都换算成明确加急成本和新的交付时间。")
    if "solar-plexus" in open_codes:
        risks.append("情绪中心开放：为了避免对方失望，当场接受额外要求。")
        practices.append("新增需求不当场答应，统一在离开对话后书面确认范围和价格。")
    if "sacral" in open_codes:
        risks.append("荐骨中心开放：容易把别人的持续工作能力当成自己的正常电量。")
        practices.append("用可交付结果而不是在线时长定价，并给工作设置明确停止点。")
    if not risks:
        risks.append("你的中心较稳定，主要风险不是借到别人的压力，而是因为能扛就把所有责任都留在自己身上。")
        practices.append("每个新承诺都先检查资源容量，不用“我能做”替代“这值得我做”。")
    return _item(
        key="wealth.promise-boundary",
        title="什么最容易让你赚得多、剩得少",
        subtitle="财富损耗常发生在承诺时，而不是花钱时",
        basis=tuple(f"开放中心：{_center_name(center.code)}" for center in open_centers),
        user="保财首先是保护时间、注意力、交付边界和议价权。真正危险的不是一次消费，而是一个会持续吞噬资源的错误承诺。",
        scenes=tuple(risks),
        blind=("把客户满意等同于无限配合，把负责等同于所有问题都自己兜底。",),
        stuck=("收入看起来不低，但修改、沟通、救火和情绪劳动不断增加，实际时薪越来越低。",),
        causes=("盘面机制：开放中心会放大证明、赶快和避免冲突的压力；现实场景：报价或合作谈判里，你可能先照顾对方感受，最后才计算自己的成本。",),
        practices=tuple(practices),
        followups=("结合我现在的工作，帮我写一套更适合我的报价和承诺边界。",),
    )


def _relationship_emotion_item(chart: HumanDesignChart) -> InterpretationMapItem:
    emotional = next((center for center in chart.centers if center.code == "solar-plexus"), None)
    defined = bool(emotional and emotional.defined)
    if defined:
        user = "你的情绪中心已定义，情绪有自己的波。关系中的清晰不是“现在感觉很强”，而是走过高点和低点之后，答案是否仍然存在。"
        scenes = ("高点容易过度承诺，低点容易否定整段关系；两边都先不作最终决定。",)
        practice = "争执或重大承诺后至少隔一晚，再用平稳状态下的答案继续谈。"
    else:
        user = "你的情绪中心开放，会放大对方和现场的情绪。你可能比对方更难受，于是急着安抚、道歉或答应，只为了让情绪赶快结束。"
        scenes = ("对方失望时，你容易先怀疑是不是自己做错了；对方生气时，你容易跳过自己的需要去恢复和平。",)
        practice = "冲突时先暂停，不急着解释和解决；离开现场后分辨哪些感受仍然属于你。"
    return _item(
        key="relationship.emotional-boundary",
        title="冲突中怎样不丢掉自己",
        subtitle="情绪强度不能替你作决定",
        basis=(f"情绪中心：{'已定义' if defined else '开放'}",),
        user=user,
        scenes=scenes,
        embodied=("你可以感受到情绪，也可以不在情绪最高处决定关系的方向。",),
        blind=("把立刻恢复和谐当成关系成熟，实际上真实问题可能只是被压了下去。",),
        stuck=("当场答应、事后后悔；表面没冲突，身体却越来越不想靠近。",),
        causes=("盘面机制：情绪波或情绪放大会暂时改变感受强度；现实场景：对方要求马上给答案时，你容易用结束不舒服来代替真正清晰。",),
        practices=(practice,),
        followups=("拿我最近一次冲突，帮我分辨当时哪些感受可能被放大了。",),
    )


def _mission_channels_item(channels) -> InterpretationMapItem:
    names = tuple(_channel_name(channel) for channel in channels)
    expressions = tuple(
        f"{_channel_name(channel)}：{CHANNEL_LINES.get(channel.code, '这条能力线路会反复参与到你的长期贡献中')}。"
        for channel in channels
    )
    return _item(
        key="mission.channel-combination",
        title="使命靠哪些真实能力落地",
        subtitle="使命不是意义感，而是能力长期服务于同一类真实问题",
        basis=tuple(f"已定义通道：{name}" for name in names),
        user=(
            f"你的{'、'.join(names)}是使命落地时可以反复使用的能力。它们不是几个平行方向，"
            "而是同一条人生主线上的不同工具：有的负责看见问题，有的负责推进，有的负责守住价值或完成转化。"
        ),
        scenes=expressions,
        embodied=("当这些能力长期服务同一类人和问题时，使命会从抽象感觉变成别人能感受到的真实贡献。",),
        blind=("只追求使命主题听起来正确，却没有让能力持续服务现实；或者每项能力都另开一个方向，主线始终无法积累。",),
        stuck=("总在寻找更准确的身份说明，却很少把一项已经有效的贡献连续做完一个周期。",),
        practices=("从过去有效的项目里选一个真实问题，让这组能力连续服务 90 天，不先扩大身份，只记录结果。",),
    )


def _relationship_open_center_line(code: str) -> str:
    lines = {
        "head": "头顶中心开放：容易被对方的问题占满头脑，把替对方想明白当成亲密。",
        "ajna": "阿姬娜中心开放：容易为了关系稳定而认同对方的观点，害怕自己显得不确定。",
        "throat": "喉咙中心开放：容易为了被看见而多说，或在不合适的时机解释自己。",
        "g": "G中心开放：容易被有方向感的人吸引，再把对方的路当成自己的路。",
        "heart": "意志力中心开放：容易用付出、承诺和比较证明自己值得被爱。",
        "spleen": "脾中心开放：容易留在熟悉但不健康的关系里，因为离开让身体不安。",
        "solar-plexus": "情绪中心开放：容易替对方承担情绪，只求冲突赶快结束。",
        "sacral": "荐骨中心开放：容易跟着对方的工作和生活节奏一直撑，不知道什么时候该停。",
        "root": "根部中心开放：容易在对方催促时赶快承诺，把紧迫感误认成关系需要。",
    }
    return lines.get(code, f"{_center_name(code)}开放：关系现场会放大这里的感受，需要离开现场再判断。")


def _activation(chart: HumanDesignChart, imprint: str, planet: str):
    data = chart.personality if imprint == "personality" else chart.design
    return next((activation for activation in data.activations if activation.planet_code == planet), None)


def _activation_sentence(label: str, activation) -> str:
    theme = display_gate_theme(activation.gate, activation.gate_theme)
    return f"{label}：{activation.gate}.{activation.line}「{theme}」。观察这个主题怎样在你重要选择和长期贡献中反复出现。"


def _authority_guide(code: str) -> str:
    guide = AUTHORITY_GUIDES.get(code, "决定要回到你自己的内在信号，而不是只看利弊表。")
    replacements = {
        "荐骨权威": "Sacral Authority",
        "情绪权威": "Emotional Authority",
        "脾权威": "Splenic Authority",
        "意志权威": "Ego Authority",
        "自我投射权威": "Self-Projected Authority",
        "外在权威": "Environmental Authority",
        "月亮权威": "Lunar Authority",
    }
    for source, target in replacements.items():
        guide = guide.replace(source, target)
    return guide


def _summary(chart: HumanDesignChart) -> dict[str, str]:
    authority = display_authority(chart.summary.authority.code, chart.summary.authority.label)
    return {
        "type": display_type(chart.summary.type.code, chart.summary.type.label),
        "strategy": display_strategy(chart.summary.strategy.code, chart.summary.strategy.label),
        "authority": authority,
        "authority_professional": display_authority_professional(chart.summary.authority.code, authority),
        "profile": display_profile(chart.summary.profile.code, chart.summary.profile.label),
        "definition": display_definition(chart.summary.definition.code, chart.summary.definition.label),
        "cross": display_incarnation_cross(chart.summary.incarnation_cross.code, chart.summary.incarnation_cross.label),
        "signature": display_signature(chart.summary.signature.code, chart.summary.signature.label),
        "not_self": display_not_self(chart.summary.not_self_theme.code, chart.summary.not_self_theme.label),
    }


def _core_basis(chart: HumanDesignChart) -> tuple[str, ...]:
    summary = _summary(chart)
    return (
        f"类型：{summary['type']}",
        f"Strategy：{summary['strategy']}",
        f"Authority：{summary['authority_professional']}",
        f"人生角色：{summary['profile']}",
        f"定义：{summary['definition']}",
    )


def _centers(chart: HumanDesignChart, defined: bool):
    return tuple(center for center in chart.centers if center.defined is defined)


def _center_names(chart: HumanDesignChart, defined: bool) -> tuple[str, ...]:
    return tuple(_center_name(center.code) for center in _centers(chart, defined))


def _center_name(code: str) -> str:
    return normalize_center_title(CENTER_LABELS.get(code, code))


def _channel_name(channel) -> str:
    return f"{channel.code}「{display_channel_label(channel.code, channel.label)}」"


def _channel_names(chart: HumanDesignChart) -> tuple[str, ...]:
    return tuple(_channel_name(channel) for channel in chart.channels)


def _section(key: str, title: str, intro: str, *items: InterpretationMapItem) -> InterpretationMapSection:
    return InterpretationMapSection(key=key, title=title, intro=intro, items=tuple(items))


def _item(
    *,
    key: str,
    title: str,
    subtitle: str,
    basis: Iterable[str],
    user: str,
    scenes: Iterable[str] = (),
    embodied: Iterable[str] = (),
    blind: Iterable[str] = (),
    stuck: Iterable[str] = (),
    causes: Iterable[str] = (),
    practices: Iterable[str] = (),
    followups: Iterable[str] = (),
) -> InterpretationMapItem:
    return InterpretationMapItem(
        key=key,
        title=title,
        subtitle=subtitle,
        diagnosis_depth="deep",
        chart_basis=tuple(basis),
        professional_basis="",
        user_language=user,
        life_scenes=tuple(scenes),
        embodied_expression=tuple(embodied),
        blind_spots=tuple(blind),
        stuck_patterns=tuple(stuck),
        stuck_causes=tuple(causes),
        common_blocks=(),
        practices=tuple(practices),
        followup_questions=tuple(followups),
        source_atom_ids=(),
        sources=(),
    )
