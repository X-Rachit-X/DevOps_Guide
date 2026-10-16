# Chapter 1 — Cloud + DevOps Fundamentals

> **Source:** Response 1 of the original conversation (`source-archive/src-01.txt`, lines 1–1213) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch01-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

Let's start from **zero at the conceptual level**, but I’ll move quickly where you already have CS knowledge.

The goal of this response is to build the mental model for the entire field. By the end, you should understand **what Cloud and DevOps actually mean, why companies use them, and how all the technologies we'll learn fit together.**

---

## 1. First: What problem are Cloud & DevOps solving?

Imagine you've built a backend:

```text
React/Next.js
      ↓
Node.js + TypeScript API
      ↓
PostgreSQL
```

It works perfectly on your laptop.

But now you have 100,000 users.

Your laptop obviously can't be the production server.

You need:

- computers to run your application
- networking
- storage
- databases
- security
- backups
- monitoring
- scaling
- deployment
- reliability

Traditionally, a company might buy physical servers:

```text
Company
   │
   ├── Physical servers
   ├── Network equipment
   ├── Storage
   ├── Firewalls
   ├── Database servers
   └── Data center
```

That's expensive and difficult to manage.

**Cloud computing** changes this model.

Instead of buying and maintaining all the infrastructure yourself, you can rent computing resources from cloud providers such as AWS.

```text
Your Application
       ↓
      AWS
       ↓
 ┌─────┼─────────┐
EC2   S3       RDS
```

You can provision infrastructure when you need it and scale it as demand changes.

---

## 2. What exactly is Cloud Computing?

A simple definition:

> **Cloud computing means using computing resources over a network instead of owning and managing all the physical infrastructure yourself.**

These resources can include:

- Compute
- Storage
- Databases
- Networking
- Security
- Messaging
- AI/ML services
- Monitoring
- Serverless functions

For example:

Instead of buying a server:

```text
Buy server
↓
Install OS
↓
Configure network
↓
Maintain hardware
↓
Replace failed hardware
```

You can use AWS:

```text
AWS
 ↓
Create EC2 instance
 ↓
Deploy application
```

---

## 3. Why Cloud?

Suppose your application normally gets:

```text
1,000 requests/minute
```

But during a sale:

```text
100,000 requests/minute
```

You don't want to permanently buy enough hardware for 100,000 requests if you only need it occasionally.

Cloud allows you to dynamically provision resources.

```text
Normal traffic
    ↓
2 servers

High traffic
    ↓
10 servers

Traffic decreases
    ↓
2 servers
```

This leads to some fundamental cloud concepts.

---

## 4. Scalability

**Scalability = ability of a system to handle increasing workload by adding resources.**

There are two major ways.

### Vertical scaling

Make one machine more powerful.

```text
Before:

CPU: 2 cores
RAM: 4 GB

       ↓

After:

CPU: 16 cores
RAM: 64 GB
```

This is called:

> **Scale Up**

---

### Horizontal scaling

Add more machines.

```text
             Load Balancer
              /    |    \
             ↓     ↓     ↓
           Server Server Server
```

This is:

> **Scale Out**

Horizontal scaling is extremely important in distributed systems.

You'll see it repeatedly in:

- AWS
- Docker
- Kubernetes
- Load balancing
- System design

---

## 5. Elasticity

Don't confuse **scalability** and **elasticity**.

#### Scalability

Can the system handle growth?

#### Elasticity

Can the system **automatically adjust resources according to demand**?

For example:

```text
Traffic
  ↓
2 instances

Traffic increases
  ↓
4 instances

Traffic increases
  ↓
8 instances

Traffic decreases
  ↓
3 instances

Traffic decreases
  ↓
2 instances
```

That's elasticity.

Cloud platforms are particularly useful because they make this kind of dynamic resource management possible.

---

## 6. Availability

Suppose you have one server:

```text
Users
  ↓
Server
```

If that server dies:

```text
Users
  ↓
💥 Server DEAD
```

Your application is unavailable.

So we introduce redundancy:

```text
             Load Balancer
              /          \
             ↓            ↓
          Server A     Server B
```

If A dies:

```text
             Load Balancer
                   ↓
                Server B
```

Users can continue using the application.

This is **High Availability (HA).**

---

## 7. Reliability vs Availability

These are related but not identical.

#### Availability

> Is the system accessible when users need it?

#### Reliability

> Does the system consistently perform correctly over time?

A system can technically be available but still unreliable.

Example:

```text
API responds
but

50% of requests return incorrect results
```

It's available, but not reliable.

---

## 8. Fault Tolerance

A fault-tolerant system continues operating even when some components fail.

Example:

```text
          Load Balancer
          /           \
         ↓             ↓
      Server A       Server B
         ❌
      FAILED
                       ↓
                    Users
```

The system tolerates the failure of Server A.

Cloud architectures often use redundancy to achieve this.

---

## 9. Disaster Recovery

Now imagine something much bigger happens.

For example:

```text
Entire AWS Region
       ↓
      💥
```

You need a way to recover.

That's **Disaster Recovery (DR).**

You might maintain infrastructure in another region:

```text
        Users
          ↓
       Region A
          │
       Database
          │
       Replication
          ↓
       Region B
```

If Region A becomes unavailable, you can recover in Region B.

Two important DR concepts:

#### RTO — Recovery Time Objective

> How quickly must the system be restored?

Example:

```text
RTO = 1 hour
```

Means the business targets restoring service within one hour.

#### RPO — Recovery Point Objective

> How much data loss can the business tolerate?

Example:

```text
RPO = 5 minutes
```

Means the business targets losing no more than about five minutes of data in a disaster.

We'll revisit these when discussing AWS architecture.

---

## 10. Cloud Service Models

You'll hear these constantly:

```text
IaaS
PaaS
SaaS
```

Let's make them intuitive.

---

### IaaS — Infrastructure as a Service

You rent infrastructure.

Example:

**AWS EC2**

AWS gives you:

```text
Physical hardware
Virtualization
Networking
Data center
```

You manage:

```text
OS
Runtime
Application
Dependencies
```

Think:

> **"Give me a computer."**

---

### PaaS — Platform as a Service

The provider manages more of the infrastructure/platform.

Think:

> **"Give me a platform where I can run my application."**

You focus more on your application instead of managing the server.

Examples include various managed application platforms.

---

### SaaS — Software as a Service

You simply use the finished software.

Examples:

- Gmail
- Google Docs
- Slack

Think:

> **"I just want to use the software."**

---

#### The spectrum

```text
More control                         Less control

IaaS ───────── PaaS ───────── SaaS
 │               │               │
EC2          App Platform      Gmail
```

As you move toward SaaS, the provider manages more.

---

## 11. Public vs Private vs Hybrid Cloud

#### Public Cloud

Infrastructure provided by companies such as:

- AWS
- Microsoft Azure
- Google Cloud

Multiple customers use the provider's infrastructure, with isolation between them.

---

#### Private Cloud

Cloud infrastructure dedicated to one organization.

Often used when organizations need specific control or regulatory arrangements.

---

#### Hybrid Cloud

Combination:

```text
Private infrastructure
        +
Public cloud
```

For example:

```text
Company Data Center
       ↕
      VPN
       ↕
      AWS
```

---

## 12. What is a Cloud Region?

A **Region** is a geographic area containing cloud infrastructure.

For example, AWS has regions around the world.

You might deploy your application to an Indian region for users primarily located in India.

Conceptually:

```text
AWS
│
├── Region A
│    ├── AZ1
│    ├── AZ2
│    └── AZ3
│
├── Region B
│    ├── AZ1
│    ├── AZ2
│    └── AZ3
```

---

## 13. What is an Availability Zone?

An **Availability Zone (AZ)** is an isolated infrastructure location within a region.

Suppose:

```text
AWS Region
│
├── AZ-A
│
├── AZ-B
│
└── AZ-C
```

Instead of putting your entire application in one AZ:

```text
          ALB
           │
        AZ-A
         EC2
```

you can distribute it:

```text
              ALB
            /     \
           ↓       ↓
         AZ-A     AZ-B
         EC2      EC2
```

If one AZ has a failure, the other can continue serving traffic.

This is a fundamental AWS architecture concept.

---

## 14. Now: What is DevOps?

Cloud and DevOps are related, but they're **not the same thing**.

Cloud is primarily about:

> **Infrastructure and services.**

DevOps is primarily about:

> **How development and operations teams build, test, deploy, and operate software together efficiently and reliably.**

Traditional workflow:

```text
Developer
   ↓
Writes code
   ↓
"Throw it over the wall"
   ↓
Operations
   ↓
Deploy manually
```

This creates friction.

DevOps tries to create a continuous process:

```text
Code
 ↓
Build
 ↓
Test
 ↓
Package
 ↓
Deploy
 ↓
Monitor
 ↓
Improve
 ↖──────────┘
```

---

## 15. CI/CD

This is one of the most important DevOps concepts.

### CI — Continuous Integration

Developers frequently integrate code into a shared repository.

A CI pipeline can automatically:

```text
Git Push
   ↓
Install dependencies
   ↓
Lint
   ↓
Build
   ↓
Run tests
   ↓
Generate artifact
```

For example:

```yaml
name: CI

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - run: npm ci

      - run: npm run lint

      - run: npm test

      - run: npm run build
```

Don't worry about understanding every line yet. **[Chapter 6](../03-cicd-gitops/ch06-cicd-github-actions.md) will go deep into this.**

The important idea now is:

> **Every code change can automatically be checked.**

---

## 16. Continuous Delivery vs Continuous Deployment

These terms are often confused.

#### Continuous Delivery

Code is automatically built and prepared for deployment.

But production deployment may require approval.

```text
Code
 ↓
Build
 ↓
Test
 ↓
Ready for production
 ↓
Manual approval
 ↓
Production
```

#### Continuous Deployment

Deployment to production happens automatically after the pipeline passes.

```text
Code
 ↓
Build
 ↓
Test
 ↓
Production
```

---

## 17. What is DevSecOps?

Security shouldn't be something you think about only at the end.

Traditional:

```text
Develop
 ↓
Test
 ↓
Deploy
 ↓
Security
```

DevSecOps:

```text
Security
   ↓
Throughout the entire lifecycle
```

Examples:

- dependency scanning
- secret detection
- container scanning
- IAM
- vulnerability scanning
- security testing
- infrastructure security

We'll incorporate this into AWS/Docker/CI/CD rather than making it an enormous separate subject.

---

## 18. What is Infrastructure as Code?

Imagine you manually create:

- VPC
- subnets
- EC2
- security groups
- load balancer
- RDS

through the AWS Console.

That's difficult to reproduce.

Instead, describe infrastructure using code.

For example, Terraform:

```hcl
resource "aws_instance" "app" {
  ami           = "ami-example"
  instance_type = "t3.micro"
}
```

Now infrastructure can be:

```text
Code
 ↓
Review
 ↓
Version control
 ↓
Terraform
 ↓
AWS infrastructure
```

That's **Infrastructure as Code (IaC).**

We'll learn Terraform properly later.

---

## 19. What are Containers?

Suppose your Node.js application needs:

```text
Node.js 22
npm dependencies
environment variables
system libraries
application code
```

It works on your machine.

But another machine may have:

```text
Node.js 20
different libraries
different OS configuration
```

and your application may behave differently.

A container packages the application and its dependencies into a standardized environment.

```text
┌──────────────────────────┐
│       Container          │
│                          │
│ Node.js                  │
│ Dependencies             │
│ Application              │
└──────────────────────────┘
```

Docker is the technology we'll use to learn this deeply.

---

## 20. Containers vs Virtual Machines

A simplified picture:

#### VM

```text
Physical Machine
      ↓
   Hypervisor
   /       \
  VM       VM
  │        │
 OS       OS
 │        │
App      App
```

Each VM includes its own guest operating system.

#### Containers

```text
Physical Machine
      ↓
Container Runtime
   /      |      \
Container Container Container
    \       |       /
       Host OS
```

Containers are generally more lightweight because they share the host kernel.

We'll explore the actual mechanics in the Docker responses.

---

## 21. What is Serverless?

Serverless doesn't mean:

> "There are no servers."

There **are** servers.

It means:

> **You don't manage the underlying servers directly.**

For example, AWS Lambda:

```text
HTTP Request
     ↓
API Gateway
     ↓
Lambda
     ↓
Your Function
```

You provide the function:

```javascript
export const handler = async (event) => {
  return {
    statusCode: 200,
    body: "Hello World"
  };
};
```

AWS handles much of the underlying infrastructure.

---

## 22. What is SRE?

**Site Reliability Engineering (SRE)** is an engineering approach to operating reliable production systems.

It focuses on things like:

- reliability
- availability
- latency
- monitoring
- incident response
- automation
- capacity
- error budgets

You'll encounter:

#### SLA

A commitment/expectation around service availability or performance.

#### SLI

A measurement.

Example:

```text
Successful requests / Total requests
```

#### SLO

A target for that measurement.

Example:

```text
99.9% successful requests
```

Don't worry about memorizing these yet—we'll revisit them in the observability response.

---

## 23. Putting Cloud + DevOps Together

Now we can connect everything.

Imagine your TypeScript backend.

#### Development

```text
Developer
   ↓
GitHub
```

#### CI/CD

```text
GitHub
   ↓
GitHub Actions
   ↓
Test
   ↓
Build
   ↓
Docker Image
```

#### Infrastructure

```text
Terraform
   ↓
AWS
```

#### Deployment

```text
Docker
   ↓
EC2 / Kubernetes
```

#### Application infrastructure

```text
                     Internet
                        │
                      Route53
                        │
                    CloudFront
                        │
                       ALB
                    /       \
                  EC2       EC2
                   │          │
                Docker      Docker
                   \          /
                    Node API
                    /  |   \
                   /   |    \
               Redis  RDS    S3
```

#### Operations

```text
Application
     ↓
CloudWatch
     ↓
Metrics / Logs / Alerts
```

And the entire lifecycle becomes:

```text
             ┌───────────────┐
             │     GitHub    │
             └───────┬───────┘
                     ↓
                    CI
                     ↓
              Build + Test
                     ↓
                Docker Image
                     ↓
                    CD
                     ↓
              AWS / Kubernetes
                     ↓
                Application
                     ↓
              Logs + Metrics
                     ↓
                Monitoring
                     ↓
                Improvement
                     │
                     └────→ Git
```

**That is the big picture of Cloud + DevOps.**

---

## 24. Technologies We'll Learn

Now you should understand why these technologies exist:

| Technology | Main purpose |
|---|---|
| **Linux** | Operating system/environment |
| **Bash** | Automation/scripting |
| **Git** | Version control |
| **GitHub** | Code collaboration |
| **Docker** | Containerization |
| **AWS** | Cloud infrastructure/services |
| **EC2** | Compute |
| **S3** | Object storage |
| **RDS** | Managed databases |
| **VPC** | Cloud networking |
| **ALB** | Load balancing |
| **Lambda** | Serverless compute |
| **SQS/SNS** | Messaging |
| **Route 53** | DNS |
| **CloudFront** | CDN |
| **CloudWatch** | Monitoring |
| **GitHub Actions** | CI/CD |
| **Kubernetes** | Container orchestration |
| **Terraform** | Infrastructure as Code |
| **Prometheus/Grafana** | Monitoring/visualization |
| **OpenTelemetry** | Observability |
| **Helm** | Kubernetes package management |

And:

| Technology | Our depth |
|---|---|
| GitOps | Concept + architecture |
| ArgoCD | Interview-level understanding |
| Jenkins | Concept/comparison |
| Ansible | Concept + basic usage |
| Service Mesh | Awareness |

---

## 🧠 The Mental Model You Should Leave With

Don't memorize 20 definitions.

Remember this:

```text
                  CLOUD
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
     Compute     Storage     Networking
        │           │           │
       EC2          S3          VPC
       ECS         EBS          ALB
     Lambda        RDS         Route53
                    │
                  AWS
                    │
                    ↓
                 DEVOPS
                    │
      ┌─────────────┼─────────────┐
      ↓             ↓             ↓
     Git           CI/CD        Docker
                                  │
                                  ↓
                             Kubernetes
                                  │
                                  ↓
                              Terraform
                                  │
                                  ↓
                           Observability
```

And underneath all of it:

```text
Linux + Networking + Security
```

Those are the foundations.

---

## 🎯 Quick Self-Test

Before moving to [Chapter 2](ch02-linux.md), try answering these **without looking back**:

1. What problem does cloud computing solve?
2. Scalability vs elasticity?
3. Horizontal vs vertical scaling?
4. High availability vs fault tolerance?
5. RTO vs RPO?
6. IaaS vs PaaS vs SaaS?
7. Region vs Availability Zone?
8. Cloud vs DevOps?
9. CI vs CD?
10. Continuous Delivery vs Continuous Deployment?
11. Why do we use containers?
12. Containers vs VMs?
13. What does Infrastructure as Code mean?
14. What is serverless?
15. What problem does DevOps ultimately try to improve?

If you can explain these **in your own words**, you're ready.
<!-- SOURCE-END -->

---

**Navigation:** [Chapter 2: Linux for Cloud & DevOps](ch02-linux.md) → · [Revision sheet](../../revision/ch01-revision.md)
