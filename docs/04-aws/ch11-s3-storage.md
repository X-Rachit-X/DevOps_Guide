# Chapter 11 — S3 + AWS Storage

> **Source:** Response 11 of the original conversation (`source-archive/src-11.txt`, lines 52–1565) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch11-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

S3 is one of the most important AWS services to understand because almost every backend engineer eventually encounters object storage.

We'll connect it directly to your Node.js backend.

---

## 1. What Is S3?

**Amazon S3 — Simple Storage Service** is an object storage service.

It is designed to store and retrieve objects such as:

```text
Images
Videos
PDFs
Documents
Backups
Logs
Static assets
Data files
```

Think:

```text
Node.js API
      ↓
     S3
      ↓
 ┌─────────────┐
 │ image.jpg   │
 │ resume.pdf  │
 │ report.csv  │
 │ video.mp4   │
 └─────────────┘
```

---

## 2. Why Not Store Files on EC2?

You might think:

```text
EC2
 ↓
/uploads
 ↓
image.jpg
```

This works for a small experiment.

But imagine:

```text
EC2 A
EC2 B
EC2 C
```

If users upload files to EC2 A:

```text
User
 ↓
EC2 A
 ↓
/uploads
```

EC2 B doesn't automatically have those files.

Now scaling becomes difficult.

Instead:

```text
                 S3
              /  |  \
             /   |   \
           EC2  EC2  EC2
```

All application instances can access the same object storage.

---

## 3. Object Storage vs Block Storage

You've already learned EBS.

#### EBS

Block storage:

```text
EC2
 ↓
Disk
 ↓
Blocks
```

Used like a disk/filesystem.

#### S3

Object storage:

```text
S3
 ↓
Objects
```

Used through APIs.

Think:

```text
EBS → virtual hard drive

S3 → highly scalable object storage
```

This distinction is extremely important.

---

## 4. S3 Bucket

An S3 **bucket** is a container for objects.

Conceptually:

```text
S3
 │
 └── Bucket
      │
      ├── image.jpg
      ├── report.pdf
      └── video.mp4
```

Example bucket:

```text
my-company-assets
```

---

## 5. Object

An S3 object consists conceptually of:

```text
Object
├── Data
├── Key
└── Metadata
```

For example:

```text
Key:
users/123/profile.jpg

Data:
<image bytes>
```

The key identifies the object's location/name within the bucket's namespace.

---

## 6. Bucket + Key

Suppose:

```text
Bucket:
my-app-files
```

Object key:

```text
users/123/profile.jpg
```

Conceptually:

```text
S3
└── my-app-files
    └── users/123/profile.jpg
```

Important:

> S3 doesn't work like a traditional hierarchical filesystem even though keys can contain `/` and therefore look like directories.

For example:

```text
users/123/profile.jpg
```

is fundamentally an **object key**.

---

## 7. S3 Is Not a Normal Filesystem

This is an interview-worthy distinction.

Traditional filesystem:

```text
/var/uploads/user123/photo.jpg
```

S3:

```text
Bucket:
my-files

Key:
users/user123/photo.jpg
```

Your application interacts with S3 through APIs rather than treating the bucket as an ordinary mounted disk in the usual architecture.

---

## 8. S3 Operations

The basic operations are:

```text
PUT
GET
DELETE
LIST
```

Conceptually:

```text
PUT
 ↓
Upload object

GET
 ↓
Download object

DELETE
 ↓
Remove object

LIST
 ↓
List objects
```

---

## 9. AWS CLI + S3

You can interact with S3 through the AWS CLI.

List buckets:

```bash
aws s3 ls
```

Copy a file:

```bash
aws s3 cp report.pdf s3://my-bucket/
```

Download:

```bash
aws s3 cp s3://my-bucket/report.pdf .
```

List bucket contents:

```bash
aws s3 ls s3://my-bucket/
```

These are useful commands to know.

---

## 10. S3 Durability vs Availability

Don't confuse these.

#### Durability

> How unlikely is it that stored data is lost?

#### Availability

> How often is the service/data accessible?

AWS S3 is designed for extremely high durability, while availability depends on the service/storage configuration.

Interview distinction:

```text
Durability
   ↓
Data preservation

Availability
   ↓
Ability to access it
```

---

## 11. S3 Storage Classes

Not every object has the same access pattern.

For example:

```text
Profile pictures
→ accessed frequently

Old backups
→ rarely accessed
```

S3 offers different storage classes optimized for different patterns.

Broadly, you'll encounter classes for:

```text
Frequent access
Infrequent access
Archive
```

Examples include:

```text
S3 Standard
S3 Standard-IA
S3 Glacier classes
```

You don't need to memorize every pricing number.

Understand the tradeoff:

```text
More frequent access
        ↓
Higher access/storage economics

Rarely accessed
        ↓
Archive-oriented storage
```

---

## 12. S3 Lifecycle Policies

Suppose:

```text
Day 0
backup created
```

After a while:

```text
90 days
rarely accessed
```

Instead of manually moving it, lifecycle rules can transition objects between storage classes or expire them.

Conceptually:

```text
New object
    ↓
Standard
    ↓
After X days
    ↓
Infrequent access
    ↓
After Y days
    ↓
Archive
```

This is useful for:

- backups
- logs
- historical reports
- compliance data

---

## 13. S3 Versioning

Suppose:

```text
report.pdf
```

gets overwritten accidentally.

With versioning enabled, S3 can retain multiple versions.

Conceptually:

```text
report.pdf
   │
   ├── Version 1
   ├── Version 2
   └── Version 3
```

This can help with:

- accidental overwrites
- recovery
- data protection

But versioning isn't a replacement for every kind of backup strategy.

---

## 14. S3 Encryption

You should understand encryption at rest.

S3 supports encryption mechanisms including:

```text
SSE-S3
SSE-KMS
```

The high-level distinction:

#### SSE-S3

AWS manages the encryption keys for the S3-managed encryption mechanism.

#### SSE-KMS

Uses AWS Key Management Service (KMS), providing additional key-management and access-control capabilities.

Conceptually:

```text
Object
 ↓
Encryption
 ↓
Stored in S3
```

For sensitive systems, understanding who can use/decrypt the data and how key access is controlled is important.

---

## 15. Encryption in Transit

Encryption at rest isn't enough.

When transferring data:

```text
Client
 ↓
HTTPS
 ↓
S3
```

you want TLS encryption in transit.

So:

```text
At rest
→ encryption

In transit
→ HTTPS/TLS
```

These solve different problems.

---

## 16. IAM + S3

Now connect [Chapter 9](ch09-aws-fundamentals-iam.md).

Suppose:

```text
Node.js API
       ↓
       S3
```

The API needs permission.

IAM policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-app-files/*"
    }
  ]
}
```

Conceptually:

```text
Node API
   ↓
IAM Role
   ↓
s3:GetObject
s3:PutObject
   ↓
my-app-files/*
```

This is much better than giving:

```text
AdministratorAccess
```

---

## 17. IAM Policy vs Bucket Policy

This is an important AWS interview topic.

#### IAM policy

Permissions attached to an identity such as:

```text
User
Role
Group
```

Example:

```text
API role
 ↓
Can read S3
```

#### Bucket policy

A resource-based policy attached to an S3 bucket.

Conceptually:

```text
Bucket
 ↓
Bucket Policy
 ↓
Defines who can access it
```

Both can participate in determining whether an S3 request is allowed.

---

## 18. Public vs Private Buckets

A common beginner mistake:

> "I'll just make my S3 bucket public."

Don't do this unless public access is actually required.

For private user data:

```text
Bucket
 ↓
Private
```

Your backend controls access.

```text
User
 ↓
API
 ↓
Authorization
 ↓
S3
```

This is generally much safer for private application data.

---

## 19. Block Public Access

S3 provides **Block Public Access** controls.

For private application storage, you generally want public access blocked unless you have a deliberate public-content architecture.

For example:

```text
Private bucket
      ↓
Backend / controlled access
```

rather than:

```text
Internet
   ↓
Anyone
   ↓
S3 bucket
```

---

## 20. Presigned URLs

Now we reach one of the most useful S3 concepts for backend developers.

Suppose users need to upload a 100 MB video.

Bad architecture:

```text
User
 ↓
Node.js API
 ↓
S3
```

The backend becomes a middleman for the entire file.

Instead:

```text
User
 ↓
Node.js API
 ↓
Generate presigned URL
 ↓
User
 ↓
S3
```

The large file goes directly to S3.

---

## 21. Presigned Upload Flow

Suppose:

```text
POST /uploads
```

User requests an upload.

Backend:

```text
Authenticate user
      ↓
Authorize operation
      ↓
Generate presigned URL
      ↓
Return URL
```

Client:

```text
Client
  ↓
PUT file
  ↓
Presigned S3 URL
  ↓
S3
```

The backend doesn't have to stream the entire file.

---

## 22. Why Presigned URLs Are Powerful

They provide:

```text
Less backend bandwidth
Less backend CPU/memory usage
Direct client → S3 transfer
Temporary controlled access
```

You can configure constraints such as:

```text
expiration
object key
allowed operation
```

The exact policy depends on the mechanism used to generate the URL.

---

## 23. Node.js Example — S3 Client

Using AWS SDK v3:

```typescript
import { S3Client } from "@aws-sdk/client-s3";

const s3 = new S3Client({
  region: process.env.AWS_REGION
});
```

Then you can use S3 commands.

For example:

```typescript
import {
  PutObjectCommand
} from "@aws-sdk/client-s3";

await s3.send(
  new PutObjectCommand({
    Bucket: "my-app-files",
    Key: "users/123/profile.jpg",
    Body: fileBuffer,
    ContentType: "image/jpeg"
  })
);
```

For large uploads, direct/presigned uploads are often a better architecture than sending the entire object through your API.

---

## 24. Generating a Presigned URL

Conceptually:

```typescript
import { PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const command = new PutObjectCommand({
  Bucket: "my-app-files",
  Key: "users/123/photo.jpg",
  ContentType: "image/jpeg"
});

const url = await getSignedUrl(s3, command, {
  expiresIn: 300
});
```

Then return:

```json
{
  "uploadUrl": "..."
}
```

The frontend can upload directly.

---

## 25. Important Security Detail

Don't let the client arbitrarily decide:

```text
bucket = "anything"
key = "anything"
```

Your backend should control:

```text
Who?
What object?
Where?
What operation?
How long?
```

For example:

```text
Authenticated user
      ↓
Backend validates ownership
      ↓
Generate limited URL
      ↓
Short expiration
```

---

## 26. Multipart Upload

What if the file is huge?

Instead of:

```text
10 GB file
 ↓
One upload
```

you can split it:

```text
10 GB
 ↓
Part 1
Part 2
Part 3
...
Part N
```

and upload parts separately.

Benefits include:

- better reliability
- parallel uploads
- retrying failed parts
- handling large objects efficiently

This is called **multipart upload**.

You don't need to implement the full protocol from memory, but you should understand why it exists.

---

## 27. S3 Static Website Hosting — Know the Concept

S3 can be used for static content hosting in appropriate configurations.

For example:

```text
HTML
CSS
JS
Images
```

But for a modern production architecture, you often combine object storage with:

```text
CloudFront
```

for CDN delivery.

We'll cover that in [Chapter 16](ch16-route53-cloudfront-waf.md).

---

## 28. S3 + CloudFront

Instead of:

```text
User
 ↓
S3
```

you can have:

```text
User
 ↓
CloudFront
 ↓
S3
```

CloudFront caches content closer to users.

Example:

```text
User in Chennai
       ↓
CloudFront edge
       ↓
Cached image
```

instead of repeatedly fetching the object from the origin.

---

## 29. S3 as Backend File Storage

A very common architecture:

```text
                  User
                    │
                    ↓
                Node.js API
                    │
          ┌─────────┴─────────┐
          ↓                   ↓
       PostgreSQL             S3
       metadata              files
```

Important:

> **Database and object storage solve different problems.**

You might store:

#### PostgreSQL

```text
user_id
file_id
file_name
content_type
s3_key
created_at
```

#### S3

```text
actual file bytes
```

This separation is extremely common.

---

## 30. Why Not Store Images Directly in PostgreSQL?

You technically can store binary data in databases.

But object storage is often better suited for large files because:

```text
Database
→ relational/queryable data

S3
→ large objects/files
```

Your database can store the metadata and reference:

```text
s3_key
```

---

## 31. S3 Event Notifications

S3 can generate events when objects change.

Conceptually:

```text
File uploaded
     ↓
S3 event
     ↓
Lambda / SQS / other target
```

Example:

```text
User uploads image
        ↓
S3
        ↓
Event
        ↓
Processing service
        ↓
Resize/compress image
```

We'll connect this with Lambda and messaging in [Chapter 15](ch15-lambda-serverless-messaging.md).

---

## 32. S3 and Backups

S3 is commonly used for:

```text
Database backups
Application backups
Logs
Data exports
Artifacts
```

For example:

```text
RDS
 ↓
Backup/export
 ↓
S3
```

This is a common cloud architecture pattern.

---

## 33. S3 Object Naming

Don't use unpredictable or poorly structured keys.

For example:

```text
users/123/profile.jpg
users/123/documents/resume.pdf
orders/456/invoice.pdf
```

This gives you logical organization.

But remember:

```text
users/123/profile.jpg
```

is still an object key, not necessarily a physical directory.

---

## 34. S3 Access Pattern

A good backend flow:

```text
User
 ↓
POST /files/upload-url
 ↓
Backend authenticates
 ↓
Backend authorizes
 ↓
Backend generates presigned URL
 ↓
Client uploads to S3
 ↓
S3
 ↓
Backend stores metadata
```

For example:

```text
PostgreSQL
──────────────
file_id: 42
user_id: 123
s3_key: users/123/file-42.pdf
```

S3:

```text
users/123/file-42.pdf
       ↓
actual PDF bytes
```

This is a strong project/interview architecture to understand.

---

## 35. S3 Security Architecture

A private file-storage setup:

```text
                    User
                      │
                      ↓
                 Node.js API
                      │
                IAM Role
                      │
                      ↓
                 Private S3
                      │
                  Encryption
```

For uploads:

```text
User
 ↓
API
 ↓
Authorization
 ↓
Presigned URL
 ↓
S3
```

For downloads:

```text
User
 ↓
API
 ↓
Authorization
 ↓
Presigned GET URL
 ↓
S3
```

This gives you controlled, temporary access.

---

## 36. S3 vs EBS vs EFS

You should know the distinction.

| Service | Type | Typical use |
|---|---|---|
| **S3** | Object storage | Files, images, backups |
| **EBS** | Block storage | EC2 disks |
| **EFS** | Shared file storage | Shared filesystem across compute |

Mental model:

```text
S3
→ objects

EBS
→ disk

EFS
→ shared filesystem
```

You don't need deep EFS knowledge for this roadmap, but know where it fits.

---

## 37. S3 Interview Scenario

#### Question:

> Your Node.js application runs on three EC2 instances. Users upload profile pictures. Where would you store them?

Reason through it:

```text
Three EC2 instances
        ↓
Local disk?
        ↓
❌ difficult to share
        ↓
S3
        ↓
Central object storage
```

Then:

```text
Database
 ↓
Store metadata + S3 key
```

For upload:

```text
Presigned URL
```

For private retrieval:

```text
Authorized API
 ↓
Presigned GET URL
```

That's a strong backend design.

---

## 38. Another Interview Scenario

> A user uploads a 500 MB video. Should your Node.js API receive the entire file and then upload it to S3?

Not necessarily.

A better architecture for many applications:

```text
Client
   ↓
API
   ↓
Presigned multipart upload
   ↓
S3
```

The backend handles:

```text
Authentication
Authorization
Upload initialization
Metadata
```

while S3 handles the large object transfer.

---

## 39. S3 Cost/Performance Thinking

When designing S3 storage, consider:

```text
Storage cost
Request cost
Data transfer
Access frequency
Object size
Lifecycle
Caching
```

For example:

```text
Frequently accessed images
        ↓
S3 + CloudFront

Old backups
        ↓
Lifecycle + archive storage
```

This is the kind of tradeoff interviewers like to see.

---

## 40. What You Need to Know for SWE Interviews

You should now be comfortable explaining:

```text
S3
Bucket
Object
Key
Storage classes
Lifecycle
Versioning
Encryption
IAM access
Bucket policies
Private buckets
Presigned URLs
Multipart uploads
S3 + CloudFront
S3 vs EBS
S3 vs database
S3 event notifications
```

You **do not** need to memorize every S3 feature or pricing number.

---

## 🧪 Practical Project

Extend your TypeScript backend.

Build:

```text
POST /files/upload-url
GET  /files/:id
DELETE /files/:id
```

Architecture:

```text
             Client
                │
                ↓
           Node.js API
                │
        ┌───────┴────────┐
        ↓                ↓
    PostgreSQL           S3
     metadata          file data
```

#### Upload

```text
Client
 ↓
POST /files/upload-url
 ↓
API authenticates
 ↓
API generates presigned URL
 ↓
Client → S3
 ↓
API stores metadata
```

#### Download

```text
Client
 ↓
GET /files/42
 ↓
API checks authorization
 ↓
Generate presigned GET URL
 ↓
Client → S3
```

This single project teaches you a **very realistic backend/cloud architecture**.

---

## 🎯 Interview Questions

Make sure you can answer:

1. What is S3?
2. What is a bucket?
3. What is an object?
4. What is an S3 key?
5. Is S3 a filesystem?
6. S3 vs EBS?
7. S3 vs EFS?
8. Why use S3 instead of EC2 local storage?
9. What is S3 versioning?
10. What are lifecycle policies?
11. What are S3 storage classes?
12. What is encryption at rest?
13. SSE-S3 vs SSE-KMS at a high level?
14. What is a bucket policy?
15. IAM policy vs bucket policy?
16. Why should private application buckets generally not be public?
17. What is a presigned URL?
18. Why use presigned URLs?
19. What is multipart upload?
20. How would you upload a 1 GB file efficiently?
21. How would your Node.js application securely access S3?
22. Why shouldn't AWS credentials be hardcoded?
23. How would you store uploaded files for a multi-instance backend?
24. Why store file metadata in PostgreSQL but file contents in S3?
25. How can CloudFront improve S3-based content delivery?

---

## 🔥 The AWS Architecture Is Taking Shape

We now have:

```text
                         AWS
                          │
                        VPC
                          │
                    ┌─────┴─────┐
                    ↓           ↓
                   EC2         S3
                    │        Files/Assets
                  Docker
                    │
                Node.js API
                    │
                    ↓
                   IAM
```

Soon we'll add:

```text
                 Internet
                    ↓
                   ALB
                    ↓
              EC2 / Containers
                 /       \
                ↓         ↓
              RDS        S3
                │
             PostgreSQL
```

Then:

```text
CloudFront
Route 53
WAF
Lambda
SQS/SNS
CloudWatch
```

So yes — **we are covering the majority of AWS that you realistically need for your SWE/backend + Cloud/DevOps preparation**, rather than attempting to learn AWS's entire service catalog.
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 10: EC2 + AWS Compute](ch10-ec2-compute.md) · [Chapter 12: VPC + AWS Networking](ch12-vpc-networking.md) → · [Revision sheet](../../revision/ch11-revision.md)
