# Chapter 32 — Revision Sheet: Advanced Terraform

> Supplements [the full chapter](../docs/06-iac-config/ch32-advanced-terraform.md). Goal: **design, explain, review, troubleshoot and safely use Terraform for real AWS infrastructure.** Builds on [Chapter 21](../docs/06-iac-config/ch21-terraform.md).

## What Terraform is really doing

Configuration (desired) + **State** + **Provider** + refresh/read operations + **dependency graph** → plan → AWS APIs → actual infrastructure ≈ desired. Production concerns: state, modules, dependencies, environments, remote state, locking, drift, CI/CD, security. Plan inputs: config ∥ state ∥ actual infrastructure → plan (this is how drift is detected).

## State (the most important advanced concept)

- State maps `aws_s3_bucket.assets` ↔ the real AWS object ID, and records what Terraform manages, attributes known and what changed. **State is not just a cache/copy of AWS.**
- **Dangerous:** may contain sensitive data (resource attributes, IDs, connection info, sensitive values). `sensitive = true` only hides values in CLI output — they can still be in state. Protect the backend.
- **`.gitignore`:** `.terraform/`, `*.tfstate`, `*.tfstate.*`, `*.tfplan` — but **commit `.terraform.lock.hcl`** (the chapter first lists it as ignored, then corrects: it pins provider versions/checksums → more reproducible infrastructure).
- **Remote state + locking** are fundamental for teams: independent local state ⇒ A's state ≠ B's state; without locking: A and B read state, both change infrastructure, B writes stale state ⇒ inconsistent. Locking flow: acquire lock → modify infrastructure/state → release. Modern S3 backend supports **native S3 locking**; older tutorials use a DynamoDB table — follow the docs for your versions.
```hcl
terraform {
  backend "s3" {
    bucket = "company-terraform-state"
    key    = "production/network/terraform.tfstate"
    region = "..."
  }
}
```
- **State bucket security:** encryption, versioning, restricted IAM, private access, logging/monitoring; never public. CI uses IAM to reach the private bucket; limit developer access (CI role vs limited developer IAM).
- **Bootstrap problem:** who creates the S3 bucket that stores state? A bootstrap Terraform creates the state infrastructure first (often managed centrally in larger organisations). **Versioning** (state-v1, v2, v3) is a recovery safety mechanism, not a replacement for proper workflows. **Disaster recovery:** if state is deleted, infrastructure still exists but Terraform loses its mapping → backups/versioning + controlled access; imports can reconstruct management.
- **Commands:** `terraform state list`, `terraform state show aws_instance.web`, `terraform state rm aws_instance.web` — removes the resource from **state without deleting the real AWS resource** (EC2 still exists; if the block remains in config, `plan` may try to create another).
- **Import:** existing AWS resource → `terraform import` → state → configuration. Import doesn't write perfect code; you still need configuration that represents the resource; run `terraform plan` after import and reconcile differences (modern Terraform also has `import` blocks).
- **Drift:** config `t3.medium` but someone changes AWS to `t3.large` → detected during planning/refresh. Dangerous because nobody knows the intended configuration → manage infrastructure through the declared workflow, not ad-hoc console changes.
- **Refresh:** old tutorials teach standalone `terraform refresh`; modern workflows incorporate refresh into plan/apply — Terraform needs current information before producing an accurate plan.

## Modules

- Reuse, consistency, abstraction, standardisation, maintainability — a module is like a reusable function (`createDatabase(config)`). Layout: `modules/network/{main.tf (resources), variables.tf (inputs), outputs.tf (outputs), README.md}`.
```hcl
# variables.tf
variable "vpc_cidr" { type = string }
# main.tf
resource "aws_vpc" "this" { cidr_block = var.vpc_cidr }
# outputs.tf
output "vpc_id" { value = aws_vpc.this.id }
# root
module "network" {
  source   = "./modules/network"
  vpc_cidr = "10.0.0.0/16"
}
# use: module.network.vpc_id
```
Flow: root module →inputs→ child module → creates infrastructure → outputs → root (like arguments and return values).
- **Good design:** expose important configuration (`cidr_block`, `az_count = 3`), hide implementation details (route tables). **Don't over-modularise** (module-vpc, module-subnet, module-route-table, module-route, module-security-group, module-rule…): prefer meaningful modules — `network`, `eks`, `database`, `observability`.
- **Sources:** local directory, Git repository, Terraform Registry. **Internal modules** let a platform team standardise VPC, logging, IAM, encryption (Platform Team → reusable modules → engineering teams). **Module versioning** (v1.0, v1.1, v2.0): production pinned at v1.2 while staging tests v1.3 → controlled promotion.
- **Root vs child:** `terraform/ {main.tf, variables.tf, outputs.tf, modules/{network, eks, rds, monitoring}}`.

## Environments and blast radius

- Pattern to know: `infra/modules/{vpc,eks,rds,redis}` + `infra/environments/{dev,staging,prod}`, each environment calling shared modules, **each with separate state** (`S3: dev/terraform.tfstate, staging/…, prod/…`). One state for dev+staging+prod ⇒ a mistake can affect everything. **Blast radius** = how much a mistake can affect → smaller states reduce it.
- **Workspaces** (`terraform workspace`): separate state instances for the same configuration; not automatically the best environment architecture — many teams use separate root configurations/state backends for explicit boundaries. *Interview:* "Workspaces provide separate state instances for the same configuration but shouldn't automatically be treated as the solution to every environment-management problem."
- **State separation:** don't put VPC, EKS, RDS, S3, 100 applications and every environment into one giant state. Smaller states = smaller plans, faster operations, smaller blast radius, better ownership, less contention, easier troubleshooting — but don't split so much that dependencies become unmanageable. **Cross-state references** (remote-state data access, e.g. network state → VPC ID → EKS state); excessive coupling is hard to maintain; prefer clear boundaries.

## Variables, secrets, data sources, dependencies

- Variable strategy: `variable "environment" { type = string }`, `variable "instance_type"`; env-specific values via `dev.tfvars` / `prod.tfvars`. **Never** put production secrets in committed `.tfvars` (`DB_PASSWORD=…`) — use Secrets Manager, SSM Parameter Store, CI/CD secret store.
- **`data` vs `resource`:** `data "aws_vpc" "existing" {…}` → `data.aws_vpc.existing.id` (read existing information) vs resource (create/manage).
- **Dependency graph:** `vpc_id = aws_vpc.main.id` → implicit dependency (VPC → Subnet), preferred. `depends_on = [aws_iam_role_policy.example]` for non-inferable dependencies — overuse serialises operations and loses parallelism. `terraform graph` visualises it.
- **Lifecycle:** `prevent_destroy = true` (critical resources like the production database), `create_before_destroy = true` (replace without downtime when the resource supports it), `ignore_changes = [tags]` (careful — hides drift).
- **`moved` blocks:** moving `aws_s3_bucket.assets` into `module "storage"` makes Terraform think "old removed, new created"; `moved { from = aws_s3_bucket.assets  to = module.storage.aws_s3_bucket.assets }` preserves identity and avoids destroy/create.
- **`count` vs `for_each`:** `count = 3` → `resource[0..2]`; `for_each = { api = …, worker = … }` → `resource["api"]`. `for_each` is safer when items have stable names (with `count`, removing the second item shifts indexes).
- **Locals/naming/tags:** `locals { name_prefix = "${var.project}-${var.environment}" }` → `name = "${local.name_prefix}-api"`; names like `payments-prod-eks`, `payments-prod-rds`, `payments-prod-assets`; tags `Project`, `Environment`, `Owner`, `ManagedBy`, `CostCenter` for cost allocation, search, operations, governance.

## Plan, apply, CI/CD

- `terraform plan` shows `+ create`, `~ modify`, `- destroy`; **read the plan**; never `terraform apply -auto-approve` against production. **Saved plans:** `terraform plan -out=tfplan` → `terraform apply tfplan` (applies exactly the reviewed plan; useful in CI/CD).
- **Mature pipeline:** PR → fmt → validate → security/static checks → plan → review → approval → (merge) → apply; production adds manual approval. GitHub Actions: `actions/checkout@v4`, `hashicorp/setup-terraform@v3`, `terraform init/fmt -check/validate/plan`. Credentials: GitHub Actions → OIDC → IAM role → temporary credentials (no long-lived keys in GitHub secrets/source/Terraform files).
- **Versioning:** commit `.terraform.lock.hcl`; pin provider ranges (`version = "~> 6.0"`) and don't blindly use `latest`; `required_version` for Terraform (choose a real range; the chapter's `">= 1.x, < 2.0"` is a placeholder). **Upgrade process:** read changelog → upgrade dev → `terraform init -upgrade` → plan → test → staging → production.
- **Guardrails:** code review, plan review, protected branches, CI checks, policy-as-code, approval gates, least privilege, separate production credentials. **Policy as code** (OPA, Sentinel): e.g. "production S3 buckets must not be publicly accessible" → Plan → policy check → ❌ reject. **Security scanning** of IaC: public S3, overly broad IAM, unencrypted resources, open security groups. **Testing:** `fmt`, `validate`, `plan`; more advanced module/integration/policy tests — infrastructure is code.

## Tool boundaries and ownership

| Tool | Owns |
|---|---|
| **Terraform** | AWS networking, EKS, node groups, IAM, RDS, S3, load-balancer infrastructure, supporting infrastructure |
| **ArgoCD** | Deployments, Services, ConfigMaps, Helm releases, application configuration |
| **Kubernetes** | Runtime reconciliation (Pods, ReplicaSets, HPA, Jobs) |
| Helm | Kubernetes packaging |
| Ansible | Configure/manage machines (install nginx, configure server, manage service) |

Terraform can also manage Helm releases (`resource "helm_release" "app"`) but watch ownership boundaries. **Two tools managing one resource** (Terraform and ArgoCD on the same Deployment) ⇒ conflicting desired states ⇒ **ownership conflict** → define clear boundaries. Terraform → EKS infrastructure → ArgoCD → Helm → workloads.

## Production scenarios

1. **Someone manually changed the RDS class** (config `db.t3.medium`, actual `db.r6g.large`): don't immediately apply. Was it intentional? If yes, update the configuration and `terraform plan`; if accidental, decide whether Terraform should restore the intended state.
2. **"Terraform wants to destroy our production database!"** → **STOP APPLY**, inspect the plan: immutable field changed, resource address changed, module refactor, provider behaviour, configuration mismatch, import/state issue. Never blindly approve a destructive plan.
3. **Resource address changes** after refactors → `moved` block.
4. **Plan as safety mechanism:** `t3.large` → `t3.nano` shows `~ change`; `- destroy` ⇒ stop and investigate.

## Interview answers (12)

Why state; why remote state; why locking; drift; module; `resource` vs `data`; Terraform vs Ansible; Terraform vs Kubernetes; why Terraform and ArgoCD shouldn't manage the same resource; how to protect production Terraform (remote state, locking, IAM, PR review, plan review, approval, CI/CD, policy checks, separate environments, least privilege); what to do if Terraform wants to destroy production RDS; why `moved` blocks.

**Depth:** 🔥 state, remote state, locking, modules, environments, drift, lifecycle, dependencies, CI/CD, security, Terraform/Kubernetes/ArgoCD boundaries · 🟡 workspaces, policy-as-code, testing, advanced module publishing, cross-state dependencies · ⚪ Terraform internals, provider development, specialised enterprise tooling.

## Added (see supplement in the chapter)

Complete S3 backend (`use_lockfile`), `for_each` map example with `each.key/each.value`, lifecycle caveat (`prevent_destroy` stops protecting if the block is deleted), `import` block + `-generate-config-out`, `removed` block, `terraform_remote_state` data source, command table (`apply -refresh-only`, `state mv`, `-replace`, `force-unlock`, `-lock-timeout`, `-target`), tooling (tflint, Checkov, Trivy, OPA/Conftest, Sentinel, `terraform test`, Terratest).

<!-- NAV -->

---

← [Sheet 31](ch31-revision.md) · [Full chapter 32](../docs/06-iac-config/ch32-advanced-terraform.md) · [All revision material](README.md) · [Sheet 33](ch33-revision.md) →
