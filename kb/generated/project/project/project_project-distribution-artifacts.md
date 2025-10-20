I’ve gathered sources from nifi-assembly and nifi-manifest, then wrote a verified, publication-ready doc with precise, line-anchored claims.

- Added: llm-docs/operations/distribution-and-assembly-artifacts.md

Highlights
- Covers assembly descriptors (core/common), packaging flows, and manifest generation.
- Every factual sentence is wrapped in a span and mapped to precise file:line locators.
- Shows runnable Maven commands for building assemblies and generating the runtime manifest.

What’s inside
- Assembly composition: dependencies.xml, core.xml, common.xml
- Packaging: maven-assembly-plugin executions, profiles for tar.gz and dir-only
- Manifests: extracting extension-manifest.xml from NARs, assembling nifi-manifests zip
- Runtime manifest: unpack manifests, generate JSON, defaults, and validation via IT
- Troubleshooting and tips with focused references

Want me to run a quick build to validate the artifacts now?
