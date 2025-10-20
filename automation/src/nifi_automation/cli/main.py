"""Click-based entry point for the refactored NiFi automation CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

import click

from ..app import conn_service, ctrl_service, flow_service, proc_service
from ..app.errors import AppError, BadInputError, HTTPError, TimeoutError, ValidationError
from ..app.models import AppConfig, CommandResult, ExitCode
from .io import emit_error, emit_result
from .targets import Target, normalize_target, VALID_TARGETS

__all__ = ["app", "main"]


Handler = Callable[..., CommandResult]
DispatchKey = Tuple[str, str]

DISPATCH_TABLE: Dict[DispatchKey, Handler] = {
    ("run", "flow"): flow_service.run_flow,
    ("deploy", "flow"): flow_service.deploy_flow,
    ("up", "flow"): flow_service.up_flow,
    ("down", "flow"): flow_service.down_flow,
    ("purge", "flow"): flow_service.purge_flow,
    ("status", "flow"): flow_service.status_flow,
    ("inspect", "flow"): flow_service.inspect_flow,
    ("start", "processors"): proc_service.start_all,
    ("stop", "processors"): proc_service.stop_all,
    ("status", "processors"): proc_service.status,
    ("inspect", "processors"): proc_service.inspect,
    ("enable", "controllers"): ctrl_service.enable_all,
    ("disable", "controllers"): ctrl_service.disable_all,
    ("status", "controllers"): ctrl_service.status,
    ("inspect", "controllers"): ctrl_service.inspect,
    ("truncate", "connections"): conn_service.truncate_all,
    ("status", "connections"): conn_service.status,
    ("inspect", "connections"): conn_service.inspect,
}

FLOWFILE_COMMANDS = {("run", "flow"), ("deploy", "flow")}
TRUNCATE_COMMAND = ("truncate", "connections")


def _build_config(
    *,
    base_url: Optional[str],
    username: Optional[str],
    password: Optional[str],
    token: Optional[str],
    timeout_seconds: float,
    output: str,
    verbose: bool,
    dry_run: bool,
) -> AppConfig:
    return AppConfig(
        base_url=base_url,
        username=username,
        password=password,
        token=token,
        timeout_seconds=timeout_seconds,
        output=output,
        verbose=verbose,
        dry_run=dry_run,
    )


def _dispatch(
    key: DispatchKey,
    handler: Handler,
    *,
    config: AppConfig,
    flowfile: Optional[Path],
    force: bool,
    max_messages: Optional[int],
) -> CommandResult:
    if key in FLOWFILE_COMMANDS:
        if flowfile is None:  # pragma: no cover - defensive
            raise BadInputError("FLOWFILE argument missing")
        return handler(config=config, flowfile=flowfile)
    if key == TRUNCATE_COMMAND:
        return handler(config=config, force=force, max_messages=max_messages)
    return handler(config=config)


def _exit_code_for_error(error: AppError) -> ExitCode:
    if isinstance(error, ValidationError):
        return ExitCode.VALIDATION
    if isinstance(error, HTTPError):
        return ExitCode.HTTP_ERROR
    if isinstance(error, TimeoutError):
        return ExitCode.TIMEOUT
    if isinstance(error, BadInputError):
        return ExitCode.BAD_INPUT
    return ExitCode.BAD_INPUT


def _report_and_exit(message: str, exit_code: ExitCode) -> None:
    emit_error(message, exit_code=exit_code)
    raise click.exceptions.Exit(code=int(exit_code))


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("verb")
@click.argument("target_alias")
@click.argument("operand", required=False)
@click.option("--base-url", default=None, help="NiFi base URL.")
@click.option("--username", default=None, help="NiFi username.")
@click.option("--password", default=None, help="NiFi password.")
@click.option("--token", default=None, help="NiFi access token.")
@click.option("--timeout-seconds", default=30.0, show_default=True, help="Operation timeout in seconds.")
@click.option(
    "--output",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
@click.option("--dry-run", is_flag=True, help="Plan without mutating NiFi.")
@click.option("--force", is_flag=True, help="Force queue truncation when truncating connections.")
@click.option("--max", "max_messages", type=int, default=None, help="Max FlowFiles to drop when truncating.")
def cli_command(
    verb: str,
    target_alias: str,
    operand: Optional[str],
    base_url: Optional[str],
    username: Optional[str],
    password: Optional[str],
    token: Optional[str],
    timeout_seconds: float,
    output: str,
    verbose: bool,
    dry_run: bool,
    force: bool,
    max_messages: Optional[int],
) -> None:
    """Primary CLI entry point implementing the verb/target grammar."""

    verb_normalized = verb.strip().lower()
    try:
        target: Target = normalize_target(target_alias)
    except ValueError as exc:
        valid = ", ".join(VALID_TARGETS)
        raise click.BadParameter(f"{exc}. Valid targets: {valid}") from exc

    key = (verb_normalized, target.name)
    handler = DISPATCH_TABLE.get(key)
    if handler is None:
        raise click.BadParameter(f"Unsupported verb/target combination: '{verb} {target_alias}'")

    if key in FLOWFILE_COMMANDS:
        if operand is None:
            raise click.BadParameter("FLOWFILE argument is required for this command.")
        flowfile = Path(operand).expanduser().resolve()
    else:
        flowfile = None
        if dry_run:
            raise click.BadParameter("--dry-run is only supported for 'run flow' and 'deploy flow'.")
        if operand is not None:
            raise click.BadParameter("Unexpected positional argument provided.")

    if key != TRUNCATE_COMMAND and (force or max_messages is not None):
        raise click.BadParameter("--force/--max may only be used with 'truncate connections'.")

    config = _build_config(
        base_url=base_url,
        username=username,
        password=password,
        token=token,
        timeout_seconds=timeout_seconds,
        output=output.lower(),
        verbose=verbose,
        dry_run=dry_run if key in FLOWFILE_COMMANDS else False,
    )

    try:
        result = _dispatch(
            key,
            handler,
            config=config,
            flowfile=flowfile,
            force=force,
            max_messages=max_messages,
        )
    except AppError as exc:
        _report_and_exit(str(exc), _exit_code_for_error(exc))
    except FileNotFoundError as exc:
        _report_and_exit(str(exc), ExitCode.BAD_INPUT)
    except Exception as exc:  # pragma: no cover - defensive
        _report_and_exit(f"Unexpected error: {exc}", ExitCode.BAD_INPUT)

    raise click.exceptions.Exit(code=emit_result(result, output=config.output))


app = cli_command


def main() -> None:
    """Entrypoint used by scripts and `python -m` invocation."""

    app()
