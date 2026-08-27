from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import zipfile


class SkillInstallError(RuntimeError):
    """Raised when the skill cannot be installed into the target agent directory."""


@dataclass(frozen=True)
class SkillInstallResult:
    skill_name: str
    source_dir: str
    target_dir: str
    mode: str


SUPPORTED_AGENT_HOSTS = (
    "codex",
    "claude-code",
    "deepseek-harness",
    "huggingface",
    "openclaw",
    "workbuddy",
)

HOST_ALIASES = {
    "claude": "claude-code",
    "dsh": "deepseek-harness",
    "deepseek": "deepseek-harness",
    "hf": "huggingface",
    "codebuddy": "workbuddy",
}

PROJECT_SKILL_ROOTS = {
    "codex": (".agents", "skills"),
    "claude-code": (".claude", "skills"),
    "deepseek-harness": (".dsh", "skills"),
    "huggingface": (".agents", "skills"),
    "openclaw": (".agents", "skills"),
    "workbuddy": (".codebuddy", "skills"),
}

USER_SKILL_ROOTS = {
    "codex": (".codex", "skills"),
    "claude-code": (".claude", "skills"),
    "deepseek-harness": (".dsh", "skills"),
    "huggingface": (".agents", "skills"),
    "openclaw": (".agents", "skills"),
    "workbuddy": (".workbuddy", "skills"),
}


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
        shutil.copytree(source, target, ignore=_copy_ignore)
    else:
        raise SkillInstallError(f"不支持的安装模式：{mode}")

    return SkillInstallResult(
        skill_name=skill_name,
        source_dir=str(source),
        target_dir=str(target),
        mode=mode,
    )


def normalize_agent_host(host: str) -> str:
    normalized = HOST_ALIASES.get(host.strip().lower(), host.strip().lower())
    if normalized not in SUPPORTED_AGENT_HOSTS:
        raise SkillInstallError(
            f"不支持的 Agent：{host}。可选值：{', '.join(SUPPORTED_AGENT_HOSTS)}"
        )
    return normalized


def resolve_agent_skill_target(
    host: str,
    *,
    scope: str = "project",
    skill_name: str = "human-design",
    project_dir: str | Path | None = None,
    home_dir: str | Path | None = None,
) -> Path:
    host_key = normalize_agent_host(host)
    if scope == "project":
        base = Path(project_dir).expanduser().resolve() if project_dir is not None else Path.cwd().resolve()
        return base.joinpath(*PROJECT_SKILL_ROOTS[host_key], skill_name)
    if scope == "user":
        base = Path(home_dir).expanduser().resolve() if home_dir is not None else Path.home()
        return base.joinpath(*USER_SKILL_ROOTS[host_key], skill_name)
    raise SkillInstallError("scope 只支持 project 或 user")


def install_agent_skill(
    source_dir: str | Path,
    *,
    host: str,
    scope: str = "project",
    skill_name: str = "human-design",
    project_dir: str | Path | None = None,
    home_dir: str | Path | None = None,
    mode: str = "copy",
    force: bool = False,
) -> SkillInstallResult:
    source = Path(source_dir).expanduser().resolve()
    _validate_skill_bundle(source)
    target = resolve_agent_skill_target(
        host,
        scope=scope,
        skill_name=skill_name,
        project_dir=project_dir,
        home_dir=home_dir,
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        if not force:
            raise SkillInstallError(f"目标已存在：{target}。如需覆盖，请传 force=True。")
        _remove_existing_target(target)
    if mode == "copy":
        shutil.copytree(source, target, ignore=_copy_ignore)
    elif mode == "link":
        target.symlink_to(source, target_is_directory=True)
    else:
        raise SkillInstallError(f"不支持的安装模式：{mode}")
    return SkillInstallResult(
        skill_name=skill_name,
        source_dir=str(source),
        target_dir=str(target),
        mode=mode,
    )


def package_skill_bundle(
    source_dir: str | Path,
    output_path: str | Path,
) -> Path:
    """Create a deterministic, WorkBuddy-uploadable Skill ZIP."""
    source = Path(source_dir).expanduser().resolve()
    _validate_skill_bundle(source)
    output = Path(output_path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in _skill_files(source):
            relative = path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if path.parent.name == "scripts" else 0o644) << 16
            archive.writestr(info, path.read_bytes())
    return output


def _validate_skill_bundle(source: Path) -> None:
    skill_file = source / "SKILL.md"
    if not source.is_dir() or not skill_file.is_file():
        raise SkillInstallError(f"Skill 包缺少 SKILL.md：{source}")
    header = skill_file.read_text(encoding="utf-8")[:2048]
    if not header.startswith("---\n") or "\nname: human-design\n" not in header:
        raise SkillInstallError("SKILL.md 必须包含 name: human-design 的 YAML frontmatter")
    for path in source.rglob("*"):
        if path.is_symlink():
            raise SkillInstallError(f"Skill 包不能包含符号链接：{path}")


def _skill_files(source: Path) -> tuple[Path, ...]:
    files = []
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(source).parts
        if _copy_ignore(str(path.parent), [path.name]):
            continue
        if any(part in {"__pycache__", ".pytest_cache"} for part in relative_parts):
            continue
        files.append(path)
    return tuple(sorted(files, key=lambda item: item.relative_to(source).as_posix()))


def _copy_ignore(directory: str, names: list[str]) -> set[str]:
    """Keep local secrets, caches, build output, and VCS metadata out of copied skills."""
    ignored_names = {
        ".git",
        ".venv",
        ".pytest_cache",
        ".cache",
        ".env",
        "node_modules",
        "dist",
        "outputs",
        "__pycache__",
        "cache.db",
        "cache.db-wal",
        "cache.db-shm",
    }
    private_suffixes = (".pem", ".key", ".p8", ".p12", ".pfx", ".jks", ".keystore")
    private_names = {
        ".npmrc",
        ".pypirc",
        ".netrc",
        "credentials.json",
        "service-account.json",
        "id_rsa",
        "id_ed25519",
    }
    ignored = set()
    for name in names:
        lower = name.lower()
        is_private_env = (lower.startswith(".env") and lower != ".env.example") or lower.endswith(".env")
        if (
            name in ignored_names
            or lower in private_names
            or is_private_env
            or lower.endswith((".pyc", ".pyo", *private_suffixes))
        ):
            ignored.add(name)
    return ignored


def _remove_existing_target(target: Path) -> None:
    if target.is_symlink() or target.is_file():
        target.unlink()
        return
    if target.is_dir():
        shutil.rmtree(target)
        return
    raise SkillInstallError(f"无法处理已有目标：{target}")
