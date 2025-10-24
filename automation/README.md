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
   - If you are already in a virtual environment (`$VIRTUAL_ENV` is set), keep using it and skip creation.
   - Otherwise, create/activate the project venv:
   ```bash
   if [ -z "${VIRTUAL_ENV:-}" ]; then
     uv venv automation/.venv --clear   # creates/refreshes automation/.venv
     source automation/.venv/bin/activate
   else
     echo "Using active venv: $VIRTUAL_ENV"
   fi
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
  - When running inside the NiFi Docker container and making REST calls back to the same container, you can prefer an internal base URL:
    - `NIFI_INTERNAL_BASE_URL="https://$(hostname):8443/nifi-api"`
    - `NIFI_PREFER_INTERNAL=true`
    The CLI resolves `$(hostname)` at runtime to the container hostname and uses the internal URL when `NIFI_PREFER_INTERNAL=true`.

4. **Run the CLI (from repo root)** (TLS verification disabled by default; add `--verify-ssl` to enable):
  ```bash
  nifi-automation auth-token
  nifi-automation flow-summary
  # Deploy the grouped aggregate (canonical):
  python -m nifi_automation.cli.main run flow automation/flows/groups-md/NiFi_Flow_groups.yaml --output json
  # Confirm final state:
  python -m nifi_automation.cli.main status flow --output json
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
  This script purges NiFi once (via the CLI), deploys `automation/flows/groups-md/NiFi_Flow_groups.yaml` (the grouped aggregate),
  verifies the resulting process groups and controller services, and fails immediately if NiFi reports any invalid
  processors. It ends by starting processors so the final deployed state is RUNNING for operator inspection and then
  prints a consolidated `status flow` summary.
  The suite does not purge after tests to allow manual inspection of the deployed state.
   > Codex sandbox note: if you execute this from a sandboxed session, enable network access first  
   > (`codex --sandbox workspace-write -c sandbox_workspace_write.network_access=true`). Otherwise the initial
   > `/access/token` call fails with `[Errno 1] Operation not permitted`, and the purge step never starts.

## Local NiFi for Integration Tests
To run the live integration suite, keep a NiFi 2.0 instance running locally with the expected credentials. The tests automatically attempt to authenticate and will skip gracefully if NiFi is unreachable.

```bash
docker run -d --name nifi \
  -p 18070-18180:18070-18180 \
  -p 8443:8443 \
  -e NIFI_WEB_HTTPS_HOST=0.0.0.0 \
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

### Docker helpers
- See `docker/README.md` for scripts to:
  - bind Jetty to `0.0.0.0` in a running container without rebuilding (`docker/bin/nifi-bind-all.sh`)
  - verify HTTPS reachability from inside the container (`docker/bin/nifi-verify.sh`)
  - manage a local `nifi.properties` overlay under `docker/overrides/` for persistent runs

Notes on HTTPS bind and SNI (dev):
- Setting `NIFI_WEB_HTTPS_HOST=0.0.0.0` ensures Jetty listens on all interfaces so `https://localhost:8443` works from inside and outside Docker.
- The default NiFi server certificate CN is `localhost`. For internal self-calls from flows, prefer `https://localhost:8443` with a `StandardSSLContextService` that trusts the CN=localhost certificate.
- If you must call `https://$(hostname):8443` from inside the container (e.g., using the container’s hostname), either reissue the server certificate with a SAN that includes that hostname, or set InvokeHTTP’s `Hostname Verifier` property to a relaxed mode (e.g., Allow All) only for these self-calls.

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

## Two‑Phase Validation Flow (Deploy → Start)

- After any change, validate in two phases. You can run them explicitly:
  - Deploy phase (no processors started yet):
    - `nifi-automation deploy flow automation/flows/groups-md/NiFi_Flow_groups.yaml --output json`
      - Fails if topology mismatches or layout overlaps exist.
  - Start phase:
    - `nifi-automation up flow --output json`
      - Requires all processors to be RUNNING; reports connection backpressure.
- Or run them together with a single helper:
  - `nifi-automation run flow automation/flows/groups-md/NiFi_Flow_groups.yaml --output json`
  - This performs deploy validations (topology + layout), starts processors, and enforces that the final status is UP. Follow with `status flow` if you want a summary print.

Important test rule
- Tests must not tolerate partial success. If a processor remains STOPPED, or an endpoint is not reachable/returns unexpected codes, the test must fail. Fix the flow or treat as error; do not skip.
- Tests must deploy at least one processor (zero processors is invalid). Ensure flow specs include processors; assertions should confirm non‑zero counts.

## Clean Deploy Workflow (root-run)

When bootstrapping a NiFi instance (e.g., before deploying `flows/simple.yaml`), follow this sequence:

1. **Purge** – clear the root process group and controller services before every deploy:
   ```bash
   set -a; source .env; set +a
   python -m nifi_automation.cli.main purge flow --output json
   ```
2. **Deploy** – run from repo root using the same venv:
   ```bash
   python -m nifi_automation.cli.main run flow automation/flows/groups-md/NiFi_Flow_groups.yaml --output json
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

### Bulletin triage (runtime-only errors)
Use bulletins to monitor runtime issues (network/TLS/auth/endpoint health) without blocking deploys.

Fetch recent ERROR bulletins and summarize:
```bash
source automation/.venv/bin/activate
set -a; source .env; set +a
python automation/scripts/fetch_bulletins.py --limit 200 --severity ERROR --output json
```

CLI wrapper example:
```bash
python -m nifi_automation.cli.main inspect bulletins --limit 100 --severity ERROR --output json
```

For LLM-assisted analysis, paste the JSON output into `prompts/analyze-bulletins.md` under BULLETINS_JSON and ask for root causes and next steps.

## Flow Specifications
- Grouped aggregate (canonical): `automation/flows/groups-md/NiFi_Flow_groups.yaml`. This is the primary deploy target used by the integration suite and CLI examples.
- Single-flow specs remain available for isolated runs: `automation/flows/trivial.yaml`, `automation/flows/simple.yaml`, `automation/flows/medium.yaml`, `automation/flows/complex.yaml`, `automation/flows/nested.yaml`, `automation/flows/nested_ports.yaml`.
- Deploy aggregate:
  - `python -m nifi_automation.cli.main run flow automation/flows/groups-md/NiFi_Flow_groups.yaml`
  - Or deploy single flows individually when iterating on one workflow at a time.

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

Groups MD build (aggregate from groups-md)
- We use a groups-first build where group metadata and per-workflow YAML fragments live under `automation/flows/groups-md/`.
  The builder assembles `automation/flows/groups-md/NiFi_Flow_groups.yaml` without reading `automation/flows/*.yaml`.
- See `automation/flows/README.md` for details and commands (groups build is the canonical aggregate used by the integration suite).
  - Build grouped YAML:
    - `python automation/scripts/build_groups_yaml_from_md.py --md-dir automation/flows/groups-md --out automation/flows/groups-md/NiFi_Flow_groups.yaml --root-name "NiFi Flow"`
  - One-time seed of per-workflow fragments (during migration):
    - `python automation/scripts/seed_groups_yaml_from_single_flows.py --md-dir automation/flows/groups-md --flows-dir automation/flows --out-md-dir automation/flows/groups-md`

Aggregate promotion rule (must-do)
- After a new flow spec deploys cleanly on its own and passes layout/validation checks, you must add it to the groups build by creating/updating its fragment under `automation/flows/groups-md/<Group>/flows/<Name>.yaml` and rebuilding `automation/flows/groups-md/NiFi_Flow_groups.yaml` in the same PR.
- Do not leave standalone specs orphaned. The grouped aggregate is the canonical end-to-end deploy used by the integration suite and operators.
- Checklist before promotion:
  - Dry-run and live deploy of the single spec succeed.
  - `run_integration_suite.sh` passes with the existing aggregate.
  - Update the aggregate by appending the new PG section; update docs if needed.

External flow tests
- Place external-trigger tests under `automation/tests/flows/<ProcessGroupName>/test_*.py` (e.g., `HttpServerWorkflow`).
- Tests must fail if the endpoint/port is not reachable; the trigger is part of the flow’s contract. A short readiness
  probe (a few retries over ~10 s) is acceptable to avoid racing the listener bind, but failures must be fatal.

## Process Library (MVP)

- Reusable Process Groups live under `automation/process-library/` as standalone YAML files with a top-level `process_group`.
- Compose a harness that references library PGs using `library_includes` and `Alias.port` syntax in connections, then inline at deploy time:
  ```bash
  python automation/scripts/compose_with_library.py \
    --input automation/flows/library/http_library_harness.yaml \
    --out automation/flows/library/http_library_harness_composed.yaml
  python -m nifi_automation.cli.main run flow automation/flows/library/http_library_harness_composed.yaml --output json
  ```
- Starter PGs: `EchoLogger` and `AttributeTagger`. Example harness at `automation/flows/library/http_library_harness.yaml`.
- Next step (roadmap): teach the deployer to process `library_includes` natively so composition doesn’t require a pre-step.
- The integration runner only executes flow tests for PGs present in `automation/flows/groups-md/NiFi_Flow_groups.yaml`. Do not add a new PG to the
  aggregate until its standalone spec and tests are green.
- Prefer parameterizing triggers (ports, paths) via Parameter Context values and referencing them in tests via `.env`.

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
## Diagram Web Server (Experimental)

- Serve generated diagrams and icon assets via a tiny web UI.
- Start the server:
  - `source automation/.venv/bin/activate`
  - `python automation/scripts/diagram_web.py --spec automation/flows/groups-md/NiFi_Flow_groups.yaml --theme dark --port 8091`
- Open `http://127.0.0.1:8091/` for the index of groups.
- Regenerate using another theme: `curl 'http://127.0.0.1:8091/api/render?theme=light'` and refresh the page.
- Browse icons preview: `http://127.0.0.1:8091/assets/processor-icons/preview/index.html`.

## Authoring: Processor Comments (Optional)

- You can add a short `comments:` field to any processor when the intent isn’t obvious from the `name` + `type`.
- Keep it brief (one sentence is ideal); multi‑line blocks (`|`) are fine for nuance.
- Example:
  ```yaml
  processors:
    - id: my-query
      name: QueryRecord (status split)
      type: org.apache.nifi.processors.standard.QueryRecord
      comments: Routes records to OK/OTHER streams based on /status.
      properties:
        record-reader: json-reader
        record-writer: json-writer
  ```
- SSL trust helper (container)
  - To trust self-signed certs for InvokeHTTP (either calling NiFi itself or external services), run the container script:
    ```bash
    # Inside the NiFi container
    /opt/nifi/scripts/nifi_trust_helper.sh local --alias local-nifi
    /opt/nifi/scripts/nifi_trust_helper.sh remote --url https://api.example.com:443 --alias api-example
    ```
    The repo version lives at `automation/scripts/nifi_trust_helper.sh`. Mount or copy it into the container.
    See `docs/ssl-trust-helper.md` for details.

- Trust tools (CLI)
  - The CLI provides `trust` subcommands that deploy HTTP-triggered flows to add/remove/inspect dedicated truststores and auto-provision a root SSL Context Service ("Workflow SSL").
  - Quick start:
    ```bash
    nifi-automation add trust --ts-name workflow --ts-type PKCS12 --ts-password abcd1234 \
      --ts-alias nifi-https --trust-url https://SELF:8443 --output json
    nifi-automation inspect trust --ts-name workflow --ts-type PKCS12 --ts-password abcd1234 --output json
    ```
  - See `docs/trust-store-ops.md` for design and operational details.
- Port ranges (dev convention)
- Tools (CLI-triggered): 18070–18079 (default 18071)
- Workflows (HTTP-triggered tests): 18080–18180 (default 18081 for examples)
- Rationale: avoids collisions between tools and workflow listeners. Trust tools deploy on-demand and remain deployed for inspection; they are not auto-deleted. Use the purge/cleardown command when starting a new batch, not after tests.
