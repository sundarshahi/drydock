#!/usr/bin/env bash
#
# load-protocol.sh — print a shared Drydock protocol to stdout as a SINGLE command.
#
# Replaces the old `cat A || cat B || cat C || true` skill loaders, which Claude
# Code's permission checker rejects as a multi-operation command (it decomposes
# at `||` and requires each sub-command to be allow-listed, and the plugin-root
# reads fall outside the project). One command keeps the loader a single, narrowly
# grantable operation: `Bash(bash "${CLAUDE_SKILL_DIR}/../_shared/load-protocol.sh" *)`.
#
# Resolution order (first existing wins), similar to scripts/bootstrap-workspace.sh
# but using a script-relative second candidate for robustness (env vars may be unset):
#   1. $CLAUDE_PLUGIN_ROOT/skills/_shared/protocols/<name>.md
#   2. <this script's dir>/protocols/<name>.md   (script-relative; always ships in-plugin)
#   3. drydock/.protocols/<name>.md              (runtime-deployed, cwd-relative)
#
# Always exits 0 (prints nothing when absent) so skill `!` expansion never errors;
# each skill's prose "Protocol Fallback" covers the not-found case.

set -u

name="${1:-}"
# Protocol names are static and trusted, but constrain to a safe slug charset so a
# stray argument can never traverse paths or read an arbitrary file.
case "$name" in
  '' | *[!a-z0-9-]*) exit 0 ;;
esac

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for f in \
  "${CLAUDE_PLUGIN_ROOT:-}/skills/_shared/protocols/${name}.md" \
  "${here}/protocols/${name}.md" \
  "drydock/.protocols/${name}.md"; do
  # Skip the first candidate when CLAUDE_PLUGIN_ROOT is unset (would be a bogus
  # absolute path beginning with /skills/...).
  case "$f" in /skills/_shared/protocols/*) continue ;; esac
  if [ -f "$f" ]; then
    cat "$f"
    exit 0
  fi
done

exit 0
