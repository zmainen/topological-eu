#!/usr/bin/env python3
"""Build essays and paper pages for topological.eu from TTT source markdown."""

import os, re, yaml, html

SRC = os.path.expanduser("~/Projects/haak/home/projects/ttt/essays/live")
DEST = os.path.expanduser("~/Projects/zmainen/topological-eu/essays")

def parse_frontmatter(text):
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.DOTALL)
    if not m:
        return {}, text
    raw = m.group(1)
    body = m.group(2)
    try:
        meta = yaml.safe_load(raw)
    except yaml.YAMLError:
        # Fallback: extract key fields with regex
        meta = {}
        tm = re.search(r'^title:\s*"?(.+?)"?\s*$', raw, re.MULTILINE)
        if tm: meta['title'] = tm.group(1)
        dm = re.search(r'^description:\s*"?(.+?)"?\s*$', raw, re.MULTILINE)
        if dm: meta['description'] = dm.group(1)
        lm = re.search(r'^length:\s*(\d+)', raw, re.MULTILINE)
        if lm: meta['length'] = int(lm.group(1))
        em = re.search(r'^excerpt:\s*>?\s*\n\s+(.+?)(?:\n\S|\Z)', raw, re.MULTILINE | re.DOTALL)
        if em: meta['excerpt'] = em.group(1).strip()
    return meta, body

def md_to_html(md):
    """Minimal markdown to HTML — handles headers, paragraphs, emphasis, blockquotes, lists, hr."""
    lines = md.strip().split('\n')
    out = []
    in_blockquote = False
    in_list = False
    bq_lines = []
    list_lines = []

    def flush_bq():
        nonlocal in_blockquote, bq_lines
        if bq_lines:
            content = '\n'.join(bq_lines)
            out.append(f'<blockquote><p>{inline(content)}</p></blockquote>')
            bq_lines = []
        in_blockquote = False

    def flush_list():
        nonlocal in_list, list_lines
        if list_lines:
            items = ''.join(f'<li>{inline(l)}</li>' for l in list_lines)
            out.append(f'<ul>{items}</ul>')
            list_lines = []
        in_list = False

    def inline(text):
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        # Em dash
        text = text.replace(' -- ', ' — ')
        text = text.replace('--', '—')
        return text

    i = 0
    para_lines = []

    def flush_para():
        nonlocal para_lines
        if para_lines:
            content = ' '.join(para_lines)
            out.append(f'<p>{inline(content)}</p>')
            para_lines = []

    while i < len(lines):
        line = lines[i]

        # Horizontal rule
        if re.match(r'^---+$', line.strip()):
            flush_para()
            flush_bq()
            flush_list()
            out.append('<hr>')
            i += 1
            continue

        # Headers
        hm = re.match(r'^(#{1,4})\s+(.+)$', line)
        if hm:
            flush_para()
            flush_bq()
            flush_list()
            level = len(hm.group(1))
            out.append(f'<h{level}>{inline(hm.group(2))}</h{level}>')
            i += 1
            continue

        # Blockquote
        if line.startswith('> ') or line.startswith('>'):
            flush_para()
            flush_list()
            in_blockquote = True
            bq_lines.append(line.lstrip('> ').strip())
            i += 1
            continue
        elif in_blockquote and line.strip():
            bq_lines.append(line.strip())
            i += 1
            continue
        elif in_blockquote:
            flush_bq()
            i += 1
            continue

        # Unordered list
        lm = re.match(r'^[-*]\s+(.+)$', line)
        if lm:
            flush_para()
            flush_bq()
            in_list = True
            list_lines.append(lm.group(1))
            i += 1
            continue
        elif in_list and line.strip():
            flush_list()
            # fall through to paragraph handling

        # Numbered list
        nm = re.match(r'^\d+\.\s+(.+)$', line)
        if nm:
            flush_para()
            flush_bq()
            # Treat as paragraph with numbering preserved
            out.append(f'<p>{inline(line)}</p>')
            i += 1
            continue

        # Empty line
        if not line.strip():
            flush_para()
            i += 1
            continue

        # Regular paragraph line
        para_lines.append(line)
        i += 1

    flush_para()
    flush_bq()
    flush_list()
    return '\n'.join(out)


NAV_HTML = """<a href="/essays/">essays</a>
    <a href="/paper/">paper</a>
    <a href="/concepts/">concepts</a>"""

def make_page(title, description, body_html, back_href="/", back_label="&larr; topological.eu"):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — Topological Theory of Things</title>
<meta name="description" content="{html.escape(description)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Gloock&family=Crimson+Pro:ital,wght@0,300;0,400;1,300;1,400&family=IBM+Plex+Mono:wght@300;400&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --bg: #0a0e1a; --bg2: #0f1424; --cream: #e8e0d4; --cream2: #7a8580;
  --gold: #c9a96e; --gold-dim: #2a2318; --silver: #8a7898; --line: #1a2028; --line2: #242d38;
}}
html {{ scroll-behavior: smooth; }}
body {{
  background: var(--bg); color: var(--cream);
  font-family: 'Crimson Pro', Georgia, serif; line-height: 1.65;
  -webkit-font-smoothing: antialiased;
}}
a {{ color: var(--gold); text-decoration: none; }}
a:hover {{ opacity: 0.8; }}
h1 {{
  font-family: 'Gloock', serif; font-weight: 400;
  font-size: clamp(28px, 5vw, 48px); color: var(--cream);
  letter-spacing: 0.01em; line-height: 1.15; margin-bottom: 12px;
}}
h2 {{
  font-family: 'Gloock', serif; font-weight: 400;
  font-size: clamp(22px, 3.5vw, 30px); color: var(--cream); margin-bottom: 16px;
  margin-top: 40px;
}}
h3 {{
  font-family: 'Gloock', serif; font-weight: 400;
  font-size: clamp(18px, 2.5vw, 22px); color: var(--cream); margin-bottom: 12px;
  margin-top: 32px;
}}
p {{ margin-bottom: 1em; font-weight: 300; }}
blockquote {{
  margin: 16px 0; padding: 10px 14px;
  border-left: 2px solid var(--gold-dim);
  background: rgba(201,169,110,0.04); border-radius: 0 4px 4px 0;
  font-family: 'Instrument Serif', serif; font-style: italic;
  color: var(--cream2);
}}
blockquote p {{ margin-bottom: 0; }}
hr {{ border: none; border-top: 1px solid var(--line2); margin: 40px 0; }}
ul {{ margin: 0 0 1em 1.5em; font-weight: 300; }}
li {{ margin-bottom: 0.3em; }}
strong {{ font-weight: 400; color: var(--cream); }}
em {{ font-style: italic; }}
.subtitle {{
  font-family: 'Instrument Serif', serif; font-style: italic;
  font-size: clamp(14px, 2vw, 20px); color: var(--cream2);
  line-height: 1.5; max-width: 600px;
}}
.mono {{
  font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 0.08em;
}}
.label {{
  font-family: 'IBM Plex Mono', monospace; font-size: 9px;
  letter-spacing: 0.14em; text-transform: uppercase; color: var(--silver);
}}
nav {{
  padding: 16px 28px; display: flex; justify-content: space-between;
  align-items: center; max-width: 1100px; margin: 0 auto;
}}
.nav-home {{ font-family: 'Gloock', serif; font-size: 18px; color: var(--cream); }}
.nav-links {{ display: flex; gap: 16px; align-items: center; }}
.nav-links a {{
  font-family: 'IBM Plex Mono', monospace; font-size: 9px;
  letter-spacing: 0.16em; text-transform: uppercase; color: var(--silver);
}}
.nav-links a:hover {{ color: var(--gold); }}
.back-link {{
  font-family: 'IBM Plex Mono', monospace; font-size: 11px;
  letter-spacing: 0.08em; color: var(--silver);
}}
.back-link:hover {{ color: var(--gold); }}
.content {{
  max-width: 700px; margin: 0 auto; padding: 48px 28px 80px;
}}
.content-wide {{
  max-width: 1100px; margin: 0 auto; padding: 48px 28px 80px;
}}
.card {{
  border: 1px solid var(--line2); border-radius: 4px;
  padding: 16px 20px; background: var(--bg2);
  transition: border-color 0.2s;
}}
.card:hover {{ border-color: var(--gold); }}
.card-title {{
  font-family: 'Gloock', serif; font-size: 16px; font-weight: 400;
  color: var(--cream); margin-bottom: 8px;
}}
.card-body {{
  font-size: 14px; font-weight: 300; line-height: 1.6; color: var(--cream2);
}}
.card-grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px;
}}
.badge {{
  display: inline-block; font-family: 'IBM Plex Mono', monospace;
  font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase;
  padding: 2px 8px; border-radius: 3px; border: 1px solid var(--gold); color: var(--gold);
}}
.btn {{
  font-family: 'IBM Plex Mono', monospace; font-size: 11px;
  letter-spacing: 0.14em; text-transform: uppercase; color: var(--gold);
  padding: 8px 20px; border: 1px solid var(--line2); border-radius: 4px;
  transition: border-color 0.2s, background 0.2s; display: inline-block;
}}
.btn:hover {{ border-color: var(--gold); background: var(--gold-dim); opacity: 1; }}
footer {{
  border-top: 1px solid var(--line2); padding: 20px 28px;
  max-width: 1100px; margin: 0 auto; display: flex; justify-content: space-between;
  font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--cream2);
}}
@media (max-width: 700px) {{
  nav {{ padding: 12px 16px; }}
  .content, .content-wide {{ padding: 32px 16px 60px; }}
  .card-grid {{ grid-template-columns: 1fr; }}
  footer {{ flex-direction: column; gap: 8px; padding: 16px; }}
}}
</style>
</head>
<body>
<nav>
  <a href="{back_href}" class="back-link">{back_label}</a>
  <div class="nav-links">
    {NAV_HTML}
  </div>
</nav>
{body_html}
<footer>
  <span>topological.eu</span>
  <span>Zachary F. Mainen</span>
</footer>
</body>
</html>'''


def build_essays():
    essays = []
    for fname in sorted(os.listdir(SRC)):
        if not fname.endswith('.md'):
            continue
        slug = fname[:-3]
        with open(os.path.join(SRC, fname)) as f:
            text = f.read()
        meta, body = parse_frontmatter(text)
        title = meta.get('title', slug).strip('"')
        desc = meta.get('description', '').strip('"')
        excerpt = meta.get('excerpt', desc).strip()
        length = meta.get('length', 0)

        essays.append({
            'slug': slug,
            'title': title,
            'description': desc,
            'excerpt': excerpt,
            'length': length,
            'body': body,
            'concepts': meta.get('concepts', []),
        })

    # Categorize essays
    # Core philosophical essays (ontology series + intro essays)
    core_slugs = [
        'before-the-first-entity', 'one-relation-is-enough', 'reality-is-a-tangle',
        'the-first-ontologist', 'there-is-no-meta-room',
        'ontology-relational-ground', 'ontology-relations', 'ontology-objects',
        'ontology-perception-memory', 'ontology-notation', 'ontology-situation-graph',
        'ontology-situation-nesting', 'ontology-relations-applied', 'ontology-identity',
        'ontology-correspondence', 'ontology-ai-writing', 'ontology-governance-situation',
        'ontology-correspondence-haak', 'ontology-audit',
    ]
    applied_slugs = [s['slug'] for s in essays if s['slug'] not in core_slugs]

    core = [e for e in essays if e['slug'] in core_slugs]
    applied = [e for e in essays if e['slug'] in applied_slugs]

    # Sort core by the order in core_slugs
    core_order = {s: i for i, s in enumerate(core_slugs)}
    core.sort(key=lambda e: core_order.get(e['slug'], 999))

    # Build individual essay pages
    for essay in essays:
        body_html = md_to_html(essay['body'])
        page_body = f'''<div class="content">
<h1>{html.escape(essay['title'])}</h1>
<p class="subtitle">{html.escape(essay['description'])}</p>
{body_html}
</div>'''
        page = make_page(essay['title'], essay['description'], page_body,
                        back_href="/essays/", back_label="&larr; essays")
        with open(os.path.join(DEST, f"{essay['slug']}.html"), 'w') as f:
            f.write(page)

    # Build essay index
    def essay_card(e):
        words = f"{e['length']} words" if e['length'] else ""
        return f'''<a href="/essays/{e['slug']}.html" style="text-decoration:none">
<div class="card">
  <div class="card-title">{html.escape(e['title'])}</div>
  <div class="card-body">{html.escape(e['excerpt'])}</div>
  {f'<div class="label" style="margin-top:8px">{words}</div>' if words else ''}
</div></a>'''

    core_cards = '\n'.join(essay_card(e) for e in core)
    applied_cards = '\n'.join(essay_card(e) for e in applied)

    index_body = f'''<div class="content-wide">
<h1>Essays</h1>
<p class="subtitle">Long-form writing on Topological Theory of Things — the relational situational ontology and its applications.</p>

<section>
<h2>Foundations</h2>
<p style="color:var(--cream2); font-weight:300; margin-bottom:20px">The philosophical ground, the single-relation ontology, and the formal apparatus.</p>
<div class="card-grid">
{core_cards}
</div>
</section>

<section>
<h2>Applications</h2>
<p style="color:var(--cream2); font-weight:300; margin-bottom:20px">The ontology applied — coordination, governance, architecture, lifecycle.</p>
<div class="card-grid">
{applied_cards}
</div>
</section>
</div>'''

    index_page = make_page("Essays", "Long-form writing on Topological Theory of Things", index_body)
    with open(os.path.join(DEST, "index.html"), 'w') as f:
        f.write(index_page)

    return len(essays)


def build_paper():
    dest = os.path.expanduser("~/Projects/zmainen/topological-eu/paper")
    body = f'''<div class="content">
<h1>Same but Different</h1>
<p class="subtitle">A Topological Theory of Things</p>
<p class="label" style="margin-top:24px; margin-bottom:32px">Zachary F. Mainen</p>

<p>Following Leibniz and Kant, we hold that among the central questions any ontology must answer are: How can things be distinct from one another and yet share characteristics? How can one thing change while still remaining the same thing? How can perceived, known, and imagined things be different from yet also the same as things themselves?</p>

<p>Rather than beginning with a plurality of objects — distinct, bare, unrelated — we start from the opposite corner: pure relationality and specificity. We introduce the <em>mess</em>, a field of pure difference with no identifiable entities. From this ground, we show how <em>coils</em> — self-referential loops in the relational fabric — give rise to persistent, identifiable things without invoking essences, substances, or hidden properties. <em>Knots</em> — topological invariants of coils — provide the formal basis for identity, similarity, and knowledge as aspects of a single relational structure.</p>

<p>The result is an ontology built from one primitive relation (<em>belongs-to</em>) and one structural principle (topological invariance under deformation), from which the classical problems of order, identity, and knowledge receive unified treatment with greater parsimony than object-oriented alternatives.</p>

<div style="margin-top:40px; display:flex; gap:16px; flex-wrap:wrap">
  <a href="/paper/same-but-different.pdf" class="btn">read the paper (pdf)</a>
</div>

<hr>

<h2>Contents</h2>
<ul>
<li>Leibniz's Leaves</li>
<li>How OOO Approaches the Problem</li>
<li>Beginning from the Opposite Corner — the mess, coils, knots</li>
<li>Order, Identity, and Knowledge</li>
<li>Situations</li>
<li>Discussion</li>
</ul>
</div>'''

    page = make_page("Same but Different", "A Topological Theory of Things", body)
    with open(os.path.join(dest, "index.html"), 'w') as f:
        f.write(page)


if __name__ == '__main__':
    n = build_essays()
    build_paper()
    print(f"Built {n} essay pages + essay index + paper page")
