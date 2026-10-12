#!/usr/bin/env python3
"""Make every page installable as the flutterdev.in app: manifest + icons + install banner + offline service worker.
Idempotent — run after any build_*.py:  python3 tools/pwa.py"""
import glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAD = ('<!-- pwa --><link rel="manifest" href="/manifest.webmanifest"><link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">'
        '<meta name="apple-mobile-web-app-title" content="flutterdev.in"><meta name="mobile-web-app-capable" content="yes">'
        '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="black">'
        '<link rel="stylesheet" href="/app.css"><script src="/app.js"></script><!-- /pwa -->')
BODY = ('<!-- pwa --><script src="/install.js" data-app="flutterdev.in" data-icon="/icons/icon-192.png" defer></script>'
        '<script>if(\'serviceWorker\' in navigator)addEventListener(\'load\',function(){navigator.serviceWorker.register(\'/sw.js\')});</script><!-- /pwa -->')
n = 0
for p in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True):
    if '/demos/' in p and not p.endswith('/demos/index.html'): continue   # Flutter demo host pages run their own app
    s = open(p, encoding='utf8').read()
    t = re.sub(r'<!-- pwa -->.*?<!-- /pwa -->', '', s)
    t = t.replace('</head>', HEAD + '\n</head>', 1).replace('</body>', BODY + '\n</body>', 1)
    if t != s: open(p, 'w', encoding='utf8').write(t); n += 1
print('pages made installable:', n)
