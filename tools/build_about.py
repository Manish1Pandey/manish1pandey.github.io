#!/usr/bin/env python3
"""Build /about/ — Manish's portfolio — with the home page's own styles, nav and footer.
The package list comes from the home page's cards, so it stays in step with the site.
Live numbers (pub.dev downloads, points) load in the browser on each visit.
Re-run after editing the text below or adding a package to the home page:
  python3 tools/build_about.py
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
home = open(os.path.join(ROOT, 'index.html'), encoding='utf8').read()
style = re.search(r'<style>(.*?)</style>', home, re.S).group(1)
favicon = re.search(r'<link rel="icon" href="[^"]*">', home).group(0)
nav = re.search(r'<nav>.*?</nav>', home, re.S).group(0).replace('href="#packages"', 'href="/#packages"')
footer = re.search(r'<footer class="wrap">.*?</footer>', home, re.S).group(0)
theme_js = re.search(r"<script>\(function\(\)\{var r=document\.documentElement.*?</script>",
                     open(os.path.join(ROOT, 'packages/mobius_carousel/index.html'), encoding='utf8').read(), re.S).group(0)
e = lambda s: html.escape(s, quote=True)

URL = 'https://flutterdev.in/about/'
DESC = ('Manish Kumar Panday, Flutter developer in Bangalore. Software Engineer at Innopay, building payment apps '
        'with 6M+ downloads, author of 14 open-source Flutter packages and Algoistan.')
LINKEDIN = 'https://www.linkedin.com/in/manish-flutter'
GITHUB = 'https://github.com/Manish1Pandey'
# Contact details are stored reversed and assembled on click, so simple scrapers miss them.
EMAIL_REV = 'manish.pandey141097@gmail.com'[::-1]
PHONE_REV = '+918317028326'[::-1]

person = {'@context': 'https://schema.org', '@type': 'Person', 'name': 'Manish Kumar Panday', 'url': URL,
          'jobTitle': 'Software Engineer (Flutter)', 'worksFor': {'@type': 'Organization', 'name': 'Innopay'},
          'address': {'@type': 'PostalAddress', 'addressLocality': 'Bangalore', 'addressCountry': 'IN'},
          'sameAs': [GITHUB, LINKEDIN, 'https://algoistan.flutterdev.in/'],
          'knowsAbout': ['Flutter', 'Dart', 'Mobile app development', 'Payments', 'CI/CD', 'Data structures and algorithms']}

# Packages straight from the home page cards: name, version, one-line blurb, live demo flag.
cards = re.findall(r'<article class="card" data-n="([a-z_0-9]+)"[^>]*data-live="(\d)"[\s\S]*?<span class="ver">([^<]*)</span>'
                   r'[\s\S]*?<p class="blurb">([^<]*)</p>', home)
FEATURED = 'morphos_ui'
pk_cards = ''.join(
    f'<a class="pk-card" href="/packages/{n}/" data-n="{n}"><span class="pk-name">{e(n)}</span>'
    f'<span class="pk-blurb">{e(b)}</span><span class="pk-foot"><span class="pk-ver">v{e(v)}</span>'
    f'{"<span class=pk-live>&#9658; demo</span>" if live == "1" else ""}<span class="pk-dl"></span></span></a>'
    for n, live, v, b in cards if n != FEATURED)
n_packages = len(cards)

CSS = """
.pf{padding:46px 0 80px;}
.pf section{margin-top:60px; padding:0;}
.pf h2{font-size:clamp(24px,3.4vw,30px); letter-spacing:-.025em; margin:0 0 8px;}
.pf .sec-sub{color:var(--mute); font-size:16px; margin:0 0 24px; max-width:720px; line-height:1.6;}
.pf p,.pf li{font-size:16.5px; line-height:1.7; color:var(--ink);}
.pf a{color:var(--brand);}

/* hero */
.pf-hero{display:grid; grid-template-columns:auto 1fr; gap:34px; align-items:center;}
.avatar{width:168px; height:168px; border-radius:50%; flex:none; filter:drop-shadow(0 18px 40px rgba(4,104,215,.35));}
.avatar svg{width:100%; height:100%; display:block;}
.core-a{transform-origin:100px 100px; animation:spin 22s linear infinite;}
.core-b{transform-origin:100px 100px; animation:spin 34s linear infinite reverse;}
.core-glow{transform-origin:100px 100px; animation:pulse 3.6s ease-in-out infinite;}
@keyframes spin{to{transform:rotate(360deg);}}
@keyframes pulse{0%,100%{opacity:.75; transform:scale(.96);} 50%{opacity:1; transform:scale(1.04);}}
@media (prefers-reduced-motion:reduce){.core-a,.core-b,.core-glow{animation:none;}}
.pf-hero h1{font-size:clamp(34px,5.4vw,54px); letter-spacing:-.035em; line-height:1.05; margin:0 0 10px;}
.role{font-size:18px; color:var(--mute); margin:0 0 18px;}
.role b{color:var(--ink); font-weight:650;}
.pf-hero .lede{font-size:18.5px; line-height:1.6; margin:0 0 24px; max-width:640px;}
.contact-row{display:flex; flex-wrap:wrap; gap:10px;}
.btn svg{width:17px; height:17px; flex:none;}
button.btn{font-family:inherit; cursor:pointer; border:0;}
button.btn.sec{border:1px solid var(--line);}
@media (max-width:700px){.pf-hero{grid-template-columns:1fr; gap:22px;} .avatar{width:128px; height:128px;}}

/* numbers */
.nums{display:grid; grid-template-columns:repeat(auto-fit,minmax(min(190px,42%),1fr)); gap:14px; margin-top:40px;}
.num{border:1px solid var(--line); background:var(--surf); border-radius:16px; padding:18px 20px; box-shadow:var(--sh-s);}
.num b{display:block; font-size:30px; letter-spacing:-.03em; line-height:1.15;}
.num span{font-size:13.5px; color:var(--mute); line-height:1.45; display:block; margin-top:4px;}
.num.lv b{color:var(--brand);}

/* experience */
.job{border:1px solid var(--line); background:var(--surf); border-radius:18px; padding:26px 28px; box-shadow:var(--sh-s);}
.job-head{display:flex; flex-wrap:wrap; justify-content:space-between; gap:6px 18px; align-items:baseline;}
.job-head h3{font-size:21px; margin:0; letter-spacing:-.02em;}
.job-head .where{color:var(--mute); font-size:15px;}
.apps{display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:12px; margin:18px 0 6px;}
.app{display:block; text-decoration:none; border:1px solid var(--line); border-radius:14px; padding:14px 16px; background:var(--bg);
  transition:border-color .18s, transform .18s;}
.app:hover{border-color:var(--brand); transform:translateY(-2px);}
.app b{display:block; color:var(--ink); font-size:15.5px;}
.app span{color:var(--mute); font-size:13.5px;}
.job ul{margin:16px 0 0; padding-left:20px;}
.job li{margin:6px 0;}

/* featured package */
.feat{display:grid; grid-template-columns:1.2fr 1fr; gap:26px; border:1px solid var(--line); border-radius:20px; padding:28px;
  background:linear-gradient(160deg,color-mix(in srgb,var(--brand) 8%,var(--surf)),var(--surf)); box-shadow:var(--sh-m);}
.feat .tag{display:inline-block; font-size:12.5px; font-weight:700; letter-spacing:.04em; text-transform:uppercase; color:var(--brand); margin-bottom:8px;}
.feat h3{font-family:ui-monospace,Menlo,monospace; font-size:26px; margin:0 0 10px; letter-spacing:-.02em;}
.feat p{margin:0 0 18px;}
.feat .acts{display:flex; flex-wrap:wrap; gap:10px;}
.bench{list-style:none; padding:0; margin:0; display:grid; gap:10px; align-content:start;}
.bench li{border:1px solid var(--line); background:var(--surf); border-radius:12px; padding:12px 14px; font-size:14.5px; line-height:1.5;}
.bench b{font-size:20px; letter-spacing:-.02em; color:var(--brand); display:block;}
@media (max-width:800px){.feat{grid-template-columns:1fr;}}

/* package grid */
.pk-grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:12px; margin-top:16px;}
.pk-card{display:flex; flex-direction:column; gap:6px; text-decoration:none; border:1px solid var(--line); background:var(--surf);
  border-radius:14px; padding:15px 16px; box-shadow:var(--sh-s); transition:border-color .18s, transform .18s;}
.pk-card:hover{border-color:var(--brand); transform:translateY(-2px);}
.pk-name{font-family:ui-monospace,Menlo,monospace; font-weight:700; color:var(--ink); font-size:14.5px; overflow-wrap:anywhere;}
.pk-blurb{color:var(--mute); font-size:13.8px; line-height:1.5; flex:1;}
.pk-foot{display:flex; gap:10px; align-items:center; font:11.5px ui-monospace,Menlo,monospace; color:var(--mute); margin-top:4px;}
.pk-live{color:var(--brand); font-family:inherit;}
.pk-dl{margin-left:auto;}

/* algoistan + skills */
.two{display:grid; grid-template-columns:1fr 1fr; gap:18px;}
@media (max-width:800px){.two{grid-template-columns:1fr;}}
.panel{border:1px solid var(--line); background:var(--surf); border-radius:18px; padding:24px 26px; box-shadow:var(--sh-s);}
.panel h3{margin:0 0 8px; font-size:20px; letter-spacing:-.02em;}
.now{background:linear-gradient(160deg,color-mix(in srgb,var(--brand2) 9%,var(--surf)),var(--surf));}
.now .tag{display:inline-block; font-size:12.5px; font-weight:700; letter-spacing:.04em; text-transform:uppercase; color:var(--brand); margin-bottom:6px;}
.now p{margin:0;}
.chips{display:flex; flex-wrap:wrap; gap:8px; margin-top:6px;}
.chip{font-size:13.5px; padding:6px 12px; border-radius:999px; border:1px solid var(--line); background:var(--bg); color:var(--ink);}

/* contact */
.reach{border:1px solid var(--line); border-radius:20px; padding:30px; box-shadow:var(--sh-m);
  background:linear-gradient(150deg,color-mix(in srgb,var(--brand2) 10%,var(--surf)),var(--surf));}
.reach .contact-row{margin-top:18px;}
.revealed{font-family:ui-monospace,Menlo,monospace;}
"""

EMBLEM = '''<svg viewBox="0 0 200 200" role="img" aria-label="Manish Kumar Panday monogram">
<defs>
<radialGradient id="em-bg" cx="50%" cy="42%" r="62%"><stop offset="0" stop-color="#0f2a4d"/><stop offset="1" stop-color="#050c18"/></radialGradient>
<radialGradient id="em-core" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#e6fbff"/><stop offset=".35" stop-color="#7fe0ff" stop-opacity=".9"/><stop offset="1" stop-color="#12b3f3" stop-opacity="0"/></radialGradient>
<linearGradient id="em-ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#12b3f3"/><stop offset="1" stop-color="#0468d7"/></linearGradient>
</defs>
<circle cx="100" cy="100" r="98" fill="url(#em-bg)"/>
<circle cx="100" cy="100" r="95" fill="none" stroke="url(#em-ring)" stroke-width="3"/>
<g class="core-a"><circle cx="100" cy="100" r="80" fill="none" stroke="#12b3f3" stroke-opacity=".85" stroke-width="7" stroke-dasharray="30 11.9"/></g>
<g class="core-b"><circle cx="100" cy="100" r="66" fill="none" stroke="#7fe0ff" stroke-opacity=".55" stroke-width="2" stroke-dasharray="2 6"/></g>
<circle class="core-glow" cx="100" cy="100" r="58" fill="url(#em-core)" opacity=".85"/>
<circle cx="100" cy="100" r="46" fill="#071426" fill-opacity=".72" stroke="#7fe0ff" stroke-opacity=".6" stroke-width="1.5"/>
<text x="100" y="112" text-anchor="middle" font-family="Inter,system-ui,-apple-system,sans-serif" font-size="34" font-weight="800" letter-spacing="1" fill="#ffffff">MKP</text>
</svg>'''

ICON = {
    'mail': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    'phone': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
    'in': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.4 20.5h-3.6v-5.6c0-1.3 0-3-1.8-3s-2.1 1.4-2.1 2.9v5.7H9.3V9h3.4v1.6h.1c.5-.9 1.6-1.8 3.4-1.8 3.6 0 4.3 2.4 4.3 5.5v6.2zM5.3 7.4a2.1 2.1 0 1 1 0-4.2 2.1 2.1 0 0 1 0 4.2zM7.1 20.5H3.6V9h3.5v11.5zM22.2 0H1.8C.8 0 0 .8 0 1.7v20.6c0 .9.8 1.7 1.8 1.7h20.4c1 0 1.8-.8 1.8-1.7V1.7C24 .8 23.2 0 22.2 0z"/></svg>',
    'gh': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 .3a12 12 0 0 0-3.8 23.4c.6.1.8-.3.8-.6v-2c-3.3.7-4-1.6-4-1.6-.6-1.4-1.4-1.8-1.4-1.8-1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.8 1.3 3.5 1 0-.8.4-1.3.7-1.6-2.7-.3-5.5-1.3-5.5-6 0-1.2.5-2.3 1.3-3.1-.2-.4-.6-1.6 0-3.2 0 0 1-.3 3.4 1.2a11.5 11.5 0 0 1 6 0C17.3 4.7 18.3 5 18.3 5c.7 1.6.2 2.9.1 3.2.8.8 1.3 1.9 1.3 3.1 0 4.6-2.8 5.6-5.5 5.9.5.4.9 1.1.9 2.3v3.3c0 .3.1.7.8.6A12 12 0 0 0 12 .3"/></svg>',
}


def contact_buttons(primary):
    first = 'pri' if primary else 'sec'
    return (f'<button class="btn {first}" data-rev="{e(EMAIL_REV)}" data-kind="mailto" aria-label="Show email address">{ICON["mail"]}<span>Email me</span></button>'
            f'<a class="btn sec" href="{LINKEDIN}">{ICON["in"]}<span>LinkedIn</span></a>'
            f'<a class="btn sec" href="{GITHUB}">{ICON["gh"]}<span>GitHub</span></a>'
            f'<button class="btn sec" data-rev="{e(PHONE_REV)}" data-kind="tel" aria-label="Show phone number">{ICON["phone"]}<span>Phone</span></button>')


page = f"""<!DOCTYPE html>
<html lang="en" data-t="">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Manish Kumar Panday · Flutter developer portfolio | flutterdev.in</title>
<meta name="description" content="{e(DESC)}">
<link rel="canonical" href="{URL}">
<meta name="theme-color" content="#f6f8fb" media="(prefers-color-scheme:light)">
<meta name="theme-color" content="#060c14" media="(prefers-color-scheme:dark)">
<meta property="og:type" content="profile">
<meta property="og:title" content="Manish Kumar Panday · Flutter developer">
<meta property="og:description" content="{e(DESC)}">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="https://flutterdev.in/og.png">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(person, separators=(',', ':'))}</script>
{favicon}
<style>{style}{CSS}</style>
</head>
<body>
{nav}
<main class="wrap pf">

  <header class="pf-hero">
    <div class="avatar">{EMBLEM}</div>
    <div>
      <h1>Manish Kumar Panday</h1>
      <p class="role"><b>Flutter developer</b> · Software Engineer at Innopay · Bangalore, India</p>
      <p class="lede">I build payment apps used by millions, and open-source Flutter packages for the gaps the framework leaves open, from iOS Control Center controls to a rendering engine that animates 100,000 items smoothly.</p>
      <div class="contact-row">{contact_buttons(True)}</div>
    </div>
  </header>

  <div class="nums">
    <div class="num"><b>6M+</b><span>Play Store downloads of the payment apps I build</span></div>
    <div class="num"><b>4.8&#9733;</b><span>Innopay app rating, from 10,960 reviews</span></div>
    <div class="num"><b>{n_packages}</b><span>open-source packages on pub.dev, every one 160/160</span></div>
    <div class="num lv"><b id="dl-total">&mdash;</b><span>package downloads in the last 30 days (live from pub.dev)</span></div>
  </div>

  <section id="experience">
    <h2>Experience</h2>
    <p class="sec-sub">Recharges, bill payments and rent payments, shipped in Flutter to Android and iOS.</p>
    <article class="job">
      <div class="job-head"><h3>Software Engineer, Flutter · Innopay</h3><span class="where">Bangalore</span></div>
      <div class="apps">
        <a class="app" href="https://play.google.com/store/apps/details?id=com.innopay.payment.user"><b>Innopay: Recharge &amp; Bills</b><span>5M+ downloads · 4.8&#9733; · Google Play</span></a>
        <a class="app" href="https://play.google.com/store/apps/details?id=com.innopay.innopay"><b>ePayRent</b><span>1M+ downloads · Google Play</span></a>
      </div>
      <ul>
        <li><b>Built the Jenkins CI/CD pipeline from scratch:</b> environment checks, UAT and production gates, build caching, iOS CocoaPods and version handling.</li>
        <li><b>Shipped payment and compliance flows:</b> Aadhaar-OTP KYC, the BBPS bill-payment checkout, a gift-card module, instant settlement, gold SIP and refund screens.</li>
        <li><b>Added product analytics</b> (Google and Meta) and deep linking across Android and iOS.</li>
      </ul>
    </article>
  </section>

  <section id="open-source">
    <h2>Open source</h2>
    <p class="sec-sub">Each package fills a gap I hit in a real app. All are documented, tested and score 160/160 on pub.dev.</p>
    <article class="feat">
      <div>
        <span class="tag">Newest · featured</span>
        <h3>morphos_ui</h3>
        <p>A rendering engine for Flutter: thousands of cards on one spring-animated surface. Grids morph into lists, cards glide into place, and it only draws what is on screen and only animates what is moving. Tested on iOS, Android, macOS, Windows, Linux and web.</p>
        <div class="acts">
          <a class="btn pri" href="/demos/morphos_ui/">&#9658; Live demo</a>
          <a class="btn sec" href="/packages/morphos_ui/">How it works</a>
        </div>
      </div>
      <ul class="bench">
        <li><b>Level</b>with a hand-written CustomPainter at 5,000 cards, with hit testing, accessibility and keyboard support built in</li>
        <li><b>~8&times; faster</b>than a hand-written painter when 100,000 cards morph at once</li>
        <li><b>~33&times; faster</b>when one card changes in a 100,000-card list</li>
      </ul>
    </article>
    <div class="pk-grid">{pk_cards}</div>
  </section>

  <section id="building">
    <h2>Currently building</h2>
    <p class="sec-sub">A personal project, in progress and not yet public.</p>
    <article class="panel now">
      <span class="tag">In progress · personal</span>
      <h3>GameLM</h3>
      <p>A behavioural-intelligence SDK for Flutter games: AI opponents that learn from how people play, and analytics that help developers understand their players. It ships with an admin dashboard for following players across several games.</p>
    </article>
  </section>

  <section id="algoistan">
    <div class="two">
      <div class="panel">
        <h3>Algoistan</h3>
        <p>A free course that teaches Dart from your first line of code to every classic algorithm: 85 animated lessons, including Flutter interview prep and a problem-solving level. Every code sample is tested.</p>
        <a class="btn sec" href="https://algoistan.flutterdev.in/">Open Algoistan &#8594;</a>
      </div>
      <div class="panel">
        <h3>What I work with</h3>
        <div class="chips">
          <span class="chip">Flutter</span><span class="chip">Dart</span><span class="chip">Custom RenderObjects</span>
          <span class="chip">Impeller &amp; CanvasKit</span><span class="chip">Platform channels: Kotlin, Swift</span>
          <span class="chip">Payments &amp; KYC flows</span><span class="chip">Jenkins CI/CD</span><span class="chip">GitHub Actions</span>
          <span class="chip">Google &amp; Meta analytics</span><span class="chip">Android &amp; iOS</span><span class="chip">Flutter web</span>
          <span class="chip">pub.dev publishing</span>
        </div>
      </div>
    </div>
  </section>

  <section id="contact">
    <div class="reach">
      <h2>Let's talk</h2>
      <p class="sec-sub" style="margin:0">Open to Flutter roles and collaborations. The quickest way to reach me is email or LinkedIn.</p>
      <div class="contact-row">{contact_buttons(False)}</div>
    </div>
  </section>
</main>
{footer}
{theme_js}
<script>
/* Contact: details are stored reversed and assembled only when clicked. */
document.querySelectorAll('[data-rev]').forEach(function(b){{
  b.addEventListener('click',function(){{
    var v=b.getAttribute('data-rev').split('').reverse().join(''), kind=b.getAttribute('data-kind');
    var a=document.createElement('a'); a.className=b.className; a.href=kind+':'+v;
    a.innerHTML=b.querySelector('svg').outerHTML+'<span class="revealed">'+(kind==='tel'?v.replace(/^\\+91/,'+91 '):v)+'</span>';
    b.replaceWith(a); a.focus();
  }});
}});
/* Live pub.dev numbers: 30-day downloads per package (refreshed by pub.dev about daily) and the total. */
(function(){{
  var names={json.dumps([c[0] for c in cards])}, total=0, left=names.length, tot=document.getElementById('dl-total');
  function fmt(n){{return n>=1e4?Math.round(n/1e3)+'k':n>=1e3?(n/1e3).toFixed(1).replace(/\\.0$/,'')+'k':String(n);}}
  names.forEach(function(n){{
    fetch('https://pub.dev/api/packages/'+n+'/score').then(function(r){{return r.ok?r.json():null;}}).then(function(s){{
      var dl=s&&s.downloadCount30Days, el=document.querySelector('.pk-card[data-n="'+n+'"] .pk-dl');
      if(dl!=null){{ total+=dl; if(el){{ el.textContent='\\u2193 '+fmt(dl); el.title=dl.toLocaleString()+' downloads in the last 30 days'; }} }}
      else if(el){{ el.textContent='\\u2193 new'; }}
    }}).catch(function(){{}}).then(function(){{ if(--left===0&&total>0) tot.textContent=fmt(total); }});
  }});
}})();
</script>
</body>
</html>
"""
os.makedirs(os.path.join(ROOT, 'about'), exist_ok=True)
open(os.path.join(ROOT, 'about', 'index.html'), 'w', encoding='utf8').write(page)
print('built about/ (%d packages)' % n_packages)
