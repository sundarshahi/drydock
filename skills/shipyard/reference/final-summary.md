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

Read ALL receipts from `Shipyard/.orchestrator/receipts/`. For each receipt, extract the `effort` field (files_read, files_written, tool_calls). Sum across all agents to produce:
- Total agents used (count of unique receipt files)
- Total tool calls (sum of all effort.tool_calls)
- Total files processed (sum of all effort.files_read + effort.files_written, deduplicated)
- Estimated tokens: use the cost estimation table from visual-identity protocol, adjusted by actual effort metrics. If actual tool_calls significantly exceed the estimate range, scale up proportionally.

Read `Shipyard/.orchestrator/rework-log.md` to get total rework cycles across all gates.

