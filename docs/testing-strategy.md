# NiFi Workflow Testing Strategy

## 1. Context and Goals
We build middleware-style applications whose “binary” is a NiFi flow definition. The supporting Python code (CLI, scripts, diagnostics) exists to deploy and validate that flow. Our testing strategy therefore needs to confirm that the NiFi pipeline itself is constructed correctly, that required controller services are healthy, and that automation leaves the instance in a inspectable state when failures occur.

## 2. Current Test Stack
| Layer | Artefacts | Purpose | Status (19 Oct 2025) |
| --- | --- | --- | --- |
| **Unit – automation Python** | `pytest`, `automation/tests/test_*.py` | Validate manifest parsing, controller-service planning, client auth/config, and flow-builder helpers. | Passing locally (`.venv/bin/pytest`). |
| **Integration – default flow** | `automation/scripts/run_integration_suite.sh` (run from repo root; deploys `automation/flows/NiFi_Flow.yaml`) | Purges once, provisions root controller services, deploys all six child flows (Trivial, Simple, Medium, Complex, Nested, NestedPorts) directly under NiFi’s built-in `NiFi Flow` root PG, and asserts processors/ports/services are valid. | Passing locally; purge now drops queues, deletes connections first, and retries port deletion to avoid transient 409s. |
| **Integration – targeted flow** | `automation/scripts/run_integration_suite.sh automation/flows/<spec>.yaml` (run from repo root) | Run the same deployment/assertion pipeline for an individual flow when isolating defects. | On-demand; same purge-first requirement as the default run. |
| **Diagnostics** | `python -m nifi_automation.cli.main inspect flow --output json` | Surfaces invalid processors/ports and their validation errors; exits non-zero if anything is invalid. | Invoked at the end of the integration test; can be run standalone for triage. |
| **Environment preparation** | `python -m nifi_automation.cli.main purge flow` | Drops queued FlowFiles, deletes connections/processors/ports/child PGs, and removes root-level controller services. | Must be executed before any deployment or test batch. Never run it after tests; preserve failing state for analysis. |

## 3. Execution Workflow
1. **Assume NiFi is dirty** – before running `python -m nifi_automation.cli.main purge flow`, schedule the root process group to `STOPPED` (via the UI or CLI) so all processors halt cleanly. Once everything reports `STOPPED`, disable the root-level controller services, then run the purge command. The purge drops queued FlowFiles, deletes connections first, and disables/deletes ports with retries to avoid conflicts.
2. **Provision controller services** – integration tests call `ensure_root_controller_services` as the first step. It aborts if any services already exist, reinforcing the purge-first rule.
3. **Deploy flow specification(s)** – `deploy_flow_from_file` pushes the YAML spec to the live instance. All specs must present a top-level `process_group.name` of `NiFi Flow`; content is materialised directly into the built-in root PG (no duplicate parent group).
4. **Assertions** – the test suite checks for:
   - Presence of every declared child process group, including nested groups.
   - Required processors, input ports, and output ports per spec (names must match).
   - Enabled controller services with canonical property keys (no lingering display-name aliases).
   - Absence of NiFi bulletins, invalid processors, invalid ports, or overlapping processor positions.
   - Manifest persistence of controller-service UUIDs without UI display-name keys.
5. **Diagnostics capture** – on failure, the test stops immediately and leaves NiFi populated so the operator can rerun `python -m nifi_automation.cli.main inspect flow --output json` or manual `curl` reproduction commands. Do **not** purge afterward; the state is evidence.

## 4. External Flow Tests
- Location: `automation/tests/flows/<ProcessGroupName>/test_*.py` (e.g., `HttpServerWorkflow`).
- Behavior: tests fail if the external endpoint/port is not reachable — the trigger is part of the contract.
- Startup: execute a short readiness probe (few retries, max ~10 s) after starting processors to avoid racing the
  listener bind. If still unreachable, the test fails.
- Scope: the runner discovers PG names in `automation/flows/NiFi_Flow.yaml` and only runs external tests for those
  groups. Do not add a PG to the aggregate until its standalone spec and external test pass.

## 5. Known Issues (updated)
- Integration suite depends on the purge succeeding; avoid external mutations during purge (e.g., other tools creating connections) to prevent race conditions. If encountered, rerun purge.

## 6. Gap Analysis
| Gap | Impact | Recommended Action |
| --- | --- | --- |
| No data-level assertions | Structural checks pass even if content is wrong. | Capture representative datasets and assert record counts/schema/metrics post-run. |
| Fault injection absent | Controller-service outages or queue backpressure may go undetected. | Add tests that intentionally disable services or exceed backpressure thresholds to confirm diagnostics. |
| Performance baselines missing | Throughput regressions slip through. | Introduce controlled load scenarios and track latency/records-per-second between runs. |
| Purge script lacks robust connection teardown | Residual queues block port deletion (current 409 error). | Enhance purge to stop upstream processors, remove connections, and retry deletes until successful. |
| Diagnostics limited to invalid components | Provenance anomalies and bulletins outside the root PG are not asserted. | Extend diagnostics module to query provenance events and NiFi bulletin board entries, failing the run when severe bulletins appear. |
| Test selection coarse-grained | Every change triggers the full NiFi_Flow deployment. | Build metadata mapping components to specs so CI can target only affected flows. |

## 7. Roadmap
1. **Short term**
   - Fix port deletion sequencing in the purge command so queued ports can be removed reliably.
   - Store diagnostics artefacts (JSON from the CLI `inspect flow` command) alongside test logs.
   - Add minimal fixture-based data assertions for `SimpleWorkflow` and `ComplexWorkflow`.
2. **Medium term**
   - Introduce fault-injection scenarios and load/performance harnesses.
   - Automate provenance checks to confirm each success/failure relationship sees traffic during tests.
   - Add CLI flag to `run_integration_suite.sh` to skip purge only when a known-clean sandbox is provided.
3. **Long term**
   - Build a regression dataset catalogue for contract testing.
   - Integrate NiFi metrics/bulletins into CI dashboards with automatic gating.

## 7. Usage Cheatsheet

<!-- All commands assume the repository root as CWD. -->

Promotion policy
- New flows must be added to `automation/flows/NiFi_Flow.yaml` once they pass individually (dry-run + live deploy) and layout checks. The aggregate is the source used by the integration suite.
- PRs introducing new flows should include: the single-flow spec, the updated aggregate PG block, and the doc description block.
- Run full suite: `automation/scripts/run_integration_suite.sh`
- Target a specific flow: `automation/scripts/run_integration_suite.sh automation/flows/complex.yaml`
- Standalone diagnostics: `python -m nifi_automation.cli.main inspect flow --output json`
- Purge before any deployment/test: `python -m nifi_automation.cli.main purge flow`
- Virtualenv activation: repo root `source automation/.venv/bin/activate`.
- Run tests: repo root `python -m pytest automation/tests -vv -ra --maxfail=1`.
- Codex tip: when running from a sandboxed Codex session, enable network access first (`codex --sandbox workspace-write -c sandbox_workspace_write.network_access=true`). Without it, even the initial `/access/token` call fails with `[Errno 1] Operation not permitted`, which can masquerade as a purge bug.
- Quick stop-all (before purge):
  ```bash
  curl -sk -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -X PUT "$NIFI_BASE_URL/flow/process-groups/root" \
    -d '{"id":"root","state":"STOPPED"}'
  ```
