---
claims:
  claim-overview-positional:
    sources:
      - source-commandprocessor-backref
      - source-toolkit-guide-backref
  claim-resolution-pipeline:
    sources:
      - source-commandprocessor-backref
  claim-feedback:
    sources:
      - source-commandprocessor-backref
      - source-toolkit-guide-backref
  claim-persistence:
    sources:
      - source-commandprocessor-holder
      - source-toolkit-guide-backref
  claim-referenceable-pattern:
    sources:
      - source-buckets-result
      - source-processgroups-result
  claim-buckets-support:
    sources:
      - source-list-buckets
      - source-buckets-result
  claim-flows-support:
    sources:
      - source-list-flows
      - source-versioned-flows-result
  claim-param-contexts-support:
    sources:
      - source-list-param-contexts
      - source-param-contexts-result
  claim-pg-list-support:
    sources:
      - source-pg-list
      - source-processgroups-result
  claim-help-produces:
    sources:
      - source-toolkit-guide-backref
  claim-session-example:
    sources:
      - source-toolkit-guide-backref
  claim-troubleshooting:
    sources:
      - source-commandprocessor-backref
  claim-reference-docs:
    sources:
      - source-toolkit-guide-backref
sources:
  - id: source-toolkit-guide-backref
    title: "Apache NiFi Toolkit Guide – Back-Referencing"
    href: nifi-docs/src/main/asciidoc/toolkit-guide.adoc
    locator: L367-L409
  - id: source-commandprocessor-backref
    title: "CommandProcessor.java – back-reference resolution"
    href: nifi-toolkit/nifi-toolkit-cli/src/main/java/org/apache/nifi/toolkit/cli/impl/command/CommandProcessor.java
    locator: L86-L160
  - id: source-commandprocessor-holder
    title: "CommandProcessor.java – resolver persistence"
    href: nifi-toolkit/nifi-toolkit-cli/src/main/java/org/apache/nifi/toolkit/cli/impl/command/CommandProcessor.java
    locator: L255-L264
  - id: source-list-buckets
    title: "ListBuckets.java"
    href: nifi-toolkit/nifi-toolkit-cli/src/main/java/org/apache/nifi/toolkit/cli/impl/command/registry/bucket/ListBuckets.java
    locator: L32-L48
  - id: source-buckets-result
    title: "BucketsResult.java"
    href: nifi-toolkit/nifi-toolkit-cli/src/main/java/org/apache/nifi/toolkit/cli/impl/result/registry/BucketsResult.java
    locator: L42-L103
  - id: source-list-flows
    title: "ListFlows.java"
    href: nifi-toolkit/nifi-toolkit-cli/src/main/java/org/apache/nifi/toolkit/cli/impl/command/registry/flow/ListFlows.java
    locator: L36-L60
  - id: source-versioned-flows-result
    title: "VersionedFlowsResult.java"
    href: nifi-toolkit/nifi-toolkit-cli/src/main/java/org/apache/nifi/toolkit/cli/impl/result/registry/VersionedFlowsResult.java
    locator: L42-L107
  - id: source-list-param-contexts
    title: "ListParamContexts.java"
    href: nifi-toolkit/nifi-toolkit-cli/src/main/java/org/apache/nifi/toolkit/cli/impl/command/nifi/params/ListParamContexts.java
    locator: L31-L47
  - id: source-param-contexts-result
    title: "ParamContextsResult.java"
    href: nifi-toolkit/nifi-toolkit-cli/src/main/java/org/apache/nifi/toolkit/cli/impl/result/nifi/ParamContextsResult.java
    locator: L45-L122
  - id: source-pg-list
    title: "PGList.java"
    href: nifi-toolkit/nifi-toolkit-cli/src/main/java/org/apache/nifi/toolkit/cli/impl/command/nifi/pg/PGList.java
    locator: L40-L99
  - id: source-processgroups-result
    title: "ProcessGroupsResult.java"
    href: nifi-toolkit/nifi-toolkit-cli/src/main/java/org/apache/nifi/toolkit/cli/impl/result/nifi/ProcessGroupsResult.java
    locator: L42-L110
---
# Back-Referencing Mechanics

## Introduction / Overview
<span id="claim-overview-positional">Interactive NiFi Toolkit CLI sessions let you reuse identifiers from the previous command by substituting `&` plus the row number—such as `&1`—into subsequent arguments.</span>

## Concepts / Architecture
<span id="claim-resolution-pipeline">Before parsing a command line, the CLI scans each argument for the `&` back-reference indicator and replaces matched positions using the active `ReferenceResolver`.</span>
<span id="claim-feedback">When a reference resolves in interactive mode, the shell prints `Using a positional back-reference` alongside the resolved display name so you can confirm what was substituted.</span>
<span id="claim-persistence">The CLI retains the last non-empty `ReferenceResolver`, allowing you to reuse results when the next command does not produce fresh back-references.</span>
<span id="claim-referenceable-pattern">Result classes such as `BucketsResult` and `ProcessGroupsResult` implement `Referenceable` to map every printed row to a numbered `ResolvedReference` entry.</span>

## Implementation / Configuration
<span id="claim-buckets-support">The `registry list-buckets` command retrieves bucket metadata and indexes each row so a token like `&1` resolves to the selected bucket identifier.</span>
<span id="claim-flows-support">The `registry list-flows` command requires a bucket argument, resolves `&n` values for that option, and exposes each returned flow so later commands can reference either the flow ID or its bucket ID from the same position.</span>
<span id="claim-param-contexts-support">The `nifi list-param-contexts` command loads available parameter contexts and stores each name/ID pair for positional reuse.</span>
<span id="claim-pg-list-support">The `nifi pg-list` command enumerates child process groups and records each group's name and identifier for back-referencing.</span>

## Usage / Examples
<span id="claim-session-example">A typical workflow chains registry and NiFi commands—`list-buckets`, `list-flows`, `list-flow-versions`, and `pg-import`—while reusing results from earlier steps.</span>

```shell
#> registry list-buckets
#   Name           Id                                     Description
-   ------------   ------------------------------------   -----------
1   My Bucket      3c7b7467-0012-4d8f-a918-6aa42b6b9d39   (empty)

#> registry list-flows -b &1
Using a positional back-reference for 'My Bucket'
#   Name      Id                                     Description
-   -------   ------------------------------------   ----------------
1   My Flow   06acb207-d2f1-447f-85ed-9b8672fe6d30   This is my flow.

#> registry list-flow-versions -f &1
Using a positional back-reference for 'My Flow'
Ver   Date                         Author                     Message
---   --------------------------   ------------------------   -------------------------------------
1     Tue, Jan 23 2018 09:48 EST   anonymous                  This is the first version of my flow.

#> nifi pg-import -b &1 -f &1 -fv 1
Using a positional back-reference for 'My Bucket'
Using a positional back-reference for 'My Flow'
9bd157d4-0161-1000-b946-c1f9b1832efd
```

## Best Practices / Tips
<span id="claim-help-produces">Check a command’s help output for the `PRODUCES BACK-REFERENCES` marker before relying on positional tokens.</span>

## Troubleshooting
<span id="claim-troubleshooting">If a back-reference cannot be resolved, the CLI leaves the argument unchanged so the command treats `&n` as a literal—indicating you need to refresh the resolver with a compatible list command.</span>

## Reference / Related Docs
<span id="claim-reference-docs">Consult the NiFi Toolkit Guide’s back-referencing section for additional context and examples.</span>
