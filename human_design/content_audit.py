from __future__ import annotations

from dataclasses import dataclass

from .interpretation_maps import build_interpretation_map
from .schema import HumanDesignChart


USER_REPORT_TYPES = ("body", "wealth", "talent", "relationship", "mission")
INTERNAL_PHRASES = (
    "chart facts",
    "prompt",
    "fallback",
    "validator",
    "当前聚焦",
    "问题切口",
    "专业信息必须",
)


@dataclass(frozen=True)
class ContentAuditResult:
    score: int
    checks: dict[str, bool]
    issues: tuple[str, ...]


def audit_report_content(chart: HumanDesignChart) -> ContentAuditResult:
    """Audit report structure and factual traceability without grading belief claims."""
    packages = {
        map_type: build_interpretation_map(chart, map_type=map_type)
        for map_type in USER_REPORT_TYPES
    }
    items_by_map = {
        map_type: tuple(item for section in package.sections for item in section.items)
        for map_type, package in packages.items()
    }
    all_items = tuple(item for items in items_by_map.values() for item in items)
    channel_codes = tuple(channel.code for channel in chart.channels)

    checks = {
        "four_clear_questions": all(
            len(package.sections) == 4
            and all(len(section.items) == 1 for section in package.sections)
            for package in packages.values()
        ),
        "facts_are_traceable": all(item.chart_basis for item in all_items),
        "channels_are_covered": all(
            all(
                code in "\n".join(
                    line
                    for item in items_by_map[map_type]
                    for line in item.chart_basis
                )
                for code in channel_codes
            )
            for map_type in ("wealth", "talent", "mission")
        ),
        "content_is_distinct": len({item.user_language for item in all_items}) == len(all_items),
        "content_is_readable": all(35 <= len(item.user_language) <= 360 for item in all_items),
        "content_is_actionable": all(item.practices for item in all_items),
        "no_internal_language": not any(
            phrase in "\n".join(item.user_language for item in all_items).lower()
            for phrase in INTERNAL_PHRASES
        ),
    }
    weights = {
        "four_clear_questions": 15,
        "facts_are_traceable": 20,
        "channels_are_covered": 20,
        "content_is_distinct": 15,
        "content_is_readable": 10,
        "content_is_actionable": 10,
        "no_internal_language": 10,
    }
    score = sum(weights[name] for name, passed in checks.items() if passed)
    issues = tuple(name for name, passed in checks.items() if not passed)
    return ContentAuditResult(score=score, checks=checks, issues=issues)
