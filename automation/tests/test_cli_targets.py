from __future__ import annotations

import pytest

from nifi_automation.cli.targets import normalize_target


def test_normalize_target_aliases() -> None:
    pairs = {
        "flow": "flow",
        "flows": "flow",
        "processor": "processors",
        "processors": "processors",
        "proc": "processors",
        "procs": "processors",
        "controller": "controllers",
        "controllers": "controllers",
        "cont": "controllers",
        "connection": "connections",
        "connections": "connections",
        "queue": "connections",
        "queues": "connections",
        "conn": "connections",
    }
    for alias, canonical in pairs.items():
        assert normalize_target(alias).name == canonical


def test_normalize_target_invalid_alias() -> None:
    with pytest.raises(ValueError):
        normalize_target("con")

    with pytest.raises(ValueError):
        normalize_target("unknown")
