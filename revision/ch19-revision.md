# Chapter 19 — Revision Sheet: Kubernetes Configuration + Storage

> Supplements [the full chapter](../docs/05-kubernetes/ch19-kubernetes-config-storage.md). Problem: give containers **configuration, secrets, resources and persistent data** without hard-coding them into the image or losing data when a Pod dies.

## Configuration

| | ConfigMap | Secret |
|---|---|---|
| Holds | Non-sensitive config: `NODE_ENV`, `PORT`, `LOG_LEVEL`, `API_TIMEOUT` | Sensitive: DB password, JWT secret, API keys, AWS credentials |
| Create | YAML (`data:` map) / `kubectl apply -f configmap.yaml` | `kubectl create secret generic api-secret --from-literal=DB_PASSWORD='supersecret'` |
| Inspect | `kubectl get configmap`, `kubectl describe configmap api-config` | `kubectl get secrets`, `kubectl describe secret api-secret` (doesn't print values) |
| Inject all keys | `envFrom: - configMapRef: { name: api-config }` | — |
| Inject one key | — | `env: - name: DB_PASSWORD  valueFrom: { secretKeyRef: { name: api-secret, key: DB_PASSWORD } }` |
| Verify | `kubectl exec -it <pod> -- env` | same |

- Mnemonic: **ConfigMap = configuration, Secret = sensitive configuration.** Local dev uses `.env`; Kubernetes uses ConfigMap/Secret (larger environments may use external secret/config systems).
- **"Kubernetes Secrets are encrypted" is an oversimplification:** manifests typically hold **base64-encoded** values — **base64 ≠ encryption** (`hello` → `aGVsbG8=`). Use encryption at rest + access controls; on AWS integrate with **Secrets Manager** (Ch.17).
- Node.js just reads env vars (`Number(process.env.PORT ?? 3000)`, `process.env.DATABASE_URL`, `process.env.JWT_SECRET`) and doesn't care whether they came from ConfigMap/Secret/Docker/AWS.
- Never casually commit `kubectl create secret ... --from-literal=...password...` commands to Git.

## Volumes and persistence

- Containers are ephemeral — data in the container filesystem disappears with it.
- **`emptyDir`** = temporary storage tied to the Pod (temp files, scratch space, intermediate processing, cache-like data). **Data is lost when the Pod is removed** — never for data that must survive Pod replacement.
```yaml
volumes:
  - name: app-data
    emptyDir: {}
containers:
  - name: api
    image: my-api:1.0
    volumeMounts:
      - name: app-data
        mountPath: /app/data
```
- **PersistentVolume (PV)** = persistent storage available to the cluster. **PersistentVolumeClaim (PVC)** = application's request ("I need 5 GiB"): `App → PVC → PV → actual storage`.
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata: { name: api-storage }
spec:
  accessModes: [ReadWriteOnce]
  resources: { requests: { storage: 5Gi } }
```
`kubectl get pvc` → `Bound`. Mount: `volumes: - name: persistent-data  persistentVolumeClaim: { claimName: api-storage }`. Pod A dies → Deployment creates Pod B → can mount the same claim (subject to storage/access-mode constraints).
- **StorageClass** = how storage is **dynamically provisioned** (PVC → StorageClass → cloud storage provisioned → PV). On AWS via CSI drivers: **EBS** (block storage) and **EFS** (managed network file storage, shared across workloads). Kubernetes → CSI driver → AWS storage.

## Requests & limits

```yaml
resources:
  requests: { cpu: "250m", memory: "256Mi" }
  limits:   { cpu: "500m", memory: "512Mi" }
```
**Request** = what the workload asks/reserves for scheduling. **Limit** = maximum boundary. Without them workloads interfere with each other; important for autoscaling later (Ch.20).

## Probes

| | Liveness | Readiness |
|---|---|---|
| Question | Is it alive? → should Kubernetes **restart** the container? | Can this Pod receive traffic **now**? |
| Example | `httpGet: /health :3000`, `initialDelaySeconds: 10`, `periodSeconds: 15` | `httpGet: /ready :3000`, `initialDelaySeconds: 5`, `periodSeconds: 10` |
| Case | Broken state repeatedly failing → restart | DB temporarily unavailable → readiness ❌ → don't send traffic, container still alive |

Not interchangeable. New Pod starts → Node starts → DB not ready: readiness prevents early traffic.

## Complete Node.js Deployment (shape)

ConfigMap (`NODE_ENV`, `PORT`) + Secret (`DATABASE_URL`, `JWT_SECRET`) + Deployment (replicas 3, `envFrom` ConfigMap, `env` from `secretKeyRef`, resources requests/limits, readinessProbe `/ready`, livenessProbe `/health`).

## Stateless vs stateful

- API should be **stateless** (any Pod can serve any request); state lives in PostgreSQL / Redis / S3 — not the Pod filesystem. Session only in Pod A is lost when A dies → use shared Redis.
- **Should PostgreSQL run in Kubernetes?** You can, but prefer **RDS** (backups, failover, maintenance, monitoring, managed storage) → `EKS → Node.js Pods → RDS`.
- **StatefulSet:** stable identities (`postgres-0`, `postgres-1`, `postgres-2`) and persistent storage semantics for certain stateful distributed systems. For a backend: Node API → Deployment; PostgreSQL → preferably RDS.
- **Where to put data:** temporary → emptyDir; persistent filesystem data → PVC/cloud storage; objects/uploads → S3; relational data → RDS; cache/session → Redis.

## Interview: "What happens when a Pod dies?"

Deployment desired replica count → controller notices missing Pod → replacement Pod created → scheduler places it → container starts → readiness probe passes → Service can send traffic.

## Debugging checklist

`kubectl get pods` → `describe pod` → `logs` → `exec -- env`. Check: ConfigMap/Secret exist? correct key? correct **namespace** (Secrets/ConfigMaps are namespace-scoped; "Secret exists in namespace A, Pod in B")? env name correct? image contains expected app? app reads `process.env`? probe endpoint and port exist?
- **ConfigMap changed but app still uses old value:** env vars injected into a running container don't update → `kubectl rollout restart deployment api`.
- **PVC stuck Pending:** `kubectl get pvc`, `kubectl describe pvc <name>` — no suitable provisioner, wrong StorageClass, insufficient capacity, access-mode mismatch.

## Added notes (not in source)

- **Access modes:** `ReadWriteOnce` (mounted read-write by a single node — typical for EBS, which is also **AZ-bound**), `ReadOnlyMany`, `ReadWriteMany` (e.g. EFS), `ReadWriteOncePod`. A multi-replica Deployment sharing one RWO PVC often fails; StatefulSets use `volumeClaimTemplates` for one PVC per Pod.
- PV **reclaim policy**: `Delete` or `Retain`. StorageClass `volumeBindingMode: WaitForFirstConsumer` delays provisioning until a Pod is scheduled (so the volume lands in the right AZ).
- ConfigMaps/Secrets can also be **mounted as files**; mounted volumes are updated eventually when the ConfigMap changes, **env vars are not**.
- `emptyDir` survives *container* restarts within the same Pod but not Pod deletion; `medium: Memory` backs it by RAM.
- **Units:** `250m` = 0.25 CPU core; `256Mi` = mebibytes. Exceeding a **CPU limit** throttles; exceeding a **memory limit** gets the container **OOMKilled**. The scheduler uses **requests**; QoS classes: Guaranteed, Burstable, BestEffort.
- **`startupProbe`** protects slow-starting apps. Keep liveness checks lightweight and independent of external dependencies (a DB outage shouldn't make Kubernetes restart every Pod); readiness failing removes the Pod from the Service's endpoints and gates rolling updates.
- The chapter's lab creates a Secret with `API_KEY` while the Deployment reads `DATABASE_URL`/`JWT_SECRET` — adapt one of them to match (see [Corrections](../CORRECTIONS.md)).

<!-- NAV -->

---

← [Sheet 18](ch18-revision.md) · [Full chapter 19](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) · [All revision material](README.md) · [Sheet 20](ch20-revision.md) →
