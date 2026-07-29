import json, hashlib, math, os

ACCENT = "#1B4D3E"
INK = "#111111"
LINE = "#111111"

# category -> (icon path builder key, tonal bg tint)
CATEGORY_STYLE = {
    'Personal Budgeting':    {'tint': '#F3F2ED', 'icon': 'jars'},
    'Saving Strategies':     {'tint': '#F1F3EF', 'icon': 'coins'},
    'Financial Habits':      {'tint': '#F4F1EE', 'icon': 'wallet'},
    'Investing Basics':      {'tint': '#EFF2F0', 'icon': 'chart'},
    'Money Psychology':      {'tint': '#F3F1F0', 'icon': 'seed'},
    'Income & Career':       {'tint': '#F2F3EE', 'icon': 'ladder'},
    'Economics':             {'tint': '#EEF2F1', 'icon': 'globe'},
    'Financial Literacy':    {'tint': '#F4F2ED', 'icon': 'book'},
    'Financial Technology':  {'tint': '#EFF3F2', 'icon': 'device'},
}

def seeded(s, n=1000):
    h = int(hashlib.md5(s.encode()).hexdigest(), 16)
    return h % n

def icon_paths(kind, cx, cy, s):
    """Return list of SVG path/shape strings, monoline, centered roughly at cx,cy scale s."""
    p = []
    if kind == 'jars':
        for i,dx in enumerate([-1.2,0,1.2]):
            x = cx+dx*s*0.5
            p.append(f'<rect x="{x-0.35*s}" y="{cy-0.6*s}" width="{0.7*s}" height="{1.1*s}" rx="{0.08*s}" fill="none" stroke="{ACCENT}" stroke-width="{0.02*s}"/>')
            p.append(f'<line x1="{x-0.35*s}" y1="{cy-0.25*s}" x2="{x+0.35*s}" y2="{cy-0.25*s}" stroke="{ACCENT}" stroke-width="{0.02*s}"/>')
    elif kind == 'coins':
        for i in range(4):
            y = cy+0.35*s-i*0.22*s
            p.append(f'<ellipse cx="{cx}" cy="{y}" rx="{0.55*s}" ry="{0.16*s}" fill="none" stroke="{ACCENT}" stroke-width="{0.02*s}"/>')
    elif kind == 'wallet':
        p.append(f'<rect x="{cx-0.8*s}" y="{cy-0.55*s}" width="{1.6*s}" height="{1.1*s}" rx="{0.1*s}" fill="none" stroke="{ACCENT}" stroke-width="{0.02*s}"/>')
        p.append(f'<circle cx="{cx+0.45*s}" cy="{cy}" r="{0.1*s}" fill="none" stroke="{ACCENT}" stroke-width="{0.02*s}"/>')
    elif kind == 'chart':
        pts = [(cx-0.9*s,cy+0.5*s),(cx-0.4*s,cy-0.1*s),(cx+0.05*s,cy+0.25*s),(cx+0.55*s,cy-0.55*s),(cx+0.95*s,cy-0.15*s)]
        d = 'M ' + ' L '.join(f'{x:.1f} {y:.1f}' for x,y in pts)
        p.append(f'<path d="{d}" fill="none" stroke="{ACCENT}" stroke-width="{0.025*s}" stroke-linejoin="round" stroke-linecap="round"/>')
        for x,y in pts:
            p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.035*s}" fill="{ACCENT}"/>')
    elif kind == 'seed':
        p.append(f'<path d="M {cx} {cy+0.6*s} Q {cx} {cy-0.1*s} {cx-0.5*s} {cy-0.4*s}" fill="none" stroke="{ACCENT}" stroke-width="{0.02*s}"/>')
        p.append(f'<path d="M {cx} {cy+0.2*s} Q {cx} {cy-0.2*s} {cx+0.5*s} {cy-0.5*s}" fill="none" stroke="{ACCENT}" stroke-width="{0.02*s}"/>')
        p.append(f'<ellipse cx="{cx}" cy="{cy+0.65*s}" rx="{0.7*s}" ry="{0.12*s}" fill="none" stroke="{ACCENT}" stroke-width="{0.02*s}"/>')
    elif kind == 'ladder':
        p.append(f'<line x1="{cx-0.5*s}" y1="{cy+0.7*s}" x2="{cx-0.5*s}" y2="{cy-0.7*s}" stroke="{ACCENT}" stroke-width="{0.02*s}"/>')
        p.append(f'<line x1="{cx+0.5*s}" y1="{cy+0.7*s}" x2="{cx+0.5*s}" y2="{cy-0.7*s}" stroke="{ACCENT}" stroke-width="{0.02*s}"/>')
        for i in range(5):
            y = cy+0.6*s-i*0.32*s
            p.append(f'<line x1="{cx-0.5*s}" y1="{y}" x2="{cx+0.5*s}" y2="{y}" stroke="{ACCENT}" stroke-width="{0.018*s}"/>')
    elif kind == 'globe':
        p.append(f'<circle cx="{cx}" cy="{cy}" r="{0.75*s}" fill="none" stroke="{ACCENT}" stroke-width="{0.02*s}"/>')
        p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{0.3*s}" ry="{0.75*s}" fill="none" stroke="{ACCENT}" stroke-width="{0.015*s}"/>')
        p.append(f'<line x1="{cx-0.75*s}" y1="{cy}" x2="{cx+0.75*s}" y2="{cy}" stroke="{ACCENT}" stroke-width="{0.015*s}"/>')
    elif kind == 'book':
        p.append(f'<path d="M {cx-0.7*s} {cy-0.55*s} Q {cx} {cy-0.75*s} {cx+0.7*s} {cy-0.55*s} L {cx+0.7*s} {cy+0.55*s} Q {cx} {cy+0.35*s} {cx-0.7*s} {cy+0.55*s} Z" fill="none" stroke="{ACCENT}" stroke-width="{0.02*s}"/>')
        p.append(f'<line x1="{cx}" y1="{cy-0.68*s}" x2="{cx}" y2="{cy+0.42*s}" stroke="{ACCENT}" stroke-width="{0.02*s}"/>')
    elif kind == 'device':
        p.append(f'<rect x="{cx-0.45*s}" y="{cy-0.75*s}" width="{0.9*s}" height="{1.5*s}" rx="{0.12*s}" fill="none" stroke="{ACCENT}" stroke-width="{0.02*s}"/>')
        p.append(f'<line x1="{cx-0.25*s}" y1="{cy-0.35*s}" x2="{cx+0.25*s}" y2="{cy-0.35*s}" stroke="{ACCENT}" stroke-width="{0.018*s}"/>')
        p.append(f'<line x1="{cx-0.25*s}" y1="{cy-0.1*s}" x2="{cx+0.1*s}" y2="{cy-0.1*s}" stroke="{ACCENT}" stroke-width="{0.018*s}"/>')
    return p

def make_cover(slug, category, article_id, w=1200, h=800):
    style = CATEGORY_STYLE.get(category, {'tint':'#F3F2ED','icon':'chart'})
    seed = seeded(slug)
    rot = (seed % 7) - 3
    cx, cy = w*0.66, h*0.52
    s = min(w,h) * 0.30
    icons = icon_paths(style['icon'], cx, cy, s)
    # fine grid dots
    dots = []
    step = 46
    for gx in range(step, w, step):
        for gy in range(step, h, step):
            dots.append(f'<circle cx="{gx}" cy="{gy}" r="1" fill="{INK}" opacity="0.045"/>')
    idx = f'{article_id:02d}'
    svg = f'''<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{w}" height="{h}" fill="{style['tint']}"/>
  {''.join(dots)}
  <line x1="0" y1="{h-1}" x2="{w}" y2="{h-1}" stroke="{INK}" stroke-opacity="0.08"/>
  <text x="56" y="88" font-family="Manrope, sans-serif" font-size="20" letter-spacing="2" fill="{INK}" opacity="0.38">{category.upper()}</text>
  <text x="56" y="{h-56}" font-family="Manrope, sans-serif" font-weight="700" font-size="72" fill="{INK}" opacity="0.08">{idx}</text>
  <g transform="rotate({rot} {cx} {cy})" opacity="0.9">
    {''.join(icons)}
  </g>
</svg>'''
    return svg

if __name__ == '__main__':
    articles = json.load(open('/home/claude/billionblogs/data/articles.json'))
    os.makedirs('/home/claude/billionblogs/assets/img/covers', exist_ok=True)
    for a in articles:
        svg = make_cover(a['slug'], a['category'], a['id'])
        open(f"/home/claude/billionblogs/assets/img/covers/{a['slug']}.svg","w").write(svg)
    # category hero covers (wide banner variant reusing icon at larger scale, no idx)
    for cat, style in CATEGORY_STYLE.items():
        slug = cat.lower().replace(' & ','-').replace(' ','-')
        svg = make_cover(slug, cat, 0, w=1600, h=520)
        svg = svg.replace('<text x="56" y="{}" font-family="Manrope, sans-serif" font-weight="700" font-size="72" fill="#111111" opacity="0.08">00</text>'.format(520-56), '')
        open(f"/home/claude/billionblogs/assets/img/covers/cat-{slug}.svg","w").write(svg)
    print("Generated", len(articles), "article covers +", len(CATEGORY_STYLE), "category covers")
