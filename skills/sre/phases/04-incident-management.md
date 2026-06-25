# Phase 4: Incident Management

## Objective

Build the organizational machinery to detect, respond to, and learn from incidents. The tools exist (from DevOps) — this phase wires them into a human process. Additionally, write runbooks that an on-call engineer woken at 3 AM can follow without thinking.

## Context Bridge

- Read Phase 2 SLOs and alerting rules from `slo/` — what triggers incidents
- Read Phase 3 chaos results from `chaos/` — known failure modes
- Read architecture docs for service topology

## Inputs

- Phase 2 SLOs and alerting rules — what triggers incidents
- Phase 3 chaos results — known failure modes
- Organization structure — team composition, time zones
- Existing tooling — PagerDuty/OpsGenie, Slack, Statuspage

## Workflow

### Step 1: Generate Severity Classification

Write `incidents/severity-classification.md`:

```markdown
# Incident Severity Classification

## SEV1 — Critical
- **Definition:** Complete service outage OR data loss/corruption OR security breach
- **User impact:** All users affected, core functionality unavailable
- **Response time:** Immediate (within 5 minutes)
- **Communication:** Statuspage updated within 10 minutes, executive notification
- **War room:** Mandatory, video call opened immediately
- **Examples:** Database down, authentication service unreachable, payment processing halted

## SEV2 — High
- **Definition:** Significant degradation OR partial outage of critical feature
- **User impact:** Large subset of users affected, workaround may exist
- **Response time:** Within 15 minutes
- **Communication:** Statuspage updated within 30 minutes
- **War room:** Opened if not resolved within 30 minutes
- **Examples:** Elevated error rate (>1%), latency 5x normal, one region degraded

## SEV3 — Medium
- **Definition:** Minor feature degradation OR non-critical service issue
- **User impact:** Small subset of users, non-critical functionality
- **Response time:** Within 1 hour (business hours)
- **Communication:** Internal Slack notification
- **War room:** Not required
- **Examples:** Admin panel slow, email notifications delayed, search results stale

## SEV4 — Low
- **Definition:** Cosmetic issue OR minor inconvenience OR proactive risk
- **User impact:** Minimal to none
- **Response time:** Next business day
- **Communication:** Ticket created
- **War room:** Not required
- **Examples:** Error budget warning, non-critical dependency degraded, log volume anomaly
```

### Step 2: Generate On-Call Rotation

Write `incidents/on-call-rotation.yaml`:

```yaml
# PagerDuty / OpsGenie rotation configuration
rotations:
  - name: primary-on-call
    type: weekly
    participants:
      - team: platform-engineering
    handoff:
      day: Monday
      time: "10:00"
      timezone: "America/New_York"
    restrictions:
      - type: business_hours
        start: "09:00"
        end: "18:00"

  - name: secondary-on-call
    type: weekly
    participants:
      - team: platform-engineering
    handoff:
      day: Monday
      time: "10:00"
      timezone: "America/New_York"
    description: >
      Secondary is the previous week's primary.
      Provides continuity and mentorship for new on-call.

overrides:
  holiday_coverage:
    description: "Volunteer-based with 2x comp time"
    advance_notice_days: 14

on_call_expectations:
  acknowledge_within: 5m
  response_within: 15m
  laptop_required: true
  escalation_if_no_ack: 10m
  compensation: "Per company on-call policy"
```

### Step 3: Generate Escalation Policy

Write `incidents/escalation-policy.md` defining the escalation chain for each severity level, including timeout-based auto-escalation.

### Step 4: Generate Communication Templates

Write templates in `incidents/communication-templates/` with pre-written content for:

- **`statuspage-investigating.md`** — Initial statuspage update when investigating
- **`statuspage-identified.md`** — Update when root cause identified
- **`statuspage-resolved.md`** — Resolution notification
- **`internal-slack-alert.md`** — Internal team notification
- **`customer-notification.md`** — Customer-facing email notification

Each template includes placeholders and instructions for what information to fill in.

### Step 5: Generate War Room Procedures

Write `incidents/war-room-checklist.md`:

```markdown
# War Room Procedures

## Opening a War Room
1. Create dedicated Slack channel: #incident-YYYY-MM-DD-<short-description>
2. Start video call (link in channel topic)
3. Assign roles:
   - **Incident Commander (IC):** Coordinates response, makes decisions
   - **Communications Lead:** Updates statuspage, stakeholders
   - **Technical Lead:** Drives debugging, delegates investigation
   - **Scribe:** Documents timeline, actions, decisions in real-time
4. Pin the incident channel with: severity, start time, user impact, assigned roles

## During the War Room
- IC runs the call. Others speak when addressed or when they have critical info.
- Every 15 minutes: IC summarizes current status and next steps
- Communications Lead updates statuspage every 30 minutes minimum
- Scribe maintains running timeline in pinned thread
- NO changes to production without IC approval
- If current IC needs to hand off, explicit verbal handoff required

## Closing a War Room
1. Confirm service restored and metrics stable for 15 minutes
2. Update statuspage to Resolved
3. Send internal all-clear notification
4. Schedule postmortem within 48 hours
5. Create follow-up tickets for all identified action items
6. Archive incident channel (do not delete)
```

### Step 6: Generate Disaster Recovery Artifacts

Write the following disaster recovery documents:

**`disaster-recovery/rto-rpo-definitions.md`:**

```markdown
# RTO/RPO Definitions

| Service | RPO (max data loss) | RTO (max downtime) | Justification |
|---------|--------------------|--------------------|---------------|
| Primary database | 1 minute | 15 minutes | Financial transactions, point-in-time recovery |
| User sessions | 0 (replicated) | 5 minutes | Active user impact, Redis replication |
| File storage | 24 hours | 1 hour | S3 cross-region replication lag acceptable |
| Search index | 4 hours | 30 minutes | Can rebuild from primary database |
| Message queue | 0 (replicated) | 10 minutes | In-flight messages must not be lost |
| Analytics data | 24 hours | 4 hours | Non-critical, can backfill |

## Definitions
- **RPO (Recovery Point Objective):** Maximum acceptable data loss measured in time.
- **RTO (Recovery Time Objective):** Maximum acceptable downtime.
```

**`disaster-recovery/failover-playbook.md`** — Step-by-step procedures for:
- Database failover (primary to replica promotion)
- Region failover (Route53/CloudFront failover, DNS TTL considerations)
- Complete cluster rebuild from infrastructure-as-code
- Partial service recovery (bring up critical path first)
- Verification steps after each failover action
- Estimated time for each step

**`disaster-recovery/backup-verification.md`** — Including:
- Automated backup verification procedures (scheduled restores to test environment)
- Backup integrity checksums
- Backup restoration time benchmarks
- Quarterly full-restoration drill procedure
- Backup monitoring alerts (failed backups, backup age)

**`disaster-recovery/recovery-procedures.md`** — Including:
- Data recovery from backups
- State reconstruction procedures
- Cache warming procedures after recovery
- Post-recovery validation checklist
- Communication procedures during recovery

### Step 7: Generate Operational Runbooks

For each service identified in the architecture, generate a directory under `docs/runbooks/<service-name>/` at the project root. Each runbook MUST follow this template:

```markdown
# Runbook: <Alert Name>

## Alert Details
- **Severity:** <SEV level>
- **Alert rule:** <Prometheus/Datadog alert name>
- **Fires when:** <human-readable condition>
- **SLO impact:** <which SLO this affects and burn rate implication>

## Triage (First 5 Minutes)

### 1. Assess Scope
<Exact commands to determine impact scope>

```bash
# Check error rate across all instances.
# Metric names + labels are EXACTLY from observability-contract.md — error is status_class="5xx",
# NOT status=~"5.." (no such label exists; that query returns empty and lies "0% errors").
kubectl exec -n monitoring prometheus-0 -- promtool query instant \
  'sum(rate(http_requests_total{status_class="5xx",service="<service>"}[5m])) / sum(rate(http_requests_total{service="<service>"}[5m]))'

# Check affected pods
kubectl get pods -n production -l app=<service> -o wide

# Check recent deployments (was this caused by a deploy?)
kubectl rollout history deployment/<service> -n production
```

### 2. Decision Tree

```
Is error rate > 10%?
+-- YES -> Go to "Emergency Mitigation"  (kill-switch FIRST, then rollback)
+-- NO
    +-- Is it correlated with a recent deployment?
    |   +-- YES -> Go to "Emergency Mitigation" then "Rollback Procedure"
    |   +-- NO
    |       +-- Is a downstream dependency unhealthy?
    |       |   +-- YES -> Go to "Dependency Failure"
    |       |   +-- NO -> Go to "Deep Investigation"
```

## Emergency Mitigation

Stop the bleeding BEFORE root cause is known and BEFORE rolling back — flipping a flag is seconds and reversible; a rollback is minutes and re-runs deploy machinery. Use the **ops kill-switch flag** from the registry to shed the failing path first, THEN escalate to rollback if the flag does not stabilize.

### 1. Flip the ops kill-switch (FIRST — read the key from the registry)
```bash
# Kill-switch keys are declared in config/feature-flags.yaml — do NOT invent a key.
# Find the ops kill-switch for the affected feature/path:
grep -A6 'kill-switch\|ops_' config/feature-flags.yaml   # confirm key, type, owner, default

# Flip it OFF via the OpenFeature client / provider CLI (env/config fallback always works):
#   - registry/provider:  set <ops.kill_switch.key> = false
#   - or env fallback (always present):  FEATURE_<KEY>=false  (per libs/shared/feature-flags/)
# Verify the path is shed:
kubectl exec -n monitoring prometheus-0 -- promtool query instant \
  'sum(rate(http_requests_total{status_class="5xx",route="<failing-route>"}[1m]))'
```
- Kill switches fail STATIC to the registry `default` — verify the `default` for the key is the SAFE (off) value so a provider outage does not re-enable the failing path.
- If the kill-switch stabilizes error rate below the SLO burn threshold → incident mitigated; proceed to Deep Investigation for root cause, no rollback needed.
- If NO kill-switch exists for this path, that is a gap → file a follow-up to add one to `config/feature-flags.yaml`, and proceed to Rollback.

### 2. If the kill-switch does not stabilize → Rollback Procedure (below)
<Other immediate levers: shed load at the gateway, scale out, drain a bad AZ — before rollback>

## Rollback Procedure
```bash
# Identify the previous revision
kubectl rollout history deployment/<service> -n production

# Rollback to previous revision
kubectl rollout undo deployment/<service> -n production

# Verify rollback
kubectl rollout status deployment/<service> -n production --timeout=120s
```

## Dependency Failure
<Steps to isolate and work around failed dependency>

## Deep Investigation
<Systematic debugging: logs, traces, recent changes, resource utilization>

## Resolution Verification
- [ ] Error rate returned to baseline
- [ ] SLO burn rate normalized
- [ ] No error log anomalies
- [ ] Downstream services healthy
- [ ] Update incident channel with resolution

## Post-Incident
- [ ] Create postmortem document
- [ ] File follow-up tickets
- [ ] Update this runbook if new information discovered
```

Generate at minimum these runbooks per service:
- `high-error-rate.md` — elevated 5xx responses (`http_requests_total{status_class="5xx"}`)
- `high-latency.md` — p99 latency exceeding the budgeted threshold (`http_request_duration_seconds_bucket`)
- `out-of-memory.md` — OOMKilled pods, memory pressure
- `dependency-down.md` — downstream service or external API unreachable (pool USE instruments)
- `feature-kill-switch.md` — **the feature-kill-switch runbook type** (see template below)

Add additional runbooks for service-specific failure modes discovered during chaos engineering (Phase 3) or identified in the architecture (e.g., `queue-consumer-lag.md`, `database-replication-lag.md`, `certificate-expiry.md`).

#### Runbook type: `feature-kill-switch.md`

A dedicated runbook for the kill-switch lever itself, so an on-call engineer can shed a bad feature WITHOUT a rollback. It enumerates every ops kill-switch key from the registry and exactly what each sheds.

```markdown
# Runbook: Feature Kill Switches

## When to use
A specific feature/code path is failing (error spike, latency, bad dependency) and you
want to disable it in seconds — reversible, no redeploy. Use BEFORE rollback.

## Available ops kill-switches (source: config/feature-flags.yaml)
| Flag key | Type | Owner | Safe default | What flipping OFF sheds |
|----------|------|-------|--------------|--------------------------|
| `ops.checkout.kill_switch` | boolean | sre | false (off) | Disables checkout flow → users see "temporarily unavailable", no 5xx |
| `ops.recommendations.kill_switch` | boolean | sre | false | Drops the recommendations call → page renders without the panel |
<!-- one row per kill-switch key actually present in config/feature-flags.yaml -->

## How to flip (provider + always-present env/config fallback)
```bash
grep -A6 'kill_switch' config/feature-flags.yaml        # confirm the exact key + default
# Flip via provider/registry, OR the env fallback that is always available:
#   FEATURE_OPS_CHECKOUT_KILL_SWITCH=false   (per libs/shared/feature-flags/)
```

## Verify it took effect
```bash
kubectl exec -n monitoring prometheus-0 -- promtool query instant \
  'sum(rate(http_requests_total{status_class="5xx",route="<route>"}[1m]))'   # should drop
```

## Aftercare
- [ ] Announce the kill-switch flip in the incident channel (it is a config change)
- [ ] Confirm the flag's `default` in config/feature-flags.yaml is the SAFE value (fail-static on provider outage)
- [ ] File the re-enable ticket; respect the flag's `removal_by` date
```

> Every key listed in this runbook MUST exist in `config/feature-flags.yaml` — `scripts/check-kill-switch.sh` (Production-Ready Gate) fails the build if a runbook references a kill-switch key absent from the registry.

## Validation

Before proceeding to Phase 5, verify:
- [ ] Severity classification has concrete examples for each level
- [ ] On-call rotation covers 24/7 with escalation policy
- [ ] Communication templates are pre-written (not "write a statuspage update")
- [ ] War room procedures define explicit roles (IC, comms, tech lead, scribe)
- [ ] RTO/RPO defined for every stateful component
- [ ] Failover playbook reviewed against actual infrastructure topology
- [ ] Every alert has a corresponding runbook with exact commands
- [ ] Runbooks include decision trees, not just prose
- [ ] All runbook commands use real metric names and pod labels from this system — error queries use `status_class="5xx"` (contract label), never `status=~"5.."`
- [ ] Emergency Mitigation flips an ops kill-switch key (read from `config/feature-flags.yaml`) BEFORE the rollback procedure
- [ ] `feature-kill-switch.md` runbook exists and every key it lists is present in `config/feature-flags.yaml` (`scripts/check-kill-switch.sh` passes)
- [ ] Runbooks that do not specify who to escalate to are rejected

## Quality Bar

Runbooks are not generic templates. They must use real pod labels, real metric names, and real service names from THIS system. A runbook that says "check the logs" without specifying WHICH logs, WHERE, or what to look for is rejected. Decision trees, not paragraphs.
