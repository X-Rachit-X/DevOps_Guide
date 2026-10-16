# Chapter 21 — Revision Sheet: Terraform — Infrastructure as Code

> Supplements [the full chapter](../docs/06-iac-config/ch21-terraform.md). Shift: from "I know how to configure AWS/Kubernetes" to "I can **create and manage** the infrastructure using code."

## Why IaC / Terraform

Without IaC: Console clicking → hard to reproduce, manual mistakes, hard to review/document/recreate environments, configuration **drift**. With Terraform: **Git → Terraform → AWS**; infra becomes code that is **version-controlled, reviewed, reproduced, automated**.

| Tool | Role |
|---|---|
| **Terraform** | Creates/manages infrastructure (VPC, EC2, S3, RDS, EKS) |
| **Docker** | Packages applications (Dockerfile → image → container) |
| **Kubernetes** | Orchestrates containers (Pods) |
| GitHub Actions | CI/CD |
| CloudWatch/Prometheus | Monitoring |
| **Ansible** | Configuration/automation on machines (install package, configure service, copy config) — awareness/basic; immutable/containerised environments reduce its need |
| **CloudFormation** | AWS-native IaC; Terraform = multi-cloud/broad provider ecosystem |

Architecture: **Terraform configuration → Terraform CLI → Provider → Cloud API → Infrastructure** (AWS: Terraform → AWS Provider → AWS APIs → AWS resources). Files: `.tf` (`main.tf`, `variables.tf`, `outputs.tf`) in **HCL** (HashiCorp Configuration Language), **declarative**.

## First program and core commands

```hcl
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 6.0" }
  }
}
provider "aws" { region = "ap-south-1" }
resource "aws_s3_bucket" "app" { bucket = "my-unique-learning-bucket" }
```
(Choose the provider version intentionally, not from an old tutorial.)

| Command | Purpose |
|---|---|
| `terraform version` | Check install |
| `terraform init` | First command in a project: initialise, download providers, prepare directory |
| `terraform fmt` | Format code |
| `terraform validate` | Syntax/structure check |
| `terraform plan` | Preview: current infra + config → proposed changes. `+` create, `~` update in place, `-` destroy, `-/+` replace |
| `terraform apply` | Show changes, ask `yes`, call provider APIs |
| `terraform destroy` | Remove managed resources — **extreme care in real environments** (great for learning: apply → build → test → destroy) |
| `terraform show` | Inspect state/current config |
| `terraform output` | Show outputs |
| `terraform state list` / `state show <resource>` | List/inspect tracked resources |
| `terraform import` | Bring an existing resource under Terraform management (config still must be written correctly) |

Typical dev loop: `terraform fmt` → `terraform validate` → `terraform plan`.

## Resources, references, dependencies

- `resource "aws_s3_bucket" "app" {…}`: `aws_s3_bucket` = resource type, `app` = local name; referenced as `aws_s3_bucket.app` (e.g. `aws_s3_bucket.app.id`). References create **implicit dependencies** — Terraform orders creation (Security Group → EC2). `depends_on = [...]` is an **explicit** dependency for cases Terraform can't infer — don't overuse.
- **Data sources** (`data`) read existing info (existing VPC/AMI/subnet) without creating it; `resource` manages/creates.
- **Locals** (`locals { environment = "dev"; project = "my-api" }` → `local.project`) avoid repetition (tags).

## Variables and outputs

```hcl
variable "aws_region" { type = string  default = "ap-south-1" }
provider "aws" { region = var.aws_region }
output "bucket_name" { value = aws_s3_bucket.app.bucket }
```
- Override via `terraform.tfvars`, or `terraform apply -var="aws_region=ap-south-1"`. Types: `string`, `number`, `bool`, `list`, `set`, `map`, `object`. Don't commit secrets in tfvars.
- Mental model: variables (input) → Terraform → infrastructure → outputs (`terraform output`).

## State (most important concept)

- After `apply`, Terraform writes `terraform.tfstate`: *Terraform code → State → Real infrastructure*; answers "what do I currently manage?" so it can compare desired vs known/real state.
- State may contain sensitive data → **don't commit** it. `.gitignore`: `.terraform/`, `*.tfstate`, `*.tfstate.*`. `.terraform.lock.hcl` (provider selections/checksums) **is generally committed**.
- **Drift:** someone manually changes AWS (t3.micro → t3.medium) → config ≠ real; `terraform plan` reveals what Terraform would change. A major reason IaC matters.
- **Remote state:** teams need shared state (not on laptops) → remote backend, commonly **S3**. **State locking** prevents two simultaneous `apply`s (acquire lock → modify state → release). Current Terraform/AWS also supports **native S3 locking**; older tutorials show a separate DynamoDB lock table — don't blindly copy that.

## Modules and environments

- **Modules** (root module + child modules): `module "network" { source = "./modules/network"  environment = "dev" }`; layout `modules/network/{main,variables,outputs}.tf`, `modules/app/…`. Avoid a 5,000-line `main.tf`.
- **Environments:** `environments/{dev,staging,prod}/` or reusable modules with separate configs. **Workspaces** (`terraform workspace`) keep separate state instances but aren't automatically best for production; large teams often use separate root configs/state backends for stronger isolation.

## Credentials and CI/CD

- Never put `AWS_ACCESS_KEY_ID/SECRET` in `main.tf`, Git, Dockerfile, committed tfvars. Local: `aws configure`/credential mechanisms. CI: GitHub Actions → **OIDC** → IAM Role → temporary credentials → Terraform.
- Pipeline: PR → `fmt`, `validate`, `plan` → review → merge → **controlled apply** (approval, permissions, environment protection). Don't auto-apply every PR.
```yaml
name: Terraform
on:
  pull_request:
  push: { branches: [main] }
jobs:
  terraform:
    runs-on: ubuntu-latest
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
      - run: terraform fmt -check
      - run: terraform validate
      - run: terraform plan
```

## Learning plan and lab

Phases: (1) S3 — provider/resource/init/plan/apply/destroy/state → (2) VPC, Subnet, Route Table, IGW, SG → (3) EC2 (dependencies, outputs, variables) → (4) RDS (network dependencies, SGs, private infra) → (5) modules → (6) remote state, CI/CD, OIDC. Project layout `infra/{main,variables,outputs}.tf, terraform.tfvars, .gitignore, modules/{network,compute,database}`.
Lab (12 steps): create dir + provider + learning bucket → `init` → `fmt`/`validate` → `plan` (read it!) → `apply` → check AWS → `state list` → `output` → change tags and `plan` → `destroy`.

## Common mistakes

1. Hard-coded secrets (`password = "mypassword"`). 2. Committing state. 3. Running `apply` blindly (read `plan`). 4. Manual AWS changes → drift. 5. Giant Terraform file.

## Explain Terraform in an interview

Configuration → `init` (providers) → `plan` (compare desired config with tracked/real infrastructure) → `apply` (cloud APIs create/modify) → state updated.

## Depth guide

Deep: IaC, HCL, provider, resource, variables, outputs, dependencies, init/fmt/validate/plan/apply/destroy, state, drift, modules, remote state, locking, secrets, CI/CD. Medium: data sources, locals, workspaces, import, lifecycle rules, dynamic blocks, `for_each`, `count`. Awareness: Terraform Cloud, Terragrunt, Ansible, CloudFormation, Pulumi.

## Added notes (not in source)

- **Code correction:** in the chapter's EC2 example, `security_groups = [aws_security_group.app.name]` is the form for EC2-Classic/default VPC; for an instance in a VPC use `vpc_security_group_ids = [aws_security_group.app.id]`. See [Corrections](../CORRECTIONS.md).
- The CI workflow above sets `id-token: write` but never configures AWS credentials; add `aws-actions/configure-aws-credentials` (role-to-assume) before `plan`, and configure a remote backend, otherwise `plan` can't reach AWS/state.
- `terraform plan -out=tfplan` + `terraform apply tfplan` guarantees you apply exactly what was reviewed; `apply -auto-approve` skips the prompt (CI only, after an approval gate).
- Terraform 1.5+ supports declarative **`import` blocks**; Terraform ≥1.10 supports S3-native locking (`use_lockfile = true` in the `s3` backend) — verify against current docs.
- Variable values can also come from `TF_VAR_name` environment variables or `*.auto.tfvars`; mark secrets `sensitive = true` (still stored in state).
- `lifecycle { prevent_destroy = true }` protects critical resources; `create_before_destroy`, `ignore_changes` also exist. `count` and `for_each` create multiple instances of a resource (see [Chapter 32](../docs/06-iac-config/ch32-advanced-terraform.md)).
- Terraform's licence changed to BSL in 2023; **OpenTofu** is the open-source fork — worth knowing for interviews.

<!-- NAV -->

---

← [Sheet 20](ch20-revision.md) · [Full chapter 21](../docs/06-iac-config/ch21-terraform.md) · [All revision material](README.md) · [Sheet 22](ch22-revision.md) →
