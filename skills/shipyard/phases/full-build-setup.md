# Full Build Pipeline — Setup

When mode is **Full Build**, follow this EXACT sequence:

1. **Print pipeline dashboard** (initial state — all pending):
```
╔══════════════════════════════════════════════════════════════╗
║  ◆ SHIPYARD v{local_version}                        ║
║  Project: [extracted from user's message]                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   DEFINE    ○ pending                                        ║
║   BUILD     ○ pending                                        ║
║   HARDEN    ○ pending                                        ║
║   SHIP      ○ pending                                        ║
║   SUSTAIN   ○ pending                                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

⧖ Bootstrapping workspace...
```

**Reprint this dashboard** at every phase transition and before every gate, updating phase statuses (`○ pending` → `● active` → `✓ complete ⏱ Xm Ys`). Track elapsed time per phase and total. This recurring dashboard IS the progress animation — the user sees the same template fill in over time.

2. **Bootstrap workspace + deploy protocols** — run the bundled script (one deterministic command instead of hand-running `mkdir` + copying each protocol):
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/shipyard/scripts/bootstrap-workspace.sh" 2>/dev/null \
  || bash "${CLAUDE_SKILL_DIR}/scripts/bootstrap-workspace.sh"
```
It creates `Shipyard/.protocols/`, `Shipyard/.orchestrator/receipts/`, and `Shipyard/.orchestrator/overrides/`, and copies every shared protocol from the plugin's `skills/_shared/protocols/` into `Shipyard/.protocols/`. If it prints a `WARN` that it could not locate the protocols, fall back to writing each from the summaries in step 3.

3. **Shared protocols** (deployed by the script in step 2 — this table is the reference / fallback if the script could not locate the source):

| Protocol File | Content |
|---------------|---------|
| `ux-protocol.md` | 6 UX rules: never open-ended questions, "Chat about this" last, recommended first, continuous execution, real-time progress, autonomy |
| `input-validation.md` | 5-step validation: read config → probe inputs in parallel → classify Critical/Degraded/Optional → print gap summary → adapt scope |
| `tool-efficiency.md` | Parallel tool calls, use Grep to locate structure + Read with offset/limit (and Glob to find files) instead of reading whole files blindly, Glob not find, Grep not grep, config-aware paths |
| `conflict-resolution.md` | Authority hierarchy, dedup by file:line (keep highest severity), HARDEN→BUILD feedback loops (2 cycle max) |
| `visual-identity.md` | Visual design language: container hierarchy (Tier 1/2/3), icon vocabulary, progress patterns, gate ceremonies, wave announcements, completion summaries, timing |
| `freshness-protocol.md` | Temporal sensitivity: volatility tiers (Critical/High/Medium/Stable), WebSearch triggers for outdated data (model IDs, versions, pricing, CVEs), search-then-implement pattern |
| `receipt-protocol.md` | Verifiable gate enforcement: receipt schema (JSON), write-after-verify pattern, remediation chain (finding → fix → verification), orchestrator verification at phase transitions |
| `boundary-safety.md` | 6 structural patterns for system boundary safety: framework abstraction limits, control flow delegation, self-referencing config detection, conditional global interceptors, cross-boundary journey testing, identity consistency across integrations |
| `grounding-protocol.md` | Evidence-first / anti-hallucination: cite-or-abstain, no invented file:line/APIs/CVEs/CVSS, `[verified]`/`[inferred]`/`[unverified]` confidence tags, chain-of-verification before asserting. Loads into ALL agents. |
| `security-testing-protocol.md` | VAPT rules of engagement: authorization + scope gate before any active test, local/authorized targets only, no DoS/destructive payloads/prod data, responsible disclosure, evidence-backed findings, CVSS discipline. Loads into security-engineer. |
| `security-defaults.md` | Secure-by-default baseline: secret handling, RFC 9457 problem+json error format, input validation, authn/authz defaults, dependency hygiene. Loads into all build/harden agents. |
| `observability-contract.md` | Observability requirements: structured logging, metrics, tracing, and the gate/receipt metric fields downstream skills emit (tests/coverage/mutation/perf/compliance). Loads into all agents. |
| `architecture-boundaries.md` | Architecture boundary rules: module/service boundaries, dependency direction, layering, and the architecture-boundary gate enforced at Gate 3. Loads into architect/build/review agents. |
| `compliance-protocol.md` | Compliance control mapping: framework scoping (SOC 2/HIPAA/GDPR/PCI/CCPA/ISO 27001/FedRAMP), mandatory controls-present/missing reporting, consumes security-engineer PII/encryption outputs. Loads into compliance-officer. |

If the bootstrap script could not locate the plugin's `skills/_shared/protocols/` (it prints a `WARN`), write each protocol to `Shipyard/.protocols/` from the summaries above.

4. **Codebase discovery — detect greenfield vs brownfield:**

   Run these scans in parallel:
   ```python
   Glob("package.json"), Glob("go.mod"), Glob("pyproject.toml"), Glob("Cargo.toml"), Glob("pom.xml")
   Glob("src/**"), Glob("services/**"), Glob("frontend/**"), Glob("tests/**"), Glob("docs/**")
   Glob("Dockerfile*"), Glob(".github/workflows/*"), Glob("infrastructure/**"), Glob("terraform/**")
   Glob(".shipyard.yaml")
   ```

   **Classify the project:**

   | Signal | Mode | Behavior |
   |--------|------|----------|
   | Empty/new directory, no source files | **Greenfield** | Create everything from scratch |
   | Source files exist, no `.shipyard.yaml` | **Brownfield (unmapped)** | Discover structure, generate config, adapt |
   | Source files + `.shipyard.yaml` exist | **Brownfield (mapped)** | Use config paths, augment existing code |

   **If Greenfield** → log `✓ Greenfield project — creating from scratch` and continue to step 5.

   **If Brownfield** → run the adaptation sequence:

   a. **Structure report** — scan and summarize what exists:
   ```
   ⧖ Existing codebase detected. Scanning structure...
   Language: [detected from package.json/go.mod/etc.]
   Framework: [detected from dependencies]
   Directories found: src/, tests/, docs/, .github/workflows/
   Files: [N] source files, [N] test files, [N] config files
   ```

   b. **Path mapping** — if no `.shipyard.yaml`, generate one from discovered structure:
   ```python
   AskUserQuestion(questions=[{
     "question": "I've detected an existing codebase. Here's what I found:\n\n"
       "[structure summary]\n\n"
       "I'll map the pipeline outputs to your existing structure.",
     "header": "Existing Codebase Detected",
     "options": [
       {"label": "Approve mapping (Recommended)", "description": "Use detected paths, generate .shipyard.yaml"},
       {"label": "Customize paths", "description": "Review and adjust the path mapping"},
       {"label": "Treat as greenfield", "description": "Ignore existing code, create fresh structure"},
       {"label": "Chat about this", "description": "Discuss how the pipeline adapts to your codebase"}
     ],
     "multiSelect": false
   }])
   ```

   c. **Write `.shipyard.yaml`** from discovered structure — map `paths.*` to actual directories found.

   d. **Set brownfield context** — write to `Shipyard/.orchestrator/codebase-context.md`:
   ```markdown
   # Codebase Context
   Mode: brownfield
   Language: [detected]
   Framework: [detected]
   Existing paths: [mapping]

   ## Rules for all agents
   - NEVER overwrite existing files without explicit user approval
   - READ existing code patterns before writing new code
   - MATCH existing code style (naming, formatting, structure)
   - ADD to existing directories, don't replace them
   - If a file exists at the target path, create alongside it or extend it
   - Existing tests must still pass after changes
   ```

   All agents read this file before executing. It overrides default "create from scratch" behavior.

5. **Engagement mode:**

```python
AskUserQuestion(questions=[{
  "question": "How deeply should the pipeline involve you in decisions?",
  "header": "Engagement Mode",
  "options": [
    {"label": "Standard (Recommended)", "description": "3 gates + moderate architect interview. Best balance of speed and control."},
    {"label": "Express", "description": "Minimal interaction. 3 gates only, auto-derive architecture from BRD. Fastest."},
    {"label": "Thorough", "description": "Deep interviews at PM and Architect. Full capacity planning. Review phase summaries."},
    {"label": "Meticulous", "description": "Maximum depth. Approve each ADR individually. Review every agent output. Full control."}
  ],
  "multiSelect": false
}])
```

Write the choice to `Shipyard/.orchestrator/settings.md`:
```markdown
# Pipeline Settings
Engagement: [express|standard|thorough|meticulous]
Parallelism: [maximum|standard|sequential]
```

All skills read this file at startup to adapt their depth. The engagement mode controls:
- **PM interview depth** — Express: 2-3 questions. Standard: 3-5. Thorough: 5-8. Meticulous: 8-12.
- **Architect discovery depth** — Express: auto-derive. Standard: 5-7 questions. Thorough: 12-15 with capacity planning. Meticulous: full walkthrough + individual ADR approval.
- **Phase summaries** — Thorough/Meticulous show intermediate outputs between phases.
- **Gate detail** — Meticulous adds per-agent output review at each gate.

6. **Parallelism preference:**

```python
AskUserQuestion(questions=[{
  "question": "How should the pipeline parallelize work?",
  "header": "Performance Mode",
  "options": [
    {"label": "Maximum parallelism + worktree isolation (Recommended)", "description": "Fastest + safest. Each agent gets its own git worktree — zero file conflicts."},
    {"label": "Maximum parallelism — shared directory", "description": "Fast but agents share the working directory. Use if worktrees cause issues."},
    {"label": "Standard", "description": "2-3 concurrent agents. Slower but lighter on system resources."},
    {"label": "Sequential", "description": "One agent at a time. Use for debugging or when inspecting each step."}
  ],
  "multiSelect": false
}])
```

Store all choices in `Shipyard/.orchestrator/settings.md`:
```markdown
# Pipeline Settings
Engagement: [express|standard|thorough|meticulous]
Parallelism: [maximum|standard|sequential]
Worktrees: [enabled|disabled]
```

Maximum parallelism with worktree isolation is the recommended default — parallel execution is both faster AND cheaper in total tokens because each agent carries minimal context instead of accumulating prior work. Worktree isolation eliminates file race conditions between concurrent agents.

**Worktree requirements:** Git repo must have a clean state (no uncommitted changes). If dirty, the BUILD phase dispatcher will prompt the user to auto-commit or skip worktrees. See `phases/build.md` for the pre-flight check.

**Show pre-pipeline cost estimate** after both selections:
```
  Est. cost: ~{low}K-{high}K tokens (~${low_cost}-${high_cost} at Sonnet pricing)
  Agents: up to {N} concurrent · {M} total tasks
  Worktrees: {enabled|disabled}
```

Use the cost estimation table from the visual-identity protocol to look up the range based on mode + engagement.

7. **Detect existing workspace** — if `Shipyard/.orchestrator/` has prior state, offer to resume or restart via AskUserQuestion.

8. **Polymath pre-flight check:**
   - If `Shipyard/polymath/handoff/context-package.md` exists → read it, pass to PM as pre-loaded context. Log: `✓ Polymath context loaded — skipping redundant discovery`
   - If no polymath context, assess the user's request for knowledge gaps:
     - **Vague scope** (no specific problem domain), **no constraints** (scale, budget, team), **complex domain with no domain language**, **contradictory signals**
     - If gaps detected → invoke `Skill("polymath")` for pre-flight consultation before proceeding. The polymath will research, clarify with the user, and write a context package when ready.
     - If no gaps → proceed directly. Log: `✓ Request is clear — proceeding to PM`
   - If user explicitly requests to skip polymath ("just build it", clear detailed spec) → proceed immediately.

9. **Research the domain** — use WebSearch before asking the user anything (skip if polymath already researched).

10. **Create the task graph:**
Create all tasks (T1–T13 plus the HARDEN-phase compliance task T6e) with dependencies (see Task Dependency Graph). Use TaskCreate for each, then TaskUpdate to set `addBlockedBy` relationships using the returned task IDs. The task graph is the orchestrator's single source of tracking — no team object is created; autonomous work is delegated to the named subagents (`agents/<name>.md`), each of which runs backgrounded in its own worktree per its own definition.

11. **Begin Phase 1** — read `phases/define.md` and start immediately. Do NOT ask "should I proceed?"

**Key principle:** The user already told you what to build. Research, plan, start building. Pause at the 3 approval gates. In Thorough/Meticulous mode, also show phase summaries between major phases — but never block on them (inform, don't gate).
