# Chapter 25 — Revision Sheet: Helm — Kubernetes Package Management

> Supplements [the full chapter](../docs/05-kubernetes/ch25-helm.md). Goal: create, configure, install, upgrade, roll back and troubleshoot a Helm-based Kubernetes application.

## Why Helm

Without Helm: `kubectl apply -f deployment.yaml / service.yaml / configmap.yaml / ingress.yaml / hpa.yaml`, and per-environment copies (`deployment-dev/staging/prod.yaml`) that differ in image, replicas, CPU, memory, hostname, DB config. **Helm = package manager + templating system (+ release management) for Kubernetes applications** — like npm for Node.js and apt for Linux.

| Term | Meaning |
|---|---|
| **Chart** | Package: templates + configuration (values) + metadata (+ optional dependencies) that generate Kubernetes manifests |
| **Release** | An **installed instance** of a chart (`dev-api`, `prod-api` from the same chart) |
| **values.yaml** | Configurable defaults (replicaCount, image.repository/tag, service, containerPort, resources) |
| **Templates** | Kubernetes YAML with `{{ ... }}` expressions |

Flow: Helm CLI → Chart (Templates + Values + metadata + dependencies) → rendered Kubernetes manifests → Kubernetes API. Same chart, different values per environment.

## Chart layout (`helm create my-api`)

```text
my-api/
├── Chart.yaml         # metadata
├── values.yaml        # default configuration
├── charts/            # dependencies
├── templates/         # deployment.yaml service.yaml ingress.yaml hpa.yaml serviceaccount.yaml _helpers.tpl tests/
└── .helmignore
```
```yaml
# Chart.yaml
apiVersion: v2
name: my-api
description: A Helm chart for my Node.js API
type: application
version: 0.1.0        # version of the CHART
appVersion: "1.0.0"   # version of the APPLICATION (not necessarily equal)
```
```yaml
# values.yaml
replicaCount: 2
image: { repository: my-api, tag: "1.0.0" }
service: { type: ClusterIP, port: 80 }
containerPort: 3000
resources:
  requests: { cpu: "100m", memory: "128Mi" }
  limits:   { cpu: "500m", memory: "512Mi" }
```

## Templating

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-api
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}-api
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}-api
    spec:
      containers:
        - name: api
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: {{ .Values.containerPort }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```
- `.Values` = values supplied to the chart (`.Values.image.repository` → `my-api`, `.Values.image.tag` → `1.0.0`). `.Release.Name` = release name given at install (`helm install my-api ./my-api` → `my-api`) — used to build resource names. `replicaCount: 5` ⇒ `replicas: 5`.

## Environments and precedence

`values.yaml` (base: replicaCount 2, tag latest) · `values-dev.yaml` (1 replica, tag `dev`) · `values-prod.yaml` (5 replicas, tag `1.4.2`):
```bash
helm install dev-api  ./my-api -f values-dev.yaml
helm install prod-api ./my-api -f values-prod.yaml
```
**Precedence:** default values → values file(s) → `--set` (the more specific override wins; `--set replicaCount=10` beats `values-prod.yaml`'s 5 beats default 2).

## Commands (memorise)

| Command | Purpose |
|---|---|
| `helm version` | Verify install (common: `curl .../get-helm-3 \| bash`) |
| `helm create my-api` | Scaffold chart |
| `helm lint ./my-api` | Check chart for common problems (template syntax errors, e.g. "unexpected EOF") |
| `helm template my-api ./my-api` | **Render YAML locally without installing** — first debugging command |
| `helm install my-api ./my-api` | Install (creates a release) |
| `helm list` | List releases |
| `helm upgrade prod-api ./my-api -f values-prod.yaml` | Update a release |
| `helm upgrade --install my-api ./my-api` | Install if absent, upgrade if present — **CI/CD staple** |
| `helm upgrade my-api ./my-api --dry-run` | Detect rendering/config issues before changing the cluster |
| `helm history prod-api` | Revisions (1 deployed, 2 deployed, 3 deployed) |
| `helm rollback prod-api 2` | Roll back to revision 2 |
| `helm status my-api` / `helm get values my-api` / `helm get manifest my-api` | Inspect what Helm actually deployed |
| `helm uninstall my-api` | Remove release |
| `helm repo add <name> <url>` / `helm repo update` / `helm search repo <name>` | Chart repositories |
| `helm package ./my-api` | Produces `my-api-0.1.0.tgz` |

Workflow: edit chart → `helm lint` → `helm template` → `helm install/upgrade`.

## CI/CD

```bash
helm upgrade --install my-api ./helm/my-api \
  --namespace production --create-namespace \
  -f ./helm/my-api/values-prod.yaml \
  --set image.tag=$GITHUB_SHA
```
Pipeline: git push → GitHub Actions → tests → build → Docker image → push to ECR → `helm upgrade` → Kubernetes. Tag images with the **Git SHA** (`my-api:8f42c91`) not `latest` → production ↔ image ↔ commit traceability and easier rollback. ECR example: `123456789.dkr.ecr.ap-south-1.amazonaws.com/my-api:1.2.0` with `values-prod.yaml` (replicaCount 4, ClusterIP, port 80, containerPort 3000).

## Debugging workflow

Helm configuration → rendered YAML → Kubernetes resources → Pods → application. `helm status` → `helm get values` → `helm get manifest` → then `kubectl get pods / describe pod / logs`.
- *Template syntax error:* `helm lint`. *Wrong value (expected 5 replicas got 2):* `helm get values`, `helm template`. *Helm succeeded but Pod broken* (`CrashLoopBackOff`): Helm isn't the problem anymore → `kubectl logs/describe`.

## Comparisons

| | |
|---|---|
| **Helm vs kubectl** | kubectl: directly manages Kubernetes resources (`kubectl apply -f`); Helm: packages/configures/manages Kubernetes *applications/releases* (still ends up as Kubernetes resources) |
| **Helm vs Docker** | Docker packages app + dependencies → container image; Helm packages Kubernetes manifests + configuration → chart. Source → Docker → image → Helm → Kubernetes deployment |
| **Helm vs Terraform** | Terraform = infrastructure (VPC, EKS, RDS, S3, IAM); Helm = Kubernetes applications (Deployment, Service, Ingress, ConfigMap, HPA). Often both: Terraform → AWS infra → EKS → Helm → applications (boundaries can overlap) |

**Dependencies:** a chart can depend on others (Redis, PostgreSQL), but with managed services keep DB in Terraform/RDS and the Node.js API in Helm — cleaner separation.
**Security:** don't put `databasePassword: mypassword` in `values.yaml`; **Helm is not a secret-management solution**. Better: AWS Secrets Manager → External Secrets/secret integration → Kubernetes Secret → Pod.

## Lab and practice

Create chart → inspect → `helm lint .` → `helm template my-api .` → `helm install my-api .` → `helm list`, `kubectl get pods/svc` → set `replicaCount: 3` → `helm upgrade my-api .`. **Break it:** set `image.repository: nonexistent-image` → `helm upgrade` → `ImagePullBackOff` → `kubectl describe pod` → fix → upgrade. **Environments:** `values-dev.yaml` (1 replica, tag dev) and `values-prod.yaml` (3 replicas, tag 1.0.0), install `dev-api` and `prod-api`.

## One-line interview answer

*Helm lets us package and template Kubernetes applications so the same deployment definitions can be reused across environments with different configuration, while providing release versioning, upgrades and rollbacks.*

## Added notes (not in source)

- `{% raw %}{{ toYaml .Values.resources | nindent 12 }}{% endraw %}` converts the values map to YAML and indents it 12 spaces on a new line; `{% raw %}{{-{% endraw %}` trims preceding whitespace. Other common template pieces: `_helpers.tpl` with `define`/`include`, `default`, `quote`, `required`, `if`, `range`, `with`.
- Exact precedence (low → high): chart `values.yaml` < parent chart values < `-f` files (later files override earlier) < `--set`/`--set-string`/`--set-file` (later flags win).
- `helm rollback` creates a **new revision** that re-applies an old one (history is preserved). Helm 3 has no Tiller; release state is stored as **Secrets** in the release namespace (`sh.helm.release.v1.<name>.v<rev>`).
- CI hardening flags: `--atomic` (roll back automatically on failure), `--wait`, `--timeout`. The `helm diff` plugin previews changes; `helm test` runs chart tests; chart **hooks** run Jobs before/after install/upgrade (e.g. DB migrations). `helm dependency update` writes `Chart.lock`.
- Secret handling options: External Secrets Operator, SOPS/helm-secrets, sealed-secrets.
- Piping a script to `bash` (the install one-liner) trusts the download; prefer your package manager or verify the checksum. Helm 4 has been released — check current docs.

<!-- NAV -->

---

← [Sheet 24](ch24-revision.md) · [Full chapter 25](../docs/05-kubernetes/ch25-helm.md) · [All revision material](README.md) · [Sheet 26](ch26-revision.md) →
