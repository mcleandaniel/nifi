# Bloomberg HTTP Client (Controller Service Doc)

```controller-service
name: BloombergHttp
type: org.apache.nifi.processors.standard.InvokeHTTP
description: HTTP client configuration for Bloomberg endpoints (example).
parameters:
  - name: BLOOMBERG_API_URL
    sensitive: false
    source: vault:kv/data/bloomberg#api_url
  - name: BLOOMBERG_USER
    sensitive: false
    source: vault:kv/data/bloomberg#user
  - name: BLOOMBERG_PASSWORD
    sensitive: true
    source: vault:kv/data/bloomberg#password
properties:
  - key: "Remote URL"
    value: "#{BLOOMBERG_API_URL}"
  - key: "Authorization"
    value: "Basic #{BLOOMBERG_USER}:#{BLOOMBERG_PASSWORD}"
```

Notes
- This document captures the intended parameters and how they bind to processor/service properties.
- Reference this file from flow YAML via `doc_refs: ["controllers-md/BloombergHttp.md"]`.
- Secrets are referenced via Vault URIs; values are not stored here.
