# Chapter 2 — Linux for Cloud & DevOps

> **Source:** Response 2 of the original conversation (`source-archive/src-02.txt`, lines 7–1589) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch02-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

Linux is one of the most important foundations for Cloud and DevOps.

Why?

Because eventually you'll encounter things like:

```text
AWS EC2
   ↓
Linux Server
   ↓
Docker
   ↓
Node.js
   ↓
Your Application
```

If something breaks, you need to understand the Linux system underneath it.

Our goal here is not to become a Linux kernel developer. It's to become someone who can **comfortably operate, understand, deploy, and troubleshoot applications on Linux servers.**

---

## 1. What is Linux?

Linux is an **operating-system kernel**.

Strictly speaking:

> Linux itself is the kernel; distributions such as Ubuntu, Debian, Fedora, and Amazon Linux package the kernel with utilities and software to form a usable operating system.

For practical purposes, you'll often hear people simply say "Linux OS."

Examples:

- Ubuntu
- Debian
- Fedora
- Arch
- Amazon Linux
- RHEL

For our Cloud/DevOps learning, **Ubuntu-style Linux commands** will be the primary examples because they're widely encountered and easy to transfer to other distributions.

---

## 2. Why Linux is so important in Cloud

A cloud server is still a computer.

For example, an AWS EC2 instance might look like:

```text
AWS
 │
 └── EC2
      │
      └── Ubuntu Linux
           │
           ├── Node.js
           ├── Docker
           ├── Nginx
           └── Your application
```

When you SSH into that server:

```bash
ssh ubuntu@<server-ip>
```

you're interacting with Linux.

You'll need to know:

```text
Files
Processes
Users
Permissions
Networking
Services
Logs
Packages
Environment variables
Resources
```

---

## 3. Linux Architecture

A simplified view:

```text
┌───────────────────────────────┐
│         Applications          │
│ Node.js | Docker | Nginx | ...│
├───────────────────────────────┤
│        System Utilities       │
│ bash | ls | ps | systemctl    │
├───────────────────────────────┤
│            Kernel             │
│ Process | Memory | Network    │
│ Filesystem | Drivers          │
├───────────────────────────────┤
│           Hardware            │
│ CPU | RAM | Disk | Network    │
└───────────────────────────────┘
```

The **kernel** is the core component.

It manages things such as:

- CPU
- memory
- processes
- filesystems
- networking
- hardware
- system calls

Applications don't normally directly control hardware.

They interact with the kernel.

---

## 4. Terminal and Shell

When you open something like:

```text
Terminal
```

you interact with a **shell**.

A common shell is:

```text
bash
```

For example:

```bash
ls
```

You type a command into Bash.

Conceptually:

```text
You
 ↓
Terminal
 ↓
Bash
 ↓
Linux system
```

---

## 5. Your First Commands

Let's start with navigation.

#### `pwd`

Print working directory:

```bash
pwd
```

Example:

```text
/home/rachit
```

Meaning:

> "Where am I?"

---

#### `ls`

List files:

```bash
ls
```

More useful:

```bash
ls -la
```

- `-l` → detailed listing
- `-a` → include hidden files

---

#### `cd`

Change directory:

```bash
cd /home
```

Go up:

```bash
cd ..
```

Go home:

```bash
cd ~
```

---

## 6. Linux Filesystem

Linux has a tree-like filesystem.

```text
/
├── bin
├── boot
├── dev
├── etc
├── home
│   └── rachit
├── opt
├── proc
├── root
├── tmp
├── usr
└── var
```

`/` is the root of the filesystem.

Don't confuse:

```text
/
```

with:

```text
/root
```

`/` = filesystem root.

`/root` = home directory of the root user.

---

## 7. Important Directories

You don't need to memorize every Linux directory, but these matter for DevOps.

#### `/home`

Regular users' home directories.

```text
/home/rachit
```

#### `/root`

Root user's home directory.

#### `/etc`

System configuration.

For example:

```text
/etc/ssh/
/etc/nginx/
/etc/hosts
```

#### `/var`

Frequently changing data.

Important:

```text
/var/log
```

contains logs.

#### `/tmp`

Temporary files.

#### `/usr`

Many user-space programs and libraries.

#### `/opt`

Often used for optional/additional software.

#### `/dev`

Device files.

#### `/proc`

Virtual filesystem exposing information about processes and the kernel.

We'll use `/proc` later for troubleshooting.

---

## 8. Creating Files and Directories

Create a directory:

```bash
mkdir project
```

Enter it:

```bash
cd project
```

Create a file:

```bash
touch app.txt
```

Write:

```bash
echo "Hello Linux" > app.txt
```

Read:

```bash
cat app.txt
```

Output:

```text
Hello Linux
```

---

## 9. `>` vs `>>`

This is a small thing that becomes very useful.

#### `>`

Overwrite:

```bash
echo "Hello" > file.txt
```

Then:

```bash
echo "World" > file.txt
```

The file becomes:

```text
World
```

#### `>>`

Append:

```bash
echo "Hello" > file.txt
echo "World" >> file.txt
```

Now:

```text
Hello
World
```

This becomes useful when working with logs.

---

## 10. Copy, Move, Delete

#### Copy

```bash
cp app.txt backup.txt
```

#### Move/rename

```bash
mv app.txt application.txt
```

#### Delete

```bash
rm application.txt
```

Delete directory recursively:

```bash
rm -r project
```

Be careful with:

```bash
rm -rf
```

On a Linux server, blindly running something like:

```bash
rm -rf /
```

can be catastrophic.

The important lesson is:

> Linux gives you powerful control, so commands should be understood before being executed.

---

## 11. Absolute vs Relative Paths

This is important.

#### Absolute path

Starts from `/`.

```bash
/home/rachit/project/app.js
```

#### Relative path

Relative to your current directory.

If you're here:

```text
/home/rachit
```

then:

```bash
project/app.js
```

means:

```text
/home/rachit/project/app.js
```

---

## 12. Hidden Files

Linux files beginning with `.` are hidden.

Example:

```text
.env
.gitignore
.ssh
```

Run:

```bash
ls -la
```

to see them.

This is especially important because `.env` files often contain configuration/secrets.

**Never casually commit secrets to Git.**

---

## 13. Users

Linux is multi-user.

For example:

```text
root
ubuntu
deploy
developer
```

Each user has an identity.

Check your current user:

```bash
whoami
```

Example:

```text
ubuntu
```

---

## 14. Root User

`root` is the superuser.

It has extremely broad privileges.

For example:

```bash
sudo apt update
```

`sudo` means:

> Execute this command with elevated privileges, subject to the user's sudo permissions.

You might see:

```bash
sudo systemctl restart nginx
```

because ordinary users shouldn't necessarily be allowed to control system services.

---

## 15. Why permissions exist

Imagine every application could modify every file.

That would be dangerous.

Linux uses permissions to control access.

Example:

```text
-rwxr-xr--
```

This looks confusing initially, but let's break it down.

---

## 16. Linux Permissions

Three categories:

```text
User
Group
Others
```

And three basic permissions:

```text
r = read
w = write
x = execute
```

For example:

```text
-rwxr-xr--
```

Break it down:

```text
Owner   Group   Others
rwx     r-x     r--
```

Therefore:

Owner:

```text
read + write + execute
```

Group:

```text
read + execute
```

Others:

```text
read
```

---

## 17. Numeric Permissions

You may see:

```bash
chmod 755 script.sh
```

Numbers correspond to:

```text
r = 4
w = 2
x = 1
```

Therefore:

```text
7 = 4 + 2 + 1 = rwx
5 = 4 + 1     = r-x
5 = 4 + 1     = r-x
```

So:

```text
755
```

means:

```text
Owner  → rwx
Group  → r-x
Others → r-x
```

---

## 18. `chmod`

Change permissions:

```bash
chmod +x script.sh
```

Now the script can be executed.

Or:

```bash
chmod 755 script.sh
```

Then:

```bash
./script.sh
```

---

## 19. `chown`

Change ownership.

```bash
sudo chown ubuntu:ubuntu app.log
```

Meaning:

```text
Owner = ubuntu
Group = ubuntu
```

This becomes important when deploying applications.

A classic production problem:

> "The application is running but can't write to this directory."

Often, permissions or ownership are involved.

---

## 20. Processes

A **process** is a running program.

If you execute:

```bash
node server.js
```

Linux creates a process for Node.js.

You can see processes:

```bash
ps
```

More commonly:

```bash
ps aux
```

You'll see things such as:

```text
USER   PID   %CPU   %MEM   COMMAND
root     1    ...    ...   ...
ubuntu 1234   ...    ...   node server.js
```

---

## 21. PID

Every process has a **Process ID (PID)**.

Example:

```text
node server.js
PID = 1234
```

You can terminate it:

```bash
kill 1234
```

Normally, `kill` sends a signal asking the process to terminate gracefully.

---

## 22. Signals

Linux processes communicate/control behavior through signals.

Common ones:

```text
SIGTERM
SIGKILL
SIGINT
```

#### SIGTERM

Request termination.

```bash
kill PID
```

Generally gives the application a chance to clean up.

#### SIGKILL

Forcefully terminate.

```bash
kill -9 PID
```

The process doesn't get the same opportunity to gracefully shut down.

#### SIGINT

Interrupt, commonly generated by:

```text
Ctrl + C
```

This distinction becomes important with **Docker and Kubernetes graceful shutdown**, which we'll revisit.

---

## 23. `top`

See resource usage:

```bash
top
```

You can monitor:

```text
CPU
Memory
Processes
Load
```

A more interactive alternative commonly found on systems is:

```bash
htop
```

if installed.

---

## 24. CPU and Memory

Important commands:

```bash
free -h
```

Memory.

```bash
df -h
```

Disk filesystem usage.

```bash
du -sh *
```

Approximate size of items in the current directory.

CPU information:

```bash
lscpu
```

These are useful when diagnosing:

> "Why is my server slow?"

---

## 25. Services

Servers run background services.

Examples:

```text
nginx
ssh
docker
postgresql
```

Modern Linux systems commonly use **systemd** to manage services.

Check service status:

```bash
systemctl status nginx
```

Start:

```bash
sudo systemctl start nginx
```

Stop:

```bash
sudo systemctl stop nginx
```

Restart:

```bash
sudo systemctl restart nginx
```

Enable at boot:

```bash
sudo systemctl enable nginx
```

---

## 26. Logs

When something doesn't work:

> **Check the logs.**

This is one of the most important operational habits you'll develop.

System logs often live under:

```text
/var/log
```

For systemd services:

```bash
journalctl
```

For a specific service:

```bash
journalctl -u nginx
```

Follow logs live:

```bash
journalctl -u nginx -f
```

`-f` means follow.

This is similar to:

```bash
tail -f application.log
```

---

## 27. Searching Through Files

Suppose you have a huge log:

```text
application.log
```

Find lines containing `ERROR`:

```bash
grep "ERROR" application.log
```

Case-insensitive:

```bash
grep -i "error" application.log
```

Search recursively:

```bash
grep -r "DATABASE_URL" .
```

This is incredibly useful when debugging.

---

## 28. Finding Files

```bash
find /var/log -name "*.log"
```

This searches for files matching the pattern.

Example:

```bash
find . -name "Dockerfile"
```

---

## 29. Environment Variables

Applications frequently depend on environment variables.

Example:

```bash
export PORT=3000
```

Check:

```bash
echo $PORT
```

Output:

```text
3000
```

Node.js can access it:

```typescript
const port = process.env.PORT || 3000;

console.log(`Server running on ${port}`);
```

This is extremely important because we'll use environment variables everywhere:

```text
Node.js
Docker
AWS
CI/CD
Kubernetes
```

---

## 30. Why `.env` exists

Locally, you might have:

```text
PORT=3000
DATABASE_URL=...
REDIS_URL=...
```

in:

```text
.env
```

Your application can load those values.

But **production secrets should not simply be committed into Git or baked into Docker images**.

Later we'll learn proper secret management with:

- AWS Secrets Manager
- Parameter Store
- Kubernetes Secrets
- CI/CD secrets

---

## 31. Package Management

On Ubuntu/Debian:

```bash
sudo apt update
```

Update package metadata.

Install:

```bash
sudo apt install nginx
```

Remove:

```bash
sudo apt remove nginx
```

Different distributions use different package managers.

For example:

```text
Ubuntu/Debian → apt
RHEL/Fedora   → dnf
Arch          → pacman
```

You don't need to memorize every package manager.

Understand the concept.

---

## 32. SSH — Extremely Important

Suppose AWS gives you an EC2 instance:

```text
Public IP:
13.xxx.xxx.xxx
```

You need to access it.

SSH:

```bash
ssh -i my-key.pem ubuntu@13.xxx.xxx.xxx
```

Conceptually:

```text
Your Laptop
     │
     │ SSH
     ↓
Internet
     │
     ↓
EC2
     │
     ↓
Linux Shell
```

Now you're operating the remote machine.

We'll go much deeper into SSH and networking later.

---

## 33. Linux Networking Commands

A few you'll start using:

#### Check IP addresses

```bash
ip addr
```

#### Check routes

```bash
ip route
```

#### Test connectivity

```bash
ping google.com
```

#### Make HTTP request

```bash
curl https://example.com
```

#### Check listening ports

```bash
ss -tulpn
```

This one is extremely useful.

Suppose your Node application is supposed to run on:

```text
localhost:3000
```

Run:

```bash
ss -tulpn | grep 3000
```

You can investigate whether something is listening on that port.

We'll cover networking properly in **[Chapter 4](ch04-networking.md)**.

---

## 34. A Real Debugging Example

Imagine you deployed your Node.js application.

User says:

> "The API is down."

Don't immediately restart everything.

Think systematically.

#### Step 1 — Is the process running?

```bash
ps aux | grep node
```

#### Step 2 — Is the port listening?

```bash
ss -tulpn | grep 3000
```

#### Step 3 — Check logs

```bash
journalctl -u my-api
```

or:

```bash
tail -f application.log
```

#### Step 4 — Test locally

```bash
curl http://localhost:3000
```

#### Step 5 — Check firewall/security/networking

Later we'll investigate:

```text
Security Group
Firewall
Load Balancer
DNS
```

This is the kind of **reasoning** I want you to develop.

---

## 35. Linux Command Cheat Sheet

Keep this mental map:

```text
Navigation
──────────
pwd
ls
cd

Files
─────
touch
cat
cp
mv
rm
mkdir

Search
──────
grep
find

Permissions
───────────
chmod
chown

Processes
─────────
ps
top
kill

Resources
─────────
free
df
du

Services
────────
systemctl
journalctl

Networking
──────────
ip
ss
ping
curl

Users
─────
whoami
id
sudo

Packages
────────
apt

Remote
──────
ssh

Environment
───────────
env
export
echo
```

Don't try to memorize all of these today.

**Use them repeatedly and they'll become natural.**

---

## 36. Mini Practical Exercise 🛠️

If you have a Linux machine, WSL, Ubuntu VM, or cloud instance, do this yourself.

#### Part A — Files

```bash
mkdir cloud-lab
cd cloud-lab

mkdir app logs config

touch app/server.log
echo "Server started" > app/server.log
echo "Request received" >> app/server.log

cat app/server.log
```

#### Part B — Search

```bash
grep "Server" app/server.log
```

#### Part C — Permissions

```bash
chmod 600 app/server.log
ls -l app/server.log
```

Think:

> Who can now read/write this file?

#### Part D — Processes

Run:

```bash
sleep 300 &
```

Find it:

```bash
ps aux | grep sleep
```

Then terminate it:

```bash
kill <PID>
```

#### Part E — Resources

Run:

```bash
free -h
df -h
```

#### Part F — Networking

Run:

```bash
ip addr
ip route
ss -tulpn
curl https://example.com
```

Don't worry if some output differs between systems.

---

## 🧠 Interview Questions You Should Now Be Able to Approach

Don't memorize answers yet. Try reasoning about them.

#### Beginner

**1. What is Linux?**

**2. What is the difference between a process and a program?**

**3. What is PID?**

**4. What does `chmod 755` mean?**

**5. What is `sudo`?**

**6. What is the difference between `/` and `/root`?**

**7. What is an environment variable?**

---

#### Intermediate

**8. How would you find which process is using a port?**

Hint:

```bash
ss
```

**9. Your application is running but users can't connect. How would you debug it?**

**10. Your server's disk is full. What would you investigate?**

Possible starting points:

```bash
df -h
du -sh
```

**11. Your Node.js process keeps crashing. What would you check?**

Think:

```text
Process
 ↓
Logs
 ↓
Resources
 ↓
Configuration
 ↓
Dependencies
```

---

#### Interview scenario

> **You SSH into an EC2 instance and users report that your API is down. What do you do?**

A strong engineer shouldn't immediately say:

> "Restart the server."

Instead:

```text
1. Check process
       ↓
2. Check logs
       ↓
3. Check port
       ↓
4. curl localhost
       ↓
5. Check application configuration
       ↓
6. Check CPU/memory/disk
       ↓
7. Check firewall/security group
       ↓
8. Check load balancer
       ↓
9. Check DNS
```

We'll become much better at this systematic debugging approach as the course progresses.

---

## 🔥 What You Learned in Chapter 2

You now have the first layer of practical Linux knowledge:

```text
Linux
 │
 ├── Filesystem
 │
 ├── Users
 │
 ├── Permissions
 │
 ├── Processes
 │
 ├── Services
 │
 ├── Logs
 │
 ├── Environment
 │
 ├── Packages
 │
 ├── SSH
 │
 └── Basic networking
```
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 1: Cloud + DevOps Fundamentals](ch01-cloud-devops-fundamentals.md) · [Chapter 3: Bash & Linux Automation](ch03-bash-automation.md) → · [Revision sheet](../../revision/ch02-revision.md)
