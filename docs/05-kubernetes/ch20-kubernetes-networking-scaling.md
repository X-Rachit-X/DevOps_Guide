# Chapter 20 — Kubernetes Networking + Scaling + Production

> **Source:** Response 20 of the original conversation (`source-archive/src-20.txt`, lines 1–1852) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch20-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

This is the **last major Kubernetes response** in our roadmap.

By the end of this response, you should be able to look at a production Kubernetes architecture and understand **how traffic enters the cluster, how it reaches Pods, how Pods communicate, how they scale, and how Kubernetes handles failures and deployments.**

We'll keep this practical.

---

## 1. Where We Are

You've already learned:

```text
Docker
  ↓
Container
  ↓
Kubernetes
  ↓
Pod
  ↓
Deployment
  ↓
Service
  ↓
ConfigMap / Secret
  ↓
Volumes / PVC
```

Now we need to solve:

```text
How does traffic reach my application?
How do Pods communicate?
How does the application scale?
How do I expose it to the Internet?
How do I secure it?
How do I run this in AWS?
How do I troubleshoot it?
```

---

## PART 1 — KUBERNETES NETWORKING

### 2. Kubernetes Networking Mental Model

A simplified architecture:

```text
                    INTERNET
                       │
                       ↓
                Load Balancer
                       │
                       ↓
                    Ingress
                       │
                       ↓
                   Service
                       │
            ┌──────────┼──────────┐
            ↓          ↓          ↓
           Pod        Pod        Pod
            │          │          │
            └──────────┼──────────┘
                       ↓
                    RDS/Redis
```

There are several networking layers here.

---

## 3. Pod-to-Pod Communication

Suppose:

```text
Pod A
Node.js API
```

needs to communicate with:

```text
Pod B
Worker
```

Kubernetes networking is designed so Pods can communicate with one another using their cluster networking.

Conceptually:

```text
Pod A
10.x.x.1
  │
  │
  ↓
Pod B
10.x.x.2
```

But remember:

> **Pod IPs are ephemeral.**

So don't hardcode:

```text
10.x.x.2
```

in your application.

Instead, use a Service.

---

## 4. Service Discovery

Suppose you have:

```text
API
Worker
Redis
```

Create a Redis Service:

```yaml
apiVersion: v1
kind: Service

metadata:
  name: redis

spec:
  selector:
    app: redis

  ports:
    - port: 6379
      targetPort: 6379
```

Now your API can connect to:

```text
redis:6379
```

instead of:

```text
10.0.4.17:6379
```

This is called **service discovery**.

---

## 5. Kubernetes DNS

Kubernetes provides DNS-based service discovery.

Conceptually:

```text
redis
 ↓
Kubernetes DNS
 ↓
Redis Service IP
 ↓
Redis Pods
```

Your Node.js code could use:

```ts
const redisHost = process.env.REDIS_HOST ?? "redis";
```

and:

```text
redis:6379
```

becomes the network destination.

---

## 6. Namespaces and DNS

Suppose:

```text
namespace: production
service: redis
```

Within the same namespace:

```text
redis
```

can usually resolve the Service.

Across namespaces, you can use the namespace-qualified service name:

```text
redis.production
```

and Kubernetes DNS supports a fuller service DNS structure.

You don't need to memorize the complete FQDN yet, but understand:

> **Service names provide stable discovery even when Pods change.**

---

## PART 2 — SERVICE TYPES

We've already seen:

```text
ClusterIP
NodePort
LoadBalancer
```

Let's understand when to use each.

---

## 7. ClusterIP

Default Service type.

```text
Cluster
│
└── Service
      ↓
     Pods
```

Accessible inside the cluster.

Perfect for:

```text
API → Redis
API → internal worker
API → internal service
```

---

## 8. NodePort

Exposes a port on each node.

```text
Internet
   ↓
NodeIP:NodePort
   ↓
Service
   ↓
Pods
```

Example:

```yaml
type: NodePort
```

Useful for learning and certain scenarios, but generally not your preferred production internet-facing architecture.

---

## 9. LoadBalancer

Cloud integrations can provision an external load-balancing mechanism.

Conceptually:

```text
Internet
   ↓
Cloud Load Balancer
   ↓
Kubernetes Service
   ↓
Pods
```

This is common in cloud environments.

---

## PART 3 — INGRESS

Now we get to a very important production concept.

Imagine you have:

```text
api.example.com
app.example.com
admin.example.com
```

You don't necessarily want a separate public load-balancing endpoint for every internal service.

You can use an **Ingress** abstraction.

---

## 10. What Is Ingress?

Ingress defines HTTP/HTTPS routing rules into your cluster.

Example:

```text
api.example.com
        ↓
     Ingress
        ↓
    API Service
```

And:

```text
admin.example.com
        ↓
     Ingress
        ↓
   Admin Service
```

---

## 11. Host-Based Routing

Example:

```yaml
rules:
  - host: api.example.com
    ...

  - host: admin.example.com
    ...
```

Traffic:

```text
api.example.com
      ↓
   API Service

admin.example.com
      ↓
 Admin Service
```

---

## 12. Path-Based Routing

You can also route:

```text
example.com/api
example.com/admin
```

to different Services.

Conceptually:

```text
              Ingress
                 │
        ┌────────┴────────┐
        ↓                 ↓
     /api              /admin
        ↓                 ↓
 API Service       Admin Service
```

---

## 13. Important Ingress Clarification

Ingress is **not itself necessarily the complete load-balancing implementation**.

You need an **Ingress Controller** to actually implement the routing behavior.

Examples include controllers based on:

```text
NGINX
AWS Load Balancer Controller
Traefik
```

For AWS/EKS, the AWS Load Balancer Controller is particularly relevant.

The mental model is:

```text
Ingress
→ routing configuration

Ingress Controller
→ implements that routing
```

This distinction is frequently asked in interviews.

---

## PART 4 — AWS + EKS NETWORKING

Now connect this with everything you've already learned about AWS.

Your previous architecture:

```text
Route 53
   ↓
ALB
   ↓
EC2
   ↓
RDS
```

Kubernetes version:

```text
Route 53
   ↓
AWS Load Balancer
   ↓
EKS
   ↓
Kubernetes routing
   ↓
Pods
   ↓
RDS
```

Depending on the exact EKS architecture and controller, AWS load-balancing resources can integrate with Kubernetes Services/Ingress.

---

## 14. Production EKS Architecture

A simplified design:

```text
                         Internet
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
                    AWS Load Balancer
                            │
                            ↓
                       EKS Cluster
                            │
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
           Node/Pod       Node/Pod      Node/Pod
              │             │             │
              └─────────────┼─────────────┘
                            ↓
                       RDS PostgreSQL
                            │
                         Redis
```

Not every application needs every component, but you should understand how they fit together.

---

## PART 5 — NETWORK POLICIES

Security Groups protect AWS network interfaces.

Kubernetes can additionally implement **NetworkPolicy** controls for Pod traffic when the cluster networking implementation supports them.

---

## 15. Why Network Policies?

Suppose:

```text
Frontend
API
Database
Worker
```

You don't want:

```text
Frontend → Database
```

directly.

You want:

```text
Frontend → API → Database
```

A NetworkPolicy can express restrictions around which Pods/namespaces/network sources can communicate.

Conceptually:

```text
Frontend
   │
   ↓ allowed
  API
   │
   ↓ allowed
Database

Frontend
   │
   ✕
Database
```

This is **defense in depth**.

---

## 16. Basic NetworkPolicy

Conceptual example:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy

metadata:
  name: allow-api-to-db

spec:
  podSelector:
    matchLabels:
      app: database

  policyTypes:
    - Ingress

  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: api
```

This says roughly:

> Only traffic from Pods labeled `app=api` should be allowed into the selected database Pods, assuming the cluster's networking implementation enforces the policy.

---

## PART 6 — READINESS + LOAD BALANCING

This is an important production interaction.

Suppose:

```text
Pod A → healthy
Pod B → starting
Pod C → healthy
```

Pod B shouldn't receive production traffic yet.

That's why:

```text
readinessProbe
```

matters.

Flow:

```text
Pod starts
   ↓
Readiness check
   ↓
Fails ❌
   ↓
Not considered ready
   ↓
Service doesn't route normal traffic to it
```

Then:

```text
Application ready
   ↓
Readiness passes ✅
   ↓
Pod becomes eligible for traffic
```

This is extremely important during deployments.

---

## PART 7 — HORIZONTAL POD AUTOSCALING

Now let's scale Kubernetes.

Suppose:

```text
3 Pods
```

are handling traffic.

Traffic increases:

```text
CPU ↑
Requests ↑
```

We might want:

```text
3 Pods
 ↓
5 Pods
 ↓
10 Pods
```

Kubernetes provides:

> **Horizontal Pod Autoscaler (HPA)**

---

## 17. What HPA Does

Conceptually:

```text
Metrics
   ↓
HPA
   ↓
Desired replica count
   ↓
Deployment
   ↓
More/fewer Pods
```

For example:

```text
CPU target = 60%
```

If average CPU goes significantly above the target:

```text
3 Pods
 ↓
HPA
 ↓
5 Pods
```

---

## 18. HPA Example

A simplified example:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler

metadata:
  name: api-hpa

spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api

  minReplicas: 2
  maxReplicas: 10

  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
```

This says:

```text
Minimum → 2
Maximum → 10
Target → 60% CPU utilization
```

---

## 19. Important HPA Dependency

HPA needs metrics.

A common Kubernetes setup uses:

```text
Metrics Server
```

for resource metrics.

If metrics aren't available:

```text
HPA
 ↓
No useful metrics
 ↓
Autoscaling won't work as expected
```

This is a common troubleshooting point.

---

## 20. HPA Doesn't Magically Create More Machines

This distinction is very important.

Suppose:

```text
Worker Node
 └── Pods
```

HPA wants:

```text
10 Pods
```

but there isn't enough node capacity.

Then you have a second scaling layer.

```text
HPA
 ↓
Pod demand ↑
 ↓
Not enough node capacity
 ↓
Cluster/node autoscaling
 ↓
More nodes
 ↓
Pods scheduled
```

So:

```text
Pod scaling ≠ Node scaling
```

---

## PART 8 — CLUSTER AUTOSCALING

At the infrastructure level, Kubernetes environments can use node autoscaling mechanisms to add/remove worker capacity.

Conceptually:

```text
Pod demand ↑
      ↓
No node capacity
      ↓
Node autoscaler
      ↓
New worker node
      ↓
Pod scheduled
```

AWS EKS environments can use mechanisms such as:

```text
Managed Node Groups
Karpenter
```

You should know these names and their purpose.

You don't need deep Karpenter internals for a normal SWE interview.

---

## 21. Two Levels of Scaling

Remember:

```text
                    SCALING
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
        Pod scaling          Node scaling
             ↓                   ↓
            HPA             Node autoscaling
```

Example:

```text
Traffic ↑
   ↓
HPA
   ↓
More Pods
   ↓
No capacity
   ↓
More Nodes
```

---

## PART 9 — RESOURCE REQUESTS + HPA

This connects [Chapter 19](ch19-kubernetes-config-storage.md).

We had:

```yaml
resources:
  requests:
    cpu: "250m"
    memory: "256Mi"

  limits:
    cpu: "500m"
    memory: "512Mi"
```

HPA can use CPU/memory utilization relative to configured resource requests.

So resource requests aren't just about scheduling.

They can also affect how resource-based autoscaling behaves.

---

## PART 10 — ROLLING DEPLOYMENTS

Suppose you're running:

```text
v1
v1
v1
```

Deploy:

```text
v2
```

Kubernetes can gradually replace Pods.

```text
v1 v1 v1
 ↓
v2 v1 v1
 ↓
v2 v2 v1
 ↓
v2 v2 v2
```

During this process:

```text
readiness probes
+
Service
+
Deployment strategy
```

work together.

---

## 22. Rollout Commands

Check:

```bash
kubectl rollout status deployment/api
```

View history:

```bash
kubectl rollout history deployment/api
```

Undo:

```bash
kubectl rollout undo deployment/api
```

Restart:

```bash
kubectl rollout restart deployment/api
```

These commands are worth knowing.

---

## 23. Why Readiness Is Critical During Rollouts

Without readiness:

```text
New Pod starts
 ↓
Traffic immediately arrives
 ↓
Application isn't ready
 ↓
Requests fail
```

With readiness:

```text
New Pod
 ↓
Not ready
 ↓
No normal traffic
 ↓
Application initializes
 ↓
Ready ✅
 ↓
Traffic
```

This is one of the simplest ways to understand production Kubernetes.

---

## PART 11 — POD DISRUPTION

Suppose you have:

```text
3 Pods
```

and someone needs to perform maintenance on a node.

You don't necessarily want:

```text
3 → 0
```

at once.

Kubernetes provides concepts such as:

> **PodDisruptionBudget (PDB)**

A PDB can help limit voluntary disruptions so that a specified level of availability is maintained.

You should know the concept, not memorize every YAML option.

---

## PART 12 — JOBS AND CRONJOBS

Not everything is a long-running API.

Suppose you need:

```text
Generate monthly report
```

You might use a Kubernetes:

> Job

For scheduled work:

> CronJob

Conceptually:

```text
CronJob
   ↓
Job
   ↓
Pod
   ↓
Task
```

Examples:

```text
database cleanup
report generation
batch processing
scheduled synchronization
```

---

## PART 13 — DAEMONSETS

Another useful awareness-level object:

> **DaemonSet**

A DaemonSet ensures a Pod runs on appropriate nodes according to its scheduling rules.

Conceptually:

```text
Node A → monitoring agent
Node B → monitoring agent
Node C → monitoring agent
```

Common use cases include:

```text
log collection
node monitoring
network agents
```

Don't spend huge amounts of time here.

---

## PART 14 — KUBERNETES PRODUCTION SECURITY

You already learned AWS IAM and Kubernetes Secrets.

Now combine them.

A production application should avoid:

```text
AWS access key
 ↓
hardcoded in source code ❌
```

or:

```text
AWS access key
 ↓
Docker image ❌
```

Instead use appropriate workload identity mechanisms.

On EKS, one important approach is:

```text
Pod
 ↓
AWS workload identity
 ↓
IAM permissions
 ↓
AWS service
```

This allows workloads to obtain AWS permissions without embedding long-lived credentials in the container.

The exact mechanism depends on the EKS setup, but **the principle is what you need to understand**:

> **Give workloads identities and least-privilege permissions instead of putting permanent AWS keys inside Pods.**

---

## 24. Example

Suppose your Node.js API needs S3 access.

Bad:

```text
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

baked into Docker.

Better:

```text
Pod
 ↓
IAM-based workload identity
 ↓
S3
```

This connects directly to your IAM [Chapter 9](../04-aws/ch09-aws-fundamentals-iam.md).

---

## PART 15 — KUBERNETES LOGGING

Your application:

```ts
console.log(JSON.stringify({
  level: "info",
  event: "order_created",
  orderId
}));
```

Kubernetes captures container stdout/stderr through the container runtime/logging architecture.

You can inspect:

```bash
kubectl logs <pod>
```

Production environments generally centralize logs into an observability system rather than relying only on `kubectl logs`.

For example:

```text
Pod
 ↓
stdout
 ↓
logging agent
 ↓
central logging
```

We'll go much deeper into observability in [Chapter 22](../07-observability-sre/ch22-observability-reliability.md).

---

## PART 16 — KUBERNETES TROUBLESHOOTING

This is one of the **most valuable interview skills**.

Don't just memorize commands.

Learn the debugging flow.

---

### Scenario 1 — Pod is Pending

```bash
kubectl get pods
```

You see:

```text
api-xxx   Pending
```

Run:

```bash
kubectl describe pod api-xxx
```

Look at Events.

Possible causes:

```text
insufficient CPU
insufficient memory
node selector mismatch
taints/tolerations
PVC issue
scheduling constraints
```

---

## 25. Scenario 2 — CrashLoopBackOff

```text
CrashLoopBackOff
```

Means the container repeatedly crashes/restarts and Kubernetes is backing off between attempts.

Check:

```bash
kubectl logs <pod>
```

If the previous container instance crashed:

```bash
kubectl logs <pod> --previous
```

Then:

```bash
kubectl describe pod <pod>
```

Common causes:

```text
application crash
missing environment variable
bad configuration
database connection failure
wrong command
failed startup
```

---

## 26. Scenario 3 — ImagePullBackOff

Check:

```bash
kubectl describe pod <pod>
```

Possible causes:

```text
wrong image name
wrong tag
private registry authentication problem
image doesn't exist
registry unavailable
```

Remember your pipeline:

```text
GitHub Actions
 ↓
Docker build
 ↓
ECR
 ↓
Kubernetes
 ↓
Pod
```

A failure anywhere can cause deployment problems.

---

## 27. Scenario 4 — Service Has No Traffic

Suppose:

```text
Service
   ↓
??? 
```

Check:

```bash
kubectl get svc
```

Then:

```bash
kubectl get endpoints
```

or, on modern Kubernetes:

```bash
kubectl get endpointslices
```

Then inspect:

```bash
kubectl describe service api-service
```

Very common problem:

```text
Service selector:
app: api

Pod label:
app: backend
```

They don't match.

Therefore:

```text
Service
 ↓
No matching Pods
```

No traffic.

---

## 28. Scenario 5 — Port Mismatch

Suppose:

```text
Service:
targetPort: 3000
```

but Node.js actually listens on:

```text
8080
```

Then:

```text
Service
 ↓
3000
 ↓
Pod
 ↓
nothing listening there
```

Result:

```text
connection failure
```

Check:

```bash
kubectl describe service api-service
kubectl describe pod <pod>
```

and inspect the application.

---

## 29. Scenario 6 — Readiness Probe Failing

Check:

```bash
kubectl describe pod <pod>
```

You might see:

```text
Readiness probe failed
```

Possible reasons:

```text
wrong path
wrong port
application isn't ready
database dependency unavailable
startup takes longer than expected
```

Don't blindly increase timeout values.

Understand **why** the application isn't ready.

---

## 30. Scenario 7 — HPA Doesn't Scale

Check:

```bash
kubectl get hpa
```

Then:

```bash
kubectl describe hpa api-hpa
```

Possible issues:

```text
Metrics Server unavailable
resource requests missing
metrics unavailable
wrong target
no traffic/load
maxReplicas already reached
```

---

## PART 17 — PRACTICAL PRODUCTION LAB

Now let's combine everything.

Your application:

```text
Node.js API
```

Container:

```text
my-api:1.0
```

Kubernetes:

```text
Deployment
3 replicas
```

Service:

```text
ClusterIP
```

Configuration:

```text
ConfigMap
Secret
```

Health:

```text
/health
/ready
```

Scaling:

```text
HPA
2–10 replicas
```

Architecture:

```text
                    Internet
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
                AWS Load Balancer
                       │
                       ↓
                    Ingress
                       │
                       ↓
                 API Service
                       │
            ┌──────────┼──────────┐
            ↓          ↓          ↓
          Pod A      Pod B      Pod C
            │          │          │
            └──────────┼──────────┘
                       ↓
                    RDS
                       │
                     Redis
```

---

## 31. Your Deployment Pipeline

Now combine **everything you've learned across 20 responses**:

```text
Developer
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
    ├── lint
    ├── typecheck
    ├── tests
    ├── build
    │
    ↓
Docker Build
    │
    ↓
Container Image
    │
    ↓
ECR
    │
    ↓
Kubernetes / EKS
    │
    ↓
Deployment
    │
    ↓
Pods
    │
    ↓
Service
    │
    ↓
Load Balancer
    │
    ↓
Internet
```

Infrastructure:

```text
Terraform
    ↓
AWS
    ├── VPC
    ├── Subnets
    ├── EKS
    ├── RDS
    ├── S3
    ├── IAM
    └── Load Balancer
```

Monitoring:

```text
Pods
 ↓
Logs + Metrics + Traces
 ↓
Observability
```

We'll make that connection much deeper in Chapters [21](../06-iac-config/ch21-terraform.md)–[23](../08-production/ch23-production-architecture-troubleshooting.md).

---

## PART 18 — WHAT YOU SHOULD KNOW FOR SWE INTERVIEWS

At this point, you should be able to explain:

#### Kubernetes basics

```text
What is Kubernetes?
Why do we need it?
Docker vs Kubernetes?
What is a cluster?
What is a Pod?
What is a Deployment?
What is a ReplicaSet?
What is a Service?
```

#### Networking

```text
How does a request reach a Pod?
Why can't we use Pod IPs directly?
What is ClusterIP?
What is NodePort?
What is LoadBalancer?
What is Ingress?
What is an Ingress Controller?
How does service discovery work?
```

#### Scaling

```text
How do you scale Pods?
What is HPA?
What is node autoscaling?
Pod scaling vs node scaling?
Why do resource requests matter?
```

#### Production

```text
How do you deploy without downtime?
Why is readiness important?
How do you handle a crashed Pod?
How do you store secrets?
How do you persist data?
How do you secure Pod-to-Pod traffic?
How do Pods access AWS services securely?
```

#### Troubleshooting

```text
Pending?
CrashLoopBackOff?
ImagePullBackOff?
Service has no endpoints?
Readiness failing?
HPA not scaling?
```

These are much more valuable than memorizing 100 Kubernetes commands.

---

## 32. The Kubernetes Mental Model — FINAL

If you remember only one architecture:

```text
                         KUBERNETES CLUSTER
                                │
                    ┌───────────┴───────────┐
                    │                       │
               Control Plane           Worker Nodes
                                            │
                                      ┌─────┼─────┐
                                      ↓     ↓     ↓
                                     Pod   Pod   Pod
                                      │     │     │
                                      └─────┼─────┘
                                            ↑
                                         Service
                                            ↑
                                         Ingress
                                            ↑
                                      Load Balancer
                                            ↑
                                         Internet
```

And:

```text
Deployment
    ↓
maintains replicas
    ↓
Pods
    ↓
Service
    ↓
stable networking
```

And:

```text
HPA
 ↓
more/fewer Pods

Node autoscaling
 ↓
more/fewer worker nodes
```

And:

```text
ConfigMap → configuration
Secret → sensitive configuration
PVC → persistent storage
NetworkPolicy → Pod traffic control
Probe → health/readiness
```

---

## 🔥 Kubernetes Is Now Covered

Our Kubernetes section is now:

```text
18. Kubernetes Fundamentals
    ✅ Cluster architecture
    ✅ Control plane
    ✅ Worker nodes
    ✅ Pods
    ✅ Deployments
    ✅ ReplicaSets
    ✅ Services
    ✅ Namespaces
    ✅ kubectl
    ✅ Desired state
    ✅ Self-healing
    ✅ Rolling deployments

19. Kubernetes Configuration + Storage
    ✅ ConfigMaps
    ✅ Secrets
    ✅ Environment variables
    ✅ Volumes
    ✅ emptyDir
    ✅ PV
    ✅ PVC
    ✅ StorageClass
    ✅ StatefulSet concepts
    ✅ Resource requests/limits
    ✅ Liveness/readiness

20. Kubernetes Networking + Scaling + Production
    ✅ Pod networking
    ✅ Service discovery
    ✅ Kubernetes DNS
    ✅ ClusterIP
    ✅ NodePort
    ✅ LoadBalancer
    ✅ Ingress
    ✅ Ingress Controllers
    ✅ NetworkPolicy
    ✅ HPA
    ✅ Node autoscaling
    ✅ EKS
    ✅ Production architecture
    ✅ Security
    ✅ Workload identity concepts
    ✅ Jobs/CronJobs
    ✅ DaemonSets
    ✅ PDB awareness
    ✅ Rolling deployments
    ✅ Production troubleshooting
```

So **yes — the container → Docker → Kubernetes → EKS progression is properly covered.**
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 19: Kubernetes Configuration + Storage](ch19-kubernetes-config-storage.md) · [Chapter 21: Terraform: Infrastructure as Code](../06-iac-config/ch21-terraform.md) → · [Revision sheet](../../revision/ch20-revision.md)
