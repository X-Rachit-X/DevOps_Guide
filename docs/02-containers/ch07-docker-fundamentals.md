# Chapter 7 — Docker Fundamentals

> **Source:** Response 7 of the original conversation (`source-archive/src-07.txt`, lines 1–1716) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch07-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

Now we move into one of the **most important technologies in modern backend + DevOps interviews**.

You should eventually be able to take your TypeScript/Node.js backend, containerize it, run it locally, connect it to a database, and understand how that same image can move through CI/CD into AWS/Kubernetes.

This response focuses on the **fundamentals**. [Chapter 8](ch08-docker-production.md) will go deeper into production Docker.

---

## 1. The Problem Docker Solves

Imagine your Node.js application works perfectly on your laptop.

```text
Your Laptop
Node 22
npm packages
Environment variables
OS configuration
```

You give it to another developer:

```text
Other Laptop
Node 20
Different OS
Different npm version
Missing dependency
```

Suddenly:

```text
❌ It works on my machine.
```

Docker addresses this by packaging the application and its environment requirements into a **container image**.

Conceptually:

```text
Application
+
Dependencies
+
Runtime configuration
        ↓
    Docker Image
        ↓
    Container
```

---

## 2. What Is Docker?

Docker is a platform/tooling ecosystem for building, distributing, and running applications in **containers**.

A container provides an isolated execution environment for a process and its dependencies while sharing the host operating system's kernel.

Think:

> **A container is an isolated process environment, not a complete virtual machine.**

---

## 3. VM vs Container

This distinction is extremely important.

#### Virtual Machine

```text
Physical Machine
       ↓
Hypervisor
       ↓
┌──────────────┐
│ VM           │
│ Guest OS     │
│ Application  │
└──────────────┘

┌──────────────┐
│ VM           │
│ Guest OS     │
│ Application  │
└──────────────┘
```

Each VM normally has its own guest operating system.

---

#### Containers

```text
Physical/Cloud Machine
       ↓
Host OS Kernel
       ↓
Container Runtime
       ↓
┌──────────┐ ┌──────────┐ ┌──────────┐
│ App      │ │ App      │ │ App      │
│ Libraries│ │ Libraries│ │ Libraries│
└──────────┘ └──────────┘ └──────────┘
```

Containers share the host kernel.

Therefore containers are generally:

- lighter
- faster to start
- more efficient in resource usage

than full VMs.

But they provide a different isolation model and are **not simply "tiny VMs."**

---

## 4. Docker's Core Concepts

You need to understand these five first:

```text
Image
Container
Dockerfile
Registry
Volume
```

And later:

```text
Network
Compose
```

---

## 5. Docker Image

An image is a packaged, immutable template used to create containers.

For example:

```text
node:22
```

is a Node.js image.

You can build your own:

```text
my-api:1.0
```

Think:

```text
Image = blueprint
Container = running instance
```

Similar idea:

```text
Class
 ↓
Object
```

Not exactly the same technically, but useful intuition.

---

## 6. Container

A container is a running or created instance of an image.

```text
Image
  ↓
docker run
  ↓
Container
```

For example:

```bash
docker run node:22
```

Docker creates a container from the Node image.

---

## 7. Image vs Container

Very common interview question:

> What's the difference between a Docker image and a container?

Answer:

> **An image is an immutable packaged template containing the application and its required filesystem/dependencies. A container is an isolated running or created instance of that image.**

Example:

```text
node:22 image
      │
      ├── container A
      ├── container B
      └── container C
```

One image can create many containers.

---

## 8. Docker Architecture

At a high level:

```text
                 Docker CLI
                    │
                    ↓
              Docker Daemon
                    │
       ┌────────────┼────────────┐
       ↓            ↓            ↓
    Images      Containers     Networks
                                  │
                               Volumes
```

The Docker CLI is what you interact with:

```bash
docker build
docker run
docker ps
docker images
```

The Docker daemon manages Docker objects and operations.

---

## 9. Docker CLI

Check Docker:

```bash
docker --version
```

Check information:

```bash
docker info
```

List available commands:

```bash
docker help
```

---

## 10. Your First Container

Run:

```bash
docker run hello-world
```

Docker will:

```text
Find image
   ↓
Download image if needed
   ↓
Create container
   ↓
Start container
   ↓
Application executes
   ↓
Container exits
```

---

## 11. Pulling Images

You can explicitly download an image:

```bash
docker pull node:22
```

Then:

```bash
docker images
```

You might see:

```text
REPOSITORY   TAG    IMAGE ID
node         22     ...
```

---

## 12. Running Node.js

Try:

```bash
docker run node:22 node --version
```

Conceptually:

```text
Node image
    ↓
Container
    ↓
node --version
    ↓
v22.x.x
    ↓
process exits
```

This demonstrates an important idea:

> **A container normally exists to run a process.**

---

## 13. Container Lifecycle

A container can go through states such as:

```text
Created
   ↓
Running
   ↓
Stopped
   ↓
Removed
```

Commands:

```bash
docker ps
```

shows running containers.

```bash
docker ps -a
```

shows running + stopped containers.

---

## 14. Start an Interactive Container

Try:

```bash
docker run -it ubuntu bash
```

Meaning:

```text
-i → interactive
-t → terminal
```

Now you're inside the container.

Try:

```bash
ls
```

or:

```bash
cat /etc/os-release
```

Exit:

```bash
exit
```

The container stops if its main process was the shell.

---

## 15. Detached Mode

For a long-running application:

```bash
docker run -d nginx
```

`-d` means detached mode.

Your terminal returns immediately.

Check:

```bash
docker ps
```

You'll see the container running.

---

## 16. Container Names

Docker can automatically generate names.

You can provide one:

```bash
docker run -d --name my-nginx nginx
```

Now:

```bash
docker ps
```

shows:

```text
my-nginx
```

instead of relying on an autogenerated name.

---

## 17. Stop and Start

Stop:

```bash
docker stop my-nginx
```

Start again:

```bash
docker start my-nginx
```

Restart:

```bash
docker restart my-nginx
```

Remove:

```bash
docker rm my-nginx
```

---

## 18. Important Distinction: Stop vs Remove

This is frequently misunderstood.

```bash
docker stop my-nginx
```

means:

> Stop the container.

The container still exists.

```bash
docker rm my-nginx
```

means:

> Remove the container.

You can verify with:

```bash
docker ps -a
```

---

## 19. Logs

Suppose your application is running:

```bash
docker run -d --name my-nginx nginx
```

View logs:

```bash
docker logs my-nginx
```

Follow logs:

```bash
docker logs -f my-nginx
```

This connects directly to the Linux debugging concepts you learned earlier.

---

## 20. Executing Commands Inside Containers

Suppose:

```text
my-nginx
```

is running.

You can execute:

```bash
docker exec -it my-nginx bash
```

Now you're inside the running container.

For images that don't contain Bash, you may need:

```bash
docker exec -it my-nginx sh
```

This is an important production debugging technique.

---

## 21. Port Mapping

This is one of the most important Docker concepts.

Suppose your application listens inside the container on:

```text
3000
```

That does **not automatically mean** your host's port 3000 reaches it.

You can map:

```text
Host:3000
      ↓
Container:3000
```

with:

```bash
docker run -p 3000:3000 my-api
```

Format:

```text
-p HOST_PORT:CONTAINER_PORT
```

---

## 22. Node.js Example

Suppose your application has:

```typescript
import express from "express";

const app = express();

app.get("/", (_req, res) => {
  res.json({ message: "Hello Docker" });
});

app.listen(3000, "0.0.0.0", () => {
  console.log("Server running on port 3000");
});
```

The important part:

```typescript
app.listen(3000, "0.0.0.0");
```

Inside a container, binding to `0.0.0.0` is usually necessary when you want the application reachable through the container's network interface.

Then:

```bash
docker run -p 3000:3000 my-api
```

Request:

```text
Browser
   ↓
localhost:3000
   ↓
Docker host port 3000
   ↓
Container port 3000
   ↓
Node.js
```

---

## 23. Why `localhost` Can Cause Problems

This is a classic Docker debugging issue.

Inside the container:

```text
localhost
```

means:

> **this container itself**

It does not mean:

> your laptop

or:

> another container.

This becomes extremely important when we discuss Docker networking.

---

## 24. Dockerfile

Now we get to the most important practical concept.

A **Dockerfile** contains instructions for building an image.

Example TypeScript backend:

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

Let's understand it line by line.

---

## 25. `FROM`

```dockerfile
FROM node:22
```

This selects the base image.

Your image starts from:

```text
Node.js 22 environment
```

Docker images are often built from other images.

```text
node:22
   ↓
your Dockerfile
   ↓
my-api
```

---

## 26. `WORKDIR`

```dockerfile
WORKDIR /app
```

Sets the working directory.

Commands afterward operate from:

```text
/app
```

Instead of repeatedly doing:

```bash
cd /app
```

---

## 27. `COPY`

```dockerfile
COPY package*.json ./
```

Copies package files into the image.

Then:

```dockerfile
RUN npm ci
```

installs dependencies.

Then:

```dockerfile
COPY . .
```

copies the rest of the application.

---

## 28. Why Copy `package.json` First?

This introduces an important Docker optimization.

Suppose your Dockerfile was:

```dockerfile
COPY . .
RUN npm ci
```

Every source-code change could invalidate the dependency installation layer.

Instead:

```dockerfile
COPY package*.json ./
RUN npm ci

COPY . .
```

means Docker can potentially reuse the dependency layer when only application source code changes.

This becomes even more important in [Chapter 8](ch08-docker-production.md).

---

## 29. `RUN`

```dockerfile
RUN npm ci
```

executes a command **while building the image**.

Another:

```dockerfile
RUN npm run build
```

compiles TypeScript.

Remember:

```text
Docker build
     ↓
RUN commands
     ↓
Image created
```

---

## 30. `CMD`

```dockerfile
CMD ["node", "dist/index.js"]
```

defines the default command used when the container starts.

So:

```bash
docker run my-api
```

effectively starts:

```bash
node dist/index.js
```

---

## 31. `CMD` vs `RUN`

Very important.

#### RUN

Happens during **image build**.

```dockerfile
RUN npm ci
```

#### CMD

Defines the default process when a **container starts**.

```dockerfile
CMD ["node", "dist/index.js"]
```

Think:

```text
docker build
    ↓
RUN
    ↓
IMAGE
    ↓
docker run
    ↓
CMD
    ↓
CONTAINER PROCESS
```

---

## 32. `EXPOSE`

```dockerfile
EXPOSE 3000
```

This documents that the application intends to listen on port 3000.

It does **not itself publish the port to your host**.

You still need:

```bash
docker run -p 3000:3000 my-api
```

Excellent interview trick.

---

## 33. Build the Image

Suppose your project contains:

```text
Dockerfile
package.json
package-lock.json
src/
tsconfig.json
```

Build:

```bash
docker build -t my-api:1.0 .
```

Meaning:

```text
docker build
       │
       ├── -t my-api:1.0
       │
       └── .  ← build context
```

---

## 34. Build Context

The final:

```text
.
```

means:

> Use the current directory as the build context.

Docker can access files within that context for instructions such as:

```dockerfile
COPY
```

This is why you should be careful about what is in your build context.

---

## 35. Run Your Image

After:

```bash
docker build -t my-api:1.0 .
```

run:

```bash
docker run -p 3000:3000 --name my-api my-api:1.0
```

Then:

```text
Browser
 ↓
localhost:3000
 ↓
Docker
 ↓
my-api container
 ↓
Node.js
```

---

## 36. `.dockerignore`

You should usually have:

```text
.dockerignore
```

Example:

```text
node_modules
.git
.env
dist
npm-debug.log
```

Why?

Because you don't want to send unnecessary files into the Docker build context.

Especially:

```text
.env
```

because it may contain secrets.

---

## 37. Environment Variables

Don't hardcode configuration:

```typescript
const dbPassword = "mypassword";
```

Instead:

```typescript
const dbPassword = process.env.DB_PASSWORD;
```

Then run:

```bash
docker run \
  -e DB_PASSWORD="..." \
  my-api:1.0
```

Now:

```text
Container
   ↓
process.env.DB_PASSWORD
```

gets the value.

For real production systems, secrets should generally come from proper secret-management mechanisms rather than being casually placed in command history or deployment files.

---

## 38. Docker Images Have Layers

A Docker image is built from layers.

For example:

```dockerfile
FROM node:22

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build
```

Conceptually:

```text
┌────────────────────┐
│ Build output       │
├────────────────────┤
│ Source code        │
├────────────────────┤
│ npm dependencies   │
├────────────────────┤
│ Working filesystem │
├────────────────────┤
│ Node base image    │
└────────────────────┘
```

Docker can reuse unchanged layers.

This is one reason Docker builds can be fast after the initial build.

---

## 39. Image Tags

You can have:

```text
my-api:1.0
my-api:1.1
my-api:latest
```

Format:

```text
repository:tag
```

For production, we'll later discuss why immutable/version-specific tags are preferable to relying on `latest`.

---

## 40. Docker Registry

A registry stores and distributes images.

Examples:

```text
Docker Hub
GitHub Container Registry
Amazon ECR
```

Conceptually:

```text
Developer
   ↓
docker build
   ↓
Image
   ↓
docker push
   ↓
Registry
```

Another machine can then:

```bash
docker pull my-api:1.0
```

and run it.

---

## 41. The Real Power of Docker

Suppose:

```text
Developer machine
       ↓
Docker image
       ↓
CI/CD
       ↓
Registry
       ↓
AWS
       ↓
Kubernetes
```

The same application artifact can move through environments.

```text
                    SAME IMAGE
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
       Testing      Staging      Production
```

This greatly reduces "works on my machine" problems.

---

## 42. Docker Networking — Basic Idea

Suppose you have:

```text
Node API
   +
PostgreSQL
```

You could run:

```text
Container A
Node.js

Container B
PostgreSQL
```

They need to communicate.

Docker provides networking mechanisms that allow containers to communicate without exposing every internal service directly to the host.

Later we'll go much deeper into this.

---

## 43. Docker Volumes

Containers have writable filesystem layers, but container-local data is not a good default place for important persistent data.

For example:

```text
PostgreSQL container
       ↓
Database files
```

If the container is removed, you don't want your database to disappear.

A **volume** provides persistent storage managed separately from the container lifecycle.

Conceptually:

```text
Container
   │
   ↓
Volume
   │
   ↓
Persistent data
```

Create:

```bash
docker volume create postgres-data
```

Then:

```bash
docker run \
  -v postgres-data:/var/lib/postgresql/data \
  postgres
```

Now the database data lives in the volume.

---

## 44. Bind Mounts vs Volumes

#### Bind mount

Maps a host path:

```bash
-v ./src:/app/src
```

Useful during local development.

#### Named volume

Managed by Docker:

```bash
-v postgres-data:/var/lib/postgresql/data
```

Often useful for persistent container data.

Think:

```text
Bind mount
Host directory ↔ Container

Volume
Docker-managed storage ↔ Container
```

---

## 45. Why Containers Should Usually Be Stateless

Suppose you have:

```text
API Container A
API Container B
API Container C
```

You don't want important user data stored only inside Container A.

Why?

Container A could disappear.

Instead:

```text
API
 ↓
Database
 ↓
Persistent storage
```

The application containers can be replaced freely.

This principle becomes extremely important in Kubernetes and cloud architecture.

---

## 46. One Main Process

A common container design principle is:

> A container should generally have one primary responsibility/process.

For example:

```text
Container 1 → Node API
Container 2 → Redis
Container 3 → PostgreSQL
```

Rather than:

```text
One container
 ├── Node
 ├── PostgreSQL
 ├── Redis
 └── Nginx
```

This makes scaling and lifecycle management easier.

There are exceptions and specialized designs, but this is the standard mental model.

---

## 47. Docker Compose — Preview

If you have:

```text
Node API
PostgreSQL
Redis
```

managing three separate `docker run` commands becomes annoying.

Docker Compose lets you describe a multi-container application declaratively.

Example:

```yaml
services:
  api:
    build: .
    ports:
      - "3000:3000"

  postgres:
    image: postgres:17

  redis:
    image: redis:7
```

Then:

```bash
docker compose up
```

creates the required services.

We'll cover Compose properly in [Chapter 8](ch08-docker-production.md).

---

## 48. Docker vs Kubernetes

Don't confuse these.

#### Docker

Primarily helps you:

```text
Build
Package
Run
Distribute
```

containers.

#### Kubernetes

Helps you manage containers at scale:

```text
Deploy
Scale
Network
Self-heal
Roll out
Roll back
```

across a cluster.

Conceptually:

```text
Docker
   ↓
Containerization

Kubernetes
   ↓
Container orchestration
```

We'll reach Kubernetes in Chapters [18](../05-kubernetes/ch18-kubernetes-fundamentals.md)–[20](../05-kubernetes/ch20-kubernetes-networking-scaling.md).

---

## 49. Complete Docker Workflow

You should now visualize:

```text
             Source Code
                  │
                  ↓
             Dockerfile
                  │
                  ↓
             docker build
                  │
                  ↓
              Docker Image
                  │
          ┌───────┴───────┐
          ↓               ↓
       Registry         Local
          │
          ↓
      docker pull
          │
          ↓
       Container
          │
     ┌────┴────┐
     ↓         ↓
   Network   Volume
```

---

## 50. What You Should Be Able to Do Now

By the end of Chapter 7, you should be comfortable with:

#### Commands

```bash
docker pull
docker images
docker build
docker run
docker ps
docker ps -a
docker stop
docker start
docker restart
docker rm
docker logs
docker exec
docker inspect
docker volume
```

#### Dockerfile

Understand:

```dockerfile
FROM
WORKDIR
COPY
RUN
EXPOSE
CMD
```

#### Concepts

```text
Image
Container
Registry
Layer
Build context
Port mapping
Environment variables
Volumes
Networks
Container lifecycle
Container vs VM
```

---

## 🧪 Practical Lab

Create a small TypeScript API.

#### Step 1 — Build normally

```bash
npm install
npm run build
npm start
```

Verify:

```text
localhost:3000
```

#### Step 2 — Create Dockerfile

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

#### Step 3 — Create `.dockerignore`

```text
node_modules
.git
.env
dist
```

#### Step 4 — Build

```bash
docker build -t my-api:1.0 .
```

#### Step 5 — Run

```bash
docker run -p 3000:3000 --name my-api my-api:1.0
```

#### Step 6 — Check

```bash
docker ps
docker logs my-api
```

#### Step 7 — Debug

```bash
docker exec -it my-api sh
```

Explore:

```bash
ls
```

Then:

```bash
exit
```

---

## 🎯 Interview Questions

Make sure you can explain these in simple language:

1. What is Docker?
2. Docker container vs VM?
3. Image vs container?
4. What is a Dockerfile?
5. What does `FROM` do?
6. `RUN` vs `CMD`?
7. What does `EXPOSE` actually do?
8. What does `-p 3000:3000` mean?
9. Why use `0.0.0.0` in a containerized Node server?
10. What is a Docker layer?
11. Why is Docker caching useful?
12. What is a Docker registry?
13. What is a volume?
14. Volume vs bind mount?
15. Why shouldn't important application state live only inside a container?
16. What is `.dockerignore`?
17. Why shouldn't `.env` or secrets be copied into an image?
18. What happens when you run `docker run nginx`?
19. How do you inspect container logs?
20. How do you execute a command inside a running container?
21. What happens when a container's main process exits?
22. Why are stateless containers useful for scaling?

---

## 🔥 One Scenario You Should Understand

Interviewer:

> "Your Node.js application works locally but doesn't respond when running inside Docker. What would you check?"

Think systematically:

```text
1. Is container running?
       ↓
docker ps

2. Did application crash?
       ↓
docker logs

3. Is Node listening on correct port?
       ↓
3000

4. Is it bound to 0.0.0.0?
       ↓
not only localhost

5. Did you publish the port?
       ↓
-p 3000:3000

6. Is Dockerfile correct?
       ↓
COPY / RUN / CMD

7. Are environment variables present?
       ↓
docker exec / configuration

8. Is another service unreachable?
       ↓
Docker networking
```

That's **DevOps troubleshooting thinking**, rather than memorizing Docker commands.
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 6: CI/CD + GitHub Actions](../03-cicd-gitops/ch06-cicd-github-actions.md) · [Chapter 8: Docker Deep Dive + Production](ch08-docker-production.md) → · [Revision sheet](../../revision/ch07-revision.md)
