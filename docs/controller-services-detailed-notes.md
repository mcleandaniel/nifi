# Controller Service Provisioning – Detailed Notes

## Key Learnings
- NiFi descriptors often mark properties `required(true)` while still supplying defaults. Required only means the value may not be left blank; NiFi will pre-populate the provided default.
- REST payloads must use the same property key NiFi declares in source. For some services (e.g., `JsonRecordSetWriter`), the descriptor name is literally the display string (`"Schema Write Strategy"`). Sending an aliased key (`schema-write-strategy`) triggers the validation error “not a supported property.”
- When provisioning via the manifest, normalise user-supplied keys/values to NiFi’s descriptors and clear any stale display-name variants so only the canonical key remains.
- Always disable a controller service before updating properties; re-enable only after NiFi has applied the changes and reported no validation errors.

## Troubleshooting Flow (Regression Workflow)
1. Purge the NiFi root process group (`purge_root`).
2. Run a focused provisioning test that calls `ensure_root_controller_services` and asserts:
   - The expected controller-service IDs exist.
   - Properties contain only canonical keys and no validation errors.
3. Use the scripted curl commands:
   ```bash
   set -a; source .env; set +a
   TOKEN=$(curl -sk -X POST "${NIFI_BASE_URL}/access/token" -d "username=${NIFI_USERNAME}&password=${NIFI_PASSWORD}")
   curl -sk -H "Authorization: Bearer $TOKEN" \
     "${NIFI_BASE_URL}/controller-services/${SERVICE_ID}" \
     | jq '.component | {name, state, validationErrors, properties}'
   ```
4. Only after the standalone test passes should you attempt higher-level deployments (e.g., `simple.yaml`).

## Next Steps
- Codify the standalone provisioning test in `tests/integration/test_live_nifi.py` and ensure the CI (or local workflow) runs it before flow deployment tests.
- Update the manifest normaliser to prefer descriptor display names when NiFi’s source uses them literally and remove alias keys entirely.
- Regenerate the controller-service report once the manifest behaves correctly; verify that services such as `JsonRecordSetWriter` show as VALID in NiFi’s UI.

## Utility Script
Run `automation/scripts/provision_json_services.py` to purge NiFi, reprovision the JsonTreeReader/JsonRecordSetWriter services, and dump their state (including validation errors and properties):
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
