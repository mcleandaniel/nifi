---
title: "NiFi Controller Services: A Developer's Guide"
author: "Gemini Research Assistant"
date: "2025-10-14"
---

# NiFi Controller Services: A Developer's Guide

## Introduction

Controller Services are a fundamental component in Apache NiFi, providing shared resources and configuration for other components like processors, reporting tasks, and even other controller services. <span id="claim-cs-purpose">They allow operators to configure complex or sensitive settings once and reuse them across the dataflow, promoting consistency and simplifying maintenance.</span> This document provides a comprehensive overview of Controller Services from a developer's perspective.

## Core Concepts

### The ControllerService Interface

The foundation of any controller service is the <span id="claim-cs-interface">`org.apache.nifi.controller.ControllerService`</span>` interface. While developers can implement this interface directly, it is more common to extend the <span id="claim-cs-abstract-class">`org.apache.nifi.controller.AbstractControllerService`</span>` base class, which provides default implementations for many of the required methods.

### Lifecycle and Annotations

A controller service has a well-defined lifecycle, managed by the NiFi framework. Developers can hook into this lifecycle by annotating methods in their controller service implementation with the following annotations:

-   `@OnAdded`: Called when the controller service is first added to the flow.
-   `@OnRemoved`: Called when the controller service is removed from the flow.
-   `@OnEnabled`: Called when the controller service is enabled.
-   `@OnDisabled`: Called when the controller service is disabled.
-   `@OnConfigurationRestored`: Called after the configuration of the controller service has been restored from a previous state.
-   `@OnPropertyModified`: Called when a property of the controller service is modified.

### Scope

Controller services can be defined at two different scopes:

-   **Process Group Level**: The service is available only to components within that process group and its descendants.
-   **Controller Level**: The service is available to all components in the flow, including other controller-level services and reporting tasks.

## Implementation Guide

### Creating a Custom Controller Service

To create a custom controller service, you typically extend `AbstractControllerService` and implement your service-specific logic.

```java
public class MyCustomService extends AbstractControllerService implements MyServiceApi {

    // ... implementation ...

}
```

### Defining Properties

Properties for a controller service are defined using the <span id="claim-cs-property-descriptor">`org.apache.nifi.components.PropertyDescriptor`</span>` class. You expose these properties to the NiFi framework by overriding the `getSupportedPropertyDescriptors` method.

```java
static final PropertyDescriptor MY_PROPERTY = new PropertyDescriptor.Builder()
        .name("My Property")
        .description("An example property.")
        .required(true)
        .addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
        .build();

@Override
protected List<PropertyDescriptor> getSupportedPropertyDescriptors() {
    return List.of(MY_PROPERTY);
}
```

### Validation

NiFi provides a set of standard validators in the <span id="claim-cs-validators">`org.apache.nifi.processor.util.StandardValidators`</span>` class. You can also create custom validators by implementing the `Validator` interface.

## Usage Guide

### Referencing from a Processor

A processor can reference a controller service by defining a `PropertyDescriptor` that identifies the service interface.

```java
static final PropertyDescriptor MY_SERVICE = new PropertyDescriptor.Builder()
    .name("My Service")
    .description("My custom controller service.")
    .identifiesControllerService(MyServiceApi.class)
    .required(true)
    .build();
```

### REST API Management

Controller services can be managed programmatically via the NiFi REST API. The key endpoints are:

-   `POST /nifi-api/process-groups/{id}/controller-services`: Create a new controller service.
-   `PUT /nifi-api/controller-services/{id}`: Update the configuration or state of a controller service.
-   `GET /nifi-api/controller-services/{id}`: Retrieve the details of a controller service.

## Packaging and Deployment

Controller services are packaged as NiFi Archives (NARs). A NAR file is a standard JAR file with a specific directory structure and a manifest file. The NAR is then placed in the `lib` directory of the NiFi installation.
