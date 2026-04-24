from __future__ import annotations

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

DEFINITION_LABELS = {
    "single": "单一定义",
    "simple-split": "二分定义",
    "split": "二分定义",
    "wide-split": "二分定义",
    "triple-split": "三分定义",
    "quadruple-split": "四分定义",
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


def display_type(code: str, fallback: str) -> str:
    return TYPE_LABELS.get(code, fallback)


def display_strategy(code: str, fallback: str) -> str:
    return STRATEGY_LABELS.get(code, fallback)


def display_authority(code: str, fallback: str) -> str:
    return AUTHORITY_LABELS.get(code, fallback)


def display_definition(code: str, fallback: str) -> str:
    return DEFINITION_LABELS.get(code, fallback)


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
