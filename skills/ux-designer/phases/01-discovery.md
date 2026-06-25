# Phase 1: Discovery

## Objective

Turn the approved BRD into a grounded understanding of WHO the users are, WHAT jobs they are hiring this product to do, and HOW the best products in this space already serve those jobs. Produce personas, jobs-to-be-done (JTBD), prioritized user needs, a competitive UX teardown of the top competitors (researched live, not from memory), and the key end-to-end scenarios the product must serve well. This phase reads, researches, and synthesizes — it does not design screens yet.

## Inputs

| Input | Path | What to Extract |
|-------|------|-----------------|
| BRD (Critical) | `drydock/product-manager/BRD/` | Problem statement, target users/segments, user stories, acceptance criteria, scope, out-of-scope, compliance scope |
| Project config | `.drydock.yaml` | Brand hints, deliverable paths, target markets |
| Brownfield context | `drydock/.orchestrator/codebase-context.md` | Existing product, existing users, prior research to honor |
| Existing research (Optional) | `drydock/ux-designer/`, prior `docs/design/research/` | Anything already known about users — do not duplicate |

If the BRD is missing or unapproved, STOP and request it — personas and JTBD are derived FROM requirements; you do not invent the product's users.

## Steps

### 1. Extract the user model from the BRD

Read every user story and the problem statement. For each distinct role/segment named or implied, capture: who they are, their context of use, their goal, and their current pain. Record the `path` or story id each fact came from. Do NOT add users the BRD does not support — flag any user you believe is missing as a finding for the product-manager.

**Deliverable:** a raw user-model table in `drydock/ux-designer/discovery-notes.md` (every row cites a BRD source).

### 2. Synthesize personas

Produce 2-5 personas (primary, secondary, and any admin/operator), each with:

- Name + one-line summary and the segment it represents
- Goals (what success looks like for them)
- Pain points / frustrations with the status quo (traced to BRD problem statement)
- Context: device, environment, frequency of use, accessibility considerations (e.g., low-vision, motor, situational — keyboard-only, one-handed, bright sunlight)
- Tech proficiency and trust expectations

Mark each persona **primary** (designed-for) or **secondary** (accommodated). The primary persona drives IA and flow prioritization in Phase 2.

**Deliverable:** `docs/design/research/personas.md`.

### 3. Frame jobs-to-be-done

For each primary/secondary persona, write JTBD statements in the form: *When [situation], I want to [motivation], so I can [expected outcome].* Tie each JTBD to the BRD user stories it serves. Rank JTBD by frequency × importance so Phase 2 can prioritize the IA around the top jobs.

**Deliverable:** `docs/design/research/jobs-to-be-done.md`.

### 4. Prioritize user needs

Convert JTBD + pain points into a prioritized list of user NEEDS (functional, emotional, and accessibility needs). Use a simple Must/Should/Could ranking. Each need names the JTBD/persona it serves and the BRD story it maps to. This is the bridge the IA, flows, and design-system spec are accountable to.

**Deliverable:** `docs/design/research/user-needs.md`.

### 5. Competitive UX teardown (LIVE research — no memory)

Identify the top 3-5 competitors / analogous products. Per `freshness-protocol.md` + `grounding-protocol.md`, **WebSearch each competitor this session** and WebFetch their product/marketing/help pages — never describe their current UX from memory. For each, record:

- Source URL(s) you actually retrieved + the date observed
- Their navigation model and primary IA
- How they handle the top JTBD (onboarding, the core task, the empty/first-run state)
- Notable interaction/motion patterns, and accessibility signals you can observe
- What they do WELL (adopt) and where they FAIL (the opportunity / differentiation)

If a competitor cannot be researched live, record `<!-- TODO: source not found — could not retrieve <name> this session -->` rather than inventing its UX.

**Deliverable:** `docs/design/research/competitive-teardown.md` — a per-competitor table plus a synthesized "patterns to adopt / gaps to exploit" section.

### 6. Key scenarios

Write the 3-7 end-to-end scenarios that matter most — the narratives a real user moves through (e.g., "first-time setup", "the core daily task", "recovering from an error", "the upgrade/conversion moment"). Each scenario names the persona, the trigger, the steps at a narrative level, and the success outcome. These seed the user flows in Phase 2.

**Deliverable:** `docs/design/research/scenarios.md`.

## Output Deliverables

| Artifact | Path |
|----------|------|
| Personas | `docs/design/research/personas.md` |
| Jobs-to-be-done | `docs/design/research/jobs-to-be-done.md` |
| Prioritized user needs | `docs/design/research/user-needs.md` |
| Competitive UX teardown | `docs/design/research/competitive-teardown.md` |
| Key scenarios | `docs/design/research/scenarios.md` |
| Discovery working notes | `drydock/ux-designer/discovery-notes.md` |

## Validation Loop

Before moving to Phase 2:
- [ ] Every persona and JTBD traces to a BRD story or a cited research source — zero invented users
- [ ] User needs are prioritized (Must/Should/Could) and each maps to a JTBD + BRD story
- [ ] Every competitor in the teardown has a real source URL retrieved this session (or an explicit TODO)
- [ ] Key scenarios cover the top-ranked JTBD, including at least one recovery/error scenario
- [ ] Any requirement gap found is filed as a finding for the product-manager (not silently fixed)

## Quality Bar

Discovery is grounded, not imagined. "Users want it to be easy" is not a finding — "Primary persona *Maya* (BRD story US-3) abandons setup because step 4 asks for data she does not have yet; competitor X (retrieved `https://… 2026-06-25`) defers it to a later optional step" is. Every persona, JTBD, and competitor claim carries a source, and the counts (personas, JTBD, competitors reviewed, scenarios) are computed and recorded for the receipt.
