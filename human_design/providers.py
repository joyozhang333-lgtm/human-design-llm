from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Protocol, runtime_checkable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


JsonTransport = Callable[[str, dict[str, str], dict[str, Any], float], dict[str, Any]]

DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
# DeepSeek 官方现行对话模型；可用 DEEPSEEK_MODEL 环境变量覆盖。
DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"
OFFICIAL_DEEPSEEK_MODELS = ("deepseek-chat", "deepseek-reasoner")
DEFAULT_ANTHROPIC_BASE_URL = "https://api.anthropic.com"
DEFAULT_ANTHROPIC_MODEL = "claude-opus-4-8"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MINIMAX_IMAGE_ENDPOINT = "https://api.minimax.io/v1/image_generation"
DEFAULT_MINIMAX_IMAGE_MODEL = "image-01"


class ProviderError(RuntimeError):
    """Base error for external AI provider failures."""


class ProviderConfigurationError(ProviderError):
    """Raised when a provider is not configured for live calls."""


class ProviderRequestError(ProviderError):
    """Raised when a provider request fails."""


class ProviderResponseError(ProviderError):
    """Raised when a provider response cannot be parsed."""


@dataclass(frozen=True)
class DeepSeekConfig:
    api_key: str | None
    base_url: str = DEFAULT_DEEPSEEK_BASE_URL
    model: str = DEFAULT_DEEPSEEK_MODEL
    timeout_seconds: float = 60.0
    temperature: float = 0.45
    max_tokens: int = 1800
    thinking_enabled: bool = False
    reasoning_effort: str | None = None

    @classmethod
    def from_env(cls) -> "DeepSeekConfig":
        env = _env_with_dotenv()
        return cls(
            api_key=_clean_secret(env.get("DEEPSEEK_API_KEY")),
            base_url=(env.get("DEEPSEEK_BASE_URL") or DEFAULT_DEEPSEEK_BASE_URL).rstrip("/"),
            model=env.get("DEEPSEEK_MODEL") or DEFAULT_DEEPSEEK_MODEL,
            timeout_seconds=_env_float(env, "DEEPSEEK_TIMEOUT_SECONDS", 60.0),
            temperature=_env_float(env, "DEEPSEEK_TEMPERATURE", 0.45),
            max_tokens=_env_int(env, "DEEPSEEK_MAX_TOKENS", 1800),
            thinking_enabled=_env_bool(env, "DEEPSEEK_THINKING_ENABLED", False),
            reasoning_effort=_clean_optional(env.get("DEEPSEEK_REASONING_EFFORT")),
        )

    @property
    def configured(self) -> bool:
        return bool(self.api_key)


@dataclass(frozen=True)
class DeepSeekAnswer:
    content: str
    provider: str
    model: str
    raw_usage: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@runtime_checkable
class LLMProvider(Protocol):
    """统一 LLM 提供方接口：DeepSeekClient / ClaudeClient 均满足。"""

    @property
    def configured(self) -> bool: ...

    @property
    def model(self) -> str: ...

    def chat(self, messages: list[dict[str, str]]) -> DeepSeekAnswer: ...


class DeepSeekClient:
    def __init__(self, config: DeepSeekConfig | None = None, transport: JsonTransport | None = None) -> None:
        self.config = config or DeepSeekConfig.from_env()
        self._transport = transport or _post_json

    @property
    def configured(self) -> bool:
        return self.config.configured

    @property
    def model(self) -> str:
        return self.config.model

    def chat(self, messages: list[dict[str, str]]) -> DeepSeekAnswer:
        if not self.config.configured or not self.config.api_key:
            raise ProviderConfigurationError("DeepSeek API key is not configured.")
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "thinking": {"type": "enabled" if self.config.thinking_enabled else "disabled"},
            "stream": False,
        }
        if self.config.thinking_enabled:
            if self.config.reasoning_effort:
                payload["reasoning_effort"] = self.config.reasoning_effort
        headers = _auth_json_headers(self.config.api_key)
        data = self._transport(
            f"{self.config.base_url}/chat/completions",
            headers,
            payload,
            self.config.timeout_seconds,
        )
        content = _extract_chat_content(data)
        return DeepSeekAnswer(
            content=content,
            provider="deepseek",
            model=self.config.model,
            raw_usage=data.get("usage") if isinstance(data.get("usage"), dict) else None,
        )


@dataclass(frozen=True)
class ClaudeConfig:
    api_key: str | None
    base_url: str = DEFAULT_ANTHROPIC_BASE_URL
    model: str = DEFAULT_ANTHROPIC_MODEL
    timeout_seconds: float = 120.0
    max_tokens: int = 1800

    @classmethod
    def from_env(cls) -> "ClaudeConfig":
        env = _env_with_dotenv()
        return cls(
            api_key=_clean_secret(env.get("ANTHROPIC_API_KEY")),
            base_url=(env.get("ANTHROPIC_BASE_URL") or DEFAULT_ANTHROPIC_BASE_URL).rstrip("/"),
            model=env.get("ANTHROPIC_MODEL") or env.get("CLAUDE_MODEL") or DEFAULT_ANTHROPIC_MODEL,
            timeout_seconds=_env_float(env, "ANTHROPIC_TIMEOUT_SECONDS", 120.0),
            max_tokens=_env_int(env, "ANTHROPIC_MAX_TOKENS", 1800),
        )

    @property
    def configured(self) -> bool:
        return bool(self.api_key)


class ClaudeClient:
    """Anthropic Messages API（api.anthropic.com/v1/messages），复用手写 _post_json，同步非流式。"""

    def __init__(self, config: ClaudeConfig | None = None, transport: JsonTransport | None = None) -> None:
        self.config = config or ClaudeConfig.from_env()
        self._transport = transport or _post_json

    @property
    def configured(self) -> bool:
        return self.config.configured

    @property
    def model(self) -> str:
        return self.config.model

    def chat(self, messages: list[dict[str, str]]) -> DeepSeekAnswer:
        if not self.config.configured or not self.config.api_key:
            raise ProviderConfigurationError("Anthropic API key is not configured.")
        system_parts = [m["content"] for m in messages if m.get("role") == "system"]
        chat_messages = [m for m in messages if m.get("role") != "system"]
        payload: dict[str, Any] = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "messages": chat_messages,
        }
        if system_parts:
            payload["system"] = "\n\n".join(system_parts)
        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        data = self._transport(
            f"{self.config.base_url}/v1/messages",
            headers,
            payload,
            self.config.timeout_seconds,
        )
        content = _extract_claude_content(data)
        return DeepSeekAnswer(
            content=content,
            provider="claude",
            model=self.config.model,
            raw_usage=data.get("usage") if isinstance(data.get("usage"), dict) else None,
        )


def resolve_provider(name: str | None = None) -> LLMProvider:
    """provider 优先级：显式参数 > 环境变量 HD_LLM_PROVIDER > 默认 deepseek。"""
    choice = (name or os.environ.get("HD_LLM_PROVIDER") or "deepseek").strip().lower()
    if choice == "claude":
        return ClaudeClient()
    return DeepSeekClient()


@dataclass(frozen=True)
class MiniMaxImageConfig:
    api_key: str | None
    endpoint: str = DEFAULT_MINIMAX_IMAGE_ENDPOINT
    model: str = DEFAULT_MINIMAX_IMAGE_MODEL
    timeout_seconds: float = 120.0
    response_format: str = "base64"

    @classmethod
    def from_env(cls) -> "MiniMaxImageConfig":
        env = _env_with_dotenv()
        return cls(
            api_key=_clean_secret(env.get("MINIMAX_API_KEY")),
            endpoint=env.get("MINIMAX_IMAGE_ENDPOINT") or DEFAULT_MINIMAX_IMAGE_ENDPOINT,
            model=env.get("MINIMAX_IMAGE_MODEL") or DEFAULT_MINIMAX_IMAGE_MODEL,
            timeout_seconds=_env_float(env, "MINIMAX_TIMEOUT_SECONDS", 120.0),
            response_format=env.get("MINIMAX_RESPONSE_FORMAT") or "base64",
        )

    @property
    def configured(self) -> bool:
        return bool(self.api_key)


@dataclass(frozen=True)
class MiniMaxImageResult:
    image_url: str
    provider: str
    model: str
    prompt: str
    response_format: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MiniMaxImageClient:
    def __init__(self, config: MiniMaxImageConfig | None = None, transport: JsonTransport | None = None) -> None:
        self.config = config or MiniMaxImageConfig.from_env()
        self._transport = transport or _post_json

    def generate(self, prompt: str, *, aspect_ratio: str = "3:4") -> MiniMaxImageResult:
        if not self.config.configured or not self.config.api_key:
            raise ProviderConfigurationError("MiniMax API key is not configured.")
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "response_format": self.config.response_format,
            "n": 1,
        }
        headers = _auth_json_headers(self.config.api_key)
        data = self._transport(self.config.endpoint, headers, payload, self.config.timeout_seconds)
        image_url = _extract_minimax_image(data)
        return MiniMaxImageResult(
            image_url=image_url,
            provider="minimax",
            model=self.config.model,
            prompt=prompt,
            response_format=self.config.response_format,
        )


def external_provider_status() -> dict[str, Any]:
    # 死线：这里的输出绝不回显任何 key 或 key 子串（有单测断言守着）。
    deepseek = DeepSeekConfig.from_env()
    claude = ClaudeConfig.from_env()
    minimax = MiniMaxImageConfig.from_env()
    return {
        "deepseek": {
            "configured": deepseek.configured,
            "model": deepseek.model,
            "base_url": deepseek.base_url,
        },
        "claude": {
            "configured": claude.configured,
            "model": claude.model,
            "base_url": claude.base_url,
        },
        "minimax": {
            "configured": minimax.configured,
            "model": minimax.model,
            "endpoint": minimax.endpoint,
            "response_format": minimax.response_format,
        },
    }


def _post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=body, headers=headers, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8")
    except HTTPError as exc:
        details = _safe_error_body(exc)
        raise ProviderRequestError(f"Provider returned HTTP {exc.code}: {details}") from exc
    except URLError as exc:
        raise ProviderRequestError(f"Provider request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise ProviderRequestError("Provider request timed out.") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProviderResponseError("Provider returned non-JSON response.") from exc
    if not isinstance(data, dict):
        raise ProviderResponseError("Provider returned an unexpected JSON payload.")
    return data


def _auth_json_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _extract_chat_content(data: dict[str, Any]) -> str:
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ProviderResponseError("DeepSeek response did not include choices.")
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    if not isinstance(message, dict):
        raise ProviderResponseError("DeepSeek response did not include a message.")
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, list):
        text = "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and isinstance(item.get("text"), str)
        ).strip()
        if text:
            return text
    raise ProviderResponseError("DeepSeek response did not include answer content.")


def _extract_claude_content(data: dict[str, Any]) -> str:
    blocks = data.get("content")
    if not isinstance(blocks, list) or not blocks:
        raise ProviderResponseError("Claude response did not include content.")
    text = "".join(
        block.get("text", "")
        for block in blocks
        if isinstance(block, dict) and block.get("type") == "text" and isinstance(block.get("text"), str)
    ).strip()
    if not text:
        raise ProviderResponseError("Claude response did not include answer text.")
    return text


def _extract_minimax_image(data: dict[str, Any]) -> str:
    base_resp = data.get("base_resp")
    if isinstance(base_resp, dict) and base_resp.get("status_code") not in (None, 0, "0"):
        status_msg = base_resp.get("status_msg") or "MiniMax image generation failed."
        raise ProviderRequestError(str(status_msg))
    candidates: list[Any] = []
    for container in (data, data.get("data")):
        if not isinstance(container, dict):
            continue
        for key in (
            "image_url",
            "image_urls",
            "images",
            "image_base64",
            "base64",
            "image",
        ):
            value = container.get(key)
            if value is not None:
                candidates.append(value)
    image = _first_image_candidate(candidates)
    if not image:
        raise ProviderResponseError("MiniMax response did not include an image.")
    return _normalize_image_payload(image)


def _first_image_candidate(candidates: list[Any]) -> str | None:
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
        if isinstance(candidate, dict):
            nested = _first_image_candidate(list(candidate.values()))
            if nested:
                return nested
        if isinstance(candidate, list):
            nested = _first_image_candidate(candidate)
            if nested:
                return nested
    return None


def _normalize_image_payload(value: str) -> str:
    if value.startswith(("http://", "https://", "data:image/")):
        return value
    return f"data:image/jpeg;base64,{value}"


def _env_with_dotenv() -> dict[str, str]:
    env = dict(os.environ)
    for path in _dotenv_candidates():
        if not path.exists():
            continue
        for key, value in _parse_dotenv(path).items():
            env.setdefault(key, value)
    return env


def runtime_environment() -> dict[str, str]:
    """Return process environment merged with local `.env`, with process values taking precedence."""
    return _env_with_dotenv()


def _dotenv_candidates() -> tuple[Path, ...]:
    package_root = Path(__file__).resolve().parent.parent
    return (Path.cwd() / ".env", package_root / ".env")


def _parse_dotenv(path: Path) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            parsed[key] = value
    return parsed


def _clean_secret(value: str | None) -> str | None:
    cleaned = _clean_optional(value)
    return cleaned if cleaned else None


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _env_float(env: dict[str, str], key: str, default: float) -> float:
    try:
        return float(env.get(key, default))
    except (TypeError, ValueError):
        return default


def _env_int(env: dict[str, str], key: str, default: int) -> int:
    try:
        return int(env.get(key, default))
    except (TypeError, ValueError):
        return default


def _env_bool(env: dict[str, str], key: str, default: bool) -> bool:
    value = env.get(key)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _safe_error_body(exc: HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8")
    except Exception:
        return ""
    return body[:500]
