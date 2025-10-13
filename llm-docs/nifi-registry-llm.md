# NiFi Registry — LLM Notes

*Sources*: 
- `nifi-registry/nifi-registry-core/nifi-registry-docs/src/main/asciidoc/administration-guide.adoc`
- `nifi-registry/nifi-registry-core/nifi-registry-docs/src/main/asciidoc/user-guide.adoc`
(Reviewed 2025-10-13)

## Product Role
- Central repository for versioned NiFi flows and extension bundles (NARs, assets).
- Provides REST API/UI to manage buckets, flows, versions, users, policies, and bundle lifecycle.

## Administration Essentials
- **System Requirements & Install**: Java runtime, supported OS; unpack distribution, edit `conf/nifi-registry.properties`, start via `bin/nifi-registry.sh/cmd`.
- **Antivirus Exclusions**: Exclude `flow_storage`, `bundle_storage`, `database_repository`, `logs`, etc., to avoid IO contention.

### Security & Authentication
- **HTTPS/TLS**: Configure `nifi.registry.security.keystore`, `truststore`, types, passwords. Optional cipher suite include/exclude lists.
- **Authentication Options**:
  - Mutual TLS (client certs).
  - LDAP (bind DN, search filters).
  - Kerberos (SPNEGO).
  - OpenID Connect (OIDC) with external identity providers.
- **Authorization**:
  - `authorizers.xml` defines `StandardManagedAuthorizer` plus providers:
    - `FileUserGroupProvider`, `LdapUserGroupProvider`, or composite.
    - `FileAccessPolicyProvider` controls policies.
  - Set **Initial Admin Identity** for first secure startup (per auth mechanism).
  - Bucket policies allow fine-grained access delegation.
- **Identity Mapping**: Regex-based mapping for certificates or directory users.

### Sensitive Configuration
- Encrypt sensitive properties (DB passwords, keystore creds) using `encrypt-config`.
- Support for migrating sensitive property key, handling legacy configs.

### Runtime Configuration
- **Bootstrap** (`conf/bootstrap.conf`): memory, logging, diagnostics.
- **Proxy**: Configure reverse proxy headers (`X-ProxyHost`, `X-ProxyPort`) when fronted by load balancers.
- **Kerberos Service**: Set service principal, keytab for SPNEGO interactions.
- **Metadata Database**:
  - Default H2 (lightweight); instructions for password change, backup.
  - Production options: PostgreSQL, MySQL (JDBC URL, driver placement).
- **Persistence Providers**:
  - Flow persistence: filesystem, Git, database.
    - Git provider setup includes repo initialization, auth, handling data model versions.
  - Bundle persistence: filesystem or S3 (access/secret keys, bucket, region).
- **Event Hooks**: Trigger scripts or logging on flow/bundle events (shared properties, provider-specific config).
- **URL Aliasing**: Map friendly URLs to buckets/flows.
- **Backup & Recovery**: Strategy for metadata DB, flow persistence, bundle persistence, configuration files.

## User Operations (UI)
- **Browser Support**: Current & previous versions of major browsers.
- **Terminology**: Buckets (namespaces), Flows, Flow Versions, Bundles, Users, Groups.
- **Authentication**: Login via configured provider (cert, OIDC, etc.).
- **Navigating UI**:
  - Dashboard lists buckets & flows; sorting/filtering available.
  - Use search to find flows/users/bundles.
- **Manage Flows**:
  - View flow details, versions, commit history.
  - Import flow (from JSON snapshot), import new version, export version, delete flow.
- **Manage Buckets**:
  - Create, rename, delete; adjust visibility (public/private), enable bundle overwrites.
  - Bucket policies: create/delete, grant read/write version privileges.
- **Users & Groups**:
  - Add/edit/delete users, groups; assign special privileges (e.g., proxy).
  - Manage group membership via UI dialogs.
- **Bundles**:
  - Upload NAR bundles with coordinates, metadata; download or delete existing bundles.
  - Maintain bundle ID and version info for NiFi extension distribution.

## LLM Answer Tips
- For security setup questions, highlight keystore/truststore properties and identity providers (`login-identity-providers.xml`, `authorizers.xml`).
- When troubleshooting authentication, ensure Initial Admin Identity is set and provider configuration matches user directory.
- For flow versioning issues, mention persistence provider specifics (Git repo initialization, DB settings) and backup procedures.
- UI/usage queries: emphasize bucket-flow-version hierarchy and policies; mention ability to import/export snapshots for CI/CD.
- Bundles: clarify difference between flow versions (logic) and bundles (code artifacts). S3 provider requires AWS creds & bucket config.
- Database migrations: instruct to backup H2 before switching, configure JDBC drivers in `lib/`.

## Quick FAQs
1. **“How do I enable HTTPS?”** → Set `nifi.registry.security.keystore`, `truststore`, types, passwords; configure `nifi.registry.web.https.host/port`.
2. **“Add LDAP auth?”** → Configure `login-identity-providers.xml` with LDAP provider, map users/groups, adjust `authorizers.xml`.
3. **“Delegate bucket access?”** → Use bucket policies to assign read/write (versioning) rights to users/groups.
4. **“Where are flows stored?”** → Depends on persistence provider: filesystem path, Git repo, or database tables (`FLOW_STORAGE`, `BUCKETS`, etc.).
5. **“Upload a new bundle?”** → UI → Manage Bundles → Upload Bundle; provide coordinates; requires write access to target bucket.
