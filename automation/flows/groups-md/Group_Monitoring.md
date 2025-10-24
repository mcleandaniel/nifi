# Monitoring

Flows focused on runtime visibility and lightweight diagnostics.

```nifidesc
name: QueueDepthsHttpWorkflow
phase: draft
live: false
Overview: Exposes an HTTP endpoint that returns a simple HTML table of connection queue depths on the current NiFi instance.
Technical: HandleHttpRequest (path=/queues) → InvokeHTTP (POST ${BASE}/access/token with single-user creds) → UpdateAttribute (sets `Authorization: Bearer ${token}`) → InvokeHTTP (GET ${BASE}/flow/process-groups/root/status?recursive=true) → JoltTransformJSON (flatten connections to name, queuedCount, queuedBytes) → ReplaceText (wrap rows in an HTML table) → HandleHttpResponse (Content-Type: text/html). For HTTPS in Docker, target the internal URL (e.g., https://$(hostname):8443/nifi-api) and ensure TLS trust; in early iterations prefer Basic token fetch + Bearer header to keep auth simple.
```

Parameter hints (planned; implemented once Parameter Contexts land)

```nifiparams
- name: BASE
  description: NiFi API base URL reachable from within the flow (e.g., https://$(hostname):8443/nifi-api)
  sensitive: false
  scope: pg
- name: NIFI_USER
  description: Single-user username used for /access/token
  sensitive: false
  scope: pg
- name: NIFI_PASSWORD
  description: Single-user password used for /access/token
  sensitive: true
  scope: pg
```

Notes
- The Processor chain relies on JSON readers/writers and the HTTP Context Map controller service used elsewhere.
- If TLS trust blocks the internal HTTPS call, attach an SSL Context Service configured to trust the NiFi certificate. As an interim workaround during development, you can map the container certificate into a truststore and reference it.
- This flow stays in draft until the Parameter Contexts feature is wired into the deployer and the internal NiFi call path is validated.
