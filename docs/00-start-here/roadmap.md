# Roadmap

The original conversation was a planned multi-response course. It was first announced as **24 responses** ("core"),
then extended to **36** ("extended"). **Thirty-six source files contain a response** (files 1–36; files 37–40 are empty). The
planned 36th item, "Final DevOps Mastery", was never delivered; file 36 is instead a stand-alone *Virtualization Internals — Deep Dive*
(see [PROGRESS](../../PROGRESS.md)).

## Chapter map

| Ch | Topic | Domain | Part |
|---:|---|---|---|
| 1 | Cloud + DevOps Fundamentals | Foundations | I |
| 2 | Linux for Cloud & DevOps | Foundations | I |
| 3 | Bash & Linux Automation | Foundations | I |
| 4 | Networking for Cloud & DevOps | Foundations | I |
| 5 | Git & GitHub Deep Dive | Foundations | I |
| 6 | CI/CD + GitHub Actions | CI/CD | I |
| 7 | Docker Fundamentals | Containers | I |
| 8 | Docker Deep Dive + Production | Containers | I |
| 9 | AWS Fundamentals + IAM | AWS | I |
| 10 | EC2 + AWS Compute | AWS | I |
| 11 | S3 + AWS Storage | AWS | I |
| 12 | VPC + AWS Networking | AWS | I |
| 13 | RDS + Databases on AWS | AWS | I |
| 14 | Load Balancing + Scaling | AWS | I |
| 15 | Lambda + Serverless + Messaging | AWS | I |
| 16 | Route 53 + CloudFront + CDN + WAF | AWS | I |
| 17 | AWS Monitoring + Security | AWS | I |
| 18 | Kubernetes Fundamentals | Kubernetes | I |
| 19 | Kubernetes Configuration + Storage | Kubernetes | I |
| 20 | Kubernetes Networking + Scaling + Production | Kubernetes | I |
| 21 | Terraform: Infrastructure as Code | IaC | I |
| 22 | Observability + Reliability | Observability/SRE | I |
| 23 | Production Architecture + Troubleshooting | Production | I |
| 24 | Complete Cloud + DevOps Interview & OA Mastery | Interview | I |
| 25 | Helm: Kubernetes Package Management | Kubernetes | II |
| 26 | GitOps + ArgoCD | CI/CD & GitOps | II |
| 27 | Jenkins + Advanced CI/CD | CI/CD & GitOps | II |
| 28 | Ansible | IaC & Config | II |
| 29 | Kubernetes CRDs + Operators | Kubernetes | II |
| 30 | Service Mesh + Istio | Kubernetes | II |
| 31 | Advanced Amazon EKS | Kubernetes | II |
| 32 | Advanced Terraform | IaC & Config | II |
| 33 | Advanced AWS for Backend Engineers | AWS | II |
| 34 | Advanced SRE | Observability/SRE | II |
| 35 | DevOps Capstone (architecture/specification) | Production | II |
| 36 | Virtualization Internals — Deep Dive | Foundations | II |
| – | *Final DevOps Mastery* — **announced at the end of Chapter 35, not present in the source** | – | – |

## The AWS block

The source states that Responses 9–17 form the AWS block (IAM → EC2 → S3 → VPC → RDS → load balancing → Lambda/SQS/SNS →
Route 53/CloudFront/WAF → monitoring and security), after which Kubernetes (18–20), Terraform (21), observability (22),
integration (23) and interview mastery (24) follow. Part II then deepens and broadens: Helm, GitOps/ArgoCD, Jenkins,
Ansible, CRDs/Operators, service mesh, advanced EKS/Terraform/AWS/SRE, and a capstone specification.

## Depth tiers used throughout the source

Each chapter ends with what to know **deeply** (🔥), **reasonably/medium** (🟡) and at the **awareness** level (⚪/🟢).
Chapter 24 gives the overall tiering; the per-chapter tiers are preserved at the end of each chapter and repeated in its
revision sheet. The target the source repeatedly names is: *a backend/SWE engineer with strong Cloud + DevOps capability*, not a
dedicated DevOps specialist.

## Teaching style (as stated in the source)

Concept → Why → Setup → Commands/code/config → Build it → Deploy it → Test it → Break it → Debug it → Interview questions.
The change to this hands-on style was made at Chapter 15 — see [course design notes](course-design-notes.md).
