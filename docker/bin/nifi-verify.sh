#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${1:-nifi}"

docker exec "$CONTAINER" bash -lc '
  set -euo pipefail
  CODE=$(curl -sS -o /dev/null -w "%{http_code}\n" -k https://localhost:8443/nifi-api/ || true)
  echo "HTTP ${CODE:-<no-response>} from /nifi-api/"
  test "$CODE" = "401"
'

