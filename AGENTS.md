# Agent Guidelines for This Repository

Purpose
- Keep the assistant aligned with project priorities and avoid noisy, repetitive suggestions.

When suggesting features or changes
- Before proposing a feature, check `automation/docs/TODO.md` and `docs/cli-refactor-plan.md`.
  - If the idea already exists there, acknowledge it and do not repeat the suggestion.
  - If the idea is new and valuable, add it to `automation/docs/TODO.md` with a concise description and acceptance criteria.

Layout/validation considerations
- Use the built-in layout checker (`infra/layout_checker.py`) semantics when discussing or proposing layout changes.
- Follow the project’s NOTDO rules in `automation/docs/TODO.md` (e.g., do not weaken backpressure gating).

CLI and scripts
- Prefer scripted commands over manual steps. When demonstrating CLI usage, include environment setup (e.g., `source .env`).
- Use the module entrypoint (`python -m nifi_automation.cli.main`) in tests to mirror real usage.

Testing defaults
- For integration behaviors (start/stop/enable/disable), prefer live tests in `automation/tests/integration/` and wire them into `automation/scripts/run_integration_suite.sh`.

