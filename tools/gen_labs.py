"""Generate exercises/labs.md: index of source labs + clearly-labelled editorial labs."""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from registry import CHAPTERS, github_slug, strip_emoji

ROOT = Path(__file__).resolve().parent.parent
PAT = re.compile(r"(practical|\blab\b|exercise|hands-on|mini project|challenge|^project$)", re.I)
SKIP = re.compile(r"(availability|best practice|practice environment|in practice|capstone)", re.I)

# Editorial labs (NOT in the source) for chapters that have no source lab.
EDITORIAL = {
 1: ["Draw the request path of a web app on a napkin: user → DNS → LB → app → DB. Mark which parts scale horizontally and which are stateful.",
     "Compute allowed downtime per month for 99.9% and 99.99%; then compute the availability of two 99.9% services in series."],
 3: ["Write `backup.sh` with `set -euo pipefail`, a `trap` cleanup, argument validation and a log function; make it fail fast on an unset variable.",
     "Write a cron entry that runs it daily at 02:00 and appends output to a log."],
 4: ["With `dig`, `curl -v`, `ss -tulpn` and `traceroute`, trace a real HTTPS request and label DNS, TCP, TLS and HTTP phases.",
     "Compute the address count and range for 10.0.0.0/16 split into /24 subnets across 2 AZs."],
 6: ["Create a GitHub Actions workflow: checkout → setup-node → `npm ci` → lint → test → build, with a matrix of two Node versions and dependency caching."],
 15: ["Create an SQS queue with a DLQ (maxReceiveCount 3) and a consumer that is idempotent; send a poison message and watch it land in the DLQ."],
 17: ["Create a CloudWatch alarm on 5xx rate with an SNS notification; then find the corresponding API call in CloudTrail."],
 22: ["Instrument a small Node API with prom-client (RED metrics); scrape with Prometheus; chart p95 in Grafana; write an alert on error ratio."],
 23: ["Take the production checklist and score your own project against it; list the five biggest gaps."],
 24: ["Time yourself answering the Chapter 24 scenario questions aloud in 2 minutes each, using the Prevent → Detect → Contain → Recover → Learn frame."],
 28: ["Write an inventory + playbook that installs nginx, templates a config and restarts via a handler; run it twice and confirm the second run reports `changed=0`."],
 29: ["Define a small CRD and create a custom resource; observe that nothing happens without a controller; then deploy a controller that sets `status`."],
 30: ["Install Istio (demo profile), label a namespace, split 90/10 traffic with a VirtualService/DestinationRule, and enforce strict mTLS."],
 31: ["Create an EKS cluster with eksctl or Terraform, install the AWS Load Balancer Controller, and give a Pod S3 access with Pod Identity/IRSA."],
 32: ["Create an S3 backend with locking, split a config into two modules, import one existing resource and use a `moved` block for a rename."],
 33: ["Build S3 → SQS → worker image-processing flow locally against LocalStack; add a DLQ and verify duplicate handling."],
 34: ["Define an SLO (99.9% availability, p95 < 300 ms), compute the error budget, and write the multi-window burn-rate alerts; then run a k6 test to find the knee of the latency curve."],
 36: ["On a Linux VM run `systemd-detect-virt`, `lscpu` and `grep -c -E '(vmx|svm)' /proc/cpuinfo`; then use `unshare --pid --fork --mount-proc bash` to see a PID namespace and compare with `docker run --rm alpine ps`."],
 35: ["Follow `code-examples/capstone/` (editorial starter) and extend it with one failure-injection test."],
}

lines = ["# Labs and Exercises", "",
 "Two parts: **(A)** the hands-on labs that exist *in the source chapters* (linked, not copied — the full text lives in the chapter), "
 "and **(B)** *editorial* labs added to give every chapter a practice task. Part B is not source material.", "",
 "> Labs touching AWS create billable resources. Use a sandbox account, set a budget alarm, and destroy resources afterwards (`terraform destroy`, delete clusters/NAT gateways/load balancers).", "",
 "## A. Labs in the source chapters", "",
 "| Ch | Lab / exercise heading | Link |", "|---|---|---|"]
found = set()
for n, ch in CHAPTERS.items():
    text = (ROOT / ch["path"]).read_text(encoding="utf-8")
    in_fence = False
    for ln in text.splitlines():
        if ln.startswith("```"):
            in_fence = not in_fence
        if in_fence or not re.match(r"^#{2,3} ", ln):
            continue
        h = ln.lstrip("#").strip()
        clean = strip_emoji(h)
        if PAT.search(clean) and not SKIP.search(clean):
            found.add(n)
            lines.append(f"| {n} | {clean} | [{ch['file']}](../{ch['path']}#{github_slug(h)}) |")
lines += ["", "## B. Editorial labs (added; not from the source)", ""]
for n in sorted(EDITORIAL):
    ch = CHAPTERS[n]
    lines.append(f"### Chapter {n} — [{ch['slug'].replace('-', ' ')}](../{ch['path']})")
    lines += [f"- {t}" for t in EDITORIAL[n]]
    lines.append("")
lines += ["## Suggested order", "",
 "1. Linux/Bash/Git (2, 3, 5) → 2. Docker (7, 8) → 3. CI (6) → 4. AWS core (9–14) → 5. Kubernetes (18–20) → 6. Terraform (21) → 7. Observability (22) → 8. GitOps/Helm (25, 26) → 9. Capstone (35).", "",
 "---", "[← Contents](../CONTENTS.md)", ""]
(ROOT / "exercises" / "labs.md").write_text("\n".join(lines), encoding="utf-8")
print("labs written; chapters with source labs:", sorted(found))
