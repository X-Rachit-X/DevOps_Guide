# Chapter 22 — Revision Sheet: Observability + Reliability

> Supplements [the full chapter](../docs/07-observability-sre/ch22-observability-reliability.md). Question: *"My system is in production. How do I know it's healthy, why it's slow, and what do I do when it fails?"*

## Three pillars

| Pillar | Answers | Example |
|---|---|---|
| **Logs** | What happened? | `{"level":"error","event":"database_connection_failed","requestId":"abc123","timestamp":…}` (via `kubectl logs`, `docker logs`, CloudWatch/central logging) |
| **Metrics** | How much / how often / how long? (numeric time series) | CPU, memory, request count/latency, error rate, DB connections, queue depth: "850 req/s, p95 240 ms, error rate 1.8%, CPU 72%" |
| **Traces** | Where did *this request* spend its time? | `POST /orders` 2 s: Auth 20 ms, Order Service 100 ms, **PostgreSQL 1700 ms**, Response 80 ms → DB is the bottleneck |

Together: metrics say p95 = 2 s → trace says DB query = 1.7 s → logs say DB timeout occurred.

## Logging in Node.js

- Avoid bare `console.log("something happened")`. Use structured JSON (`level`, `event`, `port`, `timestamp`).
- **Request logging:** `level, event:"request_completed", method, path, statusCode, durationMs, requestId`.
- **Request ID:** generate/propagate `requestId` (Client → ALB → API Pod → DB/worker logs) to correlate a failing request across services.
- **Never log:** passwords, JWT secrets, API keys, access tokens, DB credentials, sensitive personal data (e.g. never `console.log(process.env.DATABASE_URL)`). Observability itself must be secure.

## CloudWatch (recap, Ch.17)

Metrics (EC2 `CPUUtilization`, ALB `RequestCount`/`TargetResponseTime`, RDS `CPUUtilization`/`DatabaseConnections`, Lambda `Invocations`/`Errors`), Logs (container stdout → logging collector → CloudWatch; architecture depends on K8s/AWS setup), Alarms (Average CPU > 80% for 5 min → SNS notification or other action), Dashboards.

## Prometheus, Grafana, OpenTelemetry

- **Prometheus:** metrics collection/storage/query system common in Kubernetes. **Pull model:** it **scrapes** targets (API, Kubernetes, nodes, services) — your app exposes `/metrics`.
```ts
import client from "prom-client";
client.collectDefaultMetrics();
const httpRequests = new client.Counter({ name: "http_requests_total", help: "Total HTTP requests" });
httpRequests.inc();
app.get("/metrics", async (_req, res) => {
  res.set("Content-Type", client.register.contentType);
  res.end(await client.register.metrics());
});
```
Typical metrics: `http_requests_total`, `http_request_duration_seconds`, `process_cpu_seconds_total`.
- **Grafana:** visualisation/dashboards (can use many data sources, not only Prometheus). **Prometheus = collects/stores/queries; Grafana = visualises.**
- **OpenTelemetry (OTel):** vendor-neutral framework for generating/collecting traces, metrics, logs (Node.js → OTel → telemetry backend; avoids vendor lock-in).
- **Distributed tracing:** one request has a `traceId` and multiple **spans** (API 20 ms, Order Service 80 ms, Payment Service 400 ms ❌, PostgreSQL 50 ms) → find the slow component. Traces give request-level causal context (logs say "Payment request failed").
- Local architecture: Node API → Logs (logger) / Metrics (Prometheus → Grafana) / Traces (OTel).

## RED method and percentiles

- **RED** (request-driven services): **R**ate (1000 req/s) · **E**rrors (2% 5xx) · **D**uration (p95 = 250 ms).
- **Percentiles, not just averages:** requests 10, 20, 20, 30, **3000 ms** — the average hides the bad experience. p50/p90/p95/p99: e.g. p50 40 ms, p95 250 ms (95% of requests ≤ 250 ms), p99 900 ms.

## SLI / SLO / SLA and error budget

| | Meaning | Example |
|---|---|---|
| **SLI** | What did we measure? | availability 99.95%; p95 latency 180 ms |
| **SLO** | Target | ≥ 99.9% successful requests; p95 < 300 ms |
| **SLA** | Formal customer commitment, possibly with consequences if missed | |

**Error budget:** SLO 99.9% allows **0.1%** unavailability over the period → SLO → allowed failure → error budget. If it's consumed too quickly, teams prioritise reliability work over risky releases (major SRE concept; deep dive in Ch.34).

## Alerting

- Bad: `CPU > 50%` → ALERT (noisy). Better: tied to user impact/sustained risk, e.g. `5xx error rate > 5% for 5 minutes`, `p95 latency > 1 second for 10 minutes` (depending on SLOs).
- A good alert says: what's wrong, how serious, who acts, what to check. Bad: "CPU high". Better: "API 5xx rate > 5% for 5 minutes. Check ALB → Pods → RDS."

## Reliability patterns

| Pattern | Idea |
|---|---|
| **Timeouts** | Every network call needs one (without: requests wait forever and exhaust resources); e.g. wait 2 s then fail gracefully |
| **Retries** | Recover transient failures, but **retry storm** risk: 1000 requests × 3 retries = 3000 requests onto an already-overloaded service |
| **Exponential backoff + jitter** | 100 → 200 → 400 → 800 ms, with randomness so clients don't retry simultaneously |
| **Idempotency** | `Idempotency-Key: abc123` → server records `abc123 → result`; same request again returns the stored result (no double charge on `POST /payment`) |
| **Circuit breaker** | Healthy (**CLOSED**) → failures increase → **OPEN** (stop calls, fail fast) → wait → **HALF-OPEN** (test request) → healthy → CLOSED. Protects both systems |
| **Bulkhead** | Separate resource pools so a failing dependency (payment calls) can't starve others (user calls) — contain the blast radius |
| **Rate limiting** | e.g. 100 req/s per client; at CloudFront, WAF, API Gateway, load balancer, application, Redis-based distributed limiter |
| **Graceful shutdown** | On SIGTERM: stop accepting new work → finish/close existing work → close resources → exit |

```ts
process.on("SIGTERM", async () => {
  console.log("Shutting down");
  server.close();
  await databasePool.end();
  process.exit(0);
});
```
Matters during rolling deployments, node maintenance, scaling, Pod termination.

**Kubernetes + reliability:** multiple Pods + readiness probe (only ready Pods get traffic); Pod dies → replacement; traffic ↑ → HPA; node fails → scheduler recreates Pods; overload → HPA + limits + rate limiting; dependency failure → timeout + retry/backoff + circuit breaker.
**Trade-off:** don't add every mechanism (retry + breaker + timeout + queue + cache + limiter + proxy + service mesh) — use the simplest mechanism that solves the failure mode (e.g. 5 s timeout + bounded retry + exponential backoff may be enough; you don't automatically need a service mesh).

## Endpoints to implement

`/health` (process alive → `{status:"ok"}`), `/ready` (e.g. `await pool.query("SELECT 1")` → 200 `ready`, else 503 `not_ready`; keep it cheap), `/metrics` (Prometheus).

## Incident response flow

ALERT → confirm impact → check metrics → check recent deployments → check logs → trace failing requests → identify dependency → mitigate → verify recovery → root-cause analysis. (Don't immediately restart everything.)
- *5xx rate 8%:* ALB 5xx? → Pod errors? → RDS connections = 1000/1000 ⇒ API Pods increased, each created too many DB connections ⇒ RDS connection exhaustion (Ch.13).
- *p95 latency ↑, CPU/memory normal:* trace API 20 ms, **Redis 1500 ms**, DB 30 ms ⇒ investigate Redis instead of randomly scaling API Pods.

## Reliability checklist

Application: structured logs, request IDs, metrics, tracing, `/health`, `/ready`, graceful shutdown · Networking: timeouts, rate limiting, retries with backoff · Dependencies: pooling, circuit breakers where appropriate, idempotency · Kubernetes: readiness, liveness, requests, limits, HPA, rolling deployments · AWS: CloudWatch, alarms, CloudTrail, LB metrics.

## Interview checklist

Observability: logs vs metrics vs traces, Prometheus, Grafana, OpenTelemetry, CloudWatch, structured logging, request IDs, percentiles, RED. Reliability: timeouts, retries, backoff, jitter, idempotency, circuit breaker, bulkhead, rate limiting, graceful shutdown, health checks. SRE: SLI, SLO, SLA, error budget, incident response.

## Added notes (not in source)

- **Error-budget arithmetic:** `budget = (1 − SLO) × period`. For a 30-day month (43,200 min): 99% → 432 min (7.2 h); 99.9% → **43.2 min**; 99.99% → 4.32 min.
- **Backoff formula:** `delay = min(cap, base × 2^attempt)`, then add jitter (e.g. "full jitter": random between 0 and that delay).
- Prometheus extras: query language **PromQL**, **Alertmanager** routes alerts, **exporters** expose metrics for systems you can't instrument; latency is best recorded as a **histogram** (`http_request_duration_seconds`) so percentiles can be computed — averaging per-instance percentiles is incorrect.
- Trace context is propagated between services via headers (W3C `traceparent`); OTel spans share a `traceId`.
- Google SRE's **four golden signals**: latency, traffic, errors, saturation (RED + saturation); the **USE** method (utilization, saturation, errors) targets resources (see [Chapter 34](../docs/07-observability-sre/ch34-advanced-sre.md)).
- Graceful shutdown in Kubernetes also depends on `terminationGracePeriodSeconds` and often a `preStop` delay so the Pod is removed from Service endpoints before the process stops; `server.close()` stops new connections but in-flight keep-alive connections may linger.

<!-- NAV -->

---

← [Sheet 21](ch21-revision.md) · [Full chapter 22](../docs/07-observability-sre/ch22-observability-reliability.md) · [All revision material](README.md) · [Sheet 23](ch23-revision.md) →
