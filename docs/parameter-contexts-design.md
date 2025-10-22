# Parameter Contexts — Design, Implementation, and Operations

## Summary
We deploy entire flows from YAML on each update, and do not share a NiFi instance across business units. Every process group (PG) can safely see the same parameter/secret namespace. This enables fully programmatic management of Parameter Contexts (PCs) as part of deploys. This document proposes three strategies, a hybrid algorithm, the REST/CLI implementation plan, and operational guidance (monitoring, rotation, and integration with Vault or a database-backed provider).

## Goals and Constraints
- Single-tenant NiFi: no cross-BU isolation needed inside one instance.
- Full redeploy lifecycle: purge → deploy → validate → enable → start (idempotent runs).
- Programmatic PCs: generated from the flow spec at deploy time.
- Minimize operator toil while keeping a sane blast radius for parameter changes.
- Sensitive values never logged; rely on NiFi’s masking for sensitive parameters.

## Strategies
1) Single “Uber” Parameter Context
- Description: Build one context containing every parameter used by all PGs and assign it to all PGs.
- Pros: simplest to reason about; one place to rotate/override; lowest API churn; easiest for Vault/DB providers.
- Cons: blast radius on change; naming sprawl; weaker least‑privilege.
- Recommended when: small/medium deployments and teams prefer one knob for all environment config.

2) One Parameter Context per PG
- Description: Build a distinct context for each top‑level PG containing only the parameters it uses.
- Pros: strong least‑privilege; scoped blast radius; easier diff per PG; fewer accidental collisions.
- Cons: more objects to manage; duplication when many PGs share common keys; updates repeated across contexts.
- Recommended when: teams want tight separation/ownership or PGs are largely independent.

3) Hybrid (Clustered Contexts)
- Description: Compute parameter sets per PG, cluster similar sets, and produce N contexts covering all PGs. Assign each PG to exactly one cluster context containing the union of its cluster’s parameters.
- Pros: balances sprawl vs. blast radius; reduces duplication; keeps objects manageable.
- Cons: algorithm adds complexity; need stability controls to avoid noisy reassignments.
- Recommended when: many PGs with overlapping parameter sets; desire fewer contexts without a global one.

## Hybrid Algorithm (practical set clustering)
- Inputs: for each PG, the set of parameter names it references (and metadata: sensitive, default source, etc.).
- Similarity: Jaccard similarity on parameter name sets.
- Procedure:
  1. Extract name sets S(PG) from the flow spec (see Detection below).
  2. Greedy clustering: seed clusters with the k largest sets; iteratively assign unassigned PGs to the nearest cluster if similarity ≥ T (e.g., 0.7), else form a new cluster (capped at max_k if desired).
  3. Context composition: for each cluster C, union parameters U(C) = ⋃ S(PG∈C); context name = stable hash of sorted PG names (or a prefix + group tag).
  4. Stability: use sticky assignment — only re-cluster when similarity changes exceed a threshold or a PG adds a new parameter not covered by any existing cluster.
- Outputs: N contexts with their parameter definitions, and a mapping PG→Context.
- Tunables: similarity threshold T, max cluster count k, sticky duration, pin certain PGs to dedicated contexts.

## Detection of Parameter Usage
- Preferred reference: NiFi Parameter references `#{param_name}`.
- Expression Language `${...}` remains supported for attributes/env; do not interpret as PCs unless explicitly configured.
- Extraction sources:
  - Processor properties: scan string values for `#{...}`.
  - Controller service properties: same scan (some will be sensitive).
  - Optional manifest overlays (future): a `parameters:` block per PG for declarative hints and types.

## Parameter Types and Sensitivity
- Sensitivity detection:
  - Use known property descriptors (when available) to mark sensitive keys.
  - Heuristics fallback: keys containing `password`, `secret`, `token`, `key` → sensitive.
- Types: PCs are strings in NiFi; track intended type for validation only (e.g., integer ranges) in our manifest.
- Defaults and sources: permit per‑env `.env` overrides during dev; in production, prefer Vault/DB provider.

## Implementation Plan (REST + CLI)
1) Extract parameter sets from the flow YAML
- Add a parser pass that returns for each top‑level PG: `{ name, params: { key -> { sensitive: bool, default?: str } } }`.
- Merge nested PG usages into the parent PG’s set (one context per top‑level PG assignment).

2) Build the selected strategy
- Single: union of all params → one context.
- Per‑PG: context per PG.
- Hybrid: cluster as described above.

3) Apply to NiFi via REST (idempotent)
- List contexts: GET `/nifi-api/parameter-contexts`.
- Create context: POST `/nifi-api/parameter-contexts` with `{ component: { name, parameters: [{name, value, sensitive}] } }`.
- Update context: PUT `/nifi-api/parameter-contexts/{id}` using revision; or start an update request:
  - POST `/nifi-api/parameter-contexts/{id}/update-requests` with the new set; poll GET until `complete`.
- Assign to PG: PUT `/nifi-api/process-groups/{pgId}` body `{ component: { id: pgId, parameterContext: { id: ctxId } }, revision }`.
- Order of operations:
  - Create or update the contexts first.
  - Assign contexts to PGs.
  - Re-validate the flow (processors will reflect resolved parameters); then enable/start per normal.

4) CLI surfaces (staged)
- Now (Phase 1): integrate into deploy path behind a feature flag (e.g., `--params single|per-pg|hybrid`, default: `single`).
- Planned subcommands:
  - `params plan` → JSON plan of contexts and PG assignments.
  - `params apply` → Create/update contexts, assign to PGs.
  - `params inspect` → Report missing parameters, unused params, sensitive counts.
  - `params rotate` → Rotate one/many parameter values (with opt-in propagation rules).

5) Idempotency and safety
- Never log sensitive values.
- Use revision versions for all updates.
- Avoid deleting contexts during steady-state changes; prefer in-place updates.
- If a context must be removed, unassign from PGs first, then delete.

## Monitoring and Validation
- “Missing parameter” validation: scan deployed bulletins and validationErrors; produce a CLI report of unresolved `#{...}` references.
- Drift detection: compare planned parameter sets vs. NiFi state; flag unknown (stale) and missing keys.
- Metrics: count contexts, sensitive parameter totals, assignment counts per PG; track update durations and failures.
- Alerts: any invalid processor caused by parameter resolution should fail deploy (ExitCode 2) and emit curl reproduction commands for inspection.

## Rotation and Lifecycle
- Rotation flow:
  1. Update source of truth (Vault/DB or our manifest override).
  2. Apply context updates via REST (update request) — NiFi propagates to referencing components.
  3. Optionally restart PG/processors if a specific component requires it (rare with parameters).
- Audit: keep commit history of parameter manifests; avoid putting cleartext secrets in VCS — reference Vault paths instead.

## HashiCorp Vault Integration
Two viable patterns:
- Parameter Provider (preferred where available)
  - Configure the NiFi HashiCorp Vault Parameter Provider (NAR) with Vault address, auth method (token/AppRole), and mapping (path→context parameters).
  - Apply via REST: `/nifi-api/parameter-providers` to run a fetch/apply cycle that (re)creates contexts and parameters.
  - Pros: NiFi pulls secrets; sensitive values never traverse our CLI.
  - Cons: Requires provider NAR and operator configuration; context names/shape driven by provider config.

- External Sync
  - Our CLI queries Vault and updates contexts directly via REST.
  - Pros: works without a provider; greater control per deploy.
  - Cons: CLI handles secrets; ensure ephemeral storage and strict logging hygiene.

Security considerations:
- TLS to Vault; least-privilege tokens (read-only paths); avoid writing secrets to disk.
- For audits: log which keys and contexts changed (never log values).

## Database-backed Parameter Contexts
Patterns:
- Custom Parameter Provider plugin for NiFi that reads from a DB table and creates/updates contexts.
- External sync: our CLI queries the DB (via read-only account), constructs parameter sets, then applies via REST.
- Recommended schema: `parameter_context(name)`, `parameter(context_id, name, sensitive, value_or_ref)`, where `value_or_ref` can hold an external reference (e.g., Vault path) to avoid storing cleartext in DB.

## Default Recommendation
- Default to the single “uber” context, given single-tenancy and fully programmatic deploys.
- Keep a feature flag to switch to per‑PG or hybrid without changing flow YAML.
- Add sticky naming and stable assignments to avoid churn when switching strategies.

## Operational Runbooks
- First-time setup:
  - Choose strategy; set CLI flag.
  - If using Vault/DB providers, coordinate with NiFi admins to install/configure provider NARs.
- On every deploy:
  - Generate parameter plan → apply → assign → deploy flow → validate.
- Triage (on errors):
  - Use `inspect` to list unresolved parameters and emit curl to reproduce state:
    ```bash
    set -a; source .env; set +a
    TOKEN=$(curl -sk -X POST "$NIFI_BASE_URL/access/token" -d "username=$NIFI_USERNAME" -d "password=$NIFI_PASSWORD")
    # list contexts
    curl -sk -H "Authorization: Bearer $TOKEN" "$NIFI_BASE_URL/parameter-contexts" | jq '.parameterContexts[].component | {id,name,parameterCount: (.parameters|length)}'
    # show PG parameter context assignment
    curl -sk -H "Authorization: Bearer $TOKEN" "$NIFI_BASE_URL/process-groups/root" | jq '.component.parameterContext'
    ```

## Future Work
- Add `params` subcommands to the CLI as above.
- Support declarative parameter overlays in flow YAML (types, defaults, sensitivity hints).
- Implement the hybrid clustering (Jaccard-based) with sticky assignment.
- Optional: protect against accidental cleartext by requiring external provider for keys matching sensitive heuristics.

## Appendix — REST Endpoints Quick Reference
- `POST /access/token` — obtain access token.
- `GET /parameter-contexts` — list contexts.
- `POST /parameter-contexts` — create context.
- `PUT /parameter-contexts/{id}` — update context (revision required).
- `POST /parameter-contexts/{id}/update-requests` — submit an update request, then poll `GET` for completion.
- `GET /flow/process-groups/{pgId}` — list PG and its assigned context.
- `PUT /process-groups/{pgId}` — assign `parameterContext` to PG.
- Parameter Providers (if used): `/parameter-providers` (list/apply), provider-specific config endpoints.
