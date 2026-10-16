# Chapter 8 — Revision Sheet: Docker Deep Dive + Production

> Supplements [the full chapter](../docs/02-containers/ch08-docker-production.md). Goal: images that are **efficient, secure, reproducible, debuggable, production-ready**.

## Why the first Dockerfile isn't production-ready

Dev dependencies remain in the final image · image unnecessarily large · runs as root · build tools shipped to production · caching could be better · no health check · build and runtime not separated.

## Multi-stage build

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
RUN useradd --system --uid 1001 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

- Build stage has TypeScript, `tsc`, dev deps, source; final stage has only Node, **production deps**, and `dist`.
- Example sizing: ~800 MB build env vs ~200 MB runtime → **faster pulls/deploys, less storage, smaller attack surface**.
- **Build deps** (TypeScript, `tsc`, Webpack/Vite, test tooling) vs **runtime deps** (Express, Fastify, DB drivers).
- `npm ci --omit=dev` = install without devDependencies.

## Layer caching

Order instructions from least → most frequently changing: `COPY package*.json` → `RUN npm ci` → `COPY . .`. Change `src/user.ts` only → `npm ci` layer is reused. **Bad ordering:** `COPY . .` before `npm ci`.

## `.dockerignore` (extended)

`node_modules`, `.git`, `.github`, `.env`, `.env.*`, `dist`, `coverage`, `npm-debug.log`, `Dockerfile*`, `docker-compose*`, `README.md`. Principle: **send only what the build needs** — but don't exclude files the build actually requires.

## Security

| Practice | Why |
|---|---|
| Never `ENV DATABASE_PASSWORD=…` or `COPY .env .` | Secrets persist in image layers/history |
| Inject secrets at runtime (Secret Manager → deployment env → container → `process.env`) | Keeps images clean |
| `USER appuser` (non-root) | **Least privilege**: exploit yields limited privileges not root |
| Trusted, updated, minimal base images; minimise packages | Smaller attack surface |
| **Scan images** (OS packages, app deps, outdated bases → CVEs) in CI before push | Catch vulnerabilities early |
| Immutable infrastructure | Don't SSH into prod containers and patch; rebuild image → test → deploy → replace |

**Alpine vs slim:** `node:22` (full), `node:22-slim` (fewer packages), `node:22-alpine` (very small). Smaller ≠ automatically better — Alpine uses **musl libc** (not glibc), so some native modules behave differently. For many Node apps a Debian **slim** image is a safe production choice.

## Health, liveness, readiness

- **Running ≠ Healthy** (container up + Node up + DB connection broken = unusable API).
- `/health` endpoint + Dockerfile `HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD node -e "fetch('http://127.0.0.1:3000/health')…"`.
- **Liveness** = is it alive? **Readiness** = can it receive traffic? During startup: alive yes, ready no. Heavily used in Kubernetes.

## Networking

```bash
docker network create app-network
docker run -d --name postgres --network app-network postgres
docker run -d --name api      --network app-network my-api
```

- Use service/container **names** (`postgres:5432`), not container IPs (`172.x.x.x`, which change).
- `-p 8080:3000` → host 8080 → container 3000; users hit `localhost:8080`.
- Container-to-container on the same network needs **no host-published port**: use `postgres:5432` not `localhost:5432`. (Most common Docker networking mistake: `localhost` inside API = the API container.)

## Compose (full example)

```yaml
services:
  api:
    build: .
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/app
      REDIS_URL: redis://redis:6379
    depends_on: [postgres, redis]
  postgres:
    image: postgres:17
    environment: { POSTGRES_USER: postgres, POSTGRES_PASSWORD: password, POSTGRES_DB: app }
    volumes: [postgres-data:/var/lib/postgresql/data]
  redis:
    image: redis:7
volumes:
  postgres-data:
```

- `docker compose up` → one Docker network, three services, one volume.
- **`depends_on` = start order, not readiness.** The Postgres container can be running while Postgres initialises → need health/readiness + **application retry logic** (API starts → DB unavailable → wait → retry → serve).

## Resource limits, logs, immutability

- Limit CPU/memory so a leaking container can't starve the host (Kubernetes does this far better, later).
- **Log to stdout/stderr** (`console.log`, `console.error`) → `docker logs api` → cloud log collectors. Don't rely on files inside ephemeral containers.
- Container mindset: **build new image → deploy new container → replace old**; don't SSH, edit, restart.

## Tagging & registry

Tags: `my-api:1.4.2`, `my-api:git-a82f9c1` — avoid relying on `latest`. Workflow: `docker build` → `docker tag` → `docker push` → registry; elsewhere `docker pull` → `docker run`. In AWS: GitHub Actions → build → **Amazon ECR** → ECS/EKS/EC2.

Full CI/CD: push → lint → typecheck → tests → build → docker build (`my-api:commit-sha`) → image scan → push (ECR) → deploy → new container → health check → traffic.

## Troubleshooting framework

1. `docker ps` (running?) 2. `docker ps -a` (exited?) 3. `docker logs <c>` (why?) 4. `docker inspect <c>` 5. `docker exec -it <c> sh` 6. `docker network ls` / `docker network inspect <n>` 7. `docker port <c>`.

| Problem | Check |
|---|---|
| Container exits immediately | `docker logs` – app/process failure |
| Can't reach `localhost:3000` | App binding (`0.0.0.0`), port mapping, container status, firewall |
| API can't connect to PostgreSQL | Same network? hostname? port? credentials? DB ready? (`localhost` = API itself) |
| Image is huge | Base image, deps, layers, build artifacts, multi-stage, `.dockerignore` |
| Secret in image | Remove from image, **rotate the secret**, use runtime injection |

## Added (see supplement in the chapter)

`CMD` vs `ENTRYPOINT`; exec vs shell form & PID 1 signals; `USER node`; `--memory/--cpus`; Compose healthcheck + `service_healthy`; name resolution only on user-defined networks.

## Interview questions (29) — pointers

Docker/image vs container/VM/layer/registry/Dockerfile · `RUN` vs `CMD` · **`CMD` vs `ENTRYPOINT`** · `EXPOSE` · multi-stage why · copy `package.json` first · `.dockerignore` · non-root · secrets in images · stateless · immutable infrastructure · versioned tags · health checks · running vs healthy · minimise images · `-p 8080:3000` · container communication · why `localhost` fails across containers · don't hardcode IPs · debug exiting container · logs · exec · inspect · debug networking.

<!-- NAV -->

---

← [Sheet 7](ch07-revision.md) · [Full chapter 8](../docs/02-containers/ch08-docker-production.md) · [All revision material](README.md) · [Sheet 9](ch09-revision.md) →
