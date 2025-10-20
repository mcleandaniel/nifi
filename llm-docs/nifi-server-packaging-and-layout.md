---
title: NiFi Server Packaging and Layout
scope: service
plan_id: service-main
topic_id: service-main_service-main-runtime-package
category: deployment
priority: high
tags: [packaging, distribution, runtime]

claims:
  claim-assembly-output-formats:
    - source: src-assembly-pom
      locator: "L55-L70"
  claim-assembly-basedir:
    - source: src-assembly-dependencies-xml
      locator: "L17-L20"
  claim-core-libs-to-lib:
    - source: src-assembly-core-xml
      locator: "L19-L44"
  claim-bootstrap-libs-to-lib-bootstrap:
    - source: src-assembly-common-xml
      locator: "L19-L36"
  claim-aspectj-to-lib-aspectj:
    - source: src-assembly-common-xml
      locator: "L38-L49"
  claim-conf-from-resources:
    - source: src-assembly-common-xml
      locator: "L52-L70"
  claim-bin-from-resources:
    - source: src-assembly-common-xml
      locator: "L72-L90"
  claim-docs-from-nifi-docs:
    - source: src-assembly-common-xml
      locator: "L92-L110"
  claim-python-framework-layout:
    - source: src-assembly-common-xml
      locator: "L112-L133"
  claim-python-api-layout:
    - source: src-assembly-common-xml
      locator: "L135-L156"
  claim-extensions-dir-created:
    - source: src-assembly-common-xml
      locator: "L168-L175"
  claim-nars-to-lib:
    - source: src-assembly-common-xml
      locator: "L158-L166"
  claim-assembly-includes-framework-and-server-nar:
    - source: src-assembly-pom
      locator: "L216-L227"
  claim-server-nar-pulls-framework-and-webapps:
    - source: src-server-nar-pom
      locator: "L26-L49"
  claim-framework-nar-depends-jetty-nar:
    - source: src-framework-nar-pom
      locator: "L18-L25"
  claim-default-dirs-values:
    - source: src-nifi-properties-defaults
      locator: "L349-L352"
    - source: src-resources-pom-defaults
      locator: "L76-L79"
  claim-working-dirs-derived:
    - source: src-nifi-properties-working-dirs
      locator: "L767-L774"
  claim-unpacker-uses-working-dirs:
    - source: src-nar-unpacker
      locator: "L75-L85"
  claim-unpacker-framework-jetty-selection:
    - source: src-nar-unpacker
      locator: "L138-L158"
  claim-unpacker-requires-framework-jetty:
    - source: src-nar-unpacker
      locator: "L162-L177"
  claim-nar-classloaders-service-loader:
    - source: src-nar-classloaders
      locator: "L270-L299"
  claim-nar-classloaders-framework-jetty-identification:
    - source: src-nar-classloaders
      locator: "L306-L316"
  claim-system-bundle-uses-lib-as-working-dir:
    - source: src-system-bundle
      locator: "L46-L58"
  claim-classloader-bundled-deps:
    - source: src-nar-classloader
      locator: "L181-L206"
  claim-nar-autoloader-watches-extensions:
    - source: src-nar-autoloader
      locator: "L59-L68"
  claim-jetty-server-starts-nar-autoloader:
    - source: src-jetty-server
      locator: "L780-L793"
  claim-bootstrap-aspectj-agent-guidance:
    - source: src-bootstrap-conf
      locator: "L52-L59"
  claim-duplicate-nar-coordinates-error:
    - source: src-nar-classloaders-duplicate
      locator: "L189-L196"
  claim-nar-providers-copy-to-autoload:
    - source: src-nifi-properties-comment-providers
      locator: "L356-L359"
  claim-nars-to-lib-usage:
    - source: src-assembly-common-xml
      locator: "L158-L166"
  claim-bootstrap-libs-usage:
    - source: src-assembly-common-xml
      locator: "L19-L36"
  claim-extensions-usage:
    - source: src-assembly-common-xml
      locator: "L168-L175"
  claim-nifi-properties-defaults-usage:
    - source: src-nifi-properties-defaults
      locator: "L349-L352"
  claim-autoload-behavior-usage:
    - source: src-nar-autoloader
      locator: "L59-L68"
  claim-unpacker-framework-jetty-selection-tip:
    - source: src-nar-unpacker
      locator: "L138-L158"
  claim-unpacker-requires-jetty-ts:
    - source: src-nar-unpacker
      locator: "L171-L177"
  claim-unpacker-requires-framework-ts:
    - source: src-nar-unpacker
      locator: "L162-L168"
  claim-duplicate-nar-ts:
    - source: src-nar-classloaders-duplicate
      locator: "L189-L196"
  claim-aspectj-native-ts:
    - source: src-bootstrap-conf
      locator: "L52-L59"

sources:
  - id: src-assembly-pom
    path: nifi-assembly/pom.xml
  - id: src-assembly-dependencies-xml
    path: nifi-assembly/src/main/assembly/dependencies.xml
  - id: src-assembly-core-xml
    path: nifi-assembly/src/main/assembly/core.xml
  - id: src-assembly-common-xml
    path: nifi-assembly/src/main/assembly/common.xml
  - id: src-server-nar-pom
    path: nifi-framework-bundle/nifi-server-nar/pom.xml
  - id: src-framework-nar-pom
    path: nifi-framework-bundle/nifi-framework-nar/pom.xml
  - id: src-resources-pom-defaults
    path: nifi-framework-bundle/nifi-framework/nifi-resources/pom.xml
  - id: src-nifi-properties-defaults
    path: nifi-commons/nifi-properties/src/main/java/org/apache/nifi/util/NiFiProperties.java
  - id: src-nifi-properties-working-dirs
    path: nifi-commons/nifi-properties/src/main/java/org/apache/nifi/util/NiFiProperties.java
  - id: src-nar-unpacker
    path: nifi-framework-bundle/nifi-framework/nifi-nar-utils/src/main/java/org/apache/nifi/nar/NarUnpacker.java
  - id: src-nar-classloaders
    path: nifi-framework-bundle/nifi-framework/nifi-nar-utils/src/main/java/org/apache/nifi/nar/NarClassLoaders.java
  - id: src-nar-classloader
    path: nifi-framework-bundle/nifi-framework/nifi-nar-utils/src/main/java/org/apache/nifi/nar/NarClassLoader.java
  - id: src-system-bundle
    path: nifi-framework-bundle/nifi-framework/nifi-nar-utils/src/main/java/org/apache/nifi/nar/SystemBundle.java
  - id: src-nar-autoloader
    path: nifi-framework-bundle/nifi-framework/nifi-framework-nar-loading-utils/src/main/java/org/apache/nifi/nar/NarAutoLoader.java
  - id: src-jetty-server
    path: nifi-framework-bundle/nifi-framework/nifi-web/nifi-jetty/src/main/java/org/apache/nifi/web/server/JettyServer.java
  - id: src-bootstrap-conf
    path: nifi-framework-bundle/nifi-framework/nifi-resources/src/main/resources/conf/bootstrap.conf
  - id: src-nar-classloaders-duplicate
    path: nifi-framework-bundle/nifi-framework/nifi-nar-utils/src/main/java/org/apache/nifi/nar/NarClassLoaders.java
  - id: src-nifi-properties-comment-providers
    path: nifi-framework-bundle/nifi-framework/nifi-resources/src/main/resources/conf/nifi.properties
---

## Introduction / Overview

<span id="claim-assembly-output-formats">The NiFi server distribution is assembled as both a directory and a zip archive named `nifi-${project.version}`.</span>

<span id="claim-assembly-basedir">The assembly base directory is set to `nifi-${project.version}`.</span>

<span id="claim-assembly-includes-framework-and-server-nar">The server distribution pulls in framework and server NARs through Maven dependencies.</span>

## Concepts / Architecture

<span id="claim-server-nar-pulls-framework-and-webapps">The `nifi-server-nar` depends on the `nifi-framework-nar`, packages the `nifi-web-api` and `nifi-ui` WARs, and includes Jetty classes.</span>

<span id="claim-framework-nar-depends-jetty-nar">The `nifi-framework-nar` declares a dependency on the `nifi-jetty-nar`.</span>

<span id="claim-system-bundle-uses-lib-as-working-dir">At runtime, the system bundle uses the configured NAR library directory as its working directory.</span>

<span id="claim-nar-classloaders-service-loader">During initialization, NAR class loaders are created, and a `NiFiServer` implementation is located using `ServiceLoader`.</span>

<span id="claim-nar-classloaders-framework-jetty-identification">The framework and Jetty bundles are identified among unpacked NARs for class loader hierarchy.</span>

## Implementation / Configuration

### Directory Layout (installed server)

<span id="claim-core-libs-to-lib">Core libraries (logging, NiFi APIs, runtime) are written to `lib/`.</span>

<span id="claim-bootstrap-libs-to-lib-bootstrap">Bootstrap libraries are placed under `lib/bootstrap/`.</span>

<span id="claim-aspectj-to-lib-aspectj">The AspectJ weaver JAR is placed under `lib/aspectj/` for optional Java Agent use.</span>

<span id="claim-conf-from-resources">Configuration files are unpacked into `conf/` from the `nifi-resources` artifact.</span>

<span id="claim-bin-from-resources">Executable scripts are unpacked into `bin/` from the `nifi-resources` artifact.</span>

<span id="claim-docs-from-nifi-docs">Documentation is unpacked into `docs/` from the `nifi-docs` artifact.</span>

<span id="claim-python-framework-layout">Python framework files are unpacked into `python/`.</span>

<span id="claim-python-api-layout">Python extension API files are unpacked into `python/api/`.</span>

<span id="claim-nars-to-lib">All NiFi NARs are copied to `lib/`.</span>

<span id="claim-extensions-dir-created">An empty `extensions/` directory is created for drop-in NARs.</span>

### How the Assembly Pulls Framework + Server NARs

<span id="claim-assembly-includes-framework-and-server-nar">`nifi-assembly` declares `nifi-framework-nar` and `nifi-server-nar` as NAR dependencies so they are included in the packaged `lib/`.</span>

<span id="claim-server-nar-pulls-framework-and-webapps">`nifi-server-nar` pulls in framework and server-side web applications needed to run the server.</span>

### Default Locations and Working Directories

<span id="claim-default-dirs-values">Default locations are `./lib` (NAR library), `./extensions` (auto-load directory), and `./work/nar` (NAR working root).</span>

<span id="claim-working-dirs-derived">Working directories derive to `work/nar/framework` and `work/nar/extensions`.</span>

### NAR Unpacking and Loading

<span id="claim-unpacker-uses-working-dirs">At startup, NiFi computes library and working directories and initiates NAR unpacking.</span>

<span id="claim-unpacker-framework-jetty-selection">`NarUnpacker` unpacks the framework NAR to the framework working directory, Jetty NAR and other extensions to the extensions working directory.</span>

<span id="claim-unpacker-requires-framework-jetty">If required framework or Jetty NAR is missing or unreadable, startup fails with an error.</span>

<span id="claim-classloader-bundled-deps">Each NAR class loader adds `NAR-INF/bundled-dependencies` and contained JARs to its classpath.</span>

### Auto-Loading New NARs

<span id="claim-nar-autoloader-watches-extensions">The Nar Auto-Loader watches the auto-load directory and loads `.nar` files it finds.</span>

<span id="claim-jetty-server-starts-nar-autoloader">The Jetty server starts the Auto-Loader after initializing providers and passes the extensions working directory to the loader.</span>

### Bootstrap Agent for Native Libraries (optional)

<span id="claim-bootstrap-aspectj-agent-guidance">`bootstrap.conf` documents enabling an AspectJ Java Agent to address native library loading across class loaders.</span>

## Usage / Examples

- Inspect installed layout after build/install:
  - `ls -1 lib` — <span id="claim-nars-to-lib-usage">NARs and core JARs are under `lib/`.</span>
  - `ls -1 lib/bootstrap` — <span id="claim-bootstrap-libs-usage">Bootstrap JARs are under `lib/bootstrap/`.</span>
  - `ls -1 extensions` — <span id="claim-extensions-usage">Drop-in directory for additional NARs.</span>

- Verify defaults in `conf/nifi.properties`:
  - `grep -n "nifi.nar.library.directory\|nifi.nar.library.autoload.directory\|nifi.nar.working.directory" conf/nifi.properties` — <span id="claim-nifi-properties-defaults-usage">Shows active values for library, autoload, and working directories.</span>

- Drop-in extension loading at runtime:
  - Copy `example.nar` to `extensions/` — <span id="claim-autoload-behavior-usage">Nar Auto-Loader detects and loads it without restart when enabled.</span>

## Best Practices / Tips

- Use `extensions/` for third-party or custom NARs to enable auto-loading. <span id="claim-nar-providers-copy-to-autoload">NAR providers and the Auto-Loader operate on the auto-load directory.</span>
- Avoid duplicate coordinates across NARs; NiFi enforces uniqueness at startup. <span id="claim-duplicate-nar-coordinates-error">Duplicate group:artifact:version coordinates cause an error.</span>
- Do not place framework or Jetty NARs into `extensions/`; they are handled explicitly by the unpacker and class loader hierarchy. <span id="claim-unpacker-framework-jetty-selection-tip">Framework and Jetty are selected and unpacked to specific working subdirectories.</span>

## Troubleshooting

- Missing Jetty NAR: <span id="claim-unpacker-requires-jetty-ts">Startup fails if Jetty NAR is not found or unreadable.</span>
- Missing Framework NAR: <span id="claim-unpacker-requires-framework-ts">Startup fails if the framework NAR is not found or unreadable.</span>
- Duplicate NAR coordinates: <span id="claim-duplicate-nar-ts">An `IllegalStateException` is thrown when two unpacked NARs share the same coordinates.</span>
- Native library load clashes: <span id="claim-aspectj-native-ts">Enable the optional AspectJ Java Agent as documented in `bootstrap.conf` if native library conflicts occur.</span>

## Reference / Related Docs

- Build assembly descriptors under `nifi-assembly/src/main/assembly/`.
- Runtime NAR handling under `nifi-framework-bundle/nifi-framework/` packages (`nifi-nar-utils`, `nifi-web/nifi-jetty`).
- Default configuration templates in `nifi-framework-bundle/nifi-framework/nifi-resources/`.
