# Study Guide

How to use this knowledge base for first-time learning, interview revision and long-term reference.

## The three layers

| Layer | Where | Use it for |
|---|---|---|
| **Full chapters** | `docs/<domain>/chNN-*.md` | Understanding. Complete original explanations, examples, code and interview questions. Read once, carefully. |
| **Revision sheets** | `revision/chNN-revision.md` | Recall. One per chapter: key ideas, tables, commands, traps, interview answers, plus clearly marked *added notes*. |
| **Cross-cutting material** | `revision/00-…05-*.md`, [Glossary](../../GLOSSARY.md), [Corrections](../../CORRECTIONS.md), [labs](../../exercises/labs.md) | Interview prep across topics: cheat sheet, comparisons, formulas, Q&A bank, troubleshooting playbooks, traps. |

## Recommended first pass (about 10 weeks at ~1–2 h/day)

| Week | Chapters | Goal |
|---|---|---|
| 1 | 1–3 | Cloud/DevOps vocabulary, comfortable Linux shell, Bash scripts with exit codes |
| 2 | 4–5 | Networking (CIDR, DNS, TCP/HTTP/TLS, NAT) and Git internals |
| 3 | 6–8 | CI/CD pipelines, Docker images and production Dockerfiles |
| 4 | 9–11 | AWS foundation, IAM, EC2, S3 |
| 5 | 12–14 | VPC design, RDS, load balancing and autoscaling |
| 6 | 15–17 | Serverless/messaging, edge (Route 53/CloudFront/WAF), monitoring and security |
| 7 | 18–20 | Kubernetes: objects, configuration, networking, scaling |
| 8 | 21–23 | Terraform, observability/reliability, integration and incident debugging |
| 9 | 24, 25–28 | Interview map, then Helm, GitOps/ArgoCD, Jenkins, Ansible |
| 10 | 29–36 | CRDs/Operators, service mesh, advanced EKS/Terraform/AWS/SRE, capstone, then virtualization internals |

**Where does Chapter 36 (virtualization internals) fit?** It was delivered last but is conceptually foundational: read it after Chapters [7](../02-containers/ch07-docker-fundamentals.md)–[8](../02-containers/ch08-docker-production.md) if you want to understand *why* containers differ from VMs, or at the end as a deep-dive. It is not required for the DevOps tooling chapters.

Do the **labs** (`exercises/labs.md`) as you go: the source repeatedly says that reading without doing is not learning.

## Interview preparation sequence

1. [Chapter 24](../09-interview/ch24-interview-oa-mastery.md) — the whole map, the OA/MCQ traps and the "final 10 questions".
2. [Master cheat sheet](../../revision/00-master-cheatsheet.md) and [traps and misconceptions](../../revision/05-traps-and-misconceptions.md).
3. [Comparisons](../../revision/01-comparisons.md) — every "X vs Y" question in one place.
4. [Formulas and numbers](../../revision/02-formulas-and-numbers.md).
5. [Interview Q&A bank](../../revision/03-interview-qa.md) — say the answers aloud.
6. [Troubleshooting playbooks](../../revision/04-troubleshooting-playbooks.md) — rehearse the outside-in debugging flow.
7. Chapters [23](../08-production/ch23-production-architecture-troubleshooting.md) and [35](../08-production/ch35-devops-capstone.md) — be able to draw and defend a full architecture.

## Depth tiers (from the source)

- **Master** (explain, configure, write, deploy, debug): Linux, networking, Git, Docker, CI/CD, AWS fundamentals, VPC, IAM, EC2, S3, RDS, load balancing, Kubernetes fundamentals, Terraform, monitoring, troubleshooting.
- **Strong working knowledge:** EKS, Lambda, SQS/SNS, CloudFront, WAF, Prometheus, Grafana, OpenTelemetry, HPA, advanced Terraform modules (Part II promotes several of these: EKS, Terraform, AWS design, SRE).
- **Awareness** (what / why / when): ArgoCD, GitOps, Jenkins, Ansible, service mesh, Istio, Operators, CRDs — Part II then covers each in depth.

## Conventions in this repository

- **Chapter numbers equal the response numbers** of the source, so "Response 6" in any original wording means [Chapter 6](../03-cicd-gitops/ch06-cicd-github-actions.md).
- Chapter files contain the **original text** (only scaffolding removed; see [removed scaffolding](removed-scaffolding.md)). Anything added by the editor is in a separate **"Editorial supplement"** section at the end of a chapter, or in the **"Added notes"** section of a revision sheet, and says so.
- Items marked **verify** are version-dependent facts that were not independently confirmed; items in [CORRECTIONS](../../CORRECTIONS.md) marked *verified* were checked against official documentation.
