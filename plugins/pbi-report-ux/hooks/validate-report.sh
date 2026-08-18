#!/usr/bin/env bash
# PostToolUse: stdin = hook JSON. Діє лише на report.json; без python — тихий пас.
set -u
payload=$(cat)
f=$(printf '%s' "$payload" | { command -v jq >/dev/null 2>&1 && jq -r '.tool_input.file_path // .tool_response.filePath // empty'; } 2>/dev/null)
if [ -z "${f:-}" ]; then
  f=$(printf '%s' "$payload" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
fi
case "${f:-}" in
  *report.json) ;;
  *) exit 0 ;;
esac
PY=$(command -v python || command -v python3 || true)
[ -z "$PY" ] && exit 0
"$PY" "${CLAUDE_PLUGIN_ROOT}/hooks/check_report.py" "$f"
