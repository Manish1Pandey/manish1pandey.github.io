#!/usr/bin/env python3
"""Refresh the "downloads in total" number on the home page (index.html).

pub.dev's API only gives a 30-day count. Each package's pub.dev score page carries about a
year of weekly download counts, which covers every package here since its first release;
this adds them up and writes the total into index.html. Run it whenever you like, then commit:
  python3 tools/update_downloads.py && git commit -am "Downloads: refresh total" && git push
The number only grows, so the page shows it as a minimum (e.g. "6.2k+").
"""
import base64, datetime, json, math, os, re, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
page = os.path.join(ROOT, 'index.html')
html = open(page, encoding='utf8').read()
names = sorted(set(re.findall(r'class="card[^"]*" data-n="([^"]+)"', html)))
total, newest = 0, ''
for n in names:
    req = urllib.request.Request('https://pub.dev/packages/%s/score' % n, headers={'User-Agent': 'flutterdev.in downloads refresh'})
    s = urllib.request.urlopen(req, timeout=30).read().decode()
    j = json.loads(base64.b64decode(re.search(r'data-downloads-chart-points="([^"]+)"', s).group(1)))
    t = sum(j['totalWeeklyDownloads']); total += t; newest = max(newest, j.get('newestDate', ''))
    print('%-30s %6d' % (n, t))

def short(n):  # rounded DOWN, so "6.2k+" is always true
    if n >= 1e6: return ('%.1f' % (math.floor(n / 1e5) / 10)).rstrip('0').rstrip('.') + 'M+'
    if n >= 1e3: return ('%.1f' % (math.floor(n / 100) / 10)).rstrip('0').rstrip('.') + 'k+'
    return str(n)

week = datetime.date.fromisoformat(newest[:10]).strftime('%-d %b %Y') if newest else ''
title = '%s downloads since the first release of each package, from pub.dev (counted to the week of %s)' % (format(total, ','), week)
stat = '<div><b id="dl-total" data-total="%d" title="%s">%s</b><span>downloads in total</span></div>' % (total, title, short(total))
new, k = re.subn(r'<div><b id="dl-total"[^>]*>[^<]*</b><span>[^<]*</span></div>', stat, html, count=1)
assert k == 1, 'stat not found in index.html'
open(page, 'w', encoding='utf8').write(new)
print('TOTAL', total, '->', short(total), '| week of', week)
