"""Shim module exposing the refactored Typer app."""

from __future__ import annotations

from .cli.main import app, main

__all__ = ["app", "main"]
