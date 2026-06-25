# Phase 1 — Infrastructure Assessment

**Engagement mode determines assessment depth:**
- **Express**: Infer all answers from codebase analysis, architecture docs, and .shipyard.yaml. Report assumptions in output. Do NOT ask.
- **Standard**: Ask only for unknowns not discoverable from code (budget/compliance, 1 call max).
- **Thorough/Meticulous**: Use AskUserQuestion to gather (batch into 2-3 calls max):
  1. **Current state** — Existing infra? Greenfield? Migration? What's already running?
  2. **Application profile** — Language/framework, stateful/stateless, background jobs, WebSockets?
  3. **Scale requirements** — Traffic patterns (steady/bursty), auto-scaling needs, regions
  4. **Environments** — How many? (dev/staging/prod minimum), environment parity strategy
  5. **Budget & compliance** — Cost constraints, regulatory requirements (SOC2/HIPAA/PCI)
  6. **Team capabilities** — DevOps maturity, on-call rotation, incident response existing?
