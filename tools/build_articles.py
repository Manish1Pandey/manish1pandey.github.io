#!/usr/bin/env python3
"""Build article pages under /articles/<slug>/ from Markdown files in articles-src/ (front matter: title, description,
date), rendered with GitHub's Markdown API (`gh` signed in) and wrapped in the home page's styles, nav and footer.
Also writes /articles/ (an index) and keeps sitemap.xml in step.
  python3 tools/build_articles.py
"""
import glob, html, json, os, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://flutterdev.in/'
home = open(os.path.join(ROOT, 'index.html'), encoding='utf8').read()
style = re.search(r'<style>(.*?)</style>', home, re.S).group(1)
favicon = re.search(r'<link rel="icon" href="[^"]*">', home).group(0)
nav = re.search(r'<nav>.*?</nav>', home, re.S).group(0).replace('href="#packages"', 'href="/#packages"')
footer = re.search(r'<footer class="wrap">.*?</footer>', home, re.S).group(0)
pk = open(os.path.join(ROOT, 'packages/mobius_carousel/index.html'), encoding='utf8').read()
theme_js = re.search(r"<script>\(function\(\)\{var r=document\.documentElement.*?</script>", pk, re.S).group(0)
md_css = re.search(r'(\.md\{.*?)(?=\.more-pk)', re.search(r'<style>(.*?)</style>', pk, re.S).group(1), re.S).group(1)
e = lambda s: html.escape(s, quote=True)
AUTHOR = {'@type': 'Person', 'name': 'Manish Kumar Panday', 'url': SITE + 'about/'}
CSS = ".art{padding:40px 0 70px; max-width:820px;} .art h1{font-size:clamp(30px,5vw,44px); letter-spacing:-.03em; margin:6px 0 10px;} .art .meta{color:var(--mute); font-size:14px; margin-bottom:26px;} .crumbs{font-size:13.5px; color:var(--mute);} .crumbs a{color:var(--mute); text-decoration:none;} .alist{list-style:none; padding:0;} .alist li{border:1px solid var(--line); background:var(--surf); border-radius:14px; padding:16px 18px; margin-bottom:12px;} .alist a{font-weight:650; color:var(--ink); text-decoration:none; font-size:18px;} .alist p{margin:6px 0 0; color:var(--mute);}"

def shell(title, desc, url, body, ld, kind='article'):
    return f"""<!DOCTYPE html>
<html lang="en" data-t="">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} | flutterdev.in</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#f6f8fb" media="(prefers-color-scheme:light)">
<meta name="theme-color" content="#060c14" media="(prefers-color-scheme:dark)">
<meta property="og:type" content="{kind}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}og.png"><meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')}</script>
{favicon}
<style>{style}{md_css}{CSS}</style>
</head>
<body>
{nav}
<main class="wrap art">
{body}
</main>
{footer}
{theme_js}
</body>
</html>
"""

arts = []
for src in sorted(glob.glob(os.path.join(ROOT, 'articles-src', '*.md'))):
    raw = open(src, encoding='utf8').read()
    fm, md = re.match(r'---\n(.*?)\n---\n(.*)', raw, re.S).groups()
    meta = dict(re.findall(r'^(\w+):\s*(.+)$', fm, re.M))
    slug = os.path.splitext(os.path.basename(src))[0]; url = SITE + 'articles/' + slug + '/'
    body_html = subprocess.run(['gh', 'api', 'markdown', '--input', '-'], input=json.dumps({'text': md, 'mode': 'markdown'}), capture_output=True, text=True, check=True).stdout
    ld = {'@context': 'https://schema.org', '@type': 'TechArticle', 'headline': meta['title'], 'description': meta['description'], 'datePublished': meta['date'], 'author': AUTHOR, 'url': url, 'image': SITE + 'og.png', 'inLanguage': 'en'}
    body = f'<div class="crumbs"><a href="/">flutterdev.in</a> &rsaquo; <a href="/articles/">Articles</a></div>\n<h1>{e(meta["title"])}</h1>\n<div class="meta">{e(meta["date"])} · Manish Kumar Panday</div>\n<article class="md">{body_html}</article>'
    os.makedirs(os.path.join(ROOT, 'articles', slug), exist_ok=True)
    open(os.path.join(ROOT, 'articles', slug, 'index.html'), 'w', encoding='utf8').write(shell(meta['title'], meta['description'], url, body, ld))
    arts.append((meta, url)); print('built articles/' + slug + '/')

items = ''.join(f'<li><a href="{u}">{e(m["title"])}</a><p>{e(m["description"])}</p></li>' for m, u in sorted(arts, key=lambda a: a[0]['date'], reverse=True))
idx = f'<div class="crumbs"><a href="/">flutterdev.in</a> &rsaquo; Articles</div>\n<h1>Articles</h1>\n<div class="meta">Flutter and Dart notes, each claim checked by a test.</div>\n<ul class="alist">{items}</ul>'
open(os.path.join(ROOT, 'articles', 'index.html'), 'w', encoding='utf8').write(shell('Articles', 'Flutter and Dart articles from flutterdev.in, each claim checked by a test.', SITE + 'articles/', idx, {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'Articles', 'url': SITE + 'articles/'}, 'website'))
sm_p = os.path.join(ROOT, 'sitemap.xml'); sm = open(sm_p, encoding='utf8').read()
sm = re.sub(r'\s*<url><loc>https://flutterdev\.in/articles/[^<]*</loc>.*?</url>', '', sm)
add = ''.join('\n  <url><loc>%s</loc><lastmod>%s</lastmod><priority>0.7</priority></url>' % (u, m['date']) for m, u in arts) + '\n  <url><loc>%sarticles/</loc><priority>0.6</priority></url>' % SITE
open(sm_p, 'w', encoding='utf8').write(sm.replace('\n</urlset>', add + '\n</urlset>'))
print('articles index + sitemap updated (%d articles)' % len(arts))
