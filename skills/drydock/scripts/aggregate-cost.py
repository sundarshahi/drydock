#!/usr/bin/env python3
"""aggregate-cost.py — deterministically aggregate effort/cost metrics across
all orchestrator receipts for the final summary.

Replaces the prose "Cost aggregation for final summary" procedure: instead of
the orchestrator re-summing effort fields from memory (lossy, error-prone), it
runs this script and renders the returned JSON into the final summary box.

Reads:
  drydock/.orchestrator/receipts/*.json   — one receipt per completed task
  drydock/.orchestrator/rework-log.md      — gate rework cycles (optional)

Each receipt may carry an `effort` object {files_read, files_written,
tool_calls} and an `artifacts` list. Missing/garbage fields are treated as zero
so a single malformed receipt never breaks the summary.

Emits JSON to stdout:
  {agents, tool_calls, files_read, files_written, files_total,
   unique_artifacts, rework_cycles}

Usage:
  python3 aggregate-cost.py [WORKSPACE_DIR]   (default: ./drydock)
"""

from __future__ import annotations

import glob
import json
import os
import sys


def _as_int(v) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def aggregate(workspace: str) -> dict:
    receipts_dir = os.path.join(workspace, ".orchestrator", "receipts")
    rework_log = os.path.join(workspace, ".orchestrator", "rework-log.md")

    files = sorted(glob.glob(os.path.join(receipts_dir, "*.json")))
    agents = len(files)
    tool_calls = files_read = files_written = 0
    artifacts: set[str] = set()

    for path in files:
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        effort = data.get("effort") if isinstance(data.get("effort"), dict) else {}
        tool_calls += _as_int(effort.get("tool_calls"))
        files_read += _as_int(effort.get("files_read"))
        files_written += _as_int(effort.get("files_written"))
        for art in data.get("artifacts") or []:
            if isinstance(art, str):
                artifacts.add(art)

    rework_cycles = 0
    if os.path.isfile(rework_log):
        try:
            with open(rework_log, encoding="utf-8") as fh:
                rework_cycles = fh.read().count("## Gate")
        except OSError:
            rework_cycles = 0

    return {
        "agents": agents,
        "tool_calls": tool_calls,
        "files_read": files_read,
        "files_written": files_written,
        "files_total": files_read + files_written,
        "unique_artifacts": len(artifacts),
        "rework_cycles": rework_cycles,
    }


def main(argv: list[str]) -> int:
    workspace = argv[1] if len(argv) > 1 else "drydock"
    print(json.dumps(aggregate(workspace), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
