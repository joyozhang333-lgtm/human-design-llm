from __future__ import annotations

from dataclasses import asdict, dataclass

from .labels import (
    CENTER_LABELS,
    display_authority,
    display_strategy,
    display_type,
    normalize_center_title,
)
from .schema import HumanDesignChart


@dataclass(frozen=True)
class CenterEnergyNote:
    code: str
    label: str
    defined: bool
    state_label: str
    body_resource: str
    spiritual_resource: str
    consumption_pattern: str
    practice: str
    observation_prompt: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ChannelEnergyNote:
    code: str
    label: str
    centers: tuple[str, str]
    body_flow: str
    expression: str
    practice: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class GateEnergyNote:
    gate: int
    center: str
    theme: str
    activations: tuple[str, ...]
    prompt: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class BodyEnergyProfile:
    headline: str
    summary: str
    defined_centers: tuple[str, ...]
    open_centers: tuple[str, ...]
    center_notes: tuple[CenterEnergyNote, ...]
    channel_notes: tuple[ChannelEnergyNote, ...]
    gate_notes: tuple[GateEnergyNote, ...]
    energy_management: tuple[str, ...]
    suggested_questions: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


CENTER_ENERGY_GUIDES: dict[str, dict[str, str]] = {
    "head": {
        "body": "稳定接收灵感压力，适合把问题先放在系统里沉淀，而不是立刻逼自己回答。",
        "spiritual": "这里像天线，帮助你感知更高层的疑问、启示和未完成主题。",
        "open_body": "容易放大外界问题与焦虑，身体会误以为所有问题都需要你马上解决。",
        "open_spiritual": "开放时更适合做灵感筛选器：哪些问题真正属于你，哪些只是场域噪音。",
        "consumption": "卡点常表现为头脑过热、追逐答案、为了结束不确定感而提前下结论。",
        "practice": "每天只保留 1 个真正值得追的核心问题，其余问题先写下，不用马上处理。",
        "prompt": "我现在想解决的问题，是身体真的有回应，还是只是想摆脱头脑压力？",
    },
    "ajna": {
        "body": "稳定组织概念、模型和判断，适合把复杂体验整理成可表达的语言。",
        "spiritual": "这里让灵感形成认知结构，帮助你把看不见的东西讲清楚。",
        "open_body": "容易替别人证明观点，也容易为了显得确定而固定立场。",
        "open_spiritual": "开放时更像观念流动场，适合吸收多种视角但不急着认同任何一种。",
        "consumption": "卡点常表现为过度解释、反复论证、害怕别人觉得你不够确定。",
        "practice": "允许自己说“我还在观察”，把确定性留给身体权威而不是头脑表演。",
        "prompt": "这个观点让我更清晰，还是只是让我看起来更聪明、更确定？",
    },
    "throat": {
        "body": "稳定把能量带到表达、行动和可见成果，适合让正确时机推动声音出来。",
        "spiritual": "这里是显化出口，决定内在能量如何被世界听见、看见、接住。",
        "open_body": "容易受场域影响突然想说、想证明、想被看见。",
        "open_spiritual": "开放时能承接多种表达频率，但需要等待对位的邀请、回应或时机。",
        "consumption": "卡点常表现为为了获得注意而抢话、过度解释，或在不对位的场合消耗表达力。",
        "practice": "表达前先停一秒：这句话是从身体信号出来的，还是为了抓住注意力？",
        "prompt": "我现在说话，是有真实能量要通过，还是害怕自己不被看见？",
    },
    "g": {
        "body": "稳定提供方向感、身份感与爱自己的路线，适合顺着内在坐标选择环境。",
        "spiritual": "这里像内在罗盘，让你记得自己是谁、要往哪里去。",
        "open_body": "容易随环境和关系改变方向，身体会强烈感知“这里适不适合我”。",
        "open_spiritual": "开放时更适合通过环境校准方向，而不是用头脑固定一个永久身份。",
        "consumption": "卡点常表现为为了找到自己而抓住某个身份、人设或关系不放。",
        "practice": "先选对地方和人，再谈方向；环境不对时，答案也容易失真。",
        "prompt": "这个环境让我更像自己，还是让我开始扮演一个不自然的版本？",
    },
    "heart": {
        "body": "稳定处理承诺、意志力、交换和价值感，适合把承诺控制在身体能兑现的范围。",
        "spiritual": "这里检验你如何使用意志：是从真实价值出发，还是从证明自己出发。",
        "open_body": "容易为了证明价值而过度承诺，身体会被“我必须赢/必须证明”牵动。",
        "open_spiritual": "开放时适合学习价值不靠硬撑证明，真正的交换来自清晰边界。",
        "consumption": "卡点常表现为硬扛、逞强、对价格或价值感不安。",
        "practice": "任何承诺先降一档，问自己：我是否愿意并且有资源持续兑现？",
        "prompt": "这个承诺来自真实愿力，还是来自我想证明自己值得？",
    },
    "spleen": {
        "body": "稳定提供当下直觉、警觉和身体本能，适合尊重瞬间的安全感与不适感。",
        "spiritual": "这里像身体的古老智慧，帮助你分辨什么滋养生命，什么正在耗损生命。",
        "open_body": "容易吸收外界恐惧，也容易抓住熟悉但不滋养的东西不放。",
        "open_spiritual": "开放时能敏锐感知环境健康度，但不要把每个恐惧都当成命令。",
        "consumption": "卡点常表现为留恋旧模式、对不安全感上瘾、明知不对还不离开。",
        "practice": "记录身体第一秒的收缩或放松，不急着解释，只先承认它存在。",
        "prompt": "我的身体第一反应是靠近、放松，还是收缩、想逃？",
    },
    "solar-plexus": {
        "body": "稳定经历情绪波，适合等情绪过浪后再做重要决定。",
        "spiritual": "这里让情绪成为感受生命的潮汐，而不是必须立刻解决的问题。",
        "open_body": "容易放大别人的情绪，为了避免冲突而压抑真实感受。",
        "open_spiritual": "开放时适合学习分辨：这是我的情绪，还是我正在替场域消化情绪？",
        "consumption": "卡点常表现为情绪高点承诺、低点否定，或为了和谐而牺牲真实。",
        "practice": "重大决定至少隔一晚；先等情绪波过去，再看身体是否仍然清晰。",
        "prompt": "如果我不急着让情绪消失，它真正想告诉我的是什么？",
    },
    "sacral": {
        "body": "稳定提供生命力、回应力和持续工作能量，适合把精力投给身体有回应的事。",
        "spiritual": "这里是生命火种，帮助你通过真实回应进入创造和满足。",
        "open_body": "容易放大他人的工作节奏，误以为自己也必须持续输出。",
        "open_spiritual": "开放时适合学习何时停下，不把别人的生命力当成自己的义务。",
        "consumption": "卡点常表现为对无回应的事硬撑、把忙碌误认为生命力。",
        "practice": "用身体的“嗯/不嗯”做小选择训练，从饮食、会面、任务开始。",
        "prompt": "这件事让我身体变亮，还是只是头脑觉得应该做？",
    },
    "root": {
        "body": "稳定处理压力、启动和节奏，适合把压力转成有边界的行动。",
        "spiritual": "这里像地气和发动机，让你在现实压力里找到推进力量。",
        "open_body": "容易替外界压力加速，觉得所有事都必须马上完成。",
        "open_spiritual": "开放时适合学习压力不等于命令，慢下来反而能看见真正优先级。",
        "consumption": "卡点常表现为急、赶、被 deadline 推着跑，做完一件又抓下一件。",
        "practice": "每天选 3 件真正重要的事，其他压力先放入等待区。",
        "prompt": "我是在回应真实优先级，还是只是在释放被压力追赶的不舒服？",
    },
}


def build_body_energy_profile(chart: HumanDesignChart) -> BodyEnergyProfile:
    defined = tuple(_center_label(center.code) for center in chart.centers if center.defined)
    open_centers = tuple(_center_label(center.code) for center in chart.centers if not center.defined)
    center_notes = tuple(_build_center_note(center.code, center.defined) for center in chart.centers)
    channel_notes = tuple(_build_channel_note(channel) for channel in chart.channels)
    gate_notes = tuple(_build_gate_note(gate) for gate in chart.activated_gates[:12])
    type_label = display_type(chart.summary.type.code, chart.summary.type.label)
    authority_label = display_authority(chart.summary.authority.code, chart.summary.authority.label)
    summary = (
        f"这份身体能量解读以你的类型「{type_label}」和权威「{authority_label}」为主轴。"
        "已定义中心代表稳定资源，开放中心代表容易被外界放大的学习场；通道说明能量如何流动，"
        "闸门说明更细的天赋入口。"
    )
    return BodyEnergyProfile(
        headline="身体资源与灵性能量地图",
        summary=summary,
        defined_centers=defined,
        open_centers=open_centers,
        center_notes=center_notes,
        channel_notes=channel_notes,
        gate_notes=gate_notes,
        energy_management=_build_energy_management(chart),
        suggested_questions=(
            "我现在最需要先照顾哪个开放中心的消耗模式？",
            "我的已定义中心里，哪个是最稳定、最能带我回到自己的身体资源？",
            "如果我接下来 7 天只做一个能量实验，应该从哪里开始？",
        ),
    )


def _build_center_note(code: str, defined: bool) -> CenterEnergyNote:
    guide = CENTER_ENERGY_GUIDES[code]
    label = _center_label(code)
    return CenterEnergyNote(
        code=code,
        label=label,
        defined=defined,
        state_label="已定义" if defined else "开放",
        body_resource=guide["body"] if defined else guide["open_body"],
        spiritual_resource=guide["spiritual"] if defined else guide["open_spiritual"],
        consumption_pattern=guide["consumption"],
        practice=guide["practice"],
        observation_prompt=guide["prompt"],
    )


def _build_channel_note(channel) -> ChannelEnergyNote:
    center_labels = tuple(_center_label(code) for code in channel.centers)
    body_flow = (
        f"{center_labels[0]} 与 {center_labels[1]} 之间形成稳定连接。"
        "这不是偶然状态，而是你身体里会反复出现的能量路径。"
    )
    expression = (
        f"通道 {channel.code}「{channel.label}」会把两个中心的资源合成一种固定表达。"
        "真正顺的时候，它通常不是靠头脑硬推，而是像一条已经接通的内在线路。"
    )
    practice = "观察这条通道在工作、关系、表达中何时自然启动；自然启动时顺势用，卡住时不要强行证明。"
    return ChannelEnergyNote(
        code=channel.code,
        label=channel.label,
        centers=center_labels,  # type: ignore[arg-type]
        body_flow=body_flow,
        expression=expression,
        practice=practice,
    )


def _build_gate_note(gate) -> GateEnergyNote:
    activations = tuple(
        f"{activation.planet_label}.{activation.line}"
        for activation in gate.activations
    )
    prompt = (
        f"闸门 {gate.gate} 位于{_center_label(gate.center)}，主题是「{gate.theme}」。"
        "把它当作一个观察入口：它什么时候让你更有生命力，什么时候变成执念或消耗？"
    )
    return GateEnergyNote(
        gate=gate.gate,
        center=_center_label(gate.center),
        theme=gate.theme,
        activations=activations,
        prompt=prompt,
    )


def _build_energy_management(chart: HumanDesignChart) -> tuple[str, ...]:
    defined_count = sum(1 for center in chart.centers if center.defined)
    open_count = len(chart.centers) - defined_count
    authority = display_authority(chart.summary.authority.code, chart.summary.authority.label)
    strategy = display_strategy(chart.summary.strategy.code, chart.summary.strategy.label)
    return (
        f"先用策略「{strategy}」决定如何进入机会，再用权威「{authority}」决定是否继续。",
        f"你有 {defined_count} 个已定义中心、{open_count} 个开放中心；能量管理的关键不是补齐所有开放中心，而是减少被外界牵着走。",
        "当你感觉“淤堵”时，先不要把它理解成身体坏了，而要追踪：我是在哪个中心过度用力、替谁承担、或跳过了自己的权威？",
        "每周做一次复盘：哪些事情让我身体更亮、更稳、更有呼吸感；哪些事情让我急、硬撑、解释过度或失去方向？",
    )


def _center_label(code: str) -> str:
    return normalize_center_title(CENTER_LABELS.get(code, code))
