# Chapter 28 — Ansible: Configuration Management & Automation

> **Source:** Response 28 of the original conversation (`source-archive/src-28.txt`, lines 1–1811) · **Part II — Advanced extension (Responses 25–36)**  
> **Study aids:** [Revision sheet](../../revision/ch28-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

We've now covered **Terraform → Kubernetes → Helm → GitOps → ArgoCD → Jenkins**.

Ansible fills a different part of the DevOps picture:

> **Terraform creates/provisions infrastructure. Ansible configures machines and applications running on that infrastructure.**

For your SWE/backend target, you don't need to become an Ansible specialist. You need to understand it well enough to **use, explain, troubleshoot, and compare it with Terraform/Docker/Kubernetes**.

---

## 1. The Problem Ansible Solves

Imagine Terraform creates 10 EC2 instances:

```text
Terraform
   ↓
AWS
   ↓
EC2
EC2
EC2
...
EC2
```

Now every server needs:

```text
Node.js
Git
Nginx
environment configuration
system users
application files
systemd service
security configuration
```

Doing this manually:

```bash
ssh server1
ssh server2
ssh server3
...
```

is painful and error-prone.

Ansible lets you automate it:

```text
Ansible
   ↓
EC2 #1
EC2 #2
EC2 #3
...
```

with one desired configuration.

---

## 2. What Is Ansible?

An interview-ready definition:

> **Ansible is an agentless automation and configuration-management tool used to configure systems, deploy applications, and execute repeatable administrative tasks.**

Important words:

```text
automation
configuration management
agentless
idempotent
YAML
SSH
```

---

## 3. Ansible Architecture

Basic architecture:

```text
                    Ansible
                       │
                 Control Node
                       │
                      SSH
          ┌────────────┼────────────┐
          ↓            ↓            ↓
       Server 1     Server 2     Server 3
```

Unlike many management systems, the managed machines generally don't need a permanent Ansible agent installed.

For Linux hosts, Ansible commonly uses:

```text
SSH
```

---

## 4. Control Node vs Managed Node

#### Control Node

The machine where you run:

```bash
ansible
ansible-playbook
```

#### Managed Nodes

The machines being configured.

Example:

```text
Laptop / CI server
       │
       │ SSH
       ↓
   EC2 instances
```

---

## 5. Why "Agentless"?

With Ansible:

```text
Control Node
     │
     │ SSH
     ↓
Managed Server
```

You generally don't need to install an Ansible agent on the managed Linux server.

This makes the architecture relatively simple.

---

## 6. Ansible vs Terraform

This is one of the most important comparisons.

#### Terraform

Primarily:

```text
Provision infrastructure
```

Example:

```text
Create:
VPC
EC2
RDS
S3
EKS
```

#### Ansible

Primarily:

```text
Configure machines
```

Example:

```text
Install Node.js
Configure Nginx
Create users
Deploy application
Start service
```

Think:

```text
Terraform
   ↓
Create EC2
   ↓
Ansible
   ↓
Configure EC2
```

---

## 7. Ansible vs Docker

Docker packages applications.

```text
Docker
 ↓
Application
 +
Dependencies
 ↓
Container image
```

Ansible configures machines/applications.

```text
Ansible
 ↓
Server
 ↓
Install/configure software
```

They solve different problems.

---

## 8. Ansible vs Kubernetes

Kubernetes manages:

```text
containers
pods
deployments
services
scaling
self-healing
```

Ansible manages/configures:

```text
servers
software
configuration
application deployment
automation
```

You can use both, although Kubernetes often eliminates the need for Ansible for many container-workload operations.

---

## 9. Ansible vs Bash

You already know Bash.

You could write:

```bash
ssh server1 "sudo apt install nginx"
ssh server2 "sudo apt install nginx"
ssh server3 "sudo apt install nginx"
```

But this becomes messy.

Ansible lets you express:

```text
All web servers should have Nginx installed.
```

declaratively.

That's much easier to maintain.

---

## 10. Installing Ansible

On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ansible
```

Verify:

```bash
ansible --version
```

You can also use Python/pip or other OS-specific installation methods.

For learning, you can run Ansible from:

```text
your Linux machine
```

against:

```text
another Linux VM/EC2
```

or use containers for a controlled lab.

---

## 11. The Ansible Inventory

An inventory tells Ansible:

> **Which machines should I manage?**

Example:

```ini
[web]
server1 ansible_host=192.168.1.10
server2 ansible_host=192.168.1.11

[db]
server3 ansible_host=192.168.1.12
```

Groups:

```text
web
db
```

are useful because you can target specific categories of servers.

---

## 12. Inventory Mental Model

```text
Inventory
   │
   ├── web
   │    ├── server1
   │    └── server2
   │
   └── db
        └── server3
```

Then you can say:

```text
Configure all web servers.
```

instead of listing each server individually.

---

## 13. Ansible Ping

A famous first test:

```bash
ansible all -i inventory.ini -m ping
```

You may get:

```text
server1 | SUCCESS => {
    "ping": "pong"
}
```

This doesn't mean ICMP ping.

It means:

> Ansible successfully connected to the host and executed the Ansible ping module.

---

## 14. Ansible Modules

Ansible is built around modules.

Examples:

```text
package
apt
yum
copy
file
service
systemd
user
command
shell
git
template
```

For example:

```yaml
- name: Install nginx
  apt:
    name: nginx
    state: present
```

You're saying:

> Ensure Nginx is installed.

---

## 15. Idempotency

This is one of the most important Ansible concepts.

Suppose you write:

```yaml
- name: Install nginx
  apt:
    name: nginx
    state: present
```

If Nginx isn't installed:

```text
→ install it
```

If it's already installed:

```text
→ do nothing
```

That's **idempotency**.

You can run the playbook repeatedly without repeatedly changing the system unnecessarily.

---

## 16. Why Idempotency Matters

Without idempotency:

```text
Run 1 → install
Run 2 → install again
Run 3 → install again
```

Bad.

With idempotency:

```text
Run 1 → changed
Run 2 → unchanged
Run 3 → unchanged
```

Much safer.

---

## 17. Playbooks

A Playbook is a YAML file containing automation instructions.

Example:

```yaml
---
- name: Configure web servers

  hosts: web

  become: true

  tasks:

    - name: Install nginx
      apt:
        name: nginx
        state: present

    - name: Start nginx
      service:
        name: nginx
        state: started
        enabled: true
```

Save as:

```text
site.yml
```

Run:

```bash
ansible-playbook -i inventory.ini site.yml
```

---

## 18. Understanding the Playbook

Let's break it down.

```yaml
- name: Configure web servers
```

Human-readable name.

```yaml
hosts: web
```

Target:

```text
[web]
```

from your inventory.

```yaml
become: true
```

Use privilege escalation when needed.

Usually equivalent to:

```bash
sudo
```

conceptually.

---

## 19. Tasks

Each task describes something Ansible should do.

Example:

```yaml
tasks:

  - name: Install nginx
    apt:
      name: nginx
      state: present
```

Another:

```yaml
- name: Start nginx
  service:
    name: nginx
    state: started
```

---

## 20. Practical Example — Configure Node.js Server

Suppose you have:

```text
EC2 instance
```

and want:

```text
Node.js
Git
Nginx
```

installed.

Playbook:

```yaml
---
- name: Configure Node.js server

  hosts: web
  become: true

  tasks:

    - name: Install required packages
      apt:
        name:
          - git
          - nginx
        state: present
        update_cache: true

    - name: Install Node.js
      apt:
        name: nodejs
        state: present

    - name: Start nginx
      service:
        name: nginx
        state: started
        enabled: true
```

Now:

```bash
ansible-playbook -i inventory.ini server.yml
```

Ansible applies the configuration.

---

## 21. `copy`

You can copy a file:

```yaml
- name: Copy nginx configuration
  copy:
    src: nginx.conf
    dest: /etc/nginx/nginx.conf
```

This is useful for configuration management.

---

## 22. `file`

You can manage:

```text
files
directories
permissions
ownership
```

Example:

```yaml
- name: Create application directory
  file:
    path: /opt/my-api
    state: directory
    owner: app
    group: app
    mode: '0755'
```

---

## 23. `user`

Create users:

```yaml
- name: Create application user
  user:
    name: app
    state: present
    shell: /bin/bash
```

This is much safer than manually running user-management commands across dozens of servers.

---

## 24. `systemd`

You can manage services:

```yaml
- name: Start API
  systemd:
    name: my-api
    state: started
    enabled: true
```

This connects to the Linux/systemd knowledge from [Chapter 2](../01-foundations/ch02-linux.md).

---

## 25. Templates

This is extremely useful.

Suppose your configuration depends on environment variables.

Create:

```text
templates/app.conf.j2
```

Example:

```jinja2
PORT={{ app_port }}
ENVIRONMENT={{ environment }}
```

Then:

```yaml
- name: Configure application
  template:
    src: app.conf.j2
    dest: /etc/my-api/app.conf
```

Ansible renders the template using variables.

---

## 26. Variables

Example:

```yaml
vars:
  app_port: 3000
  environment: production
```

Then:

```jinja2
PORT={{ app_port }}
```

becomes:

```text
PORT=3000
```

This is similar in spirit to the templating you've seen in Helm.

---

## 27. Helm vs Ansible Templates

You may notice:

```text
Helm
→ Kubernetes templates

Ansible
→ server/application configuration templates
```

Both use templating ideas, but their purposes are different.

---

## 28. Handlers

Suppose you modify Nginx configuration.

You need to restart/reload Nginx.

Instead of restarting every time, use a handler.

```yaml
tasks:

  - name: Update nginx config
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: Reload nginx

handlers:

  - name: Reload nginx
    service:
      name: nginx
      state: reloaded
```

If the configuration changes:

```text
→ handler runs
```

If nothing changes:

```text
→ no reload
```

Again, this is idempotent behavior.

---

## 29. Conditions

You can conditionally run tasks.

Example:

```yaml
- name: Install package on Debian
  apt:
    name: nginx
    state: present
  when: ansible_os_family == "Debian"
```

You can use facts about the machine.

---

## 30. Loops

Suppose you need multiple packages:

```yaml
- name: Install packages
  apt:
    name: "{{ item }}"
    state: present
  loop:
    - git
    - curl
    - nginx
```

This avoids repeating tasks.

---

## 31. Tags

You can tag tasks:

```yaml
- name: Install nginx
  apt:
    name: nginx
    state: present
  tags:
    - nginx
```

Then:

```bash
ansible-playbook site.yml --tags nginx
```

Only relevant tasks execute.

Useful in larger playbooks.

---

## 32. Roles

As projects grow, one giant playbook becomes messy.

Roles provide structure.

Example:

```text
roles/
├── nginx/
│   ├── tasks/
│   │   └── main.yml
│   ├── templates/
│   ├── handlers/
│   ├── defaults/
│   └── vars/
│
└── nodejs/
    ├── tasks/
    ├── templates/
    └── handlers/
```

Then:

```text
site.yml
```

can use:

```yaml
roles:
  - nginx
  - nodejs
```

---

## 33. Why Roles Matter

Instead of:

```text
1000-line playbook
```

you organize:

```text
Node.js role
Nginx role
Monitoring role
Security role
```

This improves:

```text
reuse
organization
testing
maintenance
```

---

## 34. Ansible Galaxy

Ansible has an ecosystem for reusable roles/content.

Conceptually:

```text
Ansible Galaxy
       ↓
Reusable roles
       ↓
Your project
```

You don't need to memorize specific Galaxy roles.

Understand the concept.

---

## 35. Ansible Facts

Ansible can gather information about machines:

```text
OS
CPU
memory
network
IP
filesystem
```

These are called:

> **Facts**

For example:

```yaml
- debug:
    var: ansible_distribution
```

might tell you:

```text
Ubuntu
```

This allows automation to adapt to different hosts.

---

## 36. `command` vs `shell`

Important distinction.

#### command

```yaml
- name: Check version
  command: node --version
```

Executes a command without invoking a shell in the usual way.

#### shell

```yaml
- name: Run shell command
  shell: echo hello | grep hello
```

Uses shell features such as pipelines.

Prefer dedicated Ansible modules when possible.

Instead of:

```yaml
shell: apt install nginx
```

prefer:

```yaml
apt:
  name: nginx
  state: present
```

Why?

Because modules understand desired state and are generally more idempotent.

---

## 37. Ansible Vault

You should **not** put secrets directly into:

```yaml
password: my-secret
```

Ansible provides:

```text
Ansible Vault
```

for encrypting sensitive variables/files.

Conceptually:

```text
Encrypted secrets
       ↓
Ansible Vault
       ↓
Playbook
```

However, in a cloud environment you might instead use:

```text
AWS Secrets Manager
HashiCorp Vault
external secret systems
```

depending on architecture.

---

## 38. Ansible + AWS

Imagine Terraform creates:

```text
3 EC2 instances
```

Then:

```text
Terraform
   ↓
EC2
   ↓
Ansible
   ↓
Install Node.js
Install Nginx
Configure application
Start service
```

This is a classic combination.

---

## 39. Terraform + Ansible

A simplified lifecycle:

```text
                     Infrastructure
                          │
                      Terraform
                          │
              ┌───────────┼───────────┐
              ↓           ↓           ↓
            EC2         EC2         EC2
              │           │           │
              └───────────┼───────────┘
                          ↓
                       Ansible
                          ↓
                 Server configuration
                          ↓
                    Application
```

Terraform answers:

> **What infrastructure should exist?**

Ansible answers:

> **How should those machines be configured?**

---

## 40. Where Does Docker Fit?

You might instead have:

```text
Terraform
 ↓
EC2
 ↓
Docker
 ↓
Node.js container
```

In that case Ansible might configure:

```text
Docker
Nginx
system settings
monitoring
users
```

Then Docker handles application packaging.

---

## 41. Where Does Kubernetes Fit?

Modern cloud-native architecture might be:

```text
Terraform
 ↓
EKS
 ↓
Helm
 ↓
Kubernetes
```

In this scenario, you might use **much less Ansible** for application deployment.

That's why Ansible is lower priority for you.

---

## 42. Ansible + CI/CD

Ansible can be invoked from:

```text
Jenkins
GitHub Actions
GitLab CI
```

For example:

```text
GitHub
 ↓
GitHub Actions
 ↓
Tests
 ↓
Build
 ↓
Ansible
 ↓
EC2
```

Or:

```text
Jenkins
 ↓
Ansible
 ↓
Servers
```

---

## 43. Complete Example

Suppose you have:

```text
2 EC2 servers
```

Inventory:

```ini
[web]
web1 ansible_host=10.0.1.10
web2 ansible_host=10.0.1.11
```

Playbook:

```yaml
---
- name: Configure API servers

  hosts: web
  become: true

  vars:
    app_port: 3000

  tasks:

    - name: Install required packages
      apt:
        name:
          - nginx
          - git
          - nodejs
        state: present
        update_cache: true

    - name: Create application directory
      file:
        path: /opt/my-api
        state: directory
        mode: '0755'

    - name: Copy application
      copy:
        src: ./dist/
        dest: /opt/my-api/

    - name: Start nginx
      service:
        name: nginx
        state: started
        enabled: true
```

Run:

```bash
ansible-playbook -i inventory.ini deploy.yml
```

Now both servers receive the configuration.

---

## 44. What Happens Internally?

Conceptually:

```text
ansible-playbook
       ↓
Read inventory
       ↓
Connect over SSH
       ↓
Gather facts
       ↓
Execute modules
       ↓
Compare desired/current state
       ↓
Make required changes
       ↓
Return result
```

Results often show:

```text
ok
changed
failed
skipped
```

---

## 45. `changed` vs `ok`

This is important.

If Ansible installs Nginx for the first time:

```text
changed=1
```

Run again:

```text
ok
```

because the desired state is already satisfied.

This is another demonstration of idempotency.

---

## 46. Ansible Dry Run

Use:

```bash
ansible-playbook \
  -i inventory.ini \
  site.yml \
  --check
```

This attempts a check-mode execution without applying many changes.

You can also use:

```bash
--diff
```

where supported to inspect configuration differences.

This is useful before making changes.

---

## 47. Ansible Troubleshooting

Suppose:

```text
web1 | FAILED
```

Check:

#### SSH

```bash
ssh user@server
```

#### Inventory

```bash
ansible-inventory -i inventory.ini --list
```

#### Connectivity

```bash
ansible all -i inventory.ini -m ping
```

#### Verbose output

```bash
ansible-playbook -i inventory.ini site.yml -vvv
```

#### Permissions

Check:

```text
become
sudo
user
SSH key
```

---

## 48. Common Ansible Problems

#### SSH failure

```text
wrong host
wrong user
wrong key
security group
network
```

#### Permission denied

```text
sudo/become
file permissions
```

#### Module failure

```text
wrong package
wrong OS
missing dependency
```

#### Configuration keeps changing

Likely:

```text
non-idempotent task
```

Investigate the task.

---

## 49. Ansible Security

Important principles:

```text
least privilege
SSH key authentication
encrypted secrets
Ansible Vault
Secrets Manager
limited sudo
network restrictions
secure inventory
```

Don't put:

```text
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

directly into a public repository.

---

## 50. Ansible Interview Questions

#### Q1. What is Ansible?

> An agentless automation/configuration-management tool used to configure systems, deploy applications, and automate repeatable operational tasks.

---

#### Q2. Why is Ansible called agentless?

> Managed Linux hosts generally don't require a persistent Ansible agent; Ansible commonly connects using SSH and executes modules remotely.

---

#### Q3. What is an inventory?

> A definition of the hosts and groups Ansible manages.

---

#### Q4. What is a playbook?

> A YAML file describing the desired automation tasks for selected hosts.

---

#### Q5. What is idempotency?

> Repeated execution produces the same desired state without unnecessarily repeating changes.

---

#### Q6. Terraform vs Ansible?

```text
Terraform
→ provision infrastructure

Ansible
→ configure/manage machines
```

---

#### Q7. Ansible vs Docker?

```text
Ansible
→ configuration/automation

Docker
→ application packaging/containerization
```

---

#### Q8. Ansible vs Kubernetes?

```text
Ansible
→ configuration and automation

Kubernetes
→ container orchestration
```

---

#### Q9. What are Ansible roles?

> A reusable structure for organizing tasks, variables, templates, handlers, and related automation.

---

#### Q10. Why prefer modules over shell commands?

Because modules generally understand the target system and desired state, making automation more reliable and idempotent.

---

## 51. Your Mental Model

This is the important part:

```text
             TERRAFORM
                 │
          "Create infrastructure"
                 │
                 ↓
              AWS EC2
                 │
                 ↓
              ANSIBLE
                 │
        "Configure the server"
                 │
       ┌─────────┼─────────┐
       ↓         ↓         ↓
    Node.js    Nginx     Users
       │
       ↓
    Application
```

Whereas with Kubernetes:

```text
Terraform
   ↓
EKS
   ↓
Helm
   ↓
ArgoCD
   ↓
Kubernetes
   ↓
Pods
```

Ansible isn't necessarily part of every modern Kubernetes architecture.

---

## 52. When Would You Actually Use Ansible?

#### Good use cases

```text
Configure EC2 fleet
Install packages
Configure Nginx
Manage Linux servers
Deploy traditional applications
Configure system services
Bootstrap machines
Automate repetitive administration
```

#### Less necessary

For:

```text
Kubernetes application deployment
container orchestration
managed cloud infrastructure
```

you often use:

```text
Terraform
Kubernetes
Helm
ArgoCD
```

instead.

---

## 53. Ansible vs Everything We've Learned

| Technology | Main job |
|---|---|
| Git | Version control |
| GitHub Actions | CI/CD automation |
| Jenkins | CI/CD automation |
| Docker | Containerization |
| Terraform | Infrastructure provisioning |
| Ansible | Configuration management |
| Kubernetes | Container orchestration |
| Helm | Kubernetes packaging |
| ArgoCD | GitOps deployment |
| AWS | Cloud infrastructure |

This table is worth knowing extremely well.

---

## 54. Final Practical Workflow

A traditional VM-based architecture:

```text
Git
 ↓
CI
 ↓
Build
 ↓
Terraform
 ↓
EC2
 ↓
Ansible
 ↓
Configure server
 ↓
Deploy application
 ↓
Nginx
 ↓
Application
```

A modern container/Kubernetes architecture:

```text
Git
 ↓
CI
 ↓
Docker
 ↓
ECR
 ↓
Terraform
 ↓
EKS
 ↓
Helm
 ↓
ArgoCD
 ↓
Kubernetes
 ↓
Pods
```

**Both are valid architectures.**

The second is more aligned with the cloud-native stack you've been building toward.

---

## 55. What You Need to Remember

For your SWE/backend target, know these deeply enough:

```text
✅ What Ansible is
✅ Why configuration management exists
✅ Agentless architecture
✅ Control node
✅ Managed nodes
✅ Inventory
✅ Modules
✅ Playbooks
✅ Tasks
✅ Idempotency
✅ Variables
✅ Templates
✅ Handlers
✅ Conditions
✅ Loops
✅ Roles
✅ Ansible Vault
✅ SSH
✅ Ansible + Terraform
✅ Ansible + Docker
✅ Ansible + CI/CD
✅ Troubleshooting
```

You **do not** need deep expertise in every Ansible module.

---

## 🎯 Chapter 28 Summary

Your DevOps tool map is becoming much clearer:

```text
                    DEVOPS
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   Infrastructure   Configuration   Application
        │              │              │
    Terraform       Ansible         Docker
        │              │              │
        └──────────────┼──────────────┘
                       ↓
                   Kubernetes
                       │
                    Helm
                       │
                   ArgoCD
                       │
                    GitOps
```

The key distinction:

> **Terraform provisions infrastructure. Ansible configures machines. Docker packages applications. Kubernetes orchestrates containers. Helm packages Kubernetes applications. ArgoCD deploys them using GitOps.**
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 27: Jenkins + Advanced CI/CD](../03-cicd-gitops/ch27-jenkins-advanced-cicd.md) · [Chapter 29: Kubernetes CRDs + Operators](../05-kubernetes/ch29-crds-operators.md) → · [Revision sheet](../../revision/ch28-revision.md)
