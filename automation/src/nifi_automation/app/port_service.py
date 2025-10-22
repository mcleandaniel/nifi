"""Port-level orchestration services (input/output ports)."""

from __future__ import annotations

import sys

from ..infra import port_adapter, status_adapter
from .client import open_client
from .models import AppConfig, CommandResult, ExitCode
from .status_rules import rollup_ports


def _log(config: AppConfig, message: str) -> None:
    if config.verbose:
        print(message, file=sys.stderr)


def start_all(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        _log(config, "[port] starting all input/output ports")
        summary = port_adapter.start_all_ports(client)
        ports = status_adapter.fetch_ports(client)["items"]
    roll = rollup_ports(ports)
    exit_code = ExitCode.VALIDATION if roll.has_invalid else ExitCode.SUCCESS
    return CommandResult(
        exit_code=exit_code,
        message=f"Started {summary['count']} ports",
        data={"counts": roll.counts, "worst": roll.worst},
    )


def stop_all(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        _log(config, "[port] stopping all input/output ports")
        summary = port_adapter.stop_all_ports(client)
        ports = status_adapter.fetch_ports(client)["items"]
    roll = rollup_ports(ports)
    return CommandResult(
        message=f"Stopped {summary['count']} ports",
        data={"counts": roll.counts, "worst": roll.worst},
    )


def status(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        _log(config, "[port] collecting port status")
        ports = status_adapter.fetch_ports(client)["items"]
    roll = rollup_ports(ports)
    exit_code = ExitCode.VALIDATION if roll.has_invalid else ExitCode.SUCCESS
    return CommandResult(
        exit_code=exit_code,
        status_token=roll.worst,
        data={"counts": roll.counts, "worst": roll.worst},
    )


def inspect(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        ports = status_adapter.fetch_ports(client)["items"]
    invalid = [p for p in ports if (p.get("validationErrors") or [])]
    return CommandResult(
        message=f"Found {len(invalid)} ports with validation issues" if invalid else "No invalid ports",
        data={"items": invalid},
    )
