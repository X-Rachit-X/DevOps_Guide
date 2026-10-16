# Chapter 32 — Advanced Terraform

> **Source:** Response 32 of the original conversation (`source-archive/src-32.txt`, lines 1–3135) · **Part II — Advanced extension (Responses 25–36)**  
> **Study aids:** [Revision sheet](../../revision/ch32-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md) · *includes an editorial supplement at the end*

<!-- SOURCE-BEGIN -->

We're continuing exactly on the roadmap.

You already learned Terraform fundamentals in **[Chapter 21](ch21-terraform.md)**:

- HCL
- providers
- resources
- variables
- outputs
- data sources
- `init / plan / apply / destroy`
- state
- modules
- remote state
- drift
- Terraform + GitHub Actions

So I will **not repeat the basics**. This response goes into how Terraform is actually structured and operated in a production team.

The goal is:

> **Be able to design, explain, review, troubleshoot, and safely use Terraform for real AWS infrastructure.**

---

## 1. First: What Terraform Is Really Doing

At a high level:

```text
Terraform Configuration
        ↓
Desired Infrastructure
        ↓
Terraform
        ↓
AWS APIs
        ↓
Actual Infrastructure
```

Terraform continuously tries to make:

```text
Actual Infrastructure
        ≈
Desired Configuration
```

It does this using:

```text
Configuration
+
State
+
Provider
+
Refresh/read operations
+
Dependency graph
```

The most important production concepts are therefore:

```text
State
Modules
Dependencies
Environments
Remote state
Locking
Drift
CI/CD
Security
```

---

## 2. Terraform State — The Most Important Advanced Concept

You've already seen:

```text
terraform.tfstate
```

But let's understand **why it exists**.

Suppose your code says:

```hcl
resource "aws_s3_bucket" "assets" {
  bucket = "my-company-assets"
}
```

Terraform creates:

```text
AWS S3 Bucket
```

Terraform needs to remember:

> "This particular AWS object corresponds to this particular Terraform resource."

That's what state helps track.

Conceptually:

```text
Terraform resource
       ↓
aws_s3_bucket.assets
       ↓
AWS object ID
       ↓
actual infrastructure
```

---

## 3. State Is Not Just a Cache

A common beginner mistake:

> "Terraform state is just a copy of AWS."

Not exactly.

State contains Terraform's understanding of managed resources and relationships.

It helps Terraform answer:

```text
What do I manage?
What infrastructure object corresponds to this resource?
What attributes are known?
What changed?
```

---

## 4. Why State Is Dangerous

Terraform state can contain sensitive information.

For example:

```text
resource attributes
IDs
connection information
sensitive values
```

Therefore:

**Never casually commit `terraform.tfstate` to Git.**

Your `.gitignore` should generally include:

```gitignore
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl
```

Actually, one nuance:

#### Don't ignore `.terraform.lock.hcl`

The lock file should normally be committed because it pins provider versions/checksums.

So a better `.gitignore` is:

```gitignore
.terraform/
*.tfstate
*.tfstate.*
*.tfplan
```

while keeping:

```text
.terraform.lock.hcl
```

in Git.

---

## 5. Local State vs Remote State

For a personal experiment:

```text
Terraform
   ↓
local terraform.tfstate
```

For a team:

```text
Developer A
      ↓
Remote State
      ↑
Developer B
```

You need centralized state.

A common AWS architecture is:

```text
Terraform
    ↓
S3
    ↓
Remote state
```

with state locking supported through the configured backend capabilities.

---

## 6. Why Remote State?

Imagine two developers:

```text
Developer A
terraform apply

Developer B
terraform apply
```

If both use independent local state:

```text
A's state ≠ B's state
```

This can cause dangerous inconsistencies.

Remote state provides a shared source of Terraform state.

---

## 7. State Locking

Suppose:

```text
Developer A
```

is applying infrastructure.

At the same time:

```text
Developer B
```

starts an apply.

We don't want both operations modifying the same state simultaneously.

Conceptually:

```text
Terraform Apply
      ↓
Acquire lock
      ↓
Modify infrastructure/state
      ↓
Release lock
```

Modern Terraform/AWS S3 backend configurations can use **native S3 state locking**, while older tutorials commonly show DynamoDB-based locking.

For current projects, follow the backend documentation for the Terraform/AWS versions you're actually using.

---

## 8. Why Locking Matters

Without proper coordination:

```text
A reads state
B reads state

A changes infrastructure
B changes infrastructure

A writes state
B writes stale state
```

Now Terraform's state can become inconsistent with reality.

Therefore:

> **Remote state + locking is fundamental for team Terraform.**

---

## 9. State Backend

A backend determines where Terraform stores state and how state operations are handled.

Conceptually:

```hcl
terraform {
  backend "s3" {
    bucket = "company-terraform-state"
    key    = "production/network/terraform.tfstate"
    region = "..."
  }
}
```

Now state isn't sitting on your laptop.

---

## 10. State Bucket Security

Your Terraform state bucket is extremely sensitive.

Use:

```text
encryption
versioning
restricted IAM
private access
logging/monitoring
```

You should **not** make your Terraform state bucket public.

Architecture:

```text
Terraform CI
     │
     │ IAM
     ↓
Private S3 state bucket
```

---

## 11. Bootstrap Problem

Interesting problem:

> Who creates the S3 bucket that stores Terraform state?

Terraform can't use the remote backend before the backend exists.

So you often have a bootstrap step.

Conceptually:

```text
Bootstrap Terraform
       ↓
Creates state infrastructure
       ↓
S3 backend
       ↓
Main Terraform configuration
```

In larger organizations, the state bucket/backend is often provisioned separately and managed centrally.

---

## 12. State File Versioning

Suppose someone accidentally destroys or corrupts state.

S3 versioning can provide historical versions.

Conceptually:

```text
state-v1
state-v2
state-v3
```

This gives you a recovery mechanism.

But:

> Don't treat versioning as a replacement for proper Terraform workflows.

It's a safety mechanism.

---

## 13. Terraform State Commands

You've seen these, but now understand when to use them.

```bash
terraform state list
```

Shows managed resources.

```bash
terraform state show aws_instance.web
```

Shows details.

```bash
terraform state rm aws_instance.web
```

Removes the resource from Terraform state **without necessarily deleting the real AWS resource**.

This is dangerous if misunderstood.

---

## 14. State RM Example

Suppose AWS has:

```text
EC2 instance
```

and Terraform state tracks it.

You run:

```bash
terraform state rm aws_instance.web
```

Now:

```text
AWS:
EC2 still exists

Terraform:
doesn't know it manages that EC2 anymore
```

If the resource remains in configuration and you run `plan`, Terraform may attempt to create another resource or otherwise show reconciliation changes.

So:

> `state rm` changes Terraform's tracking, not AWS itself.

---

## 15. Terraform Import

Suppose someone manually created:

```text
S3 bucket
```

in AWS.

Now you want Terraform to manage it.

That's where import comes in.

Conceptually:

```text
Existing AWS resource
       ↓
Terraform import
       ↓
Terraform state
       ↓
Terraform configuration
```

Modern Terraform supports import blocks as well as CLI workflows.

---

## 16. Import Does Not Automatically Give You Perfect Code

This is important.

Importing:

```text
AWS resource
```

doesn't mean:

```text
Beautiful Terraform configuration automatically created
```

You still need configuration that correctly represents the resource.

Think:

```text
Import
→ bring resource under Terraform management

Configuration
→ describe how Terraform should manage it
```

---

## 17. Terraform Plan After Import

After importing, run:

```bash
terraform plan
```

You may see changes.

Why?

Because:

```text
Existing infrastructure
≠
your Terraform configuration
```

Your job is to reconcile them.

---

## 18. Terraform Drift

Suppose Terraform says:

```text
EC2 type = t3.medium
```

Then someone manually changes it in AWS:

```text
t3.large
```

Now:

```text
Terraform config
      ↓
t3.medium

AWS actual
      ↓
t3.large
```

That's drift.

Terraform can detect the difference during planning/refresh behavior.

---

## 19. Why Drift Is Dangerous

Imagine:

```text
Terraform
    ↓
production infrastructure
```

but engineers also make manual console changes.

Eventually:

```text
Terraform ≠ AWS
```

Now nobody knows what the actual intended configuration is.

Therefore:

> **Infrastructure should preferably be managed through the declared Terraform workflow rather than ad-hoc console changes.**

This is one reason IaC improves operational consistency.

---

## 20. Terraform Modules

Now the most important reusable architecture concept.

Suppose you repeatedly create:

```text
VPC
Subnets
Route tables
NAT
Security groups
```

Instead of copying hundreds of lines:

```text
production-vpc.tf
staging-vpc.tf
dev-vpc.tf
```

create:

```text
modules/
└── vpc/
```

Then:

```text
production
    ↓
VPC module

staging
    ↓
VPC module

development
    ↓
VPC module
```

---

## 21. Why Modules?

Modules provide:

```text
reuse
consistency
abstraction
standardization
maintainability
```

Think of a Terraform module like a reusable function.

In programming:

```typescript
createDatabase(config)
```

Terraform:

```hcl
module "database" {
  source = "./modules/database"
}
```

---

## 22. Module Structure

Example:

```text
modules/
└── network/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    └── README.md
```

#### `main.tf`

Resources.

#### `variables.tf`

Inputs.

#### `outputs.tf`

Outputs.

---

## 23. Example Module

`variables.tf`:

```hcl
variable "vpc_cidr" {
  type = string
}
```

`main.tf`:

```hcl
resource "aws_vpc" "this" {
  cidr_block = var.vpc_cidr
}
```

`outputs.tf`:

```hcl
output "vpc_id" {
  value = aws_vpc.this.id
}
```

---

## 24. Calling the Module

Root configuration:

```hcl
module "network" {
  source = "./modules/network"

  vpc_cidr = "10.0.0.0/16"
}
```

Then:

```hcl
module.network.vpc_id
```

can be used elsewhere.

---

## 25. Module Input/Output Flow

Think:

```text
Root Module
     │
     │ inputs
     ↓
Child Module
     │
     │ creates infrastructure
     ↓
outputs
     │
     ↓
Root Module
```

This is the same idea as function arguments and return values.

---

## 26. Good Module Design

A good module should expose:

```text
important configuration
```

but hide:

```text
implementation details
```

For example:

```hcl
module "vpc" {
  source = "./modules/vpc"

  cidr_block = "10.0.0.0/16"
  az_count   = 3
}
```

The caller shouldn't need to know every route-table resource inside.

---

## 27. Don't Over-Modularize

This is a common Terraform mistake.

Bad:

```text
module-vpc
module-subnet
module-route-table
module-route
module-security-group
module-rule
```

for every tiny resource.

That can make the code harder to understand.

Prefer meaningful modules:

```text
network
eks
database
observability
```

when those boundaries make sense.

---

## 28. Root Module vs Child Module

Your project might look like:

```text
terraform/
│
├── main.tf
├── variables.tf
├── outputs.tf
│
└── modules/
    ├── network/
    ├── eks/
    ├── rds/
    └── monitoring/
```

The root module composes the infrastructure.

---

## 29. Environment Structure

Now the big question:

> How do we manage dev, staging, and production?

One pattern:

```text
environments/
├── dev/
├── staging/
└── prod/
```

Each environment calls shared modules.

```text
dev
 ↓
modules

staging
 ↓
modules

prod
 ↓
modules
```

---

## 30. Why Separate Environment State?

You generally don't want:

```text
development
staging
production
```

all sharing one state file.

Instead:

```text
dev state
staging state
prod state
```

Conceptually:

```text
S3
├── dev/terraform.tfstate
├── staging/terraform.tfstate
└── prod/terraform.tfstate
```

This reduces blast radius.

---

## 31. Blast Radius

Suppose one Terraform state manages:

```text
dev + staging + prod
```

A mistake can potentially affect everything.

Instead:

```text
State A → dev
State B → staging
State C → prod
```

Now the blast radius is smaller.

This is a very important production principle.

---

## 32. Terraform Workspaces

Terraform also provides:

```bash
terraform workspace
```

which can maintain separate state instances using the same configuration.

For example:

```text
dev
prod
```

But workspaces aren't automatically the best environment architecture.

For serious infrastructure, many teams prefer separate root configurations/state backends because they make environment boundaries explicit.

Interview answer:

> Workspaces provide separate state instances for the same configuration, but they should not automatically be treated as the solution to every environment-management problem.

---

## 33. Environment Pattern I Recommend You Understand

For your projects:

```text
infra/
├── modules/
│   ├── vpc/
│   ├── eks/
│   ├── rds/
│   └── redis/
│
└── environments/
    ├── dev/
    ├── staging/
    └── prod/
```

This is easy to reason about.

---

## 34. Variable Strategy

You don't want:

```hcl
replicas = 3
```

hardcoded everywhere.

Use variables:

```hcl
variable "environment" {
  type = string
}

variable "instance_type" {
  type = string
}
```

Then environment-specific values can be provided through appropriate variable files/configuration.

For example:

```text
dev.tfvars
prod.tfvars
```

---

## 35. Sensitive Variables

Example:

```hcl
variable "db_password" {
  type      = string
  sensitive = true
}
```

But:

> `sensitive = true` does not magically make the secret secure everywhere.

It mainly affects how Terraform displays the value.

You still need proper secret handling.

---

## 36. Don't Store Production Secrets in `.tfvars`

Avoid:

```text
prod.tfvars
```

containing:

```text
DB_PASSWORD=actual-production-password
```

and committing it to Git.

Better:

```text
AWS Secrets Manager
SSM Parameter Store
CI/CD secret store
appropriate external secret system
```

depending on the architecture.

---

## 37. Data Sources

You learned data sources earlier.

Now understand their production value.

Suppose a VPC already exists.

Instead of creating:

```hcl
resource "aws_vpc" ...
```

you can look it up:

```hcl
data "aws_vpc" "existing" {
  ...
}
```

Then:

```hcl
data.aws_vpc.existing.id
```

can be passed to other resources.

So:

```text
resource
→ Terraform creates/manages it

data source
→ Terraform reads existing information
```

---

## 38. Dependency Graph

Terraform builds a dependency graph.

Suppose:

```hcl
resource "aws_subnet" "private" {
  vpc_id = aws_vpc.main.id
}
```

Terraform sees:

```text
VPC
 ↓
Subnet
```

So it knows the subnet depends on the VPC.

---

## 39. Implicit Dependencies

This is preferred.

Example:

```hcl
vpc_id = aws_vpc.main.id
```

Terraform understands:

```text
Subnet → VPC
```

automatically.

---

## 40. Explicit Dependencies

Sometimes Terraform can't infer a dependency.

Then:

```hcl
depends_on = [
  aws_iam_role_policy.example
]
```

can explicitly tell Terraform:

> Don't proceed until this resource exists.

But don't overuse `depends_on`.

---

## 41. Why Overusing `depends_on` Is Bad

If you write:

```text
everything depends on everything
```

you unnecessarily serialize operations.

Terraform loses opportunities for parallelism.

Prefer:

```text
implicit dependency
```

whenever possible.

---

## 42. Terraform Graph

You can inspect the dependency graph:

```bash
terraform graph
```

Conceptually:

```text
VPC
├── Subnet
│   └── EC2
└── Route Table
```

This is useful for understanding complex infrastructure.

---

## 43. Lifecycle Meta-Arguments

Terraform has lifecycle controls.

One important one:

```hcl
lifecycle {
  prevent_destroy = true
}
```

Useful for critical resources.

For example:

```text
production database
```

You may want additional protection against accidental destruction.

---

## 44. `create_before_destroy`

Example:

```hcl
lifecycle {
  create_before_destroy = true
}
```

Conceptually:

```text
Old resource
      │
      ├── keep
      │
Create new resource
      │
      ↓
switch
      │
      ↓
remove old
```

Useful where replacement can cause downtime, assuming the resource supports the behavior and constraints allow it.

---

## 45. `ignore_changes`

You may encounter:

```hcl
lifecycle {
  ignore_changes = [
    tags
  ]
}
```

This tells Terraform to ignore changes to specified attributes.

But be careful.

If you ignore too much:

```text
Terraform
≠
actual infrastructure
```

and drift becomes harder to detect.

Use it intentionally.

---

## 46. Terraform Plan

`terraform plan` is one of your safest tools.

It tells you approximately:

```text
+ create
~ modify
- destroy
```

Example:

```text
+ aws_s3_bucket.assets
~ aws_instance.web
- aws_instance.old
```

Before production apply:

> **Read the plan.**

Never blindly run:

```bash
terraform apply -auto-approve
```

against production.

---

## 47. Saved Plans

You can create:

```bash
terraform plan -out=tfplan
```

Then:

```bash
terraform apply tfplan
```

This lets you apply the plan that was reviewed/generated.

This is useful in CI/CD.

---

## 48. Terraform CI/CD

A production pipeline can look like:

```text
Pull Request
     ↓
terraform fmt
     ↓
terraform validate
     ↓
security/static checks
     ↓
terraform plan
     ↓
review
     ↓
approval
     ↓
terraform apply
```

For production:

```text
manual approval
```

is often valuable.

---

## 49. GitHub Actions Example

Conceptually:

```yaml
name: Terraform

on:
  pull_request:

jobs:
  plan:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3

      - run: terraform init

      - run: terraform fmt -check

      - run: terraform validate

      - run: terraform plan
```

For actual production infrastructure, authentication should use short-lived credentials/workload identity such as OIDC rather than storing long-lived AWS access keys.

---

## 50. Terraform Apply Pipeline

A more complete model:

```text
PR
 ↓
fmt
 ↓
validate
 ↓
security scan
 ↓
plan
 ↓
human review
 ↓
merge
 ↓
apply
```

For production:

```text
merge
 ↓
approval
 ↓
apply
```

This gives you controlled infrastructure changes.

---

## 51. Terraform Security

A secure Terraform workflow should avoid:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

hardcoded in:

```text
GitHub secrets
source code
Terraform files
```

where possible.

Instead:

```text
GitHub Actions
      ↓
OIDC
      ↓
AWS IAM Role
      ↓
temporary credentials
      ↓
Terraform
```

You learned this architecture earlier.

Now you're applying it to Terraform.

---

## 52. Terraform Provider Lock File

When you run:

```bash
terraform init
```

Terraform can create:

```text
.terraform.lock.hcl
```

Commit it.

Why?

It records provider selections/checksums so different environments are less likely to unexpectedly use incompatible provider builds.

Think:

```text
Terraform code
+
provider lock
=
more reproducible infrastructure
```

---

## 53. Provider Version Constraints

Example:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
```

Don't blindly use:

```text
latest
```

without considering compatibility.

Pin sensible version ranges and review upgrades.

---

## 54. Terraform Upgrade

A provider or Terraform upgrade can change behavior.

Safe process:

```text
Read changelog
     ↓
Upgrade dev
     ↓
terraform init -upgrade
     ↓
plan
     ↓
test
     ↓
staging
     ↓
production
```

Don't upgrade infrastructure tooling directly in production without testing.

---

## 55. Terraform Version Management

Teams should agree on Terraform versions.

You can specify:

```hcl
terraform {
  required_version = ">= 1.x, < 2.0"
}
```

Use a range appropriate for your project's compatibility policy.

The exact version should be chosen deliberately rather than copied blindly.

---

## 56. Modules: Local vs Registry

Modules can come from:

```text
local directory
Git repository
Terraform Registry
```

Example:

```hcl
module "vpc" {
  source = "./modules/vpc"
}
```

or:

```hcl
module "vpc" {
  source = "..."
}
```

For production teams, internal modules can standardize company infrastructure.

---

## 57. Internal Terraform Modules

Imagine your company wants every service to use:

```text
standard VPC
standard logging
standard IAM
standard encryption
```

Create:

```text
company-network-module
company-eks-module
company-service-module
```

Then teams consume them.

This creates:

```text
Platform Team
      ↓
Reusable Modules
      ↓
Engineering Teams
```

This is a major platform-engineering use case.

---

## 58. Module Versioning

Don't blindly point production at a constantly changing module.

Prefer versioning:

```text
v1.0
v1.1
v2.0
```

Then:

```text
production
→ module v1.2
```

while staging tests:

```text
module v1.3
```

This allows controlled promotion.

---

## 59. Terraform + Kubernetes

This is important for your stack.

Terraform can create:

```text
VPC
EKS
RDS
S3
IAM
```

Then Kubernetes manages:

```text
Deployments
Services
Pods
ConfigMaps
```

So:

```text
Terraform
→ infrastructure

Kubernetes
→ application orchestration
```

---

## 60. Terraform + Helm

Terraform can also manage Helm releases.

Conceptually:

```text
Terraform
   ↓
Helm provider
   ↓
Helm release
   ↓
Kubernetes
```

For example:

```hcl
resource "helm_release" "app" {
  name       = "backend"
  repository = "..."
  chart      = "backend"
}
```

But be careful with ownership boundaries.

---

## 61. Terraform + ArgoCD

A common production split:

```text
Terraform
   ↓
EKS infrastructure
```

and:

```text
ArgoCD
   ↓
Application deployments
```

This is often cleaner than having Terraform continuously manage every application manifest.

Think:

```text
Terraform
→ platform/infrastructure

ArgoCD
→ application delivery
```

---

## 62. Terraform + Helm + ArgoCD

Your complete architecture:

```text
Terraform
 │
 ├── VPC
 ├── EKS
 ├── IAM
 ├── RDS
 └── supporting infrastructure
          │
          ▼
         EKS
          │
        ArgoCD
          │
        Helm
          │
       Workloads
```

This is an excellent production mental model.

---

## 63. Terraform vs Ansible

You've already learned Ansible.

Remember:

#### Terraform

```text
Provision infrastructure
```

Example:

```text
VPC
EC2
RDS
EKS
S3
```

#### Ansible

```text
Configure/manage machines
```

Example:

```text
install nginx
configure server
manage service
```

---

## 64. Terraform vs Kubernetes

#### Terraform

```text
AWS infrastructure
```

#### Kubernetes

```text
container workloads
```

Example:

```text
Terraform
→ create EKS

Kubernetes
→ create Deployment
```

---

## 65. Terraform vs Helm

#### Terraform

```text
Infrastructure provisioning
```

#### Helm

```text
Kubernetes application packaging
```

---

## 66. Terraform vs ArgoCD

#### Terraform

```text
Infrastructure lifecycle
```

#### ArgoCD

```text
Kubernetes application GitOps
```

These tools can coexist.

---

## 67. Terraform State Separation

One advanced design principle:

Don't put everything into one giant state.

Bad:

```text
terraform.tfstate
 ├── VPC
 ├── EKS
 ├── RDS
 ├── S3
 ├── 100 applications
 └── every environment
```

This creates a huge blast radius.

Better:

```text
network state
EKS state
database state
environment state
```

depending on organizational needs.

---

## 68. Why Smaller States?

Benefits:

```text
smaller plans
faster operations
smaller blast radius
better ownership
less contention
easier troubleshooting
```

But don't split so aggressively that dependencies become impossible to manage.

It's a balance.

---

## 69. Cross-State References

Suppose:

```text
Network state
```

creates:

```text
VPC ID
```

and:

```text
EKS state
```

needs it.

Terraform supports mechanisms such as remote-state data access.

Conceptually:

```text
Network state
     ↓
VPC ID
     ↓
EKS state
```

However, excessive cross-state coupling can become difficult to maintain.

Prefer clear boundaries.

---

## 70. Terraform Refresh / Reconciliation

Terraform needs to compare:

```text
Configuration
+
State
+
Actual infrastructure
```

to determine changes.

Conceptually:

```text
config ───────┐
              ├── Terraform ──→ plan
state ────────┤
              │
actual ───────┘
```

This is why drift can be detected.

---

## 71. `terraform refresh` — Important Nuance

Older tutorials often teach:

```bash
terraform refresh
```

as a standalone command.

Modern Terraform workflows generally incorporate refreshing state information into normal planning/apply behavior, and you should follow the version's current recommended workflow.

The important concept is:

> Terraform needs current information about real infrastructure before producing an accurate plan.

---

## 72. Sensitive State

Even if:

```hcl
sensitive = true
```

hides a value from CLI output, the value may still exist in state.

Therefore:

```text
Sensitive variable
≠
secret automatically secured
```

Protect the backend itself.

---

## 73. State Access Control

Only authorized people/workloads should access:

```text
Terraform state bucket
```

For example:

```text
Developer
   ↓
limited IAM

CI/CD
   ↓
Terraform role

S3 state
   ↓
restricted access
```

Don't give every developer unrestricted production state access.

---

## 74. Terraform Disaster Recovery

Suppose:

```text
Terraform state deleted
```

Your infrastructure may still exist.

But Terraform loses its mapping.

Therefore:

```text
state backup/versioning
+
controlled access
```

is important.

If necessary, recovery/import workflows can reconstruct management.

But recovery is much easier when state is properly backed up.

---

## 75. Terraform Plan as a Safety Mechanism

Imagine someone changes:

```hcl
instance_type = "t3.large"
```

to:

```hcl
instance_type = "t3.nano"
```

and Terraform says:

```text
~ change
```

The plan lets you catch mistakes before apply.

For destructive changes:

```text
- destroy
```

you should stop and investigate.

---

## 76. Production Guardrails

Useful guardrails include:

```text
code review
plan review
protected branches
CI checks
policy-as-code
approval gates
least privilege
separate production credentials
```

Some organizations also use policy tools such as:

```text
OPA
Sentinel
```

to prevent dangerous infrastructure changes.

You only need awareness of these for your target.

---

## 77. Terraform Policy Example

Imagine a policy:

> "Production S3 buckets must not be publicly accessible."

Then:

```text
Terraform Plan
       ↓
Policy check
       ↓
❌ reject
```

This prevents bad infrastructure before deployment.

This is an example of:

> **Policy as Code**

---

## 78. Terraform Security Scanning

You may encounter tools that inspect Terraform configuration for issues such as:

```text
public S3
overly broad IAM
unencrypted resources
open security groups
```

The exact tool isn't the important part for your SWE interview.

The concept is:

```text
IaC
 ↓
static/security analysis
 ↓
prevent insecure infrastructure
```

---

## 79. Terraform Testing

Infrastructure code should also be tested.

At basic level:

```bash
terraform fmt
terraform validate
terraform plan
```

More advanced:

```text
module tests
integration tests
policy tests
```

You don't need to become a Terraform testing specialist, but understand:

> Infrastructure is code and should be reviewed/tested like code.

---

## 80. Terraform Deployment Strategy

A production deployment might be:

```text
Developer
    ↓
PR
    ↓
Terraform fmt
    ↓
Validate
    ↓
Security scan
    ↓
Plan
    ↓
Review
    ↓
Merge
    ↓
Production approval
    ↓
Apply
```

This is the mature workflow.

---

## 81. Real-World Scenario

#### Situation

You have:

```text
Production EKS
RDS
VPC
S3
```

Someone manually changes the RDS instance class.

Terraform detects:

```text
Configuration:
db.t3.medium

Actual:
db.r6g.large
```

What do you do?

Don't immediately apply.

First ask:

> Was the manual change intentional?

If intentional:

```text
Update Terraform configuration
```

Then:

```bash
terraform plan
```

If accidental:

```text
Determine whether Terraform should restore intended state
```

This is infrastructure change management.

---

## 82. Another Scenario

#### Developer says:

> "Terraform wants to destroy our production database!"

Your response should be:

```text
STOP APPLY
```

Then:

```text
terraform plan
```

inspect:

```text
why replacement?
```

Potential causes:

```text
immutable field changed
resource address changed
module refactor
provider behavior
configuration mismatch
import/state issue
```

Never blindly approve a destructive plan.

---

## 83. Resource Address Changes

Suppose you move:

```hcl
resource "aws_s3_bucket" "assets"
```

into:

```hcl
module "storage" {
   ...
}
```

Terraform may think:

```text
old resource removed
new resource created
```

even though it's logically the same infrastructure.

Modern Terraform supports mechanisms such as `moved` blocks to tell Terraform:

> This resource changed its address; it isn't a new real-world resource.

Conceptually:

```text
old address
    ↓
moved
    ↓
new address
```

This is an important production refactoring technique.

---

## 84. Example `moved`

Conceptually:

```hcl
moved {
  from = aws_s3_bucket.assets
  to   = module.storage.aws_s3_bucket.assets
}
```

Now Terraform can preserve resource identity across the refactor.

This can prevent unnecessary destroy/create operations.

---

## 85. `for_each` vs `count`

Another useful Terraform concept.

#### `count`

Good for simple numeric repetition.

```hcl
count = 3
```

Resources get numeric indexes.

```text
resource[0]
resource[1]
resource[2]
```

#### `for_each`

Better when resources have meaningful identities.

```hcl
for_each = {
  api  = "..."
  worker = "..."
}
```

Then:

```text
resource["api"]
resource["worker"]
```

For infrastructure, `for_each` is often easier to manage when items have stable names.

---

## 86. Why `for_each` Can Be Safer

Suppose:

```text
count = 3
```

and you remove the second item.

Indexes can shift.

With:

```text
for_each
```

keys can remain stable:

```text
api
worker
scheduler
```

Terraform can more accurately identify which logical resource changed.

---

## 87. Locals

Locals let you avoid repeating expressions.

Example:

```hcl
locals {
  name_prefix = "${var.project}-${var.environment}"
}
```

Then:

```hcl
name = "${local.name_prefix}-api"
```

Useful for consistent naming.

---

## 88. Naming Conventions

Production Terraform should use predictable names.

For example:

```text
project-environment-component
```

Such as:

```text
payments-prod-eks
payments-prod-rds
payments-prod-assets
```

This helps:

```text
operations
billing
debugging
security
```

---

## 89. Tags

AWS resources should generally receive useful tags such as:

```text
Project
Environment
Owner
ManagedBy
CostCenter
```

Example:

```hcl
tags = {
  Project     = "payments"
  Environment = "production"
  ManagedBy   = "terraform"
}
```

Tags help with:

```text
cost allocation
search
operations
governance
```

---

## 90. Terraform + EKS Best Practice Boundary

For your architecture:

#### Terraform

Create:

```text
VPC
EKS
Node groups
IAM
RDS
S3
Load balancer infrastructure
```

#### ArgoCD

Deploy:

```text
Deployment
Service
ConfigMap
application Helm chart
```

#### Kubernetes

Operate:

```text
Pods
ReplicaSets
Services
HPA
Jobs
```

This avoids multiple tools fighting over the same resources.

---

## 91. The "Two Tools Manage One Resource" Problem

Suppose:

```text
Terraform
```

manages:

```text
Kubernetes Deployment
```

while:

```text
ArgoCD
```

also manages:

```text
same Deployment
```

Now:

```text
Terraform
→ desired state A

ArgoCD
→ desired state B
```

They can fight.

This is called an **ownership conflict**.

Therefore:

> Define clear ownership boundaries.

---

## 92. A Clean Production Ownership Model

```text
Terraform
│
├── AWS networking
├── EKS
├── IAM
├── RDS
├── S3
└── supporting infrastructure

ArgoCD
│
├── Deployments
├── Services
├── ConfigMaps
├── Helm releases
└── application configuration

Kubernetes
│
└── runtime reconciliation
```

This is the architecture I want you to remember.

---

## 93. Advanced Terraform Mental Model

Think of Terraform as:

```text
              Terraform
                  │
       ┌──────────┼──────────┐
       ↓          ↓          ↓
   Config       State     Provider
       │          │          │
       └──────────┼──────────┘
                  ↓
              Plan
                  ↓
             Review
                  ↓
               Apply
                  ↓
             AWS APIs
                  ↓
          Actual Infrastructure
```

Then:

```text
Modules
→ reuse

Remote State
→ collaboration

Locking
→ concurrency safety

CI/CD
→ controlled changes

Policy
→ guardrails

Drift detection
→ consistency

Imports/moved blocks
→ lifecycle/refactoring
```

---

## 94. Terraform Interview Questions

#### Q1. Why does Terraform need state?

> State maps Terraform resources to real infrastructure and stores information Terraform needs to calculate changes and manage resource lifecycle.

---

#### Q2. Why remote state?

> To provide a shared, centralized state representation for team collaboration and CI/CD.

---

#### Q3. Why state locking?

> To prevent concurrent Terraform operations from corrupting or conflicting over the same state.

---

#### Q4. What is drift?

> Drift occurs when actual infrastructure differs from the configuration Terraform expects, often because of manual or external changes.

---

#### Q5. What is a module?

> A reusable package of Terraform configuration that abstracts and standardizes infrastructure creation.

---

#### Q6. `resource` vs `data`?

```text
resource
→ create/manage

data
→ read existing information
```

---

#### Q7. Terraform vs Ansible?

```text
Terraform
→ provision infrastructure

Ansible
→ configure/manage machines
```

---

#### Q8. Terraform vs Kubernetes?

```text
Terraform
→ infrastructure

Kubernetes
→ container orchestration
```

---

#### Q9. Why shouldn't Terraform and ArgoCD manage the same resource?

> They can have conflicting sources of truth and continuously overwrite each other's desired state.

---

#### Q10. How would you protect production Terraform?

```text
remote state
state locking
IAM
PR review
plan review
approval
CI/CD
policy checks
separate environments
least privilege
```

---

#### Q11. What would you do if Terraform wants to destroy production RDS?

> Stop the apply, inspect the plan and resource lifecycle/address changes, determine why Terraform wants replacement, and only proceed after confirming the change is intentional and safe.

---

#### Q12. Why use `moved` blocks?

> To tell Terraform that a resource changed its Terraform address without representing a real infrastructure replacement.

---

## 95. What You Should Be Able to Do Now

You should be comfortable designing:

```text
terraform/
│
├── modules/
│   ├── network/
│   ├── eks/
│   ├── rds/
│   └── iam/
│
└── environments/
    ├── dev/
    ├── staging/
    └── prod/
```

with:

```text
Remote S3 State
       ↓
State locking
       ↓
Terraform modules
       ↓
AWS infrastructure
```

and:

```text
GitHub
   ↓
PR
   ↓
Terraform plan
   ↓
review
   ↓
approval
   ↓
Terraform apply
```

Then:

```text
Terraform
     ↓
EKS
     ↓
ArgoCD
     ↓
Helm
     ↓
Applications
```

That's the production-grade workflow.

---

## 96. Final Advanced Terraform Checklist

#### State

```text
✅ State purpose
✅ Local vs remote
✅ S3 backend
✅ Locking
✅ State security
✅ State versioning
✅ State commands
```

#### Modules

```text
✅ Module design
✅ Inputs
✅ Outputs
✅ Reuse
✅ Versioning
✅ Internal modules
✅ Avoid over-modularization
```

#### Environments

```text
✅ Dev/staging/prod
✅ Separate state
✅ Workspaces
✅ Blast radius
```

#### Lifecycle

```text
✅ Drift
✅ Import
✅ moved blocks
✅ lifecycle
✅ prevent_destroy
✅ create_before_destroy
✅ ignore_changes
```

#### Dependencies

```text
✅ Dependency graph
✅ Implicit dependencies
✅ depends_on
✅ for_each
✅ count
```

#### CI/CD

```text
✅ fmt
✅ validate
✅ plan
✅ saved plan
✅ apply
✅ approval
✅ OIDC
```

#### Security

```text
✅ Least privilege
✅ No hardcoded credentials
✅ State protection
✅ Secret management
✅ Policy as code
✅ IaC security scanning
```

#### Tool boundaries

```text
Terraform
→ infrastructure

Helm
→ Kubernetes packaging

ArgoCD
→ Kubernetes GitOps

Kubernetes
→ runtime orchestration
```

---

## 🎯 Chapter 32 Complete

This was intentionally much deeper than [Chapter 21](ch21-terraform.md) because we're now at the **advanced/professional Terraform layer**.

We covered:

- ✅ Production Terraform state
- ✅ Remote state
- ✅ S3 backend
- ✅ State locking
- ✅ State security
- ✅ State versioning
- ✅ Bootstrap problem
- ✅ Import
- ✅ Drift
- ✅ State manipulation
- ✅ Modules
- ✅ Module design
- ✅ Module versioning
- ✅ Environment architecture
- ✅ Separate state
- ✅ Workspaces
- ✅ Blast radius
- ✅ Data sources
- ✅ Dependency graph
- ✅ `depends_on`
- ✅ Lifecycle rules
- ✅ `prevent_destroy`
- ✅ `create_before_destroy`
- ✅ `ignore_changes`
- ✅ `moved` blocks
- ✅ `count`
- ✅ `for_each`
- ✅ Locals
- ✅ Naming/tagging
- ✅ Provider versioning
- ✅ `.terraform.lock.hcl`
- ✅ CI/CD
- ✅ Terraform plans
- ✅ Saved plans
- ✅ OIDC
- ✅ Policy as Code
- ✅ IaC security
- ✅ Terraform testing
- ✅ Terraform + Kubernetes
- ✅ Terraform + Helm
- ✅ Terraform + ArgoCD
- ✅ Terraform + Ansible
- ✅ Ownership boundaries
- ✅ Production troubleshooting scenarios
- ✅ Infrastructure blast radius
- ✅ Production interview questions

#### Depth target

**🔥 Deep:** State, remote state, locking, modules, environments, drift, lifecycle, dependencies, CI/CD, security, Terraform/Kubernetes/ArgoCD boundaries.

**🟡 Medium:** Workspaces, policy-as-code, testing, advanced module publishing, cross-state dependencies.

**⚪ Awareness:** Terraform internals/provider development and highly specialized enterprise tooling.
<!-- SOURCE-END -->

---

## Editorial supplement

> **Added by the knowledge-base editor — not part of the original source.** It fills gaps the source leaves open (for example concepts named in the interview list but never explained, or configuration the chapter only describes in words). Treat the text above as the original material and this section as clearly separated additions.

### Complete Terraform snippets for the fragments in this chapter

The chapter describes several features using partial snippets (`source = "..."`, `for_each = { api = "..." }`, "remote-state data access"). Here are complete, working forms. Check the Terraform and provider documentation for the versions you use.

**1. A complete S3 backend** (sections 9–10) with encryption and native locking (Terraform ≥ 1.10; older setups used a DynamoDB table):

```hcl
terraform {
  required_version = ">= 1.10, < 2.0"        # a real range; the chapter's ">= 1.x" is a placeholder

  backend "s3" {
    bucket       = "company-terraform-state"
    key          = "production/network/terraform.tfstate"   # one key per state
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true                       # S3-native state locking
  }
}
```

**2. `count` vs `for_each`** (sections 85–86). With `count`, items are identified by position, so removing the middle item shifts the others and Terraform plans to destroy and recreate resources. With `for_each` each item has a stable key:

```hcl
variable "services" {
  type = map(string)
  default = {
    api       = "t3.small"
    worker    = "t3.medium"
    scheduler = "t3.small"
  }
}

resource "aws_instance" "svc" {
  for_each      = var.services
  ami           = data.aws_ami.ubuntu.id
  instance_type = each.value
  tags          = { Name = "${local.name_prefix}-${each.key}" }   # addresses: aws_instance.svc["api"], ["worker"], ...
}

# count form (positional): aws_instance.web[0], [1], [2]
resource "aws_instance" "web" {
  count         = 3
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
}
```

**3. `lifecycle` in practice** (sections 43–45):

```hcl
resource "aws_db_instance" "main" {
  # ...
  lifecycle {
    prevent_destroy = true            # any plan that would destroy this errors out
  }
}

resource "aws_autoscaling_group" "app" {
  # ...
  lifecycle {
    create_before_destroy = true
    ignore_changes        = [desired_capacity]   # autoscaling changes this outside Terraform
  }
}
```

Caveat: `prevent_destroy` only protects while the resource block (and its lifecycle setting) stays in the configuration — if you delete the whole block, Terraform no longer sees the protection and will plan the destroy. Review plans for removed resources.

**4. `moved` blocks and imports** (sections 15–17, 83–84):

```hcl
moved {
  from = aws_s3_bucket.assets
  to   = module.storage.aws_s3_bucket.assets
}

import {                                        # Terraform ≥ 1.5
  to = aws_s3_bucket.legacy
  id = "my-existing-bucket"
}
```
`terraform plan -generate-config-out=generated.tf` can draft configuration for resources declared in `import` blocks, which softens (but doesn't remove) the chapter's point that you must still review and own the resulting code. Newer Terraform also has a `removed` block to stop managing a resource without destroying it, the declarative counterpart of `terraform state rm`.

**5. Reading another state's outputs** (section 69):

```hcl
# in the EKS configuration
data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "company-terraform-state"
    key    = "production/network/terraform.tfstate"
    region = "ap-south-1"
  }
}

resource "aws_eks_cluster" "this" {
  # ...
  vpc_config {
    subnet_ids = data.terraform_remote_state.network.outputs.private_subnet_ids
  }
}
```
The network configuration must expose `private_subnet_ids` as an `output`. Reading a remote state requires read access to that state file.

**6. Useful commands the chapter implies.**

| Command | Purpose |
|---|---|
| `terraform apply -refresh-only` | Update state to match real infrastructure without changing resources (the modern replacement for standalone `terraform refresh`, section 71) |
| `terraform state mv <from> <to>` | Rename/move an address in state (CLI alternative to a `moved` block) |
| `terraform apply -replace=<address>` | Force recreation of one resource (replaces the deprecated `taint`) |
| `terraform force-unlock <id>` | Release a stuck lock — only when you are sure no run is active |
| `terraform plan -lock-timeout=5m` | Wait for a lock instead of failing immediately |
| `terraform plan -target=<address>` | Plan one resource — an escape hatch that can leave things inconsistent; not for routine use |
| `terraform output -json`, `terraform console`, `terraform graph` | Inspect outputs, evaluate expressions, view the dependency graph |

**7. Tooling for the "policy / scanning / testing" sections (76–79).** Static analysis and policy: `tflint`, Checkov, Trivy (the successor to tfsec), OPA/Conftest, Sentinel (Terraform Cloud/Enterprise). Native testing: `terraform test` (Terraform ≥ 1.6) with `.tftest.hcl` files; integration tests commonly use Terratest.

---

**Navigation:** ← [Chapter 31: Advanced Amazon EKS](../05-kubernetes/ch31-advanced-eks.md) · [Chapter 33: Advanced AWS for Backend Engineers](../04-aws/ch33-advanced-aws-backend.md) → · [Revision sheet](../../revision/ch32-revision.md)
