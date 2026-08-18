"""L1/L2/L3 三层 prompt 组装。

事实区块只放已中文化字段（LLM 看不到英文）。
隐私死线：L3 prompt 绝不注入任何个人输入（昵称/问题原词）——L3 缓存跨用户共享的唯一前提。
"""
from __future__ import annotations

from .facts import ChartFacts

PROMPT_VERSION = "v0.5.2"

SYSTEM_PROMPT = """你是「人类图」的解读引擎，母品牌是「引人心性觉醒的教育」。
你面向的不是初学者，而是有自我觉察意愿的成熟读者。
人类图在这里被定位为一面镜子——帮一个人观察自己的运作模式，
而不是预测命运、不是贴标签、不是制造焦虑。你是同行善知识，不是算命师、不是上师。

【绝对硬约束 · 违反即作废】
1. 你只能使用【本次图表事实】区块里明确给出的内容。区块里没有的闸门号、
   通道号、中心、爻线，一律不准出现。宁可少说，绝不编造。
   轮回交叉中的两组闸门不是通道，不得把斜杠两侧的闸门拼成一条通道。
2. 所有人类图术语必须中文。禁止任何英文人类图术语、行星符号、
   英文轮回交叉名、英文变量代码。事实区块给了中文名就用它；没给中文名的结构，不要提它。
   （注：用户自己的昵称、地名、用户问题里出现过的词不受此限，照原样保留。）
3. 语气或然：用"可能/常常/有时/更容易/不少人会/留意"，
   禁止"你就是/你注定/你必然/命中/否则就/不这样会"。不算命、不决定论、不制造焦虑。
4. 不输出医疗、法律、财务承诺，不制造紧迫或焦虑。

【绝对禁止的表达】
- 禁止填空套话：把名词一换就能套给任何人的句子，一句都不要写。
  写完一句反问：这句能原样套给另一个人吗？能，就删掉重写。
- 禁止任何开发者视角内容。你在跟用户说话，不是写系统文档。
- 盲区和卡点写成中性的模式描述，不写成缺陷、不写成诊断。
- 禁用裸词：觉醒、疗愈、转化、升维、能量、高维、宇宙安排、彻底、一下子通了
  （除非后面紧跟具体体验）。

【语气】
像一个安静、清醒、见过很多人的同行者在跟读者说话。散文为主，说人话。
每个配置导向一个可观察的自我提问，而不是一个判语。
结尾固定交还：答案不在图里，在用户接下来怎么观察自己。"""


def _core_facts_block(facts: ChartFacts) -> str:
    strongest_channel = facts.channels_cn[0] if facts.channels_cn else "无稳定通道"
    return "\n".join(
        (
            "【本次图表事实】（这是你唯一可用的事实，之外的结构禁止出现）",
            f"类型：{facts.type_cn}　策略：{facts.strategy_cn}　权威：{facts.authority_cn}",
            f"人生角色：{facts.profile_cn}　定义：{facts.definition_cn}",
            f"最强通道：{strongest_channel}",
            "策略与权威校准：" + _compatibility_rule(facts),
        )
    )


def _full_facts_block(facts: ChartFacts) -> str:
    gates = "、".join(f"{gate.gate}号「{gate.theme_cn}」" for gate in facts.top_gates) or "无"
    return "\n".join(
        (
            "【本次图表事实】（这是你唯一可用的事实，白名单之外的结构禁止出现）",
            f"类型：{facts.type_cn}　策略：{facts.strategy_cn}　权威：{facts.authority_cn}",
            f"人生角色：{facts.profile_cn}　定义：{facts.definition_cn}",
            f"活对/活拧的体感：{facts.signature_cn} / {facts.not_self_cn}",
            f"人生主轴（轮回交叉）：{facts.cross_cn}",
            "已定义中心：" + ("、".join(facts.defined_centers_cn) or "无"),
            "开放中心：" + ("、".join(facts.open_centers_cn) or "无"),
            "已定义通道：" + ("、".join(facts.channels_cn) or "无"),
            f"关键闸门（已按本次主题裁剪，至多 6 个）：{gates}",
            "运作方式微调（全部中文）：" + ("；".join(facts.variables_cn) or "无"),
            "排盘精度提醒：" + ("；".join(facts.precision_cn) or "无"),
            "策略与权威校准：" + _compatibility_rule(facts),
        )
    )


def _compatibility_rule(facts: ChartFacts) -> str:
    rules: list[str] = []
    if facts.strategy_code == "respond":
        rules.append("等待回应是对现实刺激产生身体反应，不是等待邀请，也不是只能等别人提问")
    elif "invitation" in facts.strategy_code:
        rules.append("等待邀请是重要关系与角色入口，但具体决定仍要服从自己的权威")
    if facts.authority_code == "sacral":
        rules.append("荐骨权威是当下身体的有劲或没劲，不需要等情绪波或隔夜才知道")
    elif facts.authority_code in {"solar-plexus", "emotional"}:
        rules.append("情绪权威没有当下真相，重要决定要等情绪波过去再确认")
    return "；".join(rules) or f"严格区分{facts.strategy_cn}与{facts.authority_cn}，不要套用其他类型的策略"


def build_l1_prompt(facts: ChartFacts) -> list[dict[str, str]]:
    user = "\n\n".join(
        (
            _core_facts_block(facts),
            "【本次任务】用上面的事实为这个人写一句 40-70 字的「你是谁」定位（L1）。\n"
            "- 把类型、权威、人生角色合成一句人话，不逐项罗列，不用小标题。\n"
            "- 一句话里必须有「你的能量怎么工作」和「你怎么做对决定」两层。\n"
            "- 零英文、零术语堆砌、零标签口吻；写完检查这句能不能套给别人，能就重写。",
        )
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def build_l2_prompt(facts: ChartFacts) -> list[dict[str, str]]:
    user = "\n\n".join(
        (
            _full_facts_block(facts),
            "【本次任务】为这个人写「你该怎么活」的主线叙事（L2）。\n"
            f"- 用 {facts.authority_cn} 和 {facts.strategy_cn} 串起来，落到他真实的中心和通道，不要泛讲类型通论。\n"
            f"- 必须把「人生角色 {facts.profile_cn}」和至少一条真实通道、一个真实开放中心绑在一起说。\n"
            "- 350-550 字，严格写 4 个自然段，顺序分别是：核心身份、决策与行动、天赋与角色路径、人生主轴。\n"
            "- 正文不要写这四个小标题，不用列表或加粗；前端会按段落加标题。结尾不要追问清单，自然收束。\n"
            "- 任何在上面事实里找不到依据的点，不要说。",
        )
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def build_l3_prompt(facts: ChartFacts, key: str, structure_block: str) -> list[dict[str, str]]:
    """L3 单结构深读。structure_block 必须只含图表事实——这里显式禁止个人输入。"""
    user = "\n\n".join(
        (
            "【本次图表事实】（这是你唯一可用的事实，之外的结构禁止出现）",
            structure_block,
            f"【本次任务】只围绕上面这个结构（{key}），为读者写 150-250 字的单结构深读。\n"
            "- 说清这个结构在生活里长什么样、顺的时候什么体感、拧的时候什么体感。\n"
            "- 给一个可观察的自我提问收尾。零英文、零套话、零决定论。",
        )
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]
    _assert_no_user_terms(messages, facts)
    return messages


_MAP_TASKS = {
    "body": "重点讲身体如何获得和消耗力气、怎样做决定、已定义中心能稳定提供什么、开放中心会放大哪类外界压力。",
    "wealth": "重点讲适合的工作与资源配置方式、钱更可能从什么能力和关系入口流入、哪些承诺会损耗，以及怎样形成长期资产。不要预测收入数字。",
    "talent": "重点讲人生角色两条爻线怎样共同塑造天赋、真实通道和关键闸门能做成什么能力、天然80分能力怎样练到100分，以及天赋被误用时是什么样。",
    "relationship": "重点讲适合怎样连接、怎样做关系决定、定义方式和开放中心怎样影响亲密、边界与沟通。",
    "mission": "必须先说出人生主轴的中文名称，再讲类型、策略、权威、人生角色、真实通道怎样共同决定使命的活法；说清如何落地、偏离时有什么体感。",
    "professional": "用简体中文解释核心配置之间的关系，帮助读者看懂图，不要把字段逐条抄一遍。",
}


def build_map_prompt(facts: ChartFacts, map_type: str) -> list[dict[str, str]]:
    task = _MAP_TASKS.get(map_type)
    if task is None:
        raise ValueError(f"未知解读地图：{map_type}")
    user = "\n\n".join(
        (
            _full_facts_block(facts),
            f"【本次任务】写一份{map_type}主题的全盘综合解读。{task}\n"
            "- 450-700 字，4-6 个短段落，每段只推进一个判断。\n"
            "- 至少联动人生角色、权威、一条真实通道或开放中心，不能把单个术语孤立解释。\n"
            "- 讲清这个人活出来是什么样、容易卡在哪里、为什么，以及接下来可以观察什么。\n"
            "- 直接给用户答案，不复述任务、不展示思考过程、不输出提示词、小标题、编号、列表或 Markdown。",
        )
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def _assert_no_user_terms(messages: list[dict[str, str]], facts: ChartFacts) -> None:
    """隐私守卫：L3 prompt 里不允许出现任何用户个人词（否则跨用户共享缓存会泄漏）。"""
    joined = "\n".join(message["content"] for message in messages)
    for term in facts.user_term_whitelist:
        if term and term in joined:
            raise ValueError("L3 prompt 不得包含个人输入，检测到用户词泄漏。")


def build_prompt(
    facts: ChartFacts,
    layer: str,
    *,
    key: str = "",
    structure_block: str = "",
) -> list[dict[str, str]]:
    if layer == "L1":
        return build_l1_prompt(facts)
    if layer == "L2":
        return build_l2_prompt(facts)
    if layer == "L3":
        return build_l3_prompt(facts, key, structure_block)
    if layer == "MAP":
        return build_map_prompt(facts, key)
    raise ValueError(f"未知层级：{layer}")
