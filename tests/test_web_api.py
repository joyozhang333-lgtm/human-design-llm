from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from human_design.providers import ProviderRequestError
from human_design.web_api import HumanDesignWebStore, create_app


@pytest.fixture(autouse=True)
def _disable_external_ai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "")
    monkeypatch.setenv("MINIMAX_API_KEY", "")


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
    assert payload["product_version"] == "0.4.0"
    assert payload["map_type"] == "wealth"
    assert payload["title"] == "财富地图"
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
