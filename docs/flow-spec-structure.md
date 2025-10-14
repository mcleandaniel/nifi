# Flow Specification Layout Options

Purpose: capture potential directory and file-structure strategies for NiFi automation specs so flows, shared components, and supporting metadata stay easy to discover, maintain, and extend.

We currently keep every YAML flow under `automation/flows/` and deploy directly under the root process group, which won’t scale as the library grows. Below are candidate layouts plus the artefacts we must support beyond processors and controller services.

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
- Decide how flows reference params/controller configs (naming convention, explicit metadata, or manifest file).
- Determine whether subflows stay in shared libraries or co-locate with parent flows.
- Document environment override strategy (e.g., per-env folders, var substitution).
- Align the automation CLI to traverse the chosen structure (plan/deploy commands).

This doc is a living discussion; once a direction is chosen, we can formalize it into schema, tooling expectations, and coding standards.
