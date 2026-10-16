# Interview Q&A Bank

Consolidated from the interview sections of all 36 chapters, with concise answers. Many of the source's own question lists give pointers without answers; the answers here are taken from the chapter text, and any that go beyond it are marked *(added)*. Say them aloud. Chapter in brackets.

## Fundamentals and Linux

1. **Scalability vs elasticity?** Scalability = can handle growth by adding resources; elasticity = automatically adds *and removes* resources with demand. (1)
2. **HA vs fault tolerance?** HA = redundancy keeps the service accessible; fault tolerance = continues operating correctly despite component failure. (1)
3. **RTO vs RPO?** Time to restore service vs amount of data (in time) you can lose. (1, 34)
4. **Cloud vs DevOps?** Cloud = infrastructure and services; DevOps = how teams build, test, deploy and operate together. (1)
5. **What is Linux?** An OS kernel; distributions package it with utilities. (2)
6. **Process vs program?** Running instance vs file on disk. *(added)* (2)
7. **`chmod 755`?** Owner rwx, group r-x, others r-x. (2)
8. **App is "down", you SSH in — what first?** Don't restart; process → port → logs → `curl localhost` → config → CPU/mem/disk → firewall/SG → LB → DNS. (2)
9. **Disk full?** `df -h`, then `du -sh *` down the tree; check `/var/log`, Docker images, temp files. (2, 10)
10. **What does `set -euo pipefail` do?** Exit on error, error on unset vars, fail pipelines if any stage fails. (3, 24)
11. **Deployment script: command 3 of 6 fails but 4–6 run — fix?** `set -e` / explicit exit-code checks, fail fast, validate before destructive steps, rollback. (3)
12. **Pipe / `2>&1` / `$?`?** stdout→stdin of next command; send stderr to stdout's destination; last exit status. (3)

## Networking

13. **TCP vs UDP?** Reliable ordered connection-oriented vs connectionless low overhead; HTTP/3 runs on QUIC (UDP). (4)
14. **Trace `https://api.example.com/users`.** DNS → TCP handshake → TLS → HTTP request → CDN/WAF/LB → app → DB → response back. (4)
15. **Why would an app on `localhost:3000` be unreachable?** Bound to 127.0.0.1 instead of 0.0.0.0; port not published; firewall/SG. (4, 7)
16. **Public vs private subnet?** Route to an Internet Gateway vs none; private can still reach out via NAT. (4, 12)
17. **SG vs NACL?** Stateful/resource-level/allow vs stateless/subnet-level/allow+deny. (4, 12)
18. **A, AAAA, CNAME?** Name→IPv4, name→IPv6, name→name. (4, 16)
19. **What does a 502 mean?** Proxy/LB got an invalid response from upstream — check target health, port, SG, app logs. (4)

## Git and CI/CD

20. **Merge vs rebase? When avoid rebase?** Preserve history vs rewrite to linear; avoid on shared history. (5)
21. **Reset vs revert?** Rewrite/move history vs add undoing commit (safe for shared). (5)
22. **Committed a password and pushed?** Rotate/revoke first, remove from history, investigate use, add secret scanning, use secret management. (5)
23. **CI vs CD?** CI integrates and validates continuously; Delivery keeps release-ready with approval; Deployment auto-releases. (6)
24. **Why `npm ci`?** Reproducible install from the lockfile. (6)
25. **Rolling vs blue-green vs canary?** Gradual replace; two environments + switch; small % first. (6)
26. **Why immutable image tags?** Traceability and easy rollback; `latest` is mutable. (6, 8)
27. **CI passes, deploy succeeds, users get 500s?** Image/env/secrets/migrations/logs/health/dependencies/LB → rollback if needed. (6)
28. **Why Jenkins when Actions exists?** Mature extensible server with huge plugin ecosystem; existing infra; customised pipelines. (27)
29. **GitOps definition?** Git holds declarative desired state; a controller reconciles the cluster to it. (26)
30. **Dev manually changed a prod Deployment under GitOps?** Decide if intentional; change Git via review or revert the drift; with `selfHeal` ArgoCD reverts it. (26)

## Docker

31. **Image vs container? Container vs VM?** Immutable template vs running instance; shared kernel vs guest OS. (7)
32. **`RUN` vs `CMD` vs `ENTRYPOINT`; what does `EXPOSE` do?** Build time / default start command / always-run executable *(supplement)*; documents only. (7, 8)
33. **Why multi-stage builds? Why copy `package.json` first?** Smaller, safer runtime image; cache the dependency layer. (7, 8)
34. **Why not root, why not secrets in images?** Least privilege; secrets persist in layers/history. (8)
35. **Running vs healthy?** Process up vs able to serve (health checks). (8)
36. **Container exits immediately / can't reach the API?** `docker ps -a`, `logs`, port mapping, `0.0.0.0` binding, env vars, network. (7, 8)

## AWS

37. **Region vs AZ; why multi-AZ?** Geographic area vs isolated location; survive AZ failure. (9)
38. **User vs role; least privilege; how should a Node app access S3?** Role with temporary credentials, minimal permissions, never hard-coded keys. (9, 10)
39. **GitHub Actions → AWS securely?** OIDC federation to an IAM role, short-lived credentials. (9, 17)
40. **Debug `AccessDenied`.** `aws sts get-caller-identity`, then policies, explicit deny, resource ARN. (9)
41. **AMI vs instance; stop vs terminate; why not DB on EC2?** Template vs VM; restartable vs deleted; you'd own backups/HA/patching → RDS. (10)
42. **S3 vs EBS vs EFS?** Object / block / shared filesystem. (11)
43. **Upload a 1 GB file efficiently?** Presigned (multipart) URL straight to S3. (11)
44. **Design a VPC for a Node API + PostgreSQL.** ALB in public subnets, EC2/EKS in private, RDS in private DB subnets; IGW, NAT, SG chain, ≥2 AZs. (12)
45. **Multi-AZ vs read replica?** Failover vs read scaling. (13)
46. **Scaled 2→20 instances and PostgreSQL rejects connections?** Instances × pool size exceeded DB limit → tune pools, RDS Proxy, caching. (13)
47. **ALB vs ASG roles; what if an instance is unhealthy?** ALB routes; ASG sizes. Health check fails → ALB stops routing → ASG replaces → check passes → traffic. (14)
48. **Why stateless?** Any instance can serve any request → scaling/replacement easy. (14)
49. **Lambda vs EC2; SQS vs SNS?** Event functions vs servers; queue vs pub/sub. (15, 33)
50. **Visibility timeout, DLQ, idempotency?** Hides in-flight message; stores repeatedly failing messages; makes duplicate processing safe. (15)
51. **Route 53 vs CloudFront; WAF vs SG?** DNS vs CDN; HTTP-aware filtering vs network access. (16)
52. **CloudWatch vs CloudTrail?** Metrics/logs/alarms vs API audit. (17)
53. **Monitor an EC2 server?** CloudWatch + agent (memory/disk need the agent *(added)*) + logs + alarms. (17)
54. **Choose compute?** EC2 control, ECS simple AWS-native containers, EKS Kubernetes ecosystem, Lambda events. (33)
55. **RDS vs DynamoDB?** Relational/joins vs access-pattern key-value at scale; not "faster". (13, 33)
56. **SQS vs SNS vs EventBridge?** Queue / fan-out / bus + rules. (33)
57. **Design an image-processing backend.** Upload to S3 → S3 event → SQS → Lambda/ECS worker → S3 output → DB metadata. (33)
58. **Compensation / saga?** Undo completed steps (refund) when a later step fails. (33)

## Kubernetes

59. **Why Kubernetes; Docker vs Kubernetes?** Orchestration at scale (scheduling, scaling, self-healing, discovery, rollouts). (18)
60. **Pod vs container; why Services?** Pod wraps containers; Pod IPs are ephemeral. (18)
61. **Control-plane components?** API server, scheduler, controller manager, etcd; kubelet on nodes. (18)
62. **What happens when a Pod dies?** Controller sees missing replica → creates one → scheduler places → readiness → Service routes. (19)
63. **Liveness vs readiness?** Restart vs traffic eligibility. (19, 20)
64. **Ingress vs Ingress Controller?** Rules vs implementation. (20)
65. **HPA vs node autoscaling; why does HPA need requests/Metrics Server?** Pods vs nodes; percentages are relative to requests, metrics must exist. (20)
66. **Pod Pending / CrashLoopBackOff / ImagePullBackOff / Service no endpoints?** Scheduling constraints / app crash logs / image or auth / selector mismatch. (20, 23)
67. **Secrets "encrypted"?** Only base64 by default; enable encryption at rest, restrict RBAC. (19)
68. **CRD vs operator; spec vs status; finalizer?** Type vs controller; desired vs observed; cleanup before deletion. (29)
69. **What is a service mesh; when not to use?** Sidecar-based service-to-service layer; avoid for small apps (overhead). (30)
70. **Why can EKS Pods run out of IPs?** VPC CNI uses subnet IPs/ENIs; maxPods = ENIs × (IPs per ENI − 1) + 2 *(added)*. (31)
71. **IRSA/Pod Identity; IAM vs RBAC?** Per-workload AWS credentials; AWS vs Kubernetes API authorization. (31)
72. **Helm chart vs release; Helm vs Operator?** Package vs installed instance; install vs continuous management. (25, 29)

## IaC and configuration

73. **Why Terraform; state; remote state; locking?** Reproducible infra as code; maps config↔reality; shared; prevents concurrent corruption. (21, 32)
74. **Drift?** Real infra differs from config — `plan` shows it. (21)
75. **Someone changed RDS manually?** Intentional? update code and plan; accidental? decide whether to restore. (32)
76. **Terraform wants to destroy prod RDS?** STOP, read the plan (address change, immutable field, refactor), use `moved`/fix. (32)
77. **Why not Terraform and ArgoCD on the same resource?** Ownership conflict. (32)
78. **Terraform vs Ansible; why Ansible is agentless; idempotency; why modules over `shell`?** Provision vs configure; SSH + modules; same end state on re-run; modules know desired state. (28)

## Observability and SRE

79. **Logs/metrics/traces; RED; percentiles?** What happened / how much / where time went; rate-errors-duration; averages hide tails. (22)
80. **SLI/SLO/SLA/error budget/burn rate?** Measurement / target / contract / allowed failure / consumption speed. (22, 34)
81. **Retries, backoff, jitter, circuit breaker, bulkhead, rate limiting, idempotency?** Recover transients; avoid hammering; avoid sync retries; fail fast; isolate; protect; safe repeats. (22, 34)
82. **How would you make your backend reliable?** Prevent → Detect → Contain → Recover → Learn. (34)
83. **API returns 30% 500s?** Confirm impact, metrics, recent deploy, logs, traces, dependencies, DB, mitigate/rollback, verify, RCA, postmortem. (34)
84. **Traffic 10×?** Find the bottleneck; autoscale, CDN/cache, rate limit, queue, shed load, protect DB. (14, 34)
85. **Why load test / chaos test?** Find capacity and bottlenecks / verify failure handling. (34)
86. **Multi-AZ vs multi-region; DR strategies?** AZ vs region failure; backup-restore, pilot light, warm standby, active-active. (34)
87. **Postmortem?** Blameless review: what, impact, cause, why safeguards missed it, fixes. (34)

## Virtualization internals

91. **What is a hypervisor; Type 1 vs Type 2?** Layer that creates/manages VMs and controls physical resources; bare-metal (Hardware→Hypervisor→VMs) vs hosted (Hardware→Host OS→Hypervisor→VMs). (36)
92. **What is a VM exit and why does it matter?** Guest→hypervisor transition for operations needing hypervisor handling; costs time, so modern designs minimise exits. (36)
93. **How does VM memory translation work?** GVA→GPA (guest page tables)→HPA (EPT/NPT); TLB caches translations. (36)
94. **Ballooning, overcommitment, paravirtualization, SR-IOV?** Reclaim memory via guest driver; allocate more than physical hoping peaks don't coincide; guest-aware drivers like VirtIO; one PCIe device exposing virtual functions to VMs. (36)
95. **VM vs container internals; why do containers start faster?** Guest kernel on virtual hardware vs shared host kernel isolated with namespaces + cgroups; starting a process vs booting a kernel. (7, 36)
96. **Snapshot vs live migration?** State capture for restore/clone vs moving a running VM between hosts (pre-copy). (36)

## Whole-system

88. **Deploy a production Node.js app.** Multi-stage Docker → ECR immutable tags → Kubernetes (EKS if justified) → stateless Pods behind Service + LB → Terraform → RDS/S3/Redis → private DB → CI/CD with scans → probes/limits/HPA → logs/metrics/traces + actionable alerts → outside-in troubleshooting. (23)
89. **`git push` to production — walk through it.** Git → GitHub → Actions (test/build/scan) → Docker → ECR → GitOps repo → ArgoCD → rolling update. (24, 26)
90. **Production 503 — debug layer by layer.** DNS/TLS → WAF/edge → LB → Ingress/Service → endpoints → Pod readiness → app → dependencies. (23, 31)

---
[← Revision index](README.md)
