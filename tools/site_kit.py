#!/usr/bin/env python3
"""Shared head/body pieces for every flutterdev.in page. Idempotent, like tools/pwa.py — run after any build_*.py:
  python3 tools/site_kit.py
Head: preload the two self-hosted fonts used above the fold, and apply the saved theme before first paint
(dark is the default; light is opt-in from the toggle). Body: the ⌘K quick search (/cmdk.js, index in /search.json).
Skips the Flutter demo host pages under /demos/<pkg>/ and the app-only /learn/ screen.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAD = ('<!-- kit --><link rel="preload" href="/fonts/manrope.woff2" as="font" type="font/woff2" crossorigin>'
        '<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>'
        "<script>(function(){var r=document.documentElement;r.classList.add('js');"
        "try{var s=localStorage.getItem('t');if(s)r.setAttribute('data-t',s);}catch(e){}})();</script><!-- /kit -->")
BODY = '<!-- kit --><script src="/cmdk.js" defer></script><!-- /kit -->'
OLD_EARLY = re.compile(r"<script>\(function\(\)\{var r=document\.documentElement;r\.classList\.add\('js'\);try\{var s=localStorage\.getItem\('t'\);if\(s\)r\.setAttribute\('data-t',s\);\}catch\(e\)\{\}\}\)\(\);</script>\n?")

n = 0
for dp, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('fonts', 'media', 'icons', 'tools', 'articles-src')]
    for f in files:
        if not f.endswith('.html'):
            continue
        p = os.path.join(dp, f); rel = os.path.relpath(p, ROOT)
        if rel.startswith('demos' + os.sep) and rel != os.path.join('demos', 'index.html'):
            continue   # Flutter demo host pages run their own app
        if rel.startswith('learn' + os.sep):
            continue
        h = open(p, encoding='utf8').read()
        h = re.sub(r'<!-- kit -->.*?<!-- /kit -->\n?', '', h, flags=re.S)
        h = OLD_EARLY.sub('', h)
        h = h.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + HEAD, 1)
        h = h.replace('</body>', BODY + '\n</body>', 1)
        open(p, 'w', encoding='utf8').write(h)
        n += 1
print('site kit applied to %d pages' % n)
