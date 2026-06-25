# Phase 3: Experiment Framework

## Objective

Build a rigorous A/B testing and experimentation infrastructure — experiment tracking (MLflow/W&B), statistical significance testing, metrics collection, and experiment lifecycle management — layered on top of the SHARED feature-flags/progressive-rollout machinery.

## Ownership Boundary — EXTEND, do not re-own the rollout primitives

The GENERIC progressive-rollout machinery lives in **software-engineer's feature-flags layer at `libs/shared/feature-flags/`** and is the single source of truth for:

- **Deterministic hash bucketing** (stable variant assignment via the canonical input `hash("{flagKey}:{stableId}") % 100` — colon delimiter, camelCase `flagKey` and `stableId`; do NOT reimplement a second hashing scheme; a divergent hash splits the same user into different buckets across the stack).
- **Percentage / ring rollout** (gradual %, internal/canary rings, allowlist/blocklist targeting).
- **Guardrail auto-rollback** (a flag flips to its SAFE DEFAULT fail-static when a guardrail breaches).
- **Experiment registry** entries in `config/feature-flags.yaml` (`{ key, type, owner, default, created, removal_by }`) read through the OpenFeature client with an ALWAYS-present env/config fallback.

This skill **EXTENDS** that layer for **ML experiment DESIGN** only: variant definitions, guardrail-metric thresholds, holdout populations, and statistical evaluation. You register the experiment as a flag and consume the shared client's deterministic assignment — you do not own bucketing, ring rollout, or the rollback mechanism.

> **Conflict-resolution note:** authority over the rollout primitives and `config/feature-flags.yaml` is software-engineer's (feature-flags layer); data-scientist contributes ML-experiment flag entries via that owner. See followups — `conflict-resolution.md` is a shared file this skill does not own and should record this ownership.

## Context Bridge

Read Phase 2 optimization results from `llm-optimization/` for features needing A/B validation. Read Phase 1 audit from `analysis/system-audit.md` for baseline metrics. Read `config/feature-flags.yaml` and `libs/shared/feature-flags/` for the shared client API, hash-bucketing contract, and existing flag entries before designing assignment.

## Workflow

### Step 1: Experiment Tracking Setup

Select and configure a tracking platform:

| Platform | Best For | Key Features |
|----------|----------|--------------|
| **MLflow** | Self-hosted, open-source | Experiment logging, model registry, artifacts |
| **Weights & Biases** | ML-heavy teams | Hyperparameter sweeps, collaborative dashboards |
| **OpenFeature + custom metrics** | Feature-flag-first | Targeting, gradual rollout, kill switch via the SHARED feature-flags layer |
| **In-house** | LLM apps with custom metrics | Full control, prompt versioning |

> Assignment/targeting/rollout/kill-switch are NOT a tracking-platform concern here — they are provided by the shared `libs/shared/feature-flags/` layer (Step 2). The tracking platform records outcomes and metadata only.

Produce `experiments/framework/tracking-config.md` with platform choice, metadata schema, and integration points.

### Step 2: Variant Assignment via the Shared Feature-Flags Layer (EXTEND)

Do NOT build experiment assignment from scratch. **Consume** software-engineer's shared layer at `libs/shared/feature-flags/` and register the ML experiment as a flag:

1. **Register the experiment flag** in `config/feature-flags.yaml` as a `{ key, type, owner, default, created, removal_by }` entry. `type` is a multivariate/string flag whose values are the experiment variants (`control`, `variant_a`, …); `default` is the SAFE control variant returned fail-static on provider error; `owner` is the data-scientist running the study; `removal_by` is the planned experiment end/cleanup date.
2. **Resolve the variant** at request time through the shared OpenFeature client — it performs the deterministic `hash("{flagKey}:{stableId}") % 100` bucketing (colon delimiter, camelCase `flagKey` and `stableId`), so the same unit (user/session/account) stays in the same variant across sessions and services. Pass the `stableId` + targeting context; consume the returned variant. Do not hash independently.
3. **Holdouts & targeting** reuse the shared layer's percentage/ring controls: a global holdout is a reserved bucket excluded from all variants; internal/canary rings and allowlist/blocklist targeting come from the shared client's targeting context — you configure the experiment's holdout %, not a new mechanism.
4. **Kill switch / guardrail rollback** is the shared layer's auto-rollback: when a guardrail metric (Step 4) breaches, the flag flips to its SAFE DEFAULT (control) fail-static. This skill DEFINES the guardrail thresholds; the shared layer ENFORCES the flip. Wire your guardrail evaluator to the shared rollback hook — do not write a parallel kill switch.
5. **Security:** assignment context and experiment logs follow `security-defaults.md` — no PII or secrets in the targeting context, flag values, or experiment event payloads; anonymize the unit id (hash/pseudonymous) before it enters the flag client or tracking platform.

Produce `experiments/framework/flag-integration.md` documenting: the registered `config/feature-flags.yaml` entry, the shared-client call site for variant resolution, holdout configuration, the guardrail→rollback wiring, and an explicit statement that bucketing/ring-rollout/rollback primitives are consumed from `libs/shared/feature-flags/` (not reimplemented).

### Step 3: Statistical Significance Testing

Define methodology for evaluating experiments:

- **Sample size calculator:** Required n per variant based on MDE, baseline rate, power (0.8), alpha (0.05)
- **Sequential testing:** Alpha-spending functions (O'Brien-Fleming) for safe peeking
- **Multiple comparison correction:** Bonferroni or Benjamini-Hochberg for multi-metric tests
- **Bayesian alternative:** Posterior probability for low-traffic features

Produce `experiments/framework/significance-calculator.py` with z-test, t-test, proportion test, and correction utilities.

### Step 4: Metrics Collection

Design three metric tiers for every experiment:

- **Primary:** The metric the experiment targets (e.g., quality score, conversion rate)
- **Guardrail:** Metrics that must NOT regress (e.g., error rate, p95 latency) with thresholds that trip the SHARED layer's auto-rollback (flag flips to SAFE control). Use the canonical metric names from `observability-contract.md` for the operational guardrails — error rate from `http_requests_total` (`5xx/total`), latency from `http_request_duration_seconds` — so the experiment monitor queries the same series the dashboards emit; do not invent new metric names.
- **Diagnostic:** Debugging metrics (e.g., token count, cache hit rate)

Produce `experiments/framework/metrics-schema.md` with event schema for experiment exposure, LLM request/response, and user feedback events. Exposure/feedback events carry no PII or secrets (`security-defaults.md`); the exposure event references the shared flag key + resolved variant, not a re-derived bucket.

### Step 5: Experiment Lifecycle Management

Define lifecycle stages and registry:

```
Draft -> Review -> Running -> Analysis -> Concluded (Ship / No-Ship / Iterate)
```

Registry fields: Experiment ID, **shared flag key** (the `config/feature-flags.yaml` entry resolved through `libs/shared/feature-flags/`), Hypothesis ("If [change], then [metric] will [direction] by [MDE]"), primary metric, guardrail metrics with rollback thresholds, holdout %, required sample size (from power analysis), start/end dates (`removal_by` matches the flag's), status, and decision with rationale.

This `experiments/experiment-registry.md` is the ML experiment-DESIGN registry (hypotheses, metrics, decisions). It does NOT replace `config/feature-flags.yaml` — that remains the runtime flag registry owned by the shared feature-flags layer. Cross-reference by flag key; never fork a second runtime registry.

Auto-rollback: guardrail breach is detected by the experiment monitor and trips the SHARED layer's auto-rollback — the flag flips to its SAFE DEFAULT (control) fail-static, and the team is alerted. This skill defines the thresholds and wires the breach signal; the feature-flags layer performs the flip.

Produce `experiments/experiment-registry.md`.

## Output Files

- `experiments/framework/tracking-config.md`
- `experiments/framework/flag-integration.md`
- `experiments/framework/metrics-schema.md`
- `experiments/framework/significance-calculator.py`
- `experiments/experiment-registry.md`

## Validation

Before proceeding to Phase 4, verify:
- [ ] Experiment tracking platform selected and configured
- [ ] Variant assignment CONSUMES `libs/shared/feature-flags/` deterministic bucketing — no reimplemented hashing; experiment registered as a `config/feature-flags.yaml` entry
- [ ] Holdouts/targeting use the shared layer's percentage/ring controls; guardrail breach wired to the shared auto-rollback (no parallel kill switch)
- [ ] Statistical methodology documented (sample size, significance, multiple comparisons)
- [ ] Metrics schema includes primary, guardrail, and diagnostic metrics; operational guardrails use `observability-contract.md` names
- [ ] Experiment registry includes shared flag key, hypothesis, power analysis, and decision log; cross-references (does not fork) the runtime flag registry
- [ ] Auto-rollback thresholds defined for guardrail metrics (enforced by the shared layer)
- [ ] `security-defaults checklist passes` — no PII/secrets in targeting context, flag values, exposure/feedback events; unit id pseudonymized

> **GATE: Present experiment framework design. Wait for user approval before proceeding.**

## Quality Bar

Every experiment must have a null hypothesis, power analysis, and guardrail metrics with auto-rollback, and MUST consume the shared feature-flags layer for assignment rather than reimplementing bucketing/rollout. `security-defaults checklist passes`. "We ran the experiment for a week" is not acceptable — "We ran for 14 days, collecting 12,400 samples per variant (required: 11,200 at 80% power, 5% MDE), assignment via shared flag `exp-prompt-v2` (deterministic hash bucketing), guardrail error-rate breach auto-flips to control" is acceptable.
