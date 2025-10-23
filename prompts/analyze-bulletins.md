Title: Analyze recent NiFi bulletins and suggest fixes

Instructions
- Run this command from the repository root to fetch recent bulletins:
  
  ```bash
  source automation/.venv/bin/activate
  set -a; source .env; set +a
  python automation/scripts/fetch_bulletins.py --limit 200 --severity ERROR --output json
  ```

- Paste the JSON output into the block below under BULLETINS_JSON.
- As a NiFi expert, analyze the errors and provide:
  - Root-cause hypotheses (network/DNS/TLS/auth, processor misconfig, backpressure, etc.)
  - Concrete next steps (e.g., test endpoint with curl, adjust processor properties, add controller service, increase timeouts)
  - Whether this is a deploy-time vs runtime issue, and recommended fix path
  - Any curl you want to run to reproduce/inspect NiFi state

Context
- Deploy-time issues should fail CI; runtime issues should be surfaced for triage without blocking deploys.
- Known dev patterns may be acceptable (e.g., local NiFi API unauthenticated calls will 401/timeout).

Input
```json
// BULLETINS_JSON
// Paste the JSON output of fetch_bulletins.py here
```

Output expectations
- Short summary (1–2 sentences)
- Categorized findings (by component and error type)
- Step-by-step triage plan with concrete commands (curl or NiFi REST) and config edits
- Clear recommendation whether to suppress (dev-only known) or fix immediately

