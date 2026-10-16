# Chapter 15 — Lambda + Serverless + Messaging

> **Source:** Response 15 of the original conversation (`source-archive/src-15.txt`, lines 9–1807) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch15-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

This response has two major goals:

1. Understand **serverless + Lambda**
2. Understand **messaging/event-driven systems** and actually use them

---

## PART 1 — What Problem Does Lambda Solve?

Until now, we've mostly used:

```text
GitHub
   ↓
CI/CD
   ↓
Docker
   ↓
EC2
   ↓
Node.js
```

You have to maintain:

```text
EC2
OS
Docker
Application
Scaling
Health
Deployment
```

But what if you have a small function that only needs to run occasionally?

For example:

```text
User uploads image
        ↓
Resize image
```

Why keep an EC2 server running 24/7 just for that?

Lambda gives you:

```text
Event
 ↓
Lambda
 ↓
Function executes
 ↓
Done
```

You don't manage the underlying server.

---

## 2. Lambda Mental Model

Traditional backend:

```text
                    EC2
                     │
              ┌──────┴──────┐
              │ Node.js API │
              └─────────────┘
                     │
              Running 24/7
```

Lambda:

```text
Event
  ↓
Lambda
  ↓
Function
  ↓
Execution finishes
```

Think:

> **Lambda = run code without managing servers.**

---

## 3. Lambda Function

A Lambda function is basically:

```typescript
export const handler = async (event) => {
  return {
    statusCode: 200,
    body: JSON.stringify({
      message: "Hello from Lambda",
    }),
  };
};
```

AWS invokes:

```text
handler(event)
```

You don't manually run:

```bash
node server.js
```

AWS invokes your function when an event occurs.

---

## 4. Lambda vs Node.js Server

#### Traditional Express

```typescript
app.get("/hello", (req, res) => {
  res.json({ message: "Hello" });
});

app.listen(3000);
```

You need:

```text
Server
Port
Process
Infrastructure
```

#### Lambda

```typescript
export const handler = async (event) => {
  return {
    statusCode: 200,
    body: JSON.stringify({
      message: "Hello",
    }),
  };
};
```

AWS manages the execution environment.

---

## 5. Important Lambda Terms

You should know:

```text
Function
Runtime
Handler
Event
Invocation
Execution environment
Timeout
Memory
Environment variables
Concurrency
Cold start
Layers
```

We'll understand each through practice.

---

## 6. Runtime

Lambda needs to know what environment to execute your code in.

For you:

```text
Node.js
```

is particularly relevant.

Conceptually:

```text
Lambda
 └── Node.js runtime
       └── your function
```

---

## 7. Handler

Suppose your file is:

```text
index.ts
```

and exports:

```typescript
export const handler = async () => {
  return "Hello";
};
```

The handler tells Lambda which function to invoke.

Conceptually:

```text
index.handler
```

means:

```text
index.js
   ↓
handler()
```

---

## 8. Lambda Event

Lambda doesn't have to be triggered by HTTP.

An event could come from:

```text
API Gateway
S3
SQS
SNS
EventBridge
CloudWatch Events
```

For example:

```text
S3 upload
   ↓
Lambda
   ↓
Process file
```

or:

```text
SQS message
   ↓
Lambda
   ↓
Process job
```

This is where Lambda becomes extremely powerful.

---

## PART 2 — Actually Creating a Lambda

There are several ways to deploy Lambda.

For learning, know all three:

```text
AWS Console
AWS CLI
Infrastructure as Code
```

We'll start conceptually with the CLI/IaC mindset because that's closer to DevOps.

---

## 9. AWS CLI

You already learned:

```bash
aws sts get-caller-identity
```

First verify:

```bash
aws sts get-caller-identity
```

You should see your AWS identity.

Then:

```bash
aws configure
```

can configure credentials for local development, although for production CI/CD we'll prefer temporary credentials through IAM roles/OIDC rather than long-lived access keys.

---

## 10. Create a Simple Lambda Project

Create:

```text
lambda-demo/
├── package.json
├── src/
│   └── index.ts
└── tsconfig.json
```

Install TypeScript:

```bash
npm init -y
npm install
npm install -D typescript @types/aws-lambda
```

Example:

```typescript
import type {
  APIGatewayProxyHandlerV2,
} from "aws-lambda";

export const handler: APIGatewayProxyHandlerV2 = async () => {
  return {
    statusCode: 200,
    body: JSON.stringify({
      message: "Hello from Lambda!",
    }),
  };
};
```

Compile:

```bash
npx tsc
```

Now you have JavaScript for Lambda.

---

## 11. Lambda Deployment Package

Lambda can be deployed as a package containing:

```text
index.js
node_modules/
other files
```

Conceptually:

```text
TypeScript
    ↓
Compile
    ↓
JavaScript
    ↓
Package
    ↓
Lambda
```

This is exactly where your CI/CD knowledge becomes relevant.

---

## 12. Manual Deployment vs DevOps

You *could* manually upload:

```text
ZIP
 ↓
AWS Console
 ↓
Lambda
```

But that's not a good production workflow.

Instead:

```text
Developer
   ↓
git push
   ↓
GitHub
   ↓
GitHub Actions
   ↓
npm ci
   ↓
npm test
   ↓
npm run build
   ↓
package
   ↓
AWS Lambda
```

**That's DevOps in practice.**

---

## 13. Environment Variables

Don't hardcode:

```typescript
const dbPassword = "secret";
```

Use:

```typescript
const dbHost = process.env.DB_HOST;
```

Lambda supports environment variables.

Conceptually:

```text
Lambda
 ├── Code
 ├── Environment variables
 └── IAM permissions
```

For sensitive values, use proper secrets-management mechanisms rather than treating ordinary environment variables as a secret vault.

---

## 14. Lambda IAM Role

Lambda often needs permission to access other AWS services.

For example:

```text
Lambda
   ↓
S3
```

Lambda should have an IAM execution role allowing only what it needs.

Example:

```text
Lambda Execution Role

Allow:
s3:GetObject

Resource:
specific bucket/path
```

Not:

```text
Allow:
*
```

This is the same **least privilege** principle you learned in [Chapter 9](ch09-aws-fundamentals-iam.md).

---

## 15. Lambda + S3

Now we have a practical architecture.

Suppose a user uploads:

```text
photo.jpg
```

to:

```text
S3
```

S3 can generate an event:

```text
S3
 ↓
Lambda
 ↓
Process image
```

For example:

```text
User uploads image
        ↓
       S3
        ↓
     Lambda
        ↓
Resize / validate / analyze
        ↓
      S3
```

This is event-driven architecture.

---

## PART 3 — Messaging

Now we reach a very important backend concept.

Suppose your API receives:

```text
POST /send-email
```

Should your API wait for the email provider?

Bad architecture:

```text
Client
 ↓
Node API
 ↓
Email provider
 ↓
Wait
 ↓
Response
```

If the email service is slow:

```text
API latency ↑
```

Instead:

```text
Client
 ↓
Node API
 ↓
Queue
 ↓
Immediate response

Queue
 ↓
Worker
 ↓
Email provider
```

This is **asynchronous processing**.

---

## 16. What Is a Queue?

A queue is basically:

> **A buffer of work waiting to be processed.**

Example:

```text
Producer
   ↓
Queue
   ↓
Consumer
```

Producer:

```text
Node.js API
```

Queue:

```text
SQS
```

Consumer:

```text
Lambda
```

Architecture:

```text
Node.js
   ↓
SQS
   ↓
Lambda
   ↓
Email service
```

---

## 17. Why Use a Queue?

Without queue:

```text
API
 ↓
Heavy job
 ↓
Wait 10 seconds
 ↓
Response
```

With queue:

```text
API
 ↓
Queue
 ↓
Response quickly
```

Then:

```text
Queue
 ↓
Worker
 ↓
Heavy job
```

Benefits:

- decoupling
- buffering
- retrying
- asynchronous processing
- traffic smoothing
- failure isolation

---

## 18. SQS

SQS = **Simple Queue Service**.

Mental model:

```text
Producer
    ↓
┌──────────────┐
│     SQS      │
│              │
│ Job 1        │
│ Job 2        │
│ Job 3        │
└──────────────┘
    ↓
Consumer
```

---

## 19. Standard Queue

SQS Standard is designed for highly scalable asynchronous messaging.

But don't assume:

```text
exactly once
```

processing.

Your application should generally be designed to tolerate duplicate processing.

This leads to an extremely important concept:

> **Idempotency**

---

## 20. Idempotency

Suppose your queue contains:

```json
{
  "orderId": "123",
  "action": "charge"
}
```

What if the worker processes it twice?

Bad:

```text
₹100 charged
₹100 charged again
```

You need an idempotent design.

For example:

```text
orderId = 123
payment already processed?
        ↓
Yes → don't charge again
No  → process
```

This is one of the most important concepts in distributed systems.

---

## 21. SQS Visibility Timeout

Imagine:

```text
Queue
 ↓
Message
```

Worker receives the message.

You don't want another worker immediately processing the same message while the first worker is working.

So the message becomes temporarily invisible.

Conceptually:

```text
Queue
 ↓
Worker A receives message
 ↓
Message temporarily invisible
```

If Worker A successfully finishes:

```text
Delete message
```

If Worker A crashes:

```text
Message becomes visible again
```

This enables retry behavior.

---

## 22. Retry

Suppose:

```text
Lambda
 ↓
External API
```

External API returns:

```text
500
```

You don't necessarily want to permanently lose the job.

Instead:

```text
Attempt 1 ❌
   ↓
Retry
   ↓
Attempt 2 ❌
   ↓
Retry
   ↓
Attempt 3 ❌
```

Eventually:

```text
Success
```

or:

```text
Dead Letter Queue
```

---

## 23. Dead Letter Queue

DLQ = **Dead Letter Queue**.

If a message repeatedly fails:

```text
SQS
 ↓
Worker
 ↓
❌
 ↓
Retry
 ↓
❌
 ↓
Retry
 ↓
❌
 ↓
DLQ
```

Now you can inspect failed jobs instead of silently losing them.

This is a very important production pattern.

---

## 24. Lambda + SQS

AWS can connect Lambda to SQS.

Architecture:

```text
Node.js API
     ↓
    SQS
     ↓
   Lambda
     ↓
Process message
```

Lambda can poll/process messages from the queue through an event source integration.

You don't have to maintain:

```text
Worker EC2
```

yourself.

---

## 25. Practical Example — Order Processing

Suppose:

```text
POST /orders
```

Node.js:

```typescript
await sqs.send(
  new SendMessageCommand({
    QueueUrl: process.env.ORDER_QUEUE_URL,
    MessageBody: JSON.stringify({
      orderId,
      userId,
    }),
  })
);
```

Then return:

```json
{
  "message": "Order accepted"
}
```

The API doesn't need to perform every downstream task synchronously.

---

## 26. Lambda Consumer

Conceptually:

```typescript
export const handler = async (event) => {
  for (const record of event.Records) {
    const message = JSON.parse(record.body);

    await processOrder(message.orderId);
  }
};
```

Architecture:

```text
POST /orders
     ↓
Node.js
     ↓
SQS
     ↓
Lambda
     ↓
processOrder()
```

This is a **real backend production pattern**.

---

## 27. SNS

SNS = **Simple Notification Service**.

Think:

> **Publish a message and let multiple subscribers receive it.**

Architecture:

```text
                SNS Topic
              /     |      \
             ↓      ↓       ↓
           SQS    Lambda   Email
```

This is different from a simple queue.

---

## 28. Queue vs Pub/Sub

#### Queue

```text
Producer
   ↓
Queue
   ↓
Consumer
```

Usually the work is distributed among consumers.

#### Pub/Sub

```text
Publisher
    ↓
  Topic
 /  |  \
↓   ↓   ↓
A   B   C
```

Multiple subscribers can independently receive the event.

---

## 29. Example SNS Architecture

Suppose an order is created.

```text
Order Service
     ↓
SNS Topic
  /     \
 ↓       ↓
Email   Analytics
Lambda   Lambda
```

Now the order service doesn't need to know the internal implementation of each consumer.

That's **decoupling**.

---

## 30. SQS vs SNS

| | SQS | SNS |
|---|---|---|
| Main idea | Queue | Pub/Sub |
| Consumer model | Work queue | Multiple subscribers |
| Buffer messages | Yes | Not primarily |
| Decoupling | Yes | Yes |
| Common use | Background jobs | Event fan-out |

A common architecture combines them:

```text
             SNS
           /     \
          ↓       ↓
        SQS-A   SQS-B
          ↓       ↓
       Worker   Worker
```

---

## 31. Why Not Directly Connect Everything?

Bad:

```text
Order Service
 ├── Email Service
 ├── Analytics
 ├── Inventory
 ├── Notification
 └── Shipping
```

Now Order Service knows about everything.

Better:

```text
                  Order Service
                       ↓
                    SNS
              ┌────────┼────────┐
              ↓        ↓        ↓
             SQS      SQS      Lambda
              ↓        ↓
           Inventory Shipping
```

Now services are more loosely coupled.

---

## 32. Event-Driven Architecture

This leads to:

> **Event-driven architecture**

Instead of:

```text
Service A
 ↓
directly call
 ↓
Service B
```

you can have:

```text
Service A
 ↓
Event
 ↓
Message infrastructure
 ↓
Service B
```

For example:

```text
OrderCreated
```

could trigger:

```text
Inventory
Notification
Analytics
Email
```

independently.

---

## 33. Lambda Cold Starts

Lambda execution environments can be reused, but sometimes AWS needs to initialize a new execution environment.

This can introduce:

```text
Cold start
```

Conceptually:

```text
Request
 ↓
Create environment
 ↓
Load runtime
 ↓
Load application
 ↓
Execute
```

versus a warm execution environment:

```text
Request
 ↓
Existing environment
 ↓
Execute
```

Cold starts can matter for latency-sensitive workloads.

---

## 34. Lambda Concurrency

Suppose:

```text
1 request
 ↓
1 Lambda execution
```

Now:

```text
100 requests
```

Lambda can execute multiple instances of the function concurrently, subject to account/function limits and configuration.

Conceptually:

```text
                Lambda
             /    |    \
            ↓     ↓     ↓
         Exec 1 Exec 2 Exec 3
```

This is another form of automatic horizontal execution scaling.

---

## 35. The Danger of Uncontrolled Scaling

Suppose:

```text
SQS
 ↓
Lambda
```

Suddenly:

```text
1,000,000 messages
```

Lambda may process a large number concurrently.

But downstream:

```text
Lambda
 ↓
RDS
```

could overwhelm your database.

Again:

> **Scaling one component can overload another component.**

This is the same lesson we learned with EC2 + RDS.

You need:

- concurrency controls
- batching
- queue design
- connection management
- backpressure
- database capacity planning

---

## 36. Lambda + RDS

This architecture deserves attention:

```text
Lambda
  ↓
RDS
```

It can work, but high Lambda concurrency can create database connection pressure.

For relational databases, AWS provides **RDS Proxy** as one option for managing database connections between applications such as Lambda and RDS.

Mental model:

```text
Lambda Lambda Lambda Lambda
    \     |     |     /
          ↓
      RDS Proxy
          ↓
         RDS
```

You don't need deep RDS Proxy administration for this roadmap, but understand **why it exists**.

---

## 37. Lambda vs EC2

| | EC2 | Lambda |
|---|---|---|
| Server management | You manage more | AWS manages execution infrastructure |
| Runtime | Long-running | Event/function execution |
| Scaling | ASG etc. | Managed concurrency model |
| Billing model | Instance/resource usage | Invocation/execution based |
| Best fit | Long-running APIs/workloads | Event-driven/short-lived workloads |
| Control | High | Lower |

Don't interpret this as:

> Lambda is always better.

It's a different execution model.

---

## 38. Lambda vs Containers

You now have three important choices:

```text
                    Compute
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
         EC2       Containers     Lambda
                       │
                    ECS/EKS
```

#### EC2

Maximum infrastructure control.

#### Containers

Package application + dependencies consistently.

#### Lambda

Run event-driven functions without managing servers.

We'll later connect these choices to Kubernetes.

---

## PART 4 — Actually Using DevOps With Lambda

Here's where your earlier criticism matters.

A proper workflow looks like:

```text
Developer
   ↓
Git
   ↓
GitHub
   ↓
Pull Request
   ↓
GitHub Actions
   ↓
Install
   ↓
Lint
   ↓
Typecheck
   ↓
Test
   ↓
Build
   ↓
Package
   ↓
Deploy Lambda
   ↓
AWS
```

That is **DevOps**, not just knowing what Lambda is.

---

## 39. Example GitHub Actions Pipeline

Conceptually:

```yaml
name: Deploy Lambda

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    permissions:
      id-token: write
      contents: read

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22

      - run: npm ci

      - run: npm test

      - run: npm run build

      - run: |
          zip -r lambda.zip dist node_modules

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE }}
          aws-region: ap-south-1

      - run: |
          aws lambda update-function-code \
            --function-name my-function \
            --zip-file fileb://lambda.zip
```

The exact production pipeline can be improved later, but understand the workflow.

---

## 40. What Happened Here?

You should be able to explain every stage:

```text
checkout
 ↓
Get code

setup-node
 ↓
Install Node

npm ci
 ↓
Reproducible dependencies

npm test
 ↓
Quality gate

npm run build
 ↓
TypeScript → JavaScript

zip
 ↓
Deployment artifact

AWS credentials
 ↓
OIDC → IAM role

aws lambda update-function-code
 ↓
Deploy
```

**That is the practical DevOps skill we're going to emphasize from here onward.**

---

## 41. Better Production Approach

As we progress, you'll learn Infrastructure as Code.

Eventually:

```text
Terraform
   ↓
Create:
 ├── Lambda
 ├── IAM role
 ├── SQS
 ├── SNS
 ├── API Gateway
 ├── VPC
 └── other infrastructure
```

Then:

```text
Git
 ↓
Terraform plan
 ↓
Review
 ↓
Terraform apply
```

That's much more reproducible than manually clicking around AWS Console.

Terraform is [Chapter 21](../06-iac-config/ch21-terraform.md), so we're intentionally building toward it.

---

## 42. Complete Example Architecture

Here's a realistic serverless order system:

```text
                         USER
                           │
                           ↓
                      API Gateway
                           │
                           ↓
                     Lambda API
                           │
                           ↓
                          SQS
                           │
                           ↓
                    Lambda Worker
                     /         \
                    ↓           ↓
                  RDS          SNS
                               / \
                              ↓   ↓
                           Email Analytics
```

Now imagine DevOps around it:

```text
GitHub
   ↓
GitHub Actions
   ↓
Test
   ↓
Build
   ↓
Deploy
   ↓
Lambda + SQS + SNS + infrastructure
```

---

## 43. Where Docker Fits

Important question:

> If Lambda exists, why did we spend so much time learning Docker?

Because Lambda doesn't replace containers.

Your production architecture could be:

```text
                    ALB
                     ↓
               ECS/EKS/EC2
                     ↓
               Main Node API
                     │
                     ↓
                    SQS
                     ↓
                  Lambda
```

Use:

```text
Containers
→ main long-running backend

Lambda
→ event-driven/background functions
```

depending on workload.

---

## 44. Production Decision Framework

When choosing:

#### EC2

Ask:

> Do I need maximum server-level control?

#### Containers

Ask:

> Do I have a long-running application that I want packaged consistently?

#### Lambda

Ask:

> Is this naturally event-driven and suitable for function-based execution?

#### SQS

Ask:

> Do I need asynchronous work buffering?

#### SNS

Ask:

> Do multiple consumers need to receive an event?

That's much more useful than memorizing definitions.

---

## 45. What You Should Master

#### 🔥 Deep

- Lambda fundamentals
- handlers/events
- invocation
- IAM execution roles
- environment variables
- Lambda + API Gateway concept
- Lambda + S3
- Lambda + SQS
- retries
- visibility timeout
- DLQs
- idempotency
- concurrency
- cold starts
- event-driven architecture
- asynchronous processing
- SQS vs SNS
- queue vs pub/sub
- Lambda + RDS considerations
- CI/CD deployment of Lambda

#### Medium

- Lambda layers
- provisioned concurrency
- API Gateway details
- RDS Proxy
- batching

#### Awareness

- Step Functions
- EventBridge
- advanced serverless patterns

We'll encounter some of these again when they naturally fit.

---

## 🧪 Your Practical Assignment

Build this locally first:

```text
Node.js API
    ↓
Queue
    ↓
Worker
```

The API should expose:

```text
POST /jobs
```

Request:

```json
{
  "type": "send-email",
  "userId": "123"
}
```

Instead of processing the email immediately:

```text
POST /jobs
     ↓
Queue
     ↓
202 Accepted
```

Worker:

```text
Queue
 ↓
Worker
 ↓
processJob()
```

Then add:

```text
retry
idempotency
failure handling
```

Once you understand that locally, move the architecture toward:

```text
Node.js
   ↓
AWS SQS
   ↓
AWS Lambda
```

And eventually:

```text
GitHub
   ↓
GitHub Actions
   ↓
AWS
```

That progression will teach you **DevOps by actually doing it**, rather than simply memorizing AWS services.

---

## 🧠 The Big Picture After Chapter 15

You now have:

```text
                 GitHub
                    │
                    ↓
              GitHub Actions
                    │
          ┌─────────┴─────────┐
          ↓                   ↓
       Docker              Lambda
          │                   │
          ↓                   ↓
      EC2/ECS/EKS           SQS
          │                   │
          └─────────┬─────────┘
                    ↓
                   RDS
```

And AWS networking:

```text
VPC
├── Public Subnets
│    └── ALB
│
├── Private App Subnets
│    └── EC2 / Containers
│
└── Private DB Subnets
     └── RDS
```

---
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 14: Load Balancing + Scaling](ch14-load-balancing-scaling.md) · [Chapter 16: Route 53 + CloudFront + CDN + WAF](ch16-route53-cloudfront-waf.md) → · [Revision sheet](../../revision/ch15-revision.md)
