import { DeleteMessageCommand, ReceiveMessageCommand } from "@aws-sdk/client-sqs";
import { config, pool, sqs } from "./config";

let running = true;

// Idempotent state transition (Chapter 35 section 21): only PENDING -> PROCESSING -> COMPLETED moves forward,
// so a redelivered message for an already-handled order is a no-op.
async function handle(orderId: number): Promise<void> {
  const claim = await pool.query(
    "UPDATE orders SET status='PROCESSING' WHERE id=$1 AND status='PENDING' RETURNING id",
    [orderId],
  );
  if (claim.rowCount === 0) return; // already processed (or cancelled): duplicate delivery is safe
  try {
    // ... real work here (send notification, generate invoice, write to S3, ...)
    await pool.query("UPDATE orders SET status='COMPLETED' WHERE id=$1", [orderId]);
  } catch (e) {
    await pool.query("UPDATE orders SET status='FAILED' WHERE id=$1", [orderId]);
    throw e; // message is not deleted -> visibility timeout -> retry -> eventually the DLQ
  }
}

async function loop(): Promise<void> {
  while (running) {
    const out = await sqs.send(
      new ReceiveMessageCommand({
        QueueUrl: config.queueUrl,
        MaxNumberOfMessages: 5,
        WaitTimeSeconds: 20,
        VisibilityTimeout: 60,
      }),
    );
    for (const m of out.Messages ?? []) {
      try {
        const body = JSON.parse(m.Body ?? "{}") as { event?: string; orderId?: number };
        if (body.event === "ORDER_CREATED" && body.orderId) await handle(body.orderId);
        await sqs.send(new DeleteMessageCommand({ QueueUrl: config.queueUrl, ReceiptHandle: m.ReceiptHandle! }));
      } catch (e) {
        console.error(JSON.stringify({ level: "error", msg: (e as Error).message, messageId: m.MessageId }));
      }
    }
  }
}

const stop = () => {
  running = false;
};
process.on("SIGTERM", stop);
process.on("SIGINT", stop);

loop()
  .catch((e) => {
    console.error(JSON.stringify({ level: "fatal", msg: (e as Error).message }));
    process.exitCode = 1;
  })
  .finally(async () => {
    await pool.end().catch(() => undefined);
    process.exit(process.exitCode ?? 0);
  });
