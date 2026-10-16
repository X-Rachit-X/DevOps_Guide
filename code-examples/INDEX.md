# Extracted Code Examples

Every substantial code block from the chapters (Dockerfiles, YAML, Terraform, Jenkinsfiles, JSON, TypeScript,
shell scripts, INI/Jinja templates) extracted to its own file so it can be copied or linted. These are
**source-derived** and many are deliberately simplified or contain placeholders (`...`, `<account-id>`) —
read the surrounding chapter before using them. The last column links to the block in the chapter.

| Chapter | File | Language | Lines | In chapter |
|---|---|---|---:|---|
| 1 — Cloud + DevOps Fundamentals | [`ch01/01-name-ci.yaml`](extracted/ch01/01-name-ci.yaml) | yaml | 18 | [line 689](../docs/01-foundations/ch01-cloud-devops-fundamentals.md) |
| 1 — Cloud + DevOps Fundamentals | [`ch01/02-resource-aws-instance-app.tf`](extracted/ch01/02-resource-aws-instance-app.tf) | hcl | 4 | [line 815](../docs/01-foundations/ch01-cloud-devops-fundamentals.md) |
| 1 — Cloud + DevOps Fundamentals | [`ch01/03-export-const-handler-async-event.js`](extracted/ch01/03-export-const-handler-async-event.js) | javascript | 6 | [line 946](../docs/01-foundations/ch01-cloud-devops-fundamentals.md) |
| 3 — Bash & Linux Automation | [`ch03/01-set-euo-pipefail.sh`](extracted/ch03/01-set-euo-pipefail.sh) | bash | 17 | [line 1104](../docs/01-foundations/ch03-bash-automation.md) |
| 3 — Bash & Linux Automation | [`ch03/02-if-curl-fs-http-localhost-3000-h.sh`](extracted/ch03/02-if-curl-fs-http-localhost-3000-h.sh) | bash | 9 | [line 1158](../docs/01-foundations/ch03-bash-automation.md) |
| 3 — Bash & Linux Automation | [`ch03/03-set-euo-pipefail.sh`](extracted/ch03/03-set-euo-pipefail.sh) | bash | 14 | [line 1264](../docs/01-foundations/ch03-bash-automation.md) |
| 3 — Bash & Linux Automation | [`ch03/04-set-euo-pipefail.sh`](extracted/ch03/04-set-euo-pipefail.sh) | bash | 33 | [line 1470](../docs/01-foundations/ch03-bash-automation.md) |
| 4 — Networking for Cloud & DevOps | [`ch04/01-http-1-1-200-ok.http`](extracted/ch04/01-http-1-1-200-ok.http) | http | 6 | [line 751](../docs/01-foundations/ch04-networking.md) |
| 4 — Networking for Cloud & DevOps | [`ch04/02-app-get-users-async-req-res.ts`](extracted/ch04/02-app-get-users-async-req-res.ts) | typescript | 5 | [line 1210](../docs/01-foundations/ch04-networking.md) |
| 4 — Networking for Cloud & DevOps | [`ch04/03-import-express-from-express.ts`](extracted/ch04/03-import-express-from-express.ts) | typescript | 11 | [line 1540](../docs/01-foundations/ch04-networking.md) |
| 4 — Networking for Cloud & DevOps | [`ch04/04-import-express-from-express.ts`](extracted/ch04/04-import-express-from-express.ts) | typescript | 11 | [line 1823](../docs/01-foundations/ch04-networking.md) |
| 5 — Git & GitHub Deep Dive | [`ch05/01-node-modules.gitignore`](extracted/ch05/01-node-modules.gitignore) | gitignore | 4 | [line 1049](../docs/01-foundations/ch05-git-github.md) |
| 6 — CI/CD + GitHub Actions | [`ch06/01-name-ci.yaml`](extracted/ch06/01-name-ci.yaml) | yaml | 27 | [line 272](../docs/03-cicd-gitops/ch06-cicd-github-actions.md) |
| 6 — CI/CD + GitHub Actions | [`ch06/02-jobs.yaml`](extracted/ch06/02-jobs.yaml) | yaml | 9 | [line 528](../docs/03-cicd-gitops/ch06-cicd-github-actions.md) |
| 6 — CI/CD + GitHub Actions | [`ch06/03-jobs.yaml`](extracted/ch06/03-jobs.yaml) | yaml | 7 | [line 560](../docs/03-cicd-gitops/ch06-cicd-github-actions.md) |
| 6 — CI/CD + GitHub Actions | [`ch06/04-name-ci.yaml`](extracted/ch06/04-name-ci.yaml) | yaml | 22 | [line 594](../docs/03-cicd-gitops/ch06-cicd-github-actions.md) |
| 6 — CI/CD + GitHub Actions | [`ch06/05-name-ci.yaml`](extracted/ch06/05-name-ci.yaml) | yaml | 34 | [line 1331](../docs/03-cicd-gitops/ch06-cicd-github-actions.md) |
| 7 — Docker Fundamentals | [`ch07/01-import-express-from-express.ts`](extracted/ch07/01-import-express-from-express.ts) | typescript | 11 | [line 629](../docs/02-containers/ch07-docker-fundamentals.md) |
| 7 — Docker Fundamentals | [`ch07/02-from-node-22.dockerfile`](extracted/ch07/02-from-node-22.dockerfile) | dockerfile | 15 | [line 707](../docs/02-containers/ch07-docker-fundamentals.md) |
| 7 — Docker Fundamentals | [`ch07/03-from-node-22.dockerfile`](extracted/ch07/03-from-node-22.dockerfile) | dockerfile | 11 | [line 1095](../docs/02-containers/ch07-docker-fundamentals.md) |
| 7 — Docker Fundamentals | [`ch07/04-services.yaml`](extracted/ch07/04-services.yaml) | yaml | 11 | [line 1405](../docs/02-containers/ch07-docker-fundamentals.md) |
| 7 — Docker Fundamentals | [`ch07/05-docker-pull.sh`](extracted/ch07/05-docker-pull.sh) | bash | 14 | [line 1518](../docs/02-containers/ch07-docker-fundamentals.md) |
| 7 — Docker Fundamentals | [`ch07/06-from.dockerfile`](extracted/ch07/06-from.dockerfile) | dockerfile | 6 | [line 1539](../docs/02-containers/ch07-docker-fundamentals.md) |
| 7 — Docker Fundamentals | [`ch07/07-from-node-22.dockerfile`](extracted/ch07/07-from-node-22.dockerfile) | dockerfile | 13 | [line 1586](../docs/02-containers/ch07-docker-fundamentals.md) |
| 8 — Docker Deep Dive + Production | [`ch08/01-from-node-22.dockerfile`](extracted/ch08/01-from-node-22.dockerfile) | dockerfile | 13 | [line 82](../docs/02-containers/ch08-docker-production.md) |
| 8 — Docker Deep Dive + Production | [`ch08/02-from-node-22-as-builder.dockerfile`](extracted/ch08/02-from-node-22-as-builder.dockerfile) | dockerfile | 27 | [line 163](../docs/02-containers/ch08-docker-production.md) |
| 8 — Docker Deep Dive + Production | [`ch08/03-from-node-22-slim.dockerfile`](extracted/ch08/03-from-node-22-slim.dockerfile) | dockerfile | 14 | [line 445](../docs/02-containers/ch08-docker-production.md) |
| 8 — Docker Deep Dive + Production | [`ch08/04-app-get-health-req-res.ts`](extracted/ch08/04-app-get-health-req-res.ts) | typescript | 5 | [line 525](../docs/02-containers/ch08-docker-production.md) |
| 8 — Docker Deep Dive + Production | [`ch08/05-healthcheck.dockerfile`](extracted/ch08/05-healthcheck.dockerfile) | dockerfile | 6 | [line 537](../docs/02-containers/ch08-docker-production.md) |
| 8 — Docker Deep Dive + Production | [`ch08/06-services.yaml`](extracted/ch08/06-services.yaml) | yaml | 27 | [line 757](../docs/02-containers/ch08-docker-production.md) |
| 8 — Docker Deep Dive + Production | [`ch08/07-from-node-22-as-builder.dockerfile`](extracted/ch08/07-from-node-22-as-builder.dockerfile) | dockerfile | 32 | [line 1203](../docs/02-containers/ch08-docker-production.md) |
| 9 — AWS Fundamentals + IAM | [`ch09/01-block.json`](extracted/ch09/01-block.json) | json | 12 | [line 498](../docs/04-aws/ch09-aws-fundamentals-iam.md) |
| 9 — AWS Fundamentals + IAM | [`ch09/02-import-s3client-from-aws-sdk-cli.ts`](extracted/ch09/02-import-s3client-from-aws-sdk-cli.ts) | typescript | 5 | [line 811](../docs/04-aws/ch09-aws-fundamentals-iam.md) |
| 9 — AWS Fundamentals + IAM | [`ch09/03-block.json`](extracted/ch09/03-block.json) | json | 10 | [line 1378](../docs/04-aws/ch09-aws-fundamentals-iam.md) |
| 11 — S3 + AWS Storage | [`ch11/01-block.json`](extracted/ch11/01-block.json) | json | 13 | [line 546](../docs/04-aws/ch11-s3-storage.md) |
| 11 — S3 + AWS Storage | [`ch11/02-import-s3client-from-aws-sdk-cli.ts`](extracted/ch11/02-import-s3client-from-aws-sdk-cli.ts) | typescript | 5 | [line 782](../docs/04-aws/ch11-s3-storage.md) |
| 11 — S3 + AWS Storage | [`ch11/03-import.ts`](extracted/ch11/03-import.ts) | typescript | 12 | [line 794](../docs/04-aws/ch11-s3-storage.md) |
| 11 — S3 + AWS Storage | [`ch11/04-import-putobjectcommand-from-aws.ts`](extracted/ch11/04-import-putobjectcommand-from-aws.ts) | typescript | 12 | [line 817](../docs/04-aws/ch11-s3-storage.md) |
| 13 — RDS + Databases on AWS | [`ch13/01-import-pool-from-pg.ts`](extracted/ch13/01-import-pool-from-pg.ts) | typescript | 9 | [line 242](../docs/04-aws/ch13-rds-databases.md) |
| 13 — RDS + Databases on AWS | [`ch13/02-const-pool-new-pool.ts`](extracted/ch13/02-const-pool-new-pool.ts) | typescript | 4 | [line 329](../docs/04-aws/ch13-rds-databases.md) |
| 13 — RDS + Databases on AWS | [`ch13/03-const-result-await-pool-query.ts`](extracted/ch13/03-const-result-await-pool-query.ts) | typescript | 4 | [line 338](../docs/04-aws/ch13-rds-databases.md) |
| 13 — RDS + Databases on AWS | [`ch13/04-db-host.env`](extracted/ch13/04-db-host.env) | env | 5 | [line 1498](../docs/04-aws/ch13-rds-databases.md) |
| 14 — Load Balancing + Scaling | [`ch14/01-app-get-health-req-res.ts`](extracted/ch14/01-app-get-health-req-res.ts) | typescript | 5 | [line 333](../docs/04-aws/ch14-load-balancing-scaling.md) |
| 15 — Lambda + Serverless + Messaging | [`ch15/01-export-const-handler-async-event.ts`](extracted/ch15/01-export-const-handler-async-event.ts) | typescript | 8 | [line 107](../docs/04-aws/ch15-lambda-serverless-messaging.md) |
| 15 — Lambda + Serverless + Messaging | [`ch15/02-app-get-hello-req-res.ts`](extracted/ch15/02-app-get-hello-req-res.ts) | typescript | 5 | [line 138](../docs/04-aws/ch15-lambda-serverless-messaging.md) |
| 15 — Lambda + Serverless + Messaging | [`ch15/03-export-const-handler-async-event.ts`](extracted/ch15/03-export-const-handler-async-event.ts) | typescript | 8 | [line 157](../docs/04-aws/ch15-lambda-serverless-messaging.md) |
| 15 — Lambda + Serverless + Messaging | [`ch15/04-import-type.ts`](extracted/ch15/04-import-type.ts) | typescript | 12 | [line 354](../docs/04-aws/ch15-lambda-serverless-messaging.md) |
| 15 — Lambda + Serverless + Messaging | [`ch15/05-block.json`](extracted/ch15/05-block.json) | json | 4 | [line 750](../docs/04-aws/ch15-lambda-serverless-messaging.md) |
| 15 — Lambda + Serverless + Messaging | [`ch15/06-await-sqs-send.ts`](extracted/ch15/06-await-sqs-send.ts) | typescript | 9 | [line 938](../docs/04-aws/ch15-lambda-serverless-messaging.md) |
| 15 — Lambda + Serverless + Messaging | [`ch15/07-export-const-handler-async-event.ts`](extracted/ch15/07-export-const-handler-async-event.ts) | typescript | 7 | [line 966](../docs/04-aws/ch15-lambda-serverless-messaging.md) |
| 15 — Lambda + Serverless + Messaging | [`ch15/08-name-deploy-lambda.yaml`](extracted/ch15/08-name-deploy-lambda.yaml) | yaml | 41 | [line 1400](../docs/04-aws/ch15-lambda-serverless-messaging.md) |
| 15 — Lambda + Serverless + Messaging | [`ch15/09-block.json`](extracted/ch15/09-block.json) | json | 4 | [line 1709](../docs/04-aws/ch15-lambda-serverless-messaging.md) |
| 16 — Route 53 + CloudFront + CDN + WAF | [`ch16/01-name-build-frontend.yaml`](extracted/ch16/01-name-build-frontend.yaml) | yaml | 8 | [line 1465](../docs/04-aws/ch16-route53-cloudfront-waf.md) |
| 17 — AWS Monitoring + Security | [`ch17/01-console-log-json-stringify.ts`](extracted/ch17/01-console-log-json-stringify.ts) | typescript | 6 | [line 279](../docs/04-aws/ch17-monitoring-security.md) |
| 17 — AWS Monitoring + Security | [`ch17/02-block.json`](extracted/ch17/02-block.json) | json | 7 | [line 698](../docs/04-aws/ch17-monitoring-security.md) |
| 17 — AWS Monitoring + Security | [`ch17/03-block.json`](extracted/ch17/03-block.json) | json | 5 | [line 712](../docs/04-aws/ch17-monitoring-security.md) |
| 17 — AWS Monitoring + Security | [`ch17/04-app-get-health-req-res.ts`](extracted/ch17/04-app-get-health-req-res.ts) | typescript | 5 | [line 1240](../docs/04-aws/ch17-monitoring-security.md) |
| 18 — Kubernetes Fundamentals | [`ch18/01-apiversion-v1.yaml`](extracted/ch18/01-apiversion-v1.yaml) | yaml | 12 | [line 519](../docs/05-kubernetes/ch18-kubernetes-fundamentals.md) |
| 18 — Kubernetes Fundamentals | [`ch18/02-apiversion-apps-v1.yaml`](extracted/ch18/02-apiversion-apps-v1.yaml) | yaml | 25 | [line 745](../docs/05-kubernetes/ch18-kubernetes-fundamentals.md) |
| 18 — Kubernetes Fundamentals | [`ch18/03-apiversion-v1.yaml`](extracted/ch18/03-apiversion-v1.yaml) | yaml | 15 | [line 959](../docs/05-kubernetes/ch18-kubernetes-fundamentals.md) |
| 18 — Kubernetes Fundamentals | [`ch18/04-apiversion-v1.yaml`](extracted/ch18/04-apiversion-v1.yaml) | yaml | 9 | [line 1221](../docs/05-kubernetes/ch18-kubernetes-fundamentals.md) |
| 19 — Kubernetes Configuration + Storage | [`ch19/01-apiversion-v1.yaml`](extracted/ch19/01-apiversion-v1.yaml) | yaml | 10 | [line 110](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) |
| 19 — Kubernetes Configuration + Storage | [`ch19/02-apiversion-apps-v1.yaml`](extracted/ch19/02-apiversion-apps-v1.yaml) | yaml | 29 | [line 147](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) |
| 19 — Kubernetes Configuration + Storage | [`ch19/03-env.yaml`](extracted/ch19/03-env.yaml) | yaml | 6 | [line 286](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) |
| 19 — Kubernetes Configuration + Storage | [`ch19/04-containers.yaml`](extracted/ch19/04-containers.yaml) | yaml | 7 | [line 403](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) |
| 19 — Kubernetes Configuration + Storage | [`ch19/05-apiversion-v1.yaml`](extracted/ch19/05-apiversion-v1.yaml) | yaml | 18 | [line 453](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) |
| 19 — Kubernetes Configuration + Storage | [`ch19/06-apiversion-v1.yaml`](extracted/ch19/06-apiversion-v1.yaml) | yaml | 13 | [line 576](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) |
| 19 — Kubernetes Configuration + Storage | [`ch19/07-apiversion-v1.yaml`](extracted/ch19/07-apiversion-v1.yaml) | yaml | 19 | [line 615](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) |
| 19 — Kubernetes Configuration + Storage | [`ch19/08-resources.yaml`](extracted/ch19/08-resources.yaml) | yaml | 4 | [line 770](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) |
| 19 — Kubernetes Configuration + Storage | [`ch19/09-resources.yaml`](extracted/ch19/09-resources.yaml) | yaml | 4 | [line 785](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) |
| 19 — Kubernetes Configuration + Storage | [`ch19/10-resources.yaml`](extracted/ch19/10-resources.yaml) | yaml | 8 | [line 796](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) |
| 19 — Kubernetes Configuration + Storage | [`ch19/11-livenessprobe.yaml`](extracted/ch19/11-livenessprobe.yaml) | yaml | 7 | [line 871](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) |
| 19 — Kubernetes Configuration + Storage | [`ch19/12-readinessprobe.yaml`](extracted/ch19/12-readinessprobe.yaml) | yaml | 7 | [line 893](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) |
| 19 — Kubernetes Configuration + Storage | [`ch19/13-apiversion-v1.yaml`](extracted/ch19/13-apiversion-v1.yaml) | yaml | 9 | [line 975](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) |
| 19 — Kubernetes Configuration + Storage | [`ch19/14-apiversion-apps-v1.yaml`](extracted/ch19/14-apiversion-apps-v1.yaml) | yaml | 67 | [line 1003](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) |
| 19 — Kubernetes Configuration + Storage | [`ch19/15-apiversion-v1.yaml`](extracted/ch19/15-apiversion-v1.yaml) | yaml | 18 | [line 1393](../docs/05-kubernetes/ch19-kubernetes-config-storage.md) |
| 20 — Kubernetes Networking + Scaling + Production | [`ch20/01-apiversion-v1.yaml`](extracted/ch20/01-apiversion-v1.yaml) | yaml | 13 | [line 141](../docs/05-kubernetes/ch20-kubernetes-networking-scaling.md) |
| 20 — Kubernetes Networking + Scaling + Production | [`ch20/02-rules.yaml`](extracted/ch20/02-rules.yaml) | yaml | 6 | [line 366](../docs/05-kubernetes/ch20-kubernetes-networking-scaling.md) |
| 20 — Kubernetes Networking + Scaling + Production | [`ch20/03-apiversion-networking-k8s-io-v1.yaml`](extracted/ch20/03-apiversion-networking-k8s-io-v1.yaml) | yaml | 19 | [line 577](../docs/05-kubernetes/ch20-kubernetes-networking-scaling.md) |
| 20 — Kubernetes Networking + Scaling + Production | [`ch20/04-apiversion-autoscaling-v2.yaml`](extracted/ch20/04-apiversion-autoscaling-v2.yaml) | yaml | 22 | [line 728](../docs/05-kubernetes/ch20-kubernetes-networking-scaling.md) |
| 20 — Kubernetes Networking + Scaling + Production | [`ch20/05-resources.yaml`](extracted/ch20/05-resources.yaml) | yaml | 8 | [line 899](../docs/05-kubernetes/ch20-kubernetes-networking-scaling.md) |
| 20 — Kubernetes Networking + Scaling + Production | [`ch20/06-console-log-json-stringify.ts`](extracted/ch20/06-console-log-json-stringify.ts) | ts | 5 | [line 1196](../docs/05-kubernetes/ch20-kubernetes-networking-scaling.md) |
| 21 — Terraform: Infrastructure as Code | [`ch21/01-terraform.tf`](extracted/ch21/01-terraform.tf) | hcl | 12 | [line 234](../docs/06-iac-config/ch21-terraform.md) |
| 21 — Terraform: Infrastructure as Code | [`ch21/02-variable-aws-region.tf`](extracted/ch21/02-variable-aws-region.tf) | hcl | 4 | [line 651](../docs/06-iac-config/ch21-terraform.md) |
| 21 — Terraform: Infrastructure as Code | [`ch21/03-string.tf`](extracted/ch21/03-string.tf) | hcl | 7 | [line 704](../docs/06-iac-config/ch21-terraform.md) |
| 21 — Terraform: Infrastructure as Code | [`ch21/04-variable-instance-count.tf`](extracted/ch21/04-variable-instance-count.tf) | hcl | 4 | [line 716](../docs/06-iac-config/ch21-terraform.md) |
| 21 — Terraform: Infrastructure as Code | [`ch21/05-resource-aws-instance-app.tf`](extracted/ch21/05-resource-aws-instance-app.tf) | hcl | 8 | [line 843](../docs/06-iac-config/ch21-terraform.md) |
| 21 — Terraform: Infrastructure as Code | [`ch21/06-locals.tf`](extracted/ch21/06-locals.tf) | hcl | 4 | [line 912](../docs/06-iac-config/ch21-terraform.md) |
| 21 — Terraform: Infrastructure as Code | [`ch21/07-tags.tf`](extracted/ch21/07-tags.tf) | hcl | 4 | [line 921](../docs/06-iac-config/ch21-terraform.md) |
| 21 — Terraform: Infrastructure as Code | [`ch21/08-module-network.tf`](extracted/ch21/08-module-network.tf) | hcl | 5 | [line 994](../docs/06-iac-config/ch21-terraform.md) |
| 21 — Terraform: Infrastructure as Code | [`ch21/09-name-terraform.yaml`](extracted/ch21/09-name-terraform.yaml) | yaml | 34 | [line 1280](../docs/06-iac-config/ch21-terraform.md) |
| 22 — Observability + Reliability | [`ch22/01-block.json`](extracted/ch22/01-block.json) | json | 6 | [line 88](../docs/07-observability-sre/ch22-observability-reliability.md) |
| 22 — Observability + Reliability | [`ch22/02-console-log-json-stringify.ts`](extracted/ch22/02-console-log-json-stringify.ts) | ts | 6 | [line 225](../docs/07-observability-sre/ch22-observability-reliability.md) |
| 22 — Observability + Reliability | [`ch22/03-console-log-json-stringify.ts`](extracted/ch22/03-console-log-json-stringify.ts) | ts | 9 | [line 242](../docs/07-observability-sre/ch22-observability-reliability.md) |
| 22 — Observability + Reliability | [`ch22/04-import-client-from-prom-client.ts`](extracted/ch22/04-import-client-from-prom-client.ts) | ts | 8 | [line 515](../docs/07-observability-sre/ch22-observability-reliability.md) |
| 22 — Observability + Reliability | [`ch22/05-process-on-sigterm-async.ts`](extracted/ch22/05-process-on-sigterm-async.ts) | ts | 9 | [line 1298](../docs/07-observability-sre/ch22-observability-reliability.md) |
| 22 — Observability + Reliability | [`ch22/06-app-get-health-req-res.ts`](extracted/ch22/06-app-get-health-req-res.ts) | ts | 5 | [line 1423](../docs/07-observability-sre/ch22-observability-reliability.md) |
| 22 — Observability + Reliability | [`ch22/07-app-get-ready-async-req-res.ts`](extracted/ch22/07-app-get-ready-async-req-res.ts) | ts | 13 | [line 1441](../docs/07-observability-sre/ch22-observability-reliability.md) |
| 22 — Observability + Reliability | [`ch22/08-import-client-from-prom-client.ts`](extracted/ch22/08-import-client-from-prom-client.ts) | ts | 9 | [line 1465](../docs/07-observability-sre/ch22-observability-reliability.md) |
| 23 — Production Architecture + Troubleshooting | [`ch23/01-from-node-22-as-build.dockerfile`](extracted/ch23/01-from-node-22-as-build.dockerfile) | dockerfile | 25 | [line 721](../docs/08-production/ch23-production-architecture-troubleshooting.md) |
| 23 — Production Architecture + Troubleshooting | [`ch23/02-block.json`](extracted/ch23/02-block.json) | json | 9 | [line 945](../docs/08-production/ch23-production-architecture-troubleshooting.md) |
| 24 — Complete Cloud + DevOps Interview & OA Mastery | [`ch24/01-set-euo-pipefail.sh`](extracted/ch24/01-set-euo-pipefail.sh) | bash | 10 | [line 245](../docs/09-interview/ch24-interview-oa-mastery.md) |
| 24 — Complete Cloud + DevOps Interview & OA Mastery | [`ch24/02-git-status.sh`](extracted/ch24/02-git-status.sh) | bash | 17 | [line 493](../docs/09-interview/ch24-interview-oa-mastery.md) |
| 24 — Complete Cloud + DevOps Interview & OA Mastery | [`ch24/03-name-ci.yaml`](extracted/ch24/03-name-ci.yaml) | yaml | 22 | [line 621](../docs/09-interview/ch24-interview-oa-mastery.md) |
| 24 — Complete Cloud + DevOps Interview & OA Mastery | [`ch24/04-from.dockerfile`](extracted/ch24/04-from.dockerfile) | dockerfile | 9 | [line 672](../docs/09-interview/ch24-interview-oa-mastery.md) |
| 24 — Complete Cloud + DevOps Interview & OA Mastery | [`ch24/05-from-node-22-as-build.dockerfile`](extracted/ch24/05-from-node-22-as-build.dockerfile) | dockerfile | 24 | [line 712](../docs/09-interview/ch24-interview-oa-mastery.md) |
| 25 — Helm: Kubernetes Package Management | [`ch25/01-apiversion-v2.yaml`](extracted/ch25/01-apiversion-v2.yaml) | yaml | 6 | [line 238](../docs/05-kubernetes/ch25-helm.md) |
| 25 — Helm: Kubernetes Package Management | [`ch25/02-replicacount-2.yaml`](extracted/ch25/02-replicacount-2.yaml) | yaml | 19 | [line 275](../docs/05-kubernetes/ch25-helm.md) |
| 25 — Helm: Kubernetes Package Management | [`ch25/03-apiversion-apps-v1.yaml`](extracted/ch25/03-apiversion-apps-v1.yaml) | yaml | 29 | [line 395](../docs/05-kubernetes/ch25-helm.md) |
| 25 — Helm: Kubernetes Package Management | [`ch25/04-replicacount-2.yaml`](extracted/ch25/04-replicacount-2.yaml) | yaml | 5 | [line 582](../docs/05-kubernetes/ch25-helm.md) |
| 25 — Helm: Kubernetes Package Management | [`ch25/05-replicacount-4.yaml`](extracted/ch25/05-replicacount-4.yaml) | yaml | 11 | [line 1032](../docs/05-kubernetes/ch25-helm.md) |
| 25 — Helm: Kubernetes Package Management | [`ch25/06-helm-create.sh`](extracted/ch25/06-helm-create.sh) | bash | 13 | [line 1587](../docs/05-kubernetes/ch25-helm.md) |
| 26 — GitOps + ArgoCD | [`ch26/01-apiversion-argoproj-io-v1alpha1.yaml`](extracted/ch26/01-apiversion-argoproj-io-v1alpha1.yaml) | yaml | 20 | [line 535](../docs/03-cicd-gitops/ch26-gitops-argocd.md) |
| 26 — GitOps + ArgoCD | [`ch26/02-source.yaml`](extracted/ch26/02-source.yaml) | yaml | 4 | [line 578](../docs/03-cicd-gitops/ch26-gitops-argocd.md) |
| 27 — Jenkins + Advanced CI/CD | [`ch27/01-pipeline.jenkinsfile`](extracted/ch27/01-pipeline.jenkinsfile) | groovy | 30 | [line 240](../docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md) |
| 27 — Jenkins + Advanced CI/CD | [`ch27/02-pipeline.jenkinsfile`](extracted/ch27/02-pipeline.jenkinsfile) | groovy | 15 | [line 283](../docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md) |
| 27 — Jenkins + Advanced CI/CD | [`ch27/03-withcredentials.jenkinsfile`](extracted/ch27/03-withcredentials.jenkinsfile) | groovy | 8 | [line 385](../docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md) |
| 27 — Jenkins + Advanced CI/CD | [`ch27/04-pipeline.jenkinsfile`](extracted/ch27/04-pipeline.jenkinsfile) | groovy | 43 | [line 474](../docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md) |
| 27 — Jenkins + Advanced CI/CD | [`ch27/05-post.jenkinsfile`](extracted/ch27/05-post.jenkinsfile) | groovy | 13 | [line 530](../docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md) |
| 27 — Jenkins + Advanced CI/CD | [`ch27/06-post.jenkinsfile`](extracted/ch27/06-post.jenkinsfile) | groovy | 6 | [line 569](../docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md) |
| 27 — Jenkins + Advanced CI/CD | [`ch27/07-stage-docker-build.jenkinsfile`](extracted/ch27/07-stage-docker-build.jenkinsfile) | groovy | 5 | [line 632](../docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md) |
| 27 — Jenkins + Advanced CI/CD | [`ch27/08-stage-docker-push.jenkinsfile`](extracted/ch27/08-stage-docker-push.jenkinsfile) | groovy | 5 | [line 642](../docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md) |
| 27 — Jenkins + Advanced CI/CD | [`ch27/09-stage-deploy.jenkinsfile`](extracted/ch27/09-stage-deploy.jenkinsfile) | groovy | 8 | [line 713](../docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md) |
| 27 — Jenkins + Advanced CI/CD | [`ch27/10-pipeline.jenkinsfile`](extracted/ch27/10-pipeline.jenkinsfile) | groovy | 42 | [line 1153](../docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md) |
| 27 — Jenkins + Advanced CI/CD | [`ch27/11-pipeline.jenkinsfile`](extracted/ch27/11-pipeline.jenkinsfile) | groovy | 25 | [line 1511](../docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md) |
| 27 — Jenkins + Advanced CI/CD | [`ch27/12-stage-docker-build.jenkinsfile`](extracted/ch27/12-stage-docker-build.jenkinsfile) | groovy | 5 | [line 1573](../docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/01-web.ini`](extracted/ch28/01-web.ini) | ini | 6 | [line 339](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/02-name-install-nginx.yaml`](extracted/ch28/02-name-install-nginx.yaml) | yaml | 4 | [line 429](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/03-name-install-nginx.yaml`](extracted/ch28/03-name-install-nginx.yaml) | yaml | 4 | [line 448](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/04-block.yaml`](extracted/ch28/04-block.yaml) | yaml | 19 | [line 503](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/05-tasks.yaml`](extracted/ch28/05-tasks.yaml) | yaml | 6 | [line 583](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/06-name-start-nginx.yaml`](extracted/ch28/06-name-start-nginx.yaml) | yaml | 4 | [line 594](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/07-block.yaml`](extracted/ch28/07-block.yaml) | yaml | 26 | [line 623](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/08-name-copy-nginx-configuration.yaml`](extracted/ch28/08-name-copy-nginx-configuration.yaml) | yaml | 4 | [line 666](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/09-name-create-application-director.yaml`](extracted/ch28/09-name-create-application-director.yaml) | yaml | 7 | [line 690](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/10-name-create-application-user.yaml`](extracted/ch28/10-name-create-application-user.yaml) | yaml | 5 | [line 706](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/11-name-start-api.yaml`](extracted/ch28/11-name-start-api.yaml) | yaml | 5 | [line 722](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/12-name-configure-application.yaml`](extracted/ch28/12-name-configure-application.yaml) | yaml | 4 | [line 755](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/13-tasks.yaml`](extracted/ch28/13-tasks.yaml) | yaml | 14 | [line 816](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/14-name-install-package-on-debian.yaml`](extracted/ch28/14-name-install-package-on-debian.yaml) | yaml | 5 | [line 855](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/15-name-install-packages.yaml`](extracted/ch28/15-name-install-packages.yaml) | yaml | 8 | [line 871](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/16-name-install-nginx.yaml`](extracted/ch28/16-name-install-nginx.yaml) | yaml | 6 | [line 890](../docs/06-iac-config/ch28-ansible.md) |
| 28 — Ansible: Configuration Management & Automation | [`ch28/17-block.yaml`](extracted/ch28/17-block.yaml) | yaml | 36 | [line 1278](../docs/06-iac-config/ch28-ansible.md) |
| 29 — Kubernetes CRDs + Operators | [`ch29/01-apiversion-databases-example-com.yaml`](extracted/ch29/01-apiversion-databases-example-com.yaml) | yaml | 9 | [line 197](../docs/05-kubernetes/ch29-crds-operators.md) |
| 29 — Kubernetes CRDs + Operators | [`ch29/02-apiversion-apiextensions-k8s-io-.yaml`](extracted/ch29/02-apiversion-apiextensions-k8s-io-.yaml) | yaml | 40 | [line 453](../docs/05-kubernetes/ch29-crds-operators.md) |
| 29 — Kubernetes CRDs + Operators | [`ch29/03-apiversion-platform-example-com-.yaml`](extracted/ch29/03-apiversion-platform-example-com-.yaml) | yaml | 9 | [line 546](../docs/05-kubernetes/ch29-crds-operators.md) |
| 29 — Kubernetes CRDs + Operators | [`ch29/04-apiversion-database-example-com-.yaml`](extracted/ch29/04-apiversion-database-example-com-.yaml) | yaml | 10 | [line 778](../docs/05-kubernetes/ch29-crds-operators.md) |
| 29 — Kubernetes CRDs + Operators | [`ch29/05-replicas.yaml`](extracted/ch29/05-replicas.yaml) | yaml | 4 | [line 841](../docs/05-kubernetes/ch29-crds-operators.md) |
| 29 — Kubernetes CRDs + Operators | [`ch29/06-status.yaml`](extracted/ch29/06-status.yaml) | yaml | 4 | [line 951](../docs/05-kubernetes/ch29-crds-operators.md) |
| 29 — Kubernetes CRDs + Operators | [`ch29/07-kind-kafka.yaml`](extracted/ch29/07-kind-kafka.yaml) | yaml | 5 | [line 1448](../docs/05-kubernetes/ch29-crds-operators.md) |
| 30 — Service Mesh + Istio | [`ch30/01-fetchwithretry.ts`](extracted/ch30/01-fetchwithretry.ts) | typescript | 5 | [line 54](../docs/05-kubernetes/ch30-service-mesh-istio.md) |
| 30 — Service Mesh + Istio | [`ch30/02-apiversion-networking-istio-io-v.yaml`](extracted/ch30/02-apiversion-networking-istio-io-v.yaml) | yaml | 21 | [line 461](../docs/05-kubernetes/ch30-service-mesh-istio.md) |
| 30 — Service Mesh + Istio | [`ch30/03-spec.yaml`](extracted/ch30/03-spec.yaml) | yaml | 10 | [line 506](../docs/05-kubernetes/ch30-service-mesh-istio.md) |
| 31 — Advanced Amazon EKS | [`ch31/01-block.json`](extracted/ch31/01-block.json) | json | 7 | [line 877](../docs/05-kubernetes/ch31-advanced-eks.md) |
| 31 — Advanced Amazon EKS | [`ch31/02-apiversion-v1.yaml`](extracted/ch31/02-apiversion-v1.yaml) | yaml | 6 | [line 895](../docs/05-kubernetes/ch31-advanced-eks.md) |
| 31 — Advanced Amazon EKS | [`ch31/03-spec.yaml`](extracted/ch31/03-spec.yaml) | yaml | 4 | [line 906](../docs/05-kubernetes/ch31-advanced-eks.md) |
| 31 — Advanced Amazon EKS | [`ch31/04-resources.yaml`](extracted/ch31/04-resources.yaml) | yaml | 8 | [line 1592](../docs/05-kubernetes/ch31-advanced-eks.md) |
| 31 — Advanced Amazon EKS | [`ch31/05-block.json`](extracted/ch31/05-block.json) | json | 6 | [line 1958](../docs/05-kubernetes/ch31-advanced-eks.md) |
| 32 — Advanced Terraform | [`ch32/01-tfstate.gitignore`](extracted/ch32/01-tfstate.gitignore) | gitignore | 4 | [line 171](../docs/06-iac-config/ch32-advanced-terraform.md) |
| 32 — Advanced Terraform | [`ch32/02-terraform.gitignore`](extracted/ch32/02-terraform.gitignore) | gitignore | 4 | [line 186](../docs/06-iac-config/ch32-advanced-terraform.md) |
| 32 — Advanced Terraform | [`ch32/03-terraform.tf`](extracted/ch32/03-terraform.tf) | hcl | 7 | [line 330](../docs/06-iac-config/ch32-advanced-terraform.md) |
| 32 — Advanced Terraform | [`ch32/04-module-network.tf`](extracted/ch32/04-module-network.tf) | hcl | 5 | [line 762](../docs/06-iac-config/ch32-advanced-terraform.md) |
| 32 — Advanced Terraform | [`ch32/05-module-vpc.tf`](extracted/ch32/05-module-vpc.tf) | hcl | 6 | [line 819](../docs/06-iac-config/ch32-advanced-terraform.md) |
| 32 — Advanced Terraform | [`ch32/06-variable-environment.tf`](extracted/ch32/06-variable-environment.tf) | hcl | 7 | [line 1037](../docs/06-iac-config/ch32-advanced-terraform.md) |
| 32 — Advanced Terraform | [`ch32/07-variable-db-password.tf`](extracted/ch32/07-variable-db-password.tf) | hcl | 4 | [line 1062](../docs/06-iac-config/ch32-advanced-terraform.md) |
| 32 — Advanced Terraform | [`ch32/08-lifecycle.tf`](extracted/ch32/08-lifecycle.tf) | hcl | 5 | [line 1315](../docs/06-iac-config/ch32-advanced-terraform.md) |
| 32 — Advanced Terraform | [`ch32/09-name-terraform.yaml`](extracted/ch32/09-name-terraform.yaml) | yaml | 21 | [line 1431](../docs/06-iac-config/ch32-advanced-terraform.md) |
| 32 — Advanced Terraform | [`ch32/10-terraform.tf`](extracted/ch32/10-terraform.tf) | hcl | 8 | [line 1570](../docs/06-iac-config/ch32-advanced-terraform.md) |
| 32 — Advanced Terraform | [`ch32/11-resource-helm-release-app.tf`](extracted/ch32/11-resource-helm-release-app.tf) | hcl | 5 | [line 1784](../docs/06-iac-config/ch32-advanced-terraform.md) |
| 32 — Advanced Terraform | [`ch32/12-moved.tf`](extracted/ch32/12-moved.tf) | hcl | 4 | [line 2475](../docs/06-iac-config/ch32-advanced-terraform.md) |
| 32 — Advanced Terraform | [`ch32/13-for-each.tf`](extracted/ch32/13-for-each.tf) | hcl | 4 | [line 2512](../docs/06-iac-config/ch32-advanced-terraform.md) |
| 32 — Advanced Terraform | [`ch32/14-tags.tf`](extracted/ch32/14-tags.tf) | hcl | 5 | [line 2625](../docs/06-iac-config/ch32-advanced-terraform.md) |
| 33 — Advanced AWS for Backend Engineers | [`ch33/01-block.json`](extracted/ch33/01-block.json) | json | 5 | [line 732](../docs/04-aws/ch33-advanced-aws-backend.md) |
| 33 — Advanced AWS for Backend Engineers | [`ch33/02-const-cached-await-redis-get-key.ts`](extracted/ch33/02-const-cached-await-redis-get-key.ts) | typescript | 17 | [line 1068](../docs/04-aws/ch33-advanced-aws-backend.md) |
| 34 — Advanced SRE | [`ch34/01-process-on-sigterm-async.ts`](extracted/ch34/01-process-on-sigterm-async.ts) | typescript | 7 | [line 2694](../docs/07-observability-sre/ch34-advanced-sre.md) |
| 34 — Advanced SRE | [`ch34/02-resources.yaml`](extracted/ch34/02-resources.yaml) | yaml | 8 | [line 2970](../docs/07-observability-sre/ch34-advanced-sre.md) |
| 35 — DevOps Capstone: Build a Production-Grade Backend Platform | [`ch35/01-block.json`](extracted/ch35/01-block.json) | json | 5 | [line 669](../docs/08-production/ch35-devops-capstone.md) |
| 35 — DevOps Capstone: Build a Production-Grade Backend Platform | [`ch35/02-from-node-22-alpine-as-builder.dockerfile`](extracted/ch35/02-from-node-22-alpine-as-builder.dockerfile) | dockerfile | 26 | [line 866](../docs/08-production/ch35-devops-capstone.md) |
| 35 — DevOps Capstone: Build a Production-Grade Backend Platform | [`ch35/03-node-env-development.env`](extracted/ch35/03-node-env-development.env) | env | 10 | [line 974](../docs/08-production/ch35-devops-capstone.md) |
| 35 — DevOps Capstone: Build a Production-Grade Backend Platform | [`ch35/04-apiversion-apps-v1.yaml`](extracted/ch35/04-apiversion-apps-v1.yaml) | yaml | 34 | [line 1137](../docs/08-production/ch35-devops-capstone.md) |
| 35 — DevOps Capstone: Build a Production-Grade Backend Platform | [`ch35/05-apiversion-v1.yaml`](extracted/ch35/05-apiversion-v1.yaml) | yaml | 13 | [line 1194](../docs/08-production/ch35-devops-capstone.md) |
| 35 — DevOps Capstone: Build a Production-Grade Backend Platform | [`ch35/06-readinessprobe.yaml`](extracted/ch35/06-readinessprobe.yaml) | yaml | 7 | [line 1216](../docs/08-production/ch35-devops-capstone.md) |
| 35 — DevOps Capstone: Build a Production-Grade Backend Platform | [`ch35/07-livenessprobe.yaml`](extracted/ch35/07-livenessprobe.yaml) | yaml | 6 | [line 1238](../docs/08-production/ch35-devops-capstone.md) |
| 35 — DevOps Capstone: Build a Production-Grade Backend Platform | [`ch35/08-block.json`](extracted/ch35/08-block.json) | json | 8 | [line 2066](../docs/08-production/ch35-devops-capstone.md) |
