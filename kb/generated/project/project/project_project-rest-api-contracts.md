---
claims:
  claim-api-base-path:
    - source: src-jetty-server
      locator: "L139-L148"
  claim-resource-registration:
    - source: src-resource-config
      locator: "L79-L107"
  claim-entity-envelope:
    - source: src-component-entity
      locator: "L31-L138"
  claim-flow-entity-structure:
    - source: src-process-group-flow-entity
      locator: "L32-L75"
  claim-revision-optimistic-lock:
    - source: src-revision-dto
      locator: "L35-L80"
  claim-flow-endpoint:
    - source: src-flow-resource
      locator: "L456-L493"
    - source: src-process-group-flow-entity
      locator: "L32-L75"
  claim-process-group-endpoint:
    - source: src-process-group-resource
      locator: "L240-L268"
    - source: src-process-group-entity
      locator: "L30-L87"
  claim-processor-endpoint:
    - source: src-processor-resource
      locator: "L191-L218"
    - source: src-processor-entity
      locator: "L29-L64"
  claim-connection-endpoint:
    - source: src-connection-resource
      locator: "L101-L140"
    - source: src-connection-entity
      locator: "L30-L69"
  claim-controller-service-endpoint:
    - source: src-controller-service-resource
      locator: "L180-L218"
    - source: src-controller-service-entity
      locator: "L29-L88"
  claim-parameter-context-endpoint:
    - source: src-parameter-context-resource
      locator: "L177-L214"
    - source: src-parameter-context-entity
      locator: "L24-L35"
    - source: src-parameter-context-dto
      locator: "L29-L100"
  claim-process-group-retrieve-usage:
    - source: src-process-group-resource
      locator: "L240-L268"
    - source: src-component-entity
      locator: "L31-L52"
  claim-update-revision:
    - source: src-revision-dto
      locator: "L55-L66"
    - source: src-process-group-resource
      locator: "L240-L245"
  claim-flow-uionly-stability:
    - source: src-flow-resource
      locator: "L456-L475"
  claim-non-guaranteed-endpoint:
    - source: src-application-resource
      locator: "L117-L124"
  claim-conflict-response:
    - source: src-process-group-resource
      locator: "L240-L245"
  claim-ref-process-group-resource:
    - source: src-process-group-resource
      locator: "L150-L268"
  claim-ref-dto-module:
    - source: src-process-group-entity
      locator: "L30-L87"
sources:
  src-jetty-server:
    type: file
    title: JettyServer.java
    path: nifi-framework-bundle/nifi-framework/nifi-web/nifi-jetty/src/main/java/org/apache/nifi/web/server/JettyServer.java
  src-resource-config:
    type: file
    title: NiFiWebApiResourceConfig.java
    path: nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/NiFiWebApiResourceConfig.java
  src-component-entity:
    type: file
    title: ComponentEntity.java
    path: nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/entity/ComponentEntity.java
  src-process-group-flow-entity:
    type: file
    title: ProcessGroupFlowEntity.java
    path: nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/entity/ProcessGroupFlowEntity.java
  src-revision-dto:
    type: file
    title: RevisionDTO.java
    path: nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/dto/RevisionDTO.java
  src-flow-resource:
    type: file
    title: FlowResource.java
    path: nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/FlowResource.java
  src-process-group-resource:
    type: file
    title: ProcessGroupResource.java
    path: nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ProcessGroupResource.java
  src-process-group-entity:
    type: file
    title: ProcessGroupEntity.java
    path: nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/entity/ProcessGroupEntity.java
  src-processor-resource:
    type: file
    title: ProcessorResource.java
    path: nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ProcessorResource.java
  src-processor-entity:
    type: file
    title: ProcessorEntity.java
    path: nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/entity/ProcessorEntity.java
  src-connection-resource:
    type: file
    title: ConnectionResource.java
    path: nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ConnectionResource.java
  src-connection-entity:
    type: file
    title: ConnectionEntity.java
    path: nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/entity/ConnectionEntity.java
  src-controller-service-resource:
    type: file
    title: ControllerServiceResource.java
    path: nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ControllerServiceResource.java
  src-controller-service-entity:
    type: file
    title: ControllerServiceEntity.java
    path: nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/entity/ControllerServiceEntity.java
  src-parameter-context-resource:
    type: file
    title: ParameterContextResource.java
    path: nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ParameterContextResource.java
  src-parameter-context-entity:
    type: file
    title: ParameterContextEntity.java
    path: nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/entity/ParameterContextEntity.java
  src-parameter-context-dto:
    type: file
    title: ParameterContextDTO.java
    path: nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/dto/ParameterContextDTO.java
  src-application-resource:
    type: file
    title: ApplicationResource.java
    path: nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ApplicationResource.java
---

# REST API Contract Surface

## Introduction / Overview
<span id="claim-api-base-path">NiFi exposes its REST API under the `/nifi-api` servlet context configured as a required Jetty deployment path.</span>
<span id="claim-resource-registration">The Jersey application registers Flow, ProcessGroup, Processor, Connection, ControllerService, ParameterContext, and related resources to cover the automation surface.</span>

## Concepts / Architecture
<span id="claim-entity-envelope">API responses wrap flow components in `ComponentEntity`, which adds shared metadata such as `revision`, `id`, `uri`, permissions, bulletins, and disconnected-node acknowledgment.</span>
<span id="claim-flow-entity-structure">Flow-level queries return `ProcessGroupFlowEntity` objects that combine a `RevisionDTO`, permission metadata, and the nested `ProcessGroupFlowDTO` payload.</span>
<span id="claim-revision-optimistic-lock">The `RevisionDTO` enforces optimistic locking, requiring clients to send the latest `version` (and optional `clientId`) when submitting mutable requests.</span>

## Implementation / Configuration
- <span id="claim-flow-endpoint">`GET /flow/process-groups/{id}` produces a `ProcessGroupFlowEntity` with the current flow contents for the requested process group.</span>
- <span id="claim-process-group-endpoint">`GET /process-groups/{id}` returns a `ProcessGroupEntity` whose `component` is the target group's `ProcessGroupDTO`.</span>
- <span id="claim-processor-endpoint">`GET /processors/{id}` yields a `ProcessorEntity` encapsulating the processor's `ProcessorDTO` and status.</span>
- <span id="claim-connection-endpoint">`GET /connections/{id}` responds with a `ConnectionEntity` that embeds the associated `ConnectionDTO` and connection status fields.</span>
- <span id="claim-controller-service-endpoint">`GET /controller-services/{id}` returns a `ControllerServiceEntity` wrapping the controller service `ControllerServiceDTO`.</span>
- <span id="claim-parameter-context-endpoint">`GET /parameter-contexts/{id}` responds with a `ParameterContextEntity` whose `ParameterContextDTO` carries the context name, parameters, inherited contexts, and bound process groups.</span>

## Usage / Examples
<span id="claim-process-group-retrieve-usage">Fetch the process group entity before updates to capture the authoritative `revision` metadata from the response.</span>

```bash
export NIFI_URL="https://nifi.example.com"
export NIFI_TOKEN="$(cat ~/.config/nifi/token)"
export PG_ID="root"

curl -s -H "Authorization: Bearer $NIFI_TOKEN" \
  "$NIFI_URL/nifi-api/process-groups/$PG_ID" \
  | jq '{revision, component: {id, name}}'
```

<span id="claim-update-revision">Include the returned `revision.version` (and optionally `clientId`) in mutable requests because NiFi rejects stale revisions with HTTP 409.</span>

```bash
rev="$(curl -s -H "Authorization: Bearer $NIFI_TOKEN" \
  "$NIFI_URL/nifi-api/process-groups/$PG_ID" | jq '.revision.version')"

payload="$(jq -n --arg id "$PG_ID" --arg name "Renamed by API" --argjson version "$rev" '
  {revision:{version:$version}, component:{id:$id, name:$name}}')"

curl -s -X PUT -H "Authorization: Bearer $NIFI_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$payload" \
  "$NIFI_URL/nifi-api/process-groups/$PG_ID"
```

## Best Practices / Tips
<span id="claim-flow-uionly-stability">Avoid the `uiOnly=true` projection outside the NiFi UI, because FlowResource explicitly marks those fields as subject to change between releases.</span>
<span id="claim-non-guaranteed-endpoint">Treat any endpoint labeled with `NON_GUARANTEED_ENDPOINT` as unstable, since the base resource class notes that its contract may change as the REST API evolves.</span>

## Troubleshooting
<span id="claim-conflict-response">A 409 response from controllers such as ProcessGroupResource means NiFi deemed the request valid but not actionable—typically because the revision was stale—so refresh state and retry.</span>

## Reference / Related Docs
- <span id="claim-ref-process-group-resource">`nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ProcessGroupResource.java` contains the `/process-groups` REST controller implementation.</span>
- <span id="claim-ref-dto-module">`nifi-framework-bundle/nifi-framework/nifi-client-dto/src/main/java/org/apache/nifi/web/api/entity/ProcessGroupEntity.java` illustrates how reusable DTO entities reside in the `nifi-client-dto` module.</span>
