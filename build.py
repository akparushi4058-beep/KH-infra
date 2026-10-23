#!/usr/bin/env python3
"""Generate the product and category pages, sitemap and search data from catalog.json.

Run after editing catalog.json (products, photos, specs) or the shared header/footer in index.html:

    python3 build.py

It rewrites the BUILD: sections inside index.html and writes:
  /<product-slug>/index.html, /<category-slug>/index.html, sitemap.xml, robots.txt, llms.txt
"""
import datetime
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SITE = 'https://www.khgroupindia.com'
BRAND = 'KH Infra Equipment'
PHONE_1, PHONE_1_LABEL = '+918386055533', '+91 83860 55533'
PHONE_2, PHONE_2_LABEL = '+919414076912', '+91 94140 76912'
WA_NUMBER = '918386055533'
EMAIL = 'kanishk.khgroup@gmail.com'
ADDRESS = {
    'streetAddress': 'H1/2200, RIICO Industrial Area, Ramchandrapura',
    'addressLocality': 'Jaipur', 'addressRegion': 'Rajasthan', 'postalCode': '302022', 'addressCountry': 'IN',
}
MAPS_URL = 'https://maps.app.goo.gl/HFTsFfnXqTJ4pwSG7'
INDIAMART_URL = 'https://www.indiamart.com/kh-infra-equipment/'
TODAY = datetime.date.today().isoformat()

esc = html.escape
LAZY = ' loading="lazy"'
catalog = json.loads((ROOT / 'catalog.json').read_text())
CATS = {c['id']: c for c in catalog['categories']}
PRODUCTS = catalog['products']
index = (ROOT / 'index.html').read_text()


def section(name, text=index):
    m = re.search(rf'<!-- BUILD:{name} -->(.*?)<!-- /BUILD:{name} -->', text, re.S)
    return m.group(1)


def replace_section(text, name, content):
    return re.sub(rf'(<!-- BUILD:{name} -->).*?(<!-- /BUILD:{name} -->)',
                  lambda m: m.group(1) + content + m.group(2), text, flags=re.S)


def absolute(url):
    return url if url.startswith('http') else SITE + url


def ld(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'


ORG = {
    '@context': 'https://schema.org', '@type': 'LocalBusiness', '@id': SITE + '/#business',
    'name': BRAND, 'url': SITE + '/', 'logo': SITE + '/img/kh-infra-equipment-logo.png',
    'image': SITE + '/products/gw42-expo.jpg',
    'description': 'Construction machinery supplier in Jaipur: bar bending and cutting machines, monkey cranes and hoists, '
                   'suspended platforms, concrete mixers and compaction equipment, delivered across India.',
    'telephone': PHONE_1, 'email': EMAIL,
    'address': {'@type': 'PostalAddress', **ADDRESS},
    'hasMap': MAPS_URL, 'areaServed': 'IN',
    'contactPoint': [{'@type': 'ContactPoint', 'telephone': t, 'contactType': 'sales', 'areaServed': 'IN',
                      'availableLanguage': ['en', 'hi']} for t in (PHONE_1, PHONE_2)],
    'sameAs': [INDIAMART_URL],
}

WA_ICON = re.search(r'<svg viewBox="0 0 32 32" fill="currentColor" width="16" height="16">.*?</svg>', index, re.S).group(0)
PHONE_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" width="16" height="16">'
              '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 20 20 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 20 20 0 0 1-3.1-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.6a2 2 0 0 1-.5 2.1L8 9.6a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.8.3 1.7.5 2.6.6a2 2 0 0 1 1.7 2z"/></svg>')
HEADER, FOOTER = section('HEADER'), section('FOOTER')
FAB = re.search(r'<!-- WHATSAPP FAB -->.*?</a>', index, re.S).group(0)
GA = re.search(r'<!-- Google Analytics \(GA4\) -->.*?</script>\s*<script>.*?</script>', index, re.S).group(0)


def head(title, description, path, image, schema):
    url = SITE + path
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}" />
<link rel="canonical" href="{url}" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(description)}" />
<meta property="og:type" content="website" />
<meta property="og:url" content="{url}" />
<meta property="og:image" content="{absolute(image)}" />
<meta property="og:site_name" content="{BRAND}" />
<link rel="icon" href="/favicon.ico" sizes="48x48" />
<link rel="icon" type="image/png" href="/favicon-192.png" sizes="192x192" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
{GA}
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/styles.css" />
{schema}
</head>'''


def crumbs(items):
    """items: [(label, path or None)] → visible breadcrumb + schema"""
    parts = []
    for i, (label, path) in enumerate(items):
        if i:
            parts.append('<span aria-hidden="true">›</span>')
        parts.append(f'<a href="{path}">{esc(label)}</a>' if path else f'<span>{esc(label)}</span>')
    schema = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': label, 'item': SITE + (path or '')}
        for i, (label, path) in enumerate(items) if path is not None or i == len(items) - 1]}
    return f'<nav class="crumbs" aria-label="Breadcrumb">{"".join(parts)}</nav>', schema


def card(p):
    img = p['images'][0]
    return f'''
    <a class="p" href="/{p['slug']}/" data-slug="{p['slug']}">
      <div class="ph">
        <span class="tr">↗</span>
        <img class="fill" src="{img}" alt="" aria-hidden="true" loading="lazy" />
        <img src="{img}" alt="{esc(p['name'])}" loading="lazy" />
      </div>
      <div class="info"><div class="row"><div class="name">{esc(p['name'])}</div></div></div>
    </a>'''


def wa_link(text):
    from urllib.parse import quote
    return f'https://wa.me/{WA_NUMBER}?text={quote(text)}'


def faqs(p):
    name = p['name']
    return [
        (f'What is the price of the {name}?',
         f'The price depends on the model, configuration and delivery location. WhatsApp or call us on {PHONE_1_LABEL} '
         f'and we will share today\'s price.'),
        (f'Do you deliver the {name} outside Jaipur?',
         'Yes. We deliver across India from our facility in Jaipur, Rajasthan.'),
        (f'What else is the {name} called?', 'It is also known as ' + ', '.join(p['aliases']) + '.'),
        ('Can I see the machine before buying?',
         'Yes. Visit us at H1/2200, RIICO Industrial Area, Ramchandrapura, Jaipur 302022. Call ahead so we can have the '
         'machine ready, or ask on WhatsApp for photos and videos.'),
    ]


def short_specs(p, n=2):
    return ', '.join(f'{k} {v}' for k, v in list(p['specs'].items())[:n] if '~' not in v)


def product_page(p):
    cat = CATS[p['cat']]
    path = f"/{p['slug']}/"
    alias = next((a for a in p['aliases'] if a.isascii() and a.lower() not in p['name'].lower()), '')
    title = f"{p['name']} ({alias}) | {BRAND}, Jaipur" if alias else f"{p['name']} | {BRAND}, Jaipur"
    description = (f"{p['name']}: {short_specs(p)}. {p['desc'].split('. ')[0].rstrip('.')}. "
                   f"Also called {', '.join(a for a in p['aliases'][:3] if a.isascii())}. Delivery across India. "
                   f"Call {PHONE_1_LABEL}.")
    crumb_html, crumb_schema = crumbs([('Home', '/'), (cat['title'], f"/{cat['slug']}/"), (p['name'], None)])
    crumb_schema['itemListElement'][-1]['item'] = SITE + path
    product_schema = {
        '@context': 'https://schema.org', '@type': 'Product', 'name': p['name'], 'url': SITE + path,
        'image': [absolute(i) for i in p['images']], 'description': p['desc'],
        'brand': {'@type': 'Brand', 'name': BRAND}, 'category': cat['title'],
        'seller': {'@id': SITE + '/#business'},
    }
    faq_list = faqs(p)
    images = ''.join(
        f'<a href="{img}" target="_blank" rel="noopener"><img src="{img}" alt="{esc(p["name"])} – photo {i + 1}"'
        f'{"" if i == 0 else LAZY} /></a>' for i, img in enumerate(p['images']))
    thumbs = ''.join(f'<button type="button" class="{"on" if i == 0 else ""}" aria-label="Photo {i + 1}">'
                     f'<img src="{img}" alt="" loading="lazy" /></button>' for i, img in enumerate(p['images'])) \
        if len(p['images']) > 1 else ''
    specs = ''.join(f'<dt>{esc(k)}</dt><dd>{esc(v)}</dd>' for k, v in p['specs'].items())
    related = [q for q in PRODUCTS if q['cat'] == p['cat'] and q is not p][:4]
    wa = wa_link(f"Hi {BRAND}, I'm interested in the {p['name']}. Please share price and availability.\n{SITE}{path}")
    return f'''{head(title, description, path, p['images'][0], ld(product_schema) + ld(crumb_schema))}
<body class="has-sticky-cta">
{HEADER}
<main class="container pd">
  {crumb_html}
  <div class="pd-grid">
    <div class="pd-gallery">
      <div class="pd-track" id="track">{images}</div>
      <div class="pd-thumbs" id="thumbs">{thumbs}</div>
    </div>
    <div>
      <a class="pd-cat" href="/{cat['slug']}/">{esc(cat['label'])}</a>
      <h1>{esc(p['name'])}</h1>
      <p class="pd-aka"><b>Also known as:</b> {esc(', '.join(p['aliases']))}</p>
      <p class="pd-text">{esc(p['desc'])}</p>
      <h2>Specifications</h2>
      <dl class="pd-specs">{specs}</dl>
      <div class="pd-cta pd-cta-sticky">
        <a class="btn wa" href="{esc(wa)}" target="_blank" rel="noopener">{WA_ICON} WhatsApp</a>
        <a class="btn primary" href="tel:{PHONE_1}">{PHONE_ICON} Call</a>
      </div>
      <h2>Questions</h2>
      <div class="pd-faq">{''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faq_list)}</div>
    </div>
  </div>
</main>
{f"""<section class="related"><div class="container">
  <h2>More {esc(cat['label'].lower())} machines</h2>
  <div class="grid">{''.join(card(q) for q in related)}</div>
</div></section>""" if related else ''}
{FOOTER}
{FAB}
<script>
// Gallery: thumbnails jump to a photo, and follow the photo when swiping
const track = document.getElementById('track'), thumbs = [...document.querySelectorAll('#thumbs button')];
thumbs.forEach((b, i) => b.addEventListener('click', () => track.scrollTo({{ left: i * track.clientWidth, behavior: 'smooth' }})));
track.addEventListener('scroll', () => {{
  const i = Math.round(track.scrollLeft / track.clientWidth);
  thumbs.forEach((b, k) => b.classList.toggle('on', k === i));
}}, {{ passive: true }});
</script>
</body>
</html>
'''


def category_page(c):
    items = [p for p in PRODUCTS if p['cat'] == c['id']]
    path = f"/{c['slug']}/"
    title = f"{c['title']} in Jaipur | {BRAND}"
    description = f"{c['intro']} {len(items)} models. Delivery across India. Call {PHONE_1_LABEL}."
    crumb_html, crumb_schema = crumbs([('Home', '/'), (c['title'], None)])
    crumb_schema['itemListElement'][-1]['item'] = SITE + path
    list_schema = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': c['title'],
                   'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f"{SITE}/{p['slug']}/",
                                        'name': p['name']} for i, p in enumerate(items)]}
    others = ''.join(f'<a href="/{o["slug"]}/">{esc(o["title"])}</a>' for o in catalog['categories'] if o is not c)
    return f'''{head(title, description, path, c['icon'], ld(list_schema) + ld(crumb_schema))}
<body>
{HEADER}
<main class="container cat-page">
  {crumb_html}
  <h1>{esc(c['title'])}</h1>
  <p class="intro-text">{esc(c['intro'])}</p>
  <p class="aka">Also searched as: {esc(', '.join(c['aliases']))}</p>
  <div class="grid">{''.join(card(p) for p in items)}</div>
  <div class="cat-links">{others}</div>
</main>
<section class="about" style="padding: 40px 0 0"><div class="container">
  <p>Need a price or delivery date? WhatsApp or call <a href="tel:{PHONE_1}">{PHONE_1_LABEL}</a> or
  <a href="tel:{PHONE_2}">{PHONE_2_LABEL}</a>. We deliver across India from Jaipur.</p>
</div></section>
{FOOTER}
{FAB}
</body>
</html>
'''


def build():
    # Homepage: inline the catalogue data, render cards and categories for search engines, add business schema
    cats_html = ''.join(
        f'<a class="cat-item{" on" if c["id"] == "all" else ""}" href="{"/" + c["slug"] + "/" if c.get("slug") else "/#catalog"}" '
        f'data-cat="{c["id"]}"><span class="ic{" photo" if c.get("photo") else ""}"><img src="{c["icon"]}" alt="" loading="lazy" /></span>'
        f'<span class="lb">{esc(c["label"])}</span></a>'
        for c in [{'id': 'all', 'label': 'All', 'icon': '/favicon-192.png'}] + catalog['categories'])
    data = json.dumps(catalog, ensure_ascii=False).replace('</', '<\\/')
    website = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': BRAND, 'url': SITE + '/'}
    out = index
    out = replace_section(out, 'SCHEMA', ld(ORG) + ld(website))
    out = replace_section(out, 'CATS', cats_html)
    out = replace_section(out, 'GRID', ''.join(card(p) for p in PRODUCTS))
    out = replace_section(out, 'DATA', f'<script id="catalog-data" type="application/json">{data}</script>')
    (ROOT / 'index.html').write_text(out)

    for p in PRODUCTS:
        (ROOT / p['slug']).mkdir(exist_ok=True)
        (ROOT / p['slug'] / 'index.html').write_text(product_page(p))
    for c in catalog['categories']:
        (ROOT / c['slug']).mkdir(exist_ok=True)
        (ROOT / c['slug'] / 'index.html').write_text(category_page(c))

    urls = ['/'] + [f"/{c['slug']}/" for c in catalog['categories']] + [f"/{p['slug']}/" for p in PRODUCTS]
    (ROOT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n' for u in urls) + '</urlset>\n')
    (ROOT / 'robots.txt').write_text(
        '# Search engines and AI assistants are welcome to read this site\n'
        'User-agent: *\nAllow: /\n\n'
        'User-agent: Googlebot\nAllow: /\n\nUser-agent: Bingbot\nAllow: /\n\n'
        'User-agent: OAI-SearchBot\nAllow: /\n\nUser-agent: ChatGPT-User\nAllow: /\n\nUser-agent: GPTBot\nAllow: /\n\n'
        f'Sitemap: {SITE}/sitemap.xml\n')
    lines = [f'# {BRAND}', '',
             f'> Construction machinery supplier in Jaipur, Rajasthan, India. Delivers across India. '
             f'Phone/WhatsApp {PHONE_1_LABEL}, {PHONE_2_LABEL}. Email {EMAIL}. '
             f'Address: {ADDRESS["streetAddress"]}, Jaipur, Rajasthan {ADDRESS["postalCode"]}.', '']
    for c in catalog['categories']:
        lines += [f"## {c['title']}", '']
        lines += [f"- [{p['name']}]({SITE}/{p['slug']}/): {p['desc']} Also known as: {', '.join(p['aliases'])}."
                  for p in PRODUCTS if p['cat'] == c['id']]
        lines.append('')
    (ROOT / 'llms.txt').write_text('\n'.join(lines))
    print(f'Built {len(PRODUCTS)} product pages, {len(catalog["categories"])} category pages, {len(urls)} URLs in sitemap.')


if __name__ == '__main__':
    build()
