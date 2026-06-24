# Phase 7: VAPT Execution

## Objective

The agent's default posture in this phase is read-only and static: nothing in this phase sends a payload to a running system unless Step 0's authorization gate has passed. With authorization, actually EXECUTE the pen-test (authorized DAST) against the live target -- boot the app, run real tooling against the endpoints discovered in Phase 1 `attack-surface.md`, capture request/response evidence, and mark each scenario PASS / FAIL / INCONCLUSIVE. Write all outputs to `Shipyard/security-engineer/vapt/`. Honor `security-testing-protocol.md` and `grounding-protocol.md` throughout: every active tool is gated behind Step 0, and no finding is promoted to Critical/High without a reproduction.

## Context Bridge

Read the prior phase outputs before executing anything:
- Phase 1 attack surface -- `Shipyard/security-engineer/threat-model/attack-surface.md` (the target inventory and entry points).
- Phase 6 pen-test plan -- `Shipyard/security-engineer/pen-test/test-plan.md` and `Shipyard/security-engineer/pen-test/attack-scenarios/` (the scenarios to execute).
- Orchestrator settings -- `Shipyard/.orchestrator/settings.md` for the `vapt_authorized` flag and the in-scope allowlist set by the orchestrator's Pentest (VAPT) mode.

The static findings from Phases 1-6 are LEADS, not confirmed vulnerabilities. This phase exists to confirm or refute them against the running target -- aggregate, do not re-analyze.

## Inputs

- Authorization state -- `Shipyard/.orchestrator/settings.md` (`vapt_authorized`, allowlist, RoE, testing window)
- Attack surface map -- `Shipyard/security-engineer/threat-model/attack-surface.md`
- Pen-test plan + scenarios -- `Shipyard/security-engineer/pen-test/test-plan.md`, `Shipyard/security-engineer/pen-test/attack-scenarios/<service>.md`
- API fuzzing config -- `Shipyard/security-engineer/pen-test/api-fuzzing-config.yml`
- Dependency manifests / IaC -- `package-lock.json`, `requirements.txt`, `go.mod`, Dockerfiles, Terraform (for static/passive tooling, always safe)
- The running target -- a local or authorized-staging deployment of the app (required only for active sub-phases)

## Workflow

### Step 0: Authorization Gate (HARD STOP)

Before ANY active action -- before a single payload, probe, or request reaches a running system -- verify the gate has passed:

1. Confirm explicit written authorization is recorded (`vapt_authorized: true` in `Shipyard/.orchestrator/settings.md`, set by the orchestrator's Pentest (VAPT) mode `AskUserQuestion`).
2. Confirm an in-scope target allowlist (hosts / URLs / API base) is recorded.
3. Confirm rules of engagement (RoE) and a testing window are recorded.
4. Write the authorization receipt to `Shipyard/.orchestrator/receipts/` (and mirror it to `vapt/authorization-receipt.json`) for the audit trail.

If authorization is absent or unconfirmed: run ONLY static/passive tooling (SAST, SCA, secret scanning, IaC scanning of local files) and STOP before any payload reaches a running system. Do not proceed to enumeration, active scanning, or exploitation.

Re-confirm scope before EVERY active action: verify each request target is on the allowlist; refuse out-of-scope, wildcard, or third-party assets; re-validate if a target redirects to a different host. STOP and escalate to a human if a test risks instability, touches out-of-scope systems, or touches real data.

### Methodology (recon → enum → scan → exploit/PoC → post-exploit → retest)

Map the engagement to the verified 7-phase methodology. The default posture column states what is safe without the gate versus what requires it:

| Sub-phase | Activity | Default posture |
|-----------|----------|-----------------|
| 1. Reconnaissance (passive) | Confirm scope FIRST; inventory langs/frameworks/manifests (`package-lock.json`, `requirements.txt`, `go.mod`), Dockerfiles, IaC; OSINT only on authorized assets. No payloads. Produce asset/attack-surface inventory. | Always safe |
| 2. Enumeration (active, light) | With authorization: port/service discovery on authorized hosts, web content discovery (`ffuf`, ZAP spider/AJAX), API endpoint enum from OpenAPI, tech fingerprint. Throttle; stay in scope. | Gated |
| 3. Vulnerability scanning | SAST (local) + SCA (local) + secret + IaC, then authorized DAST (ZAP baseline → full, nuclei safe templates, nikto, wapiti, schemathesis). Aggregate to SARIF, dedup, triage by exploitability -- scanner output is a CANDIDATE, not a confirmed vuln. | SAST/SCA safe; DAST gated |
| 4. Exploitation / PoC (gated) | Only with explicit written authorization + defined PoC scope. Least-invasive proof (sqlmap detection-only, single non-destructive payload, read a benign canary). Capture reproducible evidence. Stop at proof-of-impact. | Strictly gated |
| 5. Post-exploitation | Generally OUT OF SCOPE for an autonomous agent. Only if RoE explicitly permits: document demonstrated impact WITHOUT exfiltration/modification/persistence/pivoting. | Default skip |
| 6. (Reporting → Phase 8) | — | — |
| 7. Retest / verification | Re-run only confirmed-exploit scenarios after remediation; stamp Fixed / Still Vulnerable / Risk Accepted. Supports a "retest mode". | Gated |

### Tool Integration

The verified invocations and safe-by-default usage below. **Static/SCA = safe without a running target; DAST/fuzzing = active, require the gate (Step 0).** Quote every invocation verbatim; do not add flags the spec does not give.

| Tool | Category | Invocation (verbatim) | Safety |
|------|----------|------------------------|--------|
| semgrep | SAST | `semgrep scan --config auto --sarif --sarif-output semgrep.sarif --metrics=off .` (offline: `--config p/default`) | Read-only; never executes target. `auto` sends telemetry → pin ruleset + `--metrics=off` for private code. |
| CodeQL | SAST | `codeql database create ./codeql-db --language=javascript --source-root . --overwrite` then `codeql database analyze ./codeql-db codeql/javascript-queries:codeql-suites/javascript-security-extended.qls --format=sarifv2.1.0 --sarif-category=javascript --output=js-results.sarif` | Static; create-step may invoke build for compiled langs → sandbox. Pin `sarifv2.1.0`. Zero findings = verify DB quality. |
| bandit | SAST (Py) | `bandit -r ./src -ll -ii -f sarif -o bandit.sarif` | Pure static, no execution. Findings advisory. |
| gosec | SAST (Go) | `gosec -fmt=sarif -out=gosec.sarif ./...` | Static; may fetch module metadata → run where modules already downloaded for offline. |
| eslint-plugin-security | SAST (JS) | `npm i -D eslint eslint-plugin-security` (flat config), then `npx eslint . -f json -o eslint-security.json` | Lint is static; install runs npm → `npm ci --ignore-scripts` in sandbox. High FP on `detect-*`. |
| trivy (fs) | SCA | `trivy fs --scanners vuln --severity HIGH,CRITICAL --format sarif --output trivy-fs.sarif .` | Read-only; downloads vuln DB (`--offline-scan` for air-gapped). `--skip-dirs node_modules,vendor,.git`. |
| grype | SCA | `grype dir:. -o sarif > grype.sarif` (SBOM-first: `syft dir:. -o json > sbom.json && grype sbom:./sbom.json`) | Local DB, read-only. Pin/cache DB for offline. |
| npm audit | SCA | `npm audit --json > npm-audit.json` | Read-only. NEVER auto-run `npm audit fix --force` (breaking upgrades). Install untrusted repos with `--ignore-scripts`. |
| pip-audit | SCA | `pip-audit -r requirements.txt -f json -o pip-audit.json` (preferred `--require-hashes`) | Read-only. Prefer `--require-hashes`/`--no-deps`. Do not auto-apply fixes in CI. |
| osv-scanner | SCA | `osv-scanner scan source --recursive --format sarif --output osv.sarif .` | Parses lockfiles only; no execution; low FP. Air-gapped: `--offline-vulnerabilities --download-offline-databases`. |
| OWASP dependency-check | SCA | `dependency-check.sh --project "My App" --scan /path/to/project --format SARIF --out ./dc-report --nvdApiKey $NVD_API_KEY` | Read-only; needs NVD API key; cache datastore. CPE FPs → suppression XML. |
| gitleaks | Secrets | `gitleaks git . --report-format sarif --report-path leaks.sarif --redact` (non-git: `gitleaks dir .`) | Local read-only. `--redact` so secrets never logged. Verify + rotate, never exfiltrate. |
| trufflehog | Secrets | `trufflehog git file://path/to/repo --results=verified --json` | CAUTION: verification makes outbound API calls. Default `--no-verification` unless authorized. `--trust-local-git-config` only for trusted repos (CVE-2025-41390). |
| trivy (config) | IaC | `trivy config --scanners misconfig --severity HIGH,CRITICAL --format sarif --output trivy-config.sarif .` | Static, read-only. Successor to deprecated tfsec (AVD-* ids carry over). |
| hadolint | IaC | `hadolint Dockerfile --format sarif` (or `docker run --rm -i ghcr.io/hadolint/hadolint < Dockerfile`) | Static; never builds/runs image. Safe. |
| checkov | IaC | `checkov -d . --framework terraform --output sarif --output-file-path checkov.sarif` | Static; no infra provisioned. Scope with `--framework`. |
| OWASP ZAP (baseline) | DAST passive | `docker run -v $(pwd):/zap/wrk/:rw -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t https://app.localtest.me -r zap_report.html` | Baseline = spider + passive, NO attacks; safe. Use `ghcr.io/zaproxy/zaproxy:stable` (owasp/zap2docker-* deprecated). |
| OWASP ZAP (full) | DAST active | `zap-full-scan.py -t <target>` (or AF plan `zap.sh -cmd -autorun /zap/wrk/zap.yaml`) | ACTIVE — sends attack payloads. Authorized non-prod only. Exclude logout/destructive endpoints; throttle. |
| nuclei | DAST active | `nuclei -u https://app.localtest.me -t cves/ -t exposures/ -severity critical,high -rate-limit 50 -o nuclei.jsonl -jsonl` (first `nuclei -update-templates`) | ACTIVE. DoS/fuzzing templates off by default — do NOT force-enable on shared/prod. Throttle `-rate-limit/-c`. No `-as` on third-party infra. |
| nikto | DAST active | `nikto -h https://app.localtest.me -p 443 -ssl -Format json -output nikto.json` | ACTIVE + noisy; authorized local/staging only. Probes, does not exploit. |
| sqlmap | Exploit (gated) | Detection-only (safe): `sqlmap -u "http://app.localtest.me/page.php?id=1" -p id --batch --level=1 --risk=1` | EXPLOITATION TOOL. Only detection automated. `--dbs/--tables/--dump/--os-shell` require human sign-off; never on prod/real data. |
| wapiti | DAST active | `wapiti -u https://app.localtest.me/ --scope folder -x https://app.localtest.me/logout -f json -o wapiti-report.json` | ACTIVE; discovery-only (no exploit). Always `-x` the logout URL. Constrain `--scope`. |
| ffuf | Fuzzing | `ffuf -w /path/api-endpoints.txt -u https://api.localtest.me/v1/FUZZ -H 'Authorization: Bearer $TOKEN' -mc 200,201 -ac -rate 50 -c -of json -o ffuf.json` | ACTIVE; effectively DoS if unthrottled. Use `-ac` + `-rate`/lower `-t`. Authorized hosts only. |
| schemathesis | API fuzzing | `uvx schemathesis run https://api.localtest.me/openapi.json --header 'Authorization: Bearer $TOKEN' --report junit` (file: `schemathesis run openapi.yaml --url https://api.localtest.me`) | ACTIVE; can mutate state → point at test instance with disposable data. Narrow with `--checks`/`--exclude-checks`. |
| RESTler (alt) | API fuzzing (stateful) | `restler compile --api_spec openapi.json` then `restler fuzz --grammar_file Compile/grammar.py --dictionary_file Compile/dict.json --target_ip 127.0.0.1 --target_port 8080 --time_budget 1` | ACTIVE stateful; creates/modifies/deletes resources → authorized test deployment + throwaway data only. Bound with `--time_budget`. |

> tfsec / Terrascan are DEPRECATED/archived — use `trivy config` (or checkov). owasp/zap2docker-* images deprecated — use `ghcr.io/zaproxy/zaproxy:stable`.

### Evidence capture (grounding-enforced)

Each scenario records:
- the literal request sent,
- the literal response excerpt observed,
- the source→sink path (`file:line`) when applicable,
- a PASS / FAIL / INCONCLUSIVE verdict.

Reproduction is mandatory for any Critical/High finding. Treat scanner hits as candidates -- re-verify reachability and user-controlled input before promoting a candidate to a confirmed finding. Per `grounding-protocol.md`: no fabricated CVE/CVSS; tag claims `[verified]`/`[inferred]`/`[unverified]`; a finding with empty evidence is cut or downgraded.

## Output Deliverables

Write all outputs to `Shipyard/security-engineer/vapt/`:

| File | Contents |
|------|----------|
| `vapt/scan-output/*.sarif` | Raw aggregated tool output (one SARIF per tool, deduplicated) |
| `vapt/evidence/<scenario>.md` | Per-scenario request/response excerpt + source→sink path + verdict + reproduction |
| `vapt/results.md` | Scenario → PASS / FAIL / INCONCLUSIVE matrix |
| `vapt/authorization-receipt.json` | The authorization receipt (authorization reference, allowlist, RoE, window) written before any active tool ran |

## Validation

Before proceeding to Phase 8, verify:
- [ ] Authorization gate passed and the receipt was written BEFORE any active tool ran
- [ ] Every active target was on the allowlist
- [ ] No DoS / destructive / dump flags were used without explicit sign-off
- [ ] Every Critical/High finding has a reproduction
- [ ] Scanner candidates were re-verified for reachability before promotion
- [ ] Secrets were redacted

## Quality Bar

A confirmed finding = reachable code + reproduction + cited evidence. A scanner hit alone is a lead, not a finding. No fabricated CVE/CVSS (per `grounding-protocol.md`). If authorization was not confirmed, this phase produces static/passive output only and explicitly records that no active testing was performed -- that is the correct, safe outcome, not a failure.
