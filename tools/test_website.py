#!/usr/bin/env python
"""End-to-end test of the website in headless Edge via Selenium.

Usage:  python -X utf8 tools/test_website.py [--base http://127.0.0.1:8765] [--crawl] [--shots DIR]
Start a server first from the repo root:  python -m http.server 8765
Writes _work/website-test.json (and _work/website-crawl.json with --crawl) and prints a pass/fail list.
"""
import argparse
import json
import sys
import time
from pathlib import Path
from urllib.parse import unquote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--base", default="http://127.0.0.1:8765")
ap.add_argument("--crawl", action="store_true", help="load every chapter/revision/doc and validate all internal links+anchors")
ap.add_argument("--shots", default="", help="directory for screenshots")
args = ap.parse_args()
SITE = args.base + "/website/"

results = []


def check(name, ok, detail=""):
    results.append({"test": name, "ok": bool(ok), "detail": str(detail)[:300]})
    print(("PASS " if ok else "FAIL ") + name + (("  -> " + str(detail)[:200]) if (detail and not ok) else ""))


def make_driver(width=1400, height=900):
    o = webdriver.EdgeOptions()
    o.add_argument("--headless=new")
    o.add_argument("--disable-gpu")
    o.add_argument(f"--window-size={width},{height}")
    o.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    return webdriver.Edge(options=o)


def wait_content(d, css="#content article, #content .hero, #content .result, #content .notice, #content h1", t=20):
    WebDriverWait(d, t).until(lambda x: x.find_elements(By.CSS_SELECTOR, css))
    time.sleep(0.4)


def go(d, route):
    d.execute_script("window.location.hash = arguments[0]", route)
    time.sleep(0.3)


d = make_driver()
try:
    d.get(SITE)
    wait_content(d)
    check("home: title", "DevOps" in d.title, d.title)
    check("home: 9 topic cards", len(d.find_elements(By.CSS_SELECTOR, ".card")) == 9, len(d.find_elements(By.CSS_SELECTOR, ".card")))
    nav = json.loads((ROOT / "website/data/nav.json").read_text(encoding="utf-8"))
    n_ch = len(nav["chapters"])
    check("sidebar lists every chapter", len(d.find_elements(By.CSS_SELECTOR, "#sidebar a[data-n]")) == n_ch,
          len(d.find_elements(By.CSS_SELECTOR, "#sidebar a[data-n]")))
    check("progress pill starts 0/N", d.find_element(By.ID, "progress-pill").text == f"0 / {n_ch}", d.find_element(By.ID, "progress-pill").text)

    # chapter view
    go(d, "/c/12")
    wait_content(d, "#content article h1")
    h1 = d.find_element(By.CSS_SELECTOR, "#content article h1").text
    check("chapter 12 renders title", h1.startswith("Chapter 12"), h1)
    check("chapter has heading ids", len(d.find_elements(By.CSS_SELECTOR, "#content article h2[id]")) > 20)
    check("chapter has code blocks", len(d.find_elements(By.CSS_SELECTOR, "#content pre code")) > 50)
    check("copy buttons on every code block",
          len(d.find_elements(By.CSS_SELECTOR, "#content pre .copy-btn")) == len(d.find_elements(By.CSS_SELECTOR, "#content pre")))
    check("TOC built", len(d.find_elements(By.CSS_SELECTOR, "#toc a")) > 10)
    check("prev/next pager", len(d.find_elements(By.CSS_SELECTOR, ".pager a")) == 2)
    check("sidebar highlights current chapter", d.find_element(By.CSS_SELECTOR, "#sidebar a.active").get_attribute("data-n") == "12")
    check("revision toggle present", len(d.find_elements(By.CSS_SELECTOR, ".view-switch a")) == 2)
    go(d, "/c/6")
    time.sleep(1.5)
    wait_content(d, "#content article h1")
    time.sleep(1.0)
    check("syntax highlighting applied (chapter 6, YAML/bash)", len(d.find_elements(By.CSS_SELECTOR, "#content pre code.hljs")) >= 3,
          len(d.find_elements(By.CSS_SELECTOR, "#content pre code.hljs")))
    go(d, "/c/12")
    time.sleep(1.0)
    wait_content(d, "#content article h1")

    btn = d.find_element(By.CSS_SELECTOR, "#content pre .copy-btn")
    d.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", btn)
    time.sleep(0.5)
    label = btn.get_attribute("textContent")
    check("copy button gives feedback", label in ("Copied ✓", "Copy failed"), label)

    toc_links = d.find_elements(By.CSS_SELECTOR, "#toc a")
    target = toc_links[len(toc_links) // 2]
    anchor = unquote(target.get_attribute("href").split("~", 1)[1])
    d.execute_script("window.scrollTo(0,0)")
    d.execute_script("arguments[0].click()", target)
    time.sleep(0.8)
    top = d.execute_script("var e=document.getElementById(arguments[0]); return e ? e.getBoundingClientRect().top : null", anchor)
    check("TOC click scrolls to heading", top is not None and -5 <= top < 400, top)

    d.execute_script("arguments[0].click()", d.find_element(By.CSS_SELECTOR, ".pager a.next"))
    time.sleep(1.0)
    wait_content(d, "#content article h1")
    t = d.find_element(By.CSS_SELECTOR, "#content article h1").text
    check("next navigates to chapter 13", t.startswith("Chapter 13"), t)

    go(d, "/r/13")
    time.sleep(1.0)
    wait_content(d, "#content article h1")
    t = d.find_element(By.CSS_SELECTOR, "#content article h1").text
    check("revision sheet renders", t.startswith("Chapter 13"), t)

    go(d, "/c/36")
    time.sleep(1.2)
    wait_content(d, "#content article h1")
    check("chapter 36 renders", "Virtualization" in d.find_element(By.CSS_SELECTOR, "#content article h1").text)

    go(d, "/d/revision/README.md")
    time.sleep(1.0)
    wait_content(d, "#content article h1")
    links = [a.get_attribute("href") for a in d.find_elements(By.CSS_SELECTOR, "#content article a")]
    check("md links rewritten to hash routes", sum(1 for h in links if "#/r/" in h or "#/d/" in h) >= 10, links[:5])

    inp = d.find_element(By.ID, "search-input")
    inp.clear()
    inp.send_keys("ballooning")
    WebDriverWait(d, 20).until(lambda x: x.find_elements(By.CSS_SELECTOR, "#content .result"))
    time.sleep(0.3)
    res = d.find_elements(By.CSS_SELECTOR, "#content .result a")
    check("search finds results", len(res) >= 3, len(res))
    check("search hits Chapter 36", any(("/c/36" in r.get_attribute("href")) or ("/r/36" in r.get_attribute("href")) for r in res),
          [r.get_attribute("href") for r in res[:4]])
    d.execute_script("arguments[0].click()", res[0])
    time.sleep(1.5)
    check("search result opens section", "#/c/" in d.current_url or "#/r/" in d.current_url or "#/d/" in d.current_url, d.current_url)

    before = d.find_element(By.TAG_NAME, "html").get_attribute("data-theme")
    d.execute_script("document.getElementById('theme-btn').click()")
    time.sleep(0.3)
    after = d.find_element(By.TAG_NAME, "html").get_attribute("data-theme")
    saved = d.execute_script("return localStorage.getItem('kb-theme')")
    check("theme toggles and persists", before != after and saved == after, (before, after, saved))
    check("code theme stylesheet swapped", ("dark" in d.find_element(By.ID, "hljs-theme").get_attribute("href")) == (after == "dark"))
    if args.shots:
        Path(args.shots).mkdir(parents=True, exist_ok=True)
        d.save_screenshot(str(Path(args.shots) / "chapter-theme.png"))

    go(d, "/c/5")
    time.sleep(1.0)
    wait_content(d, "#done-box")
    cb = d.find_element(By.ID, "done-box")
    d.execute_script("arguments[0].click()", cb)
    time.sleep(0.3)
    pill = d.find_element(By.ID, "progress-pill").text
    check("progress pill increments", pill == f"1 / {n_ch}", pill)
    d.refresh()
    wait_content(d, "#content article h1")
    time.sleep(0.8)
    pill = d.find_element(By.ID, "progress-pill").text
    check("progress survives reload", pill == f"1 / {n_ch}", pill)
    check("sidebar shows done mark", len(d.find_elements(By.CSS_SELECTOR, "#sidebar a.done")) == 1)
    d.execute_script("localStorage.clear()")

    go(d, "/")
    time.sleep(0.8)
    d.find_element(By.TAG_NAME, "body").send_keys("/")
    time.sleep(0.3)
    check("'/' focuses search", d.execute_script("return document.activeElement.id") == "search-input")

    go(d, "/zzz")
    time.sleep(0.6)
    check("unknown route handled", "Not found" in d.find_element(By.ID, "content").text)
    go(d, "/c/999")
    time.sleep(0.8)
    check("unknown chapter handled", "Unknown chapter" in d.find_element(By.ID, "content").text)

    if args.crawl:
        pages = [f"/c/{c['n']}" for c in nav["chapters"]] + [f"/r/{c['n']}" for c in nav["chapters"]]
        docs = ["README.md", "CONTENTS.md", "GLOSSARY.md", "CORRECTIONS.md", "SOURCE_COVERAGE.md", "PROGRESS.md", "AUDIT_REPORT.md",
                "docs/00-start-here/study-guide.md", "docs/00-start-here/roadmap.md", "docs/00-start-here/course-design-notes.md",
                "docs/00-start-here/corrections-log-by-chapter.md", "exercises/labs.md", "code-examples/README.md",
                "code-examples/capstone/README.md", "revision/README.md", "code-examples/INDEX.md",
                "docs/00-start-here/removed-scaffolding.md"]
        docs += sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in (ROOT / "supplements").glob("ch*.md"))
        docs += sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in (ROOT / "revision").glob("[0-9][0-9]-*.md"))
        pages += ["/d/" + x for x in docs]
        ids, hrefs, errors = {}, {}, []
        for p in pages:
            d.execute_script("window.location.hash = arguments[0]", p)
            try:
                WebDriverWait(d, 60).until(lambda x: x.execute_script(
                    "return document.querySelectorAll('#content article h1, #content .notice').length>0 && decodeURIComponent(location.hash).indexOf(arguments[0])>=0", p))
            except Exception:
                errors.append((p, "timeout"))
                continue
            time.sleep(0.2)
            if d.find_elements(By.CSS_SELECTOR, "#content .notice"):
                errors.append((p, d.find_element(By.CSS_SELECTOR, "#content .notice").text[:100]))
                continue
            ids[p] = set(d.execute_script("return Array.from(document.querySelectorAll('#content [id]')).map(function(e){return e.id})"))
            hrefs[p] = d.execute_script("return Array.from(document.querySelectorAll('#content article a[href]')).map(function(a){return a.getAttribute('href')})")
        check(f"crawl: all {len(pages)} pages load", not errors, errors[:5])
        bad = []
        for p, hs in hrefs.items():
            for h in hs:
                if not h.startswith("#/"):
                    continue
                raw = unquote(h[1:])
                route, _, anc = raw.partition("~")
                if route not in ids:
                    if route.startswith(("/c/", "/r/", "/d/")) and route not in pages:
                        bad.append((p, h, "route not in crawl set"))
                    continue
                if anc and anc not in ids[route]:
                    bad.append((p, h, "anchor missing"))
        check("crawl: all internal links and anchors resolve", not bad, bad[:8])
        (ROOT / "_work" / "website-crawl.json").write_text(json.dumps({"pages": len(pages), "bad": bad, "errors": errors}, indent=1), encoding="utf-8")
        print(f"crawl: pages={len(pages)} links_checked={sum(len(v) for v in hrefs.values())} bad={len(bad)}")

    logs = d.get_log("browser")
    severe = [l for l in logs if l.get("level") == "SEVERE" and "favicon" not in l.get("message", "")]
    check("no severe browser console errors", not severe, severe[:3])
finally:
    d.quit()

m = make_driver(390, 844)
try:
    m.get(SITE + "#/c/12")
    wait_content(m, "#content article h1")
    check("mobile: no horizontal page overflow",
          m.execute_script("return document.documentElement.scrollWidth <= window.innerWidth + 1"),
          m.execute_script("return [document.documentElement.scrollWidth, window.innerWidth]"))
    check("mobile: menu button visible", m.find_element(By.ID, "menu-btn").is_displayed())
    check("mobile: sidebar off-screen initially", m.execute_script("return document.getElementById('sidebar').getBoundingClientRect().right <= 1"))
    m.execute_script("document.getElementById('menu-btn').click()")
    time.sleep(0.6)
    check("mobile: sidebar opens", m.execute_script("return document.getElementById('sidebar').getBoundingClientRect().left >= -1"))
    if args.shots:
        m.save_screenshot(str(Path(args.shots) / "mobile-nav.png"))
finally:
    m.quit()

(ROOT / "_work" / "website-test.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
fails = [r for r in results if not r["ok"]]
print(f"\n{len(results) - len(fails)}/{len(results)} checks passed")
sys.exit(1 if fails else 0)
