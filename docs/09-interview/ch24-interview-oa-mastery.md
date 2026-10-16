# Chapter 24 — Complete Cloud + DevOps Interview & OA Mastery

> **Source:** Response 24 of the original conversation (`source-archive/src-24.txt`, lines 1–2173) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch24-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

This is the **final response of the 24-response roadmap**.

The objective now is not to learn another giant technology.

It's to make sure you can take everything we've covered and **actually use it, explain it, troubleshoot it, and answer interview/OA questions from it.**

---

## 1. Your Complete Cloud + DevOps Map

You should now see DevOps as one connected system:

```text
                         DEVELOPER
                             │
                             ↓
                           Git
                             │
                             ↓
                          GitHub
                             │
                             ↓
                      GitHub Actions
                       /           \
                      ↓             ↓
                 Application      Terraform
                    CI/CD             │
                      │               ↓
                      ↓              AWS
                    Docker       ┌────┼─────┐
                      │          ↓    ↓     ↓
                      ↓         VPC  EKS   RDS
                     ECR          │    │
                      │           │    ↓
                      └───────────┘   Pods
                                      │
                         ┌────────────┼────────────┐
                         ↓            ↓            ↓
                       Redis         RDS          S3
                         
                             ↓
                       Observability
                    ┌────────┼────────┐
                    ↓        ↓        ↓
                  Logs    Metrics   Traces
                    │        │        │
                    └────────┼────────┘
                             ↓
                         Dashboards
                             ↓
                           Alerts
                             ↓
                      Incident Response
```

That is the big picture.

---

## 2. What "DevOps" Means for You

For your SWE/backend career, don't define DevOps as:

> "Knowing Docker and Kubernetes."

Your practical definition should be:

> **The practices and tooling used to reliably build, test, package, deploy, operate, monitor, and troubleshoot software and infrastructure.**

That includes:

```text
Code
 ↓
Version control
 ↓
CI
 ↓
Testing
 ↓
Build
 ↓
Containerization
 ↓
Infrastructure
 ↓
Deployment
 ↓
Monitoring
 ↓
Reliability
 ↓
Troubleshooting
```

---

## PART 1 — LINUX MASTER CHECKLIST

You should be comfortable with:

#### Filesystem

```bash
pwd
ls
cd
mkdir
touch
cp
mv
rm
cat
less
```

#### Permissions

```bash
chmod
chown
```

Understand:

```text
r = read
w = write
x = execute
```

and:

```text
755
644
```

#### Processes

```bash
ps
top
kill
```

Understand:

```text
PID
SIGTERM
SIGKILL
SIGINT
```

#### Disk/memory

```bash
df
du
free
```

#### Networking

```bash
ip
ss
ping
curl
```

#### Logs

```bash
journalctl
tail
grep
```

#### Remote access

```bash
ssh
```

#### Services

```bash
systemctl
```

---

## 3. Linux Interview Scenario

#### Question:

> A server is responding very slowly. What do you check?

A reasonable investigation:

```text
CPU
 ↓
Memory
 ↓
Disk
 ↓
Processes
 ↓
Network
 ↓
Application logs
 ↓
Dependencies
```

Commands:

```bash
top
free -h
df -h
ps aux
ss -tulpn
tail -f app.log
```

Don't blindly restart the server.

---

## PART 2 — BASH

You should be able to write scripts involving:

```bash
#!/bin/bash

set -euo pipefail

if curl -fsS http://localhost:3000/health; then
    echo "API healthy"
else
    echo "API unhealthy"
    exit 1
fi
```

Understand:

```text
variables
arguments
conditions
loops
functions
exit codes
pipes
redirection
cron
```

Especially:

```bash
$?
$1
$@
```

and:

```bash
set -euo pipefail
```

---

## 4. Bash Interview Question

> Why use `set -euo pipefail`?

Simplified:

```text
-e → stop on many command failures
-u → catch unset variables
-o pipefail → pipeline fails if an earlier command fails
```

It helps make scripts fail more predictably.

---

## PART 3 — NETWORKING

This is one of the highest-value DevOps topics for SWE interviews.

You should understand:

```text
IP
Subnet
CIDR
Port
Socket
TCP
UDP
DNS
HTTP
HTTPS
TLS
NAT
Routing
Firewall
Proxy
Load Balancer
```

---

## 5. TCP vs UDP

#### TCP

```text
connection-oriented
reliable
ordered
```

#### UDP

```text
connectionless
no built-in delivery guarantee
lower overhead
```

Don't simply say:

> TCP is faster than UDP.

That's an oversimplification.

---

## 6. DNS Flow

When you request:

```text
https://api.example.com
```

conceptually:

```text
Browser
 ↓
DNS resolver
 ↓
DNS hierarchy
 ↓
IP address
 ↓
TCP/TLS
 ↓
HTTP request
```

Know:

```text
A
AAAA
CNAME
MX
TXT
NS
```

---

## 7. HTTP

Know:

```text
GET
POST
PUT
PATCH
DELETE
```

and status families:

```text
2xx → success
3xx → redirection
4xx → client/request problem
5xx → server-side failure
```

Especially:

```text
200
201
204
400
401
403
404
409
429
500
502
503
504
```

---

## 8. Debugging Network Connectivity

If:

```text
curl http://server:3000
```

fails:

Think:

```text
DNS?
 ↓
IP?
 ↓
Route?
 ↓
Firewall / SG?
 ↓
Port?
 ↓
Process listening?
 ↓
Application?
```

Useful commands:

```bash
dig example.com
curl -v https://example.com
ss -lntp
ip route
ping
```

---

## PART 4 — GIT

You should confidently understand:

```text
working directory
 ↓
staging
 ↓
commit
 ↓
branch
 ↓
remote
```

Commands:

```bash
git status
git add
git commit
git log
git diff
git fetch
git pull
git push
git branch
git switch
git merge
git rebase
git stash
git cherry-pick
git reset
git revert
git reflog
```

---

## 9. Reset vs Revert

Very common interview question.

#### Reset

Moves branch/history references.

Potentially rewrites local history.

```text
git reset
```

#### Revert

Creates a new commit that reverses an earlier commit.

```text
git revert
```

For shared public history:

```text
revert
```

is often safer than rewriting history.

---

## 10. Rebase

Rebase changes the base of commits to produce a different history.

Useful for:

```text
cleaning local feature history
updating a branch
```

Be careful with rebasing commits that other people already depend on.

---

## PART 5 — CI/CD

Know the distinction:

```text
Continuous Integration
→ frequently integrate and test code

Continuous Delivery
→ keep software ready for release

Continuous Deployment
→ automatically deploy qualifying changes
```

Pipeline:

```text
Git push
 ↓
CI
 ↓
Install dependencies
 ↓
Lint
 ↓
Typecheck
 ↓
Tests
 ↓
Build
 ↓
Docker
 ↓
Registry
 ↓
Deployment
```

---

## 11. GitHub Actions

Know:

```text
workflow
event
job
runner
step
action
artifact
secret
environment
```

Basic workflow:

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22

      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test
      - run: npm run build
```

You don't need to memorize the exact YAML.

You need to understand what each part does.

---

## PART 6 — DOCKER

This should now be one of your strongest DevOps areas.

Remember:

```text
Dockerfile
 ↓
Image
 ↓
Container
```

---

## 12. Dockerfile Essentials

Know:

```dockerfile
FROM
WORKDIR
COPY
RUN
ENV
EXPOSE
CMD
ENTRYPOINT
USER
```

Especially:

#### `RUN`

Executed while building the image.

#### `CMD`

Default command when the container starts.

---

## 13. Production Dockerfile

Know why we use:

```text
multi-stage builds
small runtime image
non-root user
.dockerignore
production dependencies
layer caching
immutable tags
```

Example:

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

---

## 14. Docker Debugging

Container isn't working:

```bash
docker ps
docker logs <container>
docker inspect <container>
docker exec -it <container> sh
```

Check:

```text
container running?
port mapping?
application listening on 0.0.0.0?
environment variables?
image?
logs?
network?
```

---

## PART 7 — AWS

You don't need to memorize every AWS service.

You need to understand the **core backend architecture**.

---

## 15. AWS Core Services

```text
IAM
EC2
S3
VPC
RDS
ALB
Auto Scaling
Lambda
SQS
SNS
Route 53
CloudFront
WAF
CloudWatch
CloudTrail
ECR
EKS
Secrets Manager
KMS
```

You should be able to explain what each is for.

---

## 16. IAM

Understand:

```text
User
Group
Role
Policy
Permission
ARN
Least privilege
Temporary credentials
```

Critical concept:

```text
Authentication
≠
Authorization
```

And:

```text
GitHub Actions
 ↓
OIDC
 ↓
IAM Role
 ↓
Temporary credentials
```

is preferable to putting long-lived AWS keys in GitHub secrets when the workflow can use OIDC.

---

## 17. EC2

Know:

```text
AMI
Instance
Instance type
EBS
Security Group
Public/private IP
IAM Role
User Data
IMDS
```

Architecture:

```text
VPC
 ↓
Subnet
 ↓
Security Group
 ↓
EC2
 ↓
Docker
 ↓
Node.js
```

---

## 18. S3

Know:

```text
bucket
object
key
storage class
versioning
lifecycle
encryption
presigned URL
multipart upload
```

Remember:

> **S3 is object storage, not a normal block filesystem.**

---

## 19. VPC

This is extremely important.

Mental model:

```text
VPC
│
├── Subnet
├── Route Table
├── Internet Gateway
├── NAT Gateway
├── Security Group
├── NACL
└── VPC Endpoint
```

Production:

```text
Internet
   ↓
ALB
   ↓
Private application
   ↓
Private RDS
```

---

## 20. RDS

Know:

```text
Multi-AZ
Read Replica
Backup
Snapshot
PITR
Connection Pool
Encryption
Monitoring
```

Critical:

```text
Multi-AZ
→ availability/failover

Read Replica
→ read scaling
```

They solve different problems.

---

## 21. Scaling

Know:

```text
vertical scaling
horizontal scaling
load balancing
Auto Scaling
stateless architecture
```

And:

> **Scaling application servers doesn't necessarily scale the database.**

---

## 22. Lambda + Messaging

Understand:

```text
Lambda
SQS
SNS
```

Architecture:

```text
API
 ↓
SQS
 ↓
Lambda worker
 ↓
Database
```

Know:

```text
visibility timeout
retry
DLQ
idempotency
cold start
concurrency
```

Especially:

> Never assume a message is processed exactly once simply because your application uses a queue.

Design consumers to tolerate duplicate delivery where the system semantics require it.

---

## PART 8 — KUBERNETES

This is another major interview area.

---

## 23. Kubernetes Mental Model

```text
Cluster
│
├── Control Plane
│
└── Worker Nodes
      │
      └── Pods
```

Then:

```text
Deployment
 ↓
ReplicaSet
 ↓
Pods
```

and:

```text
Service
 ↓
Pods
```

---

## 24. Kubernetes Objects

Know:

```text
Pod
Deployment
ReplicaSet
Service
Namespace
ConfigMap
Secret
PV
PVC
StorageClass
Ingress
HPA
Job
CronJob
DaemonSet
StatefulSet
```

You don't need equal depth on all of them.

---

## 25. Kubernetes Networking

Understand:

```text
Pod
 ↓
Service
 ↓
Ingress
 ↓
Load Balancer
```

and:

```text
Service discovery
DNS
ClusterIP
NodePort
LoadBalancer
NetworkPolicy
```

---

## 26. Kubernetes Scaling

Know:

```text
HPA
 ↓
more/fewer Pods
```

versus:

```text
Node autoscaling
 ↓
more/fewer worker nodes
```

Important:

```text
Pod scaling ≠ Node scaling
```

---

## 27. Kubernetes Troubleshooting

This sequence should become automatic:

```bash
kubectl get pods
```

then:

```bash
kubectl describe pod <pod>
```

then:

```bash
kubectl logs <pod>
```

then:

```bash
kubectl logs <pod> --previous
```

then:

```bash
kubectl exec -it <pod> -- sh
```

For services:

```bash
kubectl get svc
kubectl get endpointslices
```

For deployments:

```bash
kubectl rollout status deployment/api
kubectl rollout history deployment/api
kubectl rollout undo deployment/api
```

---

## 28. Kubernetes Failure Table

| Symptom | First things to investigate |
|---|---|
| `Pending` | Scheduling/resources/PVC |
| `CrashLoopBackOff` | Application logs/config |
| `ImagePullBackOff` | Image/tag/registry/auth |
| Running but not Ready | Readiness probe |
| Service has no traffic | Selector/endpoints |
| HPA not scaling | Metrics/resources/config |
| Pod OOMKilled | Memory usage/limits |
| 503 | LB/Service/readiness/backend |
| 502 | Proxy/LB → backend communication |
| DNS failure | DNS/service configuration |

Don't memorize this mechanically.

Learn the reasoning.

---

## PART 9 — TERRAFORM

Know the lifecycle:

```bash
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
terraform destroy
```

And:

```text
Provider
Resource
Variable
Output
Data source
Module
State
Remote state
State locking
Drift
Import
```

---

## 29. Terraform Mental Model

```text
Terraform code
      ↓
Provider
      ↓
Plan
      ↓
Apply
      ↓
Cloud API
      ↓
Infrastructure
      ↓
State
```

---

## 30. Terraform Interview Question

> What happens if someone manually changes infrastructure created by Terraform?

Answer:

```text
Manual change
      ↓
Infrastructure differs
from desired configuration
      ↓
Terraform detects drift during planning
      ↓
Plan proposes reconciliation
```

Then decide whether Terraform should restore the declared configuration or whether the code should be intentionally changed.

---

## PART 10 — OBSERVABILITY

Know:

```text
Logs
Metrics
Traces
```

And:

```text
Prometheus
Grafana
OpenTelemetry
CloudWatch
```

---

## 31. RED

For APIs:

```text
Rate
Errors
Duration
```

Example:

```text
Rate     = 1000 req/s
Errors   = 2%
p95      = 300ms
```

This gives a quick view of service health.

---

## 32. SLI / SLO / SLA

Remember:

```text
SLI
→ measurement

SLO
→ target

SLA
→ formal customer commitment
```

And:

```text
SLO
 ↓
Error Budget
```

---

## PART 11 — RELIABILITY

Know these patterns:

```text
Timeout
Retry
Exponential Backoff
Jitter
Circuit Breaker
Bulkhead
Rate Limiting
Idempotency
Graceful Shutdown
```

---

## 33. The Golden Rule of Retries

Don't blindly retry.

Think:

```text
Is failure transient?
 ↓
Is operation safe to retry?
 ↓
How many retries?
 ↓
Backoff?
 ↓
Jitter?
 ↓
What happens if dependency stays down?
```

For payment-like operations:

```text
idempotency
```

is especially important.

---

## PART 12 — INTERVIEW SCENARIOS

These are probably more valuable than memorizing definitions.

---

### Scenario 1

> Your API suddenly starts returning 500 errors. What do you do?

Answer structure:

```text
1. Confirm impact
2. Check metrics
3. Check recent deployment
4. Check application logs
5. Check traces
6. Check dependencies
7. Mitigate
8. Verify recovery
9. Find root cause
```

---

### Scenario 2

> All Pods are Running, but users get 503.

Think:

```text
Running ≠ Ready
```

Check:

```text
readiness
Service
endpoints
Ingress/LB
application
```

---

### Scenario 3

> API Pods are healthy but response time is 5 seconds.

Don't immediately add Pods.

Check:

```text
metrics
 ↓
traces
 ↓
database
 ↓
Redis
 ↓
external APIs
```

Maybe:

```text
RDS query = 4.5 seconds
```

Scaling API Pods won't fix the underlying database query.

---

### Scenario 4

> Database connections suddenly reach 100%.

Think:

```text
Pods increased?
Connection pool too large?
Connection leak?
Traffic spike?
Slow queries?
```

---

### Scenario 5

> New deployment causes 5xx errors.

Possible response:

```text
check rollout
 ↓
logs
 ↓
compare v1/v2
 ↓
rollback if appropriate
 ↓
investigate
```

---

### Scenario 6

> EC2 cannot access the Internet.

Check:

```text
subnet
 ↓
route table
 ↓
Internet Gateway/NAT
 ↓
Security Group
 ↓
NACL
 ↓
DNS
```

---

### Scenario 7

> Private EC2 can't download updates.

Think:

```text
Private subnet
 ↓
route to NAT Gateway?
 ↓
NAT route correct?
 ↓
NAT in public subnet?
 ↓
Internet Gateway?
```

---

### Scenario 8

> Kubernetes Pod can't pull an image.

Think:

```text
image name
 ↓
tag
 ↓
registry
 ↓
credentials
 ↓
network
```

---

## PART 13 — OA / MCQ TRAPS

These are the kinds of distinctions you should be able to answer instantly.

#### Docker

```text
Image ≠ Container
```

#### Kubernetes

```text
Pod ≠ Container
```

#### AWS

```text
Multi-AZ ≠ Read Replica
```

#### Networking

```text
Private subnet ≠ no Internet access
```

A private subnet can have outbound Internet access through NAT.

#### Security

```text
Authentication ≠ Authorization
```

#### Storage

```text
S3 ≠ EBS
```

#### Scaling

```text
Horizontal ≠ Vertical
```

#### CI/CD

```text
Continuous Delivery ≠ Continuous Deployment
```

#### Observability

```text
Logs ≠ Metrics ≠ Traces
```

#### Terraform

```text
State ≠ configuration
```

#### Kubernetes

```text
Running ≠ Ready
```

#### Scaling

```text
HPA ≠ node autoscaling
```

These distinctions are extremely high-value.

---

## PART 14 — YOUR FINAL PRACTICAL CAPSTONE

Now I want you to eventually build **one complete project** that combines the roadmap.

Don't build 15 tiny DevOps projects.

Build one realistic backend.

---

## 34. Project

#### TypeScript Production Backend

```text
Node.js
TypeScript
PostgreSQL
Redis
Docker
Kubernetes
AWS
Terraform
GitHub Actions
Observability
```

Architecture:

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
                             EKS
                              │
                     ┌────────┼────────┐
                     ↓        ↓        ↓
                   Pod      Pod      Pod
                     │        │        │
                     └────────┼────────┘
                              │
                    ┌─────────┼─────────┐
                    ↓         ↓         ↓
                  Redis      RDS       S3
```

CI/CD:

```text
GitHub
   ↓
GitHub Actions
   ↓
Tests
   ↓
Build
   ↓
Docker
   ↓
Security scan
   ↓
ECR
   ↓
Kubernetes
```

Infrastructure:

```text
Terraform
   ↓
AWS
   ├── VPC
   ├── EKS
   ├── RDS
   ├── S3
   ├── IAM
   └── networking
```

Observability:

```text
Application
 ├── logs
 ├── metrics
 └── traces
       ↓
Monitoring
       ↓
Alerts
```

---

## 35. What Your Capstone Should Demonstrate

Don't just deploy:

```text
Hello World
```

Demonstrate:

#### Application

```text
TypeScript
REST API
PostgreSQL
Redis
authentication
validation
error handling
```

#### Docker

```text
multi-stage
non-root
health checks
small image
```

#### CI

```text
lint
typecheck
tests
build
Docker build
```

#### CD

```text
image registry
deployment
rolling update
rollback
```

#### Kubernetes

```text
Deployment
Service
ConfigMap
Secret
Ingress
probes
resources
HPA
```

#### AWS

```text
VPC
EKS
RDS
S3
IAM
Load Balancer
CloudWatch
```

#### Terraform

```text
infrastructure
modules
variables
outputs
state
```

#### Observability

```text
logs
metrics
traces
alerts
```

That single project can give you a tremendous amount to discuss in interviews.

---

## PART 15 — WHAT DEPTH DO YOU ACTUALLY NEED?

This is important because you don't want to spend six months becoming a DevOps specialist.

### 🔥 Master

```text
Linux
Networking
Git
Docker
CI/CD
AWS fundamentals
VPC
IAM
EC2
S3
RDS
Load balancing
Kubernetes fundamentals
Terraform
Monitoring
Troubleshooting
```

You should be able to:

```text
explain
configure
write
deploy
debug
```

---

### 🟡 Strong Working Knowledge

```text
EKS
Lambda
SQS/SNS
CloudFront
WAF
Prometheus
Grafana
OpenTelemetry
HPA
advanced Terraform modules
```

Understand how to use them and explain the architecture.

---

### 🟢 Awareness

You don't need deep expertise for your target role in:

```text
ArgoCD
GitOps
Jenkins
Ansible
Service Mesh
Istio
Operators
CRDs
advanced Kubernetes administration
advanced networking internals
advanced SRE practices
```

You should know:

```text
what it is
why it exists
when you'd use it
```

That's enough unless a particular job requires more.

---

## PART 16 — FINAL "CAN I SAY I KNOW DEVOPS?"

After completing the roadmap **and actually doing the labs**, you should be able to honestly say:

> I have hands-on experience with Linux, Git, Docker, CI/CD, AWS, Kubernetes, Terraform, monitoring, and production deployment concepts.

But don't claim:

> "I'm an expert DevOps engineer."

Your target is:

> **Backend/SWE engineer with strong Cloud + DevOps capabilities.**

That's a much more useful positioning for your career direction.

---

## 🧠 THE FINAL 10 QUESTIONS

Before considering this roadmap truly complete, make sure you can answer these without notes.

#### 1.

**What happens from `git push` until a new Dockerized Node.js version reaches Kubernetes?**

```text
Git
 ↓
GitHub
 ↓
Actions
 ↓
Tests
 ↓
Docker
 ↓
ECR
 ↓
Kubernetes
 ↓
Rolling deployment
```

---

#### 2.

**Why can't you just use Pod IPs?**

Because Pods are ephemeral.

Use:

```text
Service
```

for stable discovery.

---

#### 3.

**Why does Kubernetes need readiness probes?**

Because:

```text
Running ≠ Ready
```

A running application may not yet be capable of safely receiving traffic.

---

#### 4.

**Why doesn't adding API Pods automatically solve database scaling?**

Because:

```text
API
 ↓
DB
```

can make the DB the bottleneck.

---

#### 5.

**Why use Terraform?**

To manage infrastructure declaratively and reproducibly as code.

---

#### 6.

**Why use Docker?**

To package the application and its runtime dependencies consistently.

---

#### 7.

**Why use Kubernetes?**

To orchestrate containerized workloads:

```text
scheduling
scaling
self-healing
service discovery
rolling deployments
```

---

#### 8.

**How do you troubleshoot a production 503?**

Layer by layer:

```text
DNS
 ↓
WAF/edge
 ↓
Load Balancer
 ↓
Ingress/Service
 ↓
Pod readiness
 ↓
Container
 ↓
Application
 ↓
Dependencies
```

---

#### 9.

**How do you know whether the system is healthy?**

```text
Metrics
Logs
Traces
Health checks
Alerts
```

---

#### 10.

**What happens when a production deployment breaks?**

```text
Detect
 ↓
Investigate
 ↓
Mitigate
 ↓
Rollback/fix-forward where appropriate
 ↓
Verify
 ↓
Root-cause analysis
 ↓
Prevent recurrence
```

If you can reason through all ten, you're thinking about DevOps rather than merely memorizing tools.

### 🎯 Final target

Your skill stack now looks like:

```text
                SWE / BACKEND ENGINEER
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
     Backend          Cloud            DevOps
        │                │                │
 TypeScript/Node       AWS           Linux/Git
 PostgreSQL            VPC           Docker
 Redis                 EC2           CI/CD
 APIs                  S3            Kubernetes
 System Design         RDS           Terraform
                       EKS           Observability
```
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 23: Production Architecture + Troubleshooting](../08-production/ch23-production-architecture-troubleshooting.md) · [Chapter 25: Helm: Kubernetes Package Management](../05-kubernetes/ch25-helm.md) → · [Revision sheet](../../revision/ch24-revision.md)
