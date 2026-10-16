# Chapter 29 — Kubernetes CRDs + Operators

> **Source:** Response 29 of the original conversation (`source-archive/src-29.txt`, lines 1–1693) · **Part II — Advanced extension (Responses 25–36)**  
> **Study aids:** [Revision sheet](../../revision/ch29-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

We've already learned Kubernetes fundamentals, networking, storage, scaling, Helm, GitOps, and ArgoCD.

Now we're going one level deeper into **how Kubernetes itself can be extended**.

The goal is not to become a Kubernetes platform developer. For your SWE/backend target, you should understand:

- What CRDs are
- What Custom Resources are
- What Controllers are
- What Operators are
- Reconciliation
- Why operators exist
- How CRDs work with `kubectl`
- How to create a simple CRD
- How this connects to Helm/ArgoCD
- Real-world examples
- Troubleshooting
- Interview questions

---

## 1. First: What Kubernetes Already Gives You

You've already worked with:

```text
Pod
Deployment
Service
ConfigMap
Secret
Ingress
HPA
Job
CronJob
StatefulSet
```

These are Kubernetes resources.

For example:

```yaml
apiVersion: apps/v1
kind: Deployment
```

Kubernetes already knows:

> "Deployment means this particular kind of object."

But what if you want Kubernetes to understand a completely new kind of object?

For example:

```text
PostgresCluster
KafkaCluster
RedisCluster
MyApplication
DatabaseBackup
```

Kubernetes doesn't know what those mean by default.

That's where **Custom Resource Definitions** come in.

---

## 2. What Is a CRD?

CRD =

> **Custom Resource Definition**

It allows you to extend the Kubernetes API with your own resource types.

Normally:

```text
Kubernetes
 ├── Pod
 ├── Deployment
 ├── Service
 └── ConfigMap
```

After installing a CRD:

```text
Kubernetes
 ├── Pod
 ├── Deployment
 ├── Service
 ├── ConfigMap
 └── PostgresCluster   ← custom
```

Now Kubernetes recognizes:

```text
PostgresCluster
```

as a valid API resource.

---

## 3. CRD vs Custom Resource

These two terms are easy to confuse.

#### CRD

Defines the **type**.

Think:

```text
CRD
 ↓
"What is a PostgresCluster?"
```

#### Custom Resource

An actual instance.

```text
PostgresCluster
name: production-db
```

Think:

```text
CRD
→ class/schema/type

Custom Resource
→ actual object/instance
```

---

## 4. Simple Analogy

Imagine a programming language.

You define:

```typescript
class User {
    name: string;
}
```

That's similar conceptually to defining a resource type.

Then:

```typescript
const user = new User();
```

is like creating an instance.

So:

```text
CRD
 ↓
defines resource type

Custom Resource
 ↓
instance of that type
```

Not exactly the same internally, but it's a useful mental model.

---

## 5. Why Would We Need This?

Suppose you're building a platform that manages databases.

You want developers to write:

```yaml
apiVersion: databases.example.com/v1
kind: PostgresCluster

metadata:
  name: production-db

spec:
  replicas: 3
  version: "16"
```

That's much easier for developers than asking them to manually create:

```text
StatefulSets
Services
PVCs
Secrets
ConfigMaps
backup jobs
monitoring
```

The platform can hide that complexity.

---

## 6. CRD Alone Isn't Enough

This is **extremely important**.

Suppose you create:

```text
PostgresCluster
```

Kubernetes now knows:

> "This resource type exists."

But Kubernetes doesn't automatically know:

> "How do I create PostgreSQL when somebody creates this resource?"

That's the job of a:

## Controller

---

## 7. What Is a Controller?

A controller watches resources and tries to make:

```text
desired state
```

match:

```text
actual state
```

You've already encountered this concept.

Kubernetes Deployment controller:

```text
Desired:
3 Pods

Actual:
2 Pods

Controller:
Create another Pod
```

So:

```text
Controller
=
reconciliation loop
```

---

## 8. Reconciliation

The fundamental pattern:

```text
          Desired State
                │
                ↓
           Controller
                │
                ↓
          Actual State
                │
                ↓
          Compare
                │
                ↓
         Make changes
                │
                └──────────┐
                           ↓
                     Check again
```

This continuously happens.

---

## 9. Operators

An **Operator** is essentially a Kubernetes controller that understands how to manage a particular application/domain.

For example:

```text
PostgreSQL Operator
```

understands:

```text
PostgreSQL
replication
backups
failover
upgrades
scaling
configuration
```

You tell it:

```yaml
kind: PostgresCluster
```

and the operator handles the operational work.

---

## 10. CRD + Controller + Domain Knowledge

A simplified architecture:

```text
CRD
 ↓
Defines PostgresCluster
       │
       ↓
Custom Resource
       │
       ↓
Postgres Operator
       │
       ↓
Controller
       │
       ├── StatefulSet
       ├── Service
       ├── PVC
       ├── Config
       └── Backup resources
```

This is the Operator pattern.

---

## 11. Why Is It Called an Operator?

Because you're effectively encoding human operational knowledge into software.

A human operator might know:

> "If the database replica fails, recreate it."

> "If the primary fails, promote another replica."

> "Before upgrading PostgreSQL, perform these checks."

An Operator automates that knowledge.

So:

```text
Human operational knowledge
          ↓
      Controller
          ↓
      Automation
```

---

## 12. Kubernetes API Extension

CRDs extend the Kubernetes API.

After installing a CRD:

```bash
kubectl get crd
```

You might see:

```text
postgresclusters.databases.example.com
```

Then:

```bash
kubectl api-resources
```

can show the new resource type.

You can then use:

```bash
kubectl get postgresclusters
```

just like:

```bash
kubectl get deployments
```

That's the power of CRDs.

---

## 13. Create a Simple CRD

Let's create a learning example.

File:

```text
app-crd.yaml
```

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition

metadata:
  name: applications.platform.example.com

spec:

  group: platform.example.com

  names:
    kind: Application
    plural: applications
    singular: application
    shortNames:
      - app

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

                image:
                  type: string

                replicas:
                  type: integer
```

Apply:

```bash
kubectl apply -f app-crd.yaml
```

Check:

```bash
kubectl get crd
```

---

## 14. What Did We Just Create?

We've told Kubernetes:

> "There is a new resource type called `Application`."

Its API group:

```text
platform.example.com
```

Version:

```text
v1
```

Kind:

```text
Application
```

Plural:

```text
applications
```

---

## 15. Create a Custom Resource

Now:

```yaml
apiVersion: platform.example.com/v1
kind: Application

metadata:
  name: my-api

spec:
  image: nginx:latest
  replicas: 3
```

Apply:

```bash
kubectl apply -f application.yaml
```

Then:

```bash
kubectl get applications
```

You should see:

```text
NAME
my-api
```

Kubernetes now stores your custom object.

---

## 16. But Nothing Actually Happens

This is critical.

If you created:

```text
Application
replicas: 3
```

you haven't necessarily created three Pods.

Why?

Because we only created:

```text
CRD
+
Custom Resource
```

We haven't written a controller.

---

## 17. The Missing Piece

We need:

```text
Application Controller
```

that watches:

```text
Application resources
```

and says:

```text
Application says:
replicas = 3

Actual:
Deployment doesn't exist

Therefore:
create Deployment
```

---

## 18. Operator Reconciliation

Imagine:

```text
Application:
image = nginx
replicas = 3
```

Controller sees:

```text
Deployment:
doesn't exist
```

Controller creates:

```text
Deployment
replicas = 3
image = nginx
```

Kubernetes creates:

```text
Pod
Pod
Pod
```

Now:

```text
Desired
  ↓
3 Pods

Actual
  ↓
3 Pods
```

Everything matches.

---

## 19. What If a Pod Dies?

Suppose:

```text
Pod 1
Pod 2
Pod 3
```

Pod 2 crashes.

Kubernetes Deployment controller itself handles the desired replica count.

But the higher-level Operator may also manage application-specific logic.

This layered controller model is important:

```text
Operator
 ↓
Kubernetes resources
 ↓
Kubernetes controllers
 ↓
Pods
```

---

## 20. Operators Don't Replace Kubernetes

An Operator usually works **with** Kubernetes.

For example:

```text
Operator
 ↓
creates/manages
 ↓
Deployment
Service
PVC
Secret
```

Then Kubernetes handles those resources.

So:

```text
Operator
+
Kubernetes controllers
```

work together.

---

## 21. Real-World Operators

You will encounter operators for systems such as:

```text
PostgreSQL
Kafka
Redis
Prometheus
Elasticsearch
MongoDB
```

For example, a PostgreSQL operator may manage:

```text
Postgres clusters
replication
backups
failover
upgrades
```

Instead of manually managing all those pieces.

---

## 22. Operator Example

Conceptually:

```yaml
apiVersion: database.example.com/v1
kind: PostgreSQLCluster

metadata:
  name: production

spec:
  version: "16"
  replicas: 3
  storage: 100Gi
```

You tell the operator:

> "I want this PostgreSQL cluster."

The operator handles the implementation.

---

## 23. Why This Is Powerful

Without an operator:

```text
Human
 ↓
Create resources
 ↓
Configure DB
 ↓
Configure replicas
 ↓
Configure backups
 ↓
Handle failures
 ↓
Upgrade
```

With operator:

```text
Human
 ↓
Declare desired database
 ↓
Operator
 ↓
Automation
```

That's the fundamental idea.

---

## 24. CRD Validation

The CRD can define what values are valid.

For example:

```yaml
replicas:
  type: integer
  minimum: 1
  maximum: 10
```

Now:

```yaml
replicas: 100
```

can be rejected by schema validation.

This prevents invalid resources from entering the system.

---

## 25. Required Fields

You can define:

```yaml
required:
  - image
  - replicas
```

Then a resource missing:

```text
image
```

can fail validation.

---

## 26. Status

Custom resources often have:

```yaml
status:
  phase: Ready
```

The important conceptual separation:

```text
spec
 ↓
What I want

status
 ↓
What currently exists
```

This is a very important Kubernetes pattern.

---

## 27. `spec` vs `status`

Example:

```yaml
spec:
  replicas: 3
```

means:

> I want three replicas.

And:

```yaml
status:
  readyReplicas: 2
```

means:

> Currently only two are ready.

Then the controller keeps reconciling.

```text
spec
 ↓
desired
 ↓
controller
 ↓
actual
 ↓
status
```

---

## 28. Kubernetes Conditions

Many Kubernetes resources use conditions.

For example:

```yaml
status:
  conditions:
    - type: Ready
      status: "True"
```

This lets controllers communicate state.

You don't need to memorize every condition type.

Understand the pattern.

---

## 29. Finalizers

This is a more advanced concept.

Suppose an Operator manages:

```text
cloud database
```

You delete the Kubernetes resource.

Should the operator immediately let Kubernetes remove it?

Maybe not.

The operator may need to:

```text
backup database
 ↓
delete external resources
 ↓
cleanup
 ↓
allow deletion
```

Finalizers can be used to ensure cleanup occurs before an object is fully deleted.

For interviews:

> **A finalizer allows a controller to perform cleanup before Kubernetes completes deletion of a resource.**

That's enough for your target.

---

## 30. Operator Lifecycle

Conceptually:

```text
Create Custom Resource
        ↓
Operator notices
        ↓
Reconcile
        ↓
Create/update resources
        ↓
Monitor state
        ↓
Reconcile again
        ↓
Update status
```

This continues throughout the resource's lifetime.

---

## 31. Operator Pattern

The generic pattern:

```text
Custom Resource
      │
      ↓
Controller
      │
      ↓
Observe
      │
      ↓
Compare desired vs actual
      │
      ↓
Take action
      │
      ↓
Observe again
```

This is basically:

> **a control loop.**

---

## 32. How Operators Are Written

Operators can be written using frameworks/libraries such as:

```text
Kubebuilder
Operator SDK
controller-runtime
```

Common languages include:

```text
Go
```

because much of the Kubernetes ecosystem is written in Go.

You do **not** need to become a Go/Kubernetes operator developer for your current SWE goal.

---

## 33. Why Go Is Common

Kubernetes itself is heavily Go-based.

Go works well for:

```text
concurrent controllers
network services
Kubernetes APIs
cloud infrastructure
```

But again:

**Understanding the Operator pattern is much more important for you than implementing a production operator from scratch.**

---

## 34. CRDs + Helm

Helm can install CRDs.

A Helm chart can package:

```text
CRD
+
Operator
+
Custom Resources
```

For example:

```text
Helm
 ↓
PostgreSQL Operator
 ↓
CRD installed
 ↓
PostgreSQLCluster resource
 ↓
Operator manages database
```

This is a very common Kubernetes ecosystem pattern.

---

## 35. CRDs + ArgoCD

This connects directly to [Chapter 26](../03-cicd-gitops/ch26-gitops-argocd.md).

ArgoCD can manage CRDs and custom resources through GitOps.

```text
Git
 ↓
ArgoCD
 ↓
CRD
 ↓
Custom Resource
 ↓
Operator
 ↓
Application
```

For example:

```text
Git:
PostgreSQLCluster
        ↓
ArgoCD
        ↓
Kubernetes
        ↓
Postgres Operator
        ↓
PostgreSQL cluster
```

This is a powerful combination.

---

## 36. CRDs + Terraform

You can also see:

```text
Terraform
 ↓
EKS
 ↓
Helm
 ↓
Operator
 ↓
Custom Resource
```

For example, Terraform might provision:

```text
AWS infrastructure
```

while Helm installs:

```text
database operator
```

and GitOps manages:

```text
custom database resources
```

---

## 37. Why Operators Matter in Platform Engineering

Imagine a company has 200 development teams.

They don't want every team to understand:

```text
Kubernetes networking
storage
database replication
backups
failover
```

A platform team can expose:

```yaml
kind: PostgresCluster
```

and hide the implementation complexity.

This creates an internal platform:

```text
Developer
   ↓
Simple Custom Resource
   ↓
Platform Operator
   ↓
Complex infrastructure
```

This is a major reason operators are valuable.

---

## 38. Operator vs Helm

Important distinction.

#### Helm

Mostly:

```text
Template
Package
Install
Upgrade
```

#### Operator

Actively manages application lifecycle:

```text
Observe
Reconcile
Recover
Scale
Backup
Upgrade
```

Think:

```text
Helm
→ "Install this configuration."

Operator
→ "Continuously manage this application."
```

---

## 39. Operator vs Controller

A controller is a general Kubernetes reconciliation component.

An Operator is commonly understood as a controller that encodes operational knowledge for a specific application/domain.

So:

```text
Controller
→ general concept

Operator
→ application/domain-focused controller
```

Every Operator involves controller behavior, but not every Kubernetes controller is typically called an Operator.

---

## 40. Troubleshooting CRDs

Suppose:

```bash
kubectl get applications
```

fails.

Check:

```bash
kubectl get crd
```

Maybe the CRD wasn't installed.

---

#### CRD exists but resource fails

Check:

```bash
kubectl describe application my-api
```

Look for:

```text
validation errors
events
spec problems
```

---

#### Resource exists but nothing happens

This is a classic problem.

Maybe:

```text
CRD exists
Custom Resource exists
Operator isn't running
```

Check:

```bash
kubectl get pods -n <operator-namespace>
```

Then:

```bash
kubectl logs <operator-pod>
```

---

## 41. Operator CrashLoopBackOff

Use your Kubernetes troubleshooting skills:

```bash
kubectl get pods
kubectl describe pod <operator-pod>
kubectl logs <operator-pod>
kubectl logs <operator-pod> --previous
```

Now you're combining:

```text
Kubernetes troubleshooting
+
CRD/operator knowledge
```

---

## 42. RBAC Problems

Operators need permissions.

Suppose the Operator needs to create:

```text
Deployments
Services
Secrets
PVCs
```

but its ServiceAccount lacks permissions.

Then you'll see failures.

Conceptually:

```text
Operator
 ↓
Kubernetes API
 ↓
RBAC
 ↓
DENIED
```

Check:

```bash
kubectl auth can-i ...
```

This is why:

> **Operators are software running inside Kubernetes and are subject to Kubernetes security/RBAC.**

---

## 43. Real Production Example

Imagine your company runs Kafka.

Instead of manually creating dozens of Kafka-related resources:

```text
Kafka brokers
Services
Storage
Users
Topics
Monitoring
```

you might install a Kafka Operator.

Then developers could define:

```yaml
kind: Kafka
metadata:
  name: events
spec:
  replicas: 3
```

The operator handles the operational details.

---

## 44. Interview Scenario

#### Interviewer:

> What happens if I create a Custom Resource?

Good answer:

> "The CRD defines the resource type and Kubernetes stores the Custom Resource. However, creating the CR alone doesn't automatically implement application-specific behavior. A controller or Operator must watch that resource and reconcile its desired state by creating or updating the underlying Kubernetes resources."

That's an excellent answer.

---

## 45. Interview Scenario 2

> What's the difference between a CRD and an Operator?

Answer:

```text
CRD
→ defines a new Kubernetes API resource type

Operator
→ controller that watches resources and implements
  application-specific reconciliation logic
```

---

## 46. Interview Scenario 3

> Why use an Operator instead of Helm?

Answer:

> Helm is primarily a packaging and templating mechanism for Kubernetes resources, whereas an Operator continuously observes and manages an application's lifecycle using reconciliation logic.

---

## 47. Interview Scenario 4

> What is reconciliation?

Answer:

> Reconciliation is the process of comparing desired state with actual state and taking actions to make actual state converge toward the desired state.

This is one of the most important Kubernetes concepts.

---

## 48. Interview Scenario 5

> Why are Operators useful?

Answer:

> They encode domain-specific operational knowledge into software, allowing Kubernetes to automate complex lifecycle tasks such as provisioning, backups, failover, upgrades, and recovery.

---

## 49. The Big Picture

You've now learned:

```text
Kubernetes
│
├── Built-in Resources
│     ├── Pod
│     ├── Deployment
│     ├── Service
│     └── ...
│
└── Extensions
      │
      ├── CRD
      │     ↓
      │   Custom Resource
      │
      └── Operator
            ↓
        Controller
            ↓
        Reconciliation
```

---

## 50. How This Fits Your Entire Stack

Your DevOps architecture is becoming:

```text
                       Git
                        │
                        ↓
                   GitHub Actions
                        │
                        ↓
                      Docker
                        │
                        ↓
                       ECR
                        │
                        ↓
                     GitOps
                        │
                        ↓
                     ArgoCD
                        │
                        ↓
                      Helm
                        │
                        ↓
                      EKS
                        │
              ┌─────────┴─────────┐
              ↓                   ↓
         Kubernetes          Operators
              │                   │
              ↓                   ↓
           Services         Custom Resources
              │
              ↓
             Pods
```

Terraform sits underneath:

```text
Terraform
 ↓
AWS infrastructure
 ↓
EKS
```

---

## 51. What You Need to Know

For your target SWE/backend role:

#### 🔥 Know well

```text
CRD
Custom Resource
Controller
Operator
Reconciliation
spec vs status
Desired vs actual state
Finalizers
CRD validation
RBAC
CRDs + Helm
CRDs + ArgoCD
Operator troubleshooting
```

#### 🟡 Awareness

```text
Kubebuilder
Operator SDK
controller-runtime
Admission Webhooks
Conversion Webhooks
Multi-version CRDs
Advanced controller internals
```

You don't need to write a 10,000-line Kubernetes Operator.

---

## 52. One Thing to Remember

If you remember only this:

```text
CRD
 ↓
defines a new Kubernetes resource

Custom Resource
 ↓
an instance of that resource

Controller
 ↓
watches the resource

Operator
 ↓
application-specific controller

Reconciliation
 ↓
desired state → actual state
```

you've understood the core.

---

## 🎯 Chapter 29 Summary

We've covered:

```text
✅ CRDs
✅ Custom Resources
✅ CRD vs Custom Resource
✅ Controllers
✅ Operators
✅ Reconciliation
✅ Desired vs actual state
✅ spec vs status
✅ Conditions
✅ Finalizers
✅ CRD validation
✅ Custom API resources
✅ Operator architecture
✅ Operator lifecycle
✅ Helm + CRDs
✅ ArgoCD + CRDs
✅ Terraform + Operators
✅ RBAC
✅ Operator troubleshooting
✅ Real-world Operator examples
✅ Platform engineering use cases
```

And you've now moved from simply **using Kubernetes** to understanding **how Kubernetes can be extended**.
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 28: Ansible: Configuration Management & Automation](../06-iac-config/ch28-ansible.md) · [Chapter 30: Service Mesh + Istio](ch30-service-mesh-istio.md) → · [Revision sheet](../../revision/ch29-revision.md)
