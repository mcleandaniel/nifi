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

Run‑Before‑Requesting (non‑negotiable)
- If you can run commands in this environment, you MUST run them yourself before asking the user to test. No exceptions.
  - Example: before asking to try `nifi-automation add trust ...`, run it locally, capture exit code and key output, and paste the concise result.
  - If a command needs credentials or env, source them in the snippet (e.g., `set -a; source .env; set +a`). Do not require the user to hand‑edit commands.
- Only ask the user to test when one of these is true:
  - You have run the exact commands successfully, and you’re providing copy‑paste steps (plus outputs you observed), or
  - You cannot run due to sandbox/network limits; in that case, state the block clearly at the top and provide a minimal, deterministic reproduction script.
- Never hand off an unverified flow/CLI change with “please test” when you have the ability to run it yourself.
  - If something fails locally, fix it or provide the failing command + traceback/output and your next debugging step.

Testing defaults
- For integration behaviors (start/stop/enable/disable), prefer live tests in `automation/tests/integration/` and wire them into `automation/scripts/run_integration_suite.sh`.

Testing discipline (must-do before asking the user to test)
- Always run the test suite relevant to your changes before asking the user to try anything.
  - Unit/structural: `pytest automation/tests -q` (or narrow to changed areas).
  - Integration (live NiFi): `bash automation/scripts/run_integration_suite.sh` from repo root.
  - Tools/Trust ops: run `pytest -q automation/tests/tools` for structure, and opt-in live tests under `automation/tests/integration/` when applicable.
- If you add or change CLI commands, run them locally (via `python -m nifi_automation.cli.main ...`) and include the exact commands and outputs.
- Purge NiFi before running integration flows that assume a clean canvas: `python -m nifi_automation.cli.main purge flow --output json`.
- If any test fails, fix the root cause or clearly document the failure with steps to reproduce; do not hand off broken flows to the user.

Live command etiquette
- Provide small, atomic blocks (2–3 commands) and wait for feedback/output before continuing.
- Prepend comment lines that are not meant to be run to clarify intent.
- Prefer idempotent operations and include cleanup where relevant.

CI etiquette
- Keep tests deterministic and fast by scoping live tests with markers and avoiding external dependencies unless explicitly required.
- When introducing new flows, add a minimal test (unit and/or live) demonstrating expected behavior.
