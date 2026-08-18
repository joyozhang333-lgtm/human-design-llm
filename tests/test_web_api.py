from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from human_design.providers import DeepSeekAnswer, ProviderRequestError
from human_design.web_api import HumanDesignWebStore, create_app


@pytest.fixture(autouse=True)
def _disable_external_ai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.setenv("MINIMAX_API_KEY", "")
    monkeypatch.delenv("HD_GENERATION_MODE", raising=False)


def _client() -> TestClient:
    return TestClient(create_app(HumanDesignWebStore()))


def _create_chart(client: TestClient) -> dict:
    response = client.post(
        "/api/charts",
        json={
            "user_name": "测试用户",
            "gender": "male",
            "birth_date": "1970-02-04",
            "birth_time": "12:00",
            "timezone_name": "Asia/Shanghai",
            "city": "杭州",
            "region": "浙江",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_create_chart_requires_birth_time_for_formal_bodygraph() -> None:
    client = _client()
    response = client.post(
        "/api/charts",
        json={"birth_date": "1992-08-17", "timezone_name": "Asia/Shanghai"},
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "birth_time_required"
    assert "低精度引导" in response.json()["detail"]["message"]


def test_create_chart_returns_chart_and_bodygraph_svg() -> None:
    client = _client()
    payload = _create_chart(client)

    assert payload["chart_id"].startswith("chart_")
    assert payload["chart"]["summary"]["authority"]["code"] == "sacral"
    assert payload["birth_profile"]["gender"] == "male"
    assert payload["display_summary"]["type"]
    assert payload["display_summary"]["authority"] == "荐骨权威"
    assert payload["bodygraph_svg_url"].endswith("/bodygraph.svg")
    assert "<svg" in payload["bodygraph_svg"]
    assert "荐骨权威" in payload["bodygraph_svg"]
    assert "阿姬娜中心" in payload["bodygraph_svg"]
    # The web BodyGraph is graphic-only; the long booklet ships via /reading-book.
    assert "人类图解读本" not in payload["bodygraph_svg"]


def test_reading_book_endpoint_returns_structured_readable_sections() -> None:
    client = _client()
    chart = _create_chart(client)
    response = client.get(f"/api/charts/{chart['chart_id']}/reading-book")

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["chart_id"] == chart["chart_id"]
    assert payload["sections"], "reading book should contain sections"

    # Layout honours the PRD readability contract.
    layout = payload["layout"]
    assert layout["format"] == "responsive_html"
    assert layout["min_font_size"] >= 15
    assert layout["line_height"] >= 1.65

    titles = [section["title"] for section in payload["sections"]]
    assert "速览" in titles
    assert "核心身份" in titles

    for section in payload["sections"]:
        assert section["title"]
        assert isinstance(section["paragraphs"], list)
        assert isinstance(section["highlights"], list)
        for paragraph in section["paragraphs"]:
            assert len(paragraph) <= 120  # PRD: 每段不超过 120 个中文字符

    overview = next(section for section in payload["sections"] if section["title"] == "速览")
    assert overview["highlights"], "速览 should surface quick facts as highlights"
    followup = next(section for section in payload["sections"] if section["title"] == "可以继续追问")
    assert followup["highlights"], "follow-up questions should be surfaced as highlights"


def test_reading_book_endpoint_unknown_chart_returns_404() -> None:
    client = _client()
    response = client.get("/api/charts/chart_missing/reading-book")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "chart_not_found"


def test_body_energy_report_returns_structured_profile_and_export_markdown() -> None:
    client = _client()
    chart = _create_chart(client)
    response = client.post(
        "/api/reports",
        json={"chart_id": chart["chart_id"], "report_type": "body-energy"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["report_type"] == "body-energy"
    assert payload["focus"] == "growth"
    assert payload["body_energy"]["headline"] == "身体资源与灵性能量地图"
    assert len(payload["body_energy"]["center_notes"]) == 9
    assert "身体资源与能量管理补充" in payload["export_markdown"]
    assert "/Users/" not in payload["answer_markdown"]
    assert "/references/" not in payload["answer_markdown"]
    assert payload["citations"]
    assert "骶骨" not in payload["export_markdown"]


def test_talent_report_returns_deep_synthesis_profile() -> None:
    client = _client()
    chart = _create_chart(client)
    response = client.post(
        "/api/reports",
        json={"chart_id": chart["chart_id"], "report_type": "talent"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["report_type"] == "talent"
    assert payload["focus"] == "talent"
    assert payload["deep_synthesis"]["headline"] == "2/4 | 荐骨权威 纯生产者 天赋深挖"
    assert "02-14" in payload["deep_synthesis"]["structure_formula"]
    assert "方向化" in payload["answer_markdown"]
    assert "天赋深挖补充" in payload["export_markdown"]
    assert "非泛化检查" in payload["export_markdown"]
    assert any(block["key"] == "research-method" for block in payload["context_blocks"])
    assert "/Users/" not in payload["answer_markdown"]
    assert "骶骨" not in payload["export_markdown"]
    assert "当前聚焦" not in payload["answer_markdown"]
    assert "问题切口" not in payload["answer_markdown"]
    assert "焦点提示" not in payload["answer_markdown"]


def test_interpretation_map_endpoint_returns_v04_structured_map() -> None:
    client = _client()
    chart = _create_chart(client)
    response = client.post(
        "/api/interpretation-maps",
        json={"chart_id": chart["chart_id"], "map_type": "wealth", "depth": "deep"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["product_version"] == "0.5.0"
    assert payload["map_type"] == "wealth"
    assert payload["title"] == "财富地图"
    assert payload["overview"]
    assert payload["generation_mode"] == "fallback"
    assert "系统有没有编造" not in payload["overview"]
    assert payload["professional_facts"]
    assert payload["sections"][0]["items"]
    item_titles = [item["title"] for section in payload["sections"] for item in section["items"]]
    assert "财富来源：方向感加资源配置" in item_titles
    item = next(item for section in payload["sections"] for item in section["items"] if item["key"] == "wealth.02-14-main-track")
    assert item["diagnosis_depth"] == "deep"
    assert item["embodied_expression"]
    assert item["blind_spots"]
    assert item["stuck_patterns"]
    assert item["stuck_causes"]
    assert any("盘面机制" in cause and "现实场景" in cause for cause in item["stuck_causes"])
    assert payload["retrieved_knowledge"]
    assert payload["sources"]


def test_readings_main_returns_contract_fields() -> None:
    import re

    client = _client()
    chart = _create_chart(client)
    response = client.post("/api/readings/main", json={"chart_id": chart["chart_id"]})

    assert response.status_code == 200, response.text
    payload = response.json()
    # 前后端契约字段，不得擅改
    assert set(payload) == {"l1", "l2", "signature", "not_self", "detail_sections", "explore", "generation_mode"}
    assert payload["generation_mode"] == "fallback"  # 无 key 环境
    assert 40 <= len(payload["l1"]) <= 78
    paragraphs = [p for p in payload["l2"].split("\n\n") if p.strip()]
    assert len(paragraphs) == 4
    assert payload["signature"].startswith("活对了的体感")
    assert payload["not_self"].startswith("活拧了的体感")
    for section in payload["detail_sections"]:
        assert set(section) == {"key", "title", "summary"}
    for entry in payload["explore"]:
        assert set(entry) == {"key", "title", "hint"}
    assert [entry["key"] for entry in payload["explore"]] == ["talent", "mission", "body", "wealth", "relationship"]
    # 内容硬红线：零英文、零符号
    full_text = payload["l1"] + payload["l2"] + payload["signature"] + payload["not_self"]
    assert not re.search(r"[A-Za-z]{3,}", full_text)
    assert not re.search(r"[♃♄⛢♅⊕☊☋☉☽☿♀♂♆♇]", full_text)


def test_readings_main_uses_deepseek_when_dotenv_provider_is_configured(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "configured-for-test")
    monkeypatch.setenv("HD_GENERATION_MODE", "llm")
    monkeypatch.setenv("HD_CACHE_PATH", str(tmp_path / "generation.db"))
    responses = iter(
        (
            "你的生命力来自回应，做决定先听身体的有劲没劲；天赋先在独处里养熟，再让信任关系把你带到合适的位置。",
            "你的核心不是持续证明自己，而是等现实给出具体选项，再看身体有没有力量继续。02-14方向与资源通道让你在方向正确时更能集中资源。\n\n做决定时先回到荐骨权威。开放的头顶中心容易接住别人的问题，所以别在焦虑里替所有人找答案。\n\n你的人生角色是2/4，天然顺手的能力常被自己低估。先独处养熟，再让信任关系和作品把能力叫出来。\n\n人生主轴要从一次次正确回应里长出来。接近满足时继续做深，反复挫败时检查方向，答案不在图里，在你接下来怎么观察自己。",
        )
    )

    def fake_chat(self, messages):
        return DeepSeekAnswer(content=next(responses), provider="deepseek", model=self.model)

    monkeypatch.setattr("human_design.providers.DeepSeekClient.chat", fake_chat)
    client = _client()
    chart = _create_chart(client)
    response = client.post("/api/readings/main", json={"chart_id": chart["chart_id"]})

    assert response.status_code == 200, response.text
    assert response.json()["generation_mode"] == "llm"


def test_readings_detail_returns_lazy_body() -> None:
    client = _client()
    chart = _create_chart(client)
    for key in ("centers", "channels", "gates", "variables", "cross"):
        response = client.post("/api/readings/detail", json={"chart_id": chart["chart_id"], "key": key})
        assert response.status_code == 200, response.text
        payload = response.json()
        assert set(payload) == {"title", "body", "generation_mode"}
        assert payload["title"] and payload["body"]
        assert payload["generation_mode"] == "fallback"


def test_readings_detail_unknown_key_returns_422() -> None:
    client = _client()
    chart = _create_chart(client)
    response = client.post("/api/readings/detail", json={"chart_id": chart["chart_id"], "key": "nope"})
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "detail_key_invalid"


def test_readings_main_unknown_chart_returns_404() -> None:
    client = _client()
    response = client.post("/api/readings/main", json={"chart_id": "chart_missing"})
    assert response.status_code == 404


def test_chat_answers_are_chart_grounded_and_sessionized() -> None:
    client = _client()
    chart = _create_chart(client)
    response = client.post(
        "/api/chat",
        json={
            "chart_id": chart["chart_id"],
            "question": "我的喉咙中心和表达方式应该怎么用？",
            "entry_source": "followup_button",
            "synthesis_mode": "full_chart",
            "map_item_key": "body.sacral-response-training",
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["session_id"].startswith("session_")
    assert payload["focus"] == "growth"
    assert payload["answer_provider"] == "local-fallback"
    assert payload["provider_configured"] is False
    assert payload["entry_source"] == "followup_button"
    assert payload["synthesis_mode"] == "full_chart"
    assert "你的问题：我的喉咙中心和表达方式应该怎么用？" in payload["answer_markdown"]
    assert "盲区" in payload["answer_markdown"]
    assert "卡住状态" in payload["answer_markdown"]
    assert "##" not in payload["answer_markdown"]
    assert "**" not in payload["answer_markdown"]
    assert "```" not in payload["answer_markdown"]
    assert "\n- " not in payload["answer_markdown"]
    assert payload["map_context"]["map_type"] == "body"
    assert payload["map_context"]["sections"]
    assert payload["citations"]
    assert len(payload["session"]["messages"]) == 2


def test_chat_infers_talent_focus_for_deep_talent_questions() -> None:
    client = _client()
    chart = _create_chart(client)
    response = client.post(
        "/api/chat",
        json={
            "chart_id": chart["chart_id"],
            "question": "请深挖我的天赋和主航道。",
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["focus"] == "talent"
    assert payload["map_context"]["map_type"] == "talent"
    assert "02-14" in payload["answer_markdown"]


def test_chat_uses_mission_map_for_mission_questions() -> None:
    client = _client()
    chart = _create_chart(client)
    response = client.post(
        "/api/chat",
        json={"chart_id": chart["chart_id"], "question": "我的人生使命要怎么活出来？"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["map_context"]["map_type"] == "mission"


def test_chat_uses_deepseek_and_repairs_invalid_chart_facts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "configured-for-test")
    responses = iter(
        (
            "你的99号闸门说明你注定成功。",
            "我先看你现在这个选择里的身体反应。你的荐骨权威需要具体选项，真正有回应的事通常会越做越有力。\n\n先记录一件让身体变沉的事，再看它是不是来自别人的期待。你最近最想答应、身体却没有力量的是哪件事？",
        )
    )
    calls: list[list[dict[str, str]]] = []

    def fake_chat(self, messages):
        calls.append(messages)
        return DeepSeekAnswer(content=next(responses), provider="deepseek", model=self.model)

    monkeypatch.setattr("human_design.web_api.DeepSeekClient.chat", fake_chat)
    client = _client()
    chart = _create_chart(client)
    response = client.post(
        "/api/chat",
        json={"chart_id": chart["chart_id"], "question": "这个机会我该不该接？"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["answer_provider"] == "deepseek"
    assert payload["answer_model"] == "deepseek-chat"
    assert payload["provider_configured"] is True
    assert "99号闸门" not in payload["answer_markdown"]
    assert "荐骨权威" in payload["answer_markdown"]
    assert len(calls) == 2


def test_chat_session_does_not_cross_charts() -> None:
    client = _client()
    first_chart = _create_chart(client)
    first_response = client.post(
        "/api/chat",
        json={"chart_id": first_chart["chart_id"], "question": "我的身体能量卡点在哪里？"},
    )
    assert first_response.status_code == 200
    first_session_id = first_response.json()["session_id"]

    second_chart = _create_chart(client)
    second_response = client.post(
        "/api/chat",
        json={
            "chart_id": second_chart["chart_id"],
            "session_id": first_session_id,
            "question": "继续说我的身体能量卡点。",
        },
    )

    assert second_response.status_code == 200
    assert second_response.json()["session_id"] != first_session_id
    assert second_response.json()["session"]["chart_id"] == second_chart["chart_id"]


def test_reading_visual_returns_fallback_when_minimax_is_not_configured() -> None:
    client = _client()
    chart = _create_chart(client)
    response = client.post(
        "/api/images/reading-visual",
        json={"chart_id": chart["chart_id"], "prompt": "身体能量解读视觉封面"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["provider"] == "minimax"
    assert payload["provider_configured"] is False
    assert payload["image_url"] is None
    assert payload["fallback_bodygraph_svg_url"].endswith("/bodygraph.svg")
    assert "荐骨权威" in payload["prompt"]


def test_reading_visual_falls_back_when_minimax_request_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MINIMAX_API_KEY", "configured-but-invalid")

    def fail_generate(*_args, **_kwargs):
        raise ProviderRequestError("invalid api key")

    monkeypatch.setattr("human_design.web_api.MiniMaxImageClient.generate", fail_generate)
    client = _client()
    chart = _create_chart(client)
    response = client.post(
        "/api/images/reading-visual",
        json={"chart_id": chart["chart_id"], "prompt": "职业天赋报告封面"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["provider"] == "minimax"
    assert payload["provider_configured"] is True
    assert payload["image_url"] is None
    assert payload["fallback_bodygraph_svg_url"].endswith("/bodygraph.svg")
