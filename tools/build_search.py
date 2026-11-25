#!/usr/bin/env python3
"""Write /search.json, the index behind the ⌘K quick search on every page.
Sources are the site's own pages, so it stays in step: home cards (packages), the demos page, articles-src front
matter, plus the fixed site sections and courses. Re-run after adding a package, demo or article:
  python3 tools/build_search.py
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
read = lambda *p: open(os.path.join(ROOT, *p), encoding='utf8').read()
items = []

home = read('index.html')
for name, live, blurb in re.findall(r'<article class="card" data-n="([a-z_0-9]+)"[^>]*data-live="(\d)"[\s\S]*?<p class="blurb">([^<]*)</p>', home):
    items.append({'k': 'Package', 't': name, 'd': html.unescape(blurb), 'u': '/packages/%s/' % name})

demos = read('demos', 'index.html')
for href, name, what in re.findall(r'<a class="dcard" href="([^"]+)"[\s\S]*?<h2>([^<]+)</h2>[\s\S]*?<p class="dwhat">([^<]*)</p>', demos):
    items.append({'k': 'Demo', 't': name + ' demo', 'd': html.unescape(what), 'u': href})

src = os.path.join(ROOT, 'articles-src')
for fn in sorted(os.listdir(src)):
    if not fn.endswith('.md'):
        continue
    front = re.match(r'---\n(.*?)\n---', read('articles-src', fn), re.S).group(1)
    meta = dict(re.findall(r'^(\w+):\s*(.*)$', front, re.M))
    items.append({'k': 'Article', 't': meta['title'], 'd': meta.get('description', ''), 'u': '/articles/%s/' % fn[:-3]})

items += [
    {'k': 'Page', 't': 'All packages', 'd': 'Search, filter and sort every package', 'u': '/#packages'},
    {'k': 'Page', 't': 'Live demos', 'd': 'Real Flutter web builds, running in your browser', 'u': '/demos/'},
    {'k': 'Page', 't': 'Articles', 'd': 'Notes on Flutter, proven with tests', 'u': '/articles/'},
    {'k': 'Page', 't': 'About Manish', 'd': 'Flutter developer, Bangalore', 'u': '/about/'},
    {'k': 'Course', 't': 'DartIsCool', 'd': 'Learn Dart, Flutter, data structures and algorithms, from zero', 'u': 'https://dartiscool.flutterdev.in/'},
    {'k': 'Course', 't': 'ZeroToModel', 'd': 'Learn AI engineering from zero, from Python to your own model', 'u': 'https://zerotomodel.flutterdev.in/'},
    {'k': 'Tool', 't': 'DartLog', 'd': 'Record every network request of your Flutter app', 'u': 'https://dartlog.flutterdev.in/'},
    {'k': 'Link', 't': 'GitHub', 'd': 'github.com/Manish1Pandey', 'u': 'https://github.com/Manish1Pandey'},
]
open(os.path.join(ROOT, 'search.json'), 'w', encoding='utf8').write(json.dumps(items, ensure_ascii=False, separators=(',', ':')))
print('search.json: %d entries' % len(items))
