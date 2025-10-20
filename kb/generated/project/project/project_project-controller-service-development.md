I’ve drafted a verified, publication‑ready Markdown covering controller service interfaces, lifecycle annotations, usage, testing, and NAR packaging, with precise anchors into the NiFi Developer Guide.

- Added: `llm-docs/controller-service-development-patterns.md`
- Verification: Every claim is wrapped in inline spans and mapped in YAML to `nifi-docs/src/main/asciidoc/developer-guide.adoc` with exact line locators.
- Coverage:
  - Interface separation, API/impl in separate NARs, parent API NAR dependency
  - Obtaining services (`ControllerServiceLookup`, `identifiesControllerService`, `.asControllerService`)
  - Lifecycle (`@OnEnabled`, not using `@OnScheduled` for services)
  - Documentation annotations (`@CapabilityDescription`, `@Tags`, `@SeeAlso`)
  - Packaging with `nifi-nar-maven-plugin`, single nar dependency rule, service provider file path
  - Classloader best practices with `@RequiresInstanceClassLoading`
  - Testing using `nifi-mock` (`addControllerService`, `setProperty`, `assertValid`, `enableControllerService`)
- Examples: Minimal API/impl, service registration file, property descriptor, retrieval, Maven package and NAR POM highlights.

If you want, I can also add Javadoc anchors for specific classes (e.g., ControllerService, lifecycle annotations) or align examples to a specific NiFi version.
