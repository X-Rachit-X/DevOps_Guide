# Chapter 10 — Revision Sheet: EC2 + AWS Compute

> Supplements [the full chapter](../docs/04-aws/ch10-ec2-compute.md).

## What EC2 is

**Amazon EC2 (Elastic Compute Cloud)** = virtual servers in AWS. An instance = virtual machine with vCPU, RAM, storage (EBS), network interface, OS (Linux/Windows). You control much more than with managed services. Placement: Region → VPC → Subnet → Instance (+ EBS + network interface/IP).

- **AMI** (Amazon Machine Image) = blueprint (OS + preinstalled software + configuration). **Instance** = running VM launched from it. Analogy: Docker image → container (not exact).
- **Launch checklist:** AMI → instance type → network/subnet → security group → storage → IAM role → launch.

## Instance types & pricing

| Family | Use |
|---|---|
| General purpose | Balanced; Node.js API with moderate traffic |
| Compute optimized | CPU-heavy: batch, computation-heavy services |
| Memory optimized | Large in-memory datasets, caching |
| Storage optimized | High local storage performance/capacity |
| Accelerated computing | GPUs/accelerators |

Principle: **choose by workload characteristics, not the biggest instance.**

| Pricing | Notes |
|---|---|
| **On-Demand** | Pay per use, no commitment; unpredictable workloads/flexibility |
| **Commitment-based (Reserved / Savings)** | Commit for a period → discount; predictable workloads |
| **Spot** | Spare capacity, big discounts, **can be interrupted**; for batch/distributed/flexible work — never for interruption-intolerant workloads |

## Access & security

- **Key pair:** private key on your computer, public key on EC2. `ssh -i my-key.pem ubuntu@<server-ip>`. Never commit `.pem`. SSH keys let the server verify possession of the private key without transmitting it.
- **Security Group:** virtual firewall on the instance's network interface; **stateful** (return traffic of allowed connections is automatically allowed; NACLs are stateless). Open only what's needed (22/80/443). Better: Internet → LB :443 → EC2 :3000 with the EC2 SG allowing 3000 **only from the load balancer's security group**.
- **Public vs private EC2:** public (Internet → public IP → EC2) vs private (Internet → LB → private EC2, preferred for application tier).
- **Public IP ≠ permission:** reachability needs *Route + Security Group + network config + app listening*.
- **Private IP** (e.g. `10.0.1.25`) for in-VPC traffic, e.g. EC2 → RDS private IP (don't expose DBs publicly).
- **Elastic IP:** persistent public IPv4 (a normal public IPv4 can change after stop/start). In modern designs users hit DNS → LB, not an EC2 IP.
- **SSH hardening:** don't open `0.0.0.0/0 → 22` if avoidable; restrict to trusted IPs, VPN/private connectivity, or **AWS Systems Manager Session Manager** (reduces need for public SSH).
- **Security checklist:** least-privilege IAM role · restrictive SGs · updated OS/packages · no unnecessary ports · HTTPS · no secrets in source · DB not public · logs/metrics monitored · backups · careful SSH.

## Storage

- **EBS (Elastic Block Store)** = persistent block storage attached to EC2 (OS files, app files, logs, data). Compute and storage are separate, so storage can persist independently of compute in many scenarios.
- Don't run the DB on EC2 by default — you'd handle backups, updates, replication, failover, monitoring, storage → use **RDS** (Ch.13).
- What should NOT live only on EC2: ❌ uploads on EC2 disk, ❌ DB only on EC2, ❌ state only in a container → Files → **S3**, DB → **RDS**, Cache → **ElastiCache/Redis**, Compute → EC2/ECS/EKS/Lambda.

## Bootstrapping & identity

- **User data** = startup script at launch, e.g. `apt update -y; apt install -y docker.io; systemctl enable docker; systemctl start docker`.
- **Instance metadata** = info (and temporary role credentials) exposed to the instance; use **IMDSv2**.
- **EC2 IAM role** → temporary credentials → AWS APIs (Node API → EC2 role → `s3:GetObject`); SDK obtains credentials through the instance-role mechanism. **Very important interview concept.**

## Docker on EC2

Install Docker (Ubuntu: `sudo apt install docker.io`; `systemctl enable/start docker`; `docker --version`; `sudo docker ps`), then `docker pull <registry>/my-api:1.0` → `docker run -d --name api -p 3000:3000 my-api:1.0`.
Manual deploy: build image → push to registry → SSH → `docker pull` → `docker stop api; docker rm api` → `docker run …` (works, but not sophisticated → CI/CD + orchestration).
Request path: Internet → Public IP → Security Group → EC2 → Docker :3000 → Node.js → Express. Production: Users → DNS → Load Balancer → EC2 (AZ-A/AZ-B) → Docker → Node API → RDS / S3, with IAM controlling access and CloudWatch monitoring.

## Troubleshooting on a live instance

| Symptom | Check | Notes |
|---|---|---|
| Slow API / CPU 100% | `top` | Infinite loop, CPU-heavy op, traffic spike, memory pressure, poor code — **diagnose before resizing** |
| Memory | `free -h` | Leak, too many processes, big workload, undersized |
| Disk 100% | `df -h` | Can't write logs/temp/data; causes: logs, Docker images, temp files, app data |
| Unreachable externally | `ss -tulpn` | Listening on `127.0.0.1:3000` vs `0.0.0.0:3000` |

**Scenario (running app, no Internet access):** EC2 running? → Node process? → `docker ps` → `docker logs` → listening on `0.0.0.0:3000`? → Docker port mapping? → Security Group? → subnet route? → public IP / LB config? → app errors?

## Instance states

Pending → Running → Stopping → Stopped → Shutting-down → Terminated. **Stop** = shut down, can be started again. **Terminate** = deleted, cannot simply be started again.

## Scaling

Single EC2 at 100% CPU → Load Balancer + multiple EC2 → **Auto Scaling** (3 → 5 → 10 → back down). Vertical (2 CPU/4 GB → 8 CPU/16 GB) vs horizontal (1 → 3 → 10 EC2). Horizontal scaling works best with **stateless APIs**: shared DB + shared cache/session store (any instance can serve any request).

## Added notes (not in source)

- **Instance store vs EBS:** some instance types have *instance store* (ephemeral local disk lost when the instance stops/terminates); EBS volumes persist. The chapter heading "EC2 Local Disk vs EBS" only discusses EBS.
- EBS volumes live in **one AZ**; back them up with snapshots.
- **User data** by default runs once, at first boot, as root.
- **IMDSv2** is session-oriented (a token is requested with a PUT, then sent as a header) to mitigate SSRF-style credential theft.
- AWS charges for **public IPv4 addresses** (including those attached to running instances) since 2024 — relevant when choosing Elastic IPs vs a load balancer. *(Verify current pricing before relying on it.)*
- To run `docker` without `sudo`, users are added to the `docker` group — this is effectively root-equivalent access; be careful.
- Amazon Linux uses `dnf`/`yum` rather than `apt`.

## Interview questions (25) — pointers

EC2; AMI; AMI vs instance; instance type & how to choose; On-Demand vs Spot; EBS; security group; why not expose every port; public vs private EC2; public vs private IP; `0.0.0.0:3000`; running-but-unreachable; S3 access via role; role vs hardcoded creds; unrestricted SSH danger; reduce SSH exposure; deploy Dockerized app; what `docker run -p 3000:3000` does; update; roll back; vertical vs horizontal; why multiple instances; why a load balancer; Auto Scaling.

<!-- NAV -->

---

← [Sheet 9](ch09-revision.md) · [Full chapter 10](../docs/04-aws/ch10-ec2-compute.md) · [All revision material](README.md) · [Sheet 11](ch11-revision.md) →
