# Interacting with NiFi Connections

## Introduction

In Apache NiFi, **Connections** are the pathways that link dataflow components (like Processors, Input/Output Ports, Funnels, and Remote Process Groups) together on the canvas. Each Connection houses a **Queue** that buffers FlowFiles as they move from an upstream component to a downstream component. Understanding how to get data *into* and *out of* these connections from external systems is key, but it works indirectly through specific NiFi components.

## How Data Moves Through Connections

The fundamental flow of data via a connection is:

1.  An **upstream component** (e.g., a Processor like `GetFile`) finishes processing a FlowFile.
2.  The component transfers the FlowFile to one of its defined **Relationships** (e.g., `success`).
3.  The FlowFile is placed into the **Queue** of the Connection linked to that Relationship.
4.  A **downstream component** (e.g., a Processor like `PutFile`) connected to that Connection pulls the FlowFile from the Queue when it is scheduled to run and the queue is not empty.

Connections themselves are internal constructs within the NiFi dataflow.

## Sending Data *to* a Connection (from External Systems)

You **cannot directly push** data from an external system (like a script, application, or API call) straight into an arbitrary internal NiFi Connection Queue.

Instead, you must use an **Ingress Component** within your NiFi flow to receive the external data. This component then creates a FlowFile and places it onto its *outbound* connection queue.

**Common Ingress Patterns:**

1.  **HTTP/S Listener:**
    * Use a `ListenHTTP` or `HandleHttpRequest` processor.
    * Configure the processor to listen on a specific port and path.
    * External systems send data via HTTP POST requests to that endpoint.
    * The processor receives the request body, creates a FlowFile containing that data, and routes it to its `success` relationship, placing it onto the *next connection's queue*.
    * *Example Concept:* `External POST` -> `ListenHTTP` -> **Connection Queue** -> `LogAttribute`
2.  **Messaging Queues:**
    * Use processors like `ConsumeKafka`, `ConsumeJMS`, `ConsumeAMQP`, `GetSQS`.
    * Configure the processor to connect to the message broker/queue.
    * The processor polls for new messages, creates FlowFiles from them, and routes them to its `success` relationship, placing them onto the *next connection's queue*.
    * *Example Concept:* `Message Broker` -> `ConsumeKafka` -> **Connection Queue** -> `UpdateAttribute`
3.  **File/Network Protocols:**
    * Use processors like `GetFile`, `GetSFTP`, `GetFTP`.
    * Configure the processor to monitor a directory or remote server.
    * The processor picks up files, creates FlowFiles from their content, and routes them to its `success` relationship, placing them onto the *next connection's queue*.
    * *Example Concept:* `Local Directory` -> `GetFile` -> **Connection Queue** -> `PutDatabaseRecord`

**In summary: To get data onto a connection, send it to an appropriate NiFi ingress processor first.**

## Receiving Data *from* a Connection (to External Systems)

Similarly, you **cannot directly pull** data from an internal NiFi Connection Queue using an external system.

Instead, you must use an **Egress Component** connected *after* the connection queue of interest. This component pulls FlowFiles from its *inbound* connection queue and sends the data externally.

**Common Egress Patterns:**

1.  **HTTP/S Endpoint:**
    * Use an `InvokeHTTP` processor.
    * Configure the processor with the URL of the external endpoint.
    * The processor pulls a FlowFile from its *inbound connection queue*, reads its content, and sends it as the body of an HTTP POST/PUT request to the external service.
    * *Example Concept:* `GenerateFlowFile` -> **Connection Queue** -> `InvokeHTTP` -> `External API`
2.  **Messaging Queues:**
    * Use processors like `PublishKafka`, `PublishJMS`, `PutSQS`.
    * Configure the processor to connect to the message broker/topic.
    * The processor pulls a FlowFile from its *inbound connection queue*, reads its content, and sends it as a message.
    * *Example Concept:* `RouteOnAttribute` -> **Connection Queue** -> `PublishKafka` -> `Message Broker`
3.  **File/Network Protocols:**
    * Use processors like `PutFile`, `PutSFTP`, `PutFTP`.
    * Configure the processor with the target directory or remote server details.
    * The processor pulls a FlowFile from its *inbound connection queue*, reads its content, and writes it to a file externally.
    * *Example Concept:* `QueryDatabaseTable` -> **Connection Queue** -> `PutFile` -> `Local Directory`

**In summary: To get data from a connection to an external system, connect an appropriate NiFi egress processor after the connection.**

## Direct Interaction with the Queue (Management & Monitoring)

While external systems cannot arbitrarily push/pull data, NiFi *does* provide ways to interact with the connection queue for management and monitoring purposes:

1.  **NiFi UI:**
    * **List Queue:** Right-click a connection -> "List queue" shows the FlowFiles currently in the queue (up to 100 by default).
    * **View Details:** From the queue listing, you can view a FlowFile's attributes and details.
    * **Download/View Content:** From the FlowFile details view, you can download or view the FlowFile's content (if renderable).
    * **Empty Queue:** Right-click a connection -> "Empty queue" deletes all FlowFiles currently in the queue.
2.  **NiFi REST API:**
    * Endpoints exist under `/flowfile-queues/{connection-id}/` to programmatically perform actions similar to the UI capabilities:
        * Submit a listing request (`/listing-requests`).
        * Get the results of a listing request (`/listing-requests/{request-id}`).
        * Get details for a specific FlowFile in the queue (`/flowfiles/{flowfile-uuid}`).
        * Download FlowFile content (`/flowfiles/{flowfile-uuid}/content`).
        * Submit a request to empty the queue (`/drop-requests`).
    * These API endpoints are intended for monitoring, troubleshooting, and specific management tasks, **not** as a general-purpose mechanism for external systems to inject or extract data into/from the flow.

## Conclusion

NiFi Connections and their queues are fundamental internal components for buffering and channeling data *within* a dataflow. External systems interact with the dataflow **indirectly** by sending data to ingress processors (which place FlowFiles onto connections) or by receiving data from egress processors (which pull FlowFiles from connections). Direct external push/pull operations on the internal queues are not supported for general data transfer; interaction occurs via dedicated data ingress and egress components. Management and monitoring of queues can be done via the UI or specific REST API endpoints.