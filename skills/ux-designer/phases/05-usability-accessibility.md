# Phase 5: Usability & Accessibility

## Objective

Audit the whole design for usability and bake accessibility in to WCAG 2.1 AA. Produce a heuristic evaluation of the flows and screens, an accessibility-by-design conformance plan (keyboard, focus, contrast, semantics, target size — as a spec the frontend-engineer and qa-engineer verify against), and a usability test plan with measurable success metrics (task success rate, time-on-task, SUS). This phase is the gate on the design quality before it hands off to BUILD.

## Context Bridge

Read everything: Phase 1 personas (including accessibility personas), Phase 2 flows + screen states + reading/focus order, Phase 3 color contrast table + component accessibility contracts, Phase 4 motion + responsive + form patterns. You are auditing the artifacts you produced — accessibility decisions made earlier (focus order, contrast, semantics) are CONFIRMED here, not invented at the end.

## Steps

### 1. Heuristic evaluation

Evaluate the flows and key screens against the established usability heuristics (Nielsen's 10 — visibility of system status, match to the real world, user control & freedom, consistency & standards, error prevention, recognition over recall, flexibility, aesthetic & minimalist design, error recovery, help & documentation). For each heuristic, walk the top flows and record violations:

| # | Heuristic | Screen/Flow | Issue | Severity (0-4) | Recommendation |
|---|-----------|-------------|-------|----------------|----------------|

Use a 0-4 severity scale (0 = not a problem, 4 = usability catastrophe). Sort by severity. Each High/catastrophe issue gets a concrete recommendation that points back to the screen/flow/component spec to change.

**Deliverable:** `docs/design/usability/heuristic-eval.md`.

### 2. Accessibility-by-design to WCAG 2.1 AA

Produce the AA conformance plan as a SPEC the implementation is held to. Confirm each criterion's exact requirement against the WCAG 2.1 spec this session (do not recall thresholds loosely); reference each by criterion number. Cover at minimum:

| Area | WCAG 2.1 AA criteria (confirm live) | What the spec requires |
|------|-------------------------------------|------------------------|
| **Keyboard** | 2.1.1 Keyboard, 2.1.2 No Keyboard Trap | Every interactive element operable by keyboard; logical tab order matches reading order (from Phase 2); no traps; documented shortcuts |
| **Focus** | 2.4.7 Focus Visible, 2.4.3 Focus Order, 2.4.11 Focus Not Obscured | Visible focus ring (the focus token from Phase 3) on every focusable element; focus moves sensibly on dialog open/close and after submit (from Phase 4) |
| **Contrast** | 1.4.3 Contrast (Minimum), 1.4.11 Non-text Contrast | The Phase 3 contrast table — every text pair ≥ 4.5:1 (3:1 large), UI/graphics ≥ 3:1 |
| **Semantics** | 1.3.1 Info and Relationships, 4.1.2 Name/Role/Value | Correct roles/landmarks/headings; the per-component accessibility contracts from Phase 3 (name, role, ARIA, keyboard) |
| **Target size** | 2.5.8 Target Size (Minimum) | Touch/click targets meet the minimum (from Phase 4) |
| **Reflow / resize** | 1.4.10 Reflow, 1.4.4 Resize Text | Single column at 320px without loss; text scales to 200% without clipping |
| **Color independence** | 1.4.1 Use of Color | Color is never the only signal (errors/required/status pair color with text/icon) |
| **Motion** | 2.3.3 Animation from Interactions | The `prefers-reduced-motion` fallbacks from Phase 4 |
| **Forms / errors** | 3.3.1 Error Identification, 3.3.2 Labels or Instructions, 3.3.3 Error Suggestion | Per-field labels, identified errors, fix suggestions (from Phase 4) |
| **Media** | 1.1.1 Non-text Content, 1.2.x | Alt text rules; captions/transcripts if media is in scope |

Record per-criterion: how the design satisfies it (pointing to the spec) or a `<!-- TODO -->` gap to resolve before BUILD. This is the checklist the frontend-engineer's axe-core/jsx-a11y CI and qa-engineer verify the IMPLEMENTATION against — you own the by-design spec; they verify the running code.

**Deliverable:** `docs/design/usability/accessibility-aa.md`.

### 3. Usability test plan + success metrics

Write a test plan that makes "is this usable?" measurable, not a vibe:

- **Tasks** — derived from the top scenarios/flows (Phase 1/2); each task has a clear start and a defined success state
- **Participants** — number, recruited against the primary/secondary personas (including at least one assistive-technology user where feasible)
- **Method** — moderated/unmoderated, think-aloud, remote/in-person
- **Success metrics with targets:**
  - **Task success rate** (target, e.g., ≥ 80% complete unaided)
  - **Time-on-task** (baseline expectation per task)
  - **Error rate** / number of misclicks / assists needed
  - **SUS** (System Usability Scale) — the 10-item questionnaire, target score (e.g., ≥ 68 is "above average"; confirm the benchmark this session if you cite it)
  - Optional: SEQ (Single Ease Question) per task
- **Severity rubric** for issues found, and the loop: issues feed back into the relevant phase's spec before BUILD proceeds

**Deliverable:** `docs/design/usability/usability-test-plan.md`.

### 4. Update the handoff index

Update `docs/design/INDEX.md` to list the usability + accessibility deliverables and to state that the accessibility-AA checklist is the conformance target the frontend-engineer and qa-engineer verify the build against.

## Output Deliverables

| Artifact | Path |
|----------|------|
| Heuristic evaluation | `docs/design/usability/heuristic-eval.md` |
| Accessibility-by-design (WCAG 2.1 AA) | `docs/design/usability/accessibility-aa.md` |
| Usability test plan + metrics | `docs/design/usability/usability-test-plan.md` |
| Updated handoff index | `docs/design/INDEX.md` |

## Validation Loop

Before completing:
- [ ] Heuristic eval covers the top flows; every High/catastrophe issue has a concrete, traceable recommendation
- [ ] Every WCAG 2.1 AA criterion in the table is addressed by the design or flagged as a gap to fix before BUILD; thresholds confirmed live (referenced by criterion number)
- [ ] The contrast table from Phase 3 is reconciled here — zero unresolved AA failures
- [ ] The usability test plan has tasks tied to scenarios and measurable targets (task success, time-on-task, SUS)
- [ ] `docs/design/INDEX.md` names the accessibility-AA checklist as the build-verification target
- [ ] The completion receipt is written LAST (see SKILL Receipt Instruction) with computed counts; every artifact path exists on disk

## Quality Bar

Usability is measured, accessibility is designed-in, and both are verifiable. "It's intuitive" is not a finding — "Task 2 (checkout) success target ≥ 85%; heuristic issue H-04 (severity 3): the error toast auto-dismisses before a screen-reader user can read it — fix in `interaction/micro-interactions.md`" is. Every WCAG 2.1 AA criterion is either satisfied (pointing to the spec) or an explicit gap — never silently assumed. The accessibility checklist is concrete enough that the frontend-engineer's a11y CI and qa-engineer can verify the running code against it line by line. Counts (heuristic issues, AA criteria addressed) are computed and recorded for the receipt.
