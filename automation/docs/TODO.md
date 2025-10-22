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
