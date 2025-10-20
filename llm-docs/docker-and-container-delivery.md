---
title: Docker and Container Delivery
summary: Build scripts, environment variables, and operational guidance for running Apache NiFi containers using the official Docker image and scripts.
plan_id: project
topic_id: project_project-containerization-support
category: deployment
tags: [docker, containers, deployment]

sources:
  - id: src-dockerhub-readme
    title: nifi-docker/dockerhub/README.md
    url: nifi-docker/dockerhub/README.md
  - id: src-dockerfile
    title: nifi-docker/dockerhub/Dockerfile
    url: nifi-docker/dockerhub/Dockerfile
  - id: src-start-sh
    title: nifi-docker/dockerhub/sh/start.sh
    url: nifi-docker/dockerhub/sh/start.sh
  - id: src-secure-sh
    title: nifi-docker/dockerhub/sh/secure.sh
    url: nifi-docker/dockerhub/sh/secure.sh
  - id: src-common-sh
    title: nifi-docker/dockerhub/sh/common.sh
    url: nifi-docker/dockerhub/sh/common.sh
  - id: src-update-login
    title: nifi-docker/dockerhub/sh/update_login_providers.sh
    url: nifi-docker/dockerhub/sh/update_login_providers.sh
  - id: src-update-oidc
    title: nifi-docker/dockerhub/sh/update_oidc_properties.sh
    url: nifi-docker/dockerhub/sh/update_oidc_properties.sh
  - id: src-update-cluster-state
    title: nifi-docker/dockerhub/sh/update_cluster_state_management.sh
    url: nifi-docker/dockerhub/sh/update_cluster_state_management.sh
  - id: src-toolkit-sh
    title: nifi-docker/dockerhub/sh/toolkit.sh
    url: nifi-docker/dockerhub/sh/toolkit.sh

claims:
  - id: claim-base-image-java21
    summary: Official image uses Liberica OpenJDK Debian 21 as base with ARGs.
    sources:
      - src: src-dockerfile
        locator: "L20-L22"
      - src: src-dockerhub-readme
        locator: "L18-L22"
  - id: claim-nifi-version-build-arg
    summary: Build accepts NIFI_VERSION ARG and defaults to 2.0.0.
    sources:
      - src: src-dockerfile
        locator: "L29-L35"
      - src: src-dockerhub-readme
        locator: "L71-L75"
  - id: claim-env-paths
    summary: Dockerfile sets NIFI_HOME, NIFI_TOOLKIT_HOME, NIFI_LOG_DIR, and PID dir under /opt/nifi.
    sources:
      - src: src-dockerfile
        locator: "L36-L41"
  - id: claim-toolkit-included
    summary: Image includes NiFi Toolkit and sets NIFI_TOOLKIT_HOME.
    sources:
      - src: src-dockerhub-readme
        locator: "L34-L41"
      - src: src-dockerfile
        locator: "L64-L71"
  - id: claim-volumes
    summary: Image declares volumes for logs, conf, repositories, python_extensions, nar_extensions, and state.
    sources:
      - src: src-dockerfile
        locator: "L89-L97"
  - id: claim-expose-ports
    summary: Image exposes ports 8443 (HTTPS), 10000 (remote input), and 8000 (JVM debug).
    sources:
      - src: src-dockerfile
        locator: "L102-L104"
      - src: src-dockerhub-readme
        locator: "L256-L265"
  - id: claim-entrypoint
    summary: Entrypoint executes scripts/start.sh using exec form.
    sources:
      - src: src-dockerfile
        locator: "L107-L116"
  - id: claim-https-default
    summary: Image defaults to HTTPS; plain HTTP support dropped in 2.0.0.
    sources:
      - src: src-dockerhub-readme
        locator: "L18-L22"
      - src: src-secure-sh
        locator: "L57-L63"
  - id: claim-run-minimal
    summary: Minimal run maps 8443 and serves UI at https://localhost:8443/nifi.
    sources:
      - src: src-dockerhub-readme
        locator: "L82-L91"
  - id: claim-generated-credentials
    summary: Default startup generates random single-user credentials and logs them.
    sources:
      - src: src-dockerhub-readme
        locator: "L91-L97"
  - id: claim-set-single-user-creds
    summary: SINGLE_USER_CREDENTIALS_USERNAME and SINGLE_USER_CREDENTIALS_PASSWORD set single-user auth credentials.
    sources:
      - src: src-start-sh
        locator: "L99-L101"
  - id: claim-jvm-heap-env
    summary: NIFI_JVM_HEAP_INIT and NIFI_JVM_HEAP_MAX set Xms/Xmx via bootstrap.conf.
    sources:
      - src: src-start-sh
        locator: "L22-L29"
      - src: src-common-sh
        locator: "L46-L49"
  - id: claim-jvm-debugger-env
    summary: Setting NIFI_JVM_DEBUGGER enables java.arg.debug.
    sources:
      - src: src-start-sh
        locator: "L31-L33"
      - src: src-dockerhub-readme
        locator: "L264-L268"
  - id: claim-proxy-host-note
    summary: Missing NIFI_WEB_PROXY_HOST can make UI inaccessible when proxied or using port mapping.
    sources:
      - src: src-start-sh
        locator: "L58-L60"
      - src: src-dockerhub-readme
        locator: "L270-L275"
  - id: claim-cluster-env-mapping
    summary: Environment variables map to nifi.properties clustering fields and ZK settings.
    sources:
      - src: src-dockerhub-readme
        locator: "L222-L236"
      - src: src-start-sh
        locator: "L62-L71"
  - id: claim-state-management-mapping
    summary: NIFI_ZK_CONNECT_STRING and NIFI_ZK_ROOT_NODE map into state-management.xml cluster provider.
    sources:
      - src: src-dockerhub-readme
        locator: "L237-L243"
      - src: src-update-cluster-state
        locator: "L18-L33"
  - id: claim-auth-modes
    summary: Image supports Single User, TLS (client cert), LDAP, and OIDC authentication.
    sources:
      - src: src-dockerhub-readme
        locator: "L51-L56"
      - src: src-start-sh
        locator: "L105-L125"
  - id: claim-ldap-config
    summary: LDAP mode sets login identity provider and updates login-identity-providers.xml from env.
    sources:
      - src: src-start-sh
        locator: "L111-L118"
      - src: src-update-login
        locator: "L18-L48"
  - id: claim-oidc-config
    summary: OIDC mode applies nifi.security.user.oidc.* properties from env variables.
    sources:
      - src: src-start-sh
        locator: "L119-L124"
      - src: src-update-oidc
        locator: "L18-L29"
  - id: claim-secure-keystores-required
    summary: Secure modes require keystore/truststore paths, types, and passwords.
    sources:
      - src: src-secure-sh
        locator: "L25-L39"
  - id: claim-initial-admin
    summary: INITIAL_ADMIN_IDENTITY and optional INITIAL_ADMIN_GROUP seed authorizations in authorizers.xml.
    sources:
      - src: src-secure-sh
        locator: "L73-L83"
      - src: src-dockerhub-readme
        locator: "L146-L152"
  - id: claim-remote-input-secure
    summary: start.sh configures nifi.remote.input.secure=true by default.
    sources:
      - src: src-start-sh
        locator: "L46-L47"
  - id: claim-toolkit-exec
    summary: Toolkit is runnable in-container; CLI uses ~/.nifi-cli.nifi.properties.
    sources:
      - src: src-dockerhub-readme
        locator: "L245-L255"
      - src: src-toolkit-sh
        locator: "L18-L32"

---

Introduction / Overview

<span id="claim-base-image-java21">The official NiFi container is built on a Liberica OpenJDK Debian 21 base image configured through `IMAGE_NAME` and `IMAGE_TAG` build arguments.</span>
<span id="claim-https-default">NiFi 2.0.0 images default to HTTPS and dropped plain HTTP support.</span>
<span id="claim-toolkit-included">The image includes the NiFi Toolkit and sets `NIFI_TOOLKIT_HOME` accordingly.</span>

Concepts / Architecture

<span id="claim-env-paths">The Dockerfile standardizes installation under `/opt/nifi`, setting `NIFI_HOME`, `NIFI_TOOLKIT_HOME`, `NIFI_LOG_DIR`, and `NIFI_PID_DIR`.</span>
<span id="claim-volumes">Persistent data and configuration are exposed as Docker volumes for logs, configuration, repositories, extension directories, and state.</span>
<span id="claim-expose-ports">The image exposes 8443/TCP for HTTPS, 10000/TCP for Site-to-Site Remote Input, and 8000/TCP for remote JVM debugging.</span>
<span id="claim-entrypoint">The container entrypoint executes `../scripts/start.sh` using the exec form for proper signal handling.</span>

Implementation / Configuration

Build

<span id="claim-nifi-version-build-arg">Images can be built with a specific NiFi version using the `NIFI_VERSION` build argument (default `2.0.0`).</span>

Example build commands:

```bash
# Build from the dockerhub/ directory
cd nifi-docker/dockerhub
docker build -t apache/nifi:latest .

# Build for a specific NiFi release
docker build --build-arg NIFI_VERSION=2.0.0 -t apache/nifi:2.0.0 .
```

Runtime

<span id="claim-jvm-heap-env">`NIFI_JVM_HEAP_INIT` and `NIFI_JVM_HEAP_MAX` set `-Xms` and `-Xmx` in `bootstrap.conf`.</span>
<span id="claim-jvm-debugger-env">Setting `NIFI_JVM_DEBUGGER` enables the `java.arg.debug` JVM remote debugging option.</span>
<span id="claim-remote-input-secure">Remote input is configured to be secure by default.</span>
<span id="claim-proxy-host-note">If a reverse proxy or port mapping is used without `NIFI_WEB_PROXY_HOST`, the UI may be inaccessible.</span>

Clustering and State

<span id="claim-cluster-env-mapping">Clustering properties map from environment variables to `nifi.properties` (node address/port, threads, and ZooKeeper connection settings).</span>
<span id="claim-state-management-mapping">`NIFI_ZK_CONNECT_STRING` and `NIFI_ZK_ROOT_NODE` also map into `state-management.xml` for the cluster state provider.</span>

Authentication Modes

<span id="claim-auth-modes">The image supports Single User Authentication, mutual TLS with client certificates, LDAP, and OpenID Connect (OIDC).</span>
<span id="claim-secure-keystores-required">TLS-secured modes require keystore and truststore locations, types, and passwords.</span>
<span id="claim-initial-admin">`INITIAL_ADMIN_IDENTITY` (and optional `INITIAL_ADMIN_GROUP`) bootstrap administrative access in `authorizers.xml`.</span>
<span id="claim-ldap-config">In LDAP mode, the entrypoint sets `NIFI_SECURITY_USER_LOGIN_IDENTITY_PROVIDER` and applies LDAP properties from environment variables to `login-identity-providers.xml`.</span>
<span id="claim-oidc-config">In OIDC mode, `nifi.security.user.oidc.*` properties are configured from environment variables.</span>

Usage / Examples

Standalone (HTTPS + Single User)

<span id="claim-run-minimal">A minimal invocation maps 8443 and serves the UI at `https://localhost:8443/nifi`.</span>

```bash
docker run --name nifi \
  -p 8443:8443 \
  -d \
  apache/nifi:latest

# Retrieve generated credentials from logs
docker logs nifi | grep "Generated.*credentials"
```

<span id="claim-generated-credentials">On first start, NiFi generates a random username and password and writes them to the application log.</span>

Set explicit Single User credentials at startup:

```bash
docker run --name nifi \
  -p 8443:8443 \
  -e SINGLE_USER_CREDENTIALS_USERNAME=admin \
  -e SINGLE_USER_CREDENTIALS_PASSWORD='a-strong-password' \
  -d apache/nifi:latest
```

<span id="claim-set-single-user-creds">You can set Single User credentials using `SINGLE_USER_CREDENTIALS_USERNAME` and `SINGLE_USER_CREDENTIALS_PASSWORD`.</span>

Tune JVM heap and enable remote debug:

```bash
docker run --name nifi \
  -p 8443:8443 -p 8000:8000 \
  -e NIFI_JVM_HEAP_INIT=2g -e NIFI_JVM_HEAP_MAX=2g \
  -e NIFI_JVM_DEBUGGER=1 \
  -d apache/nifi:latest
```

Reverse proxy awareness:

```bash
docker run --name nifi \
  -p 8443:8443 \
  -e NIFI_WEB_PROXY_HOST="nifi.example.com:443" \
  -d apache/nifi:latest
```

TLS with LDAP authentication (minimal example):

```bash
docker run --name nifi \
  -p 8443:8443 \
  -v $(pwd)/certs:/opt/certs \
  -e AUTH=ldap \
  -e KEYSTORE_PATH=/opt/certs/keystore.jks \
  -e KEYSTORE_TYPE=JKS \
  -e KEYSTORE_PASSWORD=changeit \
  -e TRUSTSTORE_PATH=/opt/certs/truststore.jks \
  -e TRUSTSTORE_TYPE=JKS \
  -e TRUSTSTORE_PASSWORD=changeit \
  -e INITIAL_ADMIN_IDENTITY='cn=admin,dc=example,dc=org' \
  -e LDAP_AUTHENTICATION_STRATEGY='SIMPLE' \
  -e LDAP_MANAGER_DN='cn=admin,dc=example,dc=org' \
  -e LDAP_MANAGER_PASSWORD='password' \
  -e LDAP_USER_SEARCH_BASE='dc=example,dc=org' \
  -e LDAP_USER_SEARCH_FILTER='cn={0}' \
  -e LDAP_IDENTITY_STRATEGY='USE_DN' \
  -e LDAP_URL='ldap://ldap:389' \
  -d apache/nifi:latest
```

Clustering (selected environment variables):

```bash
docker run --name nifi-node1 \
  -p 8443:8443 -p 10000:10000 \
  -e NIFI_CLUSTER_IS_NODE=true \
  -e NIFI_CLUSTER_ADDRESS=nifi-node1 \
  -e NIFI_CLUSTER_NODE_PROTOCOL_PORT=11443 \
  -e NIFI_ZK_CONNECT_STRING='zk:2181' \
  -e NIFI_ZK_ROOT_NODE='/nifi' \
  -d apache/nifi:latest
```

Toolkit usage (exec inside container):

```bash
docker exec -ti nifi nifi-toolkit-current/bin/cli.sh nifi current-user
```

Best Practices / Tips

- Use named volumes for repositories and `conf` to retain state across upgrades.
- Configure `NIFI_WEB_PROXY_HOST` (and `NIFI_WEB_PROXY_CONTEXT_PATH` when applicable) when using reverse proxies.
- Pin `NIFI_VERSION` in builds to ensure reproducible images.
- Avoid exposing 8000 in production; enable only for controlled debugging.

Troubleshooting

- Credential discovery: check `nifi-app.log` via `docker logs` for generated credentials on first start.
- UI unreachable after proxying: confirm `NIFI_WEB_PROXY_HOST` (and context path) align with external URL mapping.
- LDAP/OIDC failures: verify environment variables populate `login-identity-providers.xml` or `nifi.properties` as expected.
- Cluster join issues: confirm `NIFI_ZK_CONNECT_STRING` and `NIFI_CLUSTER_*` values are consistent and ZooKeeper is reachable.

Reference / Related Docs

- <span id="claim-toolkit-exec">Run NiFi Toolkit inside the container; CLI uses `~/.nifi-cli.nifi.properties`.</span>
- <span id="claim-expose-ports">Default container ports: 8443 (HTTPS UI), 10000 (Remote Input), 8000 (Debugger).</span>
