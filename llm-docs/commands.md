---
title: "A Developer's Guide to the NiFi CLI"
author: "Gemini Research Assistant"
date: "2025-10-14"
summary: "A comprehensive guide to the commands available in the Apache NiFi Toolkit CLI."
category: "Developer Guide"
audience: ["Developers", "Operators"]
context: "Apache NiFi Toolkit 2.0.0-SNAPSHOT"
verified_against: "NiFi 2.0.0-SNAPSHOT"
dependencies: ["NiFi API", "NiFi Framework"]
related_docs: []
claims:
  claim-nifi-cli-purpose:
    sources:
      - id: src-nifi-toolkit-docs
        locator: "#nifi_cli"
  claim-nifi-command-group:
    sources:
      - id: src-nifi-command-group-java
        locator: "L155"
sources:
  src-nifi-toolkit-docs:
    title: "Apache NiFi Toolkit Guide"
    href: "https://nifi.apache.org/docs/nifi-docs/html/toolkit-guide.html"
  src-nifi-command-group-java:
    title: "NiFiCommandGroup.java"
    href: "nifi-toolkit/nifi-toolkit-cli/src/main/java/org/apache/nifi/toolkit/cli/impl/command/nifi/NiFiCommandGroup.java"
---

# A Developer's Guide to the NiFi CLI

## Introduction

<span id="claim-nifi-cli-purpose">The Apache NiFi Toolkit includes a Command Line Interface (CLI) that enables administrators and developers to interact with NiFi and NiFi Registry instances to automate tasks.</span> This guide provides a detailed overview of the commands available in the NiFi CLI.

## The `nifi` Command Group

<span id="claim-nifi-command-group">The `nifi` command group provides a wide range of commands for managing a NiFi instance.</span> These commands are organized into several sub-groups, each targeting a specific area of NiFi management.

### Access Commands

-   `get-access-token`: Obtains a JWT for authenticating with a NiFi instance that is secured with username/password.
-   `get-access-token-spnego`: Obtains a JWT for authenticating with a NiFi instance that is secured with Kerberos.
-   `logout-access-token`: Logs out the current user.

### Controller Service Commands

-   `create-controller-service`: Creates a new controller service.
-   `disable-controller-services`: Disables one or more controller services.
-   `enable-controller-services`: Enables one or more controller services.
-   `get-controller-service`: Retrieves the details of a controller service.
-   `get-controller-services`: Retrieves a list of all controller services.

### Flow Commands

-   `cluster-summary`: Retrieves a summary of the cluster status.
-   `create-flow-analysis-rule`: Creates a new flow analysis rule.
-   `create-reporting-task`: Creates a new reporting task.
-   `current-user`: Retrieves information about the current user.
-   `delete-flow-analysis-rule`: Deletes a flow analysis rule.
-   `disable-flow-analysis-rules`: Disables one or more flow analysis rules.
-   `enable-flow-analysis-rules`: Enables one or more flow analysis rules.
-   `export-reporting-task`: Exports a reporting task to a JSON file.
-   `export-reporting-tasks`: Exports all reporting tasks to a JSON file.
-   `get-controller-configuration`: Retrieves the controller configuration.
-   `get-flow-analysis-rule`: Retrieves the details of a flow analysis rule.
-   `get-flow-analysis-rules`: Retrieves a list of all flow analysis rules.
-   `get-reporting-task`: Retrieves the details of a reporting task.
-   `get-reporting-tasks`: Retrieves a list of all reporting tasks.
-   `get-root-id`: Retrieves the ID of the root process group.
-   `import-reporting-tasks`: Imports reporting tasks from a JSON file.
-   `start-reporting-tasks`: Starts one or more reporting tasks.
-   `stop-reporting-tasks`: Stops one or more reporting tasks.
-   `update-controller-configuration`: Updates the controller configuration.

### NAR Commands

-   `delete-nar`: Deletes a NAR file from the NiFi instance.
-   `download-nar`: Downloads a NAR file from the NiFi instance.
-   `list-nar-component-types`: Lists the component types in a NAR file.
-   `list-nars`: Lists all NAR files on the NiFi instance.
-   `upload-nar`: Uploads a NAR file to the NiFi instance.

### Node Commands

-   `connect-node`: Connects a node to the cluster.
-   `delete-node`: Deletes a node from the cluster.
-   `disconnect-node`: Disconnects a node from the cluster.
-   `get-node`: Retrieves the details of a node.
-   `get-nodes`: Retrieves a list of all nodes in the cluster.
-   `offload-node`: Offloads a node from the cluster.

### Parameter Commands

-   `add-asset-reference`: Adds an asset reference to a parameter context.
-   `create-asset`: Creates a new asset.
-   `create-param-context`: Creates a new parameter context.
-   `create-param-provider`: Creates a new parameter provider.
-   `delete-asset`: Deletes an asset.
-   `delete-param`: Deletes a parameter from a parameter context.
-   `delete-param-context`: Deletes a parameter context.
-   `delete-param-provider`: Deletes a parameter provider.
-   `export-param-context`: Exports a parameter context to a JSON file.
-   `fetch-params`: Fetches parameters from a parameter provider.
-   `get-asset`: Retrieves the details of an asset.
-   `get-param-context`: Retrieves the details of a parameter context.
-   `get-param-provider`: Retrieves the details of a parameter provider.
-   `import-param-context`: Imports a parameter context from a JSON file.
-   `list-assets`: Lists all assets.
-   `list-param-contexts`: Lists all parameter contexts.
-   `list-param-providers`: Lists all parameter providers.
-   `merge-param-context`: Merges a parameter context from a JSON file.
-   `remove-asset-reference`: Removes an asset reference from a parameter context.
-   `remove-inherited-param-contexts`: Removes inherited parameter contexts from a process group.
-   `set-inherited-param-contexts`: Sets the inherited parameter contexts for a process group.
-   `set-param`: Sets the value of a parameter in a parameter context.
-   `set-param-provider-property`: Sets a property for a parameter provider.

### Process Group Commands

-   `pg-change-all-versions`: Changes the version of all process groups that are under version control.
-   `pg-change-version`: Changes the version of a process group.
-   `pg-connect`: Connects a process group to a remote process group.
-   `pg-create`: Creates a new process group.
-   `pg-create-controller-service`: Creates a new controller service in a process group.
-   `pg-delete`: Deletes a process group.
-   `pg-disable-controller-services`: Disables all controller services in a process group.
-   `pg-empty-queues`: Empties all queues in a process group.
-   `pg-enable-controller-services`: Enables all controller services in a process group.
-   `pg-export`: Exports a process group to a JSON file.
-   `pg-get-all-versions`: Retrieves all versions of a process group.
-   `pg-get-controller-services`: Retrieves a list of all controller services in a process group.
-   `pg-get-param-context`: Retrieves the parameter context for a process group.
-   `pg-get-version`: Retrieves the version of a process group.
-   `pg-import`: Imports a process group from a JSON file.
-   `pg-list`: Lists all process groups.
-   `pg-list-processors`: Lists all processors in a process group.
-   `pg-rename`: Renames a process group.
-   `pg-replace`: Replaces the contents of a process group with the contents of a versioned flow.
-   `pg-set-param-context`: Sets the parameter context for a process group.
-   `pg-start`: Starts a process group.
-   `pg-status`: Retrieves the status of a process group.
-   `pg-stop`: Stops a process group.
-   `pg-stop-version-control`: Stops version control for a process group.

### Policy Commands

-   `get-access-policy`: Retrieves an access policy.
-   `update-access-policy`: Updates an access policy.

### Processor Commands

-   `change-version-processor`: Changes the version of a processor.
-   `processor-clear-state`: Clears the state of a processor.
-   `processor-run-once`: Runs a processor once.
-   `processor-start`: Starts a processor.

### Registry Commands

-   `create-registry-client`: Creates a new registry client.
-   `get-registry-client-id`: Retrieves the ID of a registry client.
-   `list-branches`: Lists all branches in a registry.
-   `list-buckets`: Lists all buckets in a registry.
-   `list-flows`: Lists all flows in a bucket.
-   `list-flow-versions`: Lists all versions of a flow.
-   `list-registry-clients`: Lists all registry clients.
-   `set-registry-client-property`: Sets a property for a registry client.
-   `update-registry-client`: Updates a registry client.

### Reporting Task Commands

-   `delete-reporting-task`: Deletes a reporting task.

### Tenant Commands

-   `create-user`: Creates a new user.
-   `create-user-group`: Creates a new user group.
-   `list-user-groups`: Lists all user groups.
-   `list-users`: Lists all users.
-   `update-user-group`: Updates a user group.
