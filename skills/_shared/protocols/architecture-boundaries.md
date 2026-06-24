# Architecture Boundaries Protocol — Inward Dependencies & Mechanical Fitness Functions

**Core principle: Dependencies point inward only. The domain knows nothing about frameworks, IO, or the outside world — and this is enforced by a machine, not by reviewer goodwill. "No framework deps in business logic" is a failing CI check, never a code comment.**

Clean/Hexagonal architecture survives only when the import graph is policed mechanically. Stated as prose ("keep the domain pure"), the rule erodes on the first deadline. This protocol fixes the dependency direction, the port→adapter wiring, and a per-language fitness function (`make arch`) that exits non-zero on any boundary violation — so the boundary is self-enforcing.

---

## Dependency-Direction Rule (the one law)

Layers, innermost to outermost. **Source-code dependencies (imports) may point INWARD only; never outward.**

```
        infrastructure / adapters   (frameworks, DB drivers, HTTP clients, ORMs, SDKs)
                  │  depends on ▼
        application / use-cases / ports   (orchestration + the PORT interfaces)
                  │  depends on ▼
        domain   (entities, value objects, business rules)   ← depends on NOTHING
```

- **Domain has zero framework/IO imports.** No web framework, ORM, HTTP/DB client, logger, env reader, clock, filesystem, or serialization-framework import in domain code. Domain imports only the language stdlib + other domain code. A framework import in the domain is a HIGH-severity violation.
- **Application depends only on domain + its own ports.** Use-cases orchestrate domain objects and call **port interfaces** (repository/gateway/clock/notifier abstractions). Use-cases MUST NOT import a concrete repository, DB driver, HTTP client, or framework type.
- **Ports are owned by the inside, implemented on the outside.** A port is an interface declared in the application (or domain) layer — `OrderRepository`, `PaymentGateway`, `Clock`. The interface lives inward; the concrete `PostgresOrderRepository` / `StripePaymentGateway` lives in infrastructure as an **adapter**.
- **Infrastructure depends inward, never the reverse.** Adapters import the port they implement and the domain types they map. No inner layer may import from `infrastructure/`, `adapters/`, `web/`, or `persistence/`.
- **No layer-skipping or cycles.** Infrastructure → domain directly (skipping application) is allowed only for type references, never for invoking business rules. The layer graph must be acyclic.

---

## Port → Adapter Wiring Rule (Dependency Inversion)

- Use-cases receive ports through **constructor/parameter injection**, typed as the interface — never `new PostgresOrderRepository()` inside a use-case.
- **The composition root is the ONLY place that names concrete adapters.** Binding port→adapter (DI container registration, factory, or `main()`/bootstrap) lives at the outermost edge: `main`, `wire`, the DI module, the framework bootstrap. Nowhere else may an inner layer reference a concrete adapter class.
- The direction of the *call* (use-case → repository) is opposite the direction of the *source dependency* (adapter → port interface). That inversion is the whole point — verify both: the call flows outward at runtime, the import flows inward at compile time.
- Test seams come for free: a use-case test injects an in-memory/fake adapter implementing the same port. If a use-case can't be unit-tested without spinning up a DB or HTTP server, a port is missing or a concrete dep leaked inward — fix the boundary, don't mock the framework.

---

## Mechanical Fitness Function (per language)

Every project MUST emit an arch-lint config + a `make arch` target wired into CI that **exits non-zero on a boundary violation**. Aspirational docs do not count; the gate is the contract.

| Stack | Tool | Config artifact | What it asserts |
|-------|------|-----------------|-----------------|
| TypeScript / JS | dependency-cruiser (or eslint `no-restricted-imports`) | `.dependency-cruiser.js` | `forbidden` rules: domain→{infra,framework}, app→infra, no cycles |
| JVM (Java/Kotlin) | ArchUnit | `*ArchitectureTest` in test source set | `layeredArchitecture()` / `noClasses().that().resideIn("..domain..").should().dependOnClassesThat().resideIn("..infra..")` |
| Python | import-linter | `.importlinter` (or `[tool.importlinter]` in `pyproject.toml`) | `layers` contract: domain \| application \| infrastructure (top→bottom), `forbidden` framework imports in domain |
| PHP | deptrac | `deptrac.yaml` | `layers` + `ruleset`: domain may depend on nothing; application on domain; infrastructure on both |
| Go | go-arch-lint | `.go-arch-lint.yml` | `components` + `deps`: domain has no `allow`; vendor/framework packages denied to inner components |

Rules for the config, whatever the tool:
- Encode the **direction law** above as explicit forbidden edges (domain→infra, app→infra, any→framework-in-domain) plus a **no-cycles** assertion.
- Treat the framework/IO package set as forbidden imports *inside the domain* (the web framework, ORM, DB/HTTP driver, cloud SDK).
- `make arch` runs the tool and propagates its exit code. CI invokes `make arch`; a non-zero exit **blocks the pipeline**.
- The config is checked in and version-controlled — it is the executable specification of the architecture.

---

## `make arch` Target (shape)

```makefile
# exits non-zero on a boundary violation → pipeline-blocking
arch:
	# TS:     npx depcruise --config .dependency-cruiser.js src
	# JVM:    ./gradlew test --tests '*ArchitectureTest'   (or mvn -Dtest=*ArchitectureTest test)
	# Python: lint-imports --config .importlinter
	# PHP:    vendor/bin/deptrac analyse --config-file=deptrac.yaml --fail-on-uncovered
	# Go:     go-arch-lint check --project-path .
.PHONY: arch
```

- CI must call `make arch` as a required, non-skippable step. No `|| true`, no `continue-on-error`.
- Run it locally in pre-commit/pre-push too — the fastest feedback loop is before the push.

---

## Severity Rule

- **Dependency-direction violations and port-boundary violations are HIGH severity — pipeline-blocking, NOT Medium.** A framework import in the domain, a use-case importing a concrete adapter, a cycle across layers, or an inner layer importing `infrastructure/` each fail the build.
- Do not downgrade these to "style" or "tech-debt to track." A boundary breach is structural rot that compounds; the gate's job is to stop it at the PR, not log it.
- The ONLY non-blocking variant: a config-covered, explicitly-annotated, time-boxed exception with a ticket reference (deptrac `skip_violations`, import-linter `ignore_imports`, dep-cruiser `comment`). Unannotated violations stay HIGH and block.

---

## Who Emits / Who Enforces

- **software-engineer EMITS** the arch-lint config (`.dependency-cruiser.js` / ArchUnit test / `.importlinter` / `deptrac.yaml` / `.go-arch-lint.yml`) and the `make arch` target, and wires `make arch` into CI as a required step. New code is authored to keep dependencies pointing inward and ports injected at the composition root.
- **code-reviewer RUNS** `make arch` (and inspects the import graph) on the change, and reports every boundary breach as a HIGH-severity finding with the offending `file:line` import and the rule it violates. A PR that introduces a violation — or removes/weakens the gate — is not approvable.
- Per `grounding-protocol.md`: cite the concrete violating import (`file:line` → the forbidden target) and the actual tool output; never assert "the boundary is clean" without `make arch` exit 0 observed this session.

---

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| `import { PrismaClient } from '@prisma/client'` inside a domain entity | Domain stays pure; `PrismaOrderRepository` (infra) implements the `OrderRepository` port |
| Use-case does `new StripeClient()` internally | Inject a `PaymentGateway` port; bind `StripeGateway` at the composition root |
| "Keep the domain framework-free" as a CONTRIBUTING.md note | A dependency-cruiser/ArchUnit/deptrac rule that fails CI on the import |
| Boundary violation filed as a Medium "cleanup later" | HIGH, pipeline-blocking; fix before merge |
| `make arch` runs with `continue-on-error: true` | Required step; non-zero exit blocks the pipeline |
| Mocking the web framework to unit-test a use-case | The use-case takes ports; inject an in-memory fake — no framework in the test |

---

## Key Principle

**An architecture you cannot fail a build on is a suggestion, not a boundary. Point every dependency inward, own your ports on the inside, bind adapters only at the composition root — and let `make arch` be the unfeeling reviewer that blocks the merge.**
