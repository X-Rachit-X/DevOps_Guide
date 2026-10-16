# Chapter 17 — Revision Sheet: AWS Monitoring + Security

> Supplements [the full chapter](../docs/04-aws/ch17-monitoring-security.md). Questions this chapter answers: *Is it healthy? Is it secure? What broke? Why? Who changed it?* Method: **Understand → Set up → Use → Test → Break → Debug → Automate.**

## Monitoring with CloudWatch

- **Monitoring** = what is happening (CPU 92%, latency 4.2 s, errors 12%, DB CPU 88%). **Observability** = why (Ch.22).
- **CloudWatch** = AWS monitoring/observability platform: **Metrics → numbers · Logs → events/details · Alarms → decisions/actions on metrics** (+ dashboards).
- **Metrics:** numeric time series — EC2/RDS CPU utilization, ALB request count & latency, Lambda invocations/errors. Compare latency vs CPU vs DB CPU vs request count vs network traffic to see whether it correlates with a traffic spike, CPU saturation or DB overload.
- **Logs:** centralise logs from EC2-A/B/C into **CloudWatch Logs** (instead of local files). Organised in **log groups** (collection/category) and **log streams** (sequence from one source, e.g. per instance).
- **CloudWatch agent:** on EC2, sends extra logs and system-level metrics; install/configure it via **Launch Template → User Data** so every new EC2 is monitored automatically (*automate machine configuration so replacement servers are reproducible*).
- **Alarms:** Metric → threshold → Alarm → Action (notify, or trigger supported automation like Auto Scaling policies). Example: EC2 CPU > 80%, period 5 min, notify. **Alarms + Auto Scaling:** metric → CPU > threshold → scaling policy → add EC2.
- **Per-service metrics:** ALB (request count, HTTP errors, target health, latency) · RDS (CPU, connections, storage, IOPS, latency) · Lambda (Invocations, Errors, Duration, Concurrency, Throttles).
- **Dashboards:** one-screen production overview (CPU, request rate, error rate, latency, DB CPU, DB connections).

```bash
aws cloudwatch list-metrics
aws cloudwatch get-metric-statistics ...
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu --metric-name CPUUtilization --namespace AWS/EC2 \
  --statistic Average --period 300 --threshold 80 \
  --comparison-operator GreaterThanThreshold --evaluation-periods 2
# (real use also needs dimensions and alarm actions)
```

## Application logging & metrics

- Don't rely on bare `console.log("something")`; emit **structured JSON**:
```typescript
console.log(JSON.stringify({ level: "info", event: "user_created", userId, timestamp: new Date().toISOString() }));
```
- Log levels: DEBUG (detailed dev info) · INFO (normal important events) · WARN (unusual, not necessarily failure) · ERROR (failure). Example: `logger.info("User created")`, `logger.warn("Slow database query")`, `logger.error("Database connection failed")`.
- **Log:** request ID, user/request context where appropriate, endpoint, status code, latency, error info, service name, timestamp. **Never log:** passwords, access tokens, API keys, credit-card data, sensitive personal data (security + compliance).
- **App-level metrics:** `request_count`, `request_latency`, `error_count`, `active_requests`, `database_latency`. (Observability = metrics + logs + traces, Ch.22.)
- **Health vs readiness:** `/health` (process alive) vs `/ready` (can connect to DB/dependencies). Don't make the check so expensive that it becomes a problem. Liveness/readiness matter heavily in Kubernetes (Ch.18–20).

## Security building blocks

| Topic | Key points |
|---|---|
| **IAM** | Use roles + temporary credentials instead of long-lived keys. Policy example: `s3:GetObject` on `arn:aws:s3:::my-bucket/uploads/*` — never `Action:"*"`, `Resource:"*"` without justification. **Least privilege**: Lambda needing S3 read gets `s3:GetObject` on a specific bucket/path, not `s3:*`. |
| **Roles in the architecture** | EC2 → IAM Role → S3 permissions; Lambda → Execution Role → SQS permissions; CI/CD → role via OIDC. App holds no AWS credentials. |
| **GitHub Actions** | GitHub Actions → OIDC → IAM Role → temporary credentials (rather than permanent access key in GitHub secrets). |
| **Secrets Manager** | Stores/retrieves DB passwords, API keys, OAuth secrets, tokens; app needs IAM permission to read; supports **rotation** (Password A → B) for supported scenarios. Centralised, not scattered in code/servers/images. |
| **KMS** | Managed service for creating/controlling cryptographic keys used by AWS services and apps (S3, RDS encryption, …). |
| **Encryption** | At rest (S3 objects, RDS storage; KMS keys) + in transit (HTTPS/TLS, DB TLS). Want both. |
| **CloudTrail** | Audit trail of AWS API/account activity: who/when/what/resource/source. E.g. who made the S3 bucket public, changed an IAM policy or SG. |
| **Security Groups** | Narrow rules: Internet → ALB SG 443; ALB SG → API SG 3000; API SG → DB SG 5432 = **network segmentation**. |
| **Defense in depth** | CloudFront → WAF → ALB → SG → EC2 → SG → RDS; IAM roles; TLS + at-rest encryption; CloudTrail auditing. |

**CloudWatch vs CloudTrail:** CloudWatch = monitoring ("CPU reached 95%"); CloudTrail = auditing AWS API activity ("someone changed an IAM policy").

## Incident walkthroughs (memorise the pattern)

- **Performance incident:** CloudWatch ALB 5xx ↑ → target health EC2-A/B ❌ → EC2 CPU 98% → app logs "Database timeout" → RDS connections = max ⇒ EC2 → too many DB connections → RDS connection exhaustion → API failures (ties to Ch.13).
- **Security incident:** CloudTrail → find API event → identity, timestamp, action → review IAM → check CloudWatch/app logs for resulting behaviour.
- **Simulations to practise:** high CPU (metric → alarm → investigation → root cause → fix); app can't connect to RDS (app → DNS → route → SG → RDS → credentials → connections).

## AWS security checklist

☑ Least-privilege IAM ☑ IAM roles instead of hard-coded creds ☑ GitHub OIDC ☑ Private databases ☑ Restrictive SGs ☑ WAF where appropriate ☑ HTTPS/TLS ☑ Encryption at rest ☑ Secrets Manager ☑ KMS ☑ CloudTrail enabled/retained ☑ CloudWatch monitoring ☑ Backups ☑ No secrets in Git ☑ No secrets in Docker images ☑ No unnecessary public resources ☑ MFA for human identities.

## Evolution of automation

Console (manual) → AWS CLI/scripts → **Terraform / IaC** (Ch.21) → complete DevOps: Git → GitHub → CI/CD → Terraform → AWS infrastructure → deploy → monitoring → alerts → troubleshooting. **DevOps loop:** code → build → test → deploy → monitor → detect issue → troubleshoot → fix → deploy.

## Depth guide

Master: CloudWatch (metrics/logs/alarms/dashboards), app & centralized logging, EC2/ALB/RDS/Lambda monitoring, IAM least privilege/roles, Secrets Manager, KMS fundamentals, CloudTrail, SGs, WAF, encryption, HTTPS/TLS, incident debugging. Medium: CloudWatch Agent, custom metrics, Log Insights, alarm actions, advanced config. Awareness: AWS Config, GuardDuty, Security Hub, Inspector, Macie.

## Interview answers (from chapter)

1. CloudWatch vs CloudTrail — monitoring/metrics/logs/alarms vs AWS API auditing. 2. Monitor EC2 — CloudWatch + system/app logs + CPU/memory/disk/network + alarms. 3. Detect DB overload — RDS metrics + connections + latency + app logs. 4. 500-error spike — ALB metrics → app logs → dependency metrics → RDS/Redis/external. 5. IAM roles — permissions without embedding long-lived credentials. 6. Least privilege — only the permissions needed. 7. DB passwords — Secrets Manager, not source/Git. 8. KMS — managed cryptographic key management. 9. CloudTrail — records AWS API/account activity. 10. SG vs WAF — network access vs web request filtering.

## Added notes (not in source)

- **EC2 memory and disk-usage metrics are not collected by default** — default EC2 metrics are hypervisor-level (CPU, network, disk I/O, status checks); memory and filesystem usage need the **CloudWatch agent**. Basic monitoring is 5-minute resolution; *detailed monitoring* is 1-minute.
- Alarm states: `OK`, `ALARM`, `INSUFFICIENT_DATA`. The `--period 300 --evaluation-periods 2` example means two consecutive 5-minute periods breaching; `--alarm-actions` (e.g. an SNS topic ARN) is what sends the notification.
- CloudWatch log groups **never expire by default** — set a retention period to control cost.
- CloudTrail: management events are recorded by default and visible in *Event history* for 90 days; create a **trail delivering to S3** for long-term retention (data events such as S3 object reads are opt-in).
- Secrets Manager vs **SSM Parameter Store**: Parameter Store is cheaper/simple configuration + secure strings; Secrets Manager adds built-in rotation and cross-account/resource-policy features.
- KMS keys are **AWS managed** (automatic) or **customer managed** (you control the key policy, rotation, grants); services use *envelope encryption* (a data key encrypts data, KMS protects the data key).

<!-- NAV -->

---

← [Sheet 16](ch16-revision.md) · [Full chapter 17](../docs/04-aws/ch17-monitoring-security.md) · [All revision material](README.md) · [Sheet 18](ch18-revision.md) →
