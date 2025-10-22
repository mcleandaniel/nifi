# CLI Refactor Plan – NiFi Automation Tool

## Overview
This document captures the agreed-upon redesign for the NiFi automation CLI prior to implementation. The refactor replaces the legacy command tree with a verb/target grammar, introduces a thin CLI shim, and pushes orchestration logic into a reusable application layer.

## Command Grammar
```
clitool <verb> <target> [args]
```
- Flowfile positional argument required only for `run flow <flowfile>` and `deploy flow <flowfile>`.
- Supported verbs: `run`, `deploy`, `up`, `down`, `start`, `stop`, `enable`, `disable`, `truncate`, `status`, `inspect`, `purge`.
- Targets (root scope only) with strict aliases:
  | Primary | Aliases |
  | ------- | ------- |
  | `flow` | `flows` |
  | `processors` | `processor`, `procs`, `proc` |
  | `controllers` | `controller`, `cont` |
  | `connections` | `connection`, `queues`, `queue`, `conn` |
- Ambiguous alias `con` is forbidden.

## Behaviour Matrix
| Command | Behaviour |
| ------- | --------- |
| `run flow <file>` | Graceful purge → deploy → wait until processors/controllers acceptable → enable controllers → start processors → final status roll-up. |
| `deploy flow <file>` | Graceful purge → deploy → status summary only. |
| `up flow` | Enable controllers → start processors. |
| `down flow` | Stop processors → disable controllers. |
| `start processors` | Start all processors (auto-enable controllers as needed). |
| `stop processors` | Stop all processors. |
| `enable controllers` | Enable all controller services. |
| `disable controllers` | Disable all controller services. |
| `truncate connections` | Drop/clear all queues (supports `--force`, `--max`). |
| `status <target>` | Return worst severity token (text mode) and counts (JSON). |
| `inspect <target>` | Detailed items including validation/bulletin/backpressure information. |
| `purge flow` | Graceful purge sequence then delete everything under the root PG. |

## Graceful Purge Sequence
1. Stop processors and poll until all are `STOPPED` (honour timeout).
2. Disable controllers and poll until all are `DISABLED`.
3. Truncate all queues.
4. Delete all components under the root process group.

## Architecture Layers
- **CLI (`automation/src/nifi_automation/cli/`)**
  - `main.py`: Typer entry point + dispatcher table.
  - `targets.py`: alias normalization.
  - `io.py`: rendering and exit-code mapping.
  - Zero business logic – no loops or NiFi calls.
- **Application (`automation/src/nifi_automation/app/`)**
  - Services per target: `flow_service`, `proc_service`, `ctrl_service`, `conn_service`.
  - Supporting modules: `status_rules`, `polling`, `errors`.
  - Implements orchestration, status/polling, graceful purge sequence.
- **Infrastructure (`automation/src/nifi_automation/infra/`)**
  - Adapters for existing backend functions (`deploy_adapter`, `purge_adapter`, `status_adapter`, `ctrl_adapter`, `diag_adapter`) and an `nifi_client` wrapper.
  - App layer calls adapters; adapters call existing backend modules (unchanged).

## Status Model (Roll-ups)
- **Processors:** transitional `STARTING`, `STOPPING`; severity `INVALID > STOPPING > STARTING > STOPPED > RUNNING`.
  - Rationale: STOPPED must rank worse than RUNNING so roll-ups surface when any processors are not running. Operators expect the platform to end RUNNING post-deploy/admin unless explicitly left otherwise by a test.
- **Controllers:** acceptable `ENABLED`, `DISABLED`; transitional `ENABLING`, `DISABLING`; severity `INVALID > DISABLING > ENABLING > ENABLED = DISABLED`.
- **Connections:** severity `BLOCKED > HEALTHY > EMPTY`; `EMPTY` = zero queued items, `HEALTHY` = queued items without backpressure.
- **Flow:** `INVALID` if any invalid; `TRANSITION` if any transitional; `UP` if processors RUNNING and controllers ENABLED; `DOWN` if processors STOPPED and controllers DISABLED; otherwise `HEALTHY`.

## Inspect Output Requirements
- Controllers must include NiFi `validationErrors` text.
- Processors must include bulletins/error details.
- Connections must include queued counts and backpressure thresholds.

## Configuration & Exit Codes
- Configuration propagated to app layer: `base_url`, `username`, `password`, `token`, `timeout_seconds` (default 30), `output` (`text` or `json`), `verbose`, `dry_run`.
- Exit codes: `0` success, `2` validation error (used when status/run detect INVALID), `3` HTTP error, `4` timeout, `5` bad input.

## Dispatcher Table
| Verb | Target | App Function |
| ---- | ------ | ------------ |
| run | flow | `app.flow_service.run_flow` |
| deploy | flow | `app.flow_service.deploy_flow` |
| up | flow | `app.flow_service.up_flow` |
| down | flow | `app.flow_service.down_flow` |
| purge | flow | `app.flow_service.purge_flow` |
| status | flow | `app.flow_service.status_flow` |
| inspect | flow | `app.flow_service.inspect_flow` |
| start | processors | `app.proc_service.start_all` |
| stop | processors | `app.proc_service.stop_all` |
| status | processors | `app.proc_service.status` |
| inspect | processors | `app.proc_service.inspect` |
| enable | controllers | `app.ctrl_service.enable_all` |
| disable | controllers | `app.ctrl_service.disable_all` |
| status | controllers | `app.ctrl_service.status` |
| inspect | controllers | `app.ctrl_service.inspect` |
| truncate | connections | `app.conn_service.truncate_all` |
| status | connections | `app.conn_service.status` |
| inspect | connections | `app.conn_service.inspect` |

## Testing Plan
1. **Unit tests** (pytest): alias parsing, dispatcher routing, severity/roll-up logic, orchestration flows (mocked adapters), graceful purge order, exception→exit mapping.
   - Include a subprocess test that runs `python -m nifi_automation.cli.main --help` to prove the module entry point is wired correctly (prevents regressions when the CLI is invoked via `python -m`).
2. **Live integration** (after unit tests pass): load `.env`; run `clitool run flow <manifest>` then `clitool status flow`; expect roll-up `UP` or `HEALTHY` (text token).
   - Automated coverage lives in `automation/tests/integration/test_cli_live.py`, which invokes the CLI via `python -m nifi_automation.cli.main ...` whenever NiFi is reachable.
   - Tests purge the instance once at the start to enforce a clean state, then leave the deployed flow in place (never purge or stop at the end).

## Constraints
- Do not alter existing backend modules until the new CLI, unit tests, and live NiFi integration have succeeded.
- If backend limitations force deviations, document them in an Adaptation Summary before making changes.

## TODO / Future Enhancements
- Replace the current `.env` + flag approach with layered configuration files:
  - A CLI runtime config (e.g. `config/cli.toml`) to persist TLS settings, defaults such as `verify_ssl`, `ca_bundle`, timeouts, and preferred output modes.
  - A separate automation defaults file to manage controller/processor property overrides that apply before deployments.
- Extend TLS handling to support custom trust stores in addition to the simple `verify_ssl` boolean used today.
- Add `validate topology` subcommand that compares the deployed NiFi topology against a flow spec and fails on:
  - Missing processors (by name/type), ports (by name), or connections (by endpoints, including cross-boundary).
  - Count mismatches for processors, connections, ports, and child groups.
  - Include JSON details with exact paths and issues for CI gating.
- Add a layout validation step (no component overlaps, left-to-right guidance) that can run after deploy and in CI:
  - Reuse `infra.layout_checker.check_layout()`; expose via CLI (e.g., `validate layout`).
  - Fail on overlaps; optionally warn on left-to-right violations.
