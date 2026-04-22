from __future__ import annotations

import enum
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version

PYHD_UPSTREAM = "https://github.com/ppo/pyhd"
PYHD_NOTES = (
    "Applied runtime Enum alias compatibility for Python versions without Enum._add_alias_.",
    "Applied runtime Enum value-alias compatibility for Python versions without Enum._add_value_alias_.",
    "Avoided upstream pyhd Chart.to_model()/to_light_model() because current main branch export is broken.",
)


def _patch_enum_aliases() -> tuple[str, ...]:
    applied: list[str] = []

    if not hasattr(enum.Enum, "_add_alias_"):
        def _add_alias_(self: enum.Enum, name: str) -> None:
            self.__class__._member_map_[name] = self

        enum.Enum._add_alias_ = _add_alias_  # type: ignore[attr-defined]
        applied.append(PYHD_NOTES[0])

    if not hasattr(enum.Enum, "_add_value_alias_"):
        def _add_value_alias_(self: enum.Enum, value: object) -> None:
            self.__class__._value2member_map_[value] = self

        enum.Enum._add_value_alias_ = _add_value_alias_  # type: ignore[attr-defined]
        applied.append(PYHD_NOTES[1])

    return tuple(applied)


def load_pyhd_chart() -> tuple[type, str | None, tuple[str, ...]]:
    notes = list(_patch_enum_aliases())

    try:
        module = import_module("pyhd")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "`pyhd` 未安装。先运行 `python -m pip install -r requirements-dev.txt`。"
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"`pyhd` 导入失败：{exc}") from exc

    try:
        installed_version = version("pyhd")
    except PackageNotFoundError:
        installed_version = None

    notes.append(PYHD_NOTES[2])
    return module.Chart, installed_version, tuple(notes)
