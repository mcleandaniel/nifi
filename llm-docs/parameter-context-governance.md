---
title: Parameter Context Governance
topic_id: project_project-parameter-context-governance
category: operations
priority: medium
tags: [parameters, governance, configuration]
claims:
  claim-param-contexts-global:
    - source: src-user-guide
      locator: "nifi-docs/src/main/asciidoc/user-guide.adoc#L881"
  claim-assign-to-pg-scope:
    - source: src-user-guide
      locator: "nifi-docs/src/main/asciidoc/user-guide.adoc#L955"
  claim-pg-one-context:
    - source: src-user-guide
      locator: "nifi-docs/src/main/asciidoc/user-guide.adoc#L957"
  claim-no-inherit-when-unset:
    - source: src-user-guide
      locator: "nifi-docs/src/main/asciidoc/user-guide.adoc#L975"
  claim-reference-syntax:
    - source: src-user-guide
      locator: "nifi-docs/src/main/asciidoc/user-guide.adoc#L979-L983"
  claim-escape-hash:
    - source: src-user-guide
      locator: "nifi-docs/src/main/asciidoc/user-guide.adoc#L993-L996"
  claim-parameter-parser-delimiters:
    - source: src-parameter-parser
      locator: "nifi-commons/nifi-parameter/src/main/java/org/apache/nifi/parameter/AbstractParameterParser.java#L21-L24"
  claim-parameter-quote-escape:
    - source: src-standard-parameter-context
      locator: "nifi-framework-bundle/nifi-framework/nifi-framework-components/src/main/java/org/apache/nifi/parameter/StandardParameterContext.java#L317-L325"
  claim-el-evaluation-order:
    - source: src-user-guide
      locator: "nifi-docs/src/main/asciidoc/user-guide.adoc#L1000-L1004"
  claim-sensitive-single-parameter:
    - source: src-user-guide
      locator: "nifi-docs/src/main/asciidoc/user-guide.adoc#L1047"
  claim-inheritance-precedence:
    - source: src-parameter-context-api
      locator: "nifi-framework-bundle/nifi-framework/nifi-framework-core-api/src/main/java/org/apache/nifi/parameter/ParameterContext.java#L149-L154"
  claim-version-increment:
    - source: src-parameter-lookup
      locator: "nifi-commons/nifi-parameter/src/main/java/org/apache/nifi/parameter/ParameterLookup.java#L37-L44"
  claim-update-stops-components:
    - source: src-user-guide
      locator: "nifi-docs/src/main/asciidoc/user-guide.adoc#L924"
  claim-admin-policy:
    - source: src-admin-guide
      locator: "nifi-docs/src/main/asciidoc/administration-guide.adoc#L1505-L1508"
  claim-api-context-basepath:
    - source: src-parameter-context-resource
      locator: "nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ParameterContextResource.java#L126-L129"
  claim-api-create-parameter-context:
    - source: src-parameter-context-resource
      locator: "nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ParameterContextResource.java#L219-L237"
  claim-api-get-parameter-context:
    - source: src-parameter-context-resource
      locator: "nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ParameterContextResource.java#L177-L216"
  claim-api-update-pg-parameter-context:
    - source: src-process-group-resource
      locator: "nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ProcessGroupResource.java#L457-L468"
  claim-api-update-pg-parameter-context-dto:
    - source: src-process-group-dto
      locator: "nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/dto/ProcessGroupDTO.java#L324-L332"
  claim-provider-fetch-endpoint:
    - source: src-parameter-provider-resource
      locator: "nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ParameterProviderResource.java#L682-L699"
  claim-provider-apply-endpoint:
    - source: src-parameter-provider-resource
      locator: "nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ParameterProviderResource.java#L812-L828"
  claim-provider-apply-longrunning:
    - source: src-parameter-provider-resource
      locator: "nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ParameterProviderResource.java#L824-L836"
  claim-provider-dto-fetch:
    - source: src-parameter-provider-fetch-entity
      locator: "nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/entity/ParameterProviderParameterFetchEntity.java#L17-L26"
  claim-provider-dto-apply:
    - source: src-parameter-provider-apply-entity
      locator: "nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/entity/ParameterProviderParameterApplicationEntity.java#L17-L25"
  claim-versioned-flows-include-params:
    - source: src-user-guide
      locator: "nifi-docs/src/main/asciidoc/user-guide.adoc#L2726-L2729"
  claim-import-merge-by-name:
    - source: src-user-guide
      locator: "nifi-docs/src/main/asciidoc/user-guide.adoc#L2730-L2756"
  claim-env-promotion-no-local-change:
    - source: src-user-guide
      locator: "nifi-docs/src/main/asciidoc/user-guide.adoc#L2662-L2664"
  claim-provider-no-manual-updates:
    - source: src-standard-parameter-context
      locator: "nifi-framework-bundle/nifi-framework/nifi-framework-components/src/main/java/org/apache/nifi/parameter/StandardParameterContext.java#L727-L733"
  claim-sensitivity-cannot-change:
    - source: src-standard-parameter-context
      locator: "nifi-framework-bundle/nifi-framework/nifi-framework-components/src/main/java/org/apache/nifi/parameter/StandardParameterContext.java#L735-L751"
sources:
  - id: src-user-guide
    title: NiFi User Guide (Asciidoc)
    path: nifi-docs/src/main/asciidoc/user-guide.adoc
  - id: src-admin-guide
    title: NiFi Administration Guide (Asciidoc)
    path: nifi-docs/src/main/asciidoc/administration-guide.adoc
  - id: src-parameter-parser
    title: AbstractParameterParser.java
    path: nifi-commons/nifi-parameter/src/main/java/org/apache/nifi/parameter/AbstractParameterParser.java
  - id: src-parameter-lookup
    title: ParameterLookup.java
    path: nifi-commons/nifi-parameter/src/main/java/org/apache/nifi/parameter/ParameterLookup.java
  - id: src-parameter-context-api
    title: ParameterContext.java
    path: nifi-framework-bundle/nifi-framework/nifi-framework-core-api/src/main/java/org/apache/nifi/parameter/ParameterContext.java
  - id: src-standard-parameter-context
    title: StandardParameterContext.java
    path: nifi-framework-bundle/nifi-framework/nifi-framework-components/src/main/java/org/apache/nifi/parameter/StandardParameterContext.java
  - id: src-parameter-context-resource
    title: ParameterContextResource.java
    path: nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ParameterContextResource.java
  - id: src-process-group-resource
    title: ProcessGroupResource.java
    path: nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ProcessGroupResource.java
  - id: src-process-group-dto
    title: ProcessGroupDTO.java
    path: nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/dto/ProcessGroupDTO.java
  - id: src-parameter-provider-resource
    title: ParameterProviderResource.java
    path: nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ParameterProviderResource.java
  - id: src-parameter-provider-fetch-entity
    title: ParameterProviderParameterFetchEntity.java
    path: nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/entity/ParameterProviderParameterFetchEntity.java
  - id: src-parameter-provider-apply-entity
    title: ParameterProviderParameterApplicationEntity.java
    path: nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/entity/ParameterProviderParameterApplicationEntity.java
---

**Introduction / Overview**

- <span id="claim-param-contexts-global">Parameter Contexts are created in NiFi and are globally defined for an instance with independent read and write access policies.</span>

- <span id="claim-assign-to-pg-scope">A Process Group must have a Parameter Context assigned before any component inside it can reference parameters.</span>

- <span id="claim-pg-one-context">Each Process Group can be assigned exactly one Parameter Context, and a Parameter Context can be bound to multiple Process Groups.</span>

- <span id="claim-no-inherit-when-unset">Unsetting a Parameter Context does not inherit from a parent group and renders existing parameter references invalid.</span>

**Concepts / Architecture**

- <span id="claim-reference-syntax">Parameter references use the syntax `#{Parameter.Name}` in component properties.</span>

- <span id="claim-escape-hash">Literal `#` characters are escaped using an extra `#` (for example `##{abc}` renders as `#{abc}`).</span>

- <span id="claim-parameter-parser-delimiters">NiFi’s parameter parser recognizes `#` as the start tag and `{`/`}` as delimiters for parameter references.</span>

- <span id="claim-parameter-quote-escape">Parameter names containing spaces or special characters can be quoted in expression contexts and are unescaped when looked up.</span>

- <span id="claim-el-evaluation-order">When parameters are used within Expression Language, the parameter reference is evaluated first, then Expression Language functions are applied.</span>

- <span id="claim-sensitive-single-parameter">Sensitive properties must be set to a single parameter reference and cannot concatenate other literals or parameters.</span>

- <span id="claim-inheritance-precedence">Parameter Contexts can inherit from other contexts; order defines overriding, and parameters defined in the current context take precedence over inherited values.</span>

- <span id="claim-version-increment">Parameter Contexts expose a version that increments on updates so components can detect value changes.</span>

**Implementation / Configuration**

- <span id="claim-update-stops-components">Applying parameter changes triggers validation and may stop and restart affected Processors and disable and re-enable affected Controller Services.</span>

- <span id="claim-admin-policy">Access to create or modify Parameter Contexts is governed by the global "access parameter contexts" policy and can be overridden from controller-level policies.</span>

- <span id="claim-api-context-basepath">The REST API for Parameter Contexts is rooted at `/nifi-api/parameter-contexts`.</span>

- <span id="claim-api-create-parameter-context">Creating a Parameter Context is a POST to `/parameter-contexts` with revision version `0` and a `component` describing the context.</span>

- <span id="claim-api-get-parameter-context">Retrieving a Parameter Context by ID is a GET to `/parameter-contexts/{id}`; specifying `includeInheritedParameters=true` returns the effective view.</span>

- <span id="claim-api-update-pg-parameter-context">Assigning a Parameter Context to a Process Group is a PUT to `/process-groups/{id}`.</span>

- <span id="claim-api-update-pg-parameter-context-dto">The `ProcessGroupDTO` contains a `parameterContext` reference used for binding.</span>

- <span id="claim-provider-fetch-endpoint">Parameter Providers support fetching parameters through POST to `/parameter-providers/{id}/parameters/fetch-requests`.</span>

- <span id="claim-provider-apply-endpoint">Fetched parameters can be applied with POST to `/parameter-providers/{id}/apply-parameters-requests`.</span>

- <span id="claim-provider-apply-longrunning">Applying fetched parameters is asynchronous and returns a request entity to poll until completion.</span>

- <span id="claim-provider-dto-fetch">The fetch request body uses `ParameterProviderParameterFetchEntity` with `id` and `revision`.</span>

- <span id="claim-provider-dto-apply">The apply request body uses `ParameterProviderParameterApplicationEntity` with `id`, `revision`, and optional group configurations.</span>

**Usage / Examples**

The snippets below assume `NIFI_URL` points to your NiFi API (for example `http://localhost:8080/nifi-api`) and that you have an authenticated session or configured proxy headers.

1) Create a Parameter Context

```bash
export NIFI_URL="http://localhost:8080/nifi-api"

curl -sS -X POST "$NIFI_URL/parameter-contexts" \
  -H 'Content-Type: application/json' \
  -d '{
    "revision": {"version": 0},
    "component": {
      "name": "pc-dev",
      "description": "Development parameters",
      "parameters": [
        {"parameter": {"name": "db.host", "sensitive": false, "value": "dev-db"}},
        {"parameter": {"name": "db.password", "sensitive": true,  "value": "dev-secret"}}
      ]
    }
  }'
```

2) Assign a Parameter Context to a Process Group

```bash
PG_ID="<your-process-group-id>"
PC_ID="<your-parameter-context-id>"

curl -sS -X PUT "$NIFI_URL/process-groups/$PG_ID" \
  -H 'Content-Type: application/json' \
  -d '{
    "revision": {"version": 0},
    "component": {
      "id": "'"$PG_ID"'",
      "parameterContext": {"id": "'"$PC_ID"'"}
    }
  }'
```

3) Parameter reference syntax in properties

```text
Input Directory = #{base.dir}/incoming
Password        = #{'db.password'}
```

4) Fetch and apply parameters from a Parameter Provider

```bash
PROVIDER_ID="<your-parameter-provider-id>"

# Fetch parameters (caches latest from the external source)
curl -sS -X POST "$NIFI_URL/parameter-providers/$PROVIDER_ID/parameters/fetch-requests" \
  -H 'Content-Type: application/json' \
  -d '{"id": "'"$PROVIDER_ID"'", "revision": {"version": 0}}'

# Apply fetched parameters to referencing contexts (async)
curl -sS -X POST "$NIFI_URL/parameter-providers/$PROVIDER_ID/apply-parameters-requests" \
  -H 'Content-Type: application/json' \
  -d '{"id": "'"$PROVIDER_ID"'", "revision": {"version": 0}}'
```

**Best Practices / Tips**

- <span id="claim-versioned-flows-include-params">When versioning flows, NiFi includes Parameter Context names and parameter metadata with the snapshot while excluding sensitive values.</span>

- <span id="claim-import-merge-by-name">On import, NiFi creates missing contexts and merges by context name, preserving existing differing values and leaving sensitive values unset.</span>

- <span id="claim-env-promotion-no-local-change">Assigning, creating, modifying, or deleting Parameter Contexts does not mark a versioned group as locally changed, enabling environment-specific promotion workflows.</span>

- <span id="claim-provider-no-manual-updates">When a context is configured to use a Parameter Provider, user-entered updates to its parameters are rejected.</span>

- <span id="claim-sensitivity-cannot-change">Parameter sensitivity cannot be changed via updates; attempts are rejected during validation.</span>

**Troubleshooting**

- <span id="claim-no-inherit-when-unset">If components become invalid after unsetting a Parameter Context, assign the appropriate context because Process Groups do not inherit a parent’s context when unset.</span>

- <span id="claim-escape-hash">If a literal `#` is required in a property, escape it using `##` to avoid unintended parameter parsing.</span>

- <span id="claim-el-evaluation-order">If Expression Language results are unexpected, ensure the parameter resolves first and that the resulting value is valid for the subsequent functions.</span>

- <span id="claim-update-stops-components">Expect brief interruptions when applying parameter updates because NiFi may stop or disable referencing components to validate changes.</span>

**Reference / Related Docs**

- NiFi User Guide: Parameter Contexts and Versioned Flows (`nifi-docs/src/main/asciidoc/user-guide.adoc`).
- NiFi Administration Guide: Access Policies (`nifi-docs/src/main/asciidoc/administration-guide.adoc`).
- API: `ParameterContextResource`, `ProcessGroupResource`, `ParameterProviderResource` (Java sources under `nifi-framework-bundle/`).

