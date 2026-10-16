# Chapter 14 — Load Balancing + Scaling

> **Source:** Response 14 of the original conversation (`source-archive/src-14.txt`, lines 1–1849) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch14-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

We're following the roadmap exactly.

You've now learned:

- EC2
- VPC
- subnets
- route tables
- security groups
- RDS
- connection pooling
- Multi-AZ
- read replicas

Now we're going to solve the next problem:

> **What happens when one EC2 server isn't enough?**

This response is extremely important for **backend + system design + AWS interviews**.

---

## 1. The Problem With One Server

Imagine your Node.js application:

```text
                    INTERNET
                        │
                        ↓
                      EC2
                        │
                    Node.js
```

Initially:

```text
100 users
```

No problem.

Then:

```text
10,000 users
```

Then:

```text
100,000 users
```

Eventually:

```text
CPU ↑
Memory ↑
Requests ↑
Latency ↑
```

Your single EC2 instance becomes a bottleneck.

---

## 2. Vertical vs Horizontal Scaling

There are two fundamental ways to scale.

### Vertical Scaling

Make the machine bigger.

```text
Before:

EC2
4 CPU
16 GB RAM

       ↓

After:

EC2
16 CPU
64 GB RAM
```

Also called:

> **Scale up**

---

### Horizontal Scaling

Add more machines.

```text
        EC2
          ↓
       EC2 EC2
          ↓
    EC2 EC2 EC2
```

Also called:

> **Scale out**

For web applications, horizontal scaling is extremely important.

---

## 3. Why Horizontal Scaling?

Suppose:

```text
1 EC2
→ 1,000 requests/sec
```

You need:

```text
3,000 requests/sec
```

You could potentially use:

```text
3 EC2 instances
```

and distribute traffic.

```text
              INTERNET
                  │
                  ↓
             Load Balancer
             /      |      \
            ↓       ↓       ↓
          EC2-A   EC2-B   EC2-C
```

Now your workload is distributed.

---

## 4. But Who Decides Which EC2 Gets the Request?

That's the job of a:

> **Load Balancer**

A load balancer distributes incoming traffic across multiple backend servers.

Conceptually:

```text
Client
  │
  ↓
Load Balancer
  │
  ├──→ EC2 A
  ├──→ EC2 B
  └──→ EC2 C
```

AWS provides **Elastic Load Balancing (ELB)**.

The most relevant load balancer for your backend work is:

> **Application Load Balancer (ALB)**

---

## 5. ALB

ALB = **Application Load Balancer**.

It's designed for application-layer traffic such as HTTP/HTTPS.

Example:

```text
https://api.example.com/users
```

Flow:

```text
User
 ↓
ALB
 ↓
Node.js
```

Instead of:

```text
User
 ↓
EC2 directly
```

---

## 6. Why Put ALB in Front of EC2?

Without ALB:

```text
Internet
 ├── EC2-A
 ├── EC2-B
 └── EC2-C
```

How does the client know which EC2 to use?

With ALB:

```text
Internet
      ↓
     ALB
      ↓
 ┌────┼────┐
 ↓    ↓    ↓
EC2  EC2  EC2
```

The client only needs to know the ALB's endpoint/domain.

---

## 7. Target Groups

ALB doesn't simply have a random list of EC2 instances.

It uses a **Target Group**.

Conceptually:

```text
ALB
 │
 ↓
Target Group
 │
 ├── EC2-A
 ├── EC2-B
 └── EC2-C
```

The target group represents the backend destinations receiving traffic.

Targets can include supported resources such as:

- EC2 instances
- IP addresses
- containers, depending on architecture

---

## 8. Health Checks

This is one of the most important ALB concepts.

Imagine:

```text
EC2-A → healthy
EC2-B → healthy
EC2-C → crashed
```

You don't want:

```text
ALB
 ├── EC2-A ✅
 ├── EC2-B ✅
 └── EC2-C ❌
```

to keep sending requests to C.

So ALB performs health checks.

Example:

```text
GET /health
```

Expected:

```text
200 OK
```

Then:

```text
EC2-C ❌
```

is removed from normal traffic distribution.

---

## 9. Health Endpoint in Node.js

You can implement:

```typescript
app.get("/health", (req, res) => {
  res.status(200).json({
    status: "ok",
  });
});
```

Then the load balancer checks:

```text
GET /health
```

If the application responds correctly:

```text
200
```

the instance can remain healthy.

---

## 10. Health Check vs Application Monitoring

Don't confuse these.

A basic load balancer health check asks:

> **Can I successfully reach this backend and get an acceptable response?**

Observability can answer much more:

```text
CPU
memory
latency
errors
database failures
request rate
```

We'll study that more in Chapters [17](ch17-monitoring-security.md) and [22](../07-observability-sre/ch22-observability-reliability.md).

---

## 11. Load Balancing Algorithms

Conceptually, a load balancer can distribute requests using strategies such as:

#### Round Robin

```text
Request 1 → A
Request 2 → B
Request 3 → C
Request 4 → A
```

#### Least Outstanding Requests

Send traffic toward a target with fewer active requests, depending on the configured balancing behavior.

You don't need to memorize every algorithm.

Understand:

> **The load balancer decides which healthy target should receive each request.**

---

## 12. ALB Listener

A listener waits for incoming traffic.

Example:

```text
ALB
 │
 ├── Listener :80
 └── Listener :443
```

For production:

```text
HTTPS :443
```

is generally what users connect to.

The listener can then route traffic to a target group.

---

## 13. ALB Routing Rules

One powerful ALB feature is application-level routing.

Suppose:

```text
api.example.com/users
api.example.com/orders
```

You could conceptually route:

```text
/users/*
      ↓
Users Target Group

/orders/*
      ↓
Orders Target Group
```

You can also route based on hostnames.

For example:

```text
api.example.com
      ↓
API targets

admin.example.com
      ↓
Admin targets
```

This is why ALB is called an **Application** Load Balancer.

---

## 14. Security Group Architecture

Remember [Chapter 12](ch12-vpc-networking.md).

Don't do:

```text
Internet
   ↓
EC2 :3000
```

Instead:

```text
Internet
   ↓
ALB :443
   ↓
EC2 :3000
```

Security groups:

```text
Internet
   ↓
ALB-SG
   ↓
API-SG
   ↓
EC2
```

ALB SG:

```text
Allow HTTPS 443
from internet
```

EC2 SG:

```text
Allow 3000
from ALB-SG
```

This is a very common interview architecture.

---

## 15. The Bigger Architecture

Now combine everything:

```text
                         INTERNET
                             │
                             ↓
                          ALB :443
                             │
                ┌────────────┼────────────┐
                ↓            ↓            ↓
              EC2-A        EC2-B        EC2-C
                │            │            │
                └────────────┼────────────┘
                             ↓
                           RDS
```

Now we've solved:

```text
Multiple application servers
+
Traffic distribution
+
Health checking
+
Database connectivity
```

But there's another problem.

---

## 16. What If Traffic Changes?

Suppose:

```text
2 AM
100 users
```

You need:

```text
2 EC2 instances
```

At:

```text
8 PM
100,000 users
```

you might need:

```text
10 EC2 instances
```

Then at:

```text
3 AM
```

you don't need 10 machines.

You want infrastructure to adjust automatically.

That's where:

> **Auto Scaling Groups**

come in.

---

## 17. Auto Scaling Group

An **Auto Scaling Group (ASG)** manages a group of EC2 instances and can adjust the number of instances according to configured rules.

Conceptually:

```text
               Auto Scaling Group
                /      |      \
               ↓       ↓       ↓
             EC2-A   EC2-B   EC2-C
```

It can:

```text
Scale out
```

or:

```text
Scale in
```

---

## 18. Scale Out

Traffic increases:

```text
CPU ↑
Requests ↑
Latency ↑
```

ASG might increase:

```text
2 EC2
 ↓
3 EC2
 ↓
4 EC2
```

Architecture:

```text
                 ALB
              /   |   \
             ↓    ↓    ↓
            EC2  EC2  EC2
```

---

## 19. Scale In

Traffic decreases:

```text
100,000 users
     ↓
5,000 users
```

ASG might reduce:

```text
6 EC2
 ↓
4 EC2
 ↓
2 EC2
```

This reduces infrastructure usage and potentially cost.

---

## 20. Desired / Minimum / Maximum Capacity

An ASG can conceptually have:

```text
Minimum = 2
Desired = 3
Maximum = 10
```

Meaning:

```text
Normal:
3 instances

Never intentionally below:
2

Can scale up to:
10
```

This gives you controlled scaling boundaries.

---

## 21. Launch Template

How does ASG know what kind of EC2 instance to create?

A **Launch Template** defines important instance configuration.

Conceptually:

```text
Launch Template
 │
 ├── AMI
 ├── Instance type
 ├── Security Group
 ├── IAM role
 ├── User data
 └── Other configuration
```

Then:

```text
ASG
 ↓
Launch Template
 ↓
New EC2 instances
```

---

## 22. Why This Is Powerful

Suppose EC2-A dies.

ASG can replace it.

```text
Before:

EC2-A ✅
EC2-B ✅
EC2-C ❌

        ↓

ASG

        ↓

EC2-A ✅
EC2-B ✅
EC2-D ✅
```

This is a core reliability concept:

> **Replace failed instances rather than depending on manually repairing them.**

---

## 23. Immutable Infrastructure

This connects directly to Docker.

Instead of:

```text
Server broken
 ↓
SSH into server
 ↓
Manually fix
```

you can use:

```text
Broken instance
      ↓
Terminate
      ↓
Create fresh instance
      ↓
Deploy known image/application
```

This is much more repeatable.

---

## 24. Scaling Policies

ASG can use metrics to decide when to scale.

For example:

```text
CPU > threshold
       ↓
Scale out
```

or:

```text
CPU < threshold
       ↓
Scale in
```

You can also use other workload signals depending on architecture.

Important idea:

> **Scaling should respond to actual workload, not just arbitrary server count.**

---

## 25. Target Tracking

A common scaling approach is:

```text
Target CPU = 50%
```

The system tries to adjust capacity so the metric stays around the target.

Conceptually:

```text
CPU = 80%
 ↓
Need more capacity
 ↓
Scale out

CPU = 20%
 ↓
Potentially too much capacity
 ↓
Scale in
```

---

## 26. Step Scaling

Another strategy:

```text
CPU > 70%
→ add 1

CPU > 85%
→ add 2

CPU > 95%
→ add 4
```

The exact configuration depends on the workload.

For interviews, know:

```text
Target tracking
Step scaling
Scheduled scaling
```

at a conceptual level.

---

## 27. Scheduled Scaling

Some workloads are predictable.

Example:

```text
Every day:

8 AM → traffic starts rising
8 PM → traffic drops
```

You could proactively increase capacity before traffic arrives.

```text
7:30 PM
↓
Scale in

7:30 AM
↓
Scale out
```

This is **scheduled scaling**.

---

## 28. Auto Scaling Doesn't Mean Infinite Scaling

This is important.

Suppose:

```text
ASG max = 10
```

and traffic requires:

```text
20 instances
```

Your ASG won't magically create 20.

It stops at:

```text
10
```

Then you'll have to address the bottleneck through:

- larger instances
- higher max capacity
- better application performance
- caching
- database scaling
- architectural changes

---

## 29. The Database Problem Again

Suppose:

```text
EC2 = 2
```

and:

```text
RDS = handles workload
```

Now ASG scales:

```text
2 → 20 EC2
```

But all 20 connect to:

```text
RDS
```

Now:

```text
DB connections ↑
Queries ↑
CPU ↑
IO ↑
```

The application tier scales, but the database may become the bottleneck.

This is why:

> **Scaling one layer doesn't automatically scale the entire system.**

Excellent system-design concept.

---

## 30. Stateless Architecture

Horizontal scaling works best when your application servers are **stateless**.

Suppose:

```text
EC2-A
```

stores user session in its local memory:

```text
Session:
user123 → logged in
```

Then the next request goes to:

```text
EC2-B
```

EC2-B doesn't know about the session.

Problem.

---

## 31. Bad Stateful Design

```text
            ALB
          /     \
         ↓       ↓
       EC2-A   EC2-B
         │
      Session
      in RAM
```

Request 1:

```text
User → EC2-A
```

Request 2:

```text
User → EC2-B
```

EC2-B:

```text
"Who is this user?" ❌
```

---

## 32. Stateless Design

Instead:

```text
            ALB
          /     \
         ↓       ↓
       EC2-A   EC2-B
          \      /
           \    /
           Redis
```

Or use other appropriate centralized/state-management mechanisms.

Then:

```text
EC2-A
  ↓
Redis
```

and:

```text
EC2-B
  ↓
Redis
```

Both instances can access shared state.

---

## 33. JWT and Stateless Authentication

Another common approach is JWT-based authentication.

Conceptually:

```text
Client
  ↓
JWT
  ↓
EC2-A
```

Later:

```text
Client
  ↓
Same JWT
  ↓
EC2-B
```

EC2-B can validate the token without needing the login session stored in EC2-A's memory, assuming the architecture is designed appropriately.

But JWT itself introduces other concerns:

- token expiry
- revocation
- refresh tokens
- key management
- token size
- compromised tokens

So don't treat "JWT = automatically perfect scaling."

---

## 34. Sticky Sessions

Load balancers can also support session stickiness in appropriate configurations.

Conceptually:

```text
User A
 ↓
ALB
 ↓
EC2-A
```

and future requests from that user tend to go to:

```text
EC2-A
```

This can help legacy/stateful applications.

But it has drawbacks:

```text
EC2-A
 ↓
Many users
```

while:

```text
EC2-B
 ↓
Few users
```

You can get uneven load.

Therefore:

> **Stateless architecture is generally preferable for horizontally scaled web applications when practical.**

---

## 35. Session State vs Application State

Don't confuse:

```text
Application code
```

with:

```text
User/session state
```

Your Node.js application code should ideally be identical across instances:

```text
EC2-A → same application
EC2-B → same application
EC2-C → same application
```

Shared state should live in appropriate external systems:

```text
Redis
Database
Object storage
Dedicated state services
```

depending on what the data is.

---

## 36. Scaling Requests vs Scaling Resources

There are several levels of scaling.

```text
                    System
                      │
         ┌────────────┼────────────┐
         ↓            ↓            ↓
      Compute       Database      Cache
         │            │            │
       EC2/ASG       RDS         Redis
```

If compute is overloaded:

```text
Scale EC2
```

If DB is overloaded:

```text
Optimize DB
+
Scale DB
+
Replicas
+
Cache
```

If cache is overloaded:

```text
Scale/configure cache appropriately
```

You need to identify the **actual bottleneck**.

---

## 37. Load Balancer Failure

What if you have:

```text
Internet
   ↓
ALB
```

and the ALB itself fails?

AWS load-balancing services are designed as managed, highly available infrastructure across Availability Zones.

Conceptually:

```text
             ALB
          /       \
        AZ-A      AZ-B
```

You don't normally manage a single physical load-balancer server yourself.

That's another benefit of using managed cloud infrastructure.

---

## 38. Multi-AZ Application Architecture

A better architecture is:

```text
                       INTERNET
                           │
                           ↓
                          ALB
                    ┌──────┴──────┐
                    ↓             ↓
                  AZ-A           AZ-B
                    │             │
               Private          Private
                subnet           subnet
                    │             │
                   EC2           EC2
                    │             │
                    └──────┬──────┘
                           ↓
                          RDS
```

Now losing one AZ doesn't necessarily mean your whole application disappears.

---

## 39. Auto Scaling + ALB

These two services solve different problems.

#### ALB

Answers:

> **Where should this request go?**

#### ASG

Answers:

> **How many EC2 instances should exist?**

Together:

```text
                    ALB
                 /   |   \
                ↓    ↓    ↓
               EC2  EC2  EC2
                ↑    ↑    ↑
                └────┴────┘
                    ASG
```

That's a key distinction.

---

## 40. Health Checks + ASG

There can be multiple layers of health checking.

```text
ALB health check
      ↓
Is application target healthy?
```

ASG can also use health information to determine whether instances should be replaced.

Conceptually:

```text
EC2 unhealthy
    ↓
ASG detects unhealthy instance
    ↓
Terminate/replace
    ↓
New EC2
    ↓
ALB health check
    ↓
Healthy?
    ↓
Receive traffic
```

This is an excellent production lifecycle.

---

## 41. Complete Production Flow

Let's put everything together.

```text
                         INTERNET
                             │
                             ↓
                       Route 53 / DNS
                             │
                             ↓
                           ALB
                      ┌──────┴──────┐
                      ↓             ↓
                    AZ-A           AZ-B
                      │             │
                    EC2            EC2
                      │             │
                      └──────┬──────┘
                             ↓
                          RDS
```

Scaling:

```text
Traffic ↑
   ↓
ASG
   ↓
More EC2
   ↓
ALB distributes traffic
```

Failure:

```text
EC2 fails
   ↓
ALB stops sending traffic
   ↓
ASG replaces instance
   ↓
New instance becomes healthy
   ↓
ALB sends traffic
```

Database:

```text
EC2
 ↓
Connection Pool
 ↓
RDS
```

Caching:

```text
EC2
 ↓
Redis
 ↓
RDS when needed
```

---

## 42. What About Deployments?

Suppose:

```text
EC2-A → version 1
EC2-B → version 1
EC2-C → version 1
```

You deploy version 2.

You don't necessarily want:

```text
v1 ❌
v2 ❌
```

all at once.

This leads to deployment strategies such as:

#### Rolling deployment

```text
v1 v1 v1
 ↓
v2 v1 v1
 ↓
v2 v2 v1
 ↓
v2 v2 v2
```

#### Blue-Green

```text
Blue → v1
Green → v2
```

Switch traffic:

```text
Blue
 ↓
Green
```

#### Canary

```text
99% → v1
1%  → v2
```

Then gradually increase:

```text
90/10
70/30
50/50
0/100
```

These concepts connect directly to CI/CD from [Chapter 6](../03-cicd-gitops/ch06-cicd-github-actions.md).

---

## 43. Load Balancing vs Reverse Proxy

You learned reverse proxies in [Chapter 4](../01-foundations/ch04-networking.md).

They overlap conceptually.

A reverse proxy:

```text
Client
 ↓
Reverse Proxy
 ↓
Backend
```

A load balancer:

```text
Client
 ↓
Load Balancer
 ├── Backend A
 ├── Backend B
 └── Backend C
```

An ALB performs load balancing and application-level routing functions.

---

## 44. When Should You Scale?

Don't blindly use:

```text
CPU > 70%
```

as the only answer.

A better engineering approach is:

```text
Identify bottleneck
       ↓
Measure it
       ↓
Understand workload
       ↓
Choose scaling strategy
       ↓
Test
       ↓
Monitor
```

Possible bottlenecks:

```text
CPU
Memory
Network
Database
Disk
Connections
External APIs
Locks
Application code
```

---

## 45. Scaling Doesn't Fix Bad Code

Suppose your API performs:

```text
O(n²)
```

work unnecessarily.

You add:

```text
10 EC2 instances
```

You may temporarily increase capacity, but you've not fixed the fundamental inefficiency.

Always ask:

```text
Can I optimize?
```

before blindly scaling.

---

## 46. Scaling and Cost

More instances:

```text
Performance ↑
Cost ↑
```

Too few:

```text
Cost ↓
Latency ↑
Reliability ↓
```

So production engineering involves balancing:

```text
Performance
Availability
Reliability
Cost
Complexity
```

This becomes especially important in system design.

---

## 47. Interview Scenario #1

#### "Your Node.js API is receiving 10× normal traffic. What would you do?"

Strong reasoning:

```text
1. Check metrics
2. Identify bottleneck
3. Ensure ALB is distributing traffic
4. Scale EC2 horizontally if compute is bottleneck
5. Verify database isn't bottleneck
6. Check connection pool
7. Use caching where appropriate
8. Verify external dependencies
9. Monitor latency/error rate
10. Scale back when traffic decreases
```

Don't simply say:

> "Add more EC2."

---

## 48. Interview Scenario #2

#### "One EC2 instance is unhealthy. What happens?"

Potential flow:

```text
EC2 unhealthy
      ↓
ALB health check fails
      ↓
ALB stops routing requests there
      ↓
ASG detects unhealthy instance
      ↓
Instance replaced
      ↓
New instance starts
      ↓
Application starts
      ↓
ALB health check passes
      ↓
Traffic resumes
```

That's a very strong interview explanation.

---

## 49. Interview Scenario #3

#### "Why is your application stateless?"

Answer:

> Because any request should be able to reach any healthy application instance without depending on state stored locally on a particular server. Shared state can be moved to systems such as a database or Redis, which makes horizontal scaling and instance replacement easier.

Excellent backend answer.

---

## 50. What You Need to Know Deeply

#### 🔥 Master

- Load balancer concept
- ALB
- target groups
- listeners
- health checks
- security groups around ALB/EC2
- horizontal vs vertical scaling
- Auto Scaling Groups
- launch templates
- minimum/desired/maximum capacity
- scaling policies
- Multi-AZ application architecture
- stateless backend architecture
- session management
- database bottleneck during scaling
- connection pooling
- failure replacement
- rolling/blue-green/canary concepts

#### Medium

- target tracking
- step scaling
- scheduled scaling
- sticky sessions
- ALB routing rules
- deployment interactions

#### Awareness

- Network Load Balancer
- Gateway Load Balancer
- advanced ELB features

You don't need to become an AWS infrastructure specialist.

---

## 🧪 Practical Exercise

Take your Node.js backend and design:

```text
                         INTERNET
                             │
                             ↓
                            ALB
                       ┌─────┴─────┐
                       ↓           ↓
                     EC2-A       EC2-B
                       │           │
                       └─────┬─────┘
                             ↓
                            RDS
```

Then answer:

#### If traffic increases 5×:

```text
What scales?
```

Expected reasoning:

```text
ALB
 ↓
ASG
 ↓
EC2 instances ↑
```

Then ask:

```text
What could become the next bottleneck?
```

Possible:

```text
RDS
Redis
External API
Network
Connection pool
```

Then ask:

> What happens if EC2-A crashes?

You should be able to explain the complete health-check + replacement flow without looking at notes.

---

## 🧠 The Most Important Mental Model

Remember these four lines:

```text
ALB
→ distributes traffic

Target Group
→ defines backend targets

Health Check
→ determines whether targets should receive traffic

ASG
→ determines how many EC2 instances should exist
```

And:

```text
Horizontal scaling
→ more instances

Vertical scaling
→ bigger instance

Stateless application
→ easier horizontal scaling

Multi-AZ
→ better availability
```

---
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 13: RDS + Databases on AWS](ch13-rds-databases.md) · [Chapter 15: Lambda + Serverless + Messaging](ch15-lambda-serverless-messaging.md) → · [Revision sheet](../../revision/ch14-revision.md)
