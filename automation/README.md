# NiFi REST Automation (Phase 1)

This package bootstraps a Python 3.13 command-line interface for interacting with the Apache NiFi REST API. Phase 1 focuses on authentication and basic flow inspection while establishing project scaffolding for future automation.

## Features
- Authentication via `/access/token` using username/password credentials (Bearer token).
- Configurable HTTP client built on `httpx` with TLS toggle.
- Typer-based CLI with subcommands for fetching tokens and viewing the root process group summary.
- Settings managed with `pydantic-settings`, including environment variable overrides (`NIFI_BASE_URL`, `NIFI_USERNAME`, `NIFI_PASSWORD`, etc.).

## Requirements
- Python 3.13
- [`uv`](https://github.com/astral-sh/uv) for dependency management (recommended)

## Quickstart
> The CLI reads NiFi connection defaults (base URL, username, password) from the repo-root `.env`. Update that file or export environment variables before running the commands below if you need different credentials.
1. **Create and activate the per-project virtual environment**  
   Always work from inside `automation/` so installs and commands target the same location:
   ```bash
   cd automation
   uv venv --clear        # creates/refreshes automation/.venv
   source .venv/bin/activate
   ```

2. **Install the package (editable) with dev tooling**  
   ```bash
   uv pip install -e .[dev]
   ```

3. **Configure NiFi connection (via repo-root `.env` or env vars)**  
   ```bash
   export NIFI_BASE_URL="https://localhost:8443/nifi-api"
   export NIFI_USERNAME="admin"
   export NIFI_PASSWORD="changeme"
   ```

4. **Run the CLI** (TLS verification disabled by default; add `--verify-ssl` to enable):
  ```bash
  nifi-automation auth-token
  nifi-automation flow-summary
  nifi-automation deploy-flow automation/flows/NiFi_Flow.yaml
  nifi-automation controller-services-report --format markdown
  nifi-automation controller-services-report -f json --log-level DEBUG  # includes required properties exactly as NiFi marks them
  ```

5. **Run unit tests**  
  ```bash
  pytest
  ```
  *(Integration coverage runs separately via the suite described below.)*

6. **Run integration suite** *(optional)*  
  ```bash
  scripts/run_integration_suite.sh
  ```
  This script purges NiFi once, deploys `automation/flows/NiFi_Flow.yaml`, verifies the resulting process groups and controller
  services, and fails immediately if NiFi reports any invalid processors. Leave NiFi untouched after the run so the
  final deployed state is available for inspection.
   > Codex sandbox note: if you execute this from a sandboxed session, enable network access first  
   > (`codex --sandbox workspace-write -c sandbox_workspace_write.network_access=true`). Otherwise the initial
   > `/access/token` call fails with `[Errno 1] Operation not permitted`, and the purge step never starts.

## Local NiFi for Integration Tests
To run the live integration suite (`RUN_NIFI_INTEGRATION=1`), keep a NiFi 2.0 instance running locally with the expected credentials:

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
- Always run installs and commands from inside `automation/` so they target `automation/.venv`.
- If Codex (or another tool) runs from the repo root, change into `automation/` before invoking `uv` or `pytest`:
  ```bash
  cd automation
  uv pip install -e .[dev]
  uv run -m pytest
  ```
- Avoid mixing the repo-root `.venv` with `automation/.venv`; choose one and stick with it. The project defaults to `automation/.venv`.
- When switching between shells/sessions, check `pwd` first. If you need to run commands from the repo root, prefix them with `cd automation && ...` to keep installs and test runs aligned.
- If repeated changes keep failing (looping), fall back to the focused workflow: **purge NiFi immediately**, run the standalone controller-service provisioning test, and use the scripted curl commands to inspect the state before attempting broader flow deployments again.
- When automation encounters an `ENABLING`/`INVALID` controller service (or any state that needs human judgement), stop further mutations and output the minimal curl commands an operator can run locally. Avoid burning time on repeated retries that the operator can resolve faster with direct inspection.

CLI options still override configuration at runtime. Settings are also loaded from
an `.env` file located at the repository root—useful when running commands from
other directories:
```bash
nifi-automation auth-token \
  --base-url https://localhost:8443/nifi-api \
  --username admin \
  --password changeme
```

## Clean Deploy Workflow

When bootstrapping a NiFi instance (e.g., before deploying `flows/simple.yaml`), follow this sequence:

1. **Purge** – clear the root process group and controller services before every deploy:
   ```bash
   cd automation
   set -a; source ../.env; set +a
   .venv/bin/python scripts/purge_nifi_root.py
   ```
2. **Deploy** – call `nifi-automation deploy-flow automation/flows/NiFi_Flow.yaml` *or* run the convenience script:
   ```bash
   .venv/bin/python scripts/deploy_flows.py
   ```
   The command/script ensures controller services exist (fail-fast if anything already exists) and
   creates all process groups/processors/connections defined in the spec.
3. **Verify** – optional `controller-services-report` or REST `curl` if you want to spot-check states/properties.

If the deploy fails because services already exist, purge again—`ensure_root_controller_services` intentionally refuses to reconcile on a dirty instance.

## Diagnostics
- `scripts/fetch_invalid_processors.py` – lists processors that NiFi currently marks as invalid, including
  the validation errors reported by NiFi. Pass `--json` for machine-readable output. The integration suite invokes
  the same checks and will fail if any processor remains invalid after deployment.

## Flow Specifications
- Declarative specs live under `flows/`. Examples:
  - `automation/flows/NiFi_Flow.yaml`: deploys `TrivialFlow`, `SimpleWorkflow`, `MediumWorkflow`, `ComplexWorkflow`, and
    `NestedWorkflow` (which itself contains a `SubFunction` process group) beneath the `NiFi Flow` root.
  - `flows/trivial.yaml`, `flows/simple.yaml`, `flows/medium.yaml`, `flows/complex.yaml`, `flows/nested.yaml`, `flows/nested_ports.yaml`:
    single-flow specs that target the same root and create only the named child group.
- `nifi-automation deploy-flow automation/flows/NiFi_Flow.yaml` recreates the entire hierarchy each time.

To run the integration suite against alternative specs (e.g., only `medium.yaml`), use:

```bash
cd automation
scripts/run_integration_suite.sh flows/medium.yaml
```

For multiple flows:

```bash
cd automation
scripts/run_integration_suite.sh flows/medium.yaml flows/complex.yaml
```

Multiple specs can be supplied (comma-separated or space-separated); the script sets `NIFI_FLOW_SPECS` for the tests.

## Next Steps
- Add specs for the Simple/Medium/Complex workflows in `flows/` and deploy them
  via the same command.
- Snapshot deployed process groups to NiFi Registry for lifecycle management.
- Add structured logging and integration tests targeting a disposable NiFi instance.
