"""V0.6 内容生成引擎：ChartFacts -> prompt -> LLM -> 护栏校验 -> 缓存，无 key 走结构化精准回退。"""
from __future__ import annotations

from .facts import ChartFacts, extract_chart_facts
from .llm_engine import GenerationResult, generate, generate_detail_reading, generate_main_reading, generate_map_reading

__all__ = [
    "ChartFacts",
    "extract_chart_facts",
    "GenerationResult",
    "generate",
    "generate_main_reading",
    "generate_detail_reading",
    "generate_map_reading",
]
