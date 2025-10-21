from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List, Tuple

import pytest

from nifi_automation.infra import layout_checker


class _DummyClient:
    pass


def _make_flow(processors: List[Tuple[str, float, float]], connections: List[Tuple[str, str]]):
    return {
        "processors": [
            {
                "component": {
                    "id": pid,
                    "name": pid,
                    "position": {"x": x, "y": y},
                }
            }
            for pid, x, y in processors
        ],
        "connections": [
            {
                "component": {
                    "source": {"id": sid, "type": "PROCESSOR"},
                    "destination": {"id": did, "type": "PROCESSOR"},
                }
            }
            for sid, did in connections
        ],
    }


def test_layout_detects_left_to_right_violation(monkeypatch: pytest.MonkeyPatch) -> None:
    def walker(_client: _DummyClient):
        yield ["root", "G"], _make_flow(
            processors=[("A", 200.0, 0.0), ("B", 230.0, 0.0)],
            connections=[("B", "A")],  # reversed; destination is not to the right
        )

    monkeypatch.setattr(layout_checker, "_walk_process_groups", walker)
    report = layout_checker.check_layout(_DummyClient(), min_dx=50.0)
    assert len(report["left_to_right_violations"]) == 1


def test_layout_detects_overlaps(monkeypatch: pytest.MonkeyPatch) -> None:
    def walker(_client: _DummyClient):
        yield ["root", "G"], _make_flow(
            processors=[("A", 100.0, 100.0), ("B", 120.0, 110.0)],  # close enough to overlap with threshold 40
            connections=[],
        )

    monkeypatch.setattr(layout_checker, "_walk_process_groups", walker)
    report = layout_checker.check_layout(_DummyClient(), min_dsep=50.0)
    assert len(report["overlaps"]) == 1

