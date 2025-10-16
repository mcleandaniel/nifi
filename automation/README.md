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
   nifi-automation deploy-flow flows/trivial.yaml
  nifi-automation controller-services-report --format markdown
  nifi-automation controller-services-report -f json --log-level DEBUG
   ```

5. **Run tests**  
   ```bash
   pytest
   ```

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
- Always run installs and commands from inside `automation/` so they target `automation/.venv`.
- If Codex (or another tool) runs from the repo root, change into `automation/` before invoking `uv` or `pytest`:
  ```bash
  cd automation
  uv pip install -e .[dev]
  uv run -m pytest
  ```
- Avoid mixing the repo-root `.venv` with `automation/.venv`; choose one and stick with it. The project defaults to `automation/.venv`.
- When switching between shells/sessions, check `pwd` first. If you need to run commands from the repo root, prefix them with `cd automation && ...` to keep installs and test runs aligned.

CLI options still override configuration at runtime. Settings are also loaded from
an `.env` file located at the repository root—useful when running commands from
other directories:
```bash
nifi-automation auth-token \
  --base-url https://localhost:8443/nifi-api \
  --username admin \
  --password changeme
```

## Flow Specifications
- Declarative specs live under `flows/`. Start with `flows/trivial.yaml`, which
  provisions a `GenerateFlowFile` -> `LogAttribute` pipeline inside a new
  process group named `TrivialFlow` beneath the NiFi root.
- `nifi-automation deploy-flow flows/trivial.yaml` recreates the flow each time.

## Next Steps
- Add specs for the Simple/Medium/Complex workflows in `flows/` and deploy them
  via the same command.
- Snapshot deployed process groups to NiFi Registry for lifecycle management.
- Add structured logging and integration tests targeting a disposable NiFi instance.
