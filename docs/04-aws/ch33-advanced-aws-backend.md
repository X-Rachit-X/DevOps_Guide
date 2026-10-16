# Chapter 33 — Advanced AWS for Backend Engineers

> **Source:** Response 33 of the original conversation (`source-archive/src-33.txt`, lines 1–3500) · **Part II — Advanced extension (Responses 25–36)**  
> **Study aids:** [Revision sheet](../../revision/ch33-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md) · *includes an editorial supplement at the end*

<!-- SOURCE-BEGIN -->

We're now at **33/36**.

You've already learned the AWS foundation:

- IAM
- EC2
- S3
- VPC
- RDS
- ALB
- Lambda
- SQS/SNS
- Route 53
- CloudFront
- WAF
- CloudWatch
- EKS
- ECR
- Terraform

So this response is about something more important than memorizing more AWS services:

> **How do you choose the right AWS service for a backend system?**

This is what separates someone who has "learned AWS" from someone who can actually **design a production backend on AWS**.

---

## 1. The AWS Backend Engineer Mental Model

A production backend might look like:

```text
                         Users
                           │
                           ▼
                      Route 53
                           │
                           ▼
                      CloudFront
                           │
                           ▼
                         WAF
                           │
                           ▼
                   API Gateway / ALB
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
            ECS           EKS         Lambda
              │            │            │
              └────────────┼────────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
           RDS          DynamoDB       ElastiCache
            │              │              │
            └──────────────┼──────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
             S3           SQS       EventBridge
```

You don't use all of these simultaneously.

The skill is knowing:

> **Which component should solve which problem?**

---

## 2. The Big Compute Decision

You now have four major compute choices:

```text
EC2
ECS
EKS
Lambda
```

Let's understand them properly.

---

## 3. EC2

EC2 gives you virtual machines.

```text
Your application
      ↓
EC2
      ↓
Operating System
      ↓
AWS hardware
```

You control much of the machine environment.

You can install:

```text
Node.js
Docker
Nginx
system packages
monitoring agents
```

#### Advantages

- maximum control
- flexible
- predictable long-running workloads
- supports unusual requirements

#### Disadvantages

You manage more:

```text
OS
patching
scaling
capacity
processes
security
```

---

## 4. ECS

ECS = **Elastic Container Service**.

ECS is AWS's container orchestration service.

Instead of managing containers manually:

```text
EC2
 └── Docker
      └── Node.js
```

you define:

```text
ECS
 └── Task
      └── Container
```

AWS handles much of the orchestration.

---

## 5. ECS Task

Think of an ECS task as a running instance of your container configuration.

For example:

```text
Task
├── backend container
└── sidecar container
```

You define:

```text
image
CPU
memory
ports
environment
IAM role
logging
```

---

## 6. ECS Services

An ECS Service keeps the desired number of tasks running.

Example:

```text
Desired count = 3
```

ECS tries to maintain:

```text
Task 1
Task 2
Task 3
```

If one crashes:

```text
Task 2
   ↓
dies
   ↓
ECS starts replacement
```

This is the same desired-state idea you've already learned from Kubernetes.

---

## 7. ECS Launch Types

Two important choices:

```text
ECS on EC2
ECS on Fargate
```

#### ECS + EC2

```text
ECS
 ↓
EC2 instances
 ↓
Containers
```

You manage the EC2 capacity.

#### ECS + Fargate

```text
ECS
 ↓
Fargate
 ↓
Containers
```

AWS manages the underlying compute capacity.

---

## 8. ECS vs EKS

This is one of the most important interview questions.

#### ECS

AWS-native container orchestration.

```text
ECS
 ↓
AWS
```

#### EKS

Managed Kubernetes.

```text
EKS
 ↓
Kubernetes
 ↓
AWS
```

---

## 9. When Would You Choose ECS?

ECS is attractive when:

```text
you want containers
+
AWS-native orchestration
+
less Kubernetes complexity
```

For example:

```text
Node.js API
Docker
ALB
ECS Fargate
RDS
Redis
S3
```

This can be a very clean architecture.

---

## 10. When Would You Choose EKS?

EKS becomes more attractive when:

```text
you specifically need Kubernetes
+
many services
+
Kubernetes ecosystem
+
operators
+
Helm
+
GitOps
+
service mesh
+
portability
```

For your roadmap:

```text
ECS
→ know well

EKS
→ know deeply
```

because EKS is already one of your major skills.

---

## 11. ECS vs EKS: Important Tradeoff

Don't answer:

> "EKS is better."

That's not technically meaningful.

Instead:

```text
ECS
→ simpler AWS-native container orchestration

EKS
→ Kubernetes ecosystem + flexibility + more complexity
```

Choice depends on requirements.

---

## 12. Lambda

Lambda is different.

Instead of managing servers/containers directly:

```text
Event
 ↓
Lambda function
 ↓
Code
```

Example:

```text
S3 upload
 ↓
Lambda
 ↓
resize image
```

or:

```text
SQS message
 ↓
Lambda
 ↓
process job
```

---

## 13. Lambda Is Event-Driven

Lambda is especially useful for:

```text
short-lived tasks
event processing
background jobs
scheduled tasks
webhooks
lightweight APIs
```

You pay based largely on execution rather than maintaining a permanently running server.

---

## 14. Lambda vs ECS

#### Lambda

```text
event
 ↓
function
```

Good when execution is naturally event-based.

#### ECS

```text
container
 ↓
long-running service
```

Good for persistent backend services.

For example:

```text
REST API
→ ECS

Image processing after S3 upload
→ Lambda
```

---

## 15. Lambda Cold Starts

A Lambda function may not always have an already-running execution environment.

So:

```text
request
 ↓
initialize environment
 ↓
run code
```

can introduce startup latency.

This is a:

> **Cold start**

This matters more for latency-sensitive applications.

---

## 16. Lambda Concurrency

Suppose:

```text
1 request
```

requires:

```text
1 Lambda execution
```

Then:

```text
1,000 requests
```

can potentially create many concurrent Lambda executions.

That's powerful.

But it can overload dependencies.

Example:

```text
1,000 Lambda executions
        ↓
1,000 DB connections
        ↓
RDS overwhelmed
```

So serverless scaling doesn't mean your dependencies can scale infinitely.

---

## 17. Lambda + RDS

This is a classic architecture problem.

Bad:

```text
Lambda
 ├── execution 1 → DB connection
 ├── execution 2 → DB connection
 ├── execution 3 → DB connection
 ├── ...
 └── execution 1000 → DB connection
```

Better approaches can include:

```text
connection pooling strategies
RDS Proxy
architectural throttling
async queues
appropriate concurrency controls
```

depending on the workload.

---

## 18. API Gateway

API Gateway provides an API entry point.

Conceptually:

```text
Client
  ↓
API Gateway
  ↓
Lambda / ECS / other backend
```

It can handle things like:

```text
routing
authentication integration
authorization
throttling
API lifecycle
monitoring
```

---

## 19. API Gateway vs ALB

Another important interview question.

#### ALB

Best thought of as:

```text
HTTP load balancing
```

Example:

```text
Internet
 ↓
ALB
 ↓
ECS/EKS
```

#### API Gateway

Best thought of as:

```text
API management + API entry layer
```

Example:

```text
Client
 ↓
API Gateway
 ↓
Lambda
```

API Gateway can also integrate with other backends.

---

## 20. When API Gateway Makes Sense

Good examples:

```text
public API
serverless APIs
API throttling
API keys/usage plans
different API consumers
managed API lifecycle
```

If you simply need:

```text
HTTPS
 ↓
load balance
 ↓
ECS service
```

an ALB may be simpler.

Again:

> There is no universal "better."

---

## 21. DynamoDB

Now databases.

You've already learned RDS.

DynamoDB is a managed NoSQL database.

Think:

```text
DynamoDB
=
highly scalable key-value/document database
```

It is fundamentally different from PostgreSQL.

---

## 22. RDS vs DynamoDB

#### RDS

Relational:

```text
tables
rows
columns
joins
SQL
transactions
```

Example:

```text
Users
Orders
Products
```

#### DynamoDB

NoSQL:

```text
partition key
sort key
items
attributes
```

The data model is designed around access patterns rather than arbitrary relational joins.

---

## 23. DynamoDB Example

Suppose you need:

```text
user_id → user profile
```

You might use:

```text
PK = USER#123
```

and store:

```json
{
  "PK": "USER#123",
  "name": "Rachit",
  "email": "..."
}
```

The important concept is:

> Design DynamoDB tables around the queries you need to perform.

---

## 24. Partition Key

DynamoDB distributes data using partitioning.

A good partition key should distribute traffic reasonably well.

Bad example:

```text
PK = "ALL_USERS"
```

could concentrate traffic.

Better:

```text
PK = userId
```

when your access pattern is user-centric.

---

## 25. Sort Key

You can also use:

```text
PK
SK
```

Example:

```text
PK = USER#123
SK = ORDER#1001
```

Then:

```text
PK = USER#123
```

can represent multiple related items.

This is one of the core DynamoDB modeling patterns.

---

## 26. Single-Table Design

You may encounter DynamoDB single-table design.

Instead of:

```text
Users table
Orders table
Products table
```

you may model multiple entity types within one table.

For example:

```text
PK              SK
USER#123        PROFILE
USER#123        ORDER#1001
USER#123        ORDER#1002
```

This can make specific access patterns extremely efficient.

But it requires careful design.

---

## 27. DynamoDB vs PostgreSQL

Don't say:

> DynamoDB is faster than PostgreSQL.

That's too simplistic.

Instead:

```text
PostgreSQL
→ relational queries
→ joins
→ flexible SQL
→ relational integrity
→ transactions

DynamoDB
→ predictable access patterns
→ massive horizontal scale
→ key-value/document model
→ low-latency access at scale
```

Choose based on workload.

---

## 28. DynamoDB Transactions

DynamoDB supports transactional operations.

But don't assume:

```text
NoSQL
=
no transactions
```

That's incorrect.

The capabilities and tradeoffs differ from relational databases.

---

## 29. DynamoDB Secondary Indexes

You can use:

```text
GSI
LSI
```

#### GSI

Global Secondary Index.

Allows additional query patterns using different key attributes.

#### LSI

Local Secondary Index.

Uses the same partition key but a different sort key and has specific constraints.

For interviews:

```text
GSI
→ alternative access pattern

LSI
→ alternate sort key under same partition key
```

is enough.

---

## 30. DynamoDB Capacity

You may encounter:

```text
On-demand
Provisioned
```

#### On-demand

AWS automatically handles capacity based on traffic.

Useful when:

```text
unpredictable workload
```

#### Provisioned

You specify expected capacity.

Useful when:

```text
predictable workload
```

and you want more explicit capacity management.

---

## 31. DynamoDB Streams

DynamoDB Streams capture item-level changes.

Conceptually:

```text
DynamoDB
   ↓
Stream
   ↓
Lambda
```

Example:

```text
Order created
 ↓
DynamoDB
 ↓
Stream
 ↓
Lambda
 ↓
send notification
```

This enables event-driven architectures.

---

## 32. ElastiCache

Now caching.

You've already learned Redis.

AWS provides managed caching through services such as:

```text
ElastiCache
```

Common engines include:

```text
Redis/Valkey
Memcached
```

depending on the service/version and AWS offering.

For your backend architecture, think:

```text
Node.js
 ↓
ElastiCache
 ↓
RDS
```

---

## 33. Why Cache?

Suppose:

```text
GET /products
```

is requested:

```text
100,000 times
```

but the database data changes only occasionally.

Without cache:

```text
100,000 requests
 ↓
RDS
```

With cache:

```text
100,000 requests
 ↓
Redis
 ↓
few DB queries
```

This reduces database load and latency.

---

## 34. Cache-Aside Pattern

The most important Redis pattern:

```text
Request
 ↓
Check cache
 ↓
Hit?
 ├── YES → return
 │
 └── NO
       ↓
      DB
       ↓
    store cache
       ↓
     return
```

Example:

```typescript
const cached = await redis.get(key);

if (cached) {
  return JSON.parse(cached);
}

const product = await db.product.findUnique({
  where: { id }
});

await redis.set(
  key,
  JSON.stringify(product),
  { EX: 300 }
);

return product;
```

---

## 35. Cache Invalidation

Caching creates a new problem:

> What happens when the underlying data changes?

Suppose:

```text
DB:
price = ₹100
```

Redis:

```text
price = ₹100
```

Then DB changes:

```text
price = ₹120
```

but Redis still contains:

```text
₹100
```

That's stale data.

Therefore cache invalidation is critical.

---

## 36. TTL

A simple solution:

```text
cache entry
 ↓
TTL = 5 minutes
 ↓
expires
```

This limits how long stale data can survive.

But TTL isn't always enough.

For important data, invalidate/update the cache when the source changes.

---

## 37. Cache Stampede

Imagine:

```text
cache expires
```

and:

```text
10,000 requests
```

arrive simultaneously.

All see:

```text
cache miss
```

and hit the DB.

```text
10,000 requests
 ↓
RDS
```

Potentially causing overload.

This is a:

> **Cache stampede**

Solutions include:

```text
locking
request coalescing
jittered TTL
background refresh
stale-while-revalidate
```

You don't need every technique memorized, but understand the problem.

---

## 38. SQS

You've already learned SQS.

Let's now place it in architecture.

Suppose:

```text
Order API
```

needs to generate invoices.

Don't make the user wait:

```text
Request
 ↓
create order
 ↓
generate invoice
 ↓
send email
 ↓
respond
```

Instead:

```text
Request
 ↓
create order
 ↓
SQS
 ↓
respond quickly
```

Worker:

```text
SQS
 ↓
Worker
 ↓
generate invoice
```

---

## 39. Why SQS?

SQS provides:

```text
decoupling
buffering
asynchronous processing
retry
DLQ
```

Architecture:

```text
Producer
   ↓
SQS
   ↓
Consumer
```

---

## 40. Queue as a Shock Absorber

Suppose traffic suddenly increases:

```text
1,000 requests/sec
```

but workers can process:

```text
500 jobs/sec
```

Without a queue:

```text
workers overwhelmed
```

With SQS:

```text
Producer
 ↓
SQS
 ↓↓↓↓↓
Workers
```

The queue absorbs the temporary spike.

This is a powerful distributed-systems pattern.

---

## 41. Visibility Timeout

Suppose a worker receives:

```text
Job A
```

SQS temporarily hides it from other consumers.

If the worker successfully processes it:

```text
delete message
```

If the worker crashes:

```text
visibility timeout expires
 ↓
message becomes available again
```

This enables retry.

---

## 42. Dead-Letter Queue

Suppose:

```text
Job
 ↓
fail
 ↓
retry
 ↓
fail
 ↓
retry
 ↓
fail
```

Eventually:

```text
DLQ
```

This prevents a permanently broken message from repeatedly blocking normal processing.

---

## 43. Idempotency

Queues can deliver messages more than once depending on the queue/delivery semantics.

Therefore:

```text
consumer
```

should often be idempotent.

Example:

```text
Process payment
```

You don't want:

```text
same message
 ↓
payment
 ↓
payment again
```

Use an idempotency key / deduplication strategy appropriate to the workflow.

This is a **backend engineering** concept, not merely an AWS concept.

---

## 44. SNS

SNS is primarily a publish/subscribe messaging service.

Think:

```text
Publisher
    ↓
  SNS Topic
   / | \
  /  |  \
 SQS SQS Lambda
```

One event can fan out to multiple consumers.

---

## 45. SQS vs SNS

#### SQS

```text
queue
```

Usually:

```text
one message
→ processed by one consumer in a competing-consumer model
```

#### SNS

```text
pub/sub
```

One published event can be delivered to multiple subscribers.

---

## 46. SNS + SQS

This is a very useful pattern.

```text
Order Service
      ↓
SNS Topic
   /     \
  ↓       ↓
SQS      SQS
Email    Analytics
Queue    Queue
```

Now each subsystem processes independently.

---

## 47. EventBridge

Now another event system.

EventBridge is useful for event-driven architectures where you want:

```text
events
+
routing rules
+
multiple targets
```

Think:

```text
Event Producer
      ↓
EventBridge
      ↓
Rules
 ┌────┼────┐
 ↓    ↓    ↓
Lambda SQS Step Functions
```

---

## 48. SNS vs EventBridge

Simplified:

#### SNS

Strong fit for:

```text
pub/sub notifications
fanout
simple event delivery
```

#### EventBridge

Strong fit for:

```text
event buses
event routing
many event sources
rule-based routing
AWS/service events
SaaS/application integration
```

Don't think of EventBridge as "SNS but newer."

They solve overlapping but distinct messaging/eventing needs.

---

## 49. EventBridge Example

Suppose:

```text
OrderCreated
```

event occurs.

EventBridge rule:

```text
source = ecommerce
detail-type = OrderCreated
```

Targets:

```text
Lambda
SQS
Step Functions
```

So:

```text
OrderCreated
      ↓
EventBridge
      ↓
Rule
 ┌────┼──────┐
 ↓    ↓      ↓
Email Analytics Workflow
```

---

## 50. Event-Driven Architecture

Now you can design:

```text
Order API
   ↓
RDS
   ↓
OrderCreated event
   ↓
EventBridge
   ├── Notification
   ├── Analytics
   └── Fulfillment
```

This reduces direct coupling.

Instead of:

```text
Order Service
 ↓
call Notification
 ↓
call Analytics
 ↓
call Fulfillment
```

you have:

```text
Order Service
 ↓
publish event
```

and independent consumers.

---

## 51. Eventual Consistency

Event-driven systems often introduce:

> **Eventual consistency**

For example:

```text
Order created
 ↓
RDS updated
 ↓
event published
 ↓
analytics updated later
```

For a short period:

```text
Order system = updated
Analytics = not yet updated
```

Eventually they converge.

This is a fundamental distributed-systems tradeoff.

---

## 52. Step Functions

Now orchestration.

Suppose you need:

```text
Process payment
 ↓
reserve inventory
 ↓
generate invoice
 ↓
send notification
```

and each step may fail.

You can use:

```text
AWS Step Functions
```

to model the workflow.

Conceptually:

```text
Start
 ↓
Payment
 ↓
Inventory
 ↓
Invoice
 ↓
Notification
 ↓
End
```

---

## 53. Why Step Functions?

Instead of writing a giant application function:

```typescript
async function processOrder() {
    ...
}
```

containing:

```text
retry logic
timeouts
state management
failure handling
branching
```

Step Functions can represent the workflow explicitly.

---

## 54. State Machine

A Step Functions workflow is essentially a state machine.

Example:

```text
START
  ↓
Charge Payment
  ↓
Success?
 ├── No → Retry / Fail
 │
 └── Yes
       ↓
Reserve Inventory
       ↓
Generate Invoice
       ↓
Send Email
       ↓
END
```

---

## 55. Step Functions vs SQS

They solve different problems.

#### SQS

```text
queue work
```

#### Step Functions

```text
orchestrate multi-step workflow
```

You can even combine them.

```text
Step Functions
      ↓
SQS
      ↓
Worker
```

---

## 56. Secrets Manager

You've already seen this in earlier responses.

Now let's make the architectural role clear.

Don't put:

```text
DB_PASSWORD
API_KEY
JWT_SECRET
```

directly in:

```text
Git
Dockerfile
source code
```

Instead:

```text
AWS Secrets Manager
        ↓
application/workload
```

---

## 57. Secrets Manager vs Parameter Store

Both can store configuration/secrets.

Simplified:

#### Secrets Manager

Strong fit for:

```text
secrets
credential lifecycle
secret rotation
```

#### Parameter Store

Useful for:

```text
configuration
parameters
some secret storage
```

Don't assume every configuration value belongs in Secrets Manager.

---

## 58. KMS

KMS = **Key Management Service**.

Think:

```text
KMS
=
managed cryptographic key management
```

Used with services such as:

```text
S3
RDS
EBS
Secrets Manager
```

to support encryption.

---

## 59. Encryption Layers

You should distinguish:

#### Encryption in transit

```text
Client
 ↓ TLS
Server
```

#### Encryption at rest

```text
Database/storage
 ↓
encrypted data
```

KMS often participates in the encryption-at-rest architecture.

---

## 60. Envelope Encryption

You may hear this term.

Conceptually:

```text
Data
 ↓
Data Encryption Key
 ↓
encrypted data

KMS key
 ↓
protects data key
```

You generally don't need to implement envelope encryption manually for normal AWS application development.

Understand the concept.

---

## 61. Backend Architecture Example

Let's design a real application.

Suppose:

> E-commerce platform.

We have:

```text
Users
Products
Orders
Payments
Notifications
```

Architecture:

```text
                    Internet
                        │
                    CloudFront
                        │
                       WAF
                        │
                  API Gateway
                        │
                    ECS/EKS
                        │
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
      User            Order          Product
     Service          Service         Service
        │               │               │
        └───────────────┼───────────────┘
                        │
                     RDS
                        │
                    Redis
                        │
                  EventBridge
                  /          \
                 ↓            ↓
             SQS Queue      Lambda
                 ↓
              Worker
                 ↓
              S3/Email
```

Now let's reason about each choice.

---

## 62. Why RDS?

Orders have relationships:

```text
user
 ↓
orders
 ↓
order_items
 ↓
products
```

Relational queries and transactional integrity are valuable.

Therefore:

```text
PostgreSQL/RDS
```

is a natural fit.

---

## 63. Why Redis?

Product catalog and sessions may be read frequently.

Use:

```text
ElastiCache
```

for:

```text
cache
sessions
rate limiting
temporary state
```

where appropriate.

---

## 64. Why SQS?

Invoice generation doesn't need to happen inside the HTTP request.

So:

```text
Order created
 ↓
SQS
 ↓
Invoice worker
```

decouples the work.

---

## 65. Why EventBridge?

Multiple systems may care about:

```text
OrderCreated
```

Instead of hardcoding:

```text
Order → Analytics
Order → Notification
Order → Fulfillment
```

publish an event:

```text
OrderCreated
 ↓
EventBridge
```

and route it.

---

## 66. Why Lambda?

A small event processor might not justify a permanently running service.

Example:

```text
S3 upload
 ↓
Lambda
 ↓
generate thumbnail
```

Lambda is a good fit.

---

## 67. Why ECS/EKS?

For the core API:

```text
long-running
HTTP
Node.js
```

a containerized service is a natural choice.

Depending on the team's needs:

```text
ECS Fargate
```

could be simpler, while:

```text
EKS
```

could be appropriate if Kubernetes ecosystem requirements justify it.

---

## 68. Why S3?

Use S3 for:

```text
images
documents
exports
backups
static assets
```

Don't store large binary files directly inside PostgreSQL unless there's a specific reason.

A common architecture:

```text
DB
→ metadata

S3
→ actual file
```

---

## 69. API Gateway vs ALB in This Architecture

If using:

```text
Lambda-first API
```

you might choose:

```text
API Gateway
```

If using:

```text
ECS/EKS HTTP services
```

you might use:

```text
ALB
```

You can also combine API Gateway with containerized backends when API management requirements justify it.

Again:

> Architecture follows requirements.

---

## 70. The AWS Decision Matrix

Here's the mental table you should memorize.

| Problem | Common AWS choice |
|---|---|
| Virtual machine | EC2 |
| Managed containers | ECS |
| Kubernetes | EKS |
| Serverless function | Lambda |
| Object storage | S3 |
| Relational database | RDS/Aurora |
| Key-value/document DB | DynamoDB |
| Cache | ElastiCache |
| Queue | SQS |
| Pub/sub fanout | SNS |
| Event routing | EventBridge |
| Workflow orchestration | Step Functions |
| API management | API Gateway |
| HTTP load balancing | ALB |
| Network load balancing | NLB |
| Secrets | Secrets Manager |
| Configuration parameters | Parameter Store |
| Encryption/key management | KMS |
| Container registry | ECR |
| DNS | Route 53 |
| CDN | CloudFront |
| Web firewall | WAF |
| Monitoring | CloudWatch |

---

## 71. RDS vs DynamoDB Decision

Ask:

#### Do I need relational modeling?

```text
yes
→ PostgreSQL/RDS
```

#### Do I need flexible document/key-value access at massive scale with predictable access patterns?

```text
yes
→ DynamoDB
```

Don't select DynamoDB simply because:

> "NoSQL is faster."

That's not a valid architecture argument.

---

## 72. SQS vs SNS vs EventBridge

Remember:

```text
SQS
→ queue

SNS
→ pub/sub fanout

EventBridge
→ event bus + routing
```

Example:

```text
One worker:
→ SQS

Many subscribers:
→ SNS

Many event sources + rule-based routing:
→ EventBridge
```

---

## 73. ECS vs EKS vs Lambda

Think:

```text
EC2
→ maximum machine control

ECS
→ containers with AWS-native orchestration

EKS
→ Kubernetes ecosystem

Lambda
→ event-driven serverless execution
```

This one diagram is worth remembering.

---

## 74. API Gateway vs ALB

```text
ALB
→ HTTP load balancing

API Gateway
→ API management/entry layer
```

If the requirement is:

> "Distribute HTTP requests across containers."

ALB is a natural fit.

If:

> "Expose APIs with managed API policies, throttling and serverless integrations."

API Gateway becomes attractive.

---

## 75. RDS vs ElastiCache

They aren't competitors.

```text
RDS
→ source of truth

Redis
→ fast temporary/access-optimized data
```

Architecture:

```text
Application
 ↓
Redis
 ↓ miss
RDS
```

---

## 76. S3 vs EBS vs EFS

Another classic interview question.

```text
S3
→ object storage

EBS
→ block storage

EFS
→ shared filesystem
```

Example:

```text
Images → S3
EC2 disk → EBS
Shared files → EFS
```

---

## 77. Queue vs Database

Don't use SQS as your primary database.

SQS answers:

> "What work needs to happen?"

Database answers:

> "What is the persistent state of the system?"

Example:

```text
Order DB
→ order exists

SQS
→ invoice generation needs to happen
```

Different responsibilities.

---

## 78. Event vs Command

A useful distributed-systems distinction.

#### Command

> "Do this."

Example:

```text
ProcessPayment
```

#### Event

> "This happened."

Example:

```text
PaymentProcessed
```

SQS is often naturally used for work/commands.

EventBridge/SNS are often used for event propagation.

The exact semantics depend on architecture.

---

## 79. Reliability Architecture

Suppose RDS becomes slow.

Your backend should have:

```text
timeouts
connection pooling
retry with limits
circuit breaking
caching
queues
backpressure
```

AWS services don't automatically make the application reliable.

You still need good application architecture.

---

## 80. AWS Doesn't Remove Distributed Systems Problems

This is extremely important.

Using:

```text
Lambda
SQS
DynamoDB
EventBridge
```

doesn't magically solve:

```text
duplicates
ordering
timeouts
partial failures
eventual consistency
idempotency
race conditions
backpressure
```

You still need to understand distributed systems.

---

## 81. Example Failure

Suppose:

```text
Order API
 ↓
SQS
 ↓
Worker
 ↓
Payment
```

Worker successfully charges payment.

Then crashes **before acknowledging the message**.

The message may be delivered again.

Now:

```text
same order
 ↓
charge payment
 ↓
charge payment again
```

Therefore:

```text
idempotency
```

is required.

For example:

```text
idempotency_key = order_id
```

and payment processing checks whether that operation has already been completed.

---

## 82. Another Failure: Event Duplication

Suppose:

```text
OrderCreated
```

is delivered twice.

Consumer:

```text
send email
```

Without idempotency:

```text
2 emails
```

With idempotency:

```text
first → send
second → ignore
```

This is fundamental backend engineering.

---

## 83. Backpressure

Suppose:

```text
Producer = 10,000 events/sec
Consumer = 1,000 events/sec
```

Don't let the consumer collapse.

Use:

```text
queue
buffer
rate limiting
consumer scaling
```

Architecture:

```text
Producer
 ↓
SQS
 ↓
Consumers
```

This creates controlled backpressure.

---

## 84. Dead-Letter Queues

Never allow permanently broken messages to endlessly retry.

Use:

```text
Main Queue
    ↓
retries
    ↓
DLQ
```

Then operators can inspect:

```text
why did these messages fail?
```

This is operationally important.

---

## 85. AWS Well-Architected Thinking

You should also know the major AWS architecture pillars:

```text
Operational Excellence
Security
Reliability
Performance Efficiency
Cost Optimization
Sustainability
```

For interviews, you don't need to memorize every subcategory.

But when designing architecture, ask:

```text
Is it secure?
Is it reliable?
Will it scale?
What does it cost?
How do we operate it?
```

---

## 86. Example: Bad Architecture

Imagine:

```text
Internet
 ↓
EC2
 ↓
PostgreSQL
```

and:

```text
EC2 has public IP
database public
SSH open to 0.0.0.0/0
password in code
single EC2
single DB
no backups
```

It might work.

But it's not a good production architecture.

---

## 87. Improved Architecture

```text
Internet
   ↓
Route53
   ↓
CloudFront/WAF
   ↓
ALB
   ↓
Private ECS/EKS
   ↓
Redis
   ↓
Private RDS
```

With:

```text
IAM
Secrets Manager
CloudWatch
autoscaling
multi-AZ
backups
least privilege
```

Now you have a production-oriented design.

---

## 88. But Don't Overengineer

This is equally important.

For a tiny application:

```text
CloudFront
WAF
API Gateway
EKS
Istio
Kafka
EventBridge
Step Functions
DynamoDB
RDS
Redis
```

could be ridiculous.

A small application may only need:

```text
ALB
ECS Fargate
RDS
S3
```

Architecture should match requirements.

---

## 89. A Strong Backend Engineer's Decision Process

When designing AWS architecture, ask:

#### 1. What kind of workload?

```text
HTTP?
event?
batch?
stream?
workflow?
```

#### 2. What compute model?

```text
EC2?
ECS?
EKS?
Lambda?
```

#### 3. What data model?

```text
relational?
key-value?
document?
object?
cache?
```

#### 4. What communication model?

```text
synchronous?
queue?
pub/sub?
event bus?
workflow?
```

#### 5. What reliability requirements?

```text
RTO?
RPO?
multi-AZ?
retries?
DLQ?
```

#### 6. What security requirements?

```text
IAM?
encryption?
private networking?
Secrets Manager?
```

#### 7. What scale?

```text
requests/sec?
data size?
concurrency?
burst?
```

#### 8. What does it cost?

Always ask this.

---

## 90. Interview Architecture Question

#### "Design a scalable image-processing backend."

A reasonable architecture:

```text
User
 ↓
API
 ↓
S3 upload
 ↓
S3 event
 ↓
SQS
 ↓
Lambda / ECS worker
 ↓
process image
 ↓
S3 output
 ↓
DB metadata
```

Why?

```text
S3
→ large files

SQS
→ buffering/retry

Lambda/ECS
→ processing

DB
→ metadata
```

That's much better than:

```text
POST /upload
 ↓
Node.js server
 ↓
process 100 MB image synchronously
 ↓
respond
```

---

## 91. Another Architecture Question

#### "Design a notification system."

```text
Application
    ↓
EventBridge / SNS
    ↓
 ┌──┴─────────┐
 ↓            ↓
Email Queue   SMS Queue
 ↓            ↓
Workers      Workers
```

Use:

```text
SQS
→ buffering/retry

SNS/EventBridge
→ distribution

Workers
→ actual delivery
```

---

## 92. Another Architecture Question

#### "Design a high-traffic product catalog."

Possible architecture:

```text
Client
 ↓
CloudFront
 ↓
ALB
 ↓
ECS/EKS
 ↓
Redis
 ↓ miss
RDS/DynamoDB
```

Use:

```text
CloudFront
→ edge caching

Redis
→ application caching

DB
→ source of truth
```

The exact database depends on access patterns.

---

## 93. Another Architecture Question

#### "Design a payment workflow."

You might use:

```text
API
 ↓
Order DB
 ↓
Step Functions
 ↓
Payment
 ↓
Inventory
 ↓
Invoice
 ↓
Notification
```

with:

```text
idempotency
timeouts
retries
compensation
audit trail
```

This is where Step Functions can be useful.

---

## 94. Compensation

Suppose:

```text
Payment successful
 ↓
Inventory reservation fails
```

You can't simply:

```text
throw error
```

You may need:

```text
refund payment
```

This is a **compensating action**.

Workflow:

```text
Charge payment
 ↓
Reserve inventory
 ↓
FAIL
 ↓
Refund payment
```

This is important distributed transaction thinking.

---

## 95. Why Not Use One Giant Transaction?

Because:

```text
Payment service
Inventory service
Notification service
```

may be independent systems.

A single ACID transaction across all of them may be impractical.

Instead, distributed workflows often use:

```text
events
sagas
compensating actions
idempotency
```

Step Functions can help orchestrate such workflows.

---

## 96. AWS Services You Should Now Recognize

You've now covered the major backend-oriented AWS ecosystem:

```text
Compute
├── EC2
├── ECS
├── EKS
└── Lambda

Storage
├── S3
├── EBS
└── EFS

Databases
├── RDS
├── Aurora
├── DynamoDB
└── ElastiCache

Messaging
├── SQS
├── SNS
└── EventBridge

Workflow
└── Step Functions

Networking
├── VPC
├── ALB
├── NLB
├── API Gateway
├── Route 53
├── CloudFront
└── WAF

Security
├── IAM
├── Secrets Manager
└── KMS

Containers
├── ECR
├── ECS
└── EKS

Observability
└── CloudWatch
```

You don't need to memorize hundreds of AWS services.

These are the ones especially relevant to your backend/SWE direction.

---

## 97. The Ultimate AWS Decision Tree

When someone asks you:

> "Which AWS service would you use?"

Think:

```text
                    Workload
                       │
          ┌────────────┼─────────────┐
          ↓            ↓             ↓
       HTTP API      Event          Batch
          │            │             │
      ┌───┴───┐        │          ECS/Lambda
      ↓       ↓        │
    ECS/EKS Lambda      │
                       ↓
                 SQS/EventBridge
                       │
                    Worker
```

Then data:

```text
                   Data
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
    relational    key-value      files
        │            │            │
       RDS       DynamoDB         S3
        │
      cache
        ↓
    ElastiCache
```

And workflow:

```text
multi-step process
       ↓
Step Functions
```

---

## 98. The AWS Architecture You Should Be Able to Explain

For a serious backend:

```text
                         Users
                           │
                       Route 53
                           │
                      CloudFront
                           │
                          WAF
                           │
                     ALB / API GW
                           │
                  ┌────────┴────────┐
                  │                 │
                 ECS               EKS
                  │                 │
                  └────────┬────────┘
                           │
                  ┌────────┼─────────┐
                  │        │         │
                 RDS     Redis      S3
                  │
              Event system
            ┌─────┴─────┐
            │           │
           SQS      EventBridge
            │           │
         Workers     Lambda
            │           │
            └─────┬─────┘
                  │
            Step Functions
```

With:

```text
Terraform
→ infrastructure

ArgoCD
→ Kubernetes delivery

IAM
→ identity

Secrets Manager
→ secrets

KMS
→ encryption

CloudWatch/OpenTelemetry
→ observability
```

---

## 99. Interview Depth

For your placement target:

#### 🔥 Know deeply

```text
EC2 vs ECS vs EKS vs Lambda
RDS vs DynamoDB
SQS vs SNS vs EventBridge
ALB vs API Gateway
S3 vs EBS vs EFS
Redis/ElastiCache
IAM
Secrets Manager
KMS
autoscaling
queues
idempotency
eventual consistency
```

#### 🟡 Know reasonably

```text
Step Functions
DynamoDB indexes
DynamoDB Streams
ECS task/service concepts
Fargate
EventBridge rules
API Gateway details
```

#### ⚪ Awareness

```text
rare AWS services
specialized analytics services
deep AWS internal implementation
service-specific edge cases
```

This is intentional.

You don't need to memorize every AWS service to be a strong backend engineer.

---

## 100. Final Interview Rapid-Fire

#### EC2 vs ECS?

```text
EC2
→ virtual machines

ECS
→ container orchestration
```

#### ECS vs EKS?

```text
ECS
→ AWS-native container orchestration

EKS
→ managed Kubernetes
```

#### ECS Fargate vs Lambda?

```text
Fargate
→ long-running/container workloads

Lambda
→ event-driven function execution
```

#### RDS vs DynamoDB?

```text
RDS
→ relational

DynamoDB
→ key-value/document
```

#### SQS vs SNS?

```text
SQS
→ queue

SNS
→ pub/sub
```

#### SNS vs EventBridge?

```text
SNS
→ fanout/pub-sub

EventBridge
→ event bus + rule-based routing
```

#### Redis vs RDS?

```text
Redis
→ cache/fast temporary data

RDS
→ persistent relational source of truth
```

#### S3 vs EBS?

```text
S3
→ object storage

EBS
→ block storage
```

#### API Gateway vs ALB?

```text
API Gateway
→ API management/entry layer

ALB
→ HTTP load balancing
```

#### Secrets Manager vs KMS?

```text
Secrets Manager
→ store/manage secrets

KMS
→ manage encryption keys
```

---

## 101. The Biggest Lesson From Chapter 33

Don't learn AWS as:

```text
Service 1
Service 2
Service 3
Service 4
...
```

Learn AWS as:

```text
Problem
   ↓
Requirement
   ↓
Architecture
   ↓
AWS service
   ↓
Tradeoff
```

For example:

> "I need asynchronous processing."

Think:

```text
SQS
```

> "I need multiple systems to receive an event."

Think:

```text
SNS/EventBridge
```

> "I need a relational source of truth."

Think:

```text
RDS
```

> "I need massive key-value/document scale with predictable access patterns."

Think:

```text
DynamoDB
```

> "I need caching."

Think:

```text
ElastiCache
```

> "I need a multi-step workflow."

Think:

```text
Step Functions
```

> "I need Kubernetes."

Think:

```text
EKS
```

> "I need simpler AWS-native containers."

Think:

```text
ECS
```

> "I need event-driven functions."

Think:

```text
Lambda
```

That's how you should approach AWS interview questions.

---

## 🎯 Chapter 33 Complete

Covered in depth:

- ✅ EC2
- ✅ ECS
- ✅ ECS Services/Tasks
- ✅ ECS EC2 vs Fargate
- ✅ ECS vs EKS
- ✅ EKS vs Lambda
- ✅ Lambda architecture
- ✅ cold starts
- ✅ concurrency
- ✅ Lambda + RDS
- ✅ API Gateway
- ✅ API Gateway vs ALB
- ✅ DynamoDB
- ✅ partition keys
- ✅ sort keys
- ✅ single-table design
- ✅ GSI/LSI
- ✅ capacity modes
- ✅ DynamoDB Streams
- ✅ RDS vs DynamoDB
- ✅ ElastiCache
- ✅ Redis/cache-aside
- ✅ TTL
- ✅ cache invalidation
- ✅ cache stampede
- ✅ SQS
- ✅ visibility timeout
- ✅ DLQ
- ✅ idempotency
- ✅ SNS
- ✅ SNS + SQS fanout
- ✅ EventBridge
- ✅ event buses/rules
- ✅ SQS vs SNS vs EventBridge
- ✅ Step Functions
- ✅ state machines
- ✅ workflow orchestration
- ✅ compensation
- ✅ Secrets Manager
- ✅ Parameter Store
- ✅ KMS
- ✅ encryption at rest/in transit
- ✅ envelope encryption
- ✅ event-driven architecture
- ✅ eventual consistency
- ✅ backpressure
- ✅ distributed-system failures
- ✅ AWS architecture decisions
- ✅ cost/complexity tradeoffs
- ✅ backend architecture examples
- ✅ AWS service decision matrix
- ✅ interview questions

#### Depth target

**🔥 Deep:** compute choices, databases, caching, messaging, event-driven architecture, queues, idempotency, API Gateway/ALB, AWS architecture decisions.

**🟡 Medium:** Step Functions, DynamoDB indexes/streams, Fargate, EventBridge details.

**⚪ Awareness:** specialized AWS services outside the backend core.
<!-- SOURCE-END -->

---

## Editorial supplement

> **Added by the knowledge-base editor — not part of the original source.** It fills gaps the source leaves open (for example concepts named in the interview list but never explained, or configuration the chapter only describes in words). Treat the text above as the original material and this section as clearly separated additions.

### Concrete examples for the services this chapter compares

The chapter is a decision guide, so it has few configuration examples. These show what each choice looks like in practice. Account IDs, ARNs and names are placeholders.

**1. An ECS Fargate task definition** (sections 4–7). Note the two different roles — a frequent interview point: the **task execution role** is used by ECS itself (pull the image from ECR, write logs, fetch secrets); the **task role** is the identity your application code uses to call AWS services (S3, SQS, DynamoDB …).

```json
{
  "family": "backend",
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::<account-id>:role/backend-task-role",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.ap-south-1.amazonaws.com/backend:a82f31c",
      "portMappings": [{ "containerPort": 3000, "protocol": "tcp" }],
      "environment": [{ "name": "NODE_ENV", "value": "production" }],
      "secrets": [
        { "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:ap-south-1:<account-id>:secret:prod/db-AbCdEf" }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/backend",
          "awslogs-region": "ap-south-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Vocabulary: a **task definition** is the blueprint (image, CPU, memory, ports, roles, logging); a **task** is a running instance of it; an **ECS service** keeps the desired number of tasks running and registers them with an ALB target group; a **cluster** groups tasks/services. With `awsvpc` networking each task gets its own ENI (and security group); the ALB uses `target-type: ip`. ECS services scale with Application Auto Scaling (target tracking on CPU, memory or request count).

**2. DynamoDB: key design and queries** (sections 23–26). Table `app` with partition key `PK` and sort key `SK` (single-table design). Fetch a user's orders with one `Query` — never a table `Scan`:

```typescript
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, PutCommand, QueryCommand } from "@aws-sdk/lib-dynamodb";

const ddb = DynamoDBDocumentClient.from(new DynamoDBClient({ region: process.env.AWS_REGION }));

await ddb.send(new PutCommand({
  TableName: "app",
  Item: { PK: "USER#123", SK: "ORDER#1001", total: 499, status: "PAID" },
}));

const result = await ddb.send(new QueryCommand({
  TableName: "app",
  KeyConditionExpression: "PK = :pk AND begins_with(SK, :sk)",
  ExpressionAttributeValues: { ":pk": "USER#123", ":sk": "ORDER#" },
}));
```

Facts to remember: an item is limited to about 400 KB; reads can be *eventually consistent* (default) or *strongly consistent*; on-demand capacity bills per request while provisioned mode uses read/write capacity units; a **hot partition** (one key receiving most traffic) throttles even when total capacity is available; a **local secondary index must be defined when the table is created**, whereas a global secondary index can be added later; the TTL feature can expire items automatically.

**3. The Redis syntax in section 34 is library-specific.** `redis.set(key, value, { EX: 300 })` is the **node-redis v4** form. With **ioredis** the equivalent is `redis.set(key, value, "EX", 300)`. The cache-aside logic is the same.

**4. Step Functions state machine with retry and compensation** (sections 52–54, 93–95). The `Catch` on `ReserveInventory` sends a failure to a compensating `RefundPayment` step — the saga idea in code:

```json
{
  "Comment": "Order workflow with compensation",
  "StartAt": "ChargePayment",
  "States": {
    "ChargePayment": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": { "FunctionName": "charge-payment", "Payload.$": "$" },
      "Retry": [{ "ErrorEquals": ["States.ALL"], "IntervalSeconds": 2, "MaxAttempts": 3, "BackoffRate": 2.0 }],
      "Next": "ReserveInventory"
    },
    "ReserveInventory": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": { "FunctionName": "reserve-inventory", "Payload.$": "$" },
      "Catch": [{ "ErrorEquals": ["States.ALL"], "Next": "RefundPayment" }],
      "Next": "GenerateInvoice"
    },
    "RefundPayment": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": { "FunctionName": "refund-payment", "Payload.$": "$" },
      "Next": "OrderFailed"
    },
    "GenerateInvoice": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": { "FunctionName": "generate-invoice", "Payload.$": "$" },
      "End": true
    },
    "OrderFailed": { "Type": "Fail", "Error": "InventoryUnavailable", "Cause": "Payment was refunded" }
  }
}
```

**5. Two distributed-systems patterns the chapter alludes to.**

- **Saga** (section 95): a long business transaction is split into local transactions, each with a *compensating action*. **Orchestration** has a central coordinator (Step Functions, as above); **choreography** has services react to each other's events (EventBridge/SNS) with no central coordinator.
- **Transactional outbox** (section 50): "write to RDS, then publish `OrderCreated`" is a *dual write* — the database commit can succeed while the publish fails (or vice versa). The outbox pattern writes the event into an `outbox` table **in the same database transaction** as the order, and a separate relay publishes outbox rows to EventBridge/SNS/SQS, retrying until delivered. Consumers must still be idempotent because delivery is at-least-once.

**6. Smaller clarifications.**

- **Aurora** (listed as "RDS/Aurora" in the decision matrix) is an AWS-built, MySQL/PostgreSQL-compatible relational engine with a distributed storage layer and faster failover/read scaling.
- **SQS FIFO queues** add ordering and deduplication (see Chapter 15 notes); Standard queues are at-least-once with best-effort ordering. EventBridge adds event **archive/replay** and **schema discovery**; SNS adds **message filtering** per subscription.
- **Streaming workloads** (the chapter lists "stream?" in the decision questions without a service): Kinesis Data Streams or Amazon MSK (managed Kafka).
- **API Gateway** comes in REST, HTTP and WebSocket API flavours, and integration timeouts/payload sizes are limited — check the current quotas when choosing it over an ALB for slow or large requests.

---

**Navigation:** ← [Chapter 32: Advanced Terraform](../06-iac-config/ch32-advanced-terraform.md) · [Chapter 34: Advanced SRE](../07-observability-sre/ch34-advanced-sre.md) → · [Revision sheet](../../revision/ch33-revision.md)
