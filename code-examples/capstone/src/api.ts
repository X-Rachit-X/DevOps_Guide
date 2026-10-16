import express, { NextFunction, Request, Response } from "express";
import { SendMessageCommand } from "@aws-sdk/client-sqs";
import { config, pool, redis, sqs } from "./config";

const app = express();
app.use(express.json());

let shuttingDown = false;

// Liveness: process is alive; do NOT depend on external systems (Chapter 35 section 28).
app.get("/health/live", (_req, res) => {
  res.json({ status: "alive" });
});

// Readiness: critical dependency (PostgreSQL) reachable and not shutting down (section 29).
app.get("/health/ready", async (_req, res) => {
  if (shuttingDown) return res.status(503).json({ status: "shutting-down" });
  try {
    await pool.query("SELECT 1");
    res.json({ status: "ready" });
  } catch {
    res.status(503).json({ status: "db-unavailable" });
  }
});

interface OrderItemInput {
  productId: number;
  quantity: number;
  price: number;
}

// Idempotent order creation (section 11): same Idempotency-Key => same order, no duplicate.
app.post("/orders", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const key = req.header("Idempotency-Key");
    const { userId, items } = req.body as { userId: number; items: OrderItemInput[] };
    if (!key || !userId || !Array.isArray(items) || items.length === 0) {
      return res.status(400).json({ error: "Idempotency-Key header, userId and items are required" });
    }
    const total = items.reduce((s, i) => s + i.price * i.quantity, 0);

    const client = await pool.connect();
    let orderId: number;
    let created = false;
    try {
      await client.query("BEGIN");
      // UNIQUE(idempotency_key) + ON CONFLICT DO NOTHING handles concurrent duplicates safely.
      const ins = await client.query(
        `INSERT INTO orders (user_id, total_amount, idempotency_key) VALUES ($1,$2,$3)
         ON CONFLICT (idempotency_key) DO NOTHING RETURNING id`,
        [userId, total, key],
      );
      if (ins.rowCount === 0) {
        const existing = await client.query("SELECT id FROM orders WHERE idempotency_key=$1", [key]);
        orderId = existing.rows[0].id;
      } else {
        orderId = ins.rows[0].id;
        created = true;
        for (const i of items) {
          await client.query(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES ($1,$2,$3,$4)",
            [orderId, i.productId, i.quantity, i.price],
          );
        }
      }
      await client.query("COMMIT");
    } catch (e) {
      await client.query("ROLLBACK");
      throw e;
    } finally {
      client.release();
    }

    if (created) {
      // Known gap (Chapter 33 outbox pattern): if this send fails after COMMIT the order stays PENDING.
      await sqs.send(
        new SendMessageCommand({
          QueueUrl: config.queueUrl,
          MessageBody: JSON.stringify({ event: "ORDER_CREATED", orderId, attempt: 1 }),
        }),
      );
    }
    res.status(created ? 202 : 200).json({ orderId, status: "PENDING", duplicate: !created });
  } catch (e) {
    next(e);
  }
});

// Cache-aside read (section 14); cache failure must not fail the request (section 15).
app.get("/orders/:id", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const id = Number(req.params.id);
    const cacheKey = `order:${id}`;
    try {
      const hit = redis ? await redis.get(cacheKey) : null;
      if (hit) return res.json(JSON.parse(hit));
    } catch {
      /* cache down: fall through to the database */
    }
    const r = await pool.query("SELECT id, user_id, status, total_amount FROM orders WHERE id=$1", [id]);
    if (r.rowCount === 0) return res.status(404).json({ error: "not found" });
    try {
      if (redis) await redis.set(cacheKey, JSON.stringify(r.rows[0]), "EX", 30);
    } catch {
      /* ignore cache write failure */
    }
    res.json(r.rows[0]);
  } catch (e) {
    next(e);
  }
});

app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error(JSON.stringify({ level: "error", msg: err.message })); // never log secrets (section 64)
  res.status(500).json({ error: "internal error" });
});

const server = app.listen(config.port, "0.0.0.0", () =>
  console.log(JSON.stringify({ level: "info", msg: "api listening", port: config.port })),
);

// Graceful shutdown (section 30): fail readiness, stop new connections, finish in-flight, close DB/Redis.
const shutdown = (signal: string) => {
  console.log(JSON.stringify({ level: "info", msg: "shutdown", signal }));
  shuttingDown = true;
  server.close(async () => {
    await pool.end().catch(() => undefined);
    if (redis) redis.disconnect();
    process.exit(0);
  });
  setTimeout(() => process.exit(1), 25_000).unref(); // keep below terminationGracePeriodSeconds
};
process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("SIGINT", () => shutdown("SIGINT"));
