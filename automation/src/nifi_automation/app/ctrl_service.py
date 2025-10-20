"""Controller-service orchestration helpers for the CLI refactor."""

from __future__ import annotations

from ..infra import ctrl_adapter, status_adapter
from .client import open_client
from .models import AppConfig, CommandResult, ExitCode
from .status_rules import rollup_controllers


def enable_all(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        summary = ctrl_adapter.enable_all_controllers(client, timeout=config.timeout_seconds)
        controllers = status_adapter.fetch_controllers(client)["items"]

    rollup = rollup_controllers(controllers)
    exit_code = ExitCode.VALIDATION if rollup.has_invalid else ExitCode.SUCCESS
    return CommandResult(
        exit_code=exit_code,
        message=f"Enabled {summary['count']} controller services",
        data={"counts": rollup.counts, "worst": rollup.worst},
    )


def disable_all(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        summary = ctrl_adapter.disable_all_controllers(client, timeout=config.timeout_seconds)
        controllers = status_adapter.fetch_controllers(client)["items"]

    rollup = rollup_controllers(controllers)
    return CommandResult(
        message=f"Disabled {summary['count']} controller services",
        data={"counts": rollup.counts, "worst": rollup.worst},
    )


def status(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        controllers = status_adapter.fetch_controllers(client)["items"]
    rollup = rollup_controllers(controllers)
    exit_code = ExitCode.VALIDATION if rollup.has_invalid else ExitCode.SUCCESS
    return CommandResult(
        exit_code=exit_code,
        status_token=rollup.worst,
        data={"counts": rollup.counts, "worst": rollup.worst},
    )


def inspect(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        controllers = status_adapter.fetch_controllers(client)["items"]
    invalid = [item for item in controllers if item.get("validationStatus") not in {"VALID", "DISABLED"}]
    return CommandResult(
        message=f"Found {len(invalid)} controller services with validation issues" if invalid else "No invalid controller services",
        data={"items": invalid},
    )
