#!/usr/bin/env bash
# PostToolUse: stdin = hook JSON. Діє на файли звіту Power BI обох форматів:
# report.json (Legacy) і PBIR enhanced — *.bookmark.json, bookmarks.json,
# visual.json, page.json, pages.json.
# Вимикач: POWERBI_CRAFT_HOOKS=0. Без python — тихий пас.
set -u
[ "${POWERBI_CRAFT_HOOKS:-1}" = "0" ] && exit 0
payload=$(cat)
f=$(printf '%s' "$payload" | { command -v jq >/dev/null 2>&1 && jq -r '.tool_input.file_path // .tool_response.filePath // empty'; } 2>/dev/null)
if [ -z "${f:-}" ]; then
  f=$(printf '%s' "$payload" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
fi
case "${f:-}" in
  *report.json|*.bookmark.json|*/bookmarks.json|*/visual.json|*/page.json|*/pages.json) ;;
  *) exit 0 ;;
esac
# python: звичайний -> python3 -> Windows-лаунчер py -3
# (на Windows "python" часто є заглушкою Microsoft Store)
if command -v python >/dev/null 2>&1 && python -c "" >/dev/null 2>&1; then
  exec python "${CLAUDE_PLUGIN_ROOT}/hooks/check_report.py" "$f"
elif command -v python3 >/dev/null 2>&1; then
  exec python3 "${CLAUDE_PLUGIN_ROOT}/hooks/check_report.py" "$f"
elif command -v py >/dev/null 2>&1; then
  exec py -3 "${CLAUDE_PLUGIN_ROOT}/hooks/check_report.py" "$f"
fi
exit 0
