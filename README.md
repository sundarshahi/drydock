# Drydock

**From a one-line idea to a launched product — a team of 19 specialized AI agents, orchestrated inside Claude Code.**

Drydock turns Claude Code into a full product team. You describe what you want in plain English; a single orchestrator routes the work to 19 specialized agents — product, architecture, UX design, backend, frontend, QA, security, DevOps, SRE, compliance, docs, and go-to-market (marketing/growth, sales, customer success) — that research, build, test, secure, document, and launch a real system. You stay in the strategist's seat and approve at three checkpoints; the agents do the work in between.

Each agent shows up as a `drydock:<skill>` skill. (Throughout these docs, "agent" and "skill" mean the same thing: a specialized worker the orchestrator routes to.)

---

## Quick start

**1. Install** — from inside Claude Code:

```text
/plugin marketplace add sundarshahi/drydock
/plugin install drydock
```

This registers the skills, hooks, and shared protocols. No local clone required.

**2. Use it** — just describe what you want, in plain English:

```text
Build a SaaS for booking dog walkers — auth, payments, and a dashboard.
```

Drydock reads your request, asks you to pick an [autonomy level](#autonomy-levels) (how often it checks in with you), then runs the [pipeline](#how-it-works) — pausing only at the three approval gates. You can also call any agent directly:

```text
/drydock:security-engineer audit my API for OWASP Top 10
```

**Requirements:** Claude Code is all you need to install and route. Git, Docker, and Docker Compose are used by the build/ship phases (git-worktree isolation, container builds, IaC) — install them if you plan to run a full build.

> **Local development** (running an unreleased checkout instead of the marketplace build):
> ```bash
> git clone https://github.com/sundarshahi/drydock ~/.claude/plugins/drydock
> claude --plugin-dir ~/.claude/plugins/drydock
> ```

---

## How it works

A full build flows through six phases. The agents work autonomously inside each phase; you only weigh in at the three gates (`◆`).

```
          Your idea, in plain English
                     │
                     ▼
   ┌─ DEFINE ────────────────────────────────────┐
   │   Product Manager    → requirements (BRD)    │
   │   Solution Architect → architecture + API    │
   │   UX Designer        → design system + flows │
   └──────────────────────────────────────────────┘
         ◆ GATE 1   you approve the requirements
         ◆ GATE 2   you approve the architecture
                     │
                     ▼
   ┌─ BUILD   ∥ in parallel ──────────────────────┐
   │   Backend · Frontend · DevOps ·              │
   │   QA · Security · Code Review · SRE          │
   └──────────────────────────────────────────────┘
                     │
                     ▼
   ┌─ HARDEN  ∥ in parallel ──────────────────────┐
   │   Tests · Security audit · Code review ·     │
   │   Container build                            │
   └──────────────────────────────────────────────┘
                     │
                     ▼
   ┌─ SHIP ───────────────────────────────────────┐
   │   IaC + CI/CD · SRE · Remediation            │
   └──────────────────────────────────────────────┘
         ◆ GATE 3   you approve production readiness
                     │
                     ▼
   ┌─ LAUNCH  ∥ in parallel ──────────────────────┐
   │   Marketing/Growth · Sales ·                 │
   │   Customer Success                           │
   └──────────────────────────────────────────────┘
                     │
                     ▼
   ┌─ SUSTAIN ────────────────────────────────────┐
   │   Docs · project-specific skills ·           │
   │   compound learning                          │
   └──────────────────────────────────────────────┘
                     │
                     ▼
     A real system: tested, secured, documented, deployed — and ready to launch.

   ∥  runs in parallel       ◆  you approve — everything between gates is autonomous
```

Not every request runs the whole pipeline. Drydock picks a [mode](#execution-modes) to match what you asked for — a code review or a single feature skips straight to the relevant agents, with fewer (or zero) gates.

---

## What you get — enterprise-grade by default

Every dimension below is **evidence-backed**: Drydock generates real artifacts and enforces blocking gates, not prose recommendations.

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

## Autonomy levels

You pick one autonomy level at the start of a build; it propagates to all 19 agents and controls **how many decisions get surfaced to you**. Higher autonomy = fewer interruptions. The three pipeline gates always fire — the autonomy level only governs the smaller, agent-level questions *between* the gates.

Drydock asks once (arrow keys + Enter). When in doubt, take **Copilot** — the recommended default.

| Level | Agent questions | Use when |
|---|---|---|
| **Autopilot** | None — auto-resolves and reports what it chose | Speed matters; trust the pipeline |
| **Copilot** *(default)* | 1–2 per skill — only key or irreversible calls | Best balance for most builds |
| **Checkpoint** | All major decisions surfaced before proceeding | Complex or high-stakes builds |
| **Manual** | Every decision, reviewed before any code is written | Full control, maximum oversight |

---

## Execution modes

Drydock routes your request to one of 14 modes (plus a **Custom** fallback when nothing matches — it shows a menu and lets you pick). You don't pick the mode — it's inferred from what you ask for.

| Mode | Say something like | Agents involved |
|---|---|---|
| **Full Build** | "build a SaaS", "from scratch" | All 19 |
| **Feature** | "add [feature]", "implement [feature]" | PM + Architect + Engineering + QA |
| **Harden** | "audit", "secure", "before launch" | Security + QA + Code Review |
| **Pentest (VAPT)** | "pentest", "vapt", "dast", "owasp api/llm" | Security Engineer (8-phase VAPT, gated) |
| **Compliance** | "soc2", "gdpr", "hipaa", "pci", "audit-ready" | Compliance Officer (controls mapping + gate) |
| **Ship** | "deploy", "CI/CD", "docker", "terraform" | DevOps + SRE |
| **Test** | "write tests", "test coverage" | QA |
| **Review** | "code review", "review my code" | Code Reviewer |
| **Architect** | "design", "architecture" | Solution Architect |
| **Design (UX)** | "wireframes", "user flows", "design system", "UX" | UX Designer |
| **Document** | "document", "write docs" | Technical Writer |
| **Explore** | "help me think", "I'm not sure" | Polymath |
| **Optimize** | "performance", "slow", "scale" | SRE + Code Reviewer |
| **Launch (GTM)** | "launch", "go to market", "pricing", "marketing", "sales" | Growth Marketer + Sales Strategist + Customer Success |

---

## The 19 agents

Each is invocable as `drydock:<skill>`, and the orchestrator routes to them based on your request.

| # | Agent | Owns |
|---|---|---|
| 1 | Orchestrator | Routing, gates, receipts |
| 2 | Polymath | Research, ideation, translation |
| 3 | Product Manager | Requirements |
| 4 | Solution Architect | Architecture |
| 5 | UX Designer | UX research, IA, design-system spec |
| 6 | Software Engineer | Backend |
| 7 | Frontend Engineer | Web UI |
| 8 | QA Engineer | Tests |
| 9 | Security Engineer | Security + VAPT |
| 10 | Code Reviewer | Code quality |
| 11 | DevOps | Infrastructure |
| 12 | SRE | Reliability |
| 13 | Data Scientist | LLM/ML optimization |
| 14 | Technical Writer | Documentation |
| 15 | Skill Maker | Project-specific skills |
| 16 | Compliance Officer | Regulatory compliance |
| 17 | Growth Marketer | Positioning, launch, marketing |
| 18 | Sales Strategist | Pricing, collateral, sales process |
| 19 | Customer Success | Onboarding, support, retention |

### Invoking an agent directly

Let the orchestrator route for you, or call any agent by name:

| Invocation | Agent |
|---|---|
| `/drydock:drydock` | Orchestrator (routing + gates) |
| `/drydock:polymath` | Polymath |
| `/drydock:product-manager` | Product Manager |
| `/drydock:solution-architect` | Solution Architect |
| `/drydock:ux-designer` | UX Designer |
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
| `/drydock:growth-marketer` | Growth Marketer |
| `/drydock:sales-strategist` | Sales Strategist |
| `/drydock:customer-success` | Customer Success |

---

## Key behaviors

What makes the output trustworthy rather than just plausible:

- **Receipt enforcement** — every agent writes JSON proof of its work; gates verify the receipts (and the artifacts they claim) before opening.
- **Re-anchoring** — specs are re-read from disk at every phase transition, so long runs don't drift from the original requirements.
- **Adversarial review** — the Code Reviewer assumes the code is wrong until proven right.
- **Grounding / anti-hallucination** — evidence-first: every claim cites `file:line`, command output, or a retrieved source, tagged `[verified]` / `[inferred]` / `[unverified]`; never invents CVEs or CVSS scores.
- **VAPT authorization gate** — active/DAST testing runs only against explicitly authorized local/staging targets; no DoS or destructive payloads; responsible disclosure.
- **Freshness protocol** — agents WebSearch volatile data (model IDs, CVEs, versions) before implementing, instead of trusting stale training data.
- **Boundary safety** — six structural patterns that catch system-boundary bugs.
- **Worktree isolation** — parallel agents each run in their own git worktree, so concurrent work never clobbers files.

---

## Workspace structure (created per project)

A run scaffolds a `drydock/` directory in your project to hold pipeline state and per-agent artifacts:

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

Configuration is optional — Drydock asks what it needs at runtime. To pin paths, preferences, and feature toggles, copy `skills/_shared/templates/drydock.yaml.tmpl` to `.drydock.yaml` at your project root.

---

## Partial execution

Run a single phase or skip one — useful for iterating on an existing project:

```bash
/drydock just define       # requirements + architecture only
/drydock just build        # requires DEFINE output
/drydock just harden       # requires BUILD output
/drydock pentest           # 8-phase VAPT — live DAST + report (gated; authorized targets only)
/drydock compliance        # map regulatory controls to artifacts (gated)
/drydock just ship         # requires HARDEN output
/drydock just document     # documentation only
/drydock skip frontend     # omit the frontend agent
```

---

## License

MIT
