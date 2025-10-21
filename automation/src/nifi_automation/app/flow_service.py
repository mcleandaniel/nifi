"""Application-layer orchestrations for NiFi flow operations."""

from __future__ import annotations

import time
from pathlib import Path
import sys

from ..infra import ctrl_adapter, deploy_adapter, diag_adapter, purge_adapter, status_adapter
from .client import open_client
from .errors import TimeoutError, ValidationError
from .models import AppConfig, CommandResult, ExitCode
from .status_rules import rollup_controllers, rollup_flow, rollup_processors, rollup_connections

POLL_INTERVAL = 0.5


def _log(config: AppConfig, message: str) -> None:
    if config.verbose:
        print(message, file=sys.stderr)


def _await_stable_states(config: AppConfig, client) -> None:
    deadline = time.time() + config.timeout_seconds
    while True:
        processors = status_adapter.fetch_processors(client)["items"]
        controllers = status_adapter.fetch_controllers(client)["items"]
        proc_roll = rollup_processors(processors)
        ctrl_roll = rollup_controllers(controllers)
        if proc_roll.has_invalid or ctrl_roll.has_invalid:
            details = diag_adapter.gather_validation_details(client)
            raise ValidationError("Invalid components detected", details=details)
        if not proc_roll.has_transitional and not ctrl_roll.has_transitional:
            return
        if time.time() > deadline:
            raise TimeoutError("Components did not settle into a stable state before timeout")
        time.sleep(POLL_INTERVAL)


def _collect_flow_status(client):
    processors = status_adapter.fetch_processors(client)["items"]
    controllers = status_adapter.fetch_controllers(client)["items"]
    proc_roll = rollup_processors(processors)
    ctrl_roll = rollup_controllers(controllers)
    status, details = rollup_flow(proc_roll, ctrl_roll)
    return status, proc_roll, ctrl_roll, details


def run_flow(*, config: AppConfig, flowfile: Path) -> CommandResult:
    if config.dry_run:
        with open_client(config) as client:
            _log(config, "[flow] generating dry-run deployment plan")
            result = deploy_adapter.deploy_flow(client, flowfile, dry_run=True)
        return CommandResult(message="Dry-run deployment plan", data=result["summary"])

    with open_client(config) as client:
        try:
            _log(config, "[flow] purging NiFi root before deployment")
            purge_adapter.graceful_purge(client)
            _log(config, "[flow] deploying flow specification")
            deploy_result = deploy_adapter.deploy_flow(client, flowfile, dry_run=False)
            _log(config, "[flow] waiting for deployed components to stabilize")
            _await_stable_states(config, client)
            _log(config, "[flow] enabling controller services")
            ctrl_adapter.enable_all_controllers(client, timeout=config.timeout_seconds)
            _log(config, "[flow] starting processors")
            ctrl_adapter.start_all_processors(client, timeout=config.timeout_seconds)
            _await_stable_states(config, client)
            status_token, proc_roll, ctrl_roll, details = _collect_flow_status(client)
        except ValidationError as exc:
            details = exc.details or diag_adapter.gather_validation_details(client)
            return CommandResult(
                exit_code=ExitCode.VALIDATION,
                message=str(exc),
                data={"process_group_id": deploy_result.get("process_group_id")},
                details=details,
            )

    if status_token in {"INVALID", "TRANSITION"}:
        return CommandResult(
            exit_code=ExitCode.VALIDATION,
            status_token=status_token,
            data={
                "processors": proc_roll.counts,
                "controllers": ctrl_roll.counts,
                "process_group_id": deploy_result.get("process_group_id"),
            },
            details=details,
        )
    return CommandResult(
        status_token=status_token,
        data={
            "processors": proc_roll.counts,
            "controllers": ctrl_roll.counts,
            "process_group_id": deploy_result.get("process_group_id"),
        },
        details=details,
    )


def deploy_flow(*, config: AppConfig, flowfile: Path) -> CommandResult:
    with open_client(config) as client:
        if config.dry_run:
            _log(config, "[flow] generating dry-run deployment plan")
            result = deploy_adapter.deploy_flow(client, flowfile, dry_run=True)
            return CommandResult(message="Dry-run deployment plan", data=result["summary"])
        _log(config, "[flow] purging NiFi root before deployment")
        purge_adapter.graceful_purge(client)
        _log(config, "[flow] deploying flow specification")
        result = deploy_adapter.deploy_flow(client, flowfile, dry_run=False)
        status_token, proc_roll, ctrl_roll, details = _collect_flow_status(client)
    exit_code = ExitCode.VALIDATION if status_token == "INVALID" else ExitCode.SUCCESS
    return CommandResult(
        exit_code=exit_code,
        message="Flow deployed" if exit_code == ExitCode.SUCCESS else "Flow deployment has invalid components",
        data={
            "process_group_id": result.get("process_group_id"),
            "controller_services": result.get("controller_services"),
            "status": status_token,
            "processors": proc_roll.counts,
            "controllers": ctrl_roll.counts,
        },
        details=details if exit_code != ExitCode.SUCCESS else {},
    )


def up_flow(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        try:
            _log(config, "[flow] enabling controller services")
            ctrl_adapter.enable_all_controllers(client, timeout=config.timeout_seconds)
            _log(config, "[flow] starting processors")
            ctrl_adapter.start_all_processors(client, timeout=config.timeout_seconds)
            _await_stable_states(config, client)
            status_token, proc_roll, ctrl_roll, details = _collect_flow_status(client)
        except ValidationError as exc:
            details = exc.details or diag_adapter.gather_validation_details(client)
            return CommandResult(
                exit_code=ExitCode.VALIDATION,
                message=str(exc),
                details=details,
            )
    exit_code = ExitCode.VALIDATION if status_token in {"INVALID", "TRANSITION"} else ExitCode.SUCCESS
    return CommandResult(
        exit_code=exit_code,
        status_token=status_token,
        data={"processors": proc_roll.counts, "controllers": ctrl_roll.counts},
        details=details,
    )


def down_flow(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        _log(config, "[flow] stopping processors")
        ctrl_adapter.stop_all_processors(client, timeout=config.timeout_seconds)
        _log(config, "[flow] disabling controller services")
        ctrl_adapter.disable_all_controllers(client, timeout=config.timeout_seconds)
        status_token, proc_roll, ctrl_roll, details = _collect_flow_status(client)
    exit_code = ExitCode.VALIDATION if status_token == "INVALID" else ExitCode.SUCCESS
    return CommandResult(
        exit_code=exit_code,
        status_token=status_token,
        data={"processors": proc_roll.counts, "controllers": ctrl_roll.counts},
        details=details if exit_code != ExitCode.SUCCESS else {},
    )


def purge_flow(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        _log(config, "[flow] purging NiFi root")
        summary = purge_adapter.graceful_purge(client)
    return CommandResult(message="Purged NiFi root", data=summary)


def status_flow(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        status_token, proc_roll, ctrl_roll, details = _collect_flow_status(client)
        # Attach connection rollup
        connections = status_adapter.fetch_connections(client)["items"]
        conn_roll = rollup_connections(connections)
        details["connections"] = {"counts": conn_roll.counts, "worst": conn_roll.worst}
        # Optionally fail on bulletins or queue thresholds
        bulletins_present = any((item.get("bulletins") for item in status_adapter.fetch_processors(client)["items"]))
        threshold_exceeded = False
        if config.queue_count_threshold is not None:
            threshold_exceeded = any(int(c.get("queuedCount", 0)) >= int(config.queue_count_threshold) for c in connections)
        # queue_bytes_threshold reserved for future; not all endpoints expose exact bytes consistently
    exit_code = ExitCode.VALIDATION if status_token == "INVALID" else ExitCode.SUCCESS
    # Elevate exit code based on diagnostics flags
    if exit_code == ExitCode.SUCCESS:
        if (config.fail_on_bulletins and bulletins_present) or threshold_exceeded:
            exit_code = ExitCode.VALIDATION
    return CommandResult(
        exit_code=exit_code,
        status_token=status_token,
        data={
            "processors": proc_roll.counts,
            "controllers": ctrl_roll.counts,
            "connections": details.get("connections", {}),
        },
        details=details if exit_code != ExitCode.SUCCESS else {},
    )


def inspect_flow(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        diagnostics = diag_adapter.gather_validation_details(client)
        # Evaluate optional fail-on conditions
        bulletins_total = len(diagnostics.get("bulletins", {}).get("processors", [])) + len(
            diagnostics.get("bulletins", {}).get("process_groups", [])
        )
        # queue threshold
        connections = diagnostics.get("connections", {}).get("blocked_or_nonempty", [])
        threshold_exceeded = False
        if config.queue_count_threshold is not None:
            threshold_exceeded = any(int(c.get("queuedCount", 0)) >= int(config.queue_count_threshold) for c in connections)

    total_issues = len(diagnostics.get("invalid_processors", [])) + len(diagnostics.get("invalid_ports", []))
    message = "No invalid components" if total_issues == 0 else f"Found {total_issues} invalid components"
    exit_code = ExitCode.SUCCESS
    if (config.fail_on_bulletins and bulletins_total > 0) or threshold_exceeded:
        exit_code = ExitCode.VALIDATION
    return CommandResult(exit_code=exit_code, message=message, data=diagnostics)
