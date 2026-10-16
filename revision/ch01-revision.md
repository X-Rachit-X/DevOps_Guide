# Chapter 1 — Revision Sheet: Cloud + DevOps Fundamentals

> Supplements [the full chapter](../docs/01-foundations/ch01-cloud-devops-fundamentals.md). Read the chapter first; use this sheet to revise.

## The one-paragraph mental model

Cloud = renting compute, storage, networking and managed services over a network instead of owning hardware. DevOps = the practices (CI/CD, IaC, containers, monitoring) that let one team build, test, ship and operate software continuously. Cloud supplies the *infrastructure*; DevOps supplies the *process and automation*. Underneath both: **Linux + networking + security**.

## Terms that are easy to confuse

| Pair | Difference |
|---|---|
| Scalability vs Elasticity | Scalability = *can* it handle growth by adding resources. Elasticity = it *automatically* grows **and shrinks** with demand. |
| Vertical vs Horizontal scaling | Vertical (scale **up**) = bigger machine. Horizontal (scale **out**) = more machines behind a load balancer. |
| Availability vs Reliability | Availability = reachable when needed. Reliability = behaves *correctly* consistently. An API that answers fast with wrong data is available but not reliable. |
| High availability vs Fault tolerance | HA = redundancy so the service stays up. Fault tolerance = the system keeps *operating correctly* through component failure (user sees nothing). |
| RTO vs RPO | RTO = how fast must service be restored (time). RPO = how much data loss is tolerable (time-window of data). |
| IaaS / PaaS / SaaS | IaaS = "give me a computer" (EC2). PaaS = "give me a platform to run my app". SaaS = "I just use the software" (Gmail). Control decreases left → right. |
| Public / Private / Hybrid | Shared provider infra / dedicated to one org / both connected (e.g. VPN). |
| Region vs AZ | Region = geographic area. AZ = isolated infrastructure location *inside* a region. Spread across AZs for HA, across regions for DR. |
| Continuous Delivery vs Deployment | Delivery = always *ready* to release, a human approves. Deployment = auto-released to production if pipeline passes. |
| Container vs VM | VM = own guest OS on a hypervisor. Container = shares the host kernel → lighter. |
| SLI / SLO / SLA | SLI = measurement (successful / total requests). SLO = target (99.9%). SLA = external commitment. |

## Key flows to be able to draw

1. Developer → GitHub → CI (lint, build, test) → Docker image → CD → AWS/Kubernetes → Logs + Metrics → Monitoring → Improvement → back to Git.
2. Internet → Route 53 → CloudFront → ALB → EC2 (Docker) in two AZs → Redis / RDS / S3.
3. Terraform code → review → version control → `terraform` → AWS infrastructure.

## Interview questions (from the chapter's self-test, with short answers)

1. *What problem does cloud solve?* Owning/maintaining/over-provisioning hardware; cloud lets you rent resources on demand.
2. *Scalability vs elasticity?* See table.
3. *Horizontal vs vertical?* See table.
4. *HA vs fault tolerance?* See table.
5. *RTO vs RPO?* See table.
6. *IaaS vs PaaS vs SaaS?* See table.
7. *Region vs AZ?* See table.
8. *Cloud vs DevOps?* Cloud = infrastructure and services; DevOps = how teams build/test/deploy/operate together.
9. *CI vs CD?* CI = frequent integration with automated checks; CD = delivery/deployment automation.
10. *Delivery vs Deployment?* Manual approval gate vs fully automatic.
11. *Why containers?* Same packaged environment everywhere ("works on my machine" fix).
12. *Containers vs VMs?* Shared kernel vs separate guest OS.
13. *What is IaC?* Describing infrastructure in versioned, reviewable code (Terraform).
14. *What is serverless?* Servers exist, you don't manage them (AWS Lambda).
15. *What does DevOps improve?* The friction and delay between writing code and running it reliably in production.

<!-- NAV -->

---

[Full chapter 1](../docs/01-foundations/ch01-cloud-devops-fundamentals.md) · [All revision material](README.md) · [Sheet 2](ch02-revision.md) →
