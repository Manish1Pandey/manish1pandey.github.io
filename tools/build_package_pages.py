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
function f(){var c=r.getAttribute('data-t');if(!c)c='dark';var n=c==='dark'?'light':'dark';r.setAttribute('data-t',n);try{localStorage.setItem('t',n);}catch(e){}}
document.getElementById('tt').addEventListener('click',function(){if(document.startViewTransition&&!matchMedia('(prefers-reduced-motion:reduce)').matches)document.startViewTransition(f);else f();});
document.querySelectorAll('.cp').forEach(function(b){b.addEventListener('click',function(){navigator.clipboard&&navigator.clipboard.writeText(b.dataset.c).then(function(){b.textContent='Copied';setTimeout(function(){b.textContent='Copy';},1400);});});});})();</script>"""

PAGE_CSS = """
.pk{padding:40px 0 70px;}
.crumbs{font-size:13.5px; color:var(--mute); margin-bottom:18px;}
.crumbs a{color:var(--mute); text-decoration:none;} .crumbs a:hover{color:var(--brand);}
.pk-head h1{font-family:var(--f-m); font-weight:700; font-size:clamp(28px,4.6vw,44px); letter-spacing:-.04em; margin:0 0 10px; word-break:break-word;}
.pk-head .lede{font-size:18px; color:var(--mute); max-width:760px; margin:0 0 20px; line-height:1.55;}
.pk-meta{display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:22px;}
.pk-meta .tag{font-size:13px; font-weight:600; padding:5px 11px; border-radius:999px; border:1px solid var(--line); background:var(--surf); color:var(--ink);}
.pk-meta .tag.ok{color:var(--ok);}
.pk-actions{display:flex; flex-wrap:wrap; gap:10px; margin-bottom:26px;}
.md{max-width:860px; font-size:16px; line-height:1.7; color:var(--ink); overflow-wrap:break-word;}
.md :not(pre) > code, .md a{overflow-wrap:anywhere;}
.pk-head .lede, .dep code{overflow-wrap:anywhere;}
.md h1{display:none;}
.md h2{font-size:26px; letter-spacing:-.02em; margin:42px 0 12px; padding-top:8px; border-top:1px solid var(--line);}
.md h3{font-size:19px; margin:28px 0 8px;}
.md a{color:var(--brand);} .md a.anchor{display:none;}
.md p,.md li{color:var(--ink);} .md ul,.md ol{padding-left:22px;}
.md code{font-family:var(--f-m); font-size:.88em; background:var(--surf2); padding:2px 6px; border-radius:6px;}
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
/* GitHub syntax colours: dark by default, light when the light theme is chosen */
.md .pl-k{color:#ff7b72;} .md .pl-s,.md .pl-pds{color:#a5d6ff;} .md .pl-c{color:#8b949e; font-style:italic;}
.md .pl-en,.md .pl-e{color:#d2a8ff;} .md .pl-c1,.md .pl-v{color:#79c0ff;} .md .pl-smi{color:inherit;} .md .pl-ent{color:#7ee787;}
:root[data-t="light"] .md .pl-k{color:#cf222e;} :root[data-t="light"] .md .pl-s,:root[data-t="light"] .md .pl-pds{color:#0a3069;}
:root[data-t="light"] .md .pl-c{color:#57606a;} :root[data-t="light"] .md .pl-en,:root[data-t="light"] .md .pl-e{color:#8250df;}
:root[data-t="light"] .md .pl-c1,:root[data-t="light"] .md .pl-v{color:#0550ae;} :root[data-t="light"] .md .pl-ent{color:#116329;}
.pk-body{display:grid; grid-template-columns:minmax(0,1fr) 340px; gap:48px; align-items:start; margin-top:8px;}
.pk-side{position:sticky; top:84px; display:flex; flex-direction:column; gap:14px;}
@media (max-width:980px){.pk-body{grid-template-columns:minmax(0,1fr); gap:28px;} .pk-side{position:static; order:-1;}}
.pk-media{border-radius:16px; overflow:hidden; border:1px solid var(--line); background:radial-gradient(120% 90% at 50% 0%,color-mix(in srgb,var(--brand) 8%,var(--bg2)),var(--bg2));}
.pk-media video{display:block; width:100%; max-height:420px; object-fit:contain; padding:14px 14px 0;}
.pk-media figcaption{font:500 11.5px var(--f-m); color:var(--mute); padding:10px 14px; border-top:1px solid var(--line);}
.inst{border-radius:16px; border:1px solid var(--line); background:var(--surf); padding:16px;}
.inst h2{font:700 13px var(--f-m); letter-spacing:.08em; text-transform:uppercase; color:var(--mute); margin:0 0 12px;}
.inst-tabs{display:flex; gap:4px; margin-bottom:10px; padding:3px; border-radius:10px; background:var(--bg2); border:1px solid var(--line);}
.inst-tabs button{flex:1; font:600 12.5px var(--f-b); padding:7px 8px; border:0; border-radius:8px; cursor:pointer; background:none; color:var(--mute);}
.inst-tabs button[aria-selected="true"]{background:var(--surf2); color:var(--ink); box-shadow:var(--sh-s);}
.inst .dep{margin:0;}
.inst .dep[hidden]{display:none;}
.inst-links{display:grid; gap:6px; margin-top:14px;}
.inst-links a{display:flex; align-items:center; justify-content:space-between; font-size:14px; font-weight:500; color:var(--ink); text-decoration:none;
  padding:9px 12px; border-radius:10px; border:1px solid var(--line); background:var(--bg2); transition:border-color .16s,color .16s;}
.inst-links a:hover{border-color:color-mix(in srgb,var(--brand) 55%,var(--line)); color:var(--brand);}
.inst-links a.demo{color:var(--brand); border-color:color-mix(in srgb,var(--brand) 35%,var(--line));}
.more-pk{margin-top:56px; padding-top:24px; border-top:1px solid var(--line);}
.more-pk h2{font-size:20px; margin:0 0 12px;}
.more-pk ul{list-style:none; padding:0; margin:0; display:flex; flex-wrap:wrap; gap:8px;}
.more-pk a{display:inline-block; font-size:14px; padding:7px 12px; border-radius:9px; border:1px solid var(--line); background:var(--surf); color:var(--ink); text-decoration:none;}
.more-pk a:hover{border-color:var(--brand); color:var(--brand);}
.pk-meta .tag#dl{font-family:var(--f-m); font-weight:500;}
"""

def gh(args, inp=None):
    return subprocess.run(['gh'] + args, input=inp, capture_output=True, text=True, check=True).stdout

def render(name, md):
    md = re.sub(r'\A\s*#\s[^\n]*\n', '', md)   # the page's own <h1> carries the name
    md = re.sub(r'^## Links\n[\s\S]*?(?=^## |\Z)', '', md, flags=re.M)   # README's links point back to this very site
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
    has_media = os.path.exists(os.path.join(ROOT, 'media', 'pkg', name + '.mp4'))
    media = ('<figure class="pk-media" style="margin:0"><video muted loop playsinline preload="metadata" poster="/media/pkg/%s.webp" data-src="/media/pkg/%s.mp4"></video>'
             '<figcaption>Demo recording from the README</figcaption></figure>' % (name, name)) if has_media else ''
    side_demo = '<a class="demo" href="/demos/%s/">&#9658; Run the live demo <span>&#8594;</span></a>' % name if live == '1' else ''
    if has_media:   # the side panel already plays this recording: drop the README's copy of the GIF
        body = re.sub(r'<p>\s*(?:<a[^>]*>)?\s*<img[^>]*/demo\.gif"[^>]*>\s*(?:</a>)?\s*</p>\s*', '', body, count=1)
    others = ''.join('<li><a href="/packages/%s/">%s</a></li>' % (n, n) for n in names if n != name)
    page = f"""<!DOCTYPE html>
<html lang="en" data-t="">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(meta_desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#07090d">
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
    <div class="pk-meta"><span class="tag">v{e(ver)}</span><span class="tag ok" id="pts">160/160 pub points</span><span class="tag" id="dl" hidden></span><span class="tag">MIT</span>{''.join('<span class="tag">%s</span>' % p for p in platforms)}</div>
    <div class="pk-actions"><a class="btn pri" href="https://pub.dev/packages/{name}">View on pub.dev &#8594;</a>{demo}<a class="btn sec" href="https://github.com/{OWNER}/{name}">Source on GitHub</a></div>
  </header>
  <div class="pk-body">
  <article class="md">
{body}
  </article>
  <aside class="pk-side">
    {media}
    <section class="inst" aria-label="Install {name}">
      <h2>Install</h2>
      <div class="inst-tabs" role="tablist"><button role="tab" aria-selected="true" data-tab="yaml">pubspec.yaml</button><button role="tab" aria-selected="false" data-tab="cli">Terminal</button></div>
      <div class="dep" data-pane="yaml"><code>{name}: ^{e(ver)}</code><button class="cp" data-c="{name}: ^{e(ver)}" aria-label="Copy dependency for {name}">Copy</button></div>
      <div class="dep" data-pane="cli" hidden><code>flutter pub add {name}</code><button class="cp" data-c="flutter pub add {name}" aria-label="Copy install command for {name}">Copy</button></div>
      <div class="inst-links">{side_demo}<a href="https://pub.dev/packages/{name}">pub.dev <span>&#8599;</span></a><a href="https://github.com/{OWNER}/{name}">Source on GitHub <span>&#8599;</span></a><a href="https://pub.dev/documentation/{name}/latest/">API reference <span>&#8599;</span></a></div>
    </section>
  </aside>
  </div>
  <section class="more-pk"><h2>More Flutter packages</h2><ul>{others}</ul></section>
</main>
{footer}
{theme_js}
<script>/* Install tabs, and the demo video plays only while it is on screen. */
document.querySelectorAll('.inst-tabs').forEach(function(tabs){{tabs.addEventListener('click',function(e){{
  var b=e.target.closest('button'); if(!b) return; var box=tabs.parentNode;
  tabs.querySelectorAll('button').forEach(function(x){{x.setAttribute('aria-selected',String(x===b));}});
  box.querySelectorAll('[data-pane]').forEach(function(p){{p.hidden=p.dataset.pane!==b.dataset.tab;}});
}});}});
(function(){{var v=document.querySelector('.pk-media video'); if(!v) return;
  if(matchMedia('(prefers-reduced-motion:reduce)').matches||(navigator.connection&&navigator.connection.saveData)||!('IntersectionObserver' in window)) return;
  new IntersectionObserver(function(es){{ if(es[0].isIntersecting){{ if(!v.src) v.src=v.dataset.src; v.play().catch(function(){{}}); }} else v.pause(); }},{{threshold:.3}}).observe(v);
}})();</script>
<script>/* Live pub.dev numbers: 30-day downloads (refreshed by pub.dev about daily) and pub points. */
fetch('https://pub.dev/api/packages/{name}/score').then(function(r){{return r.ok?r.json():null;}}).then(function(s){{
  if(!s)return; var d=document.getElementById('dl'), p=document.getElementById('pts'), n=s.downloadCount30Days;
  if(s.maxPoints)p.textContent=s.grantedPoints+'/'+s.maxPoints+' pub points';
  d.textContent=n==null?'\u2193 new on pub.dev':'\u2193 '+n.toLocaleString()+' downloads / 30 days';
  d.title=n==null?'Downloads appear after the first daily count on pub.dev':'Downloads in the last 30 days, from pub.dev'; d.hidden=false;
}}).catch(function(){{}});</script>
<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "4321e47ebde948179272a962602c33a0"}}'></script><!-- End Cloudflare Web Analytics -->
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

# keep every generated page installable (manifest, icons, install banner, offline)
import subprocess as _sp, sys as _sys, os as _os
_sp.run([_sys.executable, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "pwa.py")])
