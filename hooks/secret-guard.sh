#!/usr/bin/env bash
# Drydock Secret Guard  (PreToolUse hook)
# ---------------------------------------------------------------------------
# Closes the "Security Hooks (Continuous)" claim in skills/drydock/SKILL.md.
#
# This is a REAL enforcement hook. It runs before Write|Edit and before
# Bash commands that stage/commit code (git add / git commit), and it:
#   (1) HARD-BLOCKS writing/editing/staging/committing secret-bearing paths
#       (.env, .env.*, *.key, *.pem, credentials.json, *.p12, *.pfx,
#        id_rsa, *.keystore)
#   (2) FAST-SCANS the target content (Write/Edit/MultiEdit/NotebookEdit), the
#       staged diff, AND the contents of files about to be added — including
#       brand-new untracked files — for known secret patterns + private-key
#       headers, using `gitleaks` when available, otherwise a built-in
#       grep/regex fallback.
#
# Exit codes (Claude Code PreToolUse convention):
#   0  -> allow the tool call (nothing matched)
#   2  -> BLOCK the tool call (stderr is shown to Claude / the user)
#
# Intentional, documented bypass (NOT default):
#   DRYDOCK_ALLOW_SECRET=1   -> allow with a loud warning on stderr.
#
# Dependency-light: pure bash + coreutils (grep, sed). `jq` and `gitleaks`
# are used opportunistically if present but are never required.
# ---------------------------------------------------------------------------

set -u

# --- read the hook payload from stdin (JSON) -------------------------------
PAYLOAD="$(cat 2>/dev/null || true)"

# --- extract tool_name, file_path, command, content -----------------------
# Prefer jq for robust JSON parsing; fall back to a tolerant grep/sed parse.
TOOL_NAME=""
FILE_PATH=""
COMMAND=""
CONTENT=""

json_get() {
  # json_get <jq-filter> : echoes value or empty string
  if [ -n "$PAYLOAD" ] && command -v jq >/dev/null 2>&1; then
    printf '%s' "$PAYLOAD" | jq -r "$1 // empty" 2>/dev/null
  fi
}

# Crude fallback extractor for "key": "value" used only when jq is absent.
# Portable across BSD (macOS) and GNU sed: POSIX BRE only, no \| alternation.
# Two passes: a "short" non-greedy-ish capture (stops at first quote -> good for
# paths/tool names) and a "long" greedy capture (captures up to the last quote
# on the line -> errs toward MORE content, which is the safe bias for scanning).
fallback_get() {
  # fallback_get <key> [long]
  local flat val
  flat="$(printf '%s' "$PAYLOAD" | tr -d '\n')"
  if [ "${2:-}" = "long" ]; then
    # Greedy: everything between this key's opening quote and the last quote.
    val="$(printf '%s' "$flat" \
      | sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\\(.*\\)\".*/\\1/p" \
      | head -n1)"
  else
    # Short: stop at the first closing quote (no embedded quotes expected).
    val="$(printf '%s' "$flat" \
      | sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p" \
      | head -n1)"
  fi
  printf '%s' "$val"
}

if [ -n "$PAYLOAD" ]; then
  TOOL_NAME="$(json_get '.tool_name')"
  FILE_PATH="$(json_get '.tool_input.file_path')"
  # NotebookEdit targets .notebook_path, not .file_path.
  [ -z "$FILE_PATH" ] && FILE_PATH="$(json_get '.tool_input.notebook_path')"
  COMMAND="$(json_get '.tool_input.command')"
  # Write uses .content; Edit uses .new_string; MultiEdit packs edits in
  # .edits[].new_string; NotebookEdit uses .new_source (the cell body).
  CONTENT="$(json_get '.tool_input.content')"
  [ -z "$CONTENT" ] && CONTENT="$(json_get '.tool_input.new_string')"
  [ -z "$CONTENT" ] && CONTENT="$(json_get '[.tool_input.edits[]?.new_string] | join("\n")')"
  [ -z "$CONTENT" ] && CONTENT="$(json_get '.tool_input.new_source')"

  if [ -z "$TOOL_NAME" ]; then TOOL_NAME="$(fallback_get tool_name)"; fi
  if [ -z "$FILE_PATH" ]; then FILE_PATH="$(fallback_get file_path)"; fi
  [ -z "$FILE_PATH" ] && FILE_PATH="$(fallback_get notebook_path)"
  if [ -z "$COMMAND" ]; then COMMAND="$(fallback_get command long)"; fi
  if [ -z "$CONTENT" ]; then
    CONTENT="$(fallback_get content long)"
    [ -z "$CONTENT" ] && CONTENT="$(fallback_get new_string long)"
    [ -z "$CONTENT" ] && CONTENT="$(fallback_get new_source long)"
  fi
fi

# Env-var fallbacks (some hook runners export these).
[ -z "$TOOL_NAME" ] && TOOL_NAME="${CLAUDE_TOOL_NAME:-}"
[ -z "$FILE_PATH" ] && FILE_PATH="${CLAUDE_TOOL_FILE_PATH:-}"

# --- secret-bearing path patterns (basename globs) -------------------------
# Matched against the basename of any path we can see.
is_secret_path() {
  # is_secret_path <path>
  local p base
  p="$1"
  [ -z "$p" ] && return 1
  base="$(basename -- "$p" 2>/dev/null)"
  [ -z "$base" ] && base="$p"
  case "$base" in
    .env|.env.*|*.env) return 0 ;;
    *.key|*.pem|*.p12|*.pfx|*.keystore) return 0 ;;
    credentials.json) return 0 ;;
    id_rsa|id_rsa.*|id_dsa|id_ecdsa|id_ed25519) return 0 ;;
  esac
  return 1
}

# --- loud, documented bypass ----------------------------------------------
if [ "${DRYDOCK_ALLOW_SECRET:-}" = "1" ]; then
  {
    echo "=============================================================="
    echo "  !!  DRYDOCK SECRET GUARD BYPASSED (DRYDOCK_ALLOW_SECRET=1)"
    echo "  !!  Secret-path and secret-content checks are DISABLED for"
    echo "  !!  this tool call. This is intentional and on YOU."
    echo "  !!  Unset DRYDOCK_ALLOW_SECRET to re-enable enforcement."
    echo "=============================================================="
  } >&2
  exit 0
fi

# --- helper: emit a block message and exit 2 -------------------------------
block() {
  {
    echo "BLOCKED by Drydock Secret Guard"
    echo "--------------------------------"
    echo "$1"
    echo ""
    echo "Why: secrets must never enter the working tree, the index, or history."
    echo "Fix: keep secrets out of code; use a secret manager / env injection;"
    echo "     add the path to .gitignore; reference values via env vars."
    echo "Bypass (discouraged, you accept the risk):"
    echo "     DRYDOCK_ALLOW_SECRET=1 <your action>"
  } >&2
  exit 2
}

# ===========================================================================
# (a) PATH-BASED HARD BLOCK
# ===========================================================================

# Write / Edit / MultiEdit -> check the target file path.
case "$TOOL_NAME" in
  Write|Edit|MultiEdit|NotebookEdit)
    if is_secret_path "$FILE_PATH"; then
      block "Tool '$TOOL_NAME' targets a secret-bearing path: $FILE_PATH"
    fi
    ;;
esac

# Bash -> only care about git add / git commit (and git stash that captures all).
GIT_STAGING=0
if [ "$TOOL_NAME" = "Bash" ] && [ -n "$COMMAND" ]; then
  if printf '%s' "$COMMAND" | grep -Eq '(^|[;&|[:space:]])git[[:space:]]+(add|commit|stash([[:space:]]+(push|save))?)([[:space:]]|$)'; then
    GIT_STAGING=1
    # Block obvious explicit staging of a secret path on the command line.
    # Tokenize on whitespace and inspect each argument's basename.
    #
    # Two guards prevent false positives on commit-message text:
    #   * `set -f` disables pathname expansion, so a glob that merely appears in
    #     the command (e.g. a message "ignore *.pem files") is NOT expanded
    #     against the working tree.
    #   * `[ -e "$tok" ]` requires the token to be a real existing path before
    #     treating it as a staged secret — a glob like "*.pem" or a message word
    #     does not name an existing file, while anything you can actually
    #     `git add` does. (You cannot stage a path that does not exist, so this
    #     never weakens detection.)
    set -f
    for tok in $COMMAND; do
      case "$tok" in
        -*|git|add|commit|stash|push|save) continue ;;
      esac
      [ -e "$tok" ] || continue
      if is_secret_path "$tok"; then
        set +f
        block "git command stages/commits a secret-bearing path: $tok
Command: $COMMAND"
      fi
    done
    set +f
  fi
fi

# ===========================================================================
# (b) CONTENT / STAGED-DIFF SCAN
# ===========================================================================

# Build a temp file holding the material to scan. Create it privately
# (umask 077) via a randomized template so we never write through a file or
# symlink an attacker may have pre-planted at a predictable path.
umask 077
SCRATCH="$(mktemp "${TMPDIR:-/tmp}/drydock-secret.XXXXXX" 2>/dev/null || true)"
if [ -z "$SCRATCH" ] || [ ! -f "$SCRATCH" ]; then
  # mktemp unavailable: create with noclobber (set -C) so an existing path is
  # not silently reused/truncated.
  SCRATCH="${TMPDIR:-/tmp}/drydock-secret-$$-${RANDOM:-0}${RANDOM:-0}.txt"
  if ! ( set -C; : > "$SCRATCH" ) 2>/dev/null; then
    echo "drydock secret-guard: cannot create a private temp file; skipping scan" >&2
    exit 0
  fi
fi
trap 'rm -f "$SCRATCH" 2>/dev/null' EXIT
: > "$SCRATCH"

HAVE_MATERIAL=0

# Write/Edit content -> scan the bytes being written.
if [ -n "$CONTENT" ]; then
  printf '%s\n' "$CONTENT" >> "$SCRATCH"
  HAVE_MATERIAL=1
fi

# git add/commit -> scan the staged diff (what is about to enter history) PLUS
# the contents of files this command is about to add. Brand-new untracked files
# do NOT appear in `git diff` or `git diff --cached` at PreToolUse time (the add
# has not run yet), so we read their bytes directly.
if [ "$GIT_STAGING" = "1" ] && command -v git >/dev/null 2>&1; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git diff --cached --no-color 2>/dev/null >> "$SCRATCH" || true
    git diff --no-color 2>/dev/null >> "$SCRATCH" || true
    HAVE_MATERIAL=1

    # Append up to 1 MB of a file's content (cap keeps huge blobs cheap).
    scan_file() { [ -n "$1" ] && [ -f "$1" ] && head -c 1048576 "$1" 2>/dev/null >> "$SCRATCH"; }

    # Figure out what the command stages: explicit path args vs. a broad add.
    _broad=0
    _named=""
    set -f
    for tok in $COMMAND; do
      case "$tok" in
        .|-A|--all|-a|--update|-u) _broad=1; continue ;;
        -*|git|add|commit|stash|push|save) continue ;;
      esac
      [ -e "$tok" ] && _named="$_named
$tok"
    done
    set +f

    if [ "$_broad" = "1" ]; then
      # Whole-tree staging: scan untracked + modified files (capped at 500).
      _n=0
      while IFS= read -r _f; do
        [ -z "$_f" ] && continue
        scan_file "$_f"
        _n=$((_n + 1))
        [ "$_n" -ge 500 ] && break
      done <<EOF
$(git status --porcelain 2>/dev/null | sed -e 's/^...//' -e 's/.* -> //')
EOF
    fi

    # Always scan explicitly-named files (covers `git add notes.txt`).
    printf '%s\n' "$_named" | while IFS= read -r _f; do scan_file "$_f"; done
  fi
fi

# Nothing to scan -> allow.
if [ "$HAVE_MATERIAL" = "0" ]; then
  exit 0
fi

# --- gitleaks fast path (preferred) ---------------------------------------
if command -v gitleaks >/dev/null 2>&1; then
  # gitleaks detect on a path source is fast and authoritative.
  GL_OUT="$(gitleaks detect --no-banner --no-git --source "$SCRATCH" 2>&1)"
  GL_RC=$?
  if [ "$GL_RC" -eq 0 ]; then
    exit 0  # gitleaks ran clean: no leaks.
  fi
  # A non-zero code means EITHER leaks were found OR gitleaks itself errored
  # (bad config, version skew, unreadable source). Only BLOCK when the output
  # looks like real findings; on a runtime error fall through to the built-in
  # regex fallback so a misconfigured gitleaks doesn't block every tool call.
  if printf '%s' "$GL_OUT" | grep -qiE 'finding|secret|rule|leak|fingerprint'; then
    DETAIL="$(printf '%s' "$GL_OUT" | grep -iE 'secret|rule|finding|line|file' | head -n 8)"
    block "gitleaks detected secret-like content in the material about to be written/committed.
${DETAIL:-(run gitleaks detect for full output)}"
  fi
  echo "drydock secret-guard: gitleaks exited $GL_RC without parseable findings; using built-in regex fallback." >&2
fi

# --- built-in regex fallback ----------------------------------------------
# Each pattern is high-signal to keep false positives low.
# We use grep -E and report the first matching rule.
scan_rule() {
  # scan_rule <human-name> <ERE>
  # NOTE: use `-e` so patterns beginning with '-' (e.g. PEM headers) are not
  # mistaken for grep options.
  if grep -EnaI -e "$2" "$SCRATCH" >/dev/null 2>&1; then
    HITLINE="$(grep -EnaI -e "$2" "$SCRATCH" 2>/dev/null | head -n1)"
    block "Detected secret pattern [$1] in content about to be written/committed.
First match (line:content, redacted-ish): ${HITLINE}"
  fi
}

# AWS access key id
scan_rule "AWS Access Key (AKIA/ASIA...)" '(A3T[A-Z0-9]|AKIA|ASIA|AGPA|AIDA|AROA|ANPA|ANVA)[A-Z0-9]{16}'
# Private key PEM headers (RSA/EC/OPENSSH/PGP/generic)
scan_rule "Private key header" '-----BEGIN ([A-Z ]+ )?PRIVATE KEY-----'
scan_rule "PGP private key block" '-----BEGIN PGP PRIVATE KEY BLOCK-----'
# GitHub tokens (classic + fine-grained + oauth/app/refresh)
scan_rule "GitHub token" '(ghp|gho|ghu|ghs|ghr|github_pat)_[A-Za-z0-9_]{20,}'
# Slack tokens + webhooks
scan_rule "Slack token" 'xox[baprs]-[A-Za-z0-9-]{10,}'
scan_rule "Slack webhook" 'https://hooks\.slack\.com/services/T[A-Za-z0-9_]+/B[A-Za-z0-9_]+/[A-Za-z0-9_]+'
# Google API key
scan_rule "Google API key" 'AIza[0-9A-Za-z_\-]{35}'
# Stripe secret/live keys
scan_rule "Stripe secret key" '(sk|rk)_(live|test)_[0-9A-Za-z]{20,}'
# Generic high-entropy assignment: api_key / secret / token / password = <long>
scan_rule "Generic secret assignment" '(api[_-]?key|secret[_-]?key|secret|access[_-]?token|auth[_-]?token|client[_-]?secret|password|passwd|pwd)["'"'"' ]*[:=][[:space:]]*["'"'"']?[A-Za-z0-9/+_\-]{16,}'
# AWS secret access key style (40-char base64-ish bound to aws context)
scan_rule "AWS secret access key" 'aws_secret_access_key["'"'"' ]*[:=][[:space:]]*["'"'"']?[A-Za-z0-9/+]{40}'
# JWT (three base64url segments)
scan_rule "JWT" 'eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}'

# Nothing matched.
exit 0
