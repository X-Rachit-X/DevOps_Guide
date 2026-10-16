# Traps and Misconceptions

The "X ≠ Y" distinctions and common wrong answers flagged across the chapters (Chapter 24 lists the OA/MCQ set). *(added)* = editorial.

## High-value "not the same" list (Ch 24)

Image ≠ Container · Pod ≠ Container · Multi-AZ ≠ Read replica · Private subnet ≠ no Internet access · Authentication ≠ Authorization ·
S3 ≠ EBS · Horizontal ≠ Vertical scaling · Continuous Delivery ≠ Continuous Deployment · Logs ≠ Metrics ≠ Traces · Terraform state ≠ configuration ·
**Running ≠ Ready** · HPA ≠ node autoscaling · Base64 ≠ encryption (Ch 19) · Public IP ≠ permission to connect (Ch 10) ·
Managed service ≠ zero responsibility (Ch 13) · Availability ≠ Reliability (Ch 1).

## Wrong-but-tempting statements

| Wrong | Better |
|---|---|
| "A branch is a copy of the project." | A branch is a movable pointer to a commit (5) |
| "Deleting the commit fixes the leaked password." | Rotate/revoke first; deleted history may have been copied (5) |
| "`.gitignore` removes a file already committed." | It only affects untracked files (5) |
| "TCP is faster than UDP." | Different trade-offs; oversimplification (24) |
| "`EXPOSE` publishes the port." | Only documents; use `-p` (7) |
| "Smaller image (Alpine) is always better." | musl libc can break native deps; slim is a safe default (8) |
| "A container is a tiny VM." | Isolated process sharing the host kernel (7) |
| "`depends_on` waits until the DB is ready." | Start order only; need health checks + retry logic (8) |
| "Scaling the API scales the system." | The database/connection limit is often the bottleneck (13, 14, 22, 35) |
| "Auto Scaling means infinite scaling." | Bounded by max capacity and other bottlenecks (14) |
| "Make the S3 bucket public for simplicity." | Keep private; presigned URLs (11) |
| "Queues deliver exactly once." | Assume duplicates → idempotency (15, 33) |
| "NAT lets the Internet reach private EC2." | NAT is outbound-only (12) |
| "Kubernetes Secrets are encrypted." | Base64 unless encryption at rest is enabled (19) |
| "Kubernetes requires Docker Engine." | It needs a CRI runtime such as containerd (18) |
| "Ingress routes traffic by itself." | An Ingress Controller implements it (20) |
| "HPA creates machines." | HPA creates Pods; node autoscaling adds nodes (20) |
| "Pod = container." | Pod is the unit that may contain several (18) |
| "Namespaces isolate network traffic." | Not by default — NetworkPolicy *(added)* (18, 20) |
| "A CRD makes Kubernetes do something." | Only a controller/operator implements behaviour (29) |
| "Helm manages secrets." | It is not a secret-management solution (25) |
| "GitOps replaces CI/CD." | It is an approach to CD; CI still builds (26) |
| "`automated` sync reverts manual drift." | Only with `selfHeal: true` (verified) (26) |
| "Service mesh is needed with Kubernetes." | Often unnecessary; overhead (30) |
| "Retries make systems reliable." | Unbounded retries cause retry storms (22, 34) |
| "NoSQL = no transactions / faster." | DynamoDB has transactions; choose by access pattern (33) |
| "Terraform `sensitive` secures the value." | Hides it in output; still in state (21, 32) |
| "`terraform state rm` deletes the resource." | Only stops tracking (32) |
| "Average latency is enough." | Use percentiles; tail latency matters (22, 34) |
| "100% reliability is the goal." | SLOs and error budgets balance reliability with change (34) |
| "Untested backups are fine." | They are assumptions until a restore is tested (34) |
| "Rollback is always right." | Applied migrations / security fixes may require roll-forward (23, 34) |
| "Alert on every metric." | Alert on actionable, user-impacting conditions (22, 34) |
| "`ps aux | grep node | wc -l` counts node processes." | Also counts the grep itself *(added)* (3) |
| "`kubectl rollout undo` reverts the whole release." | Only the Deployment template; not DB/config/infra *(added)* (23) |

## Security reflexes

- Never commit or bake credentials (Git, Docker image, Dockerfile `ENV`, Terraform files, tfvars, Helm `values.yaml`, Jenkinsfile).
- Never log secrets, tokens, DB URLs.
- Roles + temporary credentials over long-lived keys; OIDC for CI.
- Least privilege everywhere (IAM, SGs, RBAC, Pod identity, CI roles); private subnets for DB/app; only expose what must be exposed.
- State files and CI servers are crown jewels — protect them.

---
[← Revision index](README.md)
