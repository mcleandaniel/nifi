#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from nifi_automation.app.client import open_client
from nifi_automation.app.models import AppConfig
from nifi_automation.infra.diag_adapter import validate_deployed_topology


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate deployed NiFi topology against a flow spec")
    ap.add_argument("spec", nargs="?", default="automation/flows/NiFi_Flow.yaml", help="Path to flow YAML")
    args = ap.parse_args()

    cfg = AppConfig(
        base_url=None, username=None, password=None, token=None,
        timeout_seconds=30.0, output="json", verbose=False, dry_run=False,
    )
    spec_path = Path(args.spec).resolve()
    with open_client(cfg) as client:
        result = validate_deployed_topology(client, spec_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

