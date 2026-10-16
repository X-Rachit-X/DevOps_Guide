# Chapter 18 — Revision Sheet: Kubernetes Fundamentals

> Supplements [the full chapter](../docs/05-kubernetes/ch18-kubernetes-fundamentals.md). Core idea: **you declare the desired state; Kubernetes continuously works to make the actual state match it.**

## Why Kubernetes

100 containers / 10 servers / many apps and environments / frequent deploys / failures / scaling → manual management is painful. If EC2-A (API + Worker + Payments) crashes you need to **detect failure, restart workloads, place them elsewhere, maintain desired replicas, route traffic, manage configuration, perform deployments**. Kubernetes = **container orchestration platform**: manages containers across a cluster. You say "I want 5 copies of my API", not `docker run/stop/restart/scale`.

| Docker | Kubernetes |
|---|---|
| Runs containers (container technology) | Manages containers at scale (orchestration) — deploy, scale, network, self-heal, roll out/back |
| Compose: local dev | Production orchestration, scaling, self-healing, service discovery, rolling deployments |
| EC2 = virtual machine | A cluster can itself run on EC2 worker nodes: AWS → EC2 → Kubernetes → Pod → container |

## Architecture

```text
Cluster
├── Control Plane: API Server · Scheduler · Controller Manager · etcd
└── Worker Nodes: kubelet · container runtime · Pods
```

| Component | Role |
|---|---|
| **API Server** | Main interface to Kubernetes; `kubectl` talks to it |
| **etcd** | Distributed key-value store holding cluster state (what deployments exist, desired replicas, configuration, objects). Interview level: *etcd stores Kubernetes cluster state* |
| **Scheduler** | Decides which worker node runs each Pod (resource availability + constraints) |
| **Controller Manager** | Controllers continuously compare **desired vs actual** state (replicas: 3 but 2 Pods → create one) — "the heart of Kubernetes" |
| **kubelet** | Agent on each worker node; talks to control plane and ensures assigned workloads run |
| **Container runtime** | Actually runs containers; modern clusters use **containerd** (or another CRI-compatible runtime) — **Kubernetes does not require Docker Engine** (your image/Dockerfile/registry knowledge still applies) |

**Desired state:** write `replicas: 3` (declarative), not step-by-step imperative commands.

## Pod

- Smallest deployable unit. Usually Pod → one container (Node.js). A Pod can hold tightly coupled containers (API + sidecar) sharing **network namespace/localhost and volumes**. **Pod ≠ container.** Don't put unrelated apps in one Pod.
- **Pod IPs are ephemeral** (replacement Pod gets a new IP) → never use Pod IPs for clients → Services.
- Basic Pod manifest:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-pod
spec:
  containers:
    - name: api
      image: node:22
      ports:
        - containerPort: 3000
```
(not a useful production deployment; standalone Pods aren't recreated the way you want → Deployments)
- **kubectl:** `get pods`, `describe pod api-pod` (events, scheduling, container state, image, volumes, networking, errors), `logs api-pod` / `logs -f`, `exec -it api-pod -- sh` (then `ls`, `env`, `curl localhost:3000/health`), `delete pod api-pod`, `apply -f pod.yaml`.

## Deployment, labels, selectors

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  replicas: 3
  selector:
    matchLabels: { app: api }
  template:
    metadata:
      labels: { app: api }
    spec:
      containers:
        - name: api
          image: my-api:1.0
          ports: [{ containerPort: 3000 }]
```
- Deployment manages a set of Pods and keeps `replicas` alive; Pod names look like `api-7c9d8f7c5d-a1b2c`.
- **Self-healing:** Pod B crashes → actual 2 / desired 3 → new Pod D created → 3 healthy.
- **Labels** = key-value metadata (`app=api`, `environment=production`, `version=v1`); **selectors** (`matchLabels`) pick objects by label — crucial for Services.

## Services

| Type | What it does |
|---|---|
| **ClusterIP** | Stable endpoint **inside** the cluster (API → internal service/worker) |
| **NodePort** | Exposes on each node's IP:port → Service → Pods; understand it, but not for production Internet traffic |
| **LoadBalancer** | In the cloud provisions/configures an external load balancer (Internet → cloud LB → Service → Pods) |

```yaml
apiVersion: v1
kind: Service
metadata: { name: api-service }
spec:
  selector: { app: api }
  ports:
    - port: 80          # Service port
      targetPort: 3000  # Pod port
  type: ClusterIP
```
Client → Service → healthy Pod; if a Pod dies, traffic goes to other healthy Pods.

## Namespaces and configuration

- **Namespace** = logical separation (development / staging / production), `kubectl get pods -n production`. Alternative: separate clusters (Dev → Cluster A, Prod → Cluster B); choice depends on isolation, security, scale, operations.
- **ConfigMap** (non-sensitive: `NODE_ENV: production`, `PORT: "3000"`) and **Secret** (credentials/tokens) injected as env vars. Don't bake environment-specific config into images. **Kubernetes Secrets aren't automatically equal to a full secrets-management system**; on AWS integrate with Secrets Manager (Ch.19/33).

## Local lab with kind

```bash
kubectl version --client
kind version
kind create cluster --name devops-learning
kubectl get nodes                     # devops-learning-control-plane
docker build -t my-api:1.0 .
kind load docker-image my-api:1.0 --name devops-learning   # no registry needed
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl get pods ; kubectl get deployments ; kubectl get svc ; kubectl get all
kubectl describe deployment api ; kubectl describe service api-service ; kubectl logs <pod>
kubectl port-forward service/api-service 3000:80 ; curl http://localhost:3000/health
```
Options: Docker Desktop Kubernetes, Minikube, **kind** (runs nodes as containers).

## "Break it" exercises

| Action | Command | Expect |
|---|---|---|
| Delete a Pod | `kubectl delete pod <pod>` / `kubectl get pods -w` | Replacement created (self-healing) |
| Scale up | edit `replicas: 5` + apply, or `kubectl scale deployment api --replicas=5` | 5 Pods |
| Scale down | `kubectl scale deployment api --replicas=2` | Excess removed (desired 2 / actual 5 → 2) |
| Bad image | `image: my-api:does-not-exist` | `ImagePullBackOff` / `ErrImagePull`; read **Events** in `describe pod` |

**Pod phases:** Pending, Running, Succeeded, Failed, Unknown. **Common problems:** `CrashLoopBackOff`, `ImagePullBackOff`, `ErrImagePull`. **Debug workflow:** `get pods` → `describe pod` → `logs` → `exec` → check image/config/network/resources.

## Kubernetes + AWS

Route 53 → CloudFront/WAF → ALB → Kubernetes Service → Pods → RDS. **EKS** = Elastic Kubernetes Service: AWS manages significant parts of the control plane; workers via managed node groups or other compute. **ECR** (Elastic Container Registry) holds images pulled by EKS. Pipeline: git push → GitHub Actions → tests → Docker build → push to registry → Kubernetes deployment → **rolling update** (v1 v1 v1 → v2 v1 v1 → v2 v2 v1 → v2 v2 v2) → Pods.

## Depth guide

Deep: why Kubernetes, Docker vs K8s, cluster, control plane, worker nodes, API server, scheduler, controllers, etcd, kubelet, Pods, Deployments, replicas, desired state, labels/selectors, Services, ClusterIP, LoadBalancer, namespaces, kubectl, YAML, Pod lifecycle, self-healing, scaling, rolling deployments, images, local setup, debugging. Medium: EKS, NodePort, ReplicaSets, readiness/liveness, requests/limits, ConfigMaps, Secrets. Awareness: StatefulSets, DaemonSets, Jobs/CronJobs, Operators, CRDs, service mesh.

## Added notes (not in source)

- A Deployment actually manages **ReplicaSets**, which manage Pods; each rollout creates a new ReplicaSet (this is what enables rollback). Useful commands: `kubectl rollout status deployment/api`, `kubectl rollout undo deployment/api`.
- The worker node also runs **kube-proxy** (implements Service routing); a cloud cluster also has a **cloud-controller-manager**.
- Services get cluster **DNS** names: `api-service.<namespace>.svc.cluster.local` (just `api-service` inside the same namespace).
- Kubernetes **Secrets are only base64-encoded** by default (not encrypted); enable encryption at rest for etcd and restrict RBAC.
- **Namespaces don't isolate network traffic** by themselves — use NetworkPolicies.
- Docker Engine support via "dockershim" was removed from Kubernetes in v1.24; clusters use CRI runtimes such as containerd.
- `CrashLoopBackOff`/`ImagePullBackOff` are status reasons shown by `kubectl get pods`, not Pod phases.
- A Pod running only `node:22` with no `command` exits immediately (no app started); the chapter notes this manifest is a learning stepping stone.

<!-- NAV -->

---

← [Sheet 17](ch17-revision.md) · [Full chapter 18](../docs/05-kubernetes/ch18-kubernetes-fundamentals.md) · [All revision material](README.md) · [Sheet 19](ch19-revision.md) →
