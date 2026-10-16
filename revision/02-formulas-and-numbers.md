# Formulas, Numbers and Worked Examples

Everything quantitative in the course in one place. *(added)* marks formulas the source only implies; they are standard and explained in the cited supplement or revision sheet.

## Networking

| Item | Formula / value | Example |
|---|---|---|
| IPv4 / IPv6 size | 32 bits / 128 bits; 2³² ≈ 4.29 billion addresses | |
| CIDR `a.b.c.d/p` | network bits = p, host bits = 32 − p | `/16` → 16 host bits |
| Addresses in block | **2^(32 − p)** | `/16` = 65,536; `/24` = 256; `/32` = 1 |
| Traditional usable hosts | 2^(32 − p) − 2 | `/24` → 254 |
| AWS usable hosts per subnet *(added)* | 2^(32 − p) − **5** | `/24` → 251 |
| Smaller prefix = larger network | | `/16` > `/24` |
| Private ranges | 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 | |
| Default route | 0.0.0.0/0 | → IGW (public) or NAT (private) |
| Handshake | SYN → SYN-ACK → ACK | |
| Return-path rule | Stateful SG auto-allows replies; stateless NACL needs explicit return rules | |

## Linux permissions (Ch 2)

r = 4, w = 2, x = 1 → `7 = rwx`, `5 = r-x`, `4 = r--`, `6 = rw-`. `755` = owner rwx, group r-x, others r-x. `644` = rw-/r--/r--. `600` = rw-------.

## Cron (Ch 3)

`minute(0-59) hour(0-23) day-of-month(1-31) month(1-12) day-of-week(0-7)` — `0 2 * * *` daily 02:00 · `0 * * * *` hourly · `0 0 * * *` midnight · `0 3 * * 0` Sunday 03:00.

## Scaling and capacity

| Concept | Formula | Source example |
|---|---|---|
| DB connections | **instances × pool size** | 10 × 100 = 1,000; 20 × 50 = 1,000; 20 Pods × 20 = 400 vs max 200 (Ch 13, 35) |
| Sequential vs parallel pipeline time | sum vs max | 5 + 2 + 4 = 11 min vs max = 5 min (Ch 27) |
| Little's Law | **L = λW** | 100 req/s × 0.2 s = 20 in flight (Ch 34) |
| Retry amplification | requests × (1 + retries) | 1,000 × 3 retries → 3,000 extra (Ch 22, 30, 34) |
| HPA desired replicas *(added)* | `ceil(current × currentMetric / targetMetric)` | 3 Pods at 90% CPU, target 60% → 5 (Ch 20 revision) |
| Max Pods per node, VPC CNI *(added)* | **ENIs × (IPv4 per ENI − 1) + 2** | m5.large: 3 × 9 + 2 = 29 (Ch 31 supplement) |
| Queue growth | producer rate − consumer rate | 1,000 − 500 = +500 jobs/s (Ch 34) |
| Image size benefit | build env ≈ 800 MB vs runtime ≈ 200 MB | multi-stage (Ch 8) |
| Timeout budget | Σ component latencies ≤ target | 50 + 20 + 100 + 80 + 30 = 280 ms of 300 ms (Ch 34) |

## Availability, SLOs and error budgets (Ch 1, 22, 34)

```text
Availability = Uptime / Total time  =  successful requests / total requests
Allowed downtime = (1 − target) × period
Error budget = 1 − SLO            (budget in requests = (1 − SLO) × total requests)
Burn rate = observed error rate / (1 − SLO)          (added formula)
```

| Availability | Downtime / month (avg 730 h) | Downtime / 30 days (43,200 min) |
|---|---:|---:|
| 99% | 7 h 18 m | 7.2 h |
| 99.9% | 43 m 49 s | 43.2 min |
| 99.99% | 4 m 23 s | 4.32 min |
| 99.999% | 26 s | 26 s |

Worked: SLO 99.9%, 1,000,000 requests → budget 1,000 failures. Observing 1% errors against a 0.1% allowance = burn rate **10**.
*(added)* Composite availability: serial `A₁ × A₂ × …` (0.999³ ≈ 99.7%); redundant `1 − (1 − A)ⁿ` (two 99% → 99.99%, if independent); `Availability ≈ MTBF / (MTBF + MTTR)`.
Latency example: 99 requests × 50 ms + 1 × 10 s → average 149.5 ms but p99 = 10 s.

## Reliability mechanics

- **Exponential backoff:** 100 → 200 → 400 → 800 ms (+ jitter). *(added)* `delay = min(cap, base × 2^attempt) + random`.
- **Circuit breaker states:** CLOSED → OPEN → HALF-OPEN → CLOSED/OPEN.
- **Token bucket:** tokens refill at a fixed rate, requests consume tokens (bursts + sustained rate).
- **RTO / RPO:** restore time / data-loss window (examples: RTO 1 h, RPO 5 min).
- **MTTD / MTTR:** failure 10:00, alert 10:02 → MTTD 2 min; restored 10:15 → MTTR 15 min.

## Kubernetes sizing units (Ch 19)

`250m` = 0.25 CPU core; `Mi` = mebibytes; requests drive scheduling and HPA percentages; exceeding CPU limit → throttled; exceeding memory limit → **OOMKilled** *(added)*.

## Cost-relevant facts *(verified/flagged)*

- Public IPv4 addresses are charged **$0.005 per IP-hour** since 1 Feb 2024 (verified against AWS blog).
- NAT Gateway: hourly + per-GB; S3/DynamoDB **gateway endpoints are free** *(added; verify)*.
- EKS control plane has a fixed hourly fee on top of EC2/EBS/LB/NAT/data transfer *(verify current price)*.

---
[← Revision index](README.md)
