from __future__ import annotations

from collections.abc import Iterable

from .body_energy import CENTER_ENERGY_GUIDES
from .channel_guides import CHANNEL_LINES
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

CHANNEL_MISUSES = {
    "01-08": "为了显得独特而刻意反常，作品还没成熟就急着要求别人理解。",
    "02-14": "方向没有确认就持续加码，把能吃苦误认为路走对了。",
    "03-60": "讨厌限制和混乱，频繁推翻刚开始形成的新秩序。",
    "04-63": "用怀疑攻击自己或别人，却没有把怀疑整理成一个可验证的问题。",
    "05-15": "为了配合外界节奏不断打乱自己的作息，最后靠意志硬撑。",
    "06-59": "为了建立亲密过早穿越边界，或者害怕受伤而把门彻底关上。",
    "07-31": "没有得到群体认可就抢着带方向，正确判断也因此难以被接住。",
    "09-52": "把专注投在不重要的细节上，越钻越深却离真正问题越来越远。",
    "10-20": "为了维持人设而表演真实，话语和当下行为开始彼此矛盾。",
    "10-34": "把独立活成拒绝合作，任何建议都被听成对自主性的干涉。",
    "10-57": "第一秒已经知道不对，后来却被合理化和别人的意见覆盖。",
    "11-56": "把每个有趣想法都当成必须完成的项目，注意力被故事不断带走。",
    "12-22": "在情绪和时机不对时强行表达，事后又因没有被理解而封闭自己。",
    "13-33": "替别人保管太多故事却没有退隐消化，最后被过去和秘密压住。",
    "16-48": "总觉得还不够好而迟迟不上场，练习变成逃避真实检验。",
    "17-62": "用细节证明自己正确，却忘了先确认对方是否真的需要这套观点。",
    "18-58": "把改善事情变成纠正别人，眼里只剩缺点而失去生命力。",
    "19-49": "需要和原则没有提前说清，忍到越界后才用决裂保护自己。",
    "20-34": "回应还没出现就凭速度开工，忙得很快，也错得很快。",
    "20-57": "为了让直觉显得合理而不断解释，反而错过第一秒最清楚的信号。",
    "21-45": "把负责变成事事掌控，别人没有空间，你也被所有资源问题绑住。",
    "23-43": "洞见刚出现就急着讲给没有准备的人，最后把听不懂误认为自己有问题。",
    "24-61": "逼自己马上想通，同一个问题在头脑里反复打转却没有新的输入。",
    "25-51": "用冲击证明自己勇敢，或者把每一次危机都当成必须独自跨越的考验。",
    "26-44": "为了成交夸大价值，短期说服成功，长期信任却被透支。",
    "27-50": "把照顾和负责当成身份，不分对象地付出，最后用委屈索取回报。",
    "28-38": "为了证明事情有意义而持续战斗，忘了检查这场仗是否还值得。",
    "29-46": "承诺太快，靠走到底维持自我形象，即使身体早已没有回应。",
    "30-41": "沉浸在渴望和想象里，把体验前的期待误当成已经发生的现实。",
    "32-54": "急着向上走而忽略基础、时机和可靠联盟，野心变成持续焦虑。",
    "34-57": "力量先冲出去，直觉却被落在后面，事后才发现是在证明而不是保护生命。",
    "35-36": "为了摆脱无聊不断追求新经历，还没消化上一段就进入下一段。",
    "37-40": "默认彼此应该懂得付出与回报，约定没说清，亲近慢慢变成欠账。",
    "39-55": "用挑动情绪确认自己有影响力，或把暂时低潮误认成生命失去意义。",
    "42-53": "不断开始却不愿完成，旧周期没有收尾，新机会也无法真正展开。",
    "47-64": "要求碎片立刻拼成答案，把还在形成中的领悟当成自己的混乱。",
}

CHANNEL_PRACTICES = {
    "02-14": "选一个正在投入的方向，连续记录四周：身体是否更有力、资源是否形成积累；两项都没有，就先停止加码。",
    "16-48": "选一项已经有基础的技能，连续四周每周公开一次作品；用真实反馈替代“我还没准备好”。",
    "21-45": "列出你必须掌控、可以授权、需要共同决定的资源，停止把三类责任混在一起。",
    "35-36": "每段新经历结束后写下一个可复用的判断，不让经历只留下刺激。",
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
        "channels": _channels_report,
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
        "channels": _channel_report_overview(channels),
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


def _channel_report_overview(channels: tuple[str, ...]) -> str:
    if not channels:
        return "你的图里没有固定接通的完整通道。重点不是强迫自己维持一种固定输出，而是认出哪些人和环境会让正确能力自然出现。"
    if len(channels) == 1:
        return (
            f"你有一条稳定通道：{channels[0]}。先把这条能力本身看清，再看它怎样经过人生角色成熟、由 Authority 判断使用时机；"
            "通道说明你能怎样运作，不替你决定眼前这件事值不值得做。"
        )
    return (
        f"你有{len(channels)}条稳定通道：{'、'.join(channels)}。"
        "先逐条看清能力，再看它们在同一件事里怎样形成完整动作，以及哪一种误用正在让强项变成消耗。"
    )


def _single_channel_integration(chart: HumanDesignChart, channel) -> InterpretationMapItem:
    summary = _summary(chart)
    name = _channel_name(channel)
    expression = CHANNEL_LINES.get(channel.code, "这条线路会把两个中心的资源接成一种可重复使用的能力")
    return _item(
        key="channels.integration",
        title=f"{name}怎样进入你的生活",
        subtitle=f"{summary['profile']}决定成熟路径，{summary['authority_professional']}决定是否投入",
        basis=(f"已定义通道：{name}", f"人生角色：{summary['profile']}", f"Authority：{summary['authority_professional']}"),
        user=(
            f"{name}是你唯一固定接通的完整能力线路，因此它在工作和关系里可能特别显眼：{expression}。"
            f"但这条通道不是你的全部，也不替你作决定。它要沿着{summary['profile']}的角色路径被看见，"
            f"并在 {summary['authority_professional']} 真正确认投入后，才适合用在眼前的人和问题上。"
        ),
        scenes=("当别人反复因为你在这类问题上创造的结果来找你，这条通道才从个人反应变成可识别的能力。",),
        embodied=("你既能承认这项能力属于自己，也不会因为它很强就把每个问题都变成自己的任务。",),
        blind=("因为这条能力反复出现，就把所有机会都理解成它的用武之地，忽略对象和时机。",),
        stuck=("能力偶尔很有冲击力，但没有稳定案例；或者一出手就过量，事后只剩消耗。",),
        causes=("盘面机制：已定义通道会稳定存在，但 Strategy 与 Authority 决定怎样进入具体事情；现实场景：别人一有需要就立刻出手，会把能力和正确时机混为一谈。",),
        practices=("找出三次这条能力真正产生结果的经历，同时记录谁邀请或触发了你、你怎样确认投入、最后改变了什么。",),
        followups=(f"结合我的其他特质，{name}在什么人和问题上最容易被正确使用？",),
    )


def _multi_channel_integration(chart: HumanDesignChart, channels) -> InterpretationMapItem:
    summary = _summary(chart)
    names = tuple(_channel_name(channel) for channel in channels)
    return _item(
        key="channels.combination",
        title="这些通道怎样在同一件事里接力",
        subtitle=f"{summary['profile']}让能力成熟，{summary['authority_professional']}筛选使用时机",
        basis=(
            *tuple(f"已定义通道：{name}" for name in names),
            f"人生角色：{summary['profile']}",
            f"Authority：{summary['authority_professional']}",
        ),
        user=(
            f"你的{'、'.join(names)}会同时存在于同一个人身上。真实工作时，它们可能先后出现，也可能由不同场景触发；"
            "关键不是给每条通道另找一个身份，而是认出你解决一个问题时反复出现的完整过程。"
            f"这套过程要沿着{summary['profile']}的角色路径成熟，并由 {summary['authority_professional']} 筛掉不值得投入的事情。"
        ),
        scenes=tuple(
            f"{_channel_name(channel)}带来的具体动作：{CHANNEL_LINES.get(channel.code, '把两种资源接成稳定能力')}。"
            for channel in channels
        ),
        embodied=("你能用真实案例说明每条能力在过程里做了什么，也能说清最终解决的是哪一类问题。",),
        blind=("把每条通道都发展成一个新方向，结果每项都只停留在概念层。",),
        stuck=("能力不少、兴趣不少，但别人仍不知道遇到什么问题应该来找你。",),
        causes=("盘面机制：多条通道会在同一个人身上同时运作；现实场景：如果按术语拆成多个身份，原本完整的解决问题方式反而被切碎。",),
        practices=("选三个结果最好的案例，标出每条通道实际承担了哪一步；最后用一句话概括这套过程共同解决的问题。",),
    )


def _channels_report(chart: HumanDesignChart) -> tuple[InterpretationMapSection, ...]:
    channels = tuple(chart.channels)
    if not channels:
        item = _item(
            key="channels.environmental-activation",
            title="你的能力更依赖人与环境被接通",
            subtitle="没有固定通道，不等于没有天赋",
            basis=("已定义通道：无",),
            user=(
                "这张图没有固定接通的完整通道。你更像一套高度响应环境的系统：不同的人、团队和关系会接通不同能力。"
                "因此，真正重要的不是逼自己永远保持同一种输出，而是辨认哪些场域会让你更清楚、更有力、更像自己。"
            ),
            scenes=("同一件事在某个团队里做得自然，换一个环境却完全提不起力，往往不是能力消失，而是接通条件改变。",),
            embodied=("能力成熟以后，你不再把流动当成不稳定，而会主动选择能让正确能力出现的人和场，并能说清这些场域共有的条件。",),
            blind=("把某个关系里被点亮的能力，当成离开那段关系后也必须独自维持。",),
            stuck=("不断要求自己稳定，却很少检查环境是否适合，最后把场域问题解释成个人缺陷。",),
            causes=("盘面机制：没有固定通道时，不同能力会被不同的人与环境接通；现实场景：离开适合的团队后仍要求自己复制原来的输出，会把场域变化误判成能力退步。",),
            practices=("列出三个你发挥最好和三个最消耗的场景，比较空间、关系、任务和节奏的共同差异。",),
        )
        return (_section("channels-environment", "什么环境会让你发挥出来", "同一个人换了环境，能用出来的能力也会不同。", item),)

    details = tuple(_channel_detail_item(channel) for channel in channels)
    integration = _single_channel_integration(chart, channels[0]) if len(channels) == 1 else _multi_channel_integration(chart, channels)
    maturation_followup = (
        "结合我的现实经历，帮我判断这条通道最适合怎样练成代表能力。"
        if len(channels) == 1
        else "结合我的现实经历，帮我判断哪条通道最值得先练成代表能力。"
    )
    maturation = _item(
        key="channels.maturation",
        title="把通道从天然反应练成可靠能力",
        subtitle="真正可靠的能力，一定能在生活里找到重复证据",
        basis=tuple(f"已定义通道：{_channel_name(channel)}" for channel in channels),
        user=(
            "一条通道被定义，只说明这套能量线路会反复出现，不代表它已经成熟。成熟要经过三步：先认出它什么时候自然启动，"
            "再看它给别人带来什么具体结果，最后学会在不适合的场景里不滥用它。"
        ),
        scenes=("当别人能稳定说出“遇到这类问题会想到你”，通道才开始从个人反应变成社会可识别的能力。",),
        embodied=("你知道什么时候该使用强项，也知道什么时候停手，不再把持续输出当成证明。",),
        blind=("只记通道名称，却没有收集任何现实案例；或者因为天然会做，就从未系统练习。",),
        stuck=("能力偶尔很亮，但无法重复交付，也说不清它解决了什么问题。",),
        practices=("未来四周只记录三件事：触发场景、你的关键动作、对方得到的结果。月底只保留重复出现的模式。",),
        followups=(maturation_followup,),
    )
    return (
        _section("channels-details", "每条通道带来什么能力", "先看它自然会怎么工作，再看什么时候容易用过头。", *details),
        _section(
            "channels-combination",
            "这条能力怎样进入你的生活" if len(channels) == 1 else "这些能力怎样一起工作",
            "同一项能力，在不同对象和时机里会产生完全不同的结果。" if len(channels) == 1 else "现实中的你不是几条通道相加，而是一套完整的做事方式。",
            integration,
        ),
        _section("channels-maturation", "怎样把能力练成熟", "用案例、反馈和边界，把偶尔做得好变成可以稳定做到。", maturation),
    )


def _channel_detail_item(channel) -> InterpretationMapItem:
    name = _channel_name(channel)
    expression = CHANNEL_LINES.get(channel.code, "这条线路会把两个中心的资源合成一种可重复使用的能力")
    misuse = CHANNEL_MISUSES.get(channel.code, "在不对的时机强行使用这项能力，会让天赋变成证明和消耗。")
    practice = CHANNEL_PRACTICES.get(
        channel.code,
        "回看三次这项能力自然出现的场景，写下触发条件、你的关键动作和最后结果，找出可重复部分。",
    )
    centers = "与".join(_center_name(code) for code in channel.centers)
    return _item(
        key=f"channels.{channel.code}",
        title=name,
        subtitle=f"{centers}之间的稳定能力线路",
        basis=(f"已定义通道：{name}", f"连接中心：{centers}"),
        user=(
            f"这条通道在你身上的核心不是一个抽象词，而是：{expression}。"
            f"对{name}来说，这项能力常先以自然反应出现，你自己甚至觉得没什么；"
            "当它被放进正确问题里，别人会从你的处理方式和结果里感到明显差异。"
        ),
        scenes=(f"在工作、关系或选择中，留意你什么时候会自然做出这套动作：{expression}。",),
        embodied=("成熟时，你能稳定使用这项能力，也能说明它在什么问题上真正有效，不需要到处证明。",),
        blind=(misuse,),
        stuck=(f"这条能力被卡住时，常见状态是：{misuse}",),
        causes=(f"盘面机制：{name}会稳定存在并反复参与；现实场景：如果对象、时机或问题不对，天然反应就容易被误用成过度用力。",),
        practices=(practice,),
        followups=(f"结合我的其他特质，{name}最适合在哪类现实问题里发挥？",),
    )


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
    stable_basis = tuple(f"{_center_name(center.code)}：已定义" for center in defined)
    if not stable_basis:
        stable_basis = ("已定义中心：无，九个中心均开放",)
    stable = _item(
        key="body.stable-resources",
        title="你身体里相对稳定的资源",
        subtitle="这些力量在你身上比较稳定",
        basis=stable_basis,
        user=(
            f"你的{'、'.join(_center_name(center.code) for center in defined)}是较稳定的资源。"
            "稳定不等于每时每刻都强，而是状态合适时，你更容易重复调用这些能力。"
            if defined
            else "你的九个中心都保持开放，没有一块能量需要被你固定成永远相同的样子。你会细致地感受并放大现场，因此身体资源首先来自对环境的辨认，而不是强迫自己稳定输出。"
        ),
        scenes=tuple(
            f"{_center_name(center.code)}：{CENTER_ENERGY_GUIDES[center.code]['body']}"
            for center in defined
        ) or ("你的稳定感更依赖正确环境，因此选地方和人比逼自己固定更重要。",),
        embodied=(
            "真正用对这些资源时，你不需要向别人证明；它们会自然进入做事、表达和关系。"
            if defined
            else "活对时，你允许每天的状态有所不同，却能稳定辨认什么环境让自己清明、什么环境让自己浑浊。",
        ),
        blind=(
            "稳定资源也会被过度使用：会做不等于每次都该由你做。"
            if defined
            else "把别人暂时带给你的能量、确定感或方向感认成自己的固定身份，离开现场后仍勉强维持。",
        ),
        stuck=(
            "长期把稳定能力拿去救火，会出现“别人越来越依赖你，你却越来越没有自己的主线”。"
            if defined
            else "在不同人面前像不同的自己，回到独处却说不清真正想要什么，于是靠承诺和人设制造虚假的稳定。",
        ),
        causes=(
            "盘面机制：已定义中心会反复提供相对稳定的资源；现实场景：因为自己能扛就长期替别人救火，会把强项用成义务。"
            if defined
            else "盘面机制：九个开放中心会持续采样并放大环境信号；现实场景：长期留在高压关系或团队里，会把现场状态误认为自己的本性。",
        ),
        practices=(
            "圈出最近一周最耗能的三件事，分辨哪一件只是因为你能做，而不是因为它值得你做。"
            if defined
            else "连续两周记录每天所在的环境、接触的人和离开后的身体感受，找出让你清明与让你浑浊的重复条件。",
        ),
    )
    if open_centers:
        pressure = _item(
            key="body.open-pressure-chain",
            title="压力最容易从哪里进入",
            subtitle="这些地方更容易把别人的状态接到自己身上",
            basis=tuple(f"{_center_name(center.code)}：开放" for center in open_centers),
            user=(
                f"你开放的是{'、'.join(_center_name(center.code) for center in open_centers)}。"
                "压力通常不是一下子把你压垮，而是先在其中一个位置出现，再带着你加速、证明、安抚或硬撑。"
            ),
            scenes=tuple(
                f"{_center_name(center.code)}：{CENTER_ENERGY_GUIDES[center.code]['open_body']}"
                for center in open_centers
            ),
            blind=tuple(CENTER_ENERGY_GUIDES[center.code]["consumption"] for center in open_centers),
            stuck=tuple(
                f"{_center_name(center.code)}被带走时：{CENTER_ENERGY_GUIDES[center.code]['consumption']}"
                for center in open_centers
            ),
            causes=("盘面机制：开放中心会放大现场信号；现实场景：催促、冲突或比较一出现，你会暂时把别人的状态当成自己的任务。",),
            practices=tuple(CENTER_ENERGY_GUIDES[center.code]["practice"] for center in open_centers[:3]),
            followups=("按我最常见的生活场景，判断压力链通常从哪个中心开始。",),
        )
    else:
        pressure = _item(
            key="body.open-pressure-chain",
            title="当所有中心都稳定，压力会怎样出现",
            subtitle="重点不是被别人放大，而是把稳定资源一直开到最大",
            basis=("九个中心均已定义",),
            user=(
                "你的九个中心都有定义，外界不容易从某个开放中心把你整个人带跑。你的主要风险反而是过度依赖自己的稳定："
                "一直思考、一直表达、一直负责、一直工作，直到身体只能用疲惫或冲突逼你停下来。"
            ),
            scenes=("事情越多时，你越容易觉得自己每一部分都能顶上，于是同时承担判断、推进、安抚、交付和收尾。",),
            embodied=("成熟时，你能使用全部稳定资源，也能主动关掉暂时不需要的部分，不把全天候有能力等同于全天候有责任。",),
            blind=("别人确实很难替代你，于是你也越来越难授权、求助或承认今天不想做。",),
            stuck=("表面仍能运转，内在却持续烦躁、紧绷，对任何新增需求都带着被侵犯的感觉。",),
            causes=("盘面机制：九个中心持续提供相对稳定的资源；现实场景：团队习惯把复杂问题都交给你时，能做会逐渐变成必须做。",),
            practices=("把本周任务分成必须由我完成、可以授权、可以停止三栏，至少真实移出一项。",),
            followups=("我没有开放中心，最需要防止哪一种稳定能力被用过头？",),
        )
    recovery = _item(
        key="body.recovery-order",
        title="能量乱掉以后，按什么顺序回来",
        subtitle="先离开让你越来越乱的现场，再想下一步",
        basis=(f"Strategy：{summary['strategy']}", f"Authority：{summary['authority_professional']}", f"开放中心数量：{len(open_centers)}"),
        user="能量乱掉时，恢复不是再逼自己做一套正确方法，而是先停止继续接收现场压力。等身体重新听得见自己，再决定下一步，不要在还被现场情绪和压力裹住时寻找答案。",
        scenes=("第一步离开高压现场；第二步把问题缩小；第三步按自己的决定方式确认；第四步只处理下一件事。",),
        embodied=("恢复之后，你会重新知道什么值得做、什么可以晚一点、什么根本不是你的责任。",),
        stuck=("如果休息时还在反复想怎样让所有人满意，身体虽然停了，压力链并没有停。",),
        practices=("今天只做一次：感到急时离开现场十分钟，不解决问题，只记录身体哪里紧、哪里松。",),
    )
    return (
        _section("body-decision", "你怎样做决定", "身体会先给信号，头脑再负责安排。", decision),
        _section("body-resources", "你能稳定使用的力量", "强项可以反复使用，也可能因为用得太多变成负担。", stable),
        _section("body-pressure", "你最容易在哪里被带着走", "压力往往不是突然出现，而是从一个熟悉的入口慢慢累积。", pressure),
        _section("body-recovery", "乱掉以后，先做什么", "先让身体重新安静下来，再处理问题。", recovery),
    )


def _wealth_report(chart: HumanDesignChart) -> tuple[InterpretationMapSection, ...]:
    summary = _summary(chart)
    channels = tuple(chart.channels)
    route = _item(
        key="wealth.income-route",
        title="钱更可能从哪里来",
        subtitle="先选对事情，再把能力做成别人愿意付费的结果",
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
    channel_items = (_wealth_channels_item(chart, channels),) if channels else (
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
        subtitle="先用 30 天看这条方向有没有真实积累",
        basis=(f"人生角色：{summary['profile']}", f"定义：{summary['definition']}", *tuple(f"通道：{_channel_name(channel)}" for channel in channels)),
        user="财富稳定的关键不是同时开发更多方向，而是选一条身体愿意投入、能力可以重复、市场已经给出反馈的路径，连续做够一个周期。",
        scenes=("把一次服务变成流程，把一个案例变成公开证据，把重复问题变成产品，把信任关系变成稳定转介绍。",),
        embodied=("你会逐渐减少临时救火型收入，增加能复用、能提价、能被转介绍的收入。",),
        stuck=("每周都在尝试新方向，短期兴奋很多，却没有任何一项走到可以定价和复购。",),
        practices=("选一个已有真实反馈的能力，连续四周只优化同一种交付；每周记录需求、结果、客户原话和可复用步骤。",),
        followups=("结合我的真实工作，帮我选一条最值得做 30 天验证的财富主线。",),
    )
    return (
        _section("wealth-route", "钱更可能从哪里来", "先看你能持续创造什么价值，再看适合什么行业。", route),
        _section("wealth-assets", "哪些能力可以形成收入", "真正能变现的能力，需要能解决清楚的问题。", *channel_items),
        _section("wealth-boundaries", "怎样定价，怎样不过度承诺", "很多损耗不是不会赚钱，而是答应得太多。", promise),
        _section("wealth-plan", "怎样形成长期积累", "把一次交付留下的经验，慢慢变成案例、方法和资产。", plan),
    )


def _talent_report(chart: HumanDesignChart) -> tuple[InterpretationMapSection, ...]:
    summary = _summary(chart)
    profile_code = chart.summary.profile.code
    profile = _profile_item(chart)
    channels = tuple(chart.channels)
    channel_items = tuple(_talent_channel_item(chart, channel) for channel in channels) if channels else (
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
    center_basis = tuple(f"{_center_name(center.code)}：已定义" for center in defined)
    if not center_basis:
        center_basis = ("已定义中心：无，九个中心均开放",)
    combination = _item(
        key="talent.center-combination",
        title="这些能力为什么能连在一起",
        subtitle="这些稳定力量会反复支持你的能力",
        basis=center_basis,
        user=(
            f"你的{'、'.join(_center_name(center.code) for center in defined)}不是几个孤立标签。"
            "中心提供资源，通道把资源接成能力线路，人生角色决定能力怎样成熟和被别人看见。"
            if defined
            else "你的天赋不靠某几个中心持续供能，而靠对人与环境的高分辨率感受完成组合。人生角色决定你怎样学习和被看见，反复出现的适配条件才是你最值得发展的能力线索。"
        ),
        scenes=tuple(f"{_center_name(center.code)}提供：{CENTER_ENERGY_GUIDES[center.code]['body']}" for center in defined)
        or ("比较你在不同团队、关系和空间里的表现，观察哪些条件会反复让判断、表达和行动同时变清楚。",),
        embodied=(
            "真正成熟时，你不会只展示一个技巧，而会把判断、节奏、表达和交付连成别人可以依赖的整体能力。"
            if defined
            else "真正成熟时，你能快速读懂一个场域，也能在离开后分清哪些能力值得留下练习、哪些只是现场借来的状态。",
        ),
        blind=(
            "容易把最自然的那一段当成“谁都会”，转而追逐别人看起来更厉害的能力。"
            if defined
            else "因为自己在不同环境里表现不同，就认定没有真正天赋，转而复制一个看起来更稳定的人设。",
        ),
        stuck=(
            "学会了很多单项技巧，却没有把它们连成一套可以重复解决问题的整体能力。"
            if defined
            else "环境一换就怀疑自己，频繁更换方向，却从未整理哪些场域条件能让能力反复出现。",
        ),
        causes=(
            "盘面机制：稳定中心与通道共同构成可重复调用的供能系统；现实场景：只追逐单项技巧，会看不见强项之间已经形成的完整动作。"
            if defined
            else "盘面机制：九个开放中心会随环境接收并放大不同信号；现实场景：如果只比较每次输出是否相同，就会错过适配条件本身才是稳定线索。",
        ),
        practices=("问三位长期认识你的人：我处理哪类问题时最自然、最有效、最像我自己？只记录重复出现的答案。",),
    )
    maturation = _item(
        key="talent.maturation-plan",
        title="把天然八十分练到一百分",
        subtitle=f"按{summary['profile']}的方式形成代表作",
        basis=(f"人生角色：{summary['profile']}", f"Strategy：{summary['strategy']}", *tuple(f"通道：{_channel_name(channel)}" for channel in channels)),
        user=(
            "天赋成熟不是再学更多，而是对一个已经反复出现的强项进行刻意练习、真实交付和证据积累。"
            f"对{summary['profile']}来说，可以沿着这条路径成熟：{_profile_maturation_path(profile_code)}"
        ),
        scenes=("一项能力至少走完“自然会做—持续练习—真实交付—得到反馈—形成方法—被稳定选择”六步。",),
        embodied=("别人不只会说你“有感觉、有天赋”，而会清楚知道在什么问题上应该找你。",),
        stuck=("会很多、学很多、灵感很多，却没有作品、案例和可复述的方法。",),
        practices=("从通道能力里选一项，做四周同题训练：每周一个作品、一次真实反馈、一次方法修订。",),
        followups=("根据我的盘和现实经历，帮我找出最可能已经有八十分基础的那项天赋。",),
    )
    return (
        _section("talent-profile", "别人为什么会看见你", "你常常最容易忽视那些自己做起来很自然的事。", profile),
        _section("talent-channels", "你天然会的能力", "每条通道都会带来一种可以反复使用的完整能力。", *channel_items),
        _section("talent-system", "这些能力怎样放在一起", "真正的天赋通常不是一个点，而是一套重复出现的做事方式。", combination),
        _section("talent-maturation", "把天赋练成代表作", "用作品和真实结果，看清哪项能力值得长期练下去。", maturation),
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
            f"{_relationship_profile_guide(profile_code)}"
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
    if open_centers:
        attraction = _item(
            key="relationship.attraction-traps",
            title="你最容易把什么误认为爱",
            subtitle="开放中心会放大吸引，也会放大代价",
            basis=tuple(f"{_center_name(center.code)}：开放" for center in open_centers),
            user=(
                f"你开放的{'、'.join(_center_name(center.code) for center in open_centers)}会让某些人显得格外有吸引力。"
                "这种吸引是真实体验，但不能代替你的决定方式。先分辨你是真的想靠近，还是只是不想失去对方带来的完整感、确定感或轻松感。"
            ),
            scenes=tuple(_relationship_open_center_line(center.code) for center in open_centers),
            blind=("最容易被吸引的地方，往往也是最容易失去边界的地方。",),
            stuck=("一开始觉得对方补足了自己，后来却发现自己越来越依赖对方的情绪、方向、肯定或节奏。",),
            causes=("盘面机制：开放中心会放大对方的稳定信号；现实场景：在关系热度最高时，你容易把放大后的感觉当成永久答案。",),
            practices=("关系中的重大承诺不要只在见面现场决定；离开对方的能量场后，再看答案是否还在。",),
        )
    else:
        attraction = _item(
            key="relationship.attraction-traps",
            title="你不缺完整感，更要看彼此能不能并肩",
            subtitle="九个中心都有定义时，吸引不一定来自互补",
            basis=("九个中心均已定义", f"Authority：{summary['authority_professional']}"),
            user=(
                "你的九个中心都有定义，关系并不主要靠对方补足某块能量。更需要观察的是：两个都很有自己节奏的人，"
                "能否协商空间、责任和决定方式，而不是谁用更强的稳定性压过谁。"
            ),
            scenes=("两个人都很确定时，关系的考验不是有没有感觉，而是分歧出现后能否保留彼此的节奏和主权。",),
            embodied=("成熟的关系不会要求一方变弱；你们可以各自完整，也能在共同决定上留出真正协商。",),
            blind=("因为自己很确定，就把对方的不同节奏理解成拖延、软弱或不够投入。",),
            stuck=("关系变成两套稳定系统互相顶住，谁都能讲清理由，却越来越听不见对方。",),
            causes=("盘面机制：九个中心都有稳定运作方式；现实场景：冲突中双方都坚持自己的节奏时，能力容易变成控制而不是合作。",),
            practices=("下一次分歧先分别说清自己的需要和不能承受的代价，再讨论共同方案，不用理由数量决定谁正确。",),
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
        _section("relationship-entry", "你怎样和人靠近", "靠近一个人时，也要看自己有没有越来越像自己。", connection),
        _section("relationship-emotion", "冲突里最容易发生什么", "先分清自己的感受，再处理现场被放大的情绪。", emotional),
        _section("relationship-attraction", "哪些吸引会让你失去自己", "感觉很强烈，不一定代表这段关系适合长期走下去。", attraction),
        _section("relationship-fit", "什么关系更适合你", "不猜理想类型，只看真实相处里有没有尊重、边界和空间。", fit),
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
            f"你会用自己的方式走这条路：先按「{summary['strategy']}」进入合适的事情，"
            f"再用 {summary['authority_professional']} 决定是否投入，并按{summary['profile']}的节奏让贡献慢慢成熟。"
        ),
        scenes=(PROFILE_GUIDES.get(chart.summary.profile.code, "你的人生角色决定经验怎样沉淀成影响力。"),),
        embodied=("你不再追问“我最终应该成为什么”，而是越来越清楚“什么事情值得我用这种方式持续承担”。",),
        stuck=(f"一旦跳过身体和角色路径，使命感会变成焦虑，日常则反复出现「{summary['not_self']}」。",),
        causes=("盘面机制：轮回交叉只能通过类型、决定方式和人生角色被活出来；现实场景：先定宏大身份再逼身体配合，会让意义感和生命力分离。",),
        practices=("回看最近一个重要选择：它是否按你的行动方式进入、经过你的决定方式确认，并允许你用自己的人生角色逐步成熟？",),
    )
    channels = tuple(chart.channels)
    channel_items = (_mission_channels_item(chart, channels),) if channels else (
        _item(
            key="mission.environmental-path",
            title="使命通过正确环境和关系显现",
            subtitle="能力流动时，场域选择就是主线选择",
            basis=("已定义通道：无",),
            user="你的使命不会靠固定输出同一种能力落地，而会在不同的人和环境里显出不同侧面。真正稳定的不是人设，而是你对场域的辨认：哪些地方让你清楚、能看见整体，也让别人因为你的存在更看清自己。先选对场域，再谈长期角色。",
            scenes=("同样一项工作，在让你清明的团队里，你能迅速看见整体状态；在持续混乱的环境里，你只会放大压力并开始怀疑自己。",),
            embodied=("使命活出来时，你不需要维持固定人格，而能稳定选择让自己清明、也让他人获得真实反馈的环境。",),
            blind=("把适应力当成必须适合所有地方，或者把某个环境里借来的能力认成永远不变的身份。",),
            stuck=("不断更换身份和方向，希望找到一个永远确定的自己，却没有认真筛选长期相处的人与环境。",),
            causes=("盘面机制：没有固定通道时，能力会由关系与环境接通；现实场景：如果先承诺角色再检查场域，长期放大的可能是压力而不是使命。",),
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
        _section("mission-theme", "你反复遇到的人生主题", "轮回交叉的名字只是入口，真正的主题会在经历里反复出现。", theme),
        _section("mission-role", "你会怎样走这条路", "你做决定、与人连接和使用能力的方式，决定了这条路怎样展开。", role),
        _section("mission-capabilities", "哪些能力帮你落地", "使命不是想出来的，它会通过你反复使用的能力留下结果。", *channel_items),
        _section("mission-proof", "用 90 天验证方向", "不急着给一生定案，先看这条路会不会让你更有力、更成熟。", experiment),
    )


def _profile_item(chart: HumanDesignChart) -> InterpretationMapItem:
    summary = _summary(chart)
    code = chart.summary.profile.code
    lines = [int(value) for value in code.split("-") if value.isdigit()]
    line_text = tuple(f"{line}爻：{LINE_TALENTS.get(line, '通过自己的角色路径让能力成熟')}。" for line in lines)
    channel_names = tuple(_channel_name(channel) for channel in chart.channels[:2])
    if channel_names:
        full_chart_context = (
            f"在你身上，这条角色路径会先通过{'、'.join(channel_names)}这些稳定能力被看见；"
            f"是否把它用于眼前的人和事，仍由 {summary['authority_professional']} 确认。"
        )
    else:
        full_chart_context = (
            "在你身上，能力更依赖合适的人和环境来组合；人生角色决定你怎样学习和被看见，"
            f"具体投入仍由 {summary['authority_professional']} 确认。"
        )
    if code == "2-4":
        user = (
            "2/4 的天赋常有一个反常点：你本来已经能做到八十分，因为做起来太容易，反而最容易忽视。"
            "身边人越说你在某件事上有天赋，你越可能觉得“这有什么”，然后去学习别人擅长的东西。"
            "真正的成长不是再找一个新天赋，而是把这个天然八十分的能力放回独处中精进，再通过信任关系、作品和小范围验证推到一百分。"
            f"{full_chart_context}"
        )
        embodied = ("你允许天赋先在独处中熟成，不急着把半熟能力推到所有人面前；被正确的人看见后，再用作品和案例形成口碑。",)
        blind = ("把别人反复认可的能力当成“太普通”，把主要时间用来追赶别人已经擅长的事。",)
        stuck = ("学了很多、认识很多人，却没有一项能力被持续打磨到能代表你。",)
        causes = ("盘面机制：2爻会低估天然能力，4爻通过信任网络获得机会；现实场景：陌生市场的噪音很大时，你容易离开自己的强项去模仿热门能力。",)
        key = "talent.profile-24"
    else:
        guide = PROFILE_GUIDES.get(code, f"{summary['profile']}说明天赋怎样成熟、怎样被看见，也说明你需要怎样的学习和关系节奏。")
        user = (
            f"{guide} 具体到天赋发展，你需要走完两步：{_profile_maturation_path(code)}"
            f"{full_chart_context}"
        )
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
        followups=(f"结合我的其他特质，{summary['profile']}最可能让我忽视哪一种天赋？",),
    )


def _profile_maturation_path(code: str) -> str:
    lines = [int(value) for value in code.split("-") if value.isdigit()]
    if len(lines) != 2:
        return "按自己的角色节奏，在真实交付和关系反馈里把能力练稳。"
    first = LINE_TALENTS.get(lines[0], "先按自己的方式建立能力")
    second = LINE_TALENTS.get(lines[1], "再让真实关系和实践检验它")
    return f"{first}；接着{second}。"


def _talent_channel_item(chart: HumanDesignChart, channel) -> InterpretationMapItem:
    summary = _summary(chart)
    name = _channel_name(channel)
    expression = CHANNEL_LINES.get(channel.code, "这条线路会把两种资源合成一种可重复使用的能力")
    misuse = CHANNEL_MISUSES.get(channel.code, "在对象或时机不对时强行使用，会让天然能力变成证明和消耗。")
    return _item(
        key=f"talent.channel-{channel.code}",
        title=f"{name}：你可以反复调用的天赋",
        subtitle=f"和{summary['profile']}、{summary['authority_professional']}放在一起理解",
        basis=(f"已定义通道：{name}", f"人生角色：{summary['profile']}", f"Authority：{summary['authority_professional']}"),
        user=(
            f"{name}给你的稳定能力是：{expression}。"
            f"对{summary['profile']}来说，{name}不是一个等着你证明的标签，而是一项要经过真实关系、作品和反馈才会被认出的本领。"
            f"对于{name}，{summary['authority_professional']}只回答眼前这件事是否值得投入；它是否成熟，则要看你能否用这项能力反复解决同一类问题，同时没有把自己耗空。"
        ),
        scenes=(f"现实里留意：{expression}。再看这种动作最后帮助谁改变了什么。",),
        embodied=("活出来时，别人会因为一类明确的问题持续找到你；你也知道何时使用、何时停手。",),
        blind=(misuse,),
        stuck=(f"{name}被卡住时，不是能力消失，而是它只剩下天然反应，没有形成可重复、可说明的结果。",),
        causes=(f"盘面机制：{name}会稳定存在；现实场景：如果跳过{summary['strategy']}和 {summary['authority_professional']}，强项容易被用在错误对象上。",),
        practices=(CHANNEL_PRACTICES.get(channel.code, "回看三次这项能力自然出现的场景，写下触发条件、关键动作和结果，找出可重复部分。"),),
        followups=(f"结合我的其他特质，{name}最可能怎样被练成一项代表能力？",),
    )


def _wealth_channels_item(chart: HumanDesignChart, channels) -> InterpretationMapItem:
    summary = _summary(chart)
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
    if len(channels) == 1:
        title = f"{names[0]}怎样形成价值"
        user = (
            f"{names[0]}在财富上的价值，不是把通道名称拿去售卖，而是把这种能力用于一个结果清楚的问题："
            f"{CHANNEL_LINES.get(channels[0].code, '把两种资源接成稳定能力')}。"
            f"当{summary['profile']}让别人以合适方式认识你，并且 {summary['authority_professional']} 确认这份承诺值得投入，你才更容易把天然能力做成可定价的服务、职责或产品。"
        )
        followup = f"结合我的现实工作，{names[0]}最适合形成哪一种产品、服务或职责？"
    else:
        title = "02-14 等能力怎样共同形成价值" if has_0214 else "你的能力组合怎样形成价值"
        user = (
            f"你的{'、'.join(names)}可以进入同一项交付，但商业价值不来自通道数量，而来自它们最终解决了什么问题。"
            "先用真实案例排出过程：你最先看见什么、接着做了什么、最后替客户减少了什么代价或增加了什么结果；可重复的部分才有资格被定价。"
        )
        followup = "结合我的现实工作，这组能力最适合形成哪一种产品、服务或职责？"
    return _item(
        key=key,
        title=title,
        subtitle="把完整能力组合变成一项清楚、可重复、能定价的交付",
        basis=tuple(f"已定义通道：{name}" for name in names),
        user=user,
        scenes=tuple(value_lines),
        embodied=("客户能说清你解决了什么问题，你也能用相似步骤再次交付，而不是每次靠临场救火。",),
        blind=("天然能力常被免费用来帮忙；如果不记录过程和结果，别人只能觉得你人很好，却不知道该购买什么。",),
        stuck=("事情做了很多，口碑也不差，但每次都从零开始，收入无法随着经验积累而提高。",),
        causes=("盘面机制：稳定通道会重复出现，却不会自动变成产品；现实场景：只临时救场、不提炼共同问题，市场就看不见这套能力组合。",),
        practices=("选一次最有效的帮助，写清客户原来的问题、你的三个关键动作和最后结果，再用同一结构验证第二次。",),
        followups=(followup,),
    )


def _wealth_boundary_item(chart: HumanDesignChart) -> InterpretationMapItem:
    summary = _summary(chart)
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
    basis = tuple(f"开放中心：{_center_name(center.code)}" for center in open_centers)
    if not basis:
        basis = ("九个中心均已定义", f"Authority：{summary['authority_professional']}")
    cause = (
        "盘面机制：开放中心会放大证明、赶快和避免冲突的压力；现实场景：报价或合作谈判里，你可能先照顾对方感受，最后才计算自己的成本。"
        if open_centers
        else "盘面机制：九个中心都能稳定供能，但稳定不等于容量无限；现实场景：因为你确实能负责、能推进，合作方会持续把额外任务留给你。"
    )
    return _item(
        key="wealth.promise-boundary",
        title="什么最容易让你赚得多、剩得少",
        subtitle="财富损耗常发生在承诺时，而不是花钱时",
        basis=basis,
        user="保财首先是保护时间、注意力、交付边界和议价权。真正危险的不是一次消费，而是一个会持续吞噬资源的错误承诺。",
        scenes=tuple(risks),
        blind=("把客户满意等同于无限配合，把负责等同于所有问题都自己兜底。",),
        stuck=("收入看起来不低，但修改、沟通、救火和情绪劳动不断增加，实际时薪越来越低。",),
        causes=(cause,),
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


def _mission_channels_item(chart: HumanDesignChart, channels) -> InterpretationMapItem:
    summary = _summary(chart)
    names = tuple(_channel_name(channel) for channel in channels)
    expressions = tuple(
        f"{_channel_name(channel)}：{CHANNEL_LINES.get(channel.code, '这条能力线路会反复参与到你的长期贡献中')}。"
        for channel in channels
    )
    if len(channels) == 1:
        user = (
            f"{names[0]}不是你的使命本身，而是让「{summary['cross']}」落进现实的一条稳定能力线路。"
            f"它具体会带来：{CHANNEL_LINES.get(channels[0].code, '这条能力线路会反复参与到你的长期贡献中')}。"
            f"这项能力要通过{summary['profile']}的人生路径成熟，并由 {summary['authority_professional']} 判断眼前的人和事情是否值得投入。"
        )
        embodied = "当这条能力长期服务同一类真实问题时，使命会从抽象感觉变成别人能感受到的贡献。"
        blind = "把最强的一条能力直接等同于使命，结果不分对象地重复使用，主线反而只剩惯性。"
        practice = "从过去有效的项目里选一个真实问题，让这条能力连续服务 90 天；每两周记录一次具体结果和自己的生命力。"
    else:
        user = (
            f"你的{'、'.join(names)}是「{summary['cross']}」落地时可以反复使用的能力。"
            "这些能力不必各自发展成一份身份；先看它们在同一项贡献里实际承担了哪些步骤，再用结果判断哪条组合值得长期积累。"
        )
        embodied = "当这些能力长期服务同一类人和问题时，使命会从抽象感觉变成别人能感受到的真实贡献。"
        blind = "只追求使命主题听起来正确，却没有让能力持续服务现实；或者每项能力都另开一个方向，主线始终无法积累。"
        practice = "从过去有效的项目里选一个真实问题，让这些能力连续服务 90 天，不先扩大身份，只记录结果。"
    return _item(
        key="mission.channel-combination",
        title="使命靠哪些真实能力落地",
        subtitle="使命不是意义感，而是能力长期服务于同一类真实问题",
        basis=tuple(f"已定义通道：{name}" for name in names),
        user=user,
        scenes=expressions,
        embodied=(embodied,),
        blind=(blind,),
        stuck=("总在寻找更准确的身份说明，却很少把一项已经有效的贡献连续做完一个周期。",),
        practices=(practice,),
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


def _relationship_profile_guide(code: str) -> str:
    if code == "2-4":
        return "你既需要不被打扰的独处，也需要从信任网络中自然进入关系；越被催着社交或立刻靠近，越难分辨真实意愿。"
    lines = [int(value) for value in code.split("-") if value.isdigit()]
    if len(lines) == 2:
        return (
            f"你以{lines[0]}爻的学习方式进入亲密，也会在关系中呈现{lines[1]}爻的社会角色。"
            "适合你的关系需要允许这两种节奏同时存在。"
        )
    return "你需要按自己的人生角色节奏建立连接，而不是复制别人靠近和承诺的速度。"


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
    scene_values = tuple(scenes)
    embodied_values = tuple(embodied)
    blind_values = tuple(blind)
    stuck_values = tuple(stuck)
    cause_values = tuple(causes)
    practice_values = tuple(practices)
    diagnosis_depth = (
        "deep"
        if all((embodied_values, blind_values, stuck_values, cause_values))
        else "standard"
    )
    return InterpretationMapItem(
        key=key,
        title=title,
        subtitle=subtitle,
        diagnosis_depth=diagnosis_depth,
        chart_basis=tuple(basis),
        professional_basis="",
        user_language=user,
        life_scenes=scene_values,
        embodied_expression=embodied_values,
        blind_spots=blind_values,
        stuck_patterns=stuck_values,
        stuck_causes=cause_values,
        common_blocks=(),
        practices=practice_values,
        followup_questions=tuple(followups),
        source_atom_ids=(),
        sources=(),
    )
