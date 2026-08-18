from __future__ import annotations

import json

from human_design.providers import (
    DEFAULT_DEEPSEEK_MODEL,
    OFFICIAL_DEEPSEEK_MODELS,
    ClaudeClient,
    ClaudeConfig,
    DeepSeekClient,
    DeepSeekConfig,
    LLMProvider,
    MiniMaxImageClient,
    MiniMaxImageConfig,
    ProviderConfigurationError,
    external_provider_status,
    resolve_provider,
)


def test_deepseek_requires_api_key() -> None:
    client = DeepSeekClient(config=DeepSeekConfig(api_key=None))

    try:
        client.chat([{"role": "user", "content": "你好"}])
    except ProviderConfigurationError:
        pass
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("DeepSeekClient should require an API key")


def test_deepseek_client_posts_openai_compatible_payload() -> None:
    captured: dict[str, object] = {}

    def fake_transport(url, headers, payload, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["payload"] = payload
        captured["timeout"] = timeout
        return {"choices": [{"message": {"content": "基于图表事实回答。"}}], "usage": {"total_tokens": 12}}

    client = DeepSeekClient(
        config=DeepSeekConfig(api_key="test-key", base_url="https://api.deepseek.com", model="deepseek-v4-pro"),
        transport=fake_transport,
    )
    answer = client.chat([{"role": "user", "content": "我的喉咙中心怎么用？"}])

    assert answer.content == "基于图表事实回答。"
    assert captured["url"] == "https://api.deepseek.com/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer test-key"  # type: ignore[index]
    assert captured["payload"]["model"] == "deepseek-v4-pro"  # type: ignore[index]
    assert captured["payload"]["thinking"] == {"type": "disabled"}  # type: ignore[index]
    assert captured["payload"]["stream"] is False  # type: ignore[index]


def test_default_deepseek_model_is_official() -> None:
    # 防回退：默认模型必须属于 DeepSeek 官方可用集合（deepseek-v4-pro 是幻觉值）。
    assert DEFAULT_DEEPSEEK_MODEL in OFFICIAL_DEEPSEEK_MODELS


def test_claude_client_posts_anthropic_messages_payload() -> None:
    captured: dict[str, object] = {}

    def fake_transport(url, headers, payload, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["payload"] = payload
        return {"content": [{"type": "text", "text": "基于图表事实回答。"}], "usage": {"input_tokens": 3}}

    client = ClaudeClient(
        config=ClaudeConfig(api_key="claude-test-key", model="claude-opus-4-8"),
        transport=fake_transport,
    )
    answer = client.chat(
        [
            {"role": "system", "content": "系统提示"},
            {"role": "user", "content": "我的喉咙中心怎么用？"},
        ]
    )

    assert answer.content == "基于图表事实回答。"
    assert answer.provider == "claude"
    assert captured["url"] == "https://api.anthropic.com/v1/messages"
    headers = captured["headers"]
    assert headers["x-api-key"] == "claude-test-key"  # type: ignore[index]
    assert headers["anthropic-version"] == "2023-06-01"  # type: ignore[index]
    payload = captured["payload"]
    assert payload["system"] == "系统提示"  # type: ignore[index]
    assert all(message["role"] != "system" for message in payload["messages"])  # type: ignore[index]


def test_claude_client_requires_api_key() -> None:
    client = ClaudeClient(config=ClaudeConfig(api_key=None))
    try:
        client.chat([{"role": "user", "content": "你好"}])
    except ProviderConfigurationError:
        pass
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("ClaudeClient should require an API key")


def test_clients_satisfy_llm_provider_protocol() -> None:
    assert isinstance(DeepSeekClient(config=DeepSeekConfig(api_key="k")), LLMProvider)
    assert isinstance(ClaudeClient(config=ClaudeConfig(api_key="k")), LLMProvider)


def test_resolve_provider_honours_env(monkeypatch) -> None:
    monkeypatch.setenv("HD_LLM_PROVIDER", "claude")
    assert isinstance(resolve_provider(), ClaudeClient)
    monkeypatch.delenv("HD_LLM_PROVIDER")
    assert isinstance(resolve_provider(), DeepSeekClient)
    assert isinstance(resolve_provider("claude"), ClaudeClient)


def test_external_provider_status_includes_claude_and_never_leaks_keys(monkeypatch) -> None:
    deepseek_key = "unit-test-deepseek-secret-123"
    anthropic_key = "unit-test-anthropic-secret-456"
    minimax_key = "unit-test-minimax-secret-789"
    monkeypatch.setenv("DEEPSEEK_API_KEY", deepseek_key)
    monkeypatch.setenv("ANTHROPIC_API_KEY", anthropic_key)
    monkeypatch.setenv("MINIMAX_API_KEY", minimax_key)

    status = external_provider_status()
    assert status["claude"]["configured"] is True
    assert status["deepseek"]["configured"] is True

    serialized = json.dumps(status, ensure_ascii=False)
    for secret in (deepseek_key, anthropic_key, minimax_key):
        assert secret not in serialized
        # 连子串都不许出现
        assert secret[8:20] not in serialized


def test_minimax_image_client_parses_base64_image() -> None:
    captured: dict[str, object] = {}

    def fake_transport(url, headers, payload, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["payload"] = payload
        captured["timeout"] = timeout
        return {"data": {"image_base64": "abc123"}}

    client = MiniMaxImageClient(
        config=MiniMaxImageConfig(api_key="test-key", endpoint="https://api.minimax.io/v1/image_generation"),
        transport=fake_transport,
    )
    result = client.generate("生成一张解读封面", aspect_ratio="3:4")

    assert result.image_url == "data:image/jpeg;base64,abc123"
    assert captured["url"] == "https://api.minimax.io/v1/image_generation"
    assert captured["headers"]["Authorization"] == "Bearer test-key"  # type: ignore[index]
    assert captured["payload"]["model"] == "image-01"  # type: ignore[index]
    assert captured["payload"]["response_format"] == "base64"  # type: ignore[index]
