"""确定性护栏（零 LLM）：扫描输出里的编造结构、英文、污染、套话、决定论。

硬违规（编造闸门/通道、污染黑名单、套话指纹、焦虑决定论）→ 定向 repair ×1 → 仍失败降级 fallback。
软违规（english_leak）→ 先剔除用户合法词再扫；命中只 repair ×1，仍失败记日志（脱敏），不直接降级。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .facts import ChartFacts

GATE_RE = re.compile(r"(\d{1,2})\s*号?\s*闸门")
# Models commonly omit a leading zero (2-14). Canonicalise both forms before
# comparing with the chart whitelist so invented pairs cannot bypass validation.
CHANNEL_RE = re.compile(r"(?<!\d)(\d{1,2})\s*-\s*(\d{1,2})(?!\d)")
ENGLISH_TERM_RE = re.compile(r"[A-Za-z]{3,}|[♃♄⛢♅⊕☊☋☉☽☿♀♂♆♇]")
INVENTED_COMPOSITE_RE = re.compile(
    r"(?:由\s*)?(?:\d{1,2}(?:\s*号?\s*闸门)?\s*[、，,]\s*){2,}"
    r"\d{1,2}(?:\s*号?\s*闸门)?[^。！？\n]{0,18}"
    r"(?:组成|构成|形成|汇聚成)[^。！？\n]{0,18}(?:轴|回路|通道|系统|模块|能力组合|主题组合)"
)
DEFINED_CHANNEL_ACTIVATION_RE = re.compile(
    r"(?:通道|这条能力)[^。！？\n]{0,20}(?:邀请|认可)[^。！？\n]{0,16}(?:激活|启动|形成|存在)"
    r"|(?:邀请|认可)[^。！？\n]{0,20}(?:才会|才能|之后)[^。！？\n]{0,10}(?:激活|启动)[^。！？\n]{0,8}(?:通道|这条能力)"
)
AUTHORITY_TERM_RE = re.compile(
    r"\b(?:Sacral|Emotional|Splenic|Ego(?:\s+(?:Manifested|Projected))?|Self-Projected|Environmental|Lunar)\s+Authority\b",
    re.IGNORECASE,
)
EXPECTED_AUTHORITY_TERMS = {
    "sacral": "Sacral Authority",
    "solar-plexus": "Emotional Authority",
    "emotional": "Emotional Authority",
    "splenic": "Splenic Authority",
    "ego": "Ego Authority",
    "ego-manifested": "Ego Manifested Authority",
    "ego-projected": "Ego Projected Authority",
    "self-projected": "Self-Projected Authority",
    "mental": "Environmental Authority",
    "outer-authority": "Environmental Authority",
    "lunar": "Lunar Authority",
}

POLLUTION = (
    "chart facts",
    "prompt",
    "专业信息必须",
    "专业依据必须",
    "方便后续",
    "回到图表事实",
    "知识原子",
    "rule_id",
    "产品价值",
    "门线解读",
    "系统有没有编造",
)

ANXIETY_FP = (
    re.compile(r"否则就"),
    re.compile(r"不这样会"),
    re.compile(r"你注定"),
    re.compile(r"你必然"),
    re.compile(r"命中注定"),
)

TEMPLATE_FINGERPRINTS = (
    re.compile(r"把与「?.+?」?相关的体验持续带进你的生命结构"),
    re.compile(r"当这股能量运作成熟时"),
    re.compile(r"形成稳定贡献"),
    re.compile(r"如果.{0,6}被焦虑或外界压力带偏"),
    re.compile(r"活成过度反应或反复内耗"),
)

SOFT_VIOLATION_TYPES = frozenset({"english_leak"})


@dataclass(frozen=True)
class ValidationResult:
    violations: tuple[tuple[str, str], ...] = field(default=())

    @property
    def has_hard(self) -> bool:
        return any(kind not in SOFT_VIOLATION_TYPES for kind, _ in self.violations)

    @property
    def has_soft(self) -> bool:
        return any(kind in SOFT_VIOLATION_TYPES for kind, _ in self.violations)

    @property
    def ok(self) -> bool:
        return not self.violations


def strip_user_terms(text: str, user_terms: tuple[str, ...] | frozenset[str]) -> str:
    """剔除昵称/出生地拼音/用户问题原词，避免英文检测误杀合法用户输入；也用于日志脱敏。"""
    result = text or ""
    for term in sorted(set(user_terms), key=len, reverse=True):
        if term:
            result = result.replace(term, "")
    return result


def validate(text: str, facts: ChartFacts) -> ValidationResult:
    violations: list[tuple[str, str]] = []
    body = text or ""
    whitelist = facts.whitelist

    for match in GATE_RE.finditer(body):
        gate = int(match.group(1))
        if gate not in whitelist.gate_nums:
            violations.append(("fabricated_gate", match.group(1)))
    for match in CHANNEL_RE.finditer(body):
        code = f"{int(match.group(1)):02d}-{int(match.group(2)):02d}"
        if code not in whitelist.channel_codes:
            violations.append(("fabricated_channel", code))

    scrubbed = strip_user_terms(body, facts.user_term_whitelist)
    expected_authority = EXPECTED_AUTHORITY_TERMS.get(facts.authority_code)
    if expected_authority:
        # Exact Authority names are intentionally kept in English in the product UI.
        scrubbed = re.sub(re.escape(expected_authority), "", scrubbed, flags=re.IGNORECASE)
    english = ENGLISH_TERM_RE.search(scrubbed)
    if english:
        violations.append(("english_leak", english.group()))

    lowered = body.lower()
    for marker in POLLUTION:
        if marker in lowered:
            violations.append(("pollution", marker))
    for fingerprint in TEMPLATE_FINGERPRINTS:
        if fingerprint.search(body):
            violations.append(("template_cliche", fingerprint.pattern))
    for fingerprint in ANXIETY_FP:
        if fingerprint.search(body):
            violations.append(("anxiety_or_determinism", fingerprint.pattern))
    invented_composite = INVENTED_COMPOSITE_RE.search(body)
    if invented_composite:
        violations.append(("invented_composite", invented_composite.group()))
    if facts.channel_codes:
        activation_conflict = DEFINED_CHANNEL_ACTIVATION_RE.search(body)
        if activation_conflict:
            violations.append(("defined_channel_activation_conflict", activation_conflict.group()))
    violations.extend(_authority_name_conflicts(body, facts))
    violations.extend(_strategy_authority_conflicts(body, facts))

    return ValidationResult(violations=tuple(violations))


def _strategy_authority_conflicts(body: str, facts: ChartFacts) -> list[tuple[str, str]]:
    conflicts: list[tuple[str, str]] = []
    if facts.strategy_code == "respond":
        patterns = (
            re.compile(r"等待被邀请"),
            re.compile(r"只等待被问"),
            re.compile(r"被邀请.{0,8}(才|之后).{0,8}(启动|行动|开始)"),
        )
        for pattern in patterns:
            if pattern.search(body):
                conflicts.append(("strategy_conflict", "生产者的等待回应被误写成等待邀请"))
                break
    if facts.authority_code == "sacral":
        patterns = (
            re.compile(r"隔一晚.{0,8}(决定|再定|确认)"),
            re.compile(r"等情绪.{0,8}(过去|平稳|稳定)"),
            re.compile(r"情绪波.{0,8}(过去|之后).{0,8}(决定|确认)"),
        )
        for pattern in patterns:
            if pattern.search(body):
                conflicts.append(("authority_conflict", "荐骨权威被误写成情绪权威"))
                break
    return conflicts


def _authority_name_conflicts(body: str, facts: ChartFacts) -> list[tuple[str, str]]:
    expected = EXPECTED_AUTHORITY_TERMS.get(facts.authority_code)
    if not expected:
        return []
    for match in AUTHORITY_TERM_RE.finditer(body):
        if match.group().lower() != expected.lower():
            return [("authority_name_conflict", f"{match.group()} -> {expected}")]
    return []


def build_repair_instruction(violations: tuple[tuple[str, str], ...]) -> str:
    """把违规项明确回灌给模型做定向重写。"""
    lines = ["你上一稿有以下问题，请只针对这些问题重写整段，其余内容保持原意："]
    for kind, detail in violations:
        if kind == "fabricated_gate":
            lines.append(f"- 你提到了 {detail} 号闸门，但这张图里没有它，请删除相关内容。")
        elif kind == "fabricated_channel":
            lines.append(f"- 你提到了 {detail} 通道，但这张图里没有它，请删除相关内容。")
        elif kind == "english_leak":
            lines.append(f"- 你写了英文或符号「{detail}」，全部改成中文表达。")
        elif kind == "pollution":
            lines.append(f"- 「{detail}」是内部术语，用户不该看到，请删掉并用人话表达。")
        elif kind == "template_cliche":
            lines.append("- 你写了可以整句套给任何人的模板句，请删掉，换成只对这个人成立的具体表达。")
        elif kind == "anxiety_or_determinism":
            lines.append("- 你写了决定论或制造焦虑的表达，请改成或然语气（可能/常常/更容易）。")
        elif kind == "strategy_conflict":
            lines.append(f"- {detail}。生产者等待的是现实刺激后的身体回应，不是投射者式等待邀请，请重写。")
        elif kind == "authority_conflict":
            lines.append(f"- {detail}。荐骨答案是当下身体的有劲或没劲，不要写成等情绪波或隔夜确认。")
        elif kind == "invented_composite":
            lines.append(f"- 你把多个独立闸门拼成了不存在的结构「{detail}」。删除这个命名，只能分别解释真实闸门，或引用事实区明确给出的完整通道。")
        elif kind == "defined_channel_activation_conflict":
            lines.append("- 已定义通道本来就稳定存在，不会因为邀请或认可才被激活。邀请只可能影响这项能力何时、向谁表达，请重写。")
        elif kind == "authority_name_conflict":
            wrong, expected = detail.split(" -> ", 1)
            lines.append(f"- Authority 名称不能简写或混用。把「{wrong}」改为当前图表的精确名称「{expected}」。")
    lines.append("直接输出重写后的完整正文，不要解释你改了什么。")
    return "\n".join(lines)


def validate_and_repair(
    messages: list[dict[str, str]],
    facts: ChartFacts,
    chat,
    *,
    max_repair: int = 1,
) -> tuple[str, str]:
    """整段生成 → 校验 → 定向重写 ×max_repair → 仍硬违规则报告降级。

    chat: Callable[[list[dict]], str]，返回模型文本。
    返回 (text, status)；status ∈ {"ok", "repaired@N", "soft_leak", "fallback_after_repair_fail"}。
    绝不把硬违规文本交给调用方展示。
    """
    text = chat(messages)
    result = validate(text, facts)
    if result.ok:
        return text, "ok"
    for attempt in range(1, max_repair + 1):
        messages = [
            *messages,
            {"role": "assistant", "content": text},
            {"role": "user", "content": build_repair_instruction(result.violations)},
        ]
        text = chat(messages)
        result = validate(text, facts)
        if result.ok:
            return text, f"repaired@{attempt}"
    if result.has_hard:
        return "", "fallback_after_repair_fail"
    # 只剩软违规（英文残留）：不降级，交给调用方记脱敏日志。
    return text, "soft_leak"
