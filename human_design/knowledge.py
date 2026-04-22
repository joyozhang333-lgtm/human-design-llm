from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

TYPE_GUIDES = {
    "manifestor": {
        "summary": "你的能量更适合主动发起、打开局面，而不是等外界先给许可。",
        "gifts": (
            "擅长率先点火，把事情从静止推到开始。",
            "当方向清晰时，执行会带有很强的穿透力和独立性。",
        ),
        "shadows": (
            "没有先告知关键相关人时，容易引发阻力或误解。",
            "过度独自推进时，别人会感到被排除在外。",
        ),
    },
    "pure-generator": {
        "summary": "你的稳定生命力来自回应，而不是凭头脑硬推。真正对的机会，会让身体先亮起来。",
        "gifts": (
            "一旦回应正确，持续力和投入度都很强。",
            "适合通过反复打磨，把事情做深做熟。",
        ),
        "shadows": (
            "为了证明自己而承诺过多，会快速耗空满足感。",
            "用脑子替代身体回应时，容易忙很多却不满足。",
        ),
    },
    "manifesting-generator": {
        "summary": "你既有回应式生命力，也有把事情快速推进的能力，但前提仍然是先有正确回应。",
        "gifts": (
            "适合并行推进、快速迭代、边做边校准。",
            "能把复杂任务压缩成更高效率的执行路径。",
        ),
        "shadows": (
            "跳步骤太快时，容易返工或让别人跟不上。",
            "若没有先确认身体回应，速度会变成消耗。",
        ),
    },
    "energy-projector": {
        "summary": "你擅长看懂系统、看懂人和资源如何运转，核心不是硬拼体力，而是精准引导能量。",
        "gifts": (
            "看见问题核心和最优路径的速度很快。",
            "在关系、团队、流程优化中容易成为关键校准点。",
        ),
        "shadows": (
            "没有被看见时主动硬推，容易陷入苦涩。",
            "拿自己和持续输出型的人比较，容易误判自己的节奏。",
        ),
    },
    "classic-projector": {
        "summary": "你的优势在识别模式、理解他人、给出定向指导。你的价值常来自洞察，而非拼总工时。",
        "gifts": (
            "适合做策略、诊断、咨询、陪跑和结构设计。",
            "能在复杂关系里看见真正需要被调整的点。",
        ),
        "shadows": (
            "未经邀请直接指导，容易不被接住。",
            "为了证明价值而长期过载，会快速耗损。",
        ),
    },
    "mental-projector": {
        "summary": "你的清晰来自环境、对话和被看见后的回响，不适合在压力里独自逼自己做决定。",
        "gifts": (
            "擅长通过语言和空间感知来发现真正的清晰。",
            "在高质量讨论里，常能把模糊问题说透。",
        ),
        "shadows": (
            "把外界的意见误当成自己的答案，会越来越失真。",
            "环境不对时，整个人会被噪音带跑。",
        ),
    },
    "reflector": {
        "summary": "你像环境的高灵敏度镜子，适合用时间和空间来感受什么真正适合自己。",
        "gifts": (
            "能非常敏锐地映照团队、家庭或系统的真实状态。",
            "在对的环境里，你的感知会非常纯净而有价值。",
        ),
        "shadows": (
            "太快定论时，常会拿到并不属于自己的答案。",
            "长期处在错误环境里，会感觉失望或失准。",
        ),
    },
}

AUTHORITY_GUIDES = {
    "solar-plexus": "情绪权威的关键不是立刻决定，而是等情绪波经过后再看清楚。你最稳的答案来自情绪清明，而不是当下高点或低点。",
    "sacral": "骶骨权威要用身体的即时回应来判断：嗯/不是、扩张/收缩、想靠近/想离开。越接近身体，越接近正确。",
    "splenic": "脾权威是安静、瞬时、一次性的直觉信号。它来得很快，不一定会重复，所以需要学会识别当下那一下真实感。",
    "ego-manifested": "意志权威要先问自己：我真想不想？我愿不愿意为这件事投入意志与承诺？不是该不该，而是我到底要不要。",
    "ego-projected": "自我投射的意志权威更适合在被看见的关系里说出来，通过表达愿望来确认自己是否真的想要。",
    "self-projected": "自我投射权威的清晰来自把话说出口。你要听见自己在什么方向上感觉“这就是我”。",
    "outer-authority": "外在权威并不是别人替你决定，而是你通过高质量对话与环境回声把自己的想法听清楚。",
    "lunar": "月亮权威需要时间。不要急着敲定，给自己完整周期去看情绪、环境和人际反馈是否仍然支持这个决定。",
}

PROFILE_GUIDES = {
    "1-3": "1/3 适合先打基础、再通过试错建立真实经验。你不是靠想明白成长，而是靠亲身验证成长。",
    "1-4": "1/4 既需要扎实理解，也需要稳定关系网络。你适合先把自己研究透，再在熟人信任中放大影响力。",
    "2-4": "2/4 需要在独处与被看见之间找到平衡。你的天赋常是天然存在的，但真正的展开通常靠正确的人来敲门。",
    "2-5": "2/5 常带着天然天赋和外界投射。你需要区分：别人期待你成为什么，和你真正能稳定提供什么。",
    "3-5": "3/5 是在试错里长本事、再把经验转成实用方案的人。你会经历很多现场学习，但真正价值恰恰来自这些经历。",
    "3-6": "3/6 前期多通过碰撞学习，中后期逐渐走向更高视角。你的成熟来自亲历后的沉淀，而不是一开始就完美。",
    "4-1": "4/1 的人生稳定度很重要。你既重视人际网络，也重视自己内在的确定结构，不适合被频繁打乱。",
    "4-6": "4/6 先通过关系网络展开人生，再逐步长出更高视角。你的影响力常建立在可信关系和长期观察之上。",
    "5-1": "5/1 很容易被投射为“能解决问题的人”。真正稳的方法是先把底层打透，再谨慎承接外界期待。",
    "5-2": "5/2 既容易被投射，又需要大量独处来校准自己。越知道自己的边界，越能把影响力用得稳。",
    "6-2": "6/2 需要时间与空间长出自己的高度。你不是一直在舞台上，而是在节奏成熟后自然成为他人参考。",
    "6-3": "6/3 把角色榜样与真实试错放在同一条路上。你的说服力来自经历过，而不是只会讲道理。",
}

DEFINITION_GUIDES = {
    "no": "无定义常见于反映者，整体更受环境影响，决定时更要重视空间与时间。",
    "single": "单一定义说明你的内部处理链路相对连贯，很多事情你可以在自己内部较快形成清晰。",
    "simple-split": "简单分裂定义代表你内部有两块系统，常通过特定人或特定互动被“接通”。",
    "wide-split": "宽分裂定义代表内部两块系统之间距离更大，别急着逼自己一次性整合，适合给过程更多时间。",
    "triple-split": "三重分裂定义说明你需要更多移动、更多人际流动和更多场域切换来帮助内部完成整合。",
    "quadruple-split": "四重分裂定义非常依赖环境流动与时间，不适合在封闭压力里做过快结论。",
}

CENTER_GUIDES = {
    "head": {
        "label": "头顶中心",
        "defined": "定义头顶中心会让灵感压力和提问驱动力较稳定，容易长期关注某些问题域。",
        "undefined": "开放头顶中心会放大外界问题和灵感压力。你的功课不是回答所有问题，而是分辨哪些问题值得你管。",
    },
    "ajna": {
        "label": "阿闸那中心",
        "defined": "定义阿闸那中心会让思考方式和认知结构较稳定，适合形成自己的分析框架。",
        "undefined": "开放阿闸那中心说明你思路更灵活，但也容易想把一切想确定。真正的成熟是允许自己不急着定论。",
    },
    "throat": {
        "label": "喉中心",
        "defined": "定义喉中心让表达与外化路径较稳定，别人更容易感到你的声音是持续存在的。",
        "undefined": "开放喉中心时，你会对“被看见、被听见”更敏感。越急着证明存在感，越容易失真。",
    },
    "g": {
        "label": "G 中心",
        "defined": "定义 G 中心代表身份感、方向感和爱之流动相对稳定，适合围绕自己一致的方向长期展开。",
        "undefined": "开放 G 中心更依赖环境与关系来映照方向。关键不是逼自己固定，而是待在真正对的场域里。",
    },
    "heart": {
        "label": "意志中心",
        "defined": "定义意志中心说明你的意志力和承诺感相对稳定，但也需要更谨慎地答应自己和别人。",
        "undefined": "开放意志中心常容易想证明自己。真正省力的方法，不是拼命证明，而是停止拿价值感去交换认可。",
    },
    "spleen": {
        "label": "脾中心",
        "defined": "定义脾中心让直觉、生存感和风险判断更稳定，很多判断会以很细微的身体信号出现。",
        "undefined": "开放脾中心会放大对安全感和熟悉感的依恋。成长点在于分辨：这是安全，还是只是熟悉。",
    },
    "solar-plexus": {
        "label": "情绪中心",
        "defined": "定义情绪中心代表你会周期性经过情绪波。清晰来自穿越波，而不是立刻解决。",
        "undefined": "开放情绪中心会强烈感到别人的情绪。你的边界练习，是知道哪些情绪不是你的。",
    },
    "sacral": {
        "label": "骶骨中心",
        "defined": "定义骶骨中心带来稳定生命力。真正的关键不是多忙，而是忙在正确回应上。",
        "undefined": "开放骶骨中心说明你不是持续输出型。节奏、休息和边界不是奢侈品，而是核心配置。",
    },
    "root": {
        "label": "根中心",
        "defined": "定义根中心会让压力转化为推动力的方式相对稳定，你往往擅长在压力中启动行动。",
        "undefined": "开放根中心会放大“赶快做完”的冲动。你的功课不是逃离压力，而是不替不属于你的压力买单。",
    },
}

CHANNEL_TYPE_GUIDES = {
    "generated": "这条通道更像持续供能的稳定回路，适合通过反复投入把主题做深。",
    "manifesting-generated": "这条通道把回应与快速执行连在一起，优势是高效率，风险是跳步骤。",
    "manifested": "这条通道有明显的发起和外推力量，常把内在冲动直接变成外部动作。",
    "projected": "这条通道更适合在关系与识别中被点亮，它的价值常在被看见后更好发挥。",
}

CIRCUIT_GROUP_GUIDES = {
    "collective": "集体回路强调经验、模式、故事与对整体的贡献。",
    "individual": "个体回路强调独特性、突变、原创表达与个人频率。",
    "tribal": "部落回路强调关系、资源、支持、承诺与交换。",
}

PLANET_GUIDES = {
    "sun": "太阳代表你最稳定、最显性的主轴力量。",
    "earth": "地球代表让你落地、稳住、校准的支点。",
    "moon": "月亮代表驱动你行动与投入的内在动力。",
    "north-node": "北交点更像人生往前展开时会不断遇到的场景与方向。",
    "south-node": "南交点代表你熟悉的背景、早期惯性与已带来的视角。",
    "mercury": "水星常显示你会反复思考、表达或传递的主题。",
    "venus": "金星常指向你的价值偏好、边界与审美判断。",
    "mars": "火星常显示你仍在练习、还带点生涩但潜力很强的课题。",
    "jupiter": "木星与扩张、信念、原则和成长法则有关。",
    "saturn": "土星常把责任、边界、现实功课和成熟要求带进来。",
    "uranus": "天王星常显示你身上不按常规的独特表达。",
    "neptune": "海王星常带来朦胧、理想、灵感，也容易形成投射。",
    "pluto": "冥王星常对应深层转化、执念与不能回避的核心变化。",
}

LINE_GUIDES = {
    1: "1线会把这股主题带向打基础、研究、求稳和先弄明白。",
    2: "2线让这股主题带有天然感、被召唤感，以及需要独处熟成的特征。",
    3: "3线会通过试错、碰撞和现场经验把主题做实。",
    4: "4线会把主题放进关系网络、熟人系统和影响力扩散中。",
    5: "5线会让这股主题更容易被外界投射为“能解决问题的力量”。",
    6: "6线会把主题带向更高视角、长期观察与后期成熟。",
}

VARIABLE_ORIENTATION_GUIDES = {
    "left": "偏左说明更适合结构、节奏、专注、可重复的方法。",
    "right": "偏右说明更适合接收、宽感知、环境读取和整体扫描。",
}

REFERENCE_ROOT = Path(__file__).resolve().parents[1] / "references"
REFERENCE_INDEX_PATH = REFERENCE_ROOT / "index.json"


@dataclass(frozen=True)
class ReferenceCard:
    code: str
    title: str
    summary: str
    gifts: tuple[str, ...]
    shadows: tuple[str, ...]
    focus: dict[str, str]
    path: str


@dataclass(frozen=True)
class CenterGuideCard:
    code: str
    title: str
    summary: str
    defined: str
    undefined: str
    focus: dict[str, str]
    path: str


def get_type_card(code: str) -> ReferenceCard | None:
    return _load_markdown_card("types", code)


def get_authority_card(code: str) -> ReferenceCard | None:
    return _load_markdown_card("authorities", code)


def get_profile_card(code: str) -> ReferenceCard | None:
    return _load_markdown_card("profiles", code)


def get_definition_card(code: str) -> ReferenceCard | None:
    return _load_markdown_card("definitions", code)


def get_center_card(code: str) -> CenterGuideCard | None:
    return _load_center_card(code)


def get_gate_card(gate: int | str) -> ReferenceCard | None:
    return _load_markdown_card("gates", str(gate))


def get_channel_card(code: str) -> ReferenceCard | None:
    return _load_markdown_card("channels", code)


@lru_cache(maxsize=1)
def load_reference_index() -> dict:
    if not REFERENCE_INDEX_PATH.exists():
        return {"version": "0.6-draft", "collections": {}}
    return json.loads(REFERENCE_INDEX_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=256)
def _load_markdown_card(collection: str, code: str) -> ReferenceCard | None:
    path = _resolve_reference_path(collection, code)
    if path is None or not path.exists():
        return None
    return _parse_markdown_card(code, path)


@lru_cache(maxsize=64)
def _load_center_card(code: str) -> CenterGuideCard | None:
    path = _resolve_reference_path("centers", code)
    if path is None or not path.exists():
        return None
    return _parse_center_card(code, path)


def _resolve_reference_path(collection: str, code: str) -> Path | None:
    index = load_reference_index()
    collection_index = index.get("collections", {}).get(collection, {})
    items = collection_index.get("items", {})
    relative_path = items.get(code)
    if relative_path:
        return REFERENCE_ROOT.parent / relative_path
    fallback = REFERENCE_ROOT / collection / f"{code}.md"
    if fallback.exists():
        return fallback
    return None


def _parse_markdown_card(code: str, path: Path) -> ReferenceCard:
    title, sections = _parse_markdown_sections(path, code)
    return ReferenceCard(
        code=code,
        title=title,
        summary=_join_section(sections.get("核心主题", [])),
        gifts=_collect_bullets(sections.get("礼物", [])),
        shadows=_collect_bullets(sections.get("失衡表现", [])),
        focus={
            "career": _join_section(sections.get("career", [])),
            "relationship": _join_section(sections.get("relationship", [])),
            "decision": _join_section(sections.get("decision", [])),
            "growth": _join_section(sections.get("growth", [])),
        },
        path=str(path),
    )


def _parse_center_card(code: str, path: Path) -> CenterGuideCard:
    title, sections = _parse_markdown_sections(path, code)
    return CenterGuideCard(
        code=code,
        title=title,
        summary=_join_section(sections.get("核心主题", [])),
        defined=_join_section(sections.get("已定义", [])),
        undefined=_join_section(sections.get("开放", [])),
        focus={
            "career": _join_section(sections.get("career", [])),
            "relationship": _join_section(sections.get("relationship", [])),
            "decision": _join_section(sections.get("decision", [])),
            "growth": _join_section(sections.get("growth", [])),
        },
        path=str(path),
    )


def _parse_markdown_sections(path: Path, default_title: str) -> tuple[str, dict[str, list[str]]]:
    raw = path.read_text(encoding="utf-8").strip()
    title = default_title
    current_heading: str | None = None
    sections: dict[str, list[str]] = {}

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            continue
        if stripped.startswith("## "):
            current_heading = stripped[3:].strip().lower()
            sections.setdefault(current_heading, [])
            continue
        if current_heading is None:
            continue
        sections.setdefault(current_heading, []).append(stripped)
    return title, sections


def _join_section(lines: list[str]) -> str:
    return " ".join(line.removeprefix("- ").strip() for line in lines).strip()


def _collect_bullets(lines: list[str]) -> tuple[str, ...]:
    bullets = [line[2:].strip() for line in lines if line.startswith("- ")]
    if bullets:
        return tuple(bullets)
    content = _join_section(lines)
    return (content,) if content else ()
