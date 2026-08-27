from __future__ import annotations

from .glossary import display_incarnation_cross_theme

TYPE_LABELS = {
    "reflector": "反映者",
    "manifestor": "显示者",
    "generator": "生产者",
    "pure-generator": "纯生产者",
    "manifesting-generator": "显示生产者",
    "pure-manifesting-generator": "显示生产者",
    "projector": "投射者",
    "energy-projector": "投射者",
    "classic-projector": "投射者",
    "mental-projector": "精神型投射者",
}

STRATEGY_LABELS = {
    "respond": "等待回应",
    "to-respond": "等待回应",
    "invitation": "等待邀请",
    "wait-invite": "等待邀请",
    "wait-for-the-invitation": "等待邀请",
    "inform": "先告知再行动",
    "respond-inform": "等待回应后告知",
    "lunar-cycle": "等待完整月亮周期",
    "wait-lunar-cycle": "等待月亮周期",
}

AUTHORITY_LABELS = {
    "sacral": "荐骨权威",
    "solar-plexus": "情绪权威",
    "emotional": "情绪权威",
    "splenic": "脾权威",
    "ego": "意志力权威",
    "ego-manifested": "意志力权威",
    "ego-projected": "意志力权威",
    "self-projected": "自我投射权威",
    "mental": "环境权威",
    "outer-authority": "环境权威",
    "lunar": "月亮权威",
}

AUTHORITY_PROFESSIONAL_LABELS = {
    "sacral": "Sacral Authority",
    "solar-plexus": "Emotional Authority",
    "emotional": "Emotional Authority",
    "splenic": "Splenic Authority",
    "ego": "Ego Authority",
    "ego-manifested": "Ego Manifested Authority",
    "ego-projected": "Ego Projected Authority",
    "self-projected": "Self-Projected Authority",
    "mental": "Environmental Authority",
    "outer-authority": "Environmental Authority",
    "lunar": "Lunar Authority",
}

DEFINITION_LABELS = {
    "single": "一分人",
    "simple-split": "二分人",
    "split": "二分人",
    "wide-split": "二分人",
    "triple-split": "三分人",
    "quadruple-split": "四分人",
    "no": "无定义",
}

SIGNATURE_LABELS = {
    "satisfaction": "满足",
    "success": "成功",
    "peace": "平和",
    "surprise": "惊喜",
}

NOT_SELF_LABELS = {
    "frustration": "挫败",
    "bitterness": "苦涩",
    "anger": "愤怒",
    "disappointment": "失望",
}

CENTER_LABELS = {
    "head": "头顶中心",
    "ajna": "阿姬娜中心",
    "throat": "喉咙中心",
    "g": "G中心",
    "heart": "意志力中心",
    "spleen": "脾中心",
    "solar-plexus": "情绪中心",
    "sacral": "荐骨中心",
    "root": "根部中心",
}

CHANNEL_LABELS = {
    "01-08": "创造贡献通道",
    "02-14": "方向与资源通道",
    "03-60": "突变通道",
    "04-63": "逻辑通道",
    "05-15": "节律通道",
    "06-59": "亲密通道",
    "07-31": "引导通道",
    "09-52": "专注通道",
    "10-20": "觉醒通道",
    "10-34": "探索通道",
    "10-57": "身体直觉通道",
    "11-56": "好奇与故事通道",
    "12-22": "开放表达通道",
    "13-33": "记忆与退隐通道",
    "16-48": "才华通道",
    "17-62": "组织表达通道",
    "18-58": "修正通道",
    "19-49": "敏感与原则通道",
    "20-34": "魅力通道",
    "20-57": "直觉表达通道",
    "21-45": "资源管理通道",
    "23-43": "洞见表达通道",
    "24-61": "内在真理通道",
    "25-51": "唤醒通道",
    "26-44": "说服与传递通道",
    "27-50": "照顾与价值通道",
    "28-38": "意义抗争通道",
    "29-46": "发现通道",
    "30-41": "情感经验通道",
    "32-54": "转化通道",
    "34-57": "力量与直觉通道",
    "35-36": "经验变化通道",
    "37-40": "社群契约通道",
    "39-55": "情绪丰盛通道",
    "42-53": "成熟周期通道",
    "47-64": "抽象整合通道",
}

GATE_THEME_LABELS = {
    1: "自我表达",
    2: "方向与接收",
    3: "新秩序",
    4: "答案与公式",
    5: "固定节律",
    6: "亲密边界",
    7: "引导角色",
    8: "贡献风格",
    9: "专注细节",
    10: "自爱与行为",
    11: "想法",
    12: "谨慎表达",
    13: "倾听与记忆",
    14: "资源能力",
    15: "极端节律",
    16: "技能热情",
    17: "观点结构",
    18: "修正判断",
    19: "需求敏感",
    20: "当下表达",
    21: "掌控资源",
    22: "开放与优雅",
    23: "简化表达",
    24: "回归思考",
    25: "本真之爱",
    26: "说服与记忆",
    27: "照顾滋养",
    28: "生命意义的抗争",
    29: "承诺投入",
    30: "渴望与情感",
    31: "影响力",
    32: "延续与保存",
    33: "退隐与故事",
    34: "大力量",
    35: "经验推进",
    36: "危机与经验",
    37: "亲密社群",
    38: "为意义而战",
    39: "挑动情绪",
    40: "独处与意志",
    41: "想象起点",
    42: "成熟完成",
    43: "洞见突破",
    44: "模式警觉",
    45: "资源分配",
    46: "身体之爱",
    47: "领悟整合",
    48: "深度",
    49: "原则与革命",
    50: "价值责任",
    51: "震动唤醒",
    52: "静止专注",
    53: "开始",
    54: "野心上升",
    55: "精神丰盛",
    56: "故事刺激",
    57: "直觉清明",
    58: "喜悦修正",
    59: "亲密破冰",
    60: "限制与突变",
    61: "内在真理",
    62: "细节命名",
    63: "怀疑检验",
    64: "混乱整合",
}

INCARNATION_CROSS_LABELS = {
    "13-07-01-02-r": "斯芬克斯右角度交叉 1（13/7 | 1/2）：使命主题是方向、倾听与带路",
    "63-64-05-35-r": "意识右角度交叉（63/64 | 5/35）：使命主题是把怀疑、混乱和经验整理成清晰",
}


def display_type(code: str, fallback: str) -> str:
    return TYPE_LABELS.get(code, fallback)


def display_strategy(code: str, fallback: str) -> str:
    return STRATEGY_LABELS.get(code, fallback)


def display_authority(code: str, fallback: str) -> str:
    return AUTHORITY_LABELS.get(code, fallback)


def display_authority_professional(code: str, fallback: str) -> str:
    return AUTHORITY_PROFESSIONAL_LABELS.get(code, fallback)


def display_definition(code: str, fallback: str) -> str:
    return DEFINITION_LABELS.get(code, fallback)


def display_gate_theme(gate: int | str, fallback: str = "") -> str:
    try:
        gate_number = int(gate)
    except (TypeError, ValueError):
        return fallback
    return GATE_THEME_LABELS.get(gate_number, fallback)


def display_channel_label(code: str, fallback: str = "") -> str:
    return CHANNEL_LABELS.get(code, fallback)


def display_incarnation_cross(code: str, fallback: str) -> str:
    if code in INCARNATION_CROSS_LABELS:
        return INCARNATION_CROSS_LABELS[code]
    if "Right Angle Cross of The Sphinx" in fallback:
        return "斯芬克斯右角度交叉：使命主题是方向、倾听与带路"
    if "Right Angle Cross of Consciousness" in fallback:
        return "意识右角度交叉：使命主题是把怀疑、混乱和经验整理成清晰"
    # 降级模板：角度 + 主轴闸门中文主题词；绝不回落英文全名。
    return display_incarnation_cross_theme(code, fallback, GATE_THEME_LABELS)


def display_signature(code: str, fallback: str) -> str:
    return SIGNATURE_LABELS.get(code, fallback)


def display_not_self(code: str, fallback: str) -> str:
    return NOT_SELF_LABELS.get(code, fallback)


def display_profile(code: str, fallback: str) -> str:
    if code:
        return code.replace("-", "/")
    if ":" in fallback:
        return fallback.split(":", 1)[0].strip()
    return fallback


def normalize_center_title(text: str) -> str:
    normalized = text.replace("G 中心", "G中心")
    normalized = normalized.replace("阿基那中心", "阿姬娜中心")
    normalized = normalized.replace("阿闸那中心", "阿姬娜中心")
    normalized = normalized.replace("骶骨中心", "荐骨中心")
    return normalized
