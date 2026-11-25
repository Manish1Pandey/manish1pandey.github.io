#!/usr/bin/env python3
"""Render the social share image (og.png, 1200x630) and the app icons (icons/*.png) in the site's look:
navy surface, teal-to-violet Flutter beams, self-hosted fonts. Numbers come from the home page, so re-run after
adding a package or demo:  python3 tools/brand_assets.py   (needs Playwright + Chrome)
"""
import os
import re
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
home = open(os.path.join(ROOT, 'index.html'), encoding='utf8').read()
n_pk = len(re.findall(r'<article class="card" data-n=', home))
n_live = len(re.findall(r'<article class="card" data-n="[^"]+"[^>]*data-live="1"', home))
total = re.search(r'<b id="dl-total"[^>]*>([^<]*)</b>', home).group(1)
import base64
FONTS = ''.join("@font-face{font-family:'%s';font-weight:%s;src:url(data:font/woff2;base64,%s) format('woff2');}"
                % (f, w, base64.b64encode(open(os.path.join(ROOT, 'fonts', n + '.woff2'), 'rb').read()).decode())
                for f, w, n in (('Manrope', '500 800', 'manrope'), ('Inter', '400 600', 'inter'), ('JetBrains Mono', '400 600', 'jetbrains-mono')))
BEAMS = ('<svg viewBox="58 16 226 266" xmlns="http://www.w3.org/2000/svg"><defs>'
         '<linearGradient id="a" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2fe3c8"/><stop offset="1" stop-color="#7c66ff"/></linearGradient>'
         '<linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7c66ff"/><stop offset="1" stop-color="#2fe3c8"/></linearGradient></defs>'
         '<path d="M196 24 66 154l40 40L276 24z" fill="url(#a)"/><path d="M196 140 130 206l40 40 66-66z" fill="url(#b)" opacity=".85"/>'
         '<path d="M106 194 66 234l40 40h84l-44-44z" fill="url(#a)" opacity=".62"/></svg>')

OG = f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
*{{box-sizing:border-box;margin:0}} body{{width:1200px;height:630px;overflow:hidden;background:#07090d;color:#e9eef6;font-family:Inter;position:relative}}
.bg{{position:absolute;inset:0;background:radial-gradient(42% 60% at 14% 18%,rgba(47,227,200,.20),transparent 70%),radial-gradient(40% 60% at 88% 30%,rgba(124,102,255,.24),transparent 72%)}}
.dots{{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.06) 1px,transparent 1.3px);background-size:24px 24px;
  -webkit-mask-image:radial-gradient(ellipse 80% 80% at 40% 40%,#000 30%,transparent 80%)}}
.l{{position:absolute;left:72px;top:64px;width:640px}}
.brand{{display:flex;align-items:center;gap:14px;font:800 26px Manrope;letter-spacing:-.03em}} .brand svg{{width:40px;height:40px}} .brand i{{font-style:normal;color:#8d99ab;font-weight:600}}
h1{{margin-top:44px;font:800 68px/1.02 Manrope;letter-spacing:-.045em}}
h1 span{{background:linear-gradient(100deg,#2fe3c8,#56a6e3 45%,#7c66ff);-webkit-background-clip:text;color:transparent}}
p{{margin-top:22px;font-size:23px;line-height:1.45;color:#a3aec0}}
.st{{position:absolute;left:72px;bottom:60px;display:flex;gap:46px}}
.st b{{display:block;font:800 40px Manrope;letter-spacing:-.04em;background:linear-gradient(100deg,#2fe3c8,#7c66ff);-webkit-background-clip:text;color:transparent}}
.st span{{font-size:16px;color:#8d99ab}}
.t{{position:absolute;right:64px;top:132px;width:400px;border-radius:16px;overflow:hidden;background:linear-gradient(180deg,#0c1118,#080b10);
  border:1px solid rgba(255,255,255,.10);box-shadow:0 40px 80px -30px rgba(0,0,0,.8),0 0 80px -20px rgba(124,102,255,.35);font:15px/1.8 'JetBrains Mono';color:#c9d4e3}}
.bar{{display:flex;gap:8px;padding:13px 16px;border-bottom:1px solid rgba(255,255,255,.06)}} .bar i{{width:12px;height:12px;border-radius:50%}}
.body{{padding:18px 20px}} .g{{color:#2fe3c8}} .d{{color:#6f7b8e}} .a{{color:#7ee7a8}} .v{{color:#b3a4ff}} .k{{color:#7fb8ff}}
</style></head><body><div class="bg"></div><div class="dots"></div>
<div class="l"><div class="brand">{BEAMS}<span>flutterdev<i>.in</i></span></div>
<h1>Flutter packages,<br><span>built for production.</span></h1>
<p>{n_pk} open-source packages. {n_live} run live in your browser.</p></div>
<div class="st"><div><b>{n_pk}</b><span>packages</span></div><div><b>{n_live}</b><span>live demos</span></div><div><b>160/160</b><span>pub points, each</span></div><div><b>{total}</b><span>downloads</span></div></div>
<div class="t"><div class="bar"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i></div>
<div class="body"><div><span class="g">&#10140;</span> flutter pub add morphos_ui</div><div class="d">Resolving dependencies&hellip;</div>
<div class="a">+ morphos_ui</div><div><span class="a">&#10003;</span> 160/160 pub points</div><div style="height:12px"></div>
<div><span class="k">dependencies</span>:</div><div>&nbsp;&nbsp;<span class="v">morphos_ui</span>: ^0.1.2</div></div></div>
</body></html>"""

def icon_html(size, pad):
    return (f"<!doctype html><html><body style='margin:0;width:{size}px;height:{size}px;background:"
            f"radial-gradient(70% 70% at 30% 20%,#16202e,#07090d);display:grid;place-items:center;overflow:hidden'>"
            f"<div style='width:{size - 2 * pad}px;height:{size - 2 * pad}px;filter:drop-shadow(0 {size // 40}px {size // 16}px rgba(124,102,255,.45))'>"
            + BEAMS.replace('<svg ', "<svg style='width:100%;height:100%' ") + "</div></body></html>")

with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome')
    pg = b.new_page(viewport={'width': 1200, 'height': 630})
    pg.set_content(OG, wait_until='load'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
    pg.screenshot(path=os.path.join(ROOT, 'og.png'))
    # maskable icons keep the mark inside the central safe zone (~60%)
    for name, size in (('icon-192.png', 192), ('icon-512.png', 512), ('apple-touch-icon.png', 180)):
        pg = b.new_page(viewport={'width': size, 'height': size})
        pg.set_content(icon_html(size, int(size * .24)), wait_until='load')
        pg.screenshot(path=os.path.join(ROOT, 'icons', name))
    b.close()
print('og.png (%d packages, %d demos, %s downloads) and 3 icons written' % (n_pk, n_live, total))
