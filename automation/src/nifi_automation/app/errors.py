"""Domain-level exception hierarchy for the CLI application layer."""

from __future__ import annotations


class AppError(Exception):
    """Base class for application-layer failures."""

    def __init__(self, message: str, *, details: object | None = None) -> None:
        super().__init__(message)
        self.details = details


class ValidationError(AppError):
    """Raised when NiFi reports invalid components during orchestration."""


class HTTPError(AppError):
    """Raised when HTTP requests fail unexpectedly."""


class TimeoutError(AppError):
    """Raised when an operation exceeds the configured timeout."""


class BadInputError(AppError):
    """Raised when CLI arguments or configs are invalid."""
