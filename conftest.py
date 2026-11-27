"""Pytest configuration anchoring default basetemp to the repository root.

Avoids relative ``--basetemp`` in ``pyproject.toml`` ``addopts`` so running
pytest from an external working directory never creates or wipes a relative
``.pytest_temp`` folder outside the repository (T-20261114-932985855).
Uses a per-process subdirectory so nested or concurrent pytest invocations do
not ``rmtree`` each other's active ``basetemp`` on Windows.
"""
from __future__ import annotations

import os
from typing import Any


def pytest_configure(config: Any) -> None:
    if getattr(config.option, "basetemp", None) is None:
        config.option.basetemp = str(config.rootpath / ".pytest_temp" / f"run-{os.getpid()}")
