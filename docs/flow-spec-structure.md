# Flow Specification Layout Options

Purpose: capture potential directory and file-structure strategies for NiFi automation specs so flows, shared components, and supporting metadata stay easy to discover, maintain, and extend.

We currently keep every YAML flow under `automation/flows/` and deploy directly under the root process group, which won’t scale as the library grows. Before settling on a directory layout, we need to align on the lifecycle we’re building for and the visibility goals we expect.

## Desired Workflow & Operating Model
- **Design/Build**: teams (or future LLM-based MCP tooling) edit flow specs locally, referencing shared assets (controller services, parameters, subflows) from a well-known library. All changes are treated as redeploy-the-world (idempotent delete + recreate of the target process groups) to avoid drift.
- **Review/Visibility**: support staff and reviewers must be able to trace dependencies—e.g., click a controller service and immediately see all processors/flows referencing it. A metadata companion (potentially stored in a database) should index these relationships for dashboards/search.
- **Deployment**: although multiple teams can develop in parallel, we serialise deployment (one release at a time) to keep automation simple and avoid NiFi revision conflicts. The directory structure should make it easy to bundle the exact artefacts for a single deployment.
- **Tooling Alignment**: the future MCP/automation should understand the hierarchy so it can generate, validate, and deploy flows consistently. Each flow module likely needs a manifest describing included components and dependencies.

## Questions to Address
- Where do we store metadata/manifests that describe dependencies (e.g., which processors reference which controller services)?
- How do we trace references across shared assets? (Database or generated index from spec files.)
- When should controller services live at the root vs. child groups, and how do we represent overrides in specs? (Root = global reuse, child = group-specific configuration, override = child defines a service with same logical role but different config.)
- (Updated) Controller services now live exclusively at the root process group and are described in a manifest that automation manages; flows only reference these services by key.
- How do we package parameter contexts and ensure environment overrides are transparent?
- What should the support experience look like? (e.g., UI/portal listing flows, controllers, dependencies.)

These questions influence the preferred layout below.

## Common Artefacts to Organize
- **Flows / Process Groups**: top-level and nested flow definitions.
- **Parameter Contexts**: reusable environment-specific parameters (`.yaml` or `.json`).
- **Controller Service Configurations**: shared service definitions (JDBC, lookup services, SSL, etc.).
- **Reusable Subflows / Templates**: smaller fragments intended for composition.
- **Metadata / Documentation**: README files, schema definitions, migration notes.
- **Test Fixtures**: sample inputs, expected outputs, integration-test specs.

Any chosen hierarchy should make these artefacts discoverable and reduce duplication.

## Option A – Component-Centric Tree
```
automation/
  flows/
    root/
      data-platform/
        ingest/
          flow.yaml            # main PG definition
          params.yaml          # parameter context
          controllers/         # controller service configs (e.g., dbcp.yaml)
          subflows/            # reusable nested PGs
          tests/               # integration/unit specs
        enrich/
          ...
    shared/
      controllers/
        jdbc-pools/
        ssl-contexts/
      param-contexts/
      subflows/
```

**Pros**
- Mirrors NiFi’s PG hierarchy → easier mental mapping.
- Keeps environment-specific pieces (params/controllers) next to their flow.
- `shared/` folder centralizes reusable assets.

**Cons**
- Deep paths if hierarchy is large.
- Harder to list “all flows” in one place without tooling.

**Best when** teams own dedicated branches of the flow tree and reuse shared assets heavily.

## Option B – Role-Based Buckets
```
automation/
  flows/
    ingest/
      kafka-to-hdfs/
      rest-to-s3/
    transform/
    publish/
  params/
    dev/
    test/
    prod/
  controllers/
    dev/
    shared/
  subflows/
  docs/
    flow-index.md
```

**Pros**
- Clear top-level buckets by flow function.
- Parameter contexts and controller services separated by environment, encouraging reuse via symlinks or references.
- Simplifies population scripts (iterate `flows/**/flow.yaml`).

**Cons**
- Relationship between a flow and its parameter/controller definitions needs metadata (e.g., naming conventions) or cross references.
- Subflows live separately from the flow using them; requires disciplined referencing.

**Best when** flows are categorized by purpose and environments are managed centrally.

## Option C – Package Bundles (Flow Modules)
Treat each deliverable flow as a self-contained module.
```
automation/
  modules/
    customer-onboarding/
      flow.yaml
      params/
        dev.yaml
        prod.yaml
      controllers/
        lookup-service.yaml
      subflows/
        sanitize-customer-data.yaml
      README.md
      tests/
        integration.yaml
    order-pipeline/
      ...
  shared/
    subflows/
    controllers/
    params/
```

**Pros**
- Easy handoff/deployment: everything needed to deploy a flow lives in one folder.
- Simplifies versioning and templating per module.
- `shared/` directory hosts truly global assets.

**Cons**
- Duplicates shared services/params unless references are explicit.
- Need conventions for declaring dependencies on `shared` assets.

**Best when** flows are versioned/owned independently and packaged like modules.

## Next Steps
- Decide where metadata manifests live (per module vs global index) and how MCP tooling updates them.
- Finalise the controller-service manifest schema (keys, names, properties, UUIDs) and integrate it as the single source of truth.
- Agree on environment override strategy (parameter contexts, per-env directories, or templating).
- Align automation/CLI tooling to traverse the chosen structure (plan/deploy commands, dependency indexer).
- Prototype the dependency database/index (controllers ↔ processors) to validate support workflows.

This doc is a living discussion; once a direction is chosen, we can formalize it into schema, tooling expectations, UI/knowledge base integration, and coding standards.

### Controller Service Manifest Direction
- All controller services are provisioned at the NiFi root before any flows or sub process groups are deployed.
- A JSON manifest (e.g., `automation/manifest/controller-services.json`) captures each service’s logical key, NiFi type, desired properties, auto-enable flag, and the last known NiFi UUID.
- Deployment tooling loads the manifest, reconciles/create services at the root, updates the manifest with fresh UUIDs, and then injects the resolved IDs into processor properties as flows are instantiated.
- Flows no longer declare controller services inline; they reference the manifest keys instead.
