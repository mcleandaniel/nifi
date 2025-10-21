# Controller Service Bootstrap Design

*(Clean Environment Provisioning)*

## Objective

Provision a complete set of **root-level controller services** into a **clean NiFi instance** based solely on a declarative manifest.
This process assumes **no existing controller services** are deployed. It should create, configure, and enable all required services in one pass.

## Guiding Principles

* **Manifest is authoritative**: the JSON manifest defines all desired services, types, and properties.
* **Deterministic**: a single run on a clean system yields the same result every time.
* **Fail-fast**: validation or REST errors stop the run immediately with clear diagnostics.
* **Minimal state**: no reconciliation, UUID lookups, or disabling logic—everything is created anew.
* **Automation owns the purge**: `ensure_root_controller_services` aborts immediately if any controller service already exists, forcing callers to purge first.

## Explicit Non-Goals
- **No reconcile/diff mode**: the automation never attempts to detect or merge with existing services. Any reconciliation logic must be handled outside this workflow.
- **No scoped controller services**: services are provisioned only at the NiFi root; child process groups will not receive scoped controller services from this pipeline.
- **No `controller-services-validate` dry-run CLI**: validation is coupled with actual provisioning. Separate “validate without mutate” tooling remains out of scope.

## Inputs

* `automation/manifest/controller-services.json`
  Each entry includes:

  * `key`: logical identifier
  * `type`: NiFi controller service type (e.g., `org.apache.nifi.json.JsonTreeReader`)
  * `display_name`
  * `bundle`: optional `{group, artifact, version}` hint
  * `properties`: canonical key–value pairs
  * `auto_enable`: boolean flag

* NiFi REST API endpoints:

  * `GET /flow/controller-service-types`
  * `GET /flow/controller-service-definition/{group}/{artifact}/{version}/{type}`
  * `POST /controller-services`
* `PUT /controller-services/{id}/run-status` (state transitions only; configuration happens at creation time)

* Utility modules:

  * `controller_registry.py`: manifest loader and builder
  * `NiFiClient`: HTTP interface for REST calls

## Workflow

1. **Purge root group**
   Use `python -m nifi_automation.cli.main purge flow` to delete all processors, controller services,
   connections, and queued FlowFiles from the root process group. This guarantees a pristine environment.

2. **Load manifest**
   Parse `controller-services.json` into memory; validate structure and required fields.

3. **Resolve service types and bundles**
   For each service type:

   * If `bundle` is provided, use it.
   * Otherwise, query `/flow/controller-service-types` and select the matching implementation.

4. **Fetch canonical property descriptors**
   Call `/flow/controller-service-definition/...` for each type to obtain the authoritative property keys, allowable values, and required flags.

5. **Normalise manifest properties**

   * Translate any aliases (display names, slugs) to NiFi’s canonical property keys.
   * Validate that all required properties are present and that provided values are allowable.
   * Reject manifests that contain unknown keys—automation fails fast with actionable errors.

6. **Create services**
   For each manifest entry:

   * Issue `POST /controller-services` under the root process group with:

     * `type`
     * `bundle` (resolved above)
     * `name` (display_name)
     * `properties` (canonical map)
   * Capture the returned service UUID.
   * Fail fast if NiFi returns validation errors after creation (`ControllerServiceProvisioningError` encapsulates diagnostics).

7. **Configure and enable**

   * Configuration is applied during create; no follow-up PUT is required.
   * If `auto_enable` is true, call
     `PUT /controller-services/{id}/run-status` with state `ENABLED`.
   * Poll until state transitions to `ENABLED` (default timeout 30 s). Non-enabled states trigger a fatal error with reproduction commands.

8. **Persist manifest with UUIDs**
   Update `controller-services.json` so each service record includes its NiFi-assigned UUID for future reference.

## Error Handling

* Immediately stop on HTTP errors (`HTTPStatusError`) and print diagnostic payloads.
* Display any validation messages from NiFi’s response (`component.validationErrors`).
* Do **not** attempt retries or disable/enable cycles.
* Provide a `curl` reproduction snippet for manual inspection (token fetch + service GET) as in the detailed notes.

## Testing

* **Unit tests** (`test_controller_registry.py`)

  * Verify property normalisation and allowable-value translation.
  * Confirm manifests with unknown properties raise `ControllerServiceProvisioningError`.
  * Confirm manifest round-trip preserves UUIDs and canonical keys.
* **Integration tests** (`test_live_nifi.py`)

  * Purge root.
  * Provision all services from manifest.
  * Assert all reach `ENABLED` with zero validation errors and that only canonical keys remain (display-name aliases are absent).
  * Purge **before** the test run; never purge immediately afterward so failed states remain available for inspection.

## Deployment Workflow

- `python -m nifi_automation.cli.main run flow <spec>` now orchestrates steps 1–7 automatically:
  1. Purge requirements are enforced by `ensure_root_controller_services`.
  2. Controller services are created directly from the manifest.
  3. Flow components (processors, connections) are created only after services validate successfully.
