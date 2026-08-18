"""生成总控：有 key 走 LLM（prompt → chat → 护栏校验 → 缓存），无 key 走结构化精准回退。

- HD_GENERATION_MODE=llm|fallback 强制切换；默认：有 key = llm，无 key = fallback。
- LLM 相关错误对外只给 fallback 文案；原始错误只进服务端日志，且日志先 strip_user_terms 脱敏。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from ..providers import LLMProvider, ProviderError, resolve_provider, runtime_environment
from ..schema import HumanDesignChart
from . import fallback as fallback_mod
from .cache import GenerationCache, cache_key, normalize_question
from .facts import ChartFacts, extract_chart_facts
from .prompt_builder import PROMPT_VERSION, build_prompt
from .validator import strip_user_terms, validate_and_repair

logger = logging.getLogger("human_design.generation")

MODE_ENV = "HD_GENERATION_MODE"


@dataclass(frozen=True)
class GenerationResult:
    text: str
    mode: str  # "llm" | "fallback"
    layer: str
    cached: bool = False


@dataclass(frozen=True)
class MainReading:
    l1: str
    l2: str
    signature: str
    not_self: str
    detail_sections: tuple[dict[str, str], ...]
    explore: tuple[dict[str, str], ...]
    generation_mode: str


@dataclass(frozen=True)
class DetailReading:
    title: str
    body: str
    generation_mode: str


def resolve_mode(provider: LLMProvider | None) -> str:
    forced = (runtime_environment().get(MODE_ENV) or "").strip().lower()
    if forced in {"llm", "fallback"}:
        return forced
    if provider is not None and getattr(provider, "configured", False):
        return "llm"
    return "fallback"


def _safe_log(message: str, error: Exception, facts: ChartFacts) -> None:
    detail = strip_user_terms(str(error), facts.user_term_whitelist)
    logger.warning("%s：%s", message, detail)


def generate(
    facts: ChartFacts,
    layer: str,
    *,
    key: str = "",
    structure_block: str = "",
    question: str | None = None,
    provider: LLMProvider | None = None,
    cache: GenerationCache | None = None,
    mode: str | None = None,
) -> GenerationResult:
    """单层生成总控。fallback 层的文本由调用方（generate_main_reading 等）负责组装。"""
    if provider is None and mode != "fallback":
        provider = resolve_provider()
    active_mode = mode or resolve_mode(provider)
    if active_mode != "llm" or provider is None or not getattr(provider, "configured", False):
        return GenerationResult(text="", mode="fallback", layer=layer)

    model_name = getattr(provider, "model", "") or ""
    store = cache or GenerationCache()
    entry_key = cache_key(
        facts.facts_hash,
        layer,
        facts.focus,
        normalize_question(question),
        model_name,
        PROMPT_VERSION,
    )
    hit = store.get(entry_key)
    if hit is not None:
        return GenerationResult(text=hit, mode="llm", layer=layer, cached=True)

    try:
        messages = build_prompt(facts, layer, key=key, structure_block=structure_block)
    except ValueError as exc:
        _safe_log("prompt 构造失败，降级 fallback", exc, facts)
        return GenerationResult(text="", mode="fallback", layer=layer)

    def _chat(current_messages: list[dict[str, str]]) -> str:
        return provider.chat(current_messages).content

    try:
        text, status = validate_and_repair(messages, facts, _chat, max_repair=1)
    except ProviderError as exc:
        _safe_log("模型调用失败，降级 fallback", exc, facts)
        return GenerationResult(text="", mode="fallback", layer=layer)

    if status == "fallback_after_repair_fail" or not text.strip():
        logger.warning("护栏拦截：%s 层输出在重写后仍有硬违规，降级 fallback。", layer)
        return GenerationResult(text="", mode="fallback", layer=layer)
    if status == "soft_leak":
        logger.warning("软违规（英文残留）：%s 层输出已记录，未降级。", layer)

    store.set(
        entry_key,
        facts.facts_hash,
        layer,
        text,
        model=model_name,
        prompt_version=PROMPT_VERSION,
    )
    return GenerationResult(text=text, mode="llm", layer=layer)


def generate_main_reading(
    chart: HumanDesignChart,
    *,
    provider: LLMProvider | None = None,
    cache: GenerationCache | None = None,
    mode: str | None = None,
    user_terms: tuple[str, ...] = (),
) -> MainReading:
    facts = extract_chart_facts(chart, layer="L2", user_terms=user_terms)

    if provider is None and mode != "fallback":
        provider = resolve_provider()
    active_mode = mode or resolve_mode(provider)

    l1_result = generate(facts, "L1", provider=provider, cache=cache, mode=active_mode)
    l2_result = generate(facts, "L2", provider=provider, cache=cache, mode=active_mode)

    l1 = l1_result.text if l1_result.mode == "llm" else fallback_mod.build_l1(facts)
    l2 = l2_result.text if l2_result.mode == "llm" else fallback_mod.build_l2(facts)
    generation_mode = "llm" if (l1_result.mode == "llm" and l2_result.mode == "llm") else "fallback"

    return MainReading(
        l1=l1,
        l2=l2,
        signature=_signature_line(facts),
        not_self=_not_self_line(facts),
        detail_sections=tuple(
            {"key": section.key, "title": section.title, "summary": section.summary}
            for section in fallback_mod.DETAIL_SECTIONS
        ),
        explore=tuple(
            {"key": key, "title": title, "hint": hint}
            for key, title, hint in fallback_mod.EXPLORE_ENTRIES
        ),
        generation_mode=generation_mode,
    )


_SIGNATURE_LINES = {
    "satisfaction": "活对了的体感：一天下来虽然累，但有一种力气用对了的满足。",
    "success": "活对了的体感：你的洞见被接住、被感谢，事情因为你顺了很多。",
    "peace": "活对了的体感：想做的事推得动，周围没有人拦你，心里是平的。",
    "surprise": "活对了的体感：生活会持续给你没规划过的小惊喜。",
}

_NOT_SELF_LINES = {
    "frustration": "活拧了的体感：忙了很多却越来越烦，挫败感反复冒头。",
    "bitterness": "活拧了的体感：一种「我看得这么清楚却没人听」的苦涩。",
    "anger": "活拧了的体感：被拦、被管、被要求解释的火气一阵阵上来。",
    "disappointment": "活拧了的体感：对人、对地方钝钝的失望感挥之不去。",
}


def _signature_line(facts: ChartFacts) -> str:
    return _SIGNATURE_LINES.get(facts.signature_code, f"活对了的体感：{facts.signature_cn}。")


def _not_self_line(facts: ChartFacts) -> str:
    return _NOT_SELF_LINES.get(facts.not_self_code, f"活拧了的体感：{facts.not_self_cn}。")


def generate_detail_reading(
    chart: HumanDesignChart,
    key: str,
    *,
    provider: LLMProvider | None = None,
    cache: GenerationCache | None = None,
    mode: str | None = None,
) -> DetailReading:
    # 隐私死线：L3 事实与 prompt 不含任何个人输入，缓存可跨用户共享。
    facts = extract_chart_facts(chart, layer="L3")
    title = fallback_mod.detail_title(key)  # 未知 key 在这里抛 KeyError，由 Web 层转 422
    structure_block = fallback_mod.build_detail_body(facts, key)

    if provider is None and mode != "fallback":
        provider = resolve_provider()
    active_mode = mode or resolve_mode(provider)

    result = generate(
        facts,
        "L3",
        key=key,
        structure_block=structure_block,
        provider=provider,
        cache=cache,
        mode=active_mode,
    )
    if result.mode == "llm":
        return DetailReading(title=title, body=result.text, generation_mode="llm")
    return DetailReading(title=title, body=structure_block, generation_mode="fallback")


def generate_map_reading(
    chart: HumanDesignChart,
    map_type: str,
    *,
    provider: LLMProvider | None = None,
    cache: GenerationCache | None = None,
    mode: str | None = None,
) -> DetailReading:
    title = fallback_mod.MAP_TITLES.get(map_type)
    if title is None:
        raise KeyError(map_type)
    facts = extract_chart_facts(chart, layer="MAP", focus=map_type)
    fallback_body = fallback_mod.build_map_body(facts, map_type)

    if provider is None and mode != "fallback":
        provider = resolve_provider()
    active_mode = mode or resolve_mode(provider)
    result = generate(
        facts,
        "MAP",
        key=map_type,
        provider=provider,
        cache=cache,
        mode=active_mode,
    )
    if result.mode == "llm":
        return DetailReading(title=title, body=result.text, generation_mode="llm")
    return DetailReading(title=title, body=fallback_body, generation_mode="fallback")
