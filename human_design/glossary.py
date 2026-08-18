"""统一翻译层（单一数据源，确定性、零 LLM）。

所有用户可见出口必须经过这里的 display_* 函数：
- 行星（代码/符号 → 中文名）
- 变量六项（Motivation/Perspective/Determination/Environment/Cognition/Sense → 白话中文）
- 回路（Individual/Tribal/Collective → 个体人/社群人/集体人回路）
- 通道类型（Projected/Generated/Manifested → 投射/生成/显示）
- design/personality → 设计面（身体层）/人格面（意识层）
- 轮回交叉降级模板（角度 + 主轴闸门中文主题词）

映射 miss 绝不回落英文：回落「第N号」式中文占位并记日志告警。
前端共用同一份数据：export_glossary_json() 导出 web/src/glossary.json。
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger("human_design.glossary")

# ---------------------------------------------------------------- 行星

PLANET_LABELS = {
    "sun": "太阳",
    "earth": "地球",
    "moon": "月亮",
    "north-node": "北交点",
    "south-node": "南交点",
    "mercury": "水星",
    "venus": "金星",
    "mars": "火星",
    "jupiter": "木星",
    "saturn": "土星",
    "uranus": "天王星",
    "neptune": "海王星",
    "pluto": "冥王星",
}

PLANET_SYMBOLS = {
    "☉": "太阳",
    "⊕": "地球",
    "☽": "月亮",
    "☊": "北交点",
    "☋": "南交点",
    "☿": "水星",
    "♀": "金星",
    "♂": "火星",
    "♃": "木星",
    "♄": "土星",
    "⛢": "天王星",
    "♅": "天王星",
    "♆": "海王星",
    "♇": "冥王星",
}

# 英文行星名 → 中文（pyhd 的 planet_label 可能是 "☉ Sun" 这类混合串）
PLANET_EN_LABELS = {
    "sun": "太阳",
    "earth": "地球",
    "moon": "月亮",
    "north node": "北交点",
    "south node": "南交点",
    "mercury": "水星",
    "venus": "金星",
    "mars": "火星",
    "jupiter": "木星",
    "saturn": "土星",
    "uranus": "天王星",
    "neptune": "海王星",
    "pluto": "冥王星",
}

# ---------------------------------------------------------------- 面向（imprint）

IMPRINT_LABELS = {
    "design": "设计面（身体层）",
    "personality": "人格面（意识层）",
}

IMPRINT_SHORT_LABELS = {
    "design": "设计面",
    "personality": "人格面",
}

# ---------------------------------------------------------------- 回路与通道类型

CIRCUIT_GROUP_LABELS = {
    "individual": "个体人回路",
    "tribal": "社群人回路",
    "collective": "集体人回路",
    "integration": "整合回路",
}

CIRCUIT_GROUP_HINTS = {
    "individual": "推动「与众不同」和突变的能量",
    "tribal": "关于支持、契约、照顾彼此",
    "collective": "关于分享经验、为众人探路",
    "integration": "关于自我保存与本能整合",
}

CHANNEL_TYPE_LABELS = {
    "projected": "投射型",
    "generated": "生成型",
    "manifested": "显示型",
    "manifesting-generated": "显示生成型",
}

# ---------------------------------------------------------------- 变量六项（全部白话）

MOTIVATION_LABELS = {
    "Fear": "恐惧",
    "Hope": "希望",
    "Desire": "渴望",
    "Need": "需要",
    "Guilt": "愧疚",
    "Innocence": "纯真",
}

MOTIVATION_HINTS = {
    "Fear": "你做事更多被「想守住什么」推动，先看清风险反而让你安心",
    "Hope": "你做事更多被「盼着会更好」推动，希望感在，劲就在",
    "Desire": "你做事更多被「想要」而非「害怕」推动",
    "Need": "你做事更多被「真的需要」推动，可有可无的事很难让你上心",
    "Guilt": "你容易被「我是不是亏欠了谁」推动，值得留意这股劲的来处",
    "Innocence": "你状态最好的时候是不带算计地去做，越单纯越有力",
}

PERSPECTIVE_LABELS = {
    "Smell": "直觉嗅觉",
    "Taste": "品味分辨",
    "Outer Vision": "外观全景",
    "Inner Vision": "内在画面",
    "Feeling": "感受",
    "Touch": "贴近触感",
}

PERSPECTIVE_HINTS = {
    "Smell": "你习惯先靠一种说不清的「气味感」判断对不对劲",
    "Taste": "你习惯先分辨「合不合口味」，挑剔其实是你的天线",
    "Outer Vision": "你习惯先扫一眼全景，把局面尽收眼底再说",
    "Inner Vision": "你习惯先在心里成像，画面清楚了才觉得看懂了",
    "Feeling": "你习惯先用感受去读一个人、一件事，而不是先讲道理",
    "Touch": "你习惯靠得足够近、亲手碰过，才真正相信自己看到的",
}

COGNITION_LABELS = PERSPECTIVE_LABELS

# Determination：pyhd 输出 "Touch, Calm" 这类完整串
DETERMINATION_LABELS = {
    "Appetite, Consecutive": "一次专注一样、按顺序来，身体最好消化",
    "Appetite, Alternating": "换着花样来，身体反而吸收得好",
    "Taste, Open": "口味开放、多尝多试，营养面宽一点更滋养你",
    "Taste, Closed": "认准合适的就固定下来，重复反而养人",
    "Thirst, Hot": "偏温热的饮食和环境更养你",
    "Thirst, Cold": "偏清凉的饮食和环境更养你",
    "Touch, Calm": "靠身体触感判断、需要安静不被打扰",
    "Touch, Nervous": "身体敏感度高，有点动静反而帮你消化",
    "Sound, High": "环境里有清亮的声音时你吸收得更好",
    "Sound, Low": "低沉安稳的声音环境里你更能消化",
    "Light, Direct": "光线充足、白天进食状态最好",
    "Light, Indirect": "柔和的光线下你更放松、吸收更好",
}

# Environment：pyhd 输出 "Valleys, Wide" 这类完整串
ENVIRONMENT_LABELS = {
    "Caves, Selective": "有安全感的小空间最让你松下来，入口由你把关",
    "Caves, Blending": "有包裹感又不封死的空间最养你",
    "Markets, Internal": "有人来人往、可交换的地方让你有活力，但要能退回自己的角落",
    "Markets, External": "热闹的交换场域让你状态好，越开放越自在",
    "Kitchens, Wet": "湿润、有烟火气的环境最让你舒服",
    "Kitchens, Dry": "干爽、有烟火气的环境最让你舒服",
    "Mountains, Active": "地势高、空气流动的地方让你清醒有力",
    "Mountains, Passive": "地势高、安静开阔的地方最能安你的神",
    "Valleys, Narrow": "地势偏低、有围合感的空间让你踏实",
    "Valleys, Wide": "地势偏低、视野开阔的空间最让你松下来",
    "Shores, Natural": "水边、边界地带最养你，越自然越好",
    "Shores, Artificial": "水边、边界地带最养你，城市水岸也可以",
}

SENSE_LABELS = {
    "Uncertainty": "不确定",
    "Certainty": "确定",
    "Action": "行动",
    "Meditation": "静观",
    "Observation": "观察",
    "Acceptance": "接纳",
}

VARIABLE_TITLES = {
    "motivation": "驱动你的内在动力",
    "perspective": "你习惯先用什么角度看世界",
    "determination": "你最适合的吸收节奏",
    "environment": "你状态最好的环境",
    "cognition": "你天生的感知通道",
    "sense": "你的意识底色",
}

# ---------------------------------------------------------------- 轮回交叉降级模板

CROSS_ANGLE_LABELS = {
    "r": "右角度交叉",
    "l": "左角度交叉",
    "j": "并列交叉",
}

_CROSS_CODE_RE = re.compile(r"^(\d{1,2})-(\d{1,2})-(\d{1,2})-(\d{1,2})-([rlj])$")

# ---------------------------------------------------------------- display_* 函数


def display_planet(code_or_symbol: str, fallback: str = "") -> str:
    key = (code_or_symbol or "").strip()
    if key in PLANET_LABELS:
        return PLANET_LABELS[key]
    if key in PLANET_SYMBOLS:
        return PLANET_SYMBOLS[key]
    lowered = key.lower()
    if lowered in PLANET_EN_LABELS:
        return PLANET_EN_LABELS[lowered]
    # 混合串："☉ Sun" / "North Node" 等：逐 token 找
    for token in re.split(r"[\s_-]+", lowered):
        if token in PLANET_EN_LABELS:
            return PLANET_EN_LABELS[token]
    for symbol, zh in PLANET_SYMBOLS.items():
        if symbol in key:
            return zh
    logger.warning("glossary miss: planet %r", code_or_symbol)
    return "行星"


def display_imprint(code: str, *, short: bool = False) -> str:
    table = IMPRINT_SHORT_LABELS if short else IMPRINT_LABELS
    label = table.get((code or "").strip().lower())
    if label:
        return label
    logger.warning("glossary miss: imprint %r", code)
    return "本命面"


def display_circuit_group(code: str) -> str:
    label = CIRCUIT_GROUP_LABELS.get((code or "").strip().lower())
    if label:
        return label
    logger.warning("glossary miss: circuit group %r", code)
    return "能量回路"


def display_channel_type(code: str) -> str:
    label = CHANNEL_TYPE_LABELS.get((code or "").strip().lower())
    if label:
        return label
    logger.warning("glossary miss: channel type %r", code)
    return "通道"


def _display_variable_value(table: dict[str, str], raw: str, kind: str) -> str:
    key = (raw or "").strip()
    if key in table:
        return table[key]
    logger.warning("glossary miss: %s %r", kind, raw)
    return "见专业信息"


def display_motivation(raw: str) -> str:
    return _display_variable_value(MOTIVATION_LABELS, raw, "motivation")


def display_perspective(raw: str) -> str:
    return _display_variable_value(PERSPECTIVE_LABELS, raw, "perspective")


def display_determination(raw: str) -> str:
    return _display_variable_value(DETERMINATION_LABELS, raw, "determination")


def display_environment(raw: str) -> str:
    return _display_variable_value(ENVIRONMENT_LABELS, raw, "environment")


def display_cognition(raw: str) -> str:
    return _display_variable_value(COGNITION_LABELS, raw, "cognition")


def display_sense(raw: str) -> str:
    return _display_variable_value(SENSE_LABELS, raw, "sense")


def display_variables(variables) -> tuple[str, ...]:
    """把 VariableSet 变成一组白话行（零英文、零代码串）。"""
    lines = [
        f"{VARIABLE_TITLES['motivation']}：{display_motivation(variables.motivation.label)}——{MOTIVATION_HINTS.get(variables.motivation.label, '看看就好，不必当规定')}。",
        f"{VARIABLE_TITLES['perspective']}：{display_perspective(variables.perspective.label)}——{PERSPECTIVE_HINTS.get(variables.perspective.label, '看看就好，不必当规定')}。",
        f"{VARIABLE_TITLES['determination']}：{display_determination(variables.determination.label)}。",
        f"{VARIABLE_TITLES['environment']}：{display_environment(variables.environment.label)}。",
    ]
    return tuple(lines)


def display_incarnation_cross_theme(code: str, label: str, gate_theme_labels: dict[int, str]) -> str:
    """轮回交叉降级模板：角度 + 主轴闸门中文主题词。

    不逐条翻译 192 个全名；labels.py 已有的精译条目优先于本函数。
    """
    match = _CROSS_CODE_RE.match((code or "").strip())
    if match:
        angle = CROSS_ANGLE_LABELS[match.group(5)]
        main_gate = int(match.group(1))
        theme = gate_theme_labels.get(main_gate)
        if theme:
            return f"{angle}·{theme}"
        logger.warning("glossary miss: gate theme %s in cross %r", main_gate, code)
        return f"{angle}·第{main_gate}号闸门主题"
    lowered = (label or "").lower()
    if "right angle" in lowered:
        return "右角度交叉"
    if "left angle" in lowered:
        return "左角度交叉"
    if "juxtaposition" in lowered:
        return "并列交叉"
    logger.warning("glossary miss: incarnation cross %r / %r", code, label)
    return "轮回交叉（详见专业信息）"


# ---------------------------------------------------------------- 精度提示中文化

_PRECISION_TOKEN_REPLACEMENTS = (
    ("UTC offset", "时区偏移"),
    ("IANA 时区", "标准时区"),
    ("IANA", "标准时区"),
    ("UTC 时间", "世界时"),
    ("UTC 处理", "世界时处理"),
    ("按 UTC", "按世界时"),
    ("UTC", "世界时"),
)


def scrub_technical_terms(text: str) -> str:
    """把精度提示里的技术缩写替换成中文（确定性替换，不改语义）。"""
    result = text or ""
    for src, dst in _PRECISION_TOKEN_REPLACEMENTS:
        result = result.replace(src, dst)
    return result


# ---------------------------------------------------------------- 前端共用 JSON 导出


def build_glossary_entries() -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []

    def add(group: str, key: str, en: str, zh: str, tier: str = "translate", hint: str = "") -> None:
        entry = {"key": key, "en": en, "zh": zh, "tier": tier, "group": group}
        if hint:
            entry["first_hint"] = hint
        entries.append(entry)

    for code, zh in PLANET_LABELS.items():
        add("planet", code, code, zh)
    for symbol, zh in PLANET_SYMBOLS.items():
        add("planet-symbol", symbol, symbol, zh, tier="hide")
    for code, zh in IMPRINT_LABELS.items():
        add("imprint", code, code, zh, hint="设计面来自身体层，人格面来自意识层")
    for code, zh in CIRCUIT_GROUP_LABELS.items():
        add("circuit", code, code, zh, hint=CIRCUIT_GROUP_HINTS.get(code, ""))
    for code, zh in CHANNEL_TYPE_LABELS.items():
        add("channel-type", code, code, zh)
    for en, zh in MOTIVATION_LABELS.items():
        add("motivation", en, en, zh, hint=MOTIVATION_HINTS.get(en, ""))
    for en, zh in PERSPECTIVE_LABELS.items():
        add("perspective", en, en, zh, hint=PERSPECTIVE_HINTS.get(en, ""))
    for en, zh in DETERMINATION_LABELS.items():
        add("determination", en, en, zh)
    for en, zh in ENVIRONMENT_LABELS.items():
        add("environment", en, en, zh)
    for en, zh in SENSE_LABELS.items():
        add("sense", en, en, zh)
    for code, zh in CROSS_ANGLE_LABELS.items():
        add("cross-angle", code, code, zh)
    return entries


def export_glossary_json(path: str | Path | None = None) -> Path:
    target = Path(path) if path else Path(__file__).resolve().parents[1] / "web" / "src" / "glossary.json"
    target.write_text(
        json.dumps(build_glossary_entries(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return target


if __name__ == "__main__":
    print(export_glossary_json())
