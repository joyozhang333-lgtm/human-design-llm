"""无 API key 时的结构化精准回退。

只用 ChartFacts + 手写优质内容；每一段都针对这张盘的真实配置组合行文，
禁止任何可整句套给别人的填空句。质量标准 = PRD 里 2/4 天赋条的具体度。
顶部诚实声明由前端根据 generation_mode 决定是否展示，这里只负责内容。
"""
from __future__ import annotations

from dataclasses import dataclass

from ..body_energy import CENTER_ENERGY_GUIDES
from ..channel_guides import CHANNEL_LINES
from .facts import ChartFacts

# ---------------------------------------------------------------- L1：类型 × 权威 × 角色 合成一句人话

_TYPE_L1 = {
    "manifestor": "你是天生先开局的人——不等许可，先把事情从静止推到开始",
    "pure-generator": "你的生命力来自回应——对的事，会让身体先亮起来",
    "generator": "你的生命力来自回应——对的事，会让身体先亮起来",
    "manifesting-generator": "你既能回应又能快速多线推进——前提是身体先点头",
    "pure-manifesting-generator": "你既能回应又能快速多线推进——前提是身体先点头",
    "energy-projector": "你的天赋在看懂人和局——被真正看见时，你最省力也最准",
    "classic-projector": "你的天赋在看懂人和局——被真正看见时，你最省力也最准",
    "projector": "你的天赋在看懂人和局——被真正看见时，你最省力也最准",
    "mental-projector": "你的清晰来自对的环境和对话——不靠一个人关起门硬想",
    "reflector": "你像一面高灵敏度的镜子——环境对了，才照得清自己",
}

_AUTH_L1 = {
    "sacral": "做决定时，信身体当下的有劲没劲，别信头脑的应该",
    "solar-plexus": "做决定时，等情绪的浪过去，隔一晚再定才算数",
    "emotional": "做决定时，等情绪的浪过去，隔一晚再定才算数",
    "splenic": "做决定时，第一秒的直觉往往比反复分析更准",
    "ego": "做决定时，先问这是不是你真心想要的",
    "ego-manifested": "做决定时，先问这是不是你真心想要的",
    "ego-projected": "做决定时，先问这是不是你真心想要的",
    "self-projected": "做决定时，把话说出口，听自己声音里的真实答案",
    "mental": "做决定时，找对的人聊一聊，清晰会在对话里浮现",
    "outer-authority": "做决定时，找对的人聊一聊，清晰会在对话里浮现",
    "lunar": "做大决定前，给自己一个完整月相周期慢慢感受",
}

_PROFILE_HOOK = {
    "1-3": "先弄明白、再从试错里长出真本事",
    "1-4": "先打牢地基，再靠熟人网络带出去",
    "2-4": "先独处养熟，再被信任的人叫出来",
    "2-5": "天然会的东西藏不住，召唤自会找来",
    "3-5": "碰撞里练出的本事，会被人指望着用",
    "3-6": "撞出来的经验会沉成看得远的智慧",
    "4-6": "靠关系网络和过来人眼光展开人生",
    "4-1": "把一门根基之学放进你的关系网络里发光",
    "5-1": "打牢根基，接得住别人的指望",
    "5-2": "只接对得上你天然会的事的召唤",
    "6-2": "你的榜样感是时间养出来的",
    "6-3": "亲身试过错过，你的话才有分量",
}


def _type_key(code: str) -> str:
    return code if code in _TYPE_L1 else "pure-generator"


def _auth_key(code: str) -> str:
    return code if code in _AUTH_L1 else "sacral"


def build_l1(facts: ChartFacts) -> str:
    type_line = _TYPE_L1.get(facts.type_code) or _TYPE_L1["pure-generator"]
    auth_line = _AUTH_L1.get(facts.authority_code) or _AUTH_L1["sacral"]
    hook = _PROFILE_HOOK.get(facts.profile_code, "")
    if hook:
        return f"{type_line}。{auth_line}；{hook}。"
    return f"{type_line}。{auth_line}。"


# ---------------------------------------------------------------- L2 段落素材（全部手写、按码取用）

_TYPE_P1 = {
    "manifestor": "你的能量是脉冲式的：想做的冲动一来，推动力很强，但不是匀速持续的电池。所以「{strategy}」对你不是客套，而是给你扫清阻力——关键的人先知道你要动，就不会在半路拦你。",
    "pure-generator": "你的能量像一口需要被问话的井：外界端来具体的事，身体有回应，力气才源源不断。「{strategy}」的意思不是被动等待，而是别再用头脑硬开局——先让生活把选项端到面前，再用身体挑。",
    "generator": "你的能量像一口需要被问话的井：外界端来具体的事，身体有回应，力气才源源不断。「{strategy}」的意思不是被动等待，而是别再用头脑硬开局——先让生活把选项端到面前，再用身体挑。",
    "manifesting-generator": "你的能量既能回应又带加速器：一旦身体点头，你可以几条线一起推进、跳过不必要的步骤。「{strategy}」提醒你——快是你的天赋，但起点必须是真实回应，不然快只是提前抵达错误的地方。",
    "pure-manifesting-generator": "你的能量既能回应又带加速器：一旦身体点头，你可以几条线一起推进、跳过不必要的步骤。「{strategy}」提醒你——快是你的天赋，但起点必须是真实回应，不然快只是提前抵达错误的地方。",
    "energy-projector": "你不是持续输出型的电池，你是聚焦的透镜：看人、看局、看系统哪里堵住，是你不费力就做得好的事。「{strategy}」的意思是——你的洞见要被对的人请出来才值钱，硬塞给没准备好的人，只会换来敷衍。",
    "classic-projector": "你不是持续输出型的电池，你是聚焦的透镜：看人、看局、看系统哪里堵住，是你不费力就做得好的事。「{strategy}」的意思是——你的洞见要被对的人请出来才值钱，硬塞给没准备好的人，只会换来敷衍。",
    "projector": "你不是持续输出型的电池，你是聚焦的透镜：看人、看局、看系统哪里堵住，是你不费力就做得好的事。「{strategy}」的意思是——你的洞见要被对的人请出来才值钱，硬塞给没准备好的人，只会换来敷衍。",
    "mental-projector": "你的清晰不在脑子里憋出来，而在对的空间和对话里浮出来。换个环境、换个人聊，同一个问题会呈现完全不同的答案。「{strategy}」提醒你：先挑场域和对话对象，再谈决定。",
    "reflector": "你的能量每天都在跟着环境和月相变，这不是不稳定，而是灵敏。你比任何人都清楚一个团队、一个家此刻的真实状态。「{strategy}」的意思是：别用一时的感受定终身的事。",
}

_AUTH_P2 = {
    "sacral": "做决定时，你身体的「有劲/没劲」比任何分析都诚实。有回应的事，越做越进入状态；没回应的事，答应了也会用拖延和疲惫来提醒你。练法很朴素：把大问题拆成能用「嗯/不嗯」回答的小问题，先从吃饭、见人、接活这种小事练起。",
    "solar-plexus": "你的真实答案藏在情绪波的后面。浪头上的「太好了」和谷底的「算了吧」都不算数，过了浪之后还留在心里的那个倾向才算。所以给自己立一条规矩：重要的事，隔一晚再答复。着急要答案的人和事，先让它等一等。",
    "emotional": "你的真实答案藏在情绪波的后面。浪头上的「太好了」和谷底的「算了吧」都不算数，过了浪之后还留在心里的那个倾向才算。所以给自己立一条规矩：重要的事，隔一晚再答复。着急要答案的人和事，先让它等一等。",
    "splenic": "你的答案来得很快、声音很轻：第一秒身体是放松还是收紧，就是判断。它不重复、不解释，最容易被后来的分析盖掉。练法是先记录再行动——每次第一反应出现时写下来，过几天回看它准不准，你会慢慢敢信它。",
    "ego": "你的答案在「我是不是真心想要」里。别人觉得该做、看起来划算的事，如果你心里没有那股「我愿意为它押上力气」的劲，做起来只会掏空你。答应任何事之前先问：这是我要的，还是我在证明自己值得？",
    "ego-manifested": "你的答案在「我是不是真心想要」里。别人觉得该做、看起来划算的事，如果你心里没有那股「我愿意为它押上力气」的劲，做起来只会掏空你。答应任何事之前先问：这是我要的，还是我在证明自己值得？",
    "ego-projected": "你的答案在「我是不是真心想要」里。别人觉得该做、看起来划算的事，如果你心里没有那股「我愿意为它押上力气」的劲，做起来只会掏空你。答应任何事之前先问：这是我要的，还是我在证明自己值得？",
    "self-projected": "你的答案在自己的声音里。想不清的事，找一个不给建议、只安静听的人，把它讲出来——讲着讲着你会听见自己哪句话是真的、哪句是应付。写下来再读出声，也是同样的原理。",
    "mental": "你没有固定的身体信号做锚，你的清晰来自环境和对话的回声。同一个问题，在不同的空间、跟不同的人聊，会照出不同的面。所以别逼自己独自定案——多聊几轮，注意哪个说法让你整个人松下来。",
    "outer-authority": "你没有固定的身体信号做锚，你的清晰来自环境和对话的回声。同一个问题，在不同的空间、跟不同的人聊，会照出不同的面。所以别逼自己独自定案——多聊几轮，注意哪个说法让你整个人松下来。",
    "lunar": "你的决定需要时间当容器：一个完整的月相周期里，你会在不同的日子对同一件事有完全不同的感受，这些感受都作数，都要收集。大事别当场答应，把「我需要一个月」说出口，这不是拖延，是你的做决定方式。",
}

_PROFILE_P3 = {
    "1-3": "你的人生角色是 1/3：先钻研到心里有底，再亲自下场试错。你以为的「失败」大多是你的研究方法——撞过的墙会变成你最扎实的判断力。别急着在没弄明白前表态，也别把试错当成自己不行。",
    "1-4": "你的人生角色是 1/4：地基型的研究者，加上靠关系网络展开的人生。你需要先把一门东西钻透，机会才会从认识你、信任你的人那里来。所以别海投陌生场子，把根基修好，让熟人网络知道你在做什么。",
    "2-4": "你的人生角色是 2/4：你有些能力是天生顺手的，顺手到你自己都不当回事，别人却一眼看见。这些能力需要先在不被打扰的独处里养熟，再由真正认识你的人把你叫出来。所以独处不是逃避，是你的工作方式；而信任关系就是你的机会入口。",
    "2-5": "你的人生角色是 2/5：你天然会的东西藏不住，别人还会把「救场」的期待投到你身上。分辨哪些召唤对得上你真实的天赋、哪些只是别人的投射，是你一生的功课。对不上的期待，越早说清楚越省力。",
    "3-5": "你的人生角色是 3/5：你的本事是在真实碰撞里练出来的，而别人也确实会指望你能解决问题。试错在你身上不是弯路，是采样。只是要留意：别人失望的时候，未必是你的错，可能是他们投射错了地方。",
    "3-6": "你的人生角色是 3/6：前半生像在做实验，什么都要亲自撞一遍；三十岁后你会自然往后退一步，把撞出来的经验酿成看得远的判断。两个阶段都是对的，别用后来的眼光否定早年的莽撞。",
    "4-6": "你的人生角色是 4/6：你的机会长在关系网络里，你的公信力长在时间里。前半生积累经验、经营真实的友谊，后半生你的话会越来越有分量。经营关系对你不是社交技巧，是命脉。",
    "4-1": "你的人生角色是 4/1：一门扎实的根基之学，放进温热的关系网络里，就是你的人生配方。你的路比别人窄一点、也直一点——认准了就深耕，靠信任你的人传出去，不必羡慕会变通的人。",
    "5-1": "你的人生角色是 5/1：别人天然觉得你能救场、能给方案，这是投射，也确实是机会。接住它的方式是把根基打牢——研究透了再出手，你就配得上那份期待；根基虚的时候硬接，投射会反过来砸你。",
    "5-2": "你的人生角色是 5/2：外面的人指望你，你自己却常常只想安静做自己的事。这个拉扯是真实的。原则是：只答应那些和你天然会的事对得上的召唤，其余的期待温和地退回去。",
    "6-2": "你的人生角色是 6/2：你身上有天然的示范感，别人会观察你怎么活。前半生尽管下场试，三十岁后你会更想退到半山腰看全局——这不是消极，是你的智慧在成形。保护好独处，它是你的养分。",
    "6-3": "你的人生角色是 6/3：一边要成为看得远的榜样，一边又忍不住亲自下场再撞一次。你的公信力恰恰来自这些撞过的痕迹——你讲的不是理论，是亲历。允许自己反复，它不妨碍你成为别人的参照。",
}

_DEFINITION_P3 = {
    "single": "你的内在能量是连成一片的：想清楚的事自己就能消化闭环，不太依赖别人帮你接通。这让你独立，但也提醒你——不是所有人都像你这样快，给别人一点接上的时间。",
    "simple-split": "你的内在能量分成两块，中间那道缝需要对的人和环境来搭桥。所以你对某些人会有「跟他在一起我就完整了」的感觉——那是配置，不是宿命。留意：借来的桥是体验，不必抓成依赖。",
    "split": "你的内在能量分成两块，中间那道缝需要对的人和环境来搭桥。所以你对某些人会有「跟他在一起我就完整了」的感觉——那是配置，不是宿命。留意：借来的桥是体验，不必抓成依赖。",
    "wide-split": "你的内在能量分成两大块，缝隙较宽，需要环境和关系来接通。你天然会被能补全你的人吸引，这没问题——只要记得，接通的感觉是加分项，不是你做决定的理由。",
    "triple-split": "你的内在能量分成三块，需要流动的场域和不同的人来轮流接通。所以你不适合长期只泡在一个小圈子里——多走动、多接触不同的场，你才会觉得自己是完整的。",
    "quadruple-split": "你的内在能量分成四块，几乎注定要在丰富的人群里被接通。独处太久你会觉得自己散着；进入合适的场域，那些部分才咔哒咬合。给生活保留足够的流动性。",
    "no": "你的九个中心都开放，没有固定的内在定义——你不是「没有自己」，而是把环境喝进来再照出去。挑对环境，等于挑对了你自己会成为的样子。",
}

# 签名/非自己按类型家族取（对照式一段）
_SIGNATURE_P4 = {
    "satisfaction": "顺的时候，你的身体会给你「满足」的信号：一天结束虽然累，但是那种用对了力气的踏实。拧的时候，最先冒出来的是挫败感——忙了很多却越来越烦。把挫败当仪表盘：它不是说你不行，是说这件事可能不是你的回应，回头看看是不是头脑替身体做了决定。",
    "success": "顺的时候，你会尝到「成功」的味道：你的洞见被采纳、被感谢，事情因为你省了很多力。拧的时候，冒出来的是苦涩——一种「我看得这么清楚却没人听」的憋闷。苦涩出现时先别加倍证明自己，退一步问：这里的人真的邀请过我吗？",
    "peace": "顺的时候，你内在是「平和」的：想做的事发起了，该通知的人通知了，世界让开一条道。拧的时候，涌上来的是愤怒——被拦、被管、被要求汇报的火气。愤怒是信号，不是罪：它常常在提醒你，要么忘了先告知，要么在不属于你的节奏里硬挤。",
    "surprise": "顺的时候，生活会持续给你「惊喜」——你没规划的好事一件件冒出来。拧的时候，弥漫的是失望：对人、对场域、对自己的钝钝的失落。失望累积时，先别怀疑自己，先检查环境：你多久没待在让你舒服的地方了？",
}

_NO_CHANNEL_P1_EXTRA = "你的图里没有固定接通的通道，这意味着你的很多能力是流动的、跟着场域被点亮的——挑对环境和合作对象，比强求稳定输出更重要。"


def _channel_sentence(facts: ChartFacts) -> str:
    for code in facts.channel_codes:
        line = CHANNEL_LINES.get(code)
        if line:
            name = next(
                (label for label in facts.channels_cn if label.startswith(code)),
                code,
            )
            return f"你图里的 {name} 是条已经接通的线路：{line}。"
    return ""


def _open_center_sentence(facts: ChartFacts) -> str:
    for code in facts.open_center_codes:
        guide = CENTER_ENERGY_GUIDES.get(code)
        if guide:
            label = _center_cn(facts, code)
            return f"同时留意你开放的{label}：{guide['open_body']}觉察到了，就先退半步再回应。"
    return ""


def _center_cn(facts: ChartFacts, code: str) -> str:
    from ..labels import CENTER_LABELS, normalize_center_title

    return normalize_center_title(CENTER_LABELS.get(code, code))


def build_l2(facts: ChartFacts) -> str:
    type_para = _TYPE_P1.get(facts.type_code, _TYPE_P1["pure-generator"]).format(strategy=facts.strategy_cn)
    channel_line = _channel_sentence(facts)
    if channel_line:
        p1 = f"{type_para}{channel_line}"
    else:
        p1 = f"{type_para}{_NO_CHANNEL_P1_EXTRA}"

    auth_para = _AUTH_P2.get(facts.authority_code, _AUTH_P2["sacral"])
    open_line = _open_center_sentence(facts)
    p2 = f"{auth_para}{open_line}"

    profile_para = _PROFILE_P3.get(facts.profile_code, "")
    definition_para = _DEFINITION_P3.get(facts.definition_code, "")
    p3 = f"{profile_para}{definition_para}".strip()

    p4 = _SIGNATURE_P4.get(facts.signature_code, _SIGNATURE_P4["satisfaction"])
    closing = "图只是个起点。真正的答案不在图里，在你接下来怎么观察自己。"

    paragraphs = [p for p in (p1, p2, p3, f"{p4}{closing}") if p]
    return "\n\n".join(paragraphs)


MAP_TITLES = {
    "body": "身体与能量",
    "channels": "稳定能力线路",
    "wealth": "财富与工作",
    "talent": "天赋与角色路径",
    "relationship": "关系与边界",
    "mission": "人生主轴与使命",
    "professional": "个人人类图简要",
}


def build_map_body(facts: ChartFacts, map_type: str) -> str:
    """无模型时仍给出完整、全盘联动的地图解读，不留空白也不显示机器指令。"""
    if map_type not in MAP_TITLES:
        raise KeyError(map_type)

    type_para = _TYPE_P1.get(facts.type_code, _TYPE_P1["pure-generator"]).format(strategy=facts.strategy_cn)
    auth_para = _AUTH_P2.get(facts.authority_code, _AUTH_P2["sacral"])
    profile_para = _PROFILE_P3.get(
        facts.profile_code,
        f"你的人生角色是{facts.profile_cn}。这两条爻线要放在真实关系、工作节奏和长期实践里一起观察。",
    )
    definition_para = _DEFINITION_P3.get(facts.definition_code, f"你的定义方式是{facts.definition_cn}。")
    channels = _map_channel_text(facts)
    gates = _map_gate_text(facts)
    defined = "、".join(facts.defined_centers_cn) or "没有固定定义的中心"
    open_centers = "、".join(facts.open_centers_cn) or "开放中心较少"

    if map_type == "body":
        paragraphs = (
            type_para,
            auth_para,
            f"你的稳定身体资源主要来自{defined}。这里更像你可以反复使用的底盘；{channels}",
            f"你开放的部分包括{open_centers}。开放不等于缺失，而是更容易放大环境和他人的状态。累、急、想证明或突然失去方向时，先离开现场一会儿，再按{facts.authority_cn}重新听一次答案。",
        )
    elif map_type == "channels":
        paragraphs = (
            f"通道不是技能证书，而是你更容易反复调用的能力线路。你的实际盘面显示：{channels}",
            f"这些能力要放回{facts.profile_cn}的人生路径里看。{profile_para} 同一条通道，在合适的人、问题和节奏里会形成可信赖的贡献；为了证明自己而强行启动时，常常只剩下用力。",
            f"做决定时仍以{facts.authority_cn}为准。{auth_para} 通道说明你能怎样运作，却不能替你判断眼前这个合作、关系或方向是否适合。",
            f"先选一条已经在现实里反复被看见的线路，用作品、案例或一次具体沟通验证它。做完若更接近{facts.signature_cn}，说明这条能力正在成熟；若长期只剩{facts.not_self_cn}，就检查场域、承诺和启动时机。",
        )
    elif map_type == "wealth":
        paragraphs = (
            f"人类图不能替你预测收入数字，但能看出你怎样工作更不容易透支。{type_para}",
            f"真正涉及报价、合作和长期投入时，要回到{facts.authority_cn}。{auth_para}",
            f"你的可变现能力要从真实线路里找：{channels} 财富更可能来自把这些能力反复做成作品、方法、服务和信任，而不是追逐与你无关的热门方向。",
            f"你的人生角色是{facts.profile_cn}。{profile_para} 对你来说，保财不只是少花钱，更重要的是少接没有身体答案的承诺，把时间和注意力留给能积累复利的主线。",
        )
    elif map_type == "talent":
        paragraphs = (
            profile_para,
            f"你的天赋不能只从爻线判断，还要看已经接通的能力线路。{channels}",
            f"关键闸门给出更细的着力点：{gates} 不必把每一项都发展成职业，先找那件别人反复认可、你却觉得太容易的事。",
            f"活出天赋，不是继续收集别人擅长的能力，而是把自己已经有80分基础的那一项，通过练习、案例、反馈和长期交付推到100分。做对时会更接近{facts.signature_cn}；若长期只有{facts.not_self_cn}，就要检查是不是在错误场域证明自己。",
        )
    elif map_type == "relationship":
        paragraphs = (
            f"你进入关系的方式要先服从{facts.strategy_cn}，做关系决定则要服从{facts.authority_cn}。不是感情越强烈就越正确，而是关系里你是否还能听见自己的身体答案。",
            profile_para,
            f"{definition_para} 这会影响你和谁在一起时感觉顺、什么时候需要流动或独处，但任何“被补全”的感觉都不能代替你的权威做决定。",
            f"关系里最容易被带走的入口在开放中心：{open_centers}。适合你的关系会让这些部分慢慢放松，也会尊重{channels}所代表的稳定表达，而不是逼你长期扮演不属于自己的角色。",
        )
    elif map_type == "mission":
        paragraphs = (
            f"你的人生主轴叫做{facts.cross_cn}。它不是一句命定口号，而是你会反复遇到、反复练习，并逐渐形成贡献的生命主题。",
            f"使命的入口仍然是{facts.strategy_cn}，决定方式仍然是{facts.authority_cn}。跳过这两步去追求宏大使命，往往只会先活出{facts.not_self_cn}。",
            f"你以{facts.profile_cn}的方式走这条路。{profile_para} 因此使命不是别人替你宣布的身份，而是你的角色路径和真实经历慢慢沉淀出的可信度。",
            f"你的使命需要借由真实能力落地：{channels} 当这些能力被持续用在正确的人和问题上，你会更接近{facts.signature_cn}。先用90天验证一条有身体回应的主线，不必急着给整个人生定案。",
        )
    else:
        paragraphs = (
            f"你的类型是{facts.type_cn}，更顺的行动策略是{facts.strategy_cn}，做决定时以{facts.authority_cn}为准。",
            profile_para,
            f"你的定义方式是{facts.definition_cn}。稳定中心包括{defined}，开放中心包括{open_centers}。",
            f"已接通的能力线路是：{channels} 人生主轴是{facts.cross_cn}。这些配置应当一起观察，而不是把任何一个术语当成对你的最终定义。",
        )
    return "\n\n".join(paragraph for paragraph in paragraphs if paragraph.strip())


def _map_channel_text(facts: ChartFacts) -> str:
    if not facts.channel_codes:
        return "你的图里没有固定接通的通道，能力更容易被环境和合作对象点亮，所以选场域比逼自己稳定输出更重要。"
    lines = []
    for code in facts.channel_codes[:4]:
        label = next((item for item in facts.channels_cn if item.startswith(code)), code)
        explanation = CHANNEL_LINES.get(code, "这是一条你可以稳定调用的能力线路")
        lines.append(f"{label}：{explanation}")
    return "；".join(lines) + "。"


def _map_gate_text(facts: ChartFacts) -> str:
    if not facts.top_gates:
        return "先从类型、权威和通道观察，不必强行放大单个闸门。"
    return "、".join(f"{gate.gate}号「{gate.theme_cn}」" for gate in facts.top_gates[:6]) + "。"


# ---------------------------------------------------------------- 想看更细（L3 结构化目录与正文）


@dataclass(frozen=True)
class DetailSection:
    key: str
    title: str
    summary: str


DETAIL_SECTIONS: tuple[DetailSection, ...] = (
    DetailSection("centers", "九大中心", "哪些中心稳定发力、哪些容易被外界放大，逐个看。"),
    DetailSection("channels", "通道", "你身体里已经接通的固定线路，逐条看它怎么用。"),
    DetailSection("variables", "运作方式微调", "吃饭、环境、动力、视角的小倾向——看看就好，不必当规定。"),
    DetailSection("cross", "轮回交叉与人生使命", "你反复会遇到、也会反复贡献出去的人生主题。"),
)

EXPLORE_ENTRIES: tuple[tuple[str, str, str], ...] = (
    ("talent", "天赋报告", "逐条看稳定天赋，以及怎样从八十分练到一百分。"),
    ("mission", "使命报告", "讲清使命名称、落地能力和九十天验证方式。"),
    ("body", "身体报告", "身体怎样决定、压力从哪里进入、怎样恢复。"),
    ("wealth", "财富报告", "钱怎样进入、能力怎样变现、承诺怎样设边界。"),
    ("relationship", "关系报告", "连接方式、情绪边界和适合你的相处条件。"),
    ("professional", "专业信息", "核对类型、Strategy、Authority、中心和通道。"),
)


def build_detail_body(facts: ChartFacts, key: str) -> str:
    if key == "centers":
        lines = []
        for code in facts.defined_center_codes:
            guide = CENTER_ENERGY_GUIDES.get(code)
            if guide:
                lines.append(f"{_center_cn(facts, code)}（已定义）：{guide['body']}")
        for code in facts.open_center_codes:
            guide = CENTER_ENERGY_GUIDES.get(code)
            if guide:
                lines.append(f"{_center_cn(facts, code)}（开放）：{guide['open_body']}练习：{guide['practice']}")
        return "\n\n".join(lines)
    if key == "channels":
        if not facts.channel_codes:
            return "你的图里没有固定接通的通道。这不是缺了什么，而是你的能力更依赖场域被点亮——挑对环境，比强求稳定输出更重要。"
        lines = []
        for code, label in zip(facts.channel_codes, facts.channels_cn, strict=False):
            line = CHANNEL_LINES.get(code, "这是你身体里稳定重复出现的能量路径，观察它在哪些场景自然启动。")
            lines.append(f"{label}：{line}。")
        return "\n\n".join(lines)
    if key == "gates":
        lines = []
        for gate in facts.all_gates:
            if gate.sentence:
                lines.append(f"{gate.gate} 号闸门·{gate.theme_cn}（位于{gate.center_cn}）：{gate.sentence}")
            else:
                lines.append(f"{gate.gate} 号闸门·{gate.theme_cn}（位于{gate.center_cn}）")
        return "\n".join(lines)
    if key == "variables":
        intro = "这些是你运作方式的小倾向，看看就好，不必当规定："
        return intro + "\n\n" + "\n".join(f"· {line}" for line in facts.variables_cn)
    if key == "cross":
        return (
            f"你的人生主轴是「{facts.cross_cn}」。"
            "它不是职业名称，而是你一生反复会遇到、也会反复贡献出去的主题。"
            "可以观察一下：过去几年让你最有生命力的事，是不是都绕着这个主题转。"
        )
    raise KeyError(f"未知的细读键：{key}")


def detail_title(key: str) -> str:
    for section in DETAIL_SECTIONS:
        if section.key == key:
            return section.title
    # Keep the endpoint backwards compatible without listing the gate catalogue
    # in the user-facing result page.
    if key == "gates":
        return "完整闸门清单"
    raise KeyError(f"未知的细读键：{key}")
