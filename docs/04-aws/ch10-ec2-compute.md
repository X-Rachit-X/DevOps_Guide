# Chapter 10 — EC2 + AWS Compute

> **Source:** Response 10 of the original conversation (`source-archive/src-10.txt`, lines 1–1746) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch10-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

We're continuing the roadmap exactly as planned.

You now know:

```text
Linux → Networking → Git → CI/CD → Docker → AWS/IAM
```

Now we're going to put your **Dockerized TypeScript backend onto an actual cloud server** using **Amazon EC2**.

The goal isn't merely to know what EC2 stands for. By the end, you should understand:

> **How a request travels from a user → AWS networking → EC2 → Docker → Node.js application, and how to deploy, secure, troubleshoot, and scale that server.**

---

## 1. What Is EC2?

**Amazon EC2 (Elastic Compute Cloud)** provides virtual servers that you can run in AWS.

Think of it as:

```text
Your laptop
   ↓
Virtual computer in AWS
   ↓
EC2
```

An EC2 instance is essentially a virtual machine with:

- CPU
- RAM
- storage
- network interface
- operating system

You control much more of the machine than you would with highly managed services.

---

## 2. Why Do We Need EC2?

Suppose you've built:

```text
TypeScript
   ↓
Node.js
   ↓
Express API
```

Locally:

```text
localhost:3000
```

But users on the internet need to access it.

EC2 gives you a server in AWS:

```text
Internet
   ↓
AWS
   ↓
EC2
   ↓
Docker
   ↓
Node.js
   ↓
Your API
```

---

## 3. EC2 vs Your Laptop

Your laptop:

```text
CPU
RAM
Disk
Network
OS
Applications
```

EC2:

```text
Virtual CPU
Virtual RAM
EBS storage
Virtual network
Linux/Windows
Applications
```

The major difference is that EC2 is provisioned in AWS infrastructure and can be managed remotely and integrated with AWS services.

---

## 4. EC2 Architecture

At a high level:

```text
                  AWS Region
                      │
                    VPC
                      │
                   Subnet
                      │
                EC2 Instance
                      │
             ┌────────┴────────┐
             ↓                 ↓
           EBS              Network
          Storage           Interface
             │                 │
             ↓                 ↓
          OS + App          IP address
```

You learned VPCs and networking earlier.

Now we're connecting those concepts to an actual compute resource.

---

## 5. What Is an EC2 Instance?

An **instance** is a virtual machine created from an image/AMI and configured with a particular hardware profile.

For example:

```text
Instance
├── CPU
├── Memory
├── Network
├── Storage
└── OS
```

You choose the instance type based on workload requirements.

---

## 6. AMI

AMI = **Amazon Machine Image**.

It provides the software configuration used to launch an EC2 instance.

Conceptually:

```text
AMI
 ↓
Launch
 ↓
EC2 Instance
```

An AMI can contain things such as:

- operating system
- preinstalled software
- configuration

For example:

```text
Ubuntu-based AMI
       ↓
EC2 instance
       ↓
Ubuntu server
```

---

## 7. AMI vs Instance

Very important:

```text
AMI
 ↓
Blueprint/template

EC2 instance
 ↓
Running virtual machine
```

Similar mental model:

```text
Docker image
 ↓
Docker container
```

The analogy isn't exact, but it's useful.

---

## 8. Instance Types

EC2 offers different hardware configurations.

For example, you may see families designed around:

```text
General purpose
Compute optimized
Memory optimized
Storage optimized
Accelerated computing
```

Think:

```text
Workload
   ↓
Required CPU/RAM/network
   ↓
Instance type
```

You don't need to memorize every instance type.

For interviews, understand **why** you would choose one family over another.

---

## 9. General Purpose

General-purpose instances are designed for balanced workloads.

For example:

```text
Node.js API
Moderate traffic
Normal CPU + RAM requirements
```

You generally don't need an extremely CPU-heavy machine.

---

## 10. Compute Optimized

Suppose:

```text
CPU-heavy workload
```

Examples could include:

- computation-heavy services
- batch processing
- CPU-intensive APIs

A compute-optimized family may be appropriate.

---

## 11. Memory Optimized

Suppose your workload needs lots of RAM:

```text
Large in-memory dataset
Caching
Memory-heavy processing
```

Then memory-optimized instances can make sense.

---

## 12. Storage Optimized

For workloads requiring high local storage performance/capacity, storage-optimized instance families exist.

The key interview concept:

> **Choose compute resources based on workload characteristics rather than simply choosing the biggest instance.**

---

## 13. EC2 Pricing Models — Basic Understanding

You should know the major models:

```text
On-Demand
Reserved / Savings-oriented commitments
Spot
```

#### On-Demand

Pay for usage without a long-term commitment.

Useful when:

```text
Workload is unpredictable
Need flexibility
```

#### Commitment-based pricing

You commit to usage for a period in exchange for discounted pricing.

Useful for predictable workloads.

#### Spot

Uses spare AWS capacity at potentially large discounts, but instances can be interrupted.

Good for workloads that can tolerate interruption:

```text
Batch jobs
Distributed processing
Flexible workloads
```

Don't use Spot blindly for a workload that cannot tolerate interruption.

---

## 14. Launching an EC2 Instance

At a high level, launching involves choosing:

```text
AMI
 ↓
Instance type
 ↓
Network/subnet
 ↓
Security group
 ↓
Storage
 ↓
IAM role
 ↓
Launch
```

This is what you'll encounter in the AWS console.

---

## 15. Key Pair

When using SSH to access a Linux EC2 instance, you commonly use a key pair.

Conceptually:

```text
Private key
     ↓
Your computer

Public key
     ↓
EC2
```

You use the private key to authenticate.

Example:

```bash
ssh -i my-key.pem ubuntu@<server-ip>
```

Never commit:

```text
my-key.pem
```

to Git.

---

## 16. Why SSH Keys Instead of Passwords?

SSH public-key authentication allows the server to verify possession of the private key without transmitting the private key.

Conceptually:

```text
Your machine
    │
Private key
    │
    ↓
SSH authentication
    │
    ↓
EC2
    │
Public key
```

Keep the private key secure.

---

## 17. Linux Connection

Once you're inside:

```bash
ssh -i my-key.pem ubuntu@<server-ip>
```

you're basically operating a Linux server.

Everything from [Chapter 2](../01-foundations/ch02-linux.md) becomes useful:

```bash
ls
cd
ps
top
free
df
systemctl
journalctl
curl
ss
grep
```

This is why learning Linux first was important.

---

## 18. Security Groups

An EC2 instance usually has one or more **Security Groups** controlling inbound/outbound traffic.

Think of a security group as a virtual firewall associated with network interfaces/resources.

Example:

```text
Internet
   │
   ├── SSH :22
   ├── HTTP :80
   └── HTTPS :443
```

You might configure:

```text
Port 22  → SSH
Port 80  → HTTP
Port 443 → HTTPS
```

But don't automatically open everything to the internet.

---

## 19. Security Group Example

Suppose your Node API listens on:

```text
3000
```

You could technically allow:

```text
TCP 3000
Source: 0.0.0.0/0
```

But in a production architecture, exposing application ports directly to the internet is often unnecessary.

A better architecture can be:

```text
Internet
   ↓
Load Balancer :443
   ↓
EC2 :3000
```

Then the EC2 security group can allow port 3000 **only from the load balancer/security-group path**, rather than from the whole internet.

We'll build this architecture in [Chapter 14](ch14-load-balancing-scaling.md).

---

## 20. Security Group Is Stateful

This is an important networking detail.

Security groups are **stateful**.

If an allowed inbound connection is established, the corresponding response traffic is automatically allowed.

You don't generally need to create a separate inbound rule just for the return packets.

Compare this later with NACLs, which are stateless.

---

## 21. Public vs Private EC2

An EC2 instance can be placed in a public or private subnet depending on the architecture.

#### Public application server

```text
Internet
   ↓
Public IP
   ↓
EC2
```

#### Private application server

```text
Internet
   ↓
Load Balancer
   ↓
Private EC2
```

The second is often preferred for application tiers because the EC2 instances aren't directly exposed to the public internet.

---

## 22. Public IP

A public IP allows internet-based communication when the surrounding networking configuration permits it.

Example:

```text
EC2
 ↓
Public IPv4
 ↓
Internet
```

But don't confuse:

```text
Public IP
```

with:

```text
Security permission
```

Having an IP doesn't automatically mean traffic is allowed.

Networking requires multiple pieces to align:

```text
Route
+
Security Group
+
Network configuration
+
Application listening
```

---

## 23. Private IP

Inside a VPC, EC2 has a private IP.

For example:

```text
10.0.1.25
```

This can be used for communication inside the VPC.

Example:

```text
EC2
  │
  └──→ RDS private IP
```

This is usually preferable to exposing databases publicly.

---

## 24. Elastic IP — Basic Concept

An EC2 public IPv4 address can change under certain stop/start scenarios.

If you need a persistent public IPv4 address, AWS provides **Elastic IP** addresses.

Conceptually:

```text
Elastic IP
    ↓
EC2
```

However, in modern architectures you often don't want users connecting directly to an EC2 IP at all.

Instead:

```text
Users
 ↓
DNS
 ↓
Load Balancer
 ↓
EC2
```

We'll get there later.

---

## 25. EBS

EBS = **Elastic Block Store**.

Think of it as persistent block storage attached to EC2.

```text
EC2
 │
 └── EBS volume
       ↓
     Disk data
```

It can store:

```text
OS files
Application files
Logs
Other persistent data
```

depending on your architecture.

---

## 26. EC2 Local Disk vs EBS

An important concept:

```text
EC2 compute
      +
EBS storage
```

The instance is compute.

EBS is block storage.

This separation lets storage persist independently of the compute lifecycle in many common scenarios.

---

## 27. Don't Put Your Database on EC2 by Default

You technically can:

```text
EC2
 ↓
PostgreSQL
```

but then **you** have to handle much more:

```text
Backups
Updates
Replication
Failover
Monitoring
Storage management
```

That's why managed databases such as RDS exist.

We'll cover RDS in [Chapter 13](ch13-rds-databases.md).

---

## 28. User Data

When launching an EC2 instance, you can provide **user data**.

It's commonly used for startup/bootstrap commands.

Example:

```bash
#!/bin/bash

apt update -y
apt install -y docker.io

systemctl enable docker
systemctl start docker
```

Conceptually:

```text
EC2 starts
   ↓
User data executes
   ↓
Install/configure software
   ↓
Server becomes ready
```

This is a simple form of instance bootstrapping.

---

## 29. EC2 Instance Metadata

EC2 exposes instance metadata to the instance itself.

Applications can use it to obtain information about the instance/environment.

Modern AWS security guidance emphasizes using the **Instance Metadata Service v2 (IMDSv2)** rather than older approaches.

You don't need to memorize the endpoint details yet.

Understand:

```text
EC2
 ↓
Instance metadata
 ↓
Instance information / temporary role credentials
```

This becomes important when discussing IAM roles on EC2.

---

## 30. EC2 IAM Role

Remember [Chapter 9](ch09-aws-fundamentals-iam.md)?

Instead of:

```text
EC2
 ↓
AWS access key hardcoded in application
```

use:

```text
EC2
 ↓
IAM role
 ↓
Temporary credentials
 ↓
AWS services
```

For example:

```text
Node API
   ↓
EC2 IAM Role
   ↓
S3:GetObject
```

The AWS SDK can obtain temporary credentials through the instance role mechanism.

This is a **very important interview concept**.

---

## 31. Deploying Docker on EC2

Now we're finally connecting our Docker knowledge to AWS.

Suppose you've already built:

```text
my-api:1.0
```

You could:

```text
EC2
 ↓
Install Docker
 ↓
Pull image
 ↓
Run container
```

For example:

```bash
docker pull <registry>/my-api:1.0
```

Then:

```bash
docker run -d \
  --name api \
  -p 3000:3000 \
  my-api:1.0
```

Now:

```text
EC2:3000
   ↓
Docker
   ↓
Node.js
```

---

## 32. Complete Request Flow

This is one of the most important diagrams in the entire roadmap.

Suppose you have a public EC2 server.

```text
                    Internet
                       │
                       ↓
                    Public IP
                       │
                       ↓
                Security Group
                       │
                       ↓
                    EC2
                       │
                       ↓
                 Docker :3000
                       │
                       ↓
                 Node.js API
                       │
                       ↓
                   Express
```

A request:

```text
GET /users
```

travels through that stack.

---

## 33. More Production-Like Architecture

Instead of exposing EC2 directly:

```text
User
 ↓
Internet
 ↓
Load Balancer
 ↓
EC2
 ↓
Docker
 ↓
Node.js
```

We'll eventually add:

```text
                 Internet
                     ↓
                   DNS
                     ↓
              Load Balancer
               /          \
             EC2          EC2
              ↓            ↓
           Docker       Docker
              \            /
               \          /
                  RDS
```

This is where high availability starts becoming meaningful.

---

## 34. Installing Docker on EC2

On a Linux EC2 instance, you can install Docker using the appropriate distribution packages/repository.

The exact commands depend on whether you're using:

```text
Ubuntu
Amazon Linux
```

For example, conceptually:

```bash
sudo apt update
sudo apt install docker.io
```

Then:

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

Verify:

```bash
docker --version
```

Then:

```bash
sudo docker ps
```

The exact package-management commands aren't the important part.

The architecture is.

---

## 35. Deployment Manually

A basic manual deployment:

```text
Developer
    ↓
Build Docker image
    ↓
Push to registry
    ↓
SSH into EC2
    ↓
docker pull
    ↓
Stop old container
    ↓
Start new container
```

For example:

```bash
docker pull registry/my-api:abc123
```

Then:

```bash
docker stop api
docker rm api
```

Then:

```bash
docker run -d \
  --name api \
  -p 3000:3000 \
  registry/my-api:abc123
```

This works, but it's not a sophisticated production deployment.

That's why CI/CD and orchestration exist.

---

## 36. Connect to Chapter 6

We previously had:

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

Now:

```text
GitHub
   ↓
GitHub Actions
   ↓
Docker Image
   ↓
Container Registry
   ↓
EC2
   ↓
Docker
   ↓
Node.js
```

Eventually we'll automate the entire process.

---

## 37. EC2 Monitoring

Once your application is running, you need to know:

```text
CPU
Memory
Disk
Network
Application health
```

Linux commands can help:

```bash
top
free -h
df -h
ss -tulpn
```

AWS also provides monitoring capabilities through **CloudWatch**, which we'll study later.

---

## 38. CPU Problem

Suppose your API suddenly becomes slow.

You SSH into EC2:

```bash
top
```

and see:

```text
CPU = 100%
```

Possible causes:

```text
Infinite loop
CPU-heavy operation
Traffic spike
Memory pressure causing other effects
Poorly optimized code
```

Don't immediately upgrade the instance.

First investigate the cause.

---

## 39. Memory Problem

Check:

```bash
free -h
```

Suppose:

```text
RAM nearly exhausted
```

Possible causes:

```text
Memory leak
Too many processes
Large workload
Insufficient instance size
```

Again:

> Diagnose first, resize second.

---

## 40. Disk Problem

Check:

```bash
df -h
```

Suppose:

```text
Disk = 100%
```

Your application may fail to:

- write logs
- create temporary files
- write application data

Possible causes:

```text
Logs
Docker images
Temporary files
Application data
```

This is a classic production troubleshooting problem.

---

## 41. Network Problem

Check:

```bash
ss -tulpn
```

You might discover:

```text
Node listening on 127.0.0.1:3000
```

instead of:

```text
0.0.0.0:3000
```

Then external connections may fail.

Remember [Chapter 7](../02-containers/ch07-docker-fundamentals.md):

```typescript
app.listen(3000, "0.0.0.0");
```

---

## 42. EC2 Instance States

You should understand:

```text
Pending
Running
Stopping
Stopped
Shutting-down
Terminated
```

The important distinction:

#### Stop

Instance is shut down but can generally be started again.

#### Terminate

Instance is deleted/terminated and cannot simply be started again.

Be careful with terminology.

---

## 43. Auto Scaling

What if one EC2 instance isn't enough?

```text
Users
  ↓
EC2
  ↓
CPU 100%
```

Instead:

```text
Users
   ↓
Load Balancer
   ↓
┌──────┬──────┬──────┐
EC2   EC2    EC2
```

And when traffic increases:

```text
3 instances
 ↓
5 instances
 ↓
10 instances
```

When traffic decreases:

```text
10
 ↓
5
 ↓
3
```

This is the foundation of **Auto Scaling**.

We'll study load balancing and scaling in [Chapter 14](ch14-load-balancing-scaling.md).

---

## 44. Horizontal vs Vertical Scaling

You already learned this in [Chapter 1](../01-foundations/ch01-cloud-devops-fundamentals.md).

#### Vertical

Make instance bigger:

```text
2 CPU / 4 GB
       ↓
8 CPU / 16 GB
```

#### Horizontal

Add instances:

```text
1 EC2
 ↓
3 EC2
 ↓
10 EC2
```

For highly available stateless APIs, horizontal scaling is often a key architectural pattern.

---

## 45. Stateless API

Suppose:

```text
EC2 A
EC2 B
EC2 C
```

A user's request can go to any instance.

That works best when the API doesn't store critical session state locally.

Instead:

```text
API instances
      ↓
Shared database
      +
Shared cache/session store
```

This is why stateless backend design is important.

---

## 46. What Should NOT Live Only on EC2?

Avoid treating one EC2 machine as the permanent home of everything.

For example:

```text
❌ User uploads only on EC2 disk
❌ Database only on EC2
❌ Important state only inside Docker container
```

Prefer appropriate managed/shared services:

```text
Files → S3
Database → RDS
Cache → ElastiCache/Redis
Compute → EC2/ECS/EKS/Lambda
```

We'll learn these services in later responses.

---

## 47. EC2 Security Checklist

For an internet-facing application:

```text
✓ Least-privilege IAM role
✓ Restrictive security groups
✓ Keep OS/packages updated
✓ Don't expose unnecessary ports
✓ Use HTTPS
✓ Don't store secrets in source code
✓ Don't expose database publicly unnecessarily
✓ Monitor logs/metrics
✓ Use backups where appropriate
✓ Use SSH carefully
```

And ideally:

```text
Internet
   ↓
Load Balancer :443
   ↓
Private EC2
```

rather than:

```text
Internet
   ↓
EC2 :22, :3000, :5432...
```

---

## 48. SSH Security

SSH commonly uses:

```text
Port 22
```

Don't blindly open:

```text
0.0.0.0/0 → port 22
```

if you can avoid it.

Depending on your architecture, you can restrict administrative access through:

- specific trusted IPs
- VPN/private connectivity
- AWS Systems Manager mechanisms

For modern AWS environments, **Systems Manager Session Manager** can often reduce the need for direct public SSH access.

You don't need to master Session Manager yet; know why it exists.

---

## 49. EC2 + IAM + Docker

Put everything we've learned together:

```text
                       AWS
                        │
                       VPC
                        │
                    Private Subnet
                        │
                       EC2
                        │
                   IAM Role
                    /     \
                   /       \
              S3 access   Other AWS APIs
                        │
                      Docker
                        │
                    Node.js
                        │
                    Express
```

The EC2 instance gets permissions through its role, while Docker runs your application.

---

## 50. Real Deployment Architecture

Here's the architecture we're building toward:

```text
                         Users
                           │
                           ↓
                         DNS
                           │
                           ↓
                    Load Balancer
                      /         \
                     /           \
                  AZ-A           AZ-B
                   │               │
                  EC2             EC2
                   │               │
                Docker           Docker
                   │               │
               Node API        Node API
                    \             /
                     \           /
                       ↓       ↓
                          RDS
                           │
                          S3
```

And:

```text
IAM
 ↓
controls access
```

while:

```text
CloudWatch
 ↓
monitors everything
```

That architecture will emerge naturally over the next few responses.

---

## 51. EC2 Interview Questions

You should be able to answer these.

#### Fundamentals

1. What is EC2?
2. What is an AMI?
3. AMI vs EC2 instance?
4. What is an instance type?
5. How do you choose an instance type?
6. On-Demand vs Spot?
7. What is EBS?

#### Networking

8. What is a security group?
9. Why shouldn't you expose every EC2 port?
10. Public vs private EC2?
11. Public IP vs private IP?
12. What does `0.0.0.0:3000` mean?
13. Why might an application be running but unreachable?

#### Security

14. How should an EC2 application access S3?
15. Why use an IAM role instead of hardcoded credentials?
16. Why is unrestricted SSH access dangerous?
17. How can you reduce direct SSH exposure?

#### Deployment

18. How would you deploy a Dockerized Node.js application to EC2?
19. What happens when you run `docker run -p 3000:3000`?
20. How would you update the application?
21. How would you roll back?

#### Scaling

22. Vertical vs horizontal scaling?
23. Why use multiple EC2 instances?
24. Why put a load balancer in front of EC2?
25. What is Auto Scaling?

---

## 🔥 Interview Scenario

#### Question

> Your Node.js application is running successfully on EC2, but users can't access it from the internet. How do you debug it?

Don't jump to one answer.

Walk through the layers:

```text
1. Is EC2 running?
        ↓
2. Does Node process exist?
        ↓
3. docker ps
        ↓
4. docker logs
        ↓
5. Is Node listening on 0.0.0.0:3000?
        ↓
6. Is Docker port mapping correct?
        ↓
7. Security Group allows required traffic?
        ↓
8. Subnet route is correct?
        ↓
9. Public IP / load balancer configuration?
        ↓
10. Application itself returning errors?
```

This is exactly why we learned:

```text
Linux
+
Networking
+
Docker
+
AWS
```

in that order.

---

## 🧪 Practical Project

Take your TypeScript backend.

Build:

```text
Node.js
   ↓
Docker
   ↓
EC2
```

#### Local

```bash
docker build -t my-api:1.0 .
```

#### Registry

Push the image to a registry.

#### EC2

Install Docker and run:

```bash
docker pull <your-image>
```

Then:

```bash
docker run -d \
  --name my-api \
  -p 3000:3000 \
  <your-image>
```

Verify on EC2:

```bash
docker ps
docker logs my-api
curl http://localhost:3000/health
```

Then troubleshoot external connectivity using:

```text
Security Group
Routing
Public/private networking
Port mapping
Application binding
```

**Don't use production secrets or open unnecessary ports just for the exercise.**

---

## 🧠 The Most Important Mental Model

EC2 isn't just:

> "AWS's virtual machine service."

Think:

```text
                 AWS
                  │
                 VPC
                  │
                Subnet
                  │
                 EC2
          ┌───────┼────────┐
          ↓       ↓        ↓
        Linux   Docker   IAM Role
                  │
                  ↓
              Node.js API
                  │
                  ↓
                Port
```

And an actual request:

```text
User
 ↓
Internet
 ↓
DNS
 ↓
Load Balancer
 ↓
EC2
 ↓
Security Group
 ↓
Docker
 ↓
Node.js
 ↓
Express
 ↓
Database / S3
```

Once you understand this flow, AWS becomes much less intimidating.
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 9: AWS Fundamentals + IAM](ch09-aws-fundamentals-iam.md) · [Chapter 11: S3 + AWS Storage](ch11-s3-storage.md) → · [Revision sheet](../../revision/ch10-revision.md)
