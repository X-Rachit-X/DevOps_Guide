# DevOps for SDEs — Knowledge Base

A complete, organised and searchable knowledge base for software engineers learning **Linux → Git → CI/CD → Docker → AWS → Kubernetes → Terraform → GitOps → observability/SRE → virtualization internals**, built from a long educational conversation (36 source responses). It is meant to be the primary study resource for online assessments (OAs), interviews, revision, hands-on practice and long-term reference.

> **Honest status:** every source file with content is imported **line for line** (a source→output audit confirms it), and everything the editor added is clearly separated from the original text. Read [PROGRESS.md](PROGRESS.md) for what is verified, what is not, and what is still open before relying on any claim of completeness.

## What is in the repository

| Path | What it is |
|---|---|
| [`docs/`](docs/) | **The canonical content.** 36 chapters (`docs/<domain>/chNN-*.md`), the original text with only documented, mechanical changes, plus start-here documents |
| [`revision/`](revision/README.md) | One **revision sheet per chapter** + cross-cutting sheets: master cheat sheet, comparisons, formulas/numbers, interview Q&A, troubleshooting playbooks, traps |
| [`supplements/`](supplements/) | Editorial additions that fill gaps in the source (appended to chapters under "Editorial supplement") |
| [`exercises/labs.md`](exercises/labs.md) | Index of the source's hands-on labs + editorial practice tasks |
| [`code-examples/`](code-examples/README.md) | Every substantial code block extracted to its own file, plus a small [capstone reference starter](code-examples/capstone/README.md) |
| [`website/`](website/) | Static viewer (landing page, TOC, search, prev/next, copy buttons, light/dark, progress tracking, responsive) |
| [`GLOSSARY.md`](GLOSSARY.md) | Terminology from all chapters |
| [`CONTENTS.md`](CONTENTS.md) | Full table of contents with every section |
| [`CORRECTIONS.md`](CORRECTIONS.md) | Technical corrections, imprecisions, version-sensitive facts, source defects |
| [`SOURCE_COVERAGE.md`](SOURCE_COVERAGE.md) | Response-by-response coverage matrix |
| [`AUDIT_REPORT.md`](AUDIT_REPORT.md) | Generated audit results (fidelity, links, code checks) |
| [`PROGRESS.md`](PROGRESS.md) | What was done, verified, and what remains |
| [`source-archive/`](source-archive/) | The untouched source text (provenance; the audit compares against it) |
| `tools/` | `build.py` (generate), `audit.py` (verify), `gen_*.py`, `test_website.py` |

## How to study

1. Start with the [study guide](docs/00-start-here/study-guide.md) (a 10-week plan and an interview-prep sequence).
2. Read each **chapter** once; use its **revision sheet** afterwards.
3. Do the [labs](exercises/labs.md); the source insists that reading without doing is not learning.
4. Before interviews: [master cheat sheet](revision/00-master-cheatsheet.md), [comparisons](revision/01-comparisons.md), [Q&A bank](revision/03-interview-qa.md), [troubleshooting playbooks](revision/04-troubleshooting-playbooks.md).

## Run the website locally

The site renders the repository's Markdown in your browser. It needs an HTTP server rooted at the **repository root** (browsers block `fetch` from `file://`):

```bash
cd knowledge-base
python -m http.server 8000
# open http://localhost:8000/website/
```

No build step or `npm install` is needed: the two libraries it uses (`marked`, `highlight.js`) are vendored in `website/vendor/` with their licences. Features: sidebar navigation (by topic or by number), full-text search (`/` focuses the box), table of contents per page, previous/next, **Full notes ↔ Revision sheet** toggle, copy buttons on code blocks, light/dark theme, per-chapter completion tracking (stored in your browser only), responsive layout.

## Rebuild and verify

```bash
python -X utf8 tools/build.py        # regenerate chapters, contents, glossary, indexes, extracted code
python -X utf8 tools/audit.py        # independent source→output audit  → AUDIT_REPORT.md
python -X utf8 tools/gen_coverage.py # SOURCE_COVERAGE.md
python -X utf8 tools/gen_labs.py     # exercises/labs.md
python -m http.server 8765 &         # then:
python -X utf8 tools/test_website.py --crawl   # headless-browser tests (needs selenium + Edge/Chrome)
```

Requires Python 3.10+ with `PyYAML` (audit only). Do **not** edit generated chapter files by hand: change `source-archive/`-derived content through `_work/trims.csv`, add editorial text in `supplements/` or `revision/`, then rebuild.

## What changed from the source (and nothing else)

Chapter files differ from the source only by: removal of chat scaffolding (progress tables, "next response" teasers, replies to meta-questions — all kept verbatim in [removed-scaffolding.md](docs/00-start-here/removed-scaffolding.md) and [course-design-notes.md](docs/00-start-here/course-design-notes.md)); header rewritten to `# Chapter N — Title`; tool-generated `id="…"` attributes stripped from code fences; "Response N" renamed to "Chapter N" and linked; heading levels demoted by one; the body wrapped in `<!-- SOURCE-BEGIN/END -->` markers; and the optional supplement appended after the end marker. Everything between the markers is source text.

## Publish to GitHub (not done automatically)

Nothing has been committed or pushed. To publish yourself:

```bash
cd knowledge-base
git init                      # if not already a repository
git add .
git commit -m "Add DevOps for SDEs knowledge base"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

To host the website on **GitHub Pages**: repository *Settings → Pages → Build and deployment → Deploy from a branch → `main` / `(root)`*. The site is then at `https://<you>.github.io/<repo>/website/` (it loads the Markdown through relative paths, so the repo root must be the Pages root). Add a `LICENSE` of your choice first — **no licence has been chosen**, and the source material's provenance/rights are yours to confirm before publishing.

## Known limits

- The source has **no "Response 36 — Final DevOps Mastery"** (promised at the end of Chapter 35). Source file 36 is a different response (virtualization internals), and files 37–40 are empty. Chapter 35 is a design specification; the [capstone starter](code-examples/capstone/README.md) is editorial and was only type-checked, not run end to end.
- Version-specific facts (prices, API versions, tool versions) are flagged for verification in [CORRECTIONS.md](CORRECTIONS.md); only the items marked *Verified* were checked against official documentation.
- Terraform, Dockerfile, TypeScript, Helm and Jenkins snippets were not executed; only YAML, JSON and Bash are machine-checked.
