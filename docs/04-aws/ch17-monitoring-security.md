# Chapter 17 — AWS Monitoring + Security

> **Source:** Response 17 of the original conversation (`source-archive/src-17.txt`, lines 1–1808) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch17-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

We're at the point where your AWS architecture is no longer just **running** — we need to know:

> **Is it healthy? Is it secure? What broke? Why did it break? Who changed it?**

This is what separates "I know AWS services" from actually understanding **production DevOps**.

And as you pointed out earlier, we're going to make this practical:

**Understand → Set up → Use → Test → Break → Debug → Automate.**

---

## 0. Our System So Far

We have:

```text
                         USERS
                           │
                           ↓
                       Route 53
                      /         \
                     ↓           ↓
                CloudFront       ALB
                    │             │
                   WAF           WAF
                    │             │
                    ↓             ↓
                   S3          EC2 / EC2
                                  │
                                  ↓
                                 RDS
```

And:

```text
GitHub
   ↓
GitHub Actions
   ↓
Docker
   ↓
AWS
```

Now we're adding:

```text
                  ┌──────────────┐
                  │  Monitoring  │
                  │ CloudWatch   │
                  └──────┬───────┘
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
        Logs           Metrics         Alarms
```

and:

```text
Security
├── IAM
├── Secrets Manager
├── KMS
├── CloudTrail
├── Security Groups
├── WAF
└── Encryption
```

---

## PART 1 — MONITORING

## 1. Why Do We Need Monitoring?

Imagine users report:

> "The API is very slow."

Without monitoring:

```text
🤷
```

With monitoring:

```text
CPU        92%
Memory     80%
Latency    4.2 sec
Errors     12%
DB CPU     88%
```

Now you have evidence.

Monitoring answers:

> **What is happening?**

Observability goes further and helps answer:

> **Why is it happening?**

We'll cover observability more deeply in [Chapter 22](../07-observability-sre/ch22-observability-reliability.md).

---

## 2. CloudWatch

**Amazon CloudWatch** is AWS's primary monitoring/observability platform.

Think:

```text
AWS resources
     │
     ├── EC2
     ├── ALB
     ├── RDS
     ├── Lambda
     └── other services
             │
             ↓
        CloudWatch
        /    |    \
      Logs Metrics Alarms
```

---

## 3. Three Things You Must Understand

The most important CloudWatch concepts are:

```text
Metrics
Logs
Alarms
```

Think:

```text
Metrics → numbers
Logs    → events/details
Alarms  → decisions/actions based on metrics
```

---

## 4. Metrics

A metric is a numerical measurement over time.

Examples:

```text
EC2 CPU utilization
RDS CPU utilization
ALB request count
ALB latency
Lambda invocations
Lambda errors
```

Example:

```text
CPU:
10%
15%
23%
45%
91%
95%
```

You can visualize it:

```text
CPU %
100 |                 ███
 80 |              █████
 60 |           █████
 40 |        ████
 20 | ███████
    +--------------------
       Time →
```

---

## 5. Why Metrics Matter

Suppose API latency increased.

You can compare:

```text
API latency
CPU
DB CPU
request count
network traffic
```

and determine whether the issue correlates with:

```text
traffic spike
CPU saturation
database overload
```

This is the beginning of production debugging.

---

## 6. CloudWatch Logs

Logs contain detailed events/messages.

Your Node.js application might produce:

```text
Server started on port 3000
Request GET /users
Database connected
Request completed
```

CloudWatch Logs lets you centralize logs from supported AWS resources/applications.

Instead of:

```text
EC2-A → local logs
EC2-B → local logs
EC2-C → local logs
```

you want centralized visibility:

```text
             CloudWatch Logs
             /      |      \
            ↓       ↓       ↓
          EC2-A   EC2-B   EC2-C
```

---

## 7. Node.js Logging

Don't rely on:

```typescript
console.log("something");
```

alone as your entire production logging strategy.

At minimum, make logs structured and useful.

For example:

```typescript
console.log(JSON.stringify({
  level: "info",
  event: "user_created",
  userId,
  timestamp: new Date().toISOString(),
}));
```

Now logs are machine-readable.

A production logging library can take this further.

---

## 8. Log Levels

Common levels:

```text
DEBUG
INFO
WARN
ERROR
```

Example:

```typescript
logger.info("User created");

logger.warn("Slow database query");

logger.error("Database connection failed");
```

Think:

```text
DEBUG → detailed development information
INFO  → normal important events
WARN  → unusual but not necessarily failure
ERROR → failure/problem
```

---

## 9. What Should You Log?

Useful:

```text
request ID
user/request context where appropriate
endpoint
status code
latency
error information
service name
timestamp
```

Avoid logging:

```text
passwords
access tokens
API keys
credit card information
sensitive personal data
```

This is both a security and compliance concern.

---

## 10. Centralized Logs

Imagine three EC2 instances:

```text
EC2-A
EC2-B
EC2-C
```

A request fails.

If logs are only on local disk:

```text
Which server handled it?
```

could become annoying.

Centralized logs let you search across instances.

```text
EC2-A ─┐
EC2-B ─┼──→ CloudWatch Logs
EC2-C ─┘
```

---

## 11. Log Groups and Streams

CloudWatch Logs organizes logs into **log groups** and **log streams**.

Conceptually:

```text
Log Group
│
├── Stream: EC2-A
├── Stream: EC2-B
└── Stream: EC2-C
```

Think:

> Log group = collection/category of logs  
> Log stream = sequence of logs from a particular source/context

---

## 12. CloudWatch Agent

Your EC2 instance can use the CloudWatch agent to send additional system/application information to CloudWatch.

Conceptually:

```text
EC2
 │
 └── CloudWatch Agent
          ↓
      CloudWatch
```

This can provide additional logs and system-level metrics depending on configuration.

---

## 13. Installing an Agent — The DevOps Perspective

You could manually SSH:

```bash
ssh ec2-user@server
```

and install/configure the agent.

But that's not ideal for many servers.

Instead:

```text
Launch Template
      ↓
User Data
      ↓
Install/configure agent
      ↓
Every new EC2 gets monitoring automatically
```

This is an important DevOps principle:

> **Automate machine configuration so replacement servers are reproducible.**

---

## 14. CloudWatch Alarms

Suppose:

```text
CPU > 80%
```

for a sustained period.

You can create:

```text
CloudWatch Alarm
```

Conceptually:

```text
Metric
  ↓
CPU > threshold
  ↓
Alarm
  ↓
Action
```

Possible actions can include notifying or triggering supported automation/scaling mechanisms.

---

## 15. Example Alarm

```text
Metric:
EC2 CPU utilization

Condition:
> 80%

Period:
5 minutes

Action:
Notify
```

Then:

```text
CPU = 90%
     ↓
Alarm
     ↓
Notification
```

Now you don't need a human continuously watching dashboards.

---

## 16. Alarms + Auto Scaling

You already learned Auto Scaling.

Now connect them:

```text
EC2
 ↓
CloudWatch Metric
 ↓
CPU > threshold
 ↓
Auto Scaling policy
 ↓
Add EC2
```

This is where monitoring becomes operational automation.

---

## 17. ALB Monitoring

Your ALB can expose metrics such as:

```text
Request count
HTTP errors
Target health
Latency-related metrics
```

So:

```text
User
 ↓
ALB
 ↓
CloudWatch
```

You can investigate:

```text
Are requests increasing?
Are targets unhealthy?
Are errors increasing?
Is latency increasing?
```

---

## 18. RDS Monitoring

For RDS, monitor things such as:

```text
CPU
Database connections
Storage
IOPS
Latency-related metrics
```

Example:

```text
RDS CPU = 95%
Connections = near limit
```

Possible diagnosis:

```text
Database is becoming overloaded
```

You now have evidence instead of guessing.

---

## 19. Lambda Monitoring

Lambda provides useful metrics such as:

```text
Invocations
Errors
Duration
Concurrency
Throttles
```

Example:

```text
Lambda
 │
 ├── Invocations ↑
 ├── Duration ↑
 ├── Errors ↑
 └── Throttles ↑
```

This can reveal:

```text
Traffic spike
Slow function
Concurrency limit
Downstream bottleneck
```

---

## 20. Dashboards

A CloudWatch dashboard can bring metrics together.

For example:

```text
┌─────────────────────────────────────┐
│          Production Dashboard       │
├───────────────┬─────────────────────┤
│ CPU           │ Request Rate        │
│ 62%           │ 12k/min             │
├───────────────┼─────────────────────┤
│ Error Rate    │ Latency             │
│ 0.4%          │ 180ms               │
├───────────────┼─────────────────────┤
│ DB CPU        │ DB Connections      │
│ 71%           │ 120                  │
└───────────────┴─────────────────────┘
```

This gives you a quick production overview.

---

## PART 2 — SECURITY

Now let's switch to security.

A good production system needs:

```text
Authentication
Authorization
Encryption
Secrets management
Network security
Auditing
Monitoring
```

---

## 21. IAM Recap

You already learned:

```text
IAM
├── Users
├── Groups
├── Roles
└── Policies
```

The most important production principle:

> **Use roles and temporary credentials wherever practical instead of long-lived access keys.**

---

## 22. IAM Policy

Example:

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject"
  ],
  "Resource": "arn:aws:s3:::my-bucket/uploads/*"
}
```

This means the identity can read objects under the specified path.

Not:

```json
{
  "Effect": "Allow",
  "Action": "*",
  "Resource": "*"
}
```

unless there's an exceptional, justified reason.

---

## 23. Least Privilege

Suppose Lambda only needs:

```text
S3 GetObject
```

Give it:

```text
s3:GetObject
```

not:

```text
s3:*
```

And preferably restrict:

```text
specific bucket
specific path
```

Mental model:

```text
Need:
READ files

Give:
READ files

Don't give:
CONTROL entire AWS account
```

---

## 24. IAM Roles in Our Architecture

Example:

```text
EC2
 ↓
IAM Role
 ↓
S3 permissions
```

and:

```text
Lambda
 ↓
IAM Execution Role
 ↓
SQS permissions
```

The application doesn't need to contain AWS credentials.

This is one of the most important security improvements we've made.

---

## 25. GitHub Actions Security

Recall our CI/CD architecture:

```text
GitHub Actions
      ↓
OIDC
      ↓
AWS IAM Role
      ↓
Temporary AWS credentials
```

This is preferable to putting a permanent AWS access key into GitHub secrets when OIDC federation is available.

The important idea:

> **CI gets temporary permissions to perform the deployment.**

---

## 26. Secrets Management

What are secrets?

Examples:

```text
Database passwords
API keys
OAuth client secrets
Private tokens
```

Bad:

```text
GitHub
 ↓
DB_PASSWORD=secret
```

or:

```text
Docker image
 ↓
embedded password
```

or:

```text
source code
 ↓
API key
```

---

## 27. AWS Secrets Manager

AWS provides **Secrets Manager** for storing and retrieving secrets.

Conceptually:

```text
Secrets Manager
       │
       ↓
   DB password
       │
       ↓
Application
```

The application needs IAM permission to retrieve the secret.

---

## 28. Secret Rotation

Secrets should ideally not live forever.

For example:

```text
Password A
   ↓
rotation
   ↓
Password B
```

Secrets Manager supports rotation workflows for supported scenarios.

The key concept:

> **Secret management should be centralized and controlled rather than scattered across source code and servers.**

---

## 29. KMS

KMS = **Key Management Service**.

Think:

> A managed service for creating and controlling cryptographic keys used by AWS services and applications.

Conceptually:

```text
KMS
 ↓
Encryption key
 ↓
Data encryption
```

KMS integrates with many AWS services.

---

## 30. Encryption at Rest

We've already seen this with S3 and RDS.

Examples:

```text
S3
 ↓
Encrypted objects

RDS
 ↓
Encrypted storage
```

KMS can be involved in managing encryption keys.

---

## 31. Encryption in Transit

Example:

```text
Browser
   ↓ HTTPS/TLS
CloudFront / ALB
   ↓
Application
```

And database connections can use TLS where configured/supported.

Remember:

```text
At rest
→ stored data

In transit
→ network communication
```

You generally want both.

---

## 32. CloudTrail

This is different from CloudWatch.

#### CloudWatch

> What is happening to my infrastructure/application?

#### CloudTrail

> What AWS API/account activity happened?

For example:

```text
Someone changed:
Security Group
IAM policy
S3 bucket
EC2 configuration
```

CloudTrail can provide an audit trail of AWS API activity.

---

## 33. CloudTrail Example

Suppose suddenly:

```text
S3 bucket became public
```

You ask:

> Who changed it?

CloudTrail can help identify relevant API activity such as:

```text
Identity
Time
API action
Resource
Source information
```

This is extremely important for security investigations.

---

## 34. CloudWatch vs CloudTrail

Memorize this:

```text
CloudWatch
→ Monitoring

CloudTrail
→ Auditing AWS API activity
```

Example:

```text
CPU reached 95%
→ CloudWatch

Someone changed IAM policy
→ CloudTrail
```

---

## 35. Security Groups

From [Chapter 12](ch12-vpc-networking.md):

```text
ALB SG
 ↓
API SG
 ↓
DB SG
```

Rules should be as narrow as practical.

Example:

```text
Internet
   ↓
ALB SG
   443

ALB SG
   ↓
API SG
   3000

API SG
   ↓
DB SG
   5432
```

This is **network segmentation**.

---

## 36. Network Security Layers

Your application now has multiple security layers:

```text
Internet
   ↓
CloudFront
   ↓
WAF
   ↓
ALB
   ↓
Security Group
   ↓
EC2
   ↓
Security Group
   ↓
RDS
```

And IAM:

```text
EC2
 ↓
IAM Role
 ↓
AWS services
```

And encryption:

```text
TLS
+
KMS/encryption at rest
```

And auditing:

```text
CloudTrail
```

This is defense in depth.

---

## PART 3 — ACTUALLY SETTING UP MONITORING

Now let's make this practical.

---

## 37. AWS CLI — View CloudWatch Metrics

The AWS CLI can interact with CloudWatch.

For example:

```bash
aws cloudwatch list-metrics
```

You can filter metrics by namespace/resource.

You can also query metric statistics with:

```bash
aws cloudwatch get-metric-statistics ...
```

You don't need to memorize every CLI option.

The important DevOps skill is:

> **Know that AWS CLI/API can automate monitoring configuration and inspection.**

---

## 38. Create an Alarm

Conceptually:

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

The exact command also needs appropriate dimensions/actions depending on your setup.

The important idea is:

```text
Metric
 ↓
Threshold
 ↓
Alarm
 ↓
Action
```

---

## 39. Application-Level Metrics

CloudWatch isn't only about AWS infrastructure.

Your application should expose useful metrics such as:

```text
request_count
request_latency
error_count
active_requests
database_latency
```

Conceptually:

```text
Node.js
 ↓
Application metrics
 ↓
Monitoring system
```

Later in [Chapter 22](../07-observability-sre/ch22-observability-reliability.md) we'll build the broader observability model around:

```text
Metrics
Logs
Traces
```

---

## 40. Health Endpoint

Remember our ALB health check:

```text
GET /health
```

We can improve it.

Basic:

```typescript
app.get("/health", (req, res) => {
  res.status(200).json({
    status: "ok",
  });
});
```

But you can also have a deeper readiness check.

For example:

```text
GET /ready
      ↓
Check DB connectivity
      ↓
Check dependencies
      ↓
Return status
```

Be careful not to make health endpoints so expensive that the health check itself becomes a problem.

---

## 41. Liveness vs Readiness

#### Liveness

> Is the application process alive?

```text
Process running?
```

#### Readiness

> Can the application currently serve traffic?

```text
Can connect to required dependencies?
```

This distinction becomes **very important in Kubernetes**.

You'll use it heavily in Chapters [18](../05-kubernetes/ch18-kubernetes-fundamentals.md)–[20](../05-kubernetes/ch20-kubernetes-networking-scaling.md).

---

## 42. Production Incident Example

Imagine:

```text
Users:
"The API is down!"
```

You investigate.

#### Step 1

CloudWatch:

```text
ALB 5xx ↑
```

#### Step 2

Target health:

```text
EC2-A ❌
EC2-B ❌
```

#### Step 3

EC2 metrics:

```text
CPU = 98%
```

#### Step 4

Application logs:

```text
Database timeout
```

#### Step 5

RDS:

```text
Connections = max
```

Now you've discovered:

```text
EC2
 ↓
Too many DB connections
 ↓
RDS connection exhaustion
 ↓
API failures
```

This connects directly to [Chapter 13](ch13-rds-databases.md).

---

## 43. Security Incident Example

Suppose:

```text
Someone changed an IAM policy.
```

Your investigation:

```text
CloudTrail
 ↓
Find API event
 ↓
Identity
 ↓
Timestamp
 ↓
Action
```

Then:

```text
IAM
 ↓
Review permissions
```

And:

```text
CloudWatch / application logs
 ↓
Look for resulting behavior
```

This is how monitoring and security work together.

---

## 44. AWS Security Checklist

For your interviews and projects:

```text
☑ Least privilege IAM
☑ IAM roles instead of hardcoded AWS credentials
☑ GitHub OIDC for CI/CD
☑ Private databases
☑ Restrictive Security Groups
☑ WAF for web-facing applications where appropriate
☑ HTTPS/TLS
☑ Encryption at rest
☑ Secrets Manager for secrets
☑ KMS where appropriate
☑ CloudTrail enabled/retained appropriately
☑ CloudWatch monitoring
☑ Backups
☑ No secrets in Git
☑ No secrets in Docker images
☑ No unnecessary public resources
☑ MFA for human identities where applicable
```

---

## 45. Practical DevOps Setup

For the application we've been building, your target setup should eventually resemble:

```text
                     INTERNET
                         │
                         ↓
                    CloudFront
                         │
                        WAF
                         │
                         ↓
                        ALB
                         │
                ┌────────┴────────┐
                ↓                 ↓
               EC2              EC2
                │                 │
                └────────┬────────┘
                         ↓
                        RDS
```

Monitoring:

```text
EC2 ───────────┐
ALB ───────────┤
RDS ───────────┼──→ CloudWatch
Lambda ────────┤
Application ───┘
```

Security:

```text
IAM
 │
 ├── EC2 Role
 ├── Lambda Role
 └── CI/CD Role

Secrets Manager
 │
 └── DB/API secrets

KMS
 │
 └── encryption keys

CloudTrail
 │
 └── AWS API audit
```

---

## 46. DevOps Automation — The Direction We're Going

Here's the important evolution.

#### Beginner

```text
AWS Console
 ↓
Create EC2
 ↓
Install things manually
```

#### Better

```text
AWS CLI
 ↓
Scripts
```

#### Professional

```text
Terraform
 ↓
Infrastructure as Code
```

#### Complete DevOps

```text
Git
 ↓
GitHub
 ↓
CI/CD
 ↓
Terraform
 ↓
AWS infrastructure
 ↓
Deploy application
 ↓
Monitoring
 ↓
Alerts
 ↓
Troubleshooting
```

**[Chapter 21](../06-iac-config/ch21-terraform.md) will make Terraform the missing piece here.**

---

## 47. What You Need to Know Deeply

#### 🔥 Master

- CloudWatch
- metrics
- logs
- alarms
- dashboards
- application logging
- centralized logging
- EC2 monitoring
- ALB monitoring
- RDS monitoring
- Lambda monitoring
- IAM least privilege
- IAM roles
- Secrets Manager
- KMS fundamentals
- CloudTrail
- security groups
- WAF
- encryption
- HTTPS/TLS
- monitoring + incident debugging

#### Medium

- CloudWatch Agent
- custom metrics
- log insights/querying
- alarm actions
- advanced CloudWatch configuration

#### Awareness

- AWS Config
- GuardDuty
- Security Hub
- Inspector
- Macie

Know **what these services are for**, but don't spend our limited roadmap responses becoming an AWS security specialist.

---

## 48. Interview Questions

You should now be able to answer:

#### Monitoring

**1. CloudWatch vs CloudTrail?**

```text
CloudWatch → monitoring/metrics/logs/alarms
CloudTrail  → AWS API auditing
```

**2. How would you monitor an EC2 server?**

```text
CloudWatch
+
system/application logs
+
CPU/memory/disk/network
+
alarms
```

**3. How would you detect database overload?**

```text
RDS metrics
+
connections
+
latency
+
application logs
```

**4. How would you investigate a 500 error spike?**

```text
ALB metrics
 ↓
application logs
 ↓
dependency metrics
 ↓
RDS/Redis/external services
```

---

#### Security

**5. Why use IAM roles?**

> To provide permissions to AWS resources without embedding long-lived credentials in the application.

**6. What is least privilege?**

> Give an identity only the permissions it actually needs.

**7. Where should database passwords be stored?**

> A proper secrets-management system such as Secrets Manager, not source code or Git.

**8. What does KMS do?**

> Provides managed cryptographic key management used for encryption and related cryptographic operations.

**9. What does CloudTrail do?**

> Records AWS API/account activity for auditing and investigation.

**10. Security Group vs WAF?**

```text
Security Group → network-level access
WAF            → web/application request filtering
```

---

## 🧪 Final Practical Assignment

Take your Node.js API and create this mental/actual production setup:

```text
Node.js
   │
   ├── /health
   ├── /ready
   └── structured logs
```

Then configure:

```text
ALB
 ↓
Health checks
```

```text
EC2
 ↓
CloudWatch monitoring
```

```text
RDS
 ↓
CloudWatch monitoring
```

```text
IAM Role
 ↓
AWS access
```

```text
Secrets Manager
 ↓
Database credentials
```

```text
CloudTrail
 ↓
AWS API auditing
```

Then deliberately simulate:

```text
High CPU
```

and reason:

```text
Metric
 ↓
Alarm
 ↓
Investigation
 ↓
Root cause
 ↓
Fix
```

And simulate:

```text
Application can't connect to RDS
```

and debug:

```text
Application
 ↓
DNS
 ↓
Route
 ↓
Security Group
 ↓
RDS
 ↓
Credentials
 ↓
Connections
```

That's the kind of practical thinking we want you to develop.

---

## 🧠 The Core Mental Model

You should now think of production AWS as:

```text
              ┌────────── SECURITY ──────────┐
              │ IAM │ WAF │ KMS │ Secrets    │
              │     │ SG  │ TLS │ CloudTrail │
              └──────────────┬───────────────┘
                             │
USER → Route53 → CloudFront → ALB
                             │
                         EC2 / Lambda
                             │
                       SQS / Redis
                             │
                            RDS
                             │
                             ↓
                         CloudWatch
                    ┌────────┼────────┐
                    ↓        ↓        ↓
                  Logs     Metrics   Alarms
```

And the DevOps loop is:

```text
                 CODE
                  ↓
                BUILD
                  ↓
                TEST
                  ↓
               DEPLOY
                  ↓
              MONITOR
                  ↓
              DETECT ISSUE
                  ↓
              TROUBLESHOOT
                  ↓
                 FIX
                  ↓
                DEPLOY
```

**That loop is DevOps.**
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 16: Route 53 + CloudFront + CDN + WAF](ch16-route53-cloudfront-waf.md) · [Chapter 18: Kubernetes Fundamentals](../05-kubernetes/ch18-kubernetes-fundamentals.md) → · [Revision sheet](../../revision/ch17-revision.md)
