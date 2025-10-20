Created verified documentation with precise sources and runnable examples.

- File: llm-docs/docker-and-container-delivery.md
- Contents:
  - Introduction/Overview, Concepts/Architecture, Implementation/Configuration
  - Usage/Examples (standalone, TLS+LDAP, clustering, toolkit)
  - Best Practices, Troubleshooting, Reference/Related Docs
  - All verifiable statements annotated with inline <span id="claim-..."> and mapped to sources + exact locators
  - Sources point to repository files with line ranges (Dockerfile, README, and shell scripts)

Highlights
- Build: NIFI_VERSION build-arg, base image details, toolkit inclusion and env paths.
- Runtime: JVM heap/debug flags, HTTPS-by-default, proxy guidance, volumes, exposed ports.
- Auth: Single User, TLS, LDAP, OIDC with exact env-to-config mappings.
- Cluster: nifi.properties and state-management.xml mappings for ZK and node properties.

Want me to add a docker-compose.yml example (single-node and clustered) to complement the docs?
