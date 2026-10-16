# Chapter 6 — Revision Sheet: CI/CD + GitHub Actions

> Supplements [the full chapter](../docs/03-cicd-gitops/ch06-cicd-github-actions.md).

## What CI/CD solves

Manual flow ("I finished" → someone tests → builds → copies to server → restarts) causes human error, slow deploys, inconsistent environments, forgotten tests, painful rollbacks. CI/CD automates it.

| Term | Meaning |
|---|---|
| **CI** | Integrate frequently; automated checks on every change → find integration problems early (e.g. 500 tests, 3 fail ❌ *before* production). |
| **Continuous Delivery** | Every good change is automatically built/tested and **ready**; production release needs **manual approval**. |
| **Continuous Deployment** | Passing changes go to production **automatically**. |

**Strong interview answer:** *CI continuously integrates changes and validates them (builds, tests). CD extends that toward deployment: Continuous Delivery keeps changes production-ready with a deploy step that may need approval, while Continuous Deployment releases successful changes automatically.* (Not "CI is testing and CD is deployment".)

## Pipeline stages

Git push → Checkout → Install deps → Lint → Type check → Tests → Build → Docker build → Push image to registry → Deploy → Health check → Monitoring.

| Check | Catches |
|---|---|
| Lint (`npm run lint`) | Code quality: unused vars, suspicious patterns, formatting/style |
| Typecheck (`tsc --noEmit`) | Type correctness, e.g. `const userId: number = "123"` — no build output |
| Tests | Behaviour correctness |
| Build | Production artifact |

Test levels: **unit** (function/service/utility) → **integration** (API ↔ DB) → **E2E** (browser ↔ API ↔ DB).

## GitHub Actions anatomy

```yaml
name: CI                       # label in Actions UI
on:                            # TRIGGER
  push: { branches: [main] }   # or pull_request: { branches: [main] }
jobs:                          # one or more jobs (parallel by default)
  test:
    runs-on: ubuntu-latest     # RUNNER environment (also Windows/macOS)
    steps:
      - uses: actions/checkout@v4          # reuse an Action: put repo code on runner
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci                        # run a shell command
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test
      - run: npm run build
  build:
    needs: test                # job dependency → build only after test passes
```

- Workflow files live in `.github/workflows/*.yml`.
- A command returning **non-zero** fails the step and normally stops the job (Linux exit codes → Bash → CI/CD, Ch.3).
- **Why `npm ci`:** clean, lockfile-based install from `package-lock.json` → reproducible dependency tree.
- **Matrix:** `strategy: matrix: node: [20, 22, 24]` → same job fanned out across versions.
- **Cache:** reuse downloaded dependencies (`cache: npm`); beware stale/wrongly-keyed caches.
- **Reusable workflows:** one central CI workflow used by many repos for consistency.
- **Artifacts:** saved build output (`dist/`, binaries, packages, reports, test results) passed to later stages or kept for inspection.
- **Env vars:** `env: NODE_ENV: production`. **Secrets:** use GitHub Secrets, never write keys in YAML. Flow: GitHub Secret → workflow → environment variable → command.
- **GitHub Environments** (development / staging / production) have their own secrets, variables, protection rules and **approvals** → implements Continuous Delivery.

## Docker in CI

```yaml
- name: Build Docker image
  run: docker build -t my-api:${{ github.sha }} .
```

- `${{ github.sha }}` = unique tag per commit → traceability + easy rollback. **Avoid deploying `latest`** in production (mutable: today's `latest` ≠ tomorrow's).
- Registries: GitHub Container Registry, **Amazon ECR**, Docker Hub.
- Full picture: Dev → git push → GitHub → Actions (lint/typecheck/test/build) → Docker build → ECR → AWS deploy (EC2/ECS/EKS) → health check → production.

## Deployment strategies

| Strategy | How | Trade-off |
|---|---|---|
| **Recreate** | Stop v1, start v2 | Simple; downtime |
| **Rolling** | Replace instances gradually (v2 v1 v1 v1 → … → v2 v2 v2 v2) | Gradual; mixed versions during rollout |
| **Blue-Green** | Two environments (Blue=v1, Green=v2); test Green; switch traffic; switch back if bad | Fast rollback; needs double capacity |
| **Canary** | Send small % (95/5) to v2, watch errors/latency/performance; 5→25→50→100% | Safer; needs good monitoring |

**Rollback** = return to previous version; easy only with versioned/immutable artifacts (`my-api:v1`, `my-api:v2`).

## CI/CD security

Consider dependency vulnerabilities, secrets, Docker image vulnerabilities, infrastructure config, permissions, supply-chain. Stages: dependency scanning → SAST → container scanning → build → deploy. Principle: **the pipeline itself is part of the production security boundary.**

## Vocabulary

Workflow · Job · Step · Runner · Trigger · Artifact · Environment · Secret · Variable · Cache · Matrix · Dependency · Pipeline · Build · Test · Deploy · Rollback · Approval.

## Scenario — "CI passes, deploy succeeds, users get 500s"

Correct image? → env vars? → secrets? → DB migrations? → app logs? → health checks? → dependency connectivity? → traffic/load balancer? → **rollback if necessary**. (Don't answer "restart it".)

## Added notes (not in source)

- Matrix jobs consume the value as `${{ matrix.node }}` (e.g. `node-version: ${{ matrix.node }}`); the source shows only the `strategy` snippet.
- Secrets are read in workflows as `${{ secrets.NAME }}`.
- Action version pins (`@v4`) drift over time; newer major versions of `actions/checkout`/`setup-node` exist — check the current docs when writing new workflows.
- A failed CI should block merge only if branch-protection rules require the check to pass ("depending on repository protection rules").

## Practical assignment (checklist)

Small TS project → workflow with checkout, Node setup, `npm ci`, lint, typecheck, tests, build → deliberately break (`const port: number = "3000";`) → see ❌ → fix → ✅ → add the Docker build step.

## Interview questions (22) — pointers

CI; Delivery; Deployment; why CI/CD; pipeline; runner; job vs step; artifact; workflow; triggers; `uses:`; `run:`; `needs:`; `npm ci`; Secrets; matrix; caching; rolling vs blue-green; blue-green vs canary; immutable tags; rollback; zero-downtime deploy.

<!-- NAV -->

---

← [Sheet 5](ch05-revision.md) · [Full chapter 6](../docs/03-cicd-gitops/ch06-cicd-github-actions.md) · [All revision material](README.md) · [Sheet 7](ch07-revision.md) →
