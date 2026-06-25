# Phase 5 — Data Model Design

Generate data models at `schemas/` at the project root:

- **ERD diagrams** in Mermaid (at `paths.erd` from config, default `schemas/erd.md`)
- **SQL migration files** (numbered, idempotent) (at `paths.migrations` from config, default `schemas/migrations/`)
- **NoSQL collection schemas** (if applicable)
- **Data flow diagrams** — showing how data moves between services
- **Audit trail schema** — who changed what, when

Standards enforced:
- Soft deletes with `deleted_at` timestamps
- UUID primary keys (not auto-increment) for distributed systems
- Created/updated timestamps on all entities
- Tenant isolation at the data layer
- PII field identification and encryption strategy
