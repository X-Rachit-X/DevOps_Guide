# Chapter 33 — Revision Sheet: Advanced AWS for Backend Engineers

> Supplements [the full chapter](../docs/04-aws/ch33-advanced-aws-backend.md). The skill: **choose the right AWS service for a backend system** — Problem → Requirement → Architecture → AWS service → Trade-off. Not memorising more services.

## Mental model

Users → Route 53 → CloudFront → WAF → API Gateway / ALB → {ECS, EKS, Lambda} → {RDS, DynamoDB, ElastiCache} → {S3, SQS, EventBridge}. You never use all at once: *which component should solve which problem?*

## Compute: EC2 vs ECS vs EKS vs Lambda

| | Characteristics |
|---|---|
| **EC2** | VMs, maximum control (install Node.js, Docker, Nginx, packages, agents); flexible, predictable long-running workloads, unusual requirements. You manage OS, patching, scaling, capacity, processes, security |
| **ECS** (Elastic Container Service) | AWS-native container orchestration. **Task** (running instance of container configuration: image, CPU, memory, ports, environment, IAM role, logging; may include a sidecar), **Service** (keeps desired count running — Desired = 3; failed task → replacement; same desired-state idea as Kubernetes). Launch types: **ECS on EC2** (you manage EC2 capacity) vs **ECS on Fargate** (AWS manages compute) |
| **EKS** | Managed Kubernetes: Kubernetes ecosystem + flexibility + more complexity. Choose when you specifically need Kubernetes, many services, operators, Helm, GitOps, service mesh, portability |
| **Lambda** | Event → function; short-lived tasks, event processing, background jobs, scheduled tasks, webhooks, lightweight APIs; pay mainly for execution |

- **ECS vs EKS:** "EKS is better" is not meaningful — ECS = simpler AWS-native orchestration; EKS = Kubernetes ecosystem. Simple clean architecture: Node.js API + Docker + ALB + **ECS Fargate** + RDS + Redis + S3. For this roadmap: know ECS well, EKS deeply.
- **Lambda vs ECS:** REST API → ECS; image processing after S3 upload → Lambda. **Cold start** = initialising a new execution environment (latency-sensitive apps). **Concurrency:** 1,000 requests → many concurrent executions → 1,000 DB connections → RDS overwhelmed — serverless scaling doesn't mean dependencies scale infinitely. **Lambda + RDS** fixes: connection pooling strategies, **RDS Proxy**, architectural throttling, async queues, concurrency controls.
- **API Gateway vs ALB:** ALB = HTTP load balancing (Internet → ALB → ECS/EKS); API Gateway = API management + API entry layer (routing, authentication integration, authorization, throttling, API lifecycle, monitoring) → Lambda/ECS/other. API Gateway fits public/serverless APIs, throttling, API keys/usage plans, different consumers, managed lifecycle; for "HTTPS → load balance → ECS service" an ALB may be simpler. Lambda-first API → API Gateway; ECS/EKS HTTP services → ALB; they can be combined.

## DynamoDB vs RDS

DynamoDB = highly scalable managed NoSQL key-value/document store; the data model is designed around **access patterns**, not arbitrary joins (design tables around the queries you need). RDS = relational (tables, rows, columns, joins, SQL, transactions).
- **Keys:** partition key (distributes data/traffic; `PK = userId` good, `PK = "ALL_USERS"` concentrates traffic), sort key `SK` (e.g. `PK = USER#123`, `SK = ORDER#1001`).
- **Single-table design:** multiple entity types in one table (`USER#123 / PROFILE`, `USER#123 / ORDER#1001`, …) — efficient for specific access patterns but needs careful design.
- **Transactions:** DynamoDB supports transactional operations (NoSQL ≠ no transactions). **Indexes:** GSI (alternative access pattern via different key attributes) vs LSI (same partition key, different sort key, specific constraints). **Capacity:** on-demand (unpredictable workloads) vs provisioned (predictable). **Streams:** item-level changes → Lambda (Order created → DynamoDB → Stream → Lambda → notification).
- *Don't say "DynamoDB is faster."* PostgreSQL → relational queries, joins, flexible SQL, integrity, transactions; DynamoDB → predictable access patterns, massive horizontal scale, key-value/document, low latency at scale. Need relational modelling → RDS; flexible key-value/document at massive scale with predictable access patterns → DynamoDB. **Don't choose NoSQL "because it's faster".**

## Caching (ElastiCache)

ElastiCache engines: Redis/Valkey, Memcached. Why: 100,000 `GET /products` with rarely-changing data → Redis → few DB queries (less DB load, lower latency). **Cache-aside:**
```typescript
const cached = await redis.get(key);
if (cached) return JSON.parse(cached);
const product = await db.product.findUnique({ where: { id } });
await redis.set(key, JSON.stringify(product), { EX: 300 });
return product;
```
- **Invalidation:** DB price ₹100 → ₹120 but Redis still has ₹100 = stale data. **TTL** (e.g. 5 min) limits staleness but isn't always enough — invalidate/update on source change for important data.
- **Cache stampede:** entry expires → 10,000 simultaneous requests all miss → hit RDS. Solutions: locking, request coalescing, jittered TTL, background refresh, stale-while-revalidate.
- RDS vs Redis aren't competitors: RDS = source of truth; Redis = fast temporary/access-optimised data. Use Redis for cache, sessions, rate limiting, temporary state.

## Messaging and events

| | |
|---|---|
| **SQS** | Queue → decoupling, buffering, async processing, retry, DLQ; competing-consumer model (one message → one consumer). **Shock absorber**: 1,000 req/s vs 500 jobs/s workers — queue absorbs the spike. **Visibility timeout** (worker crashes → message reappears → retry). **DLQ** prevents a permanently broken message blocking normal processing. Don't use SQS as your database: SQS = "what work needs to happen", DB = "persistent state" |
| **SNS** | Pub/sub fan-out; one event → many subscribers (SQS, SQS, Lambda). **SNS + SQS**: each subsystem (email, analytics queues) processes independently |
| **EventBridge** | Event bus + rule-based routing, many event sources, AWS/service events, SaaS/application integration; rule `source = ecommerce`, `detail-type = OrderCreated` → targets Lambda, SQS, Step Functions. *Not "SNS but newer"* — overlapping but distinct |
| **Step Functions** | Workflow orchestration as a **state machine** (Start → Payment → Inventory → Invoice → Notification → End) with retries, timeouts, state, branching, failure handling expressed explicitly instead of a giant function. Step Functions orchestrate multi-step workflows; SQS queues work — they can be combined |

Rule of thumb: one worker → SQS; many subscribers → SNS; many event sources + rule-based routing → EventBridge.
- **Event vs command:** command = "do this" (`ProcessPayment`, naturally SQS); event = "this happened" (`PaymentProcessed`, SNS/EventBridge). **Event-driven architecture** reduces coupling: Order API → RDS → `OrderCreated` → EventBridge → {Notification, Analytics, Fulfillment}. **Eventual consistency** is the trade-off (order system updated, analytics later).
- **Failures AWS doesn't remove:** worker charges payment then crashes before acknowledging → message redelivered → double charge → **idempotency** (`idempotency_key = order_id`, check whether already done). Duplicate `OrderCreated` → two emails unless idempotent. Also ordering, timeouts, partial failures, race conditions, backpressure. **Backpressure:** producer 10,000 events/s vs consumer 1,000/s → queue, buffer, rate limiting, consumer scaling.
- **Compensation / sagas:** payment succeeded → inventory reservation fails → refund payment (compensating action). One giant ACID transaction across independent services is impractical → events, sagas, compensating actions, idempotency; Step Functions can orchestrate.

## Secrets, keys, encryption

- Secrets Manager (secrets, credential lifecycle, rotation) vs Parameter Store (configuration, parameters, some secret storage) — not every config value belongs in Secrets Manager. Never DB_PASSWORD/API_KEY/JWT_SECRET in Git, Dockerfile or source code.
- **KMS** = managed cryptographic key management used with S3, RDS, EBS, Secrets Manager. Encryption in transit (TLS) vs at rest (KMS participates). **Envelope encryption:** data → data encryption key → encrypted data; the KMS key protects the data key — understand, don't implement manually. **Secrets Manager vs KMS:** store/manage secrets vs manage encryption keys.

## Decision matrix (memorise)

| Problem | Service |
|---|---|
| Virtual machine | EC2 |
| Managed containers | ECS |
| Kubernetes | EKS |
| Serverless function | Lambda |
| Object storage | S3 |
| Relational DB | RDS/Aurora |
| Key-value/document DB | DynamoDB |
| Cache | ElastiCache |
| Queue / Pub-sub fan-out / Event routing | SQS / SNS / EventBridge |
| Workflow orchestration | Step Functions |
| API management / HTTP LB / network LB | API Gateway / ALB / NLB |
| Secrets / config parameters / encryption keys | Secrets Manager / Parameter Store / KMS |
| Container registry / DNS / CDN / web firewall / monitoring | ECR / Route 53 / CloudFront / WAF / CloudWatch |
| Storage trio | S3 = objects, EBS = block (EC2 disk), EFS = shared filesystem |

**Rapid fire:** EC2 vs ECS (VMs vs container orchestration) · ECS vs EKS (AWS-native vs managed Kubernetes) · Fargate vs Lambda (long-running/container vs event-driven function) · RDS vs DynamoDB · SQS vs SNS · SNS vs EventBridge (fan-out vs event bus + rules) · Redis vs RDS (cache vs source of truth) · S3 vs EBS · API Gateway vs ALB · Secrets Manager vs KMS.

## Architecture examples

- **E-commerce:** CloudFront → WAF → API Gateway → ECS/EKS (User/Order/Product services) → RDS + Redis → EventBridge → SQS queue + Lambda → Worker → S3/Email. *Why:* RDS (relationships user → orders → order_items → products, transactions), Redis (catalog/sessions/rate limiting), SQS (invoice generation outside the HTTP request), EventBridge (multiple systems care about `OrderCreated`), Lambda (small event processor like thumbnails), ECS Fargate (simpler) or EKS (if Kubernetes ecosystem justified) for the core API, S3 for files (DB = metadata, S3 = bytes).
- **Bad vs improved:** bad = Internet → public EC2 → public PostgreSQL, SSH open to 0.0.0.0/0, password in code, single EC2/DB, no backups. Improved = Route 53 → CloudFront/WAF → ALB → private ECS/EKS → Redis → private RDS with IAM, Secrets Manager, CloudWatch, autoscaling, multi-AZ, backups, least privilege. **Don't over-engineer:** a small app may only need ALB + ECS Fargate + RDS + S3 (not CloudFront + WAF + API Gateway + EKS + Istio + Kafka + EventBridge + Step Functions + DynamoDB + RDS + Redis).
- **Image-processing backend:** User → API → S3 upload → S3 event → SQS → Lambda/ECS worker → process → S3 output → DB metadata (not synchronous processing of a 100 MB image in the Node.js server).
- **Notification system:** Application → EventBridge/SNS → Email queue / SMS queue → workers (SQS = buffering/retry, SNS/EventBridge = distribution, workers = delivery).
- **High-traffic product catalog:** Client → CloudFront (edge cache) → ALB → ECS/EKS → Redis → miss → RDS/DynamoDB (source of truth; choice depends on access patterns).
- **Payment workflow:** API → Order DB → Step Functions → Payment → Inventory → Invoice → Notification with idempotency, timeouts, retries, compensation, audit trail.

## Design process (8 questions)

1. Workload (HTTP? event? batch? stream? workflow?) 2. Compute (EC2/ECS/EKS/Lambda) 3. Data model (relational/key-value/document/object/cache) 4. Communication (sync/queue/pub-sub/event bus/workflow) 5. Reliability (RTO, RPO, multi-AZ, retries, DLQ) 6. Security (IAM, encryption, private networking, Secrets Manager) 7. Scale (requests/s, data size, concurrency, burst) 8. **Cost — always ask.** **Well-Architected pillars:** Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability.
**Reliability architecture** when RDS is slow: timeouts, connection pooling, bounded retries, circuit breaking, caching, queues, backpressure. *AWS doesn't remove distributed-systems problems:* duplicates, ordering, timeouts, partial failures, eventual consistency, idempotency, race conditions, backpressure.

**Depth:** 🔥 EC2/ECS/EKS/Lambda, RDS vs DynamoDB, SQS/SNS/EventBridge, ALB vs API Gateway, S3/EBS/EFS, Redis/ElastiCache, IAM, Secrets Manager, KMS, autoscaling, queues, idempotency, eventual consistency · 🟡 Step Functions, DynamoDB indexes/streams, ECS task/service concepts, Fargate, EventBridge rules, API Gateway details · ⚪ rare services, analytics services, AWS internals.

## Added (see supplement in the chapter)

ECS Fargate task definition (task role vs **task execution role**, `awsvpc`); DynamoDB `Query` example and facts (400 KB item limit, eventual vs strong reads, hot partitions, LSI at creation); node-redis vs ioredis `SET` syntax; Step Functions ASL with `Retry`/`Catch` compensation; **saga** (orchestration vs choreography) and **transactional outbox**; Aurora; SQS FIFO; Kinesis/MSK for streams; API Gateway flavours/quotas.

<!-- NAV -->

---

← [Sheet 32](ch32-revision.md) · [Full chapter 33](../docs/04-aws/ch33-advanced-aws-backend.md) · [All revision material](README.md) · [Sheet 34](ch34-revision.md) →
