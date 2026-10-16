# Chapter 9 — AWS Fundamentals + IAM

> **Source:** Response 9 of the original conversation (`source-archive/src-09.txt`, lines 1–1484) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch09-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

Now we enter the **AWS section**, which is one of the highest-value parts of this roadmap for your SWE/backend placement preparation.

The goal isn't to memorize hundreds of AWS services.

The goal is to understand:

> **How a real application is deployed, secured, connected, scaled, and operated on AWS.**

We'll build that understanding service-by-service.

---

## 1. What Is AWS?

**Amazon Web Services (AWS)** is a cloud platform that provides infrastructure and managed services over the internet.

Instead of buying:

```text
Servers
Storage
Networking equipment
Databases
Load balancers
Firewalls
```

you can provision them through AWS.

For example:

```text
Your TypeScript API
       ↓
     AWS
       ├── EC2
       ├── RDS
       ├── S3
       ├── VPC
       ├── IAM
       └── CloudWatch
```

You pay for the resources/services you use according to their pricing models.

---

## 2. Why AWS Matters for You

As a backend/SWE engineer, you don't necessarily need to become an AWS administrator.

But you should understand how your backend operates in the cloud.

For example:

```text
User
 ↓
DNS
 ↓
Load Balancer
 ↓
Node.js containers
 ↓
PostgreSQL
 ↓
S3
```

And:

```text
                    AWS
                     │
              ┌──────┴──────┐
              ↓             ↓
          Application      Data
              │             │
           EC2/ECS/EKS     RDS/S3
```

You should know **what each component does and why you'd use it**.

---

## 3. AWS Global Infrastructure

Three concepts are fundamental:

```text
Region
Availability Zone
Edge Location
```

---

## 4. Region

A **Region** is a geographic AWS location containing multiple Availability Zones.

Examples:

```text
ap-south-1
us-east-1
eu-west-1
```

For example:

```text
Mumbai Region
      │
      ├── Availability Zone A
      ├── Availability Zone B
      └── Availability Zone C
```

You choose a region when deploying many AWS resources.

---

## 5. Why Multiple Regions?

Suppose your application operates primarily in India.

You might deploy in:

```text
ap-south-1
```

because geographical proximity can influence latency and regulatory/data requirements.

For global systems, you might have:

```text
Users
 ├── India → Mumbai
 ├── Europe → Europe region
 └── US → US region
```

Multi-region architecture can improve resilience and latency, but introduces substantial complexity.

Don't assume:

> "Multi-region is always better."

It depends on the requirements.

---

## 6. Availability Zone

An Availability Zone, or **AZ**, is an isolated location within an AWS Region designed to reduce the impact of failures.

Conceptually:

```text
             AWS Region
                  │
        ┌─────────┼─────────┐
        ↓         ↓         ↓
       AZ-A      AZ-B      AZ-C
```

You don't want your entire production system depending on one AZ.

For example:

```text
Bad:

API → AZ-A only
```

If AZ-A has a major failure:

```text
API ❌
```

Better:

```text
          Load Balancer
          /           \
       AZ-A           AZ-B
        │               │
      API             API
```

We'll use this heavily when we discuss load balancing and scaling.

---

## 7. Region vs Availability Zone

Interview question:

> What's the difference between an AWS Region and an Availability Zone?

Answer:

> **A Region is a geographic AWS infrastructure area containing multiple isolated Availability Zones. An Availability Zone is an isolated location within a Region used to improve availability and fault isolation.**

Remember:

```text
Region
 ├── AZ
 ├── AZ
 └── AZ
```

---

## 8. Edge Locations

AWS also operates edge locations closer to end users.

These are important for services such as:

```text
CloudFront
```

which we'll study later.

Conceptually:

```text
Origin
  │
  ↓
CloudFront
  │
  ├── Edge location → India
  ├── Edge location → Europe
  └── Edge location → US
```

Users can retrieve cached content from locations closer to them.

---

## 9. AWS Account

An AWS account is an important security and billing boundary.

Inside your account you can have:

```text
IAM
VPCs
EC2
S3
RDS
Lambda
etc.
```

Organizations may use multiple AWS accounts:

```text
AWS Organization
      │
      ├── Production account
      ├── Development account
      ├── Security account
      └── Logging account
```

For your interview preparation, understand the concept rather than memorizing enterprise account structures.

---

## 10. IAM — The Most Important AWS Security Concept

IAM = **Identity and Access Management**.

It answers:

> **Who are you, and what are you allowed to do?**

For example:

```text
Developer
   ↓
Can access EC2
Cannot delete production database
```

or:

```text
Node.js application
   ↓
Can read S3 bucket
Cannot modify IAM
```

This is authorization.

---

## 11. Authentication vs Authorization

Very important.

#### Authentication

> Who are you?

Example:

```text
Username + password
MFA
Access credentials
```

#### Authorization

> What are you allowed to do?

Example:

```text
Read S3
Write S3
Delete S3
Launch EC2
```

Think:

```text
Authentication
       ↓
      WHO?
       ↓
Authorization
       ↓
     WHAT?
```

---

## 12. IAM Components

The main things you should understand are:

```text
IAM User
IAM Group
IAM Role
IAM Policy
```

---

## 13. IAM User

An IAM user represents an identity within an AWS account.

Example:

```text
Alice
 ↓
IAM User
```

A user can have permissions attached directly or through groups/policies.

Historically, developers sometimes used IAM users with long-lived access keys for CLI/programmatic access.

For production workloads, however, AWS generally recommends using **IAM roles and temporary credentials** instead of embedding long-lived credentials.

---

## 14. IAM Group

A group allows permissions to be managed for multiple users.

Example:

```text
Developers
   │
   ├── Alice
   ├── Bob
   └── Charlie
```

You can attach policies to the group.

Then the users inherit those permissions.

This avoids manually attaching identical permissions to every user.

---

## 15. IAM Role

**Roles are extremely important.**

A role is an identity that can be assumed by a trusted entity.

For example:

```text
EC2
 ↓
Assume IAM Role
 ↓
Temporary credentials
 ↓
Access S3
```

Your application doesn't need:

```text
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

hardcoded inside the application.

Instead:

```text
EC2
 ↓
IAM Role
 ↓
Temporary credentials
 ↓
AWS API
```

This is a much better security model.

---

## 16. Example

Suppose your Node.js backend needs to upload files to S3.

Bad architecture:

```text
Node.js
 ↓
Hardcoded AWS credentials
 ↓
S3
```

Better:

```text
Node.js
 ↓
EC2/ECS/EKS
 ↓
IAM Role
 ↓
Temporary AWS credentials
 ↓
S3
```

This is an extremely useful interview answer.

---

## 17. IAM Policy

A policy defines permissions.

A policy is generally represented as JSON.

Example:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

This essentially says:

```text
Allow
 ↓
s3:GetObject
 ↓
objects inside my-bucket
```

---

## 18. Understanding the Policy

Break it down:

```json
"Effect": "Allow"
```

means permission is allowed.

```json
"Action": "s3:GetObject"
```

defines what operation is allowed.

```json
"Resource": "arn:aws:s3:::my-bucket/*"
```

defines what resource the permission applies to.

Conceptually:

```text
WHO
 ↓
CAN DO WHAT
 ↓
TO WHICH RESOURCE
```

---

## 19. Least Privilege

This is one of the most important security principles.

Suppose your API only needs:

```text
Read S3 objects
```

Don't give it:

```text
AdministratorAccess
```

Instead:

```text
s3:GetObject
```

for the required bucket/path.

Think:

```text
Required permission
      ↓
Give exactly that
      ↓
Nothing unnecessary
```

This is **least privilege**.

---

## 20. Bad vs Good IAM

Bad:

```text
Application
    ↓
AdministratorAccess
```

If the application is compromised:

```text
Attacker
   ↓
Application
   ↓
Administrator permissions
   ↓
Potentially huge blast radius
```

Better:

```text
Application
    ↓
Limited IAM role
    ↓
s3:GetObject
    ↓
Specific bucket
```

Now the potential blast radius is smaller.

---

## 21. IAM Role vs IAM User

Very common interview question.

#### User

Typically represents a person or persistent identity.

```text
Developer
 ↓
IAM User
```

#### Role

Designed to be assumed by trusted entities.

```text
EC2
 ↓
IAM Role
```

or:

```text
GitHub Actions
 ↓
IAM Role
```

or:

```text
Lambda
 ↓
IAM Role
```

Roles are particularly important for workloads because they can provide temporary credentials.

---

## 22. IAM and CI/CD

Remember [Chapter 6](../03-cicd-gitops/ch06-cicd-github-actions.md)?

We discussed GitHub Actions.

Suppose:

```text
GitHub Actions
       ↓
Deploy to AWS
```

A naive approach is storing:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

as long-lived GitHub secrets.

A better modern architecture is:

```text
GitHub Actions
      ↓
OIDC
      ↓
AWS IAM Role
      ↓
Temporary credentials
      ↓
AWS
```

The key idea is:

> **Use short-lived credentials and federated identity instead of long-lived static credentials where possible.**

We'll use this when connecting CI/CD to AWS.

---

## 23. AWS CLI

AWS provides a command-line interface.

Install/configure it and then commands look like:

```bash
aws sts get-caller-identity
```

This is an excellent command to understand.

It tells you which AWS identity your CLI is currently using.

Conceptually:

```text
Your terminal
     ↓
AWS CLI
     ↓
AWS STS
     ↓
Current identity
```

---

## 24. Why `get-caller-identity` Is Useful

Suppose your deployment says:

```text
AccessDenied
```

Before changing random permissions, check:

```bash
aws sts get-caller-identity
```

You might discover:

```text
Wrong account
Wrong role
Wrong identity
```

This is a very practical troubleshooting technique.

---

## 25. AWS Credentials

AWS CLI/application SDKs need credentials to make authenticated API calls.

Common sources include:

```text
Environment variables
AWS credential/config files
IAM role credentials
Federated identity
```

For cloud workloads, prefer role-based temporary credentials where applicable.

Don't put credentials in:

```text
Git repository
Docker image
Source code
```

---

## 26. AWS SDK with Node.js

Your TypeScript application can use AWS SDK packages.

For example, S3.

Conceptually:

```typescript
import { S3Client } from "@aws-sdk/client-s3";

const s3 = new S3Client({
  region: process.env.AWS_REGION
});
```

Notice something important:

We didn't write:

```typescript
const accessKey = "...";
const secretKey = "...";
```

The AWS SDK can obtain credentials through the standard AWS credential provider mechanisms.

This is the architecture you want.

---

## 27. AWS Resource Naming

AWS resources often have identifiers such as:

```text
ARN
```

ARN = **Amazon Resource Name**.

Example:

```text
arn:aws:s3:::my-bucket
```

An ARN uniquely identifies many AWS resources.

IAM policies frequently use ARNs to specify resources.

You don't need to memorize every ARN format.

Understand:

```text
ARN
 ↓
Specific AWS resource identifier
```

---

## 28. AWS Shared Responsibility Model

Very important for interviews.

AWS secures:

```text
Cloud infrastructure
Physical facilities
Hardware
Underlying infrastructure
```

You are responsible for things such as:

```text
Your application
IAM configuration
Data
Operating system configuration on certain services
Network configuration
Security settings
```

The exact responsibility varies depending on the service.

Think:

```text
AWS
 ↓
Security OF the cloud

Customer
 ↓
Security IN the cloud
```

This is a simplification, but a useful mental model.

---

## 29. Example: EC2

With EC2, you're responsible for more of the operating environment.

Conceptually:

```text
AWS
 ↓
Physical infrastructure
 ↓
Hypervisor
 ↓
EC2 instance
 ↓
Your responsibility
 ├── OS
 ├── Packages
 ├── Application
 └── Configuration
```

This is different from a more managed service where AWS handles more of the underlying infrastructure.

We'll explore this in [Chapter 10](ch10-ec2-compute.md).

---

## 30. AWS VPC — Preview

You'll hear VPC constantly.

VPC = **Virtual Private Cloud**.

It gives you a logically isolated network in AWS.

Conceptually:

```text
AWS Region
    │
    ↓
   VPC
    │
 ┌──┴───────────┐
 ↓              ↓
Public subnet  Private subnet
```

Inside it you'll eventually learn:

```text
CIDR
Subnets
Route tables
Internet Gateway
NAT Gateway
Security Groups
NACLs
```

We already learned the networking fundamentals in [Chapter 4](../01-foundations/ch04-networking.md).

Now we're going to map those concepts onto AWS.

---

## 31. AWS Service Categories

You don't need to memorize every AWS service.

Think in categories.

#### Compute

```text
EC2
Lambda
ECS
EKS
```

#### Storage

```text
S3
EBS
EFS
```

#### Database

```text
RDS
DynamoDB
ElastiCache
```

#### Networking

```text
VPC
Route 53
CloudFront
ELB
```

#### Security

```text
IAM
KMS
WAF
Secrets Manager
```

#### Monitoring

```text
CloudWatch
CloudTrail
```

We'll cover the important ones throughout the roadmap.

---

## 32. AWS CLI Practical Flow

Suppose you have AWS CLI configured.

Check identity:

```bash
aws sts get-caller-identity
```

List S3 buckets:

```bash
aws s3 ls
```

Get region configuration:

```bash
aws configure get region
```

You can also specify a region:

```bash
aws s3 ls --region ap-south-1
```

The goal isn't to memorize every command.

You should understand that:

```text
AWS CLI
   ↓
AWS API
   ↓
AWS service
```

---

## 33. IAM Policy Evaluation — Basic Mental Model

When AWS receives a request:

```text
Application
    ↓
AWS API request
    ↓
Identity
    ↓
Policies
    ↓
Allowed?
```

Conceptually:

```text
Explicit Deny
     ↓
Overrides Allow
```

Otherwise, an explicit applicable Allow is needed.

If no permission grants the action, the request is generally denied.

This is why IAM debugging often involves examining:

```text
Who?
 ↓
What action?
 ↓
Which resource?
 ↓
Which policies?
 ↓
Any explicit deny?
```

---

## 34. Common IAM Mistake

Suppose you have:

```text
Role A
```

with:

```text
s3:GetObject
```

but your application tries:

```text
s3:PutObject
```

Result:

```text
AccessDenied
```

The solution isn't:

```text
Give AdministratorAccess
```

Instead ask:

```text
Does the application actually need PutObject?
```

If yes:

```text
Add narrowly scoped PutObject permission.
```

This demonstrates least-privilege thinking.

---

## 35. IAM Security Rules You Should Remember

#### Rule 1

Don't commit credentials.

#### Rule 2

Don't put credentials in Docker images.

#### Rule 3

Prefer IAM roles for AWS workloads.

#### Rule 4

Use temporary credentials where possible.

#### Rule 5

Use least privilege.

#### Rule 6

Use MFA for appropriate human identities.

#### Rule 7

Don't give applications unnecessary administrative permissions.

---

## 36. AWS Architecture We Are Building

You should now visualize the future architecture:

```text
                         AWS
                          │
                    ┌─────┴─────┐
                    │   Region  │
                    │           │
                    │    VPC    │
                    │           │
                    │  ┌─────┐  │
                    │  │ ALB │  │
                    │  └──┬──┘  │
                    │     │     │
                    │  ┌──┴───┐ │
                    │  │ EC2  │ │
                    │  │ API  │ │
                    │  └──┬───┘ │
                    │     │     │
                    │   RDS     │
                    │           │
                    └───────────┘
```

And IAM controls who/what can access these resources.

---

## 37. Connect This to Docker

Previously:

```text
Docker
 ↓
Container
 ↓
Node.js API
```

Now:

```text
AWS
 ↓
EC2
 ↓
Docker
 ↓
Node.js container
```

Later:

```text
AWS
 ↓
ECS / EKS
 ↓
Docker containers
```

So we're building the stack progressively.

---

## 38. Connect This to CI/CD

Previously:

```text
GitHub
 ↓
GitHub Actions
 ↓
Docker
```

Now:

```text
GitHub
 ↓
GitHub Actions
 ↓
Docker Build
 ↓
AWS
```

Security:

```text
GitHub Actions
       ↓
      OIDC
       ↓
    IAM Role
       ↓
Temporary credentials
       ↓
AWS
```

That's the production-grade direction we'll build toward.

---

## 39. Interview Questions

You should be able to answer these:

#### AWS fundamentals

1. What is AWS?
2. What is a Region?
3. What is an Availability Zone?
4. Region vs AZ?
5. Why deploy across multiple AZs?
6. What is an edge location?
7. What is a VPC?

#### IAM

8. What is IAM?
9. Authentication vs authorization?
10. IAM user vs role?
11. What is an IAM policy?
12. What is least privilege?
13. What is an ARN?
14. Why should applications use IAM roles?
15. Why are long-lived access keys dangerous?
16. What happens if an application gets `AdministratorAccess`?

#### Practical

17. How would a Node.js application upload to S3 securely?
18. How would GitHub Actions deploy to AWS securely?
19. How would you debug an `AccessDenied` error?
20. How do you find which AWS identity your CLI is using?
21. What is the AWS shared responsibility model?

---

## 🧪 Practical Lab

If you have an AWS account, do these carefully.

#### 1. Install/configure AWS CLI

Then:

```bash
aws sts get-caller-identity
```

Understand the returned identity.

#### 2. Explore IAM

Create/inspect:

```text
User
Group
Role
Policy
```

Do **not** create overly broad production permissions just for experimentation.

#### 3. Understand a policy

Take a policy like:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::example-bucket/*"
    }
  ]
}
```

Answer:

```text
Who?
→ Identity receiving policy

What?
→ s3:GetObject

Where?
→ example-bucket objects

Effect?
→ Allow
```

#### 4. Connect the concepts

Draw:

```text
Node API
   ↓
IAM Role
   ↓
S3
```

Then explain why this is better than:

```text
Node API
   ↓
Hardcoded AWS keys
   ↓
S3
```

---

## 🧠 The AWS Mental Model

Don't try to memorize AWS as:

```text
EC2 = X
S3 = Y
RDS = Z
...
```

Instead think:

```text
                 AWS
                  │
        ┌─────────┼─────────┐
        ↓         ↓         ↓
     Compute    Storage   Database
        │         │         │
       EC2        S3        RDS
        │
        ↓
     Network
        │
       VPC
        │
        ↓
     Security
        │
       IAM
        │
        ↓
    Monitoring
        │
   CloudWatch
```

And your backend:

```text
                  User
                    ↓
                  AWS
                    ↓
                Networking
                    ↓
                Compute
                    ↓
             TypeScript API
               /         \
              ↓           ↓
            RDS           S3
              \           /
               \         /
                IAM Roles
```

That is the foundation for the next AWS responses.
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 8: Docker Deep Dive + Production](../02-containers/ch08-docker-production.md) · [Chapter 10: EC2 + AWS Compute](ch10-ec2-compute.md) → · [Revision sheet](../../revision/ch09-revision.md)
