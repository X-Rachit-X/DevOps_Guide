# Chapter 23 — Revision Sheet: Production Architecture + Troubleshooting

> Supplements [the full chapter](../docs/08-production/ch23-production-architecture-troubleshooting.md). The integration chapter: take a TypeScript/Node.js API (`POST /users`, `POST /orders`, `GET /orders/:id`, `POST /payments`, `POST /files`) from Git to production — and keep it alive. The goal is to understand **why each component exists and what you would change when requirements change.**

## Reference architecture

```text
Internet → Route 53 → CloudFront → WAF → Load Balancer → EKS (Pods A/B/C) → Redis · RDS PostgreSQL · S3
GitHub → GitHub Actions → Docker build (+scan) → ECR → EKS            Terraform → VPC, subnets, IAM, EKS, RDS, S3, LB
App → logs + metrics + traces → observability platform → dashboards → alerts
```

| Layer | Decisions |
|---|---|
| **Network** | VPC (e.g. `10.0.0.0/16`) across AZ-A/AZ-B with public + private subnets. Public: Load Balancer, NAT Gateway. Private: EKS worker capacity, RDS, internal services. DB never directly Internet-exposed. |
| **Security groups** | Internet →(HTTPS 443) ALB SG → API/EKS SG → RDS SG (5432); API → Redis; **Internet → RDS ❌** (least privilege at network level) |
| **DNS/TLS** | Route 53 `api.example.com` → CloudFront/LB; HTTPS everywhere; ACM manages certificates |
| **CloudFront/WAF** | Cache images, JS, CSS, static files; **don't** blindly cache `POST /payment`, `GET /account`, private responses. WAF: rate limiting, managed rules, IP rules, request filtering — one layer, not a replacement for IAM, SGs, authorization, input validation |
| **Load balancing** | Stable entry point (users never see Pod IPs); distributes to healthy backends; `/health`, `/ready` |
| **Kubernetes** | EKS control plane managed by AWS; Deployment `replicas: 3` self-heals; Service gives stable discovery; ConfigMap + Secret/external secrets (same image for dev/staging/prod) |
| **Data** | RDS PostgreSQL (not in the API container); connection pooling + pool sizing (10 Pods × 100 = 1000 connections!); Redis for caching, sessions, rate limiting, short-lived state, queues (caching brings invalidation, consistency, memory, TTL, failure trade-offs); S3 for large objects, with presigned URLs |
| **Docker** | Multi-stage build, `node:22-slim`, `npm ci --omit=dev`, `USER node`, no secrets in image, `EXPOSE 3000`, `CMD ["node","dist/server.js"]` |
| **CI/CD** | `git push` → checkout, `npm ci`, lint, typecheck, tests, build, Docker build, Docker scan, push image → deploy. Immutable tags (`my-api:8f31a7c` = Git commit) → Git commit → Docker image → ECR → Kubernetes tells you exactly what runs. Deploy: ECR → Deployment → new Pods → readiness → traffic; bad deploy → `kubectl rollout undo deployment/api` |
| **Terraform** | `infra/{main,variables,outputs}.tf + modules/{network,eks,database}`; PR → fmt → validate → plan → review → merge → controlled apply |
| **Observability** | JSON request logs (`requestId`, method, path, statusCode, durationMs); metrics: request rate, error rate, p50/p95/p99, CPU, memory, Pod restarts, DB connections, Redis latency, queue depth (RED); alerts only when actionable: 5xx > threshold, p95 > threshold, RDS connections near limit, storage pressure, Pods restarting, queue backlog growing |

## Incident playbooks (memorise the reasoning)

| # | Symptom | Diagnosis path | Root cause example |
|---|---|---|---|
| 1 | API returns 503 | `kubectl get pods` → one `CrashLoopBackOff` → `kubectl logs api-c` → "DATABASE_URL is undefined" → `describe pod` | Secret/config not injected — not Kubernetes itself |
| 2 | All Pods Running, still 503 | `kubectl get svc` → `kubectl get endpointslices` → Endpoints = none → Service selector `app: api` vs Pod label `app: backend` | Selector mismatch → no endpoints |
| 3 | Pods healthy but slow (CPU 30%, mem 40%) | Don't scale; traces: API 20 ms, Redis 15 ms, **RDS 1800 ms** | Slow queries, missing indexes, connection pool, locks, DB load |
| 4 | RDS connections 100% after Pods 3 → 10 | Each Pod has its own pool → total connections ↑ | Reduce pool size, use pooling/proxy, optimise DB usage, scale DB, limit concurrency. *Scaling the API doesn't scale the whole system* |
| 5 | `ImagePullBackOff` | `kubectl describe pod`; image name/tag/registry/permissions/existence | CI pushed `my-api:abc123`, Kubernetes requests `abc124` |
| 6 | New Pods get no traffic | Readiness probe `/ready` returns 503 because DB not ready | **Running ≠ Ready** |
| 7 | CPU 90% but replicas = 2 | `kubectl get hpa`, `describe hpa api-hpa`: metrics unavailable, requests not configured, `maxReplicas` reached | Never assume HPA is broken before checking metrics/events |
| 8 | DB and API fine, users can't connect | `dig api.example.com`, `curl -v https://api.example.com/health` | Wrong DNS target, TLS certificate issue, WAF blocking |

**Troubleshooting model (outside-in):** DNS/TLS → WAF/Edge → Load Balancer → Kubernetes (Pod / Service / Ingress) → Container → Node.js app → Redis / RDS / S3. At every layer ask *"Is this layer healthy?"*

**Layer commands:** `dig`, `curl -v`, `kubectl get pods|svc|ingress`, `kubectl describe pod`, `kubectl logs <pod>`, `kubectl logs <pod> --previous`, `kubectl get endpointslices`, `kubectl top pods|nodes`, `kubectl rollout status|undo deployment/api`; AWS console/CLI/CloudWatch for ALB, EKS, RDS, Lambda, S3.

## Deployment failure walkthrough

Deploy v2 → 5xx ↑: (1) `rollout status` (2) `get pods` (3) logs → "Redis connection refused" (4) check Redis (5) did v2 change `REDIS_URL`/authentication? (6) severe impact → `kubectl rollout undo` (7) verify 5xx ↓, latency ↓ (8) investigate root cause. **Detect → Diagnose → Mitigate → Recover → Root Cause Analysis.**

**Rollback vs fix-forward:** rollback is often fastest, but not automatically right — e.g. a security vulnerability in v1 makes rolling back dangerous. Understand what changed and the risk of each option.

## Trade-offs

- **Availability isn't free:** single EC2/AZ/DB = outage on failure; multi-AZ (LB → Pods in AZ-A/B → RDS) adds infrastructure, complexity, cost.
- **Cost/complexity:** EKS for a tiny internal CRUD app? Ask *why*. Kubernetes adds cluster/network complexity, monitoring, upgrades, security, operational overhead; ECS/Fargate, EC2 + Docker, or Lambda may be simpler. Don't use Kubernetes just for the resume — explain why you chose it.

## "When to use what"

| Requirement | Choice |
|---|---|
| Simple long-running API | EC2/ECS |
| Containerised workload | Docker |
| Many containers + orchestration | Kubernetes (AWS-managed: EKS) |
| Event-driven short task | Lambda |
| Object storage / relational DB / cache | S3 / RDS / Redis |
| Async jobs / pub-sub | SQS / SNS |
| CDN / DNS / HTTP filtering | CloudFront / Route 53 / WAF |
| IaC | Terraform |
| Metrics / dashboards / traces | Prometheus or CloudWatch / Grafana / OpenTelemetry-compatible stack |

The answer always depends on requirements.

## The interview answer — "How would you deploy a production Node.js application?"

Containerise with a multi-stage Docker build, push **immutable images** to ECR; run on EKS only if Kubernetes is justified; multiple **stateless Pods** behind a Service and external load balancer; infrastructure via **Terraform**; PostgreSQL in **RDS**, files in **S3**, **Redis** where caching/shared ephemeral state fits; keep the DB private (security groups + Kubernetes networking controls); CI/CD: tests, build, build + scan image, push to ECR, deploy the selected version; readiness/liveness probes, resource requests/limits, HPA, rolling deployments; structured logs, metrics, distributed traces with alerts on meaningful health indicators; troubleshoot outside-in: DNS/TLS → WAF/LB → Service/Ingress → Pods → app → Redis/RDS/S3.

## Key lesson

Don't think "I know AWS / Kubernetes / Docker / Terraform." Think **Application (Node.js, Docker, database) + Infrastructure (AWS/K8s, Terraform, network) + Operations (monitoring, reliability, debugging)** — the valuable skill is how they **interact**.

## Added notes (not in source)

- `kubectl rollout undo` reverts the Deployment's Pod template only; it does **not** revert database migrations, ConfigMaps/Secrets, or infrastructure — a reason to use backward-compatible (expand-and-contract) migrations (Ch.13).
- The Dockerfile shown runs `npm ci` as root and then drops to `USER node`; that is acceptable because the app only needs read access to `node_modules`.
- Layer ordering for a debugging session: confirm the *symptom* from outside (`curl -v`) before touching the cluster; many incidents are DNS/TLS/WAF, not Kubernetes.

<!-- NAV -->

---

← [Sheet 22](ch22-revision.md) · [Full chapter 23](../docs/08-production/ch23-production-architecture-troubleshooting.md) · [All revision material](README.md) · [Sheet 24](ch24-revision.md) →
