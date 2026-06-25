#!/usr/bin/env bash
#
# load-file.sh — print a project file (cat) or list a directory (ls) to stdout as
# a SINGLE command.
#
# Single-command replacement for the `cat <path> 2>/dev/null || echo/true` and
# `ls <dir> 2>/dev/null || true` config loaders. Those are multi-operation
# commands the permission checker rejects; this keeps the loader one narrowly
# grantable operation: `Bash(bash "${CLAUDE_SKILL_DIR}/../_shared/load-file.sh" *)`.
#
# Reads ONLY a caller-supplied path relative to the current project. Prints nothing
# and exits 0 when the path is absent, absolute, or traverses upward, so `!`
# expansion never errors and the script can never read outside the project.

set -u

p="${1:-}"
[ -z "$p" ] && exit 0

# Defense in depth: reject absolute paths and parent-directory traversal. All real
# callers pass project-relative paths (e.g. drydock/.orchestrator/settings.md).
case "$p" in
  /* | *..*) exit 0 ;;
esac

if [ -d "$p" ]; then
  ls -1 "$p" 2>/dev/null || true
elif [ -f "$p" ]; then
  cat "$p" 2>/dev/null || true
fi

exit 0
