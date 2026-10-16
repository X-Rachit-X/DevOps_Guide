/* DevOps for SDEs — Knowledge Base viewer.
 * A dependency-light single-page app that renders the repository's canonical Markdown in the browser.
 * It fetches files relative to the repository root (the parent of /website/), so serve the repo root:
 *     python -m http.server 8000        then open http://localhost:8000/website/
 */
(function () {
  'use strict';

  // ------------------------------------------------------------------ helpers
  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* storage unavailable: app still works */ } },
  };
  const repoBase = new URL('../', document.baseURI);
  const SITE = 'DevOps for SDEs';

  const REFERENCE = [
    ['Start here', [
      ['Home', '/'],
      ['README', '/d/README.md'],
      ['Study guide', '/d/docs/00-start-here/study-guide.md'],
      ['Roadmap', '/d/docs/00-start-here/roadmap.md'],
      ['Course design notes', '/d/docs/00-start-here/course-design-notes.md'],
      ['Full contents', '/d/CONTENTS.md'],
    ]],
    ['Revision', [
      ['Revision hub', '/d/revision/README.md'],
      ['Master cheat sheet', '/d/revision/00-master-cheatsheet.md'],
      ['Comparisons (X vs Y)', '/d/revision/01-comparisons.md'],
      ['Formulas and numbers', '/d/revision/02-formulas-and-numbers.md'],
      ['Interview Q&A bank', '/d/revision/03-interview-qa.md'],
      ['Troubleshooting playbooks', '/d/revision/04-troubleshooting-playbooks.md'],
      ['Traps and misconceptions', '/d/revision/05-traps-and-misconceptions.md'],
      ['Hands-on labs', '/d/exercises/labs.md'],
    ]],
    ['Reference', [
      ['Glossary', '/d/GLOSSARY.md'],
      ['Corrections', '/d/CORRECTIONS.md'],
      ['Source coverage', '/d/SOURCE_COVERAGE.md'],
      ['Progress and status', '/d/PROGRESS.md'],
      ['Audit report', '/d/AUDIT_REPORT.md'],
      ['Code examples', '/d/code-examples/README.md'],
      ['Capstone starter', '/d/code-examples/capstone/README.md'],
      ['Full corrections log', '/d/docs/00-start-here/corrections-log-by-chapter.md'],
      ['Removed scaffolding', '/d/docs/00-start-here/removed-scaffolding.md'],
    ]],
  ];

  // ------------------------------------------------------------------ state
  let nav = null;            // data/nav.json
  let chapters = [];
  let byNum = {};
  let progress = store.get('kb-progress', {});
  let sbMode = store.get('kb-sbmode', 'topic');
  let currentKey = null;     // route key without anchor
  let searchIndex = null;
  const cache = new Map();   // path -> markdown text
  let spy = null;

  // ------------------------------------------------------------------ slug (matches tools/registry.py github_slug)
  const EMOJI = /[\u{1F000}-\u{1FFFF}☀-➿️‍⬀-⯿]+/gu;
  function slugify(text) {
    let t = text.replace(EMOJI, '').replace(/\s+/g, ' ').trim().toLowerCase();
    t = t.replace(/[^\p{L}\p{N}_\s-]/gu, '');
    return t.trim().replace(/ /g, '-');
  }

  // ------------------------------------------------------------------ routing
  function parseHash() {
    const raw = decodeURIComponent((location.hash || '#/').slice(1)) || '/';
    const i = raw.indexOf('~');
    const path = i >= 0 ? raw.slice(0, i) : raw;
    const anchor = i >= 0 ? raw.slice(i + 1) : '';
    const parts = path.split('/').filter(Boolean);
    return { path: '/' + parts.join('/'), parts, anchor };
  }
  function mdRoute(rel) {
    let m = rel.match(/^docs\/[^/]+\/ch(\d\d)-[^/]+\.md$/);
    if (m) return '/c/' + Number(m[1]);
    m = rel.match(/^revision\/ch(\d\d)-revision\.md$/);
    if (m) return '/r/' + Number(m[1]);
    return '/d/' + rel;
  }
  const hashFor = (route, anchor) => '#' + route + (anchor ? '~' + anchor : '');

  async function fetchText(path) {
    if (cache.has(path)) return cache.get(path);
    const res = await fetch(new URL(path, repoBase));
    if (!res.ok) throw new Error(path + ' → HTTP ' + res.status);
    const txt = await res.text();
    cache.set(path, txt);
    return txt;
  }

  // ------------------------------------------------------------------ theme
  function applyTheme(t) {
    document.documentElement.setAttribute('data-theme', t);
    const link = $('#hljs-theme');
    if (link) link.setAttribute('href', 'vendor/hljs-' + (t === 'dark' ? 'dark' : 'light') + '.css');
  }
  function toggleTheme() {
    const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    try { localStorage.setItem('kb-theme', next); } catch (e) { /* ignore */ }
  }

  // ------------------------------------------------------------------ progress
  function doneCount() { return chapters.filter((c) => progress[c.n]).length; }
  function updateProgressUI() {
    const pill = $('#progress-pill');
    if (pill) pill.textContent = doneCount() + ' / ' + chapters.length;
    $$('#sidebar a[data-n]').forEach((a) => a.classList.toggle('done', !!progress[a.dataset.n]));
  }
  function setDone(n, v) {
    if (v) progress[n] = true; else delete progress[n];
    store.set('kb-progress', progress);
    updateProgressUI();
  }

  // ------------------------------------------------------------------ sidebar
  function chapterLink(c) {
    const a = document.createElement('a');
    a.href = hashFor('/c/' + c.n);
    a.dataset.n = c.n;
    a.dataset.route = '/c/' + c.n;
    a.innerHTML = '<span class="num">' + c.n + '</span><span>' + esc(c.title) + '</span>';
    return a;
  }
  function group(title, items, collapsed) {
    const g = document.createElement('div');
    g.className = 'sb-group' + (collapsed ? ' collapsed' : '');
    const t = document.createElement('div');
    t.className = 'sb-title';
    t.textContent = title;
    t.setAttribute('role', 'button');
    t.tabIndex = 0;
    const toggle = () => g.classList.toggle('collapsed');
    t.addEventListener('click', toggle);
    t.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } });
    const ul = document.createElement('ul');
    items.forEach((a) => { const li = document.createElement('li'); li.appendChild(a); ul.appendChild(li); });
    g.append(t, ul);
    return g;
  }
  function buildSidebar() {
    const sb = $('#sidebar');
    sb.innerHTML = '';
    const mode = document.createElement('div');
    mode.className = 'sb-mode';
    [['topic', 'By topic'], ['number', 'By number']].forEach(([k, label]) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = label;
      b.setAttribute('aria-pressed', String(sbMode === k));
      b.addEventListener('click', () => { sbMode = k; store.set('kb-sbmode', k); buildSidebar(); });
      mode.appendChild(b);
    });
    sb.appendChild(mode);
    REFERENCE.forEach(([title, links], i) => {
      sb.appendChild(group(title, links.map(([label, route]) => {
        const a = document.createElement('a');
        a.href = hashFor(route);
        a.dataset.route = route;
        a.innerHTML = '<span>' + esc(label) + '</span>';
        return a;
      }), i > 0));
    });
    if (sbMode === 'topic') {
      nav.domains.forEach((d) => {
        const cs = chapters.filter((c) => c.domain === d.id).sort((a, b) => a.n - b.n);
        if (cs.length) sb.appendChild(group(d.title, cs.map(chapterLink)));
      });
    } else {
      [['I', 'Part I — Core curriculum'], ['II', 'Part II — Advanced extension']].forEach(([p, title]) => {
        const cs = chapters.filter((c) => c.part === p).sort((a, b) => a.n - b.n);
        if (cs.length) sb.appendChild(group(title, cs.map(chapterLink)));
      });
    }
    updateProgressUI();
    highlightNav();
  }
  function highlightNav() {
    const route = currentKey ? currentKey.replace(/^\/r\//, '/c/') : null;
    $$('#sidebar a').forEach((a) => {
      const on = a.dataset.route === route || a.dataset.route === currentKey;
      a.classList.toggle('active', on);
      if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
  }
  function openNav(open) {
    document.body.classList.toggle('nav-open', open);
    $('#scrim').hidden = !open;
    $('#menu-btn').setAttribute('aria-expanded', String(open));
  }

  // ------------------------------------------------------------------ markdown post-processing
  function highlightBlocks(root) {
    if (!window.hljs) return;
    const alias = { dockerfile: 'bash', hcl: 'ini', terraform: 'ini', groovy: 'javascript', jinja2: 'xml', env: 'ini', gitignore: 'plaintext', http: 'plaintext', promql: 'plaintext', text: null, txt: null };
    const blocks = $$('pre code', root);
    let i = 0;
    (function chunk() {
      const end = Math.min(i + 25, blocks.length);
      for (; i < end; i++) {
        const code = blocks[i];
        const m = (code.className || '').match(/language-([\w+-]+)/);
        let lang = m ? m[1].toLowerCase() : null;
        if (lang && Object.prototype.hasOwnProperty.call(alias, lang)) lang = alias[lang];
        if (lang && lang !== 'plaintext' && hljs.getLanguage(lang)) {
          try { hljs.highlightElement(code); } catch (e) { /* leave plain */ }
        }
      }
      if (i < blocks.length) setTimeout(chunk, 0);
    })();
  }
  function addCopyButtons(root) {
    $$('pre', root).forEach((pre) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'copy-btn';
      btn.textContent = 'Copy';
      btn.setAttribute('aria-label', 'Copy code to clipboard');
      btn.addEventListener('click', async () => {
        const text = (pre.querySelector('code') || pre).textContent;
        let ok = false;
        try { await navigator.clipboard.writeText(text); ok = true; } catch (e) {
          const ta = document.createElement('textarea');
          ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
          document.body.appendChild(ta); ta.select();
          try { ok = document.execCommand('copy'); } catch (e2) { ok = false; }
          ta.remove();
        }
        btn.textContent = ok ? 'Copied ✓' : 'Copy failed';
        setTimeout(() => { btn.textContent = 'Copy'; }, 1500);
      });
      pre.appendChild(btn);
    });
  }
  function addHeadingAnchors(root, route) {
    const seen = {};
    $$('h1,h2,h3,h4,h5,h6', root).forEach((h) => {
      const base = slugify(h.textContent);
      if (!base) return;
      const k = seen[base] || 0;
      seen[base] = k + 1;
      h.id = k === 0 ? base : base + '-' + k;
      const a = document.createElement('a');
      a.className = 'anchor';
      a.href = hashFor(route, h.id);
      a.textContent = '#';
      a.setAttribute('aria-label', 'Link to this section');
      h.appendChild(a);
    });
  }
  function rewriteLinks(root, docPath, route) {
    const docUrl = new URL(docPath, repoBase);
    $$('a[href]', root).forEach((a) => {
      if (a.classList.contains('anchor')) return;
      const href = a.getAttribute('href');
      if (href.startsWith('#')) { a.setAttribute('href', hashFor(route, decodeURIComponent(href.slice(1)))); return; }
      let u;
      try { u = new URL(href, docUrl); } catch (e) { return; }
      const inRepo = u.origin === location.origin && u.pathname.startsWith(repoBase.pathname);
      if (!inRepo) { a.target = '_blank'; a.rel = 'noopener noreferrer'; return; }
      const rel = decodeURIComponent(u.pathname.slice(repoBase.pathname.length));
      if (rel.endsWith('.md')) {
        a.setAttribute('href', hashFor(mdRoute(rel), u.hash ? decodeURIComponent(u.hash.slice(1)) : ''));
      } else {
        a.setAttribute('href', u.href);
        a.target = '_blank';
        a.rel = 'noopener';
      }
    });
  }
  function buildToc(root) {
    const toc = $('#toc');
    toc.innerHTML = '';
    if (spy) { spy.disconnect(); spy = null; }
    if (!root) return;
    const hs = $$('h2,h3', root).filter((h) => h.id);
    if (hs.length < 3) return;
    const title = document.createElement('h4');
    title.textContent = 'On this page';
    toc.appendChild(title);
    const links = new Map();
    hs.forEach((h) => {
      const a = document.createElement('a');
      a.href = hashFor(currentKey, h.id);
      a.className = h.tagName === 'H3' ? 'l3' : 'l2';
      a.textContent = h.textContent.replace(/#$/, '');
      toc.appendChild(a);
      links.set(h, a);
    });
    spy = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { links.forEach((a) => a.classList.remove('active')); const a = links.get(e.target); if (a) a.classList.add('active'); } });
    }, { rootMargin: '-70px 0px -75% 0px' });
    hs.forEach((h) => spy.observe(h));
  }
  function renderMarkdownInto(container, md, docPath, route) {
    container.innerHTML = marked.parse(md, { gfm: true, breaks: false });
    container.classList.add('md');
    addHeadingAnchors(container, route);
    rewriteLinks(container, docPath, route);
    addCopyButtons(container);
    highlightBlocks(container);
  }

  // ------------------------------------------------------------------ views
  function setTitle(t) { document.title = (t ? t + ' — ' : '') + SITE; }
  function scrollToAnchor(anchor) {
    if (anchor) {
      const t = document.getElementById(anchor);
      if (t) { t.scrollIntoView(); return; }
    }
    window.scrollTo(0, 0);
  }
  function fail(content, err) {
    const proto = location.protocol === 'file:'
      ? '<p>This page was opened from <code>file://</code>, where browsers block loading the Markdown files. Serve the repository root instead:</p><pre><code>python -m http.server 8000\n# then open http://localhost:8000/website/</code></pre>'
      : '';
    content.innerHTML = '<div class="notice"><strong>Could not load this page.</strong><br>' + esc(err.message || err) + '</div>' + proto;
    buildToc(null);
  }

  function pagerHtml(n, kind) {
    const prev = byNum[n - 1], next = byNum[n + 1];
    const mk = (c, cls, label) => c
      ? '<a class="' + cls + '" href="' + hashFor('/' + kind + '/' + c.n) + '"><small>' + label + '</small>' + c.n + '. ' + esc(c.title) + '</a>'
      : '<span style="flex:1"></span>';
    return '<div class="pager">' + mk(prev, 'prev', '← Previous') + mk(next, 'next', 'Next →') + '</div>';
  }

  async function viewChapter(n, kind, anchor, content) {
    const c = byNum[n];
    if (!c) { content.innerHTML = '<p>Unknown chapter.</p>'; return; }
    const path = kind === 'r' ? c.revision : c.path;
    const route = '/' + kind + '/' + n;
    const md = await fetchText(path);
    content.innerHTML = '';
    const head = document.createElement('div');
    head.innerHTML =
      '<div class="crumbs">' + esc(c.domainTitle) + ' · Part ' + c.part + ' · Chapter ' + c.n + '</div>' +
      '<div class="view-switch" role="group" aria-label="View">' +
      '<a href="' + hashFor('/c/' + n) + '" class="' + (kind === 'c' ? 'on' : '') + '">Full notes</a>' +
      '<a href="' + hashFor('/r/' + n) + '" class="' + (kind === 'r' ? 'on' : '') + '">Revision sheet</a></div>';
    const body = document.createElement('article');
    content.append(head, body);
    renderMarkdownInto(body, md, path, route);
    const box = document.createElement('label');
    box.className = 'complete-box';
    box.innerHTML = '<input type="checkbox" id="done-box"> <span>Mark Chapter ' + n + ' as complete</span>';
    content.appendChild(box);
    const cb = $('#done-box', box);
    cb.checked = !!progress[n];
    cb.addEventListener('change', () => setDone(n, cb.checked));
    content.insertAdjacentHTML('beforeend', pagerHtml(n, kind));
    setTitle('Chapter ' + n + (kind === 'r' ? ' revision' : '') + ' — ' + c.title);
    store.set('kb-last', { route, title: 'Chapter ' + n + ' — ' + c.title });
    buildToc(body);
    scrollToAnchor(anchor);
  }

  async function viewDoc(rel, anchor, content) {
    const route = '/d/' + rel;
    const md = await fetchText(rel);
    content.innerHTML = '';
    const body = document.createElement('article');
    content.appendChild(body);
    renderMarkdownInto(body, md, rel, route);
    const h1 = $('h1', body);
    setTitle(h1 ? h1.textContent.replace(/#$/, '') : rel);
    buildToc(body);
    scrollToAnchor(anchor);
  }

  function viewHome(content) {
    const done = doneCount(), total = chapters.length;
    const last = store.get('kb-last', null);
    let html = '<section class="hero"><h1>DevOps for SDEs — Knowledge Base</h1>' +
      '<p class="lead">A complete, searchable study resource for software engineers: Linux and Git, CI/CD and Docker, AWS, Kubernetes, Terraform, GitOps, observability and SRE, plus virtualization internals. Every chapter has the full original notes and a condensed revision sheet.</p></section>';
    html += '<div class="stats"><div class="stat"><b>' + total + '</b>chapters</div><div class="stat"><b>' + total + '</b>revision sheets</div>' +
      '<div class="stat"><b>' + done + '</b>completed</div></div>';
    html += '<div class="bar" aria-label="Progress"><i style="width:' + Math.round((100 * done) / Math.max(total, 1)) + '%"></i></div>' +
      '<small>' + done + ' of ' + total + ' chapters marked complete (stored in this browser only)</small>';
    if (last && last.route) html += '<p><a href="' + hashFor(last.route) + '">▶ Continue: ' + esc(last.title) + '</a></p>';
    html += '<h2>Start here</h2><div class="quick">' +
      [['Study guide', '/d/docs/00-start-here/study-guide.md'], ['Master cheat sheet', '/d/revision/00-master-cheatsheet.md'],
       ['Interview Q&A', '/d/revision/03-interview-qa.md'], ['Troubleshooting playbooks', '/d/revision/04-troubleshooting-playbooks.md'],
       ['Comparisons', '/d/revision/01-comparisons.md'], ['Glossary', '/d/GLOSSARY.md'], ['Labs', '/d/exercises/labs.md'],
       ['Corrections', '/d/CORRECTIONS.md'], ['Source coverage', '/d/SOURCE_COVERAGE.md']]
        .map(([l, r]) => '<a href="' + hashFor(r) + '">' + l + '</a>').join('') + '</div>';
    html += '<h2>Chapters by topic</h2><div class="cards">';
    nav.domains.forEach((d) => {
      const cs = chapters.filter((c) => c.domain === d.id).sort((a, b) => a.n - b.n);
      if (!cs.length) return;
      html += '<div class="card"><h3>' + esc(d.title) + '</h3><ul>' +
        cs.map((c) => '<li><a href="' + hashFor('/c/' + c.n) + '">' + c.n + '. ' + esc(c.title) + '</a>' + (progress[c.n] ? ' <span style="color:var(--ok)">✓</span>' : '') +
          ' <small>(<a href="' + hashFor('/r/' + c.n) + '">revision</a>)</small></li>').join('') + '</ul></div>';
    });
    html += '</div><p><button type="button" id="reset-progress" class="icon-btn" style="width:auto;padding:0 12px;font-size:13px">Reset progress</button></p>';
    content.innerHTML = html;
    const rb = $('#reset-progress');
    if (rb) rb.addEventListener('click', () => { if (confirm('Clear all completion marks stored in this browser?')) { progress = {}; store.set('kb-progress', progress); updateProgressUI(); viewHome(content); } });
    setTitle('');
    buildToc(null);
    window.scrollTo(0, 0);
  }

  // ------------------------------------------------------------------ search
  async function loadIndex() {
    if (searchIndex) return searchIndex;
    const res = await fetch('data/search-index.json');
    if (!res.ok) throw new Error('search-index.json → HTTP ' + res.status);
    const raw = await res.json();
    searchIndex = raw.map((d) => Object.assign(d, { _h: d.heading.toLowerCase(), _t: d.text.toLowerCase(), _ti: d.title.toLowerCase() }));
    return searchIndex;
  }
  function countOcc(hay, needle) {
    let n = 0, i = 0;
    while ((i = hay.indexOf(needle, i)) !== -1) { n++; i += needle.length; if (n > 20) break; }
    return n;
  }
  function runSearch(q) {
    const toks = q.toLowerCase().split(/\s+/).filter(Boolean);
    const phrase = toks.join(' ');
    const out = [];
    for (const d of searchIndex) {
      let score = 0, ok = true;
      for (const w of toks) {
        const inH = d._h.includes(w), inT = countOcc(d._t, w), inTi = d._ti.includes(w);
        if (!inH && !inT && !inTi) { ok = false; break; }
        score += (inH ? 10 : 0) + Math.min(inT, 5) + (inTi ? 2 : 0);
      }
      if (!ok) continue;
      if (toks.length > 1 && d._h.includes(phrase)) score += 15;
      if (toks.length > 1 && d._t.includes(phrase)) score += 6;
      if (d.kind === 'reference') score += 1;
      out.push([score, d]);
    }
    out.sort((a, b) => b[0] - a[0]);
    return out.slice(0, 40).map((x) => x[1]);
  }
  function snippet(d, toks) {
    const t = d.text;
    const low = d._t;
    let pos = -1;
    for (const w of toks) { const p = low.indexOf(w); if (p !== -1 && (pos === -1 || p < pos)) pos = p; }
    const start = Math.max(0, pos - 70);
    let s = esc(t.slice(start, start + 220));
    toks.forEach((w) => { s = s.replace(new RegExp(esc(w).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'ig'), (m) => '<mark>' + m + '</mark>'); });
    return (start > 0 ? '… ' : '') + s + (start + 220 < t.length ? ' …' : '');
  }
  async function viewSearch(q, content) {
    const input = $('#search-input');
    if (input && input.value !== q) input.value = q;
    setTitle('Search: ' + q);
    buildToc(null);
    content.innerHTML = '<h1>Search</h1><p class="loading">Searching…</p>';
    try { await loadIndex(); } catch (e) { fail(content, e); return; }
    if (!q.trim()) { content.innerHTML = '<h1>Search</h1><p>Type a term in the box above.</p>'; return; }
    const res = runSearch(q);
    const toks = q.toLowerCase().split(/\s+/).filter(Boolean);
    let html = '<h1>Search</h1><p>' + res.length + (res.length === 40 ? '+' : '') + ' result' + (res.length === 1 ? '' : 's') + ' for <strong>' + esc(q) + '</strong></p>';
    res.forEach((d) => {
      html += '<div class="result"><a href="' + hashFor(mdRoute(d.doc), d.anchor) + '">' + esc(d.heading) + '</a>' +
        '<div class="src">' + esc(d.title) + (d.kind === 'revision' && !/^Revision/.test(d.title) ? '' : '') + '</div><p>' + snippet(d, toks) + '</p></div>';
    });
    if (!res.length) html += '<p>No matches. Try fewer or different words (the search is a plain substring match).</p>';
    content.innerHTML = html;
    window.scrollTo(0, 0);
  }

  // ------------------------------------------------------------------ router
  async function router() {
    const { path, parts, anchor } = parseHash();
    const content = $('#content');
    const key = path;
    if (key === currentKey && key !== '/') {   // same page, only the anchor changed
      scrollToAnchor(anchor);
      return;
    }
    currentKey = key;
    highlightNav();
    openNav(false);
    try {
      if (parts.length === 0) viewHome(content);
      else if (parts[0] === 'c' || parts[0] === 'r') {
        content.innerHTML = '<p class="loading">Loading…</p>';
        await viewChapter(Number(parts[1]), parts[0], anchor, content);
      } else if (parts[0] === 'd') {
        content.innerHTML = '<p class="loading">Loading…</p>';
        await viewDoc(parts.slice(1).join('/'), anchor, content);
      } else if (parts[0] === 's') {
        await viewSearch(parts.slice(1).join('/'), content);
      } else {
        content.innerHTML = '<h1>Not found</h1><p><a href="#/">Go home</a></p>';
      }
    } catch (e) {
      fail(content, e);
    }
    content.focus({ preventScroll: true });
  }

  // ------------------------------------------------------------------ init
  async function init() {
    applyTheme(document.documentElement.getAttribute('data-theme') || 'light');
    $('#theme-btn').addEventListener('click', toggleTheme);
    $('#menu-btn').addEventListener('click', () => openNav(!document.body.classList.contains('nav-open')));
    $('#scrim').addEventListener('click', () => openNav(false));

    let timer = null;
    const input = $('#search-input');
    $('#search-form').addEventListener('submit', (e) => {
      e.preventDefault();
      clearTimeout(timer);
      const q = input.value.trim();
      if (q) location.hash = '#/s/' + encodeURIComponent(q);
    });
    input.addEventListener('input', () => {
      clearTimeout(timer);
      const q = input.value.trim();
      if (q.length >= 2) timer = setTimeout(() => { location.hash = '#/s/' + encodeURIComponent(q); }, 250);
    });
    document.addEventListener('keydown', (e) => {
      const typing = /^(INPUT|TEXTAREA|SELECT)$/.test((document.activeElement || {}).tagName || '');
      if (e.key === '/' && !typing && !e.ctrlKey && !e.metaKey) { e.preventDefault(); input.focus(); input.select(); }
      else if (e.key === 'Escape') { input.blur(); openNav(false); }
      else if ((e.key === '[' || e.key === ']') && !typing) {
        const p = parseHash().parts;
        if ((p[0] === 'c' || p[0] === 'r') && byNum[Number(p[1]) + (e.key === ']' ? 1 : -1)]) location.hash = '#/' + p[0] + '/' + (Number(p[1]) + (e.key === ']' ? 1 : -1));
      }
    });

    try {
      const res = await fetch('data/nav.json');
      if (!res.ok) throw new Error('data/nav.json → HTTP ' + res.status);
      nav = await res.json();
    } catch (e) {
      fail($('#content'), e);
      return;
    }
    chapters = nav.chapters;
    byNum = {};
    chapters.forEach((c) => { byNum[c.n] = c; });
    buildSidebar();
    window.addEventListener('hashchange', router);
    router();
  }

  window.addEventListener('DOMContentLoaded', init);
})();
