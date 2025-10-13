# NiFi REST API — LLM Notes

*Source focus*: `nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api` resource classes (reviewed 2025-10-13) and supporting authentication/cluster infrastructure.

## Overview
- Base context: `/nifi-api` served by the NiFi web application (`WEB-INF/web.xml`). All resource classes extend `ApplicationResource`, which handles URI construction, cluster replication, authorization checks, and request validation.
- Default media type is JSON (`application/json`). Some endpoints stream binary (FlowFile content, site-to-site) or text (Prometheus metrics). Use `Accept` headers to request alternate formats when supported.
- Responses wrap payloads in `*Entity` objects containing `revision`, `permissions`, `bulletins`, and a `component` DTO. Updates require optimistic locking via the embedded `revision.version` field.

## Authentication & Session Management
- **JWT Tokens**: `POST /nifi-api/access/token` accepts `application/x-www-form-urlencoded` username/password over HTTPS and returns a JWT (also set as `__Secure-Authorization-Bearer` cookie). `DELETE /nifi-api/access/logout` invalidates tokens; `/access/logout/complete` clears logout cookies and redirects.
- **External Login**: `GET /nifi-api/authentication/configuration` reports whether an external SSO/OIDC/SAML login is required and returns configured login/logout URIs.
- Requests authenticate via `Authorization: Bearer <token>` header or the secure cookie. Certificates/Proxies are supported when NiFi is configured for mutual TLS; proxied identities are processed by `ProxiedEntitiesUtils` in `ApplicationResource`.

## Common Request Patterns
- **Revision Control**: Mutating requests must include a `revision` block with the latest `version`. Server increments the version on success; mismatched versions trigger HTTP 409 (conflict).
- **Client ID & Disconnected Node Overrides**: Many deletion/update calls accept query parameters `clientId` (for logging) and `disconnectedNodeAcknowledged=true` to allow changes while a node is off the cluster.
- **Asynchronous Operations**: Long-running tasks (verification, starting/stopping groups, version change requests, parameter application) create request entities under `/.../requests` and return a request ID. Poll or DELETE the request to monitor/cancel.
- **Cluster Replication**: `ApplicationResource` automatically replicates mutating calls to the cluster coordinator using `RequestReplicator`. Clients typically hit any node; the API fan-outs or proxies to the appropriate node. Node-specific queries accept `nodewise=true` and `clusterNodeId=<uuid>`.
- **Non-Guaranteed Endpoints**: Many administrative endpoints include the `NON_GUARANTEED_ENDPOINT` notice (e.g., tenant/user management). Treat them as subject to change between minor versions.

## Resource Families
- **Access (`/access`) & Authentication (`/authentication`)**: Token issuance, logout flows, and discovery of external authentication endpoints.
- **Resources (`/resources`)**: Lists every secured resource and its URI so UIs can build navigation and highlight unauthorized sections.
- **Tenants (`/tenants`) & Policies (`/policies`)**: CRUD for users, user groups, and access policies. Requires a configurable authorizer; guarded by revision checks and `Write - /tenants`/`/policies` privileges.
- **Flow Composition (`/process-groups`, `/processors`, `/connections`, `/funnels`, `/input-ports`, `/output-ports`, `/labels`, `/snippets`)**:
  - Create, move, copy, and delete components.
  - Update processor configs (`PUT /processors/{id}`), diagnostics, run status (`/processors/{id}/run-status`), and configuration verification requests.
  - Manage process groups, including flow downloads, variable registries, component schedules (start/stop), and emptying connections.
- **Controller Governance (`/controller`, `/controller-services`, `/reporting-tasks`, `/parameter-contexts`, `/parameter-providers`)**:
  - Global controller state (cluster summary, bulletins, history).
  - Enable/disable controller services, analyze configuration, and list available component types.
  - Manage reporting tasks and parameter contexts/providers, including apply-parameters request lifecycles.
- **Version Control (`/versions`)**: Interacts with NiFi Registry—start/stop version tracking, upload/download flow snapshots, and coordinate change request lifecycles via `/versions/active-requests`.
- **Flow Metadata (`/flow`)**:
  - Retrieve about info, banners, current user permissions, search results, process group flows, controller status, bulletins, action history, prioritizer types, and runtime manifest.
  - Exposes Prometheus metrics under `/flow/metrics` (supports `text/plain; version=0.0.4` and JSON depending on writer).
- **Monitoring & Diagnostics**:
  - `/system-diagnostics`: JVM/OS metrics, with optional `nodewise` view.
  - `/counters`: List and reset processor counters.
  - `/flowfile-queues`: Inspect queue load, listing size/backpressure counts.
  - `/provenance` & `/provenance-events`: Query provenance, download content, and view event details; cluster-aware via `clusterNodeId`.
  - `/data-transfer` & `/site-to-site`: Raw content retrieval for queues and site-to-site handshake/peers, used by remote NiFi instances and CLI.
- **Remote Components (`/remote-process-groups`)**: Configure remote NiFi targets, adjust transmission state, and gather channel diagnostics.
- **Versions & Snippets**: `/snippets` persists canvas copies for paste/export; `/versions` handles flow version requests and conflicts.

## Error Handling & Status Codes
- 400: Validation failure or illegal request (e.g., missing property, invalid revision).
- 401: Authentication failed or missing token.
- 403: Authenticated but insufficient privileges for the secured resource.
- 404: Component not found (often due to stale IDs post-flow change).
- 409: Revision conflict or component not in modifiable state (e.g., must stop before changing configuration).
- 503: Node disconnected or cluster coordination issues (ApplicationResource will direct clients to acknowledge via `disconnectedNodeAcknowledged`).

## LLM Answering Tips
- Always mention the `/nifi-api` prefix and resource path when guiding users (e.g., “update a processor with `PUT /nifi-api/processors/{id}` including a matching `revision.version`”).
- For authentication issues, reference `POST /access/token` and remind that HTTPS is mandatory for token issuance. Mention external login flow if `loginSupported` is false.
- When updates fail, suggest fetching the latest entity (`GET`) to copy the `revision` block before retrying the `PUT`/`POST`/`DELETE`.
- For cluster-aware calls (diagnostics, provenance content), include `nodewise` and `clusterNodeId` guidance so clients target a specific node.
- Point bulk operations (start/stop groups, enable services) to `/process-groups/{id}/flow` or `/controller-services/activation` request endpoints, clarifying the asynchronous request/monitor pattern.
- Remind users that many administrative endpoints are flagged “non-guaranteed” and may change; defer to generated Swagger docs for exact schemas if they’re running a specific NiFi build.

## Quick FAQs
1. **Obtain an access token** → `POST /nifi-api/access/token` with form `username`/`password`; send `Authorization: Bearer <token>` on subsequent calls.
2. **List all processors in a group** → `GET /nifi-api/process-groups/{id}/processors` (via FlowResource helper) or inspect the process group flow: `GET /nifi-api/process-groups/{id}`.
3. **Change processor run state** → `PUT /nifi-api/processors/{id}/run-status` with desired state (`RUNNING`, `STOPPED`, `DISABLED`) and current `revision`.
4. **Start/stop an entire group** → `PUT /nifi-api/process-groups/{id}/flow` with a `scheduleComponentsEntity`, then poll the returned request until `complete`.
5. **Query provenance for a FlowFile** → `POST /nifi-api/provenance` with search criteria, poll `/provenance/{id}` to retrieve results, then fetch events under `/provenance-events/{eventId}` (supply `clusterNodeId` if clustered).
