"""Polling helpers for the CLI app layer."""

from __future__ import annotations

import time
from typing import Callable


class TimeoutExpired(RuntimeError):
    """Raised when a polling loop exceeds the configured timeout."""


def poll_until(predicate: Callable[[], bool], *, timeout: float, interval: float = 0.5) -> None:
    """Invoke *predicate* until it returns ``True`` or the timeout expires."""

    deadline = time.time() + timeout
    while True:
        if predicate():
            return
        if time.time() > deadline:
            raise TimeoutExpired("Condition not satisfied before timeout")
        time.sleep(interval)
