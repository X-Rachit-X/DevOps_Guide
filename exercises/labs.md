# Labs and Exercises

Two parts: **(A)** the hands-on labs that exist *in the source chapters* (linked, not copied — the full text lives in the chapter), and **(B)** *editorial* labs added to give every chapter a practice task. Part B is not source material.

> Labs touching AWS create billable resources. Use a sandbox account, set a budget alarm, and destroy resources afterwards (`terraform destroy`, delete clusters/NAT gateways/load balancers).

## A. Labs in the source chapters

| Ch | Lab / exercise heading | Link |
|---|---|---|
| 2 | 36. Mini Practical Exercise | [ch02-linux.md](../docs/01-foundations/ch02-linux.md#36-mini-practical-exercise) |
| 3 | 31. Practical Deployment Script | [ch03-bash-automation.md](../docs/01-foundations/ch03-bash-automation.md#31-practical-deployment-script) |
| 3 | Practical Assignment | [ch03-bash-automation.md](../docs/01-foundations/ch03-bash-automation.md#practical-assignment) |
| 4 | 42. Practical Commands | [ch04-networking.md](../docs/01-foundations/ch04-networking.md#42-practical-commands) |
| 4 | 43. A Practical Node.js Example | [ch04-networking.md](../docs/01-foundations/ch04-networking.md#43-a-practical-nodejs-example) |
| 4 | Practical Assignment | [ch04-networking.md](../docs/01-foundations/ch04-networking.md#practical-assignment) |
| 5 | Practical Git Lab | [ch05-git-github.md](../docs/01-foundations/ch05-git-github.md#practical-git-lab) |
| 6 | Practical Assignment | [ch06-cicd-github-actions.md](../docs/03-cicd-gitops/ch06-cicd-github-actions.md#practical-assignment) |
| 7 | Practical Lab | [ch07-docker-fundamentals.md](../docs/02-containers/ch07-docker-fundamentals.md#practical-lab) |
| 9 | 32. AWS CLI Practical Flow | [ch09-aws-fundamentals-iam.md](../docs/04-aws/ch09-aws-fundamentals-iam.md#32-aws-cli-practical-flow) |
| 9 | Practical Lab | [ch09-aws-fundamentals-iam.md](../docs/04-aws/ch09-aws-fundamentals-iam.md#practical-lab) |
| 10 | Practical Project | [ch10-ec2-compute.md](../docs/04-aws/ch10-ec2-compute.md#practical-project) |
| 11 | Practical Project | [ch11-s3-storage.md](../docs/04-aws/ch11-s3-storage.md#practical-project) |
| 12 | Practical Exercise | [ch12-vpc-networking.md](../docs/04-aws/ch12-vpc-networking.md#practical-exercise) |
| 13 | Practical Lab | [ch13-rds-databases.md](../docs/04-aws/ch13-rds-databases.md#practical-lab) |
| 14 | Practical Exercise | [ch14-load-balancing-scaling.md](../docs/04-aws/ch14-load-balancing-scaling.md#practical-exercise) |
| 15 | 25. Practical Example — Order Processing | [ch15-lambda-serverless-messaging.md](../docs/04-aws/ch15-lambda-serverless-messaging.md#25-practical-example--order-processing) |
| 15 | Your Practical Assignment | [ch15-lambda-serverless-messaging.md](../docs/04-aws/ch15-lambda-serverless-messaging.md#your-practical-assignment) |
| 16 | Your Hands-On Challenge | [ch16-route53-cloudfront-waf.md](../docs/04-aws/ch16-route53-cloudfront-waf.md#your-hands-on-challenge) |
| 17 | 45. Practical DevOps Setup | [ch17-monitoring-security.md](../docs/04-aws/ch17-monitoring-security.md#45-practical-devops-setup) |
| 17 | Final Practical Assignment | [ch17-monitoring-security.md](../docs/04-aws/ch17-monitoring-security.md#final-practical-assignment) |
| 18 | Your Kubernetes Lab | [ch18-kubernetes-fundamentals.md](../docs/05-kubernetes/ch18-kubernetes-fundamentals.md#your-kubernetes-lab) |
| 19 | PART 11 — PRACTICAL LAB | [ch19-kubernetes-config-storage.md](../docs/05-kubernetes/ch19-kubernetes-config-storage.md#part-11--practical-lab) |
| 19 | Lab architecture | [ch19-kubernetes-config-storage.md](../docs/05-kubernetes/ch19-kubernetes-config-storage.md#lab-architecture) |
| 19 | 32. Storage Lab | [ch19-kubernetes-config-storage.md](../docs/05-kubernetes/ch19-kubernetes-config-storage.md#32-storage-lab) |
| 20 | PART 17 — PRACTICAL PRODUCTION LAB | [ch20-kubernetes-networking-scaling.md](../docs/05-kubernetes/ch20-kubernetes-networking-scaling.md#part-17--practical-production-lab) |
| 21 | PART 21 — YOUR PRACTICAL TERRAFORM LAB | [ch21-terraform.md](../docs/06-iac-config/ch21-terraform.md#part-21--your-practical-terraform-lab) |
| 22 | PART 15 — PRACTICAL NODE.JS OBSERVABILITY | [ch22-observability-reliability.md](../docs/07-observability-sre/ch22-observability-reliability.md#part-15--practical-nodejs-observability) |
| 25 | 37. Your Hands-On Helm Lab | [ch25-helm.md](../docs/05-kubernetes/ch25-helm.md#37-your-hands-on-helm-lab) |
| 26 | 35. Hands-On Mini Project | [ch26-gitops-argocd.md](../docs/03-cicd-gitops/ch26-gitops-argocd.md#35-hands-on-mini-project) |
| 27 | 40. Jenkins Hands-On Exercise | [ch27-jenkins-advanced-cicd.md](../docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md#40-jenkins-hands-on-exercise) |
| 28 | 20. Practical Example — Configure Node.js Server | [ch28-ansible.md](../docs/06-iac-config/ch28-ansible.md#20-practical-example--configure-nodejs-server) |
| 28 | 54. Final Practical Workflow | [ch28-ansible.md](../docs/06-iac-config/ch28-ansible.md#54-final-practical-workflow) |
| 30 | 46. A Practical Canary Architecture | [ch30-service-mesh-istio.md](../docs/05-kubernetes/ch30-service-mesh-istio.md#46-a-practical-canary-architecture) |
| 31 | Practical EKS setup the chapter describes but does not show | [ch31-advanced-eks.md](../docs/05-kubernetes/ch31-advanced-eks.md#practical-eks-setup-the-chapter-describes-but-does-not-show) |

## B. Editorial labs (added; not from the source)

### Chapter 1 — [cloud devops fundamentals](../docs/01-foundations/ch01-cloud-devops-fundamentals.md)
- Draw the request path of a web app on a napkin: user → DNS → LB → app → DB. Mark which parts scale horizontally and which are stateful.
- Compute allowed downtime per month for 99.9% and 99.99%; then compute the availability of two 99.9% services in series.

### Chapter 3 — [bash automation](../docs/01-foundations/ch03-bash-automation.md)
- Write `backup.sh` with `set -euo pipefail`, a `trap` cleanup, argument validation and a log function; make it fail fast on an unset variable.
- Write a cron entry that runs it daily at 02:00 and appends output to a log.

### Chapter 4 — [networking](../docs/01-foundations/ch04-networking.md)
- With `dig`, `curl -v`, `ss -tulpn` and `traceroute`, trace a real HTTPS request and label DNS, TCP, TLS and HTTP phases.
- Compute the address count and range for 10.0.0.0/16 split into /24 subnets across 2 AZs.

### Chapter 6 — [cicd github actions](../docs/03-cicd-gitops/ch06-cicd-github-actions.md)
- Create a GitHub Actions workflow: checkout → setup-node → `npm ci` → lint → test → build, with a matrix of two Node versions and dependency caching.

### Chapter 15 — [lambda serverless messaging](../docs/04-aws/ch15-lambda-serverless-messaging.md)
- Create an SQS queue with a DLQ (maxReceiveCount 3) and a consumer that is idempotent; send a poison message and watch it land in the DLQ.

### Chapter 17 — [monitoring security](../docs/04-aws/ch17-monitoring-security.md)
- Create a CloudWatch alarm on 5xx rate with an SNS notification; then find the corresponding API call in CloudTrail.

### Chapter 22 — [observability reliability](../docs/07-observability-sre/ch22-observability-reliability.md)
- Instrument a small Node API with prom-client (RED metrics); scrape with Prometheus; chart p95 in Grafana; write an alert on error ratio.

### Chapter 23 — [production architecture troubleshooting](../docs/08-production/ch23-production-architecture-troubleshooting.md)
- Take the production checklist and score your own project against it; list the five biggest gaps.

### Chapter 24 — [interview oa mastery](../docs/09-interview/ch24-interview-oa-mastery.md)
- Time yourself answering the Chapter 24 scenario questions aloud in 2 minutes each, using the Prevent → Detect → Contain → Recover → Learn frame.

### Chapter 28 — [ansible](../docs/06-iac-config/ch28-ansible.md)
- Write an inventory + playbook that installs nginx, templates a config and restarts via a handler; run it twice and confirm the second run reports `changed=0`.

### Chapter 29 — [crds operators](../docs/05-kubernetes/ch29-crds-operators.md)
- Define a small CRD and create a custom resource; observe that nothing happens without a controller; then deploy a controller that sets `status`.

### Chapter 30 — [service mesh istio](../docs/05-kubernetes/ch30-service-mesh-istio.md)
- Install Istio (demo profile), label a namespace, split 90/10 traffic with a VirtualService/DestinationRule, and enforce strict mTLS.

### Chapter 31 — [advanced eks](../docs/05-kubernetes/ch31-advanced-eks.md)
- Create an EKS cluster with eksctl or Terraform, install the AWS Load Balancer Controller, and give a Pod S3 access with Pod Identity/IRSA.

### Chapter 32 — [advanced terraform](../docs/06-iac-config/ch32-advanced-terraform.md)
- Create an S3 backend with locking, split a config into two modules, import one existing resource and use a `moved` block for a rename.

### Chapter 33 — [advanced aws backend](../docs/04-aws/ch33-advanced-aws-backend.md)
- Build S3 → SQS → worker image-processing flow locally against LocalStack; add a DLQ and verify duplicate handling.

### Chapter 34 — [advanced sre](../docs/07-observability-sre/ch34-advanced-sre.md)
- Define an SLO (99.9% availability, p95 < 300 ms), compute the error budget, and write the multi-window burn-rate alerts; then run a k6 test to find the knee of the latency curve.

### Chapter 35 — [devops capstone](../docs/08-production/ch35-devops-capstone.md)
- Follow `code-examples/capstone/` (editorial starter) and extend it with one failure-injection test.

### Chapter 36 — [virtualization internals](../docs/01-foundations/ch36-virtualization-internals.md)
- On a Linux VM run `systemd-detect-virt`, `lscpu` and `grep -c -E '(vmx|svm)' /proc/cpuinfo`; then use `unshare --pid --fork --mount-proc bash` to see a PID namespace and compare with `docker run --rm alpine ps`.

## Suggested order

1. Linux/Bash/Git (2, 3, 5) → 2. Docker (7, 8) → 3. CI (6) → 4. AWS core (9–14) → 5. Kubernetes (18–20) → 6. Terraform (21) → 7. Observability (22) → 8. GitOps/Helm (25, 26) → 9. Capstone (35).

---
[← Contents](../CONTENTS.md)
