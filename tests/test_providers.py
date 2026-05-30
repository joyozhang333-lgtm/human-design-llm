from __future__ import annotations

from human_design.providers import (
    DeepSeekClient,
    DeepSeekConfig,
    MiniMaxImageClient,
    MiniMaxImageConfig,
    ProviderConfigurationError,
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
