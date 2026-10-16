# Chapter 26 — Revision Sheet: GitOps + ArgoCD

> Supplements [the full chapter](../docs/03-cicd-gitops/ch26-gitops-argocd.md). Core statement: **GitOps = Git is the source of truth for the desired state of infrastructure/application deployment, and an automated system continuously makes the actual environment match it.**

## Traditional CD vs GitOps

| Traditional | GitOps |
|---|---|
| GitHub → CI/CD → Test → Build → Docker → ECR → `kubectl`/Helm → Kubernetes (the pipeline *pushes* the deployment) | GitHub → CI → Build image → ECR → **update deployment config in GitOps repo** → **ArgoCD** → Kubernetes (Git says "this is what production SHOULD look like"; a controller applies it) |

- **Interview definition:** *GitOps is an operational model where Git stores the declarative desired state of applications/infrastructure, and automated controllers continuously reconcile the running environment with that state.* Keywords: Git, declarative, desired state, automation, reconciliation.
- **Desired vs actual:** Git `replicas: 5`, cluster 3 Pods → ArgoCD detects the difference and reconciles → **reconciliation** (same philosophy as Kubernetes controllers: actual → desired).
- **Why Git:** version history, auditability, review (PRs), rollback, reproducibility. If someone runs `kubectl scale ... --replicas=10` while Git says 5, Git is the truth — change Git if 10 is truly desired.

## Repositories

```text
gitops-repo/
├── apps/api/{Chart.yaml, values.yaml, values-prod.yaml, templates/}
└── environments/{dev, staging, production}
# or separate repos:  my-app/ (src, Dockerfile, package.json)   my-app-gitops/ (dev, staging, production)
```
**Application source ≠ deployment configuration** — they can be separated: application repo (code, tests, Dockerfile) vs GitOps repo (Kubernetes config, Helm values, environment config).

## Roles: CI vs CD

GitHub Actions = **CI** (tests, Docker build, push image to ECR, update GitOps repo, security scans, artifact creation). ArgoCD = **CD** (deployment sync, reconciliation, drift detection). Not the only architecture, but very common. *Don't say "GitOps replaces CI/CD"* — GitOps is an approach to CD where Git is the source of truth and a controller reconciles the cluster.
Why not just `kubectl apply` from GitHub Actions? You can, but then manual cluster changes or a non-running CI leave the cluster drifting; GitOps gives **continuous reconciliation** (`desired == actual`).

## ArgoCD

**Argo CD** = declarative GitOps CD tool for Kubernetes: Git → read desired configuration → compare with Kubernetes → detect differences → synchronise. Components to know: API/UI server, repository access, **application controller**, Kubernetes API.

```bash
kubectl get nodes
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl get pods -n argocd
kubectl port-forward svc/argocd-server -n argocd 8080:443     # https://localhost:8080  (local learning only)
argocd version                                                 # CLI
```
Production access normally needs ingress/load balancing, TLS, authentication, networking, security.

### The Application custom resource

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-api
spec:
  project: default
  source:
    repoURL: https://github.com/example/my-gitops-repo.git
    targetRevision: main        # branch/revision
    path: apps/my-api           # directory
  destination:
    server: https://kubernetes.default.svc   # which cluster
    namespace: production                    # which namespace
  syncPolicy:
    automated: {}
```
It says: *"Take this configuration from this Git repo/path and synchronise it to this cluster/namespace."* It is a **Custom Resource** (Kubernetes extended with CRDs — covered in [Chapter 29](../docs/05-kubernetes/ch29-crds-operators.md)).

- **Sync:** manual (Git changes → ArgoCD detects → `OutOfSync` → you sync) vs automatic (detect → sync → Kubernetes).
- **Sync status:** `Synced` (Git ≈ cluster) vs `OutOfSync` (Git ≠ cluster).
- **Health status:** Healthy, Progressing, Degraded, Missing, Unknown — **not the same as sync status**; `Synced + Degraded` = the desired manifests are applied but the app isn't healthy.
- **With Helm:** repo contains the chart (`api-chart/{Chart.yaml, values.yaml, templates/}`); ArgoCD renders Helm → manifests → Kubernetes; no manual `helm upgrade`.

## Production example flow

CI builds image `abc123` → push to ECR → update GitOps values (`image.repository: 1234….dkr.ecr.ap-south-1.amazonaws.com/my-api`, `tag: "abc123"`) → commit "Deploy my-api abc123" → ArgoCD sees Git changed → Helm → Kubernetes → new Pods.
Full pipeline: Developer → Git → GitHub Actions (Tests ∥ Docker build) → ECR → update GitOps repo → ArgoCD → EKS → Pods.

## Drift, rollback, principles

- **Drift:** Git `replicas: 3`, someone runs `kubectl scale ... --replicas=10` → desired 3 / actual 10 → ArgoCD `OutOfSync`; depending on sync policy it can reconcile back.
- **Principle:** don't treat the cluster as the place where you permanently edit config — change Git → PR → review → merge → ArgoCD → Kubernetes (audit trail). Instead of `kubectl edit deployment api`.
- **Rollback:** revert the Git commit (A→B→C→D(broken)→E(revert)); ArgoCD synchronises the new desired state.
- **Benefits:** auditability (who changed production = Git commit), review (who approved = PR), reproducibility (what should production look like = Git), rollback (Git history), drift detection (does Kubernetes match Git = ArgoCD).
- **GitOps security:** RBAC, secrets management, least privilege, image scanning, signed/verified images, protected branches, PR reviews, CI security, ArgoCD access controls, Kubernetes + network security. **Don't put plaintext production passwords in Git** — use Secrets Manager, External Secrets, Sealed Secrets, Vault.
- **What GitOps does NOT mean:** everything stored directly in Git (secrets need special handling), or "never use kubectl" — `kubectl` = inspect/debug/operate; GitOps = manage desired configuration.

## Troubleshooting `OutOfSync`

Git commit → repository → path → branch/revision → rendered Helm/manifests → Kubernetes. Causes: wrong repository, branch or path; invalid YAML; wrong values; permission problem; cluster-access problem; resource conflict.

## Comparisons

| | |
|---|---|
| **ArgoCD vs Helm** | Not competitors: Helm templates/packages apps; ArgoCD continuously synchronises desired state from Git to Kubernetes. Git → Helm chart → ArgoCD → Kubernetes |
| **ArgoCD vs Jenkins** | Jenkins = general-purpose automation/CI-CD server (build, test, package, deploy); ArgoCD = Kubernetes-focused GitOps CD controller. Possible: Jenkins → CI, ArgoCD → CD |
| **ArgoCD vs GitHub Actions** | Actions = CI, tests, builds, images, scans, artifacts; ArgoCD = Kubernetes deployment, reconciliation, drift detection |
| **GitOps vs Terraform** | Terraform → infrastructure (VPC, EKS, RDS, IAM, S3); GitOps/ArgoCD → Kubernetes application state (Deployment, Service, Ingress, ConfigMap, HPA). Terraform creates the platform (cluster exists) → ArgoCD deploys workloads (a mental model, not an absolute rule) |

| Tool | Primary purpose |
|---|---|
| Git | Version control |
| GitHub Actions | CI/automation |
| Docker | Containerisation |
| ECR | Container registry |
| Kubernetes | Container orchestration |
| Helm | Kubernetes packaging/templates |
| ArgoCD | GitOps continuous delivery |
| Terraform | Infrastructure as Code |
| Ansible | Configuration management |

## Hands-on mini project

Create `my-gitops-repo/apps/my-api/{Chart.yaml, values.yaml, templates/}`, commit + push, create an ArgoCD Application pointing at repo + `apps/my-api`. **Test GitOps:** `replicaCount: 2 → 4`, commit/push, `kubectl get pods` eventually shows 4. **Test drift:** `kubectl scale deployment my-api --replicas=1` → ArgoCD shows out of sync (see precision note below).

## Interview scenario

*A developer manually changed a Kubernetes deployment in production. In GitOps?* Determine whether it was intentional; desired state should change in Git via normal review; check ArgoCD sync status and Git history; revert the drift or create the matching Git change; with automated sync (self-heal), ArgoCD can reconcile back to the Git-defined state.

## Depth guide

Must know deeply: GitOps, desired state, declarative config, reconciliation, drift, ArgoCD, Application, sync, auto-sync, Git as source of truth, Helm + ArgoCD, CI + CD separation, rollback. Must be able to do: install ArgoCD, create Application, connect Git repository, deploy Helm chart, sync, check status, detect drift, rollback via Git, troubleshoot sync. Awareness: App-of-Apps, ApplicationSet, multi-cluster, progressive delivery, Argo Rollouts.

## Added notes / precision (not in source)

- **Self-heal precision:** `syncPolicy.automated: {}` only syncs when **Git changes**. To have ArgoCD **revert manual cluster edits** (the drift experiment) you need `automated: { selfHeal: true }`; to delete resources removed from Git you need `prune: true`. Without `selfHeal` the app just shows `OutOfSync`.
- The Application object normally lives in the `argocd` namespace (`metadata.namespace: argocd`); the source YAML omits it. `destination.server: https://kubernetes.default.svc` means the cluster ArgoCD itself runs in.
- Initial login: user `admin`, password from `kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d`. Large CRDs in `install.yaml` may require `kubectl apply --server-side`.
- Health statuses also include `Suspended`.
- **Pull model:** ArgoCD runs *inside* the cluster and pulls from Git, so CI does not need cluster credentials — a security advantage over push-style `kubectl apply` from CI.
- How CI "updates the GitOps repo": a commit by the pipeline (e.g. `yq`/`kustomize edit set image`) or Argo CD Image Updater.
- Argo CD also supports Kustomize and plain YAML; sync features include waves, hooks and retry policies.

<!-- NAV -->

---

← [Sheet 25](ch25-revision.md) · [Full chapter 26](../docs/03-cicd-gitops/ch26-gitops-argocd.md) · [All revision material](README.md) · [Sheet 27](ch27-revision.md) →
