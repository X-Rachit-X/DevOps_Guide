# Chapter 27 — Jenkins + Advanced CI/CD

> **Source:** Response 27 of the original conversation (`source-archive/src-27.txt`, lines 1–1728) · **Part II — Advanced extension (Responses 25–36)**  
> **Study aids:** [Revision sheet](../../revision/ch27-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md) · *includes an editorial supplement at the end*

<!-- SOURCE-BEGIN -->

You've already learned GitHub Actions in depth. So the goal of this response is **not to relearn CI/CD**.

Instead, we're going to understand:

- Why Jenkins exists
- Jenkins architecture
- Controllers and agents
- Jenkinsfiles
- Declarative pipelines
- Credentials
- Artifacts
- Webhooks
- Docker builds
- Deployment pipelines
- Jenkins vs GitHub Actions
- Jenkins + Docker + Kubernetes
- Jenkins + GitOps/ArgoCD
- Security
- Practical setup
- Troubleshooting
- Interview questions

The key idea:

> **Jenkins is a general-purpose automation server that can implement CI/CD pipelines through code.**

---

## 1. Why Jenkins Exists

Imagine a company has:

```text
Git repositories
     ↓
Build servers
     ↓
Testing
     ↓
Docker
     ↓
Artifact repositories
     ↓
Kubernetes
     ↓
AWS
```

They need automation.

Jenkins can coordinate:

```text
Code
 ↓
Build
 ↓
Test
 ↓
Package
 ↓
Deploy
```

Jenkins became extremely popular before newer cloud-native CI systems such as GitHub Actions became widespread.

You'll still encounter Jenkins heavily in:

- large enterprises
- legacy systems
- organizations with custom CI/CD infrastructure
- environments requiring highly customized pipelines

---

## 2. Jenkins vs GitHub Actions

You already know GitHub Actions.

Think:

#### GitHub Actions

```text
GitHub
  ↓
GitHub Actions
  ↓
Runner
  ↓
Pipeline
```

#### Jenkins

```text
Git repository
      ↓
   Jenkins
      ↓
Controller
      ↓
Agents
      ↓
Pipeline
```

Jenkins is more infrastructure-oriented.

You generally manage the Jenkins installation, agents, plugins, credentials, etc.

---

## 3. Jenkins Architecture

Basic architecture:

```text
                  Jenkins
                     │
                Controller
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
        Agent      Agent      Agent
          │          │          │
        Linux      Docker     Windows
```

The important pieces:

#### Controller

Coordinates Jenkins.

It manages things like:

```text
jobs
pipelines
configuration
scheduling
credentials
agents
```

#### Agent

Actually executes work.

For example:

```text
Agent
 ↓
npm ci
 ↓
npm test
 ↓
docker build
```

---

## 4. Why Use Agents?

Suppose you have:

```text
Node.js builds
Java builds
Android builds
Docker builds
```

You might use different agents.

```text
Controller
    │
    ├── Node Agent
    ├── Java Agent
    └── Android Agent
```

This keeps workloads isolated.

---

## 5. Jenkins Pipeline

A Jenkins pipeline defines:

```text
what should happen
and in what order
```

Example:

```text
Checkout
   ↓
Install
   ↓
Lint
   ↓
Test
   ↓
Build
   ↓
Docker
   ↓
Push
   ↓
Deploy
```

Modern Jenkins pipelines are generally written as code.

That leads to:

## Jenkinsfile

---

## 6. Jenkinsfile

A `Jenkinsfile` lives in your repository.

Example:

```groovy
pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install') {
            steps {
                sh 'npm ci'
            }
        }

        stage('Test') {
            steps {
                sh 'npm test'
            }
        }

        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }
    }
}
```

This is called a:

> **Declarative Pipeline**

---

## 7. Declarative Pipeline Structure

The basic structure:

```groovy
pipeline {

    agent any

    stages {

        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }

    }

}
```

Understand:

```text
pipeline
 ↓
agent
 ↓
stages
 ↓
stage
 ↓
steps
```

---

## 8. `agent`

Example:

```groovy
agent any
```

means Jenkins can execute the pipeline on an available agent.

You can also target specific agents/labels.

Conceptually:

```groovy
agent {
    label 'docker'
}
```

Meaning:

> Run this pipeline on an agent labeled `docker`.

---

## 9. Environment Variables

You can define:

```groovy
environment {
    NODE_ENV = 'test'
}
```

Then:

```groovy
sh 'echo $NODE_ENV'
```

Environment variables are useful for configuration.

But:

> **Don't put secrets directly into Jenkinsfiles.**

---

## 10. Jenkins Credentials

Jenkins has a credentials store.

You can store:

```text
AWS credentials
SSH keys
tokens
passwords
API keys
```

and inject them into jobs.

For example, conceptually:

```groovy
withCredentials([
    string(
        credentialsId: 'api-token',
        variable: 'API_TOKEN'
    )
]) {
    sh 'some-command'
}
```

The important security principle:

```text
Secret
 ↓
Jenkins credential store
 ↓
Pipeline
```

rather than:

```text
Secret
 ↓
Git repository ❌
```

---

## 11. Jenkins + Git

Jenkins can connect to:

```text
GitHub
GitLab
Bitbucket
self-hosted Git
```

A common flow:

```text
Developer
   ↓
git push
   ↓
GitHub
   ↓
Webhook
   ↓
Jenkins
   ↓
Pipeline
```

---

## 12. Webhooks

Suppose you push:

```bash
git push origin main
```

GitHub can send an HTTP request to Jenkins:

```text
GitHub
   │
   │ webhook
   ↓
Jenkins
   │
   ↓
Pipeline starts
```

This is better than constantly polling Git.

---

## 13. Jenkins Pipeline With Node.js

A more realistic example:

```groovy
pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install') {
            steps {
                sh 'npm ci'
            }
        }

        stage('Lint') {
            steps {
                sh 'npm run lint'
            }
        }

        stage('Typecheck') {
            steps {
                sh 'npm run typecheck'
            }
        }

        stage('Test') {
            steps {
                sh 'npm test'
            }
        }

        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }
    }
}
```

This should look familiar because you already learned the same CI concepts through GitHub Actions.

---

## 14. Post Actions

You can define behavior after pipeline execution.

Example:

```groovy
post {
    always {
        echo 'Pipeline finished'
    }

    success {
        echo 'Build succeeded'
    }

    failure {
        echo 'Build failed'
    }
}
```

This is useful for:

```text
notifications
cleanup
artifact handling
reporting
```

---

## 15. Artifacts

Suppose your build generates:

```text
dist/
```

You may want Jenkins to preserve it.

Example:

```groovy
post {
    success {
        archiveArtifacts artifacts: 'dist/**',
            fingerprint: true
    }
}
```

Now the build artifact can be associated with that Jenkins build.

---

## 16. Why Artifacts Matter

Imagine:

```text
Build #100
Build #101
Build #102
```

You want to know:

```text
Which binary/image came from which build?
```

Artifacts and immutable versioning help establish traceability.

This is the same principle we've discussed with:

```text
Git SHA
Docker image tags
ECR
```

---

## 17. Jenkins + Docker

Now let's connect Jenkins with Docker.

Pipeline:

```text
Git
 ↓
Jenkins
 ↓
Tests
 ↓
Docker build
 ↓
Docker image
 ↓
Registry
```

Example:

```groovy
stage('Docker Build') {
    steps {
        sh 'docker build -t my-api:${BUILD_NUMBER} .'
    }
}
```

Then:

```groovy
stage('Docker Push') {
    steps {
        sh 'docker push my-api:${BUILD_NUMBER}'
    }
}
```

In production you'd normally authenticate securely to your registry and use a proper immutable tag such as a Git commit SHA.

---

## 18. Jenkins + ECR

For AWS:

```text
Jenkins
 ↓
AWS credentials/role
 ↓
ECR authentication
 ↓
docker build
 ↓
docker push
 ↓
ECR
```

Conceptually:

```bash
aws ecr get-login-password \
  --region ap-south-1 |
docker login \
  --username AWS \
  --password-stdin \
  <account>.dkr.ecr.ap-south-1.amazonaws.com
```

Then:

```bash
docker build \
  -t <repository>:<git-sha> .

docker push \
  <repository>:<git-sha>
```

The exact credentials strategy depends on your Jenkins environment. Prefer short-lived identity/role-based credentials where practical instead of permanent access keys.

---

## 19. Jenkins + Kubernetes

Jenkins can deploy to Kubernetes.

Traditional model:

```text
Jenkins
   ↓
kubectl
   ↓
Kubernetes
```

For example:

```groovy
stage('Deploy') {
    steps {
        sh '''
          kubectl set image deployment/my-api \
            my-api=my-api:${GIT_COMMIT}
        '''
    }
}
```

This works.

But remember what we learned in [Chapter 26](ch26-gitops-argocd.md):

> In a GitOps environment, Jenkins doesn't necessarily need to directly modify Kubernetes.

Instead:

```text
Jenkins
 ↓
Build image
 ↓
Update GitOps repository
 ↓
ArgoCD
 ↓
Kubernetes
```

That's often a cleaner separation.

---

## 20. Jenkins + ArgoCD

This is an excellent interview architecture.

```text
                       Git
                        │
                        ↓
                     Jenkins
                        │
                 ┌──────┴──────┐
                 ↓             ↓
              Test          Docker
                              │
                              ↓
                             ECR
                              │
                              ↓
                      GitOps Repository
                              │
                              ↓
                           ArgoCD
                              │
                              ↓
                          Kubernetes
```

Jenkins handles:

```text
CI
build
test
package
image
```

ArgoCD handles:

```text
CD
synchronization
reconciliation
deployment
```

---

## 21. Jenkins vs GitHub Actions vs ArgoCD

This distinction is important.

| Tool | Primary role |
|---|---|
| GitHub Actions | CI/CD automation integrated with GitHub |
| Jenkins | General-purpose CI/CD automation server |
| ArgoCD | Kubernetes GitOps CD |
| Helm | Kubernetes packaging/templates |
| Terraform | Infrastructure as Code |

They can coexist.

Example enterprise architecture:

```text
GitHub
  │
  ↓
Jenkins
  │
  ├── Test
  ├── Build
  └── Docker
       │
       ↓
      ECR
       │
       ↓
 GitOps Repository
       │
       ↓
    ArgoCD
       │
       ↓
      EKS
```

---

## 22. Jenkins Plugins

Jenkins has a huge plugin ecosystem.

Plugins can integrate with:

```text
Git
Docker
Kubernetes
AWS
Slack
JUnit
SonarQube
security scanners
```

This is one reason Jenkins is powerful.

But it's also one reason Jenkins can become complicated.

---

## 23. Jenkins Controller Shouldn't Do Everything

A common architectural mistake:

```text
Controller
 ↓
Build everything
```

Better:

```text
Controller
 ↓
Schedule/orchestrate
 ↓
Agents
 ↓
Execute workloads
```

Why?

Because builds can consume:

```text
CPU
Memory
Disk
Network
```

and you don't want to overload the Jenkins controller.

---

## 24. Jenkins Agents in Kubernetes

A more modern setup:

```text
Jenkins
   ↓
Kubernetes
   ↓
Ephemeral build Pods
```

A build agent Pod is created when needed.

Then:

```text
Build
 ↓
Pod
 ↓
Build finishes
 ↓
Pod removed
```

Advantages:

```text
isolation
elasticity
clean environments
scaling
```

This connects directly to your Kubernetes knowledge.

---

## 25. Pipeline Parallelism

You can run independent stages in parallel.

For example:

```text
             Build
               │
        ┌──────┼──────┐
        ↓      ↓      ↓
      Unit   Lint   Security
        │      │      │
        └──────┼──────┘
               ↓
             Deploy
```

Jenkins supports parallel stages.

This reduces pipeline time when tasks are independent.

---

## 26. Sequential vs Parallel

Suppose:

```text
Tests = 5 min
Lint = 2 min
Security scan = 4 min
```

Sequential:

```text
5 + 2 + 4 = 11 min
```

Parallel:

```text
max(5,2,4) ≈ 5 min
```

assuming enough agents/resources.

This is a common CI/CD optimization.

---

## 27. Pipeline Parameters

You can make pipelines configurable.

For example:

```text
ENVIRONMENT:
  dev
  staging
  production
```

Then:

```text
Deploy
 ↓
Choose environment
 ↓
Use appropriate configuration
```

But production deployment should normally have stronger controls than arbitrary user input.

---

## 28. Production Approvals

A mature pipeline might be:

```text
Commit
 ↓
CI
 ↓
Tests
 ↓
Build
 ↓
Staging
 ↓
Integration tests
 ↓
Approval
 ↓
Production
```

This is where deployment governance comes into play.

GitHub Actions has environments/approvals; Jenkins can implement approval steps as well.

---

## 29. Jenkins Security

This is important.

#### Don't:

```text
hardcode AWS keys
hardcode passwords
run everything as root
allow unrestricted Jenkins access
install random plugins
```

#### Do:

```text
RBAC
least privilege
credential store
HTTPS
authentication
authorization
plugin updates
agent isolation
audit logs
network restrictions
secret rotation
```

---

## 30. Jenkins Supply Chain Security

Your CI server has enormous privileges.

Imagine Jenkins can:

```text
push Docker images
deploy to Kubernetes
access AWS
```

If Jenkins is compromised:

```text
attacker
   ↓
Jenkins
   ↓
AWS
   ↓
Kubernetes
```

Potentially catastrophic.

Therefore:

```text
least privilege
short-lived credentials
isolated agents
protected branches
dependency scanning
image scanning
signed artifacts where appropriate
```

are important.

---

## 31. Jenkins Credentials vs GitHub OIDC

You've learned AWS OIDC already.

Traditional Jenkins might use:

```text
Jenkins
 ↓
AWS access key
 ↓
AWS
```

Better where supported:

```text
Jenkins workload identity
 ↓
AWS IAM role
 ↓
temporary credentials
```

The exact implementation depends on where Jenkins runs.

The principle remains:

> Avoid unnecessary long-lived credentials.

---

## 32. Jenkins Pipeline With Docker + ECR + Kubernetes

A simplified conceptual pipeline:

```groovy
pipeline {

    agent any

    environment {
        IMAGE = "my-api:${GIT_COMMIT}"
    }

    stages {

        stage('Test') {
            steps {
                sh 'npm ci'
                sh 'npm test'
            }
        }

        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }

        stage('Docker') {
            steps {
                sh "docker build -t ${IMAGE} ."
            }
        }

        stage('Push') {
            steps {
                sh "docker push ${IMAGE}"
            }
        }

        stage('Deploy') {
            steps {
                sh 'kubectl apply -f k8s/'
            }
        }
    }
}
```

This is intentionally simplified.

A production pipeline needs:

```text
authentication
security scanning
immutable image naming
environment controls
deployment strategy
rollback
observability
```

---

## 33. Better Production Architecture With GitOps

Rather than:

```text
Jenkins → kubectl
```

you can use:

```text
Jenkins
 ↓
Build
 ↓
Test
 ↓
Docker
 ↓
ECR
 ↓
Update GitOps repo
 ↓
ArgoCD
 ↓
EKS
```

This connects our last two responses.

---

## 34. Jenkins Failure Scenario

#### Pipeline suddenly fails.

Don't immediately rerun it repeatedly.

Check:

```text
What stage failed?
        ↓
Build?
Test?
Docker?
Registry?
Credentials?
Deployment?
```

For example:

```text
Docker push failed
```

Investigate:

```text
ECR reachable?
credentials valid?
repository exists?
image tag valid?
permissions?
```

---

## 35. Jenkins Agent Offline

Suppose:

```text
Jenkins
 ↓
Agent offline
```

Check:

```text
network
agent process
resource exhaustion
disk
credentials
Jenkins-agent connection
container/node status
```

If Kubernetes is providing agents:

```text
kubectl get pods
kubectl describe pod
kubectl logs
```

Now your Kubernetes troubleshooting knowledge becomes useful.

---

## 36. Jenkins Disk Full

CI systems can accumulate:

```text
workspace
Docker images
build artifacts
logs
cache
```

Check:

```bash
df -h
du -sh *
```

Potential solutions:

```text
cleanup old builds
remove unused Docker images
artifact retention
workspace cleanup
log rotation
larger disk
```

This is a real-world DevOps problem.

---

## 37. Jenkins Pipeline Best Practices

Remember:

#### 1. Pipeline as code

```text
Jenkinsfile
```

#### 2. Small stages

```text
test
build
scan
package
deploy
```

#### 3. Immutable artifacts

Don't overwrite:

```text
latest
```

blindly.

Prefer:

```text
Git SHA
build number
version
```

#### 4. Fail fast

Tests should stop bad builds early.

#### 5. Least privilege

Pipeline shouldn't have unlimited production access.

#### 6. Reproducible builds

Same source should produce predictable artifacts.

---

## 38. Jenkins vs GitHub Actions — Interview Answer

If asked:

> "Why would a company use Jenkins when GitHub Actions exists?"

Don't say one is universally better.

Say:

> "GitHub Actions provides tightly integrated CI/CD for GitHub repositories and is convenient because runners, workflows, permissions and repository events are integrated into GitHub. Jenkins is a mature, highly extensible automation server with a large plugin ecosystem and can integrate with many source-control systems and internal infrastructure. Organizations with existing Jenkins infrastructure or highly customized pipelines may continue using it."

That's the right level of answer.

---

## 39. When Would YOU Use Jenkins?

For your projects:

#### If you're building a new personal project:

I'd generally prefer:

```text
GitHub Actions
```

because it's simpler.

#### If you're joining an enterprise:

You may encounter:

```text
Jenkins
```

and should be able to understand and maintain its pipelines.

#### If Kubernetes GitOps is used:

You might see:

```text
Jenkins/GitHub Actions
       ↓
      CI
       ↓
     ArgoCD
       ↓
      EKS
```

---

## 40. Jenkins Hands-On Exercise

If you want to practice locally:

#### Run Jenkins with Docker

```bash
docker volume create jenkins_home
```

Then:

```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

Check:

```bash
docker ps
```

Logs:

```bash
docker logs jenkins
```

Then access the Jenkins UI locally.

**Important:** this is a learning setup, not a production deployment.

---

## 41. Create a Pipeline

Create a repository containing:

```text
my-api/
├── package.json
├── src/
└── Jenkinsfile
```

Jenkins pipeline:

```groovy
pipeline {

    agent any

    stages {

        stage('Install') {
            steps {
                sh 'npm ci'
            }
        }

        stage('Test') {
            steps {
                sh 'npm test'
            }
        }

        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }
    }
}
```

Connect Jenkins to your repository.

Push:

```bash
git push
```

Then:

```text
GitHub
 ↓
Webhook
 ↓
Jenkins
 ↓
Pipeline
 ↓
Install
 ↓
Test
 ↓
Build
```

You've now actually used Jenkins.

---

## 42. Add Docker

Next stage:

```groovy
stage('Docker Build') {
    steps {
        sh 'docker build -t my-api:${BUILD_NUMBER} .'
    }
}
```

Then:

```text
Git
 ↓
Jenkins
 ↓
Node tests
 ↓
Build
 ↓
Docker
```

You can later connect this to ECR.

---

## 43. What You Must Know

For your target role, you don't need to memorize every Jenkins plugin.

#### 🔥 Deep enough

```text
Jenkins architecture
Controller
Agents
Jenkinsfile
Declarative pipelines
Stages
Steps
Environment variables
Credentials
Artifacts
Webhooks
Docker integration
CI/CD flow
Pipeline security
Jenkins + Kubernetes
Jenkins + GitOps
```

#### 🟡 Awareness

```text
Blue Ocean
Shared Libraries
Kubernetes plugin internals
Advanced plugin development
Jenkins distributed architecture internals
```

You don't need to become a Jenkins administrator.

---

## 44. Final Mental Model

You now have three generations/styles of CI/CD in your head:

#### Basic automation

```text
Git
 ↓
Jenkins
 ↓
Build/Test/Deploy
```

#### Cloud-native CI

```text
GitHub
 ↓
GitHub Actions
 ↓
Docker
 ↓
ECR
 ↓
Kubernetes
```

#### Modern GitOps

```text
Git
 ↓
GitHub Actions / Jenkins
 ↓
Build/Test
 ↓
Docker
 ↓
ECR
 ↓
GitOps Repository
 ↓
ArgoCD
 ↓
Kubernetes/EKS
```

You should be able to explain all three.

---

## 🎯 Chapter 27 Summary

We've covered:

```text
✅ Why Jenkins exists
✅ Jenkins architecture
✅ Controller
✅ Agents
✅ Jenkinsfile
✅ Declarative pipelines
✅ Stages/steps
✅ Environment variables
✅ Credentials
✅ Artifacts
✅ Git integration
✅ Webhooks
✅ Docker integration
✅ ECR
✅ Kubernetes
✅ Jenkins + ArgoCD
✅ Pipeline parallelism
✅ Approvals
✅ Security
✅ Least privilege
✅ Supply-chain security
✅ Troubleshooting
✅ Practical installation
✅ Practical Jenkins pipeline
✅ Jenkins vs GitHub Actions
✅ Jenkins vs ArgoCD
```

#### The key thing to remember:

```text
Jenkins = automation/CI/CD engine
GitHub Actions = GitHub-integrated automation/CI/CD
ArgoCD = Kubernetes GitOps CD
Helm = Kubernetes packaging
Terraform = infrastructure provisioning
```

And these tools can coexist rather than being mutually exclusive.
<!-- SOURCE-END -->

---

## Editorial supplement

> **Added by the knowledge-base editor — not part of the original source.** It fills gaps the source leaves open (for example concepts named in the interview list but never explained, or configuration the chapter only describes in words). Treat the text above as the original material and this section as clearly separated additions.

### Jenkinsfile syntax the chapter describes but does not show

The chapter explains parallel stages, parameters, approvals and conditional stages in words and diagrams. Here is the corresponding declarative syntax.

```groovy
pipeline {
    agent none                                    // choose an agent per stage

    options {
        timeout(time: 30, unit: 'MINUTES')        // fail runaway builds
        disableConcurrentBuilds()
    }

    parameters {
        choice(name: 'ENVIRONMENT',
               choices: ['dev', 'staging', 'production'],
               description: 'Target environment')
    }

    triggers { githubPush() }                     // build when the GitHub webhook fires

    stages {
        stage('Checks') {
            parallel {                            // independent stages run at the same time
                stage('Unit tests') { agent any; steps { sh 'npm ci && npm test' } }
                stage('Lint')       { agent any; steps { sh 'npm ci && npm run lint' } }
                stage('Dependency audit') { agent any; steps { sh 'npm audit --omit=dev' } }
            }
        }

        stage('Deploy to production') {
            when { branch 'main' }                // conditional stage (multibranch pipelines)
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'   // manual approval gate
                sh './deploy.sh'
            }
        }
    }

    post {
        failure { echo 'Build failed' }
    }
}
```

Notes:

- **Declarative vs scripted pipelines.** The chapter's `pipeline { ... }` form is *declarative* (structured, validated, preferred). *Scripted* pipelines use `node { ... }` blocks with free-form Groovy and are more flexible but easier to get wrong.
- **Docker inside the pipeline.** A plain Jenkins container does not ship the Docker CLI, so the `docker build` stages in the chapter need an agent that has Docker available. Two common options: an agent image/VM with Docker installed, or the Docker Pipeline plugin (`agent { docker { image 'node:22' } }`) to run the build steps inside a container. Mounting the host's `/var/run/docker.sock` into a build container gives that container root-equivalent control of the host, which is why it is a recognised security risk.
- **Webhook endpoint.** With the GitHub plugin the webhook target is typically `http(s)://<jenkins-host>/github-webhook/`; Jenkins must be reachable from GitHub (or use polling as a fallback).
- **First login to the local learning container.** Read the initial admin password with `docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword` (it is also printed in `docker logs jenkins`).
- **Multibranch pipelines** discover branches and pull requests that contain a `Jenkinsfile` and create a job for each; this is also what makes `when { branch 'main' }` meaningful.
- **Shared Libraries** (listed as awareness in the chapter) let many repositories reuse common pipeline code — the Jenkins equivalent of the reusable workflows described in [Chapter 6](../03-cicd-gitops/ch06-cicd-github-actions.md).

---

**Navigation:** ← [Chapter 26: GitOps + ArgoCD](ch26-gitops-argocd.md) · [Chapter 28: Ansible: Configuration Management & Automation](../06-iac-config/ch28-ansible.md) → · [Revision sheet](../../revision/ch27-revision.md)
