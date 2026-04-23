from __future__ import annotations

from typing import TypeVar

from .schema import LLMContextBlock, SessionState

DEPTH_MODES = ("brief", "standard", "deep")
T = TypeVar("T")


def normalize_depth(depth: str | None) -> str:
    if depth in DEPTH_MODES:
        return depth
    return "standard"


def select_sections_by_depth(items: tuple[T, ...], depth: str) -> tuple[T, ...]:
    if depth == "brief":
        return items[:2]
    return items


def followups_by_depth(items: tuple[str, ...], depth: str) -> tuple[str, ...]:
    if depth == "brief":
        return items[:2]
    return items


def highlight_limit(depth: str) -> int:
    if depth == "brief":
        return 3
    if depth == "deep":
        return 7
    return 5


def build_session_state(
    *,
    product_line: str,
    focus: str,
    headline: str,
    quick_facts: tuple[str, ...],
    context_blocks: tuple[LLMContextBlock, ...],
    suggested_followups: tuple[str, ...],
) -> SessionState:
    carry_block_keys = tuple(
        block.key
        for block in context_blocks
        if block.key not in {"focus", "quick-facts"}
    )
    return SessionState(
        product_line=product_line,
        focus=focus,
        headline=headline,
        carry_facts=quick_facts[:4],
        carry_block_keys=carry_block_keys,
        suggested_next_questions=suggested_followups,
    )
