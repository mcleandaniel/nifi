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
from nifi_automation.diagnostics import collect_invalid_processors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch NiFi processors that are currently invalid.")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args(list(argv) if argv is not None else None)

    settings = build_settings(None, None, None, False, 10.0)
    token = obtain_access_token(settings)

    with NiFiClient(settings, token) as client:
        invalid = collect_invalid_processors(client)

    if args.json:
        json.dump(invalid, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        if not invalid:
            print("No invalid processors detected.")
        else:
            for entry in invalid:
                print(f"Processor: {entry['name']} ({entry['id']})")
                print(f"  Type : {entry['type']}")
                print(f"  Path : {entry['path']}")
                print(f"  Status: {entry['validationStatus']}")
                if entry["validationErrors"]:
                    print("  Validation Errors:")
                    for err in entry["validationErrors"]:
                        print(f"    - {err}")
                if entry["bulletins"]:
                    print("  Bulletins:")
                    for bulletin in entry["bulletins"]:
                        msg = bulletin.get("bulletin", {}).get("message")
                        print(f"    - {msg}")
                print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
