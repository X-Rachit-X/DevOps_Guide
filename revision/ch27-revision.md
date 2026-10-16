# Chapter 27 — Revision Sheet: Jenkins + Advanced CI/CD

> Supplements [the full chapter](../docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md). Key idea: **Jenkins is a general-purpose automation server that can implement CI/CD pipelines through code.**

## Why Jenkins

Coordinates Git repositories → build servers → testing → Docker → artifact repositories → Kubernetes → AWS. Extremely popular before cloud-native CI such as GitHub Actions; still common in **large enterprises, legacy systems, organisations with custom CI/CD infrastructure, highly customised pipelines**.

| GitHub Actions | Jenkins |
|---|---|
| GitHub → Actions → Runner → Pipeline (integrated, hosted runners) | Git repo → Jenkins → Controller → Agents → Pipeline; **infrastructure-oriented** — you manage the installation, agents, plugins, credentials |

## Architecture

- **Controller**: coordinates Jenkins — jobs, pipelines, configuration, scheduling, credentials, agents. **Agent**: actually executes work (`npm ci`, `npm test`, `docker build`). Agents may be Linux, Docker, Windows; separate Node/Java/Android agents isolate workloads.
- **Don't build everything on the controller** — builds consume CPU/memory/disk/network; the controller should schedule/orchestrate and agents execute.
- **Agents in Kubernetes:** Jenkins → Kubernetes → **ephemeral build Pods** created when needed and removed afterwards → isolation, elasticity, clean environments, scaling (your Kubernetes troubleshooting applies: `kubectl get pods / describe / logs`).

## Jenkinsfile (Declarative Pipeline)

```groovy
pipeline {
    agent any                     // or: agent { label 'docker' }
    environment { NODE_ENV = 'test' }
    stages {
        stage('Checkout')  { steps { checkout scm } }
        stage('Install')   { steps { sh 'npm ci' } }
        stage('Lint')      { steps { sh 'npm run lint' } }
        stage('Typecheck') { steps { sh 'npm run typecheck' } }
        stage('Test')      { steps { sh 'npm test' } }
        stage('Build')     { steps { sh 'npm run build' } }
    }
    post {
        always  { echo 'Pipeline finished' }
        success { archiveArtifacts artifacts: 'dist/**', fingerprint: true }
        failure { echo 'Build failed' }
    }
}
```
Structure: `pipeline → agent → stages → stage → steps`. `Jenkinsfile` lives in the repo (**pipeline as code**). `post` blocks (`always`/`success`/`failure`) handle notifications, cleanup, artifact handling, reporting. **Artifacts** (`archiveArtifacts`) preserve build output (`dist/`) and tie it to a build — traceability: build #100/#101/#102 ↔ which binary/image (same principle as Git SHA / image tags / ECR).

## Credentials, Git, webhooks

- **Credentials store** holds AWS credentials, SSH keys, tokens, passwords, API keys; inject with `withCredentials([string(credentialsId: 'api-token', variable: 'API_TOKEN')]) { sh 'some-command' }`. Secret → Jenkins credential store → pipeline; **never** secret → Git, and don't put secrets directly in Jenkinsfiles/env blocks.
- Git integrations: GitHub, GitLab, Bitbucket, self-hosted Git. Flow: `git push` → GitHub → **webhook** (HTTP request to Jenkins) → pipeline starts (better than constantly polling Git).

## Docker, ECR, Kubernetes

```groovy
stage('Docker Build') { steps { sh 'docker build -t my-api:${BUILD_NUMBER} .' } }
stage('Docker Push')  { steps { sh 'docker push my-api:${BUILD_NUMBER}' } }
```
Production: authenticate securely to the registry and use an immutable tag (Git SHA).
```bash
aws ecr get-login-password --region ap-south-1 | \
  docker login --username AWS --password-stdin <account>.dkr.ecr.ap-south-1.amazonaws.com
docker build -t <repository>:<git-sha> .
docker push   <repository>:<git-sha>
```
Prefer short-lived identity/role-based credentials over permanent access keys.
Deploy (traditional): `kubectl set image deployment/my-api my-api=my-api:${GIT_COMMIT}` — or `kubectl apply -f k8s/`. **GitOps alternative (cleaner separation):** Jenkins → build → test → Docker → ECR → **update GitOps repo** → ArgoCD → EKS. Jenkins = CI (build, test, package, image); ArgoCD = CD (synchronisation, reconciliation, deployment).

| Tool | Primary role |
|---|---|
| GitHub Actions | CI/CD automation integrated with GitHub |
| Jenkins | General-purpose CI/CD automation server |
| ArgoCD | Kubernetes GitOps CD |
| Helm | Kubernetes packaging/templates |
| Terraform | Infrastructure as Code |

They coexist: GitHub → Jenkins (test, build, Docker) → ECR → GitOps repo → ArgoCD → EKS.

## Pipeline features

- **Plugins:** huge ecosystem (Git, Docker, Kubernetes, AWS, Slack, JUnit, SonarQube, security scanners) — powerful but can become complicated.
- **Parallelism:** independent stages (Unit ∥ Lint ∥ Security) → sequential 5 + 2 + 4 = **11 min**, parallel `max(5,2,4)` ≈ **5 min** (given enough agents/resources).
- **Parameters:** e.g. `ENVIRONMENT` (dev/staging/production) — but production deployment should have stronger controls than arbitrary user input.
- **Approvals / governance:** Commit → CI → Tests → Build → Staging → Integration tests → **Approval** → Production (GitHub Actions has environments/approvals; Jenkins can implement approval steps).

## Security (very testable)

- **Don't:** hard-code AWS keys/passwords, run everything as root, allow unrestricted Jenkins access, install random plugins.
- **Do:** RBAC, least privilege, credential store, HTTPS, authentication + authorization, plugin updates, agent isolation, audit logs, network restrictions, secret rotation.
- **Supply-chain:** the CI server has enormous privileges (push images, deploy to Kubernetes, access AWS) → if compromised: attacker → Jenkins → AWS → Kubernetes. Use least privilege, short-lived credentials, isolated agents, protected branches, dependency scanning, image scanning, signed artifacts where appropriate.
- **Jenkins credentials vs GitHub OIDC:** Jenkins + long-lived AWS key vs Jenkins workload identity → IAM role → temporary credentials (depends on where Jenkins runs). Principle: avoid unnecessary long-lived credentials.

## Troubleshooting

- **Pipeline suddenly fails:** don't rerun repeatedly; which stage? (Build / Test / Docker / Registry / Credentials / Deployment). *Docker push failed:* ECR reachable? credentials valid? repository exists? image tag valid? permissions?
- **Agent offline:** network, agent process, resource exhaustion, disk, credentials, Jenkins-agent connection, container/node status.
- **Disk full:** workspace, Docker images, build artifacts, logs, cache → `df -h`, `du -sh *`; clean old builds, remove unused Docker images, artifact retention, workspace cleanup, log rotation, bigger disk.

## Best practices

Pipeline as code (`Jenkinsfile`) · small stages (test, build, scan, package, deploy) · immutable artifacts (Git SHA / build number / version, not blind `latest`) · fail fast · least privilege · reproducible builds.

## Interview answer — "Why Jenkins when GitHub Actions exists?"

Don't say one is universally better. *GitHub Actions is tightly integrated CI/CD for GitHub repositories (runners, workflows, permissions and events integrated). Jenkins is a mature, highly extensible automation server with a large plugin ecosystem that integrates with many source-control systems and internal infrastructure; organisations with existing Jenkins or highly customised pipelines may continue using it.* Personal new project → GitHub Actions (simpler); enterprise → likely Jenkins, so be able to maintain its pipelines; Kubernetes GitOps → Jenkins/Actions (CI) → ArgoCD → EKS.

## Hands-on

```bash
docker volume create jenkins_home
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
docker ps ; docker logs jenkins        # learning setup, not production
```
Repo `my-api/{package.json, src/, Jenkinsfile}` (Install → Test → Build); connect Jenkins to the repo; push → webhook → pipeline. Add `Docker Build` (`docker build -t my-api:${BUILD_NUMBER} .`), later ECR.

## Depth guide

Deep enough: architecture, controller, agents, Jenkinsfile, declarative pipelines, stages/steps, environment variables, credentials, artifacts, webhooks, Docker integration, CI/CD flow, pipeline security, Jenkins + Kubernetes, Jenkins + GitOps. Awareness: Blue Ocean, Shared Libraries, Kubernetes plugin internals, plugin development, distributed architecture internals.

**Three CI/CD styles:** basic automation (Git → Jenkins → build/test/deploy), cloud-native CI (GitHub → Actions → Docker → ECR → Kubernetes), modern GitOps (Git → Actions/Jenkins → build/test → Docker → ECR → GitOps repo → ArgoCD → Kubernetes/EKS).

## Added (see supplement in the chapter)

Declarative syntax for `parallel`, `parameters`, `when`, `input`, `options`, `triggers`; scripted vs declarative; Docker CLI availability in agents and the Docker-socket risk; webhook endpoint; initial admin password; multibranch pipelines; Shared Libraries.

<!-- NAV -->

---

← [Sheet 26](ch26-revision.md) · [Full chapter 27](../docs/03-cicd-gitops/ch27-jenkins-advanced-cicd.md) · [All revision material](README.md) · [Sheet 28](ch28-revision.md) →
