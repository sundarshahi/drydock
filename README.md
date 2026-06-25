# Drydock — Personal Dev Plugin for Claude Code

**15 orchestrated skills. 12 execution modes. Idea to production.**

Drydock is a set of orchestrated skills (each shows up as a `drydock:<skill>` invocation) coordinated by a single orchestrator. Throughout these docs "agent" and "skill" refer to the same thing: a specialized worker the orchestrator routes to.

## Install (marketplace)

Install Drydock from inside Claude Code using the plugin marketplace flow:

```text
/plugin marketplace add sundarshahi/drydock
/plugin install drydock
```

This pulls the published plugin and registers its skills, hooks, and shared protocols. No local clone required.

**Requirements:** Claude Code, Docker & Docker Compose, Git.

## Install (dev / local clone)

For local development or to run an unreleased checkout:

```bash
git clone https://github.com/sundarshahi/drydock ~/.claude/plugins/drydock
claude --plugin-dir ~/.claude/plugins/drydock
```

---

## Enterprise-grade by default

Every dimension below is **evidence-backed** — Drydock generates real artifacts and enforces blocking gates, not prose recommendations.

- **12-Factor** — config from environment, stateless processes, and disposability are scaffolded and checked, not assumed.
- **Clean Architecture** — the dependency rule is enforced by the `architecture-boundaries` protocol; boundary violations block `production-ready`.
- **API-first** — OpenAPI specs are the source of truth; contracts are linted and `can-i-deploy` is a gate input.
- **Observability** — generated OpenTelemetry traces/metrics/logs plus RED/USE metric sets, wired to an OTLP endpoint.
- **Security-by-default** — the `security-defaults` protocol plus a real `secret-guard` hook that blocks secret writes/commits and scans staged diffs.
- **CI/CD + supply-chain** — lint-clean GitHub Actions templates with SLSA provenance and cosign artifact signing.
- **Automated testing** — unit/integration plus mutation and property-based tests default-on; coverage and mutation score are gate metrics.
- **Performance budgets** — budgets defined in `docs/architecture/performance-budget.yaml`; baseline regression blocks the readiness gate.
- **Feature flags** — OpenFeature provider with an env-var fallback, generated into the runtime.
- **Developer experience (DX)** — consistent tooling, scaffolds, and runbooks so the generated project is pleasant to extend.
- **Per-product regulatory compliance** — the Compliance Officer maps SOC 2 / GDPR / HIPAA / PCI-DSS controls to artifacts; missing controls block the gate.
- **Anti-hallucination grounding** — evidence-first generation: every claim cites `file:line`, command output, or a retrieved source.

Errors follow **RFC 9457 `application/problem+json`** by default. `production-ready` is **blocked** on failing tests, coverage, performance budget, compliance controls, or architecture-boundary violations — overridable only with a logged "accepted with justification" receipt.

---

## The Pipeline

```
YOU → "Build a SaaS for ..."
       │
       ▼
┌─────────────────────────────────────┐
│  DEFINE                             │
│  Product Manager — BRD              │
│  Solution Architect — ADRs + API    │
│  [GATE 1: Requirements]             │
│  [GATE 2: Architecture]             │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  BUILD + ANALYZE  (Wave A — parallel)│
│  Backend · Frontend · DevOps        │
│  QA · Security · Review · SRE       │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  HARDEN  (Wave B — parallel)        │
│  Tests · Security Audit · Review    │
│  Container Build                    │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  SHIP                               │
│  IaC + CI/CD · SRE · Remediation   │
│  [GATE 3: Production Readiness]     │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  SUSTAIN                            │
│  Technical Writer · Skill Maker     │
│  Compound Learning                  │
└─────────────────────────────────────┘
```

---

## 12 Execution Modes

| Mode | Trigger | Skills |
|---|---|---|
| **Full Build** | "build a SaaS", "from scratch" | All 15 |
| **Feature** | "add [feature]", "implement [feature]" | PM + Arch + Eng + QA |
| **Harden** | "audit", "secure", "before launch" | Security + QA + Review |
| **Pentest (VAPT)** | "pentest", "vapt", "dast", "owasp api/llm" | Security Engineer (8-phase VAPT, gated) |
| **Compliance** | "soc2", "gdpr", "hipaa", "pci", "compliance", "audit-ready" | Compliance Officer (controls mapping + gate) |
| **Ship** | "deploy", "CI/CD", "docker", "terraform" | DevOps + SRE |
| **Test** | "write tests", "test coverage" | QA |
| **Review** | "code review", "review my code" | Code Reviewer |
| **Architect** | "design", "architecture" | Solution Architect |
| **Document** | "document", "write docs" | Technical Writer |
| **Explore** | "help me think", "I'm not sure" | Polymath |
| **Optimize** | "performance", "slow", "scale" | SRE + Code Reviewer |

---

## The 15 Skills

These are orchestrated skills — each is invocable as `drydock:<skill>` and the orchestrator routes to them based on your request.

| # | Skill | Sole Authority |
|---|---|---|
| 1 | Orchestrator | Routes, gates, receipts |
| 2 | Polymath | Research, ideation, translation |
| 3 | Product Manager | Requirements |
| 4 | Solution Architect | Architecture |
| 5 | Software Engineer | Backend |
| 6 | Frontend Engineer | UI/UX |
| 7 | QA Engineer | Tests |
| 8 | Security Engineer | Security + VAPT |
| 9 | Code Reviewer | Code Quality |
| 10 | DevOps | Infrastructure |
| 11 | SRE | Reliability |
| 12 | Data Scientist | LLM/ML optimization |
| 13 | Technical Writer | Documentation |
| 14 | Skill Maker | Project-specific skills |
| 15 | Compliance Officer | Regulatory compliance |

---

## Invocation

Invoke any skill directly with its `drydock:<skill>` name, or let the orchestrator route for you.

| Invocation | Skill |
|---|---|
| `/drydock:drydock` | Orchestrator (routing + gates) |
| `/drydock:polymath` | Polymath |
| `/drydock:product-manager` | Product Manager |
| `/drydock:solution-architect` | Solution Architect |
| `/drydock:software-engineer` | Software Engineer |
| `/drydock:frontend-engineer` | Frontend Engineer |
| `/drydock:qa-engineer` | QA Engineer |
| `/drydock:security-engineer` | Security Engineer |
| `/drydock:code-reviewer` | Code Reviewer |
| `/drydock:devops` | DevOps |
| `/drydock:sre` | SRE |
| `/drydock:data-scientist` | Data Scientist |
| `/drydock:technical-writer` | Technical Writer |
| `/drydock:skill-maker` | Skill Maker |
| `/drydock:compliance-officer` | Compliance Officer |

---

## Key Behaviors

- **Receipt enforcement** — every agent writes JSON proof; gates verify before opening
- **Re-anchoring** — specs re-read from disk at every phase transition (no context drift)
- **Adversarial review** — code reviewer assumes code is wrong until proven right
- **Grounding / anti-hallucination** — evidence-first: every claim cites `file:line`, command output, or a retrieved source; `[verified]`/`[inferred]`/`[unverified]` confidence tags; cite-or-abstain; never invents CVEs/CVSS
- **VAPT authorization gate** — active/DAST testing only against explicitly authorized, local/staging targets; no DoS/destructive payloads; responsible disclosure
- **Freshness protocol** — agents WebSearch volatile data (model IDs, CVEs) before implementing
- **Boundary safety** — 6 structural patterns for system boundary bugs
- **Worktree isolation** — parallel agents each get their own git worktree (zero file conflicts)

---

## Autonomy Levels

You pick one autonomy level at the start of a build; it propagates to all 15 agents and controls **how many decisions get surfaced to you**. Higher autonomy = fewer interruptions. The three pipeline gates (Requirements, Architecture, Production Readiness) always fire — the autonomy level only governs the smaller, agent-level questions *between* the gates.

Drydock asks once (arrow keys + Enter). When in doubt, take **Copilot** — the recommended default.

| Level | Agent questions | Use when |
|---|---|---|
| **Autopilot** | None — auto-resolves and reports what it chose | Speed matters; trust the pipeline |
| **Copilot** *(default)* | 1–2 per skill — only key or irreversible calls | Best balance for most builds |
| **Checkpoint** | All major decisions surfaced before proceeding | Complex or high-stakes builds |
| **Manual** | Every decision, reviewed before any code is written | Full control, maximum oversight |

---

## Workspace Structure (created per project)

```
drydock/
├── .protocols/        # shared protocols deployed at bootstrap
├── .orchestrator/     # pipeline state + receipts
├── product-manager/
├── solution-architect/
├── software-engineer/
├── frontend-engineer/
├── qa-engineer/
├── security-engineer/
├── code-reviewer/
├── devops/
├── sre/
├── data-scientist/
├── technical-writer/
├── skill-maker/
└── compliance-officer/
```

---

## Configuration

Copy `skills/_shared/templates/drydock.yaml.tmpl` to `.drydock.yaml` at project root to customize paths, preferences, and feature toggles.

---

## Partial Execution

```bash
/drydock just define       # T1 + T2 only
/drydock just build        # Requires DEFINE output
/drydock just harden       # Requires BUILD output
/drydock pentest           # 8-phase VAPT — live DAST + report (gated; authorized targets only)
/drydock compliance        # Map regulatory controls to artifacts (gated)
/drydock just ship         # Requires HARDEN output
/drydock just document     # T11 only
/drydock skip frontend     # Omit T3b
```

---

## License

MIT
