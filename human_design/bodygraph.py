from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

from .labels import (
    CENTER_LABELS,
    display_authority,
    display_definition,
    display_profile,
    display_type,
)
from .reading import generate_reading
from .schema import ActivationRecord, GateState, HumanDesignChart

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

TEMPLATE_PATH = Path(__file__).resolve().parent / "assets" / "bodygraph-template.svg"

INACTIVE_GATE_FILL = "#e7dfd5"
PERSONALITY_FILL = "#151515"
DESIGN_FILL = "#a44344"
TEXT_ACTIVE_FILL = "#3b332d"
TEXT_INACTIVE_FILL = "#6c645d"
TEXT_BG_FILL_ACTIVE = "#e8e1d8"
TEXT_BG_FILL_INACTIVE = "#f1ebe4"
TEXT_BG_STROKE_ACTIVE = "#cbbdaf"
TEXT_BG_STROKE_INACTIVE = "#ddd3c8"
CENTER_UNDEFINED_FILL = "#fffdfa"
META_TEXT_FILL = "#3a332e"
SUBTLE_TEXT_FILL = "#7b7267"
BACKGROUND_FILL = "#f6f1ea"
PANEL_FILL = "#fffaf4"
PANEL_STROKE = "#e1d7cb"
DESIGN_PANEL_FILL = "#f8ebe8"
PERSONALITY_PANEL_FILL = "#f3f0ed"
SUMMARY_PANEL_FILL = "#fbf7f1"
DIVIDER_STROKE = "#e9dfd5"
SECTION_PANEL_FILL = "#fffaf4"
SECTION_HEADER_FILL = "#f4ece3"
ACCENT_FILL = "#8f6c58"

CENTER_FILLS = {
    "head": "#f6e79a",
    "ajna": "#9ccf92",
    "throat": "#b88f64",
    "g": "#f7e3a1",
    "heart": "#ea7f79",
    "spleen": "#c8a783",
    "solar-plexus": "#d9b37c",
    "sacral": "#ef8378",
    "root": "#c9a56e",
}

CENTER_TEMPLATE_IDS = {
    "head": "Head",
    "ajna": "Ajna",
    "throat": "Throat",
    "g": "G",
    "heart": "Ego",
    "spleen": "Spleen",
    "solar-plexus": "SolarPlexus",
    "sacral": "Sacral",
    "root": "Root",
}

BOTH_GRADIENT_BY_GATE = {
    10: "hd-both-horizontal",
    12: "hd-both-diagonal",
    16: "hd-both-branch",
    18: "hd-both-spleen-root",
    19: "hd-both-solar-root",
    20: "hd-both-branch",
    21: "hd-both-diagonal",
    22: "hd-both-diagonal",
    25: "hd-both-25-51",
    26: "hd-both-diagonal",
    27: "hd-both-50-27",
    28: "hd-both-spleen-root",
    30: "hd-both-solar-root",
    32: "hd-both-spleen-root",
    34: "hd-both-34",
    35: "hd-both-diagonal",
    36: "hd-both-diagonal",
    37: "hd-both-diagonal",
    38: "hd-both-spleen-root",
    39: "hd-both-solar-root",
    40: "hd-both-diagonal",
    41: "hd-both-solar-root",
    44: "hd-both-diagonal",
    48: "hd-both-branch",
    49: "hd-both-solar-root",
    50: "hd-both-50-27",
    51: "hd-both-25-51",
    54: "hd-both-spleen-root",
    55: "hd-both-solar-root",
    57: "hd-both-branch",
    59: "hd-both-59-6",
    6: "hd-both-59-6",
}

SPECIAL_GATE_ELEMENTS = {
    10: ("GateConnect10",),
    34: ("GateConnect34",),
}

SPECIAL_SPAN_CHANNELS = (
    frozenset({34, 20}),
    frozenset({34, 10}),
    frozenset({57, 20}),
)

PLANET_ORDER = (
    "sun",
    "earth",
    "north-node",
    "south-node",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
)

PLANET_LABELS = {
    "sun": "太阳",
    "earth": "地球",
    "north-node": "北交点",
    "south-node": "南交点",
    "moon": "月亮",
    "mercury": "水星",
    "venus": "金星",
    "mars": "火星",
    "jupiter": "木星",
    "saturn": "土星",
    "uranus": "天王星",
    "neptune": "海王星",
    "pluto": "冥王星",
}


@dataclass(frozen=True)
class GateRenderState:
    gate: int
    role: str
    active: bool


def render_bodygraph_svg(chart: HumanDesignChart, *, title: str | None = None) -> str:
    root = ET.fromstring(TEMPLATE_PATH.read_text(encoding="utf-8"))
    id_index = _build_id_index(root)
    reading = generate_reading(chart)

    _ensure_defs(root, id_index)

    gate_states = _build_gate_render_states(chart)
    _style_gate_layer(id_index, gate_states)
    _style_centers(id_index, chart)
    _style_meta(root, chart, reading=reading, title=title)

    return ET.tostring(root, encoding="unicode")


def write_bodygraph_svg(chart: HumanDesignChart, path: str | Path, *, title: str | None = None) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_bodygraph_svg(chart, title=title), encoding="utf-8")
    return output_path


def _build_id_index(root: ET.Element) -> dict[str, ET.Element]:
    return {
        element.attrib["id"]: element
        for element in root.iter()
        if "id" in element.attrib
    }


def _ensure_defs(root: ET.Element, id_index: dict[str, ET.Element]) -> None:
    defs = id_index.get("defs")
    if defs is None:
        defs = root.find(f"{{{SVG_NS}}}defs")
    if defs is None:
        defs = ET.Element(f"{{{SVG_NS}}}defs")
        root.insert(0, defs)

    gradients = {
        "hd-both-vertical": ("0%", "0%", "100%", "0%"),
        "hd-both-horizontal": ("0%", "0%", "0%", "100%"),
        "hd-both-diagonal": ("0%", "0%", "100%", "100%"),
        "hd-both-spleen-root": ("100%", "0%", "4%", "100%"),
        "hd-both-solar-root": ("4%", "0%", "100%", "100%"),
        "hd-both-59-6": ("9%", "25%", "50%", "100%"),
        "hd-both-50-27": ("50%", "0%", "9%", "75%"),
        "hd-both-25-51": ("100%", "0%", "4%", "100%"),
        "hd-both-34": ("100%", "0%", "4%", "100%"),
        "hd-both-branch": ("100%", "90%", "0%", "0%"),
    }

    existing_ids = {element.attrib.get("id") for element in defs}
    for gradient_id, (x1, y1, x2, y2) in gradients.items():
        if gradient_id in existing_ids:
            continue
        gradient = ET.SubElement(
            defs,
            f"{{{SVG_NS}}}linearGradient",
            {
                "id": gradient_id,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
            },
        )
        ET.SubElement(
            gradient,
            f"{{{SVG_NS}}}stop",
            {"offset": "50%", "style": f"stop-color: {DESIGN_FILL}; stop-opacity: 1"},
        )
        ET.SubElement(
            gradient,
            f"{{{SVG_NS}}}stop",
            {"offset": "50%", "style": f"stop-color: {PERSONALITY_FILL}; stop-opacity: 1"},
        )


def _build_gate_render_states(chart: HumanDesignChart) -> dict[int, GateRenderState]:
    states: dict[int, GateRenderState] = {}
    for gate in range(1, 65):
        states[gate] = GateRenderState(gate=gate, role="inactive", active=False)

    for gate in chart.activated_gates:
        role = _role_for_gate(gate)
        states[gate.gate] = GateRenderState(gate=gate.gate, role=role, active=True)
    return states


def _role_for_gate(gate: GateState) -> str:
    imprints = {activation.imprint for activation in gate.activations}
    if imprints == {"personality"}:
        return "personality"
    if imprints == {"design"}:
        return "design"
    return "both"


def _style_gate_layer(id_index: dict[str, ET.Element], gate_states: dict[int, GateRenderState]) -> None:
    for gate, state in gate_states.items():
        fill = _fill_for_gate_state(state)
        gate_element = id_index.get(f"Gate{gate}")
        if gate_element is not None:
            gate_element.set("fill", fill)

        for extra_id in SPECIAL_GATE_ELEMENTS.get(gate, ()):
            extra = id_index.get(extra_id)
            if extra is not None:
                extra.set("fill", fill if state.active else INACTIVE_GATE_FILL)

        text_bg = id_index.get(f"GateTextBg{gate}")
        if text_bg is not None:
            _style_gate_text_background(text_bg, state=state)

        text = id_index.get(f"GateText{gate}")
        if text is not None:
            text.set("fill", TEXT_ACTIVE_FILL if state.active else TEXT_INACTIVE_FILL)

    _style_special_span(id_index, gate_states)


def _style_gate_text_background(group: ET.Element, *, state: GateRenderState) -> None:
    fill = TEXT_BG_FILL_ACTIVE if state.active else TEXT_BG_FILL_INACTIVE
    stroke = TEXT_BG_STROKE_ACTIVE if state.active else TEXT_BG_STROKE_INACTIVE
    for child in group:
        child.set("fill", fill)
        child.set("stroke", stroke)
        child.set("stroke-width", "1")


def _style_special_span(id_index: dict[str, ET.Element], gate_states: dict[int, GateRenderState]) -> None:
    span = id_index.get("GateSpan")
    connect10 = id_index.get("GateConnect10")
    connect34 = id_index.get("GateConnect34")
    if span is None or connect10 is None or connect34 is None:
        return

    span.set("fill", INACTIVE_GATE_FILL)
    connect10.set("fill", _fill_for_gate_state(gate_states[10]))
    connect34.set("fill", _fill_for_gate_state(gate_states[34]))

    active_roles = []
    for pair in SPECIAL_SPAN_CHANNELS:
        left, right = tuple(pair)
        if gate_states[left].active and gate_states[right].active:
            active_roles.extend([gate_states[left].role, gate_states[right].role])

    if not active_roles:
        return

    if all(role == "personality" for role in active_roles):
        fill = PERSONALITY_FILL
    elif all(role == "design" for role in active_roles):
        fill = DESIGN_FILL
    else:
        fill = "url(#hd-both-branch)"

    span.set("fill", fill)
    connect10.set("fill", fill)
    connect34.set("fill", fill)


def _fill_for_gate_state(state: GateRenderState) -> str:
    if not state.active:
        return INACTIVE_GATE_FILL
    if state.role == "personality":
        return PERSONALITY_FILL
    if state.role == "design":
        return DESIGN_FILL
    gradient_id = BOTH_GRADIENT_BY_GATE.get(state.gate, "hd-both-vertical")
    return f"url(#{gradient_id})"


def _style_centers(id_index: dict[str, ET.Element], chart: HumanDesignChart) -> None:
    center_states = {center.code: center.defined for center in chart.centers}
    for code, template_id in CENTER_TEMPLATE_IDS.items():
        center = id_index.get(template_id)
        if center is None:
            continue
        path = _first_shape(center)
        if path is None:
            continue
        if center_states.get(code, False):
            path.set("fill", CENTER_FILLS[code])
        else:
            path.set("fill", CENTER_UNDEFINED_FILL)


def _first_shape(group: ET.Element) -> ET.Element | None:
    for child in group:
        if child.tag in {
            f"{{{SVG_NS}}}path",
            f"{{{SVG_NS}}}polygon",
            f"{{{SVG_NS}}}polyline",
            f"{{{SVG_NS}}}circle",
            f"{{{SVG_NS}}}rect",
        }:
            return child
    return None


def _style_meta(root: ET.Element, chart: HumanDesignChart, reading, *, title: str | None) -> None:
    view_box = root.attrib.get("viewBox", "0 0 851.41 1309.4").split()
    min_x, min_y, width, height = (float(value) for value in view_box)
    expanded_min_x = min_x - 240
    expanded_width = width + 480
    expanded_min_y = -125
    expanded_height = height + 1820
    root.set("viewBox", f"{expanded_min_x} {expanded_min_y} {expanded_width} {expanded_height}")

    _append_background(root, expanded_min_x, expanded_min_y, expanded_width, expanded_height)

    title_text = title or "人类图"
    summary_line = " | ".join(
        [
            display_type(chart.summary.type.code, chart.summary.type.label),
            display_authority(chart.summary.authority.code, chart.summary.authority.label),
            f"{display_profile(chart.summary.profile.code, chart.summary.profile.label)} 人生角色",
            display_definition(chart.summary.definition.code, chart.summary.definition.label),
        ]
    )

    defined_centers = [
        CENTER_LABELS.get(center.code, center.label)
        for center in chart.centers
        if center.defined
    ]
    undefined_centers = [
        CENTER_LABELS.get(center.code, center.label)
        for center in chart.centers
        if not center.defined
    ]
    channels = [channel.code for channel in chart.channels]
    center_x = min_x + (width / 2)

    _append_text(
        root,
        x=center_x,
        y=-82,
        text=title_text,
        font_size="34",
        font_weight="700",
        anchor="middle",
        fill=META_TEXT_FILL,
    )
    _append_text(
        root,
        x=center_x,
        y=-46,
        text=summary_line,
        font_size="16",
        font_weight="500",
        anchor="middle",
        fill=SUBTLE_TEXT_FILL,
    )
    _append_activation_panel(
        root,
        x=expanded_min_x + 24,
        y=12,
        width=180,
        heading="设计面",
        heading_fill=DESIGN_FILL,
        panel_fill=DESIGN_PANEL_FILL,
        align="left",
        activations=chart.design.activations,
    )
    _append_activation_panel(
        root,
        x=min_x + width + 36,
        y=12,
        width=180,
        heading="人格面",
        heading_fill=PERSONALITY_FILL,
        panel_fill=PERSONALITY_PANEL_FILL,
        align="right",
        activations=chart.personality.activations,
    )
    _append_summary_panel(
        root,
        x=120,
        y=1328,
        width=610,
        defined_centers=defined_centers,
        channels=channels,
        undefined_centers=undefined_centers,
    )
    _append_reading_booklet(
        root,
        reading=reading,
        x=expanded_min_x + 32,
        y=1498,
        width=expanded_width - 64,
    )


def _append_background(
    root: ET.Element,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    rect = ET.Element(
        f"{{{SVG_NS}}}rect",
        {
            "x": str(x),
            "y": str(y),
            "width": str(width),
            "height": str(height),
            "fill": BACKGROUND_FILL,
        },
    )
    root.insert(1, rect)


def _append_activation_panel(
    root: ET.Element,
    *,
    x: float,
    y: float,
    width: float,
    heading: str,
    heading_fill: str,
    panel_fill: str,
    align: str,
    activations: tuple[ActivationRecord, ...],
) -> None:
    row_height = 31
    panel_height = 54 + len(PLANET_ORDER) * row_height
    _append_rect(
        root,
        x=x,
        y=y,
        width=width,
        height=panel_height,
        fill=panel_fill,
        stroke=PANEL_STROKE,
        rx=18,
        ry=18,
    )
    _append_rect(
        root,
        x=x + 14,
        y=y + 12,
        width=width - 28,
        height=1,
        fill=heading_fill,
    )
    _append_text(
        root,
        x=x + width / 2,
        y=y + 31,
        text=heading,
        font_size="18",
        font_weight="700",
        anchor="middle",
        fill=heading_fill,
    )
    activations_by_code = {activation.planet_code: activation for activation in activations}
    for index, planet_code in enumerate(PLANET_ORDER):
        activation = activations_by_code.get(planet_code)
        if activation is None:
            continue
        row_y = y + 58 + (index * row_height)
        if index > 0:
            _append_rect(
                root,
                x=x + 16,
                y=row_y - 18,
                width=width - 32,
                height=1,
                fill=DIVIDER_STROKE,
            )
        _append_text(
            root,
            x=x + 18,
            y=row_y,
            text=PLANET_LABELS.get(planet_code, activation.planet_label),
            font_size="14",
            font_weight="500",
            anchor="start",
            fill=META_TEXT_FILL,
        )
        value_anchor = "end"
        value_x = x + width - 18
        _append_text(
            root,
            x=value_x,
            y=row_y,
            text=f"{activation.gate}.{activation.line}",
            font_size="14",
            font_weight="700",
            anchor=value_anchor,
            fill=heading_fill,
        )


def _append_summary_panel(
    root: ET.Element,
    *,
    x: float,
    y: float,
    width: float,
    defined_centers: list[str],
    channels: list[str],
    undefined_centers: list[str],
) -> None:
    _append_rect(
        root,
        x=x,
        y=y,
        width=width,
        height=132,
        fill=SUMMARY_PANEL_FILL,
        stroke=PANEL_STROKE,
        rx=20,
        ry=20,
    )
    _append_text(
        root,
        x=x + 22,
        y=y + 30,
        text="盘面摘要",
        font_size="18",
        font_weight="700",
        anchor="start",
        fill=META_TEXT_FILL,
    )
    _append_text(
        root,
        x=x + 22,
        y=y + 62,
        text=f"已定义中心：{'、'.join(defined_centers) if defined_centers else '无'}",
        font_size="15",
        font_weight="600",
        anchor="start",
        fill=META_TEXT_FILL,
    )
    _append_text(
        root,
        x=x + 22,
        y=y + 90,
        text=f"完整通道：{'、'.join(channels) if channels else '无'}",
        font_size="15",
        font_weight="600",
        anchor="start",
        fill=META_TEXT_FILL,
    )
    _append_text(
        root,
        x=x + 22,
        y=y + 116,
        text=f"开放中心：{'、'.join(undefined_centers) if undefined_centers else '无'}",
        font_size="14",
        font_weight="400",
        anchor="start",
        fill=SUBTLE_TEXT_FILL,
    )
    _append_text(
        root,
        x=x + width - 22,
        y=y + 30,
        text="黑=人格 红=设计 红黑渐层=双侧激活",
        font_size="13",
        font_weight="500",
        anchor="end",
        fill=SUBTLE_TEXT_FILL,
    )


def _append_reading_booklet(
    root: ET.Element,
    *,
    reading,
    x: float,
    y: float,
    width: float,
) -> None:
    _append_text(
        root,
        x=x + width / 2,
        y=y,
        text="人类图解读本",
        font_size="26",
        font_weight="700",
        anchor="middle",
        fill=META_TEXT_FILL,
    )
    _append_text(
        root,
        x=x + width / 2,
        y=y + 32,
        text=reading.headline,
        font_size="16",
        font_weight="500",
        anchor="middle",
        fill=SUBTLE_TEXT_FILL,
    )
    facts_y = y + 58
    _append_fact_panel(root, reading=reading, x=x, y=facts_y, width=width)
    sections_y = facts_y + 156
    _append_section_grid(root, reading=reading, x=x, y=sections_y, width=width)
    _append_questions_panel(root, reading=reading, x=x, y=sections_y + 892, width=width)


def _append_fact_panel(root: ET.Element, *, reading, x: float, y: float, width: float) -> None:
    _append_rect(
        root,
        x=x,
        y=y,
        width=width,
        height=128,
        fill=SUMMARY_PANEL_FILL,
        stroke=PANEL_STROKE,
        rx=22,
        ry=22,
    )
    _append_text(
        root,
        x=x + 24,
        y=y + 30,
        text="快速摘要",
        font_size="18",
        font_weight="700",
        anchor="start",
        fill=META_TEXT_FILL,
    )
    col_width = (width - 48) / 3
    for index, fact in enumerate(reading.quick_facts[:6]):
        col = index % 3
        row = index // 3
        _append_text(
            root,
            x=x + 24 + (col * col_width),
            y=y + 62 + (row * 28),
            text=fact,
            font_size="14",
            font_weight="500",
            anchor="start",
            fill=ACCENT_FILL if row == 0 else META_TEXT_FILL,
        )


def _append_section_grid(root: ET.Element, *, reading, x: float, y: float, width: float) -> None:
    gap = 24
    card_width = (width - gap) / 2
    card_height = 200
    for index, section in enumerate(reading.sections):
        col = index % 2
        row = index // 2
        card_x = x + col * (card_width + gap)
        card_y = y + row * (card_height + gap)
        _append_section_card(
            root,
            x=card_x,
            y=card_y,
            width=card_width,
            height=card_height,
            title=section.title,
            summary=section.summary,
            bullets=section.bullets,
        )


def _append_section_card(
    root: ET.Element,
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    title: str,
    summary: str,
    bullets: tuple[str, ...],
) -> None:
    _append_rect(
        root,
        x=x,
        y=y,
        width=width,
        height=height,
        fill=SECTION_PANEL_FILL,
        stroke=PANEL_STROKE,
        rx=20,
        ry=20,
    )
    _append_rect(
        root,
        x=x,
        y=y,
        width=width,
        height=40,
        fill=SECTION_HEADER_FILL,
        rx=20,
        ry=20,
    )
    _append_text(
        root,
        x=x + 18,
        y=y + 26,
        text=title,
        font_size="17",
        font_weight="700",
        anchor="start",
        fill=META_TEXT_FILL,
    )
    summary_lines = _wrap_text(_trim_text(summary, 120), max_units=36, max_lines=3)
    cursor_y = y + 64
    for line in summary_lines:
        _append_text(
            root,
            x=x + 18,
            y=cursor_y,
            text=line,
            font_size="14",
            font_weight="400",
            anchor="start",
            fill=META_TEXT_FILL,
        )
        cursor_y += 22

    cursor_y += 6
    for bullet in bullets[:2]:
        bullet_lines = _wrap_text(f"• {_trim_text(bullet, 82)}", max_units=37, max_lines=2)
        for line_index, line in enumerate(bullet_lines):
            _append_text(
                root,
                x=x + 18,
                y=cursor_y,
                text=line,
                font_size="13",
                font_weight="400",
                anchor="start",
                fill=SUBTLE_TEXT_FILL if line_index else ACCENT_FILL,
            )
            cursor_y += 19
        cursor_y += 4


def _append_questions_panel(root: ET.Element, *, reading, x: float, y: float, width: float) -> None:
    _append_rect(
        root,
        x=x,
        y=y,
        width=width,
        height=152,
        fill=SUMMARY_PANEL_FILL,
        stroke=PANEL_STROKE,
        rx=22,
        ry=22,
    )
    _append_text(
        root,
        x=x + 24,
        y=y + 30,
        text="建议继续追问",
        font_size="18",
        font_weight="700",
        anchor="start",
        fill=META_TEXT_FILL,
    )
    cursor_y = y + 62
    for question in reading.suggested_questions[:3]:
        lines = _wrap_text(f"• {_trim_text(question, 90)}", max_units=86, max_lines=2)
        for line in lines:
            _append_text(
                root,
                x=x + 24,
                y=cursor_y,
                text=line,
                font_size="14",
                font_weight="400",
                anchor="start",
                fill=META_TEXT_FILL,
            )
            cursor_y += 22
        cursor_y += 4


def _append_rect(
    root: ET.Element,
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    fill: str,
    stroke: str | None = None,
    rx: int | None = None,
    ry: int | None = None,
) -> ET.Element:
    attrs = {
        "x": str(x),
        "y": str(y),
        "width": str(width),
        "height": str(height),
        "fill": fill,
    }
    if stroke is not None:
        attrs["stroke"] = stroke
        attrs["stroke-width"] = "1"
    if rx is not None:
        attrs["rx"] = str(rx)
    if ry is not None:
        attrs["ry"] = str(ry)
    return ET.SubElement(root, f"{{{SVG_NS}}}rect", attrs)


def _append_text(
    root: ET.Element,
    *,
    x: float,
    y: float,
    text: str,
    font_size: str,
    font_weight: str,
    anchor: str,
    fill: str,
) -> ET.Element:
    element = ET.SubElement(
        root,
        f"{{{SVG_NS}}}text",
        {
            "x": str(x),
            "y": str(y),
            "font-size": font_size,
            "font-family": "PingFang SC, Hiragino Sans GB, Microsoft YaHei, Helvetica, Arial, sans-serif",
            "font-weight": font_weight,
            "text-anchor": anchor,
            "fill": fill,
        },
    )
    element.text = text
    return element


def _trim_text(text: str, limit: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def _wrap_text(text: str, *, max_units: int, max_lines: int) -> list[str]:
    lines: list[str] = []
    current = ""
    current_units = 0
    for char in text:
        units = 1 if ord(char) < 128 else 2
        if current and current_units + units > max_units:
            lines.append(current)
            current = char
            current_units = units
            if len(lines) >= max_lines:
                break
            continue
        current += char
        current_units += units
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    if lines and len("".join(lines)) < len(text):
        lines[-1] = lines[-1].rstrip("，。；、 ") + "…"
    return lines
