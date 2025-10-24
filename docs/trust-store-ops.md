# Trust Store Operations (Tools/TrustStoreManager)

This operator-only toolbox manages dedicated truststores for workflows. It never modifies the default truststore.

- Location: `/opt/nifi/nifi-current/conf/truststores/<name>.p12`
- Type: `JKS` by default (PKCS12/BCFKS supported via `ts.type`)
- Trigger: Manually via GenerateFlowFile → “Run once”
- Security: No HTTP ports; runs in NiFi with Restricted ExecuteStreamCommand

## Deploy

1) Purge NiFi for a clean slate:
```bash
source automation/.venv/bin/activate
python -m nifi_automation.cli.main purge flow --output json
```
2) Deploy tools PG:
```bash
python -m nifi_automation.cli.main run flow automation/tools/flows/trust_store_manager.yaml --output json
```

## Actions (attributes to set on the UpdateAttribute before Run once)

- Create
  - `ts.name`: truststore name (e.g., `local-nifi`)
  - `ts.type`: `JKS` (default; override with `PKCS12` or `BCFKS` if needed)
  - `ts.pass`: truststore password (required)
  - Note: Create ensures the directory; the keystore file is created by Add on first import.

- Add Certificate (from remote HTTPS endpoint)
  - `ts.name`, `ts.type`, `ts.pass`
  - `url.host`: e.g., `$(hostname)`
  - `url.port`: e.g., `8443`
  - `alias`: e.g., `local-nifi`
  - The flow fetches the remote certificate and imports it. Multiple certs in the chain are imported as `alias`, `alias-1`, `alias-2`, etc.

- Remove Certificate
  - `ts.name`, `ts.type`, `ts.pass`, `alias`

- Inspect Truststore
  - `ts.name`, `ts.type`, `ts.pass`
  - Output is text from `keytool -list -v -rfc` (first 120 lines); JSON formatting is a future enhancement.

## Wiring a Workflow

1) Create a StandardSSLContextService named `SSL TS:<name>`:
   - Truststore Filename: `/opt/nifi/nifi-current/conf/truststores/<name>.p12`
   - Truststore Type: `PKCS12`
   - Truststore Password: `<ts.pass>`
2) Set InvokeHTTP (or client) → `SSL Context Service = SSL TS:<name>`

## Notes
- No empty-password support: supply `ts.pass`. (TODO: allow reading from an env var.)
- Tools remain deployed for inspection and reuse. Do not auto-delete after running. Use the standard purge/cleardown before a new batch of deployments; never purge or delete at the end of tests.
