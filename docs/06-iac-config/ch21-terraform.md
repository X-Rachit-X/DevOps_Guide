# Chapter 21 — Terraform: Infrastructure as Code

> **Source:** Response 21 of the original conversation (`source-archive/src-21.txt`, lines 1–2076) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch21-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

This is an important transition in the roadmap.

Until now, we've mostly learned:

```text
AWS Console / CLI
        ↓
Create infrastructure
        ↓
EC2 / VPC / S3 / RDS / EKS
```

But imagine you need to recreate your entire infrastructure tomorrow.

You don't want to manually click:

```text
Create VPC
→ Create subnet
→ Create route table
→ Create EC2
→ Create security group
→ Create RDS
→ ...
```

Instead:

```text
Terraform code
      ↓
terraform plan
      ↓
terraform apply
      ↓
Infrastructure
```

That's **Infrastructure as Code (IaC)**.

---

## 1. What Is Terraform?

Terraform is an Infrastructure as Code tool.

You describe the infrastructure you want:

```text
"I want a VPC."
"I want 2 subnets."
"I want an S3 bucket."
"I want an EC2 instance."
```

using configuration files.

Terraform then creates and manages those resources.

The core idea:

> **Infrastructure becomes code that can be version-controlled, reviewed, reproduced, and automated.**

---

## 2. Why Terraform Exists

Without IaC:

```text
Developer
   ↓
AWS Console
   ↓
click click click
   ↓
Infrastructure
```

Problems:

- difficult to reproduce
- easy to make manual mistakes
- difficult to review changes
- difficult to document
- difficult to recreate environments
- configuration can drift

With Terraform:

```text
Git
 ↓
Terraform
 ↓
AWS
```

You can review infrastructure changes just like application code.

---

## 3. Terraform vs Docker vs Kubernetes

This distinction is extremely important.

#### Docker

Packages/runs applications:

```text
Dockerfile
   ↓
Image
   ↓
Container
```

#### Kubernetes

Orchestrates containers:

```text
Kubernetes
   ↓
Pods
   ↓
Containers
```

#### Terraform

Creates/manages infrastructure:

```text
Terraform
   ↓
AWS infrastructure
   ├── VPC
   ├── EC2
   ├── S3
   ├── RDS
   └── EKS
```

So:

```text
Terraform
→ infrastructure

Docker
→ application packaging

Kubernetes
→ container orchestration
```

They complement each other.

---

## 4. Terraform Architecture

The basic flow:

```text
Terraform Configuration
        ↓
Terraform CLI
        ↓
Provider
        ↓
Cloud API
        ↓
Infrastructure
```

For AWS:

```text
Terraform
    ↓
AWS Provider
    ↓
AWS APIs
    ↓
AWS Resources
```

---

## 5. Terraform Configuration

Terraform normally uses:

```text
.tf
```

files.

Example:

```text
main.tf
variables.tf
outputs.tf
```

Terraform uses **HCL** — HashiCorp Configuration Language.

It's declarative.

---

## 6. Your First Terraform Program

Create:

```text
main.tf
```

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

provider "aws" {
  region = "ap-south-1"
}
```

This says:

```text
Use AWS provider
Region = Mumbai
```

The exact provider version should be chosen intentionally for your project rather than blindly copying an old tutorial.

---

## 7. Install Terraform

After installing Terraform:

```bash
terraform version
```

You should get something like:

```text
Terraform vX.Y.Z
```

Then create:

```text
terraform/
└── main.tf
```

---

## 8. Terraform Init

Run:

```bash
terraform init
```

What happens?

Terraform:

- initializes the project
- downloads required providers
- prepares the working directory

You should see something similar to:

```text
Terraform has been successfully initialized!
```

This is usually the **first Terraform command** you run in a new project.

---

## 9. Terraform Validate

Run:

```bash
terraform validate
```

This checks whether your Terraform configuration is syntactically and structurally valid.

---

## 10. Terraform Plan

Run:

```bash
terraform plan
```

This is extremely important.

Terraform asks:

> What changes would happen if I applied this configuration?

Conceptually:

```text
Current infrastructure
        +
Terraform configuration
        ↓
Terraform plan
        ↓
Proposed changes
```

Example:

```text
+ create aws_s3_bucket.app
```

`+` generally means create.

You may also encounter:

```text
~ update
- destroy
-/+ replace
```

---

## 11. Terraform Apply

Then:

```bash
terraform apply
```

Terraform shows the proposed changes and normally asks for confirmation.

You can approve:

```text
yes
```

Terraform then calls the provider APIs.

For AWS:

```text
Terraform
   ↓
AWS Provider
   ↓
AWS API
   ↓
S3/VPC/EC2/etc.
```

---

## 12. Terraform Destroy

You can remove resources managed by Terraform:

```bash
terraform destroy
```

This is powerful.

**Be extremely careful with it in real environments.**

For learning infrastructure:

```text
terraform apply
    ↓
build
    ↓
test
    ↓
terraform destroy
```

is a great workflow.

---

## PART 2 — RESOURCES

## 13. Terraform Resource

A resource represents something Terraform manages.

Example S3 bucket:

```hcl
resource "aws_s3_bucket" "app" {
  bucket = "my-unique-learning-bucket"
}
```

Structure:

```text
resource
   ↓
provider resource type
   ↓
local name
   ↓
configuration
```

Here:

```text
aws_s3_bucket
```

is the resource type.

```text
app
```

is Terraform's local name.

---

## 14. Resource Reference

Suppose:

```hcl
resource "aws_s3_bucket" "app" {
  bucket = "my-unique-learning-bucket"
}
```

Terraform refers to it as:

```text
aws_s3_bucket.app
```

Other resources can reference it.

Example:

```hcl
some_resource {
  bucket = aws_s3_bucket.app.id
}
```

This creates a dependency.

Terraform can determine the order in which resources need to be created.

---

## 15. Create an S3 Bucket

A minimal learning example:

```hcl
resource "aws_s3_bucket" "app" {
  bucket = "rachit-terraform-learning-example"
}
```

Then:

```bash
terraform init
terraform validate
terraform plan
terraform apply
```

Check AWS.

The bucket should exist.

---

## 16. Terraform State

Now we reach one of the **most important Terraform concepts**.

After:

```bash
terraform apply
```

Terraform creates:

```text
terraform.tfstate
```

This is the Terraform **state**.

Conceptually:

```text
Terraform code
      ↓
State
      ↓
Real infrastructure
```

State helps Terraform understand:

> "What infrastructure do I currently manage?"

---

## 17. Why State Exists

Suppose Terraform knows:

```text
S3 bucket
ID = X
```

Your configuration says:

```text
S3 bucket should exist
```

Terraform can compare:

```text
Desired state
      vs
Known state / real infrastructure
```

and determine what needs to change.

---

## 18. Never Treat State as Disposable Metadata

This is important.

`terraform.tfstate` may contain sensitive information depending on the resources/configuration.

Therefore:

```text
❌ Don't casually commit terraform.tfstate to Git.
```

Add:

```gitignore
.terraform/
*.tfstate
*.tfstate.*
```

to `.gitignore`.

---

## 19. `.terraform.lock.hcl`

Terraform also creates:

```text
.terraform.lock.hcl
```

Unlike state, this file is generally useful to commit.

It helps lock provider selections/checksums so different environments use consistent provider packages.

So:

```text
.terraform/       → don't commit
terraform.tfstate → don't commit
.terraform.lock.hcl → generally commit
```

---

## PART 3 — VARIABLES

## 20. Hardcoding Is Bad

Instead of:

```hcl
provider "aws" {
  region = "ap-south-1"
}
```

you might want configurable values.

Create:

```text
variables.tf
```

```hcl
variable "aws_region" {
  type    = string
  default = "ap-south-1"
}
```

Then:

```hcl
provider "aws" {
  region = var.aws_region
}
```

Now:

```text
var.aws_region
```

references the variable.

---

## 21. Variable Values

You can override variables using:

```text
terraform.tfvars
```

Example:

```hcl
aws_region = "ap-south-1"
```

Or:

```bash
terraform apply -var="aws_region=ap-south-1"
```

Don't put sensitive secrets into files that you'll commit.

---

## 22. Variable Types

Terraform supports types such as:

```hcl
string
number
bool
list
set
map
object
```

Example:

```hcl
variable "instance_count" {
  type    = number
  default = 2
}
```

---

## PART 4 — OUTPUTS

## 23. Outputs

Suppose Terraform creates an EC2 instance.

You may want:

```text
Public IP
DNS name
Resource ID
```

Use outputs.

```hcl
output "bucket_name" {
  value = aws_s3_bucket.app.bucket
}
```

Then:

```bash
terraform apply
```

Terraform can show:

```text
bucket_name = "rachit-terraform-learning-example"
```

You can also retrieve it:

```bash
terraform output
```

---

## 24. Input vs Output

Simple mental model:

```text
Variables
   ↓
Terraform
   ↓
Infrastructure
   ↓
Outputs
```

Example:

```text
Input:
region

Output:
EC2 public IP
```

---

## PART 5 — DATA SOURCES

Terraform can also read information that already exists.

For example:

```text
Existing AWS VPC
Existing AMI
Existing subnet
```

Terraform can use **data sources** to query provider information without necessarily creating the object.

Conceptually:

```text
data
 ↓
read existing information
```

versus:

```text
resource
 ↓
manage/create infrastructure
```

This distinction is useful in larger Terraform projects.

---

## PART 6 — DEPENDENCIES

Suppose:

```text
EC2
 ↓
needs
 ↓
Security Group
```

Terraform can understand explicit/implicit dependencies.

Example:

```hcl
resource "aws_instance" "app" {
  ami           = "..."
  instance_type = "t3.micro"

  security_groups = [
    aws_security_group.app.name
  ]
}
```

Terraform sees:

```text
Security Group
      ↓
EC2
```

and creates them in the appropriate order.

---

## 25. `depends_on`

Sometimes Terraform can't infer a dependency.

Then:

```hcl
depends_on = [
  aws_some_resource.example
]
```

can explicitly express it.

Don't use `depends_on` everywhere.

Prefer natural references when Terraform can infer dependencies.

---

## PART 7 — FORMATTING

Terraform provides:

```bash
terraform fmt
```

This formats your Terraform files.

Typical workflow:

```bash
terraform fmt
terraform validate
terraform plan
```

Very similar to normal software development tooling.

---

## PART 8 — LOCALS

Terraform supports local values:

```hcl
locals {
  environment = "dev"
  project     = "my-api"
}
```

Then:

```hcl
tags = {
  Project     = local.project
  Environment = local.environment
}
```

Useful for avoiding repetition.

---

## PART 9 — MODULES

Now imagine your Terraform project grows:

```text
VPC
EC2
RDS
EKS
S3
IAM
CloudFront
```

Putting everything into one giant `main.tf` becomes messy.

Terraform provides:

> **Modules**

Think:

```text
root module
│
├── vpc module
├── ec2 module
├── rds module
└── eks module
```

---

## 26. Example Module Structure

```text
terraform/
│
├── main.tf
├── variables.tf
├── outputs.tf
│
└── modules/
    ├── network/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    │
    └── app/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

This is similar to modular programming.

---

## 27. Module Usage

Root:

```hcl
module "network" {
  source = "./modules/network"

  environment = "dev"
}
```

Now:

```text
Root Terraform
      ↓
Network module
      ↓
VPC/Subnets/etc.
```

Modules become extremely important when infrastructure gets larger.

---

## PART 10 — ENVIRONMENTS

You might have:

```text
development
staging
production
```

You don't want:

```text
dev → production infrastructure accidentally
```

A common approach is to maintain separate state/configuration for environments.

Possible structures include:

```text
environments/
├── dev/
├── staging/
└── prod/
```

or reusable modules with separate environment configurations.

The exact structure depends on team conventions.

---

## 28. Terraform Workspaces

Terraform also has:

```text
terraform workspace
```

which can maintain separate state instances.

You should know it exists.

But don't think:

> "Workspaces are automatically the best way to manage every production environment."

Large teams often use separate root configurations/state backends for stronger isolation.

---

## PART 11 — STATE DRIFT

Imagine Terraform says:

```text
EC2 type = t3.micro
```

But someone manually changes AWS:

```text
EC2 type = t3.medium
```

Now:

```text
Terraform configuration
        ≠
Real infrastructure
```

That's **drift**.

Running:

```bash
terraform plan
```

can reveal changes Terraform believes are needed to reconcile infrastructure with the configuration.

This is one of the biggest reasons IaC is useful.

---

## 29. The Terraform Principle

```text
Git
 ↓
Terraform code
 ↓
Plan
 ↓
Review
 ↓
Apply
 ↓
Infrastructure
```

Instead of:

```text
Someone manually changed production at 2 AM
```

---

## PART 12 — REMOTE STATE

Local state:

```text
Developer laptop
└── terraform.tfstate
```

works for learning.

But a team needs shared state.

You don't want:

```text
Developer A → state on laptop A
Developer B → state on laptop B
```

Instead:

```text
                 Terraform State
                       │
                       ↓
                  Remote Backend
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
       Developer A         Developer B
```

On AWS, a common pattern uses an S3-backed Terraform state backend.

Current Terraform/AWS capabilities also support native S3 state locking; older tutorials often show a separate DynamoDB locking table, so don't blindly copy that older pattern.

---

## 30. Why State Locking?

Imagine:

```text
Developer A
terraform apply
```

at the same time as:

```text
Developer B
terraform apply
```

Both modifying state simultaneously can cause problems.

State locking helps prevent conflicting operations.

Mental model:

```text
Terraform Apply
      ↓
Acquire lock
      ↓
Modify state
      ↓
Release lock
```

---

## PART 13 — AWS CREDENTIALS

This connects directly to [Chapter 9](../04-aws/ch09-aws-fundamentals-iam.md).

Don't put:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

inside:

```text
main.tf ❌
Git ❌
Dockerfile ❌
terraform.tfvars committed to Git ❌
```

Terraform's AWS provider can use standard AWS credential mechanisms.

For local development you can use:

```bash
aws configure
```

or appropriate AWS credential/environment mechanisms.

For CI/CD, prefer:

```text
GitHub Actions
      ↓
OIDC
      ↓
AWS IAM Role
      ↓
Temporary credentials
      ↓
Terraform
```

This is exactly the security model we learned earlier.

---

## PART 14 — TERRAFORM + GITHUB ACTIONS

Now we're getting into **real DevOps**.

Your infrastructure can be managed through CI/CD.

Example pipeline:

```text
Git push
   ↓
GitHub Actions
   ↓
terraform fmt
   ↓
terraform validate
   ↓
terraform plan
   ↓
Review/approval
   ↓
terraform apply
```

---

## 31. Basic GitHub Actions Workflow

Example:

```yaml
name: Terraform

on:
  pull_request:
  push:
    branches:
      - main

jobs:
  terraform:
    runs-on: ubuntu-latest

    permissions:
      id-token: write
      contents: read

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3

      - name: Terraform Init
        run: terraform init

      - name: Terraform Format
        run: terraform fmt -check

      - name: Terraform Validate
        run: terraform validate

      - name: Terraform Plan
        run: terraform plan
```

The important thing isn't memorizing this YAML.

Understand the workflow:

```text
Code
 ↓
CI
 ↓
Validate
 ↓
Plan
 ↓
Review
 ↓
Apply
```

---

## 32. Should Every PR Automatically Run `terraform apply`?

Not necessarily.

A safer common pattern is:

```text
Pull Request
    ↓
fmt
validate
plan
    ↓
review
    ↓
merge
    ↓
controlled apply
```

For production, teams often add:

```text
approval
permissions
environment protection
```

before applying changes.

---

## PART 15 — REAL TERRAFORM PROJECT

Now let's build something closer to your actual stack.

Goal:

```text
AWS
│
├── VPC
│   ├── Public Subnet
│   └── Private Subnet
│
├── Security Groups
│
├── EC2
│
├── S3
│
└── RDS
```

Later this can become:

```text
VPC
 ↓
EKS
 ↓
Pods
 ↓
RDS
 ↓
S3
```

---

## 33. Project Structure

Start:

```text
infra/
│
├── main.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars
├── .gitignore
│
└── modules/
    ├── network/
    ├── compute/
    └── database/
```

Don't try to create the entire production architecture on your first Terraform run.

Start small.

---

## 34. Recommended Learning Order

#### Phase 1

Create:

```text
S3
```

Learn:

```text
provider
resource
init
plan
apply
destroy
state
```

#### Phase 2

Create:

```text
VPC
Subnet
Route Table
Internet Gateway
Security Group
```

Learn AWS networking through Terraform.

#### Phase 3

Create:

```text
EC2
```

Learn:

```text
dependencies
outputs
variables
```

#### Phase 4

Add:

```text
RDS
```

Learn:

```text
network dependencies
security groups
private infrastructure
```

#### Phase 5

Convert into:

```text
modules
```

#### Phase 6

Add:

```text
remote state
CI/CD
OIDC
```

That's a much better learning progression than copying a 500-line Terraform project.

---

## PART 16 — TERRAFORM COMMANDS YOU SHOULD KNOW

These are worth memorizing:

```bash
terraform init
```

Initialize project.

```bash
terraform fmt
```

Format code.

```bash
terraform validate
```

Validate configuration.

```bash
terraform plan
```

Preview changes.

```bash
terraform apply
```

Apply changes.

```bash
terraform destroy
```

Destroy managed infrastructure.

```bash
terraform show
```

Inspect state/current configuration details.

```bash
terraform output
```

Show outputs.

```bash
terraform state list
```

List resources tracked in state.

```bash
terraform state show <resource>
```

Inspect a particular state entry.

```bash
terraform import
```

Bring an existing resource under Terraform management.

---

## 35. Terraform Import

Suppose someone manually created:

```text
S3 bucket
```

and you want Terraform to manage it.

You can use:

```bash
terraform import ...
```

Conceptually:

```text
Existing AWS resource
       ↓
terraform import
       ↓
Terraform state
```

But import alone doesn't magically create a perfect configuration file for every resource.

You still need to ensure the Terraform configuration correctly represents the desired resource.

---

## PART 17 — COMMON TERRAFORM MISTAKES

### Mistake 1 — Hardcoding secrets

```hcl
password = "mypassword"
```

❌

Use appropriate secret-management mechanisms.

---

### Mistake 2 — Committing state

```text
terraform.tfstate
```

❌

It may contain sensitive information.

---

### Mistake 3 — Running apply blindly

Always understand:

```bash
terraform plan
```

before applying important changes.

---

### Mistake 4 — Manual AWS changes

If Terraform owns a resource and someone constantly changes it manually:

```text
Terraform
   ↕
AWS
```

you create drift.

---

### Mistake 5 — Giant Terraform file

Avoid:

```text
main.tf
5000 lines
```

Use:

```text
modules
variables
outputs
environment structure
```

where appropriate.

---

## PART 18 — TERRAFORM + YOUR ENTIRE DEVOPS STACK

Now look at what you've learned.

```text
                  GitHub
                     │
                     ↓
               GitHub Actions
                /          \
               /            \
              ↓              ↓
       Application CI    Terraform CI
              │              │
              ↓              ↓
           Docker         AWS APIs
              │              │
              ↓              ↓
             ECR         Infrastructure
              │          ┌────┴─────┐
              │          ↓          ↓
              │         VPC        EKS
              │                     │
              │                   Pods
              │                     │
              └─────────────────────┘
                                     
                                     ↓
                                    RDS
                                     +
                                    S3
                                     +
                                   Redis
```

This is the **real DevOps picture**.

---

## PART 19 — WHAT TERRAFORM DOES NOT DO

This distinction is very important.

Terraform is not:

```text
❌ Docker
❌ Kubernetes
❌ CI/CD
❌ application runtime
❌ monitoring system
```

Instead:

```text
Terraform
→ creates/manages infrastructure
```

For example:

```text
Terraform → creates EKS
Kubernetes → manages Pods in EKS
Docker → builds container images
GitHub Actions → runs CI/CD
CloudWatch/Prometheus → monitors
```

---

## 36. Terraform vs Ansible

You may hear:

> "Why Terraform when we have Ansible?"

Simplified distinction:

#### Terraform

Infrastructure provisioning:

```text
VPC
EC2
RDS
EKS
S3
```

#### Ansible

Configuration/automation on machines:

```text
install package
configure service
copy configuration
run commands
```

There can be overlap, and modern immutable/containerized environments reduce the need for traditional server configuration management.

For your roadmap:

```text
Terraform → deep
Ansible → awareness/basic
```

That's intentional.

---

## PART 20 — TERRAFORM VS CLOUDFORMATION

AWS also has:

> CloudFormation

Both are Infrastructure as Code approaches.

Terraform:

```text
multi-cloud / broad provider ecosystem
```

CloudFormation:

```text
AWS-native
```

For your SWE interviews, understand the distinction.

You don't need to deeply learn both.

---

## PART 21 — YOUR PRACTICAL TERRAFORM LAB

I want you to actually do this.

### Step 1

Create:

```text
terraform-learning/
└── main.tf
```

### Step 2

Configure AWS provider.

### Step 3

Create a learning S3 bucket.

### Step 4

Run:

```bash
terraform init
```

### Step 5

Run:

```bash
terraform fmt
terraform validate
```

### Step 6

Run:

```bash
terraform plan
```

Read the output.

Don't blindly press enter.

### Step 7

Run:

```bash
terraform apply
```

### Step 8

Check AWS.

### Step 9

Run:

```bash
terraform state list
```

### Step 10

Run:

```bash
terraform output
```

### Step 11

Change the Terraform configuration.

For example, change tags.

Then:

```bash
terraform plan
```

Observe what Terraform wants to modify.

### Step 12

Destroy the learning resource:

```bash
terraform destroy
```

Now you've actually used Terraform.

---

## 🧠 The Terraform Mental Model

If an interviewer asks:

> "How does Terraform work?"

You can explain:

```text
Terraform Configuration
        ↓
terraform init
        ↓
Provider
        ↓
terraform plan
        ↓
Compare desired state
with tracked/real infrastructure
        ↓
terraform apply
        ↓
Cloud APIs
        ↓
Infrastructure
        ↓
State updated
```

---

## 37. The Most Important Terraform Concepts

#### 🔥 Must Know Deeply

```text
IaC
HCL
Provider
Resource
Variables
Outputs
Dependencies
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
terraform destroy
State
State drift
Modules
Remote state
State locking
Secrets
CI/CD integration
```

#### Medium

```text
Data sources
Locals
Workspaces
Import
Lifecycle rules
Dynamic blocks
for_each
count
```

#### Awareness

```text
Terraform Cloud
Terragrunt
Ansible
CloudFormation
Pulumi
```

Don't expand this response into a second DevOps course. The goal is to make you capable with Terraform and interview-ready.

---

## 🔥 The DevOps Stack Is Coming Together

At this point:

```text
                     DEVELOPMENT
                          │
                          ↓
                         Git
                          │
                          ↓
                       GitHub
                          │
                ┌─────────┴─────────┐
                ↓                   ↓
          GitHub Actions        Terraform
                │                   │
          ┌─────┴─────┐             ↓
          ↓           ↓          AWS Infra
       Testing      Docker           │
                      │              │
                      ↓              ↓
                     ECR            EKS
                      │              │
                      └──────→ Kubernetes
                                     │
                                ┌────┴────┐
                                ↓         ↓
                               Pods     Services
                                │
                         ┌──────┴──────┐
                         ↓             ↓
                        RDS           Redis
                         │
                        Data
```

Then:

```text
Observability
      ↓
Metrics
Logs
Traces
Alerts
      ↓
Production reliability
```

That's exactly where Responses **22–23** are going.
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 20: Kubernetes Networking + Scaling + Production](../05-kubernetes/ch20-kubernetes-networking-scaling.md) · [Chapter 22: Observability + Reliability](../07-observability-sre/ch22-observability-reliability.md) → · [Revision sheet](../../revision/ch21-revision.md)
