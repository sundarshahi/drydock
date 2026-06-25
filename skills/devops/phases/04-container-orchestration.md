# Phase 4 — Container Orchestration

Generate container artifacts at project root and `infrastructure/`:

### Docker
```
services/<service-name>/
└── Dockerfile                  # Per-service, multi-stage (co-located with service code)

docker-compose.yml              # Local development (project root)
docker-compose.test.yml         # Integration test environment (project root)
.dockerignore                   # (project root)
```

Dockerfile standards:
- Multi-stage builds (builder -> runtime)
- Non-root user (`USER appuser`)
- Minimal base images (distroless/alpine)
- Layer caching optimization (dependencies before source)
- Health check instruction (`HEALTHCHECK`)
- No secrets in image layers
- `.dockerignore` excluding `.git`, `node_modules`, `__pycache__`, etc.

### Kubernetes
Generate Kubernetes manifests at `infrastructure/kubernetes/` (or `paths.kubernetes` from config):

```
infrastructure/kubernetes/
├── base/
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   └── networkpolicy.yaml
├── overlays/
│   ├── dev/
│   ├── staging/
│   └── prod/
└── kustomization.yaml

infrastructure/helm/                       # (if requested)
└── <service>/
    ├── Chart.yaml
    ├── values.yaml
    ├── values-prod.yaml
    └── templates/
```

K8s standards:
- **Resource limits** on all containers (CPU/memory requests and limits)
- **Pod Disruption Budgets** — `minAvailable: 1` minimum
- **Horizontal Pod Autoscaler** — CPU/memory/custom metrics
- **Network Policies** — Default deny, explicit allow
- **Service accounts** — Per-service, bound to cloud IAM
- **Readiness/liveness probes** — Distinct endpoints, tuned thresholds
- **Anti-affinity rules** — Spread pods across nodes/zones
- **Kustomize overlays** — Environment-specific overrides without duplication
