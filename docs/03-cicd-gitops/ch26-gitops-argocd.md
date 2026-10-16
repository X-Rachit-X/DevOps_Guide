# Chapter 26 — GitOps + ArgoCD

> **Source:** Response 26 of the original conversation (`source-archive/src-26.txt`, lines 1–1625) · **Part II — Advanced extension (Responses 25–36)**  
> **Study aids:** [Revision sheet](../../revision/ch26-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

We now move from **Helm → GitOps → ArgoCD**.

You already know Git, GitHub Actions, Docker, Kubernetes, Helm, and Terraform, so this response will connect them into a modern deployment model.

The most important thing to understand is:

> **GitOps means Git becomes the source of truth for the desired state of your infrastructure/application deployment, and an automated system continuously makes the actual environment match that state.**

---

## 1. Traditional Deployment vs GitOps

You've already learned a traditional CI/CD pipeline:

```text
Developer
    ↓
GitHub
    ↓
GitHub Actions
    ↓
Test
    ↓
Build
    ↓
Docker Image
    ↓
ECR
    ↓
kubectl / Helm
    ↓
Kubernetes
```

GitHub Actions performs the deployment.

That's perfectly valid.

With GitOps:

```text
Developer
    ↓
GitHub
    ↓
CI
    ↓
Build Docker Image
    ↓
ECR
    ↓
Update deployment configuration
    ↓
GitOps Repository
    ↓
ArgoCD
    ↓
Kubernetes
```

The important difference:

#### Traditional CD

```text
CI/CD system
     ↓
"Deploy this"
     ↓
Kubernetes
```

#### GitOps

```text
Git
 ↓
"This is what production SHOULD look like"
 ↓
ArgoCD
 ↓
Kubernetes
```

---

## 2. Desired State vs Actual State

This is the core concept.

Suppose Git says:

```yaml
replicas: 5
```

But Kubernetes currently has:

```text
3 Pods
```

Then:

```text
Desired state = 5
Actual state  = 3
```

ArgoCD detects the difference.

It attempts to reconcile:

```text
Git
 ↓
5 replicas
 ↓
ArgoCD
 ↓
Kubernetes
 ↓
5 replicas
```

This is called:

> **Reconciliation**

You already encountered this idea in Kubernetes itself.

Kubernetes controllers continuously try to make:

```text
actual state → desired state
```

ArgoCD applies the same general philosophy at the application deployment level.

---

## 3. What Is GitOps?

A useful interview definition:

> **GitOps is an operational model where Git stores the declarative desired state of applications/infrastructure, and automated controllers continuously reconcile the running environment with that state.**

The important words are:

```text
Git
Declarative
Desired state
Automation
Reconciliation
```

---

## 4. Why Git?

Suppose someone manually runs:

```bash
kubectl scale deployment api --replicas=10
```

Now Kubernetes has:

```text
10 replicas
```

But Git says:

```text
5 replicas
```

What should production be?

With GitOps:

```text
Git = source of truth
```

So the configuration should be changed in Git if the desired state really is 10.

This gives you:

```text
version history
auditability
review
rollback
reproducibility
```

---

## 5. GitOps Repository

A common structure:

```text
gitops-repo/
│
├── apps/
│   └── api/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-prod.yaml
│       └── templates/
│
└── environments/
    ├── dev/
    ├── staging/
    └── production/
```

Another common approach:

```text
my-app/
├── src/
├── Dockerfile
└── package.json

my-app-gitops/
├── dev/
├── staging/
└── production/
```

The exact repository structure varies.

The principle matters more:

```text
Application source
        ≠
Deployment configuration
```

They can be separated.

---

## 6. Application Repository vs GitOps Repository

You might have:

#### Application repo

```text
backend/
├── src/
├── package.json
├── Dockerfile
└── tests/
```

This contains:

```text
application code
tests
Dockerfile
```

Then:

#### GitOps repo

```text
backend-deployment/
├── helm/
│   └── backend/
└── environments/
    ├── dev/
    ├── staging/
    └── production/
```

This contains:

```text
Kubernetes configuration
Helm values
deployment configuration
environment configuration
```

---

## 7. Where Does GitHub Actions Fit?

This is a very important interview question.

GitHub Actions can handle:

```text
CI
```

and potentially:

```text
build artifacts/images
```

ArgoCD handles:

```text
deployment synchronization
```

For example:

```text
Developer
    ↓
Git push
    ↓
GitHub Actions
    ↓
Tests
    ↓
Docker build
    ↓
Push image to ECR
    ↓
Update GitOps repo
    ↓
ArgoCD notices change
    ↓
Kubernetes
```

This creates a clean separation:

```text
CI → GitHub Actions

CD → ArgoCD
```

Not the only possible architecture, but a very common one.

---

## 8. Why Not Just Let GitHub Actions Run `kubectl apply`?

You can.

It's not inherently wrong.

But consider:

```text
GitHub Actions
     ↓
kubectl apply
     ↓
Kubernetes
```

What happens if someone manually changes Kubernetes?

Or if the CI system isn't running?

Or if the cluster drifts away from the configuration?

GitOps gives you continuous reconciliation.

```text
Git
 ↓
ArgoCD
 ↓
Kubernetes
```

ArgoCD continuously checks whether:

```text
desired state == actual state
```

---

## 9. ArgoCD

Argo CD is a declarative GitOps continuous delivery tool for Kubernetes.

Its job is essentially:

```text
Git
 ↓
Read desired configuration
 ↓
Compare with Kubernetes
 ↓
Detect differences
 ↓
Synchronize
 ↓
Kubernetes
```

---

## 10. ArgoCD Architecture

Simplified:

```text
                 Git Repository
                       │
                       ↓
                 ArgoCD Server
                       │
                       ↓
                ArgoCD Controllers
                       │
                       ↓
                  Kubernetes API
                       │
                       ↓
                  Application
```

ArgoCD has multiple components internally, but for interviews you primarily need to understand:

```text
ArgoCD API/UI
Repository access
Application controller
Kubernetes API
```

---

## 11. Install ArgoCD Locally

Since you've already learned Kubernetes with `kind`, we can use that.

Check:

```bash
kubectl get nodes
```

Install ArgoCD:

```bash
kubectl create namespace argocd
```

Then:

```bash
kubectl apply -n argocd \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Check:

```bash
kubectl get pods -n argocd
```

You should eventually see ArgoCD components running.

---

## 12. Access ArgoCD

One simple local-development approach is:

```bash
kubectl port-forward svc/argocd-server \
  -n argocd 8080:443
```

Then access the ArgoCD server through:

```text
https://localhost:8080
```

For local learning, this is enough.

Production access would normally involve proper ingress/load balancing, TLS, authentication, networking, and security.

---

## 13. ArgoCD CLI

Install the ArgoCD CLI appropriate for your OS.

Then:

```bash
argocd version
```

The CLI lets you interact with the ArgoCD server.

---

## 14. ArgoCD Application

The central ArgoCD object is:

```text
Application
```

An ArgoCD Application essentially says:

> "Take this configuration from this Git repository/path and synchronize it to this Kubernetes cluster/namespace."

Example:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application

metadata:
  name: my-api

spec:
  project: default

  source:
    repoURL: https://github.com/example/my-gitops-repo.git
    targetRevision: main
    path: apps/my-api

  destination:
    server: https://kubernetes.default.svc
    namespace: production

  syncPolicy:
    automated: {}
```

This is a **Custom Resource**.

Remember [Chapter 20](../05-kubernetes/ch20-kubernetes-networking-scaling.md)?

We learned that Kubernetes can be extended using CRDs.

ArgoCD uses Kubernetes APIs and custom resources such as:

```text
Application
```

So this also connects directly to [Chapter 29](../05-kubernetes/ch29-crds-operators.md) later.

---

## 15. Understanding the Application YAML

#### Source

```yaml
source:
  repoURL: ...
  targetRevision: main
  path: apps/my-api
```

Means:

```text
Git repository
      ↓
branch/revision
      ↓
directory
```

---

#### Destination

```yaml
destination:
  server: https://kubernetes.default.svc
  namespace: production
```

Means:

```text
which Kubernetes cluster?
which namespace?
```

---

#### Sync Policy

```yaml
syncPolicy:
  automated: {}
```

means ArgoCD can automatically synchronize changes.

---

## 16. Manual vs Automatic Sync

#### Manual

Git changes:

```text
Git
 ↓
ArgoCD detects change
 ↓
OutOfSync
```

You then explicitly synchronize.

#### Automatic

```text
Git
 ↓
change detected
 ↓
ArgoCD
 ↓
sync
 ↓
Kubernetes
```

Automatic synchronization is useful for environments where that operating model is appropriate.

---

## 17. Sync Status

One important ArgoCD concept:

```text
Synced
```

means:

```text
Git desired state
≈
Kubernetes state
```

Whereas:

```text
OutOfSync
```

means:

```text
Git desired state
≠
Kubernetes state
```

This is extremely important.

---

## 18. Health Status

ArgoCD also provides application health information.

Conceptually:

```text
Healthy
Progressing
Degraded
Missing
Unknown
```

This isn't exactly the same thing as sync status.

For example:

```text
Synced + Degraded
```

could mean:

> Kubernetes has the desired manifests, but the deployed application isn't healthy.

That's an important distinction.

---

## 19. GitOps Flow With Helm

Now combine [Chapter 25](../05-kubernetes/ch25-helm.md) and Chapter 26.

Your GitOps repo might contain:

```text
api-chart/
├── Chart.yaml
├── values.yaml
└── templates/
```

ArgoCD can use the Helm chart.

Flow:

```text
Git
 ↓
Helm Chart
 ↓
ArgoCD
 ↓
Helm rendering
 ↓
Kubernetes manifests
 ↓
Kubernetes
```

You don't necessarily need to manually run:

```bash
helm upgrade
```

ArgoCD can manage the application.

---

## 20. Production Example

Suppose your Docker image is:

```text
ECR:
my-api:abc123
```

GitOps repository has:

```yaml
image:
  repository: 123456789.dkr.ecr.ap-south-1.amazonaws.com/my-api
  tag: "abc123"
```

CI builds:

```text
abc123
```

pushes it to ECR, then updates the GitOps configuration:

```yaml
tag: "abc123"
```

Commit:

```text
Deploy my-api abc123
```

ArgoCD sees:

```text
Git changed
```

Then:

```text
Git
 ↓
ArgoCD
 ↓
Helm
 ↓
Kubernetes
 ↓
New Pods
```

---

## 21. Complete GitOps Pipeline

This is the architecture I want you to understand:

```text
                     Developer
                         │
                         ↓
                       Git
                         │
                         ↓
                 GitHub Actions
                         │
                 ┌───────┴───────┐
                 ↓               ↓
              Tests          Docker Build
                                 │
                                 ↓
                                ECR
                                 │
                                 ↓
                        Update GitOps Repo
                                 │
                                 ↓
                           Git Repository
                                 │
                                 ↓
                              ArgoCD
                                 │
                                 ↓
                              EKS
                                 │
                       ┌─────────┼─────────┐
                       ↓         ↓         ↓
                     Pod       Pod       Pod
```

This is a very strong interview architecture.

---

## 22. GitOps vs CI/CD

Don't say:

> "GitOps replaces CI/CD."

Better:

> **GitOps is an approach to continuous delivery/deployment where Git serves as the source of truth and a controller reconciles the cluster with that state.**

You can still have:

```text
CI → GitHub Actions
CD → ArgoCD
```

---

## 23. GitOps vs Infrastructure as Code

Another common question.

#### Terraform

Usually manages infrastructure:

```text
VPC
EKS
RDS
IAM
S3
```

#### GitOps/ArgoCD

Usually manages Kubernetes application state:

```text
Deployment
Service
Ingress
ConfigMap
HPA
```

You might have:

```text
Terraform
    ↓
AWS infrastructure
    ↓
EKS cluster

ArgoCD
    ↓
Kubernetes applications
    ↓
EKS
```

This is a very clean separation.

---

## 24. What About Terraform + ArgoCD?

A common architecture:

```text
Terraform
   ↓
VPC
EKS
IAM
RDS
S3
   ↓
Cluster exists
   ↓
ArgoCD
   ↓
Applications deployed
```

Terraform creates the platform.

ArgoCD manages workloads.

This isn't an absolute rule, but it's a useful mental model.

---

## 25. Drift Detection

This is one of GitOps' biggest advantages.

Git says:

```yaml
replicas: 3
```

Someone manually runs:

```bash
kubectl scale deployment my-api --replicas=10
```

Now:

```text
Desired = 3
Actual = 10
```

ArgoCD detects:

```text
OutOfSync
```

Depending on the sync policy, it can reconcile the cluster back toward Git's declared state.

---

## 26. The Important GitOps Principle

This is worth remembering:

> **Don't treat the Kubernetes cluster as the place where you permanently edit configuration. Treat Git as the place where desired configuration is changed and reviewed.**

Instead of:

```bash
kubectl edit deployment api
```

prefer:

```text
change Git
 ↓
Pull Request
 ↓
Review
 ↓
Merge
 ↓
ArgoCD
 ↓
Kubernetes
```

This gives you an audit trail.

---

## 27. Rollbacks

Suppose:

```text
Production
 ↓
version 1.5
```

You deploy:

```text
version 1.6
```

and it breaks.

With GitOps, you can revert the Git commit:

```text
Git history:

A → B → C → D
            ↑
          broken
```

Revert:

```text
A → B → C → D → E
                ↑
            rollback change
```

ArgoCD detects the desired state change and synchronizes it.

---

## 28. Why GitOps Is Powerful

You gain:

#### Auditability

Who changed production?

```text
Git commit
```

#### Review

Who approved the change?

```text
Pull Request
```

#### Reproducibility

What should production look like?

```text
Git
```

#### Rollback

What was the previous configuration?

```text
Git history
```

#### Drift detection

Does Kubernetes match Git?

```text
ArgoCD
```

---

## 29. GitOps Security

GitOps doesn't magically make deployments secure.

You still need:

```text
RBAC
Secrets management
Least privilege
Image scanning
Signed/verified images where appropriate
Protected branches
PR reviews
CI security
ArgoCD access controls
Kubernetes security
Network security
```

Especially:

**Don't put plaintext production passwords into Git just because it's a GitOps repository.**

Use:

```text
Secrets Manager
External Secrets
Sealed Secrets
Vault
```

or another appropriate secret-management mechanism.

---

## 30. What GitOps Does NOT Mean

GitOps does **not** mean:

> "Everything must be stored directly in Git."

Secrets may need special handling.

It also doesn't mean:

> "Never use kubectl."

You will still use:

```bash
kubectl get
kubectl logs
kubectl describe
```

for debugging and operations.

The important distinction is:

```text
kubectl
→ inspect/debug/operate

GitOps
→ manage desired configuration
```

---

## 31. ArgoCD Troubleshooting

Suppose ArgoCD says:

```text
OutOfSync
```

Check:

```text
Git commit
 ↓
Repository
 ↓
Path
 ↓
Branch/revision
 ↓
Rendered Helm/manifests
 ↓
Kubernetes
```

Possible problems:

```text
wrong repository
wrong branch
wrong path
invalid YAML
wrong values
permission problem
cluster access problem
resource conflict
```

---

## 32. ArgoCD vs Helm

Very common interview question.

They are not direct competitors.

#### Helm

```text
Template/package Kubernetes applications
```

#### ArgoCD

```text
Continuously synchronize desired application state
from Git to Kubernetes
```

They can work together:

```text
Git
 ↓
Helm Chart
 ↓
ArgoCD
 ↓
Kubernetes
```

---

## 33. ArgoCD vs Jenkins

#### Jenkins

General-purpose automation/CI/CD server.

Can do:

```text
build
test
package
deploy
```

#### ArgoCD

Kubernetes-focused GitOps CD controller.

```text
Git
 ↓
ArgoCD
 ↓
Kubernetes
```

A company could use:

```text
Jenkins → CI
ArgoCD → CD
```

---

## 34. ArgoCD vs GitHub Actions

#### GitHub Actions

Excellent for:

```text
CI
tests
builds
Docker images
security scans
artifact creation
```

#### ArgoCD

Excellent for:

```text
Kubernetes deployment
reconciliation
drift detection
GitOps
```

A modern pipeline can therefore be:

```text
GitHub Actions
      ↓
Build + Test + Docker
      ↓
ECR
      ↓
GitOps repo
      ↓
ArgoCD
      ↓
EKS
```

---

## 35. Hands-On Mini Project

Now let's make the concepts real.

You already have:

```text
kind cluster
Helm chart
Node.js API
```

Create:

```text
my-gitops-repo/
└── apps/
    └── my-api/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
```

Put your Helm chart there.

Commit:

```bash
git add .
git commit -m "Add my-api GitOps deployment"
git push
```

Then create an ArgoCD Application pointing to:

```text
your Git repository
        +
apps/my-api
```

ArgoCD will read the chart.

Then:

```text
Git
 ↓
ArgoCD
 ↓
Helm
 ↓
Kubernetes
```

---

## 36. Test GitOps Yourself

Change:

```yaml
replicaCount: 2
```

to:

```yaml
replicaCount: 4
```

Commit:

```bash
git add .
git commit -m "Scale API to four replicas"
git push
```

ArgoCD detects the change.

Then:

```bash
kubectl get pods
```

You should eventually see:

```text
4 Pods
```

You have now experienced GitOps.

---

## 37. Test Drift Detection

Now manually do:

```bash
kubectl scale deployment my-api --replicas=1
```

Check:

```bash
kubectl get deployment
```

Your cluster now differs from Git.

ArgoCD should identify the application as out of sync.

If automated synchronization is enabled, ArgoCD can reconcile it back toward the Git state.

This experiment is **extremely valuable** because it makes the entire GitOps idea click.

---

## 38. Interview Scenario

#### Interviewer:

> A developer manually changed a Kubernetes deployment in production. How would you handle it in a GitOps environment?

Good answer:

> "I'd first determine whether the manual change was intentional. The desired state should normally be changed in the Git repository through the normal review process. I'd check ArgoCD's sync status and Git history, then either revert the manual drift or create the corresponding Git change. If automated sync is enabled, ArgoCD can reconcile the cluster back to the Git-defined state."

That's much stronger than simply saying:

> "Use ArgoCD."

---

## 39. Important Mental Model

Memorize this:

```text
                   GIT
                    │
             Desired State
                    │
                    ↓
                 ArgoCD
                    │
             Reconciliation
                    │
                    ↓
              Kubernetes
                    │
             Actual State
```

If:

```text
Desired = Actual
```

everything is synchronized.

If:

```text
Desired ≠ Actual
```

you have drift/out-of-sync state.

---

## 40. What You Need to Know for Interviews

#### Must know deeply

```text
GitOps
Desired state
Declarative configuration
Reconciliation
Drift
ArgoCD
Application
Sync
Auto-sync
Git as source of truth
Helm + ArgoCD
CI + CD separation
Rollback
```

#### Must be able to do

```text
Install ArgoCD
Create Application
Connect Git repository
Deploy Helm chart
Sync application
Check status
Detect drift
Rollback Git change
Troubleshoot sync problems
```

#### Awareness

```text
App-of-Apps
ApplicationSet
Multi-cluster ArgoCD
Progressive delivery
Argo Rollouts
```

We'll encounter some of these concepts later if useful, but they're not prerequisites for your SWE interviews.

---

## 41. Final Comparison

| Tool | Primary purpose |
|---|---|
| Git | Version control |
| GitHub Actions | CI/automation |
| Docker | Containerization |
| ECR | Container registry |
| Kubernetes | Container orchestration |
| Helm | Kubernetes packaging/templates |
| ArgoCD | GitOps continuous delivery |
| Terraform | Infrastructure as Code |
| Ansible | Configuration management |

Put them together:

```text
Git
 ↓
GitHub Actions
 ↓
Docker
 ↓
ECR
 ↓
GitOps Repository
 ↓
ArgoCD
 ↓
Helm
 ↓
Kubernetes/EKS
 ↓
AWS Infrastructure
```

And Terraform sits underneath managing much of the infrastructure:

```text
Terraform
 ↓
VPC
EKS
RDS
IAM
S3
...
```

---

## 🎯 Chapter 26 Summary

You've now added another important layer:

```text
                GIT
                 │
          Source of Truth
                 │
                 ↓
              GitOps
                 │
                 ↓
              ArgoCD
                 │
             Reconcile
                 │
                 ↓
            Kubernetes
                 │
                Helm
                 │
             Application
```

You should now be able to explain **why GitOps exists, how ArgoCD works, how Helm fits into it, how GitHub Actions and ArgoCD complement each other, what drift is, and how a production GitOps deployment works.**
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 25: Helm: Kubernetes Package Management](../05-kubernetes/ch25-helm.md) · [Chapter 27: Jenkins + Advanced CI/CD](ch27-jenkins-advanced-cicd.md) → · [Revision sheet](../../revision/ch26-revision.md)
