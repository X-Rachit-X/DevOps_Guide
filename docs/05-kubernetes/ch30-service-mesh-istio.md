# Chapter 30 — Service Mesh + Istio

> **Source:** Response 30 of the original conversation (`source-archive/src-30.txt`, lines 1–1839) · **Part II — Advanced extension (Responses 25–36)**  
> **Study aids:** [Revision sheet](../../revision/ch30-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md) · *includes an editorial supplement at the end*

<!-- SOURCE-BEGIN -->

We're staying exactly on the roadmap.

You've already learned Kubernetes networking, Services, Ingress, NetworkPolicies, HPA, Helm, ArgoCD, CRDs, and Operators.

Now we're learning **Service Mesh** — an advanced Kubernetes/backend concept that becomes useful when you have many microservices.

The goal for you is **strong SWE interview + practical understanding**, not becoming an Istio administrator.

---

## 1. The Problem Service Mesh Solves

Imagine your application has:

```text
Frontend
   ↓
API Gateway
   ↓
User Service
   ↓
Order Service
   ↓
Payment Service
   ↓
Notification Service
```

Now every service needs to handle:

- HTTPS/mTLS
- retries
- timeouts
- circuit breaking
- service discovery
- traffic routing
- observability
- authentication
- authorization
- metrics
- tracing

Without a service mesh, every application may implement these independently.

For example, Node.js services might each implement:

```typescript
fetchWithRetry()
fetchWithTimeout()
circuitBreaker()
metrics()
tracing()
```

That creates duplicated infrastructure logic.

---

## 2. What Is a Service Mesh?

A **service mesh** is an infrastructure layer that manages communication between services.

Instead of putting all networking logic inside the application:

```text
Application
    ↓
Networking logic
```

you move much of it into infrastructure:

```text
Application
    ↓
Service Mesh
    ↓
Network
```

This allows application developers to focus more on business logic.

---

## 3. The Key Idea: Sidecar Proxy

This is the most important concept.

Suppose you have:

```text
Pod
├── Node.js container
└── Envoy proxy
```

The Envoy proxy runs alongside your application.

This is called a:

> **Sidecar proxy**

So instead of:

```text
Pod
└── Node.js
```

you have:

```text
Pod
├── Node.js
└── Envoy
```

---

## 4. How Traffic Flows

Suppose:

```text
Order Service
```

calls:

```text
Payment Service
```

Without mesh:

```text
Order
  │
  │ HTTP
  ▼
Payment
```

With a service mesh:

```text
Order Pod
├── Order application
└── Envoy
      │
      │
      ▼
Payment Pod
├── Envoy
└── Payment application
```

Traffic essentially becomes:

```text
Order App
   ↓
Order Envoy
   ↓
Payment Envoy
   ↓
Payment App
```

The proxies handle much of the networking behavior.

---

## 5. Why Envoy?

Istio commonly uses **Envoy** as its data-plane proxy.

Envoy is a high-performance proxy designed for service-to-service communication.

For your interviews, remember:

```text
Istio
 ↓
uses Envoy proxies
 ↓
to handle service traffic
```

---

## 6. Data Plane vs Control Plane

Another extremely important concept.

A service mesh has two conceptual parts:

```text
Service Mesh
│
├── Data Plane
│
└── Control Plane
```

---

## 7. Data Plane

The data plane handles **actual traffic**.

For Istio:

```text
Envoy proxies
```

are the important data-plane components.

Example:

```text
Service A
   ↓
Envoy
   ↓
Envoy
   ↓
Service B
```

The Envoys actually process the network traffic.

---

## 8. Control Plane

The control plane manages/configures the proxies.

Conceptually:

```text
Istio Control Plane
        ↓
configuration
        ↓
Envoy proxies
```

Modern Istio primarily uses:

```text
istiod
```

as the control-plane component.

It provides configuration and service information to proxies.

---

## 9. Easy Mental Model

Remember:

```text
Control Plane
=
"Tell proxies what to do"

Data Plane
=
"Actually handle traffic"
```

This distinction appears throughout distributed systems.

---

## 10. Sidecar Injection

How does Envoy get inside your Pods?

Istio can automatically inject the sidecar.

For example, you label a namespace:

```bash
kubectl label namespace default istio-injection=enabled
```

Then newly created Pods can receive the Envoy sidecar automatically.

Instead of:

```text
Pod
└── Node.js
```

you get:

```text
Pod
├── Node.js
└── Envoy
```

---

## 11. Check the Sidecar

Run:

```bash
kubectl get pods
```

You might see:

```text
NAME          READY
order-api     2/2
payment-api   2/2
```

Why `2/2`?

Because:

```text
1 application container
+
1 Envoy container
=
2 containers
```

This is a useful troubleshooting clue.

---

## 12. What Does the Service Mesh Actually Give Us?

A mesh can provide:

```text
Traffic management
Security
Observability
Reliability
```

Let's examine each.

---

## 13. Traffic Management

Suppose you have:

```text
Payment v1
Payment v2
```

You want:

```text
90% → v1
10% → v2
```

A service mesh can implement traffic routing.

Conceptually:

```text
             ┌── 90% → v1
Request ─────┤
             └── 10% → v2
```

This is useful for:

- canary deployments
- A/B testing
- gradual releases

---

## 14. Canary Deployment

Suppose the current version is:

```text
payment:v1
```

New version:

```text
payment:v2
```

Instead of immediately switching everything:

```text
100% → v2
```

you can gradually move:

```text
95% → v1
5%  → v2

↓
90% → v1
10% → v2

↓
50% → v1
50% → v2

↓
0% → v1
100% → v2
```

If errors increase:

```text
rollback traffic
```

This is much safer than immediately replacing all traffic.

---

## 15. VirtualService

Istio uses resources such as:

```text
VirtualService
DestinationRule
```

for traffic management.

Example:

```yaml
apiVersion: networking.istio.io/v1
kind: VirtualService

metadata:
  name: payment

spec:
  hosts:
    - payment

  http:
    - route:
        - destination:
            host: payment
            subset: v1
          weight: 90

        - destination:
            host: payment
            subset: v2
          weight: 10
```

Conceptually:

```text
90% → v1
10% → v2
```

---

## 16. DestinationRule

A `VirtualService` decides:

> How should traffic be routed?

A `DestinationRule` can define:

> What subsets/policies exist for that destination?

For example:

```yaml
spec:
  subsets:

    - name: v1
      labels:
        version: v1

    - name: v2
      labels:
        version: v2
```

So:

```text
VirtualService
→ routing rules

DestinationRule
→ destination/subset policies
```

This distinction is important in interviews.

---

## 17. Retries

Suppose:

```text
Order → Payment
```

Payment temporarily fails.

A mesh can retry certain requests.

Conceptually:

```text
Order
 ↓
Payment
 ↓
temporary failure
 ↓
retry
 ↓
Payment
```

Example:

```yaml
retries:
  attempts: 3
  perTryTimeout: 2s
```

But retries are **not automatically good**.

---

## 18. Why Retries Can Be Dangerous

Suppose one request causes:

```text
3 retries
```

and 1,000 requests arrive.

You could suddenly generate:

```text
1,000 × 3
=
3,000 additional requests
```

This can overload an already failing service.

This is called a **retry storm**.

Therefore:

> Retries must be used carefully.

Usually combine them with:

```text
timeouts
backoff
limits
idempotency
```

---

## 19. Timeouts

Suppose:

```text
Order → Payment
```

and Payment never responds.

Without a timeout:

```text
Request
   ↓
waiting...
   ↓
waiting...
   ↓
waiting...
```

Resources remain occupied.

With a timeout:

```text
Request
   ↓
2 seconds
   ↓
timeout
```

This prevents indefinitely hanging calls.

---

## 20. Timeout + Retry

A common pattern:

```text
Request
 ↓
timeout
 ↓
retry
 ↓
timeout
 ↓
fail
```

But you must make sure the **total request budget** is respected.

For example:

```text
API timeout = 5 seconds
```

You don't want internal retries accidentally taking:

```text
20 seconds
```

because downstream services each retry independently.

---

## 21. Circuit Breaking

Imagine:

```text
Order
 ↓
Payment
```

Payment is completely broken.

Without circuit breaking:

```text
Order
 ↓
request
 ↓
failure
 ↓
request
 ↓
failure
 ↓
request
 ↓
failure
...
```

This wastes resources.

---

## 22. Circuit Breaker

A circuit breaker can move through states:

```text
CLOSED
   ↓
failures increase
   ↓
OPEN
   ↓
requests rejected quickly
   ↓
after cooldown
   ↓
HALF-OPEN
   ↓
test request
   ↓
success → CLOSED
failure → OPEN
```

This protects the system from cascading failures.

---

## 23. Cascading Failure

This is an important interview concept.

Suppose:

```text
Payment
   ↓
slow

Order
   ↓
waiting for Payment

API Gateway
   ↓
waiting for Order

Users
   ↓
waiting for Gateway
```

Eventually:

```text
threads/connections
memory
CPU
queues
```

can become exhausted.

One service's failure can spread through the system.

This is a:

> **Cascading failure**

Timeouts, circuit breakers, load shedding, and bulkheads help prevent this.

---

## 24. mTLS

Now security.

Normal HTTP:

```text
Service A ───── HTTP ─────> Service B
```

HTTPS:

```text
Service A ─── TLS ───> Service B
```

A service mesh can provide **mutual TLS**, or mTLS.

Both sides authenticate each other.

```text
Service A
    ↕
  mTLS
    ↕
Service B
```

---

## 25. Why mTLS?

Without mutual authentication:

```text
Service A
   ↓
"Who are you?"
   ↓
Service B
```

With mTLS:

```text
A proves identity to B
B proves identity to A
```

It provides:

- encryption
- service identity
- mutual authentication

---

## 26. Application Code Doesn't Need to Implement mTLS

This is one of the biggest advantages.

Without mesh, your Node.js application may need to handle:

```text
certificates
TLS configuration
rotation
verification
```

With a service mesh:

```text
Node.js
   ↓
Envoy
   ↓
mTLS
   ↓
Envoy
   ↓
Node.js
```

The application can remain largely unaware of the transport-level security.

---

## 27. Zero Trust

Service mesh can support a zero-trust architecture.

Instead of:

> "Anything inside the VPC is trusted."

you can use:

```text
service identity
+
authentication
+
authorization
+
encryption
```

So internal communication is also protected.

---

## 28. Authorization

Authentication asks:

> Who are you?

Authorization asks:

> What are you allowed to do?

For example:

```text
Order Service
   ↓
Payment Service
```

You might allow:

```text
POST /payments
```

but deny:

```text
DELETE /payments
```

Service mesh authorization policies can enforce such communication rules.

---

## 29. Observability

Service meshes can provide networking-level telemetry.

You can collect:

```text
requests
latency
errors
traffic
connections
```

For example:

```text
Order → Payment

Requests: 20,000/min
Success: 99.8%
p95 latency: 120 ms
5xx: 0.2%
```

This is valuable because the proxy sees traffic even when application instrumentation is limited.

---

## 30. Distributed Tracing

Consider:

```text
Client
 ↓
API Gateway
 ↓
Order
 ↓
Payment
 ↓
Database
```

A request may have a trace:

```text
Trace ID: abc123
```

and spans:

```text
Gateway     20ms
Order       80ms
Payment    150ms
Database   100ms
```

You can identify:

> Payment is consuming most of the latency.

Service mesh can participate in this telemetry.

---

## 31. Service Mesh + OpenTelemetry

You've already learned OpenTelemetry.

Now connect the concepts:

```text
Application
     +
Service Mesh
     ↓
Metrics
Logs
Traces
     ↓
Observability platform
```

The mesh gives infrastructure-level visibility while application instrumentation gives business/application-level visibility.

They complement each other.

---

## 32. Istio Architecture

Simplified:

```text
                Istio Control Plane
                      │
                      │ configuration
                      ▼
        ┌─────────────────────────────┐
        │                             │
        ▼                             ▼
   Envoy Proxy                   Envoy Proxy
        │                             │
        ▼                             ▼
   Order Service                Payment Service
```

Data plane:

```text
Envoy ↔ Envoy
```

Control plane:

```text
istiod → Envoy
```

---

## 33. Installing Istio

For learning, Istio provides `istioctl`.

After installing Istio:

```bash
istioctl version
```

You can install a demo profile:

```bash
istioctl install --set profile=demo -y
```

Then check:

```bash
kubectl get pods -n istio-system
```

You should see Istio control-plane components.

---

## 34. Enable Injection

For a namespace:

```bash
kubectl label namespace default istio-injection=enabled
```

Then deploy your application.

For example:

```bash
kubectl apply -f deployment.yaml
```

Check:

```bash
kubectl get pods
```

You may see:

```text
READY
2/2
```

instead of:

```text
1/1
```

---

## 35. Important Gotcha

Labeling a namespace doesn't necessarily inject a sidecar into **already existing Pods**.

You may need to recreate/restart workloads.

For example:

```bash
kubectl rollout restart deployment order-api
```

Then:

```bash
kubectl get pods
```

---

## 36. Istio Gateway

You've already learned Kubernetes Ingress.

Istio also has its own traffic-management concepts.

You may encounter:

```text
Gateway
VirtualService
DestinationRule
```

Conceptually:

```text
Internet
   ↓
Istio Gateway
   ↓
VirtualService
   ↓
Service
   ↓
Pods
```

Don't confuse an Istio Gateway with a Kubernetes Service.

---

## 37. Service Mesh vs Kubernetes Service

Very important.

#### Kubernetes Service

Provides:

```text
stable network endpoint
service discovery
load balancing
```

Example:

```text
payment.default.svc.cluster.local
```

#### Service Mesh

Adds:

```text
traffic policies
mTLS
retries
timeouts
circuit breaking
telemetry
authorization
advanced routing
```

So:

```text
Kubernetes Service
=
basic service networking

Service Mesh
=
advanced service-to-service networking
```

---

## 38. Service Mesh vs API Gateway

Another common interview question.

#### API Gateway

Usually handles:

```text
external → internal
```

Examples:

```text
authentication
rate limiting
routing
API policies
```

#### Service Mesh

Primarily handles:

```text
service → service
```

communication.

Architecture:

```text
Internet
   ↓
API Gateway
   ↓
Service Mesh
   ↓
Microservices
```

They can coexist.

---

## 39. Service Mesh vs Ingress

Ingress typically handles:

```text
external traffic
        ↓
cluster services
```

Service mesh primarily handles:

```text
service
  ↕
service
```

Modern architectures can use mesh gateways for ingress/egress too, but the conceptual distinction remains useful.

---

## 40. Service Mesh vs Application-Level Libraries

Without mesh:

```text
Node.js
 ├── retry library
 ├── timeout library
 ├── tracing library
 ├── circuit breaker
 └── TLS configuration
```

With mesh:

```text
Node.js
     ↓
Envoy
 ├── retries
 ├── timeout
 ├── mTLS
 ├── routing
 └── telemetry
```

However, application-level logic is still required for **business semantics**.

A mesh cannot understand:

```text
"Don't charge the customer twice."
```

That requires application-level idempotency.

---

## 41. When NOT to Use a Service Mesh

This is extremely important.

A service mesh isn't automatically necessary.

For:

```text
small application
3 services
low traffic
simple deployment
```

adding Istio can introduce unnecessary:

```text
complexity
CPU/memory overhead
debugging difficulty
operational burden
```

If your architecture is:

```text
Frontend
 ↓
Node API
 ↓
PostgreSQL
```

you almost certainly don't need Istio just because Kubernetes is being used.

---

## 42. When It Becomes Useful

A service mesh becomes more compelling when you have:

```text
many microservices
+
complex traffic patterns
+
strong security requirements
+
mTLS requirements
+
advanced deployment strategies
+
need for uniform networking policies
```

For example:

```text
50+ services
multiple teams
multiple environments
canary deployments
strict service identity
```

Now centralized networking policies can become valuable.

---

## 43. Cost of a Service Mesh

Every sidecar consumes resources.

Suppose:

```text
100 Pods
```

and every Pod gets:

```text
1 Envoy
```

You now have:

```text
100 additional proxies
```

That means additional:

```text
CPU
memory
network traffic
configuration
monitoring
```

This is why you should understand the tradeoff.

---

## 44. Sidecar vs Ambient Mesh

Modern service-mesh architectures can also use an **ambient** approach, where mesh functionality doesn't necessarily require a sidecar proxy in every application Pod.

For your placement preparation:

```text
Sidecar model
→ know well

Ambient mesh
→ know conceptually
```

You don't need deep implementation details unless a job specifically asks for them.

---

## 45. Istio Traffic Flow

Let's put everything together.

Suppose:

```text
Order Service
```

calls:

```text
Payment Service
```

The flow can be:

```text
Order App
    ↓
Order Envoy
    │
    ├── mTLS
    ├── timeout
    ├── retry
    ├── routing
    └── telemetry
    ↓
Payment Envoy
    │
    ├── authentication
    ├── authorization
    └── telemetry
    ↓
Payment App
```

That's the central idea of a service mesh.

---

## 46. A Practical Canary Architecture

Suppose:

```text
payment-v1
payment-v2
```

Pods:

```text
payment-v1
├── app
└── envoy

payment-v2
├── app
└── envoy
```

Istio:

```text
Request
   ↓
Envoy
   ↓
VirtualService
   ├── 90% → v1
   └── 10% → v2
```

Monitor:

```text
error rate
latency
CPU
business metrics
```

If v2 behaves badly:

```text
100% → v1
```

This combines:

```text
Kubernetes
+
Helm
+
GitOps
+
Service Mesh
+
Observability
```

---

## 47. Important Reliability Trap

Suppose:

```text
Service A
```

has:

```text
timeout = 10 sec
```

and:

```text
Service B
```

has:

```text
timeout = 10 sec
```

and:

```text
Service C
```

also:

```text
timeout = 10 sec
```

Your total request path could become extremely slow.

Good distributed-system design needs:

```text
timeout budgets
```

and carefully chosen:

```text
retries
backoff
circuit breaking
```

This is more important than memorizing Istio YAML.

---

## 48. Common Interview Questions

#### Q1. What is a service mesh?

> A service mesh is an infrastructure layer that manages service-to-service communication, providing capabilities such as traffic management, security, reliability, and observability.

---

#### Q2. What is a sidecar?

> A sidecar is a secondary container deployed alongside the application container, typically used to handle cross-cutting infrastructure functionality.

---

#### Q3. What is Envoy?

> Envoy is a high-performance proxy commonly used as the data-plane proxy in service meshes such as Istio.

---

#### Q4. Control plane vs data plane?

> The data plane handles actual service traffic, while the control plane configures and manages the proxies.

---

#### Q5. Why use mTLS?

> To encrypt service-to-service traffic and mutually authenticate the communicating services.

---

#### Q6. What is a circuit breaker?

> A mechanism that stops repeatedly sending requests to a failing dependency, allowing the system to fail fast and recover instead of amplifying the failure.

---

#### Q7. Why are retries dangerous?

> Excessive retries can amplify traffic to an already failing service and cause retry storms or cascading failures.

---

#### Q8. Service mesh vs API Gateway?

```text
API Gateway
→ external/client → services

Service Mesh
→ service → service
```

---

#### Q9. Service mesh vs Kubernetes Service?

```text
Kubernetes Service
→ discovery + stable endpoint + basic load balancing

Service Mesh
→ advanced traffic/security/observability
```

---

#### Q10. Do you always need Istio?

> No. It introduces operational and resource overhead and is most useful when service-to-service complexity justifies it.

---

## 49. Your Mental Model

Remember this:

```text
                    ISTIO
                      │
             ┌────────┴────────┐
             │                 │
        CONTROL PLANE      DATA PLANE
             │                 │
          istiod            Envoy
                               │
                       Actual traffic
```

And:

```text
Envoy can provide:

Traffic
 ├── routing
 ├── retries
 ├── timeouts
 └── circuit breaking

Security
 ├── mTLS
 └── authorization

Observability
 ├── metrics
 ├── traces
 └── telemetry
```

---

## 50. How This Fits Your Roadmap

You've now connected:

```text
Kubernetes
    ↓
Service
    ↓
Ingress
    ↓
Helm
    ↓
ArgoCD
    ↓
CRDs / Operators
    ↓
Service Mesh
```

And the broader production architecture:

```text
                     Internet
                        │
                     Route53
                        │
                    CloudFront
                        │
                       WAF
                        │
                 Load Balancer
                        │
                       EKS
                        │
                 Istio / Mesh
                        │
       ┌────────────────┼────────────────┐
       ↓                ↓                ↓
   Order Service    Payment Service   User Service
       │                │                │
     Envoy            Envoy            Envoy
       └────────────────┼────────────────┘
                        │
                     RDS/Redis
```

Terraform provisions the infrastructure.

GitHub Actions builds and tests.

Docker packages.

ECR stores images.

ArgoCD deploys through GitOps.

Helm packages Kubernetes applications.

Istio manages advanced service-to-service communication.

Observability tells you what's happening.

That's the complete picture.

---

## 🎯 Chapter 30 Summary

Covered:

- ✅ What is a service mesh
- ✅ Why service meshes exist
- ✅ Sidecar pattern
- ✅ Envoy
- ✅ Data plane
- ✅ Control plane
- ✅ Istio architecture
- ✅ `istiod`
- ✅ Sidecar injection
- ✅ Traffic management
- ✅ Canary deployments
- ✅ `VirtualService`
- ✅ `DestinationRule`
- ✅ Retries
- ✅ Timeouts
- ✅ Retry storms
- ✅ Circuit breakers
- ✅ Cascading failures
- ✅ mTLS
- ✅ Service identity
- ✅ Authorization
- ✅ Zero-trust concepts
- ✅ Observability
- ✅ Distributed tracing
- ✅ OpenTelemetry integration
- ✅ Istio Gateway
- ✅ Service Mesh vs Kubernetes Service
- ✅ Service Mesh vs API Gateway
- ✅ Service Mesh vs Ingress
- ✅ Service Mesh vs application libraries
- ✅ When to use Istio
- ✅ When NOT to use Istio
- ✅ Sidecar resource overhead
- ✅ Ambient mesh awareness
- ✅ Interview scenarios

#### Depth target

**🔥 Deep:** service mesh concepts, Envoy, sidecar, traffic management, mTLS, retries/timeouts, circuit breaking, API Gateway vs mesh.

**🟡 Medium:** Istio resources and configuration.

**⚪ Awareness:** advanced Istio internals, ambient mesh internals, custom Envoy extensions.

You do **not** need to become an Istio specialist for a backend SWE placement.
<!-- SOURCE-END -->

---

## Editorial supplement

> **Added by the knowledge-base editor — not part of the original source.** It fills gaps the source leaves open (for example concepts named in the interview list but never explained, or configuration the chapter only describes in words). Treat the text above as the original material and this section as clearly separated additions.

### The Istio resources behind mTLS, authorization, timeouts and circuit breaking

The chapter explains these capabilities conceptually. In Istio they are configured with the following resources. (API versions change between releases — check the documentation for your Istio version; `networking.istio.io/v1` and `security.istio.io/v1` are the current stable versions.)

**Mutual TLS — `PeerAuthentication`.** `PERMISSIVE` accepts both plaintext and mTLS (useful while migrating); `STRICT` requires mTLS.

```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT
```

**Authorization — `AuthorizationPolicy`.** Allow only the Order service to call `POST /payments` on the Payment service (anything not allowed by an `ALLOW` policy is denied for the selected workload):

```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: payment-allow-order
  namespace: production
spec:
  selector:
    matchLabels:
      app: payment
  action: ALLOW
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/production/sa/order"]
      to:
        - operation:
            methods: ["POST"]
            paths: ["/payments"]
```

**Timeouts and retries — in the `VirtualService`.** Together they form the "timeout budget" discussed in the chapter:

```yaml
spec:
  hosts: [payment]
  http:
    - route:
        - destination: { host: payment, subset: v1 }
      timeout: 5s                 # total budget for the request
      retries:
        attempts: 3
        perTryTimeout: 2s
        retryOn: 5xx,reset,connect-failure
```

**Circuit breaking — in the `DestinationRule`.** Istio implements it with connection-pool limits plus *outlier detection* (ejecting unhealthy endpoints), not with a literal CLOSED/OPEN/HALF-OPEN state machine in the YAML:

```yaml
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata:
  name: payment
spec:
  host: payment
  trafficPolicy:
    connectionPool:
      tcp:  { maxConnections: 100 }
      http: { http1MaxPendingRequests: 50, maxRequestsPerConnection: 10 }
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 10s
      baseEjectionTime: 30s
  subsets:
    - name: v1
      labels: { version: v1 }
    - name: v2
      labels: { version: v2 }
```

Further points worth knowing:

- **Default retries.** Istio applies a default retry policy (about two retries for certain connection failures) even if you configure none, so retry amplification can happen without you writing a `retries:` block. Set explicit limits for non-idempotent calls.
- **How traffic reaches the sidecar.** An init container (or the Istio CNI plugin) installs iptables rules that redirect the Pod's inbound and outbound traffic through Envoy; the application doesn't change its code or addresses.
- **Installation profiles.** `profile=demo` (used in the chapter) enables extra features and is for learning only; `default` is the production-oriented profile, `minimal` installs the control plane only, and `ambient` enables the sidecar-less data plane.
- **Injection mechanisms.** The `istio-injection=enabled` namespace label is the classic method; revision labels (`istio.io/rev=<revision>`) support canary control-plane upgrades; ambient mode uses the `istio.io/dataplane-mode=ambient` label.
- **Other Istio resources:** `Gateway` (ingress/egress proxies), `ServiceEntry` (add external services to the mesh), `Sidecar` (limit what a proxy knows about).
- **Alternatives (awareness):** Linkerd (lightweight Rust proxy), Consul service mesh, Cilium (eBPF-based). *Verify:* AWS announced end of support for AWS App Mesh (Envoy-based) — check the current AWS status before recommending it.

---

**Navigation:** ← [Chapter 29: Kubernetes CRDs + Operators](ch29-crds-operators.md) · [Chapter 31: Advanced Amazon EKS](ch31-advanced-eks.md) → · [Revision sheet](../../revision/ch30-revision.md)
