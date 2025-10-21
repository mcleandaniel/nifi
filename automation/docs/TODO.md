# TODOs

## Description Sync (Docs ↔ YAML)

- CI guard: add a GitHub Actions job that runs `python automation/scripts/sync_descriptions.py --dry-run` on every PR and fails if it would modify any files. This enforces the single-source-of-truth policy without duplicating text.
- Reverse sync tool: extend `automation/scripts/sync_descriptions.py` with a `--from-yaml` mode that rebuilds the `nifidesc` blocks in `automation/flows/test-workflow-suite.md` from `automation/flows/*.yaml` (including `NiFi_Flow.yaml`). This is for exceptional cases where YAML was edited first.
- Dev ergonomics: optional pre-commit hook that runs the sync script (non-blocking) and prints a diff hint when out of sync.
- Acceptance criteria:
  - PRs that change descriptions in YAML/doc pass the CI guard only when in sync.
  - Reverse sync reproduces identical text blocks (Overview/Technical) in MD with the correct `name:`.

