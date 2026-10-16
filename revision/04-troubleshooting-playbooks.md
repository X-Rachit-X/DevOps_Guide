# Troubleshooting Playbooks

The source's consistent method: **don't restart blindly; go layer by layer, outside in, and use evidence** (metrics → logs → traces). Each playbook below consolidates the decision paths taught across chapters.

## 0. Universal method

```text
Confirm impact → check metrics → recent changes/deployments → logs → traces
→ identify the failing layer/dependency → mitigate (rollback/scale/fail over) → verify recovery → root cause → postmortem
```

## 1. "App on a server is unreachable" (Ch 2, 4, 10, 12)

1. Is the process running? `ps aux | grep node` / `docker ps`
2. Listening on the right port and address? `ss -tulpn | grep 3000` — `127.0.0.1` vs `0.0.0.0`
3. Works locally? `curl http://localhost:3000/health`
4. Docker: port published (`-p`)? logs (`docker logs`)?
5. Linux firewall → Security Group → NACL → route table → IGW/NAT → public IP
6. Load balancer: target health, listener, SG chain
7. DNS: `dig`, TTL/propagation
8. WAF blocking? TLS certificate?

## 2. HTTP error codes (Ch 4, 23, 31)

| Code | First suspects |
|---|---|
| 4xx | client/request, auth (401/403), 404 routing, 429 rate limit |
| 500 | application error → logs/traces; recent deploy; dependency (DB/Redis) |
| 502 | LB/proxy got invalid upstream response → target health, target port, SG, app logs |
| 503 | no healthy targets / Pods not Ready / Service has no endpoints / overload / readiness failing |
| 504 | upstream timeout → slow dependency (traces), timeouts mis-set |

## 3. AWS connectivity (Ch 12)

- **EC2 → RDS fails:** endpoint, port 5432, route tables, RDS SG allows source SG, NACL, DB running, credentials, pool.
- **Internet → EC2 fails:** running? listening on `0.0.0.0`? port? SG? route? IGW? public IP? NACL?
- **Private EC2 cannot reach the Internet:** route to NAT? NAT in a public subnet with IGW route? SG/NACL/DNS?
- **EC2 reaches Internet but Internet can't reach it:** public IP + route + IGW + SG + NACL + app listening (this is the intended behavior for private subnets).
- **`AccessDenied`:** `aws sts get-caller-identity` (wrong account/role?) → policy action/resource ARN → explicit deny → bucket policy → KMS permissions *(added)*.

## 4. Performance (Ch 10, 14, 34)

| Symptom | Check |
|---|---|
| CPU 100% | `top`; loop? traffic spike? inefficient code — diagnose before resizing |
| Memory | `free -h`; leak, too many processes, undersized |
| Disk full | `df -h`; logs, Docker images, temp files, data |
| Slow API, low API CPU, high DB CPU | DB bottleneck — scaling API won't help; queries, indexes, locks, pool |
| p95 up, CPU/mem normal | traces: slow dependency (Redis, DB, external API) |
| DB "too many connections" | instances × pool; connection leak; slow queries; RDS Proxy |
| Queue growing | producer vs consumer rate, queue age, failing consumers → scale consumers, DLQ poison messages |

## 5. Kubernetes (Ch 18–20, 23, 31)

```text
kubectl get pods → describe pod (Events) → logs [--previous] → exec → env/config/network/resources
```

| Status | Causes |
|---|---|
| **Pending** | insufficient CPU/memory, node selector, taints/tolerations, affinity, no nodes, **IP exhaustion (EKS)**, PVC unbound |
| **ImagePullBackOff / ErrImagePull** | wrong image/tag, registry auth/permissions, network |
| **CrashLoopBackOff** | app crash, missing env var/Secret, bad config, DB unavailable, wrong command, OOM |
| **Running but not Ready** | readiness probe path/port wrong, dependency down, slow startup |
| **Service has no traffic** | `kubectl get endpointslices` empty → selector ≠ Pod labels; port/targetPort mismatch |
| **HPA not scaling** | Metrics Server missing, no resource requests, wrong target, no load, `maxReplicas` reached |
| **PVC Pending** | no provisioner, wrong StorageClass, capacity, access-mode mismatch |
| **ConfigMap change ignored** | env vars don't update → `kubectl rollout restart` |
| **Secret not found** | wrong namespace (namespace-scoped) |
| **App can't call AWS** | ServiceAccount → Pod Identity/IRSA → role → policy; network/VPC endpoint |
| **CRD resource does nothing** | operator not running / RBAC denied / CRD missing |
| **Pod sidecar missing (Istio)** | namespace labelled after Pod creation → rollout restart |

## 6. Bad deployment (Ch 6, 23, 34)

Stop rollout → `kubectl rollout status` → compare v1/v2 logs, config, secrets, migrations → `kubectl rollout undo` (or Helm rollback / Git revert for GitOps) → verify error rate/latency → investigate. **Rollback is not always safe** (applied DB migrations, security fixes) → roll forward; prefer expand-and-contract migrations.

## 7. Pipelines and IaC (Ch 6, 21, 27, 32)

- **CI fails:** which stage? exit codes → lint/typecheck/test/build → credentials/registry.
- **Jenkins:** agent offline (network, process, disk, credentials), disk full (workspace, Docker images, artifacts, logs), push failed (ECR reachable? credentials? repo? tag?).
- **Terraform plan shows destroy:** stop; address change? immutable field? module refactor? → `moved` block / fix config. **Drift:** was the manual change intentional? **State lock stuck:** confirm nobody is applying, then `force-unlock` *(added)*.
- **ArgoCD OutOfSync:** repo, branch, path, rendered Helm/manifests, values, permissions, cluster access, resource conflict.
- **Ansible FAILED:** SSH (host/user/key/SG), `become`/sudo, wrong module/OS/package, `-vvv`; non-idempotent task if it keeps changing.

## 8. Incidents (Ch 34)

Detect → acknowledge → triage (SEV) → mitigate → recover → communicate → postmortem. **Mitigation before root cause.** Dependency questions: can it fail? what happens? retry? fallback? cache? queue? fail fast?

---
[← Revision index](README.md)
