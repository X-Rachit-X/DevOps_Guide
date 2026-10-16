# Master Cheat Sheet — Commands and Syntax

Every command here appears in a chapter (chapter in brackets). Items marked *(added)* are editorial additions.

## Linux (Ch 2)

```bash
pwd; ls -la; cd /path; cd ..; cd ~            # navigate (-a hidden, -l long)
mkdir d; touch f; cp a b; mv a b; rm f; rm -r d; cat f
echo "x" > f   # overwrite      echo "x" >> f   # append
chmod +x s.sh; chmod 755 s.sh; chown ubuntu:ubuntu f   # r=4 w=2 x=1
whoami; id; sudo cmd
ps aux | grep node; top; htop; kill PID; kill -9 PID    # SIGTERM / SIGKILL
free -h; df -h; du -sh *; lscpu
systemctl status|start|stop|restart|enable nginx; journalctl -u nginx -f
grep -i "error" f; grep -r "DATABASE_URL" .; find /var/log -name "*.log"
export PORT=3000; echo $PORT; env
sudo apt update; sudo apt install nginx               # Debian/Ubuntu (dnf RHEL, pacman Arch)
ssh -i key.pem ubuntu@<ip>
ip addr; ip route; ping host; curl https://x; ss -tulpn | grep 3000
```

## Bash (Ch 3)

```bash
#!/bin/bash
set -euo pipefail                      # -e stop on error, -u unset vars, pipefail
name="x"; echo "$name"; today=$(date)  # no spaces around =
read name; "$1" "$2" "$@" "$#" "$?" "$$" "$0"
if [ "$a" -ge 18 ]; then …; elif …; else …; fi     # -eq -ne -gt -ge -lt -le ; -f -d -e -r -w -x
for f in *.log; do …; done;  while [ "$c" -le 5 ]; do c=$((c+1)); done
f() { echo "$1"; };  cmd > out 2>&1;  a && b;  a || b;  a | b
tar -czf a.tar.gz dir/;  tar -xzf a.tar.gz;  head; tail -f; wc -l; sort | uniq; xargs -n1
crontab -e      # min hour dom month dow :  0 2 * * *
```

## Networking diagnostics (Ch 4)

`nslookup d`, `dig d`, `curl -I url` (headers), `curl -v url` (DNS→TCP→TLS→HTTP), `ss -lntp`, `ip route`, `ping`.

## Git (Ch 5)

```bash
git init; git clone url; git status; git add f; git commit -m "msg"
git diff; git diff --staged; git log --oneline --graph --decorate --all
git switch -c feature/x; git switch main; git merge feature/x; git rebase main
git fetch origin; git pull; git push -u origin feature/x; git remote -v
git stash; git stash pop; git restore f; git restore --staged f (added)
git reset --soft|--mixed|--hard HEAD~1; git revert <c>; git reflog; git cherry-pick <c>
git tag v1.0.0; git push origin v1.0.0
```

## Docker (Ch 7, 8)

```bash
docker build -t my-api:1.0 .;  docker run -d --name api -p 3000:3000 -e K=V -v vol:/path my-api:1.0
docker ps [-a]; docker logs -f c; docker exec -it c sh; docker inspect c; docker port c
docker stop|start|restart|rm c; docker pull|push img; docker tag a b; docker images
docker network create n; docker volume create v; docker compose up [-d]; docker compose down
```
Dockerfile: `FROM WORKDIR COPY RUN ENV EXPOSE CMD ENTRYPOINT USER HEALTHCHECK`; multi-stage `FROM … AS builder` + `COPY --from=builder`; `npm ci --omit=dev`.

## GitHub Actions (Ch 6)

`on: push/pull_request` · `jobs.<id>.runs-on` · `steps: uses|run` · `needs:` · `strategy.matrix` · `permissions: id-token: write` · `${{ secrets.X }}` · `${{ github.sha }}`.

## AWS CLI (Ch 9–17)

```bash
aws sts get-caller-identity;  aws configure;  aws configure get region
aws s3 ls | cp | sync;        aws lambda update-function-code --function-name f --zip-file fileb://x.zip
aws cloudwatch list-metrics | get-metric-statistics | put-metric-alarm
aws cloudfront create-invalidation --paths "/index.html" (added)
aws eks update-kubeconfig --region r --name c (added)
aws ecr get-login-password --region r | docker login --username AWS --password-stdin <acct>.dkr.ecr.r.amazonaws.com
```

## kubectl (Ch 18–20, 23, 29–31)

```bash
kubectl get pods|svc|deploy|ing|hpa|pvc|all|nodes|endpointslices -n ns [-o wide] [-w]
kubectl describe pod|deployment|svc|node|hpa|pvc X        # Events!
kubectl logs P [-f] [--previous] [-c container];  kubectl exec -it P -- sh
kubectl apply -f f.yaml;  kubectl delete pod P;  kubectl scale deployment api --replicas=5
kubectl rollout status|history|undo|restart deployment/api
kubectl port-forward service/api-service 3000:80;  kubectl top pods|nodes
kubectl create secret generic s --from-literal=K=V;  kubectl exec -it P -- env
kubectl get crd; kubectl api-resources; kubectl auth can-i … ;  kubectl label namespace default istio-injection=enabled
kind create cluster --name n;  kind load docker-image img --name n
```

## Helm (Ch 25)

`helm create|lint|template|install|upgrade [--install] [--dry-run]|list|status|history|rollback|get values|get manifest|uninstall|package|repo add|update|search repo` · `-f values.yaml` · `--set k=v` · `--namespace ns --create-namespace`.

## ArgoCD (Ch 26)

`kubectl create ns argocd` · `kubectl apply -n argocd -f …/install.yaml` · `kubectl port-forward svc/argocd-server -n argocd 8080:443` · `argocd version`. App: `source.repoURL/targetRevision/path`, `destination.server/namespace`, `syncPolicy.automated {selfHeal, prune}`.

## Terraform (Ch 21, 32)

```bash
terraform init|fmt|validate|plan [-out=tfplan]|apply [tfplan]|destroy|show|output|graph
terraform state list|show|rm|mv;  terraform import;  terraform apply -refresh-only (added)
terraform workspace …;  terraform force-unlock <id> (added)
```

## Ansible (Ch 28)

`ansible all -i inventory.ini -m ping` · `ansible-playbook -i inventory.ini site.yml [--check --diff -vvv --tags t]` · `ansible-inventory -i inventory.ini --list`.

## Istio (Ch 30)

`istioctl version` · `istioctl install --set profile=demo -y` · `kubectl label namespace default istio-injection=enabled` · `kubectl rollout restart deployment X` (inject existing).

## Load testing / SRE (Ch 34)

`k6 run script.js` (added script in Ch 34 supplement) · PromQL error ratio: `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))` (added).

## Virtualization (Ch 36)

`systemd-detect-virt` · `lscpu | grep -i -E "hypervisor|virtualization"` · `grep -c -E '(vmx|svm)' /proc/cpuinfo` · `ls /dev/kvm` · `sudo unshare --pid --fork --mount-proc bash` (added; standard Linux tools, see Ch 36 supplement).

Mental model: Hardware → Hypervisor → VMs → Guest OS → Apps. CPU: vCPU scheduling (VT-x/AMD-V, VM exit). Memory: GVA → GPA → HPA (EPT/NPT, TLB). I/O: emulation → VirtIO → passthrough/SR-IOV. Containers: host kernel + namespaces + cgroups.

---
[← Revision index](README.md)
