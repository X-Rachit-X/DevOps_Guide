# Chapter 30 — Revision Sheet: Service Mesh + Istio

> Supplements [the full chapter](../docs/05-kubernetes/ch30-service-mesh-istio.md). Goal: strong interview + practical understanding of **service mesh**, not Istio administration.

## The problem and the definition

Frontend → API Gateway → User → Order → Payment → Notification services. Each service needs HTTPS/mTLS, retries, timeouts, circuit breaking, service discovery, traffic routing, observability, authentication, authorization, metrics, tracing. Without a mesh every Node.js service re-implements `fetchWithRetry()`, `fetchWithTimeout()`, `circuitBreaker()`, `metrics()`, `tracing()` → duplicated infrastructure logic.
**Service mesh = an infrastructure layer that manages service-to-service communication** (traffic management, security, reliability, observability), freeing developers to focus on business logic.

## Core architecture

- **Sidecar proxy:** Pod = Node.js container + **Envoy** proxy. Order App → Order Envoy → Payment Envoy → Payment App; the proxies handle networking.
- **Envoy:** high-performance proxy for service-to-service communication; Istio's data-plane proxy.
- **Data plane vs control plane:** *data plane* = actual traffic (Envoy ↔ Envoy); *control plane* = "tell proxies what to do" — **`istiod`** provides configuration and service information to the proxies.
- **Sidecar injection:** `kubectl label namespace default istio-injection=enabled` → new Pods get Envoy; `kubectl get pods` shows **`2/2`** (app + Envoy) instead of `1/1` — a troubleshooting clue.
- **Gotcha:** labeling a namespace doesn't inject into **already running Pods** → `kubectl rollout restart deployment order-api`.

```bash
istioctl version
istioctl install --set profile=demo -y          # learning profile
kubectl get pods -n istio-system                 # control-plane components
kubectl label namespace default istio-injection=enabled
kubectl apply -f deployment.yaml ; kubectl get pods    # READY 2/2
```

## What a mesh gives you

| Area | Capabilities |
|---|---|
| **Traffic management** | Weighted routing (90% v1 / 10% v2), canary, A/B testing, gradual releases |
| **Security** | mTLS, service identity, authorization policies, zero trust |
| **Reliability** | Retries, timeouts, circuit breaking |
| **Observability** | Request rate, latency, errors, traffic, connections; distributed tracing |

### Traffic management resources

```yaml
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata: { name: payment }
spec:
  hosts: [payment]
  http:
    - route:
        - destination: { host: payment, subset: v1 }
          weight: 90
        - destination: { host: payment, subset: v2 }
          weight: 10
```
`DestinationRule` defines subsets: `v1` → label `version: v1`, `v2` → label `version: v2`. **VirtualService = routing rules; DestinationRule = destination/subset policies.** Canary progression: 95/5 → 90/10 → 50/50 → 0/100; on errors roll back traffic (100% → v1). Istio `Gateway` + `VirtualService` + `DestinationRule`: Internet → Istio Gateway → VirtualService → Service → Pods (an Istio Gateway ≠ a Kubernetes Service).

### Reliability

- **Retries:** `retries: { attempts: 3, perTryTimeout: 2s }` — not automatically good: 1,000 requests × 3 retries = 3,000 extra requests → **retry storm**. Combine with timeouts, backoff, limits, idempotency.
- **Timeouts:** without them, requests hang and resources stay occupied; with a 2 s timeout the call fails quickly. **Timeout + retry:** respect the **total request budget** (API timeout 5 s must not become 20 s because each downstream retries independently). **Reliability trap:** Service A/B/C each with 10 s timeouts → path becomes extremely slow → need **timeout budgets** plus carefully chosen retries, backoff, circuit breaking.
- **Circuit breaking:** CLOSED → failures increase → OPEN (reject quickly) → cooldown → HALF-OPEN (test request) → success → CLOSED / failure → OPEN. Protects against **cascading failures** (Payment slow → Order waits → Gateway waits → users wait → threads/connections/memory/CPU/queues exhausted). Defences: timeouts, circuit breakers, load shedding, bulkheads.

### Security

- **mTLS:** both sides authenticate; gives encryption, service identity, mutual authentication. Application code doesn't implement certificates/TLS config/rotation/verification — Node.js → Envoy → mTLS → Envoy → Node.js.
- **Zero trust:** don't trust "anything inside the VPC"; use service identity + authentication + authorization + encryption.
- **Authorization:** authentication = who; authorization = what (allow `POST /payments`, deny `DELETE /payments`) — enforced by mesh authorization policies.

### Observability

Proxy-level telemetry even when app instrumentation is limited, e.g. "Order → Payment: 20,000 req/min, success 99.8%, p95 120 ms, 5xx 0.2%". Distributed tracing: trace `abc123` with spans Gateway 20 ms, Order 80 ms, Payment 150 ms, Database 100 ms → Payment is the slowest. Mesh = infrastructure-level visibility; OpenTelemetry/application instrumentation = business/application-level; they complement each other.

## Comparisons

| | |
|---|---|
| **Mesh vs Kubernetes Service** | Service = stable endpoint, discovery, basic load balancing (`payment.default.svc.cluster.local`); Mesh adds traffic policies, mTLS, retries, timeouts, circuit breaking, telemetry, authorization, advanced routing |
| **Mesh vs API Gateway** | Gateway: external → internal (authentication, rate limiting, routing, API policies); Mesh: service → service. Internet → API Gateway → Service Mesh → Microservices (coexist) |
| **Mesh vs Ingress** | Ingress: external traffic → cluster services; Mesh: service ↔ service (mesh gateways can also do ingress/egress) |
| **Mesh vs app libraries** | Libraries (retry, timeout, tracing, circuit breaker, TLS) vs Envoy doing them — but **business semantics still need application code** ("don't charge the customer twice" = idempotency) |

## When (not) to use

- **Don't:** small app, 3 services, low traffic, simple deployment (Frontend → Node API → PostgreSQL) — unnecessary complexity, CPU/memory overhead, debugging difficulty, operational burden.
- **Use when:** many microservices (50+), multiple teams/environments, complex traffic, strict security/mTLS/service identity, canary deployments, need for uniform networking policies.
- **Cost:** every sidecar uses resources — 100 Pods = 100 extra proxies (CPU, memory, network traffic, configuration, monitoring).
- **Sidecar vs ambient:** ambient mesh doesn't require a sidecar proxy in each Pod — know sidecar well, ambient conceptually.

## Interview answers

Service mesh (infrastructure layer for service-to-service communication) · sidecar (secondary container alongside the app for cross-cutting infrastructure) · Envoy (high-performance data-plane proxy) · control vs data plane · mTLS (encrypt + mutually authenticate) · circuit breaker (stop sending requests to a failing dependency; fail fast) · why retries are dangerous (amplify load → retry storms/cascading failure) · mesh vs API Gateway · mesh vs Kubernetes Service · "Do you always need Istio?" No — overhead; use when complexity justifies it.

Full request path: Order App → Order Envoy (mTLS, timeout, retry, routing, telemetry) → Payment Envoy (authentication, authorization, telemetry) → Payment App. Production: Route 53 → CloudFront → WAF → Load Balancer → EKS → Istio/mesh → Order/Payment/User services with Envoy sidecars → RDS/Redis.

**Depth:** 🔥 service-mesh concepts, Envoy, sidecar, traffic management, mTLS, retries/timeouts, circuit breaking, API Gateway vs mesh · 🟡 Istio resources/configuration · ⚪ Istio internals, ambient internals, custom Envoy extensions.

## Added (see supplement in the chapter)

`PeerAuthentication` (PERMISSIVE/STRICT) and `AuthorizationPolicy` examples; `timeout`/`retries` in VirtualService; circuit breaking via `DestinationRule` `connectionPool` + `outlierDetection`; **Istio's default retry policy**; iptables redirection; installation profiles; other resources (`Gateway`, `ServiceEntry`, `Sidecar`); alternatives (Linkerd, Consul, Cilium).

<!-- NAV -->

---

← [Sheet 29](ch29-revision.md) · [Full chapter 30](../docs/05-kubernetes/ch30-service-mesh-istio.md) · [All revision material](README.md) · [Sheet 31](ch31-revision.md) →
