# Chapter 13 — Revision Sheet: RDS + Databases on AWS

> Supplements [the full chapter](../docs/04-aws/ch13-rds-databases.md). Focus: how databases run on AWS, how to secure, scale and back them up, and how Node.js connects.

## RDS basics

- **RDS = Relational Database Service**, AWS-managed relational databases. Engines: PostgreSQL, MySQL, MariaDB, Oracle, SQL Server (PostgreSQL and MySQL matter most for this career path).
- You manage: schema, queries, users, connections, configuration, app behaviour, performance. AWS manages much of: infrastructure, maintenance, backups, patching mechanisms, monitoring integrations, HA features.
- **RDS vs DB on EC2:** RDS reduces operational burden in exchange for less infrastructure-level control. On EC2 you own OS, updates, backups, monitoring, replication, recovery.
- **Managed ≠ zero responsibility:** still think about maintenance windows, app compatibility, migrations, backups, performance, connections, security, recovery.

## Placement & networking

Internet → ALB → EC2 (private app subnets) → RDS (private DB subnets). `ALB-SG :443 → API-SG :3000 → DB-SG :5432`; DB SG allows `TCP 5432` from **Source = API-SG**, never `0.0.0.0/0`.

## Connecting from Node.js

```typescript
import { Pool } from "pg";
const pool = new Pool({
  host: process.env.DB_HOST, port: 5432,
  user: process.env.DB_USER, password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
});
// or: new Pool({ connectionString: process.env.DATABASE_URL, max: 20 });
const result = await pool.query("SELECT * FROM users WHERE id = $1", [userId]);
```

Endpoint looks like `mydb.xxxxx.region.rds.amazonaws.com`. Never hard-code credentials or commit them; use configuration + **Secrets Manager** (app retrieves DB credentials according to its IAM permissions).

## Connection pooling & exhaustion (very important)

- Without a pool every request opens/closes a DB connection → wasted resources, overwhelmed DB. A **pool** keeps reusable connections.
- **Total connections = instances × pool size.** 10 EC2 × 100 = 1000; 20 API instances × `max: 50` = 1000 → DB may hit its connection limit → failures/timeouts.
- **Key lesson:** scaling application servers without considering DB connection limits can make the system *less* stable.
- **Scenario (2 → 20 EC2, PostgreSQL rejects connections):** connection count multiplied by instances. Fixes: tune pool sizes, control app concurrency, use **RDS Proxy**, optimise queries, caching, scale the DB.

## High availability vs scaling

| Mechanism | Purpose |
|---|---|
| **Multi-AZ** | Primary (AZ-A) + standby (AZ-B) for **HA/failover**, not read scaling. On failure the standby becomes primary; the app keeps using the same RDS **endpoint** |
| **Read replica** | Copies data for **read scaling**: writes → primary, reads → replicas (good for ~90% read workloads) |
| **Connection pool** | Efficient DB connections |
| **Cache (Redis)** | Reduce DB traffic: request → Redis hit → response; miss → PostgreSQL → populate Redis |
| **Vertical scaling** | More vCPU/RAM (e.g. 4 vCPU/16 GB → 8 vCPU/32 GB): simple but has a ceiling |
| **Backups** | Recovery |
| **Private subnet** | Network isolation |

**Databases don't scale like EC2** (can't just add instances): consider vertical scaling, read replicas, caching, query optimisation, indexes, partitioning, sharding, connection pooling, architecture.

**Replication lag / read-after-write problem:** `POST /profile` (write to primary) then immediate `GET /profile` served by a lagging replica returns stale data (eventual consistency behaviour). Mitigations: route critical immediate reads to primary, consistency-aware routing, tolerate small delays where acceptable, design around consistency requirements.

## Backup & recovery

- **Automated backups** = ongoing recovery capability (accidental deletion, corruption, operational recovery). **Snapshot** = explicit point-in-time copy of the database storage/state (migrations, cloning environments, backups, testing, recovery).
- **Point-in-time recovery:** e.g. bad deployment deletes data Tuesday 14:37 → restore to a point before the incident (part of disaster recovery).

## Configuration, storage, security, monitoring

- **Parameter groups** manage engine configuration (memory, connection limits, logging, query behaviour). **Option groups** configure additional engine-specific features (low priority).
- **Storage/IOPS:** capacity, type, IOPS, throughput, autoscaling options. **IOPS** = I/O operations per second; low storage performance → higher latency. DB performance = CPU, memory, storage throughput, IOPS, connections, locks, queries, indexes.
- **Encryption:** at rest (storage encryption, **KMS**-managed keys) and in transit (TLS).
- **Monitor:** CPU, memory-related metrics, connections, storage, IOPS, latency, throughput + app-level request latency, error rate, query latency, timeouts (CloudWatch, Ch.17/22).

## RDS vs DynamoDB vs DB on EC2

| | RDS | DB on EC2 | DynamoDB |
|---|---|---|---|
| Type | Managed relational | Self-managed relational | Managed NoSQL (key-value/document) |
| SQL | Yes | Yes | No traditional relational SQL |
| OS mgmt | AWS handles much | You | AWS handles infrastructure |
| Fit | Relationships, complex SQL, relational consistency | Same | Key-value access, very high scale, predictable access patterns, low latency |
| Ops burden | Lower | Higher | Lower |

DynamoDB is not "faster RDS" — different data model and access patterns.

## Migrations

Manage schema changes with migration tools (Prisma Migrate, Drizzle, TypeORM, Knex) — never hand-edit production. Flow: `schema.prisma` → migration → PostgreSQL → RDS; `npx prisma migrate deploy` in a controlled deployment.
**Don't blindly run destructive migrations:** deploy `DROP COLUMN` while the old app version is running → 💥. **Expand-and-contract:** expand → deploy compatible app → migrate data → switch usage → remove old structure later.

## Request path

User → DNS → ALB → EC2 → Node.js → connection pool → RDS PostgreSQL → query → Node.js → ALB → User.
**If RDS "is down" (500s):** RDS available? endpoint? port? EC2 can reach RDS? DB SG allows EC2 SG? DB accepting connections? pool exhausted? credentials? queries timing out? DB overloaded?

## Depth guide (from the chapter)

Know deeply: RDS concept, RDS vs EC2 DB, private DB architecture, SGs, PostgreSQL connectivity, pooling, Multi-AZ, read replicas, replication lag, backups, snapshots, PITR, encryption, Secrets Manager, scaling, connection exhaustion, migrations, RDS vs DynamoDB. Medium: storage/IOPS, parameter groups, monitoring, maintenance windows, RDS Proxy. Awareness: every engine, obscure features, advanced DBA.

## Added notes (not in source)

- **RDS Proxy** (mentioned but not explained): a managed proxy that pools/multiplexes connections between apps (e.g. many Lambda/EC2 clients) and the DB, reduces connection storms, and speeds up failover handling.
- Multi-AZ comes in two shapes: a *Multi-AZ DB instance* (standby is **not** readable) and a *Multi-AZ DB cluster* (readable standbys). **Aurora** is a separate AWS-built engine family not covered in this chapter.
- Failover works by switching the endpoint's DNS to the standby, so apps should **reconnect with retries** and avoid caching DNS too long.
- Read replicas replicate **asynchronously** (hence lag); a replica can be promoted to a standalone DB.
- PITR needs automated backups enabled (retention period configurable) and restores into a **new** DB instance. Automated backups are tied to the instance's retention window; manual snapshots persist until you delete them.
- A PostgreSQL instance's `max_connections` scales with instance size/memory and is set via parameter group.
- `prisma migrate deploy` applies existing migrations (CI/production); `prisma migrate dev` is for development.

## Interview scenario answer skeleton

*Design prod PostgreSQL on AWS:* private subnets + SG from API-SG only + encryption + Secrets Manager + Multi-AZ + automated backups/snapshots/PITR + pooling + monitoring; scale reads with replicas/cache, writes with vertical scaling/optimisation; control connections (pool size × instances, RDS Proxy).

<!-- NAV -->

---

← [Sheet 12](ch12-revision.md) · [Full chapter 13](../docs/04-aws/ch13-rds-databases.md) · [All revision material](README.md) · [Sheet 14](ch14-revision.md) →
