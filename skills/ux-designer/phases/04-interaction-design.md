# Phase 4: Interaction Design

## Objective

Make the product feel responsive, legible, and alive without getting in the user's way. Produce detailed interaction and motion specs for the top flows, the micro-interactions that give feedback, the responsive behavior at every declared breakpoint, the form/UX patterns, and a `prefers-reduced-motion` policy for every animation. These are SPECS the frontend-engineer implements — you describe timing, easing, choreography, and behavior; you do not write animation or component code.

## Context Bridge

Read Phase 2 (the flows + screens being choreographed) and Phase 3 (the motion/duration/easing tokens, breakpoints, and component states you must reference by name). Interaction design uses the design-system vocabulary — never invent a new duration when a motion token exists; reference `motion.fast` / `motion.normal` and the easing tokens from `tokens.md`.

## Steps

### 1. Choreograph the top flows

For the top 3-5 flows from Phase 2 (the highest-priority JTBD), specify the interaction choreography step by step:

- The transition between each screen/step (enter/exit, direction, what persists vs replaces)
- Feedback on every user action (optimistic UI? immediate vs deferred? progress indication for >1s waits)
- How the loading/empty/error states from Phase 2 ANIMATE in and out (skeleton → content cross-fade, error shake/slide, etc.)
- Focus management across the transition (where focus lands after navigation, on dialog open/close, after submit) — this is an accessibility requirement, not a nicety

**Deliverable:** one file per flow under `docs/design/interaction/<flow>.md`.

### 2. Micro-interactions

Specify the small feedback moments that make the UI feel direct: button press feedback, hover affordances, toggle/checkbox transitions, input focus, validation feedback (inline, on blur vs on submit), drag handles, copy-to-clipboard confirmation, toast enter/exit, menu open/close, accordion expand/collapse, tooltip delay. For each, specify the trigger, the duration token, the easing token, and the property animated. Keep micro-interactions short (typically `motion.fast`) so they feel instant, not laggy.

**Deliverable:** `docs/design/interaction/micro-interactions.md`.

### 3. Motion system + prefers-reduced-motion (mandatory per animation)

Consolidate the motion language: which easing for enter vs exit vs move, the duration ladder (and the rule that larger surfaces move slightly slower), the rule that motion is ENHANCEMENT — never the only signal of a state change or the only way to comprehend content. Then specify the **`prefers-reduced-motion: reduce` fallback for EVERY animation**: what it becomes when reduced (typically an instant state change or a simple opacity fade — no large translate/scale, no parallax, no autoplay). An animation without a reduced-motion fallback is an incomplete spec.

**Deliverable:** `docs/design/interaction/motion.md` — the motion system + a table mapping each animation → its reduced-motion fallback.

### 4. Responsive behavior at breakpoints

Using the named breakpoints from Phase 3 (`tokens.md`), specify how each key screen and the navigation reflow at each breakpoint:

| Breakpoint | What changes |
|------------|--------------|
| Mobile (e.g., < 640px) | Navigation collapse strategy, single-column reflow, touch target sizing, sticky action bar |
| Tablet (e.g., 640-1024px) | Intermediate layout, multi-column thresholds |
| Desktop (e.g., ≥ 1024px) | Full layout, max content measure, hover affordances |

Specify minimum touch target size (≥ 24x24 CSS px per WCAG 2.1 AA 2.5.8 Target Size (Minimum) — confirm the exact value against the spec this session), what content is hidden vs reflowed vs prioritized at small sizes (no horizontal scrolling of primary content), and that the design reflows to a single column at 320px width without loss of function (WCAG 1.4.10 Reflow).

**Deliverable:** `docs/design/interaction/responsive.md`.

### 5. Form & input UX patterns

Specify the product-wide form patterns the frontend-engineer implements consistently:

- Label placement, required/optional marking, help text, and placeholder usage (placeholders are not labels)
- Validation timing (inline on blur for correction, full validation on submit) and where errors appear (per-field + a focusable error summary that moves focus to the first error)
- Error message tone and that messages say HOW to fix, not just "invalid"
- Multi-step / wizard patterns: progress indication, back without data loss, save-and-resume
- Destructive-action confirmation, unsaved-changes guard, and success confirmation
- Input affordances: autocomplete/autofill hints, input modes for mobile keyboards, disabled-while-submitting

**Deliverable:** `docs/design/interaction/form-patterns.md`.

## Output Deliverables

| Artifact | Path |
|----------|------|
| Per-flow interaction specs | `docs/design/interaction/<flow>.md` |
| Micro-interactions | `docs/design/interaction/micro-interactions.md` |
| Motion system + reduced-motion table | `docs/design/interaction/motion.md` |
| Responsive behavior | `docs/design/interaction/responsive.md` |
| Form/UX patterns | `docs/design/interaction/form-patterns.md` |

## Validation Loop

Before moving to Phase 5:
- [ ] Every top flow has a choreography spec including focus management across transitions
- [ ] Every animation/micro-interaction references motion tokens (not magic numbers) and has a `prefers-reduced-motion: reduce` fallback
- [ ] Responsive behavior is specified at every named breakpoint; reflows to single column at 320px with no loss of function; touch targets meet the minimum
- [ ] Form patterns cover validation timing, the focusable error summary, multi-step, and unsaved-changes
- [ ] Motion is never the sole signal of a state change (every motion has a non-motion equivalent)
- [ ] No animation/component code authored (spec only)

## Quality Bar

Interaction design is concrete enough to implement and inclusive by default. Every animation has a timing token, an easing token, and a reduced-motion fallback — none is left to the frontend-engineer's improvisation, and none excludes a motion-sensitive user. The responsive spec answers "what happens at 320px / 768px / 1280px" for every key screen. Forms tell users how to fix errors and never lose their work. Counts (flows choreographed, micro-interactions, breakpoints covered) are computed and recorded for the receipt.
