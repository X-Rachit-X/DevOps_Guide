# Chapter 8 — Docker Deep Dive + Production

> **Source:** Response 8 of the original conversation (`source-archive/src-08.txt`, lines 119–1661) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch08-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md) · *includes an editorial supplement at the end*

<!-- SOURCE-BEGIN -->

[Chapter 7](ch07-docker-fundamentals.md) taught you:

> **What Docker is and how to use it.**

Now the goal is:

> **Build Docker images that are efficient, secure, reproducible, debuggable, and suitable for production.**

This is where Docker becomes an actual engineering skill rather than a collection of commands.

---

## 1. Production Docker Architecture

Our basic application:

```text
TypeScript Source
       ↓
   Dockerfile
       ↓
 docker build
       ↓
 Docker Image
       ↓
 Container
       ↓
 Node.js API
```

Production adds:

```text
Developer
    ↓
Git
    ↓
CI/CD
    ↓
Docker Build
    ↓
Image Registry
    ↓
Deployment Platform
    ↓
Containers
    ↓
Load Balancer
    ↓
Users
```

Later:

```text
                    AWS
                     │
                Load Balancer
                     │
           ┌─────────┼─────────┐
           ↓         ↓         ↓
       Container Container Container
           │         │         │
           └─────────┼─────────┘
                     ↓
                 Database
```

---

## 2. Why Our First Dockerfile Isn't Production-Ready

We previously had:

```dockerfile
FROM node:22

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

It works.

But there are problems.

For example:

- Development dependencies may remain in the final image.
- The image may be unnecessarily large.
- The application may run as root.
- Build tools don't necessarily belong in production.
- We could improve caching.
- We haven't added a health check.
- We haven't separated build and runtime environments.

This leads us to **multi-stage builds**.

---

## 3. Multi-Stage Builds

Suppose:

```text
Build environment
```

needs:

```text
TypeScript
tsc
dev dependencies
build tools
```

But production only needs:

```text
Node.js
compiled JavaScript
production dependencies
```

Why ship the build tools?

We don't need them.

So:

```text
Build Stage
    ↓
Compile
    ↓
Production Stage
    ↓
Copy only required output
```

---

## 4. Multi-Stage Dockerfile

Example:

```dockerfile
FROM node:22 AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY tsconfig.json ./
COPY src ./src

RUN npm run build


FROM node:22-slim AS production

WORKDIR /app

ENV NODE_ENV=production

COPY package*.json ./
RUN npm ci --omit=dev

COPY --from=builder /app/dist ./dist

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

Now we have:

```text
Stage 1
builder
 ├── dependencies
 ├── source
 ├── TypeScript
 └── build tools
       ↓
      dist
       ↓
Stage 2
production
 ├── Node
 ├── production dependencies
 └── dist
```

The final image doesn't need the TypeScript compiler.

---

## 5. Why Multi-Stage Builds Matter

Suppose your build environment is:

```text
800 MB
```

while the runtime requires:

```text
200 MB
```

Without multi-stage builds:

```text
Production image ≈ 800 MB
```

With multi-stage:

```text
Production image ≈ 200 MB
```

Smaller images can mean:

- faster pulls
- faster deployments
- less storage
- smaller attack surface

---

## 6. Build Dependencies vs Runtime Dependencies

This distinction is important.

#### Build dependencies

Needed to create the application:

```text
TypeScript
tsc
Webpack/Vite/etc.
test tooling
```

#### Runtime dependencies

Needed to execute it:

```text
Express
Fastify
database drivers
application libraries
```

Production image should ideally contain only what it needs.

---

## 7. `npm ci --omit=dev`

In production:

```bash
npm ci --omit=dev
```

means:

> Install dependencies while excluding development dependencies.

So things like test frameworks don't need to be shipped with the production application.

---

## 8. Docker Layer Caching

Remember layers?

Consider:

```dockerfile
COPY package*.json ./
RUN npm ci

COPY . .
```

Suppose you change:

```text
src/user.ts
```

but not:

```text
package.json
package-lock.json
```

Docker can potentially reuse:

```text
RUN npm ci
```

instead of reinstalling everything.

Therefore:

```text
Dependencies unchanged
        ↓
Reuse dependency layer
        ↓
Build faster
```

This is why Dockerfile instruction ordering matters.

---

## 9. Bad Layer Ordering

Avoid:

```dockerfile
COPY . .

RUN npm ci
```

when you can structure it as:

```dockerfile
COPY package*.json ./

RUN npm ci

COPY . .
```

Because source-code changes happen frequently.

Dependencies generally change less frequently.

---

## 10. `.dockerignore`

A good Node project might have:

```text
node_modules
.git
.github
.env
.env.*
dist
coverage
npm-debug.log
Dockerfile*
docker-compose*
README.md
```

But be careful.

Don't blindly exclude files your build actually requires.

The principle is:

> **Send only the files required to build the image.**

---

## 11. Never Put Secrets in the Image

Bad:

```dockerfile
ENV DATABASE_PASSWORD=myPassword
```

or:

```dockerfile
COPY .env .
```

Why?

Because secrets can end up inside image layers or otherwise become accessible through image history/artifacts.

Instead:

```text
Secret Manager
      ↓
Deployment environment
      ↓
Container
      ↓
process.env
```

For example:

```typescript
const databaseUrl = process.env.DATABASE_URL;
```

We'll later use AWS's secret-management capabilities.

---

## 12. Run Containers as Non-Root

Containers shouldn't unnecessarily run the application as root.

Example:

```dockerfile
FROM node:22-slim

WORKDIR /app

RUN useradd --system --uid 1001 appuser

COPY --chown=appuser:appuser package*.json ./
RUN npm ci --omit=dev

COPY --chown=appuser:appuser dist ./dist

USER appuser

CMD ["node", "dist/index.js"]
```

Now the application runs as:

```text
appuser
```

rather than root.

This is a security hardening technique.

---

## 13. Why Root Is Dangerous

Suppose an application vulnerability allows an attacker to execute commands.

If the process runs as root:

```text
Application vulnerability
        ↓
Command execution
        ↓
Root privileges
```

Potential impact can be greater.

With a non-root process:

```text
Application vulnerability
        ↓
Command execution
        ↓
Limited privileges
```

This is an example of:

> **Principle of least privilege**

Give processes only the permissions they need.

---

## 14. Docker Health Checks

Your container being alive doesn't necessarily mean your application is healthy.

For example:

```text
Container = running
Node process = running
Database connection = broken
API = unusable
```

So health checks can test application health.

Example endpoint:

```typescript
app.get("/health", (_req, res) => {
  res.status(200).json({
    status: "ok"
  });
});
```

Then Docker can perform a health check.

Example:

```dockerfile
HEALTHCHECK \
  --interval=30s \
  --timeout=5s \
  --start-period=10s \
  --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:3000/health').then(r => { if (!r.ok) process.exit(1) }).catch(() => process.exit(1))"
```

The important distinction:

```text
Running ≠ Healthy
```

---

## 15. Liveness vs Readiness

You'll encounter these more heavily in Kubernetes.

#### Liveness

> Is the application still alive?

#### Readiness

> Is the application ready to receive traffic?

Imagine:

```text
Container started
       ↓
Node starting
       ↓
Database connection initializing
       ↓
Application ready
```

During startup:

```text
Alive = yes
Ready = no
```

That's why production orchestration systems distinguish these concepts.

---

## 16. Docker Networking

Now let's understand containers communicating with each other.

Suppose:

```text
API
PostgreSQL
Redis
```

You could have:

```text
API container
      │
      ├──── PostgreSQL container
      │
      └──── Redis container
```

Docker networks allow containers to communicate over a virtual network.

---

## 17. Create a Network

```bash
docker network create app-network
```

Then:

```bash
docker run -d \
  --name postgres \
  --network app-network \
  postgres
```

And:

```bash
docker run -d \
  --name api \
  --network app-network \
  my-api
```

Containers on the same Docker network can communicate using service/container names in appropriate configurations.

---

## 18. Don't Use Container IPs

Avoid hardcoding:

```text
172.x.x.x
```

for another container.

Container IPs can change.

Instead use a stable service/container name where supported.

For example:

```text
postgres
```

Conceptually:

```text
API
 ↓
postgres
 ↓
PostgreSQL container
```

This is similar to service discovery.

---

## 19. Host Port vs Container Port

This distinction is crucial.

Suppose:

```bash
docker run -p 8080:3000 my-api
```

means:

```text
Host
8080
  ↓
Container
3000
```

So users access:

```text
localhost:8080
```

while Node listens on:

```text
3000
```

inside the container.

---

## 20. Container-to-Container Ports

Suppose API connects to PostgreSQL.

PostgreSQL listens on:

```text
5432
```

The API doesn't need PostgreSQL's host-published port if both containers are on the same Docker network.

It can connect to:

```text
postgres:5432
```

rather than:

```text
localhost:5432
```

This is one of the most common Docker networking mistakes.

---

## 21. Docker Compose

Managing:

```text
API
PostgreSQL
Redis
```

manually is annoying.

Compose lets you describe the application in YAML.

Example:

```yaml
services:

  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/app
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:17
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: app
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7

volumes:
  postgres-data:
```

Then:

```bash
docker compose up
```

You get:

```text
             Docker Network
                  │
        ┌─────────┼─────────┐
        ↓         ↓         ↓
       API     PostgreSQL   Redis
                  │
                  ↓
               Volume
```

---

## 22. `depends_on`

We used:

```yaml
depends_on:
  - postgres
  - redis
```

This expresses startup dependency ordering.

But here's an important production concept:

> **Starting a dependency does not necessarily mean the dependency is ready.**

PostgreSQL container may be running while PostgreSQL itself is still initializing.

Therefore robust systems need proper health/readiness handling and application-level retry behavior.

---

## 23. Application Retry Logic

Imagine:

```text
API starts
 ↓
Database unavailable
 ↓
API crashes
```

A more resilient application might:

```text
API starts
 ↓
Database unavailable
 ↓
Wait
 ↓
Retry
 ↓
Retry
 ↓
Database available
 ↓
Start serving
```

This is especially important in distributed systems because startup ordering isn't a guarantee of service readiness.

---

## 24. Resource Limits

A container can consume significant resources if unrestricted.

You can impose limits in appropriate container runtimes/configurations.

Conceptually:

```text
Container
 ├── CPU limit
 └── Memory limit
```

Why?

Imagine:

```text
Container A → memory leak
      ↓
Consumes all host memory
      ↓
Other applications affected
```

Resource limits help prevent one workload from consuming everything.

Kubernetes provides much richer resource management later.

---

## 25. Container Logs

Applications should generally write logs to:

```text
stdout
stderr
```

For example:

```typescript
console.log("Server started");
console.error("Database connection failed");
```

Then:

```bash
docker logs api
```

can retrieve them.

This is preferable to relying on arbitrary log files inside ephemeral containers.

Later, cloud logging systems can collect these streams.

---

## 26. Don't Treat Containers Like Traditional Servers

Traditional mindset:

```text
SSH into server
Edit files
Restart process
```

Container mindset:

```text
Build new image
      ↓
Deploy new container
      ↓
Replace old container
```

Instead of manually modifying production containers.

Why?

Because containers are intended to be **reproducible and replaceable**.

---

## 27. Immutable Infrastructure

This leads to an important DevOps concept:

> **Don't manually patch production instances whenever possible; build a new version and replace the old one.**

Instead of:

```text
Production container
 ↓
SSH
 ↓
apt install something
 ↓
manual changes
```

prefer:

```text
Dockerfile
 ↓
New image
 ↓
Test
 ↓
Deploy
```

Now the infrastructure/application artifact is reproducible.

---

## 28. Docker Image Security

Important security practices:

```text
Use trusted base images
        ↓
Keep images updated
        ↓
Run as non-root
        ↓
Don't embed secrets
        ↓
Minimize packages
        ↓
Scan images
        ↓
Use least privilege
```

For example, instead of:

```dockerfile
FROM ubuntu
```

and installing everything manually, a purpose-built runtime image may be smaller.

---

## 29. Alpine vs Slim

You'll often see:

```text
node:22
node:22-slim
node:22-alpine
```

The general idea:

```text
Full image
   ↓
More packages

Slim
   ↓
Fewer packages

Alpine
   ↓
Very small base
```

But:

> **Smaller does not automatically mean better.**

Some packages/native dependencies can behave differently on Alpine because Alpine commonly uses musl libc rather than glibc.

So don't blindly choose Alpine just because it has a small image size.

For many Node applications, a Debian-based slim image is a straightforward production choice.

---

## 30. Image Scanning

Before deploying:

```text
Docker Image
      ↓
Vulnerability Scanner
      ↓
Potential CVEs
```

You want to identify:

- vulnerable OS packages
- vulnerable application dependencies
- outdated base images

This can be integrated into CI/CD.

Conceptually:

```text
Git Push
   ↓
Tests
   ↓
Docker Build
   ↓
Image Scan
   ↓
Push
   ↓
Deploy
```

---

## 31. Docker Image Tagging

Avoid relying entirely on:

```text
latest
```

Instead:

```text
my-api:1.4.2
my-api:git-a82f9c1
```

or another immutable identifier.

Then:

```text
Production
    ↓
my-api:git-a82f9c1
```

You know exactly which build is running.

---

## 32. Registry Workflow

The production workflow becomes:

```text
Dockerfile
    ↓
docker build
    ↓
Image
    ↓
docker tag
    ↓
docker push
    ↓
Registry
```

Another machine:

```text
Registry
    ↓
docker pull
    ↓
docker run
```

In AWS:

```text
GitHub Actions
      ↓
Docker build
      ↓
Amazon ECR
      ↓
ECS / EKS / EC2
```

We'll learn ECR and AWS compute later.

---

## 33. Docker + CI/CD

Now connect Chapters 6–8.

```text
Developer
   ↓
Git push
   ↓
GitHub
   ↓
CI
 ├── Lint
 ├── Typecheck
 ├── Tests
 └── Build
       ↓
Docker Build
       ↓
Image Scan
       ↓
Push Image
       ↓
Registry
       ↓
Deploy
```

This is a very important architecture to understand for interviews.

---

## 34. Production Dockerfile

A more realistic TypeScript example:

```dockerfile
FROM node:22 AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY tsconfig.json ./
COPY src ./src

RUN npm run build


FROM node:22-slim AS production

WORKDIR /app

ENV NODE_ENV=production

COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force

COPY --from=builder /app/dist ./dist

RUN useradd --system --uid 1001 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

Notice the principles:

```text
Multi-stage
     +
Dependency caching
     +
Production dependencies only
     +
Smaller runtime image
     +
Non-root user
     +
No secrets
     +
Immutable artifact
```

---

## 35. What Happens When You Deploy This?

Imagine:

```text
git push
```

Then:

```text
GitHub Actions
      ↓
npm ci
      ↓
tests
      ↓
npm run build
      ↓
docker build
      ↓
my-api:commit-sha
      ↓
image scan
      ↓
ECR
      ↓
deployment platform
      ↓
new container
      ↓
health check
      ↓
traffic
```

That's a genuine production-style workflow.

---

## 36. Docker Troubleshooting Framework

If a container isn't working, don't randomly restart things.

Use:

#### 1. Is it running?

```bash
docker ps
```

#### 2. Did it exit?

```bash
docker ps -a
```

#### 3. Why did it exit?

```bash
docker logs <container>
```

#### 4. Inspect configuration

```bash
docker inspect <container>
```

#### 5. Enter container

```bash
docker exec -it <container> sh
```

#### 6. Check networking

```bash
docker network ls
docker network inspect <network>
```

#### 7. Check ports

```bash
docker port <container>
```

This is a repeatable debugging methodology.

---

## 37. Common Docker Problems

#### Problem 1

```text
Container immediately exits
```

Check:

```bash
docker logs
```

Likely application/process failure.

---

#### Problem 2

```text
Cannot access localhost:3000
```

Check:

```text
Application binding
Port mapping
Container status
Firewall/networking
```

---

#### Problem 3

```text
API cannot connect to PostgreSQL
```

Check:

```text
Same Docker network?
Correct hostname?
Correct port?
Credentials?
Database ready?
```

Remember:

```text
localhost
```

inside API means the API container itself.

---

#### Problem 4

```text
Image is huge
```

Investigate:

```text
Base image
Dependencies
Layers
Build artifacts
Multi-stage build
.dockerignore
```

---

#### Problem 5

```text
Secret appears in image
```

Bad:

```text
COPY .env .
```

Fix:

```text
Remove secret from image
Rotate exposed secret
Use runtime secret injection
```

---

## 38. Docker Interview Questions

You should now be able to answer:

#### Fundamentals

1. What is Docker?
2. Image vs container?
3. Container vs VM?
4. What is a Docker layer?
5. What is a registry?
6. What is a Dockerfile?

#### Dockerfile

7. `RUN` vs `CMD`?
8. `CMD` vs `ENTRYPOINT`?
9. What does `EXPOSE` do?
10. Why use multi-stage builds?
11. Why copy `package.json` before source?
12. What is `.dockerignore`?

#### Production

13. Why shouldn't containers run as root?
14. Why shouldn't secrets be baked into images?
15. Why should production containers be stateless?
16. What is immutable infrastructure?
17. Why use versioned image tags?
18. Why use health checks?
19. What is the difference between running and healthy?
20. Why minimize container images?

#### Networking

21. What does `-p 8080:3000` mean?
22. How do two containers communicate?
23. Why doesn't `localhost` work for another container?
24. Why shouldn't you hardcode container IPs?

#### Debugging

25. How do you debug a container that immediately exits?
26. How do you view container logs?
27. How do you enter a running container?
28. How do you inspect its configuration?
29. How do you debug container networking?

---

## 🧠 The Most Important Mental Model

Don't memorize Docker commands independently.

Think:

```text
             DOCKER
                │
       ┌────────┼────────┐
       ↓        ↓        ↓
     Build     Run    Distribute
       │        │        │
    Dockerfile Container Registry
       │        │        │
       ↓        ↓        ↓
     Image   Network   Push/Pull
              Volume
                │
                ↓
           Production
```

And production:

```text
             Git
              ↓
            CI/CD
              ↓
        Docker Build
              ↓
       Security Scan
              ↓
         Image Registry
              ↓
       Deployment Platform
              ↓
          Containers
              ↓
       Load Balancer
              ↓
            Users
```

That architecture will keep appearing throughout the rest of this roadmap.
<!-- SOURCE-END -->

---

## Editorial supplement

> **Added by the knowledge-base editor — not part of the original source.** It fills gaps the source leaves open (for example concepts named in the interview list but never explained, or configuration the chapter only describes in words). Treat the text above as the original material and this section as clearly separated additions.

### `CMD` vs `ENTRYPOINT` (asked in the interview list, not explained in the chapter body)

Both define what runs when a container starts.

| | `ENTRYPOINT` | `CMD` |
|---|---|---|
| Role | The executable that **always** runs | The **default** command/arguments |
| Overriding at `docker run` | Hard: needs `--entrypoint` | Easy: anything after the image name replaces it |
| Typical use | Make the image behave like one program | Provide default arguments or a default command |

```dockerfile
# CMD only – `docker run my-api sh` replaces the whole command
CMD ["node", "dist/index.js"]

# ENTRYPOINT + CMD – CMD becomes the default *arguments* to ENTRYPOINT
ENTRYPOINT ["node"]
CMD ["dist/index.js"]          # `docker run my-api dist/other.js` runs node dist/other.js
```

**Exec form vs shell form.** `CMD ["node", "dist/index.js"]` (JSON array, *exec form*) starts Node directly as **PID 1**, so it receives signals such as `SIGTERM` from `docker stop` (see the signal discussion in [Chapter 2](../01-foundations/ch02-linux.md)). `CMD node dist/index.js` (*shell form*) runs under `/bin/sh -c`, and the shell may not forward signals, which breaks graceful shutdown. A process running as PID 1 also has no default signal handlers on Linux, so a Node server should handle `SIGTERM` itself, or you can run the container with `docker run --init` (a tiny init process).

### Node images already contain a non-root user

The chapter creates `appuser` with `useradd`. The official `node` images also ship a non-root user called `node` (UID 1000), so `USER node` is a common alternative that needs no `useradd`.

### Resource limits in practice

The chapter describes limits conceptually. With plain Docker:

```bash
docker run -d --memory=512m --cpus=1.0 my-api:1.0
```

A container that exceeds its memory limit can be killed by the kernel's out-of-memory (OOM) killer. Kubernetes expresses the same idea as resource *requests* and *limits* (see [Chapter 20](../05-kubernetes/ch20-kubernetes-networking-scaling.md)).

### `depends_on` with real readiness

To wait until PostgreSQL is actually ready (not just started), give it a healthcheck and use a health condition:

```yaml
services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_PASSWORD: password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 10

  api:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
```

Application-level retry logic (section 23) is still recommended: a database can become unavailable after startup too.

### Container name resolution works only on user-defined networks

On the default `bridge` network, containers can reach each other by IP but **not by name**. Containers on a **user-defined** bridge network (such as `app-network`, or the network Compose creates automatically) get automatic DNS resolution of container/service names. That is why the chapter's `docker network create app-network` step matters.

### Why the health check uses Node instead of `curl`

`node:22-slim` does not ship `curl`. The `HEALTHCHECK` in section 14 therefore uses the Node runtime that is already in the image (`fetch` is built into modern Node), avoiding an extra package in the final image.

---

**Navigation:** ← [Chapter 7: Docker Fundamentals](ch07-docker-fundamentals.md) · [Chapter 9: AWS Fundamentals + IAM](../04-aws/ch09-aws-fundamentals-iam.md) → · [Revision sheet](../../revision/ch08-revision.md)
