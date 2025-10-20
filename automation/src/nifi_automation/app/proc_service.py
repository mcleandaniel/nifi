"""Processor-level orchestration services."""

from __future__ import annotations

import sys

from ..infra import ctrl_adapter, status_adapter
from .client import open_client
from .models import AppConfig, CommandResult, ExitCode


def _log(config: AppConfig, message: str) -> None:
    if config.verbose:
        print(message, file=sys.stderr)
from .status_rules import rollup_processors


def start_all(*, config: AppConfig) -> CommandResult:
    """Enable required controllers and start all processors."""

    with open_client(config) as client:
        _log(config, "[proc] enabling controller services required for processors")
        ctrl_adapter.enable_all_controllers(client, timeout=config.timeout_seconds)
        _log(config, "[proc] starting all processors")
        ctrl_adapter.start_all_processors(client, timeout=config.timeout_seconds)
        processors = status_adapter.fetch_processors(client)["items"]

    rollup = rollup_processors(processors)
    exit_code = ExitCode.VALIDATION if rollup.has_invalid else ExitCode.SUCCESS
    return CommandResult(
        exit_code=exit_code,
        message="Processors scheduled to RUNNING",
        data={"counts": rollup.counts, "worst": rollup.worst},
    )


def stop_all(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        _log(config, "[proc] stopping all processors")
        ctrl_adapter.stop_all_processors(client, timeout=config.timeout_seconds)
        processors = status_adapter.fetch_processors(client)["items"]

    rollup = rollup_processors(processors)
    return CommandResult(
        message="Processors scheduled to STOPPED",
        data={"counts": rollup.counts, "worst": rollup.worst},
    )


def status(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        _log(config, "[proc] collecting processor status")
        processors = status_adapter.fetch_processors(client)["items"]
    rollup = rollup_processors(processors)
    exit_code = ExitCode.VALIDATION if rollup.has_invalid else ExitCode.SUCCESS
    return CommandResult(
        exit_code=exit_code,
        status_token=rollup.worst,
        data={"counts": rollup.counts, "worst": rollup.worst},
    )


def inspect(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        processors = status_adapter.fetch_processors(client)["items"]
    invalid = [item for item in processors if item.get("validationStatus") not in {"VALID", "DISABLED"}]
    return CommandResult(
        message=f"Found {len(invalid)} processors with validation issues" if invalid else "No invalid processors",
        data={"items": invalid},
    )
