#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${1:-nifi}"

echo "[bind-all] Target container: $CONTAINER"
docker exec "$CONTAINER" bash -lc '
  set -euo pipefail
  CONF="/opt/nifi/nifi-current/conf/nifi.properties"
  echo "[bind-all] Patching $CONF -> nifi.web.https.host=0.0.0.0"
  if grep -q "^nifi.web.https.host=" "$CONF"; then
    sed -i "s/^nifi.web.https.host=.*/nifi.web.https.host=0.0.0.0/" "$CONF"
  else
    echo "nifi.web.https.host=0.0.0.0" >> "$CONF"
  fi
  echo "[bind-all] Restarting NiFi"
  /opt/nifi/nifi-current/bin/nifi.sh restart
  echo "[bind-all] Waiting for HTTPS on localhost:8443"
  for i in $(seq 1 60); do
    if curl -skI https://localhost:8443/nifi-api/ >/dev/null 2>&1; then
      echo "[bind-all] NiFi is up"; exit 0
    fi
    sleep 2
  done
  echo "[bind-all] Timed out waiting for NiFi"; exit 1
'

