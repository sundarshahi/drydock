#!/usr/bin/env bash
#
# bootstrap-workspace.sh — deterministically scaffold the Drydock workspace and
# deploy the shared protocols. Replaces the prose "mkdir + copy protocols"
# procedure so the orchestrator runs ONE verified command instead of re-deriving
# a multi-step file operation every run.
#
# Creates:
#   drydock/.protocols/                    (shared protocols, deployed below)
#   drydock/.orchestrator/receipts/        (gate receipts)
#   drydock/.orchestrator/overrides/       (gate override receipts)
#
# Protocol source resolution (first existing wins), mirroring load-protocol.sh's
# resolution order:
#   1. $CLAUDE_PLUGIN_ROOT/skills/_shared/protocols
#   2. $CLAUDE_SKILL_DIR/../_shared/protocols
#   3. <this script>/../../_shared/protocols   (script-relative; always ships in-plugin)
#
# Exit 0 on success. If no protocol source can be located, it still creates the
# directories, prints a WARNING to stderr, and exits 0 so the orchestrator can
# fall back to writing protocols from the embedded summaries in full-build-setup.md.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p drydock/.protocols
mkdir -p drydock/.orchestrator/receipts
mkdir -p drydock/.orchestrator/overrides

PROTO_SRC=""
for cand in \
  "${CLAUDE_PLUGIN_ROOT:-}/skills/_shared/protocols" \
  "${CLAUDE_SKILL_DIR:-}/../_shared/protocols" \
  "$SCRIPT_DIR/../../_shared/protocols"; do
  # skip candidates whose env prefix is unset/empty (would resolve to a bogus path)
  case "$cand" in
    /skills/_shared/protocols|/../_shared/protocols) continue ;;
  esac
  if [ -d "$cand" ]; then PROTO_SRC="$cand"; break; fi
done

if [ -n "$PROTO_SRC" ]; then
  cp "$PROTO_SRC"/*.md drydock/.protocols/ 2>/dev/null || true
  count="$(find drydock/.protocols -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')"
  echo "✓ Workspace bootstrapped — deployed ${count} protocols to drydock/.protocols/ (source: ${PROTO_SRC})"
else
  echo "WARN: could not locate skills/_shared/protocols; directories created but protocols NOT deployed." >&2
  echo "      The orchestrator should write protocols from the embedded summaries in phases/full-build-setup.md." >&2
fi

exit 0
