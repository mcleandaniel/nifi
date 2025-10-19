#!/usr/bin/env bash
set -euo pipefail

PLANS_DIR="kb/plans"
INDEX_FILE="${PLANS_DIR}/index.json"
OUT_PROMPTS_DIR="kb/drafts"
OUT_GENERATED_DIR="kb/generated"
CODEX_CMD="codex"   # change if your CLI name differs

log()  { printf '[INFO] %s\n' "$*"; }
err()  { printf '[ERROR] %s\n' "$*" >&2; exit 1; }

command -v jq >/dev/null 2>&1 || err "jq not found"
command -v "${CODEX_CMD}" >/dev/null 2>&1 || err "${CODEX_CMD} not found"
[ -f "${INDEX_FILE}" ] || err "Missing ${INDEX_FILE}"

mkdir -p "${OUT_PROMPTS_DIR}" "${OUT_GENERATED_DIR}"

resolve_path() {
  local p="$1"
  [ -f "$p" ] && { printf '%s\n' "$p"; return 0; }
  [ -f "kb/$p" ] && { printf '%s\n' "kb/$p"; return 0; }
  [ -f "kb/plans/$p" ] && { printf '%s\n' "kb/plans/$p"; return 0; }
  local s="${p#kb/}"
  [ -f "$s" ] && { printf '%s\n' "$s"; return 0; }
  local base; base="$(basename "$p")"
  [ -f "${PLANS_DIR}/${base}" ] && { printf '%s\n' "${PLANS_DIR}/${base}"; return 0; }
  return 1
}

# jq selectors with fallbacks for common nestings
SCOPE_JQ='.scope // .plan.scope // .data.scope'
TOPICS_JQ='.topics // .plan.topics // .data.topics'

log "Starting single-process run"
log "Index: ${INDEX_FILE}"

plans_tmp="$(mktemp)"
jq -r '.plans[].path' "${INDEX_FILE}" > "${plans_tmp}"

plans_processed=0
topics_run=0

while IFS= read -r index_path; do
  [ -z "${index_path}" ] && continue
  if [ "$(basename "${index_path}")" = "index.json" ]; then
    continue
  fi

  if ! plan_file="$(resolve_path "${index_path}")"; then
    err "Plan path in index not found on disk: ${index_path}"
  fi
  log "Plan entry: ${index_path}"
  log "Resolved to: ${plan_file}"

  # Validate we can extract scope and topics with fallbacks
  scope="$(jq -er "${SCOPE_JQ}" "${plan_file}" 2>/dev/null || true)"
  if [ -z "${scope}" ] || [ "${scope}" = "null" ]; then
    log "Plan keys:"; jq -r 'keys_unsorted[]' "${plan_file}" || true
    err "Could not find .scope at root/plan/data in ${plan_file}"
  fi

  topics_len="$(jq -er "${TOPICS_JQ} | length" "${plan_file}" 2>/dev/null || echo "")"
  if [ -z "${topics_len}" ]; then
    # Show where it failed
    jq -r '
      {
        root_topics_type: (.topics|type?),
        plan_topics_type: (.plan.topics|type?),
        data_topics_type: (.data.topics|type?)
      }' "${plan_file}" || true
    err "Could not find a topics array at root/plan/data in ${plan_file}"
  fi

  plan_id="$(basename "${plan_file%.*}")"
  log "Plan: ${plan_id} (scope: ${scope}, topics: ${topics_len})"
  plans_processed=$((plans_processed+1))

  out_prompt_dir="${OUT_PROMPTS_DIR}/${scope}/${plan_id}"
  out_generated_dir="${OUT_GENERATED_DIR}/${scope}/${plan_id}"
  mkdir -p "${out_prompt_dir}" "${out_generated_dir}"

  topics_tmp="$(mktemp)"
  jq -c "${TOPICS_JQ}[]" "${plan_file}" > "${topics_tmp}"

  idx=0
  while IFS= read -r topic_json; do
    idx=$((idx+1))
    topic_id="$(printf '%s' "${topic_json}" | jq -r '.id')"
    title="$(printf '%s' "${topic_json}" | jq -r '.title')"
    summary="$(printf '%s' "${topic_json}" | jq -r '.summary')"
    category="$(printf '%s' "${topic_json}" | jq -r '.category')"
    priority="$(printf '%s' "${topic_json}" | jq -r '.priority')"
    tags="$(printf '%s' "${topic_json}" | jq -r '[.tags[]] | join(", ")')"
    research_request="$(printf '%s' "${topic_json}" | jq -r '.research_request')"
    sources="$(printf '%s' "${topic_json}" | jq -r '.recommended_sources[]?' 2>/dev/null || true)"

    [ -z "${topic_id}" ] && err "Missing topic id in ${plan_file} (topic index ${idx})"

    full_id="${plan_id}_${topic_id}"
    prompt_file="${out_prompt_dir}/${full_id}.md"
    generated_file="${out_generated_dir}/${full_id}.md"

    log "  Topic ${idx}/${topics_len}: ${full_id}"

    {
      echo "# Task"
      echo "${research_request}"
      echo
      echo "# Context"
      echo "Scope: ${scope}"
      echo "Plan ID: ${plan_id}"
      echo "Topic ID: ${full_id}"
      echo "Category: ${category}"
      echo "Priority: ${priority}"
      echo "Tags: ${tags}"
      echo "Recommended Sources:"
      if [ -n "${sources}" ]; then
        printf '%s\n' "${sources}" | sed 's/^/- /'
      else
        echo "- None specified"
      fi
      echo
      echo "# Objective"
      echo "${summary}"
      echo
      echo "# Title"
      echo "${title}"
      echo
      echo "---"
      echo
      echo "Provide a comprehensive, evidence-based response using the context above."
    } > "${prompt_file}"

    "${CODEX_CMD}" -p "$(cat "${prompt_file}")" > "${generated_file}"
    topics_run=$((topics_run+1))
  done < "${topics_tmp}"

  rm -f "${topics_tmp}"
done < "${plans_tmp}"

rm -f "${plans_tmp}"

log "Done. Plans processed: ${plans_processed}, topics executed: ${topics_run}"
log "Prompts under: ${OUT_PROMPTS_DIR}"
log "Outputs under: ${OUT_GENERATED_DIR}"

