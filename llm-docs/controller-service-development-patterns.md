---
title: "Controller Service Development Patterns"
scope: project
plan_id: project
topic_id: project_project-controller-service-development
category: development
priority: medium
tags:
  - controller-service
  - development
  - extension
claims:
  - id: claim-cs-overview-share-state
    summary: ControllerService shares functionality and state across the JVM.
    sources: [src-dev-guide-cs-overview]
  - id: claim-cs-no-ontrigger
    summary: Controller Services are not scheduled and have no onTrigger.
    sources: [src-dev-guide-cs-overview]
  - id: claim-cs-no-relationships
    summary: Controller Services have no Relationships and are used by other components.
    sources: [src-dev-guide-cs-overview]
  - id: claim-cs-interface-required
    summary: Controller Service must be an interface that extends ControllerService.
    sources: [src-dev-guide-cs-constraint1]
  - id: claim-cs-refer-by-interface
    summary: Components reference services only via interfaces extending ControllerService.
    sources: [src-dev-guide-cs-constraint1]
  - id: claim-cs-nar-api-parent
    summary: API and implementation reside in separate NARs; both depend on the API NAR.
    sources: [src-dev-guide-cs-nar-sharing]
  - id: claim-cs-obtain-lookup-or-identifies
    summary: Obtain services via ControllerServiceLookup or PropertyDescriptor.identifiesControllerService.
    sources: [src-dev-guide-interacting-1]
  - id: claim-cs-lookup-contexts
    summary: Where ControllerServiceLookup is obtained for each component type.
    sources: [src-dev-guide-interacting-2]
  - id: claim-cs-prefer-identifies
    summary: Using identifiesControllerService is the preferred approach.
    sources: [src-dev-guide-interacting-prefer]
  - id: claim-cs-ui-dropdown
    summary: The UI prompts users with a drop-down of configured services when a property identifies a ControllerService.
    sources: [src-dev-guide-ui-dropdown]
  - id: claim-cs-ascontrollerservice
    summary: Retrieve the configured service using PropertyValue.asControllerService.
    sources: [src-dev-guide-example-asControllerService]
  - id: claim-anno-onenabled-cs
    summary: @OnEnabled methods run when a Controller Service is enabled; may take ConfigurationContext or no args.
    sources: [src-dev-guide-onenabled]
  - id: claim-anno-onenabled-scope
    summary: @OnEnabled is ignored for Processors and ReportingTasks; enabling/disabling are lifecycle events for services.
    sources: [src-dev-guide-onenabled-scope]
  - id: claim-anno-onscheduled-not-for-cs
    summary: @OnScheduled is not honored for Controller Services.
    sources: [src-dev-guide-onscheduled]
  - id: claim-doc-annotations
    summary: CapabilityDescription and Tags document components and support UI filtering.
    sources: [src-dev-guide-doc-annotations]
  - id: claim-seealso
    summary: SeeAlso links related components and applies to Processor, ControllerService, ParameterProvider, ReportingTask.
    sources: [src-dev-guide-seealso]
  - id: claim-nar-plugin
    summary: NAR packaging uses nifi-nar-maven-plugin with packaging set to nar.
    sources: [src-dev-guide-nar-plugin]
  - id: claim-nar-one-dep
    summary: A NAR may declare only one dependency of type nar.
    sources: [src-dev-guide-nar-dependency]
  - id: claim-nar-services-file
    summary: Implementation module includes META-INF/services/org.apache.nifi.controller.ControllerService file.
    sources: [src-dev-guide-nar-layout-services-file]
  - id: claim-classloader-best-practice
    summary: Bundle Controller Service API in a parent NAR; do not package it with implementations or referencing components when instance classloading is required.
    sources: [src-dev-guide-classloader-issue]
  - id: claim-state-manager-availability
    summary: ControllerServiceInitializationContext exposes getStateManager for simple state management.
    sources: [src-dev-guide-state-manager]
  - id: claim-testing-nifi-mock
    summary: nifi-mock supports testing, including Controller Services, with TestRunner utilities.
    sources: [src-dev-guide-testing1, src-dev-guide-testing2]
sources:
  - id: src-dev-guide-cs-overview
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L1882-L1891"
  - id: src-dev-guide-cs-constraint1
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L1904-L1911"
  - id: src-dev-guide-cs-nar-sharing
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L1913-L1925"
  - id: src-dev-guide-interacting-1
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L1931-L1935"
  - id: src-dev-guide-interacting-2
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L1936-L1942"
  - id: src-dev-guide-interacting-prefer
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L1944-L1949"
  - id: src-dev-guide-ui-dropdown
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L1960-L1964"
  - id: src-dev-guide-example-asControllerService
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L1966-L1972"
  - id: src-dev-guide-onenabled
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L535-L552"
  - id: src-dev-guide-onenabled-scope
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L553-L558"
  - id: src-dev-guide-onscheduled
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L571-L575"
  - id: src-dev-guide-doc-annotations
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L860-L872"
  - id: src-dev-guide-seealso
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L912-L917"
  - id: src-dev-guide-nar-plugin
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L2413-L2437"
  - id: src-dev-guide-nar-dependency
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L2439-L2444"
  - id: src-dev-guide-nar-layout-services-file
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L2482-L2494"
  - id: src-dev-guide-classloader-issue
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L2603-L2612"
  - id: src-dev-guide-state-manager
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L685-L693"
  - id: src-dev-guide-testing1
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L2205-L2212"
  - id: src-dev-guide-testing2
    type: doc
    uri: nifi-docs/src/main/asciidoc/developer-guide.adoc
    locator: "L2245-L2261"
---

# Controller Service Development Patterns

## Introduction / Overview

<span id="claim-cs-overview-share-state">The `ControllerService` interface allows developers to share functionality and state across the JVM.</span>

<span id="claim-cs-no-ontrigger">Controller Services are not scheduled to run and do not define an `onTrigger` method.</span>

<span id="claim-cs-no-relationships">Controller Services do not have Relationships and are used by Processors, Reporting Tasks, and other Controller Services.</span>

This document explains how to design, annotate, test, and package custom Controller Services across a project, with verified references to the official developer guide.

## Concepts / Architecture

<span id="claim-cs-interface-required">A Controller Service must be defined as an interface that extends `ControllerService`.</span>

<span id="claim-cs-refer-by-interface">Components interact with a service only through interfaces that extend `ControllerService`.</span>

<span id="claim-cs-nar-api-parent">To enable sharing across NARs, place the service API and its implementation in separate NARs, and make both referencing and implementation NARs depend on the API NAR.</span>

### Obtaining Services

<span id="claim-cs-obtain-lookup-or-identifies">A service can be obtained using `ControllerServiceLookup` or by declaring a property using `PropertyDescriptor.Builder.identifiesControllerService`.</span>

<span id="claim-cs-lookup-contexts">`ControllerServiceLookup` is provided via each component’s initialization context (Processor, ControllerService, ParameterProvider, ReportingTask).</span>

<span id="claim-cs-prefer-identifies">Using `identifiesControllerService` on a property is the preferred approach for most cases.</span>

<span id="claim-cs-ui-dropdown">When a property identifies a `ControllerService`, the UI presents a drop‑down of configured services for selection.</span>

### Lifecycle and State

<span id="claim-anno-onenabled-cs">Methods annotated with `@OnEnabled` run when a Controller Service is enabled and may accept either no arguments or a single `ConfigurationContext`.</span>

<span id="claim-anno-onenabled-scope">For services, enabling and disabling are lifecycle events; `@OnEnabled` is ignored for Processors and Reporting Tasks.</span>

<span id="claim-anno-onscheduled-not-for-cs">Because Controller Services are not scheduled, `@OnScheduled` is not honored for them.</span>

<span id="claim-state-manager-availability">From `ControllerServiceInitializationContext`, services can call `getStateManager()` to store and retrieve simple state.</span>

### Documentation Annotations

<span id="claim-doc-annotations">Use `@CapabilityDescription` and `@Tags` to describe functionality and provide keywords that the UI uses for filtering.</span>

<span id="claim-seealso">Use `@SeeAlso` to link related components; it applies to Processors, ControllerServices, ParameterProviders, and ReportingTasks.</span>

### Packaging and Classloading

<span id="claim-nar-plugin">NiFi extensions are packaged as NAR artifacts using the `nifi-nar-maven-plugin` and `packaging` set to `nar`.</span>

<span id="claim-nar-one-dep">Each NAR may declare only one dependency of type `nar`; additional `nar` dependencies cause a build error.</span>

<span id="claim-nar-services-file">The implementation module includes a `META-INF/services/org.apache.nifi.controller.ControllerService` file that lists implementations.</span>

<span id="claim-classloader-best-practice">When using instance classloading, do not bundle a Controller Service API with its implementation or with referencing components; instead, put the API in a parent NAR to avoid classloading errors.</span>

## Implementation / Configuration

- Define a minimal API that extends `ControllerService` and expose only the operations consumers need.
- Implement the API in a separate module; add documentation annotations and lifecycle hooks.
- Register the implementation using Java’s service provider file under `META-INF/services`.
- Expose a property on consuming components using `identifiesControllerService(MyService.class)`.

Example: API interface

```java
package org.example.services;

import org.apache.nifi.controller.ControllerService;

public interface MyService extends ControllerService {
    String doWork(String input);
}
```

Example: Implementation with annotations and lifecycle

```java
package org.example.services.impl;

import org.apache.nifi.annotation.documentation.CapabilityDescription;
import org.apache.nifi.annotation.documentation.Tags;
import org.apache.nifi.annotation.lifecycle.OnEnabled;
import org.apache.nifi.controller.ConfigurationContext;
import org.example.services.MyService;

@Tags({"example", "service"})
@CapabilityDescription("Provides MyService operations for processors and other services.")
public class StandardMyService implements MyService {

    @OnEnabled
    public void onEnabled(final ConfigurationContext context) {
        // initialize connections, validate configuration, warm caches, etc.
    }

    @Override
    public String doWork(final String input) {
        return input == null ? "" : input.trim();
    }
}
```

Service registration file (`resources/META-INF/services/org.apache.nifi.controller.ControllerService`):

```
org.example.services.impl.StandardMyService
```

Consumer property and retrieval

```java
// Property definition on a Processor/Service/ReportingTask
public static final PropertyDescriptor MY_SERVICE = new PropertyDescriptor.Builder()
        .name("My Service")
        .description("Controller Service providing MyService")
        .required(true)
        .identifiesControllerService(MyService.class)
        .build();

// Accessing the configured service
final MyService myService = context.getProperty(MY_SERVICE).asControllerService(MyService.class);
```

## Usage / Examples

Add a service property and use it across components:

```java
// In onTrigger or equivalent usage point for the component
final MyService service = context.getProperty(MY_SERVICE).asControllerService(MyService.class);
final String result = service.doWork(" payload ");
```

Build and package modules with Maven:

```bash
# Build API JAR, API NAR, implementation JAR, and implementation NAR
mvn -B -ntp -DskipTests clean package
```

POM highlights for NAR modules:

```xml
<!-- Implementation NAR -->
<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.example</groupId>
  <artifactId>my-controller-service-nar</artifactId>
  <version>1.0.0</version>
  <packaging>nar</packaging>
  <dependencies>
    <!-- Depend on the API NAR as parent for classloader visibility -->
    <dependency>
      <groupId>org.example</groupId>
      <artifactId>my-controller-service-api-nar</artifactId>
      <version>${project.version}</version>
      <type>nar</type>
    </dependency>
  </dependencies>
  <!-- nifi-nar-maven-plugin is typically inherited from the parent -->
</project>
```

## Best Practices / Tips

- Keep the service API small; colocate only related APIs in the same API NAR to manage classloader scope.
- Prefer `identifiesControllerService` on properties over manual lookup for type safety and UI integration.
- Initialize external connections in `@OnEnabled` and release them during disable or removal; avoid `@OnScheduled` in services.
- Put the Controller Service API in a parent NAR; do not bundle the API with implementations or referencing components when instance classloading is used to avoid runtime errors.
- Register implementations via `META-INF/services/org.apache.nifi.controller.ControllerService` to ensure discovery.
- Document components using `@CapabilityDescription`, `@Tags`, and `@SeeAlso` to improve usability in the UI.

## Troubleshooting

- Missing service in UI drop‑down: verify the service API type on the property and that the implementation NAR is installed and active.
- ClassNotFound or skipped extension on startup: ensure the API is provided from a parent NAR and not packaged with implementations when using instance classloading.
- `@OnEnabled` not called: confirm the service validates successfully and is enabled; check bulletins for errors during enablement.
- Not discoverable: ensure the service registration file exists at `META-INF/services/org.apache.nifi.controller.ControllerService` and lists your implementation class.

## Testing

<span id="claim-testing-nifi-mock">Use `nifi-mock` with JUnit to add, configure, validate, and enable Controller Services under test using `TestRunner.addControllerService`, `setProperty`, `assertValid`, and `enableControllerService`.</span>

Example test snippet

```java
import org.apache.nifi.util.TestRunner;
import org.apache.nifi.util.TestRunners;
import org.example.services.MyService;
import org.example.services.impl.StandardMyService;

@Test
public void testServiceEnables() throws Exception {
    final TestRunner runner = TestRunners.newTestRunner(MyProcessor.class);

    final MyService service = new StandardMyService();
    runner.addControllerService("svc", service);
    runner.setProperty(service, /* PropertyDescriptor */ MY_PROP, "value");
    runner.assertValid(service);
    runner.enableControllerService(service);
}
```

## Reference / Related Docs

- Developer Guide sections on Controller Services, Component Annotations, Testing, and NAR packaging.
