#!/usr/bin/env python3
"""Aggregate diagnostics for invalid processors and ports."""

from __future__ import annotations

import json
import sys
from typing import Iterable

from nifi_automation.auth import obtain_access_token
from nifi_automation.client import NiFiClient
from nifi_automation.config import build_settings
from nifi_automation.diagnostics import collect_invalid_ports, collect_invalid_processors


def main(argv: Iterable[str] | None = None) -> int:
    settings = build_settings(None, None, None, False, 10.0)
    token = obtain_access_token(settings)

    with NiFiClient(settings, token) as client:
        invalid_processors = collect_invalid_processors(client)
        invalid_ports = collect_invalid_ports(client)

    result = {
        "processors": invalid_processors,
        "ports": invalid_ports,
    }
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if not invalid_processors and not invalid_ports else 1


if __name__ == "__main__":
    sys.exit(main())
