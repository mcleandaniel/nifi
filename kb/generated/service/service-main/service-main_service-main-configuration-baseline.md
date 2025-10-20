---
title: Core Configuration Baseline
scope: service
plan_id: service-main
topic_id: service-main_service-main-configuration-baseline
category: operations
priority: high
tags:
  - configuration
  - nifi.properties
  - operations

claims:
  - id: claim-nifi-props-core-edit
    sources:
      - source_id: src-admin-guide
        locator: "L46"
  - id: claim-bootstrap-purpose
    sources:
      - source_id: src-admin-guide
        locator: "L2673-L2684"
  - id: claim-authorizer-props
    sources:
      - source_id: src-admin-guide
        locator: "L802-L805"
  - id: claim-login-providers-props-config-file
    sources:
      - source_id: src-admin-guide
        locator: "L370"
  - id: claim-login-providers-props-selected
    sources:
      - source_id: src-admin-guide
        locator: "L372-L377"
  - id: claim-state-mgmt-props
    sources:
      - source_id: src-admin-guide
        locator: "L2896-L2900"
  - id: claim-state-mgmt-xml-id
    sources:
      - source_id: src-state-management-xml
        locator: "L17-L21"
  - id: claim-flowfile-repo-purpose
    sources:
      - source_id: src-admin-guide
        locator: "L2916-L2924"
  - id: claim-flowfile-repo-dir-default
    sources:
      - source_id: src-admin-guide
        locator: "L2942"
  - id: claim-content-repo-purpose
    sources:
      - source_id: src-admin-guide
        locator: "L2969-L2973"
  - id: claim-content-repo-dir-default
    sources:
      - source_id: src-admin-guide
        locator: "L2990"
  - id: claim-prov-repo-purpose
    sources:
      - source_id: src-admin-guide
        locator: "L3019"
  - id: claim-prov-repo-dir-default
    sources:
      - source_id: src-admin-guide
        locator: "L3038"
  - id: claim-ports-defaults-table
    sources:
      - source_id: src-admin-guide
        locator: "L98-L110"
  - id: claim-cluster-node-protocol-port-blank
    sources:
      - source_id: src-admin-guide
        locator: "L3614-L3616"
  - id: claim-load-balance-port
    sources:
      - source_id: src-admin-guide
        locator: "L3639"
  - id: claim-loopback-default
    sources:
      - source_id: src-admin-guide
        locator: "L73"
  - id: claim-s2s-host
    sources:
      - source_id: src-admin-guide
        locator: "L3190"
  - id: claim-s2s-secure
    sources:
      - source_id: src-admin-guide
        locator: "L3191"
  - id: claim-s2s-socket-blank
    sources:
      - source_id: src-admin-guide
        locator: "L3192"
  - id: claim-s2s-http-enabled
    sources:
      - source_id: src-admin-guide
        locator: "L3193-L3194"
  - id: claim-security-keystores
    sources:
      - source_id: src-admin-guide
        locator: "L280-L304"
  - id: claim-enable-https
    sources:
      - source_id: src-admin-guide
        locator: "L308-L314"
  - id: claim-http-https-exclusive
    sources:
      - source_id: src-admin-guide
        locator: "L314-L316"
  - id: claim-authorizers-users-file
    sources:
      - source_id: src-authorizers-xml
        locator: "L53"
  - id: claim-authorizers-authz-file
    sources:
      - source_id: src-authorizers-xml
        locator: "L263"
  - id: claim-managed-authorizer-id
    sources:
      - source_id: src-authorizers-xml
        locator: "L278-L280"
  - id: claim-initial-admin-identity
    sources:
      - source_id: src-admin-guide
        locator: "L952-L955"
  - id: claim-login-default-single-user
    sources:
      - source_id: src-admin-guide
        locator: "L372-L377"
  - id: claim-sensitive-props-required
    sources:
      - source_id: src-admin-guide
        locator: "L3965"
  - id: claim-restart-required
    sources:
      - source_id: src-admin-guide
        locator: "L504-L506"
  - id: claim-zk-connect-string
    sources:
      - source_id: src-admin-guide
        locator: "L3654-L3660"
  - id: claim-embedded-zk-props
    sources:
      - source_id: src-admin-guide
        locator: "L2899-L2900"
  - id: claim-zk-data-dir-default
    sources:
      - source_id: src-zookeeper-properties
        locator: "L27"
  - id: claim-bootstrap-allow-restricted
    sources:
      - source_id: src-bootstrap-conf
        locator: "L38-L39"
  - id: claim-flow-config-default
    sources:
      - source_id: src-admin-guide
        locator: "L2852"

sources:
  - id: src-admin-guide
    type: file
    title: NiFi System Administrator's Guide (source tree)
    path: nifi-docs/src/main/asciidoc/administration-guide.adoc
  - id: src-nifi-properties
    type: file
    title: nifi.properties (template)
    path: nifi-framework-bundle/nifi-framework/nifi-resources/src/main/resources/conf/nifi.properties
  - id: src-authorizers-xml
    type: file
    title: authorizers.xml (template)
    path: nifi-framework-bundle/nifi-framework/nifi-resources/src/main/resources/conf/authorizers.xml
  - id: src-login-identity-providers-xml
    type: file
    title: login-identity-providers.xml (template)
    path: nifi-framework-bundle/nifi-framework/nifi-resources/src/main/resources/conf/login-identity-providers.xml
  - id: src-state-management-xml
    type: file
    title: state-management.xml (template)
    path: nifi-framework-bundle/nifi-framework/nifi-resources/src/main/resources/conf/state-management.xml
  - id: src-bootstrap-conf
    type: file
    title: bootstrap.conf (template)
    path: nifi-framework-bundle/nifi-framework/nifi-resources/src/main/resources/conf/bootstrap.conf
  - id: src-zookeeper-properties
    type: file
    title: zookeeper.properties (template)
    path: nifi-framework-bundle/nifi-framework/nifi-resources/src/main/resources/conf/zookeeper.properties
---

**Introduction / Overview**
- <span id="claim-nifi-props-core-edit">NiFi requires editing `conf/nifi.properties` to set core values such as the Sensitive Properties Key before first use.</span>
- <span id="claim-bootstrap-purpose">`conf/bootstrap.conf` configures how the JVM and process start (heap sizes, Java command, directories, shutdown delay) and takes effect after restart.</span>
- <span id="claim-authorizer-props">Authorization is configured via `nifi.authorizer.configuration.file` and `nifi.security.user.authorizer` in `nifi.properties` to select an authorizer defined in `authorizers.xml`.</span>
- <span id="claim-login-providers-props-config-file">Authentication providers are configured in a file referenced by `nifi.login.identity.provider.configuration.file`.</span> <span id="claim-login-providers-props-selected">The active login provider is selected in `nifi.properties` using `nifi.security.user.login.identity.provider` (default `single-user-provider`).</span>
- <span id="claim-state-mgmt-props">Local and cluster state providers are configured in a file referenced by `nifi.state.management.configuration.file`, with provider IDs selected by `nifi.state.management.provider.local`/`provider.cluster`.</span> <span id="claim-state-mgmt-xml-id">Provider identifiers must be declared in `state-management.xml` and referenced from `nifi.properties`.</span>

**Concepts / Architecture**
- <span id="claim-flowfile-repo-purpose">FlowFile Repository tracks each FlowFile’s attributes and state and is persisted on disk by default.</span>
- <span id="claim-content-repo-purpose">Content Repository stores the content bytes for FlowFiles and should be on a different disk than the FlowFile Repository to reduce risk.</span>
- <span id="claim-prov-repo-purpose">Provenance Repository records data provenance events for the flow.</span>
- <span id="claim-flowfile-repo-dir-default">The FlowFile Repository directory defaults to `./flowfile_repository` (`nifi.flowfile.repository.directory`).</span>
- <span id="claim-content-repo-dir-default">The Content Repository directory defaults to `./content_repository` (`nifi.content.repository.directory.default`).</span>
- <span id="claim-prov-repo-dir-default">The Provenance Repository directory defaults to `./provenance_repository` (`nifi.provenance.repository.directory.default`).</span>
- <span id="claim-ports-defaults-table">Key ports are configured in `nifi.properties`, including HTTPS UI (`nifi.web.https.port` default `8443`) and optional Site-to-Site RAW socket (`nifi.remote.input.socket.port`) and cluster protocol (`nifi.cluster.node.protocol.port`).</span>
- <span id="claim-load-balance-port">Cluster load balancing uses `nifi.cluster.load.balance.port` (default `6342`).</span>
- <span id="claim-cluster-node-protocol-port-blank">The node protocol port (`nifi.cluster.node.protocol.port`) is blank by default and must be set for clustering.</span>
- <span id="claim-loopback-default">Without security configuration, NiFi binds the UI to `127.0.0.1` and recommends configuring HTTPS to use other interfaces.</span>
- <span id="claim-s2s-host">Site-to-Site advertises `nifi.remote.input.host` to clients.</span> <span id="claim-s2s-secure">Secure Site-to-Site is controlled by `nifi.remote.input.secure`.</span> <span id="claim-s2s-socket-blank">RAW transport requires setting `nifi.remote.input.socket.port` (blank by default).</span> <span id="claim-s2s-http-enabled">HTTP Site-to-Site is enabled with `nifi.remote.input.http.enabled` and uses HTTPS/HTTP based on `nifi.remote.input.secure` and `nifi.web.https.port`/`nifi.web.http.port`.</span>
- <span id="claim-security-keystores">HTTPS requires configuring keystore and truststore properties (`nifi.security.keystore*`, `nifi.security.truststore*`) with supported types.</span>
- <span id="claim-enable-https">Enabling HTTPS uses `nifi.web.https.host` and `nifi.web.https.port`, with optional network interface selectors.</span> <span id="claim-http-https-exclusive">HTTP and HTTPS are mutually exclusive and the HTTP port must be unset when HTTPS is enabled.</span>
- <span id="claim-authorizers-users-file">The default user/group store is `./conf/users.xml` via `FileUserGroupProvider`.</span> <span id="claim-authorizers-authz-file">Access policies persist in `./conf/authorizations.xml` via `FileAccessPolicyProvider`.</span> <span id="claim-managed-authorizer-id">The default authorizer is `StandardManagedAuthorizer` with identifier `managed-authorizer`.</span>
- <span id="claim-initial-admin-identity">A new secured instance must set an Initial Admin Identity in `authorizers.xml`, after which NiFi creates users and policies on restart.</span>
- <span id="claim-login-default-single-user">The Single User Login Identity Provider is available by default and selected with `nifi.security.user.login.identity.provider=single-user-provider`.</span>

**Implementation / Configuration**
- <span id="claim-sensitive-props-required">Set `nifi.sensitive.props.key` in `nifi.properties` because NiFi requires a Sensitive Properties Key.</span>
- <span id="claim-flow-config-default">The flow configuration file defaults to `./conf/flow.json.gz` (`nifi.flow.configuration.file`).</span>
- <span id="claim-security-keystores">Configure TLS keystore and truststore properties before enabling HTTPS.</span>
- <span id="claim-enable-https">Set `nifi.web.https.port` (and optionally `nifi.web.https.host`) to expose the UI over HTTPS.</span> <span id="claim-http-https-exclusive">Unset `nifi.web.http.port` when HTTPS is enabled.</span>
- <span id="claim-authorizer-props">Set `nifi.authorizer.configuration.file=./conf/authorizers.xml` and `nifi.security.user.authorizer=managed-authorizer` to use the managed authorizer.</span>
- <span id="claim-initial-admin-identity">Add an Initial Admin Identity (or Group) to `authorizers.xml`, then restart NiFi to bootstrap admin access.</span>
- <span id="claim-login-providers-props-config-file">Ensure `nifi.login.identity.provider.configuration.file=./conf/login-identity-providers.xml` is set.</span> <span id="claim-login-providers-props-selected">Use `nifi.security.user.login.identity.provider` to select `single-user-provider`, LDAP, or Kerberos providers.</span>
- <span id="claim-flowfile-repo-dir-default">Review repository locations and set them to external paths where appropriate.</span>
- <span id="claim-s2s-socket-blank">Set `nifi.remote.input.socket.port` for RAW Site-to-Site or use HTTP S2S with `nifi.remote.input.http.enabled`.</span>
- <span id="claim-zk-connect-string">For clustering, set `nifi.zookeeper.connect.string` to the ZooKeeper quorum.</span> <span id="claim-cluster-node-protocol-port-blank">Set `nifi.cluster.is.node=true` and configure `nifi.cluster.node.protocol.port` on each node.</span> <span id="claim-load-balance-port">Optionally enable `nifi.cluster.load.balance.port` for intra-cluster load balancing.</span>
- <span id="claim-state-mgmt-props">Point `nifi.state.management.configuration.file` to `./conf/state-management.xml` and set provider IDs to match elements in that file.</span> <span id="claim-embedded-zk-props">If running embedded ZooKeeper, set `nifi.state.management.embedded.zookeeper.start=true` and configure `nifi.state.management.embedded.zookeeper.properties`.</span> <span id="claim-zk-data-dir-default">The embedded ZooKeeper default `dataDir` is `./state/zookeeper` in `conf/zookeeper.properties`.</span>
- <span id="claim-bootstrap-allow-restricted">In clusters, keep `-Dsun.net.http.allowRestrictedHeaders=true` in `bootstrap.conf` for node communications.</span>

Usage / Examples
- <span id="claim-enable-https">Minimal secure single-user baseline sets TLS and HTTPS UI properties in `nifi.properties`.</span>
```
# conf/nifi.properties (excerpt)
nifi.sensitive.props.key=REPLACE_WITH_12+_CHARS
nifi.security.keystore=/opt/nifi/certs/keystore.p12
nifi.security.keystoreType=PKCS12
nifi.security.keystorePasswd=changeit
nifi.security.truststore=/opt/nifi/certs/truststore.p12
nifi.security.truststoreType=PKCS12
nifi.security.truststorePasswd=changeit

nifi.web.https.host=0.0.0.0
nifi.web.https.port=8443
nifi.web.http.port=

nifi.authorizer.configuration.file=./conf/authorizers.xml
nifi.security.user.authorizer=managed-authorizer
nifi.login.identity.provider.configuration.file=./conf/login-identity-providers.xml
nifi.security.user.login.identity.provider=single-user-provider
```
- <span id="claim-initial-admin-identity">Seed an Initial Admin Identity and use file-backed providers in `authorizers.xml`.</span>
```
<!-- conf/authorizers.xml (excerpt) -->
<userGroupProvider>
  <identifier>file-user-group-provider</identifier>
  <class>org.apache.nifi.authorization.FileUserGroupProvider</class>
  <property name="Users File">./conf/users.xml</property>
  <property name="Initial User Identity 1">CN=Admin, OU=Ops, O=Example, L=City, ST=ST, C=US</property>
</userGroupProvider>

<accessPolicyProvider>
  <identifier>file-access-policy-provider</identifier>
  <class>org.apache.nifi.authorization.FileAccessPolicyProvider</class>
  <property name="User Group Provider">file-user-group-provider</property>
  <property name="Authorizations File">./conf/authorizations.xml</property>
  <property name="Initial Admin Identity">CN=Admin, OU=Ops, O=Example, L=City, ST=ST, C=US</property>
</accessPolicyProvider>

<authorizer>
  <identifier>managed-authorizer</identifier>
  <class>org.apache.nifi.authorization.StandardManagedAuthorizer</class>
  <property name="Access Policy Provider">file-access-policy-provider</property>
</authorizer>
```
- <span id="claim-state-mgmt-props">Select state providers by ID in `nifi.properties` with definitions in `state-management.xml`.</span>
```
# conf/nifi.properties (excerpt)
nifi.state.management.configuration.file=./conf/state-management.xml
nifi.state.management.provider.local=local-provider
nifi.state.management.provider.cluster=zk-provider

<!-- conf/state-management.xml (excerpt) -->
<local-provider>
  <id>local-provider</id>
  <class>org.apache.nifi.controller.state.providers.local.WriteAheadLocalStateProvider</class>
  <property name="Directory">/nifi/state/local</property>
</local-provider>

<cluster-provider>
  <id>zk-provider</id>
  <class>org.apache.nifi.controller.state.providers.zookeeper.ZooKeeperStateProvider</class>
  <property name="Connect String">zk1:2181,zk2:2181,zk3:2181</property>
</cluster-provider>
```

**Best Practices / Tips**
- <span id="claim-content-repo-purpose">Keep Content and FlowFile Repositories on different disks to avoid corruption under high volume.</span>
- <span id="claim-restart-required">Restart NiFi after changes to `nifi.properties` or `login-identity-providers.xml` and keep configurations identical across cluster nodes.</span>
- <span id="claim-bootstrap-allow-restricted">Retain `allowRestrictedHeaders` in `bootstrap.conf` for cluster communications.</span>
- <span id="claim-zk-connect-string">Use a full ZooKeeper quorum `nifi.zookeeper.connect.string` for clustering stability.</span>

**Troubleshooting**
- <span id="claim-loopback-default">If the UI is only reachable on `127.0.0.1`, configure HTTPS and bind to a non-loopback host.</span>
- <span id="claim-s2s-socket-blank">If RAW Site-to-Site fails, set `nifi.remote.input.socket.port` and ensure firewall rules allow it.</span>
- <span id="claim-s2s-http-enabled">If HTTP Site-to-Site fails, verify `nifi.remote.input.http.enabled` and that HTTP vs HTTPS matches `nifi.remote.input.secure`.</span>
- <span id="claim-initial-admin-identity">If access is denied on a new secure instance, set Initial Admin Identity in `authorizers.xml` and restart.</span>
- <span id="claim-zk-connect-string">If clustering fails, verify `nifi.zookeeper.connect.string` is correct and reachable.</span>
- <span id="claim-embedded-zk-props">For embedded ZooKeeper, verify the embedded flags and `conf/zookeeper.properties` reference are set.</span>

**Reference / Related Docs**
- <span id="claim-ports-defaults-table">Port configuration and defaults are summarized in the Administrator’s Guide.</span>
- <span id="claim-security-keystores">TLS properties and HTTPS enablement are covered in Security Configuration.</span>
- <span id="claim-authorizer-props">Authorization concepts and file locations are detailed under Authorizer Configuration.</span>
- <span id="claim-state-mgmt-props">State providers and embedded ZooKeeper settings are documented in State Management.</span>
