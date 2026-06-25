# Phase 2: Information Architecture

## Objective

Structure the product so users can find what they need and complete their jobs. Produce a sitemap, the navigation model, content hierarchy, end-to-end user flows for every key scenario, and a low-fidelity wireframe SPEC per key screen — with the empty, loading, error, and success states enumerated for every data-dependent screen. This phase defines the surfaces the design-system spec (Phase 3) will then dress.

## Context Bridge

Read Phase 1 outputs: personas (whose mental model the IA must match), the prioritized user needs (Must-haves anchor the primary navigation), key scenarios (each becomes a flow), and the competitive teardown (navigation patterns to adopt/avoid). The PRIMARY persona's top JTBD drives what is one click away.

## Steps

### 1. Inventory content & functionality

From the BRD and the user needs, list every screen-worthy object, action, and content type the product must expose. Group them by the JTBD they serve. This inventory is the raw material the sitemap organizes.

**Deliverable:** content/function inventory in `drydock/ux-designer/ia-notes.md`.

### 2. Sitemap

Organize the inventory into a hierarchy. Express the sitemap as a labelled tree (text or Mermaid) with: top-level destinations, their children, and cross-links. Each top-level node names the JTBD/user-need it serves so the structure is accountable, not arbitrary. Keep primary navigation to a defensible number of top-level items (justify the count against the user needs, do not pad).

**Deliverable:** `docs/design/ia/sitemap.md`.

### 3. Navigation model

Specify HOW users move through the sitemap: the primary navigation pattern (top bar / sidebar / tab bar / hub-and-spoke — chosen by product archetype and the primary persona's context, citing the competitive teardown), secondary/utility navigation, breadcrumbs/wayfinding, search if needed, and the responsive collapse strategy (what happens to navigation at small breakpoints — defer the exact breakpoint values to Phase 4 but name the strategy here). Define the active/selected/disabled states navigation must express.

**Deliverable:** `docs/design/ia/navigation.md`.

### 4. Content hierarchy

For the key screens, define the priority of information: what is primary (the one thing the screen is for), secondary, and tertiary. This drives visual hierarchy in Phase 3 (type scale, emphasis) and reading order for accessibility. Define a consistent page-template pattern (header / primary content / supporting / actions) so screens feel like one product.

**Deliverable:** `docs/design/ia/content-hierarchy.md`.

### 5. End-to-end user flows

For EVERY key scenario from Phase 1, produce a flow diagram (text or Mermaid) covering:

- Entry point(s) and the trigger
- Each step / screen the user passes through
- Decision points (branches) with conditions
- **Error and recovery branches** — not just the happy path
- The success outcome and where the user lands next

Annotate each step with the screen it occurs on (linking to its wireframe spec) and any system action (e.g., "calls API X" — referencing the contract, not designing it). Flag any flow that depends on a requirement or API the BRD/architecture does not yet cover as a finding for the product-manager/solution-architect.

**Deliverable:** one file per flow under `docs/design/flows/<flow>.md`.

### 6. Low-fi wireframe specs per key screen

For each key screen, write a low-fidelity layout SPEC (prose + ASCII/Markdown block diagram — NOT pixel-perfect mockups, NOT code). Each spec includes:

- Purpose (the one job this screen does) and the primary persona/JTBD it serves
- Layout regions and their content-hierarchy priority (from Step 4)
- The components it uses (named generically here — Button, DataTable, Form, EmptyState — to be specified in Phase 3)
- Primary action(s) and their placement
- Reading/focus order for keyboard and screen-reader users
- Responsive intent (what reflows / collapses — values finalized in Phase 4)

### 7. Enumerate states for every screen (first-class, not afterthoughts)

For every data-dependent screen, enumerate ALL of:

| State | What it must specify |
|-------|----------------------|
| **Loading** | Skeleton vs spinner, what is shown while data resolves, perceived-performance intent |
| **Empty** | First-run vs no-results-after-filter; the explanatory copy and the primary CTA out of the empty state |
| **Error** | What failed, the recovery action (retry / go back / contact), and that it never dead-ends the user |
| **Partial / degraded** | When some data loaded and some failed |
| **Success / populated** | The normal happy state |

A screen spec without its empty/loading/error states is incomplete and blocks Phase 3.

**Deliverable:** one file per key screen under `docs/design/wireframes/<screen>.md`.

## Output Deliverables

| Artifact | Path |
|----------|------|
| Sitemap | `docs/design/ia/sitemap.md` |
| Navigation model | `docs/design/ia/navigation.md` |
| Content hierarchy | `docs/design/ia/content-hierarchy.md` |
| User flows | `docs/design/flows/<flow>.md` (one per key scenario) |
| Wireframe specs + states | `docs/design/wireframes/<screen>.md` (one per key screen) |
| IA working notes | `drydock/ux-designer/ia-notes.md` |

## Validation Loop

Before moving to Phase 3:
- [ ] Every Must-have user need from Phase 1 is reachable in the sitemap, and the path length matches its priority (top JTBD ≤ 1-2 clicks)
- [ ] Every key scenario has a flow with entry, decision points, error branches, and a success outcome
- [ ] Every key screen has a wireframe spec, and every data-dependent screen enumerates loading/empty/error/partial/success
- [ ] Reading/focus order is specified per screen (accessibility-by-design starts here)
- [ ] Navigation reflects the active/selected/disabled states it must express
- [ ] Any missing requirement/API discovered is filed as a finding (not invented)

## Quality Bar

The IA is complete and traceable: a frontend-engineer could enumerate every route and every screen state from these specs without guessing, and a user testing the primary scenario never hits a dead-end. Every top-level navigation item earns its place against a user need. No screen "happy-paths only" — the empty, loading, and error states are designed, named, and recoverable. Counts (screens specced, flows, states enumerated) are computed and recorded for the receipt.
