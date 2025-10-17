# Gemini Project Information: Apache NiFi

This document provides essential information for the Gemini AI assistant to understand and interact with the Apache NiFi project.

## Project Overview

Apache NiFi is a powerful and reliable system to process and distribute data. It provides a web-based User Interface for designing, controlling, and monitoring dataflows.

- **Website:** https://nifi.apache.org/
- **Source Code:** https://github.com/apache/nifi
- **Issue Tracker:** https://issues.apache.org/jira/browse/NIFI

## Core Concepts

- **FlowFile:** Represents a single piece of data (a "FlowFile") moving through the system.
- **Processor:** A component that performs an operation on a FlowFile, such as reading data from a source, manipulating content, or sending it to a destination.
- **Connection:** Links Processors together, creating a dataflow path.
- **Controller Service:** A shared service that can be used by Processors, such as a database connection pool or a set of credentials.
- **Flow Controller:** Manages the dataflow, including starting and stopping Processors and managing threads.

## Build Instructions

The project uses the Maven Wrapper (`mvnw`) for building.

- **Full Build (all modules):**
  ```bash
  ./mvnw install -T1C
  ```

- **Full Build with Static Analysis:**
  ```bash
  ./mvnw install -T1C -P contrib-check
  ```

- **Build Application Binaries Only:**
  ```bash
  ./mvnw install -T1C -am -pl :nifi-assembly
  ```

The main application binary is located at `nifi-assembly/target/nifi-*-bin.zip`.

## Running Instructions

1.  **Build the project** using the instructions above.
2.  **Navigate to the distribution directory:**
    ```bash
    cd nifi-assembly/target/nifi-*-bin/nifi-*/
    ```
3.  **Start NiFi:**
    ```bash
    ./bin/nifi.sh start
    ```
4.  **Access the UI:**
    - The application runs at `https://localhost:8443/nifi`.
    - On the first startup, a random username and password are created and logged to `logs/nifi-app.log`. You can find them with:
      ```bash
      grep Generated logs/nifi-app*log
      ```
    - You can set your own credentials with:
      ```bash
      ./bin/nifi.sh set-single-user-credentials <username> <password>
      ```

## Development Notes

- The project is primarily written in **Java**.
- It requires **Java 21**.
- **Python 3.10+** is an optional dependency for some components.
- The project consists of several sub-projects, including:
    - **NiFi:** The core dataflow engine.
    - **NiFi Registry:** A subproject for storing and managing versioned flows.
    - **MiNiFi:** A smaller, lightweight version of NiFi designed for edge data collection.

This information should provide a good starting point for understanding and working with the Apache NiFi project.
