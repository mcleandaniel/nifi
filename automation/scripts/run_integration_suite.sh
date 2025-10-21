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
# Finally, run flow-triggered external tests for flows present in the aggregate spec
automation/.venv/bin/python - <<'PY'
import sys, yaml, subprocess, os
spec = yaml.safe_load(open('automation/flows/NiFi_Flow.yaml','r'))
pgs = spec.get('process_group',{}).get('process_groups',[]) or []
names = [g.get('name') for g in pgs if isinstance(g, dict)]
base = 'automation/tests/flows'
folders = [os.path.join(base, n) for n in names if n and os.path.isdir(os.path.join(base,n))]
if folders:
  for f in folders:
    print(f"[flows] running external tests in {f}")
    ret = subprocess.call(['automation/.venv/bin/pytest', f, '-q'])
    if ret != 0:
      sys.exit(ret)
else:
  print('[flows] no external flow tests to run')
PY
