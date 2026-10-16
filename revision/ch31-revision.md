# Chapter 31 — Revision Sheet: Advanced Amazon EKS

> Supplements [the full chapter](../docs/05-kubernetes/ch31-advanced-eks.md). EKS sits at the intersection of **AWS + VPC + IAM + Kubernetes + Docker + ECR + load balancing + storage + autoscaling + security + observability.**

## What EKS is

**EKS = Amazon Elastic Kubernetes Service**, AWS-managed Kubernetes. AWS manages much of the control plane (API server, etcd, scheduler, controller manager, control-plane upgrades/availability); **you manage** applications (Pods, Deployments, Services, Ingress, ConfigMaps, Secrets), node infrastructure/configuration, networking configuration, IAM integration, observability. EKS doesn't replace Kubernetes concepts — you still use `kubectl` and manifests; EKS = AWS-managed Kubernetes + deep AWS integration. Use it when you have e.g. 20 microservices needing recovery, scaling, rolling deployments, private networking, load balancing, IAM, persistent storage, observability, HA.

**Control plane:** API Server (auth → authorization → validation → store desired state → controllers reconcile), Scheduler, Controllers, **etcd** (cluster state: Deployments, Pods, Services, ConfigMaps, Secrets, CRDs, config). You don't SSH into control-plane machines or manage etcd.

## Compute options

| Option | Notes |
|---|---|
| **Managed Node Groups** | EC2 instances managed as a Kubernetes node group; important for most backends |
| **Self-managed nodes** | You manage more of the EC2 lifecycle; specialised needs, more operational work |
| **Fargate** | Pods on serverless compute, no EC2 nodes to manage |
| **Karpenter** | Dynamically provisions appropriate EC2 capacity from pending workload requirements |

Multi-AZ nodes survive an AZ failure better (if the app and dependencies are also designed for it).

## Networking

- Nodes in **private subnets** (reduce exposure) behind a public load balancer: Internet → IGW → public LB → private EKS nodes → Pods → private RDS. Private nodes still need outbound access (images, OS packages, AWS APIs, external APIs): NAT Gateway → IGW, or **VPC endpoints** for AWS service traffic.
- **CNI** (Container Network Interface) = standard interface for container networking; **Amazon VPC CNI** connects Pods to the VPC: ENIs/IP allocation → Pods can get VPC-routable IPs. Pod flow: scheduled → VPC CNI → allocate IP → configure networking → Pod gets identity.
- **Pod IP capacity:** `kubectl scale deployment api --replicas=100` → Pods `Pending` because of insufficient IPs. Subnet IP capacity and node networking limits (ENIs, IPs per ENI, bandwidth differ per instance type) constrain scaling → **VPC CIDR planning matters**; "bigger node ≠ only more CPU/RAM". IP exhaustion is a real production failure mode (secondary CIDR/larger Pod address space).
- **Security groups** (Internet → ALB SG :443 → EKS app → RDS :5432) and **Pod-level security groups** (e.g. Payment Pod with its own SG). **NetworkPolicy** (Pod A → Pod B allowed?) vs **AWS Security Group** (AWS network layer) — complementary.

## IAM for Pods (very high-yield)

Never put `AWS_ACCESS_KEY_ID/SECRET` in containers. Use workload identity:

- **IRSA** (IAM Roles for Service Accounts) — older pattern, know well. **EKS Pod Identity** — newer EKS-native approach, know well. Flow: Pod → Kubernetes ServiceAccount → (IRSA / Pod Identity association) → IAM Role → temporary AWS credentials → AWS API. App just uses the AWS SDK.
- ServiceAccount example: `kind: ServiceAccount, name: backend-sa, namespace: production`; Deployment `spec.template.spec.serviceAccountName: backend-sa`.
- Least-privilege policy example: `s3:GetObject` on `arn:aws:s3:::my-company-assets/*`.
- **Node IAM role vs Pod identity:** node role = broad permissions to everything on the EC2 node (dangerous if every Pod inherits them); Pod identity = per-workload (Pod A → S3 read, Pod B → SQS send, Pod C → Secrets Manager read). Example: User Service → DynamoDB; Image Service → S3; Payment Service → Secrets Manager — never `AdministratorAccess` for all three.
- **IAM vs Kubernetes RBAC:** IAM controls AWS resources (S3, SQS, DynamoDB, Secrets Manager, ECR) — "Can this workload access AWS?"; RBAC controls Kubernetes API resources (Pods, Deployments, Services, Secrets, ConfigMaps) — "Can this identity perform this Kubernetes API action?" (User → Role/ClusterRole → RoleBinding → API; workloads: ServiceAccount → RBAC permissions).

## ECR, load balancing, storage

- **ECR + EKS:** Developer → Git → GitHub Actions → Docker build → ECR → EKS → Pod; image `<account>.dkr.ecr.<region>.amazonaws.com/backend:<tag>`; use immutable tags (`backend:a82f31c` = Git SHA, not `latest`). `ImagePullBackOff` → `kubectl describe pod` → wrong image/tag, ECR permissions, network, registry issue.
- **AWS Load Balancer Controller:** Ingress → ALB; certain Services → NLB; reconciles AWS infrastructure from Kubernetes resources (desired state → controller → actual infrastructure — compare Ch.29). **ALB** = Layer 7 (HTTP/HTTPS, host, path, headers); **NLB** = Layer 4 (TCP/TLS, high performance). **Target type:** *instance* (ALB → Node → Service → Pod) vs *IP* (ALB → Pod IP; skips a hop; common in modern EKS).
- **EBS CSI driver:** Pod → PVC → PV → EBS volume; EBS volumes are **AZ-bound** (Pod rescheduled to another AZ → attachment/scheduling constraints). **EFS:** managed network file system shared across AZs/Pods. Don't blindly put a database on EFS — prefer RDS. **StorageClass → CSI driver → AWS storage.** **CSI** = Container Storage Interface (EBS CSI, EFS CSI).

## Autoscaling

HPA = number of Pods; node autoscaling = compute capacity. Flow: traffic ↑ → CPU ↑ → HPA more replicas → Pods Pending → **Karpenter/Cluster Autoscaler** provisions nodes → Pods schedule. **Cluster Autoscaler** primarily scales existing node groups (pending Pods → increase node group → new EC2); **Karpenter** dynamically provisions appropriate capacity (e.g. a Pod needing 8 CPU / 32 GB gets suitable capacity). **Resource requests** drive scheduling (node capacity + Pod requests); bad requests → overprovisioning, underprovisioning, Pending Pods, poor autoscaling.

## Security layers (defense in depth)

IAM (Pod identity → AWS permissions), Network (SG/NACL, NetworkPolicy), Kubernetes (RBAC, ServiceAccounts), secrets, encryption, image security, pod security, audit logs. Secrets: don't commit real secrets; AWS Secrets Manager → External Secrets/workload integration → Kubernetes Secret → Pod. Encryption: TLS (in transit) + encryption at rest (KMS-backed where supported). **Pod security:** `securityContext: runAsNonRoot: true`, read-only filesystem where possible, drop unnecessary capabilities, resource limits, seccomp. **Image security:** dependency scanning, image scanning, minimal images, non-root, signed/verified artifacts where appropriate, immutable tags, least privilege.

## Observability

Monitor cluster (node availability, API server health, capacity), node (CPU, memory, disk, network), Pod (restarts, CPU, memory, readiness, liveness), application (request rate, error rate, latency), AWS (ALB, RDS, EBS, NAT Gateway, S3). Structured logs with `requestId`/`service`; tracing example Order 50 ms, Payment 400 ms, DB 350 ms. **Control-plane logs** can go to CloudWatch Logs (API requests, authentication, authorization, audit, scheduler/controller); check current AWS docs for categories.

## Upgrades, add-ons, DNS

Upgrade process: check compatibility → check deprecated APIs → upgrade test environment → control plane → add-ons → nodes → validate workloads. Deprecated APIs (Ingress, CRDs, operators, admission controllers) can break deployments. **Add-ons:** VPC CNI, CoreDNS, kube-proxy, EBS CSI driver (some managed as EKS add-ons; compatibility matters). **CoreDNS** gives `payment.default.svc.cluster.local`; DNS failure makes services look unreachable even with healthy Pods.

## Troubleshooting a 503 (outside in)

Load balancer (healthy? listeners? target groups? SGs?) → Ingress (`kubectl get/describe ingress`: host, path, backend, events) → Service (ports, targetPort, selector) → Endpoints/EndpointSlices (none ⇒ selector mismatch) → Pods (`get pods -o wide`: Pending/CrashLoopBackOff/ImagePullBackOff/Running-not-Ready) → `describe pod` (Events) → `logs` (`--previous`, `-c <container>`) → Node (`describe node`: CPU/memory/disk pressure, taints, capacity, allocatable) → Networking (DNS, route, SG, NetworkPolicy, port 5432, RDS availability) → IAM (ServiceAccount → Pod identity/IRSA → IAM role → policy; don't modify the node role).

| Classic failure | Checks |
|---|---|
| **Pods Pending** | CPU/memory, node selector, taints/tolerations, affinity, no available nodes, **IP exhaustion**, PVC problems |
| **ImagePullBackOff** | image name, tag, ECR permissions, network, registry |
| **CrashLoopBackOff** | logs/`--previous`; bad env var, app crash, wrong command, DB unavailable, missing Secret, bad config |
| **App can't access S3** | ServiceAccount → Pod Identity → IAM role → S3 policy → bucket policy; VPC endpoint/NAT |
| **Pods can't communicate** | Service, Endpoints, DNS, NetworkPolicy, SGs, CNI, ports |
| **Pods can't get IPs** | VPC CNI → subnet IP capacity → ENI/IP limits |

## Architecture, flows, cost

- Production: Internet → Route 53 → CloudFront → WAF → AWS Load Balancer → AZ-a/AZ-b EKS nodes (Pods) → private RDS/Redis/S3/SQS. Terraform provisions AWS; GitHub Actions → Docker → ECR; ArgoCD → EKS; Helm packages apps.
- **Request flow (`GET /orders/123`):** Route 53 → CloudFront/WAF → load balancer → AWS integration routes to EKS workload → Service → Pod → app → RDS/Redis/S3/SQS (private networking + IAM) → metrics/logs/traces emitted.
- **Deployment flow:** `git push` → Actions (lint, typecheck, test, build, security checks) → Docker build → ECR push → GitOps repo image tag update → ArgoCD → EKS Deployment update → rolling update → new Pods.
- **Terraform provisions:** VPC, subnets, IAM, EKS, node groups, SGs, RDS, S3, Redis, load-balancing infra; Kubernetes/Helm/ArgoCD manage workloads. EKS + Operators (PostgreSQL Operator → Postgres CR) and EKS + Istio (Envoy) work as in Ch.29/30.
- **Cost:** EKS control-plane charges, EC2, EBS, load balancers, NAT Gateway, data transfer, CloudWatch, ECR, RDS, ElastiCache; bad designs (many NAT Gateways + cross-AZ traffic + oversized EC2 + unused load balancers + unbounded logging) get expensive. **Availability vs cost:** 1 node cheaper vs 3 AZs multi-node fault tolerance — explain trade-offs (cost, availability, performance, operational complexity), not "always use three AZs".

## Checklists

Security: private nodes where appropriate, least-privilege IAM, Pod identity, RBAC, NetworkPolicies, SGs, Secrets Manager, encryption, non-root containers, image scanning, resource limits, audit/control-plane logging, regular upgrades, restricted API access, minimal permissions. Production: Networking (multi-AZ, private subnets, CIDR planning, VPC CNI, IP capacity), Compute (managed node groups, autoscaling, requests, instance sizing), Security (IAM, Pod Identity, RBAC, Secrets, NetworkPolicy), Deployment (ECR, immutable tags, Helm, ArgoCD, rolling), Observability (logs, metrics, traces, alerts).

## Interview answers (12)

EKS (AWS-managed Kubernetes integrated with AWS infrastructure/services) · why EKS (reduced control-plane burden + AWS networking/IAM/LB/storage integration) · VPC CNI · why Pods run out of IPs (subnet address space + networking/instance limits: enough CPU but cannot allocate IPs) · Pod → S3 securely (Pod Identity or IRSA, least-privilege role) · IAM vs RBAC · exposing an app (Internet → AWS LB → Service → Pods) · HPA vs node autoscaling · Cluster Autoscaler vs Karpenter · EBS vs EFS (block/AZ vs shared FS/multi-AZ) · private nodes (limit exposure; only LB entry points) · debug a 503.

**Depth:** 🔥 EKS architecture, EKS + VPC, subnets, VPC CNI, Pod IP allocation, IAM, Pod Identity/IRSA, ECR, AWS LB Controller, Services, Ingress, HPA, node scaling, EBS/EFS, RBAC, NetworkPolicy, troubleshooting · 🟡 Managed Node Groups, Fargate, Karpenter, CSI, control-plane logging, upgrades, add-ons, Pod-level SGs · ⚪ control-plane internals, custom CNI, Karpenter internals, kernel networking, scheduler implementation, etcd internals.

## Added (see supplement in the chapter)

`eksctl` cluster config + `aws eks update-kubeconfig`; IAM→RBAC mapping via **access entries**/`aws-auth`; IRSA annotation + OIDC trust policy; Pod Identity association command + trust principal `pods.eks.amazonaws.com`; ALB Ingress annotations; **max-Pods formula** `ENIs × (IPs per ENI − 1) + 2` (m5.large = 29); endpoint access, log types, upgrade order, Fargate limits, Auto Mode, cost note.

<!-- NAV -->

---

← [Sheet 30](ch30-revision.md) · [Full chapter 31](../docs/05-kubernetes/ch31-advanced-eks.md) · [All revision material](README.md) · [Sheet 32](ch32-revision.md) →
