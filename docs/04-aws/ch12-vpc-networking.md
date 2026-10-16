# Chapter 12 — VPC + AWS Networking

> **Source:** Response 12 of the original conversation (`source-archive/src-12.txt`, lines 1–1465) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch12-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

This is one of the **most important AWS responses for SWE/backend interviews**.

You already learned networking fundamentals in [Chapter 4](../01-foundations/ch04-networking.md). We're now taking those concepts and mapping them to AWS.

By the end, you should be able to look at this:

```text
                         INTERNET
                            │
                            ↓
                    Internet Gateway
                            │
                    ┌───────┴────────┐
                    │      VPC       │
                    │                │
              Public Subnet      Private Subnet
                    │                │
                   ALB              EC2
                                     │
                                    RDS
```

and explain **exactly why each component exists and how traffic flows.**

---

## 1. What Is a VPC?

VPC = **Virtual Private Cloud**.

It's your logically isolated network inside AWS.

Think of it as:

> **Your own private network in AWS.**

For example:

```text
AWS Region
    │
    ↓
   VPC
    │
 ┌──┴────────────────────┐
 │                       │
Public Subnets       Private Subnets
 │                       │
ALB                    EC2
                        │
                       RDS
```

Inside a VPC you control things such as:

- IP address ranges
- subnets
- routing
- network access
- internet connectivity
- private connectivity

---

## 2. Why Do We Need a VPC?

Imagine putting everything directly on the public internet:

```text
Internet
 ├── EC2
 ├── Database
 ├── Redis
 └── Internal services
```

That's a terrible architecture for most production systems.

Instead:

```text
                  Internet
                     │
                     ↓
              Public Network
                     │
                     ↓
                  Private
                  Network
                     │
               ┌─────┴─────┐
               ↓           ↓
             EC2          RDS
```

The VPC gives you network isolation and control.

---

## 3. VPC CIDR

When creating a VPC, you choose an IP range.

For example:

```text
10.0.0.0/16
```

This gives you a large private address space.

You can then divide it into subnets.

For example:

```text
VPC
10.0.0.0/16

├── Public subnet
│   10.0.1.0/24
│
├── Public subnet
│   10.0.2.0/24
│
├── Private subnet
│   10.0.11.0/24
│
└── Private subnet
    10.0.12.0/24
```

This connects directly to the CIDR/subnetting concepts from [Chapter 4](../01-foundations/ch04-networking.md).

---

## 4. Why `/16` and `/24`?

Remember:

```text
10.0.0.0/16
```

is the larger network.

Then:

```text
10.0.1.0/24
```

is a smaller network inside it.

Conceptually:

```text
VPC
10.0.0.0/16
        │
        ├── 10.0.1.0/24
        ├── 10.0.2.0/24
        ├── 10.0.11.0/24
        └── 10.0.12.0/24
```

Don't just memorize `/16` and `/24`.

Understand that **CIDR determines the address range available to the network/subnet**.

---

## 5. Subnet

A subnet is a subdivision of your VPC's IP range.

Example:

```text
VPC: 10.0.0.0/16
          │
          ├── Public subnet
          │   10.0.1.0/24
          │
          └── Private subnet
              10.0.10.0/24
```

A subnet exists within a single Availability Zone.

Therefore:

```text
Region
 ├── AZ-A
 │    ├── Public subnet
 │    └── Private subnet
 │
 └── AZ-B
      ├── Public subnet
      └── Private subnet
```

---

## 6. Why Multiple AZs?

Suppose:

```text
Region
 ├── AZ-A
 │    └── EC2
 │
 └── AZ-B
      └── EC2
```

If AZ-A experiences a major failure:

```text
EC2 A ❌
```

you can potentially continue serving through:

```text
EC2 B
```

This is the basis of multi-AZ architecture.

---

## 7. Public vs Private Subnet

This is **extremely important**.

A subnet is generally called public when its route table has a route to an Internet Gateway.

For example:

```text
Public subnet
      │
      ↓
Internet Gateway
      │
      ↓
Internet
```

A private subnet does not have a direct route to the Internet Gateway.

For example:

```text
Private subnet
      │
      ↓
NAT Gateway
      │
      ↓
Internet
```

for outbound internet access.

The key distinction is **routing**, not simply whether the resource has a public IP.

---

## 8. Internet Gateway

An **Internet Gateway (IGW)** connects your VPC to the internet.

Conceptually:

```text
Internet
   │
   ↓
Internet Gateway
   │
   ↓
VPC
```

But simply attaching an Internet Gateway to a VPC does **not** automatically make every subnet public.

The subnet's route table must direct internet traffic appropriately.

---

## 9. Route Table

A route table determines where network traffic should go.

Think:

> **If traffic is going to X, send it to Y.**

Example:

```text
Destination       Target

10.0.0.0/16       local
0.0.0.0/0         igw
```

Meaning:

```text
10.0.0.0/16
    ↓
Stay inside VPC

0.0.0.0/0
    ↓
Internet Gateway
```

---

## 10. `0.0.0.0/0`

This means:

> Any IPv4 destination not covered by a more specific route.

It's often called the **default route**.

For example:

```text
0.0.0.0/0 → Internet Gateway
```

means unmatched IPv4 traffic goes toward the internet gateway.

---

## 11. Public Subnet Architecture

Example:

```text
VPC
│
└── Public Subnet
     │
     ├── Route table
     │      0.0.0.0/0 → IGW
     │
     └── EC2
```

The EC2 may have:

```text
Private IP
+
Public IPv4
```

and can communicate with the internet when security rules and other networking requirements permit it.

---

## 12. Private Subnet Architecture

Example:

```text
VPC
│
└── Private Subnet
     │
     └── EC2
```

The route table does not directly send internet traffic to the IGW.

Instead, if outbound internet access is required:

```text
Private EC2
    ↓
NAT Gateway
    ↓
Internet Gateway
    ↓
Internet
```

---

## 13. NAT Gateway

NAT = **Network Address Translation**.

A NAT Gateway allows resources in private subnets to initiate outbound connections to the internet without making those resources directly reachable from the internet.

Example:

```text
Private EC2
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

For example, EC2 may need to:

```text
apt update
download packages
call an external API
download dependencies
```

while remaining without a direct inbound internet route.

---

## 14. Important NAT Concept

Suppose:

```text
Private EC2
10.0.10.25
```

It sends:

```text
HTTPS request → example.com
```

The NAT Gateway translates the source address for internet communication.

The external server doesn't get a direct route back to:

```text
10.0.10.25
```

The important concept is:

```text
Private resource
      ↓
Outbound internet access
      ↓
No direct inbound internet route
```

---

## 15. Does NAT Allow Internet → Private EC2?

Generally:

**No.**

A NAT Gateway is designed for outbound connections initiated from the private side.

It does not make the private EC2 instance directly internet-accessible.

That's a major security benefit.

---

## 16. Production Architecture

Now we can create:

```text
                       INTERNET
                           │
                           ↓
                    Internet Gateway
                           │
                      Public Subnet
                           │
                    ┌──────┴──────┐
                    ↓             ↓
                   ALB           NAT GW
                                  │
                           Private Subnet
                                  │
                             ┌────┴────┐
                             ↓         ↓
                            EC2       EC2
                             │         │
                             └────┬────┘
                                  ↓
                            Private RDS
```

This is a very common cloud architecture pattern.

---

## 17. Security Groups

You've already seen security groups in [Chapter 10](ch10-ec2-compute.md).

Let's now place them into the VPC architecture.

A Security Group acts as a **stateful virtual firewall** for supported AWS resources/network interfaces.

Example:

```text
Internet
   ↓
ALB Security Group
   ↓
ALB
   ↓
EC2 Security Group
   ↓
EC2
```

---

## 18. Security Group Referencing

Instead of saying:

```text
Allow EC2 from 0.0.0.0/0
```

you can conceptually say:

```text
EC2 Security Group
   ↓
Allow traffic
   ↓
from ALB Security Group
```

This is much more precise.

Architecture:

```text
Internet
   ↓
ALB
   ↓
SG: ALB
   ↓
SG: API
   ↓
EC2
```

The EC2 doesn't need to accept application traffic from everyone.

---

## 19. Database Security Group

Now add RDS.

Suppose:

```text
EC2
 ↓
RDS PostgreSQL
```

EC2 security group:

```text
SG-API
```

RDS security group:

```text
SG-DB
```

Allow:

```text
SG-DB
Port 5432
Source = SG-API
```

Meaning:

> Only resources associated with the API security group can connect to PostgreSQL on port 5432.

This is far better than:

```text
5432 from 0.0.0.0/0
```

---

## 20. Network ACLs

NACL = **Network Access Control List**.

It operates at the subnet level.

Think:

```text
Security Group
→ resource/network interface level

NACL
→ subnet level
```

Another major difference:

```text
Security Group → stateful
NACL           → stateless
```

Because NACLs are stateless, inbound and outbound rules must be considered independently.

---

## 21. Security Group vs NACL

| Feature | Security Group | NACL |
|---|---|---|
| Scope | Resource/network interface | Subnet |
| Stateful | Yes | No |
| Rules | Allow-focused model | Allow + deny |
| Typical use | Primary resource-level firewall | Subnet-level traffic control |

For your interviews:

> **Security groups are usually the primary fine-grained access control mechanism around resources, while NACLs provide an additional subnet-level network control layer.**

---

## 22. Stateful Example

Suppose:

```text
Client → EC2
TCP 443
```

If the inbound connection is allowed by the security group, return traffic for that established connection is handled automatically by the stateful nature of the SG.

You don't need to create a separate "return traffic" rule in the same way you would with a stateless firewall.

---

## 23. DNS Inside AWS

DNS is essential for cloud architecture.

Instead of connecting:

```text
http://10.0.10.25:3000
```

applications can use names.

For example:

```text
api.internal
db.internal
```

AWS provides **Route 53** for DNS services.

We'll study Route 53 in [Chapter 16](ch16-route53-cloudfront-waf.md).

---

## 24. VPC DNS

VPC networking provides DNS capabilities that allow resources to resolve hostnames within AWS environments.

This is why architectures can use:

```text
database endpoint
```

instead of hardcoding an IP address.

This is important because infrastructure can change.

---

## 25. VPC Endpoints

Here's an important concept.

Suppose private EC2 needs S3.

Naive architecture:

```text
Private EC2
   ↓
NAT Gateway
   ↓
Internet
   ↓
S3
```

But AWS can provide private connectivity mechanisms such as **VPC endpoints**.

Conceptually:

```text
Private EC2
    ↓
VPC Endpoint
    ↓
AWS Service
    ↓
S3
```

This can avoid routing certain AWS service traffic through the public internet/NAT path and can improve security and architecture.

You don't need to memorize every endpoint type.

Know:

> **VPC endpoints provide private connectivity from a VPC to supported AWS services.**

---

## 26. Gateway vs Interface Endpoints

At a high level:

#### Gateway endpoint

Commonly associated with services such as:

```text
S3
DynamoDB
```

#### Interface endpoint

Uses private network interfaces and private connectivity for many AWS services.

You don't need deep implementation knowledge for every service.

Just understand the distinction.

---

## 27. IPv4 Private Address Ranges

From [Chapter 4](../01-foundations/ch04-networking.md), remember:

```text
10.0.0.0/8
172.16.0.0/12
192.168.0.0/16
```

AWS VPCs commonly use these private IPv4 ranges.

For example:

```text
10.0.0.0/16
```

Then:

```text
10.0.1.0/24
10.0.2.0/24
10.0.11.0/24
10.0.12.0/24
```

---

## 28. Subnet Design

A common architecture:

```text
VPC: 10.0.0.0/16

AZ-A
 ├── Public:  10.0.1.0/24
 └── Private: 10.0.11.0/24

AZ-B
 ├── Public:  10.0.2.0/24
 └── Private: 10.0.12.0/24
```

Then:

```text
Public subnets
→ Load Balancer

Private application subnets
→ EC2

Private database subnets
→ RDS
```

---

## 29. Three-Tier Architecture

Now you're ready for a classic architecture.

```text
                 INTERNET
                     │
                     ↓
              Public Subnets
                     │
                Load Balancer
                     │
                     ↓
            Application Subnets
                     │
               Node.js API
                     │
                     ↓
             Database Subnets
                     │
                   RDS
```

This is called a **three-tier architecture**.

Typically:

```text
Presentation
     ↓
Application
     ↓
Data
```

---

## 30. Why Private Database Subnets?

You don't want:

```text
Internet
   ↓
PostgreSQL :5432
```

Instead:

```text
Internet
   ↓
ALB
   ↓
EC2
   ↓
RDS :5432
```

The database doesn't need direct public internet access.

This dramatically reduces the attack surface.

---

## 31. Example Traffic Flow

User requests:

```text
https://api.example.com/users
```

Flow:

```text
User
 ↓
DNS
 ↓
Load Balancer
 ↓
EC2
 ↓
Node.js
 ↓
RDS
```

Networking:

```text
Internet
 ↓
IGW
 ↓
Public subnet
 ↓
ALB
 ↓
Private subnet
 ↓
EC2
 ↓
Private subnet
 ↓
RDS
```

Security groups:

```text
Internet → ALB SG :443

ALB SG → API SG :3000

API SG → DB SG :5432
```

This is an **excellent interview diagram**.

---

## 32. Why Not Expose Node.js Port 3000?

You could:

```text
Internet
 ↓
EC2 :3000
```

But there's little reason to expose your application directly if an ALB can handle internet-facing traffic.

Instead:

```text
Internet
 ↓
ALB :443
 ↓
EC2 :3000
```

Then:

```text
EC2 SG
→ only accepts 3000 from ALB SG
```

Much cleaner.

---

## 33. NAT Gateway and High Availability

Suppose you have:

```text
AZ-A → NAT Gateway A
AZ-B → NAT Gateway B
```

This avoids making a single NAT Gateway a cross-AZ dependency for all private workloads.

Conceptually:

```text
Private AZ-A → NAT-A
Private AZ-B → NAT-B
```

This can improve resilience, though NAT Gateway usage also has cost implications.

For interviews, understand the tradeoff:

> **High availability often requires avoiding single points of failure, but redundancy can increase cost and operational complexity.**

---

## 34. Route Tables in This Architecture

Public route table:

```text
Destination       Target

10.0.0.0/16       local
0.0.0.0/0         IGW
```

Private route table:

```text
Destination       Target

10.0.0.0/16       local
0.0.0.0/0         NAT Gateway
```

Now you can see why the names "public" and "private" make sense.

---

## 35. How Traffic Stays Inside VPC

Suppose:

```text
EC2:
10.0.11.10

RDS:
10.0.12.20
```

Destination:

```text
10.0.12.20
```

matches:

```text
10.0.0.0/16 → local
```

So the traffic stays within the VPC.

It doesn't need to go through:

```text
Internet
```

This is why private networking is powerful.

---

## 36. Troubleshooting AWS Networking

This is where your networking knowledge becomes practical.

Suppose:

```text
EC2 → RDS
```

fails.

Don't randomly modify things.

Check:

```text
1. Correct RDS endpoint?
2. Correct port? 5432?
3. EC2 and RDS network connectivity?
4. Route tables?
5. Security Group on RDS?
6. Source SG/IP allowed?
7. NACL?
8. Database actually running?
9. Credentials?
10. Application configuration?
```

This layered approach is extremely important.

---

## 37. Troubleshooting Internet → EC2

Suppose:

```text
User → EC2
```

doesn't work.

Check:

```text
EC2 running?
      ↓
Application listening?
      ↓
0.0.0.0 rather than localhost?
      ↓
Correct port?
      ↓
Security Group?
      ↓
Subnet route?
      ↓
Internet Gateway?
      ↓
Public IP?
      ↓
NACL?
```

This should now feel familiar from the Linux + Docker + networking responses.

---

## 38. `curl` Is Your Friend

Suppose Node listens on:

```text
3000
```

On EC2:

```bash
curl http://localhost:3000/health
```

If this works:

```text
Node application probably works locally
```

But external access fails:

```text
curl localhost → works
external request → fails
```

then investigate:

```text
Port binding
Docker port mapping
Security Group
Routing
Public/private architecture
```

That's a very useful diagnostic distinction.

---

## 39. VPC Flow Logs — Basic Awareness

AWS provides **VPC Flow Logs** for capturing information about IP traffic to/from network interfaces.

Conceptually:

```text
Traffic
 ↓
VPC Flow Logs
 ↓
Logs
 ↓
Analysis
```

They can help investigate networking issues.

We won't go deeply into their configuration now; you'll see observability later.

---

## 40. AWS Network Architecture to Remember

This is probably the single most important diagram from this response:

```text
                         INTERNET
                             │
                             ↓
                     Internet Gateway
                             │
                    ┌────────┴────────┐
                    │      VPC       │
                    │                │
              Public Subnets         │
                    │                │
                    ↓                │
              Load Balancer          │
                    │                │
              ┌─────┴─────┐          │
              ↓           ↓          │
          Private AZ-A  Private AZ-B │
              │           │           │
             EC2         EC2          │
              │           │           │
              └─────┬─────┘           │
                    ↓                 │
                 RDS                  │
             Private subnet           │
                                      │
Private outbound traffic → NAT GW ───┘
```

And security:

```text
Internet
   ↓
ALB SG :443

ALB SG
   ↓
API SG :3000

API SG
   ↓
DB SG :5432
```

---

## 41. Interview Questions

You should now be able to answer these.

#### VPC

1. What is a VPC?
2. Why do we need a VPC?
3. What is CIDR?
4. What is a subnet?
5. Why is each subnet associated with one AZ?
6. Public vs private subnet?
7. What makes a subnet public?

#### Routing

8. What is a route table?
9. What does `0.0.0.0/0` mean?
10. What is an Internet Gateway?
11. What is a NAT Gateway?
12. Why does a private subnet need NAT?
13. Does NAT allow inbound internet traffic to private EC2?

#### Security

14. Security Group vs NACL?
15. Stateful vs stateless?
16. Why shouldn't RDS be publicly accessible?
17. How would you allow EC2 to access RDS?
18. Why use security-group-to-security-group rules?

#### Architecture

19. Design a VPC for a Node.js backend.
20. Where would you put the load balancer?
21. Where would you put EC2?
22. Where would you put RDS?
23. Why put application servers in private subnets?
24. Why use multiple AZs?
25. How would private EC2 access S3?

---

## 🔥 Major Interview Scenario

#### Question:

> Design the network architecture for a production Node.js API with PostgreSQL.

A strong answer starts:

```text
                 Internet
                     ↓
                    DNS
                     ↓
              Load Balancer
                     ↓
          ┌──────────┴──────────┐
          ↓                     ↓
       AZ-A                  AZ-B
    Private subnet         Private subnet
          ↓                     ↓
        EC2                   EC2
          └──────────┬──────────┘
                     ↓
                    RDS
               Private subnet
```

Then explain:

```text
ALB → public subnets

EC2 → private subnets

RDS → private database subnets

Internet Gateway → public connectivity

NAT Gateway → outbound internet for private resources

Security Groups → restrict traffic between tiers

Multiple AZs → improve availability
```

That is a very solid **SWE-level AWS networking answer**.

---

## 🧪 Practical Exercise

Take your Dockerized Node.js backend and draw:

```text
VPC
│
├── Public Subnet
│    └── Load Balancer
│
├── Private Subnet
│    └── Node.js / EC2
│
└── Private Database Subnet
     └── PostgreSQL
```

Then add:

```text
Internet Gateway
NAT Gateway
Route Tables
Security Groups
```

Finally, draw the allowed flows:

```text
Internet
   ↓ 443
ALB
   ↓ 3000
Node API
   ↓ 5432
PostgreSQL
```

Then answer:

> **Which component would you change if EC2 can reach the internet but the internet cannot reach EC2?**

Think through:

```text
Public IP
+
Route table
+
Internet Gateway
+
Security Group
+
NACL
+
Application listening
```

---

## 🧠 The Mental Model

Don't memorize AWS networking as a list of services.

Think:

```text
VPC
 │
 ├── CIDR
 │
 ├── Subnets
 │     ├── Public
 │     └── Private
 │
 ├── Route Tables
 │
 ├── Internet Gateway
 │
 ├── NAT Gateway
 │
 ├── Security Groups
 │
 ├── NACLs
 │
 └── VPC Endpoints
```

And the production pattern:

```text
                    INTERNET
                        ↓
                      ALB
                        ↓
              ┌─────────┴─────────┐
              ↓                   ↓
             EC2                 EC2
              └─────────┬─────────┘
                        ↓
                       RDS

       Private workloads → NAT/VPC endpoints
```

This is the foundation for almost everything we're going to do next.
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 11: S3 + AWS Storage](ch11-s3-storage.md) · [Chapter 13: RDS + Databases on AWS](ch13-rds-databases.md) → · [Revision sheet](../../revision/ch12-revision.md)
