# Chapter 29 — Revision Sheet: Kubernetes CRDs + Operators

> Supplements [the full chapter](../docs/05-kubernetes/ch29-crds-operators.md). Level up: from *using* Kubernetes to understanding **how Kubernetes itself can be extended**.

## Core vocabulary (the "one thing to remember")

| Term | Meaning |
|---|---|
| **CRD** (Custom Resource Definition) | Extends the Kubernetes API with a **new resource type** (e.g. `PostgresCluster`) — the class/schema/type |
| **Custom Resource (CR)** | An **instance** of that type (`PostgresCluster` named `production-db`) |
| **Controller** | Watches resources and makes **desired state** match **actual state** — a reconciliation/control loop (Deployment controller: desired 3 Pods, actual 2 → create one) |
| **Operator** | A controller that encodes **application/domain-specific operational knowledge** (replication, backups, failover, upgrades, scaling, configuration) |
| **Reconciliation** | Compare desired vs actual and act so actual converges to desired; continuous |

Analogy: `class User { name: string }` = CRD; `new User()` = Custom Resource. Before a CRD, Kubernetes knows Pod/Deployment/Service/ConfigMap; after, it also recognises `PostgresCluster`.

**Why:** developers write
```yaml
apiVersion: databases.example.com/v1
kind: PostgresCluster
metadata: { name: production-db }
spec: { replicas: 3, version: "16" }
```
instead of hand-crafting StatefulSets, Services, PVCs, Secrets, ConfigMaps, backup jobs and monitoring — the platform hides the complexity.

## CRD alone isn't enough (critical)

A CRD tells Kubernetes the type exists, not **how to implement it**. Creating a CR stores an object; **nothing happens** until a controller/operator watches it. Flow: CRD defines type → CR created → Operator (controller) notices → creates StatefulSet/Service/PVC/config/backup resources → Kubernetes' own controllers create Pods. **Operators work with Kubernetes, not instead of it** (layered controllers: Operator → Kubernetes resources → Kubernetes controllers → Pods).

## Creating a CRD and CR

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: applications.platform.example.com      # <plural>.<group>
spec:
  group: platform.example.com
  names:
    kind: Application
    plural: applications
    singular: application
    shortNames: [app]
  scope: Namespaced
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                image: { type: string }
                replicas: { type: integer }
```
```yaml
apiVersion: platform.example.com/v1
kind: Application
metadata: { name: my-api }
spec: { image: nginx:latest, replicas: 3 }
```
```bash
kubectl apply -f app-crd.yaml ; kubectl get crd
kubectl apply -f application.yaml ; kubectl get applications     # lists my-api, but creates NO Pods
kubectl api-resources                                              # shows the new type
```
Group `platform.example.com`, version `v1`, kind `Application`, plural `applications`. After installing a CRD: `kubectl get postgresclusters` just like `kubectl get deployments`.

**Validation:** schema constraints such as `replicas: { type: integer, minimum: 1, maximum: 10 }` (so `replicas: 100` is rejected) and `required: [image, replicas]`.

## spec vs status, conditions, finalizers

- **`spec` = what I want; `status` = what currently exists** (`spec.replicas: 3`, `status.readyReplicas: 2`). The controller keeps reconciling: spec → desired → controller → actual → status.
- **Conditions** let controllers communicate state: `status.conditions: [{type: Ready, status: "True"}]` — understand the pattern.
- **Finalizer:** *allows a controller to perform cleanup before Kubernetes completes deletion of a resource* (e.g. backup + delete the external cloud database before the object disappears).

## Operator lifecycle / pattern

Create CR → Operator notices → reconcile → create/update resources → monitor state → reconcile again → update status — for the resource's whole lifetime. Generic: **Custom Resource → Controller → Observe → Compare desired vs actual → Take action → Observe again** (a control loop).
**Why "Operator":** it encodes human operational knowledge ("if a replica fails recreate it", "if the primary fails promote a replica", "before upgrading perform these checks").
**Real operators:** PostgreSQL, Kafka, Redis, Prometheus, Elasticsearch, MongoDB (e.g. `kind: Kafka`, `spec.replicas: 3`).
**Writing operators:** Kubebuilder, Operator SDK, controller-runtime; usually in **Go** (the Kubernetes ecosystem language; good for concurrent controllers, network services, Kubernetes APIs). Understanding the pattern matters more than building one.

## How it combines with your stack

- **Helm** can package CRD + Operator + Custom Resources (Helm → PostgreSQL Operator → CRD installed → `PostgreSQLCluster` → operator manages the DB).
- **ArgoCD/GitOps** can manage CRDs and CRs (Git → ArgoCD → CRD → CR → Operator → Application).
- **Terraform → EKS → Helm (operator) → Custom Resource**; GitOps manages the custom resources. Terraform provisions AWS; Helm installs the operator; GitOps manages the custom database resources.
- **Platform engineering:** with 200 teams, expose `kind: PostgresCluster` and hide networking/storage/replication/backups/failover → Developer → simple Custom Resource → Platform Operator → complex infrastructure.

## Comparisons

| | |
|---|---|
| **Operator vs Helm** | Helm = template, package, install, upgrade ("install this configuration"). Operator = observe, reconcile, recover, scale, back up, upgrade ("continuously manage this application") |
| **Operator vs controller** | Controller = general reconciliation component; Operator = controller for a specific application/domain. Every Operator involves controller behaviour; not every controller is called an Operator |
| **CRD vs Operator** | CRD defines the new API type; Operator watches resources and implements application-specific reconciliation |

## Troubleshooting

1. `kubectl get applications` fails → `kubectl get crd` (CRD not installed?). 2. CRD exists but CR fails → `kubectl describe application my-api` (validation errors, events, spec problems). 3. CR exists but nothing happens → operator not running: `kubectl get pods -n <operator-namespace>`, `kubectl logs <operator-pod>`. 4. Operator `CrashLoopBackOff` → `get pods`, `describe pod`, `logs`, `logs --previous`. 5. **RBAC:** operators run inside Kubernetes under a ServiceAccount; missing permissions (create Deployments/Services/Secrets/PVCs) → API DENIED; check `kubectl auth can-i ...`.

## Interview answers (verbatim-style)

- *What happens if I create a Custom Resource?* The CRD defines the type and Kubernetes stores the CR; creating it alone doesn't implement behaviour — a controller/Operator must watch it and reconcile by creating/updating underlying resources.
- *CRD vs Operator?* see table. *Why Operator instead of Helm?* Helm packages/templates; an Operator continuously observes and manages lifecycle. *What is reconciliation?* Comparing desired with actual state and acting so actual converges to desired. *Why are Operators useful?* They encode domain-specific operational knowledge so Kubernetes can automate provisioning, backups, failover, upgrades and recovery.

## Depth guide

Know well: CRD, CR, controller, Operator, reconciliation, spec vs status, desired vs actual, finalizers, CRD validation, RBAC, CRDs + Helm/ArgoCD, operator troubleshooting. Awareness: Kubebuilder, Operator SDK, controller-runtime, admission webhooks, conversion webhooks, multi-version CRDs, advanced controller internals.

## Added notes (not in source)

- ⚠ **Name collision:** the chapter's example CRD uses `shortNames: [app]`; Argo CD's own `Application` CRD (Chapter 26) also uses `app`, so having both in one cluster makes `kubectl get app` ambiguous. Choose distinct kinds/short names (or fully qualify `applications.platform.example.com`).
- To make `status` writable separately from `spec`, enable the **status subresource** in the CRD (`subresources: { status: {} }`); `kubectl explain applications.spec` shows the schema; v1 CRDs require a *structural* schema; newer clusters also support CEL validation rules.
- Controllers are **level-triggered**: they reconcile toward the current desired state rather than reacting to individual events, so reconciliation must be idempotent.
- Operators set **ownerReferences** on child resources so deleting the CR garbage-collects them (finalizers cover external cleanup).
- **Danger:** `kubectl delete crd <name>` deletes **all** custom resources of that type.
- Webhooks: *admission* webhooks validate/mutate objects on create/update; *conversion* webhooks translate between CRD versions.

<!-- NAV -->

---

← [Sheet 28](ch28-revision.md) · [Full chapter 29](../docs/05-kubernetes/ch29-crds-operators.md) · [All revision material](README.md) · [Sheet 30](ch30-revision.md) →
