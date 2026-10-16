# Chapter 15 — Revision Sheet: Lambda + Serverless + Messaging

> Supplements [the full chapter](../docs/04-aws/ch15-lambda-serverless-messaging.md). Two goals: understand **serverless/Lambda**, and understand **messaging/event-driven systems** and actually use them.

## Lambda in one page

- **Lambda = run code without managing servers.** Event → Lambda → function executes → done (vs EC2 running 24/7 for an occasional job such as image resize).
- **Terms:** Function · Runtime (e.g. Node.js) · Handler (`index.handler` = `handler()` exported from `index.js`) · Event · Invocation · Execution environment · Timeout · Memory · Environment variables · Concurrency · Cold start · Layers.
- **Handler:**
```typescript
import type { APIGatewayProxyHandlerV2 } from "aws-lambda";
export const handler: APIGatewayProxyHandlerV2 = async () => ({
  statusCode: 200,
  body: JSON.stringify({ message: "Hello from Lambda!" }),
});
```
- **Express vs Lambda:** Express needs server, port, process, infrastructure; Lambda: AWS manages the execution environment and calls `handler(event)`.
- **Event sources:** API Gateway, S3, SQS, SNS, EventBridge, CloudWatch Events. Examples: S3 upload → Lambda → process file; SQS message → Lambda → process job.
- **Project:** `lambda-demo/ {package.json, src/index.ts, tsconfig.json}`; `npm init -y`, `npm install -D typescript @types/aws-lambda`, `npx tsc` → JavaScript → package (zip) → deploy. Deploy ways: Console, CLI, Infrastructure as Code (CLI/IaC mindset preferred).
- **Environment variables** (`process.env.DB_HOST`); don't treat plain env vars as a secret vault — use proper secrets management.
- **Execution role (IAM):** least privilege (e.g. `s3:GetObject` on a specific bucket/path, never `*`).
- **Cold start:** new execution environment must be created → load runtime → load app → execute (a warm environment skips this); matters for latency-sensitive paths.
- **Concurrency:** many concurrent executions automatically (subject to account/function limits).
- **Danger of uncontrolled scaling:** 1,000,000 SQS messages → massive Lambda concurrency → downstream RDS overwhelmed. Needs concurrency controls, batching, queue design, connection management, **backpressure**, DB capacity planning. **Lambda + RDS** → connection pressure → **RDS Proxy** (Lambda × N → RDS Proxy → RDS).

## EC2 vs containers vs Lambda

| | EC2 | Lambda |
|---|---|---|
| Server management | You manage more | AWS manages execution infrastructure |
| Runtime | Long-running | Event/function execution |
| Scaling | ASG etc. | Managed concurrency |
| Billing | Instance/resource usage | Invocation/execution based |
| Best for | Long-running APIs/workloads | Event-driven, short-lived workloads |
| Control | High | Lower |

Decision: EC2 = max server control · Containers = long-running app packaged consistently · Lambda = naturally event-driven functions · SQS = async buffering · SNS = multiple consumers need the event. Containers (ECS/EKS/EC2) run the main backend; Lambda handles event-driven/background functions — **Lambda doesn't replace Docker**.

## Messaging

**Async processing:** `POST /send-email` → API puts job in queue → responds immediately → worker calls email provider. Prevents API latency growth when the provider is slow. Benefits: decoupling, buffering, retrying, async processing, traffic smoothing, failure isolation.

| | **SQS** | **SNS** |
|---|---|---|
| Idea | Queue (buffer of work): producer → queue → consumer | Pub/Sub: publisher → topic → many subscribers |
| Consumers | Work distributed among consumers | Multiple subscribers independently receive the event |
| Buffering | Yes | Not primarily |
| Use | Background jobs | Event fan-out |

Combined pattern: SNS → SQS-A, SQS-B → workers. Order Service publishes to SNS; Inventory/Shipping via SQS, email/analytics via Lambda; the producer needn't know the consumers (**decoupling**; event-driven architecture, e.g. `OrderCreated`).

### Reliability concepts (high-yield)

- **SQS Standard** is highly scalable but don't assume exactly-once → design for duplicates → **idempotency**: e.g. `orderId=123`, "payment already processed?" yes → skip, no → process (don't charge twice).
- **Visibility timeout:** a received message becomes temporarily invisible; success → delete; worker crash → visible again → retry.
- **Retry:** failed attempts retried; persistent failures go to a **Dead Letter Queue (DLQ)** so failed jobs can be inspected instead of silently lost.
- **Lambda + SQS:** Lambda consumes through an event-source integration (no worker EC2 to run).

```typescript
// Producer (Node API)
await sqs.send(new SendMessageCommand({
  QueueUrl: process.env.ORDER_QUEUE_URL,
  MessageBody: JSON.stringify({ orderId, userId }),
}));  // → respond { "message": "Order accepted" } (e.g. 202)

// Consumer (Lambda)
export const handler = async (event) => {
  for (const record of event.Records) {
    const message = JSON.parse(record.body);
    await processOrder(message.orderId);
  }
};
```

## Lambda CI/CD pipeline (concept)

```yaml
name: Deploy Lambda
on: { push: { branches: [main] } }
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions: { id-token: write, contents: read }   # needed for OIDC
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - run: npm ci
      - run: npm test
      - run: npm run build
      - run: zip -r lambda.zip dist node_modules
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE }}
          aws-region: ap-south-1
      - run: aws lambda update-function-code --function-name my-function --zip-file fileb://lambda.zip
```
checkout (get code) · setup-node · `npm ci` (reproducible) · `npm test` (quality gate) · build (TS→JS) · zip (artifact) · OIDC → IAM role (no static keys) · `update-function-code` (deploy). Better: Terraform creates Lambda, IAM role, SQS, SNS, API Gateway, VPC → `plan` → review → `apply` (Ch.21).

## Serverless order system

User → API Gateway → Lambda API → SQS → Lambda Worker → RDS + SNS → (Email, Analytics).

## Depth guide

Deep: Lambda fundamentals, handlers/events, invocation, execution roles, env vars, Lambda + API Gateway/S3/SQS, retries, visibility timeout, DLQs, idempotency, concurrency, cold starts, event-driven, async processing, SQS vs SNS, queue vs pub/sub, Lambda + RDS, Lambda CI/CD. Medium: layers, provisioned concurrency, API Gateway details, RDS Proxy, batching. Awareness: Step Functions, EventBridge, advanced serverless.

## Practical assignment

`POST /jobs {type:"send-email", userId:"123"}` → queue → `202 Accepted` → worker `processJob()`; add retry, idempotency, failure handling; then move to Node → SQS → Lambda; then GitHub Actions → AWS.

## Added notes (not in source)

- **Limits to remember (verify current docs):** Lambda timeout up to 15 min; memory 128 MB–10 GB with CPU proportional to memory; synchronous payload ≈ 6 MB; default regional concurrency ≈ 1,000 (use *reserved concurrency* or the SQS event-source *maximum concurrency* to cap load on a database).
- **SQS Standard** = at-least-once delivery, best-effort ordering; **FIFO** queues give ordering and deduplication. Set the queue's **visibility timeout ≥ the Lambda function timeout** (AWS recommends a multiple); configure the DLQ with `maxReceiveCount`.
- The consumer loop above fails the **whole batch** if one record throws, so successful records are retried (duplicates) — use *partial batch responses* (`ReportBatchItemFailures`) and idempotent processing.
- Idempotency techniques: idempotency key stored with a unique constraint, conditional writes, upsert, state checks.
- `aws lambda update-function-code` returns before the update is complete; use `aws lambda wait function-updated` before publishing/invoking in pipelines.
- `zip -r lambda.zip dist node_modules` ships dev dependencies too; prune with `npm ci --omit=dev` (or bundle with esbuild) to reduce package size and cold starts.
- `${{ secrets.AWS_DEPLOY_ROLE }}` holds a role ARN — not secret by nature, but kept in a secret/variable for convenience.

<!-- NAV -->

---

← [Sheet 14](ch14-revision.md) · [Full chapter 15](../docs/04-aws/ch15-lambda-serverless-messaging.md) · [All revision material](README.md) · [Sheet 16](ch16-revision.md) →
