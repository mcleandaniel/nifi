# Controller Service Provisioning Design

This document captures the end-to-end plan for provisioning and maintaining
controller services used by NiFi automation flows. It builds on the exploratory
notes in `controller-services-detailed-notes.md` and formalises the behaviour we
expect from `ensure_root_controller_services`.

## Objectives
- Treat the controller service manifest as the single source of truth for all
  root-level services required by deployed flows.
- Guarantee idempotent provisioning: repeated runs reconcile state safely and
  leave services enabled with the desired configuration.
- Provide clear validation feedback when NiFi rejects property updates so the
  CLI can surface actionable errors.
- Keep the implementation extensible for new services, additional bundle hints,
  and non-root scopes in future iterations.

## Inputs & Artifacts
- `automation/manifest/controller-services.json`: declarative manifest with the
  logical key, NiFi type, display name, desired property overrides, bundle hint,
  and `auto_enable` flag.
- NiFi REST API endpoints:
  - `GET /flow/controller-service-types`
  - `GET /flow/controller-service-definition/...`
  - `POST /controller-services`
  - `PUT /controller-services/{id}`
  - `PUT /controller-services/{id}/run-status`
- Utility modules:
  - `nifi_automation.controller_registry` – manifest loader + reconciler.
  - `nifi_automation.client.NiFiClient` – thin httpx wrapper used by the CLI.

## Provisioning Workflow
1. **Load manifest** and map existing controller services (by cached UUID and by
   user-facing name) under the root process group.
2. **Resolve bundle** for the requested type. Prefer manifest hint; otherwise
   call `/flow/controller-service-types` and cache the result.
3. **Fetch property descriptors** via
   `/flow/controller-service-definition/{group}/{artifact}/{version}/{type}` to
   obtain canonical property keys, allowable values, and required flags.
4. **Normalise manifest properties** by translating aliases (display names,
   slugified variants) into NiFi’s canonical keys, trimming whitespace, and
   validating allowable values.
5. **Create service** when no existing entity matches:
   - Issue `POST /controller-services` under the root group.
   - Persist the returned UUID back into the manifest for future runs.
6. **Reconcile existing service** (matched by cached UUID or name):
   - Fetch the live entity. If in a transient state (`ENABLING` / `DISABLING`),
     wait until the state stabilises.
   - Disable the service when updates are required.
   - Compute the desired property map, clearing stale keys that NiFi now deems
     invalid.
   - Submit `PUT /controller-services/{id}` with the merged revision payload.
7. **Enable / disable to match manifest**:
   - If `auto_enable` is true, ensure the service transitions to `ENABLED`.
   - Otherwise leave or drive it to `DISABLED`.
   - Poll `GET /controller-services/{id}` until the expected state is reached.
8. **Persist manifest** when IDs or properties changed. This keeps the manifest
   aligned with NiFi-generated UUIDs and avoids unnecessary lookups later.

## Property Normalisation Rules
- Build an alias map that includes canonical key, raw name, display name, and
  slugified variants.
- When NiFi publishes allowable values, accept either canonical `value` or
  `displayName` from the manifest and submit the canonical `value` back.
- Strip keys that NiFi does not recognise (e.g., deprecated display-name
  variants) to prevent lingering validation warnings.
- Preserve empty strings for explicitly cleared properties; omit keys only when
  the descriptor lacks defaults and the manifest does not supply a value.

## Error Handling
- Wrap httpx `HTTPStatusError` instances in domain-specific messages so CLI
  users can identify the failing service and property.
- Surface NiFi validation errors (from `component.validationErrors`) after
  update attempts. These should be bubbled up as `FlowDeploymentError`.
- Time out state transitions after a bounded wait (default 30s) to avoid CLI
  hangs when NiFi cannot reach the target state.

## Testing & Tooling
- Unit tests should cover property normalisation edge cases, bundle resolution,
  and manifest persistence (see TODO list in `controller-services-detailed-notes.md`).
- Focused integration test (`tests/integration/test_live_nifi.py`) should:
  1. Purge root PG.
  2. Run `ensure_root_controller_services`.
  3. Assert required services exist, are enabled, and have no validation errors.
- Utility script `automation/scripts/provision_json_services.py` exercises the
  workflow against a live NiFi instance for manual diagnostics.

## Roadmap & Open Questions
- **Scoped services**: extend automation to manage controller services within
  child process groups, not just the root.
- **Dependency graph**: generate metadata linking processors to controller
  services for reporting and drift detection.
- **Parameterisation**: allow different manifests per environment (dev/test/prod)
  or support overrides layered on top of a shared baseline.
- **Validation CLI**: add `nifi-automation controller-services-validate` to run
  checks without mutating NiFi.
- **Error telemetry**: capture validation failures and timing metrics to feed
  into observability tooling once automation runs in CI.

---

*Last updated: 2025-10-17.*
