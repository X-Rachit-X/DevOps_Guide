# Chapter 11 — Revision Sheet: S3 + AWS Storage

> Supplements [the full chapter](../docs/04-aws/ch11-s3-storage.md).

## Core model

- **S3 (Simple Storage Service)** = object storage. Stores images, videos, PDFs, documents, backups, logs, static assets, data files; accessed through **APIs** (PUT / GET / DELETE / LIST), not as a mounted disk.
- **Bucket** = container for objects (e.g. `my-company-assets`). **Object** = data + key + metadata. **Key** = the object's name within the bucket namespace, e.g. `users/123/profile.jpg`.
- **S3 is not a hierarchical filesystem** — `/` in keys only *looks* like directories.
- Why not store uploads on EC2 disk? With EC2 A/B/C, a file uploaded to A isn't on B → scaling breaks. S3 gives all instances one shared store.

| Service | Type | Use |
|---|---|---|
| **S3** | Object | Files, images, backups |
| **EBS** | Block | EC2 disks ("virtual hard drive") |
| **EFS** | Shared file storage | Shared filesystem across compute |

## CLI

`aws s3 ls` · `aws s3 cp report.pdf s3://my-bucket/` · `aws s3 cp s3://my-bucket/report.pdf .` · `aws s3 ls s3://my-bucket/`

## Durability vs availability

**Durability** = how unlikely data is lost (S3 designed for extremely high durability). **Availability** = how often the data/service is accessible (depends on service/storage configuration).

## Cost / data-management features

| Feature | Idea |
|---|---|
| **Storage classes** | Frequent access (S3 Standard) / infrequent access (Standard-IA) / archive (Glacier classes). Trade-off: rarely accessed → archive-oriented storage |
| **Lifecycle policies** | Auto-transition (Standard → IA after X days → archive after Y days) or expire; for backups, logs, historical reports, compliance data |
| **Versioning** | Keep multiple versions of a key (recover accidental overwrites); not a replacement for every backup strategy |
| **Event notifications** | Upload → S3 event → Lambda / SQS / other (e.g. resize images) |

Cost thinking: storage cost, request cost, data transfer, access frequency, object size, lifecycle, caching. Frequent images → S3 + CloudFront; old backups → lifecycle + archive.

## Security

- **Encryption at rest:** **SSE-S3** (AWS-managed keys) vs **SSE-KMS** (AWS KMS: extra key management + access control). **In transit:** HTTPS/TLS. They solve different problems.
- **IAM policy** (identity-based: user/role/group) vs **bucket policy** (resource-based, attached to the bucket). Both can participate in an S3 authorization decision.
- Example identity policy: `Allow s3:GetObject, s3:PutObject` on `arn:aws:s3:::my-app-files/*` for the API role (not `AdministratorAccess`).
- **Don't make buckets public** for private data; the backend authorizes then S3 serves. Use **Block Public Access** unless you deliberately host public content.

## Presigned URLs (very important)

Problem: 100 MB upload through Node.js makes the API a middleman. Solution: **API generates presigned URL → client uploads directly to S3.**

```typescript
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const s3 = new S3Client({ region: process.env.AWS_REGION });   // no hard-coded keys

const command = new PutObjectCommand({
  Bucket: "my-app-files",
  Key: "users/123/photo.jpg",
  ContentType: "image/jpeg",
});
const url = await getSignedUrl(s3, command, { expiresIn: 300 });  // → { "uploadUrl": url }
```

Flow: `POST /files/upload-url` → authenticate → authorize → generate presigned URL → return → client `PUT`s file to S3 → API stores metadata.
Benefits: less backend bandwidth/CPU/memory, direct client→S3 transfer, temporary controlled access (expiration, key, operation).
**Security detail:** the backend — not the client — decides bucket, key, operation, expiry (validate ownership; short expiry). Download the same way with a presigned **GET** URL after authorization.

## Multipart upload

Split a huge file (e.g. 10 GB) into parts → better reliability, parallel uploads, retry failed parts only. For a 500 MB video prefer *presigned multipart upload*: backend handles authentication, authorization, upload initialization, metadata; S3 handles the transfer.

## Architecture patterns

- **Files in S3, metadata in PostgreSQL** (`file_id, user_id, file_name, content_type, s3_key, created_at`). Database = relational/queryable data; S3 = large objects.
- **S3 + CloudFront** (edge caching, e.g. user in Chennai served from an edge) — details in Ch.16. S3 static website hosting is possible but usually fronted by CloudFront.
- **Backups/logs/artifacts/exports** commonly land in S3 (e.g. RDS backup/export).
- **Key naming:** `users/123/profile.jpg`, `users/123/documents/resume.pdf`, `orders/456/invoice.pdf` — logical organization, still just keys.

## Scenarios

1. *3 EC2 instances, profile pictures — where?* S3 (shared) + DB stores metadata/S3 key + presigned PUT for upload + authorized API → presigned GET for private retrieval.
2. *500 MB video — API receives all of it?* No — presigned multipart upload.

## Project (checklist)

`POST /files/upload-url`, `GET /files/:id`, `DELETE /files/:id`; Node API + PostgreSQL (metadata) + S3 (bytes).

## Added notes (not in source)

- S3 offers **strong read-after-write consistency** for object operations (since 2020).
- New buckets have **Block Public Access** enabled and objects are encrypted with **SSE-S3 by default** (2023 defaults); ACLs are disabled by default via bucket-owner-enforced ownership. *(Verify against current docs.)*
- S3 durability is designed for **11 nines** (99.999999999%).
- Browser uploads directly to S3 need **CORS** configured on the bucket.
- A presigned `PUT` signed with `ContentType` requires the client to send the same `Content-Type` header.
- A presigned URL carries the signer's permissions and cannot outlive the signing credentials (short-lived role credentials ⇒ shorter effective expiry).
- Multipart limits: parts ≥ 5 MiB (except last), up to 10,000 parts; single PUT up to 5 GB, object up to 5 TiB.
- With SSE-KMS the role also needs KMS permissions (e.g. `kms:Decrypt`, `kms:GenerateDataKey`).
- Other classes: Intelligent-Tiering, One Zone-IA, Glacier Instant/Flexible Retrieval, Deep Archive.

## Interview questions (25) — pointers

S3; bucket; object; key; is it a filesystem; S3 vs EBS vs EFS; why not EC2 local storage; versioning; lifecycle; storage classes; encryption at rest; SSE-S3 vs SSE-KMS; bucket policy; IAM vs bucket policy; why not public; presigned URL & why; multipart; 1 GB upload; secure Node → S3 access; why no hard-coded credentials; multi-instance file storage; metadata in PostgreSQL vs content in S3; CloudFront + S3.

<!-- NAV -->

---

← [Sheet 10](ch10-revision.md) · [Full chapter 11](../docs/04-aws/ch11-s3-storage.md) · [All revision material](README.md) · [Sheet 12](ch12-revision.md) →
