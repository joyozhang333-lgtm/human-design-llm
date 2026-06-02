from __future__ import annotations

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
from .input import InputNormalizationError, normalize_birth_input
from .labels import (
    CENTER_LABELS,
    display_authority,
    display_definition,
    display_not_self,
    display_profile,
    display_signature,
    display_strategy,
    display_type,
    normalize_center_title,
)
from .product import build_llm_product
from .providers import (
    DeepSeekClient,
    MiniMaxImageClient,
    ProviderConfigurationError,
    ProviderError,
    external_provider_status,
)
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
        version="1.0.0",
        description="简体中文人类图 Web/App 产品 API：排盘、出图、报告、问答。",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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
            "report_types": list(REPORT_CONFIG),
            "required_birth_fields": ["birth_date", "birth_time", "timezone_name 或 city/region/country"],
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
                    "message": "正式人类图需要出生时间和出生地/时区。仅生日只能做低精度引导，不能生成正式 BodyGraph。",
                    "required_fields": ["birth_time", "timezone_name 或 city/region/country"],
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
        svg = render_bodygraph_svg(chart, title=title)
        bodygraph_url = f"/api/charts/{chart_id}/bodygraph.svg"
        saved = SavedChart(
            chart_id=chart_id,
            user_name=request.user_name,
            birth_profile=BirthProfile(
                birth_date=request.birth_date,
                birth_time=request.birth_time,
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
        return payload

    @app.get("/api/charts/{chart_id}")
    def get_chart(chart_id: str) -> dict[str, Any]:
        chart = active_store.get_chart(chart_id)
        payload = chart.to_dict(include_svg=False)
        payload["precision_warnings"] = list(chart.chart.input.warnings)
        payload["display_summary"] = _display_summary(chart.chart)
        return payload

    @app.get("/api/charts/{chart_id}/bodygraph.svg")
    def get_bodygraph_svg(chart_id: str) -> Response:
        chart = active_store.get_chart(chart_id)
        return Response(content=chart.bodygraph_svg, media_type="image/svg+xml")

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

    @app.post("/api/chat")
    def chat(request: ChatRequest) -> dict[str, Any]:
        saved_chart = active_store.get_chart(request.chart_id)
        focus = request.focus or _infer_focus(request.question)
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
            session=session,
            question=request.question,
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
            "citations": [citation.to_dict() for citation in package.answer_citations],
            "suggested_followups": list(package.suggested_followups),
            "session": session.to_dict(),
        }

    @app.post("/api/images/reading-visual")
    def create_reading_visual(request: ImageGenerationRequest) -> dict[str, Any]:
        saved_chart = active_store.get_chart(request.chart_id)
        prompt = _build_visual_prompt(saved_chart, request.prompt)
        config = external_provider_status()["minimax"]
        if not config["configured"]:
            visual = GeneratedVisual(
                image_id=f"image_{uuid4().hex}",
                chart_id=request.chart_id,
                provider="minimax",
                model=config.get("model"),
                prompt=prompt,
                image_url=None,
                fallback_bodygraph_svg_url=saved_chart.bodygraph_svg_url,
                provider_configured=False,
                created_at_utc=utc_now_iso(),
            )
            active_store.save_visual(visual)
            return visual.to_dict()
        try:
            result = MiniMaxImageClient().generate(prompt, aspect_ratio=request.aspect_ratio)
        except ProviderConfigurationError:
            visual = GeneratedVisual(
                image_id=f"image_{uuid4().hex}",
                chart_id=request.chart_id,
                provider="minimax",
                model=config.get("model"),
                prompt=prompt,
                image_url=None,
                fallback_bodygraph_svg_url=saved_chart.bodygraph_svg_url,
                provider_configured=False,
                created_at_utc=utc_now_iso(),
            )
            active_store.save_visual(visual)
            return visual.to_dict()
        except ProviderError as exc:
            raise HTTPException(
                status_code=502,
                detail={"code": "image_generation_failed", "message": "图片服务暂时不可用，请稍后再试。"},
            ) from exc
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


def _generate_chat_answer(
    *,
    saved_chart: SavedChart,
    package,
    session: ChatSession,
    question: str,
) -> tuple[str, str, str | None, bool]:
    provider_status = external_provider_status()["deepseek"]
    if not provider_status["configured"]:
        return package.answer_markdown, "local-fallback", None, False
    messages = _build_deepseek_messages(saved_chart, package, session, question)
    try:
        answer = DeepSeekClient().chat(messages)
    except ProviderConfigurationError:
        return package.answer_markdown, "local-fallback", None, False
    except ProviderError:
        return _fallback_with_provider_note(package.answer_markdown), "local-fallback", None, True
    return answer.content, answer.provider, answer.model, True


def _build_deepseek_messages(
    saved_chart: SavedChart,
    package,
    session: ChatSession,
    question: str,
) -> list[dict[str, str]]:
    system = "\n".join(
        (
            package.system_prompt,
            "你现在面向简体中文用户，回答必须自然、具体、可执行。",
            "必须使用目标术语：荐骨中心、荐骨权威、阿姬娜中心、喉咙中心；不要使用骶骨中心、额骨中心、阿扎那。",
            "只能基于下方 chart facts、reading context 和历史会话作答；不知道就说明无法从当前图表推出。",
            "深度解读必须做结构叠加：不要只按人生角色、类型或单个闸门回答；要说明真实通道、已定义/开放中心、关键闸门如何共同作用。",
            "当用户问天赋、使命、职业主航道或深挖时，必须输出具体天赋模块、误用方式、可观察练习，避免可套给所有人的建议。",
            "不要输出医疗、法律、财务或确定性命运承诺。",
            *package.assistant_instructions,
        )
    )
    context = _context_block_text(package)
    history = _chat_history_text(session)
    user = "\n\n".join(
        (
            f"用户问题：{question}",
            "【当前图表事实】\n" + _chart_fact_digest(saved_chart.chart),
            "【可引用解读上下文】\n" + context,
            "【本轮历史】\n" + history if history else "【本轮历史】\n暂无。",
            "请输出 Markdown。结构：先给一句高密度结论，再分成 3-5 个小节，每节都要连接到具体图表事实，最后给 2 个下一步追问。",
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
        role = "用户" if message.role == "user" else "系统"
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
    channels = [f"{channel.code}「{channel.label}」" for channel in chart.channels]
    gates = [
        f"{gate.gate}「{gate.theme}」({normalize_center_title(CENTER_LABELS.get(gate.center, gate.center))})"
        for gate in chart.activated_gates
    ]
    return "\n".join(
        (
            f"类型：{summary['type']}",
            f"策略：{summary['strategy']}",
            f"权威：{summary['authority']}",
            f"人生角色：{summary['profile']}",
            f"定义：{summary['definition']}",
            f"签名/非自己主题：{summary['signature']} / {summary['not_self_theme']}",
            f"轮回交叉：{summary['incarnation_cross']}",
            "已定义中心：" + ("、".join(defined_centers) if defined_centers else "无"),
            "开放中心：" + ("、".join(open_centers) if open_centers else "无"),
            "通道：" + ("、".join(channels) if channels else "无"),
            "闸门：" + ("、".join(gates[:32]) if gates else "无"),
            f"输入时间：{chart.input.birth_datetime_local}，时区：{chart.input.timezone_name}",
        )
    )


def _fallback_with_provider_note(answer_markdown: str) -> str:
    note = (
        "\n\n> 当前外部问答服务暂时不可用，以下回答由本地结构化解读引擎生成，"
        "仍然基于当前图表事实。"
    )
    return answer_markdown.rstrip() + note


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
    channels = [f"{channel.code} {channel.label}" for channel in chart.channels[:8]]
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
        "profile": display_profile(chart.summary.profile.code, chart.summary.profile.label),
        "definition": display_definition(chart.summary.definition.code, chart.summary.definition.label),
        "signature": display_signature(chart.summary.signature.code, chart.summary.signature.label),
        "not_self_theme": display_not_self(chart.summary.not_self_theme.code, chart.summary.not_self_theme.label),
        "incarnation_cross": chart.summary.incarnation_cross.label,
    }


app = create_app()
