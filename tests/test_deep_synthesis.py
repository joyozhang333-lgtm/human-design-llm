from __future__ import annotations

from human_design.deep_synthesis import build_deep_synthesis_profile, render_deep_synthesis_markdown
from human_design.engine import calculate_chart
from human_design.input import normalize_birth_input


def test_deep_synthesis_builds_non_generic_talent_profile() -> None:
    chart = calculate_chart(normalize_birth_input("1995-03-03T18:30:00+08:00"))
    profile = build_deep_synthesis_profile(chart, question="请深挖我的天赋")
    payload = str(profile.to_dict())

    assert profile.headline == "2/4 | 荐骨权威 纯生产者 天赋深挖"
    assert "纯生产者 + 荐骨权威 + 2/4" in profile.structure_formula
    assert "02-14" in profile.structure_formula
    assert "方向化" in payload
    assert "资源配置" in payload
    assert "问题定位" in payload
    assert "混乱整合" in payload
    assert "不是只按人生角色" in payload
    assert "只列这张图实际激活的闸门" in payload
    assert "骶骨" not in payload
    assert "阿扎那" not in payload


def test_deep_synthesis_markdown_contains_experiments_and_sources() -> None:
    chart = calculate_chart(normalize_birth_input("1995-03-03T18:30:00+08:00"))
    profile = build_deep_synthesis_profile(chart)
    markdown = render_deep_synthesis_markdown(profile)

    assert "# 人类图天赋深挖" in markdown
    assert "## 研究方法" in markdown
    assert "## 非泛化检查" in markdown
    assert "## 30 天实验" in markdown
    assert "02-14 资源投放表" in markdown
    assert any(source.code == "official-foundation" for source in profile.research_sources)
