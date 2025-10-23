#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

export PYTHONPATH="$REPO_ROOT/automation/src${PYTHONPATH:+:$PYTHONPATH}"

# Optional: purge first to ensure a clean NiFi canvas for tools tests
python -m nifi_automation.cli.main purge flow --output json || true

pytest -m tools -q

