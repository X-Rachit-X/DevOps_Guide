# Comparisons — Every "X vs Y"

Source chapters in brackets. These are the highest-yield interview and OA distinctions.

## Cloud and architecture basics

| X | Y | Difference | Ch |
|---|---|---|---|
| Scalability | Elasticity | Can it grow vs does it grow **and shrink automatically** | 1 |
| Vertical scaling | Horizontal scaling | Bigger machine vs more machines (needs stateless apps) | 1, 14 |
| Availability | Reliability | Reachable vs behaves correctly consistently | 1, 34 |
| High availability | Fault tolerance | Redundancy keeps service up vs system keeps operating correctly through failure | 1 |
| RTO | RPO | Time to restore vs data-loss window | 1, 34 |
| IaaS / PaaS / SaaS | | Give me a computer / a platform / the software | 1 |
| Region | Availability Zone | Geographic area vs isolated location inside it | 1, 9 |
| Multi-AZ | Multi-Region | AZ failure (first HA layer) vs regional failure (much more complex) | 34 |
| Stateless | Stateful | Any instance serves any request vs local state breaks scaling | 14, 19 |
| Sync | Async | Client waits vs queue + worker | 15, 35 |
| Command | Event | "Do this" vs "this happened" | 33 |

## Linux / Bash / Git

| X | Y | Difference | Ch |
|---|---|---|---|
| `/` | `/root` | Filesystem root vs root user's home | 2 |
| `>` | `>>` | Overwrite vs append | 2, 3 |
| SIGTERM | SIGKILL | Graceful request (catchable) vs forced kill | 2 |
| Process | Program | Running instance vs file | 2 |
| Git | GitHub | Local DVCS vs hosting + collaboration | 5 |
| Merge | Rebase | Preserve branching history vs rewrite into linear history | 5 |
| Fast-forward | Three-way merge | Pointer move vs merge commit | 5 |
| Reset | Revert | Move/rewrite history vs new commit that undoes | 5 |
| `fetch` | `pull` | Download only vs fetch + integrate | 5 |
| Bash | Python | System automation vs complex logic/data | 3 |

## Networking

| X | Y | Difference | Ch |
|---|---|---|---|
| TCP | UDP | Reliable ordered connection vs connectionless low overhead (HTTP/3 uses QUIC over UDP) | 4 |
| Public subnet | Private subnet | Route to IGW vs no direct inbound route (private still has outbound via NAT) | 4, 12 |
| Security Group | NACL | Stateful, resource-level, allow rules vs stateless, subnet-level, allow+deny | 4, 12 |
| Security Group | WAF | Network access vs HTTP request filtering | 16 |
| Forward proxy | Reverse proxy | Acts for clients vs for servers | 4 |
| CNAME | Alias (Route 53) | Name → name (not at apex) vs AWS-resource target incl. apex *(added)* | 4, 16 |
| Route 53 | CloudFront | DNS vs CDN | 16 |
| CloudFront | ALB | Edge caching/CDN vs load balancing/target routing | 16 |
| ALB | NLB | Layer 7 HTTP vs Layer 4 TCP/TLS | 14, 31 |
| ALB | API Gateway | HTTP load balancing vs API management/entry layer | 33 |
| Load balancer | Reverse proxy | Overlapping; ALB = LB + app-level routing | 14 |

## Containers and CI/CD

| X | Y | Difference | Ch |
|---|---|---|---|
| Image | Container | Immutable template vs running instance | 7 |
| Container | VM | Shared kernel vs guest OS | 1, 7, 36 |
| Type 1 hypervisor | Type 2 hypervisor | Runs on hardware vs runs as an app on a host OS | 36 |
| Full emulation | Paravirtualization (VirtIO) | Pretend hardware vs virtualization-aware driver | 36 |
| Paravirtualization | Hardware passthrough / SR-IOV | Shared virtual device vs device (or virtual function) given to the VM | 36 |
| Shadow page tables | Nested paging (EPT/NPT) | Software-maintained mapping vs hardware second-level translation | 36 |
| Snapshot | Live migration | State capture for restore vs moving a running VM | 36 |
| Namespaces | cgroups | What a process can see vs how much it can use | 36 |
| `RUN` | `CMD` | Build time vs container start | 7 |
| `CMD` | `ENTRYPOINT` | Default overridable command vs always-run executable *(supplement)* | 8 |
| `EXPOSE` | `-p` | Documents vs publishes | 7 |
| Volume | Bind mount | Docker-managed vs host path | 7 |
| Docker | Kubernetes | Build/run containers vs orchestrate | 7, 18 |
| Docker Compose | Kubernetes | Local multi-container vs production orchestration | 18 |
| Liveness | Readiness | Restart vs receive traffic (startup probe for slow starts) | 8, 19 |
| Continuous Delivery | Continuous Deployment | Approval gate vs automatic | 1, 6 |
| `npm install` | `npm ci` | Resolve vs exact lockfile install | 6 |
| Rolling | Blue-green | Gradual replacement vs two environments + switch | 6 |
| Blue-green | Canary | Switch all traffic vs small % first | 6 |
| Recreate | Rolling | Downtime vs gradual | 6 |
| Jenkins | GitHub Actions | Self-managed extensible server vs GitHub-integrated | 27 |
| GitHub Actions | ArgoCD | CI vs Kubernetes GitOps CD | 26 |

## AWS

| X | Y | Difference | Ch |
|---|---|---|---|
| IAM user | IAM role | Persistent identity vs assumable, temporary credentials | 9 |
| Authentication | Authorization | Who vs what | 9 |
| AMI | Instance | Template vs running VM | 10 |
| Stop | Terminate | Restartable vs deleted | 10 |
| EBS | S3 | Block vs object | 11 |
| S3 / EBS / EFS | | Object / block / shared filesystem | 11, 33 |
| IAM policy | Bucket policy | Identity-based vs resource-based | 11 |
| SSE-S3 | SSE-KMS | AWS-managed keys vs KMS-controlled | 11 |
| Durability | Availability | Not lost vs accessible | 11 |
| RDS | DB on EC2 | Managed (less control) vs self-managed | 13 |
| Multi-AZ | Read replica | Failover/HA vs read scaling (replication lag) | 13 |
| Backup | Snapshot | Continuous recovery capability vs explicit point-in-time copy | 13 |
| RDS | DynamoDB | Relational vs key-value/document by access pattern | 13, 33 |
| Lambda | EC2 | Event-driven functions vs long-running servers | 15 |
| SQS | SNS | Queue vs pub/sub fan-out | 15, 33 |
| SNS | EventBridge | Fan-out vs event bus with rule routing | 33 |
| CloudWatch | CloudTrail | Monitoring vs API audit | 17 |
| Secrets Manager | Parameter Store | Secrets + rotation vs configuration | 17, 33 |
| Secrets Manager | KMS | Store secrets vs manage keys | 33 |
| ECS | EKS | AWS-native vs Kubernetes | 33 |
| ECS Fargate | Lambda | Container long-running vs function | 33 |
| Task role | Task execution role | App permissions vs ECS permissions *(supplement)* | 33 |
| IRSA | Pod Identity | OIDC-annotation approach vs EKS-native association | 31 |
| Node IAM role | Pod identity | Broad to every Pod vs per-workload | 31 |
| IAM | Kubernetes RBAC | AWS resources vs Kubernetes API | 31 |
| Cluster Autoscaler | Karpenter | Scales node groups vs provisions fitting capacity | 20, 31 |
| EBS | EFS (Kubernetes) | AZ-bound block vs shared multi-AZ filesystem | 19, 31 |
| Instance target | IP target (ALB) | Via node vs direct to Pod | 20, 31 |

## Kubernetes

| X | Y | Difference | Ch |
|---|---|---|---|
| Pod | Container | Wrapper with shared network/volumes vs process | 18 |
| Deployment | Bare Pod | Maintains replicas vs one-off | 18 |
| ConfigMap | Secret | Config vs sensitive (base64 ≠ encryption) | 19 |
| `emptyDir` | PVC | Pod-lifetime vs persistent | 19 |
| PV | PVC | Storage resource vs request for it | 19 |
| Requests | Limits | Scheduling reservation vs ceiling | 19 |
| ClusterIP / NodePort / LoadBalancer | | Internal / node port / cloud LB | 18, 20 |
| Ingress | Ingress Controller | Rules vs implementation | 20 |
| NetworkPolicy | Security Group | Pod traffic rules vs AWS network rules | 20, 31 |
| HPA | Node autoscaling | Pods vs nodes | 20, 31 |
| Pod IP | Service | Ephemeral vs stable endpoint | 18 |
| CRD | Custom Resource | Type vs instance | 29 |
| CRD | Operator | API type vs controller implementing it | 29 |
| Helm | Operator | Install/package vs continuously manage | 29 |
| Controller | Operator | General reconcile loop vs app-specific | 29 |
| Helm | kubectl | Release management vs raw resources | 25 |
| Helm | Terraform | K8s apps vs infrastructure | 25 |
| Chart | Release | Package vs installed instance | 25 |
| Service mesh | K8s Service | Advanced traffic/security/telemetry vs basic discovery | 30 |
| Service mesh | API Gateway | Service↔service vs external→internal | 30 |
| Control plane | Data plane | Configures proxies vs carries traffic | 30 |
| VirtualService | DestinationRule | Routing rules vs destination subsets/policies | 30 |
| Sidecar | Ambient mesh | Per-Pod proxy vs sidecar-less | 30 |

## IaC, config and GitOps

| X | Y | Difference | Ch |
|---|---|---|---|
| Terraform | Ansible | Provision vs configure | 21, 28 |
| Terraform | CloudFormation | Multi-cloud vs AWS-native | 21 |
| Terraform | Docker/Kubernetes | Infra vs packaging vs orchestration | 21 |
| `resource` | `data` | Manage vs read | 21, 32 |
| Terraform state | Configuration | What exists vs what you declared | 24, 32 |
| `count` | `for_each` | Positional vs keyed | 32 |
| Workspaces | Separate states | Same config/state instances vs explicit boundaries | 21, 32 |
| `state rm` | `destroy` | Stop tracking vs delete real resource | 32 |
| `import` | configuration | Adopt into state vs write the code | 32 |
| GitOps | CI/CD | A CD model, not a replacement | 26 |
| ArgoCD | Helm | Sync from Git vs templating | 26 |
| `command` | `shell` (Ansible) | No shell vs shell features; prefer modules | 28 |
| Ansible | Bash | Declarative idempotent vs imperative loops | 28 |
| Ansible | Kubernetes | Server config vs container orchestration | 28 |

## Observability / SRE

| X | Y | Difference | Ch |
|---|---|---|---|
| Logs / Metrics / Traces | | What happened / how much / where time went | 22 |
| Monitoring | Observability | Is it wrong vs why | 22, 34 |
| Prometheus | Grafana | Collect/store/query vs visualise | 22 |
| SLI / SLO / SLA | | Measurement / target / contractual commitment | 22, 34 |
| Average | Percentile | Hides tail vs reveals it | 22, 34 |
| Retry | Retry storm | Recover transient failures vs amplify overload | 22, 34 |
| Mitigation | Root cause | Stop damage vs understand why | 34 |
| Rollback | Roll forward | Revert vs fix-forward (migrations!) | 23, 34 |
| Fail open | Fail closed | Availability-first vs deny-by-default | 34 |
| Load / stress / spike / soak test | | Expected / beyond / sudden / long | 34 |
| Backup & restore / Pilot light / Warm standby / Active-active | | Cheapest-slowest → most expensive-fastest | 34 |
| Rate limiting | Load shedding | Per-client cap vs system-protecting rejection | 22, 34 |

---
[← Revision index](README.md)
