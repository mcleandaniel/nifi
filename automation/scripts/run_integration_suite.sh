#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ "$#" -gt 0 ]; then
  specs=$(printf "%s," "$@")
  specs=${specs%,}
else
  specs="automation/flows/NiFi_Flow.yaml"
fi

export NIFI_FLOW_SPECS="$specs"

./.venv/bin/python scripts/purge_nifi_root.py
RUN_NIFI_INTEGRATION=1 .venv/bin/pytest tests/integration/test_live_nifi.py
