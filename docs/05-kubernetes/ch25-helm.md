# Chapter 25 — Helm: Kubernetes Package Management

> **Source:** Response 25 of the original conversation (`source-archive/src-25.txt`, lines 1–1672) · **Part II — Advanced extension (Responses 25–36)**  
> **Study aids:** [Revision sheet](../../revision/ch25-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

We're now entering the **advanced/remaining DevOps section**.

You've already learned Kubernetes manifests, Deployments, Services, ConfigMaps, Secrets, HPA, Ingress, etc. Helm builds directly on that knowledge.

The goal here is **not just to know that Helm exists**. By the end, you should understand how to create, configure, install, upgrade, rollback, and troubleshoot a Helm-based Kubernetes application.

---

## 1. First: Why Do We Need Helm?

Suppose your application has:

```text
deployment.yaml
service.yaml
configmap.yaml
secret.yaml
ingress.yaml
hpa.yaml
```

Without Helm, you might have:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f configmap.yaml
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml
```

That's okay for one application.

But imagine you deploy:

```text
dev
staging
production
```

and each environment has different:

```text
image
replicas
CPU
memory
hostname
database configuration
```

You don't want to copy-paste five versions of every YAML file.

That's where **Helm** comes in.

---

## 2. What Is Helm?

Think of Helm as:

> **A package manager and templating system for Kubernetes applications.**

Similar idea:

```text
npm
 ↓
packages for Node.js

apt
 ↓
packages for Linux

Helm
 ↓
packages/releases for Kubernetes
```

Helm packages Kubernetes resources into something called a:

## Chart

A Helm Chart contains:

```text
templates
configuration
metadata
```

that can generate Kubernetes manifests.

---

## 3. The Problem Helm Solves

Without Helm:

```text
deployment-dev.yaml
deployment-staging.yaml
deployment-prod.yaml
```

With Helm:

```text
templates/deployment.yaml

values.yaml
values-dev.yaml
values-prod.yaml
```

Then:

```bash
helm install my-api ./my-chart -f values-dev.yaml
```

or:

```bash
helm install my-api ./my-chart -f values-prod.yaml
```

Same chart.

Different configuration.

---

## 4. Helm Architecture

The important pieces are:

```text
Helm CLI
   │
   ↓
Chart
   │
   ├── Templates
   ├── Values
   ├── Chart metadata
   └── Optional dependencies
        │
        ↓
Kubernetes manifests
        │
        ↓
Kubernetes API
```

You interact with Helm using:

```bash
helm
```

---

## 5. Installing Helm

On Linux/macOS, one common installation method is:

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

Verify:

```bash
helm version
```

You should see the Helm version.

For your learning environment, you can use the Kubernetes cluster you already created with `kind`.

Check:

```bash
kubectl get nodes
```

---

## 6. Create Your First Chart

Run:

```bash
helm create my-api
```

You'll get something like:

```text
my-api/
├── Chart.yaml
├── values.yaml
├── charts/
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   ├── serviceaccount.yaml
│   ├── _helpers.tpl
│   └── tests/
└── .helmignore
```

This is your first Helm Chart.

---

## 7. Chart.yaml

Open:

```text
Chart.yaml
```

Example:

```yaml
apiVersion: v2
name: my-api
description: A Helm chart for my Node.js API
type: application
version: 0.1.0
appVersion: "1.0.0"
```

Understand the difference:

#### `version`

Version of the **Chart**.

```text
0.1.0
```

#### `appVersion`

Version of the **application**.

```text
1.0.0
```

They aren't necessarily the same.

---

## 8. values.yaml

This is one of the most important Helm concepts.

Example:

```yaml
replicaCount: 2

image:
  repository: my-api
  tag: "1.0.0"

service:
  type: ClusterIP
  port: 80

containerPort: 3000

resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

These are configurable values.

Instead of hardcoding them inside your Kubernetes manifests, your templates reference them.

---

## 9. Helm Templates

Suppose normal Kubernetes YAML says:

```yaml
spec:
  replicas: 3
```

Helm can turn it into:

```yaml
spec:
  replicas: {{ .Values.replicaCount }}
```

Now:

```yaml
replicaCount: 3
```

produces:

```yaml
replicas: 3
```

If you change:

```yaml
replicaCount: 5
```

Helm produces:

```yaml
replicas: 5
```

That's the basic idea.

---

## 10. What Is `.Values`?

This:

```text
.Values
```

represents values supplied to the Helm chart.

For example:

```yaml
image:
  repository: my-api
  tag: "1.0.0"
```

Then:

```yaml
{{ .Values.image.repository }}
```

becomes:

```text
my-api
```

and:

```yaml
{{ .Values.image.tag }}
```

becomes:

```text
1.0.0
```

---

## 11. Example Deployment Template

A simplified Helm template:

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

Notice:

```text
{{ ... }}
```

Helm replaces these expressions with actual values.

---

## 12. What Is `.Release.Name`?

When you install:

```bash
helm install my-api ./my-api
```

the release name is:

```text
my-api
```

Then:

```yaml
{{ .Release.Name }}
```

becomes:

```text
my-api
```

You can use it to generate resource names.

---

## 13. Render Without Installing

This is extremely useful.

Run:

```bash
helm template my-api ./my-api
```

Helm generates the Kubernetes YAML locally.

You can inspect exactly what Kubernetes would receive.

This is one of the first debugging commands you should remember.

---

## 14. Helm Lint

Run:

```bash
helm lint ./my-api
```

This checks the chart for common problems.

Typical workflow:

```text
edit chart
   ↓
helm lint
   ↓
helm template
   ↓
helm install/upgrade
```

---

## 15. Installing a Chart

Run:

```bash
helm install my-api ./my-api
```

Check:

```bash
helm list
```

Then:

```bash
kubectl get pods
```

and:

```bash
kubectl get svc
```

---

## 16. Helm Release

This is an important word.

A **Chart** is the package/template.

A **Release** is an installed instance of that chart.

Think:

```text
Chart
  │
  ├── Release: dev
  ├── Release: staging
  └── Release: production
```

For example:

```bash
helm install dev-api ./my-api
helm install prod-api ./my-api
```

Same chart.

Two releases.

---

## 17. Different Environments

This is where Helm becomes really useful.

Create:

```text
values.yaml
values-dev.yaml
values-prod.yaml
```

Base:

```yaml
replicaCount: 2

image:
  repository: my-api
  tag: "latest"
```

Development:

```yaml
replicaCount: 1

image:
  tag: "dev"
```

Production:

```yaml
replicaCount: 5

image:
  tag: "1.4.2"
```

Then:

#### Development

```bash
helm install dev-api ./my-api \
  -f values-dev.yaml
```

#### Production

```bash
helm install prod-api ./my-api \
  -f values-prod.yaml
```

---

## 18. Helm Upgrade

Suppose production currently has:

```text
image: my-api:1.4.2
```

You build:

```text
my-api:1.5.0
```

Change:

```yaml
image:
  tag: "1.5.0"
```

Then:

```bash
helm upgrade prod-api ./my-api \
  -f values-prod.yaml
```

Helm updates the release.

---

## 19. Helm History

You can inspect previous releases:

```bash
helm history prod-api
```

You may see:

```text
REVISION   STATUS
1          deployed
2          deployed
3          deployed
```

This is extremely useful for deployments.

---

## 20. Helm Rollback

Suppose revision 3 introduced a bug.

You can rollback:

```bash
helm rollback prod-api 2
```

Then:

```bash
helm history prod-api
```

Verify Kubernetes:

```bash
kubectl get pods
```

This gives you a clean deployment-management workflow.

---

## 21. Helm vs kubectl

This distinction is important.

#### kubectl

Directly manages Kubernetes resources.

```bash
kubectl apply -f deployment.yaml
```

#### Helm

Manages applications/releases composed of Kubernetes resources.

```bash
helm upgrade prod-api ./my-api
```

Think:

```text
kubectl
→ Kubernetes resource management

Helm
→ Kubernetes application packaging + release management
```

Helm still ultimately works with Kubernetes resources.

---

## 22. Helm vs Docker

Another common interview question.

#### Docker

Packages:

```text
application
+
dependencies
```

into:

```text
container image
```

#### Helm

Packages:

```text
Kubernetes manifests
+
configuration
```

into:

```text
Helm Chart
```

So:

```text
Source code
 ↓
Docker
 ↓
Container Image
 ↓
Helm
 ↓
Kubernetes deployment
```

---

## 23. Helm vs Terraform

Another important distinction.

#### Terraform

Primarily manages **infrastructure**.

For example:

```text
VPC
EKS
RDS
S3
IAM
```

#### Helm

Primarily manages **Kubernetes applications/resources**.

For example:

```text
Deployment
Service
Ingress
ConfigMap
HPA
```

A realistic architecture can use both:

```text
Terraform
    ↓
AWS infrastructure
    ↓
EKS
    ↓
Helm
    ↓
Applications
```

---

## 24. Helm Dependencies

A chart can depend on other charts.

For example, your application might need:

```text
Redis
PostgreSQL
```

A chart can declare dependencies.

But in production, you often won't install a production database directly inside your application chart if you're using managed services.

For your AWS architecture:

```text
Terraform
 ↓
RDS
 ↓
PostgreSQL
```

and:

```text
Helm
 ↓
Node.js API
```

This separation is cleaner.

---

## 25. Helm Repositories

Helm charts can be distributed through chart repositories.

Conceptually:

```text
Chart Repository
       ↓
    helm repo
       ↓
      Chart
       ↓
    Install
```

Common commands:

```bash
helm repo add <name> <url>
helm repo update
helm search repo <name>
```

Then:

```bash
helm install ...
```

You don't need to memorize specific public repositories for interviews.

Understand the mechanism.

---

## 26. Helm Packaging

You can package a chart:

```bash
helm package ./my-api
```

You might get:

```text
my-api-0.1.0.tgz
```

This is a distributable chart package.

---

## 27. Helm Values Precedence

Suppose:

`values.yaml`

contains:

```yaml
replicaCount: 2
```

and:

`values-prod.yaml`

contains:

```yaml
replicaCount: 5
```

and command line:

```bash
helm upgrade prod-api ./my-api \
  -f values-prod.yaml \
  --set replicaCount=10
```

The more specific override wins.

Conceptually:

```text
Default values
      ↓
values file
      ↓
--set
```

So:

```text
replicaCount = 10
```

---

## 28. Helm Secrets — Important Security Point

Don't assume Helm makes secrets secure.

For example:

```yaml
databasePassword: mypassword
```

inside:

```text
values.yaml
```

is a bad idea.

Better architecture:

```text
AWS Secrets Manager
       ↓
External Secrets / secret integration
       ↓
Kubernetes Secret
       ↓
Pod
```

or another proper secret-management system.

Helm is primarily a packaging/deployment tool, **not a secret-management solution**.

---

## 29. Helm + Your Node.js API

Let's imagine your backend:

```text
Node.js + TypeScript
```

Docker image:

```text
123456789.dkr.ecr.ap-south-1.amazonaws.com/my-api:1.2.0
```

Your `values-prod.yaml`:

```yaml
replicaCount: 4

image:
  repository: 123456789.dkr.ecr.ap-south-1.amazonaws.com/my-api
  tag: "1.2.0"

service:
  type: ClusterIP
  port: 80

containerPort: 3000
```

Helm generates:

```text
Deployment
Service
Ingress
ConfigMap
HPA
```

Kubernetes then runs:

```text
ECR Image
    ↓
Deployment
    ↓
4 Pods
    ↓
Service
    ↓
Ingress
    ↓
Load Balancer
```

---

## 30. Helm + CI/CD

Now we connect this to everything you've learned.

Your pipeline can become:

```text
Developer
    ↓
Git push
    ↓
GitHub
    ↓
GitHub Actions
    ↓
Tests
    ↓
Build
    ↓
Docker image
    ↓
Push to ECR
    ↓
Helm upgrade
    ↓
Kubernetes
```

For example:

```bash
helm upgrade --install my-api ./helm/my-api \
  --namespace production \
  --create-namespace \
  -f ./helm/my-api/values-prod.yaml \
  --set image.tag=$GITHUB_SHA
```

This is a very realistic deployment pattern.

---

## 31. Why Use Image Tags Like Git SHA?

Instead of:

```text
my-api:latest
```

use:

```text
my-api:8f42c91
```

where:

```text
8f42c91
```

identifies a Git commit.

Then you can know:

```text
production
 ↓
image 8f42c91
 ↓
Git commit 8f42c91
```

This makes deployments traceable and rollback easier.

---

## 32. `helm upgrade --install`

You'll see this frequently:

```bash
helm upgrade --install my-api ./my-api
```

Meaning roughly:

```text
If release doesn't exist:
    install it

If it exists:
    upgrade it
```

Very useful in CI/CD.

---

## 33. Helm Dry Run

Before applying:

```bash
helm upgrade my-api ./my-api \
  --dry-run
```

This can help detect rendering/configuration issues before making the change.

Combine with:

```bash
helm template
```

for debugging.

---

## 34. Helm Debugging Workflow

Suppose your deployment is broken.

Don't immediately blame Kubernetes.

Start:

```bash
helm status my-api
```

Then:

```bash
helm get values my-api
```

Then:

```bash
helm get manifest my-api
```

This lets you inspect what Helm actually deployed.

Then move into Kubernetes:

```bash
kubectl get pods
kubectl describe pod <pod>
kubectl logs <pod>
```

Mental model:

```text
Helm configuration
       ↓
Rendered YAML
       ↓
Kubernetes resources
       ↓
Pods
       ↓
Application
```

Find where the failure occurred.

---

## 35. Common Helm Problems

#### Problem 1 — Template syntax error

Example:

```text
unexpected EOF
```

Check:

```bash
helm lint ./my-api
```

---

#### Problem 2 — Wrong value

You expected:

```text
replicas = 5
```

but got:

```text
replicas = 2
```

Check:

```bash
helm get values my-api
```

and:

```bash
helm template ...
```

---

#### Problem 3 — Correct Helm deployment, broken Pod

Helm can successfully deploy malformed application configuration.

Then Kubernetes may show:

```text
CrashLoopBackOff
```

Now use:

```bash
kubectl logs
kubectl describe
```

Helm isn't the problem anymore.

---

## 36. Helm Interview Questions

#### Q1. What is Helm?

> Helm is a package manager and templating/release-management tool for Kubernetes applications.

---

#### Q2. What is a Helm Chart?

> A package containing Kubernetes templates, configuration values, metadata, and optionally dependencies.

---

#### Q3. Chart vs Release?

```text
Chart
→ package/template

Release
→ installed instance of that chart
```

---

#### Q4. Why use Helm?

Main reasons:

```text
templating
configuration management
reusable deployments
versioning
upgrades
rollbacks
```

---

#### Q5. Helm vs kubectl?

```text
kubectl
→ directly interacts with Kubernetes resources

Helm
→ packages/configures/manages Kubernetes applications
```

---

#### Q6. Helm vs Terraform?

```text
Terraform
→ infrastructure

Helm
→ Kubernetes applications
```

Although their boundaries can overlap in real setups.

---

#### Q7. How do you rollback?

```bash
helm history my-api
helm rollback my-api 2
```

---

#### Q8. How do you see what Helm rendered?

```bash
helm template my-api ./my-api
```

---

#### Q9. How do you inspect an installed release?

```bash
helm status my-api
helm get values my-api
helm get manifest my-api
```

---

#### Q10. Should you store plaintext passwords in `values.yaml`?

**No.**

Use a proper secret-management mechanism.

---

## 37. Your Hands-On Helm Lab

Now actually do this.

#### Step 1 — Create chart

```bash
helm create my-api
```

#### Step 2 — Inspect

```bash
cd my-api
ls
```

#### Step 3 — Validate

```bash
helm lint .
```

#### Step 4 — Render

```bash
helm template my-api .
```

#### Step 5 — Install

```bash
helm install my-api .
```

#### Step 6 — Check

```bash
helm list
kubectl get pods
kubectl get svc
```

#### Step 7 — Change replicas

Edit:

```yaml
replicaCount: 3
```

Then:

```bash
helm upgrade my-api .
```

Check:

```bash
kubectl get pods
```

---

## 38. Then Break It

This is where actual learning happens.

Change:

```yaml
image:
  repository: nonexistent-image
```

Run:

```bash
helm upgrade my-api .
```

Then:

```bash
kubectl get pods
```

You'll probably see something like:

```text
ImagePullBackOff
```

Now troubleshoot:

```bash
kubectl describe pod <pod>
```

Fix the image.

Then upgrade again.

---

## 39. Practice Environment Configuration

Create:

```text
values-dev.yaml
values-prod.yaml
```

Dev:

```yaml
replicaCount: 1

image:
  tag: "dev"
```

Prod:

```yaml
replicaCount: 3

image:
  tag: "1.0.0"
```

Deploy:

```bash
helm install dev-api . -f values-dev.yaml
```

and:

```bash
helm install prod-api . -f values-prod.yaml
```

Now you've demonstrated one of Helm's most important real-world use cases.

---

## 40. What You Actually Need to Remember

Don't memorize hundreds of Helm template functions.

For your SWE/backend role, remember this:

```text
Helm
 ↓
Chart
 ↓
values.yaml
 ↓
Templates
 ↓
Rendered Kubernetes YAML
 ↓
Release
```

And these commands:

```bash
helm create
helm lint
helm template
helm install
helm upgrade
helm upgrade --install
helm list
helm status
helm history
helm rollback
helm get values
helm get manifest
helm uninstall
```

If you know those and understand what happens underneath, you're in good shape.

---

## 41. Helm in Your Final Production Architecture

Eventually your stack becomes:

```text
                    GitHub
                       │
                       ↓
                GitHub Actions
                       │
              ┌────────┴────────┐
              ↓                 ↓
           Docker           Terraform
              │                 │
              ↓                 ↓
             ECR                AWS
              │                 │
              └────────┬────────┘
                       ↓
                      EKS
                       │
                     Helm
                       │
              ┌────────┼────────┐
              ↓        ↓        ↓
          Deployment Service   HPA
              │
             Pods
              │
       ┌──────┼───────┐
       ↓      ↓       ↓
     Redis   RDS      S3
```

This is exactly where Helm fits into the larger DevOps system you've been learning.

---

## 🎯 Chapter 25 Takeaway

You should now understand:

```text
✅ Why Helm exists
✅ What a Chart is
✅ What a Release is
✅ Chart.yaml
✅ values.yaml
✅ Templates
✅ .Values
✅ .Release
✅ Environment-specific values
✅ helm install
✅ helm upgrade
✅ helm rollback
✅ Helm history
✅ Helm repositories
✅ Chart dependencies
✅ Helm vs kubectl
✅ Helm vs Docker
✅ Helm vs Terraform
✅ Helm + ECR
✅ Helm + Kubernetes
✅ Helm + GitHub Actions
✅ Helm debugging
✅ Helm security considerations
```

#### One-line interview answer:

> **Helm lets us package and template Kubernetes applications so that the same deployment definitions can be reused across environments with different configuration, while also providing release versioning, upgrades, and rollbacks.**
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 24: Complete Cloud + DevOps Interview & OA Mastery](../09-interview/ch24-interview-oa-mastery.md) · [Chapter 26: GitOps + ArgoCD](../03-cicd-gitops/ch26-gitops-argocd.md) → · [Revision sheet](../../revision/ch25-revision.md)
