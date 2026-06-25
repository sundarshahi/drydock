# Phase 3 — Tech Stack Selection

Generate `docs/architecture/tech-stack.md` (or `paths.tech_stack` from config):

| Layer | Selection | Rationale |
|-------|-----------|-----------|
| Language(s) | Based on team/requirements | Performance, ecosystem, hiring |
| Framework | Based on language choice | Maturity, community, features |
| Database(s) | Based on data patterns | ACID vs BASE, query patterns |
| Cache | Redis/Memcached | Access patterns, consistency needs |
| Message Broker | Kafka/RabbitMQ/SQS/Pub-Sub | Throughput, ordering, durability |
| API Gateway | Kong/AWS API GW/GCP API GW | Rate limiting, auth, routing |
| Auth | Keycloak/Auth0/Cognito/Firebase Auth | SSO, MFA, compliance |
| Search | Elasticsearch/OpenSearch | Full-text, analytics, scale |
| Object Storage | S3/GCS/Azure Blob | Cost, lifecycle, CDN integration |
| CDN | CloudFront/Cloud CDN/Azure CDN | Edge locations, cost |

Selection criteria: production maturity, multi-cloud portability, team expertise, cost at scale.
