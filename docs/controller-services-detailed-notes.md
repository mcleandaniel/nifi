# Controller Service Provisioning – Detailed Notes

## Key Learnings
- NiFi descriptors often mark properties `required(true)` while still supplying defaults. Required only means the value may not be left blank; NiFi will pre-populate the provided default.
- NiFi responses normalise property keys: even when we submit canonical IDs, NiFi may echo both canonical and display-name entries. Automation treats the canonical key as source of truth and expects display-name slots to be empty.
- REST payloads must use the same property key NiFi declares in source. For some services (e.g., `JsonRecordSetWriter`), the descriptor name is literally the display string (`"Schema Write Strategy"`). Sending an aliased key (`schema-write-strategy`) triggers the validation error “not a supported property.”
- When provisioning via the manifest, normalise user-supplied keys/values to NiFi’s descriptors. Automation now rejects unknown keys and sends canonical property identifiers so NiFi’s validation either passes cleanly or fails with explicit errors.
- Avoid mid-flight reconciliation cycles. Provisioning happens on a clean instance; if controller services already exist, automation aborts and instructs the operator to purge instead of attempting disable/update loops.

## Troubleshooting Flow (Regression Workflow)
1. **Purge the NiFi root process group (`purge_root`) before doing anything else.**
   Assume the instance is dirty until you personally cleared it this session.
2. Run a focused provisioning test that calls `ensure_root_controller_services` and asserts:
   - The expected controller-service IDs exist.
   - NiFi reports canonical property keys (display-name aliases are blank) and no validation errors.
   - If any service remains in `ENABLING` or `INVALID`, **stop immediately** and capture the reproduction commands (token fetch + service inspection) instead of looping on automation retries.
3. Use the scripted curl commands:
  ```bash
  set -a; source .env; set +a
  TOKEN=$(curl -sk -X POST "${NIFI_BASE_URL}/access/token" -d "username=${NIFI_USERNAME}&password=${NIFI_PASSWORD}")
  curl -sk -H "Authorization: Bearer $TOKEN" \
     "${NIFI_BASE_URL}/controller-services/${SERVICE_ID}" \
     | jq '.component | {name, state, validationErrors, properties}'
   ```
4. Only after the standalone test passes should you attempt higher-level deployments (e.g., `NiFi_Flow.yaml`).
   Avoid purging **after** tests run; preserve the deployed state so you can inspect any failures.

## Next Steps
- Codify the standalone provisioning test in `tests/integration/test_live_nifi.py` and ensure the CI (or local workflow) runs it before flow deployment tests.
- Update the manifest normaliser to prefer descriptor display names when NiFi’s source uses them literally and remove alias keys entirely.
- Regenerate the controller-service report once the manifest behaves correctly; verify that services such as `JsonRecordSetWriter` show as VALID in NiFi’s UI.

## Utility Script
Run `automation/scripts/purge_nifi_root.py` to clear the root PG (queues, processors, controller services) before
deployments. For deeper diagnostics, `automation/scripts/provision_json_services.py` can still reprovision the
JsonTreeReader/JsonRecordSetWriter services and dump their state; however, the standard
`nifi-automation deploy-flow` command now provisions services automatically when the instance is clean.
```bash
cd automation
RUN_NIFI_INTEGRATION=1 .venv/bin/python scripts/provision_json_services.py
```
For manual inspection via `curl`, load the `.env` defaults and fetch a token:
```bash
set -a
source .env
set +a
TOKEN=$(curl -sk -X POST "$NIFI_BASE_URL/access/token" -d "username=$NIFI_USERNAME&password=$NIFI_PASSWORD")
```
Then inspect controller services:
```bash
curl -sk -H "Authorization: Bearer $TOKEN" \
  "$NIFI_BASE_URL/flow/process-groups/root/controller-services?includeInherited=false" \
  | jq '.controllerServices[] | {id: .component.id, name: .component.name, state: .component.state, validationErrors: .component.validationErrors}'

curl -sk -H "Authorization: Bearer $TOKEN" \
  "$NIFI_BASE_URL/controller-services/<service-id>" \
  | jq '.component | {name, state, validationErrors, properties}'
```
Replace `<service-id>` with the UUID reported in the first command.

- When run as part of automation, emit these commands for the operator rather than attempting further REST updates while the service is unstable. This keeps investigation efficient and avoids thrashing NiFi with redundant mutations.

---

## Canonical Descriptor Reference

These tables collect the canonical property keys NiFi expects for the JSON reader/writer controller services referenced by `flows/simple.yaml`. Use these values when updating the manifest or when comparing REST payloads.

### Shared Schema Access Properties

| Canonical Key | UI Display | Required? | Default | Allowable Values (canonical → display) | Notes |
| --- | --- | --- | --- | --- | --- |
| `schema-access-strategy` | Schema Access Strategy | ✔ | `schema-name` | `schema-name` → Use 'Schema Name' Property, `schema-text-property` → Use 'Schema Text' Property, `schema-reference-reader` → Inherit Record Schema From Upstream | Drives which dependent properties NiFi requires. |
| `schema-registry` | Schema Registry | contextual | — | Controller service ref | Required when strategy is `schema-name` or `schema-reference-reader`. |
| `schema-name` | Schema Name | contextual | `${schema.name}` | string | Required when strategy is `schema-name`. |
| `schema-text` | Schema Text | contextual | `${avro.schema}` | string | Required when strategy is `schema-text-property`. |
| `schema-reference-reader` | Schema Reference Reader | contextual | — | Controller service ref | Required when strategy is `schema-reference-reader`. |
| `schema-branch` | Schema Branch | optional | — | string | Only valid with strategy `schema-name`. |
| `schema-version` | Schema Version | optional | — | string | Only valid with strategy `schema-name`. |

### JsonTreeReader-Specific Properties

| Canonical Key | UI Display | Required? | Default | Allowable Values (canonical → display) | Notes |
| --- | --- | --- | --- | --- | --- |
| `starting-field-strategy` | Starting Field Strategy | ✔ | `whole-flowfile` | `whole-flowfile` → Whole FlowFile, `nested-field` → Nested Field | `nested-field` requires `starting-field-name`. |
| `starting-field-name` | Starting Field Name | contextual | — | string | Required when `starting-field-strategy` is `nested-field`. |
| `date-format` | Date Format | optional | — | string | Inherited from base reader. |
| `time-format` | Time Format | optional | — | string | Inherited. |
| `timestamp-format` | Timestamp Format | optional | — | string | Inherited. |

### JsonRecordSetWriter-Specific Properties

| Canonical Key | UI Display | Required? | Default | Allowable Values (canonical → display) | Notes |
| --- | --- | --- | --- | --- | --- |
| `schema-write-strategy` | Schema Write Strategy | ✔ | `no-schema` | `no-schema` → Do Not Write Schema, `hwx-schema-ref` → Hortonworks Schema Reference, `embed-avro-schema` → Embed Avro Schema | Key field NiFi validates during enablement. |
| `suppress-nulls` | Suppress Nulls | optional | `false` | `true`, `false` | Boolean string. |
| `compression-format` | Compression Format | optional | `none` | `none`, `gzip`, `bzip2`, `lz4`, `snappy` | Matches `CompressionFormat` enum. |
| `date-format` | Date Format | optional | `yyyy-MM-dd` | string | Inherited writer option. |
| `time-format` | Time Format | optional | `HH:mm:ss.SSS` | string | Inherited writer option. |
| `timestamp-format` | Timestamp Format | optional | `yyyy-MM-dd HH:mm:ss.SSS` | string | Inherited writer option. |

### Canonical Value Mapping Example

If the manifest specifies:

```
Schema Access Strategy: Infer Schema
schema-name: my-schema
```

The REST payload we send must be:

```json
{
  "schema-access-strategy": "infer-schema",
  "schema-name": "my-schema"
}
```

Note the lowercase canonical keys and allowable value string (`infer-schema`) exactly match NiFi's descriptor definitions.

---

## Automation Follow-Ups

- ✅ Update `manifest/controller-services.json` to emit canonical keys/values (done).
- ✅ Extend `_normalise_properties` in `controller_registry.py` to translate display-name keys and strip stale aliases (done).
- ✅ Write a focused unit test for `_normalise_properties` covering display-name inputs and allowable value translation.
- ☐ Extend the flow manifest (or per-flow metadata) so `json-reader`/`json-writer` dependencies are guaranteed before deploying `flows/simple.yaml`.
- ☐ Consider a validation utility that diff-checks controller service properties after enablement to catch regression drift.
