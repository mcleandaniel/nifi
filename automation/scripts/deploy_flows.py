#!/usr/bin/env python3
"""Deploy one or more flow specification files to NiFi."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List

from nifi_automation.auth import obtain_access_token
from nifi_automation.client import NiFiClient
from nifi_automation.config import build_settings
from nifi_automation.controller_registry import ControllerServiceProvisioningError, ensure_root_controller_services
from nifi_automation.flow_builder import FlowDeploymentError, deploy_flow_from_file

from purge_nifi_root import purge_root


def deploy_flows(flow_paths: Iterable[Path], *, purge_first: bool = True) -> None:
    settings = build_settings(None, None, None, False, 10.0)
    token = obtain_access_token(settings)

    resolved_paths: List[Path] = []
    for path in flow_paths:
        resolved = path if path.is_absolute() else Path.cwd() / path
        if not resolved.exists():
            raise FileNotFoundError(f"Flow spec not found: {resolved}")
        resolved_paths.append(resolved)

    with NiFiClient(settings, token) as client:
        if purge_first:
            purge_root(client)

        service_map = ensure_root_controller_services(client)

        for spec_path in resolved_paths:
            deploy_flow_from_file(client, spec_path, controller_service_map=service_map)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Purge NiFi (optional) and deploy flow specification files.")
    parser.add_argument(
        "flows",
        nargs="*",
        type=Path,
        default=[Path("automation/flows/NiFi_Flow.yaml")],
        help="Flow specification files to deploy in order (default: automation/flows/NiFi_Flow.yaml).",
    )
    parser.add_argument(
        "--no-purge",
        dest="purge",
        action="store_false",
        default=True,
        help="Skip purging NiFi before deployment.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        deploy_flows(args.flows, purge_first=args.purge)
    except (FileNotFoundError, ControllerServiceProvisioningError, FlowDeploymentError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
