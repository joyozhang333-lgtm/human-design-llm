from __future__ import annotations

import re

import pytest

from human_design.engine import calculate_chart
from human_design.generation.cache import GenerationCache
from human_design.generation.facts import extract_chart_facts
from human_design.generation.llm_engine import (
    generate,
    generate_detail_reading,
    generate_map_reading,
    generate_main_reading,
    resolve_mode,
)
from human_design.input import normalize_birth_input
from human_design.providers import DeepSeekClient, DeepSeekConfig, LLMProvider

GOOD_TEXT = "你的能量更适合等待邀请，可能在被真正看见时最省力。答案不在图里，在你接下来怎么观察自己。"
BAD_TEXT = "你的 99 号闸门保证你注定成功。"


@pytest.fixture(scope="module")
def chart():
    return calculate_chart(normalize_birth_input("1988-10-09T20:30:00+08:00", timezone_name="Asia/Shanghai"))


@pytest.fixture(scope="module")
def facts(chart):
    return extract_chart_facts(chart, layer="L2")


def _client_with_responses(responses: list[str]) -> tuple[DeepSeekClient, list[dict]]:
    calls: list[dict] = []

    def transport(url, headers, payload, timeout):
        calls.append({"url": url, "payload": payload})
        index = min(len(calls) - 1, len(responses) - 1)
        return {"choices": [{"message": {"content": responses[index]}}]}

    client = DeepSeekClient(
        config=DeepSeekConfig(api_key="test-key", model="deepseek-chat"),
        transport=transport,
    )
    return client, calls


def test_llm_provider_protocol_is_satisfied() -> None:
    client, _ = _client_with_responses([GOOD_TEXT])
    assert isinstance(client, LLMProvider)


def test_generate_llm_happy_path_validates_and_caches(tmp_path, facts) -> None:
    client, calls = _client_with_responses([GOOD_TEXT])
    cache = GenerationCache(tmp_path / "cache.db")

    result = generate(facts, "L2", provider=client, cache=cache, mode="llm")
    assert result.mode == "llm"
    assert result.text == GOOD_TEXT
    assert len(calls) == 1

    # 缓存命中路径零 LLM 调用
    again = generate(facts, "L2", provider=client, cache=cache, mode="llm")
    assert again.cached is True
    assert again.text == GOOD_TEXT
    assert len(calls) == 1


def test_generate_repair_path(tmp_path, facts) -> None:
    client, calls = _client_with_responses([BAD_TEXT, GOOD_TEXT])
    cache = GenerationCache(tmp_path / "cache.db")

    result = generate(facts, "L2", provider=client, cache=cache, mode="llm")
    assert result.mode == "llm"
    assert result.text == GOOD_TEXT
    assert len(calls) == 2
    # 定向重写：第二次请求带着违规说明回灌
    second_messages = calls[1]["payload"]["messages"]
    assert any("99" in message["content"] for message in second_messages)


def test_generate_degrades_to_fallback_after_repair_fail(tmp_path, facts) -> None:
    client, calls = _client_with_responses([BAD_TEXT, BAD_TEXT])
    cache = GenerationCache(tmp_path / "cache.db")

    result = generate(facts, "L2", provider=client, cache=cache, mode="llm")
    assert result.mode == "fallback"
    assert result.text == ""  # 违规文本绝不外泄
    assert len(calls) == 2
    # 违规文本不入缓存
    assert generate(facts, "L2", provider=client, cache=cache, mode="llm").cached is False


def test_generate_degrades_on_provider_error(tmp_path, facts) -> None:
    def broken_transport(url, headers, payload, timeout):
        raise OSError("network down")

    client = DeepSeekClient(config=DeepSeekConfig(api_key="k"), transport=lambda *a: (_ for _ in ()).throw(Exception))
    # 直接用会抛 ProviderError 的客户端
    from human_design.providers import ProviderRequestError

    class Exploding:
        configured = True
        model = "deepseek-chat"

        def chat(self, messages):
            raise ProviderRequestError("HTTP 500: internal")

    result = generate(facts, "L2", provider=Exploding(), cache=GenerationCache(tmp_path / "c.db"), mode="llm")
    assert result.mode == "fallback"


def test_env_mode_forces_fallback_without_llm_calls(tmp_path, facts, monkeypatch) -> None:
    client, calls = _client_with_responses([GOOD_TEXT])
    monkeypatch.setenv("HD_GENERATION_MODE", "fallback")
    assert resolve_mode(client) == "fallback"
    result = generate(facts, "L2", provider=client, cache=GenerationCache(tmp_path / "c.db"))
    assert result.mode == "fallback"
    assert calls == []


def test_dotenv_mode_is_respected(tmp_path, monkeypatch) -> None:
    (tmp_path / ".env").write_text("HD_GENERATION_MODE=fallback\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("HD_GENERATION_MODE", raising=False)
    assert resolve_mode(None) == "fallback"


def test_generate_main_reading_llm_mode_returns_contract(tmp_path, chart) -> None:
    l1_text = "你的天赋在看懂人和局，可能被真正看见时最省力；做决定先问真心想不想要，先独处养熟再被叫出来。"
    client, calls = _client_with_responses([l1_text, GOOD_TEXT])
    reading = generate_main_reading(chart, provider=client, cache=GenerationCache(tmp_path / "c.db"), mode="llm")
    assert reading.generation_mode == "llm"
    assert reading.l1 == l1_text
    assert reading.l2 == GOOD_TEXT
    assert reading.signature and reading.not_self
    keys = [section["key"] for section in reading.detail_sections]
    assert keys == ["centers", "channels", "gates", "variables", "cross"]
    assert [entry["key"] for entry in reading.explore] == ["talent", "mission", "body", "wealth", "relationship"]


def test_generate_main_reading_fallback_mode(chart) -> None:
    reading = generate_main_reading(chart, mode="fallback")
    assert reading.generation_mode == "fallback"
    assert 40 <= len(reading.l1) <= 78
    assert len([p for p in reading.l2.split("\n\n") if p.strip()]) >= 3
    assert not re.search(r"[A-Za-z]{3,}", reading.l1 + reading.l2)


def test_generate_detail_reading_l3_prompt_contains_no_personal_input(tmp_path, chart) -> None:
    captured: list[dict] = []

    def transport(url, headers, payload, timeout):
        captured.append(payload)
        return {"choices": [{"message": {"content": GOOD_TEXT}}]}

    client = DeepSeekClient(config=DeepSeekConfig(api_key="k", model="deepseek-chat"), transport=transport)
    detail = generate_detail_reading(chart, "cross", provider=client, cache=GenerationCache(tmp_path / "c.db"), mode="llm")
    assert detail.generation_mode == "llm"
    prompt_text = "\n".join(
        message["content"] for payload in captured for message in payload["messages"]
    )
    # L3 prompt 净空：不含任何个人输入值（昵称值、性别值、出生地值）——跨用户共享缓存的前提
    for personal in ("测试用户", "小昭", "male", "female", "1988-10-09", "20:30"):
        assert personal not in prompt_text


def test_generate_detail_reading_unknown_key_raises(chart) -> None:
    with pytest.raises(KeyError):
        generate_detail_reading(chart, "nope", mode="fallback")


@pytest.mark.parametrize("map_type", ["body", "wealth", "talent", "relationship", "mission", "professional"])
def test_generate_map_reading_has_complete_fallback_for_every_map(chart, map_type) -> None:
    result = generate_map_reading(chart, map_type, mode="fallback")
    assert result.generation_mode == "fallback"
    assert len(result.body) >= 180
    assert "prompt" not in result.body.lower()
    assert "系统有没有编造" not in result.body


def test_generate_map_reading_uses_llm_and_chart_guardrails(tmp_path, chart) -> None:
    text = (
        "你的人生角色需要先把天然能力养熟，再让信任关系带来机会。\n\n"
        "做决定时更适合回到身体回应，不急着证明。\n\n"
        "真实通道会让天赋有稳定出口，开放中心则提醒你别替别人用力。\n\n"
        "先从一个真实场景观察自己，答案不在图里，在你接下来怎么观察自己。"
    )
    client, calls = _client_with_responses([text])
    result = generate_map_reading(
        chart,
        "talent",
        provider=client,
        cache=GenerationCache(tmp_path / "map.db"),
        mode="llm",
    )
    assert result.generation_mode == "llm"
    assert result.body == text
    assert len(calls) == 1
