#!/usr/bin/env python3
"""List NiFi processors that are currently invalid, including validation errors."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable

from nifi_automation.auth import obtain_access_token
from nifi_automation.client import NiFiClient
from nifi_automation.config import build_settings
from nifi_automation.diagnostics import collect_invalid_processors, collect_invalid_ports


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch NiFi processors that are currently invalid.")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args(list(argv) if argv is not None else None)

    settings = build_settings(None, None, None, False, 10.0)
    token = obtain_access_token(settings)

    with NiFiClient(settings, token) as client:
        invalid_processors = collect_invalid_processors(client)
        invalid_ports = collect_invalid_ports(client)

    result = {
        "processors": invalid_processors,
        "ports": invalid_ports,
    }

    if args.json:
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        if not invalid_processors and not invalid_ports:
            print("No invalid processors or ports detected.")
        if invalid_processors:
            print("Invalid processors:")
            for entry in invalid_processors:
                print(f"- {entry['name']} ({entry['id']})")
                print(f"    Type : {entry['type']}")
                print(f"    Path : {entry['path']}")
                print(f"    Status: {entry['validationStatus']}")
                for err in entry.get("validationErrors") or []:
                    print(f"      Validation Error: {err}")
                for bulletin in entry.get("bulletins") or []:
                    msg = bulletin.get("bulletin", {}).get("message")
                    if msg:
                        print(f"      Bulletin: {msg}")
        if invalid_ports:
            print("Invalid ports:")
            for entry in invalid_ports:
                print(f"- {entry['name']} ({entry['id']})")
                print(f"    Type : {entry['type']}")
                print(f"    Path : {entry['path']}")
                print(f"    Status: {entry['validationStatus']}")
                for err in entry.get("validationErrors") or []:
                    print(f"      Validation Error: {err}")
                for bulletin in entry.get("bulletins") or []:
                    msg = bulletin.get("bulletin", {}).get("message")
                    if msg:
                        print(f"      Bulletin: {msg}")

    return 0 if not invalid_processors and not invalid_ports else 1


if __name__ == "__main__":
    sys.exit(main())
