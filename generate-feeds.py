#!/usr/bin/env python3
"""
Generate static feeds and metadata for BillionBlogs after build.
This script runs automatically after build.py and generates:
- sitemap.xml for search engines
- rss.xml for feed readers
- search-index.json for client-side search
- robots.txt for SEO
"""

import os
import re
import json
import glob
import yaml
from datetime import datetime
from urllib.parse import urljoin

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, 'content')
OUT = os.path.join(ROOT, 'site')
SITE_URL = os.environ.get('URL', 'https://billionblogs.com')

def parse_date(s):
    """Parse publish_date string like 'March 3, 2026' """
    for fmt in ('%B %d, %Y', '%b %d, %Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(s.strip(), fmt)
        except (ValueError, TypeError):
            continue
    return datetime.min

def load_frontmatter(path):
    """Load YAML frontmatter from markdown file"""
    try:
        raw = open(path, encoding='utf-8').read()
        m = re.match(r'^---\n(.*?)\n---\n?(.*)$', raw, re.S)
        if m:
            data = yaml.safe_load(m.group(1)) or {}
            return data
    except Exception as e:
        print(f"Warning: Could not parse {path}: {e}")
    return {}

def load_collection(subdir):
    """Load all items from a content collection"""
    items = []
    for fp in sorted(glob.glob(os.path.join(CONTENT, subdir, '*.md'))):
        item = load_frontmatter(fp)
        if item:
            items.append(item)
    return items

def generate_sitemap():
    """Generate sitemap.xml for search engines"""
    articles = load_collection('articles')
    categories = load_collection('categories')
    authors = load_collection('authors')
    
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Static pages (always included)
    static_pages = [
        ('/', datetime.now()),
        ('/articles.html', datetime.now()),
        ('/categories.html', datetime.now()),
        ('/authors.html', datetime.now()),
        ('/trending.html', datetime.now()),
        ('/editors-picks.html', datetime.now()),
        ('/most-popular.html', datetime.now()),
        ('/latest.html', datetime.now()),
        ('/about.html', datetime.now()),
        ('/contact.html', datetime.now()),
        ('/newsletter.html', datetime.now()),
        ('/bookmarks.html', datetime.now()),
        ('/search.html', datetime.now()),
        ('/privacy.html', datetime.now()),
        ('/terms.html', datetime.now()),
    ]
    
    for path, date in static_pages:
        sitemap += f'  <url>\n'
        sitemap += f'    <loc>{SITE_URL}{path}</loc>\n'
        sitemap += f'    <lastmod>{date.isoformat()}</lastmod>\n'
        sitemap += f'    <changefreq>weekly</changefreq>\n'
        sitemap += f'    <priority>0.8</priority>\n'
        sitemap += f'  </url>\n'
    
    # Article pages
    for article in articles:
        slug = article.get('slug', '')
        if slug:
            pub_date = parse_date(article.get('publish_date', ''))
            sitemap += f'  <url>\n'
            sitemap += f'    <loc>{SITE_URL}/article/{slug}.html</loc>\n'
            sitemap += f'    <lastmod>{pub_date.isoformat()}</lastmod>\n'
            sitemap += f'    <changefreq>never</changefreq>\n'
            sitemap += f'    <priority>0.9</priority>\n'
            sitemap += f'  </url>\n'
    
    # Category pages
    for cat in categories:
        slug = cat.get('slug', '')
        if slug:
            sitemap += f'  <url>\n'
            sitemap += f'    <loc>{SITE_URL}/category/{slug}.html</loc>\n'
            sitemap += f'    <lastmod>{datetime.now().isoformat()}</lastmod>\n'
            sitemap += f'    <changefreq>daily</changefreq>\n'
            sitemap += f'    <priority>0.7</priority>\n'
            sitemap += f'  </url>\n'
    
    # Author pages
    for author in authors:
        slug = author.get('slug', '')
        if slug:
            sitemap += f'  <url>\n'
            sitemap += f'    <loc>{SITE_URL}/author/{slug}.html</loc>\n'
            sitemap += f'    <lastmod>{datetime.now().isoformat()}</lastmod>\n'
            sitemap += f'    <changefreq>weekly</changefreq>\n'
            sitemap += f'    <priority>0.6</priority>\n'
            sitemap += f'  </url>\n'
    
    sitemap += '</urlset>\n'
    
    # Write sitemap
    sitemap_path = os.path.join(OUT, 'sitemap.xml')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(sitemap)
    print(f'Generated sitemap.xml ({len(articles)} articles, {len(categories)} categories, {len(authors)} authors)')

def generate_rss():
    """Generate rss.xml RSS feed"""
    articles = load_collection('articles')
    articles.sort(key=lambda a: parse_date(a.get('publish_date', '')), reverse=True)
    
    rss = '<?xml version="1.0" encoding="UTF-8"?>\n'
    rss += '<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">\n'
    rss += '  <channel>\n'
    rss += '    <title>BillionBlogs</title>\n'
    rss += f'    <link>{SITE_URL}</link>\n'
    rss += '    <description>Independent financial journalism on budgeting, investing, income, and the economy.</description>\n'
    rss += f'    <lastBuildDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>\n'
    rss += f'    <language>en-us</language>\n'
    rss += f'    <image>\n'
    rss += f'      <url>{SITE_URL}/assets/img/logo-dark.png</url>\n'
    rss += f'      <title>BillionBlogs</title>\n'
    rss += f'      <link>{SITE_URL}</link>\n'
    rss += f'    </image>\n'
    
    # Add articles to feed (limit to 20 most recent)
    for article in articles[:20]:
        slug = article.get('slug', '')
        title = article.get('title', '')
        description = article.get('meta_description', '')
        category = article.get('category', '')
        pub_date = parse_date(article.get('publish_date', ''))
        author = article.get('author', 'BillionBlogs')
        
        if slug:
            rss += f'    <item>\n'
            rss += f'      <title>{escape_xml(title)}</title>\n'
            rss += f'      <link>{SITE_URL}/article/{slug}.html</link>\n'
            rss += f'      <guid>{SITE_URL}/article/{slug}.html</guid>\n'
            rss += f'      <pubDate>{pub_date.strftime("%a, %d %b %Y %H:%M:%S +0000")}</pubDate>\n'
            rss += f'      <author>{escape_xml(author)}</author>\n'
            rss += f'      <category>{escape_xml(category)}</category>\n'
            rss += f'      <description>{escape_xml(description)}</description>\n'
            rss += f'      <content:encoded><![CDATA[<p>{escape_xml(description)}</p><p><a href="{SITE_URL}/article/{slug}.html">Read full article</a></p>]]></content:encoded>\n'
            rss += f'    </item>\n'
    
    rss += '  </channel>\n'
    rss += '</rss>\n'
    
    # Write RSS feed
    rss_path = os.path.join(OUT, 'rss.xml')
    with open(rss_path, 'w', encoding='utf-8') as f:
        f.write(rss)
    print(f'Generated rss.xml (20 most recent articles)')

def generate_robots_txt():
    """Generate robots.txt for SEO"""
    robots = f"""# robots.txt for BillionBlogs
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /.netlify/

# Crawl delays
Crawl-delay: 1

# Sitemap
Sitemap: {SITE_URL}/sitemap.xml
"""
    
    robots_path = os.path.join(OUT, 'robots.txt')
    with open(robots_path, 'w', encoding='utf-8') as f:
        f.write(robots)
    print('Generated robots.txt')

def escape_xml(text):
    """Escape XML special characters"""
    if not text:
        return ""
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text

def generate_search_index():
    """Generate search-index.json for client-side search"""
    articles = load_collection('articles')
    
    search_index = []
    for article in articles:
        entry = {
            'title': article.get('title', ''),
            'slug': article.get('slug', ''),
            'category': article.get('category', ''),
            'tags': article.get('tags', []),
            'url': f"article/{article.get('slug', '')}.html",
            'description': article.get('meta_description', ''),
            'cover': f"assets/img/covers/{article.get('slug', '')}.jpg",
            'publish_date': article.get('publish_date', ''),
            'author': article.get('author', ''),
        }
        search_index.append(entry)
    
    # Write search index
    index_path = os.path.join(OUT, 'search-index.json')
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(search_index, f, indent=2)
    print(f'Generated search-index.json ({len(articles)} articles)')

if __name__ == '__main__':
    try:
        # Create output directory if it doesn't exist
        os.makedirs(OUT, exist_ok=True)
        
        # Generate all feeds and metadata
        generate_sitemap()
        generate_rss()
        generate_robots_txt()
        generate_search_index()
        
        print('\n✓ All feeds and metadata generated successfully')
    except Exception as e:
        print(f'Error generating feeds: {e}')
        import traceback
        traceback.print_exc()
        exit(1)
