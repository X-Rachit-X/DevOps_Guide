# Capstone Reference Starter (editorial)

> **Status: editorial addition, not source material.** Chapter 35 of the source is a *design* walkthrough with no complete code. This starter implements the parts it describes: API + worker, PostgreSQL, Redis cache-aside, SQS, idempotent `POST /orders`, `/health/live` + `/health/ready`, graceful shutdown, Docker, Compose, CI, Kubernetes manifests, KEDA.
>
> **Verified:** `npm ci && npm run typecheck && npm run build` (recorded in [PROGRESS.md](../../PROGRESS.md)).
> **NOT verified:** running the stack end to end (the Docker daemon was unavailable during the audit), the Kubernetes/KEDA manifests against a cluster, the CI workflow on GitHub. Treat it as a starting point and test it.

## Layout

| Path | Purpose | Chapter 35 section |
|---|---|---|
| `src/api.ts` | Express API: health, idempotent create, cache-aside read, graceful shutdown | 11, 14, 15, 27-30 |
| `src/worker.ts` | SQS long-poll worker with idempotent state transition | 17-21 |
| `src/config.ts` | env validation, pool / Redis / SQS clients | 24, 39 |
| `db/init.sql`, `prisma/schema.prisma` | Data model + `UNIQUE(idempotency_key)` | 9-11 |
| `Dockerfile`, `docker-compose.yml`, `.env.example` | Multi-stage image; local stack with LocalStack SQS | 22-26 |
| `ci/ci.yml` | typecheck/build + OIDC + SHA-tagged ECR push | 48-52 |
| `deploy/api.yaml`, `deploy/worker-keda.yaml` | Deployment, Service, probes, requests/limits, HPA; queue-depth scaling | 31-38, 18 |

## Run locally

```bash
cd code-examples/capstone
docker compose up --build
curl -X POST localhost:3000/orders -H "content-type: application/json" -H "Idempotency-Key: abc123" \
  -d '{"userId":1,"items":[{"productId":1,"quantity":2,"price":9.99}]}'
# repeat the same command: same orderId, "duplicate": true
curl localhost:3000/health/ready
```

## Known gaps (deliberate, so they can be your exercises)

1. **Dual write:** the DB commit and the SQS send are not atomic. Add a transactional outbox (Chapter 33).
2. No authentication, validation library, migration tool, `/metrics`, tracing, or automated tests.
3. `price` is trusted from the client; production code must read it from `products`.
4. Stock is not decremented; do it inside the same transaction.
5. API and worker share one image; split them for a smaller attack surface.
6. The Terraform, Helm chart and ArgoCD `Application` described in Chapter 35 are not included.
