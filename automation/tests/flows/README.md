# Flow Tests

This tree holds external trigger tests for individual flows.

Structure
- `automation/tests/flows/<flow-name>/` – one folder per externally triggerable flow
  - Add `test_*.py` files that exercise the flow through its external interface (HTTP, JMS, files, etc.).

Conventions
- Name the folder after the process group in `NiFi_Flow.yaml` (e.g., `HttpServerWorkflow`).
- Tests must fail if the endpoint/path/port is not reachable; external triggers are part of the contract.
- Keep tests idempotent and side‑effect minimal.
- Prefer small, quick probes; deep assertions belong in unit tests or separate suites.

Planned folders
- `JmsTriggerWorkflow/` – JMS‑driven tests (future)
- `FileTriggerWorkflow/` – file system watch/poll tests (future)
