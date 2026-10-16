# Chapter 13 — RDS + Databases on AWS

> **Source:** Response 13 of the original conversation (`source-archive/src-13.txt`, lines 1–1643) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch13-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

We're continuing the **locked 24-response roadmap**. At this point, you've learned how to build the network around your backend. Now we're going inside the **database layer**.

You already know DBMS and SQL, so I won't re-teach SQL. Instead, we'll focus on:

> **How databases actually run in AWS, how to secure them, scale them, back them up, and connect your Node.js backend to them.**

---

## 1. What is Amazon RDS?

**RDS = Relational Database Service.**

It is AWS's managed service for relational databases.

Instead of doing:

```text
EC2
 ├── Linux
 ├── PostgreSQL
 ├── Configure PostgreSQL
 ├── Configure backups
 ├── Configure updates
 ├── Monitor database
 └── Maintain database
```

you can use:

```text
AWS
 │
 └── RDS
      └── PostgreSQL
```

AWS handles much of the underlying database infrastructure.

You focus primarily on:

- schema
- queries
- users
- connections
- configuration
- application behavior
- performance

---

## 2. Which Databases Can RDS Run?

RDS supports several relational engines, including:

- PostgreSQL
- MySQL
- MariaDB
- Oracle
- SQL Server

For your backend career, the most important ones are:

```text
PostgreSQL
MySQL
```

Your mental model should therefore be:

```text
Node.js / NestJS
       ↓
   PostgreSQL
       ↓
      RDS
```

---

## 3. RDS vs Database on EC2

This is a classic interview question.

#### Database on EC2

You manage:

```text
EC2
 ├── OS
 ├── PostgreSQL
 ├── Updates
 ├── Backups
 ├── Monitoring
 ├── Replication
 └── Recovery
```

#### RDS

AWS manages much of:

```text
Infrastructure
Maintenance
Backups
Patching mechanisms
Monitoring integrations
High availability features
```

while you manage the database itself and its configuration/data.

The fundamental tradeoff:

> **RDS reduces operational burden in exchange for less infrastructure-level control than running the database yourself.**

---

## 4. Where Should RDS Live?

Remember [Chapter 12](ch12-vpc-networking.md).

You generally don't want:

```text
Internet
   ↓
RDS
```

Instead:

```text
Internet
   ↓
ALB
   ↓
EC2
   ↓
RDS
```

And the database should generally be in private subnets.

Example:

```text
                 INTERNET
                     │
                     ↓
                    ALB
                     │
                     ↓
             Private App Subnet
                 ┌───┴───┐
                 ↓       ↓
                EC2     EC2
                 │       │
                 └───┬───┘
                     ↓
             Private DB Subnet
                     │
                    RDS
```

---

## 5. RDS and Security Groups

Suppose PostgreSQL uses:

```text
5432
```

Create:

```text
ALB-SG
API-SG
DB-SG
```

Then:

```text
Internet
    ↓
ALB-SG :443
    ↓
API-SG :3000
    ↓
DB-SG :5432
```

RDS's security group should allow:

```text
TCP 5432
Source = API-SG
```

Not:

```text
TCP 5432
Source = 0.0.0.0/0
```

That's a fundamental production security principle.

---

## 6. How Does Node.js Connect to RDS?

Suppose RDS provides a database endpoint such as:

```text
mydb.xxxxx.region.rds.amazonaws.com
```

Your Node.js application connects using:

```text
Host
Port
Username
Password
Database name
```

Example:

```typescript
import { Pool } from "pg";

const pool = new Pool({
  host: process.env.DB_HOST,
  port: 5432,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
});
```

Your application should **not** hardcode these values.

Use environment/configuration management.

---

## 7. Never Put Database Credentials in Git

Bad:

```typescript
const password = "mySuperSecretPassword";
```

And especially:

```text
GitHub
   ↓
database password ❌
```

Instead:

```text
Secrets/configuration
       ↓
Application
       ↓
RDS
```

We'll go deeper into AWS secrets/security later.

---

## 8. Connection Pooling

This is extremely important for backend interviews.

Imagine 1,000 API requests.

If every request creates a brand-new database connection:

```text
Request
 ↓
Create DB connection
 ↓
Query
 ↓
Close connection
```

you can waste resources and overwhelm the database.

Instead:

```text
Node.js
   │
   ↓
Connection Pool
 ┌─┼──────────┐
 ↓ ↓          ↓
C1 C2 ...    Cn
 │
 ↓
PostgreSQL
```

The pool maintains reusable connections.

Example:

```typescript
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
});
```

Then:

```typescript
const result = await pool.query(
  "SELECT * FROM users WHERE id = $1",
  [userId]
);
```

---

## 9. Why Connection Pooling Becomes Important in Cloud

Suppose:

```text
10 EC2 instances
```

and each creates:

```text
100 DB connections
```

Potentially:

```text
10 × 100 = 1000 connections
```

Your database may not be able to handle that.

Therefore:

> **Application scaling can cause database connection pressure.**

This is a very common system-design problem.

We'll revisit it in later responses.

---

## 10. RDS Storage

RDS needs storage for:

```text
Database data
Indexes
Logs
Temporary data
```

You configure storage depending on the database and workload.

Important concepts include:

- storage capacity
- storage type
- IOPS
- throughput
- autoscaling options

Don't memorize every storage configuration.

Understand:

```text
More workload
     ↓
More I/O
     ↓
Storage performance becomes important
```

---

## 11. IOPS

IOPS = **Input/Output Operations Per Second**.

Imagine a database performing many random reads/writes.

```text
Application
    ↓
Database
    ↓
Storage
    ↓
IO operations
```

If storage cannot handle the workload:

```text
Database latency ↑
```

So database performance isn't just:

```text
CPU
```

It can also be:

```text
CPU
Memory
Storage throughput
IOPS
Connections
Locks
Queries
Indexes
```

---

## 12. RDS Multi-AZ

One of the most important RDS concepts.

Suppose:

```text
AZ-A
 └── Primary DB

AZ-B
 └── Standby
```

Conceptually:

```text
                RDS
                 │
        ┌────────┴────────┐
        ↓                 ↓
     AZ-A              AZ-B
    Primary           Standby
```

The standby is intended for **high availability/failover**, not as your normal read-scaling mechanism.

If the primary fails:

```text
Primary ❌
   ↓
Failover
   ↓
Standby becomes primary
```

Your application continues using the RDS endpoint rather than manually changing the database IP.

---

## 13. Multi-AZ ≠ Read Scaling

This distinction is frequently tested.

#### Multi-AZ

Primary + standby for:

```text
High availability
Failover
```

#### Read Replica

Copies data for:

```text
Read scaling
```

Conceptually:

```text
              Primary
             /       \
            ↓         ↓
        Replica 1   Replica 2
           ↓           ↓
         Reads       Reads
```

---

## 14. Read Replicas

Suppose your application has:

```text
90% reads
10% writes
```

A single database may become read-heavy.

You can use read replicas:

```text
                 Primary
               /    |    \
              ↓     ↓     ↓
             R1     R2     R3
```

Application:

```text
Writes
   ↓
Primary

Reads
   ↓
Replicas
```

This is a common scaling strategy.

---

## 15. But Replicas Introduce a Problem

Replication can have **lag**.

Suppose:

```text
t=1
User updates profile

Primary
name = Rachit
```

Replica may temporarily still have:

```text
name = OldValue
```

So:

```text
Write → Primary
Read immediately → Replica
```

could potentially return stale data.

This is called:

> **Replication lag / eventual consistency behavior**

depending on the architecture.

---

## 16. Read-After-Write Problem

Example:

```text
POST /profile
```

updates:

```text
name = Rachit
```

Then immediately:

```text
GET /profile
```

If the GET goes to a lagging replica:

```text
Old profile ❌
```

Solutions can include:

- route critical immediate reads to primary
- use consistency-aware routing
- tolerate small delays where acceptable
- design the application around consistency requirements

This is an excellent system-design discussion.

---

## 17. Automated Backups

RDS supports automated backup capabilities.

Conceptually:

```text
Database
   ↓
Automated backups
   ↓
Recovery
```

These help with:

- accidental deletion
- corruption
- operational recovery

You should understand the distinction between:

```text
Backup
```

and:

```text
Snapshot
```

---

## 18. RDS Snapshot

A snapshot is a point-in-time copy of an RDS database's storage/data state.

Conceptually:

```text
RDS
 ↓
Snapshot
 ↓
Create new database
```

Useful for:

- migrations
- cloning environments
- backups
- testing
- recovery workflows

---

## 19. Backup vs Snapshot

Think:

```text
Automated backups
→ ongoing recovery capability

Snapshot
→ explicitly created point-in-time copy
```

The exact operational behavior depends on the RDS engine/configuration, but that mental distinction is enough for SWE interviews.

---

## 20. Point-in-Time Recovery

Suppose:

```text
Monday
Database normal

Tuesday 10:00
Database normal

Tuesday 14:37
Bad deployment deletes data ❌
```

With appropriate backup configuration, you can restore to a suitable point before the incident.

Conceptually:

```text
Backups
   ↓
Choose recovery point
   ↓
Restore database
```

This is part of disaster recovery.

---

## 21. RDS Maintenance

Databases need:

```text
Patching
Updates
Maintenance
Configuration changes
```

RDS provides mechanisms to manage these without requiring you to manually manage the underlying server OS like you would with EC2.

But:

> Managed service does **not** mean zero operational responsibility.

You still need to think about:

- maintenance windows
- application compatibility
- migrations
- backups
- performance
- connections
- security
- recovery

---

## 22. Parameter Groups

RDS database engines have configuration parameters.

For example, database behavior can depend on:

```text
memory settings
connection limits
logging
query behavior
```

RDS provides **parameter groups** for managing engine configuration.

Mental model:

```text
RDS
 │
 └── Parameter Group
        ↓
    DB configuration
```

Don't memorize individual parameters yet.

---

## 23. Option Groups

Some RDS engines/features use **option groups** to configure supported additional functionality.

For SWE interviews:

> Know that RDS has engine-specific configuration mechanisms; parameter groups are especially important for database parameters.

No need to spend significant study time memorizing option-group details.

---

## 24. RDS Encryption

Database data can be encrypted at rest.

Conceptually:

```text
Application
     ↓
Encrypted storage
     ↓
RDS
```

AWS Key Management Service (**KMS**) can be involved in encryption key management.

Also:

```text
Application
     ↓ HTTPS/TLS
Database
```

can protect data in transit where supported/configured.

Think:

```text
At rest → encryption
In transit → TLS
```

---

## 25. Secrets Management

Instead of:

```text
DB_PASSWORD=abc123
```

sitting everywhere, use a secrets-management approach.

Architecture:

```text
Application
     ↓
Secrets Manager / secure configuration
     ↓
DB credentials
     ↓
RDS
```

The application retrieves credentials securely according to its permissions.

This is significantly better than hardcoding credentials.

---

## 26. RDS Monitoring

You need to monitor:

```text
CPU
Memory-related metrics
Database connections
Storage
IOPS
Latency
Throughput
```

and application-level metrics such as:

```text
request latency
error rate
query latency
timeouts
```

This gives you:

```text
Application
     ↓
Database
     ↓
Metrics
     ↓
Monitoring
```

We'll go much deeper into CloudWatch and observability in Chapters [17](ch17-monitoring-security.md) and [22](../07-observability-sre/ch22-observability-reliability.md).

---

## 27. Database Doesn't Scale Like EC2

This is important.

For EC2:

```text
Need more capacity?
→ Add instances
```

For databases:

```text
Need more capacity?
```

You need to consider:

```text
Vertical scaling
Read replicas
Caching
Query optimization
Indexes
Partitioning
Sharding
Connection pooling
Database architecture
```

The database is often one of the hardest components to scale.

---

## 28. Vertical Scaling

Suppose:

```text
RDS
4 vCPU
16 GB RAM
```

and workload grows.

You may increase instance capacity:

```text
8 vCPU
32 GB RAM
```

This is vertical scaling.

Advantage:

```text
Simple
```

Limitation:

```text
There is a ceiling.
```

---

## 29. Read Scaling

Instead of making one database increasingly powerful:

```text
               Primary
                  ↑
             Writes
```

add replicas:

```text
                 Primary
                /       \
               ↓         ↓
             Replica   Replica
                ↑         ↑
              Reads     Reads
```

This scales read workloads.

---

## 30. Caching

Suppose the application repeatedly asks:

```sql
SELECT * FROM products WHERE id = 10;
```

Instead of hitting PostgreSQL every time:

```text
Request
  ↓
Redis
  ↓ cache hit
Response
```

If cache miss:

```text
Request
  ↓
Redis
  ↓ miss
PostgreSQL
  ↓
Redis
  ↓
Response
```

You've already seen Redis in Docker.

Later, we'll connect this to AWS and production architecture.

---

## 31. RDS vs DynamoDB

Another common interview question.

#### RDS

Relational:

```text
Tables
Rows
Columns
SQL
Relationships
Transactions
```

Good when:

- relationships matter
- complex SQL queries matter
- relational consistency matters
- schema is relational

#### DynamoDB

NoSQL/key-value/document-oriented database service.

Good for workloads designed around:

```text
key-value access
very high scale
predictable access patterns
low-latency requests
```

Don't think:

> DynamoDB is simply "faster RDS."

They're designed around different data models and access patterns.

---

## 32. RDS vs EC2 vs DynamoDB

| | RDS | DB on EC2 | DynamoDB |
|---|---|---|---|
| Type | Managed relational | Self-managed relational | Managed NoSQL |
| SQL | Yes | Yes | No traditional relational SQL |
| OS management | AWS handles much of it | You manage | AWS handles infrastructure |
| Relationships | Strong fit | Strong fit | Different modeling approach |
| Scaling model | Managed DB scaling + replicas/etc. | You manage | Designed for high-scale NoSQL workloads |
| Operational burden | Lower | Higher | Lower infrastructure burden |

---

## 33. RDS in Your Node.js Architecture

Let's combine everything we've learned.

```text
                         INTERNET
                             │
                             ↓
                        Route 53
                             │
                             ↓
                           ALB
                             │
                  ┌──────────┴──────────┐
                  ↓                     ↓
               EC2-A                 EC2-B
                  │                     │
                  └──────────┬──────────┘
                             ↓
                           RDS
                       PostgreSQL
```

Networking:

```text
ALB SG
  ↓
API SG :3000
  ↓
DB SG :5432
```

Application:

```text
Node.js
   ↓
Connection Pool
   ↓
PostgreSQL
```

Security:

```text
Secrets
   ↓
DB credentials

Encryption
   ↓
Data at rest / transit
```

Availability:

```text
Multi-AZ
```

Scaling:

```text
EC2 → horizontal scaling

RDS → vertical scaling / replicas / optimization
```

---

## 34. What Happens When a User Makes a Request?

Suppose:

```text
GET /users/123
```

Flow:

```text
User
 ↓
DNS
 ↓
ALB
 ↓
EC2
 ↓
Node.js
 ↓
Connection Pool
 ↓
RDS PostgreSQL
 ↓
Query
 ↓
Node.js
 ↓
ALB
 ↓
User
```

That's the full backend path.

---

## 35. What If RDS Is Down?

Your application might show:

```text
500
```

But don't immediately blame Node.js.

Debug systematically:

```text
1. Is RDS available?
2. Is the endpoint correct?
3. Is the DB port correct?
4. Can EC2 reach RDS?
5. Is DB SG allowing EC2 SG?
6. Is the database accepting connections?
7. Is connection pool exhausted?
8. Are credentials correct?
9. Are queries timing out?
10. Is the database overloaded?
```

This is how production debugging works.

---

## 36. Connection Pool Exhaustion

Suppose:

```text
API instances = 20

pool.max = 50
```

Potential theoretical maximum:

```text
20 × 50 = 1000 connections
```

If RDS can only handle a smaller number:

```text
Database
   ↑
Too many connections
   ↓
Failures / timeouts
```

Therefore:

> **Scaling application servers without considering database connection limits can make the system less stable.**

Very important interview concept.

---

## 37. Database Migration

Your application schema changes over time.

For example:

```text
users
```

becomes:

```text
users
 ├── id
 ├── name
 ├── email
 └── created_at
```

You might add:

```text
last_login
```

You should manage this using database migrations rather than manually editing production databases.

Common tools in Node ecosystems include:

```text
Prisma Migrate
Drizzle migrations
TypeORM migrations
Knex migrations
```

For your stack, Prisma is particularly relevant.

---

## 38. Example Prisma Flow

Your code:

```text
schema.prisma
      ↓
Migration
      ↓
PostgreSQL
      ↓
RDS
```

Example conceptual command:

```bash
npx prisma migrate deploy
```

This would typically be part of a controlled deployment process.

Later, your CI/CD response will connect these pieces.

---

## 39. Important Production Rule

Don't blindly run destructive database migrations during deployment.

Bad deployment:

```text
Deploy
 ↓
DROP COLUMN
 ↓
Old application still running
 ↓
💥
```

Production deployments need compatibility thinking.

For example:

```text
Expand
 ↓
Deploy compatible application
 ↓
Migrate data
 ↓
Switch usage
 ↓
Contract/remove old structure later
```

This is commonly called an **expand-and-contract** migration strategy.

Very useful system-design knowledge.

---

## 40. RDS Architecture Checklist

When designing production PostgreSQL on AWS, think:

```text
                    RDS PostgreSQL
                         │
       ┌─────────────────┼─────────────────┐
       ↓                 ↓                 ↓
   Networking         Security          Reliability
       │                 │                 │
 Private subnet      SG :5432          Multi-AZ
       │             Encryption         Backups
       │             Secrets            Recovery
       ↓
 Application
       │
 Connection Pool
       │
       ↓
   PostgreSQL
```

Then scaling:

```text
Vertical scaling
+
Read replicas
+
Caching
+
Query optimization
+
Indexes
+
Connection pooling
```

---

## 41. What You Need to Know Deeply

For your SWE interviews, **master these**:

#### Must know deeply

- RDS concept
- RDS vs EC2 database
- private database architecture
- security groups
- PostgreSQL connectivity
- connection pooling
- Multi-AZ
- read replicas
- replication lag
- backups
- snapshots
- point-in-time recovery concept
- encryption
- Secrets Manager concept
- database scaling
- database connection exhaustion
- migrations
- RDS vs DynamoDB

#### Medium depth

- storage/IOPS
- parameter groups
- monitoring
- maintenance windows
- RDS Proxy concept

#### Awareness

- every supported RDS engine
- obscure engine-specific features
- advanced database administration

You **do not** need to become a PostgreSQL DBA for this roadmap.

---

## 🧪 Practical Lab

Take your Node.js API from the Docker sections.

Current:

```text
Node.js
   ↓
Docker
   ↓
PostgreSQL container
```

Now imagine production:

```text
Node.js
   ↓
EC2
   ↓
RDS PostgreSQL
```

Configure your application around:

```env
DB_HOST=
DB_PORT=5432
DB_NAME=
DB_USER=
DB_PASSWORD=
```

Then verify that your mental architecture is:

```text
Internet
   ↓
ALB
   ↓
EC2 private subnet
   ↓
RDS private subnet
```

and:

```text
EC2 SG → RDS SG :5432
```

not:

```text
Internet → RDS :5432 ❌
```

---

## 🎯 Interview Scenario

#### Question:

> Your Node.js backend has been scaled from 2 EC2 instances to 20. Suddenly PostgreSQL starts rejecting connections. What could have happened?

Your reasoning should be:

```text
2 instances
×
connection pool size
=
manageable connections
```

Then:

```text
20 instances
×
connection pool size
=
much larger connection count
```

Potential result:

```text
RDS connection limit reached
       ↓
Connection failures
       ↓
API errors
```

Possible solutions:

```text
Tune pool sizes
+
Control application concurrency
+
Use RDS Proxy where appropriate
+
Optimize queries
+
Caching
+
Scale database appropriately
```

That's the kind of reasoning interviewers want.

---

## 🧠 Final Mental Model

Remember this:

```text
                    INTERNET
                       │
                       ↓
                      ALB
                       │
              ┌────────┴────────┐
              ↓                 ↓
             EC2               EC2
              │                 │
              └────────┬────────┘
                       ↓
                  Connection
                     Pool
                       ↓
                RDS PostgreSQL
                  │         │
                  │         └── Read Replicas
                  │
                  └── Multi-AZ
```

And around it:

```text
Security Groups
Encryption
Secrets
Backups
Monitoring
Private Subnets
```

#### The key distinction to remember:

```text
Multi-AZ
→ availability / failover

Read Replica
→ read scaling

Connection Pool
→ efficient DB connections

Cache
→ reduce DB traffic

Vertical Scaling
→ more DB resources

Backups
→ recovery

Private Subnet
→ network isolation
```
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 12: VPC + AWS Networking](ch12-vpc-networking.md) · [Chapter 14: Load Balancing + Scaling](ch14-load-balancing-scaling.md) → · [Revision sheet](../../revision/ch13-revision.md)
