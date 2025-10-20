# Remote Process Groups in Apache NiFi

## Introduction

A **Remote Process Group (RPG)** is a specialized component within Apache NiFi designed to facilitate data transfer **between separate NiFi instances** or clusters. Think of it as a logical representation of a connection *to* another NiFi environment. RPGs utilize NiFi's native **Site-to-Site (S2S)** protocol to send data to or receive data from Input Ports and Output Ports configured on the remote NiFi instance.

## Why Use Remote Process Groups?

RPGs, leveraging the Site-to-Site protocol, are crucial for building distributed and scalable dataflows across different NiFi deployments. Key benefits include:

1.  **Ease of Configuration:** After providing the URL of the remote instance, available Input/Output ports are automatically discovered.
2.  **Security:** S2S supports TLS encryption, authentication, and authorization. Remote ports can be configured to allow access only to specific, authorized NiFi instances or users.
3.  **Scalability:** When connecting to a remote NiFi cluster, the RPG automatically discovers nodes and distributes data across them. Changes in the remote cluster (nodes added/removed) are detected automatically.
4.  **Efficiency:** Data transfer occurs in batches, minimizing the overhead of establishing connections and reducing round-trip requests. Compression can also be enabled.
5.  **Reliability:** Automatic checksums ensure data integrity during transfer. Failed transactions are retried.
6.  **Load Balancing:** Data distribution across remote cluster nodes is adjusted based on node availability and load.
7.  **Attribute Preservation:** FlowFile attributes are automatically transferred along with the content, preserving context.
8.  **Adaptability:** The S2S protocol supports version negotiation, allowing for new features while maintaining backward compatibility.

RPGs are essential for scenarios like:
* Sending data from edge NiFi instances to a central NiFi cluster.
* Distributing processing workloads across multiple NiFi clusters.
* Bridging dataflows between different security domains or networks.

## Implementation: Setting up Data Transfer with RPGs

Setting up data transfer involves configuring both the **sending (client)** NiFi instance and the **receiving (server)** NiFi instance. The RPG component itself resides on the client instance.

**On the Sending/Receiving (Client) NiFi Instance:**

1.  **Add RPG Component:** Drag the Remote Process Group icon (<img src="./images/iconRemoteProcessGroup.png" alt="Remote Process Group" width="20" style="vertical-align: middle;"/>) from the Components Toolbar onto the canvas.
2.  **Configure URL:** Enter the URL(s) of the remote NiFi instance. For a cluster, provide comma-separated URLs of multiple nodes for resilience. The URL is typically the same one used to access the remote NiFi's UI (e.g., `https://remote-nifi-node1:8443/nifi`).
3.  **Configure Transport:** In the RPG configuration dialog, select the **Transport Protocol** (default is `RAW`, `HTTP` is also available for firewall/proxy traversal). Configure proxy settings if needed.
4.  **Wait/Refresh:** Allow NiFi time (up to a minute) to discover the remote ports, or manually trigger discovery by right-clicking the RPG and selecting "Refresh remote".
5.  **Connect:**
    * **Sending Data (Push):** Drag a connection *from* a local component *to* the RPG. You'll be prompted to select one of the available **Input Ports** on the remote instance.
    * **Receiving Data (Pull):** Drag a connection *from* the RPG *to* a local component. You'll be prompted to select one of the available **Output Ports** on the remote instance.
6.  **Enable Transmission:**
    * Right-click the RPG and select "Enable transmission" to activate all connected ports.
    * Alternatively, right-click the RPG, select "Manage remote ports", and toggle transmission for individual ports. Here you can also configure concurrent tasks, compression, and batch settings per port.

**On the Remote (Server) NiFi Instance:**

* **For Receiving Data (Push):** An **Input Port** (<img src="./images/iconInputPort.png" alt="Input Port" width="20" style="vertical-align: middle;"/>) must exist on the Root Process Group canvas, or within a child Process Group specifically configured for Site-to-Site reception ("Remote connections (site-to-site)").
* **For Sending Data (Pull):** An **Output Port** (<img src="./images/iconOutputPort.png" alt="Output Port" width="20" style="vertical-align: middle;"/>) must exist on the Root Process Group canvas, or within a child Process Group specifically configured for Site-to-Site sending ("Remote connections (site-to-site)").
* **Security:** If the remote instance is secure (HTTPS), appropriate policies must be configured:
    * The **"retrieve site-to-site details"** Global Access Policy must grant access to the client NiFi instance/user.
    * The **"receive data via site-to-site"** Component Access Policy must be set on the Input Port to allow the client to push data.
    * The **"send data via site-to-site"** Component Access Policy must be set on the Output Port to allow the client to pull data.

## Monitoring Remote Process Groups

You can monitor the status and performance of RPGs in several ways:

1.  **Canvas Indicators:**
    * **Transmission Status Icon:** Shows whether transmission is enabled (<img src="./images/iconTransmissionActive.png" alt="Transmission Enabled" width="16" style="vertical-align: middle;"/>), disabled (<img src="./images/iconTransmissionInactive.png" alt="Transmission Disabled" width="16" style="vertical-align: middle;"/>), or encountering issues (<img src="./images/iconAlert.png" alt="Warning" width="16" style="vertical-align: middle;"/>). Hovering over a warning provides details.
    * **5-Minute Statistics:** Displays the count and total size of FlowFiles **Sent** and **Received** in the last five minutes.
    * **Last Refresh Time:** Indicates when information from the remote instance was last updated. Can show "Remote flow not current" if outdated.
2.  **Status History:** Right-click the RPG and select "View status history" to see graphs of historical statistics (Sent/Received rates, etc.).
3.  **Bulletins:** If communication errors occur, a bulletin indicator (<img src="./images/bulletin-indicator-small.png" alt="Bulletin" width="12" style="vertical-align: middle;"/>) may appear. Hover over it for details.
4.  **Summary Page:** The "Remote Process Groups" tab in the Summary Page (Global Menu -> Summary) provides a tabular overview of all RPGs, their status, and statistics.

## Sending Data via CLI or API

**You cannot directly send an arbitrary FlowFile to a Remote Process Group using an external NiFi CLI command or a single REST API call.**

RPGs are components *within* a NiFi dataflow. They represent the *connection endpoint* to another NiFi instance for data that is already flowing *inside* the source NiFi instance.

To send data via an RPG:

1.  **Ingest Data:** Data must first enter the NiFi flow using an appropriate ingress processor (e.g., `ListenHTTP`, `GetFile`, `ConsumeKafka`) or be generated within the flow (e.g., `GenerateFlowFile`).
2.  **Route Data:** The resulting FlowFile(s) must then be routed *within the NiFi canvas* to a connection that leads *into* the configured RPG component.
3.  **Transmission:** If the RPG and the specific port connection are enabled for transmission, NiFi will then use the Site-to-Site protocol to send the FlowFile to the corresponding Input Port on the remote NiFi instance.

**CLI/API for Management:**
While you can't *send data* directly to an RPG externally, the NiFi CLI and REST API *can* be used to **manage** RPGs, for example:
* Check the status of RPGs.
* Enable or disable transmission for an RPG or its specific ports.
* View available remote ports.
* Update RPG configuration (like URLs, timeouts).

The NiFi Toolkit Guide provides details on the `nifi cli rpg` commands (`get-ports`, `set-transmission-status`, etc.) for such management tasks.

## Conclusion

Remote Process Groups are the standard and recommended way to transfer data between NiFi instances, offering a robust, secure, and manageable solution built on the Site-to-Site protocol. They are integral to building complex, distributed data processing pipelines with Apache NiFi.