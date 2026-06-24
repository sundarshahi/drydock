# Changelog

All notable changes to **Shipyard**.

## [5.5.0] — 2026-06-24

### Added
- **Grounding & Anti-Hallucination protocol** — new shared protocol `grounding-protocol.md`, loaded by all 14 agents. Evidence-first generation: every factual/code claim cites `file:line`, command output, or a retrieved source; claim↔evidence separation; `[verified]`/`[inferred]`/`[unverified]` confidence tags; cite-or-abstain; a 4-step chain-of-verification; and security-specific no-fabrication (never invent CVE ids or CVSS scores).
- **Security Testing Authorization & Safety protocol** — new shared protocol `security-testing-protocol.md`, loaded by the Security Engineer. Mandatory authorization + scope gate before any active testing; local/authorized-staging targets only; no DoS/destructive payloads/production data; responsible disclosure; evidence-backed findings; CVSS discipline (4.0 primary, 3.1 ingested, paired with EPSS/CISA KEV).
- **Real VAPT execution** — two new Security Engineer phases. `07-vapt-execution.md` runs gated DAST/pen-testing (recon→enum→scan→exploit/PoC→retest) with a 24-tool integration table (semgrep, CodeQL, trivy, grype, osv-scanner, gitleaks, trufflehog, checkov, OWASP ZAP, nuclei, nikto, sqlmap, wapiti, ffuf, schemathesis, RESTler…), each with verified invocations and safe-by-default usage; all active/DAST tools are gated behind the authorization step. `08-vapt-report.md` assembles a professional CVSS-backed pentest report. The Security Engineer now runs 8 phases.
- **Pentest (VAPT) execution mode** — new orchestrator mode with a mandatory authorization-gate prompt before any active testing, plus `/shipyard pentest` and `/shipyard vapt` commands. HARDEN mode remains static-only so the gate cannot be bypassed.

### Changed
- **OWASP coverage** — Security Engineer audits against OWASP Top 10 2025, API Security Top 10 (2023), and the LLM Top 10 (2025), with a Standards References section and a per-finding standards tag block (CVSS 4.0 / CWE / OWASP / WSTG v4.2 / ASVS 5.0.0). Verified against official sources.
- **Plugin metadata** — version 5.5.0; description and keywords advertise VAPT + OWASP coverage and anti-hallucination guardrails.

## [5.4.0] — 2026-06-24

Baseline release — project branding, workspace layout, and configuration established.
