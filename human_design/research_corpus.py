from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .schema import InterpretationRule, KnowledgeAtom, PromptPack, SourceCard

CORPUS_ROOT = Path(__file__).resolve().parents[1] / "references" / "research-corpus" / "v0.3"

MAP_RETRIEVAL_TOPICS = {
    "body": ("荐骨回应", "身体资源", "开放中心压力", "能量卡点"),
    "wealth": ("财富来源", "资源配置", "承诺边界", "主航道"),
    "talent": ("2/4", "02-14", "意识交叉", "关键闸门"),
    "relationship": ("关系边界", "情绪放大", "信任网络", "方向感"),
    "mission": ("人生使命", "回应", "长期主线", "意识交叉"),
    "professional": ("图表事实", "专业依据", "中心", "通道", "闸门"),
}

MAP_SYSTEM_PROMPTS = {
    "body": "你是人类图身体资源解读器。只基于 chart facts 和知识原子，把中心、通道、权威翻译成身体可观察的节奏、压力和练习。",
    "wealth": "你是人类图财富地图解读器。只基于 chart facts 和知识原子，解释财富来源、赚钱方式、承诺风险和资源配置。",
    "talent": "你是人类图天赋地图解读器。只基于 chart facts 和知识原子，解释爻位、通道、闸门与天赋误用。",
    "relationship": "你是人类图关系地图解读器。只基于 chart facts 和知识原子，解释连接方式、边界、情绪和适配关系。",
    "mission": "你是人类图使命地图解读器。只基于 chart facts 和知识原子，解释人生主线、策略权威和轮回交叉。",
    "professional": "你是人类图专业信息解释器。输出必须可追溯到类型、策略、权威、中心、通道、闸门和行星激活。",
}


@lru_cache(maxsize=1)
def load_source_cards() -> tuple[SourceCard, ...]:
    return tuple(
        SourceCard(
            source_id=item["source_id"],
            title=item["title"],
            author=item["author"],
            language=item["language"],
            source_type=item["source_type"],
            url=item.get("url"),
            priority=item["priority"],
            copyright_policy=item["copyright_policy"],
            product_use=tuple(item["product_use"]),
        )
        for item in _read_json("sources.json")
    )


@lru_cache(maxsize=1)
def load_knowledge_atoms() -> tuple[KnowledgeAtom, ...]:
    return tuple(
        KnowledgeAtom(
            atom_id=item["atom_id"],
            source_ids=tuple(item["source_ids"]),
            topic=item["topic"],
            map_types=tuple(item["map_types"]),
            chart_keys=tuple(item["chart_keys"]),
            summary=item["summary"],
            user_translation=item["user_translation"],
        )
        for item in _read_json("knowledge_atoms.json")
    )


@lru_cache(maxsize=1)
def load_interpretation_rules() -> tuple[InterpretationRule, ...]:
    return tuple(
        InterpretationRule(
            rule_id=item["rule_id"],
            map_type=item["map_type"],
            applies_to=tuple(item["applies_to"]),
            title=item["title"],
            professional_basis=item["professional_basis"],
            user_language_template=item["user_language_template"],
            practice_template=item["practice_template"],
            source_atom_ids=tuple(item["source_atom_ids"]),
        )
        for item in _read_json("interpretation_rules.json")
    )


def build_prompt_pack(map_type: str, atom_ids: tuple[str, ...], rule_ids: tuple[str, ...]) -> PromptPack:
    map_key = normalize_map_type(map_type)
    return PromptPack(
        pack_id=f"v0.3:{map_key}",
        map_type=map_key,
        system_prompt=MAP_SYSTEM_PROMPTS[map_key],
        retrieval_topics=MAP_RETRIEVAL_TOPICS[map_key],
        atom_ids=atom_ids,
        rule_ids=rule_ids,
    )


def atoms_by_id() -> dict[str, KnowledgeAtom]:
    return {atom.atom_id: atom for atom in load_knowledge_atoms()}


def sources_by_id() -> dict[str, SourceCard]:
    return {source.source_id: source for source in load_source_cards()}


def normalize_map_type(map_type: str | None) -> str:
    if map_type in MAP_RETRIEVAL_TOPICS:
        return str(map_type)
    return "talent"


def _read_json(filename: str) -> list[dict]:
    path = CORPUS_ROOT / filename
    return json.loads(path.read_text(encoding="utf-8"))
