# Security & Trust

Flows and utilities focused on SSL/TLS trust management for NiFi.

```nifidesc
name: TrustBootstrapWorkflow
Overview: HTTP-triggered utility that uses ExecuteProcess to fetch the NiFi server certificate from https://$(hostname):8443 and import it into the NiFi truststore, enabling InvokeHTTP to call the local HTTPS endpoint without disabling verification.
Technical: HandleHttpRequest (path=/trust/local) → ExecuteProcess runs `/opt/nifi/scripts/nifi_trust_helper.sh local --alias local-nifi` → HandleHttpResponse streams output and returns 200 on success, 500 on failure. Requires the script to be available inside the container and the NiFi user to have write access to the truststore.
```

Notes
- Ship or mount `automation/scripts/nifi_trust_helper.sh` into the container at `/opt/nifi/scripts/nifi_trust_helper.sh`.
- After truststore import, the SSL Context Service backing InvokeHTTP may need a disable/enable cycle (or restart) to reload. This utility focuses on truststore import; a future enhancement can toggle the controller service via REST.

