# Chapter 24 — Revision Sheet: Complete Cloud + DevOps Interview & OA Mastery

> Supplements [the full chapter](../docs/09-interview/ch24-interview-oa-mastery.md). This chapter is itself a consolidation; use this sheet as the 10-minute pre-interview skim. The global cross-chapter sheets are in [revision/](./).

## DevOps — your practical definition

*The practices and tooling used to reliably build, test, package, deploy, operate, monitor, and troubleshoot software and infrastructure* (not just "knowing Docker and Kubernetes"). Code → version control → CI → testing → build → containerisation → infrastructure → deployment → monitoring → reliability → troubleshooting.

## High-value "X ≠ Y" distinctions (OA / MCQ traps)

| | |
|---|---|
| Image ≠ Container | Docker |
| Pod ≠ Container | Kubernetes |
| Multi-AZ ≠ Read Replica | RDS (availability/failover vs read scaling) |
| Private subnet ≠ no Internet access | outbound possible through NAT |
| Authentication ≠ Authorization | who vs what |
| S3 ≠ EBS | object vs block |
| Horizontal ≠ Vertical | scale out vs up |
| Continuous Delivery ≠ Continuous Deployment | approval gate vs automatic |
| Logs ≠ Metrics ≠ Traces | what happened / how much / where time went |
| State ≠ configuration | Terraform |
| Running ≠ Ready | Kubernetes readiness |
| HPA ≠ node autoscaling | Pods vs nodes |
| TCP is not simply "faster" than UDP | oversimplification; TCP = reliable/ordered/connection-oriented; UDP = connectionless, lower overhead |

## Checklists by domain (what to be able to do)

- **Linux:** `pwd ls cd mkdir touch cp mv rm cat less`; `chmod chown` (r/w/x, 755, 644); `ps top kill` (PID, SIGTERM, SIGKILL, SIGINT); `df du free`; `ip ss ping curl`; `journalctl tail grep`; `ssh`; `systemctl`. *Slow server:* CPU → memory → disk → processes → network → app logs → dependencies (`top`, `free -h`, `df -h`, `ps aux`, `ss -tulpn`, `tail -f app.log`); don't blindly restart.
- **Bash:** `set -euo pipefail`; health script `if curl -fsS http://localhost:3000/health; then … else exit 1; fi`; variables, args (`$1 $@ $?`), conditions, loops, functions, exit codes, pipes, redirection, cron. `-e` stop on many failures, `-u` unset variables, `-o pipefail` pipeline fails if an earlier command fails.
- **Networking:** IP, subnet, CIDR, port, socket, TCP/UDP, DNS, HTTP/HTTPS, TLS, NAT, routing, firewall, proxy, load balancer. DNS flow: browser → resolver → DNS hierarchy → IP → TCP/TLS → HTTP. Record types A, AAAA, CNAME, MX, TXT, NS. Methods GET/POST/PUT/PATCH/DELETE; status 200, 201, 204, 400, 401, 403, 404, **409**, 429, 500, 502, 503, 504. *Connectivity debug:* DNS → IP → route → firewall/SG → port → process listening → application (`dig`, `curl -v`, `ss -lntp`, `ip route`, `ping`).
- **Git:** working dir → staging → commit → branch → remote; `status add commit log diff fetch pull push branch switch merge rebase stash cherry-pick reset revert reflog`. Reset moves history refs (may rewrite local history); revert adds a reversing commit (safer on shared history). Rebase changes the base of commits — useful for cleaning local feature history; careful with shared commits.
- **CI/CD:** CI/Delivery/Deployment; pipeline: push → CI → deps → lint → typecheck → tests → build → Docker → registry → deployment. GitHub Actions vocabulary: workflow, event, job, runner, step, action, artifact, secret, environment.
- **Docker:** Dockerfile → image → container; know `FROM WORKDIR COPY RUN ENV EXPOSE CMD ENTRYPOINT USER`; `RUN` = build time, `CMD` = default start command. Production: multi-stage, small runtime image, non-root, `.dockerignore`, production deps, layer caching, immutable tags. Debug: `docker ps`, `logs`, `inspect`, `exec -it … sh`; check running? port mapping? listening on `0.0.0.0`? env vars? image? logs? network?
- **AWS core services:** IAM, EC2, S3, VPC, RDS, ALB, Auto Scaling, Lambda, SQS, SNS, Route 53, CloudFront, WAF, CloudWatch, CloudTrail, ECR, EKS, Secrets Manager, KMS. IAM: user/group/role/policy/permission/ARN/least privilege/temporary credentials; GitHub Actions → OIDC → IAM Role → temp credentials beats long-lived keys. EC2: AMI, instance, type, EBS, SG, public/private IP, IAM role, user data, IMDS. S3: bucket, object, key, storage class, versioning, lifecycle, encryption, presigned URL, multipart. VPC: subnet, route table, IGW, NAT GW, SG, NACL, VPC endpoint. RDS: Multi-AZ, read replica, backup, snapshot, PITR, pool, encryption, monitoring. Scaling: vertical/horizontal/LB/ASG/stateless — **scaling app servers doesn't scale the database**. Lambda/SQS/SNS: visibility timeout, retry, DLQ, idempotency, cold start, concurrency — **never assume exactly-once**.
- **Kubernetes:** Cluster = Control Plane + Worker Nodes → Pods; Deployment → ReplicaSet → Pods; Service → Pods. Objects: Pod, Deployment, ReplicaSet, Service, Namespace, ConfigMap, Secret, PV, PVC, StorageClass, Ingress, HPA, Job, CronJob, DaemonSet, StatefulSet. Networking: Pod → Service → Ingress → LB; DNS, ClusterIP, NodePort, LoadBalancer, NetworkPolicy. Troubleshooting order: `get pods` → `describe pod` → `logs` → `logs --previous` → `exec -it … sh`; services: `get svc`, `get endpointslices`; deployments: `rollout status|history|undo`.
- **Terraform:** `init fmt validate plan apply destroy`; provider, resource, variable, output, data source, module, state, remote state, locking, drift, import.
- **Observability/Reliability/SRE:** logs/metrics/traces; Prometheus, Grafana, OpenTelemetry, CloudWatch; RED (e.g. 1000 req/s, 2%, p95 300 ms); SLI/SLO/SLA/error budget; timeout, retry, exponential backoff, jitter, circuit breaker, bulkhead, rate limiting, idempotency, graceful shutdown.

## Kubernetes failure table

| Symptom | Investigate first |
|---|---|
| `Pending` | Scheduling / resources / PVC |
| `CrashLoopBackOff` | Application logs / config |
| `ImagePullBackOff` | Image / tag / registry / auth |
| Running but not Ready | Readiness probe |
| Service has no traffic | Selector / endpoints |
| HPA not scaling | Metrics / resources / config |
| Pod `OOMKilled` | Memory usage / limits |
| 503 | LB / Service / readiness / backend |
| 502 | Proxy/LB → backend communication |
| DNS failure | DNS / service configuration |

(Learn the reasoning; don't memorise mechanically.)

## Golden rule of retries

Transient failure? safe to retry? how many retries? backoff? jitter? what if the dependency stays down? For payment-like operations → **idempotency**.

## Interview scenarios (answer skeletons)

1. **500 errors:** confirm impact → metrics → recent deployment → app logs → traces → dependencies → mitigate → verify recovery → root cause.
2. **Pods Running, users get 503:** Running ≠ Ready → readiness, Service, endpoints, Ingress/LB, application.
3. **Healthy Pods but 5 s responses:** don't add Pods → metrics → traces → database → Redis → external APIs (e.g. RDS query 4.5 s; scaling Pods won't fix it).
4. **DB connections 100%:** Pods increased? pool too large? connection leak? traffic spike? slow queries?
5. **New deployment → 5xx:** check rollout → logs → compare v1/v2 → rollback if appropriate → investigate.
6. **EC2 can't reach Internet:** subnet → route table → IGW/NAT → SG → NACL → DNS.
7. **Private EC2 can't download updates:** route to NAT GW? NAT route correct? NAT in a public subnet? IGW?
8. **Pod can't pull image:** image name → tag → registry → credentials → network.

## Depth required

- 🔥 **Master:** Linux, networking, Git, Docker, CI/CD, AWS fundamentals, VPC, IAM, EC2, S3, RDS, load balancing, Kubernetes fundamentals, Terraform, monitoring, troubleshooting — explain, configure, write, deploy, debug.
- 🟡 **Strong working knowledge:** EKS, Lambda, SQS/SNS, CloudFront, WAF, Prometheus, Grafana, OpenTelemetry, HPA, advanced Terraform modules.
- 🟢 **Awareness** (what / why / when): ArgoCD, GitOps, Jenkins, Ansible, Service Mesh, Istio, Operators, CRDs, advanced Kubernetes administration, advanced networking internals, advanced SRE. *(These awareness topics are expanded in Part II, chapters 25–35.)*
- Positioning: "Backend/SWE engineer with strong Cloud + DevOps capabilities" — don't claim "expert DevOps engineer".

## The final 10 questions

1. `git push` → … → Kubernetes: Git → GitHub → Actions → tests → Docker → ECR → Kubernetes → rolling deployment.
2. Why not Pod IPs? Ephemeral → Service.
3. Why readiness probes? Running ≠ Ready.
4. Why doesn't adding API Pods solve DB scaling? DB becomes the bottleneck.
5. Why Terraform? Declarative, reproducible infrastructure as code.
6. Why Docker? Consistent packaging of app + runtime dependencies.
7. Why Kubernetes? Scheduling, scaling, self-healing, service discovery, rolling deployments.
8. Production 503? Layer by layer: DNS → WAF/edge → LB → Ingress/Service → Pod readiness → container → application → dependencies.
9. Is the system healthy? Metrics, logs, traces, health checks, alerts.
10. Deployment breaks? Detect → investigate → mitigate → rollback/fix-forward → verify → root-cause analysis → prevent recurrence.

## Capstone checklist

Application (TypeScript REST API, PostgreSQL, Redis, authentication, validation, error handling) · Docker (multi-stage, non-root, health checks, small image) · CI (lint, typecheck, tests, build, Docker build) · CD (registry, deployment, rolling update, rollback) · Kubernetes (Deployment, Service, ConfigMap, Secret, Ingress, probes, resources, HPA) · AWS (VPC, EKS, RDS, S3, IAM, LB, CloudWatch) · Terraform (infra, modules, variables, outputs, state) · Observability (logs, metrics, traces, alerts). Build **one** realistic project (details in [Chapter 35](../docs/08-production/ch35-devops-capstone.md)).

## Added notes (not in source)

- Status `409 Conflict` (listed in the HTTP section) is not covered in Chapter 4's status-code list: it signals a request conflicting with current state (duplicate resource, version conflict) and is a common answer to idempotency/duplicate-create scenarios.
- This chapter states that ArgoCD/GitOps/Jenkins/Ansible/Service Mesh/Operators/CRDs are "awareness" topics; the source later covers each in depth (Ch.25–30).

<!-- NAV -->

---

← [Sheet 23](ch23-revision.md) · [Full chapter 24](../docs/09-interview/ch24-interview-oa-mastery.md) · [All revision material](README.md) · [Sheet 25](ch25-revision.md) →
