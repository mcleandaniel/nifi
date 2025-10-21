# NiFi REST Automation (Phase 1)

This package bootstraps a Python 3.13 command-line interface for interacting with the Apache NiFi REST API. Phase 1 focuses on authentication and basic flow inspection while establishing project scaffolding for future automation.

## Features
- Authentication via `/access/token` using username/password credentials (Bearer token).
- Configurable HTTP client built on `httpx` with TLS toggle.
- Typer-based CLI: `auth-token`, `flow-summary`, and verb‑target commands (`run`/`status`/`inspect`/`purge`).
- Settings managed with `pydantic-settings`, including environment variable overrides (`NIFI_BASE_URL`, `NIFI_USERNAME`, `NIFI_PASSWORD`, etc.).

## Requirements
- Python 3.13
- [`uv`](https://github.com/astral-sh/uv) for dependency management (recommended)

## Quickstart
> The CLI reads NiFi connection defaults (base URL, username, password) from the repo-root `.env`. Update that file or export environment variables before running the commands below if you need different credentials.

If you are starting a new Codex CLI session, prime the assistant by emitting the core docs first (run from the repo root):

```bash
for f in automation/README.md docs/cli-refactor-plan.md docs/controller-services-design.md docs/controller-services-bug.md; do
  printf '\n==== %s ====\n' "$f"
  cat "$f"
done
```

Then continue with the steps below.
1. **Create and activate the per-project virtual environment (from repo root)**
   ```bash
   uv venv automation/.venv --clear   # creates/refreshes automation/.venv
   source automation/.venv/bin/activate
   ```

2. **Install the package (editable) with dev tooling**
   ```bash
   uv pip install -e automation/.[dev]
   ```

3. **Configure NiFi connection (via repo-root `.env` or env vars)**
   ```bash
   export NIFI_BASE_URL="https://localhost:8443/nifi-api"
   export NIFI_USERNAME="admin"
   export NIFI_PASSWORD="changeme"
   ```

4. **Run the CLI (from repo root)** (TLS verification disabled by default; add `--verify-ssl` to enable):
  ```bash
  nifi-automation auth-token
  nifi-automation flow-summary
  python -m nifi_automation.cli.main run flow automation/flows/NiFi_Flow.yaml --output json
  nifi-automation controller-services-report --format markdown
 nifi-automation controller-services-report -f json --log-level DEBUG  # includes required properties exactly as NiFi marks them
  ```

5. **Run unit tests (from repo root)**
  ```bash
  python -m pytest automation/tests -vv -ra --maxfail=1
  ```
  *(Integration coverage runs separately via the suite described below.)*

6. **Run integration suite** *(optional, from repo root)*
  ```bash
  bash automation/scripts/run_integration_suite.sh
  ```
  This script purges NiFi once (via the CLI), deploys `automation/flows/NiFi_Flow.yaml`, verifies the resulting process groups and controller
  services, and fails immediately if NiFi reports any invalid processors. Leave NiFi untouched after the run so the
  final deployed state is available for inspection.
   > Codex sandbox note: if you execute this from a sandboxed session, enable network access first  
   > (`codex --sandbox workspace-write -c sandbox_workspace_write.network_access=true`). Otherwise the initial
   > `/access/token` call fails with `[Errno 1] Operation not permitted`, and the purge step never starts.

## Local NiFi for Integration Tests
To run the live integration suite, keep a NiFi 2.0 instance running locally with the expected credentials. The tests automatically attempt to authenticate and will skip gracefully if NiFi is unreachable.

```bash
docker run -d --name nifi \
  -p 8443:8443 \
  -e NIFI_WEB_HTTPS_PORT=8443 \
  -e SINGLE_USER_CREDENTIALS_USERNAME=admin \
  -e SINGLE_USER_CREDENTIALS_PASSWORD='changeMe123!' \
  -v ~/nifi/conf:/opt/nifi/nifi-current/conf \
  -v ~/nifi/state:/opt/nifi/nifi-current/state \
  -v ~/nifi/logs:/opt/nifi/nifi-current/logs \
  -v ~/nifi/content:/opt/nifi/nifi-current/content_repository \
  -v ~/nifi/provenance:/opt/nifi/nifi-current/provenance_repository \
  apache/nifi:2.6.0
```

The integration tests assume NiFi is available at `https://localhost:8443/nifi-api` with the single-user credentials shown above.

## Tips for Consistent Environments
- **Always purge first**. Treat every NiFi instance as dirty until proven otherwise.
  Run the purge script or `nifi-automation purge-root` (once available) before provisioning
  controller services or deploying flows. Skipping this step leaves stale controller
  state behind and wastes cycles chasing ENABLING/INVALID loops.
- Run installs and commands from the **repo root**. Activate `automation/.venv` and reference files under `automation/...`.
- Use root-run equivalents for tooling:
  ```bash
  uv pip install -e automation/.[dev]
  python -m pytest automation/tests -vv -ra --maxfail=1
  ```
- Avoid mixing the repo-root `.venv` with `automation/.venv`; choose one and stick with it. The project defaults to `automation/.venv`.
- When switching between shells/sessions, check `pwd` first. Prefer running from repo root so relative paths like `automation/flows/...` resolve consistently.
- If repeated changes keep failing (looping), fall back to the focused workflow: **purge NiFi immediately**, run the standalone controller-service provisioning test, and use the scripted curl commands to inspect the state before attempting broader flow deployments again.
- When automation encounters an `ENABLING`/`INVALID` controller service (or any state that needs human judgement), stop further mutations and output the minimal curl commands an operator can run locally. Avoid burning time on repeated retries that the operator can resolve faster with direct inspection.

### Virtualenv & Codex cheatsheet

Outside Codex (normal shell)
- Activate venv
  - Repo root: `source automation/.venv/bin/activate`
  - Inside `automation/`: `source .venv/bin/activate`
- Run tests
  - Repo root: `python -m pytest automation/tests -vv -ra --maxfail=1`
  - Inside `automation/`: `python -m pytest tests -vv -ra --maxfail=1`
- CLI without venv (fallback): `PYTHONPATH=automation/src python -m nifi_automation.cli.main status flow --output json`

Inside Codex
- Prime context (once per session, from repo root):
  ```bash
  for f in automation/README.md docs/cli-refactor-plan.md docs/controller-services-design.md docs/controller-services-bug.md; do
    printf '\n==== %s ====\n' "$f"; cat "$f"; done
  ```
- Re-activate venv inside Codex: `source automation/.venv/bin/activate`
- Run tests/CLI as above. Avoid creating a venv or installing inside the sandbox unless needed.
- Optional: keep caches in-repo if you do use uv/pip in Codex:
  - `export UV_CACHE_DIR="$PWD/automation/.uv-cache"`
  - `export PIP_CACHE_DIR="$PWD/automation/.pip-cache"`

CLI options still override configuration at runtime. Settings are also loaded from
an `.env` file located at the repository root—useful when running commands from
other directories:
```bash
nifi-automation auth-token \
  --base-url https://localhost:8443/nifi-api \
  --username admin \
  --password changeme
```

## Clean Deploy Workflow (root-run)

When bootstrapping a NiFi instance (e.g., before deploying `flows/simple.yaml`), follow this sequence:

1. **Purge** – clear the root process group and controller services before every deploy:
   ```bash
   set -a; source .env; set +a
   python -m nifi_automation.cli.main purge flow --output json
   ```
2. **Deploy** – run from repo root using the same venv:
   ```bash
   python -m nifi_automation.cli.main run flow automation/flows/NiFi_Flow.yaml --output json
   ```
   The CLI ensures controller services exist (fail-fast if anything already exists), redeploys the flow,
   enables controllers, and starts processors. Use `--dry-run` if you only want the deployment plan.
3. **Verify** – `python -m nifi_automation.cli.main status flow --output json` (or the richer `inspect flow`)
   to confirm processors/controllers are healthy.

If the deploy fails because services already exist, purge again—`ensure_root_controller_services` intentionally refuses to reconcile on a dirty instance.

## Diagnostics
- `python -m nifi_automation.cli.main inspect flow --output json` – structured JSON including:
  - invalid processors and ports (with validation errors)
  - processor and process-group bulletins
  - connection queue snapshots (counts/bytes/percent use)
  The integration suite invokes the same command after deployment.

## Flow Specifications
- Declarative specs live under `flows/`. Examples:
  - `automation/flows/NiFi_Flow.yaml`: deploys `TrivialFlow`, `SimpleWorkflow`, `MediumWorkflow`, `ComplexWorkflow`, and
    `NestedWorkflow` (which itself contains a `SubFunction` process group) beneath the `NiFi Flow` root.
- `automation/flows/trivial.yaml`, `automation/flows/simple.yaml`, `automation/flows/medium.yaml`, `automation/flows/complex.yaml`, `automation/flows/nested.yaml`, `automation/flows/nested_ports.yaml`:
    single-flow specs that target the same root and create only the named child group.
- `python -m nifi_automation.cli.main run flow automation/flows/NiFi_Flow.yaml` recreates the entire hierarchy (purging first) each time.

Descriptions & doc sync
- Each process group in YAML may include a `description` field (alias `comments`). The deployer copies this to the NiFi PG comments.
- Keep `automation/flows/test-workflow-suite.md` in sync with the YAML descriptions. When you edit one, copy the description text verbatim into the other in the same PR to avoid drift.
- Use two subsections in both places: “Overview” (plain English) and “Technical” (processors, relationships, advanced behavior).

Doc as source-of-truth (nifidesc) and sync tool
- Preferred workflow: write/update the description once in `automation/flows/test-workflow-suite.md` using a fenced block:
  
  ```
  ```nifidesc
  name: MyWorkflow
  Overview: …
  Technical: …
  ```
  ```
  
- Then project the description into YAML (single specs and aggregate) with:
  
  ```bash
  python automation/scripts/sync_descriptions.py    # use --dry-run to preview
  ```
  
- The integration tests enforce that YAML descriptions match the doc blocks.

Aggregate promotion rule (must-do)
- After a new flow spec (e.g., `automation/flows/my_flow.yaml`) deploys cleanly on its own and passes layout/validation checks, you must add it to the aggregate `automation/flows/NiFi_Flow.yaml` in the same PR.
- Do not leave standalone specs orphaned. The aggregate is the canonical end-to-end deploy used by the integration suite and operators.
- Checklist before promotion:
  - Dry-run and live deploy of the single spec succeed.
  - `run_integration_suite.sh` passes with the existing aggregate.
  - Update the aggregate by appending the new PG section; update docs if needed.

External flow tests
- Place external-trigger tests under `automation/tests/flows/<ProcessGroupName>/test_*.py` (e.g., `HttpServerWorkflow`).
- Tests must fail if the endpoint/port is not reachable; the trigger is part of the flow’s contract.
- The integration runner executes these after deploying the aggregate and starting processors.

To run the integration suite against alternative specs (e.g., only `medium.yaml`), use:

```bash
bash automation/scripts/run_integration_suite.sh automation/flows/medium.yaml
```

For multiple flows:

```bash
bash automation/scripts/run_integration_suite.sh automation/flows/medium.yaml automation/flows/complex.yaml
```

Multiple specs can be supplied (comma-separated or space-separated); the script sets `NIFI_FLOW_SPECS` for the tests.

## Next Steps
- Add specs for the Simple/Medium/Complex workflows in `flows/` and deploy them
  via the same command.
- Snapshot deployed process groups to NiFi Registry for lifecycle management.
- Add structured logging and integration tests targeting a disposable NiFi instance.
