---
sidebar_position: 4
title: "Quality & security"
description: "QA Engineer, Security Engineer, Code Reviewer, and Compliance Officer: the agents that harden the build."
---

# Quality & security

Four agents harden the build in the **HARDEN** phase, after the implementation agents have written the code and before anything moves toward [SHIP](/docs/concepts/how-it-works). They run as isolated subagents, each with a tightly drawn authority boundary so they reinforce rather than overlap: the QA Engineer proves the code *works*, the Security Engineer proves it *resists attack*, the Code Reviewer proves it is *well-built*, and the Compliance Officer proves it *meets regulation*.

| Agent | What it proves | Authority |
|-------|----------------|-----------|
| **QA Engineer** | Tests exist, pass, and have teeth | Tests + coverage/mutation/contract/perf gates |
| **Security Engineer** | Code resists attack | SOLE authority on OWASP, STRIDE, PII, encryption; runs VAPT |
| **Code Reviewer** | Code is correct and well-structured | Architecture, code quality, performance, test quality — **NOT security** |
| **Compliance Officer** | The product meets its frameworks | Framework scoping + control-evidence map; **consumes** the security audit |

:::info All four run in HARDEN
None of these agents write product features. They run *after* the Software Engineer and Frontend Engineer have built the system, and their gates feed the [Gate 3 production-readiness](/docs/concepts/how-it-works) decision.
:::

---

## QA Engineer

The QA Engineer writes and runs the test suite. It runs after implementation is complete and **does not modify source code** — it generates test files and test infrastructure to `tests/` at the project root, and reports to `drydock/qa-engineer/`.

**What it checks** — across seven phases (planning, then five test types in parallel, then infrastructure):

- **Unit** tests for handlers, services, repositories, validators — plus **property-based and fuzz** tests on high-risk surfaces (validators, parsers, serializers, money/billing, authz predicates). A critical module without a property test is a finding.
- **Integration** tests against real dependencies via testcontainers, with images pinned by `@sha256:` digest.
- **Contract** tests (Pact consumer/provider + OpenAPI schema), gated by `pact-broker can-i-deploy`.
- **E2E** tests for the top critical user flows.
- **Performance** tests (k6), with thresholds read from `docs/architecture/performance-budget.yaml` — never hardcoded — and baseline-regression detection.
- **Mutation testing** (nightly, scoped to critical modules) to prove the tests would actually catch a bug, not just run the line.

**The gate it owns.** The orchestrator gates `production-ready` on QA, and it reads the machine-readable `metrics` block of the QA receipt — not prose. These fields, emitted from real tool output, block production-readiness:

| Receipt field | Blocks when |
|---------------|-------------|
| `tests_failing` | `> 0` |
| `coverage_lines` / `coverage_branches` | below the gate in `thresholds.json` |
| `patch_coverage` | below the patch threshold (~80%) |
| `mutation_score` | below the configured minimum |
| `contract_can_i_deploy` | `false` |
| `perf_baseline_regression` | `true` |

:::warning Any failing test is a remediation finding
There is no soft "flag if failures exceed X%" path. **Any** failing test (`tests_failing > 0`) is written as a remediation finding and feeds the HARDEN remediation chain like a Critical. The only non-remediation exit is an explicit, logged "accepted with justification" override receipt.
:::

---

## Security Engineer

The Security Engineer is the **sole authority on OWASP Top 10, STRIDE, PII, and encryption**. No other agent performs security review. It conducts application-level security analysis — threat modeling, code auditing, data-protection review, and remediation — and, unlike the Code Reviewer, **applies fixes directly to project code**.

**What it checks** — eight phases, with the analysis domains running in parallel after the threat model:

- **Threat modeling** (STRIDE), attack surface, trust boundaries, data-flow threats.
- **OWASP code audit** against **OWASP Top 10:2025 RC1** (Web), **OWASP API Security Top 10:2023**, and the **OWASP Top 10 for LLM Applications:2025** when LLM/ML usage is detected. Every finding carries a CVSS 4.0 vector, CWE, WSTG test id, and ASVS requirement id — pulled live, never recalled from memory.
- **Auth review** — auth flows, token management, RBAC/ABAC.
- **Data security** — the PII inventory and encryption audit.
- **Supply chain** — SBOM, dependency vulnerabilities, license compliance.

:::note VAPT — authorized targets only
Phases 7–8 are **VAPT** (Vulnerability Assessment & Penetration Testing): authorized DAST/pen-test execution against a live target with captured PoC evidence, followed by a professional pentest report (scope/RoE, methodology, CVSS-backed risk matrix, per-finding evidence, retest status). These phases run **only** in the orchestrator's Pentest (VAPT) mode, after an authorization gate sets `vapt_authorized`. In plain HARDEN, the audit stops at Phase 6 (static analysis).
:::

**Scope boundary.** This is *application* security. Infrastructure security — WAF rules, IAM policies, network security groups, KMS, container image scanning — belongs to the DevOps agent, not here.

---

## Code Reviewer

The Code Reviewer is an **adversarial, read-only quality gate** wired as **Gate 3**. Its job is not to confirm the code works — it is to find where it breaks. It produces findings and patch suggestions only, writing exclusively to `drydock/code-reviewer/`; remediation is a separate orchestrator task.

:::warning The Code Reviewer does NOT do security
Security analysis is the sole responsibility of the [Security Engineer](#security-engineer). The Code Reviewer performs no OWASP or vulnerability review — it defers every security finding and focuses on architecture, code quality, performance, and test quality.
:::

**What it checks** — four dimensions run in parallel, then a report compiles them:

1. **Architecture conformance** — runs `make arch` (the inward-only dependency fitness function) and audits every ADR. A non-zero `make arch`, an inward framework/IO import, a port-boundary violation, or an error response that isn't RFC 9457 `application/problem+json` is **HIGH and pipeline-blocking**.
2. **Code quality** — SOLID/DRY, cyclomatic complexity, error handling, and (proportionally, for domain-rich services only) anemic-domain / primitive-obsession.
3. **Performance** — N+1 queries, unbounded queries, missing caching, with thresholds read from `performance-budget.yaml`.
4. **Test quality** — coverage gaps, assertion strength, and test independence, cross-referenced against the QA Engineer's traceability matrix.

**Gate authority.** Every Critical and every HIGH finding feeds the blocking finding → fix → verify chain — the orchestrator must not advance to deployment-pipeline configuration while one is open. A HIGH may be accepted only with a logged, justified override (and for arch-boundary breaches, a config-covered, time-boxed, ticket-referenced exception). Softening a HIGH to Medium to "let it through" is itself a review defect.

---

## Compliance Officer

The Compliance Officer scopes the product's regulatory frameworks — SOC 2, GDPR, HIPAA, PCI-DSS v4.0.1, CCPA/CPRA, ISO 27001, FedRAMP — maps each framework's mandatory controls to implementing artifacts, verifies those controls actually exist in the generated code and infra, and produces the statutory evidence (SSP, DPIA, breach runbook). It runs in HARDEN, alongside and after the security audit.

:::info It consumes the security audit — it does not redo it
The Security Engineer remains the **sole authority** on the PII inventory, data classification, and encryption audit. The Compliance Officer **reads** `drydock/security-engineer/data-security/` — the PII inventory drives the deterministic signals→frameworks map, and the encryption audit maps to crypto/at-rest/in-transit controls. It never re-runs the PII scan or re-audits encryption; where a control needs an artifact that doesn't exist, it raises a finding for the owning agent rather than implementing it.
:::

**What it checks** — five phases:

1. **Framework scoping** — deterministic signals (PHI, cardholder data, EU users, California consumers, enterprise/federal buyers) → frameworks, each backed by evidence.
2. **Control matrix** — per-framework mandatory controls, every control id verified live against its official source (URL + quoted span), never recalled from memory.
3. **Controls implementation check** — each required control mapped to an implementing artifact `path:line` and marked Met / Partial / Missing. `Met` requires a real path; no path means `Missing`.
4. **Evidence & docs** — SSP, GDPR DPIA, and a breach runbook encoding statutory clocks (GDPR 72-hour, HIPAA 60-day), plus the control-evidence map.
5. **Compliance gate** — any **Missing mandatory control is BLOCKING**.

The orchestrator blocks `production-ready` while the receipt's `compliance.controls_missing` list is non-empty. As with the other HARDEN gates, the only release path past a gap is an explicit accept-with-justification override receipt.

---

## How the four fit together

```
HARDEN
  QA Engineer ────────► tests + coverage/mutation/contract/perf gates
  Security Engineer ──► OWASP/STRIDE/PII/encryption audit  ──┐  (+ VAPT in Pentest mode)
  Code Reviewer ──────► arch/quality/perf/test-quality gate │
  Compliance Officer ◄── consumes security audit ───────────┘
```

Each agent's blocking gate feeds the [Gate 3 production-readiness](/docs/concepts/how-it-works) decision — one of Drydock's three human approval gates. See [How it works](/docs/concepts/how-it-works) for the full DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN pipeline, and the [agents overview](/docs/agents/overview) for the other 15 specialists.
