# Chapter 7 — Revision Sheet: Docker Fundamentals

> Supplements [the full chapter](../docs/02-containers/ch07-docker-fundamentals.md).

## Why Docker

"Works on my machine" (Node 22 vs Node 20, different OS, npm version, missing deps) → package **app + dependencies + runtime config** into an **image**, run it as a **container** anywhere. A container is an **isolated process environment sharing the host kernel — not a tiny VM**.

| VM | Container |
|---|---|
| Hypervisor + full guest OS per VM | Shares host OS kernel via container runtime |
| Heavier, slower to boot | Lighter, faster start, more efficient |
| Different isolation model | Isolated *process* — not "a small VM" |

## Core objects

- **Image** = immutable blueprint (class). **Container** = running/created instance (object). One image → many containers.
- **Dockerfile** (build recipe), **Registry** (Docker Hub / GHCR / ECR), **Volume** (persistent data), later **Network**, **Compose**.
- **Architecture:** Docker CLI → Docker Daemon → images, containers, networks, volumes.
- **Layers:** every instruction adds a cached layer; unchanged layers are reused → fast rebuilds.
- **Tags:** `repository:tag` (`my-api:1.0`, `latest`). Prefer immutable/version-specific tags in production.

## Dockerfile (TypeScript backend)

```dockerfile
FROM node:22                  # base image
WORKDIR /app                  # working dir for later instructions
COPY package*.json ./         # copy manifests first (cache!)
RUN npm ci                    # build-time: install deps
COPY . .                      # then the rest of the source
RUN npm run build             # build-time: compile TS
EXPOSE 3000                   # documentation only – does NOT publish
CMD ["node", "dist/index.js"] # default process at container START
```

| Instruction | Key point |
|---|---|
| `FROM` | Base image; images are built from other images |
| `WORKDIR` | Like `cd /app` for the rest of the file |
| `COPY` | Copy from build context into image |
| `RUN` | Executes **during image build** |
| `CMD` | Default process when the **container starts** |
| `EXPOSE` | Documents the port; you still need `-p` |

**Why copy `package*.json` first?** If you `COPY . .` before `npm ci`, any source change invalidates the dependency layer. Copying manifests first lets Docker reuse the cached `npm ci` layer when only source changes.

**Build:** `docker build -t my-api:1.0 .` — `-t` names/tags, `.` = **build context** (files Docker may `COPY`).
**`.dockerignore`:** `node_modules`, `.git`, `.env`, `dist`, `npm-debug.log` — keeps junk and especially secrets out of the context.

## Commands

| Task | Command |
|---|---|
| Check | `docker --version`, `docker info`, `docker help` |
| Pull / list | `docker pull node:22`, `docker images` |
| Run | `docker run hello-world`, `docker run node:22 node --version`, `docker run -it ubuntu bash` (`-i` interactive, `-t` terminal), `docker run -d nginx` (detached), `docker run -d --name my-nginx nginx` |
| Lifecycle | `docker ps` (running), `docker ps -a` (all), `docker stop/start/restart/rm my-nginx` |
| Debug | `docker logs my-nginx`, `docker logs -f my-nginx`, `docker exec -it my-nginx bash` (or `sh` if no bash), `docker inspect` |
| Ports | `docker run -p 3000:3000 my-api` → `-p HOST_PORT:CONTAINER_PORT` |
| Env | `docker run -e DB_PASSWORD="..." my-api:1.0` |
| Volumes | `docker volume create postgres-data`; `docker run -v postgres-data:/var/lib/postgresql/data postgres` |
| Registry | `docker push`, `docker pull my-api:1.0` |
| Compose | `docker compose up` |

**Stop ≠ remove:** `docker stop` leaves the container (visible in `docker ps -a`); `docker rm` deletes it.
**Lifecycle:** Created → Running → Stopped → Removed. A container normally exists to run a process; when the **main process exits, the container stops** (e.g. `exit` from the shell).

## Networking & ports

- Inside a container **`localhost` = the container itself** — not your laptop, not another container.
- Bind Node to **`0.0.0.0`** (`app.listen(3000, "0.0.0.0")`) so the server is reachable through the container's network interface. Then publish with `-p`.
- Request path: Browser → `localhost:3000` → Docker host port 3000 → container port 3000 → Node.js.
- Containers can talk to each other via Docker networks without exposing every service to the host (deep dive: [Chapter 8](../docs/02-containers/ch08-docker-production.md)).

## Persistence

- Container writable layers aren't a good home for important data; removing the container loses it.
- **Volume** = Docker-managed persistent storage. **Bind mount** = host path ↔ container (good for local dev: `-v ./src:/app/src`; see note below).
- **Stateless containers:** keep user data in DB/persistent storage so app containers can be replaced freely — key for scaling, Kubernetes and cloud.
- **One main process per container** (Node, Redis, PostgreSQL in separate containers) → easier scaling and lifecycle management (exceptions exist).

## Compose preview

```yaml
services:
  api:
    build: .
    ports: ["3000:3000"]
  postgres:
    image: postgres:17
  redis:
    image: redis:7
```

## Docker vs Kubernetes

Docker = build, package, run, distribute containers. Kubernetes = orchestrate at scale: deploy, scale, network, self-heal, roll out, roll back.

## Same image everywhere

Developer machine → image → CI/CD → registry → AWS → Kubernetes. The **same image** moves Testing → Staging → Production.

## Secrets

Never hardcode (`const dbPassword = "mypassword"`); read `process.env.DB_PASSWORD`. Don't copy `.env`/secrets into images. In real production use secret-management systems rather than command history/deployment files.

## Scenario — "works locally, not in Docker"

1. Container running? (`docker ps`) 2. Crashed? (`docker logs`) 3. Correct port? 4. Bound to `0.0.0.0`? 5. Port published (`-p 3000:3000`)? 6. Dockerfile correct (COPY/RUN/CMD)? 7. Env vars present (`docker exec`)? 8. Another service unreachable → Docker networking.

## Verification notes (see [Corrections](../CORRECTIONS.md))

- Relative paths in `docker run -v ./src:/app/src` — use `-v "$(pwd)/src:/app/src"` to be safe.
- Official `postgres` image layout changed in newer major versions; check the image README when mounting the data volume.

## Interview questions (22) — pointers

Docker; container vs VM; image vs container; Dockerfile; `FROM`; `RUN` vs `CMD`; what `EXPOSE` does; meaning of `-p 3000:3000`; why `0.0.0.0`; layers; why caching helps; registry; volume; volume vs bind mount; why state shouldn't live only in a container; `.dockerignore`; why `.env` must not be in an image; what `docker run nginx` does (find image → pull if absent → create → start → process runs); view logs; exec into container; what happens when the main process exits; why stateless containers scale.

<!-- NAV -->

---

← [Sheet 6](ch06-revision.md) · [Full chapter 7](../docs/02-containers/ch07-docker-fundamentals.md) · [All revision material](README.md) · [Sheet 8](ch08-revision.md) →
