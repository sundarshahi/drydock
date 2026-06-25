# Phase 3: Design-System Specification

## Objective

Produce **the handoff artifact frontend-engineer implements**: the design-system SPECIFICATION. This is design tokens (color, type, space, radius, elevation, motion), a numbered type scale, a color system where every text pair meets WCAG 2.1 AA contrast, a component inventory with per-component states and variants, and a brand direction. You write VALUES + INTENT as a spec — you do NOT write token TypeScript, theme code, Tailwind config, or component implementations. frontend-engineer reads this spec and implements `frontend/app/styles/tokens/*` and the component library FROM it; their Phase 2 "functional defaults" are REPLACED by this spec where it exists.

## Context Bridge

Read Phase 1 (brand personality lives in the personas' trust/tone expectations + the competitive teardown) and Phase 2 (the screens, content hierarchy, and the generic components each wireframe named — the component inventory must cover all of them). In brownfield mode, read the existing design system / component library in `frontend/` and EXTEND it — document deltas against the existing tokens/components; never invent a competing set or rename existing components.

## Steps

### 1. Brand direction

Define the product's visual personality grounded in the personas' trust expectations and differentiated from the competitors in the teardown. Capture: tone/voice (3-5 adjectives), the feeling the UI should evoke, density (spacious vs compact), and any constraints from existing brand assets. If you reference a current design trend or a "modern" pattern, WebSearch it this session and cite the source — do not assert trends from memory.

**Deliverable:** `docs/design/design-system/brand.md`.

### 2. Color system (WCAG AA contrast is computed, not eyeballed)

Specify the full color system as NAMED tokens with hex values:

- **Brand/primary** ramp (e.g., 50-950) and any secondary/accent
- **Neutral** ramp (backgrounds, borders, text)
- **Semantic** colors: success, warning, danger/error, info — each with the foreground it pairs with
- **Surface/elevation** colors and **state** colors (hover/active/focus/disabled/selected)
- **Light AND dark theme** values for every semantic role (design dark mode IN — retrofitting is painful)

For EVERY foreground/background pair used to render text or meaningful UI, COMPUTE the contrast ratio from the actual hex pair and record it against the WCAG 2.1 AA thresholds (4.5:1 normal text, 3:1 large text ≥ 18.66px bold / 24px, 3:1 for UI component and graphical-object boundaries). Record a table: pair → computed ratio → AA pass/fail. Any failing pair is adjusted until it passes, or recorded with an explicit remediation note. Confirm the exact thresholds against the WCAG spec this session rather than recalling them loosely; reference each criterion by number (1.4.3 Contrast (Minimum), 1.4.11 Non-text Contrast).

**Deliverable:** `docs/design/design-system/color.md` — token table + the contrast-pair table (every text pair, computed ratio, AA verdict).

### 3. Type scale

Specify typography as a SPEC: font family stack (display + body + mono if needed; if you recommend a specific webfont, WebSearch its current availability/licensing this session), a numbered modular scale (base size + ratio → each step's size + line-height + weight), and the role mapping (h1-h6, body, caption, overline, code) onto those steps. Tie the role mapping back to the content-hierarchy from Phase 2. Specify minimum body size (≥ 16px recommended) and line-length/measure guidance for readability.

**Deliverable:** `docs/design/design-system/type-scale.md`.

### 4. The remaining tokens

Specify the rest of the token set as named tokens with values + intent:

| Token group | Spec content |
|-------------|--------------|
| **Spacing** | A base unit (e.g., 4px) and the scale steps; the intent (which steps are for inset padding vs stack gaps) |
| **Radius** | The radius scale (e.g., sm/md/lg/full) and which components use which |
| **Elevation / shadow** | The elevation levels and what each connotes (raised, overlay, modal) — with dark-theme equivalents |
| **Motion** | Duration tokens (fast/normal/slow) and easing curves, with intent (enter vs exit vs move); the full choreography is Phase 4, but the TOKENS are defined here |
| **Breakpoints** | The named breakpoint set the responsive behavior in Phase 4 will reference |
| **Z-index** | A z-index scale for stacking (dropdown < sticky < modal < toast) |
| **Border / focus ring** | Border widths and the focus-ring token (visible focus is mandatory — see Phase 5) |

**Deliverable:** `docs/design/design-system/tokens.md` (the consolidated token reference frontend-engineer implements).

### 5. Component inventory + per-component specs

Enumerate every component the Phase 2 wireframes referenced, plus the primitives they compose from (Button, Input, Select, Checkbox, Radio, Toggle, Textarea, Badge, Avatar, Tooltip, Modal/Dialog, Toast, Tabs, Table/DataTable, Card, Menu/Dropdown, Pagination, EmptyState, Skeleton, Banner/Alert, Breadcrumb, Nav, Form field). For EACH component, write a spec — NOT code — covering:

- **Anatomy** (the parts) and which tokens it consumes (e.g., "uses `radius.md`, `space.3` inset, `color.primary.600` fill")
- **Variants** (e.g., Button: primary / secondary / ghost / destructive; sizes sm/md/lg)
- **States** — ALL of: default, hover, active/pressed, focus-visible, disabled, loading, error/invalid, selected, read-only (as applicable)
- **Content rules** (min/max, truncation, icon placement) and responsive behavior
- **Accessibility contract** — the role/semantics, the keyboard interaction, the ARIA the implementation must wire (this is the SPEC the frontend-engineer's a11y tests verify against — see Phase 5)

Do NOT paste a component implementation from a library or write React/TS. The spec describes states and behavior; frontend-engineer writes the code.

**Deliverable:** one file per component under `docs/design/design-system/components/<name>.md`, plus an inventory index.

### 6. Handoff index

Write `docs/design/INDEX.md` (or update it) pointing frontend-engineer at the spec entry points: tokens, type scale, color (+ contrast table), the component inventory, and the brand. State explicitly that this is the BUILD-phase handoff and that the frontend-engineer implements these as code (their functional defaults are superseded by this spec).

## Output Deliverables

| Artifact | Path |
|----------|------|
| Brand direction | `docs/design/design-system/brand.md` |
| Color system + contrast table | `docs/design/design-system/color.md` |
| Type scale | `docs/design/design-system/type-scale.md` |
| Token reference | `docs/design/design-system/tokens.md` |
| Per-component specs | `docs/design/design-system/components/<name>.md` + inventory index |
| Handoff index | `docs/design/INDEX.md` |

## Validation Loop

Before moving to Phase 4:
- [ ] Every component named in any Phase 2 wireframe has a spec; every spec enumerates its states (incl. focus-visible, disabled, loading, error)
- [ ] Every text/UI foreground-background pair has a COMPUTED contrast ratio recorded with an AA pass/fail; zero unresolved failing pairs (or each is recorded with a remediation note)
- [ ] Tokens are named with values + intent for color, type, space, radius, elevation, motion, breakpoints, z-index, focus ring — light AND dark
- [ ] The type scale is numbered and mapped to the content hierarchy; body ≥ recommended minimum
- [ ] No token `.ts`, theme code, Tailwind config, or component implementation was authored here (spec only)
- [ ] `docs/design/INDEX.md` points frontend-engineer at every entry point and names the handoff explicitly

## Quality Bar

This is the artifact the whole pipeline depends on after you. A frontend-engineer implements `frontend/app/styles/tokens/*` and the component library from this spec WITHOUT asking "what color / what size / what state". Every contrast pair is computed (a number, not "looks fine") and meets WCAG 2.1 AA. Dark mode is specified, not deferred. The spec describes states and behavior; it never duplicates the eventual component code. Counts (tokens, type-scale steps, components specced, contrast pairs total/passing) are computed and recorded for the receipt.
