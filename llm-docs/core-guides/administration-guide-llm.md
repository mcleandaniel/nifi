# NiFi Administration Guide — LLM Notes

*Source*: `nifi-docs/src/main/asciidoc/administration-guide.adoc` (reviewed 2025-10-13)

## Purpose
- Reference for operators configuring, securing, and maintaining Apache NiFi deployments across single nodes and clusters.
- Covers lifecycle topics: install, configuration hardening, clustering, upgrades, diagnostics, and supporting utilities.

## Section Highlights
- **System Requirements**: Minimum Java 21; optional Python 3.9–3.12 for Python processors; supports Linux, Unix, Windows, macOS; modern browsers required for UI (`Current` and `Current - 1`).
- **Install & Start**: Unpack distribution, edit `conf/nifi.properties` (set `nifi.sensitive.props.key`), use `bin/nifi.sh` or `bin/nifi.cmd` with `start|stop|status|run`.
- **Configuration Best Practices**: Raise Linux `nofile` and `nproc` limits, widen ephemeral port range, reduce `TIME_WAIT`, disable swapping, mount repositories with `noatime`.
- **Port Configuration**: HTTP host/port blank by default; HTTPS host defaults to `localhost`, port `8443`; forwarding properties support privileged exposure; `nifi.remote.input.secure` toggles Site-to-Site protocol.
- **Security Configuration**: TLS requires keystore/truststore paths, types (`BCFKS`, `JKS`, `PEM`, `PKCS12`), and passwords; `nifi.web.https.host/port` enable HTTPS; support for certificate autoreload and cipher inclusions/exclusions.
- **User Authentication**: Configure `./conf/login-identity-providers.xml`; built-in providers include single-user, LDAP, Kerberos; restart required after changes; `nifi.security.user.login.identity.provider` selects active provider.
- **Multi-Tenant Authorization**: Governed by `authorizers.xml`; StandardManagedAuthorizer with user group provider and access policy provider; set Initial Admin Identity for first secure install; legacy conversion guidance included.
- **Encryption Configuration**: Details for content repository, provenance, and sensitive properties encryption; outlines KMS, master key handling, secret derivation, and `EncryptConfig` CLI usage.
- **Encrypted Passwords in Flows**: Explains flow.xml.gz handling and when sensitive values can be stored encrypted versus protected by master key.
- **Toolkit Administrative Utilities**: Summaries for CLI tools (e.g., `tls-toolkit`, `encrypt-config`, `flow-analyzer`) and their typical tasks.
- **Clustering**: Set `nifi.cluster.is.node=true`, configure node address and ports, ZK settings, flow election parameters; covers primary node concept, node status, and load balancing/S2S routing examples.
- **State Management**: `conf/state-management.xml` defines local and cluster state providers; providers include file-based and distributed options; properties tie provider IDs to runtime.
- **Bootstrap & JVM Settings**: `conf/bootstrap.conf` handles heap, GC logging, diagnostics automation; graceful shutdown controlled via `graceful.shutdown.seconds`.
- **Proxy Configuration**: Highlights using reverse proxies (NGINX examples), `X-ProxyHost` headers, and raw/HTTP Site-to-Site routing rules defined in `nifi.remote.route.*` properties.
- **Analytics Framework & System Properties**: Lists analytics engine toggles, reporting tasks, and an extensive table of `nifi.*` properties (repositories, queues, load balancing, web limits).
- **Upgrade Path**: Steps for stop/back up/merge configs, schema evolution, handling new properties, and migrating security/authorizer artifacts.
- **Diagnostics & JMX**: Using `bin/nifi.sh diagnostics --verbose`, log files, auto-diagnostics on shutdown, and accessing JMX metrics via REST `/system-diagnostics/jmx-metrics`.

## Key Configuration Artifacts
- `conf/nifi.properties`: Central runtime configuration (web ports, repos, security, clustering, load balancing, analytics).
- `conf/login-identity-providers.xml`: Defines credential brokers (single-user, LDAP, Kerberos, OpenID Connect SSO).
- `conf/authorizers.xml`: Declares user/group providers (file, LDAP) and policy providers; set Initial Admin and Node identities.
- `conf/state-management.xml`: Maps local (`local-provider`) and clustered (`cluster-provider`) state stores.
- `conf/bootstrap.conf`: JVM options, diagnostics-on-shutdown toggles, run-as user for Linux wrapper.
- `conf/bootstrap-notification-services.xml`: Optional email/HTTP notifications on lifecycle events (section referenced in upgrades).
- Repository directories (`content_repository`, `flowfile_repository`, `provenance_repository`, `state`): Exclude from antivirus scans to prevent IO stalls.

## Property Values Frequently Asked About
- Web defaults: `nifi.web.http.host` empty, `nifi.web.http.port` empty; `nifi.web.https.host=localhost`, `nifi.web.https.port=8443`.
- Site-to-Site: `nifi.remote.input.host`/`nifi.remote.input.socket.port` define RAW listeners; `nifi.remote.input.secure` selects HTTP vs HTTPS.
- Cluster: `nifi.cluster.node.protocol.port` default `11443`; `nifi.cluster.node.load.balance.port=6342` for load-balanced connections.
- Sensitive props: `nifi.sensitive.props.key` must be set manually; `nifi.sensitive.props.algorithm` defaults to `NIFI_PBKDF2_AES_GCM_256`.
- Diagnostics: `nifi.diagnostics.on.shutdown.enabled=false` by default; configure directory/retention for automatic dumps.
- Request throttling: `nifi.web.max.requests.per.second=30000`, access token limit 25/s, request timeout `60 secs`.

## LLM Answering Tips
- Map questions about “where do I configure X?” to the file list above, then cite relevant property names.
- For security/TLS issues, confirm both keystore/truststore paths and type-specific requirements (PEM needs `certificate`+`privateKey` pairs).
- When asked about enabling LDAP/OIDC, mention editing `login-identity-providers.xml` **and** restarting every node.
- For authorization troubleshooting, remind that `users.xml`/`authorizations.xml` are generated; Initial Admin set in `authorizers.xml`.
- Clustering answers should reference `nifi.cluster.*` properties plus ZooKeeper ensemble prerequisites (covered just after clustering section).
- Performance tuning: mention OS-level tuning (file handles, ports, swappiness, `noatime`) before JVM adjustments.
- Diagnostics and JMX endpoints require READ permission on system diagnostics resource.

## Cross-Doc Pointers
- **User Guide** explains how secured UI and restricted components appear to end users (link `user-guide.adoc` sections).
- **Developer Guide** provides extension-specific logging/provenance behavior referenced in logging and diagnostics sections.
- **NiFi In Depth** elaborates on repositories whose directories are referenced in antivirus exclusions and system properties.

## Anticipated FAQs
1. *How do I convert a standalone node into a cluster member?* → Set `nifi.cluster.is.node=true`, populate node address/ports, configure ZooKeeper connection string, restart all nodes.
2. *Where do I enable HTTPS and replace certificates?* → Update `nifi.security.*` keystore/truststore properties plus `nifi.web.https.*`; optional `nifi.security.autoreload.enabled=true` for hot reload.
3. *What files control user login and authorization?* → `login-identity-providers.xml` for credentials, `authorizers.xml` for policies/user-group providers; synchronize across cluster and restart.
4. *How can I throttle or protect the REST API?* → Use `nifi.web.max.requests.per.second`, `nifi.web.max.access.token.requests.per.second`, and request timeout; pair with proxy config if terminating TLS upstream.
5. *What should I back up before upgrading?* → `conf/`, repositories (`flowfile`, `content`, `provenance`, `state`), `work/` diagnostics as needed; follow upgrade checklist in chapter 19.
