# Chapter 22 — Observability + Reliability

> **Source:** Response 22 of the original conversation (`source-archive/src-22.txt`, lines 1–1872) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch22-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

We're now at the part of DevOps that answers:

> **"My system is running in production. How do I know whether it's healthy, why it's slow, and what do I do when something fails?"**

This response ties together almost everything you've learned:

```text
Node.js
 ↓
Docker
 ↓
Kubernetes
 ↓
AWS
 ↓
Database
 ↓
Monitoring
 ↓
Alerts
 ↓
Incident response
```

And again, we're doing this **hands-on**, not just definitions.

---

## 1. What Is Observability?

Suppose your production API suddenly becomes slow.

Users report:

```text
"API is taking 8 seconds."
```

You need to answer:

```text
Why?
```

Maybe:

```text
CPU is high
Memory is exhausted
Database is slow
Redis is unavailable
Network is failing
One endpoint is slow
External API is slow
Too many requests
Pod is restarting
```

Observability gives you the information needed to understand what's happening inside the system from its external behavior.

The classic three pillars are:

```text
          OBSERVABILITY
                │
      ┌─────────┼─────────┐
      ↓         ↓         ↓
    Logs     Metrics    Traces
```

---

## 2. Logs

Logs answer:

> **What happened?**

Example:

```json
{
  "level": "error",
  "event": "database_connection_failed",
  "requestId": "abc123",
  "timestamp": "2026-09-19T10:30:00Z"
}
```

You can inspect them with:

```bash
kubectl logs <pod>
```

or:

```bash
docker logs <container>
```

or through AWS CloudWatch / a centralized logging platform.

---

## 3. Metrics

Metrics answer:

> **How much / how often / how long?**

Examples:

```text
CPU usage
Memory usage
Request count
Request latency
Error rate
Database connections
Queue depth
```

For example:

```text
Requests/sec = 850
p95 latency = 240 ms
Error rate = 1.8%
CPU = 72%
```

Metrics are generally numerical time-series data.

---

## 4. Traces

Traces answer:

> **Where did this particular request spend its time?**

Suppose:

```text
POST /orders
```

takes 2 seconds.

A trace might show:

```text
API
 │
 ├── Authentication       20ms
 │
 ├── Order Service       100ms
 │
 ├── PostgreSQL         1700ms
 │
 └── Response             80ms
```

Now you immediately know:

```text
Database = bottleneck
```

rather than randomly optimizing the Node.js code.

---

## 5. Logs vs Metrics vs Traces

Remember:

| Tool | Main question |
|---|---|
| Logs | What happened? |
| Metrics | How much/how often? |
| Traces | Where did the request spend time? |

Example:

```text
Metrics:
p95 latency = 2 seconds

Trace:
DB query = 1.7 seconds

Logs:
DB timeout occurred
```

Together they're far more useful than any one alone.

---

## PART 1 — NODE.JS LOGGING

### 6. Don't Do This Everywhere

Avoid production logging like:

```ts
console.log("something happened");
```

It lacks useful context.

Prefer structured logs.

For example:

```ts
console.log(JSON.stringify({
  level: "info",
  event: "server_started",
  port,
  timestamp: new Date().toISOString()
}));
```

Now log aggregation systems can parse fields.

---

## 7. Request Logging

Conceptually:

```ts
console.log(JSON.stringify({
  level: "info",
  event: "request_completed",
  method: req.method,
  path: req.path,
  statusCode: res.statusCode,
  durationMs,
  requestId
}));
```

Now you can search:

```text
requestId = abc123
```

and follow a request through the system.

---

## 8. Request IDs

Suppose:

```text
Client
 ↓
ALB
 ↓
API Pod
 ↓
Database
```

A request fails.

You want to correlate all relevant logs.

Generate/propagate a:

```text
requestId
```

Example:

```text
abc123
```

Then:

```text
API log      → abc123
DB-related log → abc123
worker log   → abc123
```

This is extremely useful when debugging distributed systems.

---

## 9. What NOT to Log

Never casually log:

```text
❌ passwords
❌ JWT secrets
❌ API keys
❌ access tokens
❌ database credentials
❌ sensitive personal information
```

Bad:

```ts
console.log(process.env.DATABASE_URL);
```

Don't do this.

Observability itself must be secure.

---

## PART 2 — CLOUDWATCH

You've already learned CloudWatch in [Chapter 17](../04-aws/ch17-monitoring-security.md).

Now understand how it fits into observability.

```text
AWS Resources
     ↓
CloudWatch
     ├── Metrics
     ├── Logs
     ├── Alarms
     └── Dashboards
```

---

## 10. CloudWatch Metrics

Examples:

```text
EC2 CPUUtilization
ALB RequestCount
ALB TargetResponseTime
RDS CPUUtilization
RDS DatabaseConnections
Lambda Invocations
Lambda Errors
```

You can inspect metrics through AWS tooling.

The idea is:

```text
System
 ↓
metric
 ↓
time series
 ↓
dashboard / alarm
```

---

## 11. CloudWatch Logs

Your Node application can produce:

```text
stdout/stderr
```

which can be collected into centralized logging.

Conceptually:

```text
Node.js
 ↓
Container stdout
 ↓
Kubernetes logging
 ↓
Log collector
 ↓
CloudWatch / log platform
```

Don't rely on one exact collection architecture; it depends on your Kubernetes/AWS setup.

---

## 12. CloudWatch Alarm

Suppose:

```text
CPU > 80%
```

for a sustained period.

Create an alarm:

```text
Metric
 ↓
Threshold
 ↓
Alarm
 ↓
Notification / action
```

Example concept:

```text
Average CPU > 80%
for 5 minutes
```

Then trigger:

```text
SNS notification
```

or another appropriate response mechanism.

---

## PART 3 — PROMETHEUS

Now we move into cloud-native observability.

> **Prometheus is a monitoring and metrics system widely used in Kubernetes environments.**

Mental model:

```text
Application
   ↓
Metrics
   ↓
Prometheus
   ↓
Queries
```

---

## 13. Prometheus Pull Model

A key thing to know:

Prometheus commonly **scrapes** metrics from targets.

For example:

```text
Prometheus
    │
    ├── scrape API
    ├── scrape Kubernetes
    ├── scrape node
    └── scrape services
```

Your application can expose a metrics endpoint such as:

```text
/metrics
```

Prometheus periodically retrieves it.

---

## 14. Node.js Metrics

Conceptually:

```text
GET /metrics
```

might expose:

```text
http_requests_total
http_request_duration_seconds
process_cpu_seconds_total
```

Prometheus then stores those metrics as time series.

In a Node.js project, libraries such as `prom-client` are commonly used to expose Prometheus metrics.

Example:

```ts
import client from "prom-client";

client.collectDefaultMetrics();

const httpRequests = new client.Counter({
  name: "http_requests_total",
  help: "Total HTTP requests"
});
```

Then increment:

```ts
httpRequests.inc();
```

You expose:

```text
/metrics
```

and Prometheus scrapes it.

---

## 15. Why Metrics Matter

Suppose you see:

```text
http_requests_total
```

increasing rapidly.

That tells you traffic is increasing.

But more useful is something like:

```text
request rate
error rate
latency
```

which leads us to an important framework.

---

## PART 4 — RED METHOD

For request-driven services, remember:

> **RED**

```text
R → Rate
E → Errors
D → Duration
```

#### Rate

How many requests?

```text
1000 requests/sec
```

#### Errors

How many fail?

```text
2% 5xx
```

#### Duration

How long do requests take?

```text
p95 = 250ms
```

For a backend API, this is an extremely useful monitoring framework.

---

## 16. Percentiles

Don't only look at average latency.

Suppose:

```text
Requests:
10ms
20ms
20ms
30ms
3000ms
```

Average might hide the bad experience.

Use percentiles:

```text
p50
p90
p95
p99
```

For example:

```text
p50 = 40ms
p95 = 250ms
p99 = 900ms
```

Meaning approximately:

```text
95% of requests are at or below 250ms
99% are at or below 900ms
```

Percentiles are very important in production systems.

---

## PART 5 — GRAFANA

Prometheus is primarily the metrics collection/query system.

Grafana is commonly used for visualization and dashboards.

```text
Prometheus
    ↓
Grafana
    ↓
Dashboard
```

Example dashboard:

```text
┌─────────────────────────────────┐
│ API Requests/sec       850      │
├─────────────────────────────────┤
│ Error Rate             0.8%      │
├─────────────────────────────────┤
│ P95 Latency            210ms     │
├─────────────────────────────────┤
│ CPU                    65%       │
├─────────────────────────────────┤
│ Memory                 72%       │
└─────────────────────────────────┘
```

You can visually detect incidents quickly.

---

## 17. Grafana Is Not Prometheus

Common interview question.

```text
Prometheus
→ collects/stores/queries metrics

Grafana
→ visualizes data and creates dashboards
```

Grafana can also connect to other data sources, so it isn't limited to Prometheus.

---

## PART 6 — OPENTELEMETRY

Now traces become more practical.

> **OpenTelemetry (OTel)** is a vendor-neutral framework/ecosystem for generating and collecting telemetry such as traces, metrics, and logs.

Mental model:

```text
Node.js
   ↓
OpenTelemetry
   ↓
Telemetry backend
```

Instead of tightly coupling your application to one observability vendor.

---

## 18. Distributed Tracing

Imagine:

```text
User
 ↓
API
 ↓
Order Service
 ↓
Payment Service
 ↓
PostgreSQL
```

One request:

```text
traceId = abc
```

contains spans:

```text
Trace abc
│
├── API              20ms
├── Order Service    80ms
├── Payment Service 400ms
└── PostgreSQL       50ms
```

Now you can identify:

```text
Payment Service
```

as the slow component.

---

## 19. Trace vs Log

Logs:

```text
"Payment request failed"
```

Trace:

```text
Request
 ↓
API       20ms
 ↓
Order     80ms
 ↓
Payment  400ms ❌
```

Traces give you **request-level causal context**.

---

## PART 7 — SLI / SLO / SLA

This is important for interviews.

### 20. SLI

**Service Level Indicator**

A measurement.

Example:

```text
API availability = 99.95%
```

or:

```text
p95 latency = 180ms
```

---

## 21. SLO

**Service Level Objective**

A target.

Example:

```text
99.9% successful requests
```

or:

```text
p95 latency < 300ms
```

---

## 22. SLA

**Service Level Agreement**

A formal agreement/commitment, typically between a service provider and customer, potentially including consequences if commitments aren't met.

---

## 23. Easy Mental Model

```text
SLI
→ What did we measure?

SLO
→ What target do we want?

SLA
→ What commitment/agreement exists with customers?
```

Example:

```text
SLI:
99.95% availability

SLO:
≥99.9%

SLA:
Formal customer commitment
```

---

## PART 8 — ERROR BUDGET

If your SLO is:

```text
99.9% availability
```

then you're allowing:

```text
0.1%
```

of unavailability/error budget over the relevant period.

Conceptually:

```text
SLO
 ↓
Allowed failure
 ↓
Error budget
```

If your service is consuming the error budget too quickly, engineering teams may prioritize reliability work over risky releases.

This is a major SRE concept.

---

## PART 9 — ALERTING

A common beginner mistake:

```text
CPU > 50%
 ↓
ALERT!
```

This can create noisy alerts.

Better alerts are tied to meaningful user impact or sustained risk.

For example:

```text
5xx error rate > 5%
for 5 minutes
```

or:

```text
p95 latency > 1 second
for 10 minutes
```

depending on the service's actual SLOs.

---

## 24. Alert Quality

A good alert should ideally answer:

```text
What is wrong?
How serious is it?
Who needs to act?
What should they check?
```

Bad:

```text
CPU high
```

Better:

```text
API 5xx rate > 5% for 5 minutes.
Check ALB → Pods → RDS.
```

---

## PART 10 — RELIABILITY

Observability tells you:

> Something is wrong.

Reliability engineering asks:

> How do we design the system so failures are handled safely?

This is where resilience patterns matter.

---

## 25. Timeouts

Imagine:

```text
API
 ↓
Payment Service
```

Payment service never responds.

Without timeout:

```text
API request
   ↓
waiting...
   ↓
waiting...
   ↓
waiting...
```

Eventually resources get exhausted.

With timeout:

```text
Request
 ↓
wait 2 seconds
 ↓
timeout
 ↓
fail gracefully
```

Every network call should have a sensible timeout.

---

## 26. Retries

Suppose:

```text
API → external service
```

fails due to a transient network problem.

Retry:

```text
Attempt 1 ❌
Attempt 2 ❌
Attempt 3 ✅
```

But retries can make things worse.

Imagine:

```text
1000 requests
 ↓
each retries 3 times
 ↓
3000 requests
```

Now the already-overloaded service gets even more traffic.

This is called a **retry storm**.

---

## 27. Exponential Backoff

Instead of:

```text
retry immediately
retry immediately
retry immediately
```

use increasing delays.

Example:

```text
100ms
200ms
400ms
800ms
```

Often with **jitter** to avoid many clients retrying simultaneously.

Conceptually:

```text
failure
 ↓
wait
 ↓
retry
 ↓
wait longer
 ↓
retry
```

---

## 28. Idempotency

This connects to your earlier SQS/Lambda learning.

Suppose:

```text
POST /payment
```

is sent.

Network timeout happens.

Client doesn't know whether payment succeeded.

It retries.

Now you could accidentally charge twice.

Use an:

```text
Idempotency-Key
```

Example:

```text
payment request
Idempotency-Key: abc123
```

Server records:

```text
abc123 → payment result
```

If the same request arrives again:

```text
abc123
```

return the previous result instead of creating another payment.

This is extremely important in production backend systems.

---

## PART 11 — CIRCUIT BREAKER

Suppose:

```text
API
 ↓
Payment Service
```

Payment Service is completely down.

Without protection:

```text
1000 API requests
 ↓
1000 calls to broken service
 ↓
timeouts
 ↓
retries
 ↓
more load
```

A circuit breaker can stop repeatedly calling a failing dependency.

Conceptually:

```text
Healthy
   ↓
Failures increase
   ↓
OPEN
   ↓
Stop calls
   ↓
Wait
   ↓
Half-open
   ↓
Test request
   ↓
Healthy → CLOSED
```

States:

```text
CLOSED
OPEN
HALF-OPEN
```

Know these three.

---

## 29. Circuit Breaker

```text
             Payment Service
                    ↑
                    │
API → Circuit Breaker
          │
          ├── healthy → call
          │
          └── open → fail fast
```

This protects both systems.

---

## PART 12 — BULKHEAD

Imagine one service has several dependency pools.

If one dependency consumes all available resources:

```text
Payment calls
████████████████
```

it shouldn't necessarily starve:

```text
User calls
```

Bulkhead isolation separates resource pools so one failure doesn't consume everything.

Think:

> **Contain the blast radius.**

---

## 30. Rate Limiting

Suppose:

```text
Normal traffic:
100 requests/sec
```

Suddenly:

```text
10,000 requests/sec
```

Your service might collapse.

Rate limiting can enforce:

```text
100 requests/sec per client
```

or another appropriate policy.

Possible locations:

```text
CloudFront
WAF
API Gateway
Load balancer layer
Application
Redis-based distributed limiter
```

depending on architecture.

---

## PART 13 — GRACEFUL SHUTDOWN

This is particularly relevant to Node.js + Kubernetes.

Suppose Kubernetes wants to terminate a Pod.

Don't immediately kill the process while requests are running.

Your application should handle signals such as:

```text
SIGTERM
```

Conceptually:

```ts
process.on("SIGTERM", async () => {
  console.log("Shutting down");

  server.close();

  await databasePool.end();

  process.exit(0);
});
```

The exact implementation depends on your HTTP framework and infrastructure.

The goal:

```text
Stop accepting new work
        ↓
Finish/close existing work
        ↓
Close resources
        ↓
Exit
```

This is important during:

- rolling deployments
- node maintenance
- scaling
- Pod termination

---

## PART 14 — KUBERNETES + RELIABILITY

Now combine [Chapter 20](../05-kubernetes/ch20-kubernetes-networking-scaling.md) and this response.

```text
Deployment
 ↓
multiple Pods
 ↓
Readiness Probe
 ↓
only ready Pods receive traffic
```

If one Pod dies:

```text
Deployment
 ↓
replacement Pod
```

If traffic increases:

```text
HPA
 ↓
more Pods
```

If a node fails:

```text
scheduler
 ↓
Pods can be recreated/rescheduled
```

If application is overloaded:

```text
HPA
+
resource limits
+
rate limiting
```

If dependency fails:

```text
timeout
+
retry/backoff
+
circuit breaker
```

This is reliability engineering.

---

## PART 15 — PRACTICAL NODE.JS OBSERVABILITY

Let's build a simplified production-style setup.

Your API:

```text
Node.js
```

should expose:

```text
/health
/ready
/metrics
```

---

### `/health`

Answers:

> Is the application process alive?

Example:

```ts
app.get("/health", (_req, res) => {
  res.status(200).json({
    status: "ok"
  });
});
```

---

### `/ready`

Answers:

> Can I serve traffic?

Example concept:

```ts
app.get("/ready", async (_req, res) => {
  try {
    await pool.query("SELECT 1");

    res.status(200).json({
      status: "ready"
    });
  } catch {
    res.status(503).json({
      status: "not_ready"
    });
  }
});
```

Don't make readiness checks excessively expensive.

---

## 31. `/metrics`

Using a Prometheus client library:

```ts
import client from "prom-client";

client.collectDefaultMetrics();

app.get("/metrics", async (_req, res) => {
  res.set("Content-Type", client.register.contentType);

  res.end(await client.register.metrics());
});
```

Now:

```text
GET /metrics
```

returns metrics that Prometheus can scrape.

---

## 32. Local Observability Architecture

Conceptually:

```text
              Node.js API
              /    |    \
             ↓     ↓     ↓
          Logs   Metrics  Traces
             │     │       │
             ↓     ↓       ↓
          Logger Prometheus OTel
                    │
                    ↓
                  Grafana
```

A production setup can be significantly more sophisticated, but this is the correct mental model.

---

## PART 16 — INCIDENT RESPONSE

Observability is useless if you don't know how to respond.

Suppose:

```text
ALERT:
API 5xx rate = 8%
```

Don't immediately restart everything.

Use a structured process.

---

## 33. Incident Debugging Flow

```text
ALERT
 ↓
Confirm impact
 ↓
Check metrics
 ↓
Check recent deployments
 ↓
Check logs
 ↓
Trace failing requests
 ↓
Identify dependency
 ↓
Mitigate
 ↓
Verify recovery
 ↓
Root-cause analysis
```

---

## 34. Example Incident

Suppose:

```text
5xx ↑
```

First:

```text
ALB 5xx?
```

Then:

```text
Pod errors?
```

Then:

```text
RDS connections?
```

Maybe you discover:

```text
RDS connections = 1000/1000
```

Then:

```text
API Pods increased
 ↓
each Pod created too many DB connections
 ↓
RDS connection exhaustion
 ↓
requests fail
```

This connects directly to the RDS scaling scenario from [Chapter 13](../04-aws/ch13-rds-databases.md).

---

## 35. Another Incident

```text
p95 latency ↑
```

Metrics:

```text
CPU normal
Memory normal
```

Trace:

```text
API      20ms
Redis   1500ms
DB       30ms
```

Conclusion:

```text
Redis dependency is slow.
```

Now investigate Redis rather than randomly scaling API Pods.

That's the value of observability.

---

## PART 17 — RELIABILITY CHECKLIST

For your Node.js production service:

```text
Application
├── structured logs
├── request IDs
├── metrics
├── tracing
├── /health
├── /ready
└── graceful shutdown

Networking
├── timeouts
├── rate limiting
└── retries with backoff

Dependencies
├── connection pooling
├── circuit breakers where appropriate
└── idempotency for retry-sensitive operations

Kubernetes
├── readiness probes
├── liveness probes
├── resource requests
├── resource limits
├── HPA
└── rolling deployments

AWS
├── CloudWatch
├── alarms
├── CloudTrail
└── load balancer metrics
```

---

## PART 18 — IMPORTANT TRADEOFF

Reliability isn't:

> "Add every resilience mechanism."

For example:

```text
Retry
+
Circuit breaker
+
Timeout
+
Queue
+
Cache
+
Rate limiter
+
Proxy
+
Service mesh
```

can create a massively complicated system.

Instead:

> **Use the simplest mechanism that solves the actual failure mode.**

Example:

```text
External API
 ↓
5 second timeout
+
bounded retry
+
exponential backoff
```

may be enough.

You don't automatically need a service mesh.

---

## PART 19 — WHAT YOU SHOULD KNOW FOR INTERVIEWS

#### Observability

You should comfortably explain:

```text
Logs vs metrics vs traces
Prometheus
Grafana
OpenTelemetry
CloudWatch
structured logging
request IDs
percentiles
RED method
```

#### Reliability

Know:

```text
timeouts
retries
exponential backoff
jitter
idempotency
circuit breaker
bulkhead
rate limiting
graceful shutdown
health checks
```

#### SRE concepts

Know:

```text
SLI
SLO
SLA
error budget
incident response
```

---

## 🧠 The Complete Mental Model

You now have:

```text
                 PRODUCTION SYSTEM
                        │
          ┌─────────────┼─────────────┐
          ↓             ↓             ↓
        Logs         Metrics        Traces
          │             │             │
          └─────────────┼─────────────┘
                        ↓
                 Observability
                        │
                        ↓
                    Detection
                        │
                        ↓
                   Investigation
                        │
                        ↓
                    Mitigation
                        │
                        ↓
                    Recovery
                        │
                        ↓
                 Root Cause Analysis
```

And reliability:

```text
             FAILURE
                │
      ┌─────────┼──────────┐
      ↓         ↓          ↓
   Timeout    Retry    Circuit Breaker
      │         │          │
      └─────────┼──────────┘
                ↓
          Graceful failure
                ↓
           System survives
```

---

## 🔥 Your Full DevOps Stack Is Now Almost Complete

Look at what you can now connect:

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
    ├── Test
    ├── Build
    ├── Docker
    └── Terraform
          │
          ↓
         AWS
          │
   ┌──────┼────────┐
   ↓      ↓        ↓
  VPC    EKS      RDS
          │
       Kubernetes
          │
       ┌──┴───┐
       ↓      ↓
     Pods   Services
       │
       ↓
      App
       │
  ┌────┼─────┐
  ↓    ↓     ↓
Redis RDS   S3

          ↓
    Observability
    ┌─────┼─────┐
    ↓     ↓     ↓
   Logs Metrics Traces
    │     │     │
    └─────┼─────┘
          ↓
      Dashboards
          ↓
        Alerts
          ↓
   Incident Response
```

That's a **very solid SWE-level Cloud + DevOps foundation**.
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 21: Terraform: Infrastructure as Code](../06-iac-config/ch21-terraform.md) · [Chapter 23: Production Architecture + Troubleshooting](../08-production/ch23-production-architecture-troubleshooting.md) → · [Revision sheet](../../revision/ch22-revision.md)
