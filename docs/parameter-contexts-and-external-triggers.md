# Parameter Contexts, External Triggers, and Multi‑Environment Deploys

This note outlines options and a recommended approach for parameterizing
externally triggered flows (HTTP/JMS/File), wiring Parameter Contexts into our
flow specs and deployer, and keeping CLI‑driven deployments aligned across
environments without duplicating NiFi artifacts in a registry.

## Goals
- One spec deploys cleanly to multiple environments (dev/stage/prod) via CLI.
- External trigger settings (ports, paths, topics, directories) live in
  Parameter Contexts, not hardcoded in processor properties.
- Defaults come from a developer/operator `.env`; tests read the same values.
- Controller Services and processors validate on first deploy (no manual edits).

## Options Overview
- A) Hardcode trigger settings in YAML
  - Simple, but requires edits per environment; discourages reuse.
- B) Use Parameter Contexts + CLI population (recommended)
  - Declare a context per PG in YAML; CLI sets parameter values from `.env` or
    CLI flags; deployer attaches contexts before creating components.
- C) Use NiFi Registry with environment overlays
  - Works, but we’ve chosen CLI‑based deploys; registry not required.

We will implement (B).

## Recommended Design

### 1. Spec changes (YAML)
Add an optional `parameter_context` block at any process group (including root):

```yaml
process_group:
  name: NiFi Flow
  parameter_context:
    name: default-context           # optional explicit name
    parameters:
      http.port:
        value: "#{NIFI_HTTP_TEST_PORT}"   # placeholder (resolved by CLI from .env)
        sensitive: false
      http.path:
        value: "/test"
  process_groups:
    - name: HttpServerWorkflow
      # processor properties reference parameters with NiFi syntax
      processors:
        - id: http-request
          type: org.apache.nifi.processors.standard.HandleHttpRequest
          properties:
            Listening Port: "#{http.port}"
            Base Path: "#{http.path}"
```

Notes
- NiFi parameter reference syntax is `#{paramName}` inside component properties.
- The YAML’s `value` fields are logical defaults; our CLI injects the actual
  values from the `.env`/flags and uploads them as parameter values.
- `sensitive: true` parameters are uploaded as NiFi sensitive parameters.

### 2. CLI + `.env` mapping
- The CLI reads `.env` and exposes `--param key=value` overrides.
- A simple mapping layer resolves placeholders:
  - If a parameter `http.port` value is exactly `#{NIFI_HTTP_TEST_PORT}`, the
    CLI looks up `NIFI_HTTP_TEST_PORT` in the environment and uses it.
  - Otherwise the YAML `value` is used verbatim.

Example `.env` (repo root):
```
NIFI_HTTP_TEST_PORT=18081
NIFI_HTTP_TEST_PATH=/test
```

### 3. Deployer behavior
Sequence for each PG in deploy:
1) Ensure Parameter Context exists (create-or-update), with `parameters` from the
   spec (resolved values and sensitive flags).
2) Attach the context to the PG (including root if root has a context).
3) Provision Controller Services (root‑level uses the root PG’s context).
4) Create processors/connections. Because properties already use `#{param}` and
   the PG has a context, components validate immediately.

Implementation notes
- Root‑level Controller Services can reference parameters if the root PG has a
  parameter context assigned (we already provision services at root).
- Context updates must preserve existing sensitive flags.
- If a parameter changes, PUT the context and wait for NiFi to apply.

### 4. Tests
- tests/flows/<PG>/ read the same `.env` defaults (no test‑only duplication).
- HTTP example (HttpServerWorkflow):
  - Flow: `HandleHttpRequest` + `HandleHttpResponse` with `HTTP Context Map`; port via `#{http.port}`.
  - Note: `HandleHttpRequest` does not have a “Base Path” property; route by inspecting `http.request.uri` if needed.
  - Test:
    ```python
    import os, httpx, time
    host = os.getenv("NIFI_HTTP_TEST_HOST","127.0.0.1")
    port = int(os.getenv("NIFI_HTTP_TEST_PORT", "18081"))
    path = os.getenv("NIFI_HTTP_TEST_PATH", "/test")
    # short readiness probe (~10s)
    deadline=time.time()+10
    last=None
    while time.time()<deadline:
        try:
            r=httpx.get(f"http://{host}:{port}{path}",timeout=1.0)
            last=r
            break
        except Exception:
            time.sleep(0.2)
    assert last is not None and last.status_code==204
    ```
- Policy: external trigger tests fail if unreachable after the readiness window.

## Controller Services interplay
- Controller Services can use parameters in their properties if assigned under a
  PG with an attached context. Since our services live at the root PG, assign a
  Parameter Context to the root (e.g., `default-context`) before creating
  services; properties such as endpoints/SSL keystore paths can become
  parameters.
- Example (HTTP Context Map is not parameterized itself, but processors that
  use it can be): `HTTP Context Map: http-context-map`; ports/paths become
  parameters.

## CLI deployment across environments (no registry)
- We will continue to deploy with the CLI, not NiFi Registry.
- Parameter Contexts make the flow portable without duplicating YAML:
  - Dev/stage/prod differences are `.env` or `--param` overrides.
  - The same spec/aggregate deploys everywhere.

## Security & maintainability
- Mark secrets as `sensitive: true` in the spec; CLI uploads as sensitive
  parameters; do not store secrets in the repository.
- Keep non‑secret defaults in `.env` for local runs; CI can inject secure values
  via environment.

## Migration plan
1) Add `parameter_context` support to the spec parser and FlowDeployer.
2) Introduce CLI flags:
   - `--param name=value` (repeatable) to override `.env`/YAML values.
   - `--param-file` to point at an env‑style file (optional).
3) Convert HttpServerWorkflow to use `#{http.port}`, `#{http.path}`.
4) Update tests to read `NIFI_HTTP_TEST_PORT`, `NIFI_HTTP_TEST_PATH`.
5) Document the pattern in automation/README.md and test‑suite guide.

## Example end‑to‑end
- `.env` (repo root):
  ```
  NIFI_HTTP_TEST_PORT=18081
  NIFI_HTTP_TEST_PATH=/test
  ```
- YAML (PG excerpt):
  ```yaml
  parameter_context:
    name: default-context
    parameters:
      http.port: { value: "#{NIFI_HTTP_TEST_PORT}", sensitive: false }
      http.path: { value: "/test", sensitive: false }
  processors:
    - id: http-request
      type: org.apache.nifi.processors.standard.HandleHttpRequest
      properties:
        Listening Port: "#{http.port}"
        Base Path: "#{http.path}"
  ```
- Deploy:
  ```bash
  python -m nifi_automation.cli.main run flow automation/flows/NiFi_Flow.yaml --output json
  ```
- Test:
  ```bash
  python -m pytest automation/tests/flows/HttpServerWorkflow -q
  ```

## Open questions / trade‑offs
- Parameter scoping: keep one root context or allow per‑PG contexts for complex
  deployments? (Start with one root context; allow overrides at child PGs.)
- Ordering: context updates vs. component creation — ensure we attach contexts
  before creating components that reference them.
- Sensitive parameters: provide a clear dev workflow (local `.env` for non‑secret
  defaults; CI/ops supply secrets via env/flags).

## Summary
- Parameter Contexts + CLI value injection give us portable, secure, and
  maintainable deployments. Specs remain single‑source; `.env`/flags carry
  environment intent; tests exercise the same values end‑to‑end.
