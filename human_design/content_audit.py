from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

from .interpretation_maps import build_interpretation_map
from .schema import HumanDesignChart, InterpretationMapItem


USER_REPORT_TYPES = ("body", "channels", "wealth", "talent", "relationship", "mission")
INTERNAL_PHRASES = (
    "chart facts",
    "prompt",
    "fallback",
    "validator",
    "当前聚焦",
    "问题切口",
    "专业信息必须",
    "系统有没有编造",
    "知识原子",
)
GENERIC_FILLER = (
    "多觉察",
    "相信自己",
    "顺其自然",
    "一切都是最好的安排",
    "提升能量",
)
MAP_REQUIRED_TERMS = {
    "body": ("决定", "压力", "恢复"),
    "channels": ("通道", "能力", "成熟"),
    "wealth": ("收入", "承诺", "资产"),
    "talent": ("天赋", "人生角色", "代表作"),
    "relationship": ("关系", "边界", "冲突"),
    "mission": ("使命", "主线", "90 天"),
}


@dataclass(frozen=True)
class ContentAuditResult:
    score: int
    checks: dict[str, bool]
    issues: tuple[str, ...]


def audit_report_content(chart: HumanDesignChart) -> ContentAuditResult:
    """Measure report usefulness and factual grounding, not belief accuracy."""
    packages = {map_type: build_interpretation_map(chart, map_type=map_type) for map_type in USER_REPORT_TYPES}
    items_by_map = {
        map_type: tuple(item for section in package.sections for item in section.items)
        for map_type, package in packages.items()
    }
    all_items = tuple(item for items in items_by_map.values() for item in items)
    channel_codes = tuple(channel.code for channel in chart.channels)
    all_user_text = "\n".join(_user_text(item) for item in all_items)

    checks = {
        "reports_have_reading_shape": all(
            1 <= len(package.sections) <= 5
            and all(section.items for section in package.sections)
            and len({section.title for section in package.sections}) == len(package.sections)
            for package in packages.values()
        ),
        "facts_are_traceable": all(item.chart_basis for item in all_items),
        "channels_are_interpreted": _channels_are_interpreted(items_by_map["channels"], channel_codes),
        "map_language_is_specific": all(
            all(term in _package_text(packages[map_type]) for term in required)
            for map_type, required in MAP_REQUIRED_TERMS.items()
        ),
        "diagnosis_is_complete": all(_diagnosis_is_complete(item) for item in all_items),
        "content_is_readable": all(
            45 <= len(item.user_language) <= 460
            and all(len(line) <= 240 for line in _supporting_lines(item))
            for item in all_items
        ),
        "repetition_is_controlled": _max_pair_similarity(all_items) < 0.79 and _repeated_sentence_count(all_items) == 0,
        "content_is_actionable": all(item.practices for item in all_items),
        "channel_number_agreement": _channel_number_agreement(packages, len(channel_codes)),
        "authority_terms_are_distinct": not any(
            phrase in all_user_text for phrase in ("自我投射的Ego Authority", "自我投射的意志权威")
        ),
        "no_generic_filler": not any(phrase in all_user_text for phrase in GENERIC_FILLER),
        "no_internal_language": not any(phrase in all_user_text.lower() for phrase in INTERNAL_PHRASES),
    }
    weights = {
        "reports_have_reading_shape": 10,
        "facts_are_traceable": 12,
        "channels_are_interpreted": 12,
        "map_language_is_specific": 10,
        "diagnosis_is_complete": 13,
        "content_is_readable": 10,
        "repetition_is_controlled": 8,
        "content_is_actionable": 5,
        "channel_number_agreement": 5,
        "authority_terms_are_distinct": 5,
        "no_generic_filler": 5,
        "no_internal_language": 5,
    }
    score = sum(weights[name] for name, passed in checks.items() if passed)
    issues = tuple(name for name, passed in checks.items() if not passed)
    return ContentAuditResult(score=score, checks=checks, issues=issues)


def _channels_are_interpreted(items: tuple[InterpretationMapItem, ...], channel_codes: tuple[str, ...]) -> bool:
    if not channel_codes:
        return any(item.key == "channels.environmental-activation" for item in items)
    detail_keys = {item.key for item in items}
    return all(f"channels.{code}" in detail_keys for code in channel_codes)


def _channel_number_agreement(packages: dict[str, object], channel_count: int) -> bool:
    if channel_count != 1:
        return True
    text = "\n".join(_package_text(package) for package in packages.values())
    single_channel_placeholders = (
        "它们不会一条一条",
        "彼此配合",
        "分别卖一次",
        "共同解决一个客户",
        "一部分能力",
        "另一部分能力",
        "有的负责看见",
        "每条通道拆成",
        "哪几种能力总是一起",
        "让这组能力",
    )
    return not any(phrase in text for phrase in single_channel_placeholders)


def _diagnosis_is_complete(item: InterpretationMapItem) -> bool:
    if item.diagnosis_depth == "trace":
        return not item.embodied_expression and not item.stuck_causes
    if item.diagnosis_depth == "deep":
        return all((item.embodied_expression, item.blind_spots, item.stuck_patterns, item.stuck_causes))
    return bool(item.blind_spots or item.stuck_patterns) and bool(item.life_scenes or item.embodied_expression)


def _package_text(package) -> str:
    chunks = [package.title, package.description]
    for section in package.sections:
        chunks.extend((section.title, section.intro))
        for item in section.items:
            chunks.append(_user_text(item))
    return "\n".join(chunks)


def _user_text(item: InterpretationMapItem) -> str:
    return "\n".join((
        item.title,
        item.subtitle,
        item.user_language,
        *item.life_scenes,
        *item.embodied_expression,
        *item.blind_spots,
        *item.stuck_patterns,
        *item.stuck_causes,
        *item.practices,
    ))


def _supporting_lines(item: InterpretationMapItem) -> tuple[str, ...]:
    return (
        *item.life_scenes,
        *item.embodied_expression,
        *item.blind_spots,
        *item.stuck_patterns,
        *item.stuck_causes,
        *item.practices,
    )


def _max_pair_similarity(items: tuple[InterpretationMapItem, ...]) -> float:
    signatures = [_ngrams(_normalize(item.user_language)) for item in items]
    maximum = 0.0
    for index, left in enumerate(signatures):
        for right in signatures[index + 1:]:
            if not left or not right:
                continue
            maximum = max(maximum, len(left & right) / len(left | right))
    return maximum


def _ngrams(text: str, size: int = 3) -> set[str]:
    return {text[index:index + size] for index in range(max(0, len(text) - size + 1))}


def _normalize(text: str) -> str:
    return re.sub(r"[\s，。；：、“”‘’！？,.!?;:]", "", text)


def _repeated_sentence_count(items: tuple[InterpretationMapItem, ...]) -> int:
    sentences = Counter()
    for item in items:
        for sentence in re.split(r"[。！？]", item.user_language):
            normalized = _normalize(sentence)
            if len(normalized) >= 18:
                sentences[normalized] += 1
    return sum(1 for count in sentences.values() if count > 1)
