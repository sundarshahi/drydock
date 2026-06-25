# Conflict Resolution Protocol

**When two skills produce overlapping or contradictory outputs, this protocol determines which output takes authority.**

## Authority Hierarchy

Each artifact type has a single authoritative skill. Contributors may flag issues but do NOT override the authority.

| Artifact | Authority (Sole Owner) | Contributors (Read-Only Input) |
|----------|----------------------|-------------------------------|
| Business requirements (BRD) | **product-manager** | — |
| Architecture decisions (ADRs) | **solution-architect** | code-reviewer flags drift |
| API contracts (OpenAPI, gRPC, AsyncAPI) | **solution-architect** | software-engineer requests changes via findings |
| Implementation code (services/, libs/) | **software-engineer** | reviewers produce findings only, do NOT modify code |
| Frontend code (frontend/) | **frontend-engineer** | reviewers produce findings only, do NOT modify code |
| Test suites (tests/) | **qa-engineer** | — |
| Security findings (OWASP, STRIDE, pen-test) | **security-engineer** | code-reviewer does NOT perform OWASP review |
| PII inventory, encryption audit | **security-engineer** | compliance-officer consumes these as evidence, does NOT re-derive them |
| Regulatory framework scoping, control-evidence map | **compliance-officer** | security-engineer/sre/devops supply control evidence as findings |
| Feature-flag infrastructure (shared flag layer) | **software-engineer** | data-scientist extends for experiments, does NOT fork the layer |
| ML experiment design (flag-gated experiments) | **data-scientist** | extends the shared flag layer, does NOT fork it |
| Code quality / arch conformance findings | **code-reviewer** | — |
| SLO definitions, error budgets, runbooks | **sre** | devops provides infra metrics, does NOT define SLOs |
| Monitoring infrastructure (dashboards, alerts) | **devops** | sre defines thresholds, devops implements them |
| Infrastructure (Terraform, K8s, CI/CD) | **devops** | sre reviews for reliability concerns |
| Documentation (docs/) | **technical-writer** | — |
| UX research, information architecture, interaction design, **design-system SPEC** | **ux-designer** | frontend-engineer IMPLEMENTS the spec as code, does NOT redefine it |
| Positioning, messaging, GTM/launch plan, marketing-site copy, funnels | **growth-marketer** | sales-strategist consumes positioning; does NOT author pricing or sales process |
| Pricing & packaging, sales collateral, sales process, proposals | **sales-strategist** | consumes growth-marketer positioning + security/compliance evidence; does NOT author positioning |
| Onboarding, support ops, retention, voice-of-customer | **customer-success** | feeds prioritized feedback to product-manager; sources help-center from technical-writer docs |
| Custom project skills | **skill-maker** | — |

## Deduplication Rules

When multiple skills analyze the same code and produce overlapping findings:

1. **Keep highest severity**: If security-engineer rates a finding as Critical and code-reviewer rates the same file:line as High, keep Critical.
2. **Deduplicate by location**: Findings targeting the same `file:line` are merged. The authoritative skill's finding wins.
3. **Cross-reference, don't duplicate**: code-reviewer should write "See security-engineer findings for OWASP analysis" instead of performing its own OWASP review.

## Feedback Loops (HARDEN → BUILD)

When HARDEN phase skills find issues that require code changes:

1. **Findings become tasks**: The orchestrator reads all HARDEN findings and creates remediation TaskCreate entries.
2. **Remediation assigned to build agents**: Critical/High findings are assigned to the original build agent (software-engineer or frontend-engineer).
3. **Re-scan after remediation**: After fixes are applied, the HARDEN skill re-scans the affected files.
4. **Termination after 2 cycles**: If issues persist after 2 fix-rescan cycles, escalate to user via AskUserQuestion.

## Specific Boundary Clarifications

### security-engineer vs code-reviewer
- **security-engineer**: Sole authority on OWASP Top 10, STRIDE, penetration testing, compliance, PII, encryption.
- **code-reviewer**: Architecture conformance, code quality (SOLID, DRY), performance, test quality. Does NOT do security review — references security-engineer findings instead.

### sre vs devops
- **devops**: Owns infrastructure provisioning, CI/CD pipelines, container orchestration, monitoring tool setup.
- **sre**: Owns SLO/SLI definitions, error budget policy, chaos engineering, incident management, runbooks, capacity planning. Does NOT provision infrastructure — reviews it for reliability.

### product-manager vs solution-architect
- **product-manager**: Owns WHAT to build (requirements, user stories, acceptance criteria).
- **solution-architect**: Owns HOW to build it (architecture, tech stack, API contracts, data models). Does NOT change requirements — flags gaps back to PM.

### compliance-officer vs security-engineer
- **compliance-officer**: Sole authority on which regulatory frameworks are in scope (framework scoping) and on the control-evidence map (which control maps to which piece of evidence). Consumes the PII inventory and encryption audit as evidence — does NOT re-derive them.
- **security-engineer**: Sole authority on the PII inventory and the encryption audit. Supplies these (and other security findings) to compliance-officer as control evidence. Does NOT decide framework scope or own the control-evidence map.

### feature flags vs ML experiments
- **software-engineer**: Owns the shared feature-flag infrastructure (the flag layer itself).
- **data-scientist**: Owns ML experiment design and uses flag-gated experiments. EXTENDS the shared flag layer — does NOT fork or reimplement it.

### supply-chain provenance & signing
- **security-engineer**: AUDITS supply-chain provenance and artifact signing (verifies it is correct and complete).
- **devops**: IMPLEMENTS provenance attestation and signing in the pipeline. security-engineer audits what devops implements — neither owns both sides.

### ux-designer vs frontend-engineer
- **ux-designer**: Owns the UX — research, IA, interaction design, and the design-system SPECIFICATION (tokens, type scale, WCAG-AA color, component specs, states, motion). Produces a spec, not code.
- **frontend-engineer**: IMPLEMENTS that spec in code. When a ux-designer design-system spec exists, it supersedes frontend-engineer's Phase 2 "functional defaults" — frontend builds to the spec, does NOT redefine it.

### growth-marketer vs sales-strategist
- **growth-marketer**: Owns positioning, messaging, and GTM/launch — the narrative and demand generation. Source of truth for how the product is described.
- **sales-strategist**: Owns pricing & packaging, sales collateral, sales process, and proposals. CONSUMES growth-marketer's positioning as the narrative; does NOT re-author it.

### customer-success vs product-manager / technical-writer
- **customer-success**: Owns onboarding, support operations, retention, and voice-of-customer. Synthesizes feedback and routes prioritized requests to product-manager — does NOT change requirements itself. Sources the help center from technical-writer's docs — does NOT rewrite them.
