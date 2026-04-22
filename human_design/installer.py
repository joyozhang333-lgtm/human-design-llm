from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil


class SkillInstallError(RuntimeError):
    """Raised when the skill cannot be installed into the target Codex directory."""


@dataclass(frozen=True)
class SkillInstallResult:
    skill_name: str
    source_dir: str
    target_dir: str
    mode: str


def default_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".codex"


def resolve_skill_target(
    skill_name: str,
    *,
    codex_home: Path | None = None,
) -> Path:
    base = codex_home if codex_home is not None else default_codex_home()
    return base / "skills" / skill_name


def install_skill(
    source_dir: str | Path,
    *,
    skill_name: str = "human-design",
    codex_home: str | Path | None = None,
    mode: str = "link",
    force: bool = False,
) -> SkillInstallResult:
    source = Path(source_dir).resolve()
    if not (source / "SKILL.md").exists():
        raise SkillInstallError(f"源目录里缺少 SKILL.md：{source}")

    target = resolve_skill_target(
        skill_name,
        codex_home=Path(codex_home).expanduser().resolve()
        if codex_home is not None
        else None,
    )
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() or target.is_symlink():
        if not force:
            raise SkillInstallError(
                f"目标已存在：{target}。如需覆盖，请传 force=True。"
            )
        _remove_existing_target(target)

    if mode == "link":
        target.symlink_to(source, target_is_directory=True)
    elif mode == "copy":
        shutil.copytree(source, target)
    else:
        raise SkillInstallError(f"不支持的安装模式：{mode}")

    return SkillInstallResult(
        skill_name=skill_name,
        source_dir=str(source),
        target_dir=str(target),
        mode=mode,
    )


def _remove_existing_target(target: Path) -> None:
    if target.is_symlink() or target.is_file():
        target.unlink()
        return
    if target.is_dir():
        shutil.rmtree(target)
        return
    raise SkillInstallError(f"无法处理已有目标：{target}")
