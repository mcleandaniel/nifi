---
title: Security Response and Disclosure
topic_id: project_project-security-vulnerability-process
category: security
priority: high
tags: [security, vulnerability, governance]
sources:
  - id: src-security-md
    type: file
    path: SECURITY.md
  - id: src-authorizer-factorybean
    type: file
    path: nifi-framework-bundle/nifi-framework/nifi-authorizer/src/main/java/org/apache/nifi/authorization/AuthorizerFactoryBean.java
  - id: src-authorizer-factory
    type: file
    path: nifi-framework-bundle/nifi-framework/nifi-authorizer/src/main/java/org/apache/nifi/authorization/AuthorizerFactory.java
  - id: src-nifiprops
    type: file
    path: nifi-commons/nifi-properties/src/main/java/org/apache/nifi/util/NiFiProperties.java
  - id: src-authorizer-config
    type: file
    path: nifi-framework-bundle/nifi-framework/nifi-authorizer/src/main/java/org/apache/nifi/framework/configuration/AuthorizerConfiguration.java
  - id: src-authorizer-interface
    type: file
    path: nifi-framework-api/src/main/java/org/apache/nifi/authorization/Authorizer.java
  - id: src-access-policy-provider
    type: file
    path: nifi-framework-api/src/main/java/org/apache/nifi/authorization/AccessPolicyProvider.java
  - id: src-configurable-access-policy-provider
    type: file
    path: nifi-framework-api/src/main/java/org/apache/nifi/authorization/ConfigurableAccessPolicyProvider.java
  - id: src-user-group-provider
    type: file
    path: nifi-framework-api/src/main/java/org/apache/nifi/authorization/UserGroupProvider.java
  - id: src-configurable-user-group-provider
    type: file
    path: nifi-framework-api/src/main/java/org/apache/nifi/authorization/ConfigurableUserGroupProvider.java
  - id: src-single-user-authorizer
    type: file
    path: nifi-framework-bundle/nifi-framework-extensions/nifi-single-user-iaa-providers-bundle/nifi-single-user-iaa-providers/src/main/java/org/apache/nifi/authorization/single/user/SingleUserAuthorizer.java
  - id: src-single-user-login-identity-provider
    type: file
    path: nifi-framework-bundle/nifi-framework-extensions/nifi-single-user-iaa-providers-bundle/nifi-single-user-iaa-providers/src/main/java/org/apache/nifi/authentication/single/user/SingleUserLoginIdentityProvider.java
claims:
  claim-security-contact:
    summary: Report suspected vulnerabilities to the private security mailing list.
    sources:
      - source: src-security-md
        locator: "L42-L42"
  claim-pmc-monitors:
    summary: The PMC monitors the private security list and responds to disclosures.
    sources:
      - source: src-security-md
        locator: "L42-L43"
  claim-asf-policy-nondisclosure:
    summary: Vulnerabilities are not disclosed until a released version with a fix is available.
    sources:
      - source: src-security-md
        locator: "L47-L47"
  claim-publish-mailinglists:
    summary: Post-release, notices go to dev, users, announce, security, and oss-security mailing lists.
    sources:
      - source: src-security-md
        locator: "L48-L48"
  claim-publish-cve:
    summary: Post-release, an entry is published to the CVE database.
    sources:
      - source: src-security-md
        locator: "L49-L49"
  claim-publish-security-page:
    summary: Post-release, details appear on the Apache NiFi Security Page.
    sources:
      - source: src-security-md
        locator: "L50-L50"
  claim-authorizer-factorybean-purpose:
    summary: AuthorizerFactoryBean is the factory bean responsible for loading the configured Authorizer.
    sources:
      - source: src-authorizer-factorybean
        locator: "L60-L63"
  claim-authorizer-selection-property:
    summary: The selected authorizer is identified by the nifi.security.user.authorizer property.
    sources:
      - source: src-authorizer-factorybean
        locator: "L115-L117"
      - source: src-nifiprops
        locator: "L152-L152"
  claim-default-authorizer-when-no-ssl:
    summary: When no HTTPS port is configured, a default Authorizer is used.
    sources:
      - source: src-authorizer-factorybean
        locator: "L111-L114"
  claim-default-authorizer-approves-all:
    summary: The default Authorizer approves all authorization requests.
    sources:
      - source: src-authorizer-factorybean
        locator: "L450-L455"
  claim-authorizers-config-file-path:
    summary: The authorizers configuration file is nifi.authorizer.configuration.file or defaults to conf/authorizers.xml.
    sources:
      - source: src-nifiprops
        locator: "L62-L62"
      - source: src-nifiprops
        locator: "L634-L641"
      - source: src-nifiprops
        locator: "L338-L339"
  claim-authorizers-xml-validated:
    summary: The authorizers XML is validated against /authorizers.xsd and unmarshaled via JAXB.
    sources:
      - source: src-authorizer-factorybean
        locator: "L226-L236"
  claim-providers-and-authorizer-created:
    summary: UserGroupProvider, AccessPolicyProvider, and Authorizer instances are created from the configuration.
    sources:
      - source: src-authorizer-factorybean
        locator: "L124-L146"
  claim-install-integrity-checks:
    summary: The Authorizer is wrapped with integrity checks via AuthorizerFactory.installIntegrityChecks.
    sources:
      - source: src-authorizer-factorybean
        locator: "L155-L159"
      - source: src-authorizer-factory
        locator: "L115-L121"
  claim-no-duplicate-policies:
    summary: Integrity checks prevent multiple policies with the same resource and action.
    sources:
      - source: src-authorizer-factory
        locator: "L404-L409"
  claim-no-duplicate-users:
    summary: Integrity checks prevent multiple users with the same identity.
    sources:
      - source: src-authorizer-factory
        locator: "L412-L415"
  claim-no-duplicate-groups:
    summary: Integrity checks prevent multiple groups with the same name.
    sources:
      - source: src-authorizer-factory
        locator: "L419-L421"
  claim-authorizercontext-injection:
    summary: @AuthorizerContext enables NiFiProperties injection via method and field injection in providers and authorizers.
    sources:
      - source: src-authorizer-factorybean
        locator: "L395-L411"
      - source: src-authorizer-factorybean
        locator: "L421-L436"
  claim-bean-singleton:
    summary: AuthorizerFactoryBean produces a singleton.
    sources:
      - source: src-authorizer-factorybean
        locator: "L476-L479"
  claim-authorizer-config-wiring:
    summary: AuthorizerConfiguration wires AuthorizerFactoryBean with NiFiProperties and ExtensionManager.
    sources:
      - source: src-authorizer-config
        locator: "L45-L50"
  claim-authorizer-interface:
    summary: Authorizer implementations expose authorize(request) and lifecycle methods.
    sources:
      - source: src-authorizer-interface
        locator: "L26-L39"
      - source: src-authorizer-interface
        locator: "L41-L61"
  claim-access-policy-provider-api:
    summary: AccessPolicyProvider exposes read operations and a UserGroupProvider reference.
    sources:
      - source: src-access-policy-provider
        locator: "L33-L67"
  claim-configurable-access-policy-provider-api:
    summary: ConfigurableAccessPolicyProvider adds add, update, and delete operations for access policies.
    sources:
      - source: src-configurable-access-policy-provider
        locator: "L74-L107"
  claim-configurable-user-group-provider-api:
    summary: ConfigurableUserGroupProvider adds add, update, and delete operations for users and groups.
    sources:
      - source: src-configurable-user-group-provider
        locator: "L75-L109"
      - source: src-configurable-user-group-provider
        locator: "L119-L153"
  claim-single-user-authorizer-approves:
    summary: SingleUserAuthorizer authorizes all requests.
    sources:
      - source: src-single-user-authorizer
        locator: "L70-L73"
  claim-single-user-authorizer-requires-provider:
    summary: SingleUserAuthorizer requires SingleUserLoginIdentityProvider when selected.
    sources:
      - source: src-single-user-authorizer
        locator: "L84-L95"
  claim-sua-class-name:
    summary: The class name for the Single User Authorizer is org.apache.nifi.authorization.single.user.SingleUserAuthorizer.
    sources:
      - source: src-single-user-authorizer
        locator: "L47-L47"
  claim-sulip-class-name:
    summary: The class name for the Single User Login Identity Provider is org.apache.nifi.authentication.single.user.SingleUserLoginIdentityProvider.
    sources:
      - source: src-single-user-login-identity-provider
        locator: "L45-L45"
  claim-secure-requires-authorizer-identifier:
    summary: When running securely, the authorizer identifier must be specified; otherwise initialization fails.
    sources:
      - source: src-authorizer-factorybean
        locator: "L118-L121"
  claim-missing-authorizers-file-error:
    summary: If the authorizers configuration file is missing or invalid, initialization throws an error.
    sources:
      - source: src-authorizer-factorybean
        locator: "L231-L236"
  claim-duplicate-identifiers-error:
    summary: Duplicate identifiers for providers or authorizers in the configuration cause startup errors.
    sources:
      - source: src-authorizer-factorybean
        locator: "L126-L129"
      - source: src-authorizer-factorybean
        locator: "L134-L138"
      - source: src-authorizer-factorybean
        locator: "L142-L146"
  claim-no-duplicate-policies-usage:
    summary: Integrity checks enforce no duplicate resource-action access policies.
    sources:
      - source: src-authorizer-factory
        locator: "L404-L409"
  claim-single-user-authorizer-requires-provider-troubleshooting:
    summary: Selecting SingleUserAuthorizer without the required Single User Login Identity Provider causes initialization to fail.
    sources:
      - source: src-single-user-authorizer
        locator: "L90-L95"
---

# Introduction / Overview

<span id="claim-security-contact">Report suspected vulnerabilities to the private security mailing list at security@nifi.apache.org.</span>

<span id="claim-pmc-monitors">Members of the Project Management Committee monitor the private security list and respond to disclosures.</span>

<span id="claim-asf-policy-nondisclosure">NiFi follows ASF security policy and does not publicly disclose a vulnerability until a fixed release is available.</span>

<span id="claim-publish-mailinglists">After a fix is released, announcements go to dev@nifi.apache.org, users@nifi.apache.org, announce@apache.org, security@nifi.apache.org, and oss-security@lists.openwall.com.</span>

<span id="claim-publish-cve">A corresponding entry is published to the CVE database.</span>

<span id="claim-publish-security-page">Details are also posted on the Apache NiFi Security Page.</span>


# Concepts / Architecture

<span id="claim-authorizer-factorybean-purpose">AuthorizerFactoryBean is the factory component responsible for loading the configured Authorizer.</span>

<span id="claim-authorizer-selection-property">The active authorizer is selected by the `nifi.security.user.authorizer` property.</span>

<span id="claim-default-authorizer-when-no-ssl">When no HTTPS port is configured, NiFi uses a built-in default authorizer instead of a configured one.</span> <span id="claim-default-authorizer-approves-all">That default authorizer approves all authorization requests.</span>

<span id="claim-authorizers-config-file-path">The authorizers configuration file is set by `nifi.authorizer.configuration.file` and defaults to `conf/authorizers.xml`.</span>

<span id="claim-authorizers-xml-validated">NiFi validates the authorizers XML against `/authorizers.xsd` and unmarshals it with JAXB.</span>

<span id="claim-providers-and-authorizer-created">From that configuration, NiFi creates UserGroupProvider, AccessPolicyProvider, and Authorizer instances.</span>

<span id="claim-install-integrity-checks">NiFi wraps the Authorizer with integrity checks using `AuthorizerFactory.installIntegrityChecks`.</span> <span id="claim-no-duplicate-policies">These checks prevent duplicate policies for the same resource and action.</span> <span id="claim-no-duplicate-users">They prevent multiple users with the same identity.</span> <span id="claim-no-duplicate-groups">They prevent multiple groups with the same name.</span>

<span id="claim-authorizercontext-injection">Providers and authorizers can receive `NiFiProperties` via `@AuthorizerContext` using method or field injection.</span>

<span id="claim-bean-singleton">The configured Authorizer bean is a singleton within the application context.</span>

<span id="claim-authorizer-interface">Authorizers implement `authorize(request)` along with initialize, configure, and pre-destruction lifecycle methods.</span>

<span id="claim-access-policy-provider-api">AccessPolicyProvider exposes read operations for policies and provides access to the associated UserGroupProvider.</span>

<span id="claim-configurable-access-policy-provider-api">ConfigurableAccessPolicyProvider adds create, update, and delete operations for access policies.</span>

<span id="claim-configurable-user-group-provider-api">ConfigurableUserGroupProvider adds create, update, and delete operations for users and groups.</span>

<span id="claim-single-user-authorizer-approves">SingleUserAuthorizer authorizes all requests unconditionally.</span> <span id="claim-single-user-authorizer-requires-provider">When selected, it requires the Single User Login Identity Provider to be configured.</span>


# Implementation / Configuration

- Configure the active authorizer in `nifi.properties`:

  ```properties
  # Select the configured Authorizer by identifier
  nifi.security.user.authorizer=managed-authorizer

  # Use a custom authorizers file (optional)
  nifi.authorizer.configuration.file=conf/authorizers.xml
  ```

- Example: declare a single-user authorizer in `conf/authorizers.xml` and select it via `nifi.security.user.authorizer`:

  ```xml
  <authorizers>
    <authorizer>
      <identifier>single-user-authorizer</identifier>
      <class>org.apache.nifi.authorization.single.user.SingleUserAuthorizer</class>
    </authorizer>
  </authorizers>
  ```

  Then set in `nifi.properties`:

  ```properties
  nifi.security.user.authorizer=single-user-authorizer
  ```

- <span id="claim-authorizer-config-wiring">AuthorizerFactoryBean is wired with `NiFiProperties` and `ExtensionManager` by the `AuthorizerConfiguration` Spring configuration.</span>


# Usage / Examples

- Show current authorizer selection and authorizers file path:

  ```bash
  PROPS="${NIFI_HOME:-.}/conf/nifi.properties"; \
  awk -F= '/^nifi.security.user.authorizer=|^nifi.authorizer.configuration.file=/{print $1 "=" $2}' "$PROPS"
  ```

- Validate that Single User mode is correctly paired:

  - <span id="claim-sua-class-name">Selected authorizer uses class `org.apache.nifi.authorization.single.user.SingleUserAuthorizer`.</span>
  - <span id="claim-sulip-class-name">Login Identity Provider class is `org.apache.nifi.authentication.single.user.SingleUserLoginIdentityProvider`.</span>

- <span id="claim-no-duplicate-policies-usage">List configured access policies and ensure no duplicate resource-action pairs; integrity checks enforce this.</span>


# Best Practices / Tips

- Keep the authorizers configuration under version control and restrict write access to it.
- Use ManagedAuthorizer and the provided file-based providers for environments that require policy versioning and review.
- In production, ensure HTTPS is configured so a non-default authorizer is engaged.


# Troubleshooting

- <span id="claim-secure-requires-authorizer-identifier">Secure deployments require an authorizer identifier; startup fails if it is missing.</span>
- <span id="claim-missing-authorizers-file-error">If `conf/authorizers.xml` is missing or malformed, initialization fails when loading the configuration.</span>
- <span id="claim-duplicate-identifiers-error">Duplicate identifiers in user group providers, access policy providers, or authorizers cause startup errors.</span>
- <span id="claim-single-user-authorizer-requires-provider-troubleshooting">Selecting SingleUserAuthorizer without the required Single User Login Identity Provider results in an initialization error.</span>


# Reference / Related Docs

- Security policy and contact: `SECURITY.md`.
- Authorization code and configuration APIs: `nifi-framework-api` and `nifi-framework-bundle/nifi-framework/nifi-authorizer`.
