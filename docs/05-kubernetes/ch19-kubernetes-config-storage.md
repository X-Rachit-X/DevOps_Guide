# Chapter 19 — Kubernetes Configuration + Storage

> **Source:** Response 19 of the original conversation (`source-archive/src-19.txt`, lines 1–1677) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch19-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

We're continuing exactly from [Chapter 18](ch18-kubernetes-fundamentals.md).

The key problem now is:

> **How do we give our containers configuration, secrets, resources, and persistent data without hardcoding everything inside the Docker image?**

We'll go from **concept → YAML → actual commands → Node.js usage → debugging → interview level**.

---

## 1. The Problem We're Solving

Our application currently looks like:

```text
Deployment
   ↓
Pods
   ↓
Node.js Container
```

But a real application needs:

```text
PORT=3000
NODE_ENV=production
DATABASE_URL=...
REDIS_URL=...
JWT_SECRET=...
```

And potentially:

```text
uploaded files
database data
logs
application state
```

We don't want to:

```text
❌ hardcode secrets into code
❌ bake environment configuration into Docker images
❌ lose important data when a Pod dies
```

Kubernetes gives us several mechanisms.

---

## 2. Configuration Mental Model

Think of Kubernetes configuration as:

```text
                    Configuration
                         │
              ┌──────────┴──────────┐
              ↓                     ↓
          ConfigMap              Secret
              │                     │
        non-sensitive           sensitive
              │                     │
              └──────────┬──────────┘
                         ↓
                        Pod
                         ↓
                    Container
```

Storage is separate:

```text
Pod
 │
 └── Volume
       ↓
   Persistent storage
```

---

## PART 1 — CONFIGMAP

## 3. What Is a ConfigMap?

A **ConfigMap** stores non-sensitive configuration.

Examples:

```text
NODE_ENV=production
PORT=3000
LOG_LEVEL=info
API_TIMEOUT=5000
```

Create:

```yaml
apiVersion: v1
kind: ConfigMap

metadata:
  name: api-config

data:
  NODE_ENV: production
  PORT: "3000"
  LOG_LEVEL: info
```

Apply:

```bash
kubectl apply -f configmap.yaml
```

Check:

```bash
kubectl get configmap
```

Inspect:

```bash
kubectl describe configmap api-config
```

---

## 4. Using ConfigMap as Environment Variables

Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: api

spec:
  replicas: 2

  selector:
    matchLabels:
      app: api

  template:
    metadata:
      labels:
        app: api

    spec:
      containers:
        - name: api
          image: my-api:1.0

          envFrom:
            - configMapRef:
                name: api-config

          ports:
            - containerPort: 3000
```

Now the container receives:

```text
NODE_ENV=production
PORT=3000
LOG_LEVEL=info
```

Check:

```bash
kubectl exec -it <pod-name> -- env
```

You'll see the variables.

---

## 5. ConfigMap vs `.env`

In local development you might have:

```text
.env
```

For example:

```env
PORT=3000
NODE_ENV=development
```

That's fine for local development.

Kubernetes provides a way to inject configuration into Pods.

So:

```text
Local:
.env

Kubernetes:
ConfigMap / Secret
```

But don't assume Kubernetes ConfigMaps automatically replace every configuration-management system in production. Larger environments may use external secret/configuration systems.

---

## PART 2 — SECRETS

## 6. Why Secrets?

Suppose we have:

```text
DATABASE_PASSWORD
JWT_SECRET
AWS credentials
API keys
```

These shouldn't go into:

```yaml
ConfigMap
```

Use:

```text
Secret
```

---

## 7. Creating a Secret

For learning:

```bash
kubectl create secret generic api-secret \
  --from-literal=DB_PASSWORD='supersecret'
```

Check:

```bash
kubectl get secrets
```

Describe:

```bash
kubectl describe secret api-secret
```

Notice that `describe` doesn't simply print the secret value.

---

## 8. Using a Secret

Deployment:

```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: api-secret
        key: DB_PASSWORD
```

Now inside the container:

```text
DB_PASSWORD=supersecret
```

Your Node.js application can read it:

```ts
const password = process.env.DB_PASSWORD;
```

---

## 9. Important Kubernetes Secret Security Point

You will often hear:

> "Kubernetes Secrets are encrypted."

That's an oversimplification.

Historically, Secret manifests commonly contain **base64-encoded** values.

Base64 is **not encryption**.

For example:

```text
hello
 ↓
aGVsbG8=
```

Anyone can decode that.

So:

```text
Base64 ≠ encryption
```

Production clusters should use appropriate encryption-at-rest and access controls, and production AWS applications can integrate with systems such as:

```text
AWS Secrets Manager
```

We'll connect this with the AWS security knowledge from [Chapter 17](../04-aws/ch17-monitoring-security.md).

---

## 10. ConfigMap vs Secret

| Feature | ConfigMap | Secret |
|---|---|---|
| Normal configuration | ✅ | |
| Passwords | | ✅ |
| API keys | | ✅ |
| Environment settings | ✅ | |
| Sensitive values | | ✅ |
| Port numbers | ✅ | |
| JWT secret | | ✅ |

Mental shortcut:

> **ConfigMap = configuration. Secret = sensitive configuration.**

---

## PART 3 — VOLUMES

## 11. Why Do Containers Need Volumes?

Remember Docker.

Containers are generally treated as ephemeral.

Suppose:

```text
Pod
 ↓
Container
 ↓
/app/data/file.txt
```

Container gets destroyed.

That data may disappear with it.

Kubernetes therefore provides **Volumes**.

---

## 12. Basic Kubernetes Volume

Example:

```yaml
volumes:
  - name: app-data
    emptyDir: {}
```

Mount it:

```yaml
containers:
  - name: api
    image: my-api:1.0

    volumeMounts:
      - name: app-data
        mountPath: /app/data
```

Now:

```text
Pod
 │
 └── /app/data
        ↓
     Volume
```

---

## 13. What Is `emptyDir`?

`emptyDir` creates temporary storage associated with the Pod.

Example:

```text
Pod
 └── emptyDir
```

Useful for:

- temporary files
- scratch space
- intermediate processing
- cache-like temporary data

But:

> **Do not use `emptyDir` for data that must survive Pod replacement.**

When the Pod is removed, the `emptyDir` contents disappear.

---

## 14. Example

```yaml
apiVersion: v1
kind: Pod

metadata:
  name: storage-demo

spec:
  containers:
    - name: app
      image: nginx

      volumeMounts:
        - name: data
          mountPath: /data

  volumes:
    - name: data
      emptyDir: {}
```

Apply:

```bash
kubectl apply -f storage.yaml
```

Enter:

```bash
kubectl exec -it storage-demo -- sh
```

Create:

```bash
echo "hello" > /data/test.txt
```

Check:

```bash
cat /data/test.txt
```

The file exists.

But if the Pod itself is removed:

```bash
kubectl delete pod storage-demo
```

and a completely new Pod is created, the `emptyDir` data won't persist.

---

## PART 4 — PERSISTENT STORAGE

Now consider:

```text
PostgreSQL
```

You absolutely don't want:

```text
Pod dies
 ↓
Database data disappears
```

We need persistent storage.

---

## 15. PersistentVolume

A **PersistentVolume (PV)** represents persistent storage available to Kubernetes.

Conceptually:

```text
Persistent Storage
       ↓
      PV
       ↓
      Pod
```

The actual storage may come from cloud/block/file storage depending on the Kubernetes environment.

---

## 16. PersistentVolumeClaim

Applications generally shouldn't have to care about the exact physical disk.

Instead, the application requests storage through a:

> **PersistentVolumeClaim (PVC)**

Think:

```text
Application
    ↓
PVC
    ↓
PV
    ↓
Actual Storage
```

The PVC says:

> "I need 20 GiB of persistent storage."

---

## 17. PVC Example

```yaml
apiVersion: v1
kind: PersistentVolumeClaim

metadata:
  name: api-storage

spec:
  accessModes:
    - ReadWriteOnce

  resources:
    requests:
      storage: 5Gi
```

Apply:

```bash
kubectl apply -f pvc.yaml
```

Check:

```bash
kubectl get pvc
```

You'll see something like:

```text
NAME           STATUS
api-storage    Bound
```

---

## 18. Mount PVC Into Pod

```yaml
apiVersion: v1
kind: Pod

metadata:
  name: storage-app

spec:
  containers:
    - name: app
      image: nginx

      volumeMounts:
        - name: persistent-data
          mountPath: /data

  volumes:
    - name: persistent-data
      persistentVolumeClaim:
        claimName: api-storage
```

Now:

```text
Pod
 ↓
/data
 ↓
PVC
 ↓
PV
 ↓
Persistent storage
```

---

## 19. Why This Matters

Suppose:

```text
Pod A
 ↓
/data
 ↓
PVC
```

Pod A dies.

Deployment creates:

```text
Pod B
```

Pod B can mount the same claim according to the storage/access-mode constraints.

Therefore:

```text
Pod A ❌
      ↓
PVC
      ↓
Pod B ✅
```

The storage isn't tied to the lifecycle of one ephemeral Pod.

---

## PART 5 — STORAGECLASS

## 20. What Is StorageClass?

In cloud environments, you don't normally manually create every PV.

A `StorageClass` describes how storage can be dynamically provisioned.

Conceptually:

```text
PVC
 ↓
StorageClass
 ↓
Cloud storage provisioned
 ↓
PV
```

This is called:

> **Dynamic provisioning**

For example, on AWS, Kubernetes can work with cloud storage through the relevant CSI drivers.

---

## 21. Kubernetes Storage on AWS

This connects directly to your AWS knowledge.

Common concepts include:

```text
EBS
EFS
```

#### EBS

Block storage.

Useful for workloads requiring block storage semantics.

#### EFS

Managed network file storage.

Useful when multiple workloads need shared file storage under appropriate access patterns.

Mental model:

```text
Kubernetes
    ↓
CSI driver
    ↓
AWS storage
```

You don't need to memorize every CSI implementation detail for SWE interviews.

---

## PART 6 — REQUESTS & LIMITS

This is another important production concept.

Suppose a Node.js container consumes CPU.

Kubernetes needs to know:

> How much resource should this workload request?

---

## 22. Requests

Example:

```yaml
resources:
  requests:
    cpu: "250m"
    memory: "256Mi"
```

This means:

> Kubernetes should reserve/schedule the workload based on approximately these requested resources.

---

## 23. Limits

```yaml
resources:
  limits:
    cpu: "500m"
    memory: "512Mi"
```

This specifies a maximum resource boundary for the container under Kubernetes resource management.

Example:

```yaml
resources:
  requests:
    cpu: "250m"
    memory: "256Mi"

  limits:
    cpu: "500m"
    memory: "512Mi"
```

Mental model:

```text
Request
→ what the workload asks/reserves for scheduling

Limit
→ maximum resource boundary
```

These become very important when we get to autoscaling.

---

## 24. Why Resources Matter

Imagine:

```text
Pod A → memory hungry
Pod B → memory hungry
Pod C → memory hungry
```

Without resource management, workloads can interfere with each other.

With requests/limits:

```text
Kubernetes
    ↓
Scheduling decisions
    +
Resource constraints
```

This becomes especially important in production clusters.

---

## PART 7 — HEALTH PROBES

We touched on this earlier.

Your application needs to tell Kubernetes:

> "Am I alive?"

and:

> "Am I ready to receive traffic?"

These are different questions.

---

## 25. Liveness Probe

Liveness asks:

> Is the application alive?

Example:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 3000

  initialDelaySeconds: 10
  periodSeconds: 15
```

If the container gets into a broken state and repeatedly fails its liveness probe, Kubernetes can restart the container according to the configured behavior.

---

## 26. Readiness Probe

Readiness asks:

> Can this instance receive traffic right now?

Example:

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 3000

  initialDelaySeconds: 5
  periodSeconds: 10
```

This is extremely important for backend applications.

Imagine:

```text
New Pod starts
 ↓
Node.js starts
 ↓
Database connection isn't ready
```

You don't want traffic immediately hitting it.

Readiness can prevent the Pod from being considered ready for traffic until it passes the readiness condition.

---

## 27. Liveness vs Readiness

Remember:

```text
Liveness
→ Should Kubernetes restart this container?

Readiness
→ Should this Pod receive traffic?
```

Example:

```text
Pod running
      ↓
Database temporarily unavailable
      ↓
Readiness ❌
      ↓
Don't send traffic
```

The container may still be alive.

That's why readiness and liveness are **not interchangeable**.

---

## PART 8 — COMPLETE NODE.JS DEPLOYMENT

Now let's combine what we've learned.

Imagine your Node API has:

```text
/health
/ready
```

and needs:

```text
PORT
NODE_ENV
DATABASE_URL
JWT_SECRET
```

---

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap

metadata:
  name: api-config

data:
  NODE_ENV: production
  PORT: "3000"
```

---

### Secret

```bash
kubectl create secret generic api-secret \
  --from-literal=DATABASE_URL='postgresql://user:password@db:5432/app' \
  --from-literal=JWT_SECRET='change-me'
```

For a real production environment, don't casually commit this command containing credentials into Git.

---

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: api

spec:
  replicas: 3

  selector:
    matchLabels:
      app: api

  template:
    metadata:
      labels:
        app: api

    spec:
      containers:
        - name: api
          image: my-api:1.0

          ports:
            - containerPort: 3000

          envFrom:
            - configMapRef:
                name: api-config

          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: api-secret
                  key: DATABASE_URL

            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: api-secret
                  key: JWT_SECRET

          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"

            limits:
              cpu: "500m"
              memory: "512Mi"

          readinessProbe:
            httpGet:
              path: /ready
              port: 3000

            initialDelaySeconds: 5
            periodSeconds: 10

          livenessProbe:
            httpGet:
              path: /health
              port: 3000

            initialDelaySeconds: 10
            periodSeconds: 15
```

Now we're getting much closer to a real backend deployment.

---

## 29. Node.js Side

Your Node.js application can simply read:

```ts
const port = Number(process.env.PORT ?? 3000);

const databaseUrl = process.env.DATABASE_URL;

const jwtSecret = process.env.JWT_SECRET;
```

Your application doesn't need to know whether the values came from:

```text
ConfigMap
Secret
Docker
AWS
```

It simply receives environment variables.

This is a very useful separation of concerns.

---

## PART 9 — STATEFUL VS STATELESS

This is an important architecture concept.

Your API:

```text
Node.js API
```

should ideally be:

> **stateless**

Meaning one Pod doesn't have irreplaceable application state.

Example:

```text
Request 1 → Pod A
Request 2 → Pod B
Request 3 → Pod C
```

All should work.

State belongs in external systems:

```text
PostgreSQL
Redis
S3
```

rather than only inside a Pod's filesystem.

---

## 30. Why Stateless Matters

Imagine:

```text
Pod A
 └── user session
```

Pod A dies.

Session disappears.

Bad architecture.

Instead:

```text
Pod A ──┐
Pod B ──┼──→ Redis
Pod C ──┘
```

Now all Pods can access shared state.

Similarly:

```text
Pods
 ↓
RDS
```

for persistent relational data.

And:

```text
Pods
 ↓
S3
```

for object/file storage.

---

## 31. Should You Run PostgreSQL Inside Kubernetes?

You **can**.

But for your SWE/cloud architecture, don't automatically do it.

You already learned:

```text
AWS RDS
```

A common architecture is:

```text
EKS
 ↓
Node.js Pods
 ↓
RDS PostgreSQL
```

rather than:

```text
EKS
 ↓
PostgreSQL Pod
```

Why?

Managed databases provide things like:

- backups
- failover capabilities
- maintenance
- monitoring
- managed storage
- operational tooling

Running databases in Kubernetes introduces additional operational complexity.

---

## PART 10 — STATEFULSET

You should still know:

> **StatefulSet**

StatefulSet is designed for workloads requiring stable identity and/or persistent storage semantics.

Conceptually:

```text
StatefulSet
 ├── postgres-0
 ├── postgres-1
 └── postgres-2
```

Pods have predictable identities.

This is useful for certain stateful distributed systems.

For your backend:

```text
Node.js API → Deployment
PostgreSQL → preferably managed RDS in AWS
```

is a much more important architecture to understand.

---

## PART 11 — PRACTICAL LAB

Now let's turn this response into an actual exercise.

### Lab architecture

```text
                    Deployment
                       │
             ┌─────────┼─────────┐
             ↓         ↓         ↓
           Pod A     Pod B     Pod C
             │         │         │
             └────┬────┴────┬────┘
                  ↓         ↓
              ConfigMap   Secret
                  │         │
                  └────┬────┘
                       ↓
                  Node.js API
```

---

### Step 1 — Create ConfigMap

```bash
kubectl apply -f configmap.yaml
```

Check:

```bash
kubectl get configmap
```

---

### Step 2 — Create Secret

```bash
kubectl create secret generic api-secret \
  --from-literal=API_KEY='test-key'
```

Check:

```bash
kubectl get secrets
```

---

### Step 3 — Deploy

```bash
kubectl apply -f deployment.yaml
```

Check:

```bash
kubectl get pods
```

---

### Step 4 — Inspect Environment

```bash
kubectl exec -it <pod-name> -- env
```

Verify:

```text
NODE_ENV=production
PORT=3000
API_KEY=test-key
```

---

### Step 5 — Test Readiness

```bash
kubectl describe pod <pod-name>
```

Look for:

```text
Readiness probe
```

---

### Step 6 — Break the Health Endpoint

Temporarily make `/health` fail.

Then:

```bash
kubectl get pods
```

Watch:

```bash
kubectl get pods -w
```

Inspect:

```bash
kubectl describe pod <pod-name>
```

You should understand why Kubernetes considers the container unhealthy.

---

## 32. Storage Lab

Create:

```yaml
apiVersion: v1
kind: Pod

metadata:
  name: volume-demo

spec:
  containers:
    - name: app
      image: nginx

      volumeMounts:
        - name: data
          mountPath: /data

  volumes:
    - name: data
      emptyDir: {}
```

Apply:

```bash
kubectl apply -f volume.yaml
```

Enter:

```bash
kubectl exec -it volume-demo -- sh
```

Create:

```bash
echo "hello kubernetes" > /data/message.txt
```

Check:

```bash
cat /data/message.txt
```

Then delete the Pod.

Understand what happens to the data.

That's the difference between:

```text
ephemeral storage
```

and:

```text
persistent storage
```

---

## 33. Debugging Checklist

When configuration doesn't work:

```text
kubectl get pods
        ↓
kubectl describe pod <pod>
        ↓
kubectl logs <pod>
        ↓
kubectl exec -it <pod> -- env
```

Check:

- ConfigMap exists?
- Secret exists?
- Correct key?
- Correct namespace?
- Environment variable name correct?
- Image contains expected application?
- Application actually reads `process.env`?
- Probe endpoint exists?
- Probe port correct?

---

## 34. Common Kubernetes Problems

#### Pod can't start

Check:

```bash
kubectl describe pod <pod>
```

---

#### Secret not found

Possible issue:

```text
Secret exists in namespace A
Pod is in namespace B
```

Remember:

> Kubernetes resources such as Secrets and ConfigMaps are generally namespace-scoped.

---

#### ConfigMap changed but application still uses old value

Environment variables injected into an already-running container don't magically update the running process.

You may need to restart/redeploy Pods.

Example:

```bash
kubectl rollout restart deployment api
```

---

#### PVC stuck Pending

Check:

```bash
kubectl get pvc
kubectl describe pvc <name>
```

Possible causes:

- no suitable storage provisioner
- wrong StorageClass
- insufficient capacity
- access-mode mismatch

---

## 35. The Big Picture

You now have:

```text
                   Kubernetes
                       │
             ┌─────────┼──────────┐
             ↓         ↓          ↓
        Deployment   ConfigMap   Secret
             │
             ↓
           Pods
             │
        ┌────┴────┐
        ↓         ↓
    Container   Volume
                  │
          ┌───────┴────────┐
          ↓                ↓
      ephemeral         persistent
      emptyDir             PVC
                            ↓
                           PV
                            ↓
                      Cloud Storage
```

And your application architecture:

```text
                    Internet
                       │
                       ↓
                    ALB / LB
                       │
                       ↓
                  K8s Service
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
        Pod A        Pod B        Pod C
          │            │            │
          └────────────┼────────────┘
                       ↓
                  Node.js API
                  /        \
                 ↓          ↓
               Redis       RDS
                            │
                       Persistent DB
```

Configuration:

```text
ConfigMap ───────→ Pod
Secret ──────────→ Pod
```

Files:

```text
Pod → PVC → Persistent Storage
```

---

## 36. What You Should Be Able to Explain Now

If an interviewer asks:

#### "What happens when a Pod dies?"

You should explain:

```text
Deployment
 ↓
desired replica count
 ↓
controller notices missing Pod
 ↓
replacement Pod created
 ↓
scheduler places it
 ↓
container starts
 ↓
readiness probe passes
 ↓
Service can send traffic
```

#### "Where do your database passwords live?"

```text
Secret / external secret manager
```

not:

```text
Dockerfile ❌
GitHub repository ❌
source code ❌
```

#### "Where should application files be stored?"

Depends on their nature:

```text
temporary → emptyDir
persistent filesystem data → PVC/cloud storage
objects/uploads → S3
relational data → RDS
cache/session → Redis
```

#### "Why are APIs generally stateless?"

Because:

```text
Any healthy Pod
can process
any request
```

making:

```text
horizontal scaling
load balancing
Pod replacement
rolling deployments
```

much easier.
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 18: Kubernetes Fundamentals](ch18-kubernetes-fundamentals.md) · [Chapter 20: Kubernetes Networking + Scaling + Production](ch20-kubernetes-networking-scaling.md) → · [Revision sheet](../../revision/ch19-revision.md)
