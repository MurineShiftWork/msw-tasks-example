"""Package version is importable and non-empty."""

from __future__ import annotations

from importlib.metadata import version


def test_version_is_non_empty_string():
    v = version("msw-tasks-example")
    assert isinstance(v, str)
    assert v


def test_version_file_is_owned_by_this_distribution():
    # murineshiftwork is a namespace shared by several distributions; a shared
    # murineshiftwork/_version.py would be overwritten by whichever installs last.
    import tomllib
    from pathlib import Path

    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    cfg = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    version_file = cfg["tool"]["hatch"]["build"]["hooks"]["vcs"]["version-file"]
    assert version_file == "src/murineshiftwork/_version_msw_tasks_example.py"
