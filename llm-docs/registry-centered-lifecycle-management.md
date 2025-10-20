---
title: Registry-Centered Lifecycle Management
scope: project
plan_id: project
topic_id: project_project-registry-lifecycle-integration
category: lifecycle
priority: high
tags: [registry, lifecycle, versioning]
claims:
  - id: claim-registry-supports-versioned-flows
    sources:
      - src: src-nifi-registry-user-guide
        locator: "L22-L26"
  - id: claim-terminology-definitions
    sources:
      - src: src-nifi-registry-user-guide
        locator: "L54-L62"
  - id: claim-registry-ui-default-address
    sources:
      - src: src-nifi-registry-user-guide
        locator: "L70-L71"
  - id: claim-nifi-versioning-scope
    sources:
      - src: src-nifi-user-guide
        locator: "L2544-L2546"
  - id: claim-nifi-connect-registry-client
    sources:
      - src: src-nifi-user-guide
        locator: "L2549-L2555"
  - id: claim-versioned-flows-in-buckets
    sources:
      - src: src-nifi-user-guide
        locator: "L2575-L2575"
  - id: claim-bucket-policies-permissions
    sources:
      - src: src-nifi-registry-user-guide
        locator: "L255-L265"
  - id: claim-version-states
    sources:
      - src: src-nifi-user-guide
        locator: "L2578-L2594"
  - id: claim-version-state-display
    sources:
      - src: src-nifi-user-guide
        locator: "L2596-L2602"
  - id: claim-import-versioned-flow
    sources:
      - src: src-nifi-user-guide
        locator: "L2610-L2619"
  - id: claim-start-version-control
    sources:
      - src: src-nifi-user-guide
        locator: "L2630-L2636"
  - id: claim-root-pg-not-versioned
    sources:
      - src: src-nifi-user-guide
        locator: "L2644-L2644"
  - id: claim-commit-local-changes
    sources:
      - src: src-nifi-user-guide
        locator: "L2684-L2689"
  - id: claim-change-version-rollback
    sources:
      - src: src-nifi-user-guide
        locator: "L2691-L2706"
  - id: claim-sensitive-parameters-not-sent
    sources:
      - src: src-nifi-user-guide
        locator: "L1044-L1046"
  - id: claim-download-flow-definition-cli
    sources:
      - src: src-nifi-user-guide
        locator: "L378-L385"
  - id: claim-cli-admin-overview
    sources:
      - src: src-nifi-admin-guide
        locator: "L1904-L1910"
  - id: claim-cli-overview
    sources:
      - src: src-nifi-toolkit-guide
        locator: "L40-L57"
  - id: claim-cli-command-list-nifi
    sources:
      - src: src-nifi-toolkit-guide
        locator: "L58-L99"
  - id: claim-cli-command-list-registry
    sources:
      - src: src-nifi-toolkit-guide
        locator: "L156-L169"
  - id: claim-cli-properties-and-session
    sources:
      - src: src-nifi-toolkit-guide
        locator: "L206-L257"
  - id: claim-cli-pg-import-example
    sources:
      - src: src-nifi-toolkit-guide
        locator: "L402-L408"
  - id: claim-registry-export-all-flows
    sources:
      - src: src-nifi-toolkit-guide
        locator: "L444-L453"
  - id: claim-registry-import-all-flows
    sources:
      - src: src-nifi-toolkit-guide
        locator: "L455-L469"
  - id: claim-registry-delete-warning
    sources:
      - src: src-nifi-registry-user-guide
        locator: "L166-L178"
sources:
  - id: src-nifi-registry-user-guide
    title: Apache NiFi Registry User Guide
    path: nifi-registry/nifi-registry-core/nifi-registry-docs/src/main/asciidoc/user-guide.adoc
  - id: src-nifi-user-guide
    title: Apache NiFi User Guide
    path: nifi-docs/src/main/asciidoc/user-guide.adoc
  - id: src-nifi-admin-guide
    title: Apache NiFi Administration Guide
    path: nifi-docs/src/main/asciidoc/administration-guide.adoc
  - id: src-nifi-toolkit-guide
    title: Apache NiFi Toolkit Guide
    path: nifi-docs/src/main/asciidoc/toolkit-guide.adoc
---

# Registry-Centered Lifecycle Management

## Introduction / Overview

<span id="claim-registry-supports-versioned-flows">NiFi Registry provides centralized storage and management for shared resources and supports versioned flows created at the NiFi process-group level.</span>

<span id="claim-terminology-definitions">Key terms: a Flow is a versioned NiFi process group; a Bucket organizes versioned items; a Policy defines permissions.</span>

<span id="claim-registry-ui-default-address">The default NiFi Registry UI address is `http://<hostname>:18080/nifi-registry`.</span>

<span id="claim-nifi-versioning-scope">When connected to a NiFi Registry, NiFi can place dataflows under version control at the process-group level.</span>


## Concepts / Architecture

<span id="claim-nifi-connect-registry-client">NiFi connects to a Registry by adding a Registry Client in Controller Settings (Global Menu → Registry Clients → “+”).</span>

<span id="claim-versioned-flows-in-buckets">Versioned flows are stored and organized in Registry buckets.</span> <span id="claim-bucket-policies-permissions">Bucket Policies govern which users may import flows, commit changes, view buckets, and delete flows across Registry and NiFi.</span>

<span id="claim-version-states">A versioned process group has the following states: Up to date, Locally modified, Stale, Locally modified and stale, and Sync failure.</span> <span id="claim-version-state-display">These states appear next to the process group name, at the bottom of groups for contained flows, and in the Status Bar for the root process group.</span>

<span id="claim-sensitive-parameters-not-sent">Sensitive Parameter values are not sent to the Registry when versioning; only the fact that a sensitive Parameter is referenced is recorded.</span>


## Implementation / Configuration

<span id="claim-import-versioned-flow">When NiFi is connected to a Registry, the Add Process Group dialog shows an Import link that allows selecting a Registry, Bucket, Flow, and Version to place a versioned flow on the canvas.</span>

<span id="claim-start-version-control">To begin tracking changes, right-click a process group and select Version → Start version control, then choose the Registry and Bucket and provide a flow name.</span> <span id="claim-root-pg-not-versioned">The root process group cannot be placed under version control.</span>

<span id="claim-commit-local-changes">Commit local changes with Version → Commit local changes; commits are blocked if the modified version is not the latest (Locally modified and stale).</span>

<span id="claim-change-version-rollback">Change the deployed version with Version → Change version; this supports upgrading to newer versions or rolling back to older versions (after reverting local changes).</span>

<span id="claim-download-flow-definition-cli">From any process group, you can Download flow definition (JSON) and import it into NiFi Registry using the NiFi CLI.</span>


## Usage / Examples

### CLI foundations

<span id="claim-cli-admin-overview">The NiFi Toolkit includes a `cli` for automating NiFi and NiFi Registry tasks, including deploying versioned flows.</span> <span id="claim-cli-overview">The CLI supports standalone and interactive modes with `./bin/cli.sh`, and provides help with `-h`.</span>

<span id="claim-cli-command-list-nifi">Relevant NiFi commands include `nifi pg-import`, `nifi pg-get-version`, and `nifi pg-change-version`.</span> <span id="claim-cli-command-list-registry">Registry commands include `registry list-buckets`, `registry list-flows`, `registry list-flow-versions`, `registry export-flow-version`, and `registry import-flow-version`.</span>

<span id="claim-cli-properties-and-session">Avoid repeating URLs and TLS options by using properties files and the CLI session: define `baseUrl=...` in a properties file and set defaults with `session set nifi.props` and `session set nifi.reg.props`.</span>

Example: prepare per-environment CLI properties and set defaults without manual environment variables.

```bash
# Load optional environment file if present (auto-load credentials/URLs)
[ -f .env ] && source .env

# Write NiFi Registry CLI properties from env or defaults
cat > ./nifi-registry.dev.properties <<PROPS
baseUrl=${REGISTRY_URL:-http://localhost:18080}
keystore=${REGISTRY_KEYSTORE:-}
keystoreType=${REGISTRY_KEYSTORE_TYPE:-}
keystorePasswd=${REGISTRY_KEYSTORE_PASSWD:-}
keyPasswd=${REGISTRY_KEY_PASSWD:-}
truststore=${REGISTRY_TRUSTSTORE:-}
truststoreType=${REGISTRY_TRUSTSTORE_TYPE:-}
truststorePasswd=${REGISTRY_TRUSTSTORE_PASSWD:-}
proxiedEntity=${REGISTRY_PROXIED_ENTITY:-}
PROPS

# Write NiFi CLI properties similarly
cat > ./nifi.dev.properties <<PROPS
baseUrl=${NIFI_URL:-http://localhost:8080}
keystore=${NIFI_KEYSTORE:-}
keystoreType=${NIFI_KEYSTORE_TYPE:-}
keystorePasswd=${NIFI_KEYSTORE_PASSWD:-}
keyPasswd=${NIFI_KEY_PASSWD:-}
truststore=${NIFI_TRUSTSTORE:-}
truststoreType=${NIFI_TRUSTSTORE_TYPE:-}
truststorePasswd=${NIFI_TRUSTSTORE_PASSWD:-}
proxiedEntity=${NIFI_PROXIED_ENTITY:-}
PROPS

# Persist as defaults in CLI session (no need to pass -u/-p repeatedly)
./bin/cli.sh session set nifi.reg.props "$PWD/nifi-registry.dev.properties"
./bin/cli.sh session set nifi.props "$PWD/nifi.dev.properties"
```

### Promote a versioned flow (Dev → Test → Prod)

1) Discover bucket/flow/version in the source Registry (interactive shell recommended):

```bash
./bin/cli.sh   # enter interactive mode

# List buckets; take note of position index (e.g., 1)
registry list-buckets

# List flows in the chosen bucket using positional back-reference (&1)
registry list-flows -b &1

# List versions for the chosen flow using back-reference (&1)
registry list-flow-versions -f &1
```

<span id="claim-cli-pg-import-example">Deploy a specific flow version to NiFi using back-references, avoiding manual IDs:</span>

```bash
# Import version 1 of the selected flow into NiFi (process group created under root)
nifi pg-import -b &1 -f &1 -fv 1
```

2) Commit and version changes in Dev:

- Make edits in NiFi under the versioned process group, then use Version → Commit local changes.

3) Roll forward or roll back in higher environments:

- Use the NiFi UI on the target to select Version → Change version for the process group and pick the desired version (revert local changes first if required).

4) Bulk-promote all flows between Registries (for synchronized lower→upper env replication):

<span id="claim-registry-export-all-flows">Use `registry export-all-flows` to export every bucket/flow/version to a directory.</span> <span id="claim-registry-import-all-flows">Then use `registry import-all-flows` to create buckets/flows and import all versions in the target Registry (optionally `--skipExisting`).</span>

```bash
# Export from Dev Registry
./bin/cli.sh registry export-all-flows --outputDirectory "$PWD/flow_exports"

# Import into Test/Prod Registry (idempotent with --skipExisting)
./bin/cli.sh registry import-all-flows --input "$PWD/flow_exports" --skipExisting
```


## Best Practices / Tips

- Secrets and Parameters: <span id="claim-sensitive-parameters-not-sent">Use sensitive Parameters so secrets are not stored in the Registry; only references are versioned.</span>
- Scoping: <span id="claim-nifi-versioning-scope">Version control applies at the process-group level.</span>
- Governance: <span id="claim-bucket-policies-permissions">Use Bucket Policies to separate read/import vs. write/commit vs. delete actions across teams and environments.</span>
- Version hygiene: Revert local changes before switching versions to keep promotion deterministic.
- Change tracking: Prefer smaller, frequent commits with comments for clear flow history in the Registry.


## Troubleshooting

- State indicators: <span id="claim-version-states">Check the process group’s version state (Up to date, Locally modified, Stale, Locally modified and stale, Sync failure) to understand what action is needed.</span> <span id="claim-version-state-display">States appear inline on groups and in the Status Bar/Summary.</span>
- Commit blocked: <span id="claim-commit-local-changes">NiFi blocks commits if the edited version is not the latest; update or revert first.</span>
- Rollback: <span id="claim-change-version-rollback">Use Change version to roll back to a prior version; revert local changes before switching.</span>
- Registry deletion: <span id="claim-registry-delete-warning">It is possible to delete a flow in Registry that is still in use by NiFi; protect buckets with appropriate policies.</span>


## Reference / Related Docs

- <span id="claim-cli-admin-overview">NiFi Toolkit Administrative Tools overview (CLI for NiFi and Registry)</span>
- <span id="claim-cli-overview">NiFi Toolkit Guide — CLI usage, standalone/interactive, help</span>
- <span id="claim-cli-command-list-nifi">NiFi Toolkit Guide — NiFi command list (pg-import, pg-change-version, etc.)</span>
- <span id="claim-cli-command-list-registry">NiFi Toolkit Guide — Registry command list (list-buckets, list-flows, import/export flow version, etc.)</span>
- <span id="claim-cli-properties-and-session">NiFi Toolkit Guide — properties files and session defaults (`session set nifi.props`, `session set nifi.reg.props`)</span>
- <span id="claim-registry-supports-versioned-flows">NiFi Registry User Guide — introduction to versioned flows</span>
- <span id="claim-terminology-definitions">NiFi Registry User Guide — terminology: Flow, Bucket, Policy</span>
- <span id="claim-nifi-connect-registry-client">NiFi User Guide — connecting NiFi to a Registry Client</span>
- <span id="claim-import-versioned-flow">NiFi User Guide — importing versioned flows</span>
- <span id="claim-start-version-control">NiFi User Guide — starting version control</span>
- <span id="claim-root-pg-not-versioned">NiFi User Guide — root process group cannot be versioned</span>
- <span id="claim-commit-local-changes">NiFi User Guide — commit local changes behavior</span>
- <span id="claim-change-version-rollback">NiFi User Guide — change version and rollback</span>
- <span id="claim-download-flow-definition-cli">NiFi User Guide — download flow definition (import via CLI)</span>
