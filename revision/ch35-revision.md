# Chapter 35 — Revision Sheet: DevOps Capstone — Production-Grade Backend Platform

> Supplements [the full chapter](../docs/08-production/ch35-devops-capstone.md). ⚠ The chapter states that the capstone is **designed and specified, not already built** ("the actual implementation will be done step-by-step"). Don't claim technologies on a resume until you have implemented them. A reference starter is provided in [code-examples/capstone/](../code-examples/capstone/README.md) (see the editorial supplement in the chapter).

## What is being built

A **production-grade asynchronous order-processing platform** (backend of an e-commerce/order system): Client → API → Order Service → {PostgreSQL, Redis, SQS, S3} → Workers → notifications/processing. Edge: Route 53 → CloudFront → WAF → ALB → EKS (API Pods + Worker Pods). Infrastructure: Terraform → AWS. Delivery: GitHub → GitHub Actions → Docker → ECR → GitOps repo → ArgoCD → EKS. Observability: metrics + logs + traces → CloudWatch / Prometheus / Grafana.

**Why better than basic CRUD:** demonstrates REST APIs, PostgreSQL, Redis, queues, asynchronous processing, Docker, Kubernetes, AWS, Terraform, CI/CD, GitOps, autoscaling, observability, security, failure recovery, caching, idempotency, retries, dead-letter queues, load testing, disaster recovery — a system you can discuss for 30–60 minutes.

## Stack and repository structure

TypeScript · Node.js · Express · PostgreSQL · Prisma · Redis · AWS SDK.
```text
devops-platform/
├── apps/
│   ├── api/    {src/{controllers,services,repositories,middleware,routes,config}, server.ts}, Dockerfile, package.json
│   └── worker/ {src/}, Dockerfile, package.json
├── packages/shared/
├── prisma/schema.prisma
├── infra/terraform/
├── deploy/{helm/order-platform/{Chart.yaml,values.yaml,values-dev.yaml,values-prod.yaml,templates/}, argocd/}
├── .github/workflows/
├── docker-compose.yml, package.json, pnpm-workspace.yaml, .gitignore, README.md
```
**Two workloads:** **API** (authentication, orders, products, API requests, database operations, cache, publishing jobs) and **Worker** (reading SQS, background jobs, retrying failures, handling DLQ). Separate so expensive processing doesn't make the API slow: request → API → save order → send job to SQS → return quickly; SQS → Worker → process. **Sync** (client waits) vs **async** (client doesn't wait for background work).

## Data model and order lifecycle

```text
User(id,email,createdAt) ─┬─ Order(id,userId,status,totalAmount,idempotencyKey,createdAt) ── OrderItem(id,orderId,productId,quantity,price) ── Product(id,name,price,stock,createdAt)
```
**Order states** (not arbitrary strings): `PENDING → PROCESSING → COMPLETED`; failure `PROCESSING → FAILED`; cancellation `PENDING → CANCELLED`.

## Reliability design decisions

- **Idempotency (API):** `Idempotency-Key: abc123` → stored `abc123 → order 456`; a repeated request returns the existing order (client times out after order creation and retries → Order #1 returned again, not Order #2).
- **Redis:** caching, rate limiting, temporary data, distributed coordination where appropriate; **cache-aside** (`GET /products/123`: miss → PostgreSQL → Redis SET → response; hit → response). **If Redis goes down** (a cache): skip cache → PostgreSQL — slower but functional = graceful degradation. Local = Docker Redis; production = managed Redis (ElastiCache), not a random Redis Pod.
- **SQS:** message `{"event":"ORDER_CREATED","orderId":"123","attempt":1}`; buffer (API 5,000 jobs/s vs worker 1,000 jobs/s → jobs accumulate and workers process = backpressure through a queue). **Worker scaling** by queue depth (100 → 1,000 → 10,000 → 100,000) → more workers (HPA/KEDA-like strategy). **Visibility timeout** must be long enough for normal processing (crash → message visible again). **DLQ** after repeated failures (attempt 1–4 ❌ → DLQ for investigation). **Worker idempotency:** store processed `eventId` (e.g. `xyz123`); a repeat is ignored.
- **Scaling problem:** API 3 → 20 Pods × 20 DB connections each = 400 vs PostgreSQL `max connections = 200` → *autoscaling the application doesn't automatically make the entire system scalable.*
- **Managed services in AWS:** RDS PostgreSQL (backups, patching, Multi-AZ, monitoring, managed storage; don't run the production DB inside the cluster without reason), ElastiCache Redis, S3 for documents/reports/exports/logs (DB stores `document_id, s3_key, content_type, created_at`).

## Containers and local development

- Separate `api-image` and `worker-image`; multi-stage Dockerfile (`node:22-alpine` builder → runtime with `npm ci --omit=dev`, `COPY --from=builder /app/dist ./dist`, `ENV NODE_ENV=production`, `USER node`, `CMD ["node","dist/server.js"]`): small runtime, production dependencies, non-root, immutable image. **Never** put `ENV DATABASE_PASSWORD=secret123`, AWS keys, DB passwords, JWT secrets or API keys in the image → Kubernetes Secret / AWS Secrets Manager / environment injection.
- **Local first:** Docker Compose with `api`, `worker`, `postgres`, `redis` (everything works without AWS — "cloud should not hide broken application logic"). `.env` example: `NODE_ENV=development`, `PORT=3000`, `DATABASE_URL=postgresql://postgres:postgres@postgres:5432/orders`, `REDIS_URL=redis://redis:6379`, `AWS_REGION=ap-south-1`, `SQS_QUEUE_URL=...`; `.gitignore` `.env`.
- **Health:** `/health/live` (`{"status":"alive"}`, shouldn't depend on every external dependency) and `/health/ready` (e.g. PostgreSQL reachable? else `ready=false` → Kubernetes stops sending traffic). **Graceful shutdown** on SIGTERM: stop accepting traffic → finish active requests → close DB → close Redis → exit (matters in rolling deployments).

## Kubernetes, Terraform, IAM

- Namespace `orders`; API Deployment (3 Pods), Worker Deployment (2 Pods), API Service, ConfigMap, Secret, HPA. API Deployment: `replicas: 3`, image `<ECR_IMAGE>`, port 3000, requests `250m/256Mi`, limits `1/512Mi`; Service `port 80 → targetPort 3000`; `readinessProbe` `/health/ready` (initialDelay 5, period 10); `livenessProbe` `/health/live` (period 20). HPA: 3 → 5 → 8 → 10 on CPU/memory (or custom/external metrics).
- **Terraform provisions:** VPC (public/private subnets, route tables, NAT, security groups), EKS (cluster, node groups, IAM), RDS, Redis, S3, SQS, ECR, CloudWatch, IAM roles. Repo `infra/terraform/{main,variables,outputs,providers,versions}.tf + modules/{vpc,eks,rds,redis,s3,sqs} + environments/{dev,prod}`; clear **environment separation** (dev smaller/cheaper; prod HA, larger, stronger safeguards); remote S3 state with locking/versioning; never casually delete production state.
- **IAM least privilege:** API role — only needed permissions (never `AdministratorAccess`); Worker role — SQS receive/delete + limited S3 access → reduced blast radius.

## CI/CD and GitOps

- **CI:** checkout → install → lint → typecheck → unit tests → integration tests → build → Docker build → security scan → push image to ECR. **Tag images** with Git SHA (`orders-api:a8f91c2`), never rely on `latest` — identify the commit and reproduce the build. **OIDC** (GitHub Actions → OIDC → IAM role → temporary credentials) instead of long-lived keys.
- **GitOps:** CI builds `code → image`; CD deploys `image → cluster`: GitHub Actions (build/test/push ECR) → update deployment config in GitOps repo → ArgoCD → EKS. ArgoCD compares desired (Git) vs actual (Kubernetes) → `OutOfSync` → reconciles per sync policy. Helm: chart + `values-dev.yaml` / `values-prod.yaml` instead of per-environment YAML.
- **Rolling deployment** (3 old → 2 old + 1 new → 1 old + 2 new → 0 old + 3 new; new Pods that fail readiness get no traffic and the rollout stalls; ArgoCD + Git rollback restores the previous version). **Canary:** 5% → 25% → 50% → 100% while watching error rate, latency, business metrics (understand even if not implemented).

## Observability

`/metrics` (`http_requests_total`, `http_request_duration_seconds`, `http_errors_total`) → Prometheus → Grafana. **RED:** rate (req/s), errors (5xx), duration (p50/p95/p99). Example dashboard: 1,250 req/s · 0.08% errors · p95 180 ms · p99 420 ms · DB connections 74/100 · queue depth 1,243. Structured logs `{"level":"info","requestId":"abc123","method":"POST","path":"/orders","statusCode":201,"durationMs":82}`; **never log** password, JWT, AWS credentials, API keys, database URL, payment credentials. Tracing: `POST /orders` 2 s → API span → PostgreSQL span (1.7 s) → Redis span → SQS span. **Alerts:** 5xx > 2%, p95 > 500 ms, queue age > 60 s, DB connections > 90%, Pod restart rate increasing, storage approaching limit — each actionable.

## Failure scenarios (rehearse these)

| # | Failure | Expected behaviour |
|---|---|---|
| 1 | API Pod dies | Deployment creates replacement; Service routes to healthy Pods → self-healing |
| 2 | Redis dies | cache failure → fall back to DB; Redis error metric ↑ → alert; API stays functional |
| 3 | Worker dies | message not completed → becomes visible again → another worker processes; repeated failure → DLQ → fault tolerance + at-least-once + idempotency |
| 4 | Database slow | p95 ↑, DB latency ↑ → investigate slow queries, connections, CPU, IOPS, locks; mitigate: cache, reduce load, rollback, optimise query, scale DB |
| 5 | Bad deployment | Git push → CI → ECR → ArgoCD → new version → 5xx ↑ → stop rollout → rollback → verify → root cause |
| 6 | Traffic spike 500 → 10,000 req/s | CloudFront/cache → WAF → ALB → EKS autoscaling → Redis → PostgreSQL; if DB can't scale fast: rate limiting, queue, load shedding |

## Security, HA, DR, cost

- **Security architecture:** Internet → WAF → ALB → EKS → private resources; RDS in private subnets; Redis private; no direct public access. SGs: Internet → ALB SG → API SG → RDS SG (RDS allows the API security group, not `0.0.0.0/0`). Secrets: AWS Secrets Manager → workload identity → application (never password in Git/Docker image). Network: Route 53 → CloudFront → WAF → ALB (public subnets) → EKS nodes, RDS, Redis in private subnets; NAT for outbound.
- **High availability:** distribute across AZ-A/B/C so other AZs continue serving (if the rest of the architecture also supports it).
- **DR:** RDS backups, S3 versioning where appropriate, infrastructure as code, container images in ECR, GitOps configuration in Git → Terraform recreates infrastructure → ECR deploys → Git/ArgoCD restores configuration. **"Rebuild from nothing" test:** Terraform → AWS infrastructure; ArgoCD → applications; ECR → images; RDS backup → database; minimise manual configuration.
- **Cost:** small EKS/RDS/Redis, limited NAT for learning; size by traffic in production; always ask "Do we need this? What does it cost? What reliability does it buy?"

## Build order (21 steps) and phases

1 Backend foundation · 2 PostgreSQL · 3 Redis · 4 Async worker · 5 SQS · 6 Docker · 7 Docker Compose · 8 Tests · 9 CI · 10 AWS infrastructure · 11 Terraform · 12 ECR · 13 EKS · 14 Helm · 15 ArgoCD · 16 Production deployment · 17 Observability · 18 Security · 19 Load testing · 20 Failure testing · 21 Reliability improvements.
- **P1 Backend:** `POST /users`, `POST /orders`, `GET /orders/:id`, `GET /products`, `GET /products/:id`; `POST /orders` → validate → check idempotency → create order → publish event → return. **P2 Async:** SQS → receive → validate → process → update order → delete message (failure: don't delete → retry → DLQ). **P3 Docker** (api image, worker image; Compose runs API, Worker, PostgreSQL, Redis). **P4 CI** (install → lint → typecheck → test → build → Docker build → push ECR). **P5 Terraform** (VPC, EKS, RDS, Redis, SQS, S3, ECR, IAM; modules, variables, outputs, remote state). **P6 Kubernetes** (API, Worker, ConfigMap, Secrets, Services, HPA + readiness, liveness, resources, rolling deployment). **P7 Helm.** **P8 GitOps.** **P9 Observability** (then test pod failure, DB latency, Redis failure, queue backlog, bad deployment). **P10 Load testing** (`GET /products`, `POST /orders`, `GET /orders/:id`; RPS, p50/p95/p99, 5xx, CPU, memory, DB, Redis, queue → find and optimise the bottleneck). **P11 Security** (secret scanning, dependency scanning, container scanning, IAM review, network review; verify no public RDS, no hard-coded secrets, no privileged containers, least-privilege IAM, HTTPS, authentication, rate limiting). **P12 Failure engineering** (kill API pod, kill worker, Redis unavailable, DB slow, queue backlog, broken deployment, traffic spike; document what happened, how detected, how recovered, what changed).

## Resume and interview

Resume wording (only after building): *Production-Grade Distributed Order Processing Platform — TypeScript/Node.js backend with PostgreSQL, Redis and asynchronous SQS workers; containerised with Docker and deployed to AWS EKS using Terraform, Helm and ArgoCD, with GitHub Actions CI/CD, autoscaling, structured observability, idempotent processing, retry/DLQ handling and production failure testing.* **Don't claim technologies you haven't implemented.**
**Interviewer questions this project supports:** why SQS; why PostgreSQL instead of DynamoDB; Redis down?; Kubernetes 3 → 20 Pods?; worker crash?; can the same SQS message be processed twice?; how does EKS access AWS services?; how does code reach production?; why ArgoCD; why Terraform; Deployment vs bare Pods; why is RDS private; how do you know a deployment caused an outage; traffic 10×?; all DB connections exhausted?; rollback?; AZ failure?

## Added notes (not in source)

- The chapter's builder/runtime Dockerfile uses `node:22-alpine` (musl). **Prisma on Alpine** needs OpenSSL available and the right `binaryTargets`; the pnpm monorepo layout also doesn't match a plain `COPY package*.json` + `npm ci` — and the build must run `prisma generate`. Ch8 recommends Debian *slim* for native-dependency safety.
- Queue-depth autoscaling for workers is typically done with **KEDA** (an SQS scaler adjusts the worker Deployment's replicas from queue length); plain HPA doesn't read SQS by default.
- Implementing idempotency robustly: a **unique constraint** on `Order.idempotencyKey` (insert, catch the unique-violation, return the existing row) avoids check-then-insert races; for workers, an atomic conditional transition (`UPDATE … SET status='PROCESSING' WHERE id=$1 AND status='PENDING'`) or a processed-events table makes duplicates harmless. "Save order then publish to SQS" is a dual write — see the transactional outbox in Ch.33.
- Response 36 ("Final DevOps Mastery"), promised at the end of this chapter, does not exist in the source files (source file 36 is a different, stand-alone response on virtualization internals — [Chapter 36](ch36-revision.md)); the final consolidation material is Chapter 24 plus the global revision sheets in this repository.

<!-- NAV -->

---

← [Sheet 34](ch34-revision.md) · [Full chapter 35](../docs/08-production/ch35-devops-capstone.md) · [All revision material](README.md) · [Sheet 36](ch36-revision.md) →
