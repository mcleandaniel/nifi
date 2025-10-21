from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import pytest

from nifi_automation.app.models import AppConfig, ExitCode
from nifi_automation.app import flow_service
from nifi_automation.infra import status_adapter, diag_adapter


@contextmanager
def _dummy_client() -> Iterator[object]:
    yield object()


def test_status_flow_fails_on_bulletins(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch open_client to avoid real HTTP calls
    monkeypatch.setattr(flow_service, "open_client", lambda config: _dummy_client())

    # Processors include a bulletin
    monkeypatch.setattr(
        status_adapter,
        "fetch_processors",
        lambda client: {
            "items": [
                {
                    "id": "p1",
                    "name": "TestProc",
                    "path": "root",
                    "state": "RUNNING",
                    "validationStatus": "VALID",
                    "validationErrors": [],
                    "bulletins": [{"level": "WARN", "message": "Sample bulletin"}],
                }
            ]
        },
    )
    # Controllers healthy
    monkeypatch.setattr(
        status_adapter,
        "fetch_controllers",
        lambda client: {"items": [{"state": "ENABLED"}]},
    )
    # No connections
    monkeypatch.setattr(status_adapter, "fetch_connections", lambda client: {"items": []})

    config = AppConfig(
        base_url=None,
        username=None,
        password=None,
        token=None,
        timeout_seconds=5.0,
        output="json",
        verbose=False,
        dry_run=False,
        fail_on_bulletins=True,
    )

    result = flow_service.status_flow(config=config)
    assert result.exit_code == ExitCode.VALIDATION


def test_inspect_flow_fails_on_queue_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(flow_service, "open_client", lambda config: _dummy_client())

    # Diagnostics details with non-empty connection
    monkeypatch.setattr(
        diag_adapter,
        "gather_validation_details",
        lambda client: {
            "invalid_processors": [],
            "invalid_ports": [],
            "bulletins": {"processors": [], "process_groups": []},
            "connections": {
                "blocked_or_nonempty": [
                    {
                        "id": "c1",
                        "name": "Conn",
                        "path": "root",
                        "queuedCount": 10,
                        "percentUseCount": 0.0,
                        "percentUseBytes": 0.0,
                    }
                ],
                "totals": {"all": 1, "nonempty": 1},
            },
        },
    )

    config = AppConfig(
        base_url=None,
        username=None,
        password=None,
        token=None,
        timeout_seconds=5.0,
        output="json",
        verbose=False,
        dry_run=False,
        queue_count_threshold=5,
    )

    result = flow_service.inspect_flow(config=config)
    assert result.exit_code == ExitCode.VALIDATION
    assert result.message.startswith("No invalid components")

