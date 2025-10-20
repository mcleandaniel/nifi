Added a publication-ready, verified Markdown doc explaining NiFi’s component documentation pipeline with precise claims and sources.

- New file: llm-docs/verified/component-documentation-pipeline.md
- Covers: annotations, advanced docs, NAR packaging, REST endpoints, UI routing, runtime manifest, AsciiDoc build, assembly process, and contribution workflow
- Includes runnable curl+jq example to fetch component docs by bundle coordinates
- All verifiable statements annotated with claim spans and mapped to specific source locators

Key highlights
- Annotations and scope: `@CapabilityDescription`, `@Tags`, `@ReadsAttributes`, `@WritesAttributes`, `@SeeAlso` (nifi-docs/src/main/asciidoc/developer-guide.adoc:860, nifi-docs/src/main/asciidoc/developer-guide.adoc:891, nifi-docs/src/main/asciidoc/developer-guide.adoc:912)
- UI access: right‑click → View Documentation (nifi-docs/src/main/asciidoc/getting-started.adoc:262)
- Advanced docs: `additionalDetails.md` concept and filename (nifi-docs/src/main/asciidoc/developer-guide.adoc:934)
- Runtime location: `META-INF/docs/additional-details/<type>/additionalDetails.md` (nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/manifest/StandardRuntimeManifestService.java:380, nifi-manifest/nifi-runtime-manifest-core/src/main/java/org/apache/nifi/runtime/manifest/impl/DirectoryExtensionManifestProvider.java:99)
- Build enforcement: `nifi-nar-maven-plugin` with `enforceDocGeneration` (pom.xml:872)
- AsciiDoc site: `asciidoctor-maven-plugin` (nifi-docs/pom.xml:49)
- Assembly: unpacks `**/docs/**` from NARs (nifi-assembly/pom.xml:28), includes manifests assembly (nifi-assembly/src/main/assembly/extension-manifests.xml:1)
- REST endpoints for docs: `/nifi-api/flow/*-definition/{group}/{artifact}/{version}/{type}`, `/nifi-api/flow/additional-details/{group}/{artifact}/{version}/{type}` (nifi-framework-bundle/.../FlowResource.java:1669, 1723, 1939)
- UI routes use bundle coordinates (nifi-frontend/src/main/frontend/apps/nifi/src/app/state/documentation/documentation.effects.ts:30 and nifi-frontend/.../controller-services.component.ts:207)
- Runtime manifest generator writes versioned docs (nifi-manifest/nifi-runtime-manifest-core/.../RuntimeManifestGenerator.java:106)
- Contribution notes: AsciiDoc sources and contributor guidance (nifi-docs/src/main/asciidoc/developer-guide.adoc:2731, 2753)
- Source path convention example for advanced docs (nifi-extension-bundles/.../CSVReader/additionalDetails.md:1)
- Deprecation guidance and behavior in docs/logs (nifi-docs/src/main/asciidoc/developer-guide.adoc:2648)

Want me to also add a short README pointer under docs/components/ to reference this pipeline doc for contributors?
