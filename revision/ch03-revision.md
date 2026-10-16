# Chapter 3 — Revision Sheet: Bash & Linux Automation

> Supplements [the full chapter](../docs/01-foundations/ch03-bash-automation.md).

## Big idea

Ch2 = *operate* Linux manually. Ch3 = *automate* it. Manual `git pull; npm ci; npm test; build; restart; check health` → `./deploy.sh` → later, CI/CD.

## Syntax cheat sheet

| Concept | Syntax | Trap |
|---|---|---|
| Shebang | `#!/bin/bash` or `#!/usr/bin/env bash` | Tells the OS which interpreter runs the script; `chmod +x` then `./script.sh` |
| Variable | `name="Rachit"` | **No spaces around `=`** |
| Use variable | `"$name"` | Quote it |
| Env var | `export NODE_ENV=production` | Only *exported* vars are inherited by child processes |
| Command substitution | `today=$(date)` | |
| Input | `read name` | |
| Arguments | `$1 $2 $3`, `$#` count, `$@` all, `$0` script name | |
| Exit status / PID | `$?` last exit status, `$$` current PID | `$?` is overwritten by the *next* command |
| If | `if [ "$ENV" = "production" ]; then … else … fi` | **Spaces inside `[ ]` matter** |
| Numeric tests | `-eq -ne -gt -ge -lt -le` | Strings use `=`; numbers use these |
| File tests | `-f` file, `-d` dir, `-e` exists, `-r -w -x` | |
| For | `for s in a b c; do … done`, `for f in *.log` | |
| While | `while [ "$c" -le 5 ]; do c=$((c+1)); done` | |
| Arithmetic | `$((a + b))` with `+ - * / %` | Use Python for serious math |
| Function | `f() { echo "Hello $1"; }` | Inside a function `$1` is the function's argument |
| Pipe | `ps aux \| grep node` | stdout of left → stdin of right |
| Redirect | `>` overwrite, `>>` append, `2>` stderr, `> out.log 2>&1` both | |
| `&&` / `\|\|` | `a && b` run b if a succeeded; `a \|\| b` run b if a failed | `npm test && npm run build` |
| Exit | `exit 0` success, `exit 1` failure | CI/CD reads this |

## Standard streams

`stdin` (input) · `stdout` (normal output) · `stderr` (errors). `cat existing.txt` → stdout; `cat missing.txt` → stderr.
`command > output.log 2>&1` = stdout to file, stderr to the same place.

## Exit codes (VERY important)

`0` = success, non-zero = failure. `true; echo $?` → 0; `false; echo $?` → 1. CI/CD, Docker, Kubernetes and deploy scripts all decide success/failure from exit codes.
Cleaner than checking `$?`: `if npm test; then … else … exit 1; fi`.

## Defensive scripting

```bash
set -euo pipefail
```

| Flag | Effect |
|---|---|
| `-e` | Exit when a command returns non-zero (has subtleties — not a replacement for explicit error handling) |
| `-u` | Error on unset variables |
| `-o pipefail` | A pipeline fails if an earlier command in it fails (otherwise only the last command's status counts) |

## Cron

```text
┌ minute (0-59) ┌ hour (0-23) ┌ day of month (1-31) ┌ month (1-12) ┌ day of week (0-7)
*  *  *  *  *
0 2 * * *   backup.sh     → every day 02:00
0 * * * *                 → every hour
0 0 * * *                 → every day midnight
0 3 * * 0                 → every Sunday 03:00
```
Edit with `crontab -e`.

## Tools

`tar -cf a.tar dir/` (create) · `tar -czf a.tar.gz dir/` (gzip) · `tar -xzf a.tar.gz` (extract) · `head` · `tail` / `tail -f` · `wc -l` · `sort | uniq` · `xargs -n1` · plus `sed awk cut tr`.

## Bash vs Python

Bash: Linux commands, files, processes, deploy scripts, config, pipelines. Python: complex logic, data processing, APIs, big automation, parsing, ML. Don't write a 1,000-line Bash system.

## Patterns worth memorising

- **Deploy script:** `set -euo pipefail` → `git pull` → `npm ci` → `npm run build` → `npm test` → `systemctl restart my-api` → `curl -fs …/health`. (Production: test *before* taking down the live version and have a rollback.)
- **Health check:** `curl -fs http://localhost:3000/health > /dev/null` → exit 0 healthy / exit 1 unhealthy — same idea as Docker HEALTHCHECK, Kubernetes probes, load-balancer checks.
- **Backup:** `TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")`; `tar -czf "$BACKUP/logs_$TIMESTAMP.tar.gz" "$SOURCE"`; schedule via cron.

## Traps / precision notes

- `ps aux | grep node | wc -l` **also counts the `grep node` process itself** (off by one). Idioms: `pgrep -c node`, or `grep [n]ode`. *(Added precision — see [Corrections](../CORRECTIONS.md).)*
- `uniq` only removes **adjacent** duplicates, hence `sort | uniq` (or `sort -u`).
- `cat file | grep X` works, but `grep X file` is cleaner.
- Prefer `read -r` in real scripts (avoids backslash mangling) — *added tip*.
- `$@` vs `$*`: quote `"$@"` to preserve each argument — *added tip*.

## Interview questions with answers (answers added)

1. **Bash?** "Bourne Again SHell": an interactive shell and a scripting language.
2. **Shell?** A program that reads your commands and asks the OS to run them.
3. **Bash vs Linux?** Linux is the kernel/OS; Bash is one program (shell) that runs on it.
4. **Shebang?** `#!/bin/bash` first line; names the interpreter the OS should use.
5. **Env var?** Key/value in a process environment; exported ones are inherited by children.
6. **`$1`?** First positional argument. **`$@`?** All arguments. **`$?`** Exit status of the previous command.
9. **Pipe `ps aux | grep node`?** Shell starts both processes concurrently, connects `ps`'s stdout to `grep`'s stdin; grep prints only lines matching `node`.
10. **`>` vs `>>`?** Overwrite vs append.
11. **stdin/stdout/stderr?** Input / normal output / error output streams.
12. **`2>&1`?** Redirect stderr (fd 2) to wherever stdout (fd 1) currently goes.
13. **`chmod +x`?** Adds execute permission so `./script.sh` can run.
14. **Why exit codes in CI/CD?** Pipelines decide pass/fail and whether to continue from the status code.
15. **`set -euo pipefail`?** Stop on errors, error on undefined variables, fail pipelines if any stage fails.
- **Scenario — command #3 fails, #4–6 corrupt the deployment:** `set -e` (or explicit `if`/`||` checks with `exit 1`), validate before destructive steps, fail fast, and add rollback.

<!-- NAV -->

---

← [Sheet 2](ch02-revision.md) · [Full chapter 3](../docs/01-foundations/ch03-bash-automation.md) · [All revision material](README.md) · [Sheet 4](ch04-revision.md) →
