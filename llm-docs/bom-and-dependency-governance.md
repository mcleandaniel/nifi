---
title: Bill of Materials and Dependency Governance
scope: project
plan_id: project
topic_id: project_project-maven-bom-structure
category: build
priority: medium
tags: [bom, dependencies, build]

claims:
  - id: claim-root-modules-include-boms
    sources: [src-root-pom-modules]
  - id: claim-nifi-bom-packaging-pom
    sources: [src-nifi-bom-pom-packaging]
  - id: claim-nifi-bom-manages-nifi-api-provided
    sources: [src-nifi-bom-depMgmt-nifi-api]
  - id: claim-nifi-bom-manages-nifi-runtime-provided
    sources: [src-nifi-bom-depMgmt-nifi-runtime]
  - id: claim-nifi-bom-provides-logback
    sources: [src-nifi-bom-depMgmt-logging-logback]
  - id: claim-nifi-bom-provides-slf4j-bridges
    sources: [src-nifi-bom-depMgmt-logging-slf4j]
  - id: claim-nifi-bom-dependencies-no-scope
    sources: [src-nifi-bom-dependencies]
  - id: claim-nifi-bom-ignored-deps-config
    sources: [src-nifi-bom-maven-dependency-plugin]
  - id: claim-extension-bom-inherits-nifi-bom
    sources: [src-extension-bom-parent-nifi-bom]
  - id: claim-extension-bom-packaging-pom
    sources: [src-extension-bom-packaging]
  - id: claim-extension-bom-policy-provided-not-overridden
    sources: [src-extension-bom-comment-policy]
  - id: claim-extension-bom-provides-jetty
    sources: [src-extension-bom-jetty-provided]
  - id: claim-extension-bundles-parent-extension-bom
    sources: [src-extension-bundles-parent-extension-bom]
  - id: claim-framework-bundle-parent-extension-bom
    sources: [src-framework-bundle-parent-extension-bom]
  - id: claim-stateless-parent-extension-bom
    sources: [src-stateless-parent-extension-bom]
  - id: claim-standard-shared-bom-purpose
    sources: [src-standard-shared-bom-description]
  - id: claim-standard-services-api-bom-complement-nar
    sources: [src-standard-services-api-bom-comment, src-standard-services-api-nar-compile-scope]
  - id: claim-root-pom-jetty-version-property
    sources: [src-root-pom-jetty-version-property]
  - id: claim-root-pom-slf4j-version-property
    sources: [src-root-pom-slf4j-version-property]
  - id: claim-root-pom-jackson-version-property
    sources: [src-root-pom-jackson-version-property]
  - id: claim-root-pom-imports-jetty-bom
    sources: [src-root-pom-jetty-bom-import]
  - id: claim-root-pom-imports-slf4j-bom
    sources: [src-root-pom-slf4j-bom-import]
  - id: claim-assembly-includes-jetty-nar
    sources: [src-assembly-jetty-nar]

sources:
  - id: src-root-pom-modules
    type: file
    path: pom.xml
    locator: "L25-L36"
  - id: src-nifi-bom-pom-packaging
    type: file
    path: nifi-bom/pom.xml
    locator: "L23-L26"
  - id: src-nifi-bom-depMgmt-nifi-api
    type: file
    path: nifi-bom/pom.xml
    locator: "L33-L39"
  - id: src-nifi-bom-depMgmt-nifi-runtime
    type: file
    path: nifi-bom/pom.xml
    locator: "L41-L47"
  - id: src-nifi-bom-depMgmt-logging-logback
    type: file
    path: nifi-bom/pom.xml
    locator: "L111-L121"
  - id: src-nifi-bom-depMgmt-logging-slf4j
    type: file
    path: nifi-bom/pom.xml
    locator: "L125-L147"
  - id: src-nifi-bom-dependencies
    type: file
    path: nifi-bom/pom.xml
    locator: "L151-L185"
  - id: src-nifi-bom-maven-dependency-plugin
    type: file
    path: nifi-bom/pom.xml
    locator: "L189-L203"
  - id: src-extension-bom-parent-nifi-bom
    type: file
    path: nifi-extension-bom/pom.xml
    locator: "L17-L23"
  - id: src-extension-bom-packaging
    type: file
    path: nifi-extension-bom/pom.xml
    locator: "L23-L25"
  - id: src-extension-bom-comment-policy
    type: file
    path: nifi-extension-bom/pom.xml
    locator: "L26-L37"
  - id: src-extension-bom-jetty-provided
    type: file
    path: nifi-extension-bom/pom.xml
    locator: "L56-L106"
  - id: src-extension-bundles-parent-extension-bom
    type: file
    path: nifi-extension-bundles/pom.xml
    locator: "L18-L23"
  - id: src-framework-bundle-parent-extension-bom
    type: file
    path: nifi-framework-bundle/pom.xml
    locator: "L17-L22"
  - id: src-stateless-parent-extension-bom
    type: file
    path: nifi-stateless/pom.xml
    locator: "L17-L22"
  - id: src-standard-shared-bom-description
    type: file
    path: nifi-extension-bundles/nifi-standard-shared-bundle/nifi-standard-shared-bom/pom.xml
    locator: "L10-L17"
  - id: src-standard-services-api-bom-comment
    type: file
    path: nifi-extension-bundles/nifi-standard-services-api-bom/pom.xml
    locator: "L31-L37"
  - id: src-standard-services-api-nar-compile-scope
    type: file
    path: nifi-extension-bundles/nifi-standard-services/nifi-standard-services-api-nar/pom.xml
    locator: "L24-L36"
  - id: src-root-pom-jetty-version-property
    type: file
    path: pom.xml
    locator: "L196-L197"
  - id: src-root-pom-slf4j-version-property
    type: file
    path: pom.xml
    locator: "L167-L168"
  - id: src-root-pom-jackson-version-property
    type: file
    path: pom.xml
    locator: "L154-L156"
  - id: src-root-pom-jetty-bom-import
    type: file
    path: pom.xml
    locator: "L216-L222"
  - id: src-root-pom-slf4j-bom-import
    type: file
    path: pom.xml
    locator: "L366-L377"
  - id: src-assembly-jetty-nar
    type: file
    path: nifi-assembly/pom.xml
    locator: "L288-L293"
  - id: src-standard-bundle-tika-version
    type: file
    path: nifi-extension-bundles/nifi-standard-bundle/pom.xml
    locator: "L36-L38"
---

**Introduction / Overview**

- <span id="claim-root-modules-include-boms">The root Maven project declares `nifi-bom` and `nifi-extension-bom` modules.</span>
- <span id="claim-nifi-bom-packaging-pom">The `nifi-bom` module uses POM packaging and serves as a Bill of Materials.</span>
- <span id="claim-extension-bom-inherits-nifi-bom">The `nifi-extension-bom` inherits from `nifi-bom` to compose a layered BOM.</span>

**Concepts / Architecture**

- <span id="claim-nifi-bom-manages-nifi-api-provided">`nifi-bom` manages core NiFi artifacts such as `nifi-api` with scope `provided`.</span>
- <span id="claim-nifi-bom-manages-nifi-runtime-provided">`nifi-bom` also manages runtime artifacts (for example `nifi-runtime`) with scope `provided`.</span>
- <span id="claim-nifi-bom-provides-logback">`nifi-bom` marks `logback-classic` and `logback-core` as `provided`.</span>
- <span id="claim-nifi-bom-provides-slf4j-bridges">`nifi-bom` marks SLF4J bridge libraries (`jcl-over-slf4j`, `log4j-over-slf4j`, `jul-to-slf4j`, and `slf4j-api`) as `provided`.</span>
- <span id="claim-nifi-bom-dependencies-no-scope">The `nifi-bom` `<dependencies>` section also lists common compile-time dependencies without explicit scopes.</span>
- <span id="claim-nifi-bom-ignored-deps-config">The BOM configures `maven-dependency-plugin` to ignore these managed items when analyzing transitive copies.</span>
- <span id="claim-extension-bom-packaging-pom">`nifi-extension-bom` is a POM-packaged BOM focused on extension runtime alignment.</span>
- <span id="claim-extension-bom-policy-provided-not-overridden">`nifi-extension-bom` documents that listed dependencies are considered `provided` and must not be overridden by implementations or extensions.</span>
- <span id="claim-extension-bom-provides-jetty">`nifi-extension-bom` manages Jetty server and related EE dependencies with scope `provided`.</span>
- <span id="claim-extension-bundles-parent-extension-bom">Aggregator modules like `nifi-extension-bundles` set `nifi-extension-bom` as their parent.</span>
- <span id="claim-framework-bundle-parent-extension-bom">Framework aggregators like `nifi-framework-bundle` set `nifi-extension-bom` as their parent.</span>
- <span id="claim-stateless-parent-extension-bom">The `nifi-stateless` aggregator also uses `nifi-extension-bom` as its parent.</span>
- <span id="claim-standard-shared-bom-purpose">`nifi-standard-shared-bom` captures cross-cutting dependencies and is paired with a shared NAR to minimize duplicate jars.</span>
- <span id="claim-standard-services-api-bom-complement-nar">`nifi-standard-services-api-bom` marks APIs as `provided` and is complemented by `nifi-standard-services-api-nar` declaring the same entries with `compile` scope.</span>
- <span id="claim-assembly-includes-jetty-nar">The default NiFi assembly includes the `nifi-jetty-nar`.</span>

**Implementation / Configuration**

- <span id="claim-root-pom-jetty-version-property">The root POM centralizes Jetty version with the `jetty.version` property.</span>
- <span id="claim-root-pom-slf4j-version-property">The root POM centralizes SLF4J version with the `org.slf4j.version` property.</span>
- <span id="claim-root-pom-jackson-version-property">The root POM centralizes Jackson versions with `jackson.annotations.version` and `jackson.bom.version` properties.</span>
- <span id="claim-root-pom-imports-jetty-bom">The root POM imports the Jetty BOM in `dependencyManagement` using `type` `pom` and `scope` `import`.</span>
- <span id="claim-root-pom-imports-slf4j-bom">The root POM imports the SLF4J BOM in `dependencyManagement` using `type` `pom` and `scope` `import`.</span>

Recommended POM patterns for extensions

- Use `parent` to align with `nifi-extension-bom` versions:
  ```xml
  <parent>
    <groupId>org.apache.nifi</groupId>
    <artifactId>nifi-extension-bom</artifactId>
    <version>${project.version}</version>
    <relativePath>../nifi-extension-bom</relativePath>
  </parent>
  ```
- Import additional vendor BOMs only when needed, letting root and extension BOMs govern shared libraries:
  ```xml
  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>org.glassfish.jersey</groupId>
        <artifactId>jersey-bom</artifactId>
        <version>${jersey.bom.version}</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>
  ```

**Usage / Examples**

Centralized updates via version properties

- Update Jetty for the platform:
  ```bash
  sed -i.bak 's#<jetty.version>[^<]*</jetty.version>#<jetty.version>12.1.2</jetty.version>#' pom.xml
  ./mvnw -q -DskipTests install -pl :nifi-bom,:nifi-extension-bom -am
  ```
- Update SLF4J across the platform:
  ```bash
  sed -i.bak 's#<org.slf4j.version>[^<]*</org.slf4j.version>#<org.slf4j.version>2.0.17</org.slf4j.version>#' pom.xml
  ./mvnw -q -DskipTests install -pl :nifi-bom,:nifi-extension-bom -am
  ```

Add a shared third‑party library used by many extensions

1) Add to `nifi-standard-shared-bom` with `provided` scope and to `nifi-standard-shared-nar` with `compile` scope.
2) Reference the library in extension modules without versions; the managed version applies.

Example (Apache Tika already follows this pattern via a bundle property):
```xml
<!-- nifi-extension-bundles/nifi-standard-bundle/pom.xml -->
<properties>
  <tika.version>3.2.3</tika.version>
<!-- managed usage appears under dependencyManagement in the same POM -->
</properties>
```

Add an API dependency for services shared by extensions

1) Add to `nifi-standard-services-api-bom` with `provided` scope.
2) Mirror the same entries in `nifi-standard-services-api-nar` with `compile` scope so jars are present on the NAR classpath.

**Best Practices / Tips**

- Prefer BOM-managed versions to per-module versions for consistency.
- Use `provided` scope for artifacts that NiFi supplies at runtime through shared NARs to avoid duplicate jars.
- Keep BOMs focused: place cross-cutting libraries in `nifi-standard-shared-bom`, service APIs in `nifi-standard-services-api-bom`, and container/server libs in `nifi-extension-bom`.
- When importing vendor BOMs, prefer the root or bundle BOM to centralize versions and reduce conflicts.
- Use explicit exclusions in `dependencyManagement` when transitive dependencies need alignment.

**Troubleshooting**

- If a component sees conflicting versions at runtime, check whether the library is declared `provided` in a BOM and present in a shared NAR.
- If versions are not applied, verify that the module inherits from the appropriate BOM parent and does not declare its own version.
- Use `mvn dependency:tree -Dverbose` to inspect effective versions and identify overrides.

**Reference / Related Docs**

- Root POM modules and version properties
- NiFi BOM and Extension BOM POMs
- Standard Shared BOM and Service API BOM/NAR pairs
- Assembly POM including `nifi-jetty-nar`

