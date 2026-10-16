# Chapter 4 — Revision Sheet: Networking for Cloud & DevOps

> Supplements [the full chapter](../docs/01-foundations/ch04-networking.md).

## Layer map (what to remember from OSI / TCP-IP)

| OSI | TCP/IP | Practical examples |
|---|---|---|
| 7 Application (6 Presentation, 5 Session) | Application | HTTP, DNS, TLS-protected HTTPS |
| 4 Transport | Transport | TCP, UDP — ports live here |
| 3 Network | Internet | IP — addresses and routing |
| 2 Data Link (1 Physical) | Network Access | Ethernet, Wi-Fi, MAC |

HTTP → TCP → IP → Ethernet/Wi-Fi. Each layer adds the information needed to deliver data. Data travels as **packets**.

## Identity: MAC vs IP vs Port vs Socket

- **MAC** = local network-interface identity (relevant inside a local segment).
- **IP** = network-level address of an interface; used for routing.
- **Port** = which application/service on that machine (22 SSH, 80 HTTP, 443 HTTPS, 3000 Node, 5432 PostgreSQL, 6379 Redis).
- **Socket** = IP + port (`10.0.1.10:3000`). A TCP connection is identified by source IP:port + destination IP:port (`192.168.1.5:52144 → 10.0.1.10:3000`).

## Addressing & subnet maths

- IPv4 = 32 bits (4 × 8), 2³² ≈ 4.29 billion addresses. IPv6 = 128 bits (`2001:db8::1`), solves address exhaustion.
- Private ranges: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`. Public = globally routable.
- **CIDR** `a.b.c.d/p`: first *p* bits = network, remaining `32 − p` = hosts.
  - Total addresses = **2^(32−p)**. Traditional usable hosts = **2^(32−p) − 2** (network + broadcast).
  - `/16` → 65,536; `/24` → 256 (254 usable); `/32` → one host.
  - **Smaller prefix number = larger network.**
- ⚠ AWS reserves **5** addresses in each subnet (so a `/24` has 251 usable in AWS) — *added note; the full VPC detail is in [Chapter 12](../docs/04-aws/ch12-vpc-networking.md)*.
- Example plan: VPC `10.0.0.0/16` → Public `10.0.1.0/24`, Private `10.0.2.0/24`, Private DB `10.0.3.0/24`.

## Transport

| TCP | UDP |
|---|---|
| Connection-oriented, reliable, ordered byte stream | Connectionless datagrams, no delivery/order guarantee |
| Sequencing, ACKs, retransmission, flow + congestion control | Lower overhead |
| HTTP/HTTPS, SSH, DB connections | DNS queries, real-time media, gaming |

- **Three-way handshake:** client `SYN` → server `SYN-ACK` → client `ACK` → established.
- Not "TCP good / UDP bad" — different problems. **HTTP/3 runs over QUIC, which uses UDP.**

## DNS

Names → addresses. Records: **A** (name → IPv4), **AAAA** (→ IPv6), **CNAME** (name → another name), **MX** (mail), **TXT** (arbitrary text, verification), **NS** (name servers). Tools: `nslookup`, `dig`. (Route 53 = AWS DNS, [Chapter 16](../docs/04-aws/ch16-route53-cloudfront-waf.md).)

## HTTP

- Request: `GET /users HTTP/1.1` + `Host: api.example.com`. Response: `HTTP/1.1 200 OK` + headers + body.
- Methods: GET retrieve, POST create/submit, PUT replace, PATCH partial modify, DELETE remove.
- Status codes: 2xx success (200 OK, 201 Created, 204 No Content) · 3xx redirect (301 permanent, 302 temporary) · 4xx client (400, 401 Unauthorized, 403 Forbidden, 404, 429 Too Many Requests) · 5xx server (500, **502 Bad Gateway**, 503 Service Unavailable, 504 Gateway Timeout).
- **HTTPS = HTTP + TLS** → confidentiality, integrity, server authentication (certificates). TLS is usually terminated at load balancers, reverse proxies, or CDNs.

## Proxies, load balancing, firewalls, NAT, routing

- **Reverse proxy** (Nginx in front of Node) acts for the *server*: TLS termination, routing, buffering, compression, static files, connection management. **Forward proxy** acts for the *client*.
- **Load balancer** spreads requests over backends: scalability, availability, distribution, health checks. Algorithms: **round robin**, **least connections**, **weighted** (e.g. 70/30).
- **Firewall** = rule-based traffic control. AWS: Security Groups, Network ACLs, AWS WAF (different levels).
- **NAT** translates private source address to public so private hosts can reach the Internet without being reachable from it. AWS: Private EC2 → NAT Gateway → Internet Gateway → Internet.
- **Routing table**: `10.0.0.0/16 → local`, `0.0.0.0/0 → Internet Gateway`. `0.0.0.0/0` = **default route** (used when no more-specific route exists).

## AWS network model (preview)

Route 53 (DNS) → CloudFront (CDN) → WAF (HTTP-layer filtering) → ALB → EC2 → RDS inside a VPC with subnets, Security Groups, route tables, NAT Gateway.

| Public subnet | Private subnet |
|---|---|
| Route table has a route to an Internet Gateway + resources have public addressing | No direct inbound Internet route/addressability |
| ALB lives here | Backends/DB live here; outbound via NAT Gateway |

> **Private ≠ "no Internet".** It means *no direct inbound Internet route*.

| Security Group | Network ACL |
|---|---|
| Resource (ENI/EC2) level | Subnet boundary |
| **Stateful** | **Stateless** |
| Allow rules | Inbound + outbound rules |

Principle: **only expose what must be exposed** — Internet → ALB:443 ✅; Internet → EC2:3000 ❌; Internet → RDS:5432 ❌; EC2 → RDS:5432 ✅.

## Troubleshooting chain ("app on :3000 unreachable")

App running? → listening? → `0.0.0.0` vs `127.0.0.1`? → correct port? → Linux firewall → Security Group → NACL → route table → load balancer → DNS.

- Listening on **`127.0.0.1`** = same machine only; **`0.0.0.0`** = all IPv4 interfaces (subject to firewalls). Classic deploy bug. Node: `app.listen(3000, "0.0.0.0", …)`.
- **502 Bad Gateway:** the proxy/LB got an invalid response from upstream → check LB target health → target port → Security Group → app → app logs.

## Commands

`ip addr` · `ip route` · `ss -tulpn` · `nslookup example.com` · `dig example.com` · `ping` · `curl -I https://…` (headers) · `curl -v https://…` (shows DNS, connect, TLS handshake, request, response).

## "What happens when you visit https://api.example.com/users?" (memorise)

1. DNS resolves name → IP. 2. TCP connection (3-way handshake). 3. TLS handshake. 4. HTTP request `GET /users`, `Host:`. 5. Passes CloudFront → WAF → Load Balancer → backend. 6. Node.js handles route. 7. Queries PostgreSQL. 8. Response flows DB → Node → LB → client.

## Checkpoint questions (18) — pointers

IP; private vs public; port; TCP vs UDP; handshake; DNS; A/AAAA/CNAME; CIDR; why `/16` > `/24`; NAT; reverse proxy; load balancer; HTTPS; TLS; public vs private subnet; SG vs NACL; why `localhost:3000` isn't externally reachable; trace the request (#18, the most important).

Extra added precision: DNS usually uses UDP/53 but falls back to TCP for large responses and zone transfers.

<!-- NAV -->

---

← [Sheet 3](ch03-revision.md) · [Full chapter 4](../docs/01-foundations/ch04-networking.md) · [All revision material](README.md) · [Sheet 5](ch05-revision.md) →
