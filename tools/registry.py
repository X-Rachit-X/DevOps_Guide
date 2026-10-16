"""Chapter registry shared by build.py and audit.py.

Chapter number == response number in the original conversation.
"""
import re

DOMAINS = {
    "00-start-here": "Start Here",
    "01-foundations": "Foundations",
    "02-containers": "Containers",
    "03-cicd-gitops": "CI/CD and GitOps",
    "04-aws": "AWS",
    "05-kubernetes": "Kubernetes",
    "06-iac-config": "Infrastructure as Code and Configuration",
    "07-observability-sre": "Observability and SRE",
    "08-production": "Production Architecture",
    "09-interview": "Interview and OA Mastery",
}

# (number, slug, domain)
_CH = [
    (1, "cloud-devops-fundamentals", "01-foundations"),
    (2, "linux", "01-foundations"),
    (3, "bash-automation", "01-foundations"),
    (4, "networking", "01-foundations"),
    (5, "git-github", "01-foundations"),
    (6, "cicd-github-actions", "03-cicd-gitops"),
    (7, "docker-fundamentals", "02-containers"),
    (8, "docker-production", "02-containers"),
    (9, "aws-fundamentals-iam", "04-aws"),
    (10, "ec2-compute", "04-aws"),
    (11, "s3-storage", "04-aws"),
    (12, "vpc-networking", "04-aws"),
    (13, "rds-databases", "04-aws"),
    (14, "load-balancing-scaling", "04-aws"),
    (15, "lambda-serverless-messaging", "04-aws"),
    (16, "route53-cloudfront-waf", "04-aws"),
    (17, "monitoring-security", "04-aws"),
    (18, "kubernetes-fundamentals", "05-kubernetes"),
    (19, "kubernetes-config-storage", "05-kubernetes"),
    (20, "kubernetes-networking-scaling", "05-kubernetes"),
    (21, "terraform", "06-iac-config"),
    (22, "observability-reliability", "07-observability-sre"),
    (23, "production-architecture-troubleshooting", "08-production"),
    (24, "interview-oa-mastery", "09-interview"),
    (25, "helm", "05-kubernetes"),
    (26, "gitops-argocd", "03-cicd-gitops"),
    (27, "jenkins-advanced-cicd", "03-cicd-gitops"),
    (28, "ansible", "06-iac-config"),
    (29, "crds-operators", "05-kubernetes"),
    (30, "service-mesh-istio", "05-kubernetes"),
    (31, "advanced-eks", "05-kubernetes"),
    (32, "advanced-terraform", "06-iac-config"),
    (33, "advanced-aws-backend", "04-aws"),
    (34, "advanced-sre", "07-observability-sre"),
    (35, "devops-capstone", "08-production"),
    (36, "virtualization-internals", "01-foundations"),
]

CHAPTERS = {n: {"n": n, "slug": s, "domain": d,
                "file": f"ch{n:02d}-{s}.md",
                "path": f"docs/{d}/ch{n:02d}-{s}.md",
                "src": f"source-archive/src-{n:02d}.txt",
                "part": "I" if n <= 24 else "II"} for n, s, d in _CH}

EMOJI_RE = re.compile(r"[\U0001F000-\U0001FFFF☀-➿️‍⬀-⯿]+")


def strip_emoji(s: str) -> str:
    return re.sub(r"\s+", " ", EMOJI_RE.sub("", s)).strip()


def github_slug(text: str) -> str:
    """Approximation of GitHub's heading anchor algorithm."""
    t = strip_emoji(text).lower()
    t = re.sub(r"[`*_~]", "", t) if False else t
    t = re.sub(r"[^\w\s-]", "", t, flags=re.UNICODE)
    t = t.strip().replace(" ", "-")
    return t


def rel(from_domain_dir: str, n: int) -> str:
    """Relative link from docs/<from_domain_dir>/x.md to chapter n."""
    c = CHAPTERS[n]
    if c["domain"] == from_domain_dir:
        return c["file"]
    return f"../{c['domain']}/{c['file']}"
