"""Shared data structures for the CLI application layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Mapping, MutableMapping, Optional


class ExitCode(IntEnum):
    """Process exit codes for CLI commands."""

    SUCCESS = 0
    VALIDATION = 2
    HTTP_ERROR = 3
    TIMEOUT = 4
    BAD_INPUT = 5


@dataclass(slots=True)
class CommandResult:
    """Structured result returned by application services."""

    exit_code: ExitCode = ExitCode.SUCCESS
    message: Optional[str] = None
    data: Optional[Any] = None
    status_token: Optional[str] = None
    details: MutableMapping[str, Any] = field(default_factory=dict)

    def as_json_payload(self) -> Mapping[str, Any]:
        """Create a JSON-serializable mapping for emission in JSON mode."""

        payload: MutableMapping[str, Any] = {}
        if self.status_token is not None:
            payload["status"] = self.status_token
        if self.message is not None:
            payload["message"] = self.message
        if self.data is not None:
            payload["data"] = self.data
        if self.details:
            payload["details"] = self.details
        payload["exit_code"] = int(self.exit_code)
        return payload


@dataclass(slots=True)
class AppConfig:
    """Runtime configuration propagated from the CLI to app services."""

    base_url: Optional[str]
    username: Optional[str]
    password: Optional[str]
    token: Optional[str]
    timeout_seconds: float
    output: str
    verbose: bool
    dry_run: bool = False
    # Optional: processor type hint for describe commands
    proc_type: Optional[str] = None
    # Trust ops parameters
    ts_name: Optional[str] = None
    ts_pass: Optional[str] = None
    ts_type: Optional[str] = None
    trust_url: Optional[str] = None
    ts_alias: Optional[str] = None
    ts_file: Optional[str] = None
