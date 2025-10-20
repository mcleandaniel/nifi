"""Output rendering and exit code mapping for the refactored CLI."""

from __future__ import annotations

import json
import sys
from typing import Any

from ..app.models import CommandResult, ExitCode

__all__ = ["emit_result", "emit_error"]


def _print_json(payload: Any) -> None:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def emit_result(result: CommandResult, *, output: str) -> int:
    """Emit *result* in the requested *output* format and return the exit code."""

    mode = output.lower()
    if mode not in {"text", "json"}:
        raise ValueError(f"Unsupported output mode: {output}")

    if mode == "json":
        _print_json(result.as_json_payload())
    else:
        if result.status_token is not None:
            sys.stdout.write(f"{result.status_token}\n")
        elif result.message is not None:
            sys.stdout.write(f"{result.message}\n")
        elif result.data is not None:
            _print_json(result.data)
        if result.details and result.exit_code != ExitCode.SUCCESS:
            _print_json(result.details)
    return int(result.exit_code)


def emit_error(message: str, *, exit_code: ExitCode) -> int:
    """Render an error message to stderr and return the chosen exit code."""

    sys.stderr.write(f"{message}\n")
    return int(exit_code)
