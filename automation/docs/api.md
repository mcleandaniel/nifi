# NiFi Automation API Documentation

This document provides a detailed overview of the Python API for the NiFi Automation project.

## Core Modules

The `nifi_automation` package is organized into several core modules:

-   **`auth`**: Handles authentication with the NiFi REST API.
-   **`client`**: A thin HTTP client for interacting with the NiFi REST API.
-   **`config`**: Manages configuration using `pydantic-settings`.
-   **`flow_builder`**: Provides tools for deploying flows from declarative YAML specifications.
-   **`cli`**: The command-line interface for the project, built with `Typer`.

---

## `auth` Module

The `auth` module provides helpers for authenticating with the NiFi REST API.

### `obtain_access_token(settings: AuthSettings) -> str`

Requests a bearer token from NiFi's `/access/token` endpoint.

-   **Parameters:**
    -   `settings` (`AuthSettings`): An `AuthSettings` object containing the NiFi base URL, username, and password.
-   **Returns:**
    -   `str`: The bearer token.
-   **Raises:**
    -   `AuthenticationError`: If authentication fails.

---

## `client` Module

The `client` module provides a context manager-based HTTP client for making requests to the NiFi REST API.

### `class NiFiClient(AbstractContextManager)`

A context manager wrapper around `httpx.Client` with NiFi-specific helper methods.

-   **`__init__(self, settings: AuthSettings, token: str)`**
    -   Initializes the client with the given `AuthSettings` and bearer token.
-   **`get_root_flow() -> Dict[str, Any]`**
    -   Retrieves the root process group.
-   **`find_child_process_group_by_name(parent_id: str, name: str) -> Optional[Dict[str, Any]]`**
    -   Finds a child process group by name within a parent process group.
-   **`create_process_group(...) -> Dict[str, Any]`**
    -   Creates a new process group.
-   **`delete_process_group(pg_id: str, version: int) -> None`**
    -   Deletes a process group.
-   **`create_processor(...) -> Dict[str, Any]`**
    -   Creates a new processor.
-   **`set_processor_state(processor_id: str, state: str) -> None`**
    -   Sets the state of a processor (e.g., "RUNNING", "STOPPED").
-   **`create_connection(...) -> Dict[str, Any]`**
    -   Creates a new connection between two components.
-   **`create_controller_service(...) -> Dict[str, Any]`**
    -   Creates a new controller service.
-   **`enable_controller_service(service_id: str) -> None`**
    -   Enables a controller service.
-   **`disable_controller_service(service_id: str) -> None`**
    -   Disables a controller service.
-   **`delete_controller_service(service_id: str) -> None`**
    -   Deletes a controller service.

---

## `flow_builder` Module

The `flow_builder` module provides tools for deploying NiFi flows from declarative YAML specifications.

### `class FlowSpec`

A data class that represents a NiFi flow specification.

-   **Attributes:**
    -   `root_group` (`ProcessGroupSpec`): The root process group of the flow.

### `class ProcessGroupSpec`

A data class that represents a process group specification.

-   **Attributes:**
    -   `name` (`str`): The name of the process group.
    -   `processors` (`List[ProcessorSpec]`): A list of processors in the group.
    -   `connections` (`List[ConnectionSpec]`): A list of connections in the group.
    -   `child_groups` (`List[ProcessGroupSpec]`): A list of child process groups.

### `class ProcessorSpec`

A data class that represents a processor specification.

-   **Attributes:**
    -   `key` (`str`): A unique identifier for the processor.
    -   `name` (`str`): The name of the processor.
    -   `type` (`str`): The type of the processor (e.g., `org.apache.nifi.processors.standard.GenerateFlowFile`).
    -   `properties` (`Dict[str, str]`): A dictionary of processor properties.

### `class ConnectionSpec`

A data class that represents a connection specification.

-   **Attributes:**
    -   `name` (`str`): The name of the connection.
    -   `source` (`str`): The key of the source processor.
    -   `destination` (`str`): The key of the destination processor.
    -   `relationships` (`List[str]`): A list of relationships to connect.

### `class FlowDeployer`

Deploys flow specifications using the NiFi REST API.

-   **`__init__(self, client: NiFiClient, spec: FlowSpec, ...)`**
    -   Initializes the deployer with a `NiFiClient` and a `FlowSpec`.
-   **`deploy() -> str`**
    -   Creates the process group and all processors/connections. Returns the ID of the root process group.

### `deploy_flow_from_file(client: NiFiClient, path: Path, ...) -> str`

A convenience function that loads a flow specification from a YAML file and deploys it.

-   **Parameters:**
    -   `client` (`NiFiClient`): The `NiFiClient` to use for deployment.
    -   `path` (`Path`): The path to the YAML flow specification file.
-   **Returns:**
    -   `str`: The ID of the root process group.
