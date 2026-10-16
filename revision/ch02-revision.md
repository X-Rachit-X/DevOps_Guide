# Chapter 2 — Revision Sheet: Linux for Cloud & DevOps

> Supplements [the full chapter](../docs/01-foundations/ch02-linux.md).

## Core ideas

- **Linux = kernel**; Ubuntu/Debian/Fedora/Amazon Linux/RHEL are *distributions* (kernel + utilities + packages).
- **Layers:** Hardware → Kernel (process, memory, network, filesystem, drivers) → System utilities (bash, ls, ps, systemctl) → Applications (Node.js, Docker, Nginx). Applications talk to the kernel (system calls), never directly to hardware.
- **You → Terminal → Bash (shell) → Linux.**
- A cloud server is just a Linux computer: `AWS → EC2 → Ubuntu → Node/Docker/Nginx → your app`.

## Filesystem map (know these cold)

| Path | Purpose |
|---|---|
| `/` | Root of the whole filesystem tree |
| `/root` | Home directory of the *root user* (not the same as `/`) |
| `/home/<user>` | Normal users' home dirs |
| `/etc` | System configuration (`/etc/ssh`, `/etc/nginx`, `/etc/hosts`) |
| `/var` | Frequently changing data; `/var/log` = logs |
| `/tmp` | Temporary files |
| `/usr` | User-space programs and libraries |
| `/opt` | Optional/additional software |
| `/dev` | Device files |
| `/proc` | Virtual FS exposing process + kernel info (used in troubleshooting) |

## Permissions

```text
-rwxr-xr--   → owner rwx | group r-x | others r--
r=4  w=2  x=1        755 = rwx r-x r-x        600 = rw- --- ---
```

- `chmod +x script.sh` makes it executable; `chmod 755 script.sh` then `./script.sh`.
- `chown ubuntu:ubuntu app.log` sets owner:group. Classic prod bug: "app runs but can't write to directory" → ownership/permissions.

## Command groups (cheat sheet)

| Area | Commands |
|---|---|
| Navigation | `pwd`, `ls -la`, `cd`, `cd ..`, `cd ~` |
| Files | `touch`, `cat`, `cp`, `mv`, `rm`, `rm -r`, `mkdir`, `>` overwrite, `>>` append |
| Search | `grep "ERROR" f`, `grep -i`, `grep -r "DATABASE_URL" .`, `find /var/log -name "*.log"` |
| Permissions | `chmod`, `chown` |
| Processes | `ps aux`, `top`/`htop`, `kill PID` (SIGTERM), `kill -9 PID` (SIGKILL) |
| Resources | `free -h` (memory), `df -h` (disk), `du -sh *` (sizes), `lscpu` |
| Services (systemd) | `systemctl status/start/stop/restart/enable`, `journalctl -u svc -f` |
| Networking | `ip addr`, `ip route`, `ping`, `curl`, `ss -tulpn` |
| Users | `whoami` (current user), `id` (uid, gid, groups — *added explanation*), `sudo` |
| Packages | `apt update`, `apt install`, `apt remove` (Ubuntu/Debian); `dnf` (RHEL/Fedora); `pacman` (Arch) |
| Remote | `ssh -i my-key.pem ubuntu@<ip>` |
| Environment | `export PORT=3000`, `echo $PORT`, `env` (lists all environment variables — *added explanation*); Node: `process.env.PORT` |

## Signals (important for Docker/Kubernetes graceful shutdown)

| Signal | Meaning | How |
|---|---|---|
| SIGTERM | Polite request to terminate; app can clean up | `kill PID` |
| SIGKILL | Force kill; no cleanup | `kill -9 PID` |
| SIGINT | Interrupt | `Ctrl+C` |

## Traps

- `/` ≠ `/root`.
- `>` **overwrites**, `>>` appends.
- `rm -rf` — understand a command before running it on a server.
- `.env` files are hidden (`ls -la`); never commit secrets to Git or bake them into Docker images.
- Do **not** answer "API is down" with "restart it". Diagnose.

## The systematic debugging order (memorise)

1. Is the process running? `ps aux | grep node`
2. Is the port listening? `ss -tulpn | grep 3000`
3. Logs: `journalctl -u my-api` / `tail -f application.log`
4. Test locally: `curl http://localhost:3000`
5. App configuration
6. CPU / memory / disk (`top`, `free -h`, `df -h`)
7. Firewall / Security Group
8. Load balancer
9. DNS

## Interview questions — with answers

> The chapter lists these without answers. Answers below are **added for revision** (not source text).

1. **What is Linux?** An operating-system *kernel*; distributions bundle it with utilities to make a usable OS.
2. **Process vs program?** A program is a file on disk (e.g. the `node` binary / `server.js`); a process is a running instance of it with a PID, memory, and state. Running `node server.js` twice creates two processes of one program.
3. **PID?** Unique process ID the kernel assigns; used to signal/kill it. PID 1 is the init process (systemd on modern systems).
4. **`chmod 755`?** Owner rwx, group r-x, others r-x.
5. **`sudo`?** Run a command with elevated privileges, subject to the user's sudo permissions.
6. **`/` vs `/root`?** Filesystem root vs home directory of the root user.
7. **Environment variable?** Named key/value in a process's environment, used for configuration (PORT, DATABASE_URL); inherited by child processes.
8. **Which process uses a port?** `sudo ss -tulpn | grep :3000` (shows PID/program; `sudo` needed to see other users' processes).
9. **App running but users can't connect?** Use the 9-step order above (listening address — `127.0.0.1` vs `0.0.0.0` — security group, LB, DNS).
10. **Disk full?** `df -h` to find the full filesystem, `du -sh *` down the tree to find big directories, check `/var/log`, then clean/rotate.
11. **Node process keeps crashing?** Process → logs → resources (OOM) → configuration (env vars) → dependencies.

<!-- NAV -->

---

← [Sheet 1](ch01-revision.md) · [Full chapter 2](../docs/01-foundations/ch02-linux.md) · [All revision material](README.md) · [Sheet 3](ch03-revision.md) →
