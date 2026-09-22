#!/usr/bin/env bash
# PostToolUse hook: repair the Japanese-Markdown breakages an agent just wrote.
#
# Runs scripts/md_lint.py on the file Write/Edit touched. The safe repairs are
# applied silently; what is left needs judgement, so it is handed back to the
# model instead. A swallowed or unterminated code fence deletes the rest of the
# note from every renderer, so that one blocks (exit 2); the others are advisory.
set -uo pipefail

# Resolve the vault from this script's own location (scripts/ -> vault root) so
# moving the vault does not silently disable the hook. It lives here rather than
# in .claude/ because a global gitignore excludes .claude/*, and this half is
# worth versioning.
VAULT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
LINT="$VAULT/scripts/md_lint.py"

f=$(jq -r '.tool_response.filePath // .tool_input.file_path // empty')
case "$f" in
  *.md) ;;
  *) exit 0 ;;
esac
[ -f "$f" ] || exit 0
[ -x "$LINT" ] || exit 0

"$LINT" fix "$f" >/dev/null 2>&1
out=$("$LINT" check "$f" 2>/dev/null)
[ -n "$out" ] || exit 0

if printf '%s' "$out" | grep -q 'FENCE-'; then
  printf 'Markdown が壊れています。修正してください:\n%s\n' "$out" >&2
  exit 2
fi

jq -n --arg c "残りの Markdown 破綻 (自動修正できないもの):
$out" '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$c}}'
