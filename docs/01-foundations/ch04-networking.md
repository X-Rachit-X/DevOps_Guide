# Chapter 4 — Networking for Cloud & DevOps

> **Source:** Response 4 of the original conversation (`source-archive/src-04.txt`, lines 1–1879) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch04-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

This is one of the **most important responses in the entire roadmap**.

If Docker, AWS, Kubernetes, and DevOps are the tools, **networking is the foundation underneath them**.

When an interviewer asks:

> "Your application is running on EC2, but users can't access it. What would you check?"

You need networking knowledge to answer.

We'll go from **zero → practical → cloud-level → interview-level**.

---

## 1. The Big Picture

Imagine your TypeScript backend:

```text
                    Internet
                       │
                    User
                       │
                    HTTPS
                       │
                    DNS
                       │
                 Load Balancer
                       │
                  Application
                       │
                   Database
```

Every arrow involves networking.

You need to understand:

- How devices identify each other
- How data travels
- How applications communicate
- How domains become IP addresses
- How ports work
- How HTTPS works
- How networks are divided
- How routers forward packets
- How NAT works
- How firewalls control traffic
- How load balancers distribute traffic

Then we'll map all of that to AWS.

---

## 2. What Is a Network?

A network is simply:

> **A collection of devices that can communicate with each other.**

For example:

```text
Laptop ───── Router ───── Server
```

Or:

```text
Phone
   │
Wi-Fi Router
   │
Internet
   │
AWS
   │
EC2
```

Communication happens by sending **data** between devices.

---

## 3. Packet — The Basic Unit

When you send a large piece of data, it generally doesn't travel as one giant object.

It's broken into smaller units called **packets**.

Imagine sending:

```text
"HELLO WORLD"
```

Conceptually:

```text
Packet 1 → HEL
Packet 2 → LO
Packet 3 → WORLD
```

The network moves these packets toward their destination.

---

## 4. OSI Model

You have probably studied OSI before.

For Cloud/DevOps, don't memorize it blindly.

Understand what each layer represents.

```text
7  Application
6  Presentation
5  Session
4  Transport
3  Network
2  Data Link
1  Physical
```

For practical software engineering, these are especially important:

```text
Application → HTTP, DNS
Transport   → TCP, UDP
Network     → IP
Data Link   → Ethernet, MAC
```

---

## 5. TCP/IP Model

In practice, you'll often think in terms of TCP/IP:

```text
Application
Transport
Internet
Network Access
```

Example HTTP request:

```text
HTTP
 ↓
TCP
 ↓
IP
 ↓
Ethernet/Wi-Fi
```

Each layer adds information needed to deliver the data.

---

## 6. MAC Address

At the local network level, devices have a **MAC address** associated with their network interface.

Example:

```text
A4:5E:60:12:AB:91
```

Think:

> MAC = local network interface identity.

IP addresses are used for network-level addressing and routing.

MAC addresses are primarily relevant within local network segments.

---

## 7. IP Address

An IP address identifies a network interface at the IP layer.

IPv4 example:

```text
192.168.1.10
```

Another:

```text
8.8.8.8
```

The first is commonly used as a private address.

The second is a public address.

---

## 8. Private vs Public IP

#### Private IP

Used inside private networks.

Common IPv4 private ranges:

```text
10.0.0.0/8

172.16.0.0/12

192.168.0.0/16
```

Example:

```text
192.168.1.20
```

This isn't directly routable across the public Internet.

---

#### Public IP

Globally routable address.

For example:

```text
203.x.x.x
```

Conceptually:

```text
Private Network
       │
       │ NAT
       ↓
 Public Internet
```

This distinction becomes extremely important with AWS VPCs.

---

## 9. IPv4

IPv4 uses **32 bits**.

Example:

```text
192.168.1.10
```

Each number represents 8 bits:

```text
192    .168    .1    .10
 ↓       ↓      ↓      ↓
 8       8      8      8 bits
```

Total:

```text
8 × 4 = 32 bits
```

Maximum theoretical addresses:

```text
2^32 ≈ 4.29 billion
```

The Internet eventually needed more addresses, leading to IPv6.

---

## 10. IPv6

IPv6 uses **128 bits**.

Example:

```text
2001:db8::1
```

The address space is enormous.

You don't need to become an IPv6 specialist for our goal, but you should understand:

> IPv6 solves the address-space limitations of IPv4 and introduces other architectural differences.

---

## 11. Subnetting

This is **very important for cloud interviews**.

Suppose we have:

```text
192.168.1.0/24
```

The `/24` is called the **prefix length**.

It means:

```text
First 24 bits → network portion
Remaining 8 bits → host portion
```

Therefore:

```text
2^8 = 256
```

total addresses in the subnet.

In traditional IPv4 subnet calculations, two addresses are typically reserved for network and broadcast, leaving:

```text
254 usable host addresses
```

for a normal `/24` subnet.

---

## 12. CIDR

CIDR = **Classless Inter-Domain Routing**.

You'll constantly see:

```text
10.0.0.0/16
10.0.1.0/24
10.0.1.10/32
```

The `/number` tells you how many bits belong to the network prefix.

For example:

```text
10.0.0.0/16
```

means:

```text
16 network bits
16 remaining bits
```

So:

```text
2^16 = 65,536
```

addresses in the block.

---

## 13. `/16` vs `/24`

Consider:

```text
10.0.0.0/16
```

versus:

```text
10.0.0.0/24
```

The `/16` block is larger.

```text
/16
↓
65,536 addresses

/24
↓
256 addresses
```

Think:

```text
Smaller prefix number
        ↓
Larger network

Larger prefix number
        ↓
Smaller network
```

This will become critical when designing VPCs.

---

## 14. Example Cloud Network

Suppose we create:

```text
VPC
10.0.0.0/16
```

We divide it:

```text
VPC: 10.0.0.0/16

├── Public Subnet
│   10.0.1.0/24
│
├── Private Subnet
│   10.0.2.0/24
│
└── Private DB Subnet
    10.0.3.0/24
```

Now we have isolated network segments.

We'll later build this properly in AWS.

---

## 15. What Is a Port?

An IP address identifies the **machine/interface**.

But one machine can run many applications.

For example:

```text
Server: 10.0.1.10
```

Could have:

```text
Port 22   → SSH
Port 80   → HTTP
Port 443  → HTTPS
Port 3000  → Node.js
Port 5432  → PostgreSQL
Port 6379  → Redis
```

So think:

```text
IP = Which machine/network interface?

Port = Which application/service?
```

---

## 16. Socket

A network connection is commonly associated with:

```text
IP + Port
```

For example:

```text
10.0.1.10:3000
```

means:

> Service reachable at IP `10.0.1.10`, port `3000`.

A TCP connection is identified more precisely by a combination of source/destination IPs and ports.

Conceptually:

```text
Client
192.168.1.5:52144
        │
        │ TCP
        ↓
Server
10.0.1.10:3000
```

---

## 17. TCP

TCP = **Transmission Control Protocol**.

TCP provides reliable, ordered byte-stream communication.

It handles things such as:

- connection establishment
- sequencing
- retransmission
- acknowledgements
- flow control
- congestion control

If data is lost, TCP can retransmit it.

This reliability is useful for things like:

```text
HTTP/HTTPS
SSH
Database connections
```

---

## 18. TCP Three-Way Handshake

Before normal TCP data transfer, a connection is established.

Simplified:

```text
Client                  Server

  SYN ─────────────────→

      ←──────────── SYN-ACK

  ACK ─────────────────→

       Connection established
```

Think:

```text
Client: "Can we communicate?"
Server: "Yes."
Client: "Great."
```

This is the **three-way handshake**.

---

## 19. UDP

UDP is connectionless and provides a simpler datagram transport.

It doesn't provide TCP-style guarantees of:

- delivery
- ordering
- retransmission

This makes it useful when low overhead or application-controlled behavior matters.

Examples include:

- DNS queries commonly using UDP
- real-time media
- gaming
- certain streaming/network protocols

Don't think:

> TCP = good, UDP = bad.

They solve different problems.

---

## 20. TCP vs UDP

| TCP | UDP |
|---|---|
| Connection-oriented | Connectionless |
| Reliable delivery | No built-in delivery guarantee |
| Ordered byte stream | Datagrams |
| Retransmission | No TCP-style retransmission |
| More overhead | Lower overhead |
| HTTP/HTTPS, SSH | DNS, real-time traffic, etc. |

Interview question:

> **Why does HTTP traditionally use TCP?**

Because HTTP applications generally need reliable, ordered transport.

Modern HTTP/3 is an important exception because it runs over **QUIC**, which uses UDP underneath.

We'll touch on that later.

---

## 21. DNS

DNS = **Domain Name System**.

Humans prefer:

```text
google.com
api.myapp.com
```

Machines communicate using IP addresses.

DNS translates names into addresses or other records.

Conceptually:

```text
Browser
   │
   │ "What is api.example.com?"
   ↓
DNS
   │
   ↓
IP address
```

For example:

```text
api.example.com
        ↓
203.0.113.10
```

---

## 22. DNS Records

Important record types:

#### A

Maps a domain to an IPv4 address.

```text
example.com → 203.0.113.10
```

#### AAAA

Maps a domain to IPv6.

#### CNAME

Maps one domain name to another domain name.

#### MX

Mail exchange.

#### TXT

Arbitrary text records often used for verification and other purposes.

#### NS

Name server records.

You'll encounter these extensively with Route 53.

---

## 23. DNS Lookup

Try:

```bash
nslookup example.com
```

or:

```bash
dig example.com
```

You'll see DNS information.

You can also use:

```bash
curl https://example.com
```

which eventually depends on name resolution.

---

## 24. HTTP

HTTP = **Hypertext Transfer Protocol**.

It's an application-layer protocol used heavily for web communication.

Typical request:

```http
GET /users HTTP/1.1
Host: api.example.com
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "users": []
}
```

---

## 25. HTTP Methods

Important methods:

```text
GET
POST
PUT
PATCH
DELETE
```

Common interpretation:

```text
GET    → retrieve
POST   → create/submit
PUT    → replace
PATCH  → partially modify
DELETE → remove
```

Your Node.js APIs use these constantly.

For example:

```typescript
app.get("/users", (req, res) => {
  res.json([]);
});
```

When someone sends:

```text
GET /users
```

the server handles it.

---

## 26. HTTP Status Codes

Important categories:

```text
2xx → Success
3xx → Redirection
4xx → Client-side/request problem
5xx → Server-side failure
```

Examples:

```text
200 → OK
201 → Created
204 → No Content

301 → Permanent redirect
302 → Temporary redirect

400 → Bad Request
401 → Unauthorized
403 → Forbidden
404 → Not Found
429 → Too Many Requests

500 → Internal Server Error
502 → Bad Gateway
503 → Service Unavailable
504 → Gateway Timeout
```

These will become extremely useful when debugging distributed systems.

---

## 27. HTTPS

HTTPS is essentially HTTP protected by **TLS**.

```text
HTTP
 +
TLS
 =
HTTPS
```

Without encryption:

```text
Client ───── HTTP ───── Server
```

Network observers may be able to inspect sensitive application data.

With HTTPS:

```text
Client ───── encrypted TLS ───── Server
```

TLS provides important properties such as:

- confidentiality
- integrity
- server authentication

---

## 28. TLS — High-Level View

When connecting securely:

```text
Client
  │
  │ TLS handshake
  ↓
Server
```

The handshake establishes cryptographic parameters and authenticates the server using certificates.

Afterward, application data is encrypted.

You don't need to implement TLS yourself in normal backend development.

Cloud infrastructure commonly handles TLS termination at:

- load balancers
- reverse proxies
- CDNs

---

## 29. Reverse Proxy

Suppose users directly access your Node.js application:

```text
Internet
   ↓
Node.js :3000
```

You might instead use Nginx:

```text
Internet
   ↓
Nginx :443
   ↓
Node.js :3000
```

Nginx acts as a **reverse proxy**.

The client doesn't directly communicate with the Node process.

Nginx can handle:

- TLS termination
- routing
- buffering
- compression
- static files
- connection management

---

## 30. Forward Proxy vs Reverse Proxy

#### Forward proxy

Acts on behalf of the **client**.

```text
Client
  ↓
Forward Proxy
  ↓
Internet
```

#### Reverse proxy

Acts on behalf of the **server/application**.

```text
Client
  ↓
Reverse Proxy
  ↓
Application
```

Remember:

> Forward proxy → protects/represents clients.

> Reverse proxy → protects/represents servers.

---

## 31. Load Balancer

Imagine one server:

```text
Users
  ↓
Server
```

If traffic increases:

```text
Users
  ↓
?
```

We can add multiple servers:

```text
             Load Balancer
              /    |    \
             ↓     ↓     ↓
           App1   App2   App3
```

The load balancer distributes requests among backend servers.

Benefits include:

- scalability
- availability
- traffic distribution
- health checking

---

## 32. Load Balancing Algorithms

Common concepts:

#### Round Robin

```text
Request 1 → Server A
Request 2 → Server B
Request 3 → Server C
Request 4 → Server A
```

#### Least Connections

Send traffic toward a server with fewer active connections.

#### Weighted

Give some servers more traffic:

```text
A → 70%
B → 30%
```

Cloud load balancers provide sophisticated routing and health-check capabilities.

---

## 33. Firewall

A firewall controls network traffic based on rules.

Conceptually:

```text
Internet
   ↓
Firewall
   │
   ├── Allow 443
   ├── Allow 22 from trusted source
   └── Block everything else
```

In AWS, you'll encounter:

- Security Groups
- Network ACLs
- AWS WAF

They're different mechanisms operating at different levels.

---

## 34. NAT

NAT = **Network Address Translation**.

Suppose your private machine is:

```text
10.0.1.20
```

It needs to access the Internet.

Private addresses aren't directly routable on the public Internet.

NAT can translate the private source address to a public address.

Conceptually:

```text
Private Server
10.0.1.20
     │
     ↓
   NAT
     │
     ↓
Public Internet
```

This becomes **very important in AWS**.

For example:

```text
Private EC2
    ↓
NAT Gateway
    ↓
Internet Gateway
    ↓
Internet
```

The private EC2 can initiate outbound Internet connections without being directly reachable from the Internet.

---

## 35. Routing

A router decides where packets should go next.

Imagine:

```text
Network A
   ↓
Router
   ↓
Network B
   ↓
Router
   ↓
Network C
```

Routing tables contain rules like:

```text
Destination       Next hop
10.0.0.0/16       local
0.0.0.0/0         Internet Gateway
```

The `0.0.0.0/0` route is commonly called the **default route**.

Meaning:

> If there isn't a more specific route, use this one.

AWS route tables are based on this same fundamental concept.

---

## 36. What Happens When You Visit a Website?

This is a **very important interview question**.

Suppose you enter:

```text
https://api.example.com/users
```

Let's trace it.

#### Step 1 — DNS

Your system resolves:

```text
api.example.com
       ↓
IP address
```

#### Step 2 — Network connection

Your machine communicates with the destination using the relevant transport protocol.

For traditional HTTPS:

```text
TCP connection
```

#### Step 3 — TLS

HTTPS establishes a secure TLS connection.

#### Step 4 — HTTP request

```http
GET /users
Host: api.example.com
```

#### Step 5 — Server infrastructure

Perhaps:

```text
Internet
   ↓
CloudFront
   ↓
WAF
   ↓
Load Balancer
   ↓
Backend
```

#### Step 6 — Application

Node.js processes the request.

```typescript
app.get("/users", async (req, res) => {
  const users = await db.user.findMany();

  res.json(users);
});
```

#### Step 7 — Database

```text
Node.js
   ↓
PostgreSQL
```

#### Step 8 — Response

```text
PostgreSQL
   ↓
Node.js
   ↓
Load Balancer
   ↓
Client
```

That's the basic journey.

---

## 37. Now Connect This to AWS

Here's where networking becomes powerful.

Imagine:

```text
                         Internet
                            │
                         Route 53
                            │
                       CloudFront
                            │
                           WAF
                            │
                           ALB
                      ┌─────┴─────┐
                      ↓           ↓
                 Public subnet  Public subnet
                      │           │
                    EC2         EC2
                      │           │
                 Private networking
                      │
                     RDS
```

The important concepts are:

```text
Route 53 → DNS
CloudFront → CDN
WAF → HTTP-layer filtering
ALB → Load balancing
VPC → Private network
Subnets → Network segmentation
Security Groups → Instance/resource traffic rules
Route Tables → Routing
NAT Gateway → Private outbound Internet access
RDS → Database
```

We'll learn each of these deeply in the AWS phase.

---

## 38. Public vs Private Subnet

This is a classic interview question.

A subnet is commonly considered **public** when its route table provides a route to an Internet Gateway and resources can be assigned appropriate public addressing.

Example:

```text
Internet
   ↓
Internet Gateway
   ↓
Public Subnet
   ↓
ALB
```

Private subnet:

```text
Internet
   X
   │
Private Subnet
   │
EC2
```

For outbound Internet access, a private subnet can use:

```text
EC2
 ↓
NAT Gateway
 ↓
Internet Gateway
 ↓
Internet
```

The key idea:

> **Private doesn't mean "no Internet access."**

It usually means:

> **No direct inbound Internet route/addressability.**

---

## 39. Security Groups vs NACLs

You'll need this for AWS interviews.

#### Security Group

Think:

> Firewall associated with a resource such as an EC2 network interface.

Important characteristics include:

- stateful
- rules for allowed traffic
- commonly associated with EC2

#### Network ACL

Think:

> Firewall rules applied at the subnet boundary.

Important characteristics include:

- stateless
- inbound and outbound rules
- subnet-level

A useful simplified comparison:

```text
Security Group
     ↓
Resource level
Stateful

NACL
     ↓
Subnet level
Stateless
```

We'll go deeper in the VPC response.

---

## 40. Why This Matters for Your Backend

Suppose your application is:

```text
Node.js → PostgreSQL
```

You don't want:

```text
Internet
   ↓
PostgreSQL
```

Instead:

```text
Internet
   ↓
ALB
   ↓
Node.js
   ↓
PostgreSQL
```

And your network rules might conceptually be:

```text
Internet
  ↓
ALB :443        ✅

Internet
  ↓
EC2 :3000       ❌

Internet
  ↓
RDS :5432       ❌

EC2
  ↓
RDS :5432       ✅
```

This is a major security principle:

> **Only expose what actually needs to be exposed.**

---

## 41. Common Networking Troubleshooting

Suppose:

```text
Node.js application
running on port 3000
```

but:

```text
curl http://server-ip:3000
```

fails.

Possible causes:

```text
Application not running
        ↓
Wrong port
        ↓
Process listening only on localhost
        ↓
Linux firewall
        ↓
AWS Security Group
        ↓
NACL
        ↓
Route table
        ↓
Load balancer
        ↓
DNS
```

This is why networking knowledge is so valuable.

---

## 42. Practical Commands

You'll actually use these.

#### IP

```bash
ip addr
```

#### Routing

```bash
ip route
```

#### Listening ports

```bash
ss -tulpn
```

#### DNS

```bash
nslookup example.com
```

```bash
dig example.com
```

#### Connectivity

```bash
ping example.com
```

#### HTTP

```bash
curl -I https://example.com
```

#### Detailed HTTP request

```bash
curl -v https://example.com
```

`-v` is particularly useful when debugging HTTP/TLS behavior.

---

## 43. A Practical Node.js Example

Let's say:

```typescript
import express from "express";

const app = express();

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

app.listen(3000, "0.0.0.0", () => {
  console.log("Server listening on port 3000");
});
```

Notice:

```text
0.0.0.0
```

This matters.

If your application listens only on:

```text
127.0.0.1
```

it may only accept connections originating from the same machine.

Listening on:

```text
0.0.0.0
```

means it listens on all IPv4 interfaces on that machine, subject to firewall/network rules.

This is a very common deployment issue.

---

## 44. End-to-End Mental Model

You should now be able to visualize:

```text
                     USER
                       │
                       │ HTTPS
                       ↓
                     DNS
                       │
                       ↓
                  Public IP
                       │
                       ↓
                Load Balancer
                       │
                       ↓
                  VPC Routing
                       │
                ┌──────┴──────┐
                ↓             ↓
              EC2           EC2
                │             │
                └──────┬──────┘
                       ↓
                    Backend
                       │
                       ↓
                    RDS
```

And underneath:

```text
DNS
 ↓
IP
 ↓
TCP/UDP
 ↓
Port
 ↓
Routing
 ↓
Firewall
 ↓
Application
```

That's the foundation for almost everything coming later.

---

## 45. 🔥 Interview-Level Scenarios

Don't just memorize definitions. Learn to reason.

#### Scenario 1

> Your Node.js application is running on port 3000, but users cannot access it from the Internet. What do you check?

Think:

```text
Is Node running?
       ↓
Is it listening?
       ↓
0.0.0.0 vs localhost?
       ↓
Correct port?
       ↓
Linux firewall?
       ↓
Security Group?
       ↓
NACL?
       ↓
Route?
       ↓
Load Balancer?
       ↓
DNS?
```

---

#### Scenario 2

> EC2 can access the Internet, but the Internet cannot directly initiate connections to EC2.

Possible architecture:

```text
Internet
   X
   │
Private EC2
   │
NAT Gateway
   │
Internet
```

This is a common private-subnet design.

---

#### Scenario 3

> Your API returns 502 Bad Gateway.

Don't immediately blame the API.

A 502 can indicate that a gateway/proxy/load balancer received an invalid response from an upstream server.

Investigate:

```text
Load Balancer
     ↓
Target health
     ↓
Target port
     ↓
Security Group
     ↓
Application
     ↓
Application logs
```

---

## 46. What You Need to Remember

Don't try to memorize every detail.

Your core mental model should be:

```text
MAC
 ↓
Local network

IP
 ↓
Network-level addressing

Port
 ↓
Application endpoint

TCP/UDP
 ↓
Transport

DNS
 ↓
Name → address information

HTTP
 ↓
Application communication

TLS
 ↓
Security

Router
 ↓
Path selection

NAT
 ↓
Address translation

Firewall
 ↓
Traffic control

Load Balancer
 ↓
Traffic distribution
```

---

## 🧪 Practical Assignment

If you have Linux/WSL, run:

```bash
ip addr
```

Identify your IP addresses.

Then:

```bash
ip route
```

Identify your default route.

Then:

```bash
ss -tulpn
```

Look at listening ports.

Then:

```bash
nslookup google.com
```

Observe DNS resolution.

Then:

```bash
curl -v https://example.com
```

Pay attention to:

```text
DNS resolution
connection
TLS handshake
HTTP request
HTTP response
```

Finally, start a Node server:

```typescript
import express from "express";

const app = express();

app.get("/", (req, res) => {
  res.send("Hello Cloud!");
});

app.listen(3000, "0.0.0.0", () => {
  console.log("Listening on 3000");
});
```

Then:

```bash
curl http://localhost:3000
```

You should get:

```text
Hello Cloud!
```

Then inspect:

```bash
ss -tulpn | grep 3000
```

You've just connected:

**Node.js → TCP → port → Linux network interface.**

---

## 🎯 Chapter 4 Checkpoint

You should now be able to explain:

1. What is an IP address?
2. Private vs public IP?
3. What is a port?
4. TCP vs UDP?
5. What happens during a TCP handshake?
6. What is DNS?
7. A vs AAAA vs CNAME?
8. What is CIDR?
9. Why is `/16` larger than `/24`?
10. What is NAT?
11. What is a reverse proxy?
12. What does a load balancer do?
13. What is HTTPS?
14. What does TLS provide?
15. Public vs private subnet?
16. Security Group vs NACL?
17. Why might an application listening on `localhost:3000` not be reachable externally?
18. Trace `https://api.example.com/users` from browser → backend → database.

If you can reason through **#18**, you've understood the most important part of this response.
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 3: Bash & Linux Automation](ch03-bash-automation.md) · [Chapter 5: Git & GitHub Deep Dive](ch05-git-github.md) → · [Revision sheet](../../revision/ch04-revision.md)
