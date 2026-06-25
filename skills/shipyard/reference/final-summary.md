# Final Summary

## Final Summary Template

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ◆  SHIPYARD v{local_version} — COMPLETE    ⏱ {total}  ║
║   Project: {name}                                                ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   DEFINE    ✓ BRD ({N} stories, {M} criteria)                    ║
║             ✓ Architecture ({pattern}, {N} services)             ║
║                                                                  ║
║   BUILD     ✓ Backend ({N} services, {M} endpoints, {K} lines)   ║
║             ✓ Frontend ({N} page groups, {M} components)         ║
║             ✓ Containers ({N} Dockerfiles, 1 compose)            ║
║                                                                  ║
║   HARDEN    ✓ Security ({N} findings → {M} Critical remaining)   ║
║             ✓ QA ({N} tests, {M}% passing)                       ║
║             ✓ Code Review ({N} findings → all resolved)          ║
║                                                                  ║
║   SHIP      ✓ Infrastructure (Terraform, {N} environments)       ║
║             ✓ CI/CD ({provider}, {N} workflows)                  ║
║             ✓ SRE ({N} SLOs, {M} alerts, {K} runbooks)          ║
║                                                                  ║
║   SUSTAIN   ✓ Documentation ({N} docs generated)                 ║
║             ✓ Custom Skills ({N} project-specific)               ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   Agents: {N} used · Tasks: {M} completed · Errors: {K}         ║
║   Files: {N} created · Tests: {M} passing · Vulnerabilities: {K}║
║   Worktrees: {enabled|disabled} · Rework cycles: {N}            ║
║                                                                  ║
║   Cost       {N} agents · {M} total tool calls · {K} files      ║
║              Est. ~{X}K tokens · ~${A}-${B} at current pricing   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

**Cost aggregation for final summary:**

Run the bundled aggregation script and render its JSON into the box above (deterministic — don't re-sum receipts from memory):
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/shipyard/scripts/aggregate-cost.py" 2>/dev/null \
  || python3 "${CLAUDE_SKILL_DIR}/scripts/aggregate-cost.py"
```
It reads every receipt in `Shipyard/.orchestrator/receipts/` plus `Shipyard/.orchestrator/rework-log.md` and emits `{agents, tool_calls, files_read, files_written, files_total, unique_artifacts, rework_cycles}` (malformed receipts skipped, artifacts deduplicated). Use those numbers directly for Agents / total tool calls / files / rework cycles.

For **estimated tokens**, start from the cost-estimation table in the visual-identity protocol and scale up by the actual `tool_calls` if it exceeds the estimate range.

