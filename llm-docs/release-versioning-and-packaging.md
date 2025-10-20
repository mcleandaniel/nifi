---
title: Release Versioning and Packaging Process
description: End-to-end overview of NiFi version bump workflow, manifest generation, and assembly validation before publishing.
tags: [release, versioning, packaging]
topic_id: project_project-release-versioning
plan_id: project
claims:
  - id: claim-root-version-current
    sources:
      - source: src-root-pom
        locator: "pom.xml:L22"
  - id: claim-root-modules-include-assembly-and-manifest
    sources:
      - source: src-root-pom
        locator: "pom.xml:L25-L47"
  - id: claim-assembly-parent-version
    sources:
      - source: src-assembly-pom
        locator: "nifi-assembly/pom.xml:L14-L19"
  - id: claim-assembly-unpack-nar-docs
    sources:
      - source: src-assembly-pom
        locator: "nifi-assembly/pom.xml:L24-L42"
  - id: claim-assembly-base-directory
    sources:
      - source: src-assembly-dependencies-descriptor
        locator: "nifi-assembly/src/main/assembly/dependencies.xml:L19"
  - id: claim-assembly-formats-dir-zip
    sources:
      - source: src-assembly-pom
        locator: "nifi-assembly/pom.xml:L63-L70"
  - id: claim-manifests-assembly-base
    sources:
      - source: src-assembly-manifests-descriptor
        locator: "nifi-assembly/src/main/assembly/extension-manifests.xml:L16-L20"
  - id: claim-manifests-assembly-attached
    sources:
      - source: src-assembly-pom
        locator: "nifi-assembly/pom.xml:L74-L95"
  - id: claim-runtime-unpack-manifests-zip
    sources:
      - source: src-runtime-manifest-pom
        locator: "nifi-manifest/nifi-runtime-manifest/pom.xml:L68-L102"
  - id: claim-runtime-generator-exec-config
    sources:
      - source: src-runtime-manifest-pom
        locator: "nifi-manifest/nifi-runtime-manifest/pom.xml:L104-L125"
  - id: claim-runtime-build-properties-fields
    sources:
      - source: src-runtime-generator
        locator: "nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/RuntimeManifestGenerator.java:L56-L62"
  - id: claim-runtime-writes-json
    sources:
      - source: src-runtime-generator
        locator: "nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/RuntimeManifestGenerator.java:L113-L116"
  - id: claim-runtime-sets-type-nifi
    sources:
      - source: src-runtime-generator
        locator: "nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/RuntimeManifestGenerator.java:L104-L111"
  - id: claim-directory-provider-locations
    sources:
      - source: src-directory-extension-provider
        locator: "nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/DirectoryExtensionManifestProvider.java:L71"
      - source: src-directory-extension-provider
        locator: "nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/DirectoryExtensionManifestProvider.java:L99-L121"
  - id: claim-runtime-manifest-structure-fields
    sources:
      - source: src-c2-runtime-manifest
        locator: "c2/c2-protocol/c2-protocol-component-api/src/main/java/org/apache/nifi/c2/protocol/component/api/RuntimeManifest.java:L30-L35"
  - id: claim-buildinfo-structure-fields
    sources:
      - source: src-c2-build-info
        locator: "c2/c2-protocol/c2-protocol-component-api/src/main/java/org/apache/nifi/c2/protocol/component/api/BuildInfo.java:L27-L32"
  - id: claim-component-manifest-structure
    sources:
      - source: src-c2-component-manifest
        locator: "c2/c2-protocol/c2-protocol-component-api/src/main/java/org/apache/nifi/c2/protocol/component/api/ComponentManifest.java:L29-L34"
  - id: claim-scheduling-defaults-values
    sources:
      - source: src-scheduling-defaults-factory
        locator: "nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/SchedulingDefaultsFactory.java:L37-L44"
  - id: claim-builder-default-penalty-yield-bulletin
    sources:
      - source: src-standard-runtime-builder
        locator: "nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/StandardRuntimeManifestBuilder.java:L83-L85"
  - id: claim-runtime-it-json-path
    sources:
      - source: src-runtime-manifest-it
        locator: "nifi-manifest/nifi-runtime-manifest-test/src/test/java/org/apache/nifi/runtime/manifest/RuntimeManifestIT.java:L57"
  - id: claim-runtime-it-scheduling-asserts
    sources:
      - source: src-runtime-manifest-it
        locator: "nifi-manifest/nifi-runtime-manifest-test/src/test/java/org/apache/nifi/runtime/manifest/RuntimeManifestIT.java:L72-L85"
  - id: claim-enforcer-require-release-deps
    sources:
      - source: src-root-pom
        locator: "pom.xml:L921-L929"
  - id: claim-enforcer-maven-version
    sources:
      - source: src-root-pom
        locator: "pom.xml:L918-L919"
  - id: claim-java-21-min-build
    sources:
      - source: src-root-pom
        locator: "pom.xml:L105-L107"
      - source: src-assembly-readme
        locator: "nifi-assembly/README.md:L70-L71"
  - id: claim-targz-profile
    sources:
      - source: src-assembly-pom
        locator: "nifi-assembly/pom.xml:L1036-L1067"
sources:
  - id: src-root-pom
    url: pom.xml
  - id: src-assembly-pom
    url: nifi-assembly/pom.xml
  - id: src-assembly-dependencies-descriptor
    url: nifi-assembly/src/main/assembly/dependencies.xml
  - id: src-assembly-manifests-descriptor
    url: nifi-assembly/src/main/assembly/extension-manifests.xml
  - id: src-runtime-manifest-pom
    url: nifi-manifest/nifi-runtime-manifest/pom.xml
  - id: src-runtime-generator
    url: nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/RuntimeManifestGenerator.java
  - id: src-directory-extension-provider
    url: nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/DirectoryExtensionManifestProvider.java
  - id: src-c2-runtime-manifest
    url: c2/c2-protocol/c2-protocol-component-api/src/main/java/org/apache/nifi/c2/protocol/component/api/RuntimeManifest.java
  - id: src-c2-build-info
    url: c2/c2-protocol/c2-protocol-component-api/src/main/java/org/apache/nifi/c2/protocol/component/api/BuildInfo.java
  - id: src-c2-component-manifest
    url: c2/c2-protocol/c2-protocol-component-api/src/main/java/org/apache/nifi/c2/protocol/component/api/ComponentManifest.java
  - id: src-scheduling-defaults-factory
    url: nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/SchedulingDefaultsFactory.java
  - id: src-standard-runtime-builder
    url: nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/StandardRuntimeManifestBuilder.java
  - id: src-runtime-manifest-it
    url: nifi-manifest/nifi-runtime-manifest-test/src/test/java/org/apache/nifi/runtime/manifest/RuntimeManifestIT.java
  - id: src-assembly-readme
    url: nifi-assembly/README.md
---

# Release Versioning and Packaging Process

## Introduction / Overview
- <span id="claim-root-version-current">NiFi defines the project version in the root `pom.xml`.</span>
- <span id="claim-root-modules-include-assembly-and-manifest">The root POM lists `nifi-assembly` and `nifi-manifest` as modules.</span>
- <span id="claim-assembly-base-directory">The binary distribution is assembled under a base directory named `nifi-${project.version}`.</span>
- <span id="claim-manifests-assembly-base">An additional assembly packages all extension manifests under a base directory named `nifi-manifests`.</span>

## Concepts / Architecture
- <span id="claim-assembly-unpack-nar-docs">Assembly extracts each NAR’s documentation into `target/extension-manifests` during `prepare-package`.</span>
- <span id="claim-manifests-assembly-attached">The manifests ZIP is attached as an additional assembly artifact.</span>
- <span id="claim-runtime-unpack-manifests-zip">The `nifi-runtime-manifest` module unpacks the manifests ZIP for downstream processing.</span>
- <span id="claim-runtime-generator-exec-config">A build-time Java runner generates a runtime manifest JSON with identifier, version, type, build info, and bundles.</span>
- <span id="claim-directory-provider-locations">Manifests are read from `META-INF/docs/extension-manifest.xml` and optional `META-INF/docs/additional-details/.../additionalDetails.md`.</span>

## Implementation / Configuration
- <span id="claim-assembly-parent-version">`nifi-assembly` inherits the parent `nifi` POM version.</span>
- <span id="claim-assembly-formats-dir-zip">The assembly builds `dir` and `zip` distributions for the binary.</span>
- <span id="claim-targz-profile">Profile `targz` switches the distribution format to `tar.gz`.</span>
- <span id="claim-runtime-build-properties-fields">Runtime manifest generation uses build properties including project version, revision, timestamp, and JDK details.</span>
- <span id="claim-runtime-sets-type-nifi">The generated manifest sets the runtime type to `nifi`.</span>
- <span id="claim-runtime-writes-json">The manifest is serialized to a JSON file in the build output.</span>

## Usage / Examples

Version bump (project-wide) using the declared Versions Plugin:

```bash
#!/usr/bin/env bash
set -euo pipefail
NEW="2.7.0"   # example

mvn -q -DgenerateBackupPoms=false -DprocessAllModules versions:set -DnewVersion="${NEW}" 

# Optional: re-run to update any child module parents
mvn -q -DgenerateBackupPoms=false -DprocessAllModules versions:commit
```

Build binary distribution and manifests ZIP:

```bash
# Build default dir+zip assemblies
mvn -pl nifi-assembly -am -DskipTests package

# Build tar.gz via profile
mvn -pl nifi-assembly -am -DskipTests -P targz package
```

Generate the runtime manifest JSON and docs tree:

```bash
mvn -pl nifi-manifest/nifi-runtime-manifest -am -DskipTests package

# Inspect generated files
ls -la nifi-manifest/nifi-runtime-manifest/target/classes | grep -E 'build.properties|nifi-runtime-manifest.json'
```

Validate manifest content with integration tests:

```bash
mvn -pl nifi-manifest/nifi-runtime-manifest-test -am test
```

Release pre-checks (enforcer rules active during `verify`):

```bash
mvn -DskipTests -Denforcer.skip=false verify
```

## Best Practices / Tips
- <span id="claim-enforcer-require-release-deps">Ensure external dependencies are non-SNAPSHOT; Enforcer `requireReleaseDeps` excludes NiFi org artifacts from this rule.</span>
- <span id="claim-enforcer-maven-version">Use Maven `3.9.11` or later to satisfy the build enforcer.</span>
- <span id="claim-java-21-min-build">Build with Java 21 as required by the project.</span>

## Troubleshooting
- <span id="claim-runtime-it-json-path">If tests cannot find `nifi-runtime-manifest.json`, confirm the generator ran and wrote to the expected path.</span>
- <span id="claim-runtime-it-scheduling-asserts">If scheduling defaults differ, check `SchedulingDefaultsFactory` and component defaults for updates.</span>

## Reference / Related Docs
- <span id="claim-runtime-manifest-structure-fields">Runtime Manifest fields are defined in the C2 component API.</span>
- <span id="claim-buildinfo-structure-fields">Build Info fields include version, revision, timestamp, and compiler information.</span>
- <span id="claim-component-manifest-structure">Component Manifest lists APIs, Controller Services, Processors, Reporting Tasks, Parameter Providers, and Flow Analysis Rules.</span>
- <span id="claim-scheduling-defaults-values">Default scheduling values are centralized in the Scheduling Defaults Factory.</span>
- <span id="claim-builder-default-penalty-yield-bulletin">Component-level defaults include yield, penalization, and bulletin level in the runtime builder.</span>

