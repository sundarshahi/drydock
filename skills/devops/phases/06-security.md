# Phase 6 — Security

Generate `infrastructure/security/`:

```
security/
├── scanning/
│   ├── sast-config.yml         # Semgrep/CodeQL rules
│   ├── dependency-scan.yml     # Snyk/Trivy config
│   ├── container-scan.yml      # Image vulnerability scanning
│   └── iac-scan.yml            # tfsec/checkov config
├── secrets/
│   ├── secrets-policy.md       # Secrets management standard
│   └── external-secrets.yaml   # External Secrets Operator config
├── network/
│   ├── waf-rules.tf            # WAF rule sets
│   ├── security-groups.tf      # Network access control
│   └── tls-config.md           # TLS 1.3 minimum, cert management
├── iam/
│   ├── service-roles.tf        # Per-service IAM roles
│   ├── ci-cd-roles.tf          # Pipeline execution roles
│   └── break-glass.md          # Emergency access procedures
├── compliance/
│   ├── checklist.md            # SOC2/HIPAA/GDPR checklist
│   └── data-classification.md  # PII/PHI data handling
└── incident-response/
    ├── playbook.md             # Incident response process
    └── post-mortem-template.md # Blameless post-mortem format
```

### Security Standards
- **Zero trust** — Verify every request, assume breach
- **Least privilege** — Minimal permissions, time-bounded access
- **Encryption** — At rest (KMS) and in transit (TLS 1.3)
- **Secret rotation** — Automated rotation via Secrets Manager
- **Container security** — No root, read-only filesystem, no capabilities
- **Supply chain** — Pin dependency versions, verify checksums, SBOM generation
- **Audit logging** — All admin actions logged, immutable audit trail (cross-ref `security-defaults.md` → "Security event logging")

### CI/CD & Supply-Chain Platform Security (OWASP Top 10 CI/CD Security Risks)

The pipeline itself is production infrastructure with credentials and deploy authority — secure it to the same bar as the app. Each control below is a reviewer-verifiable assertion, not advice.

- **Dependency confusion (CICD-SEC-3)** — Scope/namespace every internal package and lock the registry source with NO implicit public fallback. npm: a scoped `@org/` registry pinned in `.npmrc` (no public-registry fallback for the scope); pip: `--index-url` to the private index, never `--extra-index-url` (which races public PyPI). Verify package provenance (publish attestation / signed index) before install. Cross-ref `security-defaults.md` → "Dependency pinning, lockfile, post-add SCA".
- **Pipeline execution safety / PPE (CICD-SEC-4)** — Never interpolate `${{ github.event.* }}` (title, body, branch, label, comment) into a `run:` step — pass it via `env:` and reference `"$VAR"`. Restrict `pull_request_target` and `workflow_run` triggers (they run with repo secrets against attacker-controlled code). Keep `GITHUB_TOKEN` least-privilege (`permissions: contents: read` by default, widen per-job only). Require review for any workflow-file (`.github/workflows/**`) change. NEVER expose prod secrets / environments to fork PRs.
- **CI/CD identity & access (CICD-SEC-2)** — Inventory every PAT, deploy/SSH key, and service account with SCM/CI access. Enforce SSO + MFA on the SCM and CI platform. Prefer short-lived OIDC over long-lived secrets everywhere a token is needed. Deprovision identities on offboarding. No shared ambient admin tokens. Cross-ref `security-defaults.md` → "Authentication & credential-handling defaults" and "Session & self-contained-token lifecycle".
- **Runner isolation (CICD-SEC-5)** — Prefer ephemeral/hosted runners: one job per VM, destroyed after the job. If self-hosted runners are unavoidable, isolate them by trust level and NEVER run untrusted (fork-PR) code on a runner that holds prod credentials.
- **CI/CD audit & detection (CICD-SEC-10)** — Forward SCM, CI, and artifact-registry audit logs to the SIEM. Alert on workflow-file changes, new/changed secrets, and permission changes. Cross-ref `security-defaults.md` → "Security event logging".
- **Source-track integrity (SLSA v1.2 source track)** — Require signed commits, protected branches that block force-push AND branch deletion, and a verified, tamper-evident change history. The generated `scripts/setup-branch-protection.sh` MUST enforce these (signed-commit requirement + `allow_force_pushes: false` + `allow_deletions: false`), not just configure required status checks.
- **IaC + signed SBOM gates** — `tfsec`/`checkov` runs as an actual CI job that FAILS the pipeline on HIGH severity (not advisory). The released SBOM is SIGNED/ATTESTED — `cosign attest` (in-toto predicate) keyed to the image **digest**, not merely attached as a release file. Verify the attestation in the pre-deploy gate.

### CI Security Gates (Fail Pipeline on)
- Critical/High CVEs in dependencies
- Secrets detected in code (gitleaks/trufflehog)
- Terraform misconfigurations (tfsec/checkov severity: HIGH — an actual job, not advisory)
- Container image CVEs (Trivy severity: CRITICAL)
- SAST findings (Semgrep severity: ERROR)
- `${{ github.event.* }}` interpolated into a `run:` step (PPE / CICD-SEC-4)
- Unpinned third-party action (not a full 40-char commit SHA) or a `GITHUB_TOKEN` widened beyond least-privilege
- Unverifiable supply-chain attestation at the pre-deploy gate — missing/failed SLSA provenance, cosign signature, or **signed SBOM attestation** (`cosign attest` keyed to the digest)
