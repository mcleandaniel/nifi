"""CLI package exports.

Expose ``app`` and ``main`` so the console script
entry point ``nifi_automation.cli:app`` resolves correctly.
"""

from __future__ import annotations

from .main import app, main  # re-export for console entry point

__all__ = ["app", "main"]
