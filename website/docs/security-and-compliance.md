---
sidebar_position: 7
title: "Security & compliance"
description: "Security-by-default controls, OWASP/ASVS audits, VAPT, and per-product compliance mapping."
---

# Security & compliance

Drydock treats security as a build-time contract, not a final-phase clean-up. Code ships secure-by-default the moment it is written, a dedicated audit confirms it, and — only when explicitly authorized — Drydock runs penetration testing and maps your product against the regulatory frameworks that actually apply to it.

This page describes what Drydock does and the published standards it audits against. It is not a certification, and Drydock does not issue one. See [Honest claims](#honest-claims-and-limitations) below for the boundaries.

:::info Where this fits in the pipeline
Security and compliance work runs in the **HARDEN** phase of the [DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN](/docs/concepts/how-it-works) pipeline, after implementation and testing are complete. Two of Drydock's 19 agents own it: the **security-engineer** (application security, the SOLE authority on OWASP review, STRIDE, PII, and encryption) and the **compliance-officer** (per-product framework scoping and control evidence). Both run as isolated subagents.
:::

## Secure-by-default at build time

Every BUILD agent ships secure-by-default code at write time. The core principle is explicit: you do not wait for the HARDEN audit to add input validation, authorization, or output encoding — **the audit confirms; it does not retrofit the basics.**

These defaults are non-negotiable for any code that touches external input, data stores, outbound calls, auth, or rendering. Each rule maps to a published OWASP standard and is written so a reviewer can verify pass/fail by reading the diff.

| Default | Standard |
|---------|----------|
| Validate all external input at the trust boundary (fail-closed, allowlist) | ASVS V5.1 / OPC C5 |
| Parameterized queries / prepared statements only | ASVS V5.3 / OPC C3 |
| Context-aware output encoding & safe templating (no unsanitized HTML) | ASVS V5.2 / OPC C4 |
| SSRF allowlist on user-controlled outbound URLs | ASVS V5.2.6 / OPC C5 |
| Secrets only from env / secret manager, never logged | ASVS V6.4 / OPC C8 |
| Default-deny per-object authorization (no BOLA/IDOR) | ASVS V4.2 / OPC C7 |
| Property-level authorization (no mass assignment / BOPLA) | API3:2023 / ASVS V4 |
| Security headers, strict CORS, secure cookies | ASVS V3 / V13 |
| Dependency pinning, committed lockfile, post-add SCA | ASVS V14.2 / OPC C2 |
| Strong crypto: memory-hard KDF, authenticated encryption, CSPRNG, TLS 1.2+ | ASVS V11 / OPC C8 |
| Auth throttling, lockout, safe recovery, no user enumeration | ASVS V6 / OPC C6 |
| Session / JWT lifecycle (regenerate on privilege change, alg allowlist) | ASVS V7 / V9 |
| Resource-consumption & anti-automation limits | API4:2023 / API6:2023 |
| Treat third-party / upstream API responses as untrusted | API10:2023 |
| Security event logging (authn / authz / denials) | ASVS V16 / OPC C9 |
| LLM/AI defaults: untrusted model output, gated tool calls, prompt-injection boundary | LLM01 / LLM02 / LLM06 |

The defaults target **OWASP ASVS 5.0 Level 2** (the standard level for most apps and regulated industries) and the **OWASP Proactive Controls (OPC)**.

:::note The BUILD Quality Bar
A BUILD phase is not complete until it asserts `security-defaults checklist passes` in its completion receipt. Any consciously deferred item is logged explicitly as a HARDEN hand-off with a reason — never silently skipped.
:::

## The HARDEN audit + STRIDE

The security-engineer runs an eight-phase audit in HARDEN, after the code is stable.

| Phase | Focus |
|-------|-------|
| 0 | Reconnaissance — map services, data flows, auth, integrations |
| 1 | Threat modeling — STRIDE, attack surface, trust boundaries, data-flow threats |
| 2 | Code audit — OWASP Top 10 review, per-service findings, injection points |
| 3 | Auth review — authentication flows, token management, RBAC/ABAC |
| 4 | Data security — PII inventory, encryption audit, data retention |
| 5 | Supply chain — SBOM, dependency vulnerabilities, license compliance |
| 6 | Remediation — fixes with before/after code, timeline, pen-test plan |
| 7 | VAPT execution — *gated; authorized targets only* |
| 8 | VAPT report — professional pentest report |

Phase 1 uses **STRIDE** (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege) to derive a threat model. That model feeds forward into machine-readable security requirements that BUILD agents read — so threats drive controls in code, not just a HARDEN reconcile.

After threat modeling, phases 2–5 run in parallel; phase 6 synthesizes all findings sequentially. In plain HARDEN, the audit stops at phase 6 (static analysis). Phases 7–8 are **not** part of the parallel HARDEN wave.

### Standards every finding maps to

Findings are tagged against the current published standards, with the precise per-finding id pulled from the live checklist at audit time (never recalled from memory):

- **OWASP Top 10:2025 RC1 (Web)** — Drydock audits against the Release Candidate categories ahead of ratification. The 2025 set is RC1 and not yet finalized; 2021 remains the last ratified edition, and the RC1 set may still shift. Reports are labeled "OWASP Top 10:2025 RC1".
- **OWASP API Security Top 10 — 2023** — BOLA, BOPLA, BFLA, unrestricted resource consumption, SSRF, and the rest.
- **OWASP Top 10 for LLM Applications — 2025 (v2.0)** — applied when LLM/ML usage is detected (prompt injection, sensitive information disclosure, excessive agency, system prompt leakage, and more).
- **OWASP ASVS 5.0.0** (May 2025) — L1/L2/L3 verification levels; the requirement id and level are cited per finding.
- **OWASP WSTG v4.2** — the test id is cited per active test.
- **CVSS 4.0** for new findings (with 3.1 retained for NVD compatibility); base score paired with EPSS and CISA KEV, never used alone. Human-readable severity is derived from the CVSS base score, not assigned ad hoc.

Every finding references specific files, lines, and code patterns — a generic checklist item is not a finding.

## VAPT mode and the authorization gate

Vulnerability Assessment and Penetration Testing (phases 7–8) is **active** testing — DAST execution and proof-of-concept exploitation against a live target. It runs only in the orchestrator's dedicated **Pentest (VAPT)** mode, one of Drydock's 14 execution modes.

:::warning Authorized targets only
Phases 7–8 do not run until an **authorization gate** sets `vapt_authorized`. Without it, the security audit stops at phase 6 and stays **static/passive only**. Active scanning and exploitation are never performed against a target you have not explicitly authorized.
:::

Once authorized, VAPT execution runs attack scenarios, captures request/response evidence and PoCs, and records PASS/FAIL/INCONCLUSIVE per scenario across the OWASP API and LLM Top 10. Phase 8 then produces a professional pentest report: scope and rules of engagement, methodology, a CVSS-backed risk matrix, per-finding evidence with retest status, and a tools appendix.

## Per-product compliance mapping

The compliance-officer scopes the regulatory frameworks that apply to **your specific product**, then maps mandatory controls to the artifacts that implement them. Scoping is deterministic: a framework is only scoped when a present, evidenced **product signal** is found (e.g. PHI in the data classification, cardholder data in a code path, EU users in the BRD). Out-of-scope frameworks are logged with the missing signal so the decision is auditable.

| Framework | Typical triggering signal |
|-----------|---------------------------|
| **SOC 2** | Enterprise buyer needing a trust attestation |
| **GDPR** | EU personal data in scope |
| **HIPAA** | Protected health information (PHI) |
| **PCI-DSS** (v4.0.1) | Cardholder data |
| **ISO 27001** | Information-security management attestation |
| **FedRAMP** | Federal customer / government cloud |

The compliance-officer runs five phases: framework scoping → control matrix (per framework, with control ids **verified live** against the official source) → controls-implementation check (each control mapped to an implementing artifact at `path:line`, marked Met/Partial/Missing) → evidence & docs → compliance gate.

It consumes the security-engineer's outputs rather than redoing them: the **PII inventory** and **encryption audit** remain the security-engineer's sole authority. The compliance-officer reads `drydock/security-engineer/data-security/` and maps those findings to controls; where a control needs an artifact that does not exist, it raises a finding for the owning agent instead of implementing the control itself.

### Statutory documents and the compliance gate

Phase 4 produces the statutory evidence — a System Security Plan (SSP), a GDPR Data Protection Impact Assessment (DPIA) when EU personal data is in scope, and a breach/incident runbook that encodes the statutory clocks (GDPR 72-hour supervisory-authority notice, HIPAA 60-day individual notice), with the exact wording verified live.

:::note Blocking gate
A **Missing mandatory control is a BLOCKING finding** — it routes to HARDEN remediation or requires an explicit accept-with-justification override receipt; it is never silently skipped. The orchestrator blocks production-readiness (Gate 3) while any mandatory control remains Missing.
:::

## Honest claims and limitations

Drydock is rigorous about not overstating what it provides.

- **Drydock does not certify your product.** It produces the controls, evidence map, and statutory documents that support an audit; it does not issue or substitute for a SOC 2 report, ISO 27001 certificate, FedRAMP authorization, or any third-party attestation.
- **OWASP Top 10:2025 is RC1, not ratified.** Drydock deliberately audits against the RC1 categories ahead of ratification, labels reports accordingly, and the category set may still change before the final release.
- **Control ids and citations are verified live, not recalled.** The compliance-officer never states a control id, article number, or requirement text from memory — every cited id is verified against its official source in-session, with a URL and quoted span.
- **VAPT requires your authorization.** Active scanning and exploitation only run against targets you have explicitly authorized via the gate.
- **Security is continuous.** A single audit is a snapshot. Re-audit when architecture, data classification, or target markets change.

## Related

- [How it works](/docs/concepts/how-it-works) — the full DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN pipeline and the three human approval gates
- [Agents](/docs/agents/overview) — the 19-agent team, including the security-engineer and compliance-officer
- [Execution modes](/docs/concepts/modes) — the 14 modes, including Pentest (VAPT)
