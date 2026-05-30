from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


JsonTransport = Callable[[str, dict[str, str], dict[str, Any], float], dict[str, Any]]

DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-pro"
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


class DeepSeekClient:
    def __init__(self, config: DeepSeekConfig | None = None, transport: JsonTransport | None = None) -> None:
        self.config = config or DeepSeekConfig.from_env()
        self._transport = transport or _post_json

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
    deepseek = DeepSeekConfig.from_env()
    minimax = MiniMaxImageConfig.from_env()
    return {
        "deepseek": {
            "configured": deepseek.configured,
            "model": deepseek.model,
            "base_url": deepseek.base_url,
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
