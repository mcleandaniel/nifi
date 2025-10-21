#!/usr/bin/env bash
set -euo pipefail

# Always run from the repository root so relative paths like
# `automation/flows/NiFi_Flow.yaml` resolve consistently.
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

# Ensure the automation sources are importable when invoking pytest and modules directly
export PYTHONPATH="$REPO_ROOT/automation/src${PYTHONPATH:+:$PYTHONPATH}"

if [ "$#" -gt 0 ]; then
  specs=$(printf "%s," "$@")
  specs=${specs%,}
else
  specs="automation/flows/NiFi_Flow.yaml"
fi

export NIFI_FLOW_SPECS="$specs"

# Use the per-project venv under automation/.venv
automation/.venv/bin/python -m nifi_automation.cli.main purge flow --output json
# First deploy and validate flows
automation/.venv/bin/pytest automation/tests/integration/test_live_nifi.py
# Then run layout checks against the deployed instance
automation/.venv/bin/pytest automation/tests/integration/test_layout_live.py
# Start processors for externally triggered flows
automation/.venv/bin/python -m nifi_automation.cli.main up flow --output json || true
# Finally, run flow-triggered external tests (HTTP now; JMS/File later)
automation/.venv/bin/pytest automation/tests/flows -q
