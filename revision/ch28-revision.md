# Chapter 28 — Revision Sheet: Ansible — Configuration Management & Automation

> Supplements [the full chapter](../docs/06-iac-config/ch28-ansible.md). One line: **Terraform provisions infrastructure; Ansible configures machines; Docker packages applications; Kubernetes orchestrates containers; Helm packages Kubernetes apps; ArgoCD deploys them with GitOps.**

## The problem and the definition

Terraform creates 10 EC2 instances; each needs Node.js, Git, Nginx, environment configuration, system users, application files, a systemd service, security configuration. SSH-ing into each is painful and error-prone. **Ansible** = *an agentless automation and configuration-management tool used to configure systems, deploy applications and execute repeatable administrative tasks.* Keywords: automation, configuration management, agentless, idempotent, YAML, SSH.

**Architecture:** Control Node →(SSH)→ Managed Nodes (Server 1/2/3). Control node = where you run `ansible` / `ansible-playbook` (laptop or CI server). **Agentless:** managed Linux hosts generally need no permanent Ansible agent; Ansible connects over SSH and runs modules.

## Comparisons

| | |
|---|---|
| **Ansible vs Terraform** | Terraform provisions (VPC, EC2, RDS, S3, EKS); Ansible configures (install Node.js, configure Nginx, create users, deploy app, start service). Terraform → create EC2 → Ansible → configure EC2 |
| **Ansible vs Docker** | Docker packages app + dependencies into an image; Ansible configures servers (install/configure software) |
| **Ansible vs Kubernetes** | Kubernetes manages containers/Pods/Deployments/Services/scaling/self-healing; Ansible manages servers/software/configuration/app deployment/automation. Kubernetes often removes the need for Ansible for container workloads |
| **Ansible vs Bash** | `ssh serverN "sudo apt install nginx"` ×N gets messy; Ansible expresses "all web servers should have Nginx installed" **declaratively** |
| **Ansible vs Helm templates** | Helm: Kubernetes templates; Ansible: server/application configuration templates (Jinja2) |

## Inventory, modules, idempotency

```ini
[web]
server1 ansible_host=192.168.1.10
server2 ansible_host=192.168.1.11
[db]
server3 ansible_host=192.168.1.12
```
Inventory = which machines to manage; groups (`web`, `db`) let you target categories. `ansible all -i inventory.ini -m ping` → `server1 | SUCCESS => {"ping": "pong"}` (**not ICMP** — it means Ansible connected and ran its ping module).
- **Modules** are the building blocks: `package`, `apt`, `yum`, `copy`, `file`, `service`, `systemd`, `user`, `command`, `shell`, `git`, `template`.
- **Idempotency:** `apt: name=nginx state=present` — installs if missing, does nothing if present. Run 1 → `changed`, runs 2–3 → `ok/unchanged`. Safe to rerun.
- Install: `sudo apt update && sudo apt install ansible`; `ansible --version`.

## Playbook

```yaml
---
- name: Configure web servers
  hosts: web
  become: true                 # privilege escalation (≈ sudo)
  tasks:
    - name: Install nginx
      apt: { name: nginx, state: present }
    - name: Start nginx
      service: { name: nginx, state: started, enabled: true }
```
Run: `ansible-playbook -i inventory.ini site.yml`. `name` = human-readable; `hosts: web` = target group; `become: true`; `tasks:` list.

| Feature | Example |
|---|---|
| Multiple packages | `apt: name: [git, nginx]  state: present  update_cache: true` |
| `copy` | `copy: { src: nginx.conf, dest: /etc/nginx/nginx.conf }` |
| `file` (files/dirs/permissions/ownership) | `file: { path: /opt/my-api, state: directory, owner: app, group: app, mode: '0755' }` |
| `user` | `user: { name: app, state: present, shell: /bin/bash }` |
| `systemd` | `systemd: { name: my-api, state: started, enabled: true }` |
| **Templates (Jinja2)** | `templates/app.conf.j2` → `PORT={{ app_port }}`; `template: { src: app.conf.j2, dest: /etc/my-api/app.conf }` |
| **Variables** | `vars: { app_port: 3000 }` → `PORT=3000` |
| **Handlers** | `notify: Reload nginx` + `handlers: - name: Reload nginx  service: {name: nginx, state: reloaded}` — runs only if the config actually changed |
| **Conditions** | `when: ansible_os_family == "Debian"` (using facts) |
| **Loops** | `loop: [git, curl, nginx]` with `name: "{{ item }}"` |
| **Tags** | `tags: [nginx]` → `ansible-playbook site.yml --tags nginx` |
| **Facts** | gathered info (OS, CPU, memory, network, IP, filesystem); `- debug: var=ansible_distribution` → `Ubuntu` |
| **Roles** | `roles/nginx/{tasks/main.yml, templates, handlers, defaults, vars}`, `roles/nodejs/...`; `roles: [nginx, nodejs]` — reuse, organisation, testing, maintenance (instead of a 1000-line playbook) |
| **Galaxy** | ecosystem of reusable roles/content |
| **`command` vs `shell`** | `command` runs without a shell (`node --version`); `shell` allows pipelines (`echo hello \| grep hello`). **Prefer dedicated modules** (`apt` not `shell: apt install nginx`) — they understand desired state and are more idempotent |
| **Vault** | Ansible Vault encrypts sensitive variables/files (encrypted secrets → Vault → playbook); in the cloud consider Secrets Manager / HashiCorp Vault |

## Execution, dry run, troubleshooting

Internally: read inventory → connect over SSH → gather facts → execute modules → compare desired/current state → make required changes → return result: `ok`, `changed`, `failed`, `skipped`. First install → `changed=1`; rerun → `ok`.
- **Dry run:** `ansible-playbook -i inventory.ini site.yml --check`; `--diff` shows configuration differences.
- **Debug:** `ssh user@server`; `ansible-inventory -i inventory.ini --list`; `ansible all -i inventory.ini -m ping`; `-vvv`; check become/sudo/user/SSH key.
- **Common problems:** SSH failure (wrong host/user/key, security group, network); permission denied (sudo/become, file permissions); module failure (wrong package/OS/missing dependency); config keeps changing → non-idempotent task.
- **Security:** least privilege, SSH key authentication, encrypted secrets, Vault, Secrets Manager, limited sudo, network restrictions, secure inventory; never commit `AWS_ACCESS_KEY_ID/SECRET` to a public repo.

## Where it fits

- **Classic:** Terraform → EC2 → Ansible (install Node.js/Nginx, configure app, start service) → application. Ansible can also configure Docker, Nginx, system settings, monitoring, users on EC2 that run containers. **Modern:** Terraform → EKS → Helm → ArgoCD → Kubernetes → Pods — much less Ansible (hence lower priority).
- **CI/CD:** invoked from Jenkins, GitHub Actions or GitLab CI (e.g. Actions → tests → build → Ansible → EC2; Jenkins → Ansible → servers).
- Good use cases: configuring an EC2 fleet, installing packages, Nginx, managing Linux servers, traditional app deployment, system services, bootstrapping, repetitive administration. Less necessary for Kubernetes deployment, orchestration, managed cloud infrastructure.

| Technology | Main job |
|---|---|
| Git | Version control |
| GitHub Actions / Jenkins | CI/CD automation |
| Docker | Containerisation |
| Terraform | Infrastructure provisioning |
| **Ansible** | **Configuration management** |
| Kubernetes | Container orchestration |
| Helm | Kubernetes packaging |
| ArgoCD | GitOps deployment |
| AWS | Cloud infrastructure |

## Interview answers (10)

Ansible (agentless automation/config management); why agentless (no persistent agent, SSH + remote modules); inventory (hosts and groups); playbook (YAML desired automation for selected hosts); idempotency; Terraform vs Ansible; Ansible vs Docker; Ansible vs Kubernetes; roles (reusable structure of tasks, variables, templates, handlers); modules over shell (understand desired state → reliable, idempotent).

## Added notes / corrections (not in source)

- ⚠ **`environment` is a reserved Ansible keyword** (it sets environment variables for plays/tasks). The chapter's `vars: environment: production` / `ENVIRONMENT={{ environment }}` example should use a different name such as `app_env`. See [Corrections](../CORRECTIONS.md).
- "Agentless" still requires **Python** on Linux managed nodes (modules run via Python) and working SSH; Windows uses WinRM. Agent-based tools (Chef, Puppet) install a persistent agent.
- Inventory needs connection details: `ansible_user`, `ansible_ssh_private_key_file`; `ansible.cfg` sets defaults. With Terraform-created EC2s use **dynamic inventory** (e.g. the AWS EC2 inventory plugin) rather than hard-coded IPs.
- Useful commands: `ansible-playbook --syntax-check`, `--limit web1`, `-e key=value`, `ansible-lint`; Vault: `ansible-vault encrypt|edit|view file.yml`, run with `--ask-vault-pass`. Check mode skips tasks that cannot predict changes (e.g. `command`/`shell`).
- Handlers run **once at the end of the play** (use `meta: flush_handlers` to run them earlier). `state: present` ensures installed; `state: latest` upgrades.
- Ubuntu's default `nodejs` package can be old — real playbooks usually add the NodeSource repository. `copy` is fine for small trees; the `synchronize` module is better for large directories. Prefer fully qualified module names (`ansible.builtin.apt`) in modern playbooks. Installing via `pip/pipx` gives newer versions than the distro package.

<!-- NAV -->

---

← [Sheet 27](ch27-revision.md) · [Full chapter 28](../docs/06-iac-config/ch28-ansible.md) · [All revision material](README.md) · [Sheet 29](ch29-revision.md) →
