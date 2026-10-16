#!/usr/bin/env python
"""Independent audit of the generated knowledge base.

Does NOT reuse build.py's transformation. It re-normalises both the archived
source and the generated chapter and compares them, then runs link, placeholder,
reference and code-syntax checks.  Writes AUDIT_REPORT.md and _work/audit.json.

Usage: python -X utf8 tools/audit.py
"""
import json
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from registry import CHAPTERS, github_slug  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "_work"
FENCE = re.compile(r"^\s*```")


# ---------------------------------------------------------------- normalisation (independent)
def canon(lines, strip_header=False):
    """Return canonical list of (kind,text). Normalisations applied identically to source and output:
    - heading level ignored; - chapter links reduced to text; - Response->Chapter; - fence id attrs removed."""
    out, in_fence = [], False
    for ln in lines:
        s = ln.rstrip()
        s = re.sub(r"\bResponses (?=\d)", "Chapters ", s)
        s = re.sub(r"\bResponse (?=\d)", "Chapter ", s)
        if FENCE.match(s):
            s = re.sub(r'\s+id="[^"]*"\s*$', "", s)
            in_fence = not in_fence
            out.append(("fence", s))
            continue
        if in_fence:
            out.append(("code", s))
            continue
        # drop chapter links  [Chapter 6](../x/ch06-foo.md) / [7](ch07-foo.md)
        s = re.sub(r"\[([^\]]+)\]\((?:\.\./)?(?:[0-9a-z-]+/)?ch\d\d-[^)\s]*\.md\)", r"\1", s)
        m = re.match(r"^#{1,6}(\s+.*)$", s)
        if m:
            out.append(("heading", m.group(1).strip()))
        else:
            out.append(("text", s))
    return out


def read_trims():
    trims, extra = {}, {}
    for raw in (WORK / "trims.csv").read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        p = raw.split(",", 3)
        if p[0].startswith("cut"):
            extra[int(p[0][3:])] = (int(p[1]), int(p[2]))
        else:
            trims[int(p[0])] = (int(p[1]), int(p[2]), p[3] if len(p) > 3 else "")
    return trims, extra


def count_tables(lines):
    in_fence, n = False, 0
    for i, l in enumerate(lines[:-1]):
        if FENCE.match(l):
            in_fence = not in_fence
        if not in_fence and l.lstrip().startswith("|") and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1].replace("|", "", 1) if lines[i + 1].lstrip().startswith("|") else ""):
            n += 1
    return n


def fidelity():
    trims, extra = read_trims()
    results = {}
    for n, c in CHAPTERS.items():
        src = (ROOT / c["src"]).read_text(encoding="utf-8").splitlines()
        a, b, note = trims[n]
        keep = [i for i in range(a, b + 1)]
        if n in extra:
            x, y = extra[n]
            keep = [i for i in keep if not (x <= i <= y)]
        kept = [src[i - 1] for i in keep][1:]  # drop header line
        removed = [src[i - 1] for i in range(1, len(src) + 1) if i not in set(keep) and i != keep[0]]
        out = (ROOT / c["path"]).read_text(encoding="utf-8").splitlines()
        try:
            bi = next(i for i, l in enumerate(out) if "<!-- SOURCE-BEGIN -->" in l)
            ei = next(i for i, l in enumerate(out) if "<!-- SOURCE-END -->" in l)
        except StopIteration:
            results[n] = {"ok": False, "reason": "missing SOURCE markers"}
            continue
        body = out[bi + 1:ei]
        ck, cb = canon(kept), canon(body)
        # a trailing blank line is added before SOURCE-END marker? compare ignoring trailing blanks
        while ck and ck[-1] == ("text", ""):
            ck.pop()
        while cb and cb[-1] == ("text", ""):
            cb.pop()
        ok = ck == cb
        first_diff = None
        if not ok:
            for i, (u, v) in enumerate(zip(ck, cb)):
                if u != v:
                    first_diff = (i, u, v)
                    break
            else:
                first_diff = (min(len(ck), len(cb)), len(ck), len(cb))
        fences_src = sum(1 for l in kept if FENCE.match(l))
        fences_out = sum(1 for l in body if FENCE.match(l))
        heads_src = sum(1 for k, _ in ck if k == "heading")
        heads_out = sum(1 for k, _ in cb if k == "heading")
        results[n] = {
            "ok": ok and fences_src == fences_out and fences_src % 2 == 0 and heads_src == heads_out,
            "kept_nonempty": sum(1 for l in kept if l.strip()),
            "out_nonempty": sum(1 for l in body if l.strip()),
            "removed_nonempty": sum(1 for l in removed if l.strip()),
            "code_blocks": fences_src // 2,
            "code_blocks_out": fences_out // 2,
            "headings": heads_src,
            "headings_out": heads_out,
            "tables": count_tables(kept),
            "tables_out": count_tables(body),
            "diff": None if ok else str(first_diff)[:300],
            "has_supplement": any("## Editorial supplement" in l for l in out),
        }
        # removed lines must be present verbatim in the removed-scaffolding appendix or course notes
        appendix = (ROOT / "docs/00-start-here/removed-scaffolding.md").read_text(encoding="utf-8")
        missing = [l for l in removed if l.strip() and l not in appendix]
        results[n]["removed_not_in_appendix"] = len(missing)
    return results


# ---------------------------------------------------------------- links
MD_LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def headings_of(path, cache={}):
    if path in cache:
        return cache[path]
    slugs, seen, in_fence = set(), defaultdict(int), False
    for l in path.read_text(encoding="utf-8").splitlines():
        if FENCE.match(l):
            in_fence = not in_fence
        m = None if in_fence else re.match(r"^#{1,6}\s+(.*)$", l)
        if m:
            s = github_slug(m.group(1)); k = seen[s]; seen[s] += 1
            slugs.add(s if k == 0 else f"{s}-{k}")
    cache[path] = slugs
    return slugs


def check_links():
    broken, checked = [], 0
    skip_dirs = {"source-archive", "_work", "node_modules", ".git", "extracted", "supplements"}
    for p in ROOT.rglob("*.md"):
        if any(part in skip_dirs for part in p.relative_to(ROOT).parts):
            continue
        in_fence = False
        for ln, l in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if FENCE.match(l):
                in_fence = not in_fence
            if in_fence:
                continue
            for m in MD_LINK.finditer(re.sub(r"`[^`]*`", "", l)):
                tgt = m.group(1)
                if re.match(r"^(https?:|mailto:|#$)", tgt):
                    continue
                checked += 1
                path_part, _, anchor = tgt.partition("#")
                dest = (p.parent / path_part).resolve() if path_part else p
                if not dest.exists():
                    broken.append((str(p.relative_to(ROOT)), ln, tgt, "file not found"))
                    continue
                if anchor and dest.suffix == ".md":
                    if github_slug(anchor) not in headings_of(dest) and anchor not in headings_of(dest):
                        broken.append((str(p.relative_to(ROOT)), ln, tgt, "anchor not found"))
    return checked, broken


# ---------------------------------------------------------------- misc checks
def check_text():
    issues = {"leftover_response_refs": [], "chapter_refs_out_of_range": [], "placeholders": [], "empty_headings": []}
    for n, c in CHAPTERS.items():
        full = (ROOT / c["path"]).read_text(encoding="utf-8")
        text = full.split("<!-- SOURCE-BEGIN -->", 1)[1].split("<!-- SOURCE-END -->", 1)[0]
        for m in re.finditer(r"\bResponses? \d", text):
            issues["leftover_response_refs"].append((c["path"], m.group(0)))
        for m in re.finditer(r"\bChapters? (\d+)", text):
            if int(m.group(1)) > len(CHAPTERS):
                issues["chapter_refs_out_of_range"].append((c["path"], m.group(0)))
    own = [p for p in ROOT.rglob("*.md")
           if not any(x in p.relative_to(ROOT).parts for x in ("source-archive", "_work", "extracted", "docs", "node_modules")) and p.name != "AUDIT_REPORT.md"]
    own += [ROOT / "docs/00-start-here/study-guide.md", ROOT / "docs/00-start-here/roadmap.md"]
    for p in own:
        if not p.exists():
            continue
        lines = p.read_text(encoding="utf-8").splitlines()
        in_fence = False
        for i, l in enumerate(lines):
            if FENCE.match(l):
                in_fence = not in_fence
            if not in_fence and re.search(r"\b(TODO|TBD|FIXME|lorem ipsum)\b", l):
                issues["placeholders"].append((str(p.relative_to(ROOT)), i + 1, l.strip()[:80]))
            m = re.match(r"^(#{1,6})\s+\S", l)
            if m and not in_fence:
                # next non-blank line
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j >= len(lines) or re.match(r"^#{1,6}\s", lines[j]) and len(re.match(r"^(#+)", lines[j]).group(1)) <= len(m.group(1)):
                    issues["empty_headings"].append((str(p.relative_to(ROOT)), i + 1, l.strip()[:60]))
    return issues


def check_code():
    res = {"passed": 0, "failed": [], "skipped": 0, "by_type": defaultdict(lambda: [0, 0, 0])}
    try:
        import yaml  # type: ignore
    except Exception:
        yaml = None
    base = ROOT / "code-examples" / "extracted"
    if not base.exists():
        return res
    placeholder = re.compile(r"(\.\.\.|<[A-Za-z_-]+>|\{\{|\$\{\{|xxx|my-bucket-name)")
    for f in sorted(base.rglob("*")):
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8")
        ext = f.suffix.lower() if f.suffix else f.name.lower()
        kind = None
        err = None
        if ext in (".yaml", ".yml"):
            kind = "yaml"
            if yaml is None:
                continue
            if "{{" in text:  # Helm templates / GH expressions are not plain YAML
                res["skipped"] += 1; res["by_type"][kind][2] += 1; continue
            try:
                list(yaml.safe_load_all(text))
            except Exception as e:
                err = str(e).splitlines()[0][:120]
        elif ext == ".json":
            kind = "json"
            try:
                json.loads(text)
            except Exception as e:
                err = str(e)[:120]
        elif ext == ".sh":
            kind = "bash"
            try:
                r = subprocess.run(["bash", "-n"], input=text.encode("utf-8"), capture_output=True)
                if r.returncode != 0:
                    err = (r.stderr.decode("utf-8", "replace").strip().splitlines() or ["syntax error"])[0][:120]
            except Exception:  # bash unavailable
                res["skipped"] += 1
                continue
        else:
            continue
        b = res["by_type"][kind]
        if err:
            if placeholder.search(text):
                res["skipped"] += 1; b[2] += 1
            else:
                res["failed"].append((str(f.relative_to(ROOT)), err)); b[1] += 1
        else:
            res["passed"] += 1; b[0] += 1
    res["by_type"] = {k: v for k, v in res["by_type"].items()}
    return res


def check_site():
    issues = []
    nav = ROOT / "website" / "data" / "nav.json"
    if nav.exists():
        for c in json.loads(nav.read_text(encoding="utf-8"))["chapters"]:
            for k in ("path", "revision"):
                if not (ROOT / c[k]).exists():
                    issues.append(f"nav.json: missing {c[k]}")
    idx = ROOT / "website" / "data" / "search-index.json"
    if idx.exists():
        docs = {d["doc"] for d in json.loads(idx.read_text(encoding="utf-8"))}
        for d in docs:
            if not (ROOT / d).exists():
                issues.append(f"search index: missing {d}")
    for f in ("index.html", "styles.css", "app.js"):
        if not (ROOT / "website" / f).exists():
            issues.append(f"website/{f} missing")
    return issues


def main():
    fid = fidelity()
    checked, broken = check_links()
    txt = check_text()
    code = check_code()
    site = check_site()
    all_ok = all(v["ok"] for v in fid.values())
    data = {"fidelity": fid, "links_checked": checked, "broken_links": broken, "text": txt, "code": code, "site": site,
            "all_chapters_lossless": all_ok}
    (WORK / "audit.json").write_text(json.dumps(data, ensure_ascii=False, indent=1, default=str), encoding="utf-8")

    L = ["# Audit Report", "",
         "Generated by `tools/audit.py` (independent of `tools/build.py`). Re-run with `python -X utf8 tools/audit.py`.", "",
         "## 1. Source-to-output fidelity (per chapter)", "",
         "For each chapter the audit normalises the *archived source* (kept range) and the *generated chapter* body",
         "(heading levels, `Response`→`Chapter`, chapter links, fence id attributes) and requires the two sequences to be",
         "identical line for line. It also compares code-block, heading and table counts and checks that every removed line",
         "is preserved in `docs/00-start-here/removed-scaffolding.md`.", "",
         "| Ch | Identical | Non-empty lines (source→output) | Removed lines (all preserved in appendix) | Code blocks | Headings | Tables | Supplement |",
         "|---:|:---:|---:|---:|---:|---:|---:|:---:|"]
    for n in sorted(fid):
        v = fid[n]
        if "reason" in v:
            L.append(f"| {n} | ❌ | {v['reason']} | | | | | |"); continue
        L.append(f"| {n} | {'✅' if v['ok'] else '❌'} | {v['kept_nonempty']} → {v['out_nonempty']} | {v['removed_nonempty']} "
                 f"({'✅' if v['removed_not_in_appendix'] == 0 else '❌ ' + str(v['removed_not_in_appendix'])}) | "
                 f"{v['code_blocks']} → {v['code_blocks_out']} | {v['headings']} → {v['headings_out']} | {v['tables']} → {v['tables_out']} | "
                 f"{'yes' if v['has_supplement'] else '–'} |")
    tot_k = sum(v.get('kept_nonempty', 0) for v in fid.values())
    tot_o = sum(v.get('out_nonempty', 0) for v in fid.values())
    tot_c = sum(v.get('code_blocks', 0) for v in fid.values())
    L += ["", f"**Result: {f'ALL {len(CHAPTERS)} chapters reproduce their source exactly (modulo the documented transformations).' if all_ok else 'FAILURES PRESENT — see rows marked ❌.'}**",
          f"Totals: {tot_k} non-empty source lines kept → {tot_o} in chapters; {tot_c} code blocks.", ""]
    bad = [(n, v) for n, v in fid.items() if not v["ok"]]
    for n, v in bad:
        L.append(f"- Chapter {n} first difference: `{v.get('diff')}`")
    L += ["", "## 2. Links", "", f"Relative Markdown links checked: **{checked}**. Broken: **{len(broken)}**.", ""]
    for p, ln, t, why in broken[:60]:
        L.append(f"- `{p}:{ln}` → `{t}` ({why})")
    L += ["", "## 3. Text checks", "",
          f"- Leftover `Response N` references in chapters: **{len(txt['leftover_response_refs'])}**",
          f"- `Chapter N` references beyond Chapter {len(CHAPTERS)}: **{len(txt['chapter_refs_out_of_range'])}** "
          + ("(these come from references to material that does not exist in the source)" if txt['chapter_refs_out_of_range'] else ""),
          f"- Placeholder markers (TODO/TBD/FIXME) in authored docs: **{len(txt['placeholders'])}**",
          f"- Empty headings in authored docs: **{len(txt['empty_headings'])}**", ""]
    for k in ("chapter_refs_out_of_range", "placeholders", "empty_headings"):
        for item in txt[k][:15]:
            L.append(f"  - {k}: {item}")
    L += ["", "## 4. Syntax check of extracted code", "",
          f"Passed: **{code['passed']}** · Skipped (templates/placeholders/pseudo-syntax): **{code['skipped']}** · Failed: **{len(code['failed'])}**.",
          f"By type (passed, failed, skipped): `{json.dumps(code['by_type'])}`", "",
          "Only YAML, JSON and Bash are machine-checked here (no Terraform, TypeScript or Groovy toolchain was used).", ""]
    for f, e in code["failed"][:30]:
        L.append(f"- `{f}`: {e}")
    L += ["", "## 5. Website data", ""]
    L += [f"- {s}" for s in site] or ["- navigation, search index and website files are consistent."]
    (ROOT / "AUDIT_REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print(f"lossless={all_ok} links_checked={checked} broken={len(broken)} code_passed={code['passed']} code_failed={len(code['failed'])} "
          f"leftover_refs={len(txt['leftover_response_refs'])} oor_refs={len(txt['chapter_refs_out_of_range'])} "
          f"placeholders={len(txt['placeholders'])} empty_headings={len(txt['empty_headings'])} site_issues={len(site)}")
    return 0 if all_ok and not broken else 1


if __name__ == "__main__":
    sys.exit(main())
