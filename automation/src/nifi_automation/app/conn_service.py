"""Connection/queue orchestration services."""

from __future__ import annotations

import sys
from typing import Optional

from ..infra import purge_adapter, status_adapter
from .client import open_client
from .models import AppConfig, CommandResult, ExitCode
from .status_rules import rollup_connections


def _log(config: AppConfig, message: str) -> None:
    if config.verbose:
        print(message, file=sys.stderr)


def truncate_all(*, config: AppConfig, force: bool = False, max_messages: Optional[int] = None) -> CommandResult:
    # force/max currently informational; NiFi drop endpoint clears entire queue.
    with open_client(config) as client:
        _log(config, "[conn] truncating root-level connections")
        summary = purge_adapter.truncate_connections(client)
    return CommandResult(
        message=f"Dropped FlowFiles from {summary['count']} connections",
        data={"connections": summary.get("connections", []), "errors": summary.get("errors")},
    )


def status(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        _log(config, "[conn] collecting connection status")
        connections = status_adapter.fetch_connections(client)["items"]
    rollup = rollup_connections(connections)
    exit_code = ExitCode.VALIDATION if rollup.worst == "BLOCKED" else ExitCode.SUCCESS
    return CommandResult(
        exit_code=exit_code,
        status_token=rollup.worst,
        data={"counts": rollup.counts, "worst": rollup.worst},
    )


def inspect(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        connections = status_adapter.fetch_connections(client)["items"]
    blocked = [item for item in connections if item.get("queuedCount", 0) or item.get("percentUseCount", 0)]
    return CommandResult(
        message=f"Found {len(blocked)} connections with queued data" if blocked else "All connections empty",
        data={"items": blocked},
    )
