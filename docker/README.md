# Docker Helpers

This folder contains small, runnable helpers for common NiFi-in-Docker ops and a place to keep overrides.

Goals
- Avoid rebuilding the image for simple config tweaks.
- Provide an in-place option (edit `nifi.properties` inside the container + restart) and an overlay option (mount a prepared `nifi.properties`).

Quick Start (in-place bind to all interfaces)
- Ensure a container named `nifi` is running.
- Run: `bash docker/bin/nifi-bind-all.sh nifi`
- Verify: `bash docker/bin/nifi-verify.sh nifi` (expects HTTP 401 from `/nifi-api/`).

Overlay workflow (persistent across container recreates)
Important: Do not bind‑mount a single file at `conf/nifi.properties`. NiFi's entrypoint uses `sed -i` on startup, which replaces the file via atomic rename. Replacing a bind‑mounted single file fails with “Device or resource busy.” Instead, mount the entire `conf/` directory.

1) Export the current conf directory (from a running or temporary container):
   - `docker cp nifi:/opt/nifi/nifi-current/conf docker/overrides/conf`  
     If the container isn't running, create a temporary one and copy:
   - `docker create --name nifi-tmp apache/nifi:2.6.0 >/dev/null`
   - `docker cp nifi-tmp:/opt/nifi/nifi-current/conf docker/overrides/conf`
   - `docker rm -f nifi-tmp >/dev/null`
2) Edit locally (at minimum):
   - `sed -i 's/^nifi.web.https.host=.*/nifi.web.https.host=0.0.0.0/' docker/overrides/conf/nifi.properties`
   - Ensure write perms so NiFi can update values on start: `chmod -R u+rwX docker/overrides/conf`
3) Recreate container with the conf directory mounted (read‑write):
   ```bash
   docker rm -f nifi || true
   docker run -d --name nifi \
     -p 18081-18180:18081-18180 \
     -p 8443:8443 \
     -e SINGLE_USER_CREDENTIALS_USERNAME=admin \
     -e SINGLE_USER_CREDENTIALS_PASSWORD='changeMe123!' \
     -v "$PWD/docker/overrides/conf:/opt/nifi/nifi-current/conf" \
     apache/nifi:2.6.0
   ```

Notes
- Do not set `NIFI_WEB_PROXY_HOST` to `0.0.0.0`. If you use a reverse proxy, set it to your external host:port.
- The default server certificate is `CN=localhost`. Prefer `https://localhost:8443` for NiFi self-calls in flows. If you must call `https://$(hostname):8443`, either reissue the server cert with SANs including that hostname or set InvokeHTTP Hostname Verifier to a relaxed mode for that specific internal call.

