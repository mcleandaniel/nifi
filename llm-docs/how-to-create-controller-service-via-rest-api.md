# How to Create a Controller Service via the REST API

This document provides a detailed walkthrough of the process for creating, configuring, and enabling a NiFi Controller Service using the REST API.

## Prerequisites

- A running NiFi instance.
- A valid authentication token (JWT). See the documentation on how to obtain one.
- `curl` or a similar command-line tool for making HTTP requests.

## High-Level Workflow

The process of creating and enabling a controller service involves three main steps:

1.  **Create** the Controller Service within a specific Process Group.
2.  **Configure** the properties of the newly created Controller Service.
3.  **Enable** the Controller Service to make it available for use by other components.

## Detailed Steps

### Step 1: Create the Controller Service

To create a new Controller Service, you need to issue a `POST` request to the `/nifi-api/process-groups/{id}/controller-services` endpoint. The `{id}` in the URL is the ID of the Process Group where you want to create the service. To create a controller service at the root level, you can use `root` as the process group ID.

The body of the request must be a `ControllerServiceEntity` JSON object. The most important fields to include are:

-   `revision`: This is used for optimistic locking. For a new component, the version should be `0`.
-   `component`: This is a `ControllerServiceDTO` object that contains the configuration of the controller service.
    -   `type`: The fully qualified class name of the controller service you want to create.
    -   `bundle`: The bundle information for the controller service. This includes the `group`, `artifact`, and `version` of the bundle.

**Example Request:**

```bash
curl 'https://localhost:8443/nifi-api/process-groups/root/controller-services' \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <your-jwt-token>' \
  --data-raw '{
    "revision": {
      "version": 0
    },
    "component": {
      "type": "org.apache.nifi.ssl.StandardSSLContextService",
      "bundle": {
        "group": "org.apache.nifi",
        "artifact": "nifi-ssl-context-service-nar",
        "version": "2.0.0-SNAPSHOT"
      }
    }
  }' \
  --insecure
```

The response to this request will be a `ControllerServiceEntity` object that includes the ID and the initial revision of the newly created controller service. You will need this ID and revision for the subsequent steps.

### Step 2: Configure the Controller Service

Once the controller service is created, you need to configure its properties. This is done by sending a `PUT` request to the `/nifi-api/controller-services/{id}` endpoint, where `{id}` is the ID of the controller service you obtained in the previous step.

**Important Considerations:**

*   **Live Revision:** The `revision` object in the request body must contain the latest version number of the controller service. This value is obtained from the response of the previous request. Hard-coding this value will result in a `409 Conflict` error.
*   **Canonical Property Names:** The keys in the `properties` map must be the canonical (internal) names of the properties, not the display names shown in the NiFi UI. You can find the canonical names by:
    *   Inspecting the response from the `/nifi-api/controller-services/types/{type-name}` endpoint.
    *   Consulting the source code of the controller service.
*   **Service State:** The controller service must be in the `DISABLED` state to be configured. If you have already attempted to enable it, you must disable it before making configuration changes.

The body of the request is a `ControllerServiceEntity` object. This time, you need to include the latest `revision` number and the `properties` that you want to set in the `component` object.

**Example Request:**

```bash
curl 'https://localhost:8443/nifi-api/controller-services/<your-controller-service-id>' \
  -X PUT \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <your-jwt-token>' \
  --data-raw '{
    "revision": {
      "version": <latest-revision-version>
    },
    "component": {
      "id": "<your-controller-service-id>",
      "properties": {
        "keystore-file": "/path/to/keystore.jks",
        "keystore-password": "your_keystore_password",
        "key-password": "your_key_password",
        "keystore-type": "JKS",
        "truststore-file": "/path/to/truststore.jks",
        "truststore-password": "your_truststore_password",
        "truststore-type": "JKS"
      }
    }
  }' \
  --insecure
```

### Step 3: Enable the Controller Service

After configuring the controller service, the final step is to enable it. This is done by sending another `PUT` request to the same `/nifi-api/controller-services/{id}` endpoint.

In this request, you need to set the `state` of the component to `ENABLED`. Again, you must provide the latest `revision` number from the response of the configuration step.

**Example Request:**

```bash
curl 'https://localhost:8443/nifi-api/controller-services/<your-controller-service-id>' \
  -X PUT \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <your-jwt-token>' \
  --data-raw '{
    "revision": {
      "version": <latest-revision-version>
    },
    "component": {
      "id": "<your-controller-service-id>",
      "state": "ENABLED"
    }
  }' \
  --insecure
```

After this request is successful, the controller service will be running and available for other components to use.

## Error Handling

When working with the NiFi REST API, you may encounter the following common HTTP status codes:

-   `400 Bad Request`: The request was malformed. Check your JSON payload and ensure that you are using the correct property names.
-   `401 Unauthorized`: Your authentication token is missing or invalid.
-   `403 Forbidden`: You do not have the necessary permissions to perform the requested action.
-   `404 Not Found`: The requested resource (e.g., process group or controller service) could not be found.
-   `409 Conflict`: The `revision` number you provided is not the latest version. You need to fetch the latest revision and try again.
