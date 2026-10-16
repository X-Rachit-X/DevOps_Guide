# Chapter 12 — Revision Sheet: VPC + AWS Networking

> Supplements [the full chapter](../docs/04-aws/ch12-vpc-networking.md). Goal: look at the VPC diagram and explain *exactly why each component exists and how traffic flows*.

## VPC building blocks

| Component | What it does |
|---|---|
| **VPC** | Your logically isolated private network in AWS; you control IP ranges, subnets, routing, network access, internet and private connectivity |
| **CIDR** | VPC range, e.g. `10.0.0.0/16`; subnets carve it up (`10.0.1.0/24`, `10.0.2.0/24`, `10.0.11.0/24`, `10.0.12.0/24`). CIDR determines the available address range — don't just memorise /16 and /24 |
| **Subnet** | Subdivision of the VPC range; **lives in exactly one AZ** |
| **Route table** | "If traffic is going to X, send it to Y" |
| **Internet Gateway (IGW)** | Connects the VPC to the Internet. Attaching it does **not** make every subnet public — the subnet's route table must send Internet traffic to it |
| **NAT Gateway** | Lets private-subnet resources **initiate outbound** connections without being reachable inbound |
| **Security Group** | Stateful firewall on resources/ENIs |
| **NACL** | Stateless firewall at subnet boundary |
| **VPC Endpoint** | Private connectivity from the VPC to supported AWS services |
| **VPC Flow Logs** | Capture info about IP traffic to/from network interfaces (for investigating network issues) |

## Public vs private subnet = routing

```text
Public route table :  10.0.0.0/16 → local      0.0.0.0/0 → IGW
Private route table:  10.0.0.0/16 → local      0.0.0.0/0 → NAT Gateway
```

- Public subnet = route table has a route to the IGW (resources may also have public IPv4). Private = no direct IGW route; outbound via NAT.
- **The key distinction is routing, not whether the resource has a public IP.**
- `0.0.0.0/0` = default route (anything without a more specific route). `10.0.0.0/16 → local` keeps VPC-internal traffic inside the VPC (EC2 `10.0.11.10` → RDS `10.0.12.20` never touches the Internet).
- **NAT:** private EC2 `10.0.10.25` → NAT Gateway → IGW → Internet (e.g. `apt update`, external API calls, dependency downloads). Outside servers have no direct route back to the private IP. **NAT does not allow Internet → private EC2.**

## Security groups, NACLs

| | Security Group | NACL |
|---|---|---|
| Scope | Resource / network interface | Subnet |
| State | **Stateful** | **Stateless** (inbound and outbound evaluated independently) |
| Rules | Allow-focused | Allow + deny |
| Role | Primary fine-grained control | Additional subnet-level layer |

- **SG-to-SG referencing:** allow API SG only from ALB SG; allow DB SG port 5432 **only from SG-API** (instead of `0.0.0.0/0`). Much more precise.
- Flow of rules: `Internet → ALB SG :443` · `ALB SG → API SG :3000` · `API SG → DB SG :5432`.
- Stateful example: inbound TCP 443 allowed ⇒ return traffic automatically allowed.

## Reference architecture (memorise)

```text
VPC 10.0.0.0/16
AZ-A: Public 10.0.1.0/24 | Private 10.0.11.0/24        AZ-B: Public 10.0.2.0/24 | Private 10.0.12.0/24
Public subnets → ALB (+ NAT Gateway) ; Private app subnets → EC2 ; Private DB subnets → RDS
```

**Three-tier:** Presentation (public subnets/LB) → Application (Node.js in private subnets) → Data (RDS in database subnets). Database should not face the Internet — smaller attack surface.
**Traffic:** User → DNS → IGW → public subnet ALB → private subnet EC2/Node → private subnet RDS.
**Don't expose `:3000`** to the Internet when an ALB can take `:443`; EC2 SG accepts 3000 only from the ALB SG.

**NAT and HA:** NAT-A for AZ-A and NAT-B for AZ-B avoids a cross-AZ single point of failure, but costs more. *Trade-off: high availability needs avoiding single points of failure, but redundancy raises cost and complexity.*

## DNS and endpoints

- Use names (`api.internal`, DB endpoint) instead of IPs because infrastructure changes. VPC provides DNS resolution inside AWS; Route 53 is AWS DNS (Ch.16).
- **VPC endpoints:** private EC2 → endpoint → AWS service (S3) instead of NAT → Internet → S3. **Gateway endpoint** (S3, DynamoDB) vs **Interface endpoint** (private network interfaces, many AWS services).

## Troubleshooting

**EC2 → RDS fails:** correct RDS endpoint? port 5432? network connectivity? route tables? RDS SG? source SG/IP allowed? NACL? DB running? credentials? app configuration?
**Internet → EC2 fails:** EC2 running? app listening on `0.0.0.0`? port? SG? subnet route? IGW? public IP? NACL?
**`curl http://localhost:3000/health` works but external fails** → check port binding, Docker port mapping, SG, routing, public/private architecture.
**Practical question:** *EC2 can reach the Internet but the Internet can't reach EC2 — what to change?* Public IP + route table + IGW + SG + NACL + app listening.

## Interview design answer

ALB → public subnets · EC2 → private subnets · RDS → private DB subnets · IGW → public connectivity · NAT GW → outbound Internet for private resources · SGs → restrict traffic between tiers · multiple AZs → availability.

## Added notes (not in source)

- AWS **reserves 5 IP addresses per subnet** (network address, VPC router, DNS, future use, broadcast) — a `/24` gives 251 usable addresses. VPC CIDR sizes range from `/16` to `/28`.
- **Defaults:** a new SG denies all inbound and allows all outbound; the default NACL allows all traffic in and out; custom NACL rules are numbered and evaluated in order, and (because stateless) need ephemeral-port rules for return traffic.
- The NAT Gateway is created **in a public subnet** (with an Elastic IP); private route tables point to it. NAT Gateways bill hourly plus per-GB processed; interface endpoints also bill, **gateway endpoints for S3/DynamoDB are free** — a common cost optimisation.
- VPC DNS needs `enableDnsSupport` / `enableDnsHostnames`.
- Related topics not covered here: VPC peering, Transit Gateway, bastion hosts, IPv6/egress-only IGW.

## Interview questions (25) — pointers

VPC; why VPC; CIDR; subnet; why one AZ per subnet; public vs private; what makes a subnet public; route table; `0.0.0.0/0`; IGW; NAT; why private subnets need NAT; does NAT permit inbound; SG vs NACL; stateful vs stateless; why RDS shouldn't be public; EC2 → RDS access; SG-to-SG rules; design a VPC; where ALB / EC2 / RDS go; why app in private subnets; multiple AZs; private EC2 → S3 (VPC endpoint).

<!-- NAV -->

---

← [Sheet 11](ch11-revision.md) · [Full chapter 12](../docs/04-aws/ch12-vpc-networking.md) · [All revision material](README.md) · [Sheet 13](ch13-revision.md) →
