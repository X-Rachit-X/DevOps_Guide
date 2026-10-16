#!/usr/bin/env python
"""Build the knowledge base from the archived source conversation.

Run from anywhere:  python tools/build.py

What it does (all deterministic / idempotent):
  1. Reads source-archive/src-NN.txt and _work/trims.csv.
  2. Writes docs/<domain>/chNN-<slug>.md with ONLY these transformations
     (so that nothing of the source is lost):
        - conversational scaffolding listed in trims.csv is removed
        - '# Response N/24 - Title' header -> '# Chapter N - Title'
        - tool-generated ' id="..."' attributes on code fences are removed
        - 'Response N' cross references -> 'Chapter N' (and linked)
        - Markdown heading levels are demoted by one (chapter title is the only H1)
  3. Appends supplements/chNN.md (clearly labelled editorial additions).
  4. Rewrites links in revision/chNN-revision.md and adds navigation footers.
  5. Generates CONTENTS.md, GLOSSARY.md, appendix logs, search index and
     code-examples/extracted/ (+ INDEX.md).
"""
import csv
import json
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from registry import CHAPTERS, DOMAINS, github_slug, strip_emoji  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "_work"
PLAIN_HEADER_CHAPTERS = {36}
FENCE_RE = re.compile(r"^\s*```")
HEADER_RE = re.compile(r"^# Response (\d+)/(\d+)\s+[—-]\s+(.*)$")
# Source 36 has no 'Response N/M' prefix: its first kept line is a plain H1 title.
PLAIN_HEADER_RE = re.compile(r"^# (?!Response )(\S.*)$")
ID_ATTR_RE = re.compile(r'^(\s*```[^\s`]*)\s+id="[^"]*"\s*$')
HEADING_RE = re.compile(r"^(#{1,5})(\s+\S.*)$")


# ---------------------------------------------------------------- trims
def load_trims():
    trims, extra = {}, {}
    for raw in (WORK / "trims.csv").read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        parts = raw.split(",", 3)
        key = parts[0].strip()
        if key.startswith("cut"):
            extra[int(key[3:])] = (int(parts[1]), int(parts[2]))
        else:
            trims[int(key)] = (int(parts[1]), int(parts[2]), parts[3].strip().strip('"') if len(parts) > 3 else "")
    return trims, extra


# ---------------------------------------------------------------- text transforms
def split_inline_code(line):
    """Split a line into [(text, is_code)] segments on backtick spans."""
    out, buf, in_code = [], "", False
    for ch in line:
        if ch == "`":
            if in_code:
                out.append((buf + "`", True)); buf = ""
            else:
                if buf:
                    out.append((buf, False))
                buf = "`"
            in_code = not in_code
        else:
            buf += ch
    if buf:
        out.append((buf, in_code))
    return out


def rename_refs(text):
    text = re.sub(r"\bResponses (\d)", r"Chapters \1", text)
    text = re.sub(r"\bResponse (\d)", r"Chapter \1", text)
    return text


LINK_MULTI = re.compile(r"\bChapters (\d{1,2})(\s*[–-]\s*|\s+and\s+|\s*,\s*)(\d{1,2})\b")
LINK_ONE = re.compile(r"(?<![\[\w/])\bChapter (\d{1,2})\b(?![\]\w])")


def link_chapters(line, cur_n, cur_domain):
    """Turn 'Chapter N' mentions into relative links (outside code spans)."""
    def url(n):
        c = CHAPTERS[n]
        return c["file"] if c["domain"] == cur_domain else f"../{c['domain']}/{c['file']}"

    def multi(m):
        a, sep, b = int(m.group(1)), m.group(2), int(m.group(3))
        if a == cur_n or b == cur_n or a not in CHAPTERS or b not in CHAPTERS:
            return m.group(0)
        return f"Chapters [{a}]({url(a)}){sep}[{b}]({url(b)})"

    def one(m):
        n = int(m.group(1))
        if n == cur_n or n not in CHAPTERS:
            return m.group(0)
        return f"[Chapter {n}]({url(n)})"

    segs = []
    for text, is_code in split_inline_code(line):
        if not is_code:
            text = LINK_MULTI.sub(multi, text)
            text = LINK_ONE.sub(one, text)
        segs.append(text)
    return "".join(segs)


def transform_body(lines, n, domain, link=True):
    """Apply the documented transformations to the kept source lines.

    The first line is the '# Response ...' header and is handled separately.
    Returns the transformed body (without header)."""
    out, in_fence = [], False
    for line in lines:
        if FENCE_RE.match(line):
            line = ID_ATTR_RE.sub(r"\1", line)
            in_fence = not in_fence
            out.append(rename_refs(line))
            continue
        line = rename_refs(line)
        if in_fence:
            out.append(line)
            continue
        m = HEADING_RE.match(line)
        if m:
            line = "#" + line  # demote one level; headings are not linked (kept clean)
            out.append(line)
            continue
        out.append(link_chapters(line, n, domain) if link else line)
    return out


# ---------------------------------------------------------------- build chapters
def read_src(n):
    return (ROOT / CHAPTERS[n]["src"]).read_text(encoding="utf-8").splitlines()


def chapter_title(n, src_lines):
    for ln in src_lines:
        m = HEADER_RE.match(ln)
        if m:
            return strip_emoji(m.group(3))
    if n in PLAIN_HEADER_CHAPTERS:
        for ln in src_lines:
            m = PLAIN_HEADER_RE.match(ln)
            if m:
                return strip_emoji(m.group(1))
    raise SystemExit(f"no header in chapter {n}")


def build_chapters(trims, extra):
    titles, meta = {}, {}
    for n in CHAPTERS:
        src = read_src(n)
        titles[n] = chapter_title(n, src)
    for n, c in CHAPTERS.items():
        src = read_src(n)
        start, end, note = trims[n]
        keep = list(range(start, end + 1))
        if n in extra:
            a, b = extra[n]
            keep = [i for i in keep if not (a <= i <= b)]
        kept_lines = [src[i - 1] for i in keep]
        is_header = HEADER_RE.match(kept_lines[0]) or (n in PLAIN_HEADER_CHAPTERS and PLAIN_HEADER_RE.match(kept_lines[0]))
        assert is_header, f"chapter {n}: first kept line is not the header"
        body = transform_body(kept_lines[1:], n, c["domain"])
        prev_n, next_n = n - 1, n + 1
        nav = []
        if prev_n in CHAPTERS:
            nav.append(f"← [Chapter {prev_n}: {titles[prev_n]}]({'../' + CHAPTERS[prev_n]['domain'] + '/' if CHAPTERS[prev_n]['domain'] != c['domain'] else ''}{CHAPTERS[prev_n]['file']})")
        if next_n in CHAPTERS:
            nav.append(f"[Chapter {next_n}: {titles[next_n]}]({'../' + CHAPTERS[next_n]['domain'] + '/' if CHAPTERS[next_n]['domain'] != c['domain'] else ''}{CHAPTERS[next_n]['file']}) →")
        part = "Part I — Core curriculum (Responses 1–24)" if n <= 24 else "Part II — Advanced extension (Responses 25–36)"
        sup_path = ROOT / "supplements" / f"ch{n:02d}.md"
        header = [
            f"# Chapter {n} — {titles[n]}",
            "",
            f"> **Source:** Response {n} of the original conversation (`{c['src']}`, lines {start}–{end}) · **{part}**  ",
            f"> **Study aids:** [Revision sheet](../../revision/ch{n:02d}-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)"
            + (" · *includes an editorial supplement at the end*" if sup_path.exists() else ""),
            "",
            "<!-- SOURCE-BEGIN -->",
        ]
        footer = ["<!-- SOURCE-END -->", ""]
        if sup_path.exists():
            footer += [
                "---",
                "",
                "## Editorial supplement",
                "",
                "> **Added by the knowledge-base editor — not part of the original source.** "
                "It fills gaps the source leaves open (for example concepts named in the interview list but never "
                "explained, or configuration the chapter only describes in words). Treat the text above as the "
                "original material and this section as clearly separated additions.",
                "",
            ]
            footer += sup_path.read_text(encoding="utf-8").rstrip("\n").splitlines()
            footer += [""]
        footer += ["---", "", "**Navigation:** " + " · ".join(nav) + f" · [Revision sheet](../../revision/ch{n:02d}-revision.md)", ""]
        out = ROOT / c["path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(header + body + footer), encoding="utf-8", newline="\n")
        meta[n] = {"title": titles[n], "kept": [start, end], "note": note, "removed_extra": extra.get(n)}
    return titles, meta


# ---------------------------------------------------------------- course design notes (preambles)
def build_course_notes():
    """Preserve the conversational preambles that contain course-design information."""
    parts = [
        ("src-02.txt", 1, 6, "Opening reply before Chapter 2 (scope of 'fundamentals')"),
        ("src-08.txt", 1, 118, "Reply before Chapter 8 — where testing belongs in the roadmap"),
        ("src-11.txt", 1, 51, "Reply before Chapter 11 — scope of the AWS block (Responses 9–17)"),
        ("src-15.txt", 1, 8, "Reply before Chapter 15 — change of teaching style to hands-on"),
        ("src-15.txt", 1809, 1870, "Closing note of Chapter 15 — 'Build It / Set It Up' commitment for later chapters"),
        ("src-18.txt", 1, 10, "Reply before Chapter 18 — scope of DevOps coverage and containers"),
        ("src-36.txt", 1, 2, "Opening reply before Chapter 36 — why a dedicated virtualization deep dive"),
    ]
    lines = [
        "# Course Design Notes",
        "",
        "> Preserved verbatim from the conversational parts of the original source that were removed from the chapter files.",
        "> They explain how the course was scoped and why it is taught the way it is. Cross-references were renamed from",
        "> \"Response N\" to \"Chapter N\"; nothing else was changed.",
        "",
    ]
    for fname, a, b, title in parts:
        src = (ROOT / "source-archive" / fname).read_text(encoding="utf-8").splitlines()[a - 1:b]
        lines += [f"## {title}", "", f"*Source: `source-archive/{fname}`, lines {a}–{b}*", ""]
        in_fence = False
        for l in src:
            if FENCE_RE.match(l):
                l = ID_ATTR_RE.sub(r"\1", l)
                in_fence = not in_fence
                lines.append(rename_refs(l))
                continue
            l = rename_refs(l)
            m = HEADING_RE.match(l)
            if m and not in_fence:
                l = "###" + l[len(m.group(1)):] if False else "#" * (len(m.group(1)) + 2) + m.group(2)
            lines.append(l)
        lines += ["", "---", ""]
    out = ROOT / "docs" / "00-start-here" / "course-design-notes.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- removed scaffolding appendix
def build_removed_appendix(trims, extra):
    lines = [
        "# Removed Scaffolding (verbatim)",
        "",
        "Every block of conversational scaffolding (roadmap progress tables, \"next response\" teasers, replies to",
        "meta-questions) that was removed from a chapter file, reproduced verbatim so that nothing is lost. The",
        "originals of course remain untouched in `source-archive/`.",
        "",
    ]
    for n in CHAPTERS:
        src = read_src(n)
        start, end, note = trims[n]
        kept = set(range(start, end + 1))
        if n in extra:
            a, b = extra[n]
            kept -= set(range(a, b + 1))
        removed = [i for i in range(1, len(src) + 1) if i not in kept]
        if not removed:
            continue
        lines += [f"## Chapter {n}", "", f"*Reason recorded:* {note}", ""]
        # group into contiguous runs
        runs, cur = [], [removed[0]]
        for i in removed[1:]:
            if i == cur[-1] + 1:
                cur.append(i)
            else:
                runs.append(cur); cur = [i]
        runs.append(cur)
        for run in runs:
            block = [src[i - 1] for i in run]
            if not any(x.strip() for x in block):
                continue
            lines += [f"**Lines {run[0]}–{run[-1]}**", "", "````text"] + block + ["````", ""]
    out = ROOT / "docs" / "00-start-here" / "removed-scaffolding.md"
    out.write_text("\n".join(lines), encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- revision sheets
def fix_revision_links(titles):
    link_re = re.compile(r"\]\(((?:\.\./)+)docs/[^)#]*?ch(\d{2})-[^)#]*?\.md((?:#[^)]*)?)\)")
    for n in CHAPTERS:
        p = ROOT / "revision" / f"ch{n:02d}-revision.md"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        # drop previous navigation footer
        text = re.split(r"\n<!-- NAV -->\n", text)[0].rstrip("\n") + "\n"

        def sub(m):
            k = int(m.group(2))
            return f"](../{CHAPTERS[k]['path']}{m.group(3)})" if k in CHAPTERS else m.group(0)

        text = link_re.sub(sub, text)
        # main chapter link inside the first blockquote
        nav = ["", "<!-- NAV -->", "", "---", ""]
        parts = []
        if n - 1 in CHAPTERS:
            parts.append(f"← [Sheet {n-1}](ch{n-1:02d}-revision.md)")
        parts.append(f"[Full chapter {n}](../{CHAPTERS[n]['path']})")
        parts.append("[All revision material](README.md)")
        if n + 1 in CHAPTERS:
            parts.append(f"[Sheet {n+1}](ch{n+1:02d}-revision.md) →")
        nav.append(" · ".join(parts))
        p.write_text(text + "\n".join(nav) + "\n", encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- headings / contents
def chapter_sections(n):
    """Return [(level, text, anchor)] of the chapter's headings (source sections)."""
    text = (ROOT / CHAPTERS[n]["path"]).read_text(encoding="utf-8").splitlines()
    out, in_fence, seen = [], False, defaultdict(int)
    begin = False
    for l in text:
        if "SOURCE-BEGIN" in l:
            begin = True
        if "SOURCE-END" in l:
            break
        if not begin:
            continue
        if FENCE_RE.match(l):
            in_fence = not in_fence
        if in_fence:
            continue
        m = re.match(r"^(#{2,4})\s+(.*)$", l)
        if m:
            slug = github_slug(m.group(2))
            k = seen[slug]; seen[slug] += 1
            out.append((len(m.group(1)), m.group(2).strip(), slug if k == 0 else f"{slug}-{k}"))
    return out


def build_contents(titles):
    lines = [
        "# Contents",
        "",
        "Complete table of contents of the knowledge base. Chapter numbers equal the response numbers of the original",
        "conversation, so a *Response N* reference anywhere means *Chapter N* here.",
        "",
        "**Reading order for first-time study:** follow the chapter numbers 1 → 36 (the source is already ordered by",
        "dependency). **Topic order for revision:** use the domain sections below.",
        "",
        "## Start here",
        "",
        "- [README](README.md) — what this is and how to use it",
        "- [Study guide](docs/00-start-here/study-guide.md) — recommended path and time plan",
        "- [Course design notes](docs/00-start-here/course-design-notes.md) · [Roadmap](docs/00-start-here/roadmap.md)",
        "",
        "## Reference documents",
        "",
        "- [Glossary](GLOSSARY.md) · [Corrections and ambiguities](CORRECTIONS.md) · [Source coverage matrix](SOURCE_COVERAGE.md)",
        "- [Progress and audit](PROGRESS.md) · [Audit report](AUDIT_REPORT.md)",
        "- [Revision material index](revision/README.md): master cheat sheet, comparisons, formulas, interview Q&A, troubleshooting, traps",
        "- [Hands-on labs](exercises/labs.md) · [Code examples](code-examples/README.md)",
        "",
    ]
    by_domain = OrderedDict((d, []) for d in DOMAINS if d not in ("00-start-here",))
    for n, c in CHAPTERS.items():
        by_domain[c["domain"]].append(n)
    lines += ["## Chapters by domain", ""]
    for d, nums in by_domain.items():
        lines += [f"### {DOMAINS[d]}", ""]
        for n in sorted(nums):
            c = CHAPTERS[n]
            lines.append(f"- **[Chapter {n} — {titles[n]}]({c['path']})** · [revision sheet](revision/ch{n:02d}-revision.md)")
        lines.append("")
    lines += ["## Chapters in study order, with their sections", ""]
    for part, rng in (("Part I — Core curriculum", range(1, 25)), ("Part II — Advanced extension", range(25, 37))):
        lines += [f"### {part}", ""]
        for n in rng:
            c = CHAPTERS[n]
            lines += [f"#### [Chapter {n} — {titles[n]}]({c['path']})", ""]
            for lvl, text, anchor in chapter_sections(n):
                if lvl == 2:
                    lines.append(f"- [{strip_emoji(text) or text}]({c['path']}#{anchor})")
            lines.append("")
    (ROOT / "CONTENTS.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- glossary
def build_glossary():
    entries = defaultdict(list)  # key -> [(term, defn, chs)]
    srcs = [WORK / "glossary_raw.md"] + sorted((WORK / "gl").glob("*.txt"))
    for p in srcs:
        for l in p.read_text(encoding="utf-8").splitlines():
            if "|" not in l:
                continue
            parts = [x.strip() for x in l.rsplit("|", 1)[0].split("|", 1)]
            if len(parts) != 2 or not parts[0] or not parts[1]:
                continue
            ch = l.rsplit("|", 1)[1].strip()
            if not ch.isdigit():
                continue
            term, defn = parts
            entries[term.lower()].append((term, defn, int(ch)))
    lines = [
        "# Glossary",
        "",
        "Terminology, abbreviations and technical vocabulary from all 36 chapters, alphabetical. The number in",
        "brackets is the chapter in which the term is defined or used most clearly; when the same term appears in",
        "several chapters each definition is listed.",
        "",
    ]
    letters = OrderedDict()
    for key in sorted(entries, key=lambda k: re.sub(r"[^a-z0-9]", "", k) or k):
        t = entries[key][0][0]
        first = re.sub(r"[^A-Za-z0-9]", "", t)[:1].upper() or "#"
        if first.isdigit():
            first = "#"
        letters.setdefault(first, []).append(key)
    lines.append("**Jump to:** " + " · ".join(f"[{l}](#{l.lower() if l != '#' else 'symbols'})" for l in letters))
    lines.append("")
    total = 0
    for l, keys in letters.items():
        lines += [f"## {l if l != '#' else 'Symbols'}", ""]
        for key in keys:
            items = entries[key]
            term = items[0][0]
            seen, defs = set(), []
            for _, d, ch in items:
                if (d, ch) in seen:
                    continue
                seen.add((d, ch))
                defs.append((d, ch))
            if len(defs) == 1:
                d, ch = defs[0]
                lines.append(f"- **{term}** — {d} *([Ch {ch}]({CHAPTERS[ch]['path']}))*")
            else:
                lines.append(f"- **{term}**")
                for d, ch in defs:
                    lines.append(f"  - {d} *([Ch {ch}]({CHAPTERS[ch]['path']}))*")
            total += 1
        lines.append("")
    (ROOT / "GLOSSARY.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return total


# ---------------------------------------------------------------- appendix: corrections log
def build_corrections_appendix():
    parts = ["# Corrections and Ambiguities — Chapter-by-Chapter Log", "",
             "Working log kept while reading each response. The curated, categorised summary is in",
             "[CORRECTIONS.md](../../CORRECTIONS.md); this file is the complete record.", ""]
    raw = (WORK / "corrections_raw.md").read_text(encoding="utf-8").splitlines()
    parts += [l.replace("# Raw corrections / ambiguity log (work file)", "") for l in raw if not l.startswith("# Raw")]
    for p in sorted((WORK / "co").glob("ch*.md"), key=lambda x: int(re.search(r"ch(\d+)", x.name).group(1))):
        parts += ["", p.read_text(encoding="utf-8").rstrip()]
    out = ROOT / "docs" / "00-start-here" / "corrections-log-by-chapter.md"
    out.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- search index
def sections_of_md(path, title, kind):
    text = path.read_text(encoding="utf-8").splitlines()
    out, cur, in_fence, seen = [], None, False, defaultdict(int)
    def flush():
        if cur and "".join(cur["lines"]).strip():
            cur["text"] = re.sub(r"\s+", " ", " ".join(cur["lines"])).strip()
            del cur["lines"]
            out.append(cur)
    for l in text:
        if FENCE_RE.match(l):
            in_fence = not in_fence
        m = None if in_fence else re.match(r"^(#{1,4})\s+(.*)$", l)
        if m:
            flush()
            slug = github_slug(m.group(2)); k = seen[slug]; seen[slug] += 1
            cur = {"doc": str(path.relative_to(ROOT)).replace("\\", "/"), "title": title, "kind": kind,
                   "heading": strip_emoji(m.group(2)) or m.group(2), "anchor": slug if k == 0 else f"{slug}-{k}", "lines": []}
        elif cur is not None:
            cur["lines"].append(l)
        else:
            cur = {"doc": str(path.relative_to(ROOT)).replace("\\", "/"), "title": title, "kind": kind,
                   "heading": title, "anchor": "", "lines": [l]}
    flush()
    return out


def build_search_index(titles):
    docs = []
    for n, c in CHAPTERS.items():
        docs += sections_of_md(ROOT / c["path"], f"Chapter {n} — {titles[n]}", "chapter")
        rv = ROOT / "revision" / f"ch{n:02d}-revision.md"
        if rv.exists():
            docs += sections_of_md(rv, f"Revision {n} — {titles[n]}", "revision")
    for p, t in (("GLOSSARY.md", "Glossary"), ("CORRECTIONS.md", "Corrections"), ("README.md", "README"),
                 ("docs/00-start-here/study-guide.md", "Study guide"),
                 ("docs/00-start-here/course-design-notes.md", "Course design notes"),
                 ("docs/00-start-here/roadmap.md", "Roadmap"), ("exercises/labs.md", "Hands-on labs")):
        if (ROOT / p).exists():
            docs += sections_of_md(ROOT / p, t, "reference")
    for p in sorted((ROOT / "revision").glob("[0-9][0-9]-*.md")) + sorted((ROOT / "revision").glob("README.md")):
        docs += sections_of_md(p, "Revision — " + p.stem, "revision")
    (ROOT / "website" / "data").mkdir(parents=True, exist_ok=True)
    (ROOT / "website" / "data" / "search-index.json").write_text(json.dumps(docs, ensure_ascii=False), encoding="utf-8")
    nav = {
        "chapters": [{"n": n, "title": titles[n], "path": c["path"], "domain": c["domain"],
                      "domainTitle": DOMAINS[c["domain"]], "part": c["part"],
                      "revision": f"revision/ch{n:02d}-revision.md"} for n, c in CHAPTERS.items()],
        "domains": [{"id": d, "title": t} for d, t in DOMAINS.items() if d != "00-start-here"],
    }
    (ROOT / "website" / "data" / "nav.json").write_text(json.dumps(nav, ensure_ascii=False, indent=1), encoding="utf-8")
    return len(docs)


# ---------------------------------------------------------------- code extraction
EXT = {"dockerfile": "Dockerfile", "yaml": "yaml", "yml": "yaml", "hcl": "tf", "groovy": "Jenkinsfile", "json": "json",
       "typescript": "ts", "ts": "ts", "javascript": "js", "ini": "ini", "jinja2": "j2", "gitignore": "gitignore",
       "env": "env", "bash": "sh", "sh": "sh", "http": "http", "promql": "promql"}


def build_code_examples(titles):
    root = ROOT / "code-examples" / "extracted"
    if root.exists():
        for f in root.rglob("*"):
            if f.is_file():
                f.unlink()
    index = []
    count = 0
    for n, c in CHAPTERS.items():
        lines = (ROOT / c["path"]).read_text(encoding="utf-8").splitlines()
        begin = next(i for i, l in enumerate(lines) if "SOURCE-BEGIN" in l)
        end = next(i for i, l in enumerate(lines) if "SOURCE-END" in l)
        i, k = begin, 0
        while i < end:
            m = re.match(r"^```([A-Za-z0-9_+-]+)\s*$", lines[i])
            if m:
                lang = m.group(1).lower()
                j = i + 1
                while j < end and not FENCE_RE.match(lines[j]):
                    j += 1
                block = lines[i + 1:j]
                nonempty = [b for b in block if b.strip()]
                keep = lang in EXT and (
                    len(nonempty) >= (8 if lang in ("bash", "sh") else 4)
                    and (lang not in ("bash", "sh") or any(b.startswith("#!") for b in block) or len(nonempty) >= 12)
                )
                if keep:
                    k += 1
                    ext = EXT[lang]
                    first = next((b for b in nonempty if not b.lstrip().startswith(("#", "//"))), nonempty[0])
                    slug = re.sub(r"[^a-z0-9]+", "-", first.lower()).strip("-")[:32] or "block"
                    name = f"{k:02d}-{slug}.{ext}" if ext not in ("Jenkinsfile", "Dockerfile") else f"{k:02d}-{slug}.{ext.lower()}"
                    d = root / f"ch{n:02d}"
                    d.mkdir(parents=True, exist_ok=True)
                    (d / name).write_text("\n".join(block) + "\n", encoding="utf-8", newline="\n")
                    index.append((n, name, lang, len(block), i + 1))
                    count += 1
                i = j
            i += 1
    lines = ["# Extracted Code Examples", "",
             "Every substantial code block from the chapters (Dockerfiles, YAML, Terraform, Jenkinsfiles, JSON, TypeScript,",
             "shell scripts, INI/Jinja templates) extracted to its own file so it can be copied or linted. These are",
             "**source-derived** and many are deliberately simplified or contain placeholders (`...`, `<account-id>`) —",
             "read the surrounding chapter before using them. The last column links to the block in the chapter.", "",
             "| Chapter | File | Language | Lines | In chapter |", "|---|---|---|---:|---|"]
    for n, name, lang, nl, ln in index:
        lines.append(f"| {n} — {titles[n]} | [`ch{n:02d}/{name}`](extracted/ch{n:02d}/{name}) | {lang} | {nl} | "
                     f"[line {ln}](../{CHAPTERS[n]['path']}) |")
    (ROOT / "code-examples" / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return count


def main():
    trims, extra = load_trims()
    titles, meta = build_chapters(trims, extra)
    build_course_notes()
    build_removed_appendix(trims, extra)
    fix_revision_links(titles)
    build_contents(titles)
    g = build_glossary()
    build_corrections_appendix()
    s = build_search_index(titles)
    c = build_code_examples(titles)
    (WORK / "build-meta.json").write_text(json.dumps({"titles": titles, "meta": meta}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"chapters={len(CHAPTERS)} glossary_terms={g} search_sections={s} code_files={c}")


if __name__ == "__main__":
    main()
