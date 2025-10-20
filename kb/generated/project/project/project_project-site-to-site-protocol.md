---
claims:
  claim-overview-scope:
    sources:
      - src-user-guide-site-to-site
  claim-overview-discovery:
    sources:
      - src-user-guide-site-to-site
  claim-overview-load-balance:
    sources:
      - src-user-guide-site-to-site
  claim-overview-handshake-compat:
    sources:
      - src-user-guide-site-to-site
  claim-overview-crc:
    sources:
      - src-user-guide-site-to-site
  claim-concepts-client-server:
    sources:
      - src-user-guide-site-to-site
  claim-concepts-push-pull:
    sources:
      - src-user-guide-site-to-site
  claim-handshake-site-detail:
    sources:
      - src-admin-guide-sequence
  claim-handshake-peers-transport:
    sources:
      - src-admin-guide-sequence
  claim-handshake-peer-metadata:
    sources:
      - src-admin-guide-sequence
  claim-handshake-transaction-flow:
    sources:
      - src-admin-guide-sequence
  claim-handshake-crc32:
    sources:
      - src-admin-guide-sequence
  claim-security-certs:
    sources:
      - src-user-guide-site-to-site
  claim-security-retrieve-policy:
    sources:
      - src-user-guide-remote-process-group
  claim-security-input-policy:
    sources:
      - src-user-guide-input-port
  claim-security-port-authorization:
    sources:
      - src-code-standard-public-port
  claim-config-host:
    sources:
      - src-admin-guide-properties
  claim-config-secure:
    sources:
      - src-admin-guide-properties
  claim-config-raw-port:
    sources:
      - src-admin-guide-properties
  claim-config-http-enabled:
    sources:
      - src-admin-guide-properties
  claim-config-transaction-ttl:
    sources:
      - src-admin-guide-properties
  claim-config-cache:
    sources:
      - src-admin-guide-properties
  claim-routing-peer-access:
    sources:
      - src-admin-guide-routing
  claim-routing-rules:
    sources:
      - src-admin-guide-routing
  claim-handshake-properties-batch:
    sources:
      - src-code-handshake-property
  claim-client-builder-url-port:
    sources:
      - src-code-site-to-site-client-builder
  claim-client-builder-timeouts:
    sources:
      - src-code-site-to-site-client-builder
  claim-client-builder-ssl:
    sources:
      - src-code-site-to-site-client-builder
  claim-client-builder-transport:
    sources:
      - src-code-site-to-site-client-builder
  claim-client-builder-batch:
    sources:
      - src-code-site-to-site-client-builder
  claim-handshake-response-codes:
    sources:
      - src-code-socket-client-protocol
  claim-http-listener-ttl:
    sources:
      - src-code-http-remote-site-listener
sources:
  src-user-guide-site-to-site:
    title: "Apache NiFi User Guide"
    href: "https://nifi.apache.org/docs/nifi-docs/html/user-guide.html"
    locator: "#site-to-site"
  src-user-guide-remote-process-group:
    title: "Apache NiFi User Guide"
    href: "https://nifi.apache.org/docs/nifi-docs/html/user-guide.html"
    locator: "#Site-to-Site_Remote_Process_Group"
  src-user-guide-input-port:
    title: "Apache NiFi User Guide"
    href: "https://nifi.apache.org/docs/nifi-docs/html/user-guide.html"
    locator: "#Site-to-Site_Input_Port"
  src-admin-guide-properties:
    title: "Apache NiFi System Administrator’s Guide"
    href: "https://nifi.apache.org/docs/nifi-docs/html/administration-guide.html"
    locator: "#site_to_site_properties"
  src-admin-guide-sequence:
    title: "Apache NiFi System Administrator’s Guide"
    href: "https://nifi.apache.org/docs/nifi-docs/html/administration-guide.html"
    locator: "#site_to_site_protocol_sequence"
  src-admin-guide-routing:
    title: "Apache NiFi System Administrator’s Guide"
    href: "https://nifi.apache.org/docs/nifi-docs/html/administration-guide.html"
    locator: "#site_to_site_reverse_proxy_properties"
  src-code-handshake-property:
    title: "HandshakeProperty.java"
    href: "https://github.com/apache/nifi/blob/main/nifi-commons/nifi-site-to-site-client/src/main/java/org/apache/nifi/remote/protocol/HandshakeProperty.java"
    locator: "L23-L58"
  src-code-site-to-site-client-builder:
    title: "SiteToSiteClient.java"
    href: "https://github.com/apache/nifi/blob/main/nifi-commons/nifi-site-to-site-client/src/main/java/org/apache/nifi/remote/client/SiteToSiteClient.java"
    locator: "L48-L640"
  src-code-standard-public-port:
    title: "StandardPublicPort.java"
    href: "https://github.com/apache/nifi/blob/main/nifi-framework-bundle/nifi-framework/nifi-site-to-site/src/main/java/org/apache/nifi/remote/StandardPublicPort.java"
    locator: "L341-L383"
  src-code-socket-client-protocol:
    title: "SocketClientProtocol.java"
    href: "https://github.com/apache/nifi/blob/main/nifi-commons/nifi-site-to-site-client/src/main/java/org/apache/nifi/remote/protocol/socket/SocketClientProtocol.java"
    locator: "L100-L203"
  src-code-http-remote-site-listener:
    title: "HttpRemoteSiteListener.java"
    href: "https://github.com/apache/nifi/blob/main/nifi-framework-bundle/nifi-framework/nifi-site-to-site/src/main/java/org/apache/nifi/remote/HttpRemoteSiteListener.java"
    locator: "L42-L133"
---

# Site-to-Site Data Movement

## Introduction / Overview
<span id="claim-overview-scope">NiFi Site-to-Site is the preferred protocol for securely moving data between NiFi nodes and external clients when building data flows.</span>
<span id="claim-overview-discovery">Remote ports on the target instance are discovered automatically after you register the remote NiFi URLs.</span>
<span id="claim-overview-load-balance">The protocol detects cluster membership changes and load balances transactions across the available nodes.</span>
<span id="claim-overview-handshake-compat">Each connection starts with a handshake that negotiates protocol versions so newer capabilities remain backward compatible.</span>
<span id="claim-overview-crc">Senders and receivers compare CRC32 checksums at the end of every transfer so corrupted batches can be retried safely.</span>

## Concepts / Architecture
<span id="claim-concepts-client-server">Any NiFi instance can act as client or server depending on the direction of a specific Site-to-Site exchange, even if it plays the opposite role in another flow.</span>
<span id="claim-concepts-push-pull">Push flows send data from a client into a remote input port, while pull flows let a client receive data exposed through a server output port.</span>

### Handshake Sequence
1. <span id="claim-handshake-site-detail">The client begins by calling `/nifi-api/site-to-site` to obtain remote port listings and the RAW and HTTP transport endpoints.</span>
2. <span id="claim-handshake-peers-transport">It then requests the peer list on the advertised transport port, switching to raw sockets for the RAW protocol while HTTP exchanges stay on HTTP(S).</span>
3. <span id="claim-handshake-peer-metadata">Peer responses include hostnames, ports, secure flags, and workload metrics that guide client-side peer selection.</span>
4. <span id="claim-handshake-transaction-flow">After choosing a peer, the client opens a transaction, the server accepts it, and the parties stream data in batches.</span>
5. <span id="claim-handshake-crc32">Both ends validate the transfer by comparing CRC32 hashes before committing the transaction.</span>

## Implementation / Configuration
<span id="claim-security-certs">Site-to-Site can apply certificates to encrypt traffic, authenticate callers, and hide ports from users who lack authorization.</span>

### Core Properties
- <span id="claim-config-host">Set `nifi.remote.input.host` to the hostname you want advertised to Site-to-Site clients.</span>
- <span id="claim-config-secure">Use `nifi.remote.input.secure` to enforce secure Site-to-Site and align it with other TLS properties.</span>
- <span id="claim-config-raw-port">Populate `nifi.remote.input.socket.port` whenever you intend to use the RAW socket transport.</span>
- <span id="claim-config-http-enabled">Toggle `nifi.remote.input.http.enabled` to control HTTP Site-to-Site, noting that HTTPS follows the `nifi.remote.input.secure` flag and the corresponding web port.</span>
- <span id="claim-config-transaction-ttl">Adjust `nifi.remote.input.http.transaction.ttl` so inactive HTTP transactions expire before clients go idle indefinitely.</span>
- <span id="claim-config-cache">Tune `nifi.remote.contents.cache.expiration` to balance remote metadata caching with freshness.</span>
- <span id="claim-handshake-properties-batch">Handshake properties cover compression, destination identifiers, request expiration, and optional batch count, size, or duration hints available from protocol version 5.</span>

### Security Controls
- <span id="claim-security-retrieve-policy">Secure deployments must grant the remote NiFi user or group the global “retrieve site-to-site details” policy so it can query ports and peer information.</span>
- <span id="claim-security-input-policy">Input and output ports need the “receive data via site-to-site” or “send data via site-to-site” component policies constrained to authorized users.</span>
- <span id="claim-security-port-authorization">At runtime, secure public ports validate distinguished names or mapped identities with the NiFi authorizer before allowing transfers.</span>

### Reverse Proxy Routing
- <span id="claim-routing-peer-access">Site-to-Site requires direct reachability to every node in the target cluster, so proxy deployments must ensure client traffic can be routed to each peer.</span>
- <span id="claim-routing-rules">Define `nifi.remote.route.{protocol}.{name}` rules with `when`, `hostname`, `port`, and `secure` fields to expose the correct endpoints based on request context.</span>

## Usage / Examples
<span id="claim-client-builder-url-port">The Java SiteToSiteClient builder refuses to construct a client unless you provide at least one remote URL and either a port name or identifier.</span>
<span id="claim-client-builder-timeouts">Builder options expose communication timeouts, node penalization periods, idle connection expiration, and cache expiration so you can tune connectivity.</span>
<span id="claim-client-builder-ssl">Keystore and truststore setters let the client supply TLS material when secure Site-to-Site is enforced.</span>
<span id="claim-client-builder-transport">You can select RAW or HTTP transport and attach proxy details directly on the builder.</span>
<span id="claim-client-builder-batch">Batch request methods specify preferred counts, sizes, or durations for pull transactions.</span>

```java
SiteToSiteClient client = new SiteToSiteClient.Builder()
    .url("https://nifi.example.com:8443/nifi")
    .portName("s2s-input")
    .transportProtocol(SiteToSiteTransportProtocol.HTTP)
    .keystoreFilename("/opt/client.p12")
    .keystorePass(System.getenv("SITE2SITE_KEYSTORE_PASS"))
    .keystoreType(KeystoreType.PKCS12)
    .truststoreFilename("/opt/ca.jks")
    .truststorePass(System.getenv("SITE2SITE_TRUSTSTORE_PASS"))
    .truststoreType(KeystoreType.JKS)
    .timeout(60, TimeUnit.SECONDS)
    .nodePenalizationPeriod(30, TimeUnit.SECONDS)
    .requestBatchCount(500)
    .requestBatchSize(16 * 1024 * 1024L)
    .requestBatchDuration(30, TimeUnit.SECONDS)
    .build();
```

## Best Practices / Tips
- <span id="claim-routing-peer-access">Keep proxy routing tables current whenever cluster membership changes so clients always reach every advertised peer.</span>
- <span id="claim-handshake-properties-batch">Use handshake batch hints to align transaction sizing with downstream expectations without modifying the server configuration.</span>

## Troubleshooting
- <span id="claim-handshake-response-codes">Handshake responses differentiate invalid ports, unknown ports, and destination capacity issues; surface the specific response to operators before retrying blindly.</span>
- <span id="claim-http-listener-ttl">HTTP Site-to-Site maintains a background task that expires idle transactions once they exceed the configured TTL, so stalled transfers usually indicate a client that stopped communicating.</span>

## Reference / Related Docs
- [Apache NiFi User Guide — Site-to-Site](https://nifi.apache.org/docs/nifi-docs/html/user-guide.html#site-to-site)
- [Apache NiFi System Administrator’s Guide — Site-to-Site Properties](https://nifi.apache.org/docs/nifi-docs/html/administration-guide.html#site_to_site_properties)
- [SiteToSiteClient API (GitHub)](https://github.com/apache/nifi/blob/main/nifi-commons/nifi-site-to-site-client/src/main/java/org/apache/nifi/remote/client/SiteToSiteClient.java)
- [Site-to-Site Server Components (GitHub)](https://github.com/apache/nifi/tree/main/nifi-framework-bundle/nifi-framework/nifi-site-to-site)
