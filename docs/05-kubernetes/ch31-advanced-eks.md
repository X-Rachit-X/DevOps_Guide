# Chapter 31 — Advanced Amazon EKS

> **Source:** Response 31 of the original conversation (`source-archive/src-31.txt`, lines 1–3410) · **Part II — Advanced extension (Responses 25–36)**  
> **Study aids:** [Revision sheet](../../revision/ch31-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md) · *includes an editorial supplement at the end*

<!-- SOURCE-BEGIN -->

Absolutely. This response will be **deep and complete**, because EKS sits at the intersection of almost everything you've learned:

**AWS + VPC + IAM + Kubernetes + Docker + ECR + Load Balancing + Storage + Autoscaling + Security + Observability.**

We will not just memorize EKS terms. We'll understand **what happens when you deploy a real backend to EKS**, why each AWS component exists, how traffic flows, how pods get AWS permissions, how networking works, how nodes scale, and how to troubleshoot failures.

---

## 1. What Exactly Is EKS?

EKS = **Amazon Elastic Kubernetes Service**.

It is AWS's managed Kubernetes service.

Instead of running Kubernetes yourself:

```text
You manage:
Kubernetes control plane
etcd
API server
scheduler
controller manager
control-plane upgrades
control-plane availability
```

AWS manages much of the Kubernetes control-plane infrastructure for you.

You primarily manage:

```text
Your applications
Pods
Deployments
Services
Ingress
ConfigMaps
Secrets
Node infrastructure/configuration
Networking configuration
IAM integration
Observability
```

Simplified:

```text
                  AWS
                   │
            ┌──────┴──────┐
            │             │
      EKS Control      Your Workloads
         Plane              │
            │               │
            └───────┬───────┘
                    │
                 Kubernetes
```

---

## 2. Kubernetes vs EKS

You already know Kubernetes.

Think:

```text
Kubernetes
=
container orchestration platform
```

while:

```text
EKS
=
AWS-managed Kubernetes
+
AWS infrastructure integration
```

EKS doesn't replace Kubernetes concepts.

You still use:

```bash
kubectl
```

and Kubernetes manifests:

```yaml
apiVersion: apps/v1
kind: Deployment
```

The difference is that EKS integrates Kubernetes deeply with AWS.

---

## 3. Why Would We Use EKS?

Suppose your backend has:

```text
20 microservices
```

You want:

- automatic recovery
- horizontal scaling
- rolling deployments
- private networking
- load balancing
- IAM
- persistent storage
- AWS integrations
- observability
- high availability

EKS provides Kubernetes orchestration while AWS provides the surrounding infrastructure.

---

## 4. EKS Architecture

A simplified production EKS architecture:

```text
                         AWS Region
                             │
              ┌──────────────┴──────────────┐
              │                             │
        EKS Control Plane               Your VPC
              │                             │
        Kubernetes API              ┌───────┴────────┐
              │                     │                │
          Scheduler             AZ-a             AZ-b
              │                     │                │
        Controllers            Worker Nodes      Worker Nodes
                                    │                │
                                  Pods             Pods
```

The control plane and worker infrastructure should be thought of separately.

---

## 5. EKS Control Plane

The control plane contains the Kubernetes components responsible for managing the cluster.

Conceptually:

```text
EKS Control Plane
│
├── Kubernetes API Server
├── Scheduler
├── Controllers
└── etcd
```

You interact primarily through:

```text
kubectl
```

which talks to the Kubernetes API.

---

## 6. Kubernetes API Server

This is the main entry point.

When you execute:

```bash
kubectl apply -f deployment.yaml
```

the flow is roughly:

```text
kubectl
   ↓
EKS Kubernetes API
   ↓
Authentication
   ↓
Authorization
   ↓
Validate request
   ↓
Store desired state
   ↓
Controllers reconcile
```

The API server is therefore central to the cluster.

---

## 7. etcd

Kubernetes uses **etcd** as its distributed key-value store for cluster state.

It stores information representing things such as:

```text
Deployments
Pods
Services
ConfigMaps
Secrets
CRDs
Cluster configuration
```

Conceptually:

```text
Kubernetes API
      ↓
    etcd
      ↓
cluster state
```

With EKS, AWS manages the EKS control-plane infrastructure, including the managed control-plane components.

You generally don't SSH into an EKS control-plane machine and manage etcd yourself.

---

## 8. Worker Nodes

Your workloads ultimately run on worker nodes.

A node could be:

```text
EC2 instance
```

or, depending on the architecture:

```text
AWS Fargate
```

or newer EKS compute approaches.

For the core EKS mental model:

```text
EKS
 ↓
Nodes
 ↓
Pods
 ↓
Containers
```

---

## 9. EKS Compute Options

You should know the major options.

#### EC2 Managed Node Groups

AWS manages much of the node-group lifecycle.

You still get:

```text
EC2 instances
```

but EKS helps manage them as a Kubernetes node group.

---

#### Self-managed nodes

You manage more of the EC2 lifecycle yourself.

Useful for specialized requirements, but more operational work.

---

#### Fargate

Pods run on serverless compute without you managing EC2 worker nodes.

Conceptually:

```text
Pod
 ↓
Fargate
```

rather than:

```text
Pod
 ↓
EC2 Node
```

---

#### Karpenter

Karpenter is an advanced Kubernetes node provisioning/autoscaling solution commonly used with EKS.

It can dynamically provision appropriate EC2 capacity based on pending workload requirements.

We'll discuss this later.

---

## 10. Managed Node Groups

For most backend applications, Managed Node Groups are an important EKS concept.

Example:

```text
EKS Cluster
│
├── Node Group
│     ├── EC2
│     ├── EC2
│     └── EC2
│
└── Node Group
      ├── EC2
      └── EC2
```

Pods are scheduled onto these nodes.

---

## 11. Why Multiple Availability Zones?

Suppose all nodes are in:

```text
AZ-a
```

and AZ-a fails.

Potentially:

```text
everything unavailable
```

Instead:

```text
Region
│
├── AZ-a
│   ├── Node
│   └── Node
│
├── AZ-b
│   ├── Node
│   └── Node
│
└── AZ-c
    ├── Node
    └── Node
```

Now workloads can survive an AZ-level failure better, assuming the application and supporting dependencies are also designed for that level of availability.

---

## 12. EKS + VPC

This is one of the most important sections.

EKS runs within your AWS networking environment.

Think:

```text
VPC
│
├── Public Subnets
│
└── Private Subnets
      │
      └── EKS nodes
            │
            └── Pods
```

A common architecture is:

```text
Internet
   ↓
Internet Gateway
   ↓
Public Load Balancer
   ↓
Private EKS Nodes
   ↓
Pods
   ↓
Private RDS
```

---

## 13. Why Put Nodes in Private Subnets?

Your worker nodes usually don't need to accept arbitrary inbound Internet traffic.

Instead:

```text
Internet
   ↓
Load Balancer
   ↓
Private nodes
```

This reduces the direct exposure of the compute layer.

---

## 14. Private Nodes Need Outbound Access

A private node may still need to download:

```text
container images
OS packages
AWS resources
external APIs
```

So it may need outbound connectivity.

Common architecture:

```text
Private Subnet
      │
      ↓
NAT Gateway
      │
      ↓
Internet Gateway
      │
      ↓
Internet
```

But AWS service traffic can also be routed through VPC endpoints where appropriate.

---

## 15. EKS Networking

This is where EKS becomes more interesting.

AWS commonly uses the **Amazon VPC CNI** for pod networking.

The CNI is responsible for connecting Kubernetes Pods to the VPC networking environment.

A simplified model:

```text
Pod
 ↓
VPC networking
 ↓
ENI/IP allocation
 ↓
AWS network
```

This differs from the simple mental model of:

> "Every Pod is just behind one node IP."

With VPC-native networking, Pods can receive VPC-routable IP addresses depending on the configured networking mode.

---

## 16. What Is a CNI?

CNI = **Container Network Interface**.

It's a standard interface for configuring container networking.

Kubernetes itself doesn't implement all networking mechanics.

A CNI plugin handles networking.

For EKS, one major component is:

```text
Amazon VPC CNI
```

---

## 17. VPC CNI Architecture

Conceptually:

```text
Kubernetes
     │
     ↓
VPC CNI
     │
     ↓
AWS VPC
     │
     ↓
ENIs / IP addresses
```

This allows Pods to communicate using AWS networking.

---

## 18. Why Pod IP Capacity Matters

This is a major EKS troubleshooting concept.

Suppose your node can only obtain a limited number of usable Pod IPs.

You attempt:

```text
kubectl scale deployment api --replicas=100
```

but eventually:

```text
Pods Pending
```

because there aren't enough available IP addresses.

Therefore:

> **Subnet IP capacity and node networking limits can constrain Pod scaling.**

This is why VPC CIDR planning matters.

---

## 19. EKS Networking Limits

Different EC2 instance types have different networking capabilities.

They can differ in:

```text
network interfaces
IP addresses
network bandwidth
```

Therefore:

```text
bigger node
≠
only more CPU/RAM
```

It may also provide more networking capacity.

This matters when running many Pods.

---

## 20. Secondary CIDR / Larger Pod Address Space

If your cluster's networking design needs more addresses, you need sufficient IP address space.

You may encounter:

```text
VPC CIDR
Subnet CIDR
Pod IP allocation
```

You should understand:

```text
IP exhaustion
```

as a real production failure mode.

---

## 21. How a Pod Gets an IP

Simplified:

```text
Pod scheduled
      ↓
VPC CNI
      ↓
allocate IP
      ↓
attach/configure networking
      ↓
Pod receives network identity
```

The exact implementation has additional details, but this is the correct mental model.

---

## 22. EKS + Security Groups

You already learned Security Groups.

Now combine them with EKS.

A simplified flow:

```text
Internet
   ↓
Load Balancer SG
   ↓
Node/Pod networking
   ↓
Application
```

You must ensure traffic is allowed appropriately.

Example:

```text
Internet
  ↓
ALB :443
  ↓
EKS application
  ↓
RDS :5432
```

The security model needs to allow only the necessary traffic.

---

## 23. Pod-Level Security Groups

EKS can also support associating security groups more directly with Pods through AWS networking capabilities.

This is useful when different workloads require different network access policies.

For example:

```text
Payment Pod
   ↓
Payment-specific SG
   ↓
specific AWS resources
```

rather than giving every workload identical network access.

For interviews, know the concept:

> EKS can provide finer-grained AWS network security for workloads beyond simply securing the entire node.

---

## 24. NetworkPolicy vs Security Group

Don't confuse them.

#### Kubernetes NetworkPolicy

Controls Kubernetes/network traffic at the cluster/workload level depending on the networking implementation.

Conceptually:

```text
Pod A → Pod B
allowed?
```

#### AWS Security Group

Controls network traffic at the AWS networking layer.

Conceptually:

```text
network interface/workload
→ AWS security rules
```

They can complement each other.

---

## 25. EKS IAM

Now one of the most important EKS concepts:

> **How does a Kubernetes Pod get permission to call AWS APIs?**

For example, your Node.js application wants to:

```text
upload to S3
read from SQS
access Secrets Manager
```

You should **not** put:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

inside the container.

Instead, use workload identity mechanisms.

---

## 26. Old Pattern vs Modern Pattern

Historically, EKS commonly used:

```text
IAM Roles for Service Accounts
(IRSA)
```

The broader modern AWS direction also includes:

```text
EKS Pod Identity
```

For your interviews:

```text
IRSA
→ know well

EKS Pod Identity
→ know well as the newer EKS-native approach
```

---

## 27. The Basic Idea

You want:

```text
Payment Pod
   ↓
Kubernetes ServiceAccount
   ↓
AWS IAM Role
   ↓
S3 permissions
```

So:

```text
Pod identity
≠
AWS root credentials
```

---

## 28. Why This Is Better

Suppose your application only needs:

```text
s3:GetObject
```

Give it only:

```text
s3:GetObject
```

Don't give:

```text
AdministratorAccess
```

This follows:

> **Principle of least privilege.**

---

## 29. EKS Pod Identity Concept

The conceptual flow is:

```text
Pod
 ↓
Kubernetes ServiceAccount
 ↓
EKS Pod Identity association
 ↓
IAM Role
 ↓
temporary AWS credentials
 ↓
AWS API
```

The application can use the AWS SDK without embedding long-lived AWS keys.

---

## 30. Example IAM Policy

Suppose the application only needs to read:

```text
my-company-assets
```

A policy might conceptually grant:

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject"
  ],
  "Resource": "arn:aws:s3:::my-company-assets/*"
}
```

The exact resource/policy design should be carefully scoped.

---

## 31. Kubernetes ServiceAccount

Example:

```yaml
apiVersion: v1
kind: ServiceAccount

metadata:
  name: backend-sa
  namespace: production
```

Deployment:

```yaml
spec:
  template:
    spec:
      serviceAccountName: backend-sa
```

Now your Pods run under:

```text
backend-sa
```

and AWS identity integration can associate that workload identity with an IAM role.

---

## 32. Node IAM vs Pod IAM

This distinction is critical.

#### Node IAM role

Permissions belong broadly to the EC2 node.

Potentially dangerous if every Pod can inherit broad permissions.

#### Pod identity

Permissions are associated with the specific workload.

```text
Node
 ├── Pod A → S3 read
 ├── Pod B → SQS send
 └── Pod C → Secrets Manager read
```

This provides better isolation.

---

## 33. Example

Imagine:

```text
User Service
→ DynamoDB

Image Service
→ S3

Payment Service
→ Secrets Manager
```

Don't give all three:

```text
AdministratorAccess
```

Instead:

```text
User Service
→ DynamoDB permissions

Image Service
→ S3 permissions

Payment Service
→ Secrets Manager permissions
```

This is exactly the kind of security reasoning interviewers like.

---

## 34. ECR + EKS

You've already learned ECR.

ECR = Elastic Container Registry.

Your deployment pipeline becomes:

```text
Developer
   ↓
Git
   ↓
GitHub Actions
   ↓
Docker build
   ↓
ECR
   ↓
EKS
   ↓
Pod
```

The Kubernetes Deployment references an image:

```yaml
containers:
  - name: backend
    image: <account>.dkr.ecr.<region>.amazonaws.com/backend:<tag>
```

---

## 35. Why Immutable Image Tags?

Avoid:

```text
backend:latest
```

Prefer:

```text
backend:a82f31c
```

where:

```text
a82f31c
```

could be a Git commit SHA.

Then:

```text
Git commit
    ↓
Docker image
    ↓
ECR
    ↓
EKS
```

You know exactly what version is running.

---

## 36. ECR Authentication

Your EKS workloads/nodes need permission to pull images from ECR.

The relevant AWS/Kubernetes integration ensures nodes or workloads can authenticate to ECR appropriately.

If image pulling fails, you may see:

```text
ImagePullBackOff
```

Troubleshoot:

```bash
kubectl describe pod <pod>
```

Look at Events.

Potential causes:

```text
wrong image
wrong tag
ECR permissions
network connectivity
registry issue
```

---

## 37. EKS Load Balancers

You already know:

```text
Service
Ingress
Load Balancer
```

In AWS, Kubernetes can integrate with AWS load-balancing infrastructure.

A common architecture:

```text
Internet
   ↓
AWS Application Load Balancer
   ↓
Kubernetes Service
   ↓
Pods
```

This integration is commonly provided through AWS's load-balancing controller.

---

## 38. AWS Load Balancer Controller

The **AWS Load Balancer Controller** allows Kubernetes resources to provision/configure AWS load-balancing resources.

It can work with:

```text
Ingress
```

to provision:

```text
Application Load Balancer
```

and with certain Service configurations for:

```text
Network Load Balancer
```

The exact behavior depends on the resource and configuration.

---

## 39. Why Is This Useful?

Instead of manually creating:

```text
ALB
target groups
listeners
routing rules
```

you can declare Kubernetes resources.

For example:

```yaml
kind: Ingress
```

and the controller reconciles the AWS infrastructure.

This is another example of:

```text
desired state
      ↓
controller
      ↓
actual infrastructure
```

Notice how this connects directly to **[Chapter 29](ch29-crds-operators.md) — Operators and Controllers**.

---

## 40. ALB vs NLB

You should know the basic distinction.

#### ALB

Application Load Balancer.

Layer 7.

Understands things like:

```text
HTTP
HTTPS
host
path
headers
```

Good for:

```text
web applications
REST APIs
HTTP routing
```

#### NLB

Network Load Balancer.

Layer 4-oriented.

Good for:

```text
TCP
TLS
high-performance network traffic
```

Don't memorize every edge case; understand the layer distinction.

---

## 41. Target Type: Instance vs IP

This is an important EKS concept.

AWS load balancers can route to:

```text
EC2 instances
```

or directly to:

```text
Pod IPs
```

depending on configuration.

Conceptually:

#### Instance target

```text
ALB
 ↓
Node
 ↓
Service
 ↓
Pod
```

#### IP target

```text
ALB
 ↓
Pod IP
```

Direct Pod targeting can reduce an extra networking hop and is common in modern EKS configurations.

---

## 42. EBS + EKS

Now storage.

You've learned:

```text
EBS
```

is block storage.

EKS can use EBS through the:

```text
Amazon EBS CSI Driver
```

This allows Kubernetes PersistentVolumes to use EBS-backed storage.

Architecture:

```text
Pod
 ↓
PVC
 ↓
PV
 ↓
EBS volume
```

---

## 43. Important EBS Limitation

EBS volumes are generally associated with a specific Availability Zone.

Suppose:

```text
EBS
AZ-a
```

and the Pod gets rescheduled to:

```text
AZ-b
```

You can encounter volume attachment/scheduling constraints.

This is one reason stateful workload design needs careful thought.

---

## 44. EFS + EKS

EFS = Elastic File System.

Unlike EBS, EFS is a managed network file system designed for shared file access across Availability Zones.

Conceptually:

```text
Pod A ─┐
       ├── EFS
Pod B ─┤
       │
Pod C ─┘
```

This can be useful when multiple Pods need shared filesystem access.

---

## 45. EBS vs EFS

Remember:

```text
EBS
→ block storage
→ commonly attached to workloads requiring block semantics
→ AZ-oriented

EFS
→ shared network filesystem
→ can be accessed across AZs
```

For databases, however, don't blindly put a database on EFS just because it is shared. Managed database services like RDS are often a better architectural choice.

---

## 46. StorageClass

You've already learned Kubernetes StorageClasses.

EKS might have:

```text
StorageClass
 ↓
EBS CSI driver
 ↓
EBS volume
```

Example conceptual flow:

```text
PVC
 ↓
StorageClass
 ↓
CSI Driver
 ↓
AWS EBS
```

---

## 47. CSI

CSI = **Container Storage Interface**.

It standardizes how Kubernetes interacts with storage systems.

Examples:

```text
EBS CSI
EFS CSI
```

Mental model:

```text
Kubernetes
   ↓
CSI driver
   ↓
AWS storage
```

---

## 48. EKS Autoscaling

Now one of the most important production topics.

There are two different scaling levels.

#### Pod scaling

```text
HPA
```

changes:

```text
number of Pods
```

#### Node scaling

Cluster/node autoscaling mechanisms change:

```text
number/type of nodes
```

So:

```text
HPA
→ workload scaling

Node autoscaling
→ compute capacity scaling
```

---

## 49. Example

Suppose:

```text
3 nodes
10 Pods
```

Traffic increases.

HPA says:

```text
10 Pods → 30 Pods
```

But there isn't enough node capacity.

Some Pods become:

```text
Pending
```

Then node autoscaling needs to provide additional compute.

```text
HPA
 ↓
more Pods
 ↓
insufficient capacity
 ↓
node autoscaler
 ↓
more nodes
 ↓
Pods scheduled
```

This relationship is extremely important.

---

## 50. Cluster Autoscaler

Cluster Autoscaler traditionally scales node groups based on unschedulable Pods and node utilization/other configured conditions.

Conceptually:

```text
Pending Pods
      ↓
Cluster Autoscaler
      ↓
increase node group
      ↓
new EC2 node
      ↓
Pods scheduled
```

---

## 51. Karpenter

Karpenter takes a more flexible approach to node provisioning.

Instead of simply thinking:

```text
Node Group
→ add another identical node
```

Karpenter can consider workload requirements and provision appropriate compute capacity.

For example:

```text
Pod requires:
8 CPU
32 GB RAM
```

Karpenter can choose suitable capacity based on your configuration and constraints.

---

## 52. Cluster Autoscaler vs Karpenter

Simplified interview-level distinction:

```text
Cluster Autoscaler
→ primarily scales existing node groups

Karpenter
→ dynamically provisions appropriate node capacity
```

Karpenter can provide more flexible capacity management.

You don't need to memorize every Karpenter scheduling detail for SWE interviews.

---

## 53. HPA + Karpenter

Production flow:

```text
Traffic increases
      ↓
CPU increases
      ↓
HPA increases replicas
      ↓
Pods become Pending
      ↓
Karpenter provisions nodes
      ↓
Pods schedule
      ↓
Traffic handled
```

This is a very good interview scenario.

---

## 54. Resource Requests

Remember:

```yaml
resources:
  requests:
    cpu: "250m"
    memory: "256Mi"

  limits:
    cpu: "500m"
    memory: "512Mi"
```

Requests tell Kubernetes:

> "I need at least this much capacity for scheduling."

Limits tell Kubernetes:

> "Don't let this container exceed this configured resource ceiling."

---

## 55. Why Requests Matter for Autoscaling

Suppose a Pod says:

```text
request = 1 CPU
```

The scheduler needs a node with sufficient allocatable capacity.

So:

```text
Node capacity
+
Pod requests
```

directly affect scheduling.

Bad resource requests can lead to:

```text
overprovisioning
underprovisioning
Pending Pods
poor autoscaling behavior
```

---

## 56. EKS Security Layers

Production EKS security is defense in depth.

Think:

```text
                    Security
                       │
        ┌──────────────┼───────────────┐
        ↓              ↓               ↓
       IAM          Network          Kubernetes
        │              │               │
    Pod identity     SG/NACL       RBAC
                     NetworkPolicy  ServiceAccount
        │
        ↓
AWS permissions
```

And:

```text
Secrets
Encryption
Image security
Pod security
Audit logs
```

all contribute.

---

## 57. Kubernetes RBAC

You've already learned RBAC.

Example:

```text
User
 ↓
Role / ClusterRole
 ↓
RoleBinding
 ↓
Kubernetes API
```

For workloads:

```text
ServiceAccount
 ↓
RBAC permissions
```

Don't confuse:

```text
Kubernetes RBAC
```

with:

```text
AWS IAM
```

They control different authorization domains.

---

## 58. IAM vs Kubernetes RBAC

This is an excellent interview question.

#### IAM

Controls:

```text
AWS resources
```

Examples:

```text
S3
SQS
DynamoDB
Secrets Manager
ECR
```

#### Kubernetes RBAC

Controls:

```text
Kubernetes API resources
```

Examples:

```text
Pods
Deployments
Services
Secrets
ConfigMaps
```

So:

```text
IAM
→ "Can this workload access AWS?"

Kubernetes RBAC
→ "Can this identity perform this Kubernetes API action?"
```

---

## 59. Secrets in EKS

Don't put real secrets directly into Git.

Avoid:

```yaml
stringData:
  DATABASE_PASSWORD: "myrealpassword"
```

in a Git repository.

Better architecture:

```text
AWS Secrets Manager
        ↓
External Secrets / workload integration
        ↓
Kubernetes Secret
        ↓
Pod
```

or use an appropriate secret-management integration.

---

## 60. EKS Encryption

You can encrypt sensitive Kubernetes data using AWS/KMS-backed mechanisms where supported.

The important conceptual distinction:

```text
TLS
→ protects data in transit

Encryption at rest
→ protects stored data
```

You should know both.

---

## 61. EKS Pod Security

Applications should follow least privilege.

Important practices include:

```text
non-root containers
read-only filesystem where possible
drop unnecessary Linux capabilities
resource limits
seccomp
security contexts
restricted permissions
```

Example:

```yaml
securityContext:
  runAsNonRoot: true
```

Don't run everything as:

```text
root
```

unless there is a legitimate reason.

---

## 62. Image Security

Your container supply chain:

```text
Git
 ↓
CI
 ↓
Docker
 ↓
ECR
 ↓
EKS
```

can be attacked.

Therefore:

```text
dependency scanning
image scanning
minimal images
non-root
signed/verified artifacts where appropriate
immutable tags
least privilege
```

matter.

---

## 63. EKS Observability

You've already learned CloudWatch, Prometheus, Grafana and OpenTelemetry.

Now combine them.

You need visibility into:

```text
Cluster
Nodes
Pods
Containers
Applications
AWS resources
```

---

## 64. What Should We Monitor?

#### Cluster level

```text
node availability
API server health
cluster capacity
```

#### Node level

```text
CPU
memory
disk
network
```

#### Pod level

```text
restarts
CPU
memory
readiness
liveness
```

#### Application level

```text
request rate
error rate
latency
```

#### AWS level

```text
ALB
RDS
EBS
NAT Gateway
S3
```

---

## 65. Logs

Your application should produce structured logs.

Example:

```json
{
  "level": "info",
  "requestId": "abc123",
  "service": "order-api",
  "message": "Order created"
}
```

Then centralized log collection can aggregate them.

Avoid:

```text
console.log("password =", password)
```

Obviously.

---

## 66. Metrics

For Kubernetes workloads:

```text
CPU
Memory
Pod count
Restarts
Request rate
Error rate
Latency
```

For backend services:

```text
HTTP requests
5xx
p95
p99
DB latency
queue depth
```

---

## 67. Tracing

Suppose:

```text
ALB
 ↓
Order
 ↓
Payment
 ↓
RDS
```

A distributed trace can show:

```text
Request
├── Order: 50ms
├── Payment: 400ms
└── DB: 350ms
```

Now you know where latency comes from.

---

## 68. EKS Control Plane Logs

EKS can expose control-plane-related logging to CloudWatch Logs depending on enabled logging categories.

These logs can help troubleshoot things involving:

```text
API requests
authentication
authorization
audit activity
scheduler/controller behavior
```

Exact categories and current AWS behavior should be checked against current AWS documentation when implementing production logging.

---

## 69. EKS Upgrade Strategy

Kubernetes versions evolve.

You can't just think:

```text
upgrade
→ done
```

A production upgrade requires planning.

Typical process:

```text
Check compatibility
       ↓
Check deprecated APIs
       ↓
Upgrade test environment
       ↓
Upgrade control plane
       ↓
Upgrade add-ons
       ↓
Upgrade nodes
       ↓
Validate workloads
```

---

## 70. Deprecated Kubernetes APIs

Suppose your application uses:

```yaml
apiVersion: old/version
```

and that API disappears in a future Kubernetes version.

Your deployment can break during an upgrade.

Therefore:

> Kubernetes upgrades require API compatibility checks.

This is particularly important with:

```text
Ingress
CRDs
operators
admission controllers
```

---

## 71. EKS Add-ons

EKS clusters commonly depend on components such as:

```text
VPC CNI
CoreDNS
kube-proxy
EBS CSI driver
```

Some can be managed as EKS add-ons.

When upgrading the cluster, compatibility of these components matters.

---

## 72. CoreDNS

CoreDNS provides Kubernetes DNS.

For example:

```text
payment.default.svc.cluster.local
```

resolves to the appropriate Kubernetes Service.

If DNS breaks:

```text
Pod
 ↓
DNS lookup
 ↓
failure
```

services may appear unreachable even though Pods are healthy.

---

## 73. EKS Troubleshooting Workflow

Let's build a real debugging process.

Suppose:

```text
Users receive 503.
```

Don't randomly restart Pods.

Work from outside inward.

---

## 74. Step 1 — Check Load Balancer

Check:

```text
ALB/NLB
```

Questions:

```text
Is it healthy?
Are listeners correct?
Are target groups healthy?
Are security groups correct?
```

---

## 75. Step 2 — Check Ingress

```bash
kubectl get ingress
kubectl describe ingress <name>
```

Check:

```text
host
path
backend
events
```

---

## 76. Step 3 — Check Service

```bash
kubectl get svc
```

Then:

```bash
kubectl describe svc <service>
```

Check:

```text
ports
targetPort
selector
```

---

## 77. Step 4 — Check Endpoints

```bash
kubectl get endpoints
```

or EndpointSlices:

```bash
kubectl get endpointslices
```

If there are no endpoints:

```text
Service
   ↓
no matching Pods
```

Check labels/selectors.

---

## 78. Step 5 — Check Pods

```bash
kubectl get pods -o wide
```

Look for:

```text
Pending
CrashLoopBackOff
ImagePullBackOff
Running but not Ready
```

---

## 79. Step 6 — Describe the Pod

```bash
kubectl describe pod <pod>
```

Look at:

```text
Events
```

Events often tell you exactly what went wrong.

---

## 80. Step 7 — Check Logs

```bash
kubectl logs <pod>
```

For previous crashed container:

```bash
kubectl logs <pod> --previous
```

If multiple containers:

```bash
kubectl logs <pod> -c <container>
```

---

## 81. Step 8 — Check Node

```bash
kubectl get nodes
```

Then:

```bash
kubectl describe node <node>
```

Look for:

```text
CPU pressure
memory pressure
disk pressure
taints
capacity
allocatable resources
```

---

## 82. Step 9 — Check Networking

If the application cannot reach RDS:

```text
Pod
 ↓
VPC networking
 ↓
Security Group
 ↓
RDS
```

Check:

```text
DNS
route
security groups
network policy
port
RDS availability
```

For PostgreSQL:

```text
5432
```

---

## 83. Step 10 — Check IAM

If the application says:

```text
AccessDenied
```

check:

```text
ServiceAccount
 ↓
Pod identity/IRSA
 ↓
IAM role
 ↓
IAM policy
```

Don't immediately modify the node's IAM role.

---

## 84. Classic EKS Failure #1

#### Symptom:

```text
Pods stuck Pending
```

Possible causes:

```text
insufficient CPU
insufficient memory
node selector mismatch
taints/tolerations
affinity constraints
no available nodes
IP exhaustion
PVC problems
```

Use:

```bash
kubectl describe pod <pod>
```

The scheduler events are often the key.

---

## 85. Classic EKS Failure #2

#### Symptom:

```text
ImagePullBackOff
```

Check:

```text
image name
tag
ECR permissions
network
registry
```

Command:

```bash
kubectl describe pod <pod>
```

---

## 86. Classic EKS Failure #3

#### Symptom:

```text
CrashLoopBackOff
```

Check:

```bash
kubectl logs <pod>
kubectl logs <pod> --previous
```

Potential causes:

```text
bad environment variable
application crash
wrong command
database unavailable
missing Secret
bad configuration
```

---

## 87. Classic EKS Failure #4

#### Symptom:

```text
Application can't access S3
```

Check:

```text
ServiceAccount
 ↓
Pod Identity
 ↓
IAM role
 ↓
S3 policy
 ↓
bucket policy
```

Potentially also:

```text
network/VPC endpoint/NAT
```

depending on the architecture.

---

## 88. Classic EKS Failure #5

#### Symptom:

```text
Pods cannot communicate
```

Check:

```text
Service
Endpoints
DNS
NetworkPolicy
Security Groups
CNI
ports
```

---

## 89. Classic EKS Failure #6

#### Symptom:

```text
Pods cannot obtain IPs
```

Think:

```text
VPC CNI
 ↓
subnet IP capacity
 ↓
ENI/IP limits
```

This is an advanced EKS-specific troubleshooting skill.

---

## 90. Production EKS Architecture

Now let's build the architecture you should be able to explain in an interview.

```text
                         Internet
                            │
                            ▼
                        Route 53
                            │
                            ▼
                       CloudFront
                            │
                            ▼
                           WAF
                            │
                            ▼
                    AWS Load Balancer
                            │
                    ┌───────┴───────┐
                    │               │
                   AZ-a            AZ-b
                    │               │
              ┌─────┴─────┐   ┌─────┴─────┐
              │ EKS Node   │   │ EKS Node   │
              │            │   │            │
              │ Pod        │   │ Pod        │
              │ Pod        │   │ Pod        │
              └────────────┘   └────────────┘
                    │               │
                    └───────┬───────┘
                            │
                     Private Services
                       │         │
                      RDS       Redis
                       │
                     S3/SQS
```

And:

```text
Terraform
    ↓
AWS infrastructure

GitHub Actions
    ↓
Docker
    ↓
ECR

ArgoCD
    ↓
EKS

Helm
    ↓
Kubernetes applications
```

---

## 91. Complete Request Flow

Let's follow a request.

User:

```text
GET /orders/123
```

#### Step 1

DNS:

```text
orders.example.com
```

resolves through Route 53.

#### Step 2

Request reaches:

```text
CloudFront/WAF
```

depending on architecture.

#### Step 3

Load balancer receives it.

#### Step 4

AWS load-balancing integration routes to EKS workload.

#### Step 5

Kubernetes Service routes to the appropriate Pod.

#### Step 6

Application executes.

#### Step 7

Application may access:

```text
RDS
Redis
S3
SQS
```

using private networking and appropriate IAM.

#### Step 8

Metrics/logs/traces are emitted.

That's the production flow you should be able to draw.

---

## 92. Complete Deployment Flow

Now the other direction.

Developer:

```text
git push
```

↓

GitHub Actions:

```text
lint
typecheck
test
build
security checks
```

↓

Docker:

```text
build image
```

↓

ECR:

```text
push image
```

↓

GitOps repository:

```text
update image tag
```

↓

ArgoCD:

```text
detect change
```

↓

EKS:

```text
Deployment update
```

↓

Kubernetes:

```text
rolling update
```

↓

Pods:

```text
new version
```

This is your complete CI/CD → EKS workflow.

---

## 93. EKS + Terraform

Terraform can provision:

```text
VPC
Subnets
IAM
EKS
Node Groups
Security Groups
RDS
S3
Redis
Load Balancing infrastructure
```

Then Kubernetes/Helm/ArgoCD manages workloads.

This separation is useful:

```text
Terraform
→ infrastructure

Kubernetes
→ workload orchestration

Helm
→ packaging

ArgoCD
→ deployment/reconciliation
```

---

## 94. EKS + Operators

From [Chapter 29](ch29-crds-operators.md):

```text
CRD
+
Operator
```

can run inside EKS.

For example:

```text
EKS
 ↓
PostgreSQL Operator
 ↓
Postgres Custom Resource
 ↓
database resources
```

So all of your previous topics are connecting together.

---

## 95. EKS + Istio

From [Chapter 30](ch30-service-mesh-istio.md):

```text
EKS
 ↓
Istio
 ↓
Envoy
 ↓
service-to-service traffic
```

Now you have:

```text
AWS
+
Kubernetes
+
Operators
+
Service Mesh
```

---

## 96. EKS Cost Awareness

EKS isn't just a technical problem.

There are costs from:

```text
EKS control-plane/service charges
EC2
EBS
Load Balancers
NAT Gateway
Data transfer
CloudWatch
ECR
RDS
ElastiCache
```

A badly designed architecture can become expensive.

For example:

```text
many NAT Gateways
+
excessive cross-AZ traffic
+
oversized EC2 instances
+
unused load balancers
+
unbounded logging
```

can increase costs.

---

## 97. Availability vs Cost

Suppose:

```text
1 node
```

is cheaper.

But:

```text
3 AZs
multiple nodes
```

provides better fault tolerance.

So architecture involves tradeoffs:

```text
cost
vs
availability
vs
performance
vs
operational complexity
```

You should be able to explain these tradeoffs rather than saying:

> "Always use three AZs."

---

## 98. EKS Security Checklist

For a production EKS environment:

```text
☑ Private nodes where appropriate
☑ Least-privilege IAM
☑ Pod identity
☑ Kubernetes RBAC
☑ NetworkPolicies
☑ Security Groups
☑ Secrets Manager
☑ Encryption
☑ Non-root containers
☑ Image scanning
☑ Resource limits
☑ Audit/control-plane logging
☑ Regular upgrades
☑ Restricted API access
☑ Minimal permissions
```

---

## 99. EKS Production Checklist

You should think about:

#### Networking

```text
☑ Multi-AZ
☑ private subnets
☑ CIDR planning
☑ VPC CNI
☑ IP capacity
```

#### Compute

```text
☑ Managed Node Groups
☑ autoscaling
☑ resource requests
☑ instance sizing
```

#### Security

```text
☑ IAM
☑ Pod Identity
☑ RBAC
☑ Secrets
☑ NetworkPolicy
```

#### Deployment

```text
☑ ECR
☑ immutable image tags
☑ Helm
☑ ArgoCD
☑ rolling deployment
```

#### Observability

```text
☑ logs
☑ metrics
☑ traces
☑ alerts
```

---

## 100. The Most Important EKS Interview Questions

### Q1. What is EKS?

> Amazon EKS is AWS's managed Kubernetes service that integrates Kubernetes with AWS infrastructure and services.

---

### Q2. Why use EKS instead of running Kubernetes yourself?

> EKS reduces the operational burden of managing the Kubernetes control plane and provides deep integration with AWS networking, IAM, load balancing, storage, and other services.

---

### Q3. What is VPC CNI?

> It is the Kubernetes networking plugin used in EKS that integrates Pod networking with the AWS VPC networking model.

---

### Q4. Why can Pods run out of IPs?

> Pod IP allocation depends on available subnet address space and networking/instance limits. A cluster can therefore have enough CPU but still be unable to schedule additional Pods because it cannot allocate IP addresses.

---

### Q5. How does a Pod access S3 securely?

> Use workload identity such as EKS Pod Identity or IRSA to associate the workload with a least-privilege IAM role instead of embedding long-lived AWS credentials in the container.

---

### Q6. IAM vs RBAC?

> IAM controls access to AWS resources, while Kubernetes RBAC controls access to Kubernetes API resources.

---

### Q7. How does EKS expose an application?

A common approach:

```text
Internet
 ↓
AWS Load Balancer
 ↓
Kubernetes Service
 ↓
Pods
```

---

### Q8. HPA vs node autoscaling?

> HPA changes the number of application Pods, while node autoscaling changes the amount of compute capacity available to schedule those Pods.

---

### Q9. Cluster Autoscaler vs Karpenter?

> Cluster Autoscaler primarily adjusts existing node groups, while Karpenter can dynamically provision appropriate compute capacity based on pending workload requirements and constraints.

---

### Q10. EBS vs EFS?

```text
EBS
→ block storage
→ AZ-oriented

EFS
→ shared filesystem
→ multi-AZ access
```

---

### Q11. Why use private EKS nodes?

> To reduce direct Internet exposure of worker infrastructure while exposing only the required entry points such as load balancers.

---

### Q12. How would you debug a 503?

Start:

```text
Load Balancer
 ↓
Ingress
 ↓
Service
 ↓
Endpoints
 ↓
Pods
 ↓
Application
 ↓
Dependencies
```

Don't randomly restart everything.

---

## 101. The EKS Mental Model You Should Memorize

This is probably the most useful diagram from this response:

```text
                         AWS REGION
                             │
                 ┌───────────┴───────────┐
                 │                       │
          EKS CONTROL PLANE             VPC
                 │                       │
          Kubernetes API          ┌──────┴──────┐
                 │                │             │
             Scheduler          AZ-a           AZ-b
                 │                │             │
           Controllers        EKS Nodes      EKS Nodes
                                  │             │
                                Pods          Pods
                                  │             │
                           ┌──────┴─────────────┐
                           │                    │
                          ECR               AWS Services
                           │              ┌────┼────┐
                           │             RDS S3 SQS
                           │
                     Container Images
```

Then add:

```text
IAM
 ↓
Pod Identity
 ↓
AWS permissions
```

and:

```text
VPC CNI
 ↓
Pod networking
```

and:

```text
AWS Load Balancer Controller
 ↓
ALB/NLB
```

and:

```text
EBS/EFS CSI
 ↓
Persistent Storage
```

and:

```text
HPA
 +
Karpenter
 ↓
Scaling
```

That's **Advanced EKS**.

---

## 102. What You Should Know Deeply vs Broadly

For your SWE placement goal:

#### 🔥 Deep

You should be able to explain and troubleshoot:

```text
EKS architecture
EKS + VPC
private/public subnets
VPC CNI
Pod IP allocation
IAM
Pod Identity / IRSA
ECR
AWS Load Balancer Controller
Services
Ingress
HPA
node scaling
EBS/EFS
RBAC
NetworkPolicy
EKS troubleshooting
```

#### 🟡 Medium

Understand:

```text
Managed Node Groups
Fargate
Karpenter
CSI
control-plane logging
EKS upgrades
EKS add-ons
Pod-level security groups
```

#### ⚪ Awareness

You don't need specialist depth in:

```text
EKS control-plane internals
custom CNI development
advanced Karpenter internals
EKS networking kernel internals
Kubernetes scheduler implementation
etcd internals
```

Those are platform/SRE specialization areas rather than necessary SWE placement depth.

---

## 103. Final Connection With Everything You've Learned

At this point your mental model should be:

```text
                         AWS
                          │
                       Terraform
                          │
                          ▼
                         VPC
                          │
               ┌──────────┴──────────┐
               │                     │
              ALB                   EKS
                                     │
                             ┌───────┴───────┐
                             │               │
                          Node Group      Node Group
                             │               │
                            Pods            Pods
                             │               │
                       ┌─────┴─────┐   ┌─────┴─────┐
                       │           │   │           │
                     Envoy       App Envoy       App
                       │           │   │           │
                       └─────┬─────┘   └─────┬─────┘
                             │               │
                          Services ───────────┘
                             │
                   ┌─────────┼─────────┐
                   ↓         ↓         ↓
                  RDS      Redis       S3
```

Deployment:

```text
Developer
    ↓
GitHub
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
EKS
```

Security:

```text
IAM
 ├── Pod Identity
 ├── least privilege
 └── AWS access

Kubernetes RBAC
 └── Kubernetes API access

Network
 ├── Security Groups
 ├── NetworkPolicy
 └── VPC

Secrets
 └── Secrets Manager
```

Scaling:

```text
Traffic
  ↓
HPA
  ↓
More Pods
  ↓
Insufficient node capacity
  ↓
Karpenter / Cluster Autoscaler
  ↓
More nodes
  ↓
Pods schedule
```

This is the level of EKS understanding you want as a backend SWE.

---

## 🎯 Chapter 31 Complete

We covered in depth:

- ✅ EKS architecture
- ✅ EKS vs Kubernetes
- ✅ Control plane
- ✅ API server
- ✅ etcd
- ✅ Worker nodes
- ✅ Managed Node Groups
- ✅ Self-managed nodes
- ✅ Fargate
- ✅ Karpenter
- ✅ Multi-AZ architecture
- ✅ VPC integration
- ✅ Private/public subnets
- ✅ NAT
- ✅ VPC CNI
- ✅ CNI fundamentals
- ✅ Pod IP allocation
- ✅ IP exhaustion
- ✅ ENI/networking considerations
- ✅ Security Groups
- ✅ Pod-level security groups
- ✅ NetworkPolicy
- ✅ IAM
- ✅ IRSA
- ✅ EKS Pod Identity
- ✅ ServiceAccounts
- ✅ Least privilege
- ✅ ECR
- ✅ Immutable images
- ✅ AWS Load Balancer Controller
- ✅ ALB vs NLB
- ✅ Instance vs IP targets
- ✅ EBS
- ✅ EFS
- ✅ CSI
- ✅ StorageClasses
- ✅ HPA
- ✅ Cluster Autoscaler
- ✅ Karpenter
- ✅ Resource requests/limits
- ✅ IAM vs Kubernetes RBAC
- ✅ Secrets Manager
- ✅ Encryption
- ✅ Pod security
- ✅ Image security
- ✅ Observability
- ✅ EKS control-plane logging
- ✅ CoreDNS
- ✅ EKS upgrades
- ✅ EKS add-ons
- ✅ Production architecture
- ✅ Deployment architecture
- ✅ Cost considerations
- ✅ Security checklist
- ✅ Production checklist
- ✅ Advanced troubleshooting
- ✅ Interview scenarios

We also explicitly connected **EKS ↔ CRDs/Operators ↔ Istio ↔ Helm ↔ ArgoCD ↔ Terraform ↔ AWS**, so these aren't isolated topics anymore.
<!-- SOURCE-END -->

---

## Editorial supplement

> **Added by the knowledge-base editor — not part of the original source.** It fills gaps the source leaves open (for example concepts named in the interview list but never explained, or configuration the chapter only describes in words). Treat the text above as the original material and this section as clearly separated additions.

### Practical EKS setup the chapter describes but does not show

The chapter explains EKS concepts without setup commands. These are the concrete counterparts. Check current AWS documentation before using them in a real account (versions and flags change), and remember that a running EKS cluster, NAT gateways and load balancers all cost money.

**1. Create a cluster (eksctl) and connect `kubectl`.**

```yaml
# cluster.yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: devops-learning
  region: ap-south-1
managedNodeGroups:
  - name: general
    instanceType: t3.medium
    minSize: 2
    desiredCapacity: 2
    maxSize: 4
    privateNetworking: true        # nodes in private subnets (section 13)
```

```bash
eksctl create cluster -f cluster.yaml
aws eks update-kubeconfig --region ap-south-1 --name devops-learning   # writes ~/.kube/config
kubectl get nodes
eksctl delete cluster -f cluster.yaml                                   # clean up to stop charges
```

**2. How an IAM identity gets Kubernetes permissions (authentication → authorization).** `kubectl` authenticates to the EKS API with an **IAM** identity (a token generated from your AWS credentials), then Kubernetes **RBAC** decides what that identity may do. The mapping from IAM principals to Kubernetes users/groups is configured with **EKS access entries** (current mechanism) or, in older clusters, the `aws-auth` ConfigMap. This is the practical meaning of "IAM vs RBAC" in section 58: IAM answers "may this principal reach the cluster?", RBAC answers "what may it do inside it?".

**3. IRSA (IAM Roles for Service Accounts).** The ServiceAccount is annotated with the role, and the role's trust policy trusts the cluster's OIDC provider for exactly that ServiceAccount:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: backend-sa
  namespace: production
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::<account-id>:role/backend-s3-read
```

```json
{
  "Effect": "Allow",
  "Principal": { "Federated": "arn:aws:iam::<account-id>:oidc-provider/oidc.eks.ap-south-1.amazonaws.com/id/<OIDC_ID>" },
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {
    "StringEquals": {
      "oidc.eks.ap-south-1.amazonaws.com/id/<OIDC_ID>:sub": "system:serviceaccount:production:backend-sa"
    }
  }
}
```

**4. EKS Pod Identity.** Install the *EKS Pod Identity Agent* add-on, give the IAM role a trust policy for the service principal `pods.eks.amazonaws.com` (actions `sts:AssumeRole` and `sts:TagSession`), then link ServiceAccount to role with an association — no OIDC annotation is needed:

```bash
aws eks create-pod-identity-association \
  --cluster-name devops-learning \
  --namespace production \
  --service-account backend-sa \
  --role-arn arn:aws:iam::<account-id>:role/backend-s3-read
```

**5. An Ingress handled by the AWS Load Balancer Controller** (creates an ALB; `target-type: ip` sends traffic straight to Pod IPs, section 41):

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:ap-south-1:<account-id>:certificate/<id>
spec:
  ingressClassName: alb
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service: { name: api-service, port: { number: 80 } }
```

**6. Maximum Pods per node (the formula behind "Pod IP capacity").** With the default VPC CNI mode each Pod consumes a secondary IP address on one of the node's ENIs:

```text
maxPods = ENIs × (IPv4 addresses per ENI − 1) + 2
```

Example: an `m5.large` supports 3 ENIs with 10 IPv4 addresses each, so `3 × (10 − 1) + 2 = 29` Pods — regardless of how much CPU and memory are free. A bigger instance type therefore raises the Pod ceiling as well as capacity (sections 18–19). *Prefix delegation* (each ENI slot holds a /28 prefix) greatly increases the number of Pod IPs per node, and a *secondary CIDR* gives Pods a larger address range when the primary VPC CIDR is exhausted (section 20).

**7. Other practical details.**

- **Cluster endpoint access** can be public, private, or both; restrict public access by CIDR or make it private-only for stricter environments.
- **Control-plane log types** you can enable: `api`, `audit`, `authenticator`, `controllerManager`, `scheduler`.
- **Upgrades** move **one minor version at a time**: control plane first, then add-ons (VPC CNI, CoreDNS, kube-proxy, EBS CSI), then nodes; check deprecated APIs before you start. Older versions eventually fall out of standard support, which can add cost or force an upgrade.
- **Fargate** has constraints worth remembering: no DaemonSets, no EBS volumes (use EFS), and it needs a Fargate profile that selects which Pods run there.
- **EKS Auto Mode** is a newer option where AWS also manages node capacity, load balancing and storage components — verify current features and pricing.
- **Cost.** The EKS control plane has a fixed hourly charge in addition to EC2, EBS, load balancers, NAT gateways, data transfer and logging (verify current prices).

---

**Navigation:** ← [Chapter 30: Service Mesh + Istio](ch30-service-mesh-istio.md) · [Chapter 32: Advanced Terraform](../06-iac-config/ch32-advanced-terraform.md) → · [Revision sheet](../../revision/ch31-revision.md)
