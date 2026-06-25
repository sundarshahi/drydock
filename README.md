# Shipyard — Personal Dev Plugin for Claude Code

**15 orchestrated skills. 12 execution modes. Idea to production.**

Shipyard is a set of orchestrated skills (each shows up as a `shipyard:<skill>` invocation) coordinated by a single orchestrator. Throughout these docs "agent" and "skill" refer to the same thing: a specialized worker the orchestrator routes to.

## Install (marketplace)

Install Shipyard from inside Claude Code using the plugin marketplace flow:

```text
/plugin marketplace add sundarshahi/shipyard
/plugin install shipyard
```

This pulls the published plugin and registers its skills, hooks, and shared protocols. No local clone required.

**Requirements:** Claude Code, Docker & Docker Compose, Git.

## Install (dev / local clone)

For local development or to run an unreleased checkout:

```bash
git clone https://github.com/sundarshahi/shipyard ~/.claude/plugins/shipyard
claude --plugin-dir ~/.claude/plugins/shipyard
```

---

## Enterprise-grade by default

Every dimension below is **evidence-backed** — Shipyard generates real artifacts and enforces blocking gates, not prose recommendations.

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

These are orchestrated skills — each is invocable as `shipyard:<skill>` and the orchestrator routes to them based on your request.

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

Invoke any skill directly with its `shipyard:<skill>` name, or let the orchestrator route for you.

| Invocation | Skill |
|---|---|
| `/shipyard:shipyard` | Orchestrator (routing + gates) |
| `/shipyard:polymath` | Polymath |
| `/shipyard:product-manager` | Product Manager |
| `/shipyard:solution-architect` | Solution Architect |
| `/shipyard:software-engineer` | Software Engineer |
| `/shipyard:frontend-engineer` | Frontend Engineer |
| `/shipyard:qa-engineer` | QA Engineer |
| `/shipyard:security-engineer` | Security Engineer |
| `/shipyard:code-reviewer` | Code Reviewer |
| `/shipyard:devops` | DevOps |
| `/shipyard:sre` | SRE |
| `/shipyard:data-scientist` | Data Scientist |
| `/shipyard:technical-writer` | Technical Writer |
| `/shipyard:skill-maker` | Skill Maker |
| `/shipyard:compliance-officer` | Compliance Officer |

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

## Engagement Modes

| Mode | Questions | Use When |
|---|---|---|
| Express | Zero (3 gates only) | Speed matters, trust the pipeline |
| Standard | 1-2 per skill | Best default balance |
| Thorough | All major decisions | Complex or high-stakes builds |
| Meticulous | Every decision | Full control, maximum oversight |

---

## Workspace Structure (created per project)

```
Shipyard/
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

Copy `skills/_shared/templates/shipyard.yaml.tmpl` to `.shipyard.yaml` at project root to customize paths, preferences, and feature toggles.

---

## Partial Execution

```bash
/shipyard just define       # T1 + T2 only
/shipyard just build        # Requires DEFINE output
/shipyard just harden       # Requires BUILD output
/shipyard pentest           # 8-phase VAPT — live DAST + report (gated; authorized targets only)
/shipyard compliance        # Map regulatory controls to artifacts (gated)
/shipyard just ship         # Requires HARDEN output
/shipyard just document     # T11 only
/shipyard skip frontend     # Omit T3b
```

---

## License

MIT
