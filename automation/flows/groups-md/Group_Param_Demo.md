# Parameters Demo

A small group to exercise parameter context planning from Markdown hints and
flow YAML fragments. This group declares a mix of non‑sensitive and sensitive
parameters, as well as a flow that references an external controller service
(described in a separate controller MD file).

```nifiparams
- name: API_URL
  description: Base endpoint for Example API
  sensitive: false
  value: https://httpbin.org     # non-sensitive value may be declared in MD
  scope: pg                      # pg|global
  used_by:
    - processor: InvokeHTTP
      property: Remote URL
- name: API_TOKEN
  description: Bearer token for Example API
  sensitive: true
  source: vault:kv/data/example#api_token
  used_by:
    - processor: InvokeHTTP
      property: Authorization (dynamic header)
- name: LOG_LEVEL
  description: Log level for LogAttribute
  sensitive: false
  value: info
  used_by:
    - processor: LogAttribute
      property: Log Level
- name: NIFI_BASE_URL
  description: Base URL for local NiFi API
  sensitive: false
  value: https://localhost:8443/nifi-api
  used_by:
    - processor: InvokeHTTP
      property: Remote URL
- name: NIFI_USERNAME
  description: Dev single-user username (DEV ONLY)
  sensitive: false
  value: admin
- name: NIFI_PASSWORD
  description: Dev single-user password (DEV ONLY)
  sensitive: true
  value: changeMe123!
```

## Param Demo Workflow
```nifidesc
name: ParamDemoWorkflow
```

## Controller Ref Workflow
```nifidesc
name: ControllerRefWorkflow
```
