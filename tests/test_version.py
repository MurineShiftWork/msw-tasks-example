"""Package version is importable and non-empty."""

from __future__ import annotations

from importlib.metadata import version


def test_version_is_non_empty_string():
    v = version("msw-tasks-example")
    assert isinstance(v, str)
    assert v
