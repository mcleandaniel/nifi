"""Layout validation service for CLI.

Runs the layout checker and returns a report; fails when overlaps are present.
"""

from __future__ import annotations

from ..infra.layout_checker import check_layout
from .client import open_client
from .models import AppConfig, CommandResult, ExitCode


def validate(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        report = check_layout(client)

    overlaps = report.get("overlaps", []) or []
    lr = report.get("left_to_right_violations", []) or []
    exit_code = ExitCode.VALIDATION if overlaps else ExitCode.SUCCESS
    msg = (
        f"Layout OK (lr_violations={len(lr)})" if not overlaps else f"Layout overlaps detected: {len(overlaps)}"
    )
    return CommandResult(exit_code=exit_code, message=msg, data=report)

