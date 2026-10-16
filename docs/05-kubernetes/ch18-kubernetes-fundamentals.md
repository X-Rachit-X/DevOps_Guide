# Chapter 18 — Kubernetes Fundamentals

> **Source:** Response 18 of the original conversation (`source-archive/src-18.txt`, lines 11–2172) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch18-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

### What Kubernetes Actually Solves

You've already learned Docker.

You can run:

```text
Docker
  ↓
Node.js container
```

For one application:

```text
EC2
 └── Docker
      └── Node.js
```

Fine.

But imagine:

```text
100 containers
10 servers
multiple applications
multiple environments
frequent deployments
failed containers
scaling requirements
```

Manually managing them becomes painful.

That's the problem Kubernetes solves.

---

## 1. What Is Kubernetes?

Kubernetes is a **container orchestration platform**.

Simple definition:

> **Kubernetes manages containers across a cluster of machines.**

Instead of manually doing:

```bash
docker run ...
docker stop ...
docker restart ...
docker scale ...
```

you tell Kubernetes what you want:

```text
"I want 5 copies of my API running."
```

Kubernetes works toward maintaining that desired state.

---

## 2. Docker vs Kubernetes

This distinction is extremely important.

#### Docker

Runs containers.

```text
Docker
 ↓
Container
 ↓
Node.js
```

#### Kubernetes

Manages containers at scale.

```text
Kubernetes
 ├── Node
 │    ├── Container
 │    └── Container
 │
 ├── Node
 │    ├── Container
 │    └── Container
 │
 └── Node
      └── Container
```

Think:

```text
Docker
→ container technology

Kubernetes
→ container orchestration
```

---

## 3. Why Not Just Docker?

Suppose you have:

```text
EC2-A
 ├── API
 ├── Worker
 └── Payments

EC2-B
 ├── API
 ├── Worker
 └── Payments
```

Now:

```text
EC2-A crashes
```

What happens?

You need automation to:

- detect failure
- restart workloads
- place them somewhere else
- maintain desired replicas
- route traffic
- manage configuration
- perform deployments

Kubernetes is designed to solve these orchestration problems.

---

## 4. Kubernetes Cluster

A Kubernetes environment is called a **cluster**.

Conceptually:

```text
Kubernetes Cluster
│
├── Control Plane
│
└── Worker Nodes
     ├── Node
     ├── Node
     └── Node
```

---

## 5. Control Plane

The control plane is responsible for managing the cluster.

Conceptually:

```text
Control Plane
│
├── API Server
├── Scheduler
├── Controller Manager
└── etcd
```

You don't need to memorize implementation details yet. Understand their responsibilities.

---

## 6. API Server

The API Server is essentially the main interface to Kubernetes.

When you run:

```bash
kubectl get pods
```

you're interacting with the Kubernetes API.

Conceptually:

```text
kubectl
   ↓
API Server
   ↓
Kubernetes
```

---

## 7. etcd

`etcd` is the distributed key-value store used by Kubernetes for cluster state.

Conceptually:

```text
Kubernetes
    ↓
etcd
    ↓
Cluster state
```

For example, Kubernetes needs to know things such as:

```text
What deployments exist?
How many replicas are desired?
What configuration is stored?
What cluster objects exist?
```

You generally don't manually manipulate etcd.

For your interview level:

> **etcd stores Kubernetes cluster state.**

That's enough.

---

## 8. Scheduler

Suppose you request:

```text
5 Pods
```

Kubernetes needs to determine:

> Which worker node should run each Pod?

That's the scheduler's responsibility.

```text
Pod
 ↓
Scheduler
 ↓
Node A
```

or:

```text
Pod
 ↓
Scheduler
 ↓
Node B
```

It considers resource availability and scheduling constraints.

---

## 9. Controller Manager

Controllers continuously compare:

```text
Desired state
```

with:

```text
Actual state
```

Example:

You specify:

```text
replicas: 3
```

but currently:

```text
2 Pods
```

Controller logic notices:

```text
Desired = 3
Actual = 2
```

and Kubernetes works toward:

```text
3 Pods
```

This is the heart of Kubernetes.

---

## 10. Desired State

This concept is **extremely important**.

You don't normally tell Kubernetes:

```text
"Start container A.
Then wait.
Then start container B."
```

Instead:

```yaml
replicas: 3
```

You're saying:

> **I want 3 replicas to exist.**

Kubernetes continuously tries to make reality match your declaration.

---

## 11. Worker Node

A worker node is a machine that runs workloads.

Conceptually:

```text
Worker Node
│
├── kubelet
├── container runtime
└── Pods
```

The container runtime actually runs the containers.

Modern Kubernetes environments commonly use **containerd** or another CRI-compatible runtime rather than Docker Engine itself.

This is an important clarification:

> **Kubernetes does not require Docker Engine to run containers.**

Your Docker knowledge is still extremely valuable because you're learning container images, Dockerfiles, registries, networking, volumes, etc.

---

## 12. kubelet

`kubelet` runs on each worker node.

It communicates with the Kubernetes control plane and makes sure the workloads assigned to that node are running.

Conceptually:

```text
Control Plane
     ↓
  kubelet
     ↓
   Node
     ↓
   Pods
```

---

## 13. Pod

Now the most important Kubernetes object:

> **Pod**

A Pod is the smallest deployable unit in Kubernetes.

Most commonly:

```text
Pod
 └── Container
      └── Node.js
```

But a Pod can contain multiple tightly coupled containers:

```text
Pod
├── Container A
└── Container B
```

For your normal backend:

```text
Pod
 └── Node.js container
```

is the common mental model.

---

## 14. Docker Container vs Kubernetes Pod

Don't say:

> Pod = container.

That's not technically correct.

Think:

```text
Pod
 └── Container
```

A Pod provides a shared execution/network context for its containers.

Multiple containers in one Pod can share:

- network namespace
- localhost
- volumes where configured

Example:

```text
Pod
├── API container
└── Sidecar container
```

The API could reach the sidecar through localhost.

But don't put unrelated applications into one Pod just because you can.

---

## 15. Pod IP

Pods receive IP addresses within the Kubernetes networking model.

Example:

```text
Pod A
10.x.x.x

Pod B
10.x.x.x
```

But here's an important point:

> **Pod IPs are generally ephemeral.**

A Pod can die and be replaced.

The replacement may receive a different IP.

Therefore:

```text
Client
  ↓
Pod IP ❌
```

is generally not how you expose an application.

That's why Kubernetes has **Services**.

---

## 16. Creating Your First Pod

Here's a basic Pod manifest.

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

This says:

```text
Create a Pod
 ↓
Run node:22 container
 ↓
Container port = 3000
```

But this isn't yet a useful production deployment.

We'll improve it.

---

## 17. kubectl

`kubectl` is the primary command-line tool for interacting with Kubernetes.

Think:

```text
kubectl
   ↓
Kubernetes API
```

Common commands:

```bash
kubectl get pods
```

```bash
kubectl describe pod api-pod
```

```bash
kubectl logs api-pod
```

```bash
kubectl exec -it api-pod -- sh
```

```bash
kubectl delete pod api-pod
```

These commands are extremely important.

---

## 18. Create the Pod

Save:

```text
pod.yaml
```

Then:

```bash
kubectl apply -f pod.yaml
```

Check:

```bash
kubectl get pods
```

You might see:

```text
NAME       READY   STATUS    RESTARTS
api-pod    1/1     Running   0
```

---

## 19. Describe a Pod

If something is wrong:

```bash
kubectl describe pod api-pod
```

This can show:

- events
- scheduling information
- container state
- image
- volumes
- networking information
- errors

Very useful for troubleshooting.

---

## 20. Pod Logs

Application logs:

```bash
kubectl logs api-pod
```

Follow them:

```bash
kubectl logs -f api-pod
```

This connects directly to your Linux/Docker knowledge.

---

## 21. Exec Into a Container

You can inspect a running container:

```bash
kubectl exec -it api-pod -- sh
```

Then:

```bash
ls
```

or:

```bash
env
```

or:

```bash
curl localhost:3000/health
```

This is one of the most useful debugging skills.

---

## 22. Why Pods Alone Aren't Enough

Suppose:

```text
Pod
 ↓
Node.js
```

and the Pod crashes.

Kubernetes won't necessarily recreate it in the way you want just because you manually created a standalone Pod.

For application deployments, we generally use a:

> **Deployment**

---

## PART 2 — DEPLOYMENTS

## 23. What Is a Deployment?

A Deployment manages a set of Pods.

Conceptually:

```text
Deployment
     │
     ├── Pod
     ├── Pod
     └── Pod
```

You specify:

```yaml
replicas: 3
```

and Kubernetes maintains the desired number of Pods.

---

## 24. Our Node.js Deployment

Suppose you have already built:

```text
my-api:1.0
```

Docker image.

Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: api

spec:
  replicas: 3

  selector:
    matchLabels:
      app: api

  template:
    metadata:
      labels:
        app: api

    spec:
      containers:
        - name: api
          image: my-api:1.0

          ports:
            - containerPort: 3000
```

This says:

```text
Deployment
 ↓
3 Pods
 ↓
my-api:1.0
```

---

## 25. Apply It

```bash
kubectl apply -f deployment.yaml
```

Then:

```bash
kubectl get deployments
```

and:

```bash
kubectl get pods
```

You should see multiple Pods.

For example:

```text
api-7c9d8f7c5d-a1b2c
api-7c9d8f7c5d-b3c4d
api-7c9d8f7c5d-d5e6f
```

---

## 26. Kubernetes Replica Self-Healing

Suppose:

```text
3 Pods
```

Then:

```text
Pod B crashes
```

Now:

```text
Actual = 2
Desired = 3
```

Kubernetes creates another Pod.

```text
Pod A ✅
Pod B ❌
Pod C ✅
Pod D 🆕
```

Eventually:

```text
3 healthy Pods
```

This is one of Kubernetes' core benefits.

---

## 27. Labels

You saw:

```yaml
labels:
  app: api
```

Labels are key-value metadata attached to Kubernetes objects.

For example:

```text
app=api
environment=production
version=v1
```

They're heavily used to identify/select resources.

---

## 28. Selectors

Suppose:

```yaml
selector:
  matchLabels:
    app: api
```

This means:

> Select objects with `app=api`.

This becomes extremely important with Services.

---

## PART 3 — SERVICES

## 29. Why Do We Need a Service?

Remember:

```text
Pod IPs change.
```

Suppose:

```text
Pod A → 10.0.1.5
Pod B → 10.0.1.6
Pod C → 10.0.1.7
```

Pod A dies.

New Pod:

```text
Pod D → 10.0.2.8
```

Now clients can't rely on individual Pod IPs.

Enter:

> **Service**

---

## 30. Kubernetes Service

A Service provides a stable network endpoint for a set of Pods.

Conceptually:

```text
             Service
           /    |    \
          ↓     ↓     ↓
        Pod A  Pod B  Pod C
```

Clients talk to:

```text
Service
```

not:

```text
Pod IP
```

---

## 31. Service Manifest

```yaml
apiVersion: v1
kind: Service

metadata:
  name: api-service

spec:
  selector:
    app: api

  ports:
    - port: 80
      targetPort: 3000

  type: ClusterIP
```

Meaning:

```text
Service port = 80
       ↓
Pod port = 3000
```

---

## 32. ClusterIP

`ClusterIP` exposes the service inside the Kubernetes cluster.

Architecture:

```text
Internal Service
      ↓
┌─────┼─────┐
↓     ↓     ↓
Pod   Pod   Pod
```

Useful for:

```text
API → internal service
API → worker
API → internal backend
```

---

## 33. NodePort

Another Service type:

```text
NodePort
```

Conceptually:

```text
External
   ↓
Node IP:port
   ↓
Service
   ↓
Pods
```

Useful to understand, but you generally won't expose production internet traffic this way in modern cloud architectures.

---

## 34. LoadBalancer

Kubernetes also has:

```yaml
type: LoadBalancer
```

In a cloud environment, the Kubernetes integration can provision or configure an external load-balancing mechanism depending on the platform/controller.

Conceptually:

```text
Internet
   ↓
Cloud Load Balancer
   ↓
Kubernetes Service
   ↓
Pods
```

This connects directly to the AWS ALB knowledge you already learned.

---

## 35. Deployment + Service

Now combine:

```text
Deployment
    │
    ├── Pod
    ├── Pod
    └── Pod
          ↑
          │
       Service
```

Client:

```text
Client
 ↓
Service
 ↓
healthy Pod
```

If a Pod dies:

```text
Service
 ↓
other healthy Pod
```

This gives you stable access despite ephemeral Pods.

---

## 36. Your First Real Kubernetes Architecture

```text
                   Client
                     │
                     ↓
                Load Balancer
                     │
                     ↓
                K8s Service
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
        Pod A      Pod B      Pod C
          │          │          │
          └──────────┼──────────┘
                     ↓
                 Node.js API
```

Now we have:

```text
Docker
+
Kubernetes
+
Load balancing
+
Self-healing
+
Scaling
```

---

## PART 4 — NAMESPACE

## 37. What Is a Namespace?

Namespaces logically separate Kubernetes resources.

Example:

```text
Cluster
│
├── development
│    ├── API
│    └── Redis
│
├── staging
│    ├── API
│    └── Redis
│
└── production
     ├── API
     └── Redis
```

You can have:

```text
kubectl get pods -n production
```

This is useful for organizing environments and teams.

---

## 38. Why Not Separate Clusters?

Sometimes you might use:

```text
Dev → Cluster A
Prod → Cluster B
```

Other architectures use:

```text
One cluster
├── dev namespace
├── staging namespace
└── production namespace
```

The correct choice depends on isolation, security, scale, and operational requirements.

For interviews, understand both concepts.

---

## PART 5 — KUBERNETES CONFIGURATION

We'll go deeper in [Chapter 19](ch19-kubernetes-config-storage.md), but you should already understand the basics.

Applications need configuration:

```text
PORT=3000
NODE_ENV=production
DATABASE_HOST=...
```

Don't bake environment-specific configuration directly into your image.

We can use:

```text
ConfigMap
Secret
```

---

## 39. ConfigMap

Used for non-sensitive configuration.

Example:

```yaml
apiVersion: v1
kind: ConfigMap

metadata:
  name: api-config

data:
  NODE_ENV: production
  PORT: "3000"
```

Then inject it into the container.

Conceptually:

```text
ConfigMap
    ↓
Pod
    ↓
Environment variables
```

---

## 40. Secret

For sensitive configuration:

```text
Database credentials
API tokens
```

Kubernetes provides:

```text
Secret
```

Conceptually:

```text
Secret
  ↓
Pod
  ↓
Environment
```

But an important security point:

> Kubernetes Secrets are not automatically equivalent to a fully fledged external secrets-management system.

Their storage/protection depends on cluster configuration.

In production on AWS, you may integrate Kubernetes with services such as AWS Secrets Manager.

We'll cover this more deeply later.

---

## PART 6 — ACTUALLY RUNNING KUBERNETES LOCALLY

Now let's make this practical.

You have several options:

```text
Docker Desktop Kubernetes
Minikube
kind
```

For learning, **kind** is excellent because it runs Kubernetes nodes using containers.

---

## 41. Install kubectl

On Windows, you can install `kubectl` through the Kubernetes documentation/package manager appropriate to your environment.

Then verify:

```bash
kubectl version --client
```

---

## 42. Install kind

Verify:

```bash
kind version
```

Create a cluster:

```bash
kind create cluster --name devops-learning
```

Then:

```bash
kubectl get nodes
```

You should see something like:

```text
NAME
devops-learning-control-plane
```

Congratulations — you have a Kubernetes cluster.

---

## 43. Deploy Your Node.js App

Build your Docker image:

```bash
docker build -t my-api:1.0 .
```

If you're using kind, load the image into the cluster:

```bash
kind load docker-image my-api:1.0 \
  --name devops-learning
```

Now Kubernetes can use:

```text
my-api:1.0
```

without needing to pull it from Docker Hub.

---

## 44. Deploy

Create:

```text
deployment.yaml
service.yaml
```

Apply:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

Check:

```bash
kubectl get pods
```

```bash
kubectl get svc
```

---

## 45. Inspect Everything

```bash
kubectl get all
```

Then:

```bash
kubectl describe deployment api
```

```bash
kubectl describe service api-service
```

```bash
kubectl logs <pod-name>
```

This is where your DevOps skills start becoming practical.

---

## 46. Test the API

If you're using a local ClusterIP service, one simple learning approach is:

```bash
kubectl port-forward service/api-service 3000:80
```

Then:

```bash
curl http://localhost:3000/health
```

Flow:

```text
localhost:3000
      ↓
port-forward
      ↓
Kubernetes Service
      ↓
Pod
      ↓
Node.js
```

---

## PART 7 — BREAK IT

This is **very important**.

Don't just deploy something and declare Kubernetes learned.

Break it.

---

## 47. Delete a Pod

```bash
kubectl get pods
```

Then:

```bash
kubectl delete pod <pod-name>
```

Immediately:

```bash
kubectl get pods
```

You should see Kubernetes create a replacement because the Deployment wants the desired replica count.

That's self-healing.

---

## 48. Scale the Application

Currently:

```yaml
replicas: 3
```

Change to:

```yaml
replicas: 5
```

Apply:

```bash
kubectl apply -f deployment.yaml
```

Then:

```bash
kubectl get pods
```

You should now have five Pods.

Or scale directly:

```bash
kubectl scale deployment api --replicas=5
```

---

## 49. Scale Back

```bash
kubectl scale deployment api --replicas=2
```

Then:

```bash
kubectl get pods
```

Kubernetes removes excess replicas.

Again:

```text
Desired = 2
Actual = 5
```

Kubernetes works toward:

```text
Actual = 2
```

---

## 50. Break the Container

You can intentionally configure an invalid image:

```yaml
image: my-api:does-not-exist
```

Apply it.

Then:

```bash
kubectl get pods
```

You may see states such as:

```text
ImagePullBackOff
ErrImagePull
```

Now:

```bash
kubectl describe pod <pod>
```

Look at the Events section.

This is exactly how you learn Kubernetes troubleshooting.

---

## 51. Common Pod States

Know these:

```text
Pending
Running
Succeeded
Failed
Unknown
```

And common problems:

```text
CrashLoopBackOff
ImagePullBackOff
ErrImagePull
```

Don't memorize only the names.

Understand the debugging workflow:

```text
kubectl get pods
      ↓
kubectl describe pod
      ↓
kubectl logs
      ↓
kubectl exec
      ↓
Check image/config/network/resources
```

---

## PART 8 — KUBERNETES + YOUR AWS KNOWLEDGE

Now everything starts connecting.

Previously:

```text
AWS
 ↓
ALB
 ↓
EC2
 ↓
Docker
```

With Kubernetes:

```text
AWS
 ↓
Load Balancer
 ↓
Kubernetes
 ↓
Service
 ↓
Pods
 ↓
Containers
```

And:

```text
Pod
 ↓
Application
 ↓
RDS
```

So your architecture becomes:

```text
                         INTERNET
                             │
                             ↓
                          Route 53
                             │
                             ↓
                       CloudFront/WAF
                             │
                             ↓
                           ALB
                             │
                             ↓
                     Kubernetes Service
                             │
                  ┌──────────┼──────────┐
                  ↓          ↓          ↓
                 Pod        Pod        Pod
                  │          │          │
                  └──────────┼──────────┘
                             ↓
                           RDS
```

This is the architecture we're going to develop further.

---

## 52. EKS

On AWS, Kubernetes can be provided as:

> **Amazon EKS — Elastic Kubernetes Service**

Instead of manually building the Kubernetes control plane:

```text
You
 ↓
EKS
 ↓
Kubernetes cluster
```

AWS manages significant portions of the control-plane infrastructure.

Worker capacity can be provided through mechanisms such as managed node groups or other compute options.

---

## 53. EKS Mental Model

Eventually:

```text
AWS
│
└── EKS
     │
     ├── Control Plane
     │
     └── Worker Nodes
           ├── Pods
           ├── Pods
           └── Pods
```

We'll cover EKS more practically in the later Kubernetes responses.

---

## 54. Docker → Kubernetes Deployment Pipeline

Now your DevOps pipeline becomes:

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
Docker build
    ↓
Push image to registry
    ↓
Kubernetes deployment
    ↓
Rolling update
    ↓
Pods
```

This is the workflow you should eventually be able to implement yourself.

---

## 55. Image Registry

Kubernetes needs access to your container image.

Production example:

```text
GitHub Actions
      ↓
Docker build
      ↓
Amazon ECR
      ↓
Kubernetes/EKS
      ↓
Pull image
      ↓
Pod
```

ECR = **Elastic Container Registry**.

We'll use this when we build the full deployment workflow.

---

## 56. Rolling Update

Suppose you're running:

```text
api:v1
api:v1
api:v1
```

Deploy:

```text
api:v2
```

Kubernetes can perform a rolling update:

```text
v1 v1 v1
 ↓
v2 v1 v1
 ↓
v2 v2 v1
 ↓
v2 v2 v2
```

This connects directly to the deployment strategies you learned earlier.

---

## 57. Kubernetes vs Docker Compose

You've seen Docker Compose.

#### Compose

Great for:

```text
Local development
```

Example:

```text
Node.js
PostgreSQL
Redis
```

#### Kubernetes

Designed for:

```text
Container orchestration
Scaling
Self-healing
Service discovery
Production workloads
Rolling deployments
```

They aren't direct substitutes in every situation.

---

## 58. Kubernetes vs EC2

Remember:

```text
EC2
→ virtual machine
```

Kubernetes:

```text
→ orchestration platform
```

They operate at different levels.

A Kubernetes cluster can itself run on EC2-based worker nodes.

So:

```text
AWS
 ↓
EC2
 ↓
Kubernetes
 ↓
Pod
 ↓
Container
```

is perfectly possible.

---

## 59. What You Need to Master

#### 🔥 Deep

- Why Kubernetes exists
- Docker vs Kubernetes
- cluster
- control plane
- worker nodes
- API server
- scheduler
- controllers
- etcd concept
- kubelet
- Pods
- Deployments
- replicas
- desired state
- labels/selectors
- Services
- ClusterIP
- LoadBalancer
- namespaces
- kubectl
- YAML manifests
- Pod lifecycle
- self-healing
- scaling
- basic rolling deployments
- container images in Kubernetes
- local Kubernetes setup
- basic Kubernetes debugging

#### Medium

- EKS
- NodePort
- ReplicaSets
- readiness/liveness
- resource requests/limits
- ConfigMaps
- Secrets

We'll go deeper into many of these in Chapters [19](ch19-kubernetes-config-storage.md)–[20](ch20-kubernetes-networking-scaling.md).

#### Awareness

- StatefulSets
- DaemonSets
- Jobs/CronJobs
- Operators
- CRDs
- service mesh

Don't worry about mastering those yet.

---

## 🧪 Your Kubernetes Lab

This is the lab I want you to actually perform.

#### Step 1

Create cluster:

```bash
kind create cluster --name devops-learning
```

#### Step 2

Build your Node.js Docker image:

```bash
docker build -t my-api:1.0 .
```

#### Step 3

Load it:

```bash
kind load docker-image my-api:1.0 \
  --name devops-learning
```

#### Step 4

Create:

```text
deployment.yaml
service.yaml
```

#### Step 5

Deploy:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

#### Step 6

Verify:

```bash
kubectl get pods
kubectl get deployments
kubectl get services
```

#### Step 7

Access it:

```bash
kubectl port-forward service/api-service 3000:80
```

Then:

```bash
curl http://localhost:3000/health
```

#### Step 8 — Break it

Delete a Pod:

```bash
kubectl delete pod <pod-name>
```

Watch:

```bash
kubectl get pods -w
```

#### Step 9 — Scale it

```bash
kubectl scale deployment api --replicas=5
```

#### Step 10 — Debug a broken image

Change:

```yaml
image: my-api:does-not-exist
```

Then:

```bash
kubectl get pods
kubectl describe pod <pod-name>
```

Find the problem.

**If you can perform this lab and explain every step, you've genuinely started learning Kubernetes rather than memorizing Kubernetes terminology.**

---

## 🧠 The Kubernetes Mental Model

Remember this:

```text
                 CLUSTER
                    │
          ┌─────────┴─────────┐
          ↓                   ↓
    CONTROL PLANE         WORKER NODES
                              │
                         ┌────┴────┐
                         ↓         ↓
                       Pod       Pod
                         │         │
                     Container  Container
```

Then:

```text
Deployment
     ↓
maintains Pods
     ↓
Pods
     ↓
Service
     ↓
stable networking
```

And:

```text
kubectl
 ↓
API Server
 ↓
Kubernetes
```

The central idea:

> **You declare the desired state; Kubernetes continuously works to make the actual state match it.**

---

## 🔥 And Yes — Containers Are Fully Part of This Roadmap

Your concern from the beginning is valid, so let's make the scope explicit.

We've covered:

```text
CONTAINERS
│
├── Docker
│   ├── Images
│   ├── Containers
│   ├── Dockerfiles
│   ├── Layers
│   ├── Volumes
│   ├── Networks
│   ├── Compose
│   ├── Multi-stage builds
│   ├── Production images
│   ├── Security
│   ├── Registries
│   └── CI/CD integration
│
└── Kubernetes
    ├── Pods
    ├── Deployments
    ├── Services
    ├── Scaling
    ├── Self-healing
    ├── Configuration
    ├── Networking
    └── Production deployment
```

And later:

```text
Docker
   ↓
ECR
   ↓
EKS
   ↓
Kubernetes
   ↓
Terraform
   ↓
AWS
```

So **yes, containers are a major part of the DevOps curriculum, not an afterthought.**
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 17: AWS Monitoring + Security](../04-aws/ch17-monitoring-security.md) · [Chapter 19: Kubernetes Configuration + Storage](ch19-kubernetes-config-storage.md) → · [Revision sheet](../../revision/ch18-revision.md)
