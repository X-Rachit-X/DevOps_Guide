# Corrections and Ambiguities — Chapter-by-Chapter Log

Working log kept while reading each response. The curated, categorised summary is in
[CORRECTIONS.md](../../CORRECTIONS.md); this file is the complete record.

## Ch1
- [CLARIFY] Ch1 §22: SLA described as "a commitment/expectation". Precisely, an SLA is a *contractual* agreement with consequences (credits/penalties) when missed; SLO is the internal target. Ref: Google SRE Book, ch. "Service Level Objectives". (Ch.34 covers this in depth — check consistency.)
- [CLARIFY] Ch1 §20: container diagram shows "Container Runtime" directly on "Physical Machine" and "Host OS" below the containers; in reality hardware → host OS (kernel) → container runtime → containers. Diagram is a simplification; not changed.
- [CLARIFY] Ch1 §10 PaaS gives no concrete example ("various managed application platforms"); examples commonly cited: AWS Elastic Beanstalk, Heroku. Added in glossary only.
## Ch2
- [CLARIFY] §33: `ss -tulpn | grep 3000` — process names/PIDs for sockets owned by other users only appear when run with sudo. Not a source error; added to revision sheet.
- [GAP] Interview Q "process vs program" (§Interview) has no answer in source; answer added to revision sheet and marked as added.
- [GAP] Cheat sheet (§35) lists `id` and `env` which are never explained in the chapter body; brief explanation added in revision sheet.
- [AMBIGUITY] §21: "kill sends a signal asking the process to terminate gracefully" — true for default SIGTERM; a process may handle or ignore SIGTERM (only SIGKILL cannot be caught). Consistent with §22.
## Ch3
- [CORRECTION-minor] §21: `ps aux | grep node | wc -l` also matches the grep process itself, so the count is one too high. Fix: `pgrep -c node`, or `ps aux | grep [n]ode | wc -l`. Ref: GNU grep / procps docs (behavioural, well known). Source text preserved; note added in revision + CORRECTIONS.
- [CLARIFY] §28: source warns about `set -e` subtleties but doesn't list them (e.g. not triggered in conditions `if cmd`, `cmd && x`, `cmd || x`, or in non-final pipeline stages without pipefail). Not changed.
- [CLARIFY] §3/§2: Source mixes "npm build" (§42 pseudo list "npm build") — the real command is `npm run build`. Cosmetic.
- [ADDED] Interview Qs 1-15 had no answers; answers added in revision sheet only.
## Ch4
- [TOOLING] Source code fences contain tool-generated attributes e.g. ```bash id="atx2dv" — stripped during import (language tag kept). No content change.
- [CLARIFY] §11: "254 usable host addresses" is the traditional figure. AWS reserves 5 addresses per subnet (251 usable for /24). Ch12 should cover; cross-check there. Ref: AWS VPC docs "Subnet CIDR blocks".
- [INCONSISTENCY] §37 diagram places EC2 instances directly under "Public subnet" with ALB; §38/§40/§45 describe the normal pattern of ALB in public and EC2/RDS in private subnets. Treated as simplified diagram; later chapters give the proper layout.
- [CLARIFY] §19: DNS "commonly using UDP" — also uses TCP (large responses, zone transfers, DNS over TLS). Added in revision.
- [CLARIFY] §39: NACL rules are numbered, evaluated in order, and support allow AND deny; Security Groups support allow rules only. Source says "rules for allowed traffic" for SG which is correct; NACL deny capability is not mentioned (check Ch12).
## Ch5
- [AMBIGUITY] §10: Branch-pointer diagrams — the 3rd diagram (after "After a new commit") is confusing (shows 'main → C' under D) and the source immediately says "Actually, more clearly:" and gives the correct one. Kept as-is; correct diagram is the second.
- [CLARIFY] §30/§47: Reset/Revert/secret removal details — added precision in revision (force-with-lease, revert -m for merge commits, git filter-repo / BFG). Ref: git-scm.com docs (git-revert, git-push --force-with-lease, git-filter-repo).
- [CLARIFY] §7: "Modern Git uses SHA-1 ... with support for SHA-256 repositories" — accurate; SHA-256 support is still considered experimental/limited in hosting providers. Ref: git hash-function-transition docs.
- [GAP] §43 tags listed as object type but not explained (annotated vs lightweight). Added to revision.
## Ch6
- [VERSION-DRIFT] Workflows pin actions/checkout@v4 and actions/setup-node@v4; node-version 22 and matrix [20,22,24] are time-sensitive (Node release schedule). Not changed; flagged for verification at use time. Ref: github.com/actions/checkout, nodejs.org/en/about/previous-releases.
- [GAP] §34 matrix snippet is incomplete as shown (does not use ${{ matrix.node }}). Completed in revision sheet.
- [GAP] §36 uses `cache: npm` in setup-node but the text never explains it (covered generally in §33).
- [CLARIFY] §23 forward-reference "Response 7/8 later" — fine; Docker chapters are 7 and 8.
## Ch7
- [VERIFY] §44 `-v ./src:/app/src` in `docker run`: relative host paths in `-v` have historically not been accepted by `docker run` (treated as a volume name); Compose accepts them. Safer: `-v "$(pwd)/src:/app/src"` or `--mount type=bind,src=...`. Check current Docker docs before asserting.
- [VERIFY] §43 `docker run -v postgres-data:/var/lib/postgresql/data postgres` — newer official postgres images (18+) changed the data directory layout (mount point /var/lib/postgresql). Source compose uses postgres:17 where the path is valid. Verify via docker-library/postgres README.
- [CLARIFY] §13 lifecycle lists Created/Running/Stopped/Removed; Docker also has paused, restarting, exited, dead states. Simplification.
- [CLARIFY] §3 'Physical/Cloud Machine -> Host OS Kernel -> Container Runtime' — fine.
- [CLARIFY] §24 uses full node:22 image and installs devDependencies into the final image; Ch8 improves (multi-stage, slim, non-root).
## Ch8
- [GAP-FILLED] Interview Q8 'CMD vs ENTRYPOINT' not explained in body → supplements/ch08.md (labelled editorial). Also exec vs shell form, PID 1 signal handling, `USER node`, resource-limit flags, Compose service_healthy, user-defined bridge DNS. Refs: Docker docs (Dockerfile reference, Compose startup order, bridge networks).
- [CLARIFY] §12 `useradd` works in Debian-based node:22-slim; Alpine uses `adduser`/`addgroup`. Official node images already include user `node`.
- [CLARIFY] §21 Compose: top-level `version:` omitted (correct for current Compose Spec). `postgres:17` + volume path /var/lib/postgresql/data valid for 17; see Ch7 VERIFY note about newer images.
- [CLARIFY] §22/§23 consistent with Compose docs: depends_on short form only controls start order.
- [CLARIFY] §14 HEALTHCHECK inline `node -e "fetch(...)"` requires Node >= 18 (global fetch); fine for node:22.

## Ch9
- [GAP] Role trust policy vs permissions policy, resource-based policies, permission boundaries and SCPs are not covered; ListBucket vs GetObject ARN distinction is not mentioned. Added to revision sheet. Ref: AWS IAM User Guide (Policies and permissions; S3 policy actions/resources).
- [CLARIFY] Sections 22 and 38 mention OIDC conceptually only; concrete trust-policy and workflow configuration appear later (check Ch17/Ch33).
- [CLARIFY] Section 28 shared responsibility is labelled 'a simplification' in the source, which is accurate.

## Ch10
- [GAP] Section 26 is titled 'EC2 Local Disk vs EBS' but never describes instance store (ephemeral local storage). Added to revision. Ref: AWS EC2 User Guide, Instance store.
- [VERIFY] Public IPv4 addresses are billed by AWS since Feb 2024; source (Elastic IP discussion) predates/omits this. Check current pricing page.
- [CLARIFY] Section 34 installs docker.io via apt (Ubuntu). On Amazon Linux use dnf/yum; adding a user to the docker group is root-equivalent. Added to revision.
- [CLARIFY] Section 29 IMDSv2 details intentionally omitted in source ('no need to memorize endpoint details yet'); mechanism summarised in revision.
- [CLARIFY] Section 21/47 recommend private EC2 behind a load balancer; consistent with Ch4 note about simplified diagram in Ch4 section 37.

## Ch11
- [GAP] No concrete durability figure given (11 nines); consistency model, CORS requirement for browser direct upload, presigned URL expiry limits, multipart size limits, KMS permissions for SSE-KMS not mentioned. Added to revision. Ref: AWS S3 User Guide (Data protection; Presigned URLs; Multipart upload overview; CORS).
- [VERIFY] 2023 defaults (Block Public Access on, SSE-S3 default encryption, ACLs disabled) stated in revision from general knowledge; verify against current S3 docs.
- [CLARIFY] Section 36 names only S3/EBS/EFS; other storage types (FSx, Storage Gateway, instance store) not covered. Out of scope.
- [FORMAT] Preamble of source file 11 (lines 1-51) is an AWS-block roadmap reply; preserved in docs/00-start-here/course-design-notes.

## Ch12
- [RESOLVED] Ch4 flag about NACL deny capability: Ch12 section 21 table states SG = allow-focused, NACL = allow + deny. Consistent with AWS docs.
- [GAP] AWS reserves 5 IPs per subnet (251 usable in a /24); source Ch4 says 254 (traditional) and Ch12 does not mention the reservation. Added to revision. Ref: AWS VPC User Guide, Subnet CIDR blocks.
- [GAP] Default SG/NACL behaviour, NAT Gateway placement in public subnet + Elastic IP, NAT/endpoint cost model, DNS attributes. Added to revision. Ref: AWS VPC docs (Security groups, Network ACLs, NAT gateways, Gateway endpoints pricing).
- [CLARIFY] Section 40 final diagram is hard to read (box drawing); the narrative description before/after it is authoritative.
- [CLARIFY] Section 16 diagram places NAT GW in the public subnet; correct and consistent with AWS requirements.

## Ch13
- [GAP] RDS Proxy appears in the depth guide and the scenario solutions but is never explained. Explained in revision. Ref: AWS RDS Proxy docs.
- [GAP] Multi-AZ variants (instance vs cluster), Aurora, asynchronous replication, DNS-based failover, PITR retention details not covered. Added to revision. Ref: AWS RDS User Guide (Multi-AZ deployments, Read replicas, Backups).
- [CLARIFY] Section 19 itself notes backup/snapshot behaviour depends on engine/configuration; kept as mental model.
- [CLARIFY] Section 6 hard-codes port 5432 while other values come from env; minor inconsistency, harmless.

## Ch14
- [CLARIFY] Section 40: 'ASG can also use health information' - by default ASG health checks are EC2 status checks; ELB health checks must be enabled on the ASG for ALB-driven replacement. Added to revision. Ref: AWS EC2 Auto Scaling User Guide, Health checks for instances in an Auto Scaling group.
- [GAP] Deregistration delay, warm-up/cooldown, health-check thresholds, ACM/TLS termination at ALB, X-Forwarded-For, target types (instance/ip/lambda) not covered; ELB types NLB/GWLB only as 'awareness'. Added to revision.
- [CLARIFY] Section 27 scheduled-scaling snippet uses labels 'Scale in/Scale out' next to 7:30 PM / 7:30 AM; it is illustrative only.
- [CLARIFY] Section 11 lists round robin and least outstanding requests; ALB also supports weighted random with anomaly mitigation. Not changed.

## Ch15
- [GAP] SQS standard vs FIFO, visibility-timeout vs Lambda-timeout relation, DLQ maxReceiveCount, partial batch failure, Lambda limits (timeout/memory/payload/concurrency) not stated. Added to revision. Ref: AWS Lambda Developer Guide (Quotas; Using Lambda with Amazon SQS); SQS Developer Guide.
- [CLARIFY] Section 39 pipeline zips node_modules including devDependencies and does not wait for update completion (aws lambda wait function-updated). Source says 'the exact production pipeline can be improved later'. Added improvements in revision.
- [CLARIFY] Section 26 consumer loop has no partial-failure handling; relies on idempotency (section 20) - consistent but incomplete.
- [FORMAT] Source file 15 lines 1-8 (teaching-style reply) and trailing 'one important adjustment going forward' note preserved in docs/00-start-here/course-design-notes.
- [VERSION-DRIFT] actions/checkout@v4, setup-node@v4, aws-actions/configure-aws-credentials@v4 pinned; verify current major versions.

## Ch16
- [GAP] Alias-vs-CNAME at the zone apex, ACM/WAF Region requirements for CloudFront (us-east-1), Origin Access Control for private S3 origins, CloudFront invalidation command in the pipeline, CORS between www and api origins. Added to revision. Ref: AWS Route 53 Developer Guide (Choosing between alias and non-alias records); CloudFront Developer Guide (Using ACM certificates; Restricting access to an S3 origin); AWS WAF Developer Guide (Associating a web ACL).
- [CLARIFY] Sections 35, 36, 44: WAF is drawn as a hop between CloudFront and ALB; it is actually attached to (associated with) the CloudFront distribution or ALB. Source states diagrams show the concept (section 44 last paragraph).
- [CLARIFY] Section 46: S3 sync is shown without --delete or CloudFront invalidation; cached stale index.html is a common issue (section 51 covers debugging).
- [CLARIFY] Section 39: 'EC2 instances in public subnets A/B behind ALB' conflicts with earlier best practice (EC2 in private subnets). Source is describing the minimal setup; Ch12/Ch14 describe the preferred private-subnet layout.

## Ch17
- [GAP/IMPORTANT] Source does not state that EC2 memory and disk-usage metrics are not published by default (need CloudWatch agent); basic vs detailed monitoring resolution. Added to revision. Ref: AWS CloudWatch User Guide (Metrics collected by the CloudWatch agent; Amazon EC2 metrics).
- [GAP] Alarm states and the need for alarm actions (SNS) in the put-metric-alarm example; log retention default; CloudTrail event history/trail/S3; Secrets Manager vs SSM Parameter Store; KMS key types. Added to revision.
- [CLARIFY] Section 15 example says period 5 min while section 38 CLI uses evaluation-periods 2; consistent but different illustrations.
- [CLARIFY] Sections 47: 'Awareness' services (Config, GuardDuty, Security Hub, Inspector, Macie) are named without descriptions; one-line descriptions added to glossary only.

## Ch18
- [GAP] kube-proxy, cloud-controller-manager, Deployment->ReplicaSet->Pod relationship and rollout/rollback commands, Service DNS names, Secret base64 caveat, NetworkPolicy, dockershim removal (v1.24). Added to revision. Ref: kubernetes.io/docs (Concepts: Components, Deployments, Services/DNS, Secrets; Dockershim removal FAQ).
- [CLARIFY] Section 51 lists Pod phases (Pending, Running, Succeeded, Failed, Unknown) together with CrashLoopBackOff/ImagePullBackOff, which are container status reasons not phases. Clarified in revision.
- [CLARIFY] Section 16 Pod manifest runs node:22 with no command; would exit immediately. Source flags it as 'not yet useful'.
- [CLARIFY] Section 11: 'Modern Kubernetes ... containerd rather than Docker Engine' correct; v1.24+ removed dockershim.
- [FORMAT] Source file 18 lines 1-10 (scope reassurance reply) and trailing scope section/roadmap preserved in course-design-notes.

## Ch19
- [INCONSISTENCY] Lab (Part 11 step 2) creates Secret api-secret with API_KEY and step 4 expects API_KEY=test-key, but the Deployment in Part 8 references api-secret keys DATABASE_URL and JWT_SECRET. Lab and Deployment are separate illustrations; to run end-to-end create the matching keys or add an API_KEY env entry. Source preserved.
- [CLARIFY] Section numbering skips 28 (the 'Complete Node.js Deployment' part is unnumbered). Cosmetic.
- [GAP] PVC access modes (RWO/ROX/RWX/RWOP), EBS AZ-binding, reclaim policy, WaitForFirstConsumer, mounted ConfigMap/Secret volumes auto-update, CPU throttling vs OOMKill, QoS classes, startupProbe, liveness-should-not-check-dependencies. Added to revision. Ref: kubernetes.io/docs (Persistent Volumes; Configure Quality of Service; Configure Liveness, Readiness and Startup Probes; ConfigMaps).
- [CLARIFY] Section 9 correctly states base64 is not encryption; Kubernetes can encrypt Secrets at rest in etcd (EncryptionConfiguration; on EKS via KMS envelope encryption) - see Ch31.
- [CLARIFY] Step 6 'Break the Health Endpoint' exercises the liveness probe (restart), distinct from readiness.

## Ch20
- [GAP] No complete Ingress manifest (only rules fragment); HPA formula not stated; rolling-update parameters maxSurge/maxUnavailable; NetworkPolicy default-allow semantics and CNI enforcement requirement; names of EKS workload-identity mechanisms (IRSA, Pod Identity) not given; Gateway API not mentioned. Added to revision. Ref: kubernetes.io/docs (Ingress; HorizontalPodAutoscaler walkthrough - algorithm details; Deployments - rolling update; Network Policies); AWS EKS docs (IAM roles for service accounts; EKS Pod Identity).
- [CLARIFY] Section 16 NetworkPolicy is labelled 'conceptual'; source includes the caveat 'assuming the cluster networking implementation enforces the policy'.
- [VERSION-DRIFT] kubectl get endpoints: Endpoints API is being deprecated in favour of EndpointSlices (source mentions both).
- [CLARIFY] Section 31 pipeline lists Terraform infrastructure; Terraform covered in Ch21/Ch32; observability in Ch22.

## Ch21
- [CORRECTION] Section 24 (Dependencies) example: `security_groups = [aws_security_group.app.name]` in aws_instance is the EC2-Classic/default-VPC argument. For instances launched in a (non-default) VPC subnet the correct argument is `vpc_security_group_ids = [aws_security_group.app.id]`. Source code preserved verbatim; correction noted in CORRECTIONS and revision. Ref: Terraform AWS provider docs, aws_instance (security_groups vs vpc_security_group_ids).
- [INCOMPLETE-EXAMPLE] Section 31 workflow declares `permissions: id-token: write` but has no credentials step and no backend, so `terraform plan` would fail against AWS. Source states 'the important thing isn't memorizing this YAML'. Completion described in revision.
- [GAP] count/for_each/lifecycle/dynamic blocks listed as 'medium' but not explained here (see Ch32); plan -out, import blocks, S3 native locking syntax, TF_VAR env vars, sensitive variables, BSL licence/OpenTofu. Added to revision. Ref: developer.hashicorp.com/terraform docs (CLI commands, S3 backend, import).
- [VERIFY] S3 native state locking (`use_lockfile`) requires Terraform >= 1.10 (as of knowledge); confirm in current docs.
- [VERSION-DRIFT] AWS provider `~> 6.0`, hashicorp/setup-terraform@v3, actions/checkout@v4 are time-sensitive.

## Ch22
- [GAP] No numeric error-budget examples, backoff formula, PromQL/Alertmanager/exporters/histograms, trace context propagation, golden signals/USE, K8s terminationGracePeriod/preStop. Added to revision as clearly labelled additions. Ref: Google SRE Book (Embracing Risk; Monitoring Distributed Systems), prometheus.io docs, opentelemetry.io docs, kubernetes.io (Pod lifecycle - termination).
- [CLARIFY] Section 14: the example defines a Counter but the request-duration metric (histogram) mentioned in section 14 list is not implemented; percentiles require histograms/summaries.
- [CLARIFY] Section 28: idempotency here (client Idempotency-Key for HTTP) complements Ch15 (queue consumer idempotency); same principle, different mechanism.
- [CLARIFY] Graceful shutdown snippet is explicitly 'conceptual'; `server.close()` is not awaited in the sample.

## Ch23
- [CLARIFY] Section 11 ends with 'Earlier.' as a sentence fragment (editorial); no technical issue.
- [CLARIFY] Incident 2 uses `kubectl get endpointslices`; in older clusters `kubectl get endpoints` works too (see Ch20 note on Endpoints deprecation).
- [GAP] rollout undo scope (does not revert DB/config/infra) added to revision. Ref: kubernetes.io Deployments - Rolling back.
- [CLARIFY] The 'interview answer' in Part 20 describes EKS 'if Kubernetes is justified' consistent with the cost-thinking section (Part 17).

## Ch24
- [SUPERSEDED] The chapter closes with 'The roadmap is complete / 24/24' and lists ArgoCD, GitOps, Jenkins, Ansible, Service Mesh, Istio, Operators, CRDs as awareness-only topics. The source conversation continues with Responses 25-35, which cover these in depth (and later renumber the roadmap '/36'). Kept as historical statement; PROGRESS/README explain the extension.
- [CLARIFY] Section 3 Bash example uses `curl -fsS` (silent but shows errors) whereas Ch3 used `curl -fs ... > /dev/null`; both valid.
- [CLARIFY] Section 7 lists status 409 which Ch4's list did not include; explained in revision.
- [CLARIFY] Dockerfile in section 13 omits tsconfig/src copy splitting from Ch8; equivalent simplified version.
- [FORMAT] Trailing '24/24 complete' progress table and closing paragraph removed from the chapter (pure scaffolding).

## Ch25
- [GAP] `toYaml | nindent` not explained; precedence stated loosely; no mention of atomic/wait flags, hooks, helm test, release storage as Secrets, Helm 3 vs Tiller, secret-handling tools. Added to revision. Ref: helm.sh/docs (Values Files; Chart Template Guide; helm upgrade flags; Chart Hooks).
- [SECURITY] Install one-liner pipes a downloaded script to bash; prefer package manager/verify checksum. Source preserved.
- [VERSION-DRIFT] get-helm-3 script and Helm 3 assumptions; Helm 4 has been released. Verify current install docs.
- [CLARIFY] Section 29 says Helm generates Ingress/ConfigMap/HPA but the sample values.yaml does not define them; scaffolded `helm create` chart includes ingress/hpa toggles (disabled by default).
- [FORMAT] Response numbering switches to 'n/36' (extended roadmap: 25/36). Trailing roadmap progress (1674-1682) removed.

## Ch26
- [CORRECTION/PRECISION - IMPORTANT] Sections 25 and 37 (drift test) say that with automated sync ArgoCD 'can reconcile the cluster back'. `syncPolicy.automated: {}` alone does NOT revert manual changes; that requires `selfHeal: true` (and `prune: true` for deletions). Without it the app only shows OutOfSync. Source text preserved; precision added to revision and CORRECTIONS. Ref: Argo CD docs, Automated Sync Policy (argo-cd.readthedocs.io).
- [INCOMPLETE-EXAMPLE] Application YAML lacks `metadata.namespace: argocd` (Applications are normally created in the argocd namespace). Added to revision.
- [BACKREF-ERROR] Section 14: 'Remember Response 20? We learned that Kubernetes can be extended using CRDs.' CRDs are not covered in Ch20; they are the subject of Ch29 (the source itself says 'connects directly to Response 29 later'). Treat as a mistaken back-reference; no content in Ch20 was lost.
- [GAP] Initial admin password retrieval, server-side apply for large CRDs, Suspended health status, pull-vs-push security advantage, how CI updates the GitOps repo. Added to revision.
- [ROADMAP] Roadmap table at the end lists '36 Final DevOps Mastery' as pending; no such response exists in the source files (see PROGRESS).
- [VERSION-DRIFT] install.yaml from the `stable` branch URL changes over time.

## Ch27
- [GAP-FILLED] Parallel/parameters/when/input/options/triggers syntax, scripted vs declarative, multibranch pipelines, webhook endpoint, initial admin password: supplements/ch27.md (editorial). Ref: jenkins.io/doc (Pipeline Syntax; Using a Jenkinsfile; Managing Credentials).
- [PRACTICAL ISSUE] Section 40 runs jenkins/jenkins:lts which has no Docker CLI; the docker build/push pipelines in sections 17, 32, 42 will fail there unless the agent has Docker (or Docker Pipeline plugin is used). Docker-socket mounting is a security risk. Documented in supplement.
- [CLARIFY] Sections 17/32: `docker push my-api:${BUILD_NUMBER}` has no registry prefix, so it targets Docker Hub; source says production needs secure registry auth + immutable tags.
- [CLARIFY] Section 19 `kubectl set image deployment/my-api my-api=...` requires the container name to be `my-api`.
- [CLARIFY] Section 28: approvals only mentioned conceptually; `input` step shown in supplement.

## Ch28
- [CORRECTION] Sections 25-26: `vars: environment: production` and template `ENVIRONMENT={{ environment }}`. `environment` is an Ansible play/task keyword (sets environment variables); using it as a variable name conflicts with a reserved name (Ansible warns/errors depending on version). Use e.g. `app_env`. Source preserved verbatim. Ref: Ansible docs, 'Creating valid variable names' / Playbook Keywords.
- [GAP] Python requirement on managed nodes, ansible_user/key settings, dynamic inventory with Terraform-created EC2, vault commands, syntax-check/limit/lint, handler timing (end of play), copy vs synchronize, FQCN module names, NodeSource for current Node.js. Added to revision. Ref: docs.ansible.com (Intro to inventory; Handlers; ansible-vault).
- [CLARIFY] Section 20/43: `apt: name: nodejs` installs the distro's (often old) Node.js; real deployments typically use NodeSource or a version manager.
- [CLARIFY] Section 36: `command` vs `shell` description is accurate; `command` does not support shell operators (pipes, redirects).

## Ch29
- [TOOLING] Code fences use the form ```text id="..." (space-separated id attribute); build script strips ` id="..."` generally.
- [PRACTICAL ISSUE] Example CRD `shortNames: [app]` collides with Argo CD's Application CRD short name if both exist in the same cluster (Ch26 installs Argo CD in the same kind cluster). Documented in revision. Ref: argo-cd manifests (applications.argoproj.io shortNames: app, apps).
- [GAP] status subresource, ownerReferences/garbage collection, level-triggered reconcile, `kubectl explain`, CEL validation, danger of deleting a CRD. Added to revision. Ref: kubernetes.io/docs (Custom Resources; Extend the Kubernetes API with CustomResourceDefinitions; Finalizers; Garbage Collection).
- [CLARIFY] Section 19 is deliberately a layered-controller note: Deployment controller handles replica count; Operator handles app-specific logic.
- [CLARIFY] Section 26 `status.phase` is a convention, not a required field; conditions are the recommended pattern.

## Ch30
- [GAP-FILLED] Istio resources for mTLS (PeerAuthentication), authorization (AuthorizationPolicy), timeouts/retries (VirtualService), circuit breaking (DestinationRule connectionPool + outlierDetection) are not named in the source; plus Istio's default retry behaviour, iptables redirection, profiles, injection mechanisms, alternatives: supplements/ch30.md. Ref: istio.io/latest/docs (Traffic Management; Security; Install profiles; Ambient).
- [CLARIFY] Section 22 describes the circuit breaker as a CLOSED/OPEN/HALF-OPEN state machine (general pattern); Istio's implementation is connection-pool limits + outlier detection. Noted in supplement.
- [VERSION-DRIFT] `networking.istio.io/v1` is the current stable API version for newer Istio; older releases use v1beta1/v1alpha3. The demo profile is for learning only.
- [VERIFY] AWS App Mesh end-of-support announcement (supplement mentions as verify item).
- [CLARIFY] Section 23 lists load shedding but doesn't define it; defined in glossary.

## Ch31
- [GAP-FILLED] No concrete setup in the source: eksctl cluster creation, kubeconfig, IAM->RBAC mapping (access entries / aws-auth), IRSA ServiceAccount annotation + OIDC trust policy, Pod Identity association, ALB Ingress annotations, max-pods formula, endpoint access, control-plane log types, upgrade order, Fargate limits, Auto Mode, cost note: supplements/ch31.md. Ref: docs.aws.amazon.com/eks (Getting started; IAM roles for service accounts; EKS Pod Identity; Amazon VPC CNI - max pods; Cluster endpoint; Control plane logs; Update cluster).
- [VERIFY] EKS Auto Mode feature list/pricing; EKS control-plane hourly charge; extended-support pricing for old Kubernetes versions; access entries as current default authentication mode.
- [CLARIFY] Section 77 shows `kubectl get endpoints` with EndpointSlices as the modern alternative (Endpoints API being deprecated).
- [CLARIFY] Section 36 ECR authentication is described generically; worker node IAM role needs ECR read permissions (e.g. AmazonEC2ContainerRegistryReadOnly) and Pod Identity/IRSA can be used for other AWS access.
- [CLARIFY] Preamble 'Absolutely.' (line 3) is conversational; kept.

## Ch32
- [SELF-CORRECTION] Section 4 first shows a .gitignore that lists `.terraform.lock.hcl`, then immediately corrects it ('Actually, one nuance... Don't ignore .terraform.lock.hcl'). Final guidance (commit the lock file) agrees with Ch21 section 19. Both blocks preserved verbatim; the second is authoritative.
- [PLACEHOLDER] Section 55 `required_version = ">= 1.x, < 2.0"` is not valid syntax (placeholder); section 56 `source = "..."` and section 85 `for_each = { api = "..." }` are fragments. Complete forms in supplements/ch32.md.
- [GAP-FILLED] Complete S3 backend with use_lockfile, for_each/count, lifecycle caveat, import blocks and -generate-config-out, removed block, terraform_remote_state, command table, tooling: supplements/ch32.md. Ref: developer.hashicorp.com/terraform (S3 backend; lifecycle meta-argument; import; moved blocks; terraform test).
- [VERSION/VERIFY] `use_lockfile` (Terraform >= 1.10), import blocks (>= 1.5), `terraform test` (>= 1.6), `removed` block (>= 1.7): confirm against the Terraform version in use. `terraform refresh` is superseded by `apply -refresh-only`.
- [NUANCE] `prevent_destroy` does not protect if the whole resource block is removed from configuration.

## Ch33
- [GAP-FILLED] No concrete config in the source: ECS task definition (task role vs execution role), DynamoDB Query example/limits, Step Functions ASL with Retry/Catch, saga and outbox patterns, Aurora, SQS FIFO, Kinesis/MSK, API Gateway flavours: supplements/ch33.md. Ref: docs.aws.amazon.com (ECS task definition parameters; DynamoDB Developer Guide - best practices for designing and architecting; Step Functions - error handling; Amazon EventBridge; Microservices patterns - saga/outbox).
- [LIBRARY-SPECIFIC] Section 34: `redis.set(key, value, { EX: 300 })` is node-redis v4 syntax; ioredis uses positional arguments.
- [DUAL-WRITE] Section 50 (RDS write then publish OrderCreated) is a dual write; outbox pattern addresses it. Noted in supplement.
- [GAP] Section 89 lists 'stream?' as a workload type but no streaming service is covered; Kinesis/MSK noted.
- [CLARIFY] Section 70 decision matrix lists 'RDS/Aurora' without defining Aurora; defined in glossary/supplement.
- [CLARIFY] Section 100 'ECS Fargate vs Lambda' pairing: Fargate = containers, Lambda = functions; both serverless in terms of server management.
- [VERIFY] API Gateway integration timeout/payload quotas have changed over time.

## Ch34
- [VERIFIED-ARITHMETIC] Availability/downtime table (730-hour average month), Little's Law example (100 x 0.2 = 20), average latency example (149.5 ms), burn-rate example (1% / 0.1% = 10x), error budget example (1,000,000 x 0.1% = 1,000) are all arithmetically correct. Ch22 supplement-style note uses a 30-day month (43.2 min for 99.9%) - both valid; the supplement explains the difference.
- [CONSISTENT] SLA defined here as contractual commitment; Ch1 defined it as 'commitment/expectation'. Ch34 is the precise version (see Ch1 clarification).
- [GAP-FILLED] General formulas (allowed downtime, burn rate, composite availability, MTBF/MTTR), PromQL error ratio, runnable k6 script, token bucket code, golden signals/USE: supplements/ch34.md. Ref: Google SRE Book (Service Level Objectives; Monitoring Distributed Systems), Google SRE Workbook (Alerting on SLOs), k6.io docs.
- [VERIFY] The workbook's example multi-burn-rate thresholds (14.4x/1h, 6x/6h, 1x/3d) are given as examples only.
- [CLARIFY] Section 84 MTTR acronym ambiguity is acknowledged in the source (Recovery/Repair/Resolve).
- [CLARIFY] Sections 90/91 graceful-shutdown snippet awaits cleanup in the server.close callback; unhandled SIGINT and timeouts are not shown.

## Ch35
- [SCOPE-STATEMENT] The chapter says (line 3246): 'the capstone architecture is designed and specified here; the actual implementation will be done step-by-step rather than pretending it has already been built.' The source therefore contains a specification plus only fragments of code (Dockerfile, Deployment, Service, probes). A reference starter is provided under code-examples/capstone/ and is labelled as editorial, not source.
- [INCONSISTENCY] Section 5 repo uses pnpm workspaces (pnpm-workspace.yaml) but the Dockerfile in section 23 uses `COPY package*.json` + `npm ci`; section 23 also omits `prisma generate`. Also node:22-alpine vs the Ch8 advice to prefer Debian slim for native dependencies (Prisma needs OpenSSL/binaryTargets on Alpine).
- [GAP] Local SQS for Docker Compose (section 25-26 `SQS_QUEUE_URL=...`) is not specified; LocalStack/ElasticMQ is the usual answer. Queue-depth autoscaling (section 18 'HPA/KEDA-like') not specified.
- [MISSING-RESPONSE] The chapter promises Response 36 'Final Cloud + DevOps Mastery'; no such response exists in the provided files (file 36 is a different topic, Virtualization Internals, imported as Chapter 36; files 37-40 are empty). Documented in PROGRESS.
- [CLARIFY] Section 76 network diagram shows ALB twice (box drawing artefact). Section 3 and 97 diagrams are consistent in content.
- [CLARIFY] Section 94 resume wording is explicitly provisional ('wait until we've actually built it').

## Ch36
- [STRUCTURE] Found during the final audit (the first inventory had wrongly treated file 36 as empty): source file 36 contains a full response ("Virtualization Internals — Deep Dive", 58 sections, 2,006 lines). It has no `Response N/M` header and is not the "Response 36 — Final DevOps Mastery" that Chapter 35 promised. It was imported as Chapter 36 (domain: foundations; placed in Part II because it was produced after the capstone). Source files 37-40 are empty.
- [CLARIFY] §3: KVM is listed as a Type 1 example. KVM is a Linux kernel module that turns the host kernel into a hypervisor, so it is sometimes classified as Type 2 because a general-purpose host OS is present. The Type 1/Type 2 split is a teaching simplification; the source's "KVM-based virtualization environments" wording is acceptable. Ref: linux-kvm.org.
- [CLARIFY] §5/§6: the source's description of the "Ring 0 / Ring 3" model is the x86 view; VT-x/AMD-V add a separate root/non-root (host/guest) mode orthogonal to the rings, which is why a guest kernel can run in guest-mode Ring 0 without owning the machine. Not in the source; added in the supplement. Ref: Intel SDM Vol. 3C (VMX operation).
- [CLARIFY] §19: AMD's nested paging is also marketed as RVI (Rapid Virtualization Indexing); EPT/NPT are the names used in the source. Terminology only.
- [CLARIFY] §47-§49: the source says AWS EC2 is a virtual machine on AWS virtualization infrastructure and mentions Nitro; EC2 also offers bare-metal instance types where no hypervisor runs for the customer. Not in the source; added in the supplement as a reference item.
- [CLARIFY] §23: ballooning/§24 page sharing are classic features of some hypervisors (e.g. VMware); not every hypervisor or cloud provider overcommits memory, and public-cloud instances usually do not expose overcommit to the customer.
- [CLARIFY] §28: "A snapshot is not automatically a backup" is correct; point-in-time EBS snapshots are crash-consistent unless the application is quiesced (see Ch13/Ch33 backup notes).
- [VERIFY] The chapter is deliberately conceptual; no commands or configuration appear. Commands in the supplement (`lscpu`, `/proc/cpuinfo` flags, `systemd-detect-virt`, `unshare`, cgroup files) are standard Linux tooling but were not executed in the audit environment (Windows).
- [CONSISTENT] Container internals (§41-§46) agree with Chapter 7/8/18 (shared kernel, namespaces + cgroups, resource limits). The chapter closes with "SWE-level depth is enough" scope statements, preserved.
