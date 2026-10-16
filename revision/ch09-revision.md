# Chapter 9 — Revision Sheet: AWS Fundamentals + IAM

> Supplements [the full chapter](../docs/04-aws/ch09-aws-fundamentals-iam.md). Goal: understand **how a real application is deployed, secured, connected, scaled and operated on AWS** — not memorise hundreds of services.

## AWS basics

- **AWS** = cloud platform of infrastructure + managed services over the Internet; pay per use.
- **Region** (e.g. `ap-south-1` Mumbai, `us-east-1`, `eu-west-1`) = geographic location with multiple AZs. **AZ** = isolated location in a Region to reduce failure impact. **Edge location** = closer-to-user points used by CloudFront for caching.
- *Region vs AZ answer:* A Region is a geographic area containing multiple isolated AZs; an AZ is an isolated location within a Region used for availability and fault isolation.
- Don't put everything in one AZ (bad: API → AZ-A only). Better: Load Balancer → API in AZ-A and AZ-B. Multi-region improves resilience/latency but adds substantial complexity — not always better.
- **AWS account** = security + billing boundary. Organizations use multiple accounts (production, development, security, logging) under an AWS Organization.
- **VPC** (preview) = logically isolated network: CIDR, subnets, route tables, Internet Gateway, NAT Gateway, Security Groups, NACLs (Ch.12).

## Service categories

| Category | Services |
|---|---|
| Compute | EC2, Lambda, ECS, EKS |
| Storage | S3, EBS, EFS |
| Database | RDS, DynamoDB, ElastiCache |
| Networking | VPC, Route 53, CloudFront, ELB |
| Security | IAM, KMS, WAF, Secrets Manager |
| Monitoring | CloudWatch, CloudTrail |

## IAM — "Who are you, and what are you allowed to do?"

- **Authentication** = *who?* (username+password, MFA, access credentials). **Authorization** = *what?* (read/write/delete S3, launch EC2).
- **User** = a person/persistent identity (historically with long-lived access keys). **Group** = manage permissions for many users. **Role** = identity *assumed by trusted entities* (EC2, Lambda, GitHub Actions) giving **temporary credentials**. **Policy** = JSON permission document.

```json
{ "Version": "2012-10-17",
  "Statement": [{ "Effect": "Allow",
                  "Action": ["s3:GetObject"],
                  "Resource": "arn:aws:s3:::my-bucket/*" }] }
```
WHO → CAN DO WHAT (`Action`) → TO WHICH RESOURCE (`Resource`, an **ARN**). Example ARN: `arn:aws:s3:::my-bucket`.

- **Least privilege:** give exactly the permission needed (e.g. `s3:GetObject` on one bucket/path, not `AdministratorAccess`). A compromised admin app = huge **blast radius**.
- `AccessDenied` for `PutObject` with only `GetObject` → don't grant admin; ask whether PutObject is truly needed, then add a narrowly scoped permission.
- **Policy evaluation:** explicit **Deny overrides Allow**; otherwise an applicable explicit Allow is needed; no grant = denied. Debug: who? action? resource? which policies? any explicit deny?

### Secure patterns

| Need | Insecure | Better |
|---|---|---|
| Node.js uploads to S3 | Hard-coded keys | EC2/ECS/EKS → **IAM Role** → temporary credentials → S3 (the SDK finds credentials via the default provider chain: `new S3Client({ region: process.env.AWS_REGION })`) |
| GitHub Actions → AWS | Long-lived `AWS_ACCESS_KEY_ID/SECRET` in GitHub secrets | **OIDC** federation → IAM Role → short-lived credentials |

Credential sources: environment variables, credential/config files, IAM role credentials, federated identity. **Never** in Git, Docker images or source code.

### IAM rules (memorise)

1. Don't commit credentials. 2. Don't put credentials in Docker images. 3. Prefer IAM roles for workloads. 4. Use temporary credentials. 5. Least privilege. 6. MFA for human identities. 7. No unnecessary admin for apps.

## AWS CLI

`aws sts get-caller-identity` (which identity am I? — first step when debugging `AccessDenied`: wrong account/role/identity?), `aws s3 ls`, `aws configure get region`, `aws s3 ls --region ap-south-1`. CLI → AWS API → service.

## Shared responsibility model

AWS = security **OF** the cloud (facilities, hardware, underlying infrastructure). Customer = security **IN** the cloud (application, IAM config, data, OS config on certain services, network config, security settings). Varies by service — on EC2 you own OS, packages, application, configuration.

## Architecture preview

Region → VPC → ALB → EC2 (API) → RDS; IAM controls who/what can access resources. Progression: Docker container → EC2+Docker → ECS/EKS. CI/CD: GitHub Actions → Docker build → AWS via OIDC role.

## Added notes (not in source)

- An IAM **role has two policy types**: a **trust policy** (who may assume the role — e.g. `ec2.amazonaws.com` or GitHub's OIDC provider) and **permission policies** (what the role can do).
- For S3, `s3:ListBucket` applies to the **bucket ARN** (`arn:aws:s3:::my-bucket`), whereas `s3:GetObject` applies to **object ARNs** (`arn:aws:s3:::my-bucket/*`).
- Protect the account **root user** with MFA and avoid using it for daily work.
- Policy types beyond identity policies (resource-based policies, permission boundaries, Organizations SCPs) are not covered in this chapter.

## Interview questions (21) — pointers

AWS; Region; AZ; Region vs AZ; why multiple AZs; edge location; VPC; IAM; authN vs authZ; user vs role; policy; least privilege; ARN; why roles for apps; why long-lived keys are dangerous; consequence of `AdministratorAccess`; secure S3 upload from Node; secure GitHub Actions deploy (OIDC); debug `AccessDenied` (`sts get-caller-identity`, policies, explicit deny); find CLI identity; shared responsibility model.

<!-- NAV -->

---

← [Sheet 8](ch08-revision.md) · [Full chapter 9](../docs/04-aws/ch09-aws-fundamentals-iam.md) · [All revision material](README.md) · [Sheet 10](ch10-revision.md) →
