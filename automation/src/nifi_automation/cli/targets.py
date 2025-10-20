"""Target alias normalization utilities for the refactored CLI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

__all__ = ["Target", "normalize_target", "VALID_TARGETS"]


@dataclass(frozen=True)
class Target:
    """Nominal type representing a canonical command target."""

    name: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


CANONICAL_TARGETS = {
    "flow": {"flow", "flows"},
    "processors": {"processor", "processors", "proc", "procs"},
    "controllers": {"controller", "controllers", "cont"},
    "connections": {"connection", "connections", "queue", "queues", "conn"},
}

ALIAS_TO_CANONICAL: Dict[str, str] = {
    alias: canonical for canonical, aliases in CANONICAL_TARGETS.items() for alias in aliases
}

VALID_TARGETS = tuple(sorted(CANONICAL_TARGETS.keys()))


def normalize_target(alias: str) -> Target:
    """Return the canonical target corresponding to *alias*.

    Raises:
        ValueError: if the alias does not map to a known target.
    """

    key = alias.strip().lower()
    try:
        canonical = ALIAS_TO_CANONICAL[key]
    except KeyError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Unrecognized target alias: {alias}") from exc
    return Target(canonical)
