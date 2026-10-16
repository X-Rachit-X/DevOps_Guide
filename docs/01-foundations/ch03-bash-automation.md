# Chapter 3 — Bash & Linux Automation

> **Source:** Response 3 of the original conversation (`source-archive/src-03.txt`, lines 1–1862) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch03-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

In [Chapter 2](ch02-linux.md), we learned how to **operate Linux manually**.

Now we learn how to **automate Linux**.

This is where Bash becomes important.

The central idea is simple:

> If you find yourself repeatedly typing the same commands, you can probably turn them into a script.

For DevOps, this matters because servers often need repetitive operations such as:

```text
Install software
↓
Configure application
↓
Create directories
↓
Set permissions
↓
Start services
↓
Check health
↓
Collect logs
↓
Backup data
```

Instead of manually doing all of this, we automate it.

---

## 1. What is Bash?

**Bash = Bourne Again SHell.**

It's both:

1. A **shell** through which you interact with Linux.
2. A **scripting language** used to automate commands.

For example, manually:

```bash
mkdir app
cd app
touch server.log
echo "Application started" > server.log
```

Bash lets us put this into a script:

```bash
#!/bin/bash

mkdir app
cd app
touch server.log
echo "Application started" > server.log
```

Then execute the script.

```text
One command
    ↓
Multiple operations
    ↓
Automation
```

---

## 2. Your First Bash Script

Create:

```bash
nano hello.sh
```

Put:

```bash
#!/bin/bash

echo "Hello from Linux!"
echo "Starting DevOps journey..."
```

Save it.

Give execute permission:

```bash
chmod +x hello.sh
```

Run:

```bash
./hello.sh
```

Output:

```text
Hello from Linux!
Starting DevOps journey...
```

---

## 3. What is `#!/bin/bash`?

This is called a **shebang**.

```bash
#!/bin/bash
```

It tells the operating system which interpreter should execute the script.

Conceptually:

```text
hello.sh
   ↓
#!/bin/bash
   ↓
Bash
   ↓
Commands executed
```

You may also see:

```bash
#!/usr/bin/env bash
```

This finds Bash through the environment.

---

## 4. Variables

Bash variables are simple.

```bash
name="Rachit"
age=21
```

Important:

❌ Don't put spaces around `=`:

```bash
name = "Rachit"
```

That's incorrect Bash syntax.

Use:

```bash
name="Rachit"
```

Access the variable:

```bash
echo "$name"
```

Output:

```text
Rachit
```

---

## 5. Why `$`?

When defining:

```bash
name="Rachit"
```

`name` refers to the variable.

When accessing:

```bash
echo "$name"
```

`$name` means:

> Give me the value stored in `name`.

---

## 6. Environment Variables

This is particularly important for DevOps.

You can define:

```bash
export PORT=3000
```

Then:

```bash
echo "$PORT"
```

Output:

```text
3000
```

A child process can inherit exported environment variables.

For example:

```bash
export NODE_ENV=production
node server.js
```

Your Node.js application can access:

```typescript
console.log(process.env.NODE_ENV);
```

Output:

```text
production
```

This same idea appears in:

- Docker
- Kubernetes
- AWS
- CI/CD
- production applications

---

## 7. Command Substitution

Sometimes you want the output of one command inside another command.

Use:

```bash
$(command)
```

Example:

```bash
current_dir=$(pwd)

echo "$current_dir"
```

Or:

```bash
today=$(date)

echo "Today is $today"
```

Conceptually:

```text
date
 ↓
output
 ↓
store in variable
 ↓
use output
```

---

## 8. User Input

Use `read`.

```bash
#!/bin/bash

echo "Enter your name:"
read name

echo "Hello $name"
```

Run:

```bash
./hello.sh
```

Then:

```text
Enter your name:
Rachit

Hello Rachit
```

---

## 9. Script Arguments

This is very useful for automation.

Suppose:

```bash
./deploy.sh production
```

Inside the script:

```bash
echo "$1"
```

Output:

```text
production
```

`$1` = first argument.

Similarly:

```text
$1 → first argument
$2 → second
$3 → third
```

Example:

```bash
./deploy.sh production v2.4
```

Script:

```bash
echo "Environment: $1"
echo "Version: $2"
```

Output:

```text
Environment: production
Version: v2.4
```

---

## 10. Special Bash Variables

Some useful ones:

```text
$0       Script name
$1       First argument
$2       Second argument
$#       Number of arguments
$@       All arguments
$?       Exit status of previous command
$$       Current process ID
```

Example:

```bash
echo "Script: $0"
echo "Arguments: $#"
echo "All: $@"
```

---

## 11. Conditions

Bash supports `if`.

```bash
if [ "$ENV" = "production" ]; then
    echo "Production environment"
else
    echo "Non-production environment"
fi
```

Notice:

```bash
[ "$ENV" = "production" ]
```

The spaces matter.

---

## 12. Numeric Comparisons

For numbers:

```bash
if [ "$age" -ge 18 ]; then
    echo "Adult"
else
    echo "Minor"
fi
```

Common operators:

```text
-eq   equal
-ne   not equal
-gt   greater than
-ge   greater/equal
-lt   less than
-le   less/equal
```

Example:

```bash
if [ "$count" -gt 10 ]; then
    echo "High count"
fi
```

---

## 13. File Conditions

This is extremely useful in automation.

Check whether a file exists:

```bash
if [ -f "app.log" ]; then
    echo "Log exists"
fi
```

Directory:

```bash
if [ -d "logs" ]; then
    echo "Logs directory exists"
fi
```

Common checks:

```text
-f → regular file
-d → directory
-e → exists
-r → readable
-w → writable
-x → executable
```

---

## 14. Loops

Automation often requires repetition.

### `for`

```bash
for server in server1 server2 server3
do
    echo "Deploying to $server"
done
```

Output:

```text
Deploying to server1
Deploying to server2
Deploying to server3
```

---

## 15. Loop Through Files

```bash
for file in *.log
do
    echo "Processing $file"
done
```

If the directory contains:

```text
app.log
error.log
access.log
```

the loop processes each file.

---

## 16. `while` Loop

```bash
count=1

while [ "$count" -le 5 ]
do
    echo "Count: $count"
    count=$((count + 1))
done
```

Output:

```text
Count: 1
Count: 2
Count: 3
Count: 4
Count: 5
```

---

## 17. Arithmetic

Bash can perform basic arithmetic.

```bash
a=10
b=20

sum=$((a + b))

echo "$sum"
```

Output:

```text
30
```

You can use:

```bash
+
-
*
/
%
```

For serious numerical/data processing, you'd normally use another language such as Python rather than Bash.

Bash's strength is **system automation**, not complex computation.

---

## 18. Functions

Instead of repeating commands, create functions.

```bash
backup_logs() {
    echo "Backing up logs..."
    mkdir -p backup
    cp *.log backup/
}
```

Call it:

```bash
backup_logs
```

A better script:

```bash
#!/bin/bash

backup_logs() {
    mkdir -p backup
    cp *.log backup/
    echo "Backup complete"
}

backup_logs
```

---

## 19. Function Arguments

```bash
greet() {
    echo "Hello $1"
}

greet "Rachit"
```

Output:

```text
Hello Rachit
```

Inside the function:

```text
$1
```

refers to the function's first argument.

---

## 20. Pipes — One of the Most Important Bash Concepts

Consider:

```bash
ps aux
```

It produces lots of output.

Suppose you only want Node processes:

```bash
ps aux | grep node
```

The `|` is a **pipe**.

It takes the output of the command on the left and feeds it to the command on the right.

```text
ps aux
   ↓
output
   ↓
 pipe
   ↓
grep node
   ↓
filtered output
```

This is fundamental to Linux operations.

---

## 21. More Pipe Examples

Count Node processes:

```bash
ps aux | grep node | wc -l
```

Conceptually:

```text
ps
 ↓
grep
 ↓
wc
```

Another:

```bash
cat application.log | grep ERROR
```

Although for simple cases:

```bash
grep ERROR application.log
```

is cleaner.

---

## 22. Redirection

We've already seen:

```bash
echo "Hello" > file.txt
```

This redirects output into a file.

#### Standard output

```text
stdout
```

Normally goes to the terminal.

You can redirect:

```bash
command > output.txt
```

---

#### Append

```bash
command >> output.txt
```

---

#### Standard error

Errors are generally sent to:

```text
stderr
```

Redirect stderr:

```bash
command 2> error.log
```

---

#### Both stdout and stderr

A common form:

```bash
command > output.log 2>&1
```

Meaning:

```text
stdout → output.log
stderr → same place
```

This becomes useful in scripts and CI/CD.

---

## 23. Standard Streams

A process generally has:

```text
stdin
stdout
stderr
```

Think:

```text
           Process
          /   |    \
       stdin stdout stderr
```

#### stdin

Input.

#### stdout

Normal output.

#### stderr

Error output.

Example:

```bash
cat existing.txt
```

Normal result → stdout.

```bash
cat does-not-exist.txt
```

Error → stderr.

---

## 24. Exit Codes — VERY Important

Every Linux command returns an **exit status**.

Generally:

```text
0     → success
non-0 → failure
```

Check the previous command:

```bash
echo $?
```

Example:

```bash
true
echo $?
```

Output:

```text
0
```

And:

```bash
false
echo $?
```

Output:

```text
1
```

This becomes extremely important in:

- Bash scripts
- CI/CD
- Docker
- Kubernetes
- deployment automation

because automation needs to know:

> **Did the previous operation succeed?**

---

## 25. Using Exit Codes

Example:

```bash
npm test

if [ $? -eq 0 ]; then
    echo "Tests passed"
else
    echo "Tests failed"
fi
```

A cleaner approach:

```bash
if npm test; then
    echo "Tests passed"
else
    echo "Tests failed"
    exit 1
fi
```

---

## 26. `exit`

You can terminate a script:

```bash
exit 0
```

Success.

Or:

```bash
exit 1
```

Failure.

Example:

```bash
if [ ! -f "config.json" ]; then
    echo "Config missing"
    exit 1
fi
```

Now your CI/CD pipeline can detect the failure.

---

## 27. `&&` and `||`

These are very useful.

#### `&&`

Execute the second command only if the first succeeds.

```bash
mkdir app && cd app
```

Conceptually:

```text
mkdir succeeds?
     ↓
   YES
     ↓
  cd app
```

---

#### `||`

Execute the second command if the first fails.

```bash
cd app || echo "Directory doesn't exist"
```

---

#### Combining

```bash
npm test && npm run build
```

Meaning:

> Only build if tests succeed.

This is exactly the type of logic you'll encounter in CI/CD.

---

## 28. `set -e`

A useful Bash scripting option:

```bash
set -e
```

It tells Bash to generally exit when a command returns a non-zero status.

Example:

```bash
#!/bin/bash

set -e

npm ci
npm test
npm run build

echo "Build successful"
```

If `npm test` fails, the script stops rather than blindly continuing.

There are subtleties around `set -e`, so don't treat it as a universal replacement for explicit error handling.

---

## 29. `set -u`

Another useful option:

```bash
set -u
```

It makes Bash complain about unset variables.

Often you'll see:

```bash
set -euo pipefail
```

This is a common defensive pattern for Bash scripts.

We'll break down `pipefail` next.

---

## 30. `pipefail`

Suppose:

```bash
command1 | command2
```

A pipeline can hide failures depending on which command's exit status is considered.

With:

```bash
set -o pipefail
```

the pipeline can fail if an earlier command fails.

Therefore:

```bash
set -euo pipefail
```

is a common starting point for robust scripts.

You don't need to blindly put it everywhere, but you should understand what it does.

---

## 31. Practical Deployment Script

Now let's make something realistic.

Imagine you want to deploy a Node.js application.

```bash
#!/bin/bash

set -euo pipefail

echo "Starting deployment..."

git pull origin main

npm ci

npm run build

npm test

sudo systemctl restart my-api

echo "Deployment successful."
```

Conceptually:

```text
Git
 ↓
Pull latest code
 ↓
Install dependencies
 ↓
Build
 ↓
Test
 ↓
Restart application
```

If a step fails:

```text
Deployment stops
```

That's basic DevOps automation.

**In production, you'd usually make this safer than the simplified example above**—for example, test before taking down the current version and have a rollback strategy.

---

## 32. Health Check Script

Suppose your API should run on port `3000`.

We can automate checking it:

```bash
#!/bin/bash

if curl -fs http://localhost:3000/health > /dev/null; then
    echo "API is healthy"
    exit 0
else
    echo "API is unhealthy"
    exit 1
fi
```

Now another system can execute this script and determine whether:

```text
0 → healthy
1 → unhealthy
```

This idea eventually connects to:

- Docker health checks
- Kubernetes probes
- load balancers
- monitoring

---

## 33. Cron — Scheduling Automation

What if you want something to run automatically?

Linux has **cron**.

For example:

> Run a backup every day at 2 AM.

Edit your cron jobs:

```bash
crontab -e
```

A simplified entry:

```text
0 2 * * * /home/ubuntu/backup.sh
```

Meaning:

```text
minute = 0
hour   = 2
day    = *
month  = *
weekday= *
```

Therefore:

> Every day at 02:00.

---

## 34. Cron Format

The five fields:

```text
┌──── minute (0-59)
│ ┌── hour (0-23)
│ │ ┌── day of month (1-31)
│ │ │ ┌── month (1-12)
│ │ │ │ ┌── day of week (0-7)
│ │ │ │ │
* * * * *
```

Examples:

Every hour:

```text
0 * * * *
```

Every day at midnight:

```text
0 0 * * *
```

Every Sunday at 3 AM:

```text
0 3 * * 0
```

---

## 35. Real Backup Script

Let's combine what we've learned.

```bash
#!/bin/bash

set -euo pipefail

SOURCE="/var/log/myapp"
BACKUP="/var/backups/myapp"

mkdir -p "$BACKUP"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

tar -czf "$BACKUP/logs_$TIMESTAMP.tar.gz" "$SOURCE"

echo "Backup created successfully"
```

What's happening?

```text
SOURCE
 ↓
Application logs

TIMESTAMP
 ↓
Current date/time

tar
 ↓
Compress logs

BACKUP
 ↓
Store archive
```

Now this script could be scheduled using cron.

---

## 36. `tar`

You'll encounter `tar` often on Linux.

Create archive:

```bash
tar -cf archive.tar files/
```

Compressed gzip archive:

```bash
tar -czf archive.tar.gz files/
```

Extract:

```bash
tar -xzf archive.tar.gz
```

You don't need to memorize all flags right now.

Understand:

> `tar` packages files into an archive and can work with compression.

---

## 37. Useful Text Processing Tools

Bash becomes powerful because Linux provides many small utilities.

Important ones:

```text
grep
sed
awk
cut
sort
uniq
wc
head
tail
tr
xargs
```

We don't need a giant separate lesson for each, but you should understand their purpose.

#### `head`

```bash
head application.log
```

First lines.

#### `tail`

```bash
tail application.log
```

Last lines.

Live logs:

```bash
tail -f application.log
```

#### `wc`

```bash
wc -l application.log
```

Count lines.

---

## 38. `sort` and `uniq`

Example:

```bash
sort users.txt | uniq
```

Sort and remove adjacent duplicates.

Count unique values:

```bash
sort users.txt | uniq | wc -l
```

This style of composing small commands is one of Bash's biggest strengths.

---

## 39. `xargs`

Suppose you have:

```text
server1
server2
server3
```

and want to run a command against each.

`xargs` can turn input into command arguments.

Example:

```bash
cat servers.txt | xargs -n1 echo
```

You'll encounter more advanced uses later.

---

## 40. Bash vs Python

Since you know Python, this distinction is important.

#### Bash is excellent for:

```text
Linux commands
File operations
Process management
Deployment scripts
System configuration
Pipelines
Simple automation
```

#### Python is better for:

```text
Complex logic
Data processing
APIs
Large automation systems
Parsing complicated formats
Machine learning
```

Don't try to build a 1,000-line automation system in Bash just because Bash can technically do it.

Use the right tool.

---

## 41. A More Realistic DevOps Script

Here's a simplified deployment automation:

```bash
#!/bin/bash

set -euo pipefail

APP_DIR="/opt/my-api"

echo "Deploying application..."

cd "$APP_DIR"

echo "Pulling latest code..."
git pull origin main

echo "Installing dependencies..."
npm ci

echo "Building..."
npm run build

echo "Running tests..."
npm test

echo "Restarting service..."
sudo systemctl restart my-api

echo "Checking application..."

if curl -fs http://localhost:3000/health > /dev/null; then
    echo "Deployment successful"
else
    echo "Deployment failed: health check unsuccessful"
    exit 1
fi
```

Notice how many concepts from this response come together:

```text
Variables
↓
Commands
↓
Exit codes
↓
Conditions
↓
Environment
↓
Git
↓
Node.js
↓
systemd
↓
curl
↓
Automation
```

This is exactly why we're learning Bash.

---

## 42. The DevOps Mental Model

You should now see Bash as:

```text
Linux Commands
      ↓
Bash
      ↓
Automation
      ↓
Repeatable Operations
      ↓
DevOps
```

For example:

```text
Manual:

git pull
npm install
npm test
npm build
restart service
check health

             ↓

Automated:

./deploy.sh
```

And later:

```text
GitHub Push
     ↓
CI/CD
     ↓
Automated deployment
```

Bash is one of the building blocks underneath this.

---

## 43. What You Should Actually Memorize

Don't memorize every command.

Remember the **categories**:

```text
Variables
    ↓
$NAME

Input
    ↓
read

Arguments
    ↓
$1, $2, $@

Conditions
    ↓
if

Loops
    ↓
for / while

Functions
    ↓
function_name()

Output
    ↓
echo

Pipes
    ↓
|

Redirect
    ↓
> >> 2>

Exit status
    ↓
$?

Success/failure
    ↓
&& ||

Scheduling
    ↓
cron

Automation
    ↓
.sh scripts
```

Once you understand these, you can look up exact syntax when necessary.

---

## 🧪 Practical Assignment

Don't just read this one.

Create:

```text
devops-lab/
├── scripts/
├── logs/
├── backups/
└── config/
```

Then create:

```text
scripts/system-check.sh
```

It should:

#### 1. Print the hostname

```bash
hostname
```

#### 2. Print current date

```bash
date
```

#### 3. Print memory usage

```bash
free -h
```

#### 4. Print disk usage

```bash
df -h
```

#### 5. Check whether Docker is running

Use:

```bash
systemctl is-active docker
```

#### 6. Write the result to a log

Something like:

```text
2026-09-18 11:30
Hostname: ...
Docker: active
Disk: ...
```

#### 7. Return an appropriate exit code

If Docker isn't running:

```bash
exit 1
```

Otherwise:

```bash
exit 0
```

---

## 🎯 Interview Questions

Try answering these yourself.

#### Basic

1. What is Bash?
2. What is a shell?
3. What is the difference between Bash and Linux?
4. What is a shebang?
5. What is an environment variable?
6. What is `$1`?
7. What is `$@`?
8. What does `$?` represent?

#### Intermediate

9. What is a pipe?

```bash
ps aux | grep node
```

Explain exactly what happens.

10. What's the difference between:

```bash
>
>>
```

11. What are stdin, stdout, and stderr?

12. What does:

```bash
2>&1
```

mean?

13. What does:

```bash
chmod +x script.sh
```

do?

14. Why are exit codes important in CI/CD?

15. What does:

```bash
set -euo pipefail
```

generally accomplish?

#### Scenario

> You have a deployment script with 6 commands. Command #3 fails, but commands #4–6 continue executing and corrupt the deployment. How would you design the script to prevent that?

You should now be thinking about:

```text
exit codes
↓
error handling
↓
set -e
↓
explicit conditions
↓
rollback
```

---

## 🧠 Chapter 2 vs Chapter 3

You've now covered:

#### Chapter 2

**Operate Linux**

```text
Files
Users
Permissions
Processes
Services
Logs
SSH
Resources
Basic networking
```

#### Chapter 3

**Automate Linux**

```text
Bash
Variables
Environment
Arguments
Conditions
Loops
Functions
Pipes
Redirection
Exit codes
Error handling
Text processing
Cron
Deployment scripts
Health checks
Backups
```

So the progression is:

```text
                    LINUX
                      │
          ┌───────────┴───────────┐
          ↓                       ↓
      Manual                    Automated
          │                       │
     Commands                  Bash
          │                       │
     Processes                 Scripts
          │                       │
      Services                Cron
          │                       │
       Logs                   CI/CD
```
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 2: Linux for Cloud & DevOps](ch02-linux.md) · [Chapter 4: Networking for Cloud & DevOps](ch04-networking.md) → · [Revision sheet](../../revision/ch03-revision.md)
