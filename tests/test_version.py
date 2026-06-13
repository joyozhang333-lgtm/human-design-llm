from __future__ import annotations

import tomllib
from pathlib import Path

from human_design import __version__

ROOT = Path(__file__).resolve().parents[1]


def _pyproject_version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as fh:
        return tomllib.load(fh)["project"]["version"]


def test_package_version_matches_pyproject() -> None:
    """The exported package version must stay in sync with pyproject.toml.

    These are two independent sources of truth (a Python module and the
    build metadata). A release that bumps one but not the other would ship
    a mismatched version; this guard catches that drift.
    """
    assert __version__ == _pyproject_version()
