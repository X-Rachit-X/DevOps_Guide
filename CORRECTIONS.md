# Corrections, Clarifications and Verify-Items

This is the curated list of places where the source material is **technically wrong, imprecise, incomplete, internally inconsistent or time-sensitive**. The unabridged working log (including minor notes) is [docs/00-start-here/corrections-log-by-chapter.md](docs/00-start-here/corrections-log-by-chapter.md).

## Policy

- **Source text is never silently changed.** Imported chapter text is identical to the source apart from the documented mechanical transformations (see [AUDIT_REPORT.md](AUDIT_REPORT.md)). A correction lives *beside* the text — here, in the chapter's revision sheet, or in its clearly labelled "Editorial supplement".
- **Status legend**
  - **Verified** — checked against a primary source (official documentation page) *in this project*; the page is named.
  - **Reference** — the cited official documentation is the right place to confirm, but it was **not** re-fetched here. Treat as "believed correct; confirm before relying on it".
  - **Verify at use time** — depends on a version, price, quota or date and may already have changed.
- Nothing is marked *Verified* without a fetched source. "Reference" items are honest pointers, not claims of independent confirmation.

---

## A. Technical corrections (the source is wrong or misleading as written)

| # | Chapter | Issue | Correct statement | Status / reference |
|---|---|---|---|---|
| A1 | [26](docs/03-cicd-gitops/ch26-gitops-argocd.md) (§25, §37) | Says automated sync lets ArgoCD "reconcile the cluster back" after manual changes. | `syncPolicy.automated` alone does **not** revert live-cluster edits; the app shows *OutOfSync*. Reverting needs `selfHeal: true`; deleting resources removed from Git needs `prune: true`. Both default to **false**. | **Verified** — Argo CD docs, *Automated Sync Policy* (argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/) |
| A2 | [21](docs/06-iac-config/ch21-terraform.md) (§24) | `aws_instance` example uses `security_groups = [aws_security_group.app.name]`. | For an instance in a non-default VPC subnet use `vpc_security_group_ids = [aws_security_group.app.id]`. | Reference — Terraform AWS provider docs, `aws_instance` |
| A3 | [28](docs/06-iac-config/ch28-ansible.md) (§25–26) | Uses a play variable named `environment`. | `environment` is an Ansible **keyword** (task/play environment variables); pick another name such as `app_env`. | Reference — Ansible docs, *Creating valid variable names* / *Playbook keywords* |
| A4 | [3](docs/01-foundations/ch03-bash-automation.md) (§21) | `ps aux \| grep node \| wc -l` as a process count. | It also counts the `grep` itself (off by one). Use `pgrep -c node` or `grep [n]ode`. | Reference — procps/GNU grep behaviour |
| A5 | [33](docs/04-aws/ch33-advanced-aws-backend.md) (§34) | `redis.set(key, value, { EX: 300 })`. | That is **node-redis v4** syntax; **ioredis** (used in Chapter 35) takes positional arguments: `set(key, value, "EX", 300)`. | Reference — library docs |
| A6 | [32](docs/06-iac-config/ch32-advanced-terraform.md) (§55, §56, §85) | `required_version = ">= 1.x, < 2.0"`, `source = "..."`, `for_each = { api = "..." }`. | Placeholders, not valid HCL. Valid forms are in the chapter's supplement. | Editorial |
| A7 | [32](docs/06-iac-config/ch32-advanced-terraform.md) (§4) | First `.gitignore` lists `.terraform.lock.hcl`. | The source corrects itself immediately: **commit** the lock file. Final advice agrees with Chapter 21 §19. | Source self-correction |

## B. Precision issues (true in spirit, misleading if memorised literally)

| # | Chapter | Statement | More precise |
|---|---|---|---|
| B1 | [1](docs/01-foundations/ch01-cloud-devops-fundamentals.md) (§22) | SLA = "commitment/expectation". | An SLA is **contractual** with consequences (credits/penalties); the SLO is the internal target. Chapter 34 uses the precise definition. |
| B2 | [4](docs/01-foundations/ch04-networking.md) (§11) | A `/24` has 254 usable hosts. | Traditional figure. **AWS reserves 5 addresses per subnet → 251 usable.** (Reference: AWS VPC User Guide, *Subnet CIDR blocks*) |
| B3 | [4](docs/01-foundations/ch04-networking.md) (§19) | DNS "commonly UDP". | Also TCP (large responses, zone transfers) and DNS-over-TLS/HTTPS. |
| B4 | [14](docs/04-aws/ch14-load-balancing-scaling.md) (§40) | "ASG can also use health information". | By default an ASG uses **EC2 status checks**; enable ELB health checks on the ASG so a failing ALB target is replaced. (Reference: EC2 Auto Scaling User Guide, *Health checks*) |
| B5 | [18](docs/05-kubernetes/ch18-kubernetes-fundamentals.md) (§51) | Lists `CrashLoopBackOff`/`ImagePullBackOff` with Pod phases. | Those are container-status **reasons**; Pod phases are Pending, Running, Succeeded, Failed, Unknown. |
| B6 | [16](docs/04-aws/ch16-route53-cloudfront-waf.md) (§35, 36, 44) | WAF drawn as a hop in the traffic path. | WAF is **attached** to CloudFront/ALB (a web ACL association), not a separate hop. (Reference: AWS WAF Developer Guide) |
| B7 | [4](docs/01-foundations/ch04-networking.md) (§37), [16](docs/04-aws/ch16-route53-cloudfront-waf.md) (§39) | Diagrams put EC2 in public subnets behind the ALB. | Simplified; recommended layout (Ch 12/14/23) is ALB public, app and DB private. |
| B8 | [22](docs/07-observability-sre/ch22-observability-reliability.md) (§14) | Mentions latency metric but sample defines only a Counter. | Percentiles need a histogram/summary. |
| B9 | [19](docs/05-kubernetes/ch19-kubernetes-config-storage.md) | Lab Secret has key `API_KEY`; the Deployment references `DATABASE_URL`/`JWT_SECRET`. | Separate illustrations; create matching keys to run end to end. |
| B10 | [7](docs/02-containers/ch07-docker-fundamentals.md) (§13) | Container lifecycle: Created/Running/Stopped/Removed. | Docker also has paused, restarting, exited, dead. |

## C. Incomplete, placeholder or non-runnable examples

| Chapter | Example | Missing / fix |
|---|---|---|
| [6](docs/03-cicd-gitops/ch06-cicd-github-actions.md) §34 | Matrix snippet | does not use `${{ matrix.node }}` (completed in revision sheet) |
| [15](docs/04-aws/ch15-lambda-serverless-messaging.md) §39 | Deploy pipeline | zips devDependencies; does not wait for `aws lambda wait function-updated` |
| [21](docs/06-iac-config/ch21-terraform.md) §31 | Terraform workflow | `id-token: write` but no credentials step and no backend → `plan` would fail |
| [26](docs/03-cicd-gitops/ch26-gitops-argocd.md) | Application YAML | no `metadata.namespace: argocd` |
| [27](docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md) §17, 32, 40, 42 | `docker build/push` in `jenkins/jenkins:lts` | the image has no Docker CLI/daemon; `docker push my-api:${BUILD_NUMBER}` has no registry prefix (targets Docker Hub). Docker-socket mounting is a security risk (supplement) |
| [29](docs/05-kubernetes/ch29-crds-operators.md) | CRD `shortNames: [app]` | collides with Argo CD's `Application` short name if both are installed (Ch 26 installs Argo CD in the same cluster) |
| [35](docs/08-production/ch35-devops-capstone.md) §23 | Dockerfile | `pnpm` workspace in §5 but `npm ci` in §23; no `prisma generate`; Alpine vs Prisma/OpenSSL — see [capstone starter](code-examples/capstone/README.md) |
| [35](docs/08-production/ch35-devops-capstone.md) §25–26 | `SQS_QUEUE_URL=...` | no local SQS specified (LocalStack/ElasticMQ); queue-depth autoscaling unspecified (KEDA) |
| [33](docs/04-aws/ch33-advanced-aws-backend.md) §50 | Write to RDS then publish event | a dual write; use the outbox pattern |
| [18](docs/05-kubernetes/ch18-kubernetes-fundamentals.md) §16 | Pod with `node:22`, no command | exits immediately (the source says so) |

## D. Version-sensitive facts

| Fact | Where | Status |
|---|---|---|
| Public IPv4 addresses cost **$0.005 per IP-hour** since **1 Feb 2024** (announced 28 Jul 2023) | Ch 10, 12 | **Verified** — AWS News Blog, *New: AWS Public IPv4 Address Charge* |
| All new S3 objects get SSE-S3 encryption by default since **5 Jan 2023** | Ch 11 | **Verified** — S3 User Guide, *Default encryption FAQ* |
| New S3 buckets don't allow public access by default (Block Public Access) | Ch 11 | **Verified (summary level)** — S3 User Guide, *Blocking public access*; exact enablement date not extracted |
| S3 backend supports `use_lockfile` native locking; DynamoDB locking is **deprecated** | Ch 21, 32 | **Verified** (Terraform S3 backend page). The page does not state the introduction version; "Terraform ≥ 1.10" is from general knowledge → verify |
| `import` blocks ≥ 1.5, `terraform test` ≥ 1.6, `removed` block ≥ 1.7 | Ch 32 | Verify at use time |
| `docker run -v ./path:/x` relative host paths | Ch 7 §44 | Search results suggest recent Docker CLI work on relative sources, but no primary doc was confirmed → **use `-v "$(pwd)/src:/app/src"`**, which always works |
| Official `postgres` image 18+ changed the data directory layout (mount `/var/lib/postgresql`, not `/var/lib/postgresql/data`) | Ch 7 §43, Ch 8 | Search results point to docker-library/postgres issue #1370; primary README not fetched → verify. The source's `postgres:17` usage is fine |
| AWS App Mesh end of support | Ch 30 supplement | **Not confirmed** by the search; verify on the AWS page |
| API Gateway integration timeout / payload quotas | Ch 33 | Quota page was fetched but values were not extracted; they have changed over time → verify |
| EKS control-plane hourly fee, extended-support pricing, Auto Mode features | Ch 31 | Verify on the AWS pricing page |
| `actions/checkout@v4`, `setup-node@v4`, `configure-aws-credentials@v4`, `hashicorp/setup-terraform@v3`, Node 20/22/24 matrix, AWS provider `~> 6.0` | Ch 6, 15, 21 | Verify current majors |
| Helm 3 assumptions (`get-helm-3`); Helm 4 now exists | Ch 25 | Verify install docs |
| Argo CD install manifest from the `stable` branch URL | Ch 26 | Floating reference; pin a release in real use |
| `networking.istio.io/v1` stable API for newer Istio; older releases use `v1beta1` | Ch 30 | Match your Istio version |
| `kubectl get endpoints` → EndpointSlices | Ch 20, 23, 31 | Endpoints API being deprecated; both appear in the source |
| SHA-256 Git repositories | Ch 5 §7 | Accurate; still limited hosting support |

## E. Structural problems in the source material

| # | Issue | Handling |
|---|---|---|
| E1 | The request said **37 responses**; the supplied material has **36 files with content** (files 1–36). Files 37–40 are empty (0 bytes). Neither count matches 37, and no source file is missing a response in between. (An earlier pass of this project wrongly treated file 36 as empty; it was caught in the final audit and imported as Chapter 36.) | Documented in [PROGRESS.md](PROGRESS.md) and [SOURCE_COVERAGE.md](SOURCE_COVERAGE.md). |
| E2 | Chapter 35 promises **"Response 36 — Final Cloud + DevOps Mastery"**; no such response exists. Source file 36 is a different, stand-alone *Virtualization Internals* deep dive (no `Response N/M` header). The roadmap tables also changed from `/24` to `/36`. | Reported, not invented. Chapter 35 is a *design specification*; an editorial starter is provided and labelled. |
| E3 | Chapter 24 says "The roadmap is complete (24/24)" and lists ArgoCD, GitOps, Jenkins, Ansible, service mesh, Operators, CRDs as awareness-only. Responses 25–35 later teach them. | Kept as historical text; the Part I / Part II structure explains it. |
| E4 | Chapter 26 §14 says "Remember Response 20? We learned that Kubernetes can be extended using CRDs." CRDs are in Chapter 29, not 20. | Mistaken back-reference noted; nothing is missing from Chapter 20. |
| E5 | Several sources begin or end with conversational/meta text and progress tables. | Moved verbatim to [removed-scaffolding.md](docs/00-start-here/removed-scaffolding.md) and [course-design-notes.md](docs/00-start-here/course-design-notes.md) — nothing deleted. |
| E6 | Source code fences carried tool-generated `id="…"` attributes. | Stripped from the fence info string; code content untouched. |
| E7 | Ch 19 numbering skips §28 (unnumbered section); Ch 5 §10 has a confusing diagram the text itself corrects ("Actually, more clearly:"). | Kept. |

## F. Gaps filled editorially (additions, not corrections)

These topics are **absent** from the source and were added in clearly labelled places. They are not source facts.

| Chapter | Added | Where |
|---|---|---|
| 8 | CMD vs ENTRYPOINT, exec vs shell form, PID 1 signals, `USER node`, resource flags, Compose `service_healthy`, bridge DNS | [supplements/ch08.md](supplements/ch08.md) |
| 9–17 | Instance store, IMDSv2 summary, RDS Proxy, Multi-AZ variants, ASG health-check type, SQS FIFO/DLQ/visibility rules, Lambda limits, Alias vs CNAME, CloudWatch agent for memory/disk, Secrets Manager vs Parameter Store | each chapter's revision sheet |
| 18–20 | kube-proxy, rollout commands, PVC access modes, QoS, startupProbe, HPA formula, rolling-update parameters, NetworkPolicy semantics | revision sheets |
| 22, 34 | Burn rate, composite availability, MTBF/MTTR, PromQL, k6, token bucket, USE/golden signals | [supplements/ch34.md](supplements/ch34.md) and revision sheet |
| 27 | Jenkinsfile `parallel`/`when`/`input`/`parameters`, Docker-in-Jenkins caveats | [supplements/ch27.md](supplements/ch27.md) |
| 30 | `PeerAuthentication`, `AuthorizationPolicy`, timeouts/retries, outlier detection, default retries | [supplements/ch30.md](supplements/ch30.md) |
| 31 | eksctl, IRSA vs Pod Identity, ALB Ingress annotations, max-pods formula | [supplements/ch31.md](supplements/ch31.md) |
| 32 | S3 backend with `use_lockfile`, `for_each`, lifecycle, import/moved/removed, remote state | [supplements/ch32.md](supplements/ch32.md) |
| 33 | ECS task vs execution role, DynamoDB query, Step Functions ASL, saga/outbox | [supplements/ch33.md](supplements/ch33.md) |
| 36 | Commands to observe virtualization, VMX vs rings, nested-paging cost, Nitro/Firecracker notes | [supplements/ch36.md](supplements/ch36.md) |
| 35 | Reference starter (API, worker, schema, Compose, CI, K8s, KEDA) | [supplements/ch35.md](supplements/ch35.md), [code-examples/capstone/](code-examples/capstone/README.md) |

## G. Security notes on the source

- [Ch 25](docs/05-kubernetes/ch25-helm.md): installs Helm with `curl … | bash`; prefer the package manager or verify the checksum.
- [Ch 27](docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md): mounting `/var/run/docker.sock` into Jenkins is root-equivalent on the host.
- [Ch 10](docs/04-aws/ch10-ec2-compute.md): adding a user to the `docker` group is root-equivalent.
- Everywhere: never commit secrets, state files, or `terraform.tfvars` with credentials; Kubernetes Secrets are base64, not encryption (Ch 19).

---
[← Contents](CONTENTS.md)
