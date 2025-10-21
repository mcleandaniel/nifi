#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

export PYTHONPATH="$ROOT_DIR/automation/src${PYTHONPATH:+:$PYTHONPATH}"

if [ "$#" -gt 0 ]; then
  specs=$(printf "%s," "$@")
  specs=${specs%,}
else
  specs="automation/flows/NiFi_Flow.yaml"
fi

export NIFI_FLOW_SPECS="$specs"

./.venv/bin/python -m nifi_automation.cli.main purge flow --output json
.venv/bin/pytest tests/integration/test_live_nifi.py
