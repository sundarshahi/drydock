# Shipyard — Personal Dev Plugin for Claude Code

**14 specialized agents. 11 execution modes. Idea to production.**

## Installation

```bash
git clone <your-repo-url> ~/.claude/plugins/shipyard
claude --plugin-dir ~/.claude/plugins/shipyard
```

**Requirements:** Claude Code, Docker & Docker Compose, Git.

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

## 11 Execution Modes

| Mode | Trigger | Agents |
|---|---|---|
| **Full Build** | "build a SaaS", "from scratch" | All 14 |
| **Feature** | "add [feature]", "implement [feature]" | PM + Arch + Eng + QA |
| **Harden** | "audit", "secure", "before launch" | Security + QA + Review |
| **Pentest (VAPT)** | "pentest", "vapt", "dast", "owasp api/llm" | Security Engineer (8-phase VAPT, gated) |
| **Ship** | "deploy", "CI/CD", "docker", "terraform" | DevOps + SRE |
| **Test** | "write tests", "test coverage" | QA |
| **Review** | "code review", "review my code" | Code Reviewer |
| **Architect** | "design", "architecture" | Solution Architect |
| **Document** | "document", "write docs" | Technical Writer |
| **Explore** | "help me think", "I'm not sure" | Polymath |
| **Optimize** | "performance", "slow", "scale" | SRE + Code Reviewer |

---

## The 14 Agents

| # | Agent | Sole Authority |
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
├── .protocols/        # 8 shared protocols
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
└── skill-maker/
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
/shipyard just ship         # Requires HARDEN output
/shipyard just document     # T11 only
/shipyard skip frontend     # Omit T3b
```

---

## License

MIT
