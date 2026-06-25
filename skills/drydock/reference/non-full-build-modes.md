# Non-Full-Build Mode Execution

### Feature Mode

Add a feature to an existing codebase. Lightweight DEFINE → BUILD → TEST.

1. **Codebase scan** — read existing code structure, framework, patterns
2. **PM (Autopilot depth)** — 2-3 questions to scope the feature. Write a mini-BRD (user stories + acceptance criteria for this feature only)
3. **Architect (scoped)** — design how this feature fits the existing architecture. New endpoints, schema changes, component additions. NOT a full system redesign.
4. **Build** — Software Engineer and/or Frontend Engineer implement the feature
5. **Test** — QA writes and runs tests for the new feature
6. **Optional: Review** — Code Reviewer checks the new code against existing patterns

**1 gate:** After PM scoping (step 2), confirm scope before building.

### Harden Mode

Security + quality audit on existing code. No building, pure analysis + fixes.

1. **Codebase scan** — read all existing code
2. **Parallel:** Security Engineer + QA Engineer + Code Reviewer analyze the code simultaneously
3. **Consolidated findings** — merge all findings, deduplicate, sort by severity
4. **Present findings** — severity grid with Critical/High detail
5. **Remediation** — fix Critical and High issues (with user confirmation)

**1 gate:** After findings (step 4), before remediation.

**Visual flow:**
```
━━━ Harden Mode ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Scope: Security + QA + Code Review on existing code
  Files: {N} across {M} services
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ⧖ 3 agents analyzing in parallel...

  ✓ QA Engineer          {N} tests written, {M} passing       ⏱ Xm Ys
  ✓ Security Engineer    {N} findings ({M} Critical/High)     ⏱ Xm Ys
  ✓ Code Reviewer        {N} findings ({M} Critical/High)     ⏱ Xm Ys

━━━ Findings ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Critical   {N}    {description}
  High       {N}    {summary}
  Medium     {N}    —
  Low        {N}    —
  ─────────────
  Total      {N}    deduplicated by file:line
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Pentest (VAPT) Mode

Vulnerability Assessment & Penetration Testing on existing (and optionally running) code. Distinct from Harden (static audit + QA + review): this mode can execute **live DAST/fuzzing** against an authorized target. Single-skill-heavy (Security Engineer) but it ALWAYS presents the authorization gate — never the silent single-skill path.

1. **Recon** — scan the codebase; identify services, endpoints, and any running target.
2. **MANDATORY authorization gate** — before ANY active testing, confirm explicit authorization, in-scope targets, and rules of engagement. Block all active testing until confirmed:

```python
AskUserQuestion(questions=[{
  "question": "Active security testing (DAST/fuzzing/exploitation) sends real payloads to a running target. "
    "I will ONLY test targets you explicitly authorize, on local/authorized-staging hosts, with no DoS or destructive payloads and no production data.\n\n"
    "Do you authorize active testing, and against which exact targets (hosts/URLs/API base)?",
  "header": "VAPT Authorization Gate",
  "options": [
    {"label": "Authorize — local/staging only (Recommended)", "description": "Active testing against the targets I list (localhost / authorized staging). No prod."},
    {"label": "Static/passive only", "description": "Run SAST/SCA/secret/IaC scans only — no payloads to any running system."},
    {"label": "Authorize — I'll specify scope", "description": "Active testing; let me enumerate the exact in-scope hosts/URLs."},
    {"label": "Chat about this", "description": "Discuss scope and rules of engagement first."}
  ],
  "multiSelect": false
}])
```

3. **Persist authorization** — write the choice + target allowlist to `drydock/.orchestrator/settings.md` as `vapt_authorized: true|false` and the in-scope list, and write an authorization receipt to `drydock/.orchestrator/receipts/`.
4. **Dispatch Security Engineer** — run phases 1-6 (static) → **07-vapt-execution** (live DAST/PoC, ONLY if `vapt_authorized: true`; otherwise static/passive only) → **08-vapt-report**. The agent honors `drydock/.protocols/security-testing-protocol.md` and `grounding-protocol.md`.
5. **Present the VAPT report**; offer a retest pass after remediation.

**1 gate:** the authorization gate (step 2). If the user chooses "Static/passive only", this collapses to the Harden static path (phases 1-6, no execution).

### Compliance Mode

Map implemented controls to one or more compliance frameworks on existing code. Runs in/after HARDEN — it CONSUMES the security audit (PII inventory, encryption audit, OWASP/STRIDE findings) produced by security-engineer; it never re-derives them. Single-skill (Compliance Officer) but it ALWAYS presents the scoping gate — never the silent single-skill path.

1. **Codebase + audit scan** — read existing code and, if present, the security-engineer outputs in `drydock/security-engineer/` (PII inventory, encryption audit, findings). If no security audit exists yet, note that controls evidence will be incomplete and offer to run Harden first.
2. **MANDATORY scoping gate** — before mapping any controls, confirm which frameworks are in scope. Block the mapping run until confirmed:

```python
AskUserQuestion(questions=[{
  "question": "Compliance mapping is framework-specific — the required controls differ per framework. "
    "Which framework(s) are in scope for this assessment?",
  "header": "Compliance Scoping Gate",
  "options": [
    {"label": "SOC 2 (Recommended)", "description": "Trust Services Criteria — security, availability, confidentiality."},
    {"label": "HIPAA / GDPR", "description": "Health data (HIPAA) and/or EU personal data (GDPR), incl. DPIA."},
    {"label": "PCI DSS / ISO 27001 / FedRAMP", "description": "Cardholder data, ISMS, or US federal (SSP) — let me confirm exact set."},
    {"label": "Chat about this", "description": "Discuss which frameworks apply and audit readiness scope first."}
  ],
  "multiSelect": true
}])
```

3. **Persist scope** — write the in-scope framework list to `drydock/.orchestrator/settings.md` as `compliance_frameworks: [...]`, and write a scoping receipt to `drydock/.orchestrator/receipts/`.
4. **Dispatch Compliance Officer** (`drydock:compliance-officer`) — it reads the security-engineer audit outputs, maps implemented controls to the in-scope frameworks, and reports each mandatory control as present or missing. It honors `drydock/.protocols/compliance-protocol.md` and `grounding-protocol.md`. **Authority note:** security-engineer remains the sole authority on PII inventory and encryption audit — the compliance-officer consumes those outputs and never overrides them. It writes a receipt to `drydock/.orchestrator/receipts/Tcomp-compliance-officer.json` with controls-present/missing status.
5. **Present the compliance report**; for each missing mandatory control, offer remediation or a logged exception.

**1 gate:** the scoping gate (step 2).

### Ship Mode

Get existing code deployed. Infrastructure + reliability.

1. **Codebase scan** — read existing code, identify services, dependencies
2. **DevOps** — Dockerfiles, CI/CD pipelines, IaC (Terraform/Pulumi), monitoring
3. **SRE** — SLO definitions, runbooks, alerting, chaos experiment plan

**1 gate:** After DevOps infra plan, before applying.

### Test Mode

Write tests for existing code. Single skill.

1. Invoke QA Engineer directly against existing code
2. QA reads code, writes test plan, implements tests, runs them
3. Report results

**0 gates.** QA operates autonomously.

### Review Mode

Code quality review. Single skill, read-only.

1. Invoke Code Reviewer directly
2. Review produces findings report
3. Present findings with severity distribution

**0 gates.** Read-only operation.

### Architect Mode

Design or redesign architecture. Single skill.

1. Invoke Solution Architect
2. Full discovery interview (depth based on autonomy level)
3. Produces ADRs, diagrams, tech stack, API contracts, scaffold

**1 gate:** Architecture approval before scaffold generation.

### Document Mode

Generate documentation for existing code. Single skill.

1. Invoke Technical Writer
2. Reads all code + existing docs
3. Generates API reference, dev guides, architecture overview

**0 gates.** Technical Writer operates autonomously.

### Explore Mode

Thinking partner. Single skill.

1. Invoke Polymath
2. Research, advise, ideate — whatever the user needs
3. When ready, offer to hand off to any other mode

**0 gates.** Polymath manages its own dialogue.

### Optimize Mode

Performance + reliability analysis. Two skills.

1. **Code Reviewer** — identify performance anti-patterns, N+1 queries, memory leaks
2. **SRE** — capacity analysis, scaling bottlenecks, SLO evaluation
3. **Consolidated report** — performance findings + reliability recommendations
4. **Remediation** — fix top issues

**1 gate:** After analysis, before fixes.

### Custom Mode

User picks skills from a menu.

```python
AskUserQuestion(questions=[{
  "question": "Which skills do you need?",
  "header": "Skill Selection",
  "options": [
    {"label": "Product Manager", "description": "Requirements, user stories, BRD"},
    {"label": "Solution Architect", "description": "System design, API contracts, tech stack"},
    {"label": "UX Designer", "description": "UX research, IA, interaction design, design-system spec"},
    {"label": "Software Engineer", "description": "Backend implementation"},
    {"label": "Frontend Engineer", "description": "UI components, pages, design system"},
    {"label": "QA Engineer", "description": "Tests — unit, integration, e2e, performance"},
    {"label": "Security Engineer", "description": "OWASP audit, STRIDE, vulnerability scan"},
    {"label": "Compliance Officer", "description": "Maps controls to SOC 2 / HIPAA / GDPR / PCI / ISO 27001 / FedRAMP; consumes the security audit"},
    {"label": "Code Reviewer", "description": "Architecture conformance, code quality"},
    {"label": "DevOps", "description": "Docker, CI/CD, Terraform, monitoring"},
    {"label": "SRE", "description": "SLOs, chaos engineering, runbooks"},
    {"label": "Technical Writer", "description": "API docs, dev guides, architecture docs"},
    {"label": "Data Scientist", "description": "LLM optimization, ML pipelines, experiments"},
    {"label": "Growth Marketer", "description": "Positioning, launch plan, marketing, funnels"},
    {"label": "Sales Strategist", "description": "Pricing, sales collateral, process, proposals"},
    {"label": "Customer Success", "description": "Onboarding, support ops, retention"},
    {"label": "Chat about this", "description": "Free-form input"}
  ],
  "multiSelect": true
}])
```

Execute selected skills in dependency order. If user picks conflicting skills, resolve via the authority hierarchy.

---

## Design (UX) Mode

**Trigger:** "design the UX", "wireframes", "user flows", "design system", "UX research", "personas", "usability".

Single-skill, 0 gates. Invoke directly:

```python
Skill(skill="ux-designer")
```

The UX Designer runs its phases — discovery/research → information architecture → design-system spec → interaction design → usability/accessibility — and writes the design-system spec to `docs/design/` for frontend-engineer to implement. If a frontend already exists (brownfield), it produces a UX audit + improvement spec instead of greenfield IA. Prints its own `━━━ UX Designer ━━━` header and `[N/5]` phase progress.

---

## Launch (GTM) Mode

**Trigger:** "launch", "go to market", "GTM", "pricing", "packaging", "positioning", "marketing", "sales collateral", "onboarding", "customer success", "support".

Multi-skill (3 agents), 1 gate (GTM plan). **Requires a shipped/described product** — confirm one exists before running.

1. **Scope gate.** Present the GTM plan (target market, primary channels, pricing direction) via `AskUserQuestion` — these are strategic, user-owned choices.
2. **Dispatch the wave** (parallel) to the three LAUNCH subagents per `phases/launch.md`: `growth-marketer` (positioning + launch plan + site copy + funnels), `sales-strategist` (pricing + collateral + process + trust pack), `customer-success` (onboarding + support + retention). sales-strategist consumes growth-marketer's positioning and the security/compliance evidence; customer-success sources the help center from the docs.
3. Verify receipts, merge worktree branches, print the multi-skill completion box. customer-success carries into SUSTAIN.
