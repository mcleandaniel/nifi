---
title: Component Documentation Pipeline
claims:
  - id: claim-annotations-capability-tags
    sources: [src-dev-guide-annotations]
  - id: claim-annotations-reads-writes-generate-docs
    sources: [src-dev-guide-reads-writes]
  - id: claim-annotations-seeoalso-applies
    sources: [src-dev-guide-seealso]
  - id: claim-annotations-impl-scope
    sources: [src-dev-guide-annotations]
  - id: claim-ui-view-docs-menu
    sources: [src-getting-started-view-docs]
  - id: claim-advanced-docs-file-name
    sources: [src-dev-guide-advanced-details]
  - id: claim-additional-details-location-runtime
    sources: [src-runtime-additional-details-service, src-runtime-additional-details-provider]
  - id: claim-src-path-convention
    sources: [src-example-additionaldetails-csvreader]
  - id: claim-nar-plugin-enforces-docs
    sources: [src-root-pom-nar-plugin]
  - id: claim-asciidoctor-user-docs
    sources: [src-nifi-docs-asciidoctor]
  - id: claim-assembly-unpacks-docs
    sources: [src-assembly-unpack-docs, src-assembly-manifests-assembly]
  - id: claim-rest-endpoints-component-definitions
    sources: [src-flowresource-processor-def, src-flowresource-cs-def, src-flowresource-additional-details]
  - id: claim-ui-routes-bundle-coordinates
    sources: [src-frontend-doc-effects, src-frontend-doc-request]
  - id: claim-runtime-manifest-generator-writes-docs
    sources: [src-runtime-manifest-generator]
  - id: claim-docs-asciidoc-and-contrib
    sources: [src-dev-guide-asciidoc, src-dev-guide-contrib]
  - id: claim-deprecation-renders-warning
    sources: [src-dev-guide-deprecation]
sources:
  - id: src-dev-guide-annotations
    url: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L860-L876"
  - id: src-dev-guide-reads-writes
    url: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L891-L899"
  - id: src-dev-guide-seealso
    url: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L912-L917"
  - id: src-getting-started-view-docs
    url: nifi-docs/src/main/asciidoc/getting-started.adoc
    locator: "L262-L270"
  - id: src-dev-guide-advanced-details
    url: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L934-L940"
  - id: src-runtime-additional-details-service
    url: nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/manifest/StandardRuntimeManifestService.java
    locator: "L380-L392"
  - id: src-runtime-additional-details-provider
    url: nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/DirectoryExtensionManifestProvider.java
    locator: "L96-L105"
  - id: src-root-pom-nar-plugin
    url: pom.xml
    locator: "L872-L879"
  - id: src-nifi-docs-asciidoctor
    url: nifi-docs/pom.xml
    locator: "L49-L76"
  - id: src-assembly-unpack-docs
    url: nifi-assembly/pom.xml
    locator: "L28-L42"
  - id: src-assembly-manifests-assembly
    url: nifi-assembly/src/main/assembly/extension-manifests.xml
    locator: "L1-L24"
  - id: src-flowresource-processor-def
    url: nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/FlowResource.java
    locator: "L1669-L1676"
  - id: src-flowresource-cs-def
    url: nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/FlowResource.java
    locator: "L1723-L1732"
  - id: src-flowresource-additional-details
    url: nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/FlowResource.java
    locator: "L1939-L1948"
  - id: src-frontend-doc-effects
    url: nifi-frontend/src/main/frontend/apps/nifi/src/app/state/documentation/documentation.effects.ts
    locator: "L30-L45"
  - id: src-frontend-doc-request
    url: nifi-frontend/src/main/frontend/apps/nifi/src/app/pages/flow-designer/ui/controller-service/controller-services.component.ts
    locator: "L207-L215"
  - id: src-runtime-manifest-generator
    url: nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/RuntimeManifestGenerator.java
    locator: "L106-L144"
  - id: src-dev-guide-asciidoc
    url: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L2731-L2742"
  - id: src-dev-guide-contrib
    url: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L2753-L2753"
  - id: src-example-additionaldetails-csvreader
    url: nifi-extension-bundles/nifi-standard-services/nifi-record-serialization-services-bundle/nifi-record-serialization-services/src/main/resources/docs/org.apache.nifi.csv.CSVReader/additionalDetails.md
    locator: "L1-L3"
  - id: src-dev-guide-deprecation
    url: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L2648-L2653"
---

# Component Documentation Pipeline

## Overview

<span id="claim-annotations-capability-tags">NiFi components declare documentation using Java annotations such as `@CapabilityDescription` and `@Tags` under `org.apache.nifi.annotation.documentation`.</span> <span id="claim-annotations-reads-writes-generate-docs">Attribute interactions are expressed with `@ReadsAttribute(s)` and `@WritesAttribute(s)` and are incorporated into generated documentation.</span> <span id="claim-annotations-seeoalso-applies">Related components can be linked with `@SeeAlso` on Processors, ControllerServices, ParameterProviders, and ReportingTasks.</span>

<span id="claim-ui-view-docs-menu">In the UI, right‑click a component and choose View Documentation to open the usage page.</span> <span id="claim-advanced-docs-file-name">Advanced, narrative documentation lives in an `additionalDetails.md` file that is linked from the generated component page.</span>

This document explains how component docs are generated, packaged, and served in NiFi releases, and how to contribute updates.

## Concepts / Architecture

- <span id="claim-nar-plugin-enforces-docs">The build enables the `nifi-nar-maven-plugin` with `extensions` and `enforceDocGeneration` so component bundles must produce documentation during packaging.</span>
- <span id="claim-asciidoctor-user-docs">System‑level user guides are authored in AsciiDoc and rendered by the `asciidoctor-maven-plugin`.</span>
- <span id="claim-assembly-unpacks-docs">During assembly, NiFi unpacks each NAR’s `docs` content into `target/extension-manifests` and includes a manifests archive in the distribution.</span>
- <span id="claim-runtime-manifest-generator-writes-docs">The runtime manifest generator collates extension manifests and writes versioned docs directories per bundle (`group/artifact/version/type/additionalDetails.md`).</span>
- <span id="claim-additional-details-location-runtime">At runtime, NiFi loads `additionalDetails.md` from `META-INF/docs/additional-details/<type>/additionalDetails.md` within each installed bundle.</span>
- <span id="claim-rest-endpoints-component-definitions">Component definitions and additional details are served over REST under `/nifi-api/flow/*-definition/{group}/{artifact}/{version}/{type}` and `/nifi-api/flow/additional-details/{group}/{artifact}/{version}/{type}`.</span>
- <span id="claim-ui-routes-bundle-coordinates">The UI routes documentation views using the selected component’s bundle coordinates (group, artifact, version, type).</span>

## Implementation / Configuration

- Annotations
  - Add `@CapabilityDescription` and `@Tags` to each component class; include concise, user‑facing descriptions and relevant keywords. <span id="claim-annotations-impl-scope">The annotations apply to Processors, Controller Services, and Reporting Tasks.</span>
  - Use `@ReadsAttributes`/`@WritesAttributes` to document attribute usage; prefer concrete attribute names and behavior‑oriented descriptions.
  - Link related components with `@SeeAlso` to improve navigation.

- Advanced documentation
  - Author a Markdown file named `additionalDetails.md` specific to each component type. In source trees, place it under a folder named for the fully‑qualified type. For example: `src/main/resources/docs/org.apache.nifi.csv.CSVReader/additionalDetails.md`.
    <span id="claim-src-path-convention">Place component advanced docs under a type‑named folder within `src/main/resources/docs/`.</span>
  - At build and packaging time, this content is embedded so that the runtime can read it from `META-INF/docs/additional-details/<type>/additionalDetails.md` inside the installed bundle.

- Build and packaging
  - NAR packaging: Ensure the module uses NiFi’s NAR build and inherits the parent `nifi-nar-maven-plugin` configuration with documentation enforcement.
  - AsciiDoc site: Edit AsciiDoc sources under `nifi-docs/src/main/asciidoc`. The Asciidoctor plugin renders HTML as part of the build and `nifi-assembly` includes these docs alongside the runtime.
  - Manifest collation: The assembly unpacks `**/docs/**` from all NARs, then `RuntimeManifestGenerator` aggregates manifests and copies additionalDetails into versioned bundle subdirectories.

## Usage / Examples

The examples below demonstrate how to retrieve documentation for a specific Processor from a running NiFi.

Example: fetch the definition and additional details for `org.apache.nifi.processors.standard.SplitText` without manual variable setup.

```bash
#!/usr/bin/env bash
set -euo pipefail

NIFI_API="${NIFI_API:-http://localhost:8080/nifi-api}"
TYPE="${TYPE:-org.apache.nifi.processors.standard.SplitText}"

# Find bundle coordinates for the type
read -r GROUP ARTIFACT VERSION < <(
  curl -fsSL "${NIFI_API}/flow/processor-types?type=${TYPE}" \
  | jq -r '.processorTypes[0].bundle | "\(.group) \(.artifact) \(.version)"'
)

urlencode() { python3 - <<'PY'
import sys, urllib.parse
print(urllib.parse.quote(sys.argv[1], safe=''))
PY
} 

TYPE_ENC=$(urlencode "$TYPE")

echo "# Processor Definition"
curl -fsSL "${NIFI_API}/flow/processor-definition/${GROUP}/${ARTIFACT}/${VERSION}/${TYPE_ENC}" | jq .

echo -e "\n# Additional Details (Markdown)"
curl -fsSL "${NIFI_API}/flow/additional-details/${GROUP}/${ARTIFACT}/${VERSION}/${TYPE_ENC}" | jq -r .additionalDetails
```

Notes:
- Endpoints are version‑scoped, so the documentation corresponds to the installed bundle exactly.
- Substitute definitions for Controller Services, Reporting Tasks, Parameter Providers, or Flow Analysis Rules using the corresponding REST paths.

## Best Practices / Tips

- Keep `@CapabilityDescription` short and actionable; elaborate in `additionalDetails.md` with scenarios and examples.
- Use `@Tags` for discoverability; prefer nouns and domains users search for.
- Avoid duplicating annotation content in `additionalDetails.md`; link related components via `@SeeAlso`.
- Use `@DeprecationNotice` when deprecating components; include alternatives so the warning appears in docs and logs.
  <span id="claim-deprecation-renders-warning">Deprecation annotations render warnings in generated documentation and also log a warning when a deprecated component is present in the flow.</span>
- Validate locally by building the NAR and testing the REST endpoints against a dev NiFi instance.

## Troubleshooting

- Documentation generation failed in Maven: ensure your component has `@CapabilityDescription` and `@Tags`; the build is configured to enforce doc generation.
- Additional details not appearing: confirm the file exists under the component’s type folder and is packaged so the runtime can read `META-INF/docs/additional-details/<type>/additionalDetails.md` from the bundle.
- UI cannot open docs: verify the bundle’s coordinates (group, artifact, version) match an installed NAR and that the REST definition endpoints return 200.

## Reference / Related Docs

- Developer Guide: documentation annotations, advanced “Usage” docs, deprecation and contribution guidance.
- REST API: component definition and additional‑details endpoints under `/nifi-api/flow/*`.
- Build and Assembly: AsciiDoc generation and NAR documentation collation in the distribution.
