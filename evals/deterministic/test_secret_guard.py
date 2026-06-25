#!/usr/bin/env python3
"""Behavioral guard for hooks/secret-guard.sh — the PreToolUse secret hook.

WHAT THIS GUARDS / WHY IT MATTERS
---------------------------------
The deterministic frontmatter/manifest tests prove the hook is *wired*; they do
not prove it *behaves*. This test drives the real shell script with crafted hook
payloads and asserts its allow/block decisions (exit 0 vs exit 2). It pins three
regressions found in audit:

  * NotebookEdit cell bodies (`.tool_input.new_source`) must be scanned — they
    were previously invisible, so a secret pasted into a notebook cell passed.
  * A glob that merely appears in a commit MESSAGE (e.g. "ignore *.pem files")
    must NOT be mistaken for a staged secret path (it used to be glob-expanded
    against the working tree and falsely blocked).
  * `git add <new-untracked-file>` whose bytes contain a secret must block — new
    untracked files don't show up in `git diff`, so their contents are scanned
    directly.

It also pins the baseline true-positives (Write/Edit content, secret-bearing
paths, explicit `git add` of a secret file) so a future refactor can't silently
weaken them.

Pure stdlib. Shells out to `bash` (and `git` for the staging cases); skips
gracefully if those binaries are absent so the suite never hard-fails on a host
that lacks them.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "hooks" / "secret-guard.sh"

# A private-key header is detected by BOTH gitleaks and the built-in regex
# fallback, so this test is deterministic regardless of whether gitleaks is
# installed on the host (unlike the canonical AKIA…EXAMPLE key, which some
# gitleaks allowlists deliberately ignore).
PEM = (
    "-----BEGIN RSA PRIVATE KEY-----\n"
    "MIIBOwIBAAJBAKj34GkxFhD90vcNLYLInFEX6Ppy1tPf9Cnzj4p4WGeKLs1Pt8Qu\n"
    "KUpRKfFLfRYC9AIKjbJTWit+CqvjWYzvQwECAwEAAQ==\n"
    "-----END RSA PRIVATE KEY-----"
)

ALLOW, BLOCK = 0, 2


def _run(payload: dict, cwd: Path) -> tuple[int, str]:
    env = dict(os.environ)
    env.pop("DRYDOCK_ALLOW_SECRET", None)  # never run with the bypass on
    proc = subprocess.run(
        ["bash", str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
    )
    return proc.returncode, (proc.stdout + proc.stderr)


def _git(args: list[str], cwd: Path) -> None:
    env = dict(os.environ)
    env.update(
        {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t.t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t.t",
        }
    )
    subprocess.run(
        ["git", *args], cwd=str(cwd), env=env, capture_output=True, text=True, check=True
    )


def run() -> list[str]:
    failures: list[str] = []

    if shutil.which("bash") is None:
        print("SKIP: bash not on PATH; cannot exercise secret-guard.sh")
        return failures
    if not HOOK.is_file():
        failures.append(f"hook not found: {HOOK}")
        return failures

    def expect(label, rc, want, out):
        if rc != want:
            failures.append(f"{label}: expected exit {want}, got {rc} :: {out.strip()[:200]}")

    # --- content scanning across tools (no git needed) ---------------------
    with tempfile.TemporaryDirectory() as d:
        cwd = Path(d)

        rc, out = _run(
            {"tool_name": "Write",
             "tool_input": {"file_path": "a.py", "content": f"k = '''{PEM}'''"}}, cwd)
        expect("Write w/ private key -> BLOCK", rc, BLOCK, out)

        # Regression: NotebookEdit cell body was not scanned before.
        rc, out = _run(
            {"tool_name": "NotebookEdit",
             "tool_input": {"notebook_path": "n.ipynb", "new_source": f"k = '''{PEM}'''"}}, cwd)
        expect("NotebookEdit secret in new_source -> BLOCK", rc, BLOCK, out)

        rc, out = _run(
            {"tool_name": "Write",
             "tool_input": {"file_path": "a.py", "content": "print('hello world')"}}, cwd)
        expect("clean Write -> ALLOW", rc, ALLOW, out)

        rc, out = _run(
            {"tool_name": "Write",
             "tool_input": {"file_path": "config/.env", "content": "X=1"}}, cwd)
        expect("Write to .env path -> BLOCK", rc, BLOCK, out)

    # --- git staging tests --------------------------------------------------
    if shutil.which("git") is None:
        print("SKIP: git not on PATH; ran content-only checks")
        return failures

    with tempfile.TemporaryDirectory() as d:
        repo = Path(d)
        _git(["init", "-q"], repo)
        (repo / "seed.txt").write_text("seed\n")
        _git(["add", "seed.txt"], repo)
        _git(["commit", "-q", "-m", "init"], repo)

        # Regression: a glob in a commit MESSAGE must not be treated as a path,
        # even when a matching secret-named file exists but is NOT staged.
        (repo / "leaked.pem").write_text("this file is not staged\n")
        rc, out = _run(
            {"tool_name": "Bash",
             "tool_input": {"command": 'git commit -m "ignore *.pem files"'}}, repo)
        expect("commit message mentioning '*.pem' -> ALLOW", rc, ALLOW, out)

        # True positive preserved: explicitly staging an existing secret path.
        rc, out = _run(
            {"tool_name": "Bash", "tool_input": {"command": "git add leaked.pem"}}, repo)
        expect("git add of existing *.pem path -> BLOCK", rc, BLOCK, out)

        # Regression: new untracked file whose bytes contain a secret must block.
        (repo / "notes.txt").write_text(f"key = '''{PEM}'''\n")
        rc, out = _run(
            {"tool_name": "Bash", "tool_input": {"command": "git add notes.txt"}}, repo)
        expect("git add of untracked file w/ secret -> BLOCK", rc, BLOCK, out)

    return failures


if __name__ == "__main__":
    fails = run()
    if not fails:
        print(f"PASS: {Path(__file__).relative_to(ROOT).as_posix()}")
        sys.exit(0)
    for f in fails:
        print(f"FAIL: {f}")
    sys.exit(1)
