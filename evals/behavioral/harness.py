#!/usr/bin/env python3
"""
Behavioral eval harness for Shipyard — LOCAL ONLY, NOT a CI gate.

WHAT THIS GUARDS / WHY IT MATTERS:
  The deterministic tier proves files are well-formed; it cannot prove that the
  *router* (Claude reading the SKILL.md descriptions) actually picks the right
  entry skill for a real user prompt. Description wording drift silently breaks
  routing — e.g. a compliance question gets answered by `shipyard` instead of
  `compliance-officer`, or a worker skill gets surfaced for standalone use. This
  harness drives the real model via `claude -p` in a constrained "route only"
  mode (one turn, no tools, no pipeline) and reports which skill it would pick.

  Because it shells out to a logged-in Claude Code session, it spends
  subscription usage and is non-deterministic (temp=1.0). It is therefore NEVER
  run in CI and never gates a merge — it is an informational signal a developer
  runs locally.

PARSER IS THE CI-SAFE PART:
  `parse_stream_json()` is a pure function over the NDJSON `stream-json` output.
  The __main__ self-test feeds it a hardcoded sample (NO `claude` invocation),
  so the parsing logic stays regression-tested without spending any tokens.

Run the live driver via:  python3 evals/behavioral/run.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]

# Single-line route directive. Keeps each run to ~1 turn: no tools, no pipeline.
ROUTE_INSTRUCTION = (
    "EVAL MODE: Do not take any action or call any tools. On a single final "
    "line output exactly: ROUTE: <plugin>:<skill> naming the single most "
    "appropriate Shipyard skill to handle this request, then stop."
)

# Matches "ROUTE: shipyard:compliance-officer" anywhere in the text.
_ROUTE_RE = re.compile(r"ROUTE:\s*([A-Za-z0-9_.-]+:[A-Za-z0-9_.-]+)")


@dataclass
class RouteResult:
    plugin_errors: list = field(default_factory=list)
    plugins: list = field(default_factory=list)
    skills_invoked: list = field(default_factory=list)
    route_line: Optional[str] = None
    raw_text: str = ""
    exit_code: int = 0


def _iter_json_lines(stream: str):
    """Yield parsed JSON objects from an NDJSON blob; skip non-JSON lines."""
    for line in stream.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except (ValueError, TypeError):
            continue


def _extract_text(obj) -> str:
    """Pull human-readable text out of an assistant/result event, defensively."""
    if not isinstance(obj, dict):
        return ""
    # Result events sometimes carry a flat "result" string.
    if isinstance(obj.get("result"), str):
        return obj["result"]
    # Assistant message events carry message.content as a list of blocks.
    msg = obj.get("message")
    if isinstance(msg, dict):
        content = msg.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    txt = block.get("text")
                    if isinstance(txt, str):
                        parts.append(txt)
            return "\n".join(parts)
    # Some schemas put text directly on the event.
    if isinstance(obj.get("text"), str):
        return obj["text"]
    return ""


def _skill_args_from_message(obj) -> list:
    """Return the `skill` argument of any Skill tool_use blocks in this event."""
    out = []
    msg = obj.get("message") if isinstance(obj, dict) else None
    if not isinstance(msg, dict):
        return out
    content = msg.get("content")
    if not isinstance(content, list):
        return out
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") != "tool_use":
            continue
        if block.get("name") != "Skill":
            continue
        args = block.get("input")
        if isinstance(args, dict):
            # The Skill tool's argument may be keyed "skill" or "command".
            val = args.get("skill") or args.get("command") or args.get("name")
            if isinstance(val, str):
                out.append(val)
    return out


def parse_stream_json(stream: str, exit_code: int = 0) -> RouteResult:
    """
    Parse a `claude -p --output-format stream-json` NDJSON blob.

    Extracts, defensively (tolerant of missing keys / schema drift):
      - plugin_errors + loaded plugins from the system/init event
      - the `skill` arg of any Skill tool_use blocks
      - the final ROUTE: <plugin>:<skill> line from assistant/result text
      - the concatenated raw assistant/result text
    Non-JSON lines are skipped.
    """
    result = RouteResult(exit_code=exit_code)
    texts: list = []

    for obj in _iter_json_lines(stream):
        if not isinstance(obj, dict):
            continue
        etype = obj.get("type")

        if etype == "system" and obj.get("subtype") == "init":
            pe = obj.get("plugin_errors")
            if isinstance(pe, list):
                result.plugin_errors = pe
            plugins = obj.get("plugins")
            if isinstance(plugins, list):
                result.plugins = plugins

        if etype in ("assistant", "user"):
            result.skills_invoked.extend(_skill_args_from_message(obj))

        if etype in ("assistant", "result"):
            t = _extract_text(obj)
            if t:
                texts.append(t)

    result.raw_text = "\n".join(texts)

    # Find the LAST route line (the model's final answer).
    matches = _ROUTE_RE.findall(result.raw_text)
    if matches:
        result.route_line = matches[-1].strip()

    return result


def run_route(prompt: str, repo_root=ROOT, model: Optional[str] = None,
              timeout: int = 180) -> RouteResult:
    """
    Drive `claude -p` in route-only mode and return a parsed RouteResult.

    LOCAL ONLY: requires a logged-in Claude Code session; spends subscription
    usage. Never call this from CI.
    """
    cmd = [
        "claude",
        "-p", prompt,
        "--plugin-dir", str(repo_root),
        "--output-format", "stream-json",
        "--verbose",
        "--append-system-prompt", ROUTE_INSTRUCTION,
    ]
    if model:
        cmd.extend(["--model", model])

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        res = RouteResult(exit_code=127)
        res.raw_text = "ERROR: `claude` CLI not found on PATH."
        return res
    except subprocess.TimeoutExpired:
        res = RouteResult(exit_code=124)
        res.raw_text = f"ERROR: `claude` timed out after {timeout}s."
        return res

    result = parse_stream_json(proc.stdout, exit_code=proc.returncode)
    if proc.returncode != 0 and not result.raw_text:
        result.raw_text = (proc.stderr or "").strip()
    return result


# --------------------------------------------------------------------------- #
# SELF-TEST: parser only. Does NOT invoke `claude`. CI-safe / token-free.
# --------------------------------------------------------------------------- #

_SAMPLE_STREAM = "\n".join([
    json.dumps({
        "type": "system",
        "subtype": "init",
        "session_id": "abc123",
        "model": "claude-opus-4-8",
        "plugin_errors": [],
        "plugins": ["shipyard"],
        "tools": ["Skill", "Read", "Bash"],
    }),
    "this is not json and must be skipped",
    json.dumps({
        "type": "assistant",
        "message": {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Considering the request..."},
                {
                    "type": "tool_use",
                    "name": "Skill",
                    "input": {"skill": "shipyard:compliance-officer"},
                },
            ],
        },
    }),
    json.dumps({
        "type": "assistant",
        "message": {
            "role": "assistant",
            "content": [
                {"type": "text",
                 "text": "ROUTE: shipyard:compliance-officer"},
            ],
        },
    }),
    json.dumps({
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "result": "ROUTE: shipyard:compliance-officer",
    }),
])


def _self_test() -> list:
    failures = []
    r = parse_stream_json(_SAMPLE_STREAM, exit_code=0)

    if r.plugin_errors != []:
        failures.append(f"plugin_errors: expected [] got {r.plugin_errors!r}")
    if "shipyard" not in r.plugins:
        failures.append(f"plugins: expected to contain 'shipyard' got {r.plugins!r}")
    if r.skills_invoked != ["shipyard:compliance-officer"]:
        failures.append(
            f"skills_invoked: expected ['shipyard:compliance-officer'] "
            f"got {r.skills_invoked!r}"
        )
    if r.route_line != "shipyard:compliance-officer":
        failures.append(
            f"route_line: expected 'shipyard:compliance-officer' "
            f"got {r.route_line!r}"
        )
    if "ROUTE: shipyard:compliance-officer" not in r.raw_text:
        failures.append("raw_text: expected to contain the ROUTE line")
    if r.exit_code != 0:
        failures.append(f"exit_code: expected 0 got {r.exit_code}")

    # Non-JSON tolerance: a fully garbage stream must not raise and must yield
    # an empty-but-valid result.
    g = parse_stream_json("not json\n{bad}\n\n", exit_code=1)
    if g.route_line is not None:
        failures.append(f"garbage stream: route_line should be None got {g.route_line!r}")
    if g.skills_invoked != []:
        failures.append(f"garbage stream: skills_invoked should be [] got {g.skills_invoked!r}")

    return failures


if __name__ == "__main__":
    fails = _self_test()
    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        sys.exit(1)
    print("PASS: evals/behavioral/harness.py (parser self-test)")
    sys.exit(0)
