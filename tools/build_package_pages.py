#!/usr/bin/env python3
"""Build one page per package at /packages/<name>/ from the package's README on GitHub and its pub.dev metadata.
Reuses the home page's styles, nav and footer so every page looks like the site. Re-run after a README or version change.
Needs: the GitHub CLI (`gh`, signed in) for README fetch + GitHub-flavoured Markdown rendering.
  python3 tools/build_package_pages.py
"""
import html, json, os, re, subprocess, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://flutterdev.in/'
OWNER = 'Manish1Pandey'
AUTHOR = {'@type': 'Person', 'name': 'Manish Kumar Panday', 'url': SITE}
e = lambda s: html.escape(s, quote=True)

home = open(os.path.join(ROOT, 'index.html'), encoding='utf8').read()
style = re.search(r'<style>(.*?)</style>', home, re.S).group(1)
favicon = re.search(r'<link rel="icon" href="[^"]*">', home).group(0)
nav = re.search(r'<nav>.*?</nav>', home, re.S).group(0).replace('href="#packages"', 'href="/#packages"')
footer = re.search(r'<footer class="wrap">.*?</footer>', home, re.S).group(0)
theme_js = """<script>(function(){var r=document.documentElement;try{var s=localStorage.getItem('t');if(s)r.setAttribute('data-t',s);}catch(e){}
function f(){var c=r.getAttribute('data-t');if(!c)c=matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light';var n=c==='dark'?'light':'dark';r.setAttribute('data-t',n);try{localStorage.setItem('t',n);}catch(e){}}
document.getElementById('tt').addEventListener('click',function(){if(document.startViewTransition&&!matchMedia('(prefers-reduced-motion:reduce)').matches)document.startViewTransition(f);else f();});
document.querySelectorAll('.cp').forEach(function(b){b.addEventListener('click',function(){navigator.clipboard&&navigator.clipboard.writeText(b.dataset.c).then(function(){b.textContent='Copied';setTimeout(function(){b.textContent='Copy';},1400);});});});})();</script>"""

PAGE_CSS = """
.pk{padding:40px 0 70px;}
.crumbs{font-size:13.5px; color:var(--mute); margin-bottom:18px;}
.crumbs a{color:var(--mute); text-decoration:none;} .crumbs a:hover{color:var(--brand);}
.pk-head h1{font-size:clamp(30px,5vw,46px); letter-spacing:-.03em; margin:0 0 10px; word-break:break-word;}
.pk-head .lede{font-size:18px; color:var(--mute); max-width:760px; margin:0 0 20px; line-height:1.55;}
.pk-meta{display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:22px;}
.pk-meta .tag{font-size:13px; font-weight:600; padding:5px 11px; border-radius:999px; border:1px solid var(--line); background:var(--surf); color:var(--ink);}
.pk-meta .tag.ok{color:var(--ok);}
.pk-actions{display:flex; flex-wrap:wrap; gap:10px; margin-bottom:26px;}
.pk .dep{max-width:520px; margin-bottom:34px;}
.md{max-width:860px; font-size:16px; line-height:1.7; color:var(--ink); overflow-wrap:break-word;}
.md :not(pre) > code, .md a{overflow-wrap:anywhere;}
.pk-head .lede, .dep code{overflow-wrap:anywhere;}
.md h1{display:none;}
.md h2{font-size:26px; letter-spacing:-.02em; margin:42px 0 12px; padding-top:8px; border-top:1px solid var(--line);}
.md h3{font-size:19px; margin:28px 0 8px;}
.md a{color:var(--brand);} .md a.anchor{display:none;}
.md p,.md li{color:var(--ink);} .md ul,.md ol{padding-left:22px;}
.md code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.88em; background:var(--surf2); padding:2px 6px; border-radius:6px;}
.md pre{background:var(--surf2); border:1px solid var(--line); border-radius:12px; padding:16px 18px; overflow-x:auto; line-height:1.55;}
.md pre code{background:none; padding:0; font-size:13.5px;}
.md .highlight{margin:14px 0;}
.md table{border-collapse:collapse; display:block; overflow-x:auto; max-width:100%; margin:16px 0;}
.md th,.md td{border:1px solid var(--line); padding:8px 12px; text-align:left; vertical-align:top;}
.md th{background:var(--surf2);}
.md img{max-width:100%; height:auto; border-radius:10px;}
.md p > a > img, .md p > img[src*="shields.io"], .md p > a > img[src*="pub.dev"]{border-radius:0;}
.md blockquote{margin:16px 0; padding:4px 16px; border-left:3px solid var(--brand); color:var(--mute);}
.md .markdown-alert{border-left:3px solid var(--brand); padding:6px 16px; margin:16px 0; background:var(--sky); border-radius:0 10px 10px 0;}
.md .markdown-alert-title{font-weight:700;} .md svg.octicon{display:none;}
/* GitHub syntax colours */
.md .pl-k{color:#cf222e;} .md .pl-s,.md .pl-pds{color:#0a3069;} .md .pl-c{color:#6e7781; font-style:italic;}
.md .pl-en,.md .pl-e{color:#8250df;} .md .pl-c1,.md .pl-v{color:#0550ae;} .md .pl-smi{color:inherit;} .md .pl-ent{color:#116329;}
:root[data-t="dark"] .md .pl-k{color:#ff7b72;} :root[data-t="dark"] .md .pl-s,:root[data-t="dark"] .md .pl-pds{color:#a5d6ff;}
:root[data-t="dark"] .md .pl-c{color:#8b949e;} :root[data-t="dark"] .md .pl-en,:root[data-t="dark"] .md .pl-e{color:#d2a8ff;}
:root[data-t="dark"] .md .pl-c1,:root[data-t="dark"] .md .pl-v{color:#79c0ff;} :root[data-t="dark"] .md .pl-ent{color:#7ee787;}
@media (prefers-color-scheme:dark){:root:not([data-t="light"]) .md .pl-k{color:#ff7b72;} :root:not([data-t="light"]) .md .pl-s,:root:not([data-t="light"]) .md .pl-pds{color:#a5d6ff;}
  :root:not([data-t="light"]) .md .pl-c{color:#8b949e;} :root:not([data-t="light"]) .md .pl-en,:root:not([data-t="light"]) .md .pl-e{color:#d2a8ff;}
  :root:not([data-t="light"]) .md .pl-c1,:root:not([data-t="light"]) .md .pl-v{color:#79c0ff;} :root:not([data-t="light"]) .md .pl-ent{color:#7ee787;}}
.more-pk{margin-top:56px; padding-top:24px; border-top:1px solid var(--line);}
.more-pk h2{font-size:20px; margin:0 0 12px;}
.more-pk ul{list-style:none; padding:0; margin:0; display:flex; flex-wrap:wrap; gap:8px;}
.more-pk a{display:inline-block; font-size:14px; padding:7px 12px; border-radius:9px; border:1px solid var(--line); background:var(--surf); color:var(--ink); text-decoration:none;}
.more-pk a:hover{border-color:var(--brand); color:var(--brand);}
"""

def gh(args, inp=None):
    return subprocess.run(['gh'] + args, input=inp, capture_output=True, text=True, check=True).stdout

def render(name, md):
    md = re.sub(r'\A\s*#\s[^\n]*\n', '', md)   # the page's own <h1> carries the name
    out = gh(['api', 'markdown', '--input', '-'], json.dumps({'text': md, 'mode': 'markdown', 'context': OWNER + '/' + name}))
    raw = 'https://raw.githubusercontent.com/%s/%s/HEAD/' % (OWNER, name)
    blob = 'https://github.com/%s/%s/blob/HEAD/' % (OWNER, name)
    out = re.sub(r'(<img[^>]*\ssrc=")(?!https?:|data:)\.?/?([^"]+)"', lambda m: m.group(1) + raw + m.group(2) + '"', out)
    out = re.sub(r'(<a[^>]*\shref=")(?!https?:|#|mailto:)\.?/?([^"]+)"', lambda m: m.group(1) + blob + m.group(2) + '"', out)
    out = re.sub(r'<img ', '<img loading="lazy" ', out)
    return out

cards = re.findall(r'<article class="card" data-n="([a-z_0-9]+)" data-b="[^"]*" data-p="([^"]*)" data-live="(\d)"', home)
names = [c[0] for c in cards]
PLAT = {'android': 'Android', 'ios': 'iOS', 'macos': 'macOS', 'windows': 'Windows', 'linux': 'Linux', 'web': 'Web'}
sitemap_urls = []

for name, plats, live in cards:
    pub = json.load(urllib.request.urlopen('https://pub.dev/api/packages/' + name))['latest']
    ver, desc = pub['version'], pub['pubspec']['description'].strip()
    blurb = re.search(r'data-n="%s"[\s\S]*?<p class="blurb">([^<]*)</p>' % name, home).group(1)
    md = gh(['api', 'repos/%s/%s/readme' % (OWNER, name), '-H', 'Accept: application/vnd.github.raw'])
    body = render(name, md)
    url = SITE + 'packages/' + name + '/'
    title = '%s · Flutter package: %s | flutterdev.in' % (name, blurb.rstrip('.'))
    meta_desc = desc if len(desc) <= 160 else desc[:157].rsplit(' ', 1)[0] + '…'
    platforms = [PLAT[p] for p in plats.split() if p in PLAT]
    ld = [
        {'@context': 'https://schema.org', '@type': 'SoftwareSourceCode', 'name': name, 'description': desc, 'url': url,
         'codeRepository': 'https://github.com/%s/%s' % (OWNER, name), 'programmingLanguage': 'Dart', 'runtimePlatform': 'Flutter',
         'version': ver, 'license': 'https://opensource.org/licenses/MIT', 'author': AUTHOR,
         'targetProduct': {'@type': 'SoftwareApplication', 'name': name, 'operatingSystem': ', '.join(platforms), 'applicationCategory': 'DeveloperApplication'}},
        {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'flutterdev.in', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': 'Packages', 'item': SITE + '#packages'},
            {'@type': 'ListItem', 'position': 3, 'name': name, 'item': url}]}]
    demo = '<a class="btn sec" href="/demos/%s/">&#9658; Live demo</a>' % name if live == '1' else ''
    others = ''.join('<li><a href="/packages/%s/">%s</a></li>' % (n, n) for n in names if n != name)
    page = f"""<!DOCTYPE html>
<html lang="en" data-t="">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(meta_desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#f6f8fb" media="(prefers-color-scheme:light)">
<meta name="theme-color" content="#060c14" media="(prefers-color-scheme:dark)">
<meta property="og:type" content="article">
<meta property="og:site_name" content="flutterdev.in">
<meta property="og:title" content="{e(name)} · Flutter package">
<meta property="og:description" content="{e(meta_desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}og.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{''.join('<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>' for o in ld)}
{favicon}
<style>{style}{PAGE_CSS}</style>
</head>
<body>
{nav}
<main class="wrap pk">
  <div class="crumbs"><a href="/">flutterdev.in</a> &rsaquo; <a href="/#packages">Packages</a> &rsaquo; {e(name)}</div>
  <header class="pk-head">
    <h1>{e(name)}</h1>
    <p class="lede">{e(desc)}</p>
    <div class="pk-meta"><span class="tag">v{e(ver)}</span><span class="tag ok">160/160 pub points</span><span class="tag">MIT</span>{''.join('<span class="tag">%s</span>' % p for p in platforms)}</div>
    <div class="pk-actions"><a class="btn pri" href="https://pub.dev/packages/{name}">View on pub.dev &#8594;</a>{demo}<a class="btn sec" href="https://github.com/{OWNER}/{name}">Source on GitHub</a></div>
    <div class="dep"><code>{name}: ^{e(ver)}</code><button class="cp" data-c="{name}: ^{e(ver)}" aria-label="Copy dependency for {name}">Copy</button></div>
  </header>
  <article class="md">
{body}
  </article>
  <section class="more-pk"><h2>More Flutter packages</h2><ul>{others}</ul></section>
</main>
{footer}
{theme_js}
</body>
</html>
"""
    os.makedirs(os.path.join(ROOT, 'packages', name), exist_ok=True)
    open(os.path.join(ROOT, 'packages', name, 'index.html'), 'w', encoding='utf8').write(page)
    sitemap_urls.append(url)
    print('built packages/%s/ (v%s)' % (name, ver))

# keep the sitemap in step: home/demos entries stay, package pages are (re)listed
sm_path = os.path.join(ROOT, 'sitemap.xml'); sm = open(sm_path, encoding='utf8').read()
sm = re.sub(r'\s*<url><loc>https://flutterdev\.in/packages/[^<]*</loc>.*?</url>', '', sm)
import time; today = time.strftime('%Y-%m-%d')
add = ''.join('\n  <url><loc>%s</loc><lastmod>%s</lastmod><priority>0.8</priority></url>' % (u, today) for u in sitemap_urls)
sm = sm.replace('\n</urlset>', add + '\n</urlset>')
open(sm_path, 'w', encoding='utf8').write(sm)
print('sitemap: %d package pages listed' % len(sitemap_urls))
