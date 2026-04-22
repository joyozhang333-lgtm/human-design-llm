from __future__ import annotations

from datetime import UTC, datetime

from .knowledge import get_channel_card, get_gate_card
from .reading import generate_reading
from .schema import HumanDesignChart, LLMContextBlock, LLMProductPackage

PRODUCT_NAME = "human-design-llm"
PRODUCT_VERSION = "0.1.0"

FOCUS_SECTIONS = {
    "overview": (
        "core",
        "decision",
        "profile-definition",
        "cross-variables",
        "centers",
        "channels",
        "gates",
        "integration",
    ),
    "career": (
        "core",
        "decision",
        "profile-definition",
        "cross-variables",
        "channels",
        "integration",
    ),
    "relationship": (
        "core",
        "decision",
        "profile-definition",
        "centers",
        "channels",
        "integration",
    ),
    "decision": (
        "decision",
        "profile-definition",
        "cross-variables",
        "integration",
    ),
    "growth": (
        "core",
        "profile-definition",
        "centers",
        "channels",
        "gates",
        "integration",
    ),
}

FOCUS_GUIDANCE = {
    "overview": "输出一份完整总览，帮助用户先看懂自己的人类图骨架。",
    "career": "重点把图里的能量配置翻译成工作方式、协作方式、职业选择和资源配置建议。",
    "relationship": "重点把图里的决策、边界、情绪、互动模式翻译成关系建议。",
    "decision": "重点帮助用户用策略与权威做现实决策，不要把结果写成玄学断言。",
    "growth": "重点把图里的卡点、练习方向和 30 天实验建议说清楚。",
}

FOCUS_FOLLOWUPS = {
    "overview": (
        "如果只先抓一件事开始练，我最该先练策略还是权威？",
        "我这张图里最值得继续深挖的中心、通道或闸门是哪几个？",
    ),
    "career": (
        "这张图更适合什么样的工作环境、合作关系和节奏？",
        "如果我现在正处在职业转向期，这张图最该提醒我的风险是什么？",
    ),
    "relationship": (
        "我在亲密关系或合作关系里最容易重复的模式是什么？",
        "什么样的人和互动方式最容易把我带回对位状态？",
    ),
    "decision": (
        "如果我现在要做一个重要决定，这张图要求我先停下来观察什么？",
        "我过去做错决定时，通常是跳过了哪一步？",
    ),
    "growth": (
        "接下来 30 天最值得做的一个具体实验是什么？",
        "我最该从哪个开放中心或已定义结构开始练习？",
    ),
}

SYSTEM_PROMPT = """You are `human-design-llm`, a Human Design interpretation product layer.

Your job is to transform structured chart data into clear, grounded, non-fatalistic guidance.

Operating rules:
- Always start from the provided chart and reading objects. Do not invent chart facts.
- Use Human Design as a reflective framework, not as deterministic truth.
- Prefer language such as "更可能", "更适合", "容易", "需要留意".
- Never present the reading as medical, legal, financial, or guaranteed advice.
- When the user asks a focused question, answer it through strategy, authority, profile, centers, channels, and gates that are actually present in the chart.
- If birth time or timezone is uncertain, explicitly say precision may be affected.
- Keep the answer practical: insight first, then concrete application, then follow-up questions.
"""

ASSISTANT_INSTRUCTIONS = (
    "先给一句高密度结论，再展开，不要一上来铺术语。",
    "先引用 chart 中真实存在的类型、权威、Profile、定义、中心和通道，再解释。",
    "当用户问题有明确焦点时，只展开和焦点最相关的 3 到 5 个结构，不要把整份盘重讲一遍。",
    "结尾给 2 个可以继续追问的问题。",
)


def build_llm_product(
    chart: HumanDesignChart,
    focus: str = "overview",
    question: str | None = None,
) -> LLMProductPackage:
    focus_key = focus if focus in FOCUS_SECTIONS else "overview"
    reading = generate_reading(chart)
    selected_keys = set(FOCUS_SECTIONS[focus_key])
    selected_sections = tuple(
        section for section in reading.sections if section.key in selected_keys
    )
    focus_highlights = _build_focus_highlights(chart, focus_key)

    context_blocks = (
        LLMContextBlock(
            key="focus",
            title="Focus",
            content=FOCUS_GUIDANCE[focus_key],
        ),
        *(
            (
                LLMContextBlock(
                    key="input-precision",
                    title="Input Precision",
                    content="\n".join(chart.input.warnings),
                ),
            )
            if chart.input.warnings
            else ()
        ),
        LLMContextBlock(
            key="quick-facts",
            title="Quick Facts",
            content="\n".join(reading.quick_facts),
        ),
        *(
            (
                LLMContextBlock(
                    key="focus-highlights",
                    title="Focus Highlights",
                    content=focus_highlights,
                ),
            )
            if focus_highlights
            else ()
        ),
        *tuple(
            LLMContextBlock(
                key=section.key,
                title=section.title,
                content=_section_to_text(section.summary, section.bullets),
            )
            for section in selected_sections
        ),
    )

    answer_markdown = _render_focus_answer(
        chart,
        reading.headline,
        focus_key,
        question,
        focus_highlights,
        selected_sections,
        FOCUS_FOLLOWUPS[focus_key],
    )

    return LLMProductPackage(
        generated_at_utc=datetime.now(UTC).isoformat(),
        product_name=PRODUCT_NAME,
        product_version=PRODUCT_VERSION,
        focus=focus_key,
        question=question,
        system_prompt=SYSTEM_PROMPT,
        assistant_instructions=ASSISTANT_INSTRUCTIONS,
        context_blocks=context_blocks,
        answer_markdown=answer_markdown,
        suggested_followups=FOCUS_FOLLOWUPS[focus_key],
        reading=reading,
    )


def _render_focus_answer(
    chart: HumanDesignChart,
    headline: str,
    focus: str,
    question: str | None,
    focus_highlights: str | None,
    sections,
    followups: tuple[str, ...],
) -> str:
    lines: list[str] = []
    lines.append("# Human Design LLM Session")
    lines.append("")
    lines.append(headline)
    lines.append("")
    lines.append(f"当前聚焦：{focus}")
    if question:
        lines.append(f"当前问题：{question}")
    precision_note = _precision_note(chart)
    if precision_note:
        lines.append(f"输入精度提示：{precision_note}")
    if focus_highlights:
        lines.append("")
        lines.append("## 焦点提示")
        lines.append(focus_highlights)

    for section in sections:
        lines.append("")
        lines.append(f"## {section.title}")
        lines.append(section.summary)
        if section.bullets:
            lines.append("")
            for bullet in section.bullets:
                lines.append(f"- {bullet}")

    lines.append("")
    lines.append("## 建议继续追问")
    for item in followups:
        lines.append(f"- {item}")

    return "\n".join(lines).strip() + "\n"


def _section_to_text(summary: str, bullets: tuple[str, ...]) -> str:
    lines = [summary]
    for bullet in bullets:
        lines.append(f"- {bullet}")
    return "\n".join(lines)


def _precision_note(chart: HumanDesignChart | None) -> str | None:
    if chart is None or not chart.input.warnings:
        return None
    return "；".join(chart.input.warnings)


def _build_focus_highlights(chart: HumanDesignChart, focus: str) -> str | None:
    if focus == "overview":
        return None

    lines: list[str] = []
    for channel in chart.channels:
        card = get_channel_card(channel.code)
        if card and card.focus.get(focus):
            lines.append(f"{channel.code}：{card.focus[focus]}")
    for gate in chart.activated_gates:
        card = get_gate_card(gate.gate)
        if card and card.focus.get(focus):
            lines.append(f"{gate.gate} 号闸门：{card.focus[focus]}")
        if len(lines) >= 4:
            break
    if not lines:
        return None
    return "\n".join(f"- {line}" for line in lines[:4])
