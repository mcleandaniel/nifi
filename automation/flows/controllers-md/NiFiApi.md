# NiFi API Client (Controller Service Doc)

```controller-service
name: NiFiApi
type: org.apache.nifi.processors.standard.InvokeHTTP
description: HTTP client configuration for local NiFi REST API (dev only).
parameters:
  - name: NIFI_BASE_URL
    sensitive: false
    value: https://localhost:8443/nifi-api
  - name: NIFI_USERNAME
    sensitive: false
    value: admin
  - name: NIFI_PASSWORD
    sensitive: true
    value: changeMe123!
properties:
  - key: "Remote URL"
    value: "#{NIFI_BASE_URL}"
  - key: "Authorization"
    value: "Basic #{NIFI_USERNAME}:#{NIFI_PASSWORD}"
```

Notes
- Dev environment only — values are hardcoded from MD for demonstration.
- Production should use a Parameter Provider (Vault/DB) or token flow.
- Reference this file from flow YAML via `doc_refs: ["controllers-md/NiFiApi.md"]`.
