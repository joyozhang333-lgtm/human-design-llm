from __future__ import annotations

import re

import pytest

from human_design.engine import calculate_chart
from human_design.generation.facts import extract_chart_facts
from human_design.generation import fallback as fallback_mod
from human_design.generation.prompt_builder import (
    PROMPT_VERSION,
    build_l1_prompt,
    build_l2_prompt,
    build_l3_prompt,
    build_prompt,
)
from human_design.generation.validator import (
    build_repair_instruction,
    strip_user_terms,
    validate,
    validate_and_repair,
)
from human_design.input import normalize_birth_input

ENGLISH_RE = re.compile(r"[A-Za-z]{3,}")
SYMBOL_RE = re.compile(r"[♃♄⛢♅⊕☊☋☉☽☿♀♂♆♇]")

BANNED_USER_FACING = (
    "chart facts",
    "方便后续",
    "回到图表事实",
    "门线解读",
    "产品价值",
    "系统有没有编造",
)
TEMPLATE_SENTENCES = (
    "当这股能量运作成熟时",
    "形成稳定贡献",
    "活成过度反应或反复内耗",
)
FATALISM = ("你注定", "你必然", "命中注定", "否则就", "不这样会")


@pytest.fixture(scope="module")
def projector_chart():
    return calculate_chart(normalize_birth_input("1988-10-09T20:30:00+08:00", timezone_name="Asia/Shanghai"))


@pytest.fixture(scope="module")
def generator_chart():
    return calculate_chart(normalize_birth_input("1970-02-04T12:00:00+08:00"))


@pytest.fixture(scope="module")
def projector_facts(projector_chart):
    return extract_chart_facts(projector_chart, layer="L2")


# ---------------------------------------------------------------- facts


def test_facts_are_fully_chinese_and_carry_whitelist(projector_facts) -> None:
    facts = projector_facts
    joined = "\n".join(
        (
            facts.type_cn,
            facts.strategy_cn,
            facts.authority_cn,
            facts.profile_cn,
            facts.definition_cn,
            facts.signature_cn,
            facts.not_self_cn,
            facts.cross_cn,
            *facts.defined_centers_cn,
            *facts.open_centers_cn,
            *facts.channels_cn,
            *facts.variables_cn,
            *facts.precision_cn,
            *(f"{g.theme_cn}{g.center_cn}{g.sentence}" for g in facts.all_gates),
        )
    )
    assert not ENGLISH_RE.search(joined.replace("G中心", "")), ENGLISH_RE.search(joined).group()
    assert not SYMBOL_RE.search(joined)
    assert facts.whitelist.gate_nums
    assert "25-51" in facts.whitelist.channel_codes
    assert len(facts.top_gates) <= 6
    assert len(facts.all_gates) == len(facts.whitelist.gate_nums)


def test_facts_hash_excludes_user_terms(projector_chart) -> None:
    plain = extract_chart_facts(projector_chart, layer="L2")
    with_terms = extract_chart_facts(projector_chart, layer="L2", user_terms=("小明", "Leo"))
    assert plain.facts_hash == with_terms.facts_hash


# ---------------------------------------------------------------- validator


def test_validate_catches_fabricated_structures(projector_facts) -> None:
    result = validate("你的 99 号闸门和 02-14 通道决定了一切。", projector_facts)
    kinds = {kind for kind, _ in result.violations}
    assert "fabricated_gate" in kinds
    assert "fabricated_channel" in kinds
    assert result.has_hard


def test_validate_normalises_single_digit_channel_codes(projector_facts) -> None:
    result = validate("你的天赋核心落在13-7这条通道上。", projector_facts)
    assert ("fabricated_channel", "13-07") in result.violations


def test_validate_flags_pollution_template_and_fatalism(projector_facts) -> None:
    text = "为了产品价值，当这股能量运作成熟时你注定会形成稳定贡献。"
    result = validate(text, projector_facts)
    kinds = {kind for kind, _ in result.violations}
    assert "pollution" in kinds
    assert "template_cliche" in kinds
    assert "anxiety_or_determinism" in kinds


def test_validate_rejects_generator_strategy_and_sacral_authority_conflicts(generator_chart) -> None:
    facts = extract_chart_facts(generator_chart, layer="L2")
    result = validate("你要等待被邀请，等情绪波过去再决定。", facts)
    kinds = {kind for kind, _ in result.violations}
    assert "strategy_conflict" in kinds
    assert "authority_conflict" in kinds


def test_validate_rejects_invented_gate_composites_and_channel_activation(projector_facts) -> None:
    result = validate(
        "由57、51、53、54组成的直觉与启动轴，需要得到邀请之后才会激活这条通道。",
        projector_facts,
    )
    kinds = {kind for kind, _ in result.violations}
    assert "invented_composite" in kinds
    assert "defined_channel_activation_conflict" in kinds

    instruction = build_repair_instruction(result.violations)
    assert "多个独立闸门" in instruction
    assert "本来就稳定存在" in instruction


def test_validate_allows_invitation_to_start_work_without_claiming_it_activates_a_channel(
    projector_facts,
) -> None:
    result = validate(
        "你更适合在收到邀请后启动合作。这条通道本来就稳定存在，只是表达时机不同。",
        projector_facts,
    )
    assert "defined_channel_activation_conflict" not in {
        kind for kind, _ in result.violations
    }


def test_validate_rejects_shortened_or_wrong_authority_name(projector_facts) -> None:
    result = validate("这次请用 Ego Authority 判断是否投入。", projector_facts)
    assert ("authority_name_conflict", "Ego Authority -> Ego Projected Authority") in result.violations
    instruction = build_repair_instruction(result.violations)
    assert "Ego Projected Authority" in instruction

    exact = validate("这次请用 Ego Projected Authority 判断是否投入。", projector_facts)
    assert exact.ok, exact.violations


def test_english_leak_is_soft_and_user_terms_are_stripped_first(projector_chart) -> None:
    facts = extract_chart_facts(projector_chart, layer="L2", user_terms=("Leo",))
    ok = validate("Leo，你的能量来自回应。", facts)
    assert ok.ok, ok.violations
    leak = validate("你的 Penetration 主题很强。", facts)
    assert leak.has_soft and not leak.has_hard


def test_strip_user_terms_for_log_sanitisation() -> None:
    assert "Leo" not in strip_user_terms("Leo 在北京出生", ("Leo", "北京"))


def test_repair_instruction_mentions_each_violation(projector_facts) -> None:
    result = validate("你的 99 号闸门注定了，Penetration。你注定成功。", projector_facts)
    instruction = build_repair_instruction(result.violations)
    assert "99" in instruction
    assert "英文" in instruction
    assert "或然" in instruction


def test_validate_and_repair_repairs_then_falls_back(projector_facts) -> None:
    good = "你的能量更适合等待邀请。可能你更容易在被看见时发挥。答案在你接下来怎么观察自己。"
    bad = "你的 99 号闸门保证你注定成功。"

    responses = [bad, good]
    calls: list[list[dict[str, str]]] = []

    def chat(messages):
        calls.append(messages)
        return responses[len(calls) - 1]

    text, status = validate_and_repair([{"role": "user", "content": "写一段"}], projector_facts, chat)
    assert text == good
    assert status == "repaired@1"
    # 定向重写：第二次调用带上了违规说明
    assert any("99" in message["content"] for message in calls[1])

    always_bad_calls = []

    def always_bad(messages):
        always_bad_calls.append(messages)
        return bad

    text, status = validate_and_repair([{"role": "user", "content": "写一段"}], projector_facts, always_bad)
    assert status == "fallback_after_repair_fail"
    assert text == ""  # 绝不把违规文本交给调用方
    assert len(always_bad_calls) == 2  # 原始 + repair ×1


# ---------------------------------------------------------------- prompt builder


def test_l1_l2_prompts_only_contain_chinese_facts(projector_facts) -> None:
    for messages in (build_l1_prompt(projector_facts), build_l2_prompt(projector_facts)):
        user = messages[-1]["content"]
        assert "本次图表事实" in user
        assert "Motivation" not in user
        assert "PLR" not in user
        assert not SYMBOL_RE.search(user)
    assert PROMPT_VERSION


def test_l2_prompt_requires_three_element_binding(projector_facts) -> None:
    user = build_l2_prompt(projector_facts)[-1]["content"]
    assert "人生角色" in user and "真实通道" in user and "开放中心" in user


def test_l3_prompt_rejects_user_terms(projector_chart) -> None:
    facts = extract_chart_facts(projector_chart, layer="L3", user_terms=("小昭",))
    clean_block = fallback_mod.build_detail_body(facts, "cross")
    messages = build_l3_prompt(facts, "cross", clean_block)
    joined = "\n".join(message["content"] for message in messages)
    assert "小昭" not in joined
    with pytest.raises(ValueError):
        build_l3_prompt(facts, "cross", clean_block + "（小昭专属）")


def test_build_prompt_rejects_unknown_layer(projector_facts) -> None:
    with pytest.raises(ValueError):
        build_prompt(projector_facts, "L9")


# ---------------------------------------------------------------- fallback 内容质量


def _assert_user_facing_clean(text: str) -> None:
    assert not ENGLISH_RE.search(text), ENGLISH_RE.search(text).group()
    assert not SYMBOL_RE.search(text)
    lowered = text.lower()
    for banned in BANNED_USER_FACING:
        assert banned not in lowered, banned
    for template in TEMPLATE_SENTENCES:
        assert template not in text, template
    for phrase in FATALISM:
        assert phrase not in text, phrase


def test_fallback_l1_synthesises_type_authority_profile(projector_facts) -> None:
    l1 = fallback_mod.build_l1(projector_facts)
    assert 40 <= len(l1) <= 78
    _assert_user_facing_clean(l1)


def test_fallback_l1_covers_all_type_authority_combos() -> None:
    for type_code, type_line in fallback_mod._TYPE_L1.items():
        for auth_code, auth_line in fallback_mod._AUTH_L1.items():
            for hook in fallback_mod._PROFILE_HOOK.values():
                line = f"{type_line}。{auth_line}；{hook}。"
                assert 40 <= len(line) <= 78, (type_code, auth_code, len(line))
                _assert_user_facing_clean(line)


def test_fallback_l2_is_specific_prose(projector_facts, generator_chart) -> None:
    l2 = fallback_mod.build_l2(projector_facts)
    paragraphs = [p for p in l2.split("\n\n") if p.strip()]
    assert 3 <= len(paragraphs) <= 5
    _assert_user_facing_clean(l2)
    # 三元素绑定：真实通道 + 真实开放中心 + 人生角色都要出现在正文里。
    assert "25-51" in l2
    assert projector_facts.profile_cn in l2
    assert any(center in l2 for center in projector_facts.open_centers_cn)
    # 结尾交还
    assert "答案不在图里" in l2

    other = fallback_mod.build_l2(extract_chart_facts(generator_chart, layer="L2"))
    _assert_user_facing_clean(other)
    # 不同的盘必须得到不同的正文（反套话底线）。
    assert other != l2


def test_fallback_l2_passes_own_validator(projector_facts) -> None:
    result = validate(fallback_mod.build_l2(projector_facts), projector_facts)
    assert result.ok, result.violations


def test_fallback_channel_lines_cover_all_36_channels() -> None:
    from human_design.labels import CHANNEL_LABELS

    assert set(fallback_mod.CHANNEL_LINES) == set(CHANNEL_LABELS)
    for line in fallback_mod.CHANNEL_LINES.values():
        _assert_user_facing_clean(line)


def test_fallback_detail_bodies_clean(projector_facts) -> None:
    for section in fallback_mod.DETAIL_SECTIONS:
        body = fallback_mod.build_detail_body(projector_facts, section.key)
        assert body.strip()
        _assert_user_facing_clean(body)
    with pytest.raises(KeyError):
        fallback_mod.build_detail_body(projector_facts, "nope")
