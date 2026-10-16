# Chapter 23 — Production Architecture + Troubleshooting

> **Source:** Response 23 of the original conversation (`source-archive/src-23.txt`, lines 1–1924) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch23-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

This is the **integration response**.

You've learned the individual pieces. Now we're going to think like a backend/SWE engineer who is responsible for getting an application from:

```text
Code
 ↓
GitHub
 ↓
CI/CD
 ↓
Docker
 ↓
AWS
 ↓
Production
```

and keeping it alive when things go wrong.

The goal is **not** to memorize one architecture. The goal is to understand **why each component exists and what you would change when requirements change.**

---

## 1. Our Production Application

Let's use a realistic application:

> **TypeScript + Node.js backend API**

Suppose it provides:

```text
POST /users
POST /orders
GET /orders/:id
POST /payments
POST /files
```

Technologies:

```text
TypeScript
Node.js
PostgreSQL
Redis
Docker
AWS
Kubernetes
Terraform
GitHub Actions
```

---

## 2. Complete Production Architecture

Here's the architecture we'll reason through:

```text
                             INTERNET
                                │
                                ↓
                            Route 53
                                │
                                ↓
                           CloudFront
                                │
                                ↓
                              WAF
                                │
                                ↓
                         Load Balancer
                                │
                                ↓
                         EKS / Kubernetes
                                │
                    ┌───────────┼───────────┐
                    ↓           ↓           ↓
                  Pod A       Pod B       Pod C
                    │           │           │
                    └───────────┼───────────┘
                                │
                  ┌─────────────┼─────────────┐
                  ↓             ↓             ↓
                Redis         RDS           S3
                              PostgreSQL
```

Supporting infrastructure:

```text
GitHub
   ↓
GitHub Actions
   ↓
Docker Build
   ↓
ECR
   ↓
EKS
```

Infrastructure:

```text
Terraform
   ↓
AWS
   ├── VPC
   ├── Subnets
   ├── IAM
   ├── EKS
   ├── RDS
   ├── S3
   └── Load Balancer
```

Observability:

```text
Application
 ├── Logs
 ├── Metrics
 └── Traces
        ↓
Observability platform
        ↓
Dashboards
        ↓
Alerts
```

Now let's understand why.

---

## PART 1 — NETWORK ARCHITECTURE

### 3. VPC

Our AWS environment starts with:

```text
VPC
```

Example:

```text
10.0.0.0/16
```

Inside:

```text
VPC
│
├── Public Subnets
│
└── Private Subnets
```

Across multiple Availability Zones:

```text
                VPC
        ┌────────┴────────┐
        ↓                 ↓
       AZ-A              AZ-B
        │                 │
   Public subnet     Public subnet
   Private subnet    Private subnet
```

Multiple AZs improve availability.

---

## 4. What Goes Where?

A simplified production arrangement:

```text
Public
├── Load Balancer
└── NAT Gateway

Private
├── EKS worker capacity
├── RDS
└── internal services
```

You don't want your database directly exposed to the public Internet.

So:

```text
Internet
   ❌
   ↓
RDS
```

Instead:

```text
Internet
   ↓
Load Balancer
   ↓
EKS
   ↓
RDS
```

---

## 5. Security Group Architecture

Think in terms of allowed flows.

```text
Internet
   │
   │ HTTPS :443
   ↓
ALB Security Group
   │
   │ application traffic
   ↓
EKS/API Security Group
   │
   │ PostgreSQL :5432
   ↓
RDS Security Group
```

Conceptually:

```text
Internet → ALB
ALB → API
API → RDS
API → Redis
```

But:

```text
Internet → RDS ❌
```

This is **least privilege at the network level**.

---

## PART 2 — DNS + HTTPS

### 6. Route 53

User enters:

```text
https://api.example.com
```

DNS needs to determine where the request goes.

Conceptually:

```text
api.example.com
       ↓
Route 53
       ↓
CloudFront / Load Balancer
```

---

## 7. TLS

The user should communicate over:

```text
HTTPS
```

not:

```text
HTTP
```

TLS protects the connection in transit.

AWS services such as ACM can manage certificates for appropriate AWS-integrated endpoints.

So:

```text
Client
 ↓ HTTPS
Edge/load-balancing layer
 ↓
Application
```

---

## PART 3 — CLOUDFRONT + WAF

### 8. CloudFront

For cacheable content:

```text
User
 ↓
CloudFront Edge
 ↓
Origin
```

Good candidates include:

```text
images
JavaScript
CSS
static files
```

Don't blindly cache:

```text
POST /payment
GET /account
private user-specific responses
```

Caching strategy depends on the application's semantics.

---

## 9. WAF

WAF can inspect HTTP requests and apply rules.

For example:

```text
Internet
 ↓
WAF
 ↓
Application
```

Possible protections include:

```text
rate limiting
managed attack rules
IP-based rules
request filtering
```

WAF is one layer of defense.

It's not a replacement for:

```text
IAM
Security Groups
application authorization
input validation
```

---

## PART 4 — LOAD BALANCING

### 10. Load Balancer

Suppose:

```text
3 Pods
```

We don't want the user to know their individual IP addresses.

Traffic goes through a stable entry point:

```text
Client
 ↓
Load Balancer
 ↓
Kubernetes networking
 ↓
Pods
```

The load-balancing layer distributes requests across eligible healthy backends.

---

## 11. Health Checks

Suppose:

```text
Pod A → healthy
Pod B → unhealthy
Pod C → healthy
```

The routing layer should avoid sending normal traffic to unhealthy backends.

This is why we learned:

```text
/health
/ready
```

Earlier.

---

## PART 5 — KUBERNETES

### 12. EKS

AWS manages the Kubernetes control-plane service through:

```text
EKS
```

Your workloads run as Kubernetes workloads.

Conceptually:

```text
EKS
│
├── Node
│    ├── Pod
│    └── Pod
│
├── Node
│    ├── Pod
│    └── Pod
│
└── Node
     └── Pod
```

---

## 13. Deployment

Our API might use:

```yaml
replicas: 3
```

So:

```text
Deployment
   ↓
3 Pods
```

If one dies:

```text
3 desired
2 actual
   ↓
replacement
   ↓
3 actual
```

That's self-healing.

---

## 14. Kubernetes Service

Our API Pods are behind a Service:

```text
Load Balancer
     ↓
Service
     ↓
┌────┼────┐
↓    ↓    ↓
Pod  Pod  Pod
```

The Service provides stable discovery while Pods remain replaceable.

---

## 15. Configuration

We don't bake production configuration into our Docker image.

Instead:

```text
ConfigMap
    ↓
Pod

Secret / external secret system
    ↓
Pod
```

Application:

```ts
const port = Number(process.env.PORT ?? 3000);
const databaseUrl = process.env.DATABASE_URL;
```

Same application image can run in:

```text
development
staging
production
```

with different configuration.

---

## PART 6 — DATABASE

### 16. RDS PostgreSQL

Our API needs relational data.

Use:

```text
RDS PostgreSQL
```

rather than making your API container responsible for database persistence.

Architecture:

```text
API Pods
   │
   ↓
RDS PostgreSQL
```

---

## 17. Connection Pooling

Suppose:

```text
10 API Pods
```

and each creates:

```text
100 DB connections
```

Potentially:

```text
10 × 100 = 1000 connections
```

Your database may not support that workload.

So connection pooling and appropriate pool sizing matter.

This is a classic production scaling problem.

---

## 18. Redis

Redis can be used for things such as:

```text
caching
sessions
rate limiting
short-lived state
queues
```

Example:

```text
Request
 ↓
API
 ↓
Redis
 ↓
cache hit
```

instead of:

```text
Request
 ↓
API
 ↓
RDS
```

every time.

But don't cache everything.

Caching introduces:

```text
invalidation
consistency
memory
TTL
failure
```

tradeoffs.

---

## PART 7 — S3

Suppose users upload:

```text
profile.jpg
invoice.pdf
video.mp4
```

Don't put large objects directly inside PostgreSQL.

Use:

```text
S3
```

Architecture:

```text
User
 ↓
API
 ↓
S3
```

Often the backend can generate a presigned URL:

```text
Backend
 ↓
Presigned URL
 ↓
Client
 ↓
S3
```

This can reduce unnecessary application-server bandwidth.

---

## PART 8 — DOCKER

### 19. Application Image

Our Node application gets packaged:

```text
Dockerfile
   ↓
Docker image
```

Example production structure:

```dockerfile
FROM node:22 AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build


FROM node:22-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

COPY --from=build /app/dist ./dist

USER node

EXPOSE 3000

CMD ["node", "dist/server.js"]
```

Important production principles:

```text
multi-stage build
small runtime image
production dependencies
non-root user
no secrets in image
```

---

## 20. Image Registry

We don't expect every Kubernetes node to have the image already.

Push it to:

```text
ECR
```

Flow:

```text
Docker build
    ↓
ECR
    ↓
EKS
    ↓
Pod
```

---

## PART 9 — CI/CD

### 21. GitHub Actions

Developer:

```bash
git push
```

Pipeline:

```text
GitHub
   ↓
GitHub Actions
   ├── checkout
   ├── npm ci
   ├── lint
   ├── typecheck
   ├── tests
   ├── build
   ├── Docker build
   ├── Docker scan
   └── push image
```

Then deployment proceeds through the chosen deployment mechanism.

---

## 22. Image Tagging

Don't rely only on:

```text
latest
```

Prefer immutable/versioned identifiers.

For example:

```text
my-api:8f31a7c
```

where the identifier corresponds to a Git commit.

Then:

```text
Git commit
 ↓
Docker image
 ↓
ECR
 ↓
Kubernetes
```

You can determine exactly what code is running.

---

## 23. Deployment

Conceptually:

```text
ECR
 ↓
Kubernetes Deployment
 ↓
new Pods
 ↓
readiness checks
 ↓
traffic
```

If the deployment is bad:

```bash
kubectl rollout undo deployment/api
```

Rollback becomes much easier when images are immutable.

---

## PART 10 — TERRAFORM

### 24. Infrastructure as Code

Instead of manually creating:

```text
VPC
EKS
RDS
S3
IAM
```

Terraform manages them.

```text
Terraform
   ↓
AWS APIs
   ↓
Infrastructure
```

The repository might look like:

```text
infra/
├── main.tf
├── variables.tf
├── outputs.tf
└── modules/
    ├── network/
    ├── eks/
    └── database/
```

---

## 25. Infrastructure Pipeline

```text
Pull Request
    ↓
Terraform fmt
    ↓
Terraform validate
    ↓
Terraform plan
    ↓
Review
    ↓
Merge
    ↓
Controlled apply
```

This prevents random manual infrastructure changes.

---

## PART 11 — OBSERVABILITY

### 26. Application Monitoring

Every request should generate useful telemetry.

Example:

```json
{
  "level": "info",
  "event": "request_completed",
  "requestId": "abc123",
  "method": "GET",
  "path": "/orders/123",
  "statusCode": 200,
  "durationMs": 84
}
```

Now you have:

```text
Logs
Metrics
Traces
```

---

## 27. Metrics

Monitor:

```text
request rate
error rate
p50 latency
p95 latency
p99 latency
CPU
memory
Pod restarts
database connections
Redis latency
queue depth
```

For APIs:

```text
RED
│
├── Rate
├── Errors
└── Duration
```

is an excellent starting framework.

---

## 28. Alerts

Don't alert on everything.

Meaningful examples:

```text
5xx rate > threshold
p95 latency > threshold
RDS connections near limit
disk/storage pressure
Pods repeatedly restarting
queue backlog growing
```

Alerts should correspond to something actionable.

---

## PART 12 — NOW LET'S BREAK THE SYSTEM

This is arguably the most important part of Chapter 23.

A production engineer isn't judged only by whether they can build the happy path.

They need to diagnose failures.

---

## 🔥 Incident 1 — API Returns 503

User reports:

```text
"API is down."
```

Don't randomly restart Pods.

Start:

```bash
kubectl get pods
```

Suppose:

```text
api-a   Running
api-b   Running
api-c   CrashLoopBackOff
```

Then:

```bash
kubectl logs api-c
```

You discover:

```text
DATABASE_URL is undefined
```

Now inspect:

```bash
kubectl describe pod api-c
```

Maybe the Secret wasn't correctly mounted/injected.

Root cause:

```text
Secret/configuration problem
```

Not Kubernetes itself.

---

## 🔥 Incident 2 — All Pods Running, API Still Returns 503

Now:

```text
Pods = Running
```

But requests fail.

Check:

```bash
kubectl get svc
```

Then:

```bash
kubectl get endpointslices
```

Suppose:

```text
API Service
Endpoints = none
```

Check the Service selector:

```yaml
selector:
  app: api
```

Pods:

```yaml
labels:
  app: backend
```

Mismatch.

Therefore:

```text
Service
   ↓
selector doesn't match Pods
   ↓
no endpoints
```

Fix the labels/selectors.

This is a classic Kubernetes issue.

---

## 🔥 Incident 3 — Pods Are Healthy but Requests Are Slow

Metrics:

```text
CPU = 30%
Memory = 40%
```

So you don't immediately scale.

Check traces:

```text
API        20ms
Redis      15ms
RDS     1800ms
```

Database is taking:

```text
1.8 seconds
```

Investigate:

```text
slow queries
missing indexes
connection pool
locks
database load
```

The problem isn't Kubernetes.

It's the database path.

---

## 🔥 Incident 4 — RDS Connection Exhaustion

Metrics:

```text
RDS connections = 100%
```

API Pods:

```text
3 → 10
```

Potential explanation:

```text
Pods increased
 ↓
each Pod created a connection pool
 ↓
total connections increased
 ↓
RDS exhausted
```

Possible remedies depend on the architecture:

```text
reduce pool size
use connection pooling/proxying
optimize DB usage
scale DB appropriately
limit application concurrency
```

This is why:

> **Scaling the API does not automatically mean the whole system scales.**

Always look for the bottleneck.

---

## 🔥 Incident 5 — ImagePullBackOff

Deployment:

```text
ImagePullBackOff
```

Debug:

```bash
kubectl describe pod <pod>
```

Check:

```text
image name
tag
registry
permissions
image existence
```

Pipeline:

```text
GitHub Actions
 ↓
Docker build
 ↓
ECR push
 ↓
Kubernetes
```

Maybe CI pushed:

```text
my-api:abc123
```

but Kubernetes requests:

```text
my-api:abc124
```

Simple tag mismatch.

---

## 🔥 Incident 6 — Deployment Works but New Pods Receive No Traffic

Check:

```text
readiness probe
```

Maybe:

```text
/ready
```

returns:

```text
503
```

because the database connection isn't ready.

Therefore:

```text
Pod = Running
Pod = not Ready
```

This distinction is extremely important:

```text
Running ≠ Ready
```

---

## 🔥 Incident 7 — HPA Isn't Scaling

You observe:

```text
CPU = 90%
```

but:

```text
replicas = 2
```

Check:

```bash
kubectl get hpa
```

Then:

```bash
kubectl describe hpa api-hpa
```

Potential issue:

```text
metrics unavailable
```

or:

```text
resource requests aren't configured correctly
```

or:

```text
maxReplicas already reached
```

Never assume HPA is broken before checking its metrics and events.

---

## 🔥 Incident 8 — Database Is Fine, API Is Fine, Users Still Can't Connect

Check DNS.

```bash
dig api.example.com
```

Then:

```bash
curl -v https://api.example.com/health
```

Potential problem:

```text
DNS record
 ↓
wrong target
```

or:

```text
TLS certificate
 ↓
configuration issue
```

or:

```text
WAF
 ↓
request blocked
```

This demonstrates why troubleshooting must happen **layer by layer**.

---

## PART 13 — THE TROUBLESHOOTING MODEL

When something breaks, think:

```text
                    INCIDENT
                       │
                       ↓
                   DNS / TLS
                       │
                       ↓
                   WAF / Edge
                       │
                       ↓
                Load Balancer
                       │
                       ↓
                 Kubernetes
                       │
             ┌─────────┼─────────┐
             ↓         ↓         ↓
           Pod      Service    Ingress
             │
             ↓
          Container
             │
             ↓
        Node.js app
             │
       ┌─────┼─────┐
       ↓     ↓     ↓
      Redis RDS   S3
```

At every layer ask:

> **Is this layer healthy?**

---

## 29. Layer-by-Layer Commands

#### DNS

```bash
dig api.example.com
```

#### HTTP/TLS

```bash
curl -v https://api.example.com/health
```

#### Kubernetes

```bash
kubectl get pods
kubectl get svc
kubectl get ingress
```

#### Pod details

```bash
kubectl describe pod <pod>
```

#### Logs

```bash
kubectl logs <pod>
```

#### Previous crashed container

```bash
kubectl logs <pod> --previous
```

#### Service endpoints

```bash
kubectl get endpointslices
```

#### Resource usage

```bash
kubectl top pods
kubectl top nodes
```

#### Deployment

```bash
kubectl rollout status deployment/api
```

#### Rollback

```bash
kubectl rollout undo deployment/api
```

#### AWS

Use the relevant AWS console/CLI/CloudWatch metrics to inspect:

```text
ALB
EKS
RDS
Lambda
S3
CloudWatch
```

---

## PART 14 — A REAL DEPLOYMENT FAILURE

Let's simulate an entire incident.

Suppose you deploy:

```text
v2
```

Immediately:

```text
5xx ↑
```

What do you do?

#### Step 1

Check deployment:

```bash
kubectl rollout status deployment/api
```

#### Step 2

Check Pods:

```bash
kubectl get pods
```

#### Step 3

Logs:

```bash
kubectl logs <pod>
```

Suppose:

```text
Redis connection refused
```

#### Step 4

Check Redis.

```text
Redis unavailable
```

#### Step 5

Could v2 be responsible?

Maybe the new application version changed:

```text
REDIS_URL
```

or authentication.

#### Step 6

If production impact is severe:

```bash
kubectl rollout undo deployment/api
```

#### Step 7

Verify:

```text
5xx ↓
latency ↓
requests successful
```

#### Step 8

Investigate the root cause.

This is:

```text
Detect
 ↓
Diagnose
 ↓
Mitigate
 ↓
Recover
 ↓
Root Cause Analysis
```

---

## PART 15 — ROLLBACK VS ROLLFORWARD

An important engineering decision.

Sometimes:

```text
Rollback
```

is fastest.

Other times:

```text
Fix forward
```

is safer.

For example:

```text
Security vulnerability in v1
```

Rolling back to v1 might be dangerous.

So:

> **Rollback isn't automatically the right answer.**

You need to understand what changed and the risk of each option.

---

## PART 16 — AVAILABILITY

Suppose:

```text
one EC2
one AZ
one database
```

Failure:

```text
EC2 dies
```

Application:

```text
DOWN
```

More resilient:

```text
           Load Balancer
            /         \
           ↓           ↓
        AZ-A          AZ-B
         Pod           Pod
           \           /
             RDS
```

Now one application instance can fail without necessarily taking down the entire service.

But availability isn't free.

You introduce:

```text
more infrastructure
more complexity
more cost
```

This is why architecture is about **tradeoffs**.

---

## PART 17 — COST THINKING

Suppose someone says:

> "Let's use EKS for our tiny internal CRUD application."

You should ask:

```text
Why?
```

Kubernetes can be powerful, but it introduces:

```text
cluster complexity
networking complexity
monitoring
upgrades
security
operational overhead
```

For a simple service:

```text
ECS/Fargate
EC2 + Docker
Lambda
```

may sometimes be simpler depending on requirements.

You shouldn't use Kubernetes simply because it appears on your resume.

For interviews, explain **why you chose it**.

---

## PART 18 — WHEN TO USE WHAT?

A useful decision framework:

| Requirement | Possible choice |
|---|---|
| Simple long-running API | EC2/ECS |
| Containerized workload | Docker |
| Many containers + orchestration | Kubernetes |
| AWS-managed Kubernetes | EKS |
| Event-driven short task | Lambda |
| Object storage | S3 |
| Relational database | RDS |
| Cache | Redis |
| Async jobs | SQS |
| Pub/sub notifications | SNS |
| CDN | CloudFront |
| DNS | Route 53 |
| HTTP filtering | WAF |
| Infrastructure as Code | Terraform |
| Metrics | Prometheus/CloudWatch |
| Dashboards | Grafana |
| Distributed traces | OpenTelemetry-compatible stack |

The answer is always dependent on requirements.

---

## PART 19 — COMPLETE DEVOPS LIFECYCLE

You can now describe the complete lifecycle:

```text
                  CODE
                   │
                   ↓
                  Git
                   │
                   ↓
                GitHub
                   │
                   ↓
            GitHub Actions
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
      Tests      Build      Security
                   │
                   ↓
                 Docker
                   │
                   ↓
                  ECR
                   │
                   ↓
              Kubernetes
                   │
                   ↓
                Deploy
                   │
                   ↓
               Production
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
      Logs       Metrics     Traces
        │          │          │
        └──────────┼──────────┘
                   ↓
              Monitoring
                   │
                   ↓
                 Alert
                   │
                   ↓
             Investigation
                   │
                   ↓
              Fix / Rollback
                   │
                   ↓
               Recovery
```

Infrastructure:

```text
Terraform
   ↓
AWS
```

That's the complete picture.

---

## PART 20 — THE INTERVIEW QUESTION YOU SHOULD NOW BE ABLE TO ANSWER

> **"How would you deploy a production Node.js application?"**

A strong answer would sound roughly like:

```text
I would containerize the Node.js application using a
multi-stage Docker build and push immutable images to a
container registry such as ECR.

I would run the application using a managed container
platform such as EKS if Kubernetes is justified by the
requirements.

The application would run as multiple stateless Pods behind
a Kubernetes Service and an external load balancer.

The infrastructure would be provisioned with Terraform.

I'd keep PostgreSQL in RDS, object files in S3, and use Redis
where caching or shared ephemeral state is appropriate.

I'd keep the database private and restrict network access
using security groups and Kubernetes networking controls.

CI/CD would run tests, build the application, build and scan
the container image, push it to ECR, and deploy the selected
image version.

I'd use readiness and liveness probes, resource requests and
limits, HPA where appropriate, and rolling deployments.

For observability, I'd collect structured logs, metrics, and
distributed traces, with alerts based on meaningful service
health indicators.

If something failed, I'd troubleshoot from the outside in:
DNS/TLS → WAF/load balancer → Kubernetes Service/Ingress →
Pods → application → Redis/RDS/S3.
```

That's the level of answer we're aiming for.

---

## 🔥 THE MOST IMPORTANT LESSON OF RESPONSE 23

Don't think:

```text
"I know AWS."
"I know Kubernetes."
"I know Docker."
"I know Terraform."
```

Think:

```text
                    SYSTEM
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
   Application     Infrastructure  Operations
        │             │             │
     Node.js        AWS/K8s       Monitoring
     Docker        Terraform      Reliability
     Database        Network      Debugging
```

The valuable skill is knowing:

> **How these technologies interact.**

That's what turns a list of technologies on a resume into actual engineering knowledge.
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 22: Observability + Reliability](../07-observability-sre/ch22-observability-reliability.md) · [Chapter 24: Complete Cloud + DevOps Interview & OA Mastery](../09-interview/ch24-interview-oa-mastery.md) → · [Revision sheet](../../revision/ch23-revision.md)
