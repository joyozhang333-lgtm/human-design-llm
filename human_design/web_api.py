from __future__ import annotations

import re
from datetime import date, time
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .body_energy import build_body_energy_profile
from .bodygraph import render_bodygraph_svg
from .deep_synthesis import build_deep_synthesis_profile
from .engine import calculate_chart
from .generation import generate_detail_reading, generate_main_reading
from .generation.facts import extract_chart_facts
from .generation.validator import validate_and_repair
from .input import InputNormalizationError, normalize_birth_input
from .interpretation_maps import build_interpretation_map, map_context_text, map_type_from_focus
from .labels import (
    CENTER_LABELS,
    display_authority,
    display_authority_professional,
    display_channel_label,
    display_definition,
    display_gate_theme,
    display_incarnation_cross,
    display_not_self,
    display_profile,
    display_signature,
    display_strategy,
    display_type,
    normalize_center_title,
)
from .product import build_llm_product
from .report_maps import build_report_overview
from .reading import generate_reading
from .providers import (
    DeepSeekClient,
    MiniMaxImageClient,
    ProviderConfigurationError,
    ProviderError,
    external_provider_status,
)
from .version import VERSION
from .web_models import (
    BirthProfile,
    ChatMessage,
    ChatSession,
    GeneratedVisual,
    ReportPackage,
    SavedChart,
    utc_now_iso,
)


REPORT_CONFIG = {
    "overview": {
        "focus": "overview",
        "depth": "standard",
        "question": "请给我一份完整但清晰的人类图总览。",
    },
    "body-energy": {
        "focus": "growth",
        "depth": "deep",
        "question": "请重点解读我的身体资源、九大中心、通道、闸门和能量卡点。",
    },
    "career": {
        "focus": "career",
        "depth": "deep",
        "question": "我最适合怎么工作、赚钱、选方向？",
    },
    "talent": {
        "focus": "talent",
        "depth": "deep",
        "question": "请深挖我的天赋、主航道、资源配置方式和容易误用的消耗链。",
    },
    "relationship": {
        "focus": "relationship",
        "depth": "deep",
        "question": "请解读我在关系里的连接方式、边界、情绪和沟通模式。",
    },
    "deep": {
        "focus": "talent",
        "depth": "deep",
        "question": "请给我一份可长期阅读的人类图深度解读。",
    },
}


class ChartCreateRequest(BaseModel):
    user_name: str | None = Field(default=None, max_length=80)
    gender: str | None = Field(default=None, max_length=20)
    birth_date: str = Field(description="YYYY-MM-DD")
    birth_time: str | None = Field(default=None, description="HH:MM or HH:MM:SS")
    city: str | None = None
    region: str | None = None
    country: str | None = None
    timezone_name: str | None = Field(default=None, description="IANA timezone")


class ReportRequest(BaseModel):
    chart_id: str
    report_type: str = "overview"
    depth: str | None = None
    question: str | None = None


class ChatRequest(BaseModel):
    chart_id: str
    question: str = Field(min_length=1)
    session_id: str | None = None
    focus: str | None = None
    depth: str = "deep"
    map_type: str | None = None
    map_item_key: str | None = None
    question_id: str | None = None
    entry_source: str | None = None
    synthesis_mode: str | None = None
    external_ai_consent: bool = False


class InterpretationMapRequest(BaseModel):
    chart_id: str
    map_type: str = "talent"
    depth: str = "deep"


class MainReadingRequest(BaseModel):
    chart_id: str


class DetailReadingRequest(BaseModel):
    chart_id: str
    key: str


class ImageGenerationRequest(BaseModel):
    chart_id: str
    prompt: str | None = Field(default=None, max_length=1200)
    aspect_ratio: str = Field(default="3:4", max_length=12)


class HumanDesignWebStore:
    def __init__(self) -> None:
        self.charts: dict[str, SavedChart] = {}
        self.reports: dict[str, ReportPackage] = {}
        self.sessions: dict[str, ChatSession] = {}
        self.visuals: dict[str, GeneratedVisual] = {}

    def save_chart(self, chart: SavedChart) -> None:
        self.charts[chart.chart_id] = chart

    def get_chart(self, chart_id: str) -> SavedChart:
        chart = self.charts.get(chart_id)
        if chart is None:
            raise HTTPException(status_code=404, detail={"code": "chart_not_found", "message": "没有找到这张人类图。"})
        return chart

    def save_report(self, report: ReportPackage) -> None:
        self.reports[report.report_id] = report

    def get_session(self, session_id: str | None, chart_id: str, focus: str) -> ChatSession:
        next_session_id = session_id
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            if session.chart_id == chart_id:
                return session
            next_session_id = None
        now = utc_now_iso()
        return ChatSession(
            session_id=next_session_id or f"session_{uuid4().hex}",
            chart_id=chart_id,
            focus=focus,
            messages=(),
            created_at_utc=now,
            updated_at_utc=now,
        )

    def save_session(self, session: ChatSession) -> None:
        self.sessions[session.session_id] = session

    def save_visual(self, visual: GeneratedVisual) -> None:
        self.visuals[visual.image_id] = visual


def create_app(store: HumanDesignWebStore | None = None) -> FastAPI:
    active_store = store or HumanDesignWebStore()
    app = FastAPI(
        title="Human Design Web/App API",
        version=VERSION,
        description="简体中文人类图 Web/App 产品 API：排盘、出图、报告、问答。",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "product": "human-design-web-app"}

    @app.get("/api/product/config")
    def product_config() -> dict[str, Any]:
        return {
            "product_version": f"V{VERSION.rsplit('.', 1)[0]}",
            "api_version": VERSION,
            "report_types": list(REPORT_CONFIG),
            "map_types": ["body", "channels", "wealth", "talent", "relationship", "mission", "professional"],
            "required_birth_fields": ["birth_date", "birth_time", "city/region"],
            "precision_policy": "birthday_only_is_guidance_not_formal_chart",
            "terminology": {
                "sacral": "荐骨中心",
                "ajna": "阿姬娜中心",
                "throat": "喉咙中心",
            },
        }

    @app.get("/api/product/providers")
    def product_providers() -> dict[str, Any]:
        return external_provider_status()

    @app.post("/api/charts")
    def create_chart(request: ChartCreateRequest) -> dict[str, Any]:
        birth_datetime = _compose_birth_datetime(request.birth_date, request.birth_time)
        if not request.timezone_name and not any((request.city, request.region, request.country)):
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "timezone_or_location_required",
                    "message": "正式人类图需要出生时间和出生地。仅生日只能做低精度引导，不能生成正式 BodyGraph。",
                    "required_fields": ["birth_time", "city/region"],
                },
            )
        try:
            normalized = normalize_birth_input(
                birth_datetime,
                timezone_name=request.timezone_name,
                city=request.city,
                region=request.region,
                country=request.country,
            )
            chart = calculate_chart(normalized)
        except (InputNormalizationError, ValueError) as exc:
            raise HTTPException(
                status_code=422,
                detail={"code": "birth_input_invalid", "message": str(exc)},
            ) from exc

        chart_id = f"chart_{uuid4().hex}"
        title = request.user_name or "我的人类图"
        # Web BodyGraph stays graphic-only; the long reading ships via /reading-book.
        svg = render_bodygraph_svg(chart, title=title, include_booklet=False)
        bodygraph_url = f"/api/charts/{chart_id}/bodygraph.svg"
        saved = SavedChart(
            chart_id=chart_id,
            user_name=request.user_name,
            birth_profile=BirthProfile(
                birth_date=request.birth_date,
                birth_time=request.birth_time,
                gender=request.gender,
                city=request.city,
                region=request.region,
                country=request.country,
                timezone_name=request.timezone_name,
            ),
            chart=chart,
            bodygraph_svg_url=bodygraph_url,
            bodygraph_svg=svg,
            created_at_utc=utc_now_iso(),
        )
        active_store.save_chart(saved)
        payload = saved.to_dict(include_svg=True)
        payload["precision_warnings"] = list(chart.input.warnings)
        payload["display_summary"] = _display_summary(chart)
        payload["guidance"] = _chart_guidance(chart)
        return payload

    @app.get("/api/charts/{chart_id}")
    def get_chart(chart_id: str) -> dict[str, Any]:
        chart = active_store.get_chart(chart_id)
        payload = chart.to_dict(include_svg=False)
        payload["precision_warnings"] = list(chart.chart.input.warnings)
        payload["display_summary"] = _display_summary(chart.chart)
        payload["guidance"] = _chart_guidance(chart.chart)
        return payload

    @app.get("/api/charts/{chart_id}/bodygraph.svg")
    def get_bodygraph_svg(chart_id: str) -> Response:
        chart = active_store.get_chart(chart_id)
        return Response(content=chart.bodygraph_svg, media_type="image/svg+xml")

    @app.get("/api/charts/{chart_id}/reading-book")
    def get_reading_book(chart_id: str) -> dict[str, Any]:
        saved_chart = active_store.get_chart(chart_id)
        return _build_reading_book(saved_chart)

    @app.post("/api/reports")
    def create_report(request: ReportRequest) -> dict[str, Any]:
        saved_chart = active_store.get_chart(request.chart_id)
        config = _report_config(request.report_type)
        focus = config["focus"]
        depth = request.depth or config["depth"]
        question = request.question or config["question"]
        package = build_llm_product(
            saved_chart.chart,
            focus=focus,
            question=question,
            citation_mode="none",
            depth=depth,
        )
        body_energy = (
            build_body_energy_profile(saved_chart.chart).to_dict()
            if request.report_type in {"body-energy", "deep", "talent"}
            else None
        )
        deep_synthesis = (
            build_deep_synthesis_profile(saved_chart.chart, focus=focus, question=question).to_dict()
            if request.report_type in {"talent", "deep", "career"} or depth == "deep"
            else None
        )
        export_markdown = _compose_export_markdown(package.answer_markdown, body_energy, deep_synthesis)
        report = ReportPackage(
            report_id=f"report_{uuid4().hex}",
            chart_id=request.chart_id,
            report_type=request.report_type,
            focus=focus,
            depth=depth,
            package=package,
            body_energy=body_energy,
            deep_synthesis=deep_synthesis,
            export_markdown=export_markdown,
            created_at_utc=utc_now_iso(),
        )
        active_store.save_report(report)
        return report.to_dict()

    @app.post("/api/readings/main")
    def create_main_reading(request: MainReadingRequest) -> dict[str, Any]:
        saved_chart = active_store.get_chart(request.chart_id)
        user_terms = tuple(term for term in (saved_chart.user_name,) if term)
        # LLM 相关错误在 generation 层内部消化（对外只给 fallback 文案，原始错误只进脱敏日志）。
        # The main report must be instant and private. External AI is reserved for
        # the consultation endpoint after the user has explicitly opted in.
        reading = generate_main_reading(saved_chart.chart, mode="fallback", user_terms=user_terms)
        return {
            "l1": reading.l1,
            "l2": reading.l2,
            "signature": reading.signature,
            "not_self": reading.not_self,
            "detail_sections": [dict(section) for section in reading.detail_sections],
            "explore": [dict(entry) for entry in reading.explore],
            "generation_mode": reading.generation_mode,
        }

    @app.post("/api/readings/detail")
    def create_detail_reading(request: DetailReadingRequest) -> dict[str, Any]:
        saved_chart = active_store.get_chart(request.chart_id)
        try:
            detail = generate_detail_reading(saved_chart.chart, request.key)
        except KeyError as exc:
            raise HTTPException(
                status_code=422,
                detail={"code": "detail_key_invalid", "message": f"未知的细读入口：{request.key}"},
            ) from exc
        return {
            "title": detail.title,
            "body": detail.body,
            "generation_mode": detail.generation_mode,
        }

    @app.post("/api/interpretation-maps")
    def create_interpretation_map(request: InterpretationMapRequest) -> dict[str, Any]:
        saved_chart = active_store.get_chart(request.chart_id)
        try:
            package = build_interpretation_map(
                saved_chart.chart,
                map_type=request.map_type,
                depth=request.depth,
                chart_id=request.chart_id,
            )
        except KeyError as exc:
            raise HTTPException(
                status_code=422,
                detail={"code": "map_type_invalid", "message": f"未知解读地图：{request.map_type}"},
            ) from exc
        payload = package.to_dict()
        payload["overview"] = build_report_overview(package.map_type, saved_chart.chart)
        payload["generation_mode"] = "instant"
        return payload

    @app.post("/api/chat")
    def chat(request: ChatRequest) -> dict[str, Any]:
        saved_chart = active_store.get_chart(request.chart_id)
        focus = request.focus or _infer_focus(request.question)
        map_package = build_interpretation_map(
            saved_chart.chart,
            map_type=request.map_type or _infer_map_type(request.question, focus),
            depth=request.depth,
            chart_id=request.chart_id,
        )
        package = build_llm_product(
            saved_chart.chart,
            focus=focus,
            question=request.question,
            citation_mode="none",
            depth=request.depth,
        )
        session = active_store.get_session(request.session_id, request.chart_id, focus)
        answer_markdown, answer_provider, answer_model, provider_configured = _generate_chat_answer(
            saved_chart=saved_chart,
            package=package,
            map_package=map_package,
            session=session,
            question=request.question,
            map_item_key=request.map_item_key,
            allow_external_ai=request.external_ai_consent,
        )
        user_message = ChatMessage(
            role="user",
            content=request.question,
            created_at_utc=utc_now_iso(),
        )
        assistant_message = ChatMessage(
            role="assistant",
            content=answer_markdown,
            citations=tuple(citation.to_dict() for citation in package.answer_citations),
            created_at_utc=utc_now_iso(),
        )
        session = session.append(user_message, assistant_message, focus=focus)
        active_store.save_session(session)
        return {
            "session_id": session.session_id,
            "chart_id": request.chart_id,
            "focus": focus,
            "answer_markdown": answer_markdown,
            "answer_provider": answer_provider,
            "answer_model": answer_model,
            "provider_configured": provider_configured,
            "entry_source": request.entry_source,
            "synthesis_mode": request.synthesis_mode,
            "external_ai_consent": request.external_ai_consent,
            "citations": [citation.to_dict() for citation in package.answer_citations],
            "map_context": {
                "map_type": map_package.map_type,
                "title": map_package.title,
                "sections": [section.to_dict() for section in map_package.sections],
                "retrieved_knowledge": [atom.to_dict() for atom in map_package.retrieved_knowledge],
            },
            "suggested_followups": list(package.suggested_followups),
            "session": session.to_dict(),
        }

    @app.post("/api/images/reading-visual")
    def create_reading_visual(request: ImageGenerationRequest) -> dict[str, Any]:
        saved_chart = active_store.get_chart(request.chart_id)
        prompt = _build_visual_prompt(saved_chart, request.prompt)
        config = external_provider_status()["minimax"]
        if not config["configured"]:
            visual = _fallback_visual(saved_chart, prompt, config, provider_configured=False)
            active_store.save_visual(visual)
            return visual.to_dict()
        try:
            result = MiniMaxImageClient().generate(prompt, aspect_ratio=request.aspect_ratio)
        except ProviderConfigurationError:
            visual = _fallback_visual(saved_chart, prompt, config, provider_configured=False)
            active_store.save_visual(visual)
            return visual.to_dict()
        except ProviderError:
            visual = _fallback_visual(saved_chart, prompt, config, provider_configured=True)
            active_store.save_visual(visual)
            return visual.to_dict()
        visual = GeneratedVisual(
            image_id=f"image_{uuid4().hex}",
            chart_id=request.chart_id,
            provider=result.provider,
            model=result.model,
            prompt=prompt,
            image_url=result.image_url,
            fallback_bodygraph_svg_url=saved_chart.bodygraph_svg_url,
            provider_configured=True,
            created_at_utc=utc_now_iso(),
        )
        active_store.save_visual(visual)
        return visual.to_dict()

    return app


def _fallback_visual(
    saved_chart: SavedChart,
    prompt: str,
    config: dict[str, Any],
    *,
    provider_configured: bool,
) -> GeneratedVisual:
    return GeneratedVisual(
        image_id=f"image_{uuid4().hex}",
        chart_id=saved_chart.chart_id,
        provider="minimax",
        model=config.get("model"),
        prompt=prompt,
        image_url=None,
        fallback_bodygraph_svg_url=saved_chart.bodygraph_svg_url,
        provider_configured=provider_configured,
        created_at_utc=utc_now_iso(),
    )


def _compose_birth_datetime(birth_date: str, birth_time: str | None) -> str:
    if not birth_time:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "birth_time_required",
                "message": "正式人类图需要出生时间。仅生日可以进入低精度引导，但不能生成正式 BodyGraph。",
                "required_fields": ["birth_time"],
            },
        )
    try:
        parsed_date = date.fromisoformat(birth_date)
        parsed_time = time.fromisoformat(birth_time)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "birth_datetime_invalid", "message": "出生日期或时间格式不正确，请使用 YYYY-MM-DD 与 HH:MM。"},
        ) from exc
    return f"{parsed_date.isoformat()}T{parsed_time.isoformat()}"


def _report_config(report_type: str) -> dict[str, str]:
    config = REPORT_CONFIG.get(report_type)
    if config is None:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "report_type_invalid",
                "message": f"未知报告类型：{report_type}",
                "allowed": list(REPORT_CONFIG),
            },
        )
    return config


def _infer_focus(question: str) -> str:
    if any(keyword in question for keyword in ("天赋", "优势", "潜能", "使命", "主航道", "深挖", "挖掘")):
        return "talent"
    if any(keyword in question for keyword in ("职业", "工作", "赚钱", "收入", "方向", "事业")):
        return "career"
    if any(keyword in question for keyword in ("关系", "亲密", "伴侣", "沟通", "边界")):
        return "relationship"
    if any(keyword in question for keyword in ("决定", "要不要", "该不该", "选择", "时机")):
        return "decision"
    if any(keyword in question for keyword in ("身体", "能量", "中心", "通道", "闸门", "卡点", "淤堵", "内耗")):
        return "growth"
    return "overview"


def _infer_map_type(question: str, focus: str) -> str:
    if any(keyword in question for keyword in ("通道", "能力线路")):
        return "channels"
    if any(keyword in question for keyword in ("使命", "人生主轴", "轮回交叉", "人生主题")):
        return "mission"
    return map_type_from_focus(focus)


def _generate_chat_answer(
    *,
    saved_chart: SavedChart,
    package,
    map_package,
    session: ChatSession,
    question: str,
    map_item_key: str | None,
    allow_external_ai: bool,
) -> tuple[str, str, str | None, bool]:
    def normalize(text: str) -> str:
        cleaned = _normalize_chat_answer(_professionalize_authority_terms(text, saved_chart.chart))
        return _ensure_progressive_followup(
            cleaned,
            session=session,
            map_package=map_package,
            question=question,
            map_item_key=map_item_key,
        )

    provider_status = external_provider_status()["deepseek"]
    if not allow_external_ai:
        return (
            normalize(_fallback_map_answer(map_package, question, map_item_key)),
            "local-fallback",
            None,
            bool(provider_status["configured"]),
        )
    if not provider_status["configured"]:
        return normalize(_fallback_map_answer(map_package, question, map_item_key)), "local-fallback", None, False
    messages = _build_deepseek_messages(saved_chart, package, map_package, session, question, map_item_key)
    facts = extract_chart_facts(
        saved_chart.chart,
        layer="CHAT",
        focus=map_package.map_type,
        user_terms=tuple(term for term in (saved_chart.user_name, question) if term),
    )
    client = DeepSeekClient()
    try:
        answer_text, status = validate_and_repair(
            messages,
            facts,
            lambda current_messages: client.chat(current_messages).content,
            max_repair=1,
        )
    except ProviderConfigurationError:
        return normalize(_fallback_map_answer(map_package, question, map_item_key)), "local-fallback", None, False
    except ProviderError:
        return normalize(
            _fallback_with_provider_note(_fallback_map_answer(map_package, question, map_item_key))
        ), "local-fallback", None, True
    if status == "fallback_after_repair_fail" or not answer_text.strip():
        return normalize(_fallback_map_answer(map_package, question, map_item_key)), "local-fallback", None, True
    return normalize(answer_text), "deepseek", client.model, True


def _build_deepseek_messages(
    saved_chart: SavedChart,
    package,
    map_package,
    session: ChatSession,
    question: str,
    map_item_key: str | None,
) -> list[dict[str, str]]:
    system = "\n".join(
        (
            package.system_prompt,
            "你现在面向简体中文用户，回答必须自然、具体、可执行。",
            "必须使用目标术语：荐骨中心、荐骨权威、阿姬娜中心、喉咙中心；不要使用骶骨中心、额骨中心、阿扎那。",
            "只能基于下方 chart facts、reading context 和历史会话作答；不知道就说明无法从当前图表推出。",
            "不要把三个或更多独立闸门拼成自创的能力轴、回路、系统、模块或组合；只能引用当前事实里真实存在的完整通道。",
            "已定义通道本来就稳定存在。邀请、认可和策略只影响进入事情及表达时机，不能说它们会激活、启动或创造通道。",
            "Authority 的专业名称必须逐字使用当前图表事实中的精确名称，不能简写，也不能换成另一种 Authority。",
            "优先引用当前地图条目和资料依据；回答要像给用户看的解读，不要输出内部字段名。",
            "深度解读必须做结构叠加：不要只按人生角色、类型或单个闸门回答；要说明真实通道、已定义/开放中心、关键闸门如何共同作用。",
            "如果当前地图条目提供特质诊断层，必须基于活出来、盲区、卡住状态和卡住原因继续展开；不要复制卡片原文，要围绕用户问题生成新的深度回答。",
            "点击追问时，不能只补充当前卡片；至少联动两个其他结构，例如身体回应、开放中心、通道、人生角色、财富边界、关系模式或使命主题。",
            "回答要像一位成熟的人类图咨询师在继续聊天，不像报告、课程讲义或百科词条。",
            "不要把前面卡片重新整理一遍；每次只推进一层：更具体的现实场景、更尖锐的盲区、更可验证的练习，或一个能继续深聊的问题。",
            "历史里咨询师已经问过、用户已经回答的问题，不得原样或换词重复；结尾必须根据用户本轮新增的事实推进下一层。",
            "如果用户的问题很大，先收窄到当下最关键的一层，并用一句话说明为什么先看这一层。",
            "先看身体真实反应，再看心理模式、关系环境和现实行动四层如何互相影响。",
            "内容底层可以吸收整合心理学、儒释道和佛法见地，但不要堆术语；要帮助用户少一点自我证明和执着，多一点鲜活、清醒、落地的生命力。",
            "当用户问天赋、使命、职业主航道或深挖时，必须输出具体天赋模块、误用方式、可观察练习，避免可套给所有人的建议。",
            "不要输出医疗、法律、财务或确定性命运承诺。",
            *package.assistant_instructions,
            "本轮聊天的最高优先级：不要输出 Markdown 标题、编号大纲、加粗符号、代码块或长列表。",
            "段落要短，每段 2-4 句；不要一次性给标准答案，最后只问 1 个能继续深入的具体问题。",
        )
    )
    context = _context_block_text(package)
    history = _chat_history_text(session)
    user = "\n\n".join(
        (
            f"用户问题：{question}",
            "【当前图表事实】\n" + _chart_fact_digest(saved_chart.chart),
            "【当前解读地图】\n" + map_context_text(map_package, selected_item_key=map_item_key),
            "【可引用解读上下文】\n" + context,
            "【本轮历史】\n" + history if history else "【本轮历史】\n暂无。",
            "请输出自然聊天文本，不要输出 Markdown。控制在 300-550 字。结构：先接住问题；再指出一个盘面机制；然后给一个现实验证练习；最后只问一个继续深聊的问题。",
        )
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _context_block_text(package, *, max_chars: int = 14000) -> str:
    lines: list[str] = []
    for block in package.context_blocks:
        lines.append(f"## {block.title}")
        lines.append(block.content)
    text = "\n".join(lines).strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n\n[上下文已截断：请只基于已提供内容作答]"


def _chat_history_text(session: ChatSession, *, limit: int = 8) -> str:
    if not session.messages:
        return ""
    lines = []
    for message in session.messages[-limit:]:
        role = "用户" if message.role == "user" else "咨询师"
        lines.append(f"{role}: {message.content}")
    return "\n".join(lines)


def _chart_fact_digest(chart) -> str:
    summary = _display_summary(chart)
    defined_centers = [
        normalize_center_title(CENTER_LABELS.get(center.code, center.label))
        for center in chart.centers
        if center.defined
    ]
    open_centers = [
        normalize_center_title(CENTER_LABELS.get(center.code, center.label))
        for center in chart.centers
        if not center.defined
    ]
    channels = [f"{channel.code}「{display_channel_label(channel.code, channel.label)}」" for channel in chart.channels]
    gates = [
        f"{gate.gate}「{display_gate_theme(gate.gate, gate.theme)}」({normalize_center_title(CENTER_LABELS.get(gate.center, gate.center))})"
        for gate in chart.activated_gates
    ]
    return "\n".join(
        (
            f"类型：{summary['type']}",
            f"策略：{summary['strategy']}",
            f"Authority：{summary['authority_professional']}",
            f"人生角色：{summary['profile']}",
            f"定义：{summary['definition']}",
            f"签名/非自己主题：{summary['signature']} / {summary['not_self_theme']}",
            f"使命名称：{summary['incarnation_cross']}",
            "已定义中心：" + ("、".join(defined_centers) if defined_centers else "无"),
            "开放中心：" + ("、".join(open_centers) if open_centers else "无"),
            "通道：" + ("、".join(channels) if channels else "无"),
            "闸门：" + ("、".join(gates[:32]) if gates else "无"),
        )
    )


def _professionalize_authority_terms(text: str, chart) -> str:
    chinese = display_authority(chart.summary.authority.code, chart.summary.authority.label)
    professional = display_authority_professional(chart.summary.authority.code, chart.summary.authority.label)
    normalized = (text or "").replace(chinese, professional).replace("权威", professional)
    duplicate = re.compile(
        rf"{re.escape(professional)}\s*(?:是|为|：|:)?\s*{re.escape(professional)}",
        re.IGNORECASE,
    )
    normalized = duplicate.sub(professional, normalized)
    generic_prefix = re.compile(
        rf"(?<![A-Za-z-])Authority\s*(?:是|为|：|:)?\s*{re.escape(professional)}",
        re.IGNORECASE,
    )
    normalized = generic_prefix.sub(professional, normalized)
    return re.sub(r"[ \t]{2,}", " ", normalized).strip()


def _fallback_with_provider_note(answer_markdown: str) -> str:
    note = (
        "\n\n当前外部问答服务暂时不可用，以下回答由本地结构化解读引擎生成，"
        "仍然基于当前图表事实。"
    )
    return answer_markdown.rstrip() + note


def _fallback_map_answer(map_package, question: str, map_item_key: str | None = None) -> str:
    items = _ordered_map_items(map_package, map_item_key)
    selected = items[0] if items else None
    supporting = items[1:3]
    lines = [f"你的问题：{question}", ""]
    if selected is not None:
        lines.append(
            f"我先不急着给标准答案。这个问题我会先看「{selected.title}」有没有在生活里被用对，"
            "因为人类图里很多困惑不是不知道，而是身体、关系和行动节奏没有对上。"
        )
        lines.append("")
        lines.append(_dialogue_pattern(selected, supporting))
        lines.append("")
        blind_spot = _first_item(selected.blind_spots)
        stuck = _first_item(selected.stuck_patterns)
        if blind_spot or stuck:
            lines.append(
                "盲区不是“你不懂”，而是你可能太快跳到解释，忽略身体已经给出的松紧感。"
                + (f" 盲区：{blind_spot}" if blind_spot else "")
                + (f" 卡住状态：{stuck}" if stuck else "")
            )
            lines.append("")
        cause = _first_item(selected.stuck_causes)
        if cause:
            lines.append(f"为什么会卡住，我会先看这里：{cause}")
            lines.append("")
        practice = _first_item(selected.practices)
        if practice:
            lines.append(f"先做一个小验证，不要急着想通：{practice}")
            lines.append("")
    if supporting:
        support_text = "；".join(f"{item.title}：{_first_sentence(item.user_language)}" for item in supporting)
        lines.append(f"我还会放在旁边一起看：{support_text} 这样就不是单点解释，而是看这个模式怎样牵动你的身体节奏、关系入口和现实选择。")
        lines.append("")
    facts = "；".join(_dialogue_fact_subset(map_package.professional_facts))
    if facts:
        lines.append(f"我看盘时抓的依据是：{facts}。")
        lines.append("")
    lines.append(f"我想继续问你：{_progressive_question(selected, question)}")
    return "\n".join(lines).strip() + "\n"


def _dialogue_pattern(item, supporting) -> str:
    if item.key == "talent.profile-24":
        base = (
            "你要找的不是一个全新的天赋，而是那个已经能做到80分、你却觉得太普通的能力。"
            "2爻容易低估自己天然会的东西，4爻又需要通过信任关系被看见；所以关键不是马上公开证明，"
            "而是先把这个80分能力练到100分，再让作品、案例和熟人网络把你召唤出来。"
        )
    else:
        alive = _first_item(item.embodied_expression)
        base = _trim_text(alive, 220) if alive else _first_sentence(item.user_language)
    if not supporting:
        return base
    support_titles = "、".join(next_item.title for next_item in supporting[:2])
    return f"{base} 这件事还会牵动 {support_titles}，所以不能只看单一特质，要看它怎样影响你的身体节奏、关系入口和现实选择。"


def _dialogue_fact_subset(facts: tuple[str, ...] | list[str]) -> list[str]:
    priority_prefixes = ("类型：", "权威：", "人生角色：", "定义：", "使命名称：", "已定义通道：")
    selected: list[str] = []
    for prefix in priority_prefixes:
        selected.extend(fact for fact in facts if fact.startswith(prefix))
    return selected[:6] or list(facts[:4])


def _next_followup(item, question: str) -> str:
    normalized_question = question.strip()
    for followup in item.followup_questions:
        if followup != normalized_question:
            return followup
    return ""


def _progressive_question(item, question: str) -> str:
    if item is None:
        return "这件事最近最具体发生在哪个场景，是工作、关系、钱，还是身体状态？"
    if item.key == "talent.profile-24":
        return "最近别人反复夸你、但你觉得“这有什么难的”的能力是哪一个？它现在有没有被你做成作品、案例或稳定服务？"
    if "02-14" in item.key or "02-14" in item.title:
        return "最近哪一个方向一想到就有身体力量，哪一个方向只是看起来有资源、但你身体并不想持续投入？"
    if item.key.startswith("wealth."):
        return "你现在赚钱最容易卡住的是定价、承诺、合作边界，还是不知道该把资源投向哪里？"
    if item.key.startswith("relationship."):
        return "你在关系里最常见的卡点，是太快答应、太晚表达边界，还是等对方看懂你？"
    if item.key.startswith("body."):
        return "最近一件让你身体变沉的事是什么？如果只看身体，不看道理，它在拒绝什么？"
    if item.key.startswith("mission."):
        return "你现在最想证明给别人看的东西是什么？如果先不证明，你真正想服务或创造的是什么？"
    next_followup = _next_followup(item, question)
    if next_followup:
        return next_followup
    return "如果只选一个现实场景继续拆，你想先看工作、关系、财富，还是身体能量？"


def _first_item(items) -> str:
    return items[0] if items else ""


def _consultant_summary(item) -> str:
    source = item.user_language.strip()
    if item.stuck_causes:
        source += " " + item.stuck_causes[0]
    return _trim_text(source, 460)


def _first_sentence(text: str) -> str:
    for marker in ("。", "；", "\n"):
        if marker in text:
            return text.split(marker, 1)[0].strip() + "。"
    return _trim_text(text, 120)


def _trim_text(text: str, limit: int) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit].rstrip("，。；、 ") + "。"


def _normalize_chat_answer(text: str) -> str:
    cleaned_lines: list[str] = []
    for raw_line in text.replace("\r\n", "\n").split("\n"):
        line = raw_line.strip()
        if not line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue
        if line.startswith("```"):
            continue
        line = line.lstrip("#").strip() if line.startswith("#") else line
        if line.startswith(">"):
            line = line.lstrip(">").strip()
        line = line.replace("**", "").replace("__", "").replace("`", "")
        for marker in ("- ", "* ", "• "):
            if line.startswith(marker):
                line = line[len(marker) :].strip()
                break
        cleaned_lines.append(line)
    normalized = "\n".join(cleaned_lines).strip()
    while "\n\n\n" in normalized:
        normalized = normalized.replace("\n\n\n", "\n\n")
    return normalized + ("\n" if normalized else "")


def _ensure_progressive_followup(
    text: str,
    *,
    session: ChatSession,
    map_package,
    question: str,
    map_item_key: str | None,
) -> str:
    """Replace a repeated closing question after the user has already answered it."""
    matches = tuple(re.finditer(r"[^。！？?\n]{4,}[？?]", text.rstrip()))
    if not matches:
        return text
    final_match = matches[-1]
    if final_match.end() != len(text.rstrip()):
        return text
    previous_questions = {
        _normalize_question_for_comparison(match.group())
        for message in session.messages
        if message.role == "assistant"
        for match in re.finditer(r"[^。！？?\n]{4,}[？?]", message.content)
    }
    current_followup = _normalize_question_for_comparison(final_match.group())
    if not current_followup or current_followup not in previous_questions:
        return text
    replacement = _progressive_chat_followup(map_package, question, map_item_key)
    prefix = text.rstrip()[: final_match.start()].rstrip()
    return f"{prefix}\n\n{replacement}\n"


def _normalize_question_for_comparison(question: str) -> str:
    return re.sub(r"[\s，。！？?：、“”‘’（）()《》]", "", question)


def _progressive_chat_followup(map_package, question: str, map_item_key: str | None) -> str:
    map_type = getattr(map_package, "map_type", "")
    if any(keyword in question for keyword in ("提前", "忍不住", "冒犯", "立刻指出", "抢着说")):
        return "下一次你想立刻指出问题时，你愿不愿意先确认“对方是否正在邀请我的判断”，再观察表达效果有什么不同？"
    if map_type == "channels":
        return "最近哪一个具体场景最适合用“先确认对象和时机，再使用这项能力”做一次对照实验？"
    if map_type == "talent":
        return "如果只选一个真实案例来验证这项天赋，你会选哪件事，当时谁需要你、你具体改变了什么？"
    if map_type == "relationship":
        return "在最近一次关系拉扯里，你最先越过的是自己的决定节奏、表达边界，还是身体已经出现的拒绝？"
    if map_type == "wealth":
        return "拿最近一笔收入来看，你最想先验证的是价值表达、定价边界，还是承诺过量？"
    if map_type == "mission":
        return "回看最近一年，哪件事同时让你的能力变强、身体更有生命力，也真实影响了别人？"
    if map_type == "body":
        return "最近一次身体明显变紧或变沉时，你当时正在替谁承担什么决定或压力？"
    if map_item_key:
        return "如果拿一个刚发生的真实场景继续拆，你最想验证这里的对象、时机，还是行动方式？"
    return "这轮你补充的信息里，哪一个具体场景最值得我们继续往下拆？"


def _append_optional_markdown_list(lines: list[str], title: str, items) -> None:
    if not items:
        return
    lines.append(title)
    for item in items:
        lines.append(f"- {item}")
    lines.append("")


def _ordered_map_items(map_package, map_item_key: str | None):
    items = [item for section in map_package.sections for item in section.items]
    if not map_item_key:
        return items
    selected = [item for item in items if item.key == map_item_key]
    rest = [item for item in items if item.key != map_item_key]
    return selected + rest


def _build_visual_prompt(saved_chart: SavedChart, user_prompt: str | None) -> str:
    chart = saved_chart.chart
    summary = _display_summary(chart)
    defined_centers = [
        normalize_center_title(CENTER_LABELS.get(center.code, center.label))
        for center in chart.centers
        if center.defined
    ]
    open_centers = [
        normalize_center_title(CENTER_LABELS.get(center.code, center.label))
        for center in chart.centers
        if not center.defined
    ]
    channels = [f"{channel.code} {display_channel_label(channel.code, channel.label)}" for channel in chart.channels[:8]]
    custom = user_prompt.strip() if user_prompt and user_prompt.strip() else "身体能量解读封面"
    return (
        "生成一张适合中文人类图解读产品的高质感视觉封面图，风格成熟、干净、东方纸本质感、温暖大地色。"
        "不要生成密集文字，不要生成错误的人类图闸门数字，不要画医学器官，不要画真实人物照片。"
        "可以用抽象几何、九个能量中心的柔和轮廓、红黑能量线、纸张纹理、细腻光影表达。"
        f"主题：{custom}。"
        f"图表事实：类型 {summary['type']}，策略 {summary['strategy']}，权威 {summary['authority']}，"
        f"人生角色 {summary['profile']}，定义 {summary['definition']}。"
        f"已定义中心：{'、'.join(defined_centers) if defined_centers else '无'}。"
        f"开放中心：{'、'.join(open_centers) if open_centers else '无'}。"
        f"主要通道：{'、'.join(channels) if channels else '无'}。"
        "画面目标：不是正式排盘图，而是报告封面/能量视觉；正式 BodyGraph 会由系统模板另行渲染。"
    )


def _compose_export_markdown(
    answer_markdown: str,
    body_energy: dict[str, Any] | None,
    deep_synthesis: dict[str, Any] | None = None,
) -> str:
    if not body_energy and not deep_synthesis:
        return answer_markdown
    lines = [answer_markdown.strip()]
    if deep_synthesis:
        lines.extend(("", "## 天赋深挖补充"))
        lines.append(str(deep_synthesis["thesis"]))
        lines.append("")
        lines.append(f"结构公式：{deep_synthesis['structure_formula']}")
        lines.append("")
        lines.append("### 非泛化检查")
        for item in deep_synthesis["non_genericity_checks"]:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("### 30 天实验")
        for item in deep_synthesis["suggested_experiments"]:
            lines.append(f"- {item}")
    if body_energy:
        lines.extend(("", "## 身体资源与能量管理补充"))
        lines.append(str(body_energy["summary"]))
        lines.append("")
        lines.append("### 九大中心")
        for item in body_energy["center_notes"]:
            lines.append(
                f"- {item['label']}（{item['state_label']}）：{item['body_resource']} "
                f"消耗模式：{item['consumption_pattern']} 练习：{item['practice']}"
            )
        lines.append("")
        lines.append("### 能量管理")
        for item in body_energy["energy_management"]:
            lines.append(f"- {item}")
    return "\n".join(lines).strip() + "\n"


def _display_summary(chart) -> dict[str, str]:
    return {
        "type": display_type(chart.summary.type.code, chart.summary.type.label),
        "strategy": display_strategy(chart.summary.strategy.code, chart.summary.strategy.label),
        "authority": display_authority(chart.summary.authority.code, chart.summary.authority.label),
        "authority_professional": display_authority_professional(
            chart.summary.authority.code,
            chart.summary.authority.label,
        ),
        "profile": display_profile(chart.summary.profile.code, chart.summary.profile.label),
        "definition": display_definition(chart.summary.definition.code, chart.summary.definition.label),
        "signature": display_signature(chart.summary.signature.code, chart.summary.signature.label),
        "not_self_theme": display_not_self(chart.summary.not_self_theme.code, chart.summary.not_self_theme.label),
        "incarnation_cross": display_incarnation_cross(chart.summary.incarnation_cross.code, chart.summary.incarnation_cross.label),
    }


def _chart_guidance(chart) -> dict[str, Any]:
    """Return compact, chart-grounded guidance used by the result page.

    This payload deliberately excludes the gate catalogue. Gate activations remain
    available in the chart for verification, while the reading UI focuses on the
    user's stable centers, open learning fields, channels, and combined talents.
    """
    body_profile = build_body_energy_profile(chart)
    talent_profile = build_deep_synthesis_profile(chart, focus="talent")
    talent_keys = {"deep-talent-axis", "deep-talent-modules"}
    return {
        "center_notes": [note.to_dict() for note in body_profile.center_notes],
        "channel_notes": [note.to_dict() for note in body_profile.channel_notes],
        "talent_sections": [
            section.to_dict()
            for section in talent_profile.sections
            if section.key in talent_keys
        ],
    }


def _split_paragraphs(text: str, *, max_chars: int = 118) -> list[str]:
    """Split long Chinese prose into readable paragraphs (PRD: 每段 ≤ 120 字)."""
    cleaned = (text or "").strip()
    if not cleaned:
        return []
    sentences = re.findall(r"[^。！？；\n]*[。！？；\n]|[^。！？；\n]+", cleaned)
    paragraphs: list[str] = []
    buffer = ""

    def flush() -> None:
        nonlocal buffer
        if buffer:
            paragraphs.append(buffer)
            buffer = ""

    for raw in sentences:
        sentence = raw.strip()
        if not sentence:
            continue
        # A single over-long sentence is hard-wrapped so no paragraph breaks the budget.
        if len(sentence) > max_chars:
            flush()
            for start in range(0, len(sentence), max_chars):
                paragraphs.append(sentence[start : start + max_chars])
            continue
        if buffer and len(buffer) + len(sentence) > max_chars:
            flush()
        buffer = f"{buffer}{sentence}" if buffer else sentence
    flush()
    return paragraphs


def _build_reading_book(saved_chart: SavedChart) -> dict[str, Any]:
    """Structured, responsive-HTML-ready reading book.

    Reuses the local grounded reading engine so the text stays tied to chart facts,
    and ships separately from the BodyGraph SVG so it can be read comfortably.
    """
    reading = generate_reading(saved_chart.chart)
    sections: list[dict[str, Any]] = [
        {
            "title": "速览",
            "summary": reading.headline,
            "paragraphs": [],
            "highlights": list(reading.quick_facts),
        }
    ]
    for section in reading.sections:
        sections.append(
            {
                "title": section.title,
                "summary": (_split_paragraphs(section.summary)[:1] or [""])[0],
                "paragraphs": _split_paragraphs(section.summary),
                "highlights": [],
            }
        )
    if reading.suggested_questions:
        sections.append(
            {
                "title": "可以继续追问",
                "summary": "带着这些问题进入对话，会比一次读完更有用。",
                "paragraphs": [],
                "highlights": list(reading.suggested_questions),
            }
        )
    return {
        "chart_id": saved_chart.chart_id,
        "title": f"{saved_chart.user_name or '我的人类图'} · 人类图解读本",
        "sections": sections,
        "layout": {
            "format": "responsive_html",
            "min_font_size": 15,
            "line_height": 1.65,
            "max_content_width": 760,
        },
    }


app = create_app()
