# Chapter 6 — CI/CD + GitHub Actions

> **Source:** Response 6 of the original conversation (`source-archive/src-06.txt`, lines 1–1726) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch06-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

This response is where **Git + Bash + testing + Docker + deployment** start becoming one complete DevOps workflow.

By the end, you should be able to look at a CI/CD pipeline and understand:

```text
Developer
   ↓
Git push
   ↓
GitHub
   ↓
CI
   ↓
Build + Test + Security checks
   ↓
Artifact / Docker image
   ↓
CD
   ↓
Deployment
   ↓
Production
   ↓
Monitoring
```

And importantly, you'll understand **how to build this yourself**.

---

## 1. What problem does CI/CD solve?

Imagine 20 developers working on a backend.

Without automation:

```text
Developer
   ↓
"Hey, I finished my code."
   ↓
Someone manually tests it
   ↓
Someone builds it
   ↓
Someone copies files to server
   ↓
Someone restarts application
```

This creates:

- human error
- slow deployments
- inconsistent environments
- forgotten tests
- difficult rollbacks

CI/CD automates much of this.

---

## 2. CI — Continuous Integration

CI means developers integrate changes frequently and have automated checks run against those changes.

Typical flow:

```text
git push
   ↓
CI starts
   ↓
Install dependencies
   ↓
Lint
   ↓
Type check
   ↓
Test
   ↓
Build
```

For a TypeScript project:

```bash
npm ci
npm run lint
npm run typecheck
npm test
npm run build
```

If something fails:

```text
❌ Pipeline failed
```

If everything succeeds:

```text
✅ Pipeline passed
```

---

## 3. Why CI is Valuable

Suppose you modify authentication.

You accidentally break payment functionality.

Your code may compile.

But automated tests might catch it:

```text
Pull Request
     ↓
CI
     ↓
500 tests
     ↓
3 failed ❌
```

Now the problem is detected **before production**.

This is the fundamental value of CI:

> **Find integration problems early and automatically.**

---

## 4. Continuous Delivery vs Continuous Deployment

Let's separate them clearly.

#### Continuous Delivery

Every successful change is automatically prepared and made **ready to deploy**, but production may require approval.

```text
Code
 ↓
CI
 ↓
Build
 ↓
Test
 ↓
Production-ready
 ↓
Manual approval
 ↓
Production
```

#### Continuous Deployment

Successful changes automatically go to production.

```text
Code
 ↓
CI
 ↓
Build
 ↓
Test
 ↓
Production
```

Both are legitimate approaches.

---

## 5. CI/CD Pipeline

A pipeline is a sequence of automated steps.

Example:

```text
                  Git Push
                     │
                     ↓
                 Checkout
                     │
                     ↓
             Install Dependencies
                     │
                     ↓
                  Lint
                     │
                     ↓
                Type Check
                     │
                     ↓
                  Tests
                     │
                     ↓
                  Build
                     │
                     ↓
               Docker Build
                     │
                     ↓
             Push Image to Registry
                     │
                     ↓
                 Deploy
                     │
                     ↓
               Health Check
```

This is the architecture we'll understand.

---

## 6. GitHub Actions

We'll use **GitHub Actions** as our primary CI/CD tool.

It allows workflows to execute automatically in response to GitHub events.

For example:

```text
git push
   ↓
GitHub
   ↓
GitHub Actions
```

Workflow files are typically stored in:

```text
.github/workflows/
```

Example:

```text
.github/
└── workflows/
    └── ci.yml
```

---

## 7. Your First GitHub Actions Workflow

Create:

```text
.github/workflows/ci.yml
```

```yaml
name: CI

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 22

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build
```

Don't memorize this yet.

Let's understand every part.

---

## 8. `name`

```yaml
name: CI
```

Just gives the workflow a name.

GitHub will show:

```text
CI
```

in the Actions interface.

---

## 9. `on`

```yaml
on:
  push:
    branches: [main]
```

This defines the **trigger**.

Meaning:

> Run this workflow when code is pushed to `main`.

You could also trigger on:

```yaml
on:
  pull_request:
    branches: [main]
```

Meaning:

> Run when a Pull Request targeting `main` is created/updated.

---

## 10. Jobs

```yaml
jobs:
  test:
```

A workflow contains one or more **jobs**.

Think:

```text
Workflow
   │
   ├── Job A
   ├── Job B
   └── Job C
```

A job runs on a runner.

---

## 11. Runner

```yaml
runs-on: ubuntu-latest
```

This tells GitHub which environment executes the job.

Conceptually:

```text
GitHub Actions
      ↓
Ubuntu machine
      ↓
Your commands
```

Other runner types can include Windows or macOS.

---

## 12. Steps

Inside the job:

```yaml
steps:
```

we define individual operations.

Example:

```yaml
- name: Install dependencies
  run: npm ci
```

`run` executes a shell command.

So:

```yaml
run: npm test
```

is essentially:

```bash
npm test
```

on the runner.

---

## 13. `uses`

This:

```yaml
uses: actions/checkout@v4
```

uses an existing GitHub Action.

It checks your repository's code into the runner.

Without checkout, the runner doesn't automatically have your repository files available for your build commands.

---

## 14. Why `npm ci` Instead of `npm install`?

This is an excellent interview detail.

For CI environments, `npm ci` is generally preferred because it performs a clean, lockfile-based installation.

It uses:

```text
package-lock.json
```

to reproduce the dependency tree.

Conceptually:

```text
package.json
     +
package-lock.json
     ↓
npm ci
     ↓
Same dependency versions
```

This makes builds more reproducible.

---

## 15. Pipeline Failure

Suppose:

```yaml
- name: Run tests
  run: npm test
```

returns a non-zero exit code.

Remember [Chapter 3](../01-foundations/ch03-bash-automation.md)?

```text
0     → success
non-0 → failure
```

GitHub Actions detects the failed command.

Then the job normally stops.

```text
Install
  ↓
Lint
  ↓
Tests ❌
  ↓
Build doesn't run
```

This is where **Linux exit codes → Bash → CI/CD** connect.

---

## 16. Multiple Jobs

Suppose you want:

```text
test
security
build
```

You can have:

```yaml
jobs:
  test:
    ...

  security:
    ...

  build:
    ...
```

Conceptually:

```text
            Workflow
          /     |      \
       Test  Security  Build
```

Independent jobs can run in parallel.

That can make pipelines faster.

---

## 17. Job Dependencies

Suppose build should happen only after tests pass.

You can use:

```yaml
jobs:
  test:
    ...

  build:
    needs: test
    ...
```

Now:

```text
test
 ↓
build
```

instead of:

```text
test ─────┐
          ↓
build
```

This is useful when designing pipelines.

---

## 18. A Better CI Pipeline

For your TypeScript backend:

```yaml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22

      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test
      - run: npm run build
```

Now every Pull Request can be automatically validated.

---

## 19. Type Checking

Because you're using TypeScript:

```bash
npm run typecheck
```

might run:

```bash
tsc --noEmit
```

This checks TypeScript correctness without producing build output.

Your pipeline can therefore catch:

```typescript
const userId: number = "123";
```

before merging.

---

## 20. Linting

Linting catches code-quality problems.

For example:

```bash
npm run lint
```

might detect:

- unused variables
- suspicious patterns
- formatting issues
- style violations

Linting isn't a replacement for tests.

Think:

```text
Lint
 ↓
Code quality

Typecheck
 ↓
Type correctness

Tests
 ↓
Behavior correctness

Build
 ↓
Production artifact
```

---

## 21. Unit Tests vs Integration Tests

CI can run different levels of tests.

#### Unit tests

Test small pieces:

```text
function
service
utility
```

#### Integration tests

Test multiple components together:

```text
API
 ↓
Database
```

#### End-to-end tests

Test the system from the user's perspective:

```text
Browser
 ↓
API
 ↓
Database
```

A production pipeline might have:

```text
Lint
 ↓
Unit Tests
 ↓
Integration Tests
 ↓
E2E
 ↓
Build
```

We won't build an entire testing course here, but you should understand where each fits.

---

## 22. Artifacts

Suppose your TypeScript build produces:

```text
dist/
```

You may want to save that output from the workflow.

That's a **build artifact**.

Conceptually:

```text
Source Code
    ↓
Build
    ↓
dist/
    ↓
Artifact
```

Artifacts can be:

- binaries
- compiled JavaScript
- packages
- reports
- test results

They can be passed to later workflow stages or retained for inspection.

---

## 23. Docker in CI/CD

Now we connect [Chapter 7](../02-containers/ch07-docker-fundamentals.md)/8 later with CI/CD.

Instead of deploying raw source code, build a Docker image.

```text
GitHub
   ↓
CI
   ↓
Tests
   ↓
Docker Build
   ↓
Docker Image
   ↓
Container Registry
   ↓
Deployment
```

Example:

```yaml
- name: Build Docker image
  run: docker build -t my-api:${{ github.sha }} .
```

Notice:

```text
${{ github.sha }}
```

This gives the image a unique identifier corresponding to the commit.

That is much better than blindly deploying:

```text
latest
```

for production traceability.

---

## 24. Container Registry

You need somewhere to store Docker images.

Examples include:

- GitHub Container Registry
- Amazon ECR
- Docker Hub

For our AWS-focused roadmap, you'll learn **Amazon ECR** later.

Conceptually:

```text
GitHub Actions
      ↓
Docker build
      ↓
Image
      ↓
ECR
      ↓
AWS deployment
```

---

## 25. Why Use Immutable Image Tags?

Imagine:

```text
my-api:latest
```

today means:

```text
version A
```

Tomorrow:

```text
my-api:latest
```

means:

```text
version B
```

Now it's difficult to know exactly what production is running.

Instead:

```text
my-api:a83f91c
my-api:7b12e44
my-api:f82d911
```

Each can correspond to a specific commit.

This makes deployment and rollback much easier.

---

## 26. Secrets

CI/CD often needs credentials.

For example:

```text
AWS credentials
Database credentials
API keys
Signing keys
```

**Do not put them directly in YAML.**

Bad:

```yaml
env:
  AWS_SECRET_ACCESS_KEY: "super-secret"
```

Instead use GitHub Secrets/appropriate secret-management mechanisms.

Conceptually:

```text
GitHub Secret
      ↓
Workflow
      ↓
Environment variable
      ↓
Command
```

Later we'll discuss how production workloads should use services such as **AWS Secrets Manager** rather than embedding long-lived credentials.

---

## 27. Environment Variables

You can define:

```yaml
env:
  NODE_ENV: production
```

Then:

```bash
echo "$NODE_ENV"
```

Your application:

```typescript
const env = process.env.NODE_ENV;
```

This connects directly to the Bash concepts from [Chapter 3](../01-foundations/ch03-bash-automation.md).

---

## 28. GitHub Environments

You might have:

```text
development
staging
production
```

Each can have different:

- secrets
- variables
- protection rules
- approvals

Conceptually:

```text
              CI
              │
          Build/Test
              │
       ┌──────┴──────┐
       ↓             ↓
    Staging       Production
                    │
               Approval
```

Production can require manual approval.

This is useful for **Continuous Delivery**.

---

## 29. Deployment Example

A simplified pipeline:

```text
Pull Request
     ↓
Lint
     ↓
Test
     ↓
Build
     ↓
Merge
     ↓
Docker Build
     ↓
Push to ECR
     ↓
Deploy
     ↓
Health Check
```

That is a realistic high-level CI/CD architecture.

---

## 30. Deployment Strategies

Suppose you're replacing:

```text
v1
```

with:

```text
v2
```

You don't necessarily want:

```text
v1 → 💥 → v2
```

There are different strategies.

---

### Recreate

Stop old version.

Start new version.

```text
v1
 ↓
STOP
 ↓
v2
```

Simple, but may cause downtime.

---

### Rolling Deployment

Gradually replace instances.

```text
v1 v1 v1 v1
 ↓
v2 v1 v1 v1
 ↓
v2 v2 v1 v1
 ↓
v2 v2 v2 v1
 ↓
v2 v2 v2 v2
```

Good for gradual replacement.

---

### Blue-Green

Maintain two environments:

```text
Blue → v1
Green → v2
```

Initially:

```text
Users
  ↓
Blue
```

Test Green:

```text
Green → v2
```

Then switch:

```text
Users
  ↓
Green
```

If something goes wrong, traffic can potentially be switched back to Blue.

---

### Canary

Send a small percentage of users to the new version:

```text
Users
  │
  ├── 95% → v1
  │
  └── 5%  → v2
```

Monitor:

```text
errors
latency
performance
```

If healthy:

```text
5%
 ↓
25%
 ↓
50%
 ↓
100%
```

These strategies become particularly important when we reach Kubernetes.

---

## 31. Rollback

Suppose:

```text
v1 → production
```

Then:

```text
v2 → production
```

and errors spike.

You need to return to v1.

```text
v2
 ↓
❌
 ↓
v1
```

If your images are versioned:

```text
my-api:v1
my-api:v2
```

rollback becomes much easier.

This is another reason **immutable/versioned artifacts** matter.

---

## 32. CI/CD Security

A production pipeline should also consider:

```text
Dependency vulnerabilities
Secrets
Docker image vulnerabilities
Infrastructure configuration
Permissions
Supply-chain security
```

Possible checks:

```text
Code
 ↓
Dependency scanning
 ↓
SAST
 ↓
Container scanning
 ↓
Build
 ↓
Deploy
```

You don't need to memorize every security tool.

Understand the principle:

> **The pipeline itself is part of the production security boundary.**

---

## 33. Caching

CI can become slow.

Suppose dependencies take:

```text
2 minutes
```

every run.

Caching can reduce repeated downloads.

For example:

```text
First run
 ↓
Download dependencies
 ↓
Cache

Next run
 ↓
Restore cache
 ↓
Faster
```

GitHub Actions supports caching through actions and workflow configuration.

But be careful:

> Cache correctness matters. A stale or incorrectly keyed cache can produce confusing builds.

---

## 34. Matrix Builds

Suppose you want to test your application on multiple Node versions:

```yaml
strategy:
  matrix:
    node: [20, 22, 24]
```

Then:

```text
             Test
       /       |       \
   Node 20   Node 22   Node 24
```

This is called a **matrix strategy**.

Useful when compatibility across environments matters.

---

## 35. Reusable Workflows

Large organizations may have many repositories.

Instead of duplicating:

```text
100 lines of CI YAML
```

everywhere, workflows can be reused.

Conceptually:

```text
Central CI workflow
       ↓
Repo A
Repo B
Repo C
Repo D
```

This improves consistency.

You don't need to master this immediately, but recognize it as a scaling pattern for CI/CD configuration.

---

## 36. Complete TypeScript CI Pipeline

Here's a reasonable starting point:

```yaml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - name: Install
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npm run typecheck

      - name: Test
        run: npm test

      - name: Build
        run: npm run build
```

This is something you should eventually be able to write **without copying it**.

---

## 37. CI + Docker + AWS

Now imagine production.

```text
Developer
    │
    │ git push
    ↓
 GitHub
    │
    ↓
GitHub Actions
    │
    ├── Lint
    ├── Typecheck
    ├── Test
    └── Build
           │
           ↓
      Docker Build
           │
           ↓
          ECR
           │
           ↓
       AWS Deploy
           │
           ↓
        EC2/ECS/EKS
           │
           ↓
      Health Check
           │
           ↓
       Production
```

This is the architecture you should keep in your head.

---

## 38. CI vs CD — Interview Answer

If an interviewer asks:

> **What's the difference between CI and CD?**

A strong concise answer:

> **CI continuously integrates code changes and automatically validates them through checks such as builds and tests. CD extends that process toward deployment: Continuous Delivery keeps changes production-ready with a deployment step that may require approval, while Continuous Deployment automatically releases successful changes to production.**

That's substantially better than:

> "CI is testing and CD is deployment."

---

## 39. What Happens If CI Fails?

Suppose:

```text
Developer
 ↓
Pull Request
 ↓
CI
 ↓
Tests ❌
```

The PR should generally not be merged until the failure is understood/resolved, depending on repository protection rules.

This creates:

```text
Developer
    ↓
Fast feedback
    ↓
Fix
    ↓
CI
    ↓
Pass
    ↓
Merge
```

This is the essence of continuous integration.

---

## 40. A Production Pipeline

Eventually, your pipeline could look like:

```text
                   Developer
                       │
                    Git Push
                       │
                       ↓
                    GitHub
                       │
               ┌───────┴───────┐
               ↓               ↓
             PR CI          Security
               │               │
               └───────┬───────┘
                       ↓
                     Merge
                       │
                       ↓
                    Build
                       │
                       ↓
                Docker Image
                       │
                       ↓
                     ECR
                       │
                       ↓
                  Deployment
                       │
                 ┌─────┴─────┐
                 ↓           ↓
              Staging    Production
                 │           │
                 └─────┬─────┘
                       ↓
                  Health Check
                       │
                       ↓
                   Monitoring
```

Now you can see how:

**Git → Bash → Docker → AWS → Kubernetes → Monitoring**

will eventually connect.

---

## 41. Important CI/CD Concepts to Know

You should now recognize:

```text
Workflow
Job
Step
Runner
Trigger
Artifact
Environment
Secret
Variable
Cache
Matrix
Dependency
Pipeline
Build
Test
Deploy
Rollback
Approval
```

But don't just memorize these terms.

Think of them as components of:

```text
Code
 ↓
Validate
 ↓
Package
 ↓
Release
 ↓
Deploy
 ↓
Observe
 ↓
Rollback if necessary
```

---

## 🧪 Practical Assignment

Create a small Node.js/TypeScript project.

Your workflow should:

```text
GitHub push
   ↓
Checkout
   ↓
Node setup
   ↓
npm ci
   ↓
Lint
   ↓
Typecheck
   ↓
Tests
   ↓
Build
```

Then deliberately break something.

For example:

```typescript
const port: number = "3000";
```

Push it.

You should see:

```text
CI ❌
```

Fix it.

Push again:

```text
CI ✅
```

Then add:

```yaml
- name: Build Docker image
  run: docker build -t my-api:${{ github.sha }} .
```

Now your pipeline is beginning to produce a deployable artifact.

---

## 🎯 Interview Questions

Try answering these without looking back:

#### Fundamentals

1. What is CI?
2. What is Continuous Delivery?
3. What is Continuous Deployment?
4. Why do companies use CI/CD?
5. What is a pipeline?
6. What is a runner?
7. Job vs step?
8. What is an artifact?

#### GitHub Actions

9. What is a workflow?
10. What triggers a workflow?
11. What does `uses:` mean?
12. What does `run:` mean?
13. What does `needs:` do?
14. Why use `npm ci` in CI?
15. What are GitHub Secrets?
16. What is a matrix strategy?
17. Why cache dependencies?

#### Deployment

18. Rolling vs Blue-Green?
19. Blue-Green vs Canary?
20. Why are immutable image tags useful?
21. What is rollback?
22. How would you deploy without downtime?

#### Scenario

> **You pushed a new version of your Node.js backend. CI passes, Docker image builds successfully, deployment succeeds, but users suddenly receive 500 errors. What would you investigate?**

Don't simply answer "restart it."

Think:

```text
Deployment
   ↓
Correct image?
   ↓
Environment variables?
   ↓
Secrets?
   ↓
Database migrations?
   ↓
Application logs?
   ↓
Health checks?
   ↓
Dependency connectivity?
   ↓
Traffic/load balancer?
   ↓
Rollback if necessary
```

That is the type of production reasoning we're building.

---

## 🧠 The Big Connection

You've now built:

```text
Chapter 2
Linux
   ↓
Chapter 3
Bash
   ↓
Chapter 5
Git
   ↓
Chapter 6
CI/CD
```

So:

```text
Developer
   ↓
Git
   ↓
GitHub
   ↓
GitHub Actions
   ↓
Bash/Linux environment
   ↓
Test
   ↓
Build
   ↓
Docker
```

And **Docker is our next major topic.**
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 5: Git & GitHub Deep Dive](../01-foundations/ch05-git-github.md) · [Chapter 7: Docker Fundamentals](../02-containers/ch07-docker-fundamentals.md) → · [Revision sheet](../../revision/ch06-revision.md)
