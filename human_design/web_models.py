from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from .schema import HumanDesignChart, LLMProductPackage


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class UserProfile:
    user_id: str
    display_name: str | None
    created_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BirthProfile:
    birth_date: str
    birth_time: str | None
    city: str | None
    region: str | None
    country: str | None
    timezone_name: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SavedChart:
    chart_id: str
    user_name: str | None
    birth_profile: BirthProfile
    chart: HumanDesignChart
    bodygraph_svg_url: str
    bodygraph_svg: str
    created_at_utc: str

    def to_dict(self, *, include_svg: bool = False) -> dict[str, Any]:
        payload = {
            "chart_id": self.chart_id,
            "user_name": self.user_name,
            "birth_profile": self.birth_profile.to_dict(),
            "chart": self.chart.to_dict(),
            "bodygraph_svg_url": self.bodygraph_svg_url,
            "created_at_utc": self.created_at_utc,
        }
        if include_svg:
            payload["bodygraph_svg"] = self.bodygraph_svg
        return payload


@dataclass(frozen=True)
class ReportPackage:
    report_id: str
    chart_id: str
    report_type: str
    focus: str
    depth: str
    package: LLMProductPackage
    body_energy: dict[str, Any] | None
    export_markdown: str
    created_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "chart_id": self.chart_id,
            "report_type": self.report_type,
            "focus": self.focus,
            "depth": self.depth,
            "answer_markdown": self.package.answer_markdown,
            "citations": [citation.to_dict() for citation in self.package.answer_citations],
            "context_blocks": [block.to_dict() for block in self.package.context_blocks],
            "suggested_followups": list(self.package.suggested_followups),
            "session_state": self.package.session_state.to_dict(),
            "body_energy": self.body_energy,
            "export_markdown": self.export_markdown,
            "created_at_utc": self.created_at_utc,
        }


@dataclass(frozen=True)
class GeneratedVisual:
    image_id: str
    chart_id: str
    provider: str
    model: str | None
    prompt: str
    image_url: str | None
    fallback_bodygraph_svg_url: str
    provider_configured: bool
    created_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str
    created_at_utc: str
    citations: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ChatSession:
    session_id: str
    chart_id: str
    focus: str
    messages: tuple[ChatMessage, ...]
    created_at_utc: str
    updated_at_utc: str

    def append(self, *messages: ChatMessage, focus: str | None = None) -> "ChatSession":
        now = utc_now_iso()
        return ChatSession(
            session_id=self.session_id,
            chart_id=self.chart_id,
            focus=focus or self.focus,
            messages=(*self.messages, *messages),
            created_at_utc=self.created_at_utc,
            updated_at_utc=now,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "chart_id": self.chart_id,
            "focus": self.focus,
            "messages": [message.to_dict() for message in self.messages],
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
