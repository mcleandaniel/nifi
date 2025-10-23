#!/usr/bin/env bash
set -euo pipefail

# nifi_trust_helper.sh
#
# Manage trusted server certificates for NiFi inside the NiFi container.
# - Import NiFi's own HTTPS server certificate into the truststore (local mode)
# - Fetch a remote server certificate and import it into the truststore (remote mode)
#
# Defaults are discovered from /opt/nifi/nifi-current/conf/nifi.properties.
# You can override via flags. Works with PKCS12 (default), JKS, or BCFKS.
#
# Usage examples (run inside the NiFi container):
#   # 1) Trust this NiFi's own HTTPS certificate (useful for InvokeHTTP -> https://$(hostname):8443)
#   automation/scripts/nifi_trust_helper.sh local --alias local-nifi
#
#   # 2) Trust an external HTTPS endpoint's certificate
#   automation/scripts/nifi_trust_helper.sh remote --url https://api.example.com:443 --alias api-example
#
#   # 3) Specify/override truststore explicitly
#   automation/scripts/nifi_trust_helper.sh remote \
#     --url https://minio:9000 \
#     --truststore /opt/nifi/nifi-current/conf/truststore.p12 \
#     --truststore-pass changeMe123! \
#     --truststore-type PKCS12 \
#     --alias minio
#
# Notes
# - After modifying a truststore used by a StandardSSLContextService, disable/enable the service in NiFi (or restart) so it reloads the truststore.
# - The script creates a timestamped backup alongside the truststore before importing.

NF_CONF_DIR=${NF_CONF_DIR:-/opt/nifi/nifi-current/conf}
NF_PROPS=${NF_PROPS:-"$NF_CONF_DIR/nifi.properties"}

mode=""
url=""
alias_name=""
host=""
port=""
ts_file=""
ts_pass=""
ts_type=""
ks_file=""
ks_pass=""
ks_type=""

err() { echo "[trust] ERROR: $*" >&2; exit 1; }
log() { echo "[trust] $*" >&2; }

prop() {
  # Read a property from nifi.properties (simple key=value, ignoring comments)
  local key=$1
  grep -E "^${key}=" "$NF_PROPS" | tail -n1 | sed -E "s/^${key}=//"
}

backup_truststore() {
  local f=$1
  if [ -f "$f" ]; then
    local ts
    ts=$(date +%Y%m%d%H%M%S)
    cp -p "$f" "${f}.bak-${ts}"
    log "Backed up truststore to ${f}.bak-${ts}"
  fi
}

detect_defaults() {
  if [ -z "$ts_file" ]; then ts_file=$(prop nifi.security.truststore) || true; fi
  if [ -z "$ts_pass" ]; then ts_pass=$(prop nifi.security.truststorePasswd) || true; fi
  if [ -z "$ts_type" ]; then ts_type=$(prop nifi.security.truststoreType) || true; fi
  if [ -z "$ks_file" ]; then ks_file=$(prop nifi.security.keystore) || true; fi
  if [ -z "$ks_pass" ]; then ks_pass=$(prop nifi.security.keystorePasswd) || true; fi
  if [ -z "$ks_type" ]; then ks_type=$(prop nifi.security.keystoreType) || true; fi

  ts_type=${ts_type:-PKCS12}
  ks_type=${ks_type:-PKCS12}

  if [ -z "$ts_file" ] || [ -z "$ts_pass" ]; then
    err "Could not determine truststore path/password from $NF_PROPS; please pass --truststore and --truststore-pass"
  fi
}

fetch_remote_cert() {
  # Fetch server certificate(s) in PEM. Prefer openssl s_client if available; fallback to keytool -printcert -sslserver
  local target=$1
  if command -v openssl >/dev/null 2>&1; then
    # shellcheck disable=SC2005
    echo "$(
      echo | openssl s_client -showcerts -verify 0 -connect "$target" -servername "${target%%:*}" 2>/dev/null |
      sed -n '/BEGIN CERTIFICATE/,/END CERTIFICATE/p'
    )"
  else
    keytool -printcert -rfc -sslserver "$target" 2>/dev/null |
      sed -n '/BEGIN CERTIFICATE/,/END CERTIFICATE/p'
  fi
}

import_pem_into_truststore() {
  local pem_path=$1
  local alias=$2
  backup_truststore "$ts_file"
  keytool -importcert -noprompt \
    -alias "$alias" \
    -file "$pem_path" \
    -keystore "$ts_file" \
    -storetype "$ts_type" \
    -storepass "$ts_pass"
  log "Imported alias '$alias' into $ts_file ($ts_type)"
}

make_temp() {
  mktemp "${NF_CONF_DIR%/}/cert-XXXXXX.pem"
}

split_pem_chain() {
  # Split a PEM stream with one or more certs into temp files; echo paths
  local pem_stream=$1
  local out_dir=${2:-$NF_CONF_DIR}
  awk 'BEGIN{n=0} /BEGIN CERTIFICATE/{n++} {print > ("'"${out_dir%/}"/cert-" n ".pem")}' <<< "$pem_stream"
  ls -1 "${out_dir%/}"/cert-*.pem 2>/dev/null || true
}

usage() {
  cat <<USAGE
Usage:
  $0 local [--host \\$(hostname)] [--port 8443] [--alias name] [--truststore FILE] [--truststore-pass PASS] [--truststore-type PKCS12|JKS|BCFKS]
  $0 remote --url https://host:port [--alias name] [--truststore FILE] [--truststore-pass PASS] [--truststore-type PKCS12|JKS|BCFKS]

Options:
  --truststore FILE         Path to truststore (defaults from nifi.properties)
  --truststore-pass PASS    Truststore password (defaults from nifi.properties)
  --truststore-type TYPE    Truststore type (PKCS12|JKS|BCFKS). Default: PKCS12 or value from nifi.properties
  --alias NAME              Alias to import under (default: local-nifi for local; derived from host for remote)
  --url URL                 Remote HTTPS URL (e.g., https://api.example.com:443)
  --host HOST               Host for local mode (default: \\$(hostname))
  --port PORT               Port for local mode (default: 8443)

Notes:
  - After import, disable/enable the SSL Context Service in NiFi (or restart) to pick up changes.
  - This script must run inside the NiFi container so paths match nifi.properties.
USAGE
}

# Parse args
if [ $# -lt 1 ]; then usage; exit 1; fi
mode=$1; shift
while [ $# -gt 0 ]; do
  case "$1" in
    --truststore) ts_file=$2; shift 2 ;;
    --truststore-pass) ts_pass=$2; shift 2 ;;
    --truststore-type) ts_type=$2; shift 2 ;;
    --alias) alias_name=$2; shift 2 ;;
    --url) url=$2; shift 2 ;;
    --host) host=$2; shift 2 ;;
    --port) port=$2; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) err "Unknown option: $1" ;;
  esac
done

detect_defaults

case "$mode" in
  local)
    host=${host:-$(hostname)}
    port=${port:-8443}
    alias_name=${alias_name:-local-nifi}
    target="${host}:${port}"
    pem_stream=$(fetch_remote_cert "$target")
    if [ -z "$pem_stream" ]; then
      err "Failed to fetch certificate(s) from https://$target"
    fi
    files=$(split_pem_chain "$pem_stream" "$NF_CONF_DIR")
    idx=0
    for f in $files; do
      sfx=${idx}
      a="$alias_name"
      if [ "$idx" -gt 0 ]; then a="${alias_name}-${sfx}"; fi
      import_pem_into_truststore "$f" "$a"
      rm -f "$f" || true
      idx=$((idx+1))
    done
    ;;
  remote)
    [ -n "$url" ] || err "--url is required for remote mode"
    # Normalize URL to host:port
    host=$(echo "$url" | sed -E 's#^https?://([^/:]+).*#\1#')
    port=$(echo "$url" | sed -nE 's#^https?://[^/:]+:([0-9]+).*#\1#p')
    port=${port:-443}
    target="${host}:${port}"
    alias_name=${alias_name:-$host}
    tmp=$(make_temp)
    trap 'rm -f "$tmp"' EXIT
    log "Fetching certificate from $target"
    fetch_remote_cert "$target" > "$tmp"
    if ! grep -q "BEGIN CERTIFICATE" "$tmp"; then
      err "Failed to fetch certificate from $target. Ensure host/port reachable."
    fi
    import_pem_into_truststore "$tmp" "$alias_name"
    ;;
  *)
    usage; exit 1 ;;
esac

log "Done. If this truststore backs an SSL Context Service, disable/enable that service to reload."
