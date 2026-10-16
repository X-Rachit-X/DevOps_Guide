# Chapter 34 — Advanced SRE

> **Source:** Response 34 of the original conversation (`source-archive/src-34.txt`, lines 1–3735) · **Part II — Advanced extension (Responses 25–36)**  
> **Study aids:** [Revision sheet](../../revision/ch34-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md) · *includes an editorial supplement at the end*

<!-- SOURCE-BEGIN -->

We are now at **Chapter 34/36**.

This is the final major theory section before the capstone.

You already covered SRE fundamentals in [Chapter 22](ch22-observability-reliability.md):

- logs
- metrics
- traces
- RED
- p50/p95/p99
- SLIs/SLOs/SLAs
- error budgets
- timeouts
- retries
- backoff
- jitter
- idempotency
- circuit breakers
- bulkheads
- rate limiting
- graceful shutdown
- incident debugging

So this response goes **much deeper into operating production systems**.

The central SRE idea is:

> **Building a system that works is only half the job. SRE is about keeping it reliable when traffic, failures, deployments, dependencies, and humans do unexpected things.**

---

## 1. What SRE Actually Means

SRE = **Site Reliability Engineering**.

A simplified view:

```text
Software Engineering
       +
Operations
       +
Reliability
       +
Automation
       ↓
      SRE
```

An SRE cares about questions like:

```text
Can users reach the service?

How often does it fail?

How quickly can we detect failures?

How quickly can we recover?

Can we deploy without breaking production?

Can the system survive traffic spikes?

What happens when a dependency fails?

How much reliability are we actually promising?
```

---

## 2. SRE Is Not Just "DevOps"

DevOps is a broader engineering culture/practice around:

```text
development
+
operations
+
automation
+
delivery
```

SRE provides a more reliability-focused engineering approach.

Think:

```text
DevOps
  ↓
How do development and operations work together?

SRE
  ↓
How do we engineer measurable reliability?
```

They overlap heavily.

---

## 3. Reliability Is a Feature

Suppose you have:

```text
Amazing UI
Fast API
Great database
```

but:

```text
service unavailable 10% of the time
```

The system is still bad for users.

Therefore:

> **Reliability is part of the product, not merely an infrastructure concern.**

---

## 4. Availability

Availability answers:

> "How often is the service usable?"

A simple formula:

```text
Availability =
Uptime / Total Time
```

Suppose a service is available:

```text
99 hours
```

out of:

```text
100 hours
```

Then:

```text
Availability = 99%
```

---

## 5. Availability and Downtime

This becomes important with SLAs/SLOs.

Approximate monthly downtime:

| Availability | Approx. downtime/month |
|---|---:|
| 99% | 7h 18m |
| 99.9% | 43m 49s |
| 99.99% | 4m 23s |
| 99.999% | 26s |

This is why:

> "We need five nines."

is a very expensive requirement.

---

## 6. More Reliability Is Not Free

Going from:

```text
99%
```

to:

```text
99.9%
```

may require:

```text
redundancy
monitoring
failover
automation
testing
```

Going from:

```text
99.99%
```

to:

```text
99.999%
```

can require significantly more engineering and operational complexity.

Therefore:

> Reliability must be balanced against cost and product requirements.

---

## 7. SLA

SLA = **Service Level Agreement**.

This is a contractual/business commitment.

For example:

> "Service availability will be at least X%."

An SLA may have consequences if the provider fails to meet the commitment.

Important distinction:

```text
SLA
→ external/business commitment
```

---

## 8. SLO

SLO = **Service Level Objective**.

This is the reliability target your engineering organization sets.

Example:

```text
99.9% successful requests
```

or:

```text
99.95% availability
```

SLOs are engineering targets.

---

## 9. SLI

SLI = **Service Level Indicator**.

This is the measurement.

For example:

```text
successful requests / total requests
```

That's an SLI.

So:

```text
SLI
→ measurement

SLO
→ target

SLA
→ contractual commitment
```

Memorize this.

---

## 10. Example

Suppose:

```text
SLI:
successful HTTP requests
```

You define:

```text
SLO:
99.9% successful requests
```

And your company promises:

```text
SLA:
99.5% availability
```

Then:

```text
SLI = what happened
SLO = what engineers aim for
SLA = what business promises
```

---

## 11. Why SLOs Matter

Without SLOs:

```text
Developer:
"It seems reliable."

Manager:
"It should be faster."

SRE:
"We need better reliability."
```

Nobody has a precise target.

With SLOs:

```text
Availability ≥ 99.9%
p95 latency < 300 ms
error rate < 0.1%
```

Now reliability becomes measurable.

---

## 12. Good SLOs Should Represent User Experience

Don't monitor:

```text
CPU = 72%
```

and call that a user-facing SLO.

CPU is an infrastructure metric.

A better SLI might be:

```text
HTTP requests successfully completed
```

or:

```text
p95 checkout latency
```

The question is:

> **Can users successfully accomplish what they came to do?**

---

## 13. Different Types of SLI

#### Availability

```text
successful requests / total requests
```

#### Latency

```text
percentage of requests under threshold
```

#### Correctness

For some systems:

```text
correct results / total results
```

#### Freshness

For data systems:

```text
age of latest data
```

#### Durability

For storage:

```text
data successfully preserved
```

The right SLI depends on the service.

---

## 14. Error Budget

This is one of the most important SRE concepts.

Suppose:

```text
SLO = 99.9%
```

Then allowed failure is:

```text
0.1%
```

That allowed failure is your:

> **Error budget**

Conceptually:

```text
100% reliability
     -
SLO
     =
error budget
```

---

## 15. Why Error Budgets Exist

You could demand:

```text
100% reliability
```

but that's unrealistic.

Software needs:

```text
deployments
experiments
changes
new features
```

Some risk is unavoidable.

Error budgets give teams a controlled amount of failure.

---

## 16. Error Budget Example

Suppose:

```text
SLO = 99.9%
```

Then:

```text
Error budget = 0.1%
```

If your service performs:

```text
1,000,000 requests
```

approximately:

```text
1,000 failed requests
```

would consume the entire 0.1% budget, depending on the exact SLI definition.

---

## 17. Error Budget and Deployments

Suppose your service has plenty of error budget:

```text
Budget remaining = high
```

You might safely allow:

```text
new release
performance experiment
architecture change
```

But if:

```text
Budget remaining = almost zero
```

you may prioritize:

```text
reliability work
bug fixes
rollback
capacity
```

rather than adding risky changes.

---

## 18. Error Budget Is a Decision Mechanism

This is the key idea.

Instead of arguing:

> "Should we release this?"

you can ask:

> "How much reliability budget do we have?"

This creates an objective engineering framework.

---

## 19. Burn Rate

Error budget isn't only about whether you've exceeded it.

You should also ask:

> "How quickly are we consuming it?"

That's:

> **Error budget burn rate**

Example:

```text
Normal:
small amount of errors
```

Suddenly:

```text
deployment
 ↓
error rate increases dramatically
```

Your error budget is being consumed quickly.

That's a high burn rate.

---

## 20. Burn Rate Example

Suppose:

```text
SLO = 99.9%
```

Your expected allowed error rate:

```text
0.1%
```

If you're seeing:

```text
0.1%
```

you're consuming the budget at approximately the expected rate.

If you suddenly see:

```text
1%
```

you're burning the budget roughly ten times faster.

This can trigger an alert.

---

## 21. Why Burn-Rate Alerts Are Useful

A normal alert might say:

```text
CPU > 80%
```

But CPU isn't necessarily a user problem.

A burn-rate alert asks:

```text
Are we consuming our reliability budget too quickly?
```

That's much closer to user impact.

---

## 22. Reliability vs Availability

They aren't exactly identical.

#### Availability

> Is the service accessible/working?

#### Reliability

> Does the system consistently perform correctly over time despite failures?

A system can be:

```text
available
```

but unreliable.

Example:

```text
API responds
but 20% of responses are incorrect
```

It's technically reachable but not reliable from the user's perspective.

---

## 23. Latency Percentiles

You've already learned:

```text
p50
p95
p99
```

Let's go deeper.

Suppose:

```text
100,000 requests
```

#### p50

50% of requests are faster than this value.

#### p95

95% are faster.

5% are slower.

#### p99

99% are faster.

1% are slower.

---

## 24. Why Average Latency Is Dangerous

Suppose:

```text
99 requests = 50 ms
1 request = 10 seconds
```

Average:

```text
~149.5 ms
```

That doesn't tell the whole story.

p99:

```text
10 seconds
```

which reveals the terrible tail latency.

Therefore:

> Production systems care heavily about tail latency.

---

## 25. Tail Latency

Tail latency means the slowest portion of requests.

Examples:

```text
p95
p99
p99.9
```

Why does it matter?

Large systems often have multiple dependencies.

If one request calls:

```text
API
 ↓
Service A
 ↓
Service B
 ↓
Service C
 ↓
Database
```

the slowest dependency can dominate the user's latency.

---

## 26. Latency Budget

Just like reliability has an error budget, you can reason about latency constraints.

Suppose:

```text
API target = 300 ms
```

Then you might allocate:

```text
API logic      50 ms
Redis          20 ms
DB             100 ms
external API   80 ms
network        30 ms
```

Total:

```text
280 ms
```

Now you have little margin.

This helps identify bottlenecks.

---

## 27. Capacity Planning

Capacity planning asks:

> "Can our infrastructure handle expected demand?"

Suppose:

```text
Current:
1,000 requests/sec
```

Expected next year:

```text
10,000 requests/sec
```

You need to understand:

```text
CPU
memory
network
database
cache
queue
storage
connections
```

---

## 28. Capacity Planning Is Not Just CPU

A common mistake:

> "CPU is only 40%, so we have plenty of capacity."

Maybe:

```text
CPU = 40%
RAM = 60%
DB connections = 95%
```

Your actual bottleneck is:

```text
database connections
```

Capacity planning requires identifying the limiting resource.

---

## 29. Little's Law

A useful queueing concept:

```text
L = λW
```

where:

```text
L = average number of items in system
λ = arrival rate
W = average time in system
```

Example:

```text
100 requests/sec
```

and:

```text
average latency = 200 ms = 0.2 sec
```

Then:

```text
L = 100 × 0.2
  = 20
```

Approximately 20 requests are in the system on average.

This becomes useful when reasoning about concurrency.

---

## 30. Load Testing

Load testing asks:

> "What happens when we give the system realistic traffic?"

Tools you may encounter:

```text
k6
JMeter
Locust
Gatling
```

You don't need to master all of them.

For your backend projects, understanding **k6** is enough.

---

## 31. Types of Load Tests

#### Load test

Expected normal/high traffic.

```text
1,000 req/s
```

#### Stress test

Push beyond expected capacity.

```text
1,000
2,000
5,000
10,000...
```

until the system degrades.

#### Spike test

Sudden traffic increase:

```text
100
 ↓
10,000 req/s
```

#### Soak test

Long duration:

```text
several hours
```

to detect:

```text
memory leaks
resource exhaustion
connection leaks
```

---

## 32. What You Measure During Load Tests

Don't just measure:

```text
requests/sec
```

Also:

```text
p50 latency
p95 latency
p99 latency
error rate
CPU
memory
DB connections
DB latency
Redis hit rate
queue depth
GC behavior
network
```

---

## 33. Load Test Example

Suppose:

```text
100 req/s
```

System:

```text
p95 = 120ms
errors = 0.01%
```

Then:

```text
500 req/s
```

becomes:

```text
p95 = 200ms
errors = 0.1%
```

At:

```text
1,000 req/s
```

you see:

```text
p95 = 2s
errors = 5%
```

You've found a capacity boundary.

---

## 34. Bottleneck Analysis

Suppose API latency increases.

Don't immediately increase EC2/EKS replicas.

Investigate:

```text
API CPU?
API memory?
DB?
Redis?
network?
external API?
connection pool?
lock contention?
```

For example:

```text
API CPU = 30%
RDS CPU = 95%
```

Scaling API instances won't solve the main problem.

---

## 35. Queue Depth as a Reliability Signal

For asynchronous systems:

```text
queue depth
```

is extremely important.

Suppose:

```text
Producer = 1,000 jobs/sec
Consumer = 500 jobs/sec
```

Then queue depth grows:

```text
+500 jobs/sec
```

Eventually:

```text
queue
→ millions of messages
```

The system may still appear "up," but users experience increasing delays.

---

## 36. Queue Age

Queue depth isn't always enough.

Suppose:

```text
queue depth = 100
```

That might be perfectly fine.

But if the oldest message is:

```text
2 hours old
```

you have a serious processing problem.

So monitor:

```text
oldest message age
```

as well.

---

## 37. Database Reliability

Your database is often the hardest dependency.

Important metrics:

```text
CPU
memory
connections
latency
IOPS
locks
deadlocks
replication lag
storage
query performance
```

---

## 38. Connection Pooling

Suppose:

```text
10 API instances
```

and each has:

```text
100 DB connections
```

Then:

```text
10 × 100
= 1,000 connections
```

Your database may not support that.

Therefore:

> Scaling application instances can accidentally overload your database.

This is one of the most important production lessons.

---

## 39. Retry Storm

Suppose database becomes slow.

100 requests timeout.

Each retries 3 times.

Now:

```text
100 original requests
+
300 retries
=
400 requests
```

The dependency becomes even more overloaded.

This is:

> **Retry amplification / retry storm**

---

## 40. Correct Retry Strategy

Don't blindly retry everything.

Use:

```text
bounded retries
+
exponential backoff
+
jitter
+
timeouts
```

For example:

```text
attempt 1
 ↓
100ms
 ↓
attempt 2
 ↓
200ms
 ↓
attempt 3
 ↓
400ms
```

with randomness/jitter to prevent synchronized retries.

---

## 41. What Should You Retry?

Generally, retry operations that are:

```text
transiently failing
```

such as:

```text
temporary network failure
temporary 503
temporary dependency overload
```

Be careful with:

```text
400 Bad Request
authentication failures
validation errors
```

Retrying those usually doesn't fix anything.

---

## 42. Idempotency + Retries

Retries create a dangerous question:

> "What if the first request succeeded but the response was lost?"

Example:

```text
Client
 ↓
POST /payment
 ↓
Payment succeeds
 ↓
network failure
 ↓
client doesn't know
 ↓
retry
```

Now payment might happen twice.

Therefore critical operations need:

```text
idempotency keys
```

Example:

```http
Idempotency-Key: abc123
```

The server records:

```text
abc123 → completed result
```

A retry returns the existing result rather than performing the operation again.

---

## 43. Circuit Breaker

You've seen the concept.

Now understand why.

Suppose:

```text
API
 ↓
Payment Service
```

Payment service is failing.

Without circuit breaker:

```text
1000 API requests
 ↓
1000 payment requests
 ↓
payment service overwhelmed
```

Circuit breaker:

```text
healthy
 ↓
failures increase
 ↓
OPEN
 ↓
reject/fallback
```

The failing dependency gets breathing room.

---

## 44. Circuit Breaker States

Usually:

```text
CLOSED
```

Normal operation.

Failures exceed threshold:

```text
OPEN
```

Calls are blocked/fail fast.

After a period:

```text
HALF-OPEN
```

Test a small number of requests.

If successful:

```text
CLOSED
```

If failures continue:

```text
OPEN
```

---

## 45. Bulkheads

Imagine one service has:

```text
10 worker threads
```

and one slow dependency consumes all of them.

Now unrelated requests cannot execute.

Bulkheads isolate resources.

Conceptually:

```text
Pool A
→ Payment

Pool B
→ Search

Pool C
→ User
```

If Payment fails:

```text
Pool A exhausted
```

but:

```text
Pool B
Pool C
```

continue working.

---

## 46. Graceful Degradation

Suppose:

```text
Recommendation Service
```

fails.

Does the entire application need to fail?

Maybe not.

Instead:

```text
Product page
 ↓
recommendations unavailable
 ↓
show product normally
```

This is:

> **Graceful degradation**

---

## 47. Fail Open vs Fail Closed

This depends on the system.

#### Fail closed

When failure should deny access.

Example:

```text
security authorization unavailable
→ don't allow sensitive operation
```

#### Fail open

When availability is more important and the risk is acceptable.

Example scenarios may involve certain non-critical features.

The correct choice depends heavily on the security/business requirement.

---

## 48. Dependency Mapping

A production service should know its dependencies.

Example:

```text
Order API
├── PostgreSQL
├── Redis
├── Payment API
├── S3
└── Notification service
```

Now ask:

> What happens if each dependency fails?

Create a table mentally:

| Dependency | Failure strategy |
|---|---|
| Redis | fallback to DB |
| Payment | retry + circuit breaker |
| S3 | retry |
| Notifications | async queue |
| DB | fail request safely |

This is reliability engineering.

---

## 49. Dependency Failure Matrix

For every dependency ask:

```text
Can it fail?
What happens?
Do we retry?
How many times?
Can we fallback?
Should we cache?
Should we queue?
Should we fail fast?
```

This is an excellent interview framework.

---

## 50. Disaster Recovery

Now we move from small failures to major failures.

Examples:

```text
AZ failure
region failure
database corruption
accidental deletion
ransomware/security incident
major deployment failure
```

Disaster Recovery = ability to restore service after major disruption.

---

## 51. RTO

RTO = **Recovery Time Objective**.

Question:

> "How long can we be down?"

Example:

```text
RTO = 1 hour
```

means:

```text
service should recover within 1 hour
```

---

## 52. RPO

RPO = **Recovery Point Objective**.

Question:

> "How much data can we afford to lose?"

Example:

```text
RPO = 5 minutes
```

means:

```text
at most approximately 5 minutes of data loss
```

depending on the system's backup/replication design.

---

## 53. RTO vs RPO

Memorize:

```text
RTO
→ how long can we be down?

RPO
→ how much data can we lose?
```

---

## 54. DR Strategies

There are several approaches.

#### Backup and Restore

```text
Primary
   ↓
Backups
   ↓
disaster
   ↓
restore
```

Cheaper.

Recovery takes longer.

---

## 55. Pilot Light

Keep minimal infrastructure ready.

```text
small standby environment
```

During disaster:

```text
scale up
restore/attach data
redirect traffic
```

---

## 56. Warm Standby

Maintain a smaller working environment:

```text
Primary
 ↓
full capacity

Secondary
 ↓
reduced capacity
```

During disaster:

```text
scale secondary
redirect traffic
```

Faster recovery than backup/restore.

---

## 57. Active-Active

Both environments serve traffic.

```text
Region A
 ↘
  users
 ↗
Region B
```

During failure:

```text
Region A down
 ↓
Region B continues
```

This can provide strong availability but is much more complex and expensive.

---

## 58. DR Strategy Comparison

```text
Backup/Restore
→ cheapest
→ slowest recovery

Pilot Light
→ low standby capacity
→ moderate recovery

Warm Standby
→ running reduced system
→ faster

Active-Active
→ both serve traffic
→ highest complexity/cost
```

Choose according to:

```text
RTO
RPO
cost
business criticality
```

---

## 59. Multi-AZ vs Multi-Region

This is important.

#### Multi-AZ

Protects against:

```text
Availability Zone failure
```

Usually the first layer of high availability.

#### Multi-Region

Protects against larger regional failures and can support geographic requirements.

But it introduces major complexity:

```text
data replication
DNS/traffic routing
consistency
deployment
operations
cost
```

Don't use multi-region just because it sounds impressive.

---

## 60. Backups Are Not Enough

A backup is useful only if:

```text
you can restore it
```

Therefore:

> **Untested backups are assumptions, not proven recovery capability.**

Regularly test restoration.

---

## 61. Backup Strategy

For a database:

```text
automated backups
+
point-in-time recovery
+
snapshots
+
retention policy
+
restore testing
```

For objects:

```text
versioning
+
replication where needed
+
lifecycle
```

---

## 62. Chaos Engineering

Chaos engineering asks:

> "What happens if we intentionally break something?"

Examples:

```text
kill a pod
terminate an instance
inject latency
drop network traffic
make dependency unavailable
fill disk
```

Then observe whether the system recovers.

---

## 63. Why Chaos Engineering?

Because production will eventually perform the experiment for you.

Better:

```text
controlled failure
→ observe
→ improve
```

than:

```text
real failure
→ discover architecture is broken
```

---

## 64. Simple Chaos Experiment

Suppose:

```text
EKS
→ 5 backend pods
```

Kill one:

```bash
kubectl delete pod <pod>
```

Expected:

```text
Deployment
 ↓
detect missing replica
 ↓
create replacement
```

Now you have tested self-healing.

---

## 65. Another Experiment

Suppose:

```text
Redis
```

becomes unavailable.

Question:

> Does the API completely fail?

If your design supports fallback:

```text
Redis unavailable
 ↓
cache miss
 ↓
RDS
```

the application can continue.

This validates graceful degradation.

---

## 66. Game Days

A game day is a planned reliability exercise.

Example:

> "Today we'll simulate database failure."

Teams practice:

```text
detection
diagnosis
communication
mitigation
recovery
postmortem
```

This tests both technology and people/processes.

---

## 67. Incident Management

When production breaks:

```text
incident
 ↓
detect
 ↓
acknowledge
 ↓
triage
 ↓
mitigate
 ↓
recover
 ↓
communicate
 ↓
postmortem
```

The first goal isn't:

> "Find the perfect root cause immediately."

The first goal is:

> **Restore user-facing service safely.**

---

## 68. Incident Severity

Organizations often define levels such as:

```text
SEV-1
SEV-2
SEV-3
```

Exact definitions vary.

For example:

```text
SEV-1
→ major user-facing outage

SEV-2
→ significant degradation

SEV-3
→ limited impact
```

Don't memorize exact labels because companies define them differently.

Understand severity classification.

---

## 69. Mitigation vs Root Cause

Suppose:

```text
deployment
 ↓
error rate 50%
```

Immediate mitigation:

```text
rollback
```

Root cause investigation:

```text
bad database migration
```

These are different.

```text
Mitigation
→ stop damage

Root cause
→ understand why
```

---

## 70. Rollback

If a deployment caused the incident:

```text
version 42
 ↓
errors
```

rollback:

```text
version 41
```

This is why you learned:

```text
immutable images
versioned deployments
Helm rollback
ArgoCD Git revert
```

earlier.

---

## 71. Roll Forward

Sometimes rollback is dangerous.

Example:

```text
database migration already applied
```

Rolling application code backward might not work.

Instead:

```text
fix forward
```

deploy a corrected version.

This is why database migrations should be backward-compatible where possible.

---

## 72. Expand-and-Contract Migration

Suppose old application expects:

```text
name
```

You need:

```text
first_name
last_name
```

Don't immediately remove `name`.

Instead:

#### Phase 1

Add:

```text
first_name
last_name
```

while keeping:

```text
name
```

#### Phase 2

Application writes both.

#### Phase 3

Migrate data.

#### Phase 4

New application reads new columns.

#### Phase 5

Remove old column later.

This minimizes deployment coupling.

---

## 73. Postmortem

After a significant incident:

```text
What happened?
When did it start?
How was it detected?
What was the impact?
Why did it happen?
Why didn't our safeguards catch it?
How did we recover?
What will we change?
```

---

## 74. Blameless Postmortem

A good postmortem focuses on:

```text
systems
processes
conditions
technical causes
missing safeguards
```

rather than:

```text
"Who made the mistake?"
```

Humans make mistakes.

Good systems make those mistakes less catastrophic.

---

## 75. Example Postmortem

#### Incident

```text
API returned 5xx for 20 minutes.
```

#### Cause

```text
Database connection pool too large.
```

#### Contributing factor

```text
new deployment increased replicas from 5 → 20.
```

#### Why wasn't it caught?

```text
no connection saturation alert
```

#### Mitigation

```text
rollback
```

#### Prevention

```text
connection pool limits
+
DB connection alert
+
load testing
```

This is a good postmortem structure.

---

## 76. Alerting

A bad alert:

```text
CPU > 70%
```

Maybe CPU is normally 75%.

You'll get noise.

A better alert:

```text
5xx error rate > SLO threshold
```

because it represents user impact.

---

## 77. Alert Fatigue

Suppose engineers receive:

```text
200 alerts/day
```

Most are not actionable.

Eventually:

```text
engineer sees alert
 ↓
ignores it
```

Then the one important alert appears.

This is dangerous.

Therefore:

> **Alerts should be actionable.**

---

## 78. Alert vs Dashboard

#### Dashboard

Used for:

```text
investigation
trend analysis
visibility
```

#### Alert

Used for:

```text
something needs attention
```

Don't alert on every metric.

---

## 79. What Should Trigger an Alert?

Good candidates:

```text
SLO violation
high error rate
rapid error-budget burn
queue age too high
database unavailable
critical dependency failure
disk nearly full
certificate expiration
```

The exact thresholds depend on the service.

---

## 80. Alert Should Have Context

A useful alert should tell you:

```text
what happened
impact
service
severity
dashboard
runbook
```

Example:

```text
ALERT:
Checkout API 5xx rate > 5%

Impact:
High checkout failure rate

Dashboard:
...

Runbook:
...
```

Much better than:

```text
CPU ALERT
```

---

## 81. Runbooks

A runbook is a documented operational procedure.

Example:

> "Checkout API is returning 5xx."

Runbook:

```text
1. Check error rate.
2. Check latest deployment.
3. Check DB health.
4. Check DB connections.
5. Check dependency latency.
6. Roll back if deployment is responsible.
7. Escalate if DB unavailable.
```

Runbooks reduce response time.

---

## 82. On-Call

On-call means engineers are responsible for responding to incidents during assigned periods.

A healthy on-call system requires:

```text
reasonable alert volume
clear escalation
runbooks
observability
incident tooling
postmortems
```

On-call shouldn't be:

> "Engineer manually watches dashboards all night."

Automation should detect problems.

---

## 83. Mean Time to Detect

MTTD:

> How quickly do we detect a problem?

Example:

```text
failure at 10:00
alert at 10:02
```

MTTD:

```text
2 minutes
```

---

## 84. Mean Time to Recover

MTTR is commonly used for:

> Mean Time to Recovery/Repair/Resolve

depending on organizational terminology.

Example:

```text
failure = 10:00
service restored = 10:15
```

MTTR:

```text
15 minutes
```

The important idea is:

```text
detect quickly
+
recover quickly
```

---

## 85. Reliability Improvement Loop

A mature organization operates like:

```text
Build
 ↓
Measure
 ↓
Observe
 ↓
Incident
 ↓
Learn
 ↓
Improve
 ↓
Automate
 ↓
Build again
```

This is continuous reliability engineering.

---

## 86. Observability vs Monitoring

You've already learned observability.

The distinction:

#### Monitoring

> "Is something wrong?"

#### Observability

> "Why is it wrong?"

Monitoring might tell you:

```text
5xx = 20%
```

Observability lets you investigate:

```text
which endpoint?
which pod?
which DB query?
which dependency?
which deployment?
which trace?
```

---

## 87. Three Pillars

Classic model:

```text
Logs
Metrics
Traces
```

But modern observability is broader.

You also care about:

```text
profiles
events
correlations
deployment metadata
```

For your roadmap:

```text
Logs + Metrics + Traces
```

are the core.

---

## 88. Correlation IDs

Suppose request:

```text
POST /orders
```

has:

```text
X-Request-ID: abc123
```

Then services log:

```text
API        → abc123
Order      → abc123
Payment    → abc123
Inventory  → abc123
```

Now you can trace a request across services.

This is extremely useful during incidents.

---

## 89. Distributed Tracing

Example:

```text
Request
│
├── API       20ms
│
├── Redis     5ms
│
├── DB        150ms
│
└── Payment   500ms
```

You immediately see:

```text
Payment service
```

is the major latency contributor.

Without tracing, you might waste time inspecting the API server.

---

## 90. Graceful Shutdown

Suppose Kubernetes sends:

```text
SIGTERM
```

to your Node.js application.

Bad application:

```text
SIGTERM
 ↓
immediately exits
 ↓
requests dropped
```

Better:

```text
SIGTERM
 ↓
stop accepting new requests
 ↓
finish existing requests
 ↓
close DB
 ↓
close Redis
 ↓
exit
```

Example:

```typescript
process.on("SIGTERM", async () => {
  server.close(async () => {
    await prisma.$disconnect();
    await redis.quit();
    process.exit(0);
  });
});
```

This is essential in Kubernetes/container environments.

---

## 91. Readiness vs Liveness

#### Liveness

> "Is this container alive?"

If no:

```text
restart it
```

#### Readiness

> "Can this instance receive traffic?"

If no:

```text
remove it from traffic
```

Example:

```text
database temporarily unavailable
```

The application may still be alive.

So:

```text
liveness = healthy process
readiness = capable of serving traffic
```

This distinction prevents unnecessary restarts.

---

## 92. Startup Probe

For applications that take a long time to start:

```text
startup probe
```

can prevent Kubernetes from treating the application as unhealthy before initialization finishes.

Think:

```text
startup
 ↓
startup probe
 ↓
ready
 ↓
readiness/liveness
```

---

## 93. Pod Disruption Budget

Suppose:

```text
5 backend pods
```

You require:

```text
minimum 4 available
```

A PDB can help constrain voluntary disruptions.

This protects availability during:

```text
node maintenance
cluster operations
voluntary evictions
```

It does not magically protect against every failure.

---

## 94. Graceful Degradation Example

Imagine your product page depends on:

```text
Recommendations
```

If recommendation service fails:

Bad:

```text
Product page → 500
```

Better:

```text
Product page
 ├── product information → works
 ├── price → works
 ├── inventory → works
 └── recommendations → unavailable
```

User can still purchase.

This is reliability engineering.

---

## 95. Rate Limiting

Suppose:

```text
API
```

is receiving:

```text
100,000 requests/sec
```

from one client.

Without protection:

```text
backend
 ↓
overloaded
```

Rate limiting:

```text
Client
 ↓
100 req/sec
 ↓
API
```

Excess:

```text
429 Too Many Requests
```

---

## 96. Rate Limiting Strategies

Common approaches:

```text
fixed window
sliding window
token bucket
leaky bucket
```

For interviews:

#### Token bucket

Imagine a bucket containing tokens.

Requests consume tokens.

Tokens refill at a fixed rate.

This allows:

```text
controlled bursts
+
long-term rate limit
```

---

## 97. Load Shedding

Sometimes traffic exceeds what the system can safely handle.

Instead of letting everything fail slowly:

```text
10,000 requests
 ↓
everything becomes slow
 ↓
entire system collapses
```

you can reject excess traffic:

```text
10,000 requests
 ↓
accept safe amount
 ↓
reject excess quickly
```

This is:

> **Load shedding**

Failing fast can preserve the core service.

---

## 98. Backpressure

Backpressure means:

> "Slow down producers because consumers can't keep up."

Example:

```text
Producer
→ 10k jobs/sec

Consumer
→ 2k jobs/sec
```

Use:

```text
queue
rate limiting
bounded concurrency
```

rather than allowing unlimited work to accumulate in memory.

---

## 99. Resource Limits

In Kubernetes:

```yaml
resources:
  requests:
    cpu: "250m"
    memory: "256Mi"

  limits:
    cpu: "1"
    memory: "512Mi"
```

Requests influence scheduling.

Limits constrain resource usage.

These help prevent one workload from consuming all node resources.

---

## 100. Noisy Neighbor Problem

Suppose:

```text
Node
├── Service A
├── Service B
└── Service C
```

Service A consumes:

```text
100% CPU
```

Service B and C suffer.

Resource requests/limits and appropriate isolation can reduce this problem.

---

## 101. Reliability Testing

A mature system doesn't only test:

```text
happy path
```

Test:

```text
database unavailable
Redis unavailable
network timeout
dependency slow
pod killed
node failure
queue backlog
disk full
invalid configuration
expired credentials
```

This is how you discover failure modes before users do.

---

## 102. Failure Injection

Example:

```text
API
 ↓
Redis
```

Inject:

```text
Redis latency = 2 seconds
```

Then verify:

```text
timeout
fallback
circuit breaker
```

rather than waiting for a real outage.

---

## 103. Reliability Review Before Production

Before launching a backend, ask:

#### Compute

```text
Can instances/pods scale?
What happens when one dies?
```

#### Database

```text
What if DB is slow?
What if DB is unavailable?
What if connections are exhausted?
```

#### Cache

```text
What if Redis disappears?
```

#### Queue

```text
What if consumers stop?
What if messages duplicate?
```

#### Deployment

```text
Can we rollback?
```

#### Networking

```text
What if DNS/LB fails?
```

#### Security

```text
What if credentials leak?
```

#### Observability

```text
How will we know something is broken?
```

---

## 104. Production Readiness Checklist

Before calling a backend production-ready:

```text
✅ Health endpoints
✅ Readiness/liveness
✅ Graceful shutdown
✅ Timeouts
✅ Retry policies
✅ Idempotency
✅ Rate limiting
✅ Circuit breakers where appropriate
✅ Structured logging
✅ Metrics
✅ Distributed tracing
✅ Dashboards
✅ Actionable alerts
✅ Runbooks
✅ Backups
✅ Restore testing
✅ Rollback strategy
✅ Capacity testing
✅ Security controls
✅ Secret management
✅ Failure testing
```

---

## 105. The SRE Architecture You Should Remember

```text
                         Production System
                                │
                ┌───────────────┼────────────────┐
                │               │                │
              Users          Metrics            Logs
                │               │                │
                ▼               ▼                ▼
             Service         Prometheus       Log system
                │
                ├───────────────┐
                │               │
              Traces         Alerts
                │               │
                └───────┬───────┘
                        ▼
                    Incident
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
           Detect     Mitigate   Recover
              │         │         │
              └─────────┼─────────┘
                        ▼
                    Postmortem
                        │
                        ▼
                    Improvements
                        │
                        ▼
                    Automation
```

That's the SRE loop.

---

## 106. SRE Interview Framework

If an interviewer asks:

> **"How would you make your backend reliable?"**

Don't start randomly listing AWS services.

Use this structure:

#### 1. Prevent

```text
testing
code review
safe deployment
capacity planning
```

#### 2. Detect

```text
metrics
logs
traces
alerts
SLOs
```

#### 3. Contain

```text
rate limiting
circuit breaker
bulkheads
load shedding
```

#### 4. Recover

```text
rollback
failover
backups
DR
```

#### 5. Learn

```text
postmortem
root cause
action items
automation
```

This is an excellent interview framework.

---

## 107. Scenario Question

#### "Your API suddenly returns 30% 500 errors. What do you do?"

Don't immediately say:

> "Restart the server."

Use:

```text
1. Confirm impact.
2. Check error rate/latency.
3. Check recent deployments.
4. Check logs.
5. Check traces.
6. Identify affected endpoint.
7. Check dependencies.
8. Check database.
9. Mitigate.
10. Roll back if deployment-related.
11. Verify recovery.
12. Investigate root cause.
13. Postmortem.
```

---

## 108. Scenario: Database Is Slow

You observe:

```text
p95 latency ↑
RDS latency ↑
```

Investigate:

```text
CPU
connections
IOPS
slow queries
locks
indexes
replication
connection pool
```

Potential immediate actions:

```text
reduce load
cache
queue
rollback
scale appropriately
kill problematic queries
```

Then permanent fix:

```text
query optimization
index
connection pool tuning
capacity
architecture change
```

---

## 109. Scenario: Redis Is Down

Don't automatically say:

> "Restart Redis."

Ask:

> Is Redis a cache or source of truth?

If cache:

```text
Redis down
 ↓
fallback to DB
```

If Redis contains critical state:

```text
different reliability requirements
```

This illustrates why architecture matters.

---

## 110. Scenario: Queue Is Growing

Observe:

```text
queue depth ↑
oldest message age ↑
```

Investigate:

```text
producer rate
consumer rate
worker failures
downstream latency
worker concurrency
```

Possible actions:

```text
scale consumers
reduce producer rate
fix failing consumers
increase downstream capacity
DLQ poison messages
```

---

## 111. Scenario: Deployment Broke Production

Immediate:

```text
stop rollout
```

Then:

```text
rollback
```

if safe.

Check:

```text
error rate
logs
traces
DB compatibility
config
secrets
dependencies
```

Then:

```text
root cause
fix
test
redeploy
```

---

## 112. Scenario: Traffic Suddenly 10×s

Possible protections:

```text
autoscaling
CDN
caching
rate limiting
queue
load shedding
database protection
```

Don't blindly scale everything.

Find the bottleneck.

---

## 113. The Most Important SRE Principle

When a system is under stress:

> **Protect the system before trying to make every request succeed.**

Example:

```text
100,000 requests
```

If the system can safely process:

```text
20,000
```

it's sometimes better to:

```text
accept 20,000
reject 80,000 quickly
```

than:

```text
attempt all 100,000
 ↓
everything slows
 ↓
system collapses
```

This is graceful overload handling.

---

## 114. Reliability Is a System Property

You can't make a system reliable simply by:

```text
adding Kubernetes
```

or:

```text
adding AWS
```

or:

```text
adding replicas
```

Reliability comes from the interaction of:

```text
architecture
+
code
+
database
+
network
+
deployment
+
observability
+
security
+
operations
```

---

## 115. Your Complete SRE Mental Model

Remember this:

```text
              RELIABILITY
                   │
       ┌───────────┼────────────┐
       ↓           ↓            ↓
    Prevent      Detect       Recover
       │           │            │
    Testing     Metrics       Rollback
    Capacity    Logs          Failover
    Security    Traces        Backups
    Safe CI/CD  Alerts        DR
       │           │            │
       └───────────┼────────────┘
                   ↓
                Improve
                   │
              Postmortems
                   │
               Automation
```

---

## 116. What You Need to Know for Interviews

#### 🔥 Deep

```text
SLI / SLO / SLA
Error budgets
Burn rate
Availability
Latency percentiles
Capacity planning
Load testing
Retries/backoff/jitter
Timeouts
Idempotency
Circuit breakers
Bulkheads
Rate limiting
Backpressure
Graceful degradation
Incident response
Rollback
RTO/RPO
DR strategies
Database reliability
Queue reliability
Observability
```

#### 🟡 Medium

```text
Chaos engineering
Game days
Active-active
Pilot light
Warm standby
Load shedding
PDB
failure injection
runbooks
on-call
```

#### ⚪ Awareness

```text
specialized SRE platforms
large-scale multi-region internals
advanced chaos frameworks
organization-specific incident tooling
```

---

## 117. Final SRE Interview Questions

You should now be able to answer:

#### What is SLO?

> Engineering reliability target.

#### What is SLI?

> Measurement used to determine service performance/reliability.

#### What is SLA?

> External/business commitment.

#### What is an error budget?

> The amount of unreliability allowed by the SLO.

#### What is burn rate?

> The rate at which the error budget is being consumed.

#### RTO?

> Maximum acceptable recovery time.

#### RPO?

> Maximum acceptable data-loss window.

#### Why p99 instead of average?

> Average can hide severe tail latency.

#### Why use exponential backoff?

> To avoid immediately retrying a failing dependency and worsening overload.

#### Why jitter?

> To prevent many clients from retrying simultaneously.

#### Why idempotency?

> To make retries safe for operations that shouldn't happen multiple times.

#### Circuit breaker?

> Prevents repeatedly calling a failing dependency and allows it to recover.

#### Bulkhead?

> Isolates resources so failure in one workload doesn't consume everything.

#### Graceful degradation?

> Preserve core functionality while allowing non-critical functionality to fail.

#### Why load testing?

> To understand capacity, bottlenecks, latency, and failure behavior before production traffic exposes them.

#### Why chaos testing?

> To validate that the system actually handles failures as designed.

---

## 🎯 Chapter 34 Complete

We covered:

- ✅ SRE fundamentals at production depth
- ✅ Availability
- ✅ Reliability
- ✅ SLI
- ✅ SLO
- ✅ SLA
- ✅ Error budgets
- ✅ Burn rate
- ✅ Latency budgets
- ✅ p50/p95/p99
- ✅ Tail latency
- ✅ Capacity planning
- ✅ Little's Law
- ✅ Load testing
- ✅ Stress testing
- ✅ Spike testing
- ✅ Soak testing
- ✅ Queue depth/age
- ✅ Database reliability
- ✅ Connection pool exhaustion
- ✅ Retry storms
- ✅ Timeouts
- ✅ Backoff
- ✅ Jitter
- ✅ Idempotency
- ✅ Circuit breakers
- ✅ Bulkheads
- ✅ Graceful degradation
- ✅ Fail-open/fail-closed
- ✅ Backpressure
- ✅ Rate limiting
- ✅ Load shedding
- ✅ RTO/RPO
- ✅ Backup/restore
- ✅ Pilot light
- ✅ Warm standby
- ✅ Active-active
- ✅ Multi-AZ vs Multi-Region
- ✅ Chaos engineering
- ✅ Failure injection
- ✅ Game days
- ✅ Incident response
- ✅ Mitigation vs root cause
- ✅ Rollback vs roll-forward
- ✅ Expand-and-contract migrations
- ✅ Postmortems
- ✅ Alerting
- ✅ Alert fatigue
- ✅ Runbooks
- ✅ On-call
- ✅ MTTD/MTTR
- ✅ Observability
- ✅ Correlation IDs
- ✅ Distributed tracing
- ✅ Graceful shutdown
- ✅ Readiness/liveness/startup probes
- ✅ PDB
- ✅ Production readiness
- ✅ SRE interview scenarios
<!-- SOURCE-END -->

---

## Editorial supplement

> **Added by the knowledge-base editor — not part of the original source.** It fills gaps the source leaves open (for example concepts named in the interview list but never explained, or configuration the chapter only describes in words). Treat the text above as the original material and this section as clearly separated additions.

### Formulas, queries and code for the SRE concepts in this chapter

The chapter gives worked numbers but few general formulas. These are the standard ones, plus runnable examples for tools it names.

**1. Availability and downtime.**

```text
Availability = Uptime / (Uptime + Downtime)            = successful requests / total requests (request-based SLI)
Allowed downtime = (1 − availability target) × period
```

The chapter's downtime table uses an *average month of about 730 hours* (43,800 minutes): 99% → 7 h 18 m, 99.9% → 43 m 49 s, 99.99% → 4 m 23 s, 99.999% → 26 s. For a *30-day* month (43,200 minutes) the 99.9% figure is 43.2 minutes — both are correct; know which period you are using.

**2. Error budget and burn rate.**

```text
Error budget          = 1 − SLO                         (e.g. 0.001 for a 99.9% SLO)
Budget in time        = (1 − SLO) × window
Budget in requests    = (1 − SLO) × total requests      (1,000,000 requests × 0.001 = 1,000 failures)
Burn rate             = observed error rate / allowed error rate (1 − SLO)
```

A burn rate of 1 uses the budget exactly over the SLO window; the chapter's example (1% errors against a 0.1% allowance) is a burn rate of **10**, which would exhaust a 30-day budget in about 3 days. A widely used practice (from Google's SRE Workbook) is *multi-window, multi-burn-rate alerting*, e.g. page when the burn rate is high over a short window and confirmed over a longer one (the workbook's example thresholds: 14.4× over 1 h, 6× over 6 h; ticket at 1× over 3 days). Treat those numbers as a starting point, not a rule.

**3. Composite availability** (why dependencies matter):

```text
Serial dependencies (all must work):  A_total = A1 × A2 × A3
   e.g. three 99.9% services in a chain → 0.999³ ≈ 99.7%
Redundant components (any one works): A_total = 1 − (1 − A)^n
   e.g. two independent 99% instances → 1 − 0.01² = 99.99%
```

Redundancy only helps if failures are independent (two replicas in one AZ, or sharing one database, are not).

**4. MTBF / MTTR and availability.** `Availability ≈ MTBF / (MTBF + MTTR)` where MTBF = mean time between failures and MTTR = mean time to recover. Improving *either* raises availability — which is why the chapter stresses detecting fast (MTTD) and recovering fast (MTTR), not only preventing failures.

**5. Little's Law applied to capacity.** `L = λW`. Use it to size concurrency: 500 requests/s at 200 ms average latency means about `500 × 0.2 = 100` requests in flight, so a Node.js service needs room for ~100 concurrent requests, and a database pool (or Lambda concurrency) must be sized accordingly. If latency doubles under load, in-flight requests double.

**6. Error ratio in PromQL** (SLI for the availability SLO; assumes the `http_requests_total` counter from Chapter 22 has a `status` label):

```promql
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```
Burn rate = that ratio divided by `(1 − SLO)`, e.g. `… / 0.001` for a 99.9% SLO.

**7. A k6 load test** (the chapter recommends k6 but shows no script). It ramps to 100 virtual users, holds, ramps down, and fails the run if the error rate or p95 latency breaches the SLO:

```javascript
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "1m", target: 100 },   // ramp up
    { duration: "3m", target: 100 },   // hold
    { duration: "1m", target: 0 },     // ramp down
  ],
  thresholds: {
    http_req_failed: ["rate<0.01"],      // < 1% errors
    http_req_duration: ["p(95)<300"],    // p95 < 300 ms
  },
};

export default function () {
  const res = http.get("https://api.example.com/health");
  check(res, { "status is 200": (r) => r.status === 200 });
  sleep(1);
}
```
Run with `k6 run script.js`. Changing the `stages` gives the other test types in section 31: a larger target (stress), a sudden jump (spike), or a long duration (soak).

**8. A token-bucket rate limiter** (section 96), minimal in-memory form:

```typescript
class TokenBucket {
  private tokens: number;
  private last = Date.now();
  constructor(private capacity: number, private refillPerSec: number) {
    this.tokens = capacity;
  }
  allow(): boolean {
    const now = Date.now();
    this.tokens = Math.min(this.capacity, this.tokens + ((now - this.last) / 1000) * this.refillPerSec);
    this.last = now;
    if (this.tokens >= 1) { this.tokens -= 1; return true; }
    return false;                 // caller responds 429 Too Many Requests
  }
}
// new TokenBucket(20, 10): bursts of up to 20, sustained 10 requests/s
```
With several API instances the limiter state must be shared (for example a Redis-based limiter), otherwise each instance enforces its own limit.

**9. The four golden signals.** Google's SRE book names latency, traffic, errors and saturation as the signals to monitor for any service — RED (Chapter 22) plus saturation (how "full" the most constrained resource is, such as DB connections or queue depth). The USE method (utilisation, saturation, errors) is the resource-oriented counterpart.

---

**Navigation:** ← [Chapter 33: Advanced AWS for Backend Engineers](../04-aws/ch33-advanced-aws-backend.md) · [Chapter 35: DevOps Capstone: Build a Production-Grade Backend Platform](../08-production/ch35-devops-capstone.md) → · [Revision sheet](../../revision/ch34-revision.md)
