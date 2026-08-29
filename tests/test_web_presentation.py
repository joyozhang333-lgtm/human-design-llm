from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_reading_ui_does_not_render_internal_product_labels() -> None:
    reading = (ROOT / "web" / "src" / "reading.tsx").read_text(encoding="utf-8")
    banned_fragments = (
        'className="consult-fab"',
        "<span>基本配置</span>",
        "<span>全盘先读</span>",
        "<span>当前章节</span>",
        "个人主题报告",
        "继续和咨询师聊：",
        "说人话的解读",
    )

    for fragment in banned_fragments:
        assert fragment not in reading


def test_consultation_is_a_separate_reading_workspace() -> None:
    reading = (ROOT / "web" / "src" / "reading.tsx").read_text(encoding="utf-8")
    styles = (ROOT / "web" / "src" / "styles.css").read_text(encoding="utf-8")

    assert 'className={chatOpen ? "reading-workspace with-chat" : "reading-workspace"}' in reading
    assert "conversation-context" in reading
    assert ".reading-workspace.with-chat" in styles
    assert ".consultation.open" in styles
    assert ".consult-fab" not in styles


def test_consultation_navigation_does_not_reuse_stale_report_context() -> None:
    reading = (ROOT / "web" / "src" / "reading.tsx").read_text(encoding="utf-8")

    assert 'className="brand-button" onClick={returnToChart}' in reading
    assert 'sendQuestion(next, null, "chat_input", reportKey ?? null)' in reading
    assert "itemKey === null ? undefined : itemKey ?? chatContext?.itemKey" in reading


def test_public_web_version_is_v07() -> None:
    version = (ROOT / "web" / "src" / "version.ts").read_text(encoding="utf-8")
    assert 'PUBLIC_VERSION = "V0.7"' in version
