# Chapter 16 — Route 53 + CloudFront + CDN + WAF

> **Source:** Response 16 of the original conversation (`source-archive/src-16.txt`, lines 1–1951) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch16-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

Yes — and we're now making the course **hands-on**, as you requested.

This response will teach you not only **what Route 53, CloudFront, CDN, and WAF are**, but also **how they fit into the AWS architecture, how you'd configure them, what traffic actually does, and how you'd deploy/use them.**

---

## 0. Where We Are

Our production architecture is becoming:

```text
                         USER
                           │
                           ↓
                      Route 53
                         DNS
                           │
                           ↓
                       CloudFront
                          CDN
                           │
                           ↓
                         ALB
                           │
                ┌──────────┴──────────┐
                ↓                     ↓
              EC2                   EC2
                │                     │
                └──────────┬──────────┘
                           ↓
                         RDS
```

And we also have:

```text
S3
Lambda
SQS
IAM
VPC
Security Groups
GitHub Actions
Docker
```

Today's job is to understand the **front door of your application**.

---

## PART 1 — DNS AND ROUTE 53

## 1. What Problem Does DNS Solve?

Suppose your EC2 server has:

```text
13.234.56.78
```

You don't want users to remember:

```text
http://13.234.56.78
```

Instead:

```text
api.myapp.com
```

DNS translates:

```text
api.myapp.com
       ↓
13.234.56.78
```

But in production, the destination may not even be a fixed IP.

For example:

```text
api.myapp.com
       ↓
ALB
       ↓
EC2
```

---

## 2. Route 53

**Route 53** is AWS's DNS and domain-routing service.

Think:

```text
Domain
  ↓
Route 53
  ↓
AWS resource
```

For example:

```text
api.example.com
        ↓
Application Load Balancer
```

or:

```text
www.example.com
        ↓
CloudFront
```

---

## 3. Domain Structure

Suppose you own:

```text
example.com
```

You can create:

```text
www.example.com
api.example.com
admin.example.com
cdn.example.com
```

These are DNS records.

---

## 4. Important DNS Records

You should know:

| Record | Purpose |
|---|---|
| A | hostname → IPv4 |
| AAAA | hostname → IPv6 |
| CNAME | hostname → another hostname |
| MX | mail servers |
| TXT | arbitrary verification/text information |
| NS | name servers |

For SWE interviews, focus especially on:

```text
A
AAAA
CNAME
TXT
NS
```

---

## 5. A Record

Example:

```text
api.example.com
       ↓
A record
       ↓
13.234.56.78
```

Meaning:

> Resolve this hostname to this IPv4 address.

---

## 6. CNAME

Example:

```text
www.example.com
       ↓
CNAME
       ↓
some-target.example.com
```

It maps one hostname to another hostname.

---

## 7. DNS Lookup

From Linux:

```bash
dig example.com
```

or:

```bash
nslookup example.com
```

You can inspect:

```text
DNS response
records
TTL
addresses
```

This becomes useful when debugging domains.

---

## 8. TTL

TTL = **Time To Live**.

Suppose:

```text
api.example.com
TTL = 300
```

DNS resolvers can cache the result for roughly:

```text
300 seconds
```

This means DNS changes aren't necessarily visible everywhere instantly.

---

## 9. Why TTL Matters

Suppose:

```text
api.example.com
        ↓
Old ALB
```

You change it to:

```text
api.example.com
        ↓
New ALB
```

If clients/resolvers still have the old DNS result cached:

```text
Old destination
```

may continue being used until the cache expires.

Therefore:

> **DNS changes have propagation/caching considerations.**

---

## 10. Route 53 Hosted Zone

A hosted zone contains DNS information for a domain.

Conceptually:

```text
Route 53
   │
   └── Hosted Zone
         │
         ├── example.com
         ├── www.example.com
         ├── api.example.com
         └── admin.example.com
```

---

## 11. Public vs Private Hosted Zones

#### Public Hosted Zone

Used for:

```text
Internet users
```

Example:

```text
api.example.com
```

#### Private Hosted Zone

Used for DNS names inside your VPC/private environment.

Example:

```text
db.internal
api.internal
```

Conceptually:

```text
VPC
 └── Private DNS
```

---

## PART 2 — CONNECTING ROUTE 53 TO YOUR APP

## 12. Our Application

Suppose:

```text
example.com
```

We have:

```text
Internet
   ↓
ALB
   ↓
EC2
```

We want:

```text
api.example.com
```

to reach the ALB.

Architecture:

```text
User
 ↓
api.example.com
 ↓
Route 53
 ↓
ALB
 ↓
EC2
```

---

## 13. How You Configure It

In AWS:

```text
Route 53
 ↓
Hosted Zones
 ↓
example.com
 ↓
Create Record
```

Then:

```text
Name:
api

Record:
A

Alias:
ALB
```

AWS supports alias records for supported AWS resources.

So you don't need to hardcode the ALB's changing infrastructure details.

---

## 14. Why This Is Better Than EC2 IP

Bad:

```text
api.example.com
       ↓
EC2 public IP
```

If EC2 changes:

```text
Old EC2 ❌
New EC2
```

your DNS target becomes problematic.

Better:

```text
api.example.com
       ↓
ALB
       ↓
EC2 fleet
```

The ALB becomes the stable application entry point.

---

## PART 3 — CDN

## 15. What Is a CDN?

CDN = **Content Delivery Network**.

Suppose your server is in:

```text
Mumbai
```

and a user is in:

```text
New York
```

Without CDN:

```text
New York
   ↓
Mumbai
   ↓
Your server
```

Every request travels to your origin.

---

## 16. CDN Idea

Instead:

```text
                  Origin
                    │
             ┌──────┼──────┐
             ↓      ↓      ↓
           Edge   Edge   Edge
             ↑      ↑      ↑
           Users  Users  Users
```

The CDN caches content closer to users.

---

## 17. CloudFront

**Amazon CloudFront** is AWS's CDN.

Think:

```text
User
 ↓
CloudFront Edge Location
 ↓
Origin
```

The origin could be:

- S3
- ALB
- EC2
- other supported origins

---

## 18. Why Use CloudFront?

Benefits can include:

#### Lower latency

Content can be served closer to users.

#### Caching

Repeated requests may be served from the edge.

#### Reduced origin load

Instead of:

```text
100,000 requests
 ↓
Origin
```

some requests can be served:

```text
100,000 requests
 ↓
CloudFront
 ↓
Origin receives fewer requests
```

#### Security

CloudFront integrates with other AWS security features and TLS.

---

## 19. What Should You Cache?

Good candidates:

```text
Images
CSS
JavaScript
Fonts
Videos
Static files
Public assets
```

Potentially:

```text
API GET responses
```

but only when your caching/consistency requirements make that safe.

---

## 20. What Shouldn't You Blindly Cache?

Be careful with:

```text
POST
PUT
DELETE
```

and personalized/private responses.

For example:

```text
GET /profile
```

might return:

```text
Rachit's profile
```

You don't want another user receiving that cached response.

So caching requires understanding:

```text
Who can see the response?
How long is it valid?
Can it become stale?
```

---

## 21. CloudFront Architecture

For your application:

```text
                    USER
                      │
                      ↓
                  CloudFront
                      │
             ┌────────┴────────┐
             ↓                 ↓
            S3               ALB
             │                 │
          Static            Dynamic
          Assets              API
```

This is a very common architecture.

---

## 22. Frontend + Backend Architecture

Suppose you have:

```text
React / Next.js frontend
Node.js backend
```

A possible architecture:

```text
                         USER
                           │
                           ↓
                      CloudFront
                       /       \
                      ↓         ↓
                    S3         ALB
                 Frontend      API
                                │
                         ┌──────┴──────┐
                         ↓             ↓
                       EC2           EC2
                         │             │
                         └──────┬──────┘
                                ↓
                               RDS
```

Now:

```text
Static content → S3 + CloudFront

API → ALB + EC2

Database → RDS
```

---

## 23. Cache Hit

Suppose:

```text
GET /logo.png
```

First user:

```text
User
 ↓
CloudFront
 ↓
Cache MISS
 ↓
S3
 ↓
CloudFront
 ↓
User
```

CloudFront caches it.

Next user:

```text
User
 ↓
CloudFront
 ↓
CACHE HIT
 ↓
User
```

No request to S3 is needed for that hit.

---

## 24. Cache Miss

If the requested content isn't cached:

```text
User
 ↓
CloudFront
 ↓
MISS
 ↓
Origin
 ↓
Response
 ↓
CloudFront
 ↓
User
```

Depending on cache behavior, CloudFront may cache the response.

---

## 25. Cache-Control

Your application/origin can provide HTTP caching headers such as:

```http
Cache-Control: public, max-age=3600
```

Meaning the response can be cached according to that policy.

For immutable frontend assets:

```text
app.a8f3c1.js
```

you can often use long cache lifetimes because the filename changes when the content changes.

This is a powerful production pattern.

---

## 26. Cache Invalidation

Suppose CloudFront has:

```text
logo.png
```

cached.

You upload a new:

```text
logo.png
```

The edge may still have the old version.

You can invalidate cached objects when necessary.

Conceptually:

```text
CloudFront
 ↓
Invalidate
 ↓
/logo.png
```

But frequent invalidations aren't always the best cache strategy.

A better frontend pattern is often:

```text
app.v1.js
app.v2.js
app.v3.js
```

using content-hashed filenames.

---

## PART 4 — HTTPS

## 27. Why HTTPS?

Without TLS:

```text
HTTP
```

data can potentially be intercepted/modified in transit.

With:

```text
HTTPS
```

TLS protects communication between client and endpoint.

---

## 28. AWS Certificate Manager

AWS provides **Certificate Manager (ACM)** for managing TLS certificates for supported AWS services.

Conceptually:

```text
example.com
     ↓
TLS Certificate
     ↓
CloudFront / ALB
```

For your architecture:

```text
User
 ↓ HTTPS
CloudFront
 ↓ HTTPS
ALB
 ↓
EC2
```

depending on your chosen configuration.

---

## 29. Redirect HTTP → HTTPS

You generally want:

```text
http://example.com
```

to redirect to:

```text
https://example.com
```

For example:

```text
HTTP :80
   ↓
Redirect
   ↓
HTTPS :443
```

This should be part of your production configuration.

---

## PART 5 — WAF

## 30. What Is WAF?

WAF = **Web Application Firewall**.

Think:

> A firewall designed specifically to inspect web/application requests.

Architecture:

```text
User
 ↓
WAF
 ↓
CloudFront / ALB
 ↓
Application
```

---

## 31. Why WAF?

Suppose attackers send:

```text
malicious requests
```

WAF can inspect requests and apply rules.

For example:

```text
Request
 ↓
WAF
 ├── allowed → application
 └── blocked → rejected
```

---

## 32. Common Threat Categories

WAF can help mitigate certain classes of web attacks, including patterns associated with:

- SQL injection
- cross-site scripting
- malicious bots
- abusive request patterns
- unwanted IP addresses
- excessive request rates

It is not a replacement for secure application code.

---

## 33. Rate Limiting

Suppose someone sends:

```text
1,000 requests/sec
```

to:

```text
/login
```

You may want to limit suspicious/request-heavy traffic.

Conceptually:

```text
Client
 ↓
WAF
 ↓
Rate-based rule
 ↓
Too many?
 ↓
BLOCK
```

This can help mitigate some abusive traffic patterns.

---

## 34. AWS Managed Rules

AWS WAF supports managed rule groups.

Instead of writing every security rule yourself:

```text
WAF
 ↓
Managed Rules
 ↓
Common attack patterns
```

For example, managed rules can help detect common web attack patterns.

For your interviews:

> **Managed rules reduce the burden of writing and maintaining every rule manually.**

---

## 35. WAF Placement

Common patterns include:

```text
User
 ↓
CloudFront
 ↓
WAF
 ↓
Origin
```

or:

```text
User
 ↓
ALB
 ↓
WAF
 ↓
EC2
```

AWS WAF can associate with supported AWS resources such as CloudFront and ALB.

---

## 36. CloudFront + WAF

A very common architecture:

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
                EC2               EC2
                 └────────┬────────┘
                          ↓
                         RDS
```

This gives you:

```text
CDN
+
Caching
+
Edge delivery
+
Web security filtering
+
Load balancing
+
Horizontal scaling
+
Database
```

---

## PART 6 — ACTUALLY SETTING THIS UP

Now let's move from concepts to **doing it**.

---

## 37. Step 1 — Buy/Use a Domain

You need a domain such as:

```text
example.com
```

You can register one through Route 53 or another registrar.

If your registrar is external, you can configure its DNS delegation to Route 53.

---

## 38. Step 2 — Create Hosted Zone

In AWS:

```text
Route 53
 ↓
Hosted Zones
 ↓
Create Hosted Zone
```

Enter:

```text
example.com
```

Choose:

```text
Public Hosted Zone
```

Route 53 gives you name servers.

Your registrar needs to delegate the domain to those Route 53 name servers.

---

## 39. Step 3 — Create ALB

From previous responses, you should have:

```text
VPC
├── Public Subnet A
└── Public Subnet B
```

Create:

```text
EC2 instances
```

and:

```text
Target Group
```

Then:

```text
ALB
 ↓
Target Group
 ↓
EC2
```

Listener:

```text
HTTPS :443
```

---

## 40. Step 4 — Configure DNS

Route 53:

```text
example.com
 ↓
Create record
```

For:

```text
api.example.com
```

use an alias to the ALB.

Final:

```text
api.example.com
        ↓
      ALB
        ↓
      EC2
```

Test:

```bash
curl https://api.example.com/health
```

---

## 41. Step 5 — Add CloudFront

Suppose your frontend is stored in S3:

```text
S3
 └── index.html
```

Create:

```text
CloudFront Distribution
```

Origin:

```text
S3 bucket
```

Then:

```text
User
 ↓
CloudFront
 ↓
S3
```

---

## 42. Step 6 — Configure Custom Domain

Instead of:

```text
d123abc.cloudfront.net
```

you want:

```text
www.example.com
```

CloudFront supports alternate domain names and TLS certificates.

Architecture:

```text
www.example.com
       ↓
Route 53
       ↓
CloudFront
       ↓
S3
```

---

## 43. Step 7 — Add WAF

Create:

```text
AWS WAF Web ACL
```

Then associate it with the relevant supported resource.

Example:

```text
CloudFront
    ↑
   WAF
```

or:

```text
ALB
 ↑
WAF
```

Then configure rules.

Start conceptually with:

```text
Managed rules
+
Rate-based protection
```

rather than trying to write hundreds of custom rules.

---

## 44. What the Final System Looks Like

You now have:

```text
                         USER
                           │
                           ↓
                       Route 53
                         DNS
                           │
              ┌────────────┴────────────┐
              ↓                         ↓
         CloudFront                    ALB
              │                         │
             WAF                       WAF
              │                         │
              ↓                         ↓
             S3                      EC2 / EC2
         Frontend                     Backend
                                        │
                                        ↓
                                       RDS
```

There are different valid ways to place WAF and structure the domains; the diagram is showing the concept rather than requiring this exact topology.

---

## 45. Frontend Domain + API Domain

A clean architecture could be:

```text
www.example.com
       ↓
CloudFront
       ↓
S3
```

and:

```text
api.example.com
       ↓
ALB
       ↓
EC2
```

So:

```text
Browser
 ├── www.example.com
 │       ↓
 │   CloudFront → S3
 │
 └── api.example.com
         ↓
        ALB
         ↓
        EC2
         ↓
        RDS
```

This is a very realistic architecture for a web application.

---

## PART 7 — DEVOPS AUTOMATION

Now let's connect this to your earlier concern.

You don't want:

```text
Developer
 ↓
AWS Console
 ↓
Click 50 things
```

Instead:

```text
Developer
 ↓
Git
 ↓
GitHub
 ↓
CI/CD
 ↓
Infrastructure as Code
 ↓
AWS
```

Terraform comes later in [Chapter 21](../06-iac-config/ch21-terraform.md).

---

## 46. What Should CI/CD Deploy?

Your GitHub Actions pipeline might handle:

```text
Code
 ↓
Test
 ↓
Build
 ↓
Docker image
 ↓
Push registry
 ↓
Deploy backend
```

For frontend:

```text
React
 ↓
npm run build
 ↓
dist/
 ↓
S3
 ↓
CloudFront
```

For example:

```yaml
- name: Build frontend
  run: |
    npm ci
    npm run build

- name: Upload to S3
  run: |
    aws s3 sync dist/ s3://my-frontend-bucket
```

Then CloudFront serves the updated files.

---

## 47. Frontend Deployment Pipeline

The actual DevOps flow:

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
S3
   ↓
CloudFront
```

That's a real deployment pipeline.

---

## 48. Backend Deployment Pipeline

Your backend:

```text
Developer
   ↓
GitHub
   ↓
GitHub Actions
   ↓
Test
   ↓
Build
   ↓
Docker image
   ↓
Registry
   ↓
EC2 / ECS / EKS
   ↓
ALB
```

DNS doesn't change during each deployment.

That's another reason to put stable infrastructure such as ALB/CloudFront in front of replaceable application instances.

---

## 49. What Happens During a User Request?

Let's trace the complete system.

User opens:

```text
https://www.example.com
```

Flow:

```text
Browser
 ↓
DNS
 ↓
Route 53
 ↓
CloudFront
 ↓
WAF
 ↓
S3
 ↓
Frontend
```

Then React calls:

```text
https://api.example.com/users
```

Flow:

```text
Browser
 ↓
Route 53
 ↓
ALB
 ↓
WAF
 ↓
EC2
 ↓
Node.js
 ↓
RDS
```

That's the architecture you should be able to draw in an interview.

---

## 50. Debugging DNS

Suppose:

```text
api.example.com
```

doesn't work.

Start with:

```bash
dig api.example.com
```

Check:

```text
Does DNS resolve?
```

If no:

```text
Route 53 record
Hosted zone
Name servers
Registrar delegation
```

If yes:

```text
DNS works
```

Continue:

```bash
curl -v https://api.example.com/health
```

Then investigate:

```text
TLS
ALB
WAF
Security Groups
Target Group
EC2
Application
```

---

## 51. Debugging CloudFront

Suppose:

```text
www.example.com
```

returns old content.

Check:

```text
1. Is DNS pointing to CloudFront?
2. Is CloudFront distribution deployed?
3. Is origin correct?
4. Is object cached?
5. Cache-Control headers?
6. Does origin have new file?
7. Is invalidation needed?
```

---

## 52. Debugging WAF

Suppose legitimate requests get:

```text
403 Forbidden
```

Potential causes:

```text
WAF rule
IP restriction
rate-based rule
managed rule false positive
```

Check:

```text
WAF logs/metrics
```

and determine which rule blocked the request.

Don't simply disable WAF.

---

## 53. Common Interview Question

#### Route 53 vs CloudFront?

Simple answer:

```text
Route 53
→ DNS / domain routing

CloudFront
→ CDN / edge caching / content delivery
```

They solve different problems.

---

## 54. CloudFront vs ALB

#### CloudFront

```text
Global edge delivery
Caching
CDN
```

#### ALB

```text
Application load balancing
Target routing
Health checks
```

Typical architecture:

```text
CloudFront
    ↓
ALB
    ↓
EC2
```

---

## 55. WAF vs Security Group

#### Security Group

Controls network-level access such as:

```text
TCP 443
TCP 3000
TCP 5432
```

#### WAF

Understands web/application requests and can inspect HTTP behavior/rules.

Think:

```text
Security Group
→ Network access

WAF
→ Web/application request filtering
```

They complement each other.

---

## 56. What You Need to Master

#### 🔥 Deep

- DNS fundamentals
- Route 53
- hosted zones
- A/AAAA/CNAME/TXT/NS
- TTL
- Route 53 → ALB
- Route 53 → CloudFront
- CloudFront fundamentals
- CDN caching
- cache hit/miss
- cache-control
- invalidation
- custom domains
- HTTPS/TLS
- ACM concept
- WAF
- WAF vs Security Groups
- rate-based protection
- managed rules
- frontend S3 + CloudFront architecture
- API ALB architecture
- DNS/CloudFront/WAF troubleshooting

#### Medium

- CloudFront behaviors
- origin groups
- signed URLs/cookies
- advanced Route 53 routing policies

#### Awareness

- latency-based routing
- weighted routing
- failover routing
- geolocation/geoproximity routing
- Route 53 health checks

You should understand **what they solve**, but we don't need to spend a huge amount of roadmap time configuring every advanced routing policy.

---

## 🧪 Your Hands-On Challenge

Build/draw this:

```text
                         USER
                           │
                           ↓
                       Route 53
                       /       \
                      /         \
                     ↓           ↓
               CloudFront       ALB
                   │              │
                  WAF            WAF
                   │              │
                   ↓              ↓
                  S3            EC2
              Frontend          Backend
                                  │
                                  ↓
                                 RDS
```

Then make sure you can explain:

#### Frontend request

```text
www.example.com
 ↓
Route 53
 ↓
CloudFront
 ↓
S3
```

#### Backend request

```text
api.example.com
 ↓
Route 53
 ↓
ALB
 ↓
EC2
 ↓
RDS
```

#### Security

```text
WAF
 ↓
HTTP request filtering

Security Group
 ↓
Network access
```

#### Deployment

```text
GitHub
 ↓
GitHub Actions
 ↓
Build/Test
 ↓
S3 / EC2
 ↓
CloudFront / ALB
```

---

## 🚀 What We've Built So Far

Our architecture has now evolved from:

```text
EC2
```

to:

```text
                         INTERNET
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
                                │     │
                                └──┬──┘
                                   ↓
                                  RDS
```

And around the infrastructure:

```text
GitHub
   ↓
GitHub Actions
   ↓
Docker
   ↓
AWS
   ↓
VPC
   ↓
Monitoring ← coming
   ↓
Terraform ← coming
```

**This is the point where the roadmap starts becoming a real DevOps system rather than a collection of definitions.**

<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 15: Lambda + Serverless + Messaging](ch15-lambda-serverless-messaging.md) · [Chapter 17: AWS Monitoring + Security](ch17-monitoring-security.md) → · [Revision sheet](../../revision/ch16-revision.md)
