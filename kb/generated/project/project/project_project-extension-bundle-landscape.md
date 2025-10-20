---
claims:
  - id: claim-nar-classloader
    sources:
      - id: src-developer-guide
        locator: "#nars"
  - id: claim-extension-module-aggregator
    sources:
      - id: src-bundles-pom
        locator: "L24-L98"
  - id: claim-standard-bundle-structure
    sources:
      - id: src-standard-bundle-pom
        locator: "L27-L35"
  - id: claim-standard-shared-nar-parent
    sources:
      - id: src-standard-shared-nar-pom
        locator: "L24-L35"
  - id: claim-standard-services-modules
    sources:
      - id: src-standard-services-pom
        locator: "L27-L58"
  - id: claim-standard-services-api-nar
    sources:
      - id: src-standard-services-api-nar-pom
        locator: "L25-L136"
  - id: claim-aws-bundle-modules
    sources:
      - id: src-aws-bundle-pom
        locator: "L33-L41"
  - id: claim-standard-nar-deps
    sources:
      - id: src-standard-nar-pom
        locator: "L23-L47"
  - id: claim-nar-packaging
    sources:
      - id: src-developer-guide
        locator: "#nars"
  - id: claim-component-docs-scope
    sources:
      - id: src-components-readme
        locator: "L3-L19"
  - id: claim-processors-implemented-doc
    sources:
      - id: src-processors-implemented
        locator: "L3-L8"
  - id: claim-nar-parent-limit
    sources:
      - id: src-developer-guide
        locator: "#nars"
  - id: claim-classloader-troubleshoot
    sources:
      - id: src-developer-guide
        locator: "#nars"
  - id: claim-reference-developer-guide
    sources:
      - id: src-developer-guide
        locator: "#nars"
  - id: claim-reference-components-doc
    sources:
      - id: src-components-readme
        locator: "L3-L24"
  - id: claim-reference-bundles-pom
    sources:
      - id: src-bundles-pom
        locator: "L24-L98"
sources:
  - id: src-developer-guide
    title: "Apache NiFi Developer Guide"
    href: "nifi-docs/src/main/asciidoc/developer-guide.adoc"
    locator: "#nars"
  - id: src-bundles-pom
    title: "nifi-extension-bundles/pom.xml"
    href: "nifi-extension-bundles/pom.xml"
    locator: "L24-L98"
  - id: src-standard-bundle-pom
    title: "nifi-standard-bundle/pom.xml"
    href: "nifi-extension-bundles/nifi-standard-bundle/pom.xml"
    locator: "L27-L35"
  - id: src-standard-shared-nar-pom
    title: "nifi-standard-shared-nar/pom.xml"
    href: "nifi-extension-bundles/nifi-standard-shared-bundle/nifi-standard-shared-nar/pom.xml"
    locator: "L24-L135"
  - id: src-standard-services-pom
    title: "nifi-standard-services/pom.xml"
    href: "nifi-extension-bundles/nifi-standard-services/pom.xml"
    locator: "L27-L58"
  - id: src-standard-services-api-nar-pom
    title: "nifi-standard-services-api-nar/pom.xml"
    href: "nifi-extension-bundles/nifi-standard-services/nifi-standard-services-api-nar/pom.xml"
    locator: "L25-L136"
  - id: src-aws-bundle-pom
    title: "nifi-aws-bundle/pom.xml"
    href: "nifi-extension-bundles/nifi-aws-bundle/pom.xml"
    locator: "L33-L41"
  - id: src-standard-nar-pom
    title: "nifi-standard-nar/pom.xml"
    href: "nifi-extension-bundles/nifi-standard-bundle/nifi-standard-nar/pom.xml"
    locator: "L23-L47"
  - id: src-components-readme
    title: "docs/components/README.md"
    href: "docs/components/README.md"
    locator: "L3-L24"
  - id: src-processors-implemented
    title: "docs/components/processors-implemented.md"
    href: "docs/components/processors-implemented.md"
    locator: "L3-L8"
---

# NiFi Extension Bundle Catalog

## Introduction / Overview
<span id="claim-nar-classloader">NiFi packages extension components into NiFi Archives (NARs) to isolate classloader dependencies between bundles.</span>
<span id="claim-extension-module-aggregator">The aggregator `nifi-extension-bundles/pom.xml` lists bundle families such as `nifi-standard-bundle`, `nifi-hadoop-bundle`, `nifi-kafka-bundle`, `nifi-aws-bundle`, and `nifi-azure-bundle` to coordinate their builds.</span>

## Concepts / Architecture
<span id="claim-standard-bundle-structure">The `nifi-standard-bundle` POM groups modules for processors, reporting tasks, rules, parameter providers, and associated NAR and content viewer artifacts.</span>
<span id="claim-standard-shared-nar-parent">The `nifi-standard-shared-nar` designates `nifi-standard-services-api-nar` as its parent so child NARs inherit standard controller service APIs and shared dependencies.</span>
<span id="claim-standard-services-modules">The `nifi-standard-services` aggregator enumerates modules including distributed cache, SSL context, lookup services, OAuth2 provider, database DBCP, record serialization, proxy configuration, and the standard services API NAR.</span>
<span id="claim-standard-services-api-nar">The `nifi-standard-services-api-nar` reintroduces the standard service APIs at compile scope to package those definitions for downstream NARs.</span>
<span id="claim-aws-bundle-modules">The `nifi-aws-bundle` modules cover processors, the AWS NAR, service API and API NAR, abstract processor utilities, parameter providers, and the schema registry service.</span>

## Implementation / Configuration
<span id="claim-standard-nar-deps">The `nifi-standard-nar` pulls in the shared NAR along with standard processors, reporting tasks, rules, and parameter providers to assemble the runtime archive.</span>
<span id="claim-nar-packaging">NiFi extension NAR artifacts must declare `nar` packaging and apply the `nifi-nar-maven-plugin` in their Maven build.</span>

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.nifi</groupId>
            <artifactId>nifi-nar-maven-plugin</artifactId>
            <version>1.3.4</version>
            <extensions>true</extensions>
        </plugin>
    </plugins>
</build>
```

## Usage / Examples
- <span id="claim-component-docs-scope">The `docs/components/README.md` explains that candidate inventories are generated by scanning modules such as `nifi-standard-processors` and that implemented lists track automation handling.</span>
- <span id="claim-processors-implemented-doc">The `docs/components/processors-implemented.md` table currently documents automation for `GenerateFlowFile` and `LogAttribute`, including notes on scheduling and relationship handling.</span>

## Best Practices / Tips
<span id="claim-nar-parent-limit">The developer guide states that each NAR may declare only one parent NAR dependency, which becomes its parent classloader.</span>

## Troubleshooting
<span id="claim-classloader-troubleshoot">The developer guide flags `NoClassDefFoundError` as a symptom of conflicting dependencies that NiFi resolves through NAR isolation.</span>

## Reference / Related Docs
- <span id="claim-reference-developer-guide">Refer to the NiFi Developer Guide NAR section for classloader behavior, packaging rules, and parent hierarchy details.</span>
- <span id="claim-reference-components-doc">Consult `docs/components/README.md` for inventory maintenance steps and scan guidance.</span>
- <span id="claim-reference-bundles-pom">Review `nifi-extension-bundles/pom.xml` for the authoritative list of extension bundle modules.</span>
