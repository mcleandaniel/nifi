---
title: Distribution and Assembly Artifacts
scope: project
plan_id: project
topic_id: project_project-distribution-artifacts
category: release
tags: [assembly, distribution, release]
claims:
  - id: claim-assembly-bin-id
    sources: [src-dependencies-xml-bin]
  - id: claim-assembly-components
    sources: [src-dependencies-xml-bin]
  - id: claim-core-lib-includes
    sources: [src-core-xml-libs]
  - id: claim-common-bootstrap-output
    sources: [src-common-xml-bootstrap]
  - id: claim-aspectj-weaver
    sources: [src-common-xml-aspectj]
  - id: claim-config-unpack-conf
    sources: [src-common-xml-conf]
  - id: claim-bin-unpack-bin
    sources: [src-common-xml-bin]
  - id: claim-docs-unpack
    sources: [src-common-xml-docs]
  - id: claim-python-framework
    sources: [src-common-xml-python-framework]
  - id: claim-python-api
    sources: [src-common-xml-python-api]
  - id: claim-nar-bundles
    sources: [src-common-xml-nar-bundles]
  - id: claim-create-extensions-dir
    sources: [src-common-xml-extensions-dir]
  - id: claim-top-files
    sources: [src-common-xml-top-files]
  - id: claim-assemble-make-shared
    sources: [src-assembly-pom-make-shared]
  - id: claim-assemble-manifests-zip
    sources: [src-assembly-pom-make-manifests, src-extension-manifests-xml]
  - id: claim-extract-manifests-dep-plugin
    sources: [src-assembly-pom-dep-unpack-manifests]
  - id: claim-nifi-manifest-unpack
    sources: [src-runtime-pom-dep-unpack]
  - id: claim-runtime-gen-exec
    sources: [src-runtime-pom-exec]
  - id: claim-generator-buildinfo
    sources: [src-generator-build-keys, src-build-properties]
  - id: claim-generator-parsing
    sources: [src-generator-exec-build, src-dir-extension-provider, src-jaxb-parser]
  - id: claim-scheduling-defaults
    sources: [src-scheduling-defaults]
  - id: claim-runtime-manifest-fields
    sources: [src-runtime-manifest-model]
  - id: claim-standard-runtime-builder
    sources: [src-standard-builder-build, src-standard-builder-switch]
  - id: claim-extension-manifest-required-systemapiversion
    sources: [src-extension-manifest-required-systemapiversion]
  - id: claim-extension-type-enum
    sources: [src-extension-type-enum]
  - id: claim-assemble-targz-profile
    sources: [src-assembly-pom-profiles-targz]
  - id: claim-avoid-archive-dir-only
    sources: [src-assembly-pom-profile-dir-only]
  - id: claim-runtime-manifest-it-asserts
    sources: [src-runtime-manifest-it]
sources:
  - id: src-dependencies-xml-bin
    type: file
    path: nifi-assembly/src/main/assembly/dependencies.xml
    locator: L16-L24
  - id: src-core-xml-libs
    type: file
    path: nifi-assembly/src/main/assembly/core.xml
    locator: L19-L43
  - id: src-common-xml-bootstrap
    type: file
    path: nifi-assembly/src/main/assembly/common.xml
    locator: L18-L36
  - id: src-common-xml-aspectj
    type: file
    path: nifi-assembly/src/main/assembly/common.xml
    locator: L38-L49
  - id: src-common-xml-conf
    type: file
    path: nifi-assembly/src/main/assembly/common.xml
    locator: L52-L70
  - id: src-common-xml-bin
    type: file
    path: nifi-assembly/src/main/assembly/common.xml
    locator: L72-L90
  - id: src-common-xml-docs
    type: file
    path: nifi-assembly/src/main/assembly/common.xml
    locator: L92-L110
  - id: src-common-xml-python-framework
    type: file
    path: nifi-assembly/src/main/assembly/common.xml
    locator: L112-L133
  - id: src-common-xml-python-api
    type: file
    path: nifi-assembly/src/main/assembly/common.xml
    locator: L135-L156
  - id: src-common-xml-nar-bundles
    type: file
    path: nifi-assembly/src/main/assembly/common.xml
    locator: L158-L166
  - id: src-common-xml-extensions-dir
    type: file
    path: nifi-assembly/src/main/assembly/common.xml
    locator: L168-L176
  - id: src-common-xml-top-files
    type: file
    path: nifi-assembly/src/main/assembly/common.xml
    locator: L177-L199
  - id: src-assembly-pom-make-shared
    type: file
    path: nifi-assembly/pom.xml
    locator: L55-L71
  - id: src-assembly-pom-make-manifests
    type: file
    path: nifi-assembly/pom.xml
    locator: L74-L94
  - id: src-extension-manifests-xml
    type: file
    path: nifi-assembly/src/main/assembly/extension-manifests.xml
    locator: L16-L25
  - id: src-assembly-pom-dep-unpack-manifests
    type: file
    path: nifi-assembly/pom.xml
    locator: L33-L41
  - id: src-runtime-pom-dep-unpack
    type: file
    path: nifi-manifest/nifi-runtime-manifest/pom.xml
    locator: L68-L90
  - id: src-runtime-pom-exec
    type: file
    path: nifi-manifest/nifi-runtime-manifest/pom.xml
    locator: L103-L124
  - id: src-generator-build-keys
    type: file
    path: nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/RuntimeManifestGenerator.java
    locator: L56-L63
  - id: src-build-properties
    type: file
    path: nifi-manifest/nifi-runtime-manifest/src/main/resources/build.properties
    locator: L16-L25
  - id: src-generator-exec-build
    type: file
    path: nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/RuntimeManifestGenerator.java
    locator: L79-L87
  - id: src-dir-extension-provider
    type: file
    path: nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/DirectoryExtensionManifestProvider.java
    locator: L37-L45
  - id: src-jaxb-parser
    type: file
    path: nifi-manifest/nifi-extension-manifest-parser/src/main/java/org/apache/nifi/extension/manifest/parser/jaxb/JAXBExtensionManifestParser.java
    locator: L34-L47
  - id: src-scheduling-defaults
    type: file
    path: nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/SchedulingDefaultsFactory.java
    locator: L16-L35
  - id: src-runtime-manifest-model
    type: file
    path: c2/c2-protocol/c2-protocol-component-api/src/main/java/org/apache/nifi/c2/protocol/component/api/RuntimeManifest.java
    locator: L21-L44
  - id: src-standard-builder-build
    type: file
    path: nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/StandardRuntimeManifestBuilder.java
    locator: L178-L187
  - id: src-standard-builder-switch
    type: file
    path: nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/StandardRuntimeManifestBuilder.java
    locator: L196-L212
  - id: src-extension-manifest-required-systemapiversion
    type: file
    path: nifi-manifest/nifi-extension-manifest-model/src/main/java/org/apache/nifi/extension/manifest/ExtensionManifest.java
    locator: L40-L45
  - id: src-extension-type-enum
    type: file
    path: nifi-manifest/nifi-extension-manifest-model/src/main/java/org/apache/nifi/extension/manifest/ExtensionType.java
    locator: L18-L36
  - id: src-assembly-pom-profiles-targz
    type: file
    path: nifi-assembly/pom.xml
    locator: L1046-L1066
  - id: src-assembly-pom-profile-dir-only
    type: file
    path: nifi-assembly/pom.xml
    locator: L1121-L1152
  - id: src-runtime-manifest-it
    type: file
    path: nifi-manifest/nifi-runtime-manifest-test/src/test/java/org/apache/nifi/runtime/manifest/RuntimeManifestIT.java
    locator: L56-L79
---

# Distribution and Assembly Artifacts

## Introduction / Overview

<span id="claim-assembly-bin-id">Apache NiFi builds its binary distribution using a Maven Assembly descriptor with id `bin` and base directory `nifi-${project.version}`.</span>

<span id="claim-assembly-components">The `bin` assembly composes two component descriptors: `core.xml` and `common.xml`.</span>

<span id="claim-assemble-make-shared">Packaging is driven by `maven-assembly-plugin` to produce a `dir` and `zip` distribution named `nifi-${project.version}` using the `dependencies.xml` descriptor.</span>

<span id="claim-assemble-manifests-zip">A separate `manifests` ZIP is attached that collects extension manifests under a `nifi-manifests` base directory.</span>

## Concepts / Architecture

<span id="claim-core-lib-includes">`core.xml` declares a dependency set that writes core libraries to `lib`, including logging artifacts such as `org.slf4j:slf4j-api` and NiFi modules such as `org.apache.nifi:nifi-api`.</span>

<span id="claim-common-bootstrap-output">`common.xml` writes runtime-scoped bootstrap libraries to `lib/bootstrap`, including `nifi-bootstrap`, `slf4j-api`, `logback-classic`, `logback-core`, `nifi-api`, and related utilities.</span>

<span id="claim-aspectj-weaver">`common.xml` places `org.aspectj:aspectjweaver` under `lib/aspectj` with a note that it is used by the Java Agent for native library loading and not required on the classpath.</span>

<span id="claim-config-unpack-conf">Configuration files are unpacked from `nifi-resources` `conf/*` into the top-level directory with filtering enabled.</span>

<span id="claim-bin-unpack-bin">Executable scripts are unpacked from `nifi-resources` `bin/*` into the top-level directory with file mode `0770` and filtering enabled.</span>

<span id="claim-docs-unpack">Documentation from `nifi-docs` is unpacked under `docs/` with `LICENSE` and `NOTICE` excluded.</span>

<span id="claim-python-framework">The Python framework is unpacked to `python/` from `nifi-python-framework` with `META-INF` and license files excluded.</span>

<span id="claim-python-api">The Python extension API is unpacked to `python/api` from `nifi-python-extension-api` with `META-INF` and license files excluded.</span>

<span id="claim-nar-bundles">All NiFi NAR bundles (`org.apache.nifi:*:nar`) are copied to `lib` without transitive dependencies.</span>

<span id="claim-create-extensions-dir">An empty `extensions/` directory is created using a placeholder file set.</span>

<span id="claim-top-files">Top-level `README`, `LICENSE`, and `NOTICE` are included with mode `0644` and filtering enabled.</span>

## Implementation / Configuration

<span id="claim-extract-manifests-dep-plugin">During the `prepare-package` phase, the assembly module unpacks NAR `docs` content into `${project.build.directory}/extension-manifests`, using one subdirectory per artifact and stripping classifier and version.</span>

<span id="claim-assemble-targz-profile">A `targz` profile switches the assembly output format to `tar.gz` while using the same `dependencies.xml` descriptor.</span>

<span id="claim-avoid-archive-dir-only">A `avoid-archive-formats` profile activated with property `dir-only` builds only a directory-based assembly.</span>

<span id="claim-nifi-manifest-unpack">The `nifi-runtime-manifest` module unpacks the attached `nifi-assembly` `manifests` ZIP into `${extension.manifest.unpack.dir}` during `prepare-package`.</span>

<span id="claim-runtime-gen-exec">The same module then runs `org.apache.nifi.runtime.manifest.impl.RuntimeManifestGenerator` via `exec-maven-plugin`, passing four arguments: the manifests directory, the `build.properties` file, the output JSON path, and a manifest identifier.</span>

<span id="claim-generator-buildinfo">`RuntimeManifestGenerator` reads keys such as `Project-Version`, `Build-Revision`, `Build-Timestamp`, `Build-Jdk`, and `Build-Jdk-Vendor` from a filtered `build.properties` resource.</span>

<span id="claim-generator-parsing">Extension manifests are discovered from `META-INF/docs/extension-manifest.xml` and parsed using a JAXB-based parser wired through `DirectoryExtensionManifestProvider`.</span>

## Usage / Examples

Build the binary distribution and manifests from the repository root:

```
mvn -pl nifi-assembly -am -DskipTests package
mvn -pl nifi-manifest/nifi-runtime-manifest -am -DskipTests package
```

Inspect artifacts after the build:

```
ls -la nifi-assembly/target
ls -la nifi-manifest/nifi-runtime-manifest/target/classes | grep -E 'build.properties|nifi-runtime-manifest.json'
```

Generate only a directory layout or `tar.gz` archive when needed:

```
# Directory-only assembly
mvn -pl nifi-assembly -Ddir-only -DskipTests package

# Tar.gz archive assembly
mvn -pl nifi-assembly -Ptargz -DskipTests package
```

## Best Practices / Tips

- Prefer `-DskipTests` only for packaging speed; run tests before a release.
- Use the `avoid-archive-formats` and `targz` profiles to target environment-specific packaging formats.
- Verify that `nifi-assembly` has attached the `manifests` ZIP before generating the runtime manifest.

## Troubleshooting

<span id="claim-runtime-manifest-it-asserts">An integration test reads `target/nifi-runtime-manifest/nifi-runtime-manifest.json` and asserts identifier, agent type, scheduling defaults, and that bundles are present.</span>

If runtime manifest generation fails with a message about the manifest directory, confirm the manifests directory exists and is a directory before execution.

If parsing fails, ensure each extension includes a valid `META-INF/docs/extension-manifest.xml` and that it conforms to the JAXB model version.

## Reference / Related Docs

<span id="claim-runtime-manifest-fields">The runtime manifest model contains `identifier`, `agentType`, `version`, `buildInfo`, `bundles`, and `schedulingDefaults` fields with corresponding accessors.</span>

<span id="claim-standard-runtime-builder">`StandardRuntimeManifestBuilder` sets identifier, version, runtime type, build info, bundles, scheduling defaults, and maps extension types into processor, controller service, reporting task, flow analysis rule, and parameter provider definitions.</span>

<span id="claim-extension-manifest-required-systemapiversion">`ExtensionManifest` requires a `systemApiVersion` element and lists `extension` entries that describe bundled components.</span>

<span id="claim-extension-type-enum">`ExtensionType` enumerates allowable extension kinds: `PROCESSOR`, `CONTROLLER_SERVICE`, `REPORTING_TASK`, `FLOW_ANALYSIS_RULE`, and `PARAMETER_PROVIDER`.</span>
