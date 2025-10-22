# TODOs

## Description Sync (Docs ↔ YAML)

- CI guard: add a GitHub Actions job that runs `python automation/scripts/sync_descriptions.py --dry-run` on every PR and fails if it would modify any files. This enforces the single-source-of-truth policy without duplicating text.
- Reverse sync tool: extend `automation/scripts/sync_descriptions.py` with a `--from-yaml` mode that rebuilds the `nifidesc` blocks in `automation/flows/test-workflow-suite.md` from `automation/flows/*.yaml` (including `NiFi_Flow.yaml`). This is for exceptional cases where YAML was edited first.
- Dev ergonomics: optional pre-commit hook that runs the sync script (non-blocking) and prints a diff hint when out of sync.
- Acceptance criteria:
  - PRs that change descriptions in YAML/doc pass the CI guard only when in sync.
  - Reverse sync reproduces identical text blocks (Overview/Technical) in MD with the correct `name:`.

## Validation & CI Gates

- Expose `validate topology` as a CLI subcommand to compare deployed NiFi against a flow spec and fail with a machine-readable issues list.
- Add `validate layout` (no overlaps, optional left-to-right hints) using `infra.layout_checker.check_layout()`; fail on overlaps in CI.
- Wire both validators into the integration suite and offer standalone scripts for local runs.

## NOTDO / Non‑Goals

These are intentional non‑goals to prevent churn and preserve test intent.

- Backpressure gating stays as‑is.
  - Do NOT tweak queue/backpressure thresholds in code or tests to coerce `UP`.
  - Do NOT add flags to ignore or downgrade `BLOCKED` connections during `up flow`/`status flow`.
  - `BLOCKED` must continue to elevate the flow status to `INVALID` for CI visibility.
