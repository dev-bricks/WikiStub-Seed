"""Pytest configuration anchoring default basetemp to the repository root.

Avoids relative ``--basetemp`` in ``pyproject.toml`` ``addopts`` so running
pytest from an external working directory never creates or wipes a relative
``.pytest_temp`` folder outside the repository (T-20261114-932985855).
Pre-creates ``.pytest_temp`` and uses a per-process subdirectory so fresh
checkouts and nested/concurrent pytest runs work cleanly across platforms.
"""
from __future__ import annotations

import os
from typing import Any


def pytest_configure(config: Any) -> None:
    if getattr(config.option, "basetemp", None) is None:
        base_root = config.rootpath / ".pytest_temp"
        base_root.mkdir(mode=0o700, exist_ok=True)
        config.option.basetemp = str(base_root / f"run-{os.getpid()}")
