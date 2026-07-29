import os, re, glob, shutil, json, datetime
import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'site')
CONTENT = os.path.join(ROOT, 'content')
COVERS_DIR = os.path.join(ROOT, 'assets/img/covers')

def cat_slug(c): return re.sub(r'[^a-z0-9]+', '-', c.lower()).strip('-')
def auth_slug(a): return re.sub(r'[^a-z0-9]+', '-', a.lower()).strip('-')

def load_frontmatter(path):
    """Parse YAML frontmatter between --- markers. Handles CRLF and missing closing ---."""
    raw = open(path, encoding='utf-8').read()
    # Normalise Windows line-endings so the regex works on any OS
    raw = raw.replace('\r\n', '\n').replace('\r', '\n')
    # Match opening ---, capture everything up to the next ---, ignore body
    m = re.match(r'^---\n(.*?)\n---(?:\n|$)', raw, re.S)
    if not m:
        # Fallback: if there is only an opening --- with no closing one, try to
        # parse everything after the first line as YAML (Decap CMS sometimes
        # writes files this way on the first save before a closing marker exists)
        m2 = re.match(r'^---\n(.*)', raw, re.S)
        if m2:
            data = yaml.safe_load(m2.group(1)) or {}
            if data:
                return data
        raise ValueError(f"No valid YAML frontmatter in: {path}")
    data = yaml.safe_load(m.group(1)) or {}
    return data

def load_collection(subdir):
    items = []
    pattern = os.path.join(CONTENT, subdir, '*.md')
    paths = sorted(glob.glob(pattern))
    if not paths:
        print(f"WARNING: No .md files found matching {pattern}")
    for fp in paths:
        try:
            items.append(load_frontmatter(fp))
        except Exception as e:
            print(f"WARNING: Skipping {fp} — {e}")
    return items

def resolve_cover(slug, explicit=''):
    if explicit and os.path.exists(os.path.join(COVERS_DIR, explicit)):
        return explicit
    if os.path.exists(os.path.join(COVERS_DIR, f'{slug}.jpg')):
        return f'{slug}.jpg'
    return f'{slug}.svg'  # generated placeholder fallback (see covergen.py)

def resolve_cat_cover(slug, explicit=''):
    if explicit and os.path.exists(os.path.join(COVERS_DIR, explicit)):
        return explicit
    if os.path.exists(os.path.join(COVERS_DIR, f'cat-{slug}.jpg')):
        return f'cat-{slug}.jpg'
    return f'cat-{slug}.svg'

def parse_date(s):
    """publish_date is a free-text string like 'March 3, 2026' — parse for sorting, fall back gracefully."""
    for fmt in ('%B %d, %Y', '%b %d, %Y', '%Y-%m-%d'):
        try:
            return datetime.datetime.strptime(s.strip(), fmt)
        except (ValueError, TypeError):
            continue
    return datetime.datetime.min

def process_sections(raw_sections):
    out = []
    for sec in raw_sections:
        content = sec.get('content', '')
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        is_list = bool(lines) and all(l.startswith('-') for l in lines)
        if is_list:
            out.append({'title': sec['title'], 'is_list': True, 'bullets': [l.lstrip('- ').strip() for l in lines]})
        else:
            out.append({'title': sec['title'], 'is_list': False, 'content': ' '.join(lines)})
    return out

COMMENT_BANK = [
    {'name': 'Priya K.', 'time': '2 days ago', 'text': 'This is the clearest breakdown of this topic I\u2019ve read all year. Bookmarking to reread before my next budget review.'},
    {'name': 'Marcus T.', 'time': '4 days ago', 'text': 'Appreciate that this didn\u2019t try to sell me an app halfway through. Just the actual mechanics, which is rare.'},
    {'name': 'Whitney L.', 'time': '1 week ago', 'text': 'Would love a follow-up on how this plays out for people with irregular freelance income.'},
]

# ---------------------------------------------------------------------------
# Load everything from content/ (this is the CMS-editable source of truth)
# ---------------------------------------------------------------------------
raw_articles = load_collection('articles')
raw_categories = load_collection('categories')
raw_authors = load_collection('authors')

if not raw_articles:
    raise SystemExit("No articles found in content/articles/ — aborting build.")

# sort articles by publish_date ascending (oldest first) — same convention the
# rest of the build (prev/next, 'latest' reversal) already assumes
raw_articles.sort(key=lambda a: (parse_date(a.get('publish_date', '')), a.get('id', 0)))

AUTHORS = {a['name']: a for a in raw_authors}
CATEGORIES_META = {c['name']: c for c in raw_categories}

articles = raw_articles
by_slug = {a['slug']: a for a in articles}
by_title = {a['title']: a for a in articles}

# ---- enrich each article with derived/display fields ----
for i, a in enumerate(articles):
    a.setdefault('tags', [])
    a.setdefault('key_takeaways', [])
    a.setdefault('faqs', [])
    a.setdefault('sections', [])
    author_meta = AUTHORS.get(a['author'])
    if not author_meta:
        raise SystemExit(f"Article '{a['slug']}' references unknown author '{a['author']}'. "
                          f"Known authors: {list(AUTHORS.keys())}")
    a['category_slug'] = cat_slug(a['category'])
    a['author_slug'] = auth_slug(a['author'])
    a['author_bio'] = author_meta['bio']
    a['author_photo'] = author_meta['photo']
    a['cover'] = resolve_cover(a['slug'], a.get('cover', ''))
    a['sections_processed'] = process_sections(a['sections'])
    a['callout'] = a['key_takeaways'][-1] if a['key_takeaways'] else (a.get('conclusion', '')[:140])
    a['pullquote'] = a['key_takeaways'][0] if a['key_takeaways'] else None
    a['comments'] = COMMENT_BANK
    rel_titles = a.get('related_titles', []) or []
    rel = [by_title[t] for t in rel_titles if t in by_title]
    if len(rel) < 3:
        pool = [x for x in articles if x['category'] == a['category'] and x['slug'] != a['slug'] and x not in rel]
        rel += pool[:3 - len(rel)]
    a['related_ref'] = rel[:3]
    a['prev_ref'] = articles[i - 1] if i > 0 else articles[-1]
    a['next_ref'] = articles[(i + 1) % len(articles)]

# ---- categories ----
categories = []
for name, meta in CATEGORIES_META.items():
    slug = meta.get('slug') or cat_slug(name)
    items = [a for a in articles if a['category'] == name]
    categories.append({
        'name': name, 'slug': slug, 'desc': meta.get('description', ''),
        'count': len(items), 'items': items,
        'cover': resolve_cat_cover(slug, meta.get('cover', '')),
    })
# categories with zero articles still show (count 0) so the CMS can pre-create sections

# ---- authors ----
authors_list = []
for name, meta in AUTHORS.items():
    slug = meta.get('slug') or auth_slug(name)
    items = [a for a in articles if a['author'] == name]
    authors_list.append({
        'name': name, 'slug': slug, 'count': len(items), 'items': items,
        'title': meta.get('title', ''), 'bio': meta.get('bio', ''),
        'bio_long': meta.get('bio_long', ''), 'expertise': meta.get('expertise', []),
        'photo': meta.get('photo', ''),
    })

# ---------------------------------------------------------------------------
# Flag-driven curated sections (CMS-toggleable booleans, with graceful
# fallback to "most recent" if an editor hasn't flagged enough articles yet)
# ---------------------------------------------------------------------------
def flagged_or_fallback(flag, n):
    flagged = [a for a in articles if a.get(flag)]
    if len(flagged) >= n:
        return list(reversed(flagged))[:n]
    fallback = [a for a in reversed(articles) if a not in flagged]
    return (list(reversed(flagged)) + fallback)[:n]

latest_articles = list(reversed(articles))[:8]
trending_articles = flagged_or_fallback('trending', 8)
picks_articles = flagged_or_fallback('editors_pick', 8)
popular_articles = flagged_or_fallback('popular', 8)
featured_candidates = [a for a in articles if a.get('featured')]
featured = featured_candidates[-1] if featured_candidates else articles[-1]

# search index (compact) for client-side search
search_index = [{
    'title': a['title'], 'category': a['category'], 'tags': a['tags'],
    'url': f"article/{a['slug']}.html", 'cover': f"assets/img/covers/{a['cover']}",
    'description': a.get('meta_description', ''), 'author': a.get('author', ''),
    'publish_date': a.get('publish_date', ''),
} for a in articles]
SEARCH_JSON = json.dumps(search_index)

# Also write search index as a JSON file for potential external use
SEARCH_INDEX_PATH = os.path.join(OUT, 'search-index.json')

env = Environment(loader=FileSystemLoader(os.path.join(ROOT, 'templates')), autoescape=False)

def write(path, tpl_name, ctx, base):
    tpl = env.get_template(tpl_name)
    full_ctx = dict(ctx)
    full_ctx['base'] = base
    full_ctx['search_index'] = SEARCH_JSON
    full_ctx.setdefault('page_description', 'BillionBlogs — independent financial journalism on budgeting, investing, income, and the economy.')
    # Add OG meta tags for social sharing
    full_ctx['og_type'] = full_ctx.get('og_type', 'website')
    full_ctx['og_image'] = full_ctx.get('og_image', '/assets/img/og-default.jpg')
    html = tpl.render(**full_ctx)
    fp = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, 'w', encoding='utf-8').write(html)

if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)

# ---- home ----
write('index.html', 'home.html', {
    'page_title': 'Finance, Made Legible',
    'page_description': 'BillionBlogs is an independent finance publication covering investing, budgeting, income, and the economy — reported clearly, without the sales pitch.',
    'nav': 'home',
    'featured': featured,
    'categories': categories,
    'trending': trending_articles[:6],
    'wealth_features': [by_slug[s] for s in ['ai-electrification-supercycle-2026', 'private-markets-global-diversification-2026', 'agentic-ai-productivity-wealth-2026'] if s in by_slug],
    'picks': picks_articles[:4],
    'latest': latest_articles[:8],
    'authors': authors_list,
}, base='')
print('Built home.')

# ---- article pages ----
for a in articles:
    ctx = {
        'page_title': a['meta_title'],
        'page_description': a['meta_description'],
        'nav': 'articles',
        'a': {
            **a,
            'sections': a['sections_processed'],
            'related': a['related_ref'],
            'prev': a['prev_ref'],
            'next': a['next_ref'],
        },
    }
    write(f"article/{a['slug']}.html", 'article.html', ctx, base='../')
print(f'Built {len(articles)} article pages.')

# ---- all articles (paginated) ----
PER_PAGE = 9
pages = [articles[i:i + PER_PAGE] for i in range(0, len(articles), PER_PAGE)]
for idx, page_items in enumerate(pages, start=1):
    pag = {
        'prev': ('articles.html' if idx == 2 else f'articles-{idx-1}.html') if idx > 1 else None,
        'next': f'articles-{idx+1}.html' if idx < len(pages) else None,
        'pages': [{'n': n, 'current': n == idx, 'href': 'articles.html' if n == 1 else f'articles-{n}.html'} for n in range(1, len(pages) + 1)],
    }
    fname = 'articles.html' if idx == 1 else f'articles-{idx}.html'
    write(fname, 'listing.html', {
        'page_title': 'All Articles',
        'nav': 'articles', 'eyebrow': 'The Archive', 'heading': 'All articles',
        'subheading': f'{len(articles)} stories across nine sections, from first-budget basics to macro trends.',
        'items': page_items, 'pagination': pag, 'show_newsletter': idx == len(pages),
    }, base='')
print(f'Built articles index across {len(pages)} pages.')

# ---- curated listings ----
listing_defs = [
    ('trending.html', 'Right Now', 'Trending this week', 'The stories readers are sharing most right now.', trending_articles),
    ('editors-picks.html', "Curated", "Editor's picks", 'Selected by the BillionBlogs editorial team for depth and clarity.', picks_articles),
    ('most-popular.html', 'All-Time', 'Most popular', 'The most-read stories on BillionBlogs since launch.', popular_articles),
    ('latest.html', 'Fresh', 'Latest articles', 'The newest stories, in publication order.', latest_articles),
]
for fname, eyebrow, heading, sub, items in listing_defs:
    write(fname, 'listing.html', {
        'page_title': heading, 'nav': 'articles', 'eyebrow': eyebrow, 'heading': heading,
        'subheading': sub, 'items': items, 'show_newsletter': True,
    }, base='')
print('Built curated listing pages.')

# ---- categories ----
write('categories.html', 'categories.html', {
    'page_title': 'Categories', 'nav': 'categories',
    'categories': categories,
}, base='')

for cat in categories:
    chips = [{'name': c['name'], 'slug': c['slug'], 'active': c['slug'] == cat['slug']} for c in categories]
    write(f"category/{cat['slug']}.html", 'listing.html', {
        'page_title': cat['name'], 'nav': 'categories', 'eyebrow': 'Section', 'heading': cat['name'],
        'subheading': cat['desc'], 'items': cat['items'], 'chips': chips,
        'breadcrumb': cat['name'], 'show_newsletter': True, 'banner': cat['cover'],
    }, base='../')
print(f'Built categories overview + {len(categories)} category pages.')

# ---- authors ----
write('authors.html', 'authors.html', {
    'page_title': 'Authors', 'nav': 'authors', 'authors': authors_list,
}, base='')

for auth in authors_list:
    write(f"author/{auth['slug']}.html", 'author.html', {
        'page_title': auth['name'], 'nav': 'authors',
        'auth': {**auth, 'articles': auth['items']},
    }, base='../')
print(f'Built authors overview + {len(authors_list)} author pages.')

# ---- search / bookmarks ----
write('search.html', 'search.html', {'page_title': 'Search', 'nav': ''}, base='')
write('bookmarks.html', 'bookmarks.html', {'page_title': 'Bookmarks', 'nav': ''}, base='')

# ---- about / contact / newsletter ----
write('about.html', 'about.html', {'page_title': 'About', 'nav': 'about'}, base='')
write('contact.html', 'contact.html', {'page_title': 'Contact', 'nav': ''}, base='')
write('newsletter.html', 'newsletter.html', {'page_title': 'Newsletter', 'nav': ''}, base='')

# ---- legal ----
privacy_body = """
<p class="lede">BillionBlogs ("we", "us") respects your privacy. This policy explains what we collect and why.</p>
<h2>Information we collect</h2>
<p>We collect the email address you provide when subscribing to our newsletter, and standard analytics data (pages visited, approximate location, device type) via privacy-respecting analytics tools. We do not sell personal data to third parties.</p>
<h2>Cookies</h2>
<p>We use essential cookies to remember your theme preference and bookmarked articles, stored locally in your browser. We do not use third-party advertising trackers.</p>
<h2>Your rights</h2>
<p>You may request access to, correction of, or deletion of your personal data at any time by contacting privacy@billionblogs.com. You can unsubscribe from the newsletter with one click at the bottom of any email.</p>
<h2>Changes to this policy</h2>
<p>We may update this policy periodically. Material changes will be announced via the newsletter.</p>
"""
terms_body = """
<p class="lede">By using BillionBlogs, you agree to the following terms.</p>
<h2>Editorial content, not financial advice</h2>
<p>Content on BillionBlogs is for informational and educational purposes only and does not constitute personalized financial, investment, tax, or legal advice. Consult a licensed professional before making financial decisions.</p>
<h2>Intellectual property</h2>
<p>All articles, illustrations, and branding on BillionBlogs are the property of BillionBlogs unless otherwise credited. Reproduction requires written permission.</p>
<h2>Acceptable use</h2>
<p>You agree not to scrape, republish, or misrepresent BillionBlogs content, and not to use the site for unlawful purposes.</p>
<h2>Limitation of liability</h2>
<p>BillionBlogs is provided "as is." We are not liable for financial decisions made based on our content.</p>
"""
write('privacy.html', 'legal.html', {'page_title': 'Privacy Policy', 'nav': '', 'heading': 'Privacy Policy', 'body': privacy_body}, base='')
write('terms.html', 'legal.html', {'page_title': 'Terms of Use', 'nav': '', 'heading': 'Terms of Use', 'body': terms_body}, base='')

# ---- 404 ----
write('404.html', '404.html', {'page_title': 'Page Not Found', 'nav': ''}, base='')

print('Built static/legal/utility pages.')

# ---- generate SVG placeholder covers for any article/category without a real photo ----
try:
    import covergen
    for a in articles:
        if a['cover'].endswith('.svg') and not os.path.exists(os.path.join(COVERS_DIR, a['cover'])):
            svg = covergen.make_cover(a['slug'], a['category'], a.get('id', 0))
            open(os.path.join(COVERS_DIR, a['cover']), 'w').write(svg)
    print('Generated any missing SVG placeholder covers.')
except Exception as e:
    print(f'Warning: covergen skipped ({e})')

# ---- copy assets ----
shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
print('Copied assets.')

# ---- write search index JSON ----
open(SEARCH_INDEX_PATH, 'w', encoding='utf-8').write(SEARCH_JSON)
print('Generated search-index.json.')

print('BUILD COMPLETE')
