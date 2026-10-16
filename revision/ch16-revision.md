# Chapter 16 — Revision Sheet: Route 53 + CloudFront + CDN + WAF

> Supplements [the full chapter](../docs/04-aws/ch16-route53-cloudfront-waf.md). Theme: the **front door** of your application.

## DNS & Route 53

- DNS lets users use `api.myapp.com` instead of `13.234.56.78`; in production the target is often an **ALB**, not a fixed IP. **Route 53** = AWS DNS/domain-routing service (`api.example.com → ALB`, `www.example.com → CloudFront`).
- Records: **A** (→ IPv4), **AAAA** (→ IPv6), **CNAME** (→ another hostname), **MX** (mail), **TXT** (verification/arbitrary text), **NS** (name servers). Focus: A, AAAA, CNAME, TXT, NS.
- Debug with `dig example.com` / `nslookup` (response, records, TTL, addresses).
- **TTL** (e.g. 300 s): resolvers may cache for ~that long → DNS changes (old ALB → new ALB) aren't instantly visible everywhere.
- **Hosted zone** = container of DNS records for a domain. **Public** (Internet users, `api.example.com`) vs **Private** (names inside a VPC, `db.internal`, `api.internal`).
- **Route 53 → ALB:** Route 53 → Hosted Zones → `example.com` → Create Record → Name `api`, Type `A`, **Alias → ALB**. Alias records for supported AWS resources mean you don't hard-code the ALB's changing infrastructure details. Pointing at an EC2 IP is fragile; the ALB is the **stable entry point** in front of a replaceable fleet.

## CDN & CloudFront

- **CDN** caches content at edge locations near users (New York user → nearby edge instead of Mumbai origin). **CloudFront** = AWS CDN; origins: S3, ALB, EC2, other supported origins.
- Benefits: lower latency, caching, **reduced origin load**, security/TLS integration.
- **What to cache:** images, CSS, JS, fonts, videos, static files, public assets; maybe API GET responses when safe. **Careful:** POST/PUT/DELETE and personalized/private responses (e.g. `GET /profile` must not leak one user's page to another). Ask: who can see it? how long valid? can it be stale?
- **Cache hit** (served at the edge, no origin request) vs **miss** (CloudFront → origin → cache per behaviour → user).
- **Cache-Control:** `Cache-Control: public, max-age=3600`. Immutable frontend assets with **content-hashed filenames** (`app.a8f3c1.js`) can use long TTLs because the name changes when content changes.
- **Invalidation:** CloudFront can invalidate (`/logo.png`) but frequent invalidation isn't the best strategy; prefer versioned/hashed filenames (`app.v1.js`, `app.v2.js`).
- **Typical architecture:** `USER → CloudFront → {S3: static assets / frontend, ALB: dynamic API → EC2 → RDS}`. Custom domain: `www.example.com → Route 53 → CloudFront → S3` (CloudFront supports alternate domain names + TLS certs).

## HTTPS

- TLS protects client ↔ endpoint. **ACM (AWS Certificate Manager)** manages certificates for supported services (CloudFront/ALB). User →HTTPS→ CloudFront →HTTPS→ ALB → EC2 (depending on configuration).
- Redirect **HTTP :80 → HTTPS :443** as part of production configuration.

## WAF

- **WAF = Web Application Firewall**: inspects HTTP/web requests, applies rules (allow → app, block → rejected). Mitigates classes such as SQL injection, XSS, malicious bots, abusive patterns, unwanted IPs, excessive request rates — **not a replacement for secure application code**.
- **Rate-based rule** (e.g. 1,000 req/s to `/login` → block). **AWS Managed Rules** = prebuilt rule groups for common attack patterns (reduce burden of writing/maintaining rules). Start with managed rules + rate-based protection, not hundreds of custom rules.
- **Placement:** WAF is associated with supported resources — **CloudFront** and **ALB** (diagrams show the concept; several valid topologies).
- **WAF vs Security Group:** SG = network-level access (TCP 443/3000/5432); WAF = understands HTTP requests and rules. They complement each other.

## Full architecture to draw

```text
www.example.com → Route 53 → CloudFront (+WAF) → S3 (frontend)
api.example.com → Route 53 → ALB (+WAF) → EC2 (Node.js) → RDS
```
Browser loads the frontend through CloudFront, then the React app calls `https://api.example.com/users`. DNS does not change during deployments — stable infrastructure (ALB/CloudFront) fronts replaceable instances.

## Hands-on setup (7 steps)

1. Domain (Route 53 or external registrar → delegate to Route 53 name servers). 2. Public hosted zone `example.com` (note NS records). 3. ALB + target group + EC2 across public subnets A/B; HTTPS :443 listener. 4. Route 53 `api` alias → ALB; test `curl https://api.example.com/health`. 5. CloudFront distribution with S3 origin. 6. Custom domain (`www.example.com`) + certificate. 7. WAF Web ACL associated with CloudFront/ALB (managed rules + rate-based).

## Deployment pipelines

```yaml
- name: Build frontend
  run: |
    npm ci
    npm run build
- name: Upload to S3
  run: aws s3 sync dist/ s3://my-frontend-bucket
```
Frontend: push → Actions → `npm ci` → `npm test` → `npm run build` → S3 → CloudFront. Backend: Actions → test → build → Docker image → registry → EC2/ECS/EKS → ALB. Prefer Infrastructure as Code (Terraform, Ch.21) over clicking in the console.

## Troubleshooting

- **DNS:** `dig api.example.com` — resolves? If not: Route 53 record, hosted zone, name servers, registrar delegation. If yes: `curl -v https://api.example.com/health` → TLS → ALB → WAF → SGs → target group → EC2 → app.
- **CloudFront serves old content:** DNS pointing to CloudFront? distribution deployed? origin correct? object cached? Cache-Control headers? origin has the new file? invalidation needed?
- **WAF 403 for legitimate requests:** WAF rule, IP restriction, rate-based rule, managed-rule false positive → check WAF logs/metrics to find the rule. Don't just disable WAF.

## Comparisons

| | Route 53 | CloudFront | ALB | WAF | Security Group |
|---|---|---|---|---|---|
| Role | DNS/domain routing | CDN/edge caching | Load balancing, target routing, health checks | HTTP request filtering | Network access |

## Depth guide

Deep: DNS, Route 53, hosted zones, A/AAAA/CNAME/TXT/NS, TTL, Route 53 → ALB/CloudFront, CDN caching, hit/miss, cache-control, invalidation, custom domains, HTTPS/ACM, WAF + vs SG, rate-based, managed rules, S3+CloudFront, ALB API, troubleshooting. Medium: CloudFront behaviours, origin groups, signed URLs/cookies, advanced routing policies. Awareness: latency-based, weighted, failover, geolocation/geoproximity routing, Route 53 health checks.

## Added notes (not in source)

- **Alias vs CNAME:** a CNAME cannot exist at the **zone apex** (`example.com`); Route 53 **alias** records can point the apex at an ALB/CloudFront/S3 website and are free for AWS targets (no TTL to set).
- For CloudFront, the **ACM certificate must be in `us-east-1`**, and WAF web ACLs for CloudFront are in the **global/us-east-1** scope; for an ALB, ACM and WAF live in the ALB's Region.
- Keep the S3 origin **private** and use **Origin Access Control (OAC)** so only CloudFront can read the bucket.
- After `aws s3 sync dist/ s3://bucket --delete`, run `aws cloudfront create-invalidation --paths "/index.html"` (or version assets); `index.html` itself is the file that usually must not be cached long.
- Redirect HTTP→HTTPS at the ALB listener (80 → 443 redirect action) or via CloudFront's *viewer protocol policy*.
- Frontend (`www`) and API (`api`) are different origins → configure **CORS** on the API.
- Route 53 routing policies beyond simple: weighted, latency, failover, geolocation, geoproximity, multivalue.

<!-- NAV -->

---

← [Sheet 15](ch15-revision.md) · [Full chapter 16](../docs/04-aws/ch16-route53-cloudfront-waf.md) · [All revision material](README.md) · [Sheet 17](ch17-revision.md) →
