# Security Testing Protocol — Authorization, Scope & Safe-by-Default

**Core principle: Authorization first, always. Never run any active or dynamic test (DAST, fuzzing, exploitation) without explicit, written authorization and a documented scope. No authorization → passive/static only, and stop before anything that sends a payload to a running system.**

Active security testing sends real payloads to running systems. Done without authorization or scope, it is indistinguishable from an attack — legally, operationally, and ethically. This protocol makes read-only and static analysis the default posture, and gates every active action behind an explicit authorization check.

---

## Authorization & Scope Gate (BEFORE any active testing)

- **Mandatory gate before the FIRST active action.** Confirm explicit written authorization, an in-scope target allowlist (hosts/domains/IPs/API base URLs), rules of engagement (RoE), and a testing window. Do not send a single payload until all four are recorded.
- **Implementation hook.** The gate is an `AskUserQuestion` with an explicit "I authorize active testing against these targets" confirmation plus a scope list. Record the authorization in a receipt for an audit trail (`Shipyard/.orchestrator/receipts/` per `receipt-protocol.md`).
- **No authorization → passive/static only.** If authorization cannot be confirmed, run ONLY passive/static tooling (SAST, SCA, secret/IaC scanning of local files) and halt before any payload.
- **Re-confirm scope before EVERY active action.** Maintain the allowlist and verify each request target is on it. Refuse out-of-scope, wildcard, or third-party assets. Re-validate if a target redirects to a different host.

---

## Authorized / Local Targets Only

- Prefer `localhost`, `127.0.0.1`, a dedicated lab, `*.localtest.me`, or an explicitly authorized staging environment.
- Never point active scanners at production, shared SaaS, or any system the user does not own or have written permission to test.

---

## No DoS / Destructive Payloads / Production Data

| Rule | Concrete enforcement |
|------|----------------------|
| No denial-of-service | No flood/stress payloads; no unbounded high-concurrency fuzzing. Throttle every active tool (`nuclei -rate-limit`, `ffuf -rate/-t`, ZAP/wapiti scope+delay). Keep DoS-prone nuclei/sqlmap templates + high `--risk/--level` disabled unless explicitly authorized. |
| No destructive actions | Nothing that deletes/modifies/encrypts/corrupts data or state. No `sqlmap --dump`/`--os-shell`, no persistence, no lateral movement. Exclude logout + state-destroying endpoints (`wapiti -x`). Stay at proof-of-impact, not weaponization. |
| No production data | Synthetic/disposable accounts + data only. Never exfiltrate/copy/store/transmit real customer or production data. Do not exercise flows that send real emails/payments/notifications. |
| Supply-chain safety while tooling | `--ignore-scripts` on dependency installs in untrusted repos; pin security GitHub Actions to known-good commit SHAs; prefer cached/offline vuln DBs for reproducibility. |
| Minimize + stay reversible | Choose the least-invasive technique that proves the point; run in agreed windows; log all actions for auditability; clean up test artifacts. STOP and escalate to a human if a test risks instability, touches out-of-scope systems, or touches real data. |

---

## Handle Secrets Responsibly

- When secret scanners surface credentials: redact (`gitleaks --redact`), never log/transmit externally, report for rotation.
- Default `trufflehog --no-verification` unless live verification against the credential's service is explicitly authorized (verification makes outbound calls).

---

## Responsible Disclosure

- Report findings only to the authorized owner via agreed channels. Do not publicly disclose, sell, or share vulnerabilities or recovered secrets. Follow any embargo/disclosure timeline in the RoE / bug-bounty policy.

---

## Evidence-Backed Findings Only

- **Reproduction is the citation for exploitability.** A finding's evidence for being exploitable is a concrete runnable reproduction (input → vulnerable sink → observable effect), not prose.
- **Critical/High require a reproduction.** Findings rated Critical/High MUST carry a reproduction (specific input/request, the path it travels, the observable effect). No reproduction → downgrade severity, label unconfirmed.
- **Two clearly labeled buckets:**
  - **Confirmed** — reachable code + reproduction + cited evidence.
  - **Needs-Verification** — a lead only. A Needs-Verification item never carries Critical/High or a CVE/CVSS as if confirmed.
- **Re-evaluate scanner output in context.** SAST/SCA produce many false positives: is the vulnerable function actually called? is the path reachable in this config? is the input user-controlled? Adjust severity with written justification + cited code.

---

## CVSS Discipline

- Use CVSS **4.0** (FIRST, Nov 2023) for new findings; retain the ability to ingest/interpret **3.1** — provide both scores where possible.
- Never fabricate a score: retrieve the official advisory score (cite it) or compute from the vector and show each metric.
- Do NOT directly compare scores across CVSS versions; never rely on the base score alone — pair with EPSS and CISA KEV.
- Every finding maps to the verified standards: CWE id, OWASP category id, WSTG test id, ASVS requirement id + level.

---

## Decision Flow

```
About to send a payload / request to a RUNNING system?
  → Authorization + in-scope target confirmed?  NO → STOP. Static/passive only.
                                                 YES ↓
  → Target is localhost/lab/authorized-staging?  NO → STOP. Refuse out-of-scope.
                                                 YES ↓
  → Payload is non-destructive + throttled + no real data?  NO → STOP. Reduce to safe variant.
                                                 YES → Proceed; capture evidence; log the action.
```

---

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| Running ZAP full/active scan before the authorization gate | Run `zap-baseline.py` (passive) first, gate the active scan |
| `sqlmap --dump` to "prove" SQLi | Detection-only (`--level=1 --risk=1`); the repro is enough |
| Pointing nuclei at a prod URL with auto-scan | Scoped authorized host + `-rate-limit`, DoS templates off |
| Logging a recovered secret into the report | Redact + report for rotation |

---

## Key Principle

**The agent's default posture is read-only and static. Active testing is a deliberate, authorized, throttled, evidence-capturing exception — never the default.**
