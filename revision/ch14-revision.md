# Chapter 14 — Revision Sheet: Load Balancing + Scaling

> Supplements [the full chapter](../docs/04-aws/ch14-load-balancing-scaling.md). Core question: **what happens when one EC2 server isn't enough?**

## The pieces

| Piece | Answers |
|---|---|
| **Load balancer / ELB / ALB** | *Where should this request go?* ALB = Application Load Balancer (HTTP/HTTPS, application-layer) |
| **Target group** | Defines the backend destinations (EC2 instances, IP addresses, containers) |
| **Health check** | Should this target receive traffic? (e.g. `GET /health` → `200 OK`; failing targets are removed from rotation) |
| **Listener** | Waits for traffic on a port/protocol (`:80`, `:443`); forwards to a target group. Production = HTTPS `:443` |
| **ASG (Auto Scaling Group)** | *How many EC2 instances should exist?* — scale out / scale in, replace failed instances |
| **Launch template** | What ASG launches: AMI, instance type, security group, IAM role, user data, other config |

```text
ALB  → distributes traffic          Target Group → backend targets
Health check → who receives traffic  ASG → how many instances exist
```

- Client only needs the ALB endpoint/domain, not individual EC2s.
- **ALB routing rules:** path-based (`/users/*` → Users TG, `/orders/*` → Orders TG) and host-based (`api.example.com` → API targets, `admin.example.com` → Admin targets) — why it's *Application* LB.
- **Algorithms:** round robin; least outstanding requests (fewer active requests). Principle: the LB decides which *healthy* target gets each request.
- **Health check vs monitoring:** health check = "can I reach this backend and get an acceptable response?"; observability = CPU, memory, latency, errors, DB failures, request rate (Ch.17/22).
- **Security groups:** `Internet → ALB-SG (443 from Internet) → API-SG (3000 from ALB-SG) → EC2`.
- **LB availability:** ELB is managed, highly available across AZs; you don't run a single LB server.
- **LB vs reverse proxy:** overlapping concepts; ALB does load balancing + application-level routing.

## Scaling concepts

- **Vertical (scale up)** vs **Horizontal (scale out)**. For web apps, horizontal scaling matters most; it needs **stateless** app servers.
- **ASG capacity:** Minimum / Desired / Maximum (e.g. 2 / 3 / 10) — normal 3, never intentionally below 2, can scale to 10. **Auto Scaling ≠ infinite scaling**: stops at max; then larger instances, higher max, better code, caching, DB scaling, architectural change.
- **Scale out** when CPU/requests/latency rise; **scale in** when traffic drops (cost saving).
- **Policies:** **Target tracking** (e.g. keep CPU ≈ 50%) · **Step scaling** (CPU>70% add 1, >85% add 2, >95% add 4) · **Scheduled scaling** (predictable load, e.g. scale before 8 AM / after 8 PM). Scaling should respond to workload, not arbitrary server count.
- **Self-healing:** failed instance replaced by ASG (replace instead of repairing). Immutable infrastructure: broken instance → terminate → fresh instance from known image.

**Full failure flow:** EC2 unhealthy → ALB health check fails → ALB stops routing there → ASG detects unhealthy instance → replaces it → new instance starts → app starts → ALB health check passes → traffic resumes.

## Stateless architecture

- **Bad:** session in EC2-A's RAM; request 2 hits EC2-B → "Who is this user?" ❌.
- **Good:** shared state in Redis / database / object storage / dedicated state services; application code identical on all instances.
- **JWT:** any instance can validate the token without local session — but adds expiry, revocation, refresh tokens, key management, token size, compromised-token concerns ("JWT ≠ automatically perfect scaling").
- **Sticky sessions:** requests from a user tend to go to the same instance — helps legacy stateful apps but can cause uneven load. Stateless is generally preferable.
- *Why is your app stateless? Any request can reach any healthy instance without relying on local state; shared state lives in a DB/Redis, making horizontal scaling and instance replacement easier.*

## Bottlenecks, cost, and code

- **Scaling one layer doesn't scale the system**: ASG 2 → 20 EC2 multiplies DB connections/queries/CPU/IO → RDS becomes the bottleneck (see Ch.13).
- Identify the **actual bottleneck** (CPU, memory, network, database, disk, connections, external APIs, locks, application code): identify → measure → understand workload → choose strategy → test → monitor.
- **Scaling doesn't fix bad code** (O(n²) unnecessarily + 10 EC2 only hides it): optimise first.
- Cost trade-off: more instances = performance↑ cost↑; too few = latency↑ reliability↓. Balance performance, availability, reliability, cost, complexity.

## Multi-AZ application architecture

Internet → ALB → AZ-A/AZ-B private subnets → EC2 → RDS. Losing one AZ doesn't necessarily lose the app. Full flow: Route 53/DNS → ALB → EC2 (ASG) → connection pool → RDS; Redis for caching.

## Deployments (interaction)

Rolling (v1 v1 v1 → v2 v1 v1 → … → v2 v2 v2); Blue-Green (switch traffic Blue → Green); Canary (99/1 → 90/10 → 70/30 → 50/50 → 0/100). See [Chapter 6](../docs/03-cicd-gitops/ch06-cicd-github-actions.md).

## Scenarios

1. **10× traffic:** check metrics → identify bottleneck → ensure ALB distributes → scale EC2 horizontally if compute-bound → verify DB isn't the bottleneck → check connection pool → cache → verify external dependencies → monitor latency/errors → scale back later. (Not just "add more EC2".)
2. **One EC2 unhealthy:** see failure flow above.
3. **Practical exercise:** ALB → EC2-A/EC2-B → RDS; if traffic ×5 "what scales?" ALB → ASG → more EC2; next bottleneck: RDS, Redis, external API, network, connection pool.

## Depth guide

Master: LB concept, ALB, target groups, listeners, health checks, SGs, horizontal vs vertical, ASG, launch templates, min/desired/max, scaling policies, multi-AZ, stateless design, sessions, DB bottleneck, pooling, failure replacement, rolling/blue-green/canary. Medium: target tracking, step, scheduled, sticky sessions, routing rules, deployment interaction. Awareness: Network Load Balancer, Gateway Load Balancer, advanced ELB.

## Added notes (not in source)

- **ELB types:** ALB (Layer 7 HTTP/HTTPS), NLB (Layer 4 TCP/UDP, very high throughput, static IPs), GWLB (inline virtual appliances).
- **ASG health check type:** by default an ASG uses **EC2 status checks**; to have it replace instances that the **ALB** marks unhealthy, enable **ELB health checks** on the ASG (the source's "ASG can also use health information" glosses over this).
- Health check settings to know: path, interval, timeout, healthy/unhealthy threshold counts, success codes.
- **Deregistration delay / connection draining** lets in-flight requests finish before a target is removed during scale-in or deployments.
- ASG **cooldown / instance warm-up** prevents flapping while new instances boot.
- ALB terminates TLS (certificate from **AWS Certificate Manager**), can redirect `:80` → `:443`, adds `X-Forwarded-For` so the app can see the client IP.
- Target types for target groups: `instance`, `ip`, `lambda`.

## Interview questions — checklist

Why a load balancer; ALB vs reverse proxy; target group; health check design (`/health`); listener rules; SG chain; vertical vs horizontal; ASG min/desired/max; launch template; scaling policy types; stateless design vs sticky sessions; JWT trade-offs; what fails when scaling EC2 2 → 20 (DB); ALB vs ASG roles; failure-replacement lifecycle; rolling/blue-green/canary; how to respond to 10× traffic.

<!-- NAV -->

---

← [Sheet 13](ch13-revision.md) · [Full chapter 14](../docs/04-aws/ch14-load-balancing-scaling.md) · [All revision material](README.md) · [Sheet 15](ch15-revision.md) →
