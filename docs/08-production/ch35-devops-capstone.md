# Chapter 35 — DevOps Capstone: Build a Production-Grade Backend Platform

> **Source:** Response 35 of the original conversation (`source-archive/src-35.txt`, lines 1–3246) · **Part II — Advanced extension (Responses 25–36)**  
> **Study aids:** [Revision sheet](../../revision/ch35-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md) · *includes an editorial supplement at the end*

<!-- SOURCE-BEGIN -->

Now we move from **learning individual DevOps technologies → combining everything into one system**.

This response is deliberately practical. The goal is not to build another CRUD application. The goal is to build something you can explain in an interview from:

**code → database → containers → CI → AWS → Kubernetes → deployment → observability → failure recovery.**

---

## 1. What We Are Building

We will build a **production-grade asynchronous order-processing platform**.

Think of it as the backend infrastructure behind an e-commerce/order system.

The system will support:

```text
Client
  ↓
API
  ↓
Order Service
  ├── PostgreSQL
  ├── Redis
  ├── SQS
  └── S3
        ↓
     Workers
        ↓
  notifications / processing
```

And around it:

```text
                     Route 53
                        │
                     CloudFront
                        │
                       WAF
                        │
                       ALB
                        │
                  ┌─────┴─────┐
                  │    EKS    │
                  │           │
             API Pods     Worker Pods
                  │           │
          ┌───────┼───────┐   │
          │       │       │   │
       Redis   PostgreSQL SQS ─┘
          │               │
          │               ↓
          │            Workers
          │
          └────────── Cache

             S3
              │
         Object Storage
```

Infrastructure:

```text
Terraform
    ↓
AWS Infrastructure

GitHub
   ↓
GitHub Actions
   ↓
Docker
   ↓
ECR
   ↓
GitOps Repository
   ↓
ArgoCD
   ↓
EKS
```

Observability:

```text
Application
    ↓
Metrics + Logs + Traces
    ↓
CloudWatch / Prometheus / Grafana
```

---

## 2. Why This Project Is Better Than a Basic CRUD App

A normal CRUD project demonstrates:

```text
GET
POST
PUT
DELETE
```

That's not enough to demonstrate serious backend/DevOps knowledge.

Our project demonstrates:

```text
REST APIs
PostgreSQL
Redis
queues
asynchronous processing
Docker
Kubernetes
AWS
Terraform
CI/CD
GitOps
autoscaling
observability
security
failure recovery
caching
idempotency
retries
dead-letter queues
load testing
disaster recovery
```

That's much closer to the kind of system you can discuss for 30–60 minutes.

---

## 3. Project Architecture

Let's first understand the complete system.

```text
                         INTERNET
                            │
                            ▼
                       Route 53
                            │
                            ▼
                       CloudFront
                            │
                            ▼
                           WAF
                            │
                            ▼
                           ALB
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
           API Service              Static/S3
                │
        ┌───────┼────────┐
        │       │        │
        ▼       ▼        ▼
    PostgreSQL Redis    SQS
        │       │        │
        │       │        ▼
        │       │      Worker
        │       │        │
        │       │        ├── S3
        │       │        └── External services
        │       │
        └───────┴──────────
```

---

## 4. The Application

We'll use:

```text
TypeScript
Node.js
Express
PostgreSQL
Prisma
Redis
AWS SDK
```

Why TypeScript?

Because it matches your target backend stack.

---

## 5. Repository Structure

We'll use a monorepo-style structure:

```text
devops-platform/
│
├── apps/
│   ├── api/
│   │   ├── src/
│   │   │   ├── controllers/
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── middleware/
│   │   │   ├── routes/
│   │   │   ├── config/
│   │   │   └── server.ts
│   │   ├── Dockerfile
│   │   └── package.json
│   │
│   └── worker/
│       ├── src/
│       ├── Dockerfile
│       └── package.json
│
├── packages/
│   └── shared/
│
├── prisma/
│   └── schema.prisma
│
├── infra/
│   └── terraform/
│
├── deploy/
│   ├── helm/
│   │   └── order-platform/
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       ├── values-dev.yaml
│   │       ├── values-prod.yaml
│   │       └── templates/
│   │
│   └── argocd/
│
├── .github/
│   └── workflows/
│
├── docker-compose.yml
├── package.json
├── pnpm-workspace.yaml
├── .gitignore
└── README.md
```

Don't worry if this looks large.

We'll build it incrementally.

---

## 6. Major Components

We have two main application workloads.

### API

Responsible for:

```text
authentication
orders
products
API requests
database operations
cache
publishing jobs
```

### Worker

Responsible for:

```text
reading SQS
processing background jobs
retrying failures
handling DLQ
```

This separation is important.

---

## 7. Why Separate API and Worker?

Suppose you receive:

```text
10,000 orders
```

If the API itself performs expensive processing:

```text
request
 ↓
API
 ↓
process everything
 ↓
response
```

the API becomes slow.

Instead:

```text
request
 ↓
API
 ↓
save order
 ↓
send job to SQS
 ↓
return quickly
```

Then:

```text
SQS
 ↓
Worker
 ↓
process job
```

This is asynchronous architecture.

---

## 8. Synchronous vs Asynchronous

#### Synchronous

```text
Client
 ↓
API
 ↓
DB
 ↓
response
```

Client waits.

#### Asynchronous

```text
Client
 ↓
API
 ↓
Queue
 ↓
response

Queue
 ↓
Worker
 ↓
processing
```

Client doesn't wait for background work.

---

## 9. Database Design

We'll keep the initial schema simple but realistic.

```text
User
 │
 └── Order
       │
       └── OrderItem
              │
              └── Product
```

Conceptually:

```text
User
----
id
email
createdAt

Product
-------
id
name
price
stock
createdAt

Order
-----
id
userId
status
totalAmount
idempotencyKey
createdAt

OrderItem
---------
id
orderId
productId
quantity
price
```

---

## 10. Order States

Don't use arbitrary strings everywhere.

Use:

```text
PENDING
PROCESSING
COMPLETED
FAILED
CANCELLED
```

State transitions:

```text
PENDING
   ↓
PROCESSING
   ↓
COMPLETED
```

Failure:

```text
PROCESSING
   ↓
FAILED
```

Cancellation:

```text
PENDING
   ↓
CANCELLED
```

This becomes important for reliability.

---

## 11. Idempotency

Suppose:

```http
POST /orders
```

The client sends:

```text
Idempotency-Key: abc123
```

The API stores:

```text
abc123 → order 456
```

If the request is repeated:

```text
abc123
```

we don't create another order.

Instead:

```text
return existing order
```

---

## 12. Why This Matters

Imagine:

```text
Client
 ↓
POST /orders
 ↓
Order created
 ↓
network timeout
```

Client thinks:

```text
"Maybe it failed."
```

It retries.

Without idempotency:

```text
Order #1
Order #2
```

With idempotency:

```text
Order #1
Order #1 returned again
```

---

## 13. Redis

Redis will be used for:

```text
caching
rate limiting
temporary data
distributed coordination where appropriate
```

Example:

```text
GET /products/123
```

First request:

```text
API
 ↓
Redis miss
 ↓
PostgreSQL
 ↓
Redis SET
 ↓
response
```

Next request:

```text
API
 ↓
Redis hit
 ↓
response
```

---

## 14. Cache-Aside

We'll use:

```text
Application
 ↓
Redis
```

If missing:

```text
Redis miss
 ↓
DB
 ↓
Redis
 ↓
response
```

This is called:

> Cache-aside.

---

## 15. Cache Failure

Critical design question:

> What if Redis goes down?

Because Redis is a cache, we can often do:

```text
Redis unavailable
       ↓
skip cache
       ↓
PostgreSQL
```

The system becomes slower but remains functional.

That's graceful degradation.

---

## 16. SQS

We'll use Amazon SQS for asynchronous processing.

Example:

```text
POST /orders
    ↓
create order
    ↓
SQS
    ↓
worker
```

Message:

```json
{
  "event": "ORDER_CREATED",
  "orderId": "123",
  "attempt": 1
}
```

---

## 17. Why SQS?

It provides a buffer.

Suppose:

```text
API = 5,000 jobs/sec
worker = 1,000 jobs/sec
```

Instead of immediately crashing:

```text
API
 ↓
SQS
 ↓
jobs accumulate
 ↓
workers process
```

This is:

> Backpressure through a queue.

---

## 18. Worker Scaling

Suppose queue depth becomes:

```text
100
1,000
10,000
100,000
```

We can increase workers.

Conceptually:

```text
Queue depth
    ↓
HPA/KEDA-like scaling strategy
    ↓
more workers
```

For the capstone, understand the architecture even if some production autoscaling integrations are treated as advanced implementation.

---

## 19. SQS Visibility Timeout

Important concept.

Suppose worker receives:

```text
Message A
```

SQS temporarily hides it.

Worker processes it.

If worker succeeds:

```text
delete message
```

If worker crashes:

```text
message becomes visible again
```

Therefore:

```text
visibility timeout
```

must be long enough for normal processing.

---

## 20. DLQ

What if a message repeatedly fails?

Example:

```text
attempt 1 ❌
attempt 2 ❌
attempt 3 ❌
attempt 4 ❌
```

Don't retry forever.

Send to:

```text
Dead Letter Queue
```

Then engineers can investigate.

---

## 21. Worker Idempotency

Messages can be delivered more than once.

Therefore:

```text
worker
 ↓
process job
```

must be designed to tolerate duplicates.

For example:

```text
eventId = xyz123
```

Store processed event IDs.

If:

```text
xyz123
```

appears again:

```text
already processed
→ ignore
```

This is critical in distributed systems.

---

## 22. Docker Architecture

We'll create separate images:

```text
api-image
worker-image
```

Each image contains only what that workload needs.

Example:

```text
Node
 ↓
build TypeScript
 ↓
production JS
 ↓
runtime image
```

Use multi-stage builds.

---

## 23. Production Dockerfile

Conceptually:

```dockerfile
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

RUN npm run build


FROM node:22-alpine AS runtime

WORKDIR /app

ENV NODE_ENV=production

COPY package*.json ./
RUN npm ci --omit=dev

COPY --from=builder /app/dist ./dist

USER node

CMD ["node", "dist/server.js"]
```

Important ideas:

```text
multi-stage
small runtime
production dependencies
non-root
immutable image
```

---

## 24. Don't Put Secrets in Docker

Never:

```dockerfile
ENV DATABASE_PASSWORD=secret123
```

Don't put:

```text
AWS keys
DB passwords
JWT secrets
API keys
```

inside the image.

Instead:

```text
Kubernetes Secret
AWS Secrets Manager
environment injection
```

depending on the architecture.

---

## 25. Local Development

Before AWS, everything must work locally.

We'll use:

```text
Docker Compose
```

for:

```text
API
PostgreSQL
Redis
Local worker
```

Architecture:

```text
docker-compose
│
├── api
├── worker
├── postgres
└── redis
```

---

## 26. Local Environment

Example:

```env
NODE_ENV=development

PORT=3000

DATABASE_URL=postgresql://postgres:postgres@postgres:5432/orders

REDIS_URL=redis://redis:6379

AWS_REGION=ap-south-1
SQS_QUEUE_URL=...
```

Never commit real secrets.

Use:

```text
.env
```

and:

```gitignore
.env
```

---

## 27. Health Endpoint

API:

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

But production health endpoints should be more thoughtful.

We can have:

```text
/health/live
/health/ready
```

---

## 28. Liveness

```http
GET /health/live
```

Means:

> Is the process alive?

Simple response:

```json
{
  "status": "alive"
}
```

It shouldn't necessarily depend on every external dependency.

---

## 29. Readiness

```http
GET /health/ready
```

Can verify critical dependencies.

For example:

```text
PostgreSQL reachable?
```

If not:

```text
ready = false
```

Kubernetes then stops sending traffic to that pod.

---

## 30. Graceful Shutdown

Our API must handle:

```text
SIGTERM
```

Sequence:

```text
SIGTERM
 ↓
stop accepting new traffic
 ↓
finish active requests
 ↓
close DB
 ↓
close Redis
 ↓
exit
```

This matters when Kubernetes performs rolling deployments.

---

## 31. Kubernetes Architecture

Eventually:

```text
EKS Cluster
│
├── namespace: orders
│
├── API Deployment
│     ├── pod
│     ├── pod
│     └── pod
│
├── Worker Deployment
│     ├── pod
│     └── pod
│
├── API Service
│
├── ConfigMap
│
├── Secret
│
└── HPA
```

---

## 32. API Deployment

Conceptually:

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: api

spec:
  replicas: 3

  selector:
    matchLabels:
      app: api

  template:
    metadata:
      labels:
        app: api

    spec:
      containers:
        - name: api
          image: <ECR_IMAGE>

          ports:
            - containerPort: 3000

          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"

            limits:
              cpu: "1"
              memory: "512Mi"
```

---

## 33. Service

Pods are ephemeral.

Their IPs can change.

So:

```text
Client
 ↓
Service
 ↓
Pods
```

Example:

```yaml
apiVersion: v1
kind: Service

metadata:
  name: api

spec:
  selector:
    app: api

  ports:
    - port: 80
      targetPort: 3000
```

---

## 34. Readiness Probe

Example:

```yaml
readinessProbe:
  httpGet:
    path: /health/ready
    port: 3000

  initialDelaySeconds: 5
  periodSeconds: 10
```

If readiness fails:

```text
Pod remains alive
but
traffic is removed
```

---

## 35. Liveness Probe

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 3000

  periodSeconds: 20
```

If the application becomes genuinely stuck:

```text
Kubernetes
 ↓
restart pod
```

---

## 36. Resource Requests

Suppose:

```yaml
requests:
  cpu: "250m"
  memory: "256Mi"
```

This tells Kubernetes roughly:

> "I need at least this much capacity to schedule me."

This affects scheduling.

---

## 37. Resource Limits

```yaml
limits:
  cpu: "1"
  memory: "512Mi"
```

This establishes a resource ceiling.

Important distinction:

```text
requests
→ scheduling expectation

limits
→ maximum resource boundary
```

---

## 38. HPA

Suppose:

```text
API pods = 3
```

Traffic increases.

HPA can increase:

```text
3
 ↓
5
 ↓
8
 ↓
10
```

based on metrics such as CPU or memory, and potentially custom/external metrics with the appropriate setup.

---

## 39. Important Scaling Problem

Suppose:

```text
API scales:
3 → 20 pods
```

But PostgreSQL has:

```text
max connections = 200
```

Each pod:

```text
20 DB connections
```

Then:

```text
20 × 20
= 400
```

You have now overloaded your database.

Therefore:

> **Autoscaling the application doesn't automatically make the entire system scalable.**

This is a very important interview point.

---

## 40. Database

For AWS production:

```text
EKS
 ↓
private network
 ↓
RDS PostgreSQL
```

Don't run your production database inside the same Kubernetes cluster unless there is a specific reason.

Use a managed database when appropriate.

Benefits:

```text
backups
patching
Multi-AZ options
monitoring
managed storage
```

---

## 41. Redis

Similarly:

```text
EKS
 ↓
ElastiCache Redis
```

rather than treating a random Redis pod as production infrastructure.

Local:

```text
Docker Redis
```

Production:

```text
Managed Redis
```

This is an important environment distinction.

---

## 42. S3

We'll use S3 for object storage.

Possible future use:

```text
order documents
reports
exports
logs/artifacts
```

Database stores metadata:

```text
document_id
s3_key
content_type
created_at
```

S3 stores the actual bytes.

---

## 43. Terraform Architecture

Terraform will provision:

```text
VPC
├── public subnets
├── private subnets
├── route tables
├── NAT
└── security groups

EKS
├── cluster
├── node groups
└── IAM

RDS
Redis
S3
SQS
ECR
CloudWatch
IAM roles
```

Conceptually:

```text
Terraform
    ↓
AWS APIs
    ↓
Infrastructure
```

---

## 44. Terraform Repository

Example:

```text
infra/terraform/
│
├── main.tf
├── variables.tf
├── outputs.tf
├── providers.tf
├── versions.tf
│
├── modules/
│   ├── vpc/
│   ├── eks/
│   ├── rds/
│   ├── redis/
│   ├── s3/
│   └── sqs/
│
└── environments/
    ├── dev/
    └── prod/
```

---

## 45. Environment Separation

Don't put:

```text
dev
prod
```

in one giant configuration with random conditionals.

Prefer clear environment separation.

Example:

```text
dev
 ↓
smaller resources
lower cost

prod
 ↓
HA
larger resources
stronger safeguards
```

---

## 46. Terraform State

State tracks:

```text
what Terraform believes exists
```

Production should use remote state.

Conceptually:

```text
Developer/CI
      ↓
Terraform
      ↓
S3 remote state
```

Use appropriate state locking/versioning strategy.

Never casually delete production state.

---

## 47. IAM

The system should follow least privilege.

Example:

API should not have:

```text
AdministratorAccess
```

Instead:

```text
API role
 ↓
only required permissions
```

Worker:

```text
Worker role
 ↓
SQS receive/delete
 ↓
limited S3 access
```

This reduces blast radius.

---

## 48. CI Pipeline

Now we connect GitHub Actions.

Developer:

```text
git push
```

Pipeline:

```text
Checkout
   ↓
Install
   ↓
Lint
   ↓
Typecheck
   ↓
Unit tests
   ↓
Integration tests
   ↓
Build
   ↓
Docker build
   ↓
Security scan
   ↓
Push image to ECR
```

---

## 49. Image Tagging

Never rely only on:

```text
latest
```

Use immutable identifiers:

```text
orders-api:git-sha
```

For example:

```text
orders-api:a8f91c2
```

Now you know exactly which source produced the image.

---

## 50. Why Git SHA Tags Matter

Suppose production has:

```text
orders-api:a8f91c2
```

and something breaks.

You can identify:

```text
commit a8f91c2
```

and reproduce the build.

With:

```text
latest
```

you don't have that clarity.

---

## 51. ECR

ECR = Elastic Container Registry.

Pipeline:

```text
GitHub Actions
      ↓
docker build
      ↓
ECR
      ↓
image
```

EKS then pulls:

```text
ECR image
```

---

## 52. OIDC

Don't put:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

in GitHub secrets if you can avoid long-lived credentials.

Use:

```text
GitHub Actions
       ↓
OIDC
       ↓
AWS IAM role
       ↓
temporary credentials
```

This is a major production security improvement.

---

## 53. GitOps

Now we separate:

#### CI

Builds:

```text
code → image
```

#### CD

Deploys:

```text
image → cluster
```

With GitOps:

```text
GitHub Actions
 ↓
build/test/push ECR
 ↓
update deployment config
 ↓
GitOps repository
 ↓
ArgoCD
 ↓
EKS
```

---

## 54. Why ArgoCD?

ArgoCD continuously compares:

```text
desired state in Git
```

against:

```text
actual state in Kubernetes
```

If they differ:

```text
OutOfSync
```

ArgoCD reconciles them depending on your sync policy.

---

## 55. Helm

Helm packages the Kubernetes application.

Instead of maintaining:

```text
deployment-dev.yaml
deployment-prod.yaml
deployment-staging.yaml
```

we can have:

```text
Chart
+
values
```

Example:

```text
values-dev.yaml
values-prod.yaml
```

---

## 56. Deployment Flow

Our complete flow:

```text
Developer
    │
    ▼
GitHub
    │
    ▼
GitHub Actions
    │
    ├── test
    ├── build
    ├── scan
    └── Docker
          │
          ▼
         ECR
          │
          ▼
     GitOps update
          │
          ▼
       ArgoCD
          │
          ▼
         EKS
          │
          ▼
      API / Worker
```

This is the core DevOps pipeline you should be able to draw in an interview.

---

## 57. Deployment Strategy

We'll use rolling deployments.

Suppose:

```text
3 old pods
```

Deployment:

```text
old pod
 ↓
new pod
 ↓
health check
 ↓
traffic
```

Gradually:

```text
3 old
2 old + 1 new

1 old + 2 new

0 old + 3 new
```

---

## 58. What If New Pods Are Broken?

Readiness fails.

Kubernetes should not send traffic to them.

Deployment can stop progressing.

Then:

```text
ArgoCD
+
Git
+
rollback
```

can restore the previous version.

---

## 59. Canary Deployment

For advanced deployment:

```text
100% old
```

Deploy:

```text
5% new
```

Observe:

```text
error rate
latency
business metrics
```

Then:

```text
5%
 ↓
25%
 ↓
50%
 ↓
100%
```

This reduces blast radius.

You don't necessarily need to implement full progressive delivery in this capstone, but you should understand it.

---

## 60. Observability

Our API should expose:

```text
/metrics
```

Example metrics:

```text
http_requests_total
http_request_duration_seconds
http_errors_total
```

Prometheus scrapes:

```text
API
 ↓
/metrics
 ↓
Prometheus
```

Grafana visualizes:

```text
Prometheus
 ↓
Grafana
```

---

## 61. RED Metrics

For the API:

#### Rate

```text
requests/sec
```

#### Errors

```text
5xx rate
```

#### Duration

```text
p50
p95
p99
```

These should become your first backend dashboard.

---

## 62. Example Dashboard

```text
┌─────────────────────────────────────┐
│ Requests/sec                        │
│ 1,250                               │
├─────────────────────────────────────┤
│ Error Rate                          │
│ 0.08%                               │
├─────────────────────────────────────┤
│ p95 Latency                         │
│ 180ms                               │
├─────────────────────────────────────┤
│ p99 Latency                         │
│ 420ms                               │
├─────────────────────────────────────┤
│ DB Connections                      │
│ 74 / 100                            │
├─────────────────────────────────────┤
│ Queue Depth                         │
│ 1,243                               │
└─────────────────────────────────────┘
```

---

## 63. Logs

Don't log:

```text
console.log("something happened")
```

randomly.

Use structured logs:

```json
{
  "level": "info",
  "requestId": "abc123",
  "method": "POST",
  "path": "/orders",
  "statusCode": 201,
  "durationMs": 82
}
```

Now logs are searchable.

---

## 64. Never Log Secrets

Never log:

```text
password
JWT
AWS credentials
API keys
database URL
payment credentials
```

This is an extremely common production mistake.

---

## 65. Tracing

A request:

```text
POST /orders
```

may produce:

```text
API span
 ↓
PostgreSQL span
 ↓
Redis span
 ↓
SQS span
```

If order creation takes:

```text
2 seconds
```

tracing can reveal:

```text
DB = 1.7 seconds
```

instead of blindly investigating the API.

---

## 66. Alerting

Example alerts:

```text
5xx rate > 2%
p95 latency > 500ms
queue age > 60s
DB connections > 90%
pod restart rate increasing
disk/storage approaching limit
```

But remember:

> Don't create alerts just because a metric exists.

Each alert should be actionable.

---

## 67. Failure Scenario #1 — API Pod Dies

```text
API pod
 ↓
crashes
```

Kubernetes:

```text
Deployment
 ↓
detect missing replica
 ↓
create replacement
```

Service:

```text
continues routing to healthy pods
```

This demonstrates:

```text
self-healing
```

---

## 68. Failure Scenario #2 — Redis Dies

```text
Redis
 ↓
unavailable
```

Application:

```text
cache failure
 ↓
fallback DB
```

Monitoring:

```text
Redis error metric ↑
```

Alert:

```text
Redis unavailable
```

Core API remains functional if the architecture allows that degradation.

---

## 69. Failure Scenario #3 — Worker Dies

```text
Worker
 ↓
crashes
```

SQS message isn't successfully completed.

Eventually:

```text
message becomes visible
```

Another worker can process it.

If repeated failures:

```text
DLQ
```

This demonstrates:

```text
fault tolerance
+
at-least-once processing
+
idempotency
```

---

## 70. Failure Scenario #4 — Database Slow

Observe:

```text
p95 latency ↑
DB latency ↑
```

Investigate:

```text
slow queries
connections
CPU
IOPS
locks
```

Potential mitigation:

```text
cache
reduce load
rollback
optimize query
scale DB appropriately
```

---

## 71. Failure Scenario #5 — Bad Deployment

```text
Git push
 ↓
CI
 ↓
ECR
 ↓
ArgoCD
 ↓
new version
 ↓
5xx increases
```

Observability detects:

```text
error rate ↑
```

Response:

```text
stop rollout
 ↓
rollback
 ↓
verify recovery
```

Then investigate root cause.

---

## 72. Failure Scenario #6 — Traffic Spike

Normal:

```text
500 req/sec
```

Sudden:

```text
10,000 req/sec
```

System protections:

```text
CloudFront/cache
 ↓
WAF
 ↓
ALB
 ↓
EKS autoscaling
 ↓
Redis
 ↓
PostgreSQL
```

But if DB cannot scale fast enough:

```text
rate limiting
queue
load shedding
```

protect the system.

---

## 73. Security Architecture

We should have:

```text
Internet
   ↓
WAF
   ↓
ALB
   ↓
EKS
   ↓
private resources
```

RDS:

```text
private subnet
```

Redis:

```text
private
```

No direct public access.

---

## 74. Security Groups

Conceptually:

```text
Internet
   ↓
ALB SG
   ↓
API SG
   ↓
RDS SG
```

RDS should allow traffic from:

```text
API security group
```

not:

```text
0.0.0.0/0
```

---

## 75. Secrets Architecture

Production:

```text
AWS Secrets Manager
        ↓
workload identity
        ↓
application
```

rather than:

```text
password inside Git
```

or:

```text
password inside Docker image
```

---

## 76. Network Architecture

A sensible AWS architecture:

```text
                  Internet
                     │
                  Route53
                     │
                  CloudFront
                     │
                    WAF
                     │
                    ALB
                     │
        ┌────────────┴────────────┐
        │                         │
 Public Subnets              Public Subnets
        │
        ▼
       ALB
        │
        ▼
Private Subnets
        │
        ├── EKS nodes
        ├── RDS
        └── Redis
```

NAT allows appropriate outbound traffic from private workloads.

---

## 77. High Availability

We should distribute workloads across multiple Availability Zones.

Conceptually:

```text
           EKS
      ┌─────┼─────┐
      │     │     │
     AZ-A  AZ-B  AZ-C
      │     │     │
     Pods  Pods  Pods
```

If one AZ has problems:

```text
other AZs
 ↓
continue serving
```

assuming the rest of the architecture is also designed for it.

---

## 78. Disaster Recovery

Our capstone should include:

```text
RDS backups
S3 versioning where appropriate
infrastructure as code
container images in ECR
GitOps configuration in Git
```

Why?

If infrastructure disappears:

```text
Terraform
 ↓
recreate infrastructure
```

Application:

```text
ECR
 ↓
deploy
```

Configuration:

```text
Git
 ↓
ArgoCD
```

This is a major advantage of Infrastructure as Code + GitOps.

---

## 79. The "Rebuild From Nothing" Test

A powerful DevOps exercise:

> Imagine the entire environment disappears.

Can you recreate it?

Ideally:

```text
Terraform
 ↓
AWS infrastructure

ArgoCD
 ↓
Kubernetes applications

ECR
 ↓
container images

RDS backup
 ↓
database
```

The goal is to minimize manual configuration.

---

## 80. Cost Awareness

Production architecture shouldn't mean:

```text
maximum AWS services everywhere
```

For learning:

```text
small EKS
small RDS
small Redis
limited NAT
```

For real production:

```text
size according to traffic
```

Always ask:

```text
Do we need this?
What does it cost?
What reliability does it buy?
```

---

## 81. Capstone Development Order

Don't build the entire thing simultaneously.

We'll build it in this order:

```text
1. Backend foundation
2. PostgreSQL
3. Redis
4. Async worker
5. SQS
6. Docker
7. Docker Compose
8. Tests
9. CI
10. AWS infrastructure
11. Terraform
12. ECR
13. EKS
14. Helm
15. ArgoCD
16. Production deployment
17. Observability
18. Security
19. Load testing
20. Failure testing
21. Reliability improvements
```

This prevents the project from becoming unmanageable.

---

## 82. Phase 1 — Backend

First build:

```text
POST /users
POST /orders
GET /orders/:id
GET /products
GET /products/:id
```

Then:

```text
POST /orders
```

will:

```text
validate
 ↓
check idempotency
 ↓
create order
 ↓
publish event
 ↓
return
```

---

## 83. Phase 2 — Async Processing

Worker:

```text
SQS
 ↓
receive message
 ↓
validate
 ↓
process
 ↓
update order
 ↓
delete message
```

Failure:

```text
process fails
 ↓
don't delete
 ↓
SQS retry
```

Repeated failure:

```text
DLQ
```

---

## 84. Phase 3 — Docker

Build:

```text
api image
worker image
```

Run:

```text
API
Worker
PostgreSQL
Redis
```

using Compose.

At this point:

> The entire application works without AWS.

This is important.

Cloud should not hide broken application logic.

---

## 85. Phase 4 — CI

Every push:

```text
install
 ↓
lint
 ↓
typecheck
 ↓
test
 ↓
build
 ↓
Docker build
```

Then:

```text
push image to ECR
```

---

## 86. Phase 5 — Terraform

Provision:

```text
VPC
EKS
RDS
Redis
SQS
S3
ECR
IAM
```

Use:

```text
modules
variables
outputs
remote state
```

---

## 87. Phase 6 — Kubernetes

Deploy:

```text
API
Worker
ConfigMap
Secrets
Services
HPA
```

Add:

```text
readiness
liveness
resources
rolling deployment
```

---

## 88. Phase 7 — Helm

Convert raw YAML:

```text
deployment.yaml
service.yaml
hpa.yaml
```

into:

```text
Helm Chart
```

Then:

```text
values-dev.yaml
values-prod.yaml
```

---

## 89. Phase 8 — GitOps

ArgoCD:

```text
GitOps repository
       ↓
ArgoCD
       ↓
EKS
```

Now deployment state is controlled through Git.

---

## 90. Phase 9 — Observability

Add:

```text
structured logs
metrics
traces
dashboards
alerts
```

Then test:

```text
pod failure
DB latency
Redis failure
queue backlog
bad deployment
```

---

## 91. Phase 10 — Load Testing

Use realistic traffic:

```text
GET /products
POST /orders
GET /orders/:id
```

Measure:

```text
RPS
p50
p95
p99
5xx
CPU
memory
DB
Redis
queue
```

Find the bottleneck.

Then optimize it.

---

## 92. Phase 11 — Security

Perform:

```text
secret scanning
dependency scanning
container scanning
IAM review
network review
```

Verify:

```text
no public RDS
no hardcoded secrets
no privileged containers
least privilege IAM
HTTPS
authentication
rate limiting
```

---

## 93. Phase 12 — Failure Engineering

Intentionally:

```text
kill API pod
kill worker
make Redis unavailable
make DB slow
create queue backlog
deploy broken version
generate traffic spike
```

Then document:

```text
what happened
how it was detected
how it recovered
what you changed
```

This turns the project into something you can defend deeply in an interview.

---

## 94. What Goes on Your Resume?

Eventually, something like:

> **Production-Grade Distributed Order Processing Platform**  
> Built a TypeScript/Node.js backend using PostgreSQL, Redis and asynchronous SQS workers; containerized services with Docker and deployed them to AWS EKS using Terraform, Helm and ArgoCD, with GitHub Actions CI/CD, autoscaling, structured observability, idempotent processing, retry/DLQ handling and production failure testing.

The exact resume wording should wait until we've actually built it.

Don't claim technologies you haven't implemented.

---

## 95. What an Interviewer Can Ask

This project creates excellent interview questions.

#### Architecture

> Why did you use SQS?

#### Database

> Why PostgreSQL instead of DynamoDB?

#### Cache

> What happens when Redis goes down?

#### Scaling

> What happens when Kubernetes scales from 3 to 20 pods?

#### Reliability

> What happens if the worker crashes?

#### Messaging

> Can the same SQS message be processed twice?

#### Security

> How does EKS access AWS services?

#### CI/CD

> How does code reach production?

#### GitOps

> Why ArgoCD?

#### Infrastructure

> Why Terraform?

#### Kubernetes

> Why Deployment rather than bare Pods?

#### Networking

> Why is RDS private?

#### Observability

> How do you know a deployment caused an outage?

#### Performance

> What happens if traffic increases 10×?

#### Database

> What happens if all DB connections are exhausted?

#### Deployment

> How would you rollback?

#### DR

> What happens if an Availability Zone fails?

These are exactly the kinds of questions that expose whether someone actually understands their project.

---

## 96. The Most Important Part

Don't treat this as:

```text
"one project I need to finish."
```

Treat it as your:

> **Cloud + DevOps laboratory.**

Every technology you've learned should appear somewhere meaningful.

```text
Linux
   ↓
Docker
   ↓
Git
   ↓
CI/CD
   ↓
AWS
   ↓
Terraform
   ↓
Kubernetes
   ↓
Helm
   ↓
ArgoCD
   ↓
Observability
   ↓
SRE
```

Everything connects.

---

## 97. Final Capstone Architecture

Your mental picture should now be:

```text
                           USERS
                             │
                             ▼
                         Route 53
                             │
                             ▼
                        CloudFront
                             │
                             ▼
                           WAF
                             │
                             ▼
                           ALB
                             │
                             ▼
                    ┌─────────────────┐
                    │       EKS       │
                    │                 │
                    │  API Pods       │
                    │  Worker Pods    │
                    │                 │
                    └───────┬─────────┘
                            │
            ┌───────────────┼─────────────────┐
            │               │                 │
            ▼               ▼                 ▼
        PostgreSQL        Redis              SQS
           RDS          ElastiCache            │
                                               ▼
                                            Workers
                                               │
                                               ▼
                                               S3


      ───────────── INFRASTRUCTURE ─────────────

                 Terraform
                    │
                    ▼
             AWS Infrastructure


      ───────────── DELIVERY ─────────────

Developer
    │
    ▼
 GitHub
    │
    ▼
GitHub Actions
    │
    ├── Tests
    ├── Build
    ├── Scan
    └── Docker
          │
          ▼
         ECR
          │
          ▼
      GitOps Repo
          │
          ▼
        ArgoCD
          │
          ▼
         EKS


      ─────────── OBSERVABILITY ───────────

API / Worker / Kubernetes
          │
    ┌─────┼─────┐
    ▼     ▼     ▼
  Logs  Metrics Traces
    │     │     │
    └─────┼─────┘
          ▼
     Dashboards
          │
          ▼
        Alerts
          │
          ▼
       Incident
```

---

## 98. What You've Now Learned

At this point, your Cloud + DevOps curriculum has moved through:

```text
Cloud Fundamentals          ✅
Linux                        ✅
Bash                         ✅
Networking                   ✅
Git                          ✅
CI/CD                        ✅
Docker                       ✅
AWS                          ✅
EC2                          ✅
S3                           ✅
VPC                          ✅
RDS                          ✅
Load Balancing               ✅
Lambda                       ✅
Route53                      ✅
CloudFront                   ✅
WAF                          ✅
CloudWatch                   ✅
Kubernetes                   ✅
Terraform                    ✅
Observability                ✅
SRE                          ✅
Helm                         ✅
GitOps                       ✅
ArgoCD                       ✅
Jenkins                      ✅
Ansible                      ✅
CRDs/Operators               ✅
Service Mesh/Istio           ✅
Advanced EKS                 ✅
Advanced Terraform           ✅
Advanced AWS                 ✅
Advanced SRE                 ✅
```

And now:

```text
Production Capstone          ✅
```

**Important:** the capstone architecture is designed and specified here; the actual implementation will be done step-by-step rather than pretending it has already been built.
<!-- SOURCE-END -->

---

## Editorial supplement

> **Added by the knowledge-base editor — not part of the original source.** It fills gaps the source leaves open (for example concepts named in the interview list but never explained, or configuration the chapter only describes in words). Treat the text above as the original material and this section as clearly separated additions.

### From design to a runnable starter

This chapter is a **design walkthrough**: architecture diagrams, a repository layout, reliability reasoning, failure scenarios and a build order — but it contains no complete application, and the source conversation stopped here (the promised Response 36 was never produced). To make the chapter usable as practice, the repository includes an **editorial reference starter**: [`code-examples/capstone/`](../../code-examples/capstone/README.md).

| Chapter section | Where it is implemented in the starter |
|---|---|
| §9–11 data model, order states, idempotency | `db/init.sql` (`UNIQUE(idempotency_key)`), `prisma/schema.prisma`, `POST /orders` in `src/api.ts` |
| §14–15 cache-aside, cache failure | `GET /orders/:id` — Redis errors fall through to PostgreSQL |
| §16–21 SQS, visibility timeout, DLQ, worker idempotency | `src/worker.ts` (conditional `UPDATE … WHERE status='PENDING'`; message deleted only after success) |
| §22–26 Docker, local development | `Dockerfile`, `docker-compose.yml`, `.env.example` |
| §27–30 health endpoints, graceful shutdown | `/health/live`, `/health/ready`, SIGTERM handler |
| §32–38 Kubernetes Deployment, probes, requests/limits, HPA | `deploy/api.yaml` |
| §18, §39 worker scaling, connection math | `deploy/worker-keda.yaml`, `DB_POOL_MAX` in `src/config.ts` |
| §48–52 CI, SHA tags, ECR, OIDC | `ci/ci.yml` |

**What is deliberately missing** (and is the learning value): the transactional outbox for the DB-write + queue-send gap, authentication, metrics and tracing, tests, Terraform, the Helm chart and the ArgoCD `Application`. Chapter 33 (outbox/saga), 21/32 (Terraform), 25 (Helm), 26 (ArgoCD) and 22/34 (observability) show how to add each.

**The connection-pool trap from §39, as numbers.** With 20 API Pods and a pool of 20 each, the API alone can open `20 × 20 = 400` connections; a PostgreSQL limit of 200 will reject the surplus. Fix by lowering `DB_POOL_MAX`, adding RDS Proxy/PgBouncer, or capping `maxReplicas` — and remember worker replicas (KEDA may scale to 20) also hold connections.

**Honest status.** The starter's TypeScript passes `tsc --noEmit` and builds, and its YAML parses; it has not been run end to end, so expect to debug the first `docker compose up`.

---

**Navigation:** ← [Chapter 34: Advanced SRE](../07-observability-sre/ch34-advanced-sre.md) · [Chapter 36: Virtualization Internals — Deep Dive](../01-foundations/ch36-virtualization-internals.md) → · [Revision sheet](../../revision/ch35-revision.md)
