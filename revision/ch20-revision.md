# Chapter 20 — Revision Sheet: Kubernetes Networking + Scaling + Production

> Supplements [the full chapter](../docs/05-kubernetes/ch20-kubernetes-networking-scaling.md). Goal: understand **how traffic enters the cluster, reaches Pods, how Pods communicate, scale, and how failures/deployments are handled.**

## Request path and discovery

`Internet → Load Balancer → Ingress → Service → Pods → RDS/Redis`.

- **Pod-to-Pod** traffic works via cluster networking, but Pod IPs are ephemeral → don't hard-code (`10.x.x.2`); use a **Service**.
- **Service discovery:** create a Service (`name: redis`, selector `app: redis`, port 6379/targetPort 6379) and the API connects to `redis:6379`. `const redisHost = process.env.REDIS_HOST ?? "redis";`
- **Kubernetes DNS:** `redis` → cluster DNS → Redis Service IP → Redis Pods. Same namespace: `redis`. Cross-namespace: `redis.production` (a fuller service DNS structure exists). Service names give stable discovery as Pods change.

## Service types

| Type | Use |
|---|---|
| **ClusterIP** (default) | Inside the cluster: API → Redis, internal worker/service |
| **NodePort** | `NodeIP:NodePort → Service → Pods`; learning/certain scenarios, not preferred for production Internet-facing |
| **LoadBalancer** | Cloud integration provisions an external LB → Service → Pods |

## Ingress

- **Ingress** = HTTP/HTTPS routing rules into the cluster, so you don't need one public LB per service. **Host-based:** `api.example.com → API Service`, `admin.example.com → Admin Service`. **Path-based:** `example.com/api → API Service`, `example.com/admin → Admin Service`.
- **Ingress ≠ the implementation.** You need an **Ingress Controller** (NGINX, AWS Load Balancer Controller, Traefik). *Ingress = routing configuration; Ingress Controller = implements it.* (Frequently asked.) On EKS the AWS Load Balancer Controller integrates AWS load balancers with Services/Ingress.
- EKS production flow: Route 53 → CloudFront → WAF → AWS Load Balancer → EKS cluster (Node/Pod ×3) → RDS PostgreSQL → Redis.

## NetworkPolicy

Security Groups protect AWS network interfaces; **NetworkPolicy** controls Pod traffic (when the cluster networking implementation enforces it). Example: Frontend → API → Database allowed; Frontend → Database blocked. Defense in depth.
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-api-to-db }
spec:
  podSelector: { matchLabels: { app: database } }
  policyTypes: [Ingress]
  ingress:
    - from:
        - podSelector: { matchLabels: { app: api } }
```

## Readiness + load balancing

Pod B starting (A, C healthy) → readiness fails → not ready → Service doesn't route normal traffic; passes → eligible. Critical in deployments: without readiness, new Pod gets traffic before the app is ready → failed requests.

## Scaling

**HPA (Horizontal Pod Autoscaler):** metrics → HPA → desired replicas → Deployment → more/fewer Pods.
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: api-hpa }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: api }
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: { type: Utilization, averageUtilization: 60 }
```
- Needs **Metrics Server** for resource metrics; otherwise HPA has no useful metrics.
- HPA uses CPU/memory **relative to the configured resource requests** (so requests matter beyond scheduling — Ch.19).
- **HPA creates Pods, not machines.** Not enough node capacity → **node/cluster autoscaling** adds worker nodes (EKS: Managed Node Groups, **Karpenter**). *Pod scaling ≠ node scaling.* Traffic ↑ → HPA → more Pods → no capacity → more Nodes.

## Rolling deployments & rollout commands

v1 v1 v1 → v2 v1 v1 → v2 v2 v1 → v2 v2 v2 (readiness probes + Service + Deployment strategy cooperate).
```bash
kubectl rollout status  deployment/api
kubectl rollout history deployment/api
kubectl rollout undo    deployment/api
kubectl rollout restart deployment/api
```

## Other workload objects (awareness)

- **PodDisruptionBudget (PDB):** limit voluntary disruptions (e.g. node maintenance) so a level of availability is maintained (don't go 3 → 0).
- **Job / CronJob:** one-off or scheduled tasks (database cleanup, report generation, batch processing, scheduled sync): CronJob → Job → Pod → task.
- **DaemonSet:** a Pod on each (matching) node — log collection, node monitoring, network agents.

## Security & logging

- No AWS access keys in code/images. On EKS use **workload identity**: Pod → AWS workload identity → IAM permissions → AWS service (e.g. API needs S3 → IAM-based identity, not `AWS_ACCESS_KEY_ID` baked into Docker). *Give workloads identities and least-privilege permissions instead of permanent AWS keys inside Pods.*
- **Logging:** write JSON to stdout; `kubectl logs <pod>`; production centralises: Pod → stdout → logging agent → central logging (Ch.22).

## Troubleshooting scenarios (high-yield)

| Symptom | Investigate |
|---|---|
| **Pending** | `kubectl describe pod` → Events: insufficient CPU/memory, node selector mismatch, taints/tolerations, PVC issue, scheduling constraints |
| **CrashLoopBackOff** | `kubectl logs <pod>`, `kubectl logs <pod> --previous`, `describe`; app crash, missing env var, bad config, DB connection failure, wrong command, failed startup |
| **ImagePullBackOff** | wrong image name/tag, private-registry auth, image doesn't exist, registry unavailable (pipeline: Actions → Docker build → ECR → K8s → Pod) |
| **Service has no traffic** | `kubectl get svc`, `kubectl get endpoints` (or `endpointslices`), `describe service` — **selector/label mismatch** (`app: api` vs Pod `app: backend`) |
| **Port mismatch** | Service `targetPort: 3000` but Node listens on 8080 → connection failure |
| **Readiness failing** | wrong path/port, app not ready, DB dependency down, slow startup — understand *why*, don't just raise timeouts |
| **HPA doesn't scale** | `kubectl get hpa`, `describe hpa api-hpa`; Metrics Server unavailable, resource requests missing, wrong target, no load, `maxReplicas` reached |

## Final mental models

- Cluster: Control Plane + Worker Nodes (Pods) ← Service ← Ingress ← Load Balancer ← Internet.
- Deployment maintains replicas → Pods → Service gives stable networking. HPA = more/fewer Pods; node autoscaling = more/fewer nodes. ConfigMap = config; Secret = sensitive config; PVC = persistent storage; NetworkPolicy = Pod traffic control; Probe = health/readiness.

## Added notes (not in source)

- **HPA scaling formula:** `desiredReplicas = ceil( currentReplicas × currentMetricValue / targetMetricValue )` — e.g. 3 Pods at 90% CPU with target 60% → ceil(3 × 90/60) = 5. HPA also has stabilization windows and conflicts with a hard-coded `replicas` in a re-applied Deployment manifest. `kubectl top pods` needs Metrics Server.
- **A complete Ingress** (the chapter only shows the `rules` fragment):
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata: { name: api-ingress }
spec:
  ingressClassName: alb           # or nginx
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service: { name: api-service, port: { number: 80 } }
```
- **Gateway API** is the newer, more expressive successor to Ingress; Ingress remains widely used.
- **Rolling update tuning:** `strategy.rollingUpdate.maxSurge` / `maxUnavailable` (default 25% each).
- **NetworkPolicy:** by default all Pod traffic is allowed; once a policy selects a Pod, traffic of that type not explicitly allowed is denied; enforcement requires a CNI that supports it (Calico, Cilium, or AWS VPC CNI network policy support).
- On EKS the workload-identity mechanisms are **IRSA** (IAM Roles for Service Accounts via OIDC) and **EKS Pod Identity** — see Ch.31.
- AWS Load Balancer Controller: Ingress → **ALB**, Service type `LoadBalancer` → **NLB**; target type `ip` routes straight to Pod IPs.
- Cluster Autoscaler vs Karpenter: both add nodes for unschedulable Pods; Karpenter provisions right-sized nodes directly.
- Example CronJob: `schedule: "0 2 * * *"` (same cron syntax as Ch.3).
- PDB example: `minAvailable: 2` (or `maxUnavailable: 1`) with a `selector` for the Pods.

<!-- NAV -->

---

← [Sheet 19](ch19-revision.md) · [Full chapter 20](../docs/05-kubernetes/ch20-kubernetes-networking-scaling.md) · [All revision material](README.md) · [Sheet 21](ch21-revision.md) →
