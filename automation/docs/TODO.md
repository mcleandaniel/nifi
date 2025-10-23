# TODOs

## Description Sync (Docs ↔ YAML)

- CI guard: add a GitHub Actions job that runs `python automation/scripts/sync_descriptions.py --dry-run` on every PR and fails if it would modify any files. This enforces the single-source-of-truth policy without duplicating text.
- Reverse sync tool: extend `automation/scripts/sync_descriptions.py` with a `--from-yaml` mode that rebuilds the `nifidesc` blocks in `automation/flows/test-workflow-suite.md` from `automation/flows/*.yaml` (including `NiFi_Flow.yaml`). This is for exceptional cases where YAML was edited first.

Authoring pipeline (MD → stub → YAML → deploy)
- Add CLI subcommands later to manage authoring life-cycle (out of scope for now):
  - `author stubs` (calls generate_stubs_from_md)
  - `author validate` (lint fragment structure; require canonical NiFi property keys)
  - `author promote` (enforce `phase: ready` before build/deploy)
- Develop detailed guidelines for human/LLM transformation from stub to full YAML:
  - Canonical processor types, property keys, and allowed relationships
  - Stable `id` conventions for wiring
  - When to introduce controller services, ports, nested PGs
  - Scheduling conventions (e.g., generators at `1 min`)
- Publish a prompt pack (llm-docs/) for LLMs to expand stubs:
  - Input: group MD + stub, Output: full YAML fragment (validated)
  - Include “dos & don’ts” and examples for common patterns
- Optionally add a checker that flags fragments with `phase != ready` during build to prevent accidental deploys

Markdown-driven parameters and controller docs
- Define MD schemas and parsers:
  - `nifiparams` fenced block in group MD for declaring parameter hints (name, description, sensitive, scope, source, used_by).
  - `controller-service` fenced block in controller MD files under `automation/flows/controllers-md/`.
- Extend parameter planner to merge MD hints with extracted `#{...}` references and include Vault/DB source refs (omit values).
- Support `doc_refs` metadata in flow YAML (PG/component) pointing to controller MD files.
- Add `params plan --with-md` flag to include MD hints and show provenance in output (source=md|discovered).

Deploy warnings
- Add non-blocking warnings in `deploy_adapter.deploy_flow` when any top-level child PG or fragment carries `phase != ready`.
  - Surface as `result["warnings"]` to the CLI. Do not fail the deploy.

Reverse tests (leave env as found)
- Establish a convention in integration tests to undo side-effects at test end:
  - If a test stops processors/ports or disables controllers, it must start/enable them at the end unless a subsequent test depends on the changed state.
  - For multi-step sequences, only the last test restores the environment.
- Add a final assertion in admin-ops test to leave processors RUNNING and ports RUNNING.
- Consider a shared fixture/helper to capture state and restore on teardown for more complex cases.
- Dev ergonomics: optional pre-commit hook that runs the sync script (non-blocking) and prints a diff hint when out of sync.
- Acceptance criteria:
  - PRs that change descriptions in YAML/doc pass the CI guard only when in sync.
  - Reverse sync reproduces identical text blocks (Overview/Technical) in MD with the correct `name:`.

## Validation & CI Gates

- Expose `validate topology` as a CLI subcommand to compare deployed NiFi against a flow spec and fail with a machine-readable issues list.
- Expose `validate layout` as a CLI subcommand (status/inspect style) using `infra.layout_checker.check_layout()`:
  - Fail on overlaps in CI; report left-to-right violations (non-fatal) with counts and locations.
  - Acceptance: `nifi-automation validate layout --output json` returns `{ overlaps:[], left_to_right_violations:[...] }`.
- Wire both validators into the integration suite and offer standalone scripts for local runs.

## Layout Optionality Tests

- Positions in YAML are optional and should not be required for deployment.
  - Add tests that deploy representative flows with no `position` fields (auto-layout) and with explicit positions mixed in.
  - Acceptance:
    - Deploy succeeds without any `position` entries.
    - Deploy succeeds when some components include `position` while others omit it (auto-layout fills the rest).

## NOTDO / Non‑Goals

These are intentional non‑goals to prevent churn and preserve test intent.

- Backpressure gating stays as‑is.
  - Do NOT tweak queue/backpressure thresholds in code or tests to coerce `UP`.
  - Do NOT add flags to ignore or downgrade `BLOCKED` connections during `up flow`/`status flow`.
  - `BLOCKED` must continue to elevate the flow status to `INVALID` for CI visibility.

## Icons & Diagramming

- Add a tiny “icon theme” flag (e.g., dark/light) to the icon generator (`automation/scripts/generate_processor_icons.py`) and document usage in `automation/assets/processor-icons/README.md`.
- Expand initial icon coverage beyond the first 20 common processors; prioritize types used in `automation/flows/NiFi_Flow.yaml` (e.g., UpdateRecord, GenerateRecord, CompressContent, RouteOnContent) and add tests to ensure a safe fallback icon when missing.

## Comments Policy

- Add `comments` support in processor specs (YAML) and propagate to NiFi `component.config.comments` on deploy.
- Add CLI validator: `nifi-automation validate comments [SPEC] --output json` that reports processors missing comments except for trivial allow‑list types (initially: `LogAttribute`).
- Wire comments validator into the deploy‑phase validation and integration suite gates (fail build if violations exist).
- Authoring guide: see `automation/docs/tests/processor-comments.md` for schema, rules, and examples.

- Backfill pass (non‑blocking): create an issue checklist to add concise `comments:` to existing processors across flows.
  - Scope: `automation/flows/NiFi_Flow.yaml` and any single‑flow specs under `automation/flows/*.yaml`.
  - Provide a helper script (advisory only) to list processors without `comments:`; do not fail CI.
  - Track completion per process group; keep increments small to ease review.

## ProcessGroup Library (new)

Goal: Curate reusable Process Group fragments that can be injected into flows by reference.

- Directory layout: `automation/process-library/` (siblings of `flows/` and `diagrams/`).
- Fragment format: standalone YAML with a top-level `process_group` mapping; each PG exposes `input_ports`/`output_ports`.
- Composition (MVP): preprocessor inlines library PGs into a harness flow at deploy time.
  - Script: `automation/scripts/compose_with_library.py` (done)
  - Harness example: `automation/flows/library/http_library_harness.yaml` (done)
  - Two starter PGs: `EchoLogger.yaml`, `AttributeTagger.yaml` (done)
- Roadmap (native support):
  - Extend deployer to recognize `library_includes` directly in flow YAML and perform composition internally.
  - Add aliasing, namespacing of child port keys, and conflict detection.
  - Enable parameterization of library PGs (e.g., attr names) via future Parameter Contexts and/or templated properties.
  - Add docs with patterns and catalog, plus tests that deploy each library PG in isolation and under a harness.

## Trust Store Tools (follow-ups)

- Optional `--ephemeral` flag to purge tools PG after completion; default remains manual delete. (Implemented by default for trust CLI.)

## QueueDepthsHttpWorkflow response body

- Ensure the `/queues` endpoint returns a non-empty HTML table. Investigate current `EvaluateJsonPath` + `ReplaceText` chain:
  - If content remains empty despite `Replacement Strategy: Always Replace`, switch to a Jolt or explicit `ReplaceText` that wraps a known JSON payload from `/flow/process-groups/root/status?recursive=true`.
  - Add an assertion in the test for presence of `<table` and a `Queued` or equivalent label.
  - Stretch goal: provide a JSON variant at `/queues.json` and keep HTML as a simple view.
