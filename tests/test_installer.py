from __future__ import annotations

from pathlib import Path

import pytest

from human_design.installer import SkillInstallError, install_skill, resolve_skill_target


def test_resolve_skill_target_defaults_to_codex_skills(tmp_path: Path) -> None:
    target = resolve_skill_target("human-design", codex_home=tmp_path)

    assert target == tmp_path / "skills" / "human-design"


def test_install_skill_creates_symlink(tmp_path: Path) -> None:
    source = tmp_path / "source-skill"
    source.mkdir()
    (source / "SKILL.md").write_text("# demo", encoding="utf-8")

    result = install_skill(source, codex_home=tmp_path, force=False)
    target = Path(result.target_dir)

    assert target.is_symlink()
    assert target.resolve() == source.resolve()


def test_install_skill_can_copy(tmp_path: Path) -> None:
    source = tmp_path / "source-skill"
    source.mkdir()
    (source / "SKILL.md").write_text("# demo", encoding="utf-8")

    result = install_skill(
        source,
        codex_home=tmp_path,
        mode="copy",
        skill_name="human-design-copy",
    )
    target = Path(result.target_dir)

    assert target.is_dir()
    assert (target / "SKILL.md").read_text(encoding="utf-8") == "# demo"


def test_install_skill_requires_force_when_target_exists(tmp_path: Path) -> None:
    source = tmp_path / "source-skill"
    source.mkdir()
    (source / "SKILL.md").write_text("# demo", encoding="utf-8")

    install_skill(source, codex_home=tmp_path)

    with pytest.raises(SkillInstallError):
        install_skill(source, codex_home=tmp_path)
