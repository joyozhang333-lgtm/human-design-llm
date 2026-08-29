from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys
import zipfile

import pytest

from human_design.installer import (
    SkillInstallError,
    default_codex_home,
    install_agent_skill,
    install_skill,
    package_skill_bundle,
    resolve_agent_skill_target,
    resolve_skill_target,
)


def test_resolve_skill_target_defaults_to_codex_skills(tmp_path: Path) -> None:
    target = resolve_skill_target("human-design", codex_home=tmp_path)

    assert target == tmp_path / "skills" / "human-design"


def test_default_codex_home_matches_the_documented_user_skill_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("CODEX_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))

    assert default_codex_home() == tmp_path / ".codex"


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
    (source / ".env").write_text("SECRET=never-copy", encoding="utf-8")
    (source / "cache.db").write_text("private-cache", encoding="utf-8")
    (source / ".env.example").write_text("SECRET=", encoding="utf-8")

    result = install_skill(
        source,
        codex_home=tmp_path,
        mode="copy",
        skill_name="human-design-copy",
    )
    target = Path(result.target_dir)

    assert target.is_dir()
    assert (target / "SKILL.md").read_text(encoding="utf-8") == "# demo"
    assert not (target / ".env").exists()
    assert not (target / "cache.db").exists()
    assert (target / ".env.example").exists()


def test_install_skill_requires_force_when_target_exists(tmp_path: Path) -> None:
    source = tmp_path / "source-skill"
    source.mkdir()
    (source / "SKILL.md").write_text("# demo", encoding="utf-8")

    install_skill(source, codex_home=tmp_path)

    with pytest.raises(SkillInstallError):
        install_skill(source, codex_home=tmp_path)


@pytest.mark.parametrize(
    ("host", "relative"),
    (
        ("codex", ".agents/skills/human-design"),
        ("claude-code", ".claude/skills/human-design"),
        ("deepseek-harness", ".dsh/skills/human-design"),
        ("huggingface", ".agents/skills/human-design"),
        ("openclaw", ".agents/skills/human-design"),
        ("workbuddy", ".codebuddy/skills/human-design"),
    ),
)
def test_project_agent_targets_match_host_discovery_paths(tmp_path: Path, host: str, relative: str) -> None:
    target = resolve_agent_skill_target(host, project_dir=tmp_path)
    assert target == tmp_path / relative


@pytest.mark.parametrize(
    ("host", "relative"),
    (
        ("codex", ".codex/skills/human-design"),
        ("claude-code", ".claude/skills/human-design"),
        ("deepseek-harness", ".dsh/skills/human-design"),
        ("huggingface", ".agents/skills/human-design"),
        ("workbuddy", ".workbuddy/skills/human-design"),
    ),
)
def test_user_agent_targets_match_host_discovery_paths(tmp_path: Path, host: str, relative: str) -> None:
    target = resolve_agent_skill_target(host, scope="user", home_dir=tmp_path)
    assert target == tmp_path / relative


def test_agent_install_copies_self_contained_bundle(tmp_path: Path) -> None:
    source = tmp_path / "bundle"
    (source / "scripts").mkdir(parents=True)
    (source / "SKILL.md").write_text(
        "---\nname: human-design\ndescription: demo\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    (source / "scripts" / "run.py").write_text("print('ok')\n", encoding="utf-8")

    result = install_agent_skill(source, host="claude", project_dir=tmp_path / "project")
    target = Path(result.target_dir)

    assert target == tmp_path / "project" / ".claude" / "skills" / "human-design"
    assert (target / "SKILL.md").is_file()
    assert (target / "scripts" / "run.py").is_file()


def test_workbuddy_zip_is_deterministic_and_secret_free(tmp_path: Path) -> None:
    source = tmp_path / "bundle"
    source.mkdir()
    (source / "SKILL.md").write_text(
        "---\nname: human-design\ndescription: demo\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    (source / ".env").write_text("SECRET=never-package\n", encoding="utf-8")
    (source / ".env.production").write_text("API_KEY=never-package\n", encoding="utf-8")
    (source / "private.pem").write_text("PRIVATE KEY\n", encoding="utf-8")
    (source / "credentials.json").write_text('{"token":"never-package"}\n', encoding="utf-8")
    first = package_skill_bundle(source, tmp_path / "first.zip")
    second = package_skill_bundle(source, tmp_path / "second.zip")

    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as archive:
        assert archive.namelist() == ["SKILL.md"]
        assert b"SECRET" not in archive.read("SKILL.md")


@pytest.mark.parametrize(
    "birth_args",
    (
        ("1990-01-01T12:00:00",),
        ("1990-01-01T12:00:00", "--city", "杭州"),
    ),
)
def test_canonical_agent_script_rejects_ambiguous_or_unconsented_timezone(
    birth_args: tuple[str, ...],
) -> None:
    root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        (
            sys.executable,
            str(root / "skills/human-design/scripts/human_design_agent.py"),
            "chart",
            *birth_args,
        ),
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    assert "input error" in completed.stderr


def test_repository_agent_entrypoints_load_the_canonical_skill() -> None:
    root = Path(__file__).resolve().parents[1]
    for relative in (
        ".agents/skills/human-design/SKILL.md",
        ".claude/skills/human-design/SKILL.md",
        ".dsh/skills/human-design/SKILL.md",
        ".codebuddy/skills/human-design/SKILL.md",
    ):
        content = (root / relative).read_text(encoding="utf-8")
        assert content.startswith("---\n")
        assert "name: human-design" in content
        assert "skills/human-design/SKILL.md" in content


def test_canonical_skill_installs_the_current_release() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "skills/human-design/SKILL.md").read_text(encoding="utf-8")

    assert "@v0.7.1" in content
    assert "@v0.7.0" not in content


def test_canonical_agent_script_generates_a_grounded_channel_report() -> None:
    root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        (
            sys.executable,
            str(root / "skills/human-design/scripts/human_design_agent.py"),
            "report",
            "1988-10-09T20:30:00+08:00",
            "--map-type",
            "channels",
        ),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["map_type"] == "channels"
    assert payload["sections"]


def test_package_only_does_not_install_into_project(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "workbuddy.zip"
    subprocess.run(
        (
            sys.executable,
            str(root / "scripts/install_skill.py"),
            "--target",
            "workbuddy",
            "--project-dir",
            str(tmp_path),
            "--package",
            str(output),
            "--package-only",
        ),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    assert output.is_file()
    assert not (tmp_path / ".codebuddy").exists()
