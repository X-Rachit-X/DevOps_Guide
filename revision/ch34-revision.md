# Chapter 34 — Revision Sheet: Advanced SRE

> Supplements [the full chapter](../docs/07-observability-sre/ch34-advanced-sre.md). Builds on [Chapter 22](../docs/07-observability-sre/ch22-observability-reliability.md). Central idea: *building a system that works is half the job — SRE keeps it reliable when traffic, failures, deployments, dependencies and humans do unexpected things.*

## What SRE is

**SRE = Site Reliability Engineering** = software engineering + operations + reliability + automation. Cares about: can users reach it, how often does it fail, how quickly do we detect and recover, can we deploy without breaking production, survive spikes, what if a dependency fails, how much reliability are we promising. **SRE vs DevOps:** DevOps = how development and operations work together (culture/practice); SRE = how we **engineer measurable reliability** (overlapping). **Reliability is a feature** — an amazing UI/fast API/great DB is still bad if the service is unavailable 10% of the time.

## Availability, SLI / SLO / SLA, error budget

- **Availability = Uptime / Total Time** (99 of 100 hours = 99%). Approx. monthly downtime: 99% → 7 h 18 m · 99.9% → 43 m 49 s · 99.99% → 4 m 23 s · 99.999% → 26 s (so "we need five nines" is very expensive). Going 99% → 99.9% needs redundancy, monitoring, failover, automation, testing; 99.99% → 99.999% needs far more. **Reliability must be balanced against cost and product requirements.**
- **SLI** = measurement (`successful requests / total requests`). **SLO** = engineering target (99.9% successful requests; 99.95% availability). **SLA** = external/business **contractual** commitment (may carry consequences). Example: SLI = successful HTTP requests; SLO = 99.9%; SLA = 99.5% → *SLI = what happened, SLO = what engineers aim for, SLA = what the business promises.*
- Without SLOs nobody has a precise target; with them: availability ≥ 99.9%, p95 < 300 ms, error rate < 0.1%. **Good SLOs reflect user experience** (not "CPU = 72%"): can users accomplish what they came to do? **SLI types:** availability (`successful/total`), latency (% under threshold), correctness (`correct/total results`), freshness (age of latest data), durability (data preserved).
- **Error budget** = `100% − SLO` (SLO 99.9% → 0.1%; with 1,000,000 requests ≈ 1,000 failures consume it all, depending on SLI definition). Exists because 100% reliability is unrealistic and software needs deployments/experiments/changes. Plenty of budget → release, experiment, architecture change; nearly zero budget → reliability work, bug fixes, rollback, capacity. **It's a decision mechanism:** instead of "should we release?" ask "how much reliability budget do we have?"
- **Burn rate** = how quickly the budget is consumed. SLO 99.9% allows 0.1%; observing 0.1% = expected rate; observing 1% ≈ **10×** faster. **Burn-rate alerts** are closer to user impact than "CPU > 80%".
- **Reliability vs availability:** available but unreliable = API responds but 20% of responses are wrong.

## Latency, capacity, load testing

- **Percentiles:** p50 (50% faster), p95 (5% slower), p99 (1% slower). **Average hides tail latency:** 99 requests at 50 ms + 1 at 10 s → average ≈ 149.5 ms but p99 = 10 s. Tail latency matters because one request may call API → Service A → B → C → DB and the slowest dependency dominates. **Latency budget:** target 300 ms → API logic 50 + Redis 20 + DB 100 + external API 80 + network 30 = 280 ms (little margin).
- **Capacity planning:** 1,000 → 10,000 req/s means checking CPU, memory, network, database, cache, queue, storage, connections. "CPU 40%" isn't "plenty" if DB connections are at 95% — find the **limiting resource**. **Little's Law:** `L = λW` (L = average items in system, λ = arrival rate, W = average time in system): 100 req/s × 0.2 s = 20 requests in flight on average.
- **Load testing** (tools: k6, JMeter, Locust, Gatling; k6 is enough): **load** (expected normal/high traffic, 1,000 req/s), **stress** (push beyond expected: 1,000 → 2,000 → 5,000 → 10,000 until it degrades), **spike** (100 → 10,000 req/s), **soak** (hours; finds memory leaks, resource exhaustion, connection leaks). Measure p50/p95/p99, error rate, CPU, memory, DB connections/latency, Redis hit rate, queue depth, GC behaviour, network. Example: 100 req/s → p95 120 ms, 0.01% errors; 500 → 200 ms, 0.1%; 1,000 → 2 s, 5% ⇒ capacity boundary found.
- **Bottleneck analysis:** latency up but API CPU 30% and RDS CPU 95% → scaling API instances won't help.

## Queues, databases, retries, dependencies

- **Queue depth** (producer 1,000/s vs consumer 500/s → +500 jobs/s) and **queue age** (depth 100 is fine, but oldest message 2 hours old is a serious problem) — monitor both; the system looks "up" while users see delays.
- **Database reliability metrics:** CPU, memory, connections, latency, IOPS, locks, deadlocks, replication lag, storage, query performance. **Connection pooling:** 10 API instances × 100 = 1,000 connections → scaling app instances can overload the DB.
- **Retry storm / amplification:** 100 timeouts × 3 retries = 100 + 300 = 400 requests. Correct strategy: **bounded retries + exponential backoff (100 → 200 → 400 ms) + jitter + timeouts**. Retry **transient** failures (temporary network failure, temporary 503, dependency overload); not 400 Bad Request, authentication failures, validation errors.
- **Idempotency + retries:** `POST /payment` succeeds, network fails, client retries → double payment unless `Idempotency-Key: abc123` is recorded (`abc123 → completed result`) and a retry returns the existing result.
- **Circuit breaker:** CLOSED → failures exceed threshold → OPEN (block/fail fast, reject or fallback) → after a period HALF-OPEN (test a few requests) → success → CLOSED / failure → OPEN. **Bulkheads:** separate pools (A=Payment, B=Search, C=User) so one slow dependency can't exhaust all worker threads. **Graceful degradation:** recommendations down → product page still shows product, price, inventory.
- **Fail open vs fail closed:** security authorization unavailable → fail closed (deny sensitive operation); non-critical features may fail open — depends on security/business risk.
- **Dependency mapping / failure matrix** (Order API → PostgreSQL, Redis, Payment API, S3, Notification service): Redis → fall back to DB; Payment → retry + circuit breaker; S3 → retry; Notifications → async queue; DB → fail the request safely. Ask for each: can it fail? what happens? retry? how many times? fallback? cache? queue? fail fast?

## Disaster recovery

- Failures: AZ failure, region failure, database corruption, accidental deletion, ransomware/security incident, major deployment failure. **RTO** = how long can we be down (RTO 1 h = recover within 1 h). **RPO** = how much data can we afford to lose (RPO 5 min ≈ 5 min of data).
- **DR strategies:** **Backup & restore** (cheapest, slowest) · **Pilot light** (minimal standby; during a disaster scale up, restore/attach data, redirect traffic; moderate) · **Warm standby** (reduced-capacity working environment; scale and redirect; faster) · **Active-active** (both regions serve traffic; strong availability but most complex/expensive). Choose by RTO, RPO, cost, business criticality.
- **Multi-AZ** (first layer of HA; protects against AZ failure) vs **Multi-Region** (larger failures/geographic needs; adds data replication, DNS/traffic routing, consistency, deployment, operations, cost) — don't use it because it sounds impressive.
- **Backups:** *untested backups are assumptions, not proven recovery capability* — regularly test restores. DB: automated backups + PITR + snapshots + retention + restore testing; objects: versioning + replication + lifecycle.

## Chaos, incidents, postmortems

- **Chaos engineering:** intentionally break things (kill a pod, terminate an instance, inject latency, drop network, make a dependency unavailable, fill disk) and observe recovery — production will eventually run the experiment for you. Examples: `kubectl delete pod <pod>` (self-healing); Redis down → cache miss → RDS (graceful degradation). **Game day** = planned reliability exercise (detection, diagnosis, communication, mitigation, recovery, postmortem) testing technology *and* people/process. **Failure injection:** Redis latency = 2 s → verify timeout, fallback, circuit breaker.
- **Incident flow:** detect → acknowledge → triage → mitigate → recover → communicate → postmortem. First goal: **restore user-facing service safely**, not find the perfect root cause. **Severity** SEV-1 (major user-facing outage), SEV-2 (significant degradation), SEV-3 (limited impact) — definitions vary. **Mitigation** (stop damage, e.g. rollback) ≠ **root cause** (e.g. bad DB migration).
- **Rollback vs roll-forward:** rollback (v42 → v41) is why immutable images, versioned deployments, Helm rollback and ArgoCD Git revert matter; if a DB migration has already been applied rollback may not work → fix forward → make migrations backward-compatible. **Expand-and-contract** (`name` → `first_name`/`last_name`): add new columns keeping `name` → application writes both → migrate data → new app reads new columns → remove old column later.
- **Postmortem** questions: what happened, when did it start, how detected, impact, why, why didn't safeguards catch it, how recovered, what changes. **Blameless** (systems, processes, conditions, missing safeguards — not "who made the mistake"). Example: API 5xx 20 min; cause: DB connection pool too large; contributing: replicas 5 → 20; not caught: no connection-saturation alert; mitigation: rollback; prevention: pool limits + DB connection alert + load testing.

## Alerting, runbooks, on-call

- Bad alert `CPU > 70%` (maybe normally 75%) vs good `5xx error rate > SLO threshold`. **Alert fatigue** (200 alerts/day) → real alerts ignored → **alerts must be actionable**. Dashboard = investigation/trends/visibility; alert = needs attention. Alert triggers: SLO violation, high error rate, rapid burn, queue age too high, DB unavailable, critical dependency failure, disk nearly full, certificate expiration. Alert context: what happened, impact, service, severity, dashboard, runbook (e.g. "Checkout API 5xx rate > 5%").
- **Runbook** = documented operational procedure (check error rate → latest deployment → DB health → DB connections → dependency latency → roll back if deployment-related → escalate if DB unavailable). **On-call** needs reasonable alert volume, clear escalation, runbooks, observability, incident tooling, postmortems — not an engineer watching dashboards all night. **MTTD** (failure 10:00, alert 10:02 → 2 min). **MTTR** (mean time to recover/repair/resolve; 10:00 → 10:15 = 15 min). Detect quickly + recover quickly.
- **Improvement loop:** build → measure → observe → incident → learn → improve → automate → build again.
- **Monitoring** = "is something wrong?"; **observability** = "why?" (which endpoint/pod/DB query/dependency/deployment/trace). Core: logs + metrics + traces (plus profiles, events, correlations, deployment metadata). **Correlation IDs** (`X-Request-ID: abc123` across API/Order/Payment/Inventory logs). **Distributed trace** example: API 20 ms, Redis 5 ms, DB 150 ms, Payment 500 ms → Payment dominates.

## Runtime protections

- **Graceful shutdown:** SIGTERM → stop accepting new requests → finish existing → close DB → close Redis → exit.
```typescript
process.on("SIGTERM", async () => {
  server.close(async () => {
    await prisma.$disconnect();
    await redis.quit();
    process.exit(0);
  });
});
```
- **Liveness** ("alive?" → restart) vs **readiness** ("can receive traffic?" → remove from traffic); DB temporarily down → alive but not ready, so no needless restarts. **Startup probe** for slow-starting apps (startup → startup probe → ready → readiness/liveness). **PDB:** 5 pods, require ≥ 4 available → constrains voluntary disruptions (node maintenance, cluster operations, voluntary evictions) — doesn't protect against every failure.
- **Rate limiting:** 100,000 req/s from one client → limit to 100 req/s; excess → `429 Too Many Requests`. Strategies: fixed window, sliding window, **token bucket** (tokens refill at a fixed rate; allows controlled bursts + long-term rate limit), leaky bucket. **Load shedding:** accept the safe amount, reject the excess quickly (failing fast can preserve the core service). **Backpressure:** slow down producers because consumers can't keep up (producer 10k/s vs consumer 2k/s → queue, rate limiting, bounded concurrency, not unlimited in-memory work). **Resource limits** (requests influence scheduling, limits constrain usage; `requests: cpu 250m mem 256Mi`, `limits: cpu 1 mem 512Mi`); **noisy neighbour** (Service A at 100% CPU starves B and C).
- **Most important SRE principle:** when stressed, **protect the system before trying to make every request succeed** — accept 20,000 and reject 80,000 quickly rather than attempt all 100,000 and collapse. Reliability is a **system property** (architecture + code + database + network + deployment + observability + security + operations), not a result of "adding Kubernetes/AWS/replicas".

## Reliability testing and review

Test: DB unavailable, Redis unavailable, network timeout, slow dependency, pod killed, node failure, queue backlog, disk full, invalid configuration, expired credentials. **Pre-production review:** compute (scale? one dies?), database (slow/unavailable/connections exhausted?), cache (Redis disappears?), queue (consumers stop? duplicates?), deployment (rollback?), networking (DNS/LB fails?), security (credentials leak?), observability (how will we know?). **Production-readiness checklist:** health endpoints, readiness/liveness, graceful shutdown, timeouts, retry policies, idempotency, rate limiting, circuit breakers, structured logging, metrics, tracing, dashboards, actionable alerts, runbooks, backups, restore testing, rollback strategy, capacity testing, security controls, secret management, failure testing.

## Interview framework — "How would you make your backend reliable?"

1. **Prevent** (testing, code review, safe deployment, capacity planning) · 2. **Detect** (metrics, logs, traces, alerts, SLOs) · 3. **Contain** (rate limiting, circuit breaker, bulkheads, load shedding) · 4. **Recover** (rollback, failover, backups, DR) · 5. **Learn** (postmortem, root cause, action items, automation).

**Scenarios:** *30% 500s* — confirm impact → error rate/latency → recent deployments → logs → traces → affected endpoint → dependencies → database → mitigate → roll back if deployment-related → verify → root cause → postmortem. *DB slow* — CPU, connections, IOPS, slow queries, locks, indexes, replication, pool; immediate: reduce load, cache, queue, rollback, scale, kill problem queries; permanent: query optimisation, index, pool tuning, capacity, architecture. *Redis down* — cache or source of truth? cache → fall back to DB. *Queue growing* — producer rate, consumer rate, worker failures, downstream latency, concurrency; scale consumers, reduce producer rate, fix failing consumers, DLQ poison messages. *Deployment broke production* — stop rollout → rollback if safe → check error rate, logs, traces, DB compatibility, config, secrets, dependencies → root cause → fix → test → redeploy. *Traffic 10×* — autoscaling, CDN, caching, rate limiting, queue, load shedding, database protection; find the bottleneck.

**Definitions:** SLO = engineering reliability target · SLI = measurement · SLA = external/business commitment · error budget = unreliability allowed by the SLO · burn rate = rate the budget is consumed · RTO = maximum acceptable recovery time · RPO = maximum acceptable data-loss window · p99 not average (average hides tail latency) · backoff (avoid immediately re-hitting a failing dependency) · jitter (prevent synchronised retries) · idempotency (safe retries) · circuit breaker (stop calling a failing dependency so it can recover) · bulkhead (isolate resources) · graceful degradation (preserve core functionality) · load testing (understand capacity, bottlenecks, latency, failure behaviour) · chaos testing (validate failure handling as designed).

**Depth:** 🔥 SLI/SLO/SLA, error budgets, burn rate, availability, percentiles, capacity planning, load testing, retries/backoff/jitter, timeouts, idempotency, circuit breakers, bulkheads, rate limiting, backpressure, graceful degradation, incident response, rollback, RTO/RPO, DR strategies, database and queue reliability, observability · 🟡 chaos engineering, game days, active-active, pilot light, warm standby, load shedding, PDB, failure injection, runbooks, on-call · ⚪ specialised SRE platforms, large-scale multi-region internals, advanced chaos frameworks, org-specific incident tooling.

## Added (see supplement in the chapter)

Formulas: allowed downtime, error budget in time/requests, **burn rate = observed error rate ÷ (1 − SLO)**, multi-window multi-burn-rate alerting, **composite availability** (serial multiply, redundant `1 − (1 − A)ⁿ`), MTBF/MTTR availability, Little's Law for pool sizing; PromQL error ratio; runnable **k6** script with SLO thresholds; **token-bucket** TypeScript; four golden signals / USE.

<!-- NAV -->

---

← [Sheet 33](ch33-revision.md) · [Full chapter 34](../docs/07-observability-sre/ch34-advanced-sre.md) · [All revision material](README.md) · [Sheet 35](ch35-revision.md) →
