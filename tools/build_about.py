#!/usr/bin/env python3
"""Build /about/ with the home page's own styles, nav and footer. Re-run after editing the text below.
  python3 tools/build_about.py
"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
home = open(os.path.join(ROOT, 'index.html'), encoding='utf8').read()
style = re.search(r'<style>(.*?)</style>', home, re.S).group(1)
favicon = re.search(r'<link rel="icon" href="[^"]*">', home).group(0)
nav = re.search(r'<nav>.*?</nav>', home, re.S).group(0).replace('href="#packages"', 'href="/#packages"')
footer = re.search(r'<footer class="wrap">.*?</footer>', home, re.S).group(0)
theme_js = re.search(r"<script>\(function\(\)\{var r=document\.documentElement.*?</script>", open(os.path.join(ROOT, 'packages/mobius_carousel/index.html'), encoding='utf8').read(), re.S).group(0)
URL = 'https://flutterdev.in/about/'
DESC = 'Manish Kumar Panday, a Flutter developer in Bangalore building fintech apps, open-source Flutter packages and Algoistan, a free course on DSA in Dart.'
person = {'@context': 'https://schema.org', '@type': 'Person', 'name': 'Manish Kumar Panday', 'url': URL, 'jobTitle': 'Flutter developer',
          'address': {'@type': 'PostalAddress', 'addressLocality': 'Bangalore', 'addressCountry': 'IN'},
          'sameAs': ['https://github.com/Manish1Pandey', 'https://www.linkedin.com/in/manish-flutter', 'https://algoistan.flutterdev.in/'],
          'knowsAbout': ['Flutter', 'Dart', 'Mobile app development', 'Fintech', 'Data structures and algorithms']}
CSS = """
.ab{padding:44px 0 70px; max-width:820px;}
.ab h1{font-size:clamp(32px,5vw,48px); letter-spacing:-.03em; margin:0 0 10px;}
.ab .lede{font-size:19px; color:var(--mute); line-height:1.6; margin:0 0 30px;}
.ab h2{font-size:22px; letter-spacing:-.02em; margin:38px 0 12px;}
.ab p,.ab li{font-size:16.5px; line-height:1.7; color:var(--ink);}
.ab ul{padding-left:20px;}
.ab a{color:var(--brand);}
.facts{display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; margin:8px 0 6px;}
.fact{border:1px solid var(--line); background:var(--surf); border-radius:14px; padding:16px 18px; box-shadow:var(--sh-s);}
.fact b{display:block; font-size:26px; letter-spacing:-.02em;}
.fact span{font-size:13.5px; color:var(--mute);}
.links{display:flex; flex-wrap:wrap; gap:10px; margin-top:14px;}
"""
page = f"""<!DOCTYPE html>
<html lang="en" data-t="">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>About · Manish Kumar Panday, Flutter developer | flutterdev.in</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{URL}">
<meta name="theme-color" content="#f6f8fb" media="(prefers-color-scheme:light)">
<meta name="theme-color" content="#060c14" media="(prefers-color-scheme:dark)">
<meta property="og:type" content="profile">
<meta property="og:title" content="About · Manish Kumar Panday">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="https://flutterdev.in/og.png">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(person, separators=(',', ':'))}</script>
{favicon}
<style>{style}{CSS}</style>
</head>
<body>
{nav}
<main class="wrap ab">
  <h1>Hi, I'm Manish.</h1>
  <p class="lede">I'm a Flutter developer in Bangalore. By day I build payment apps for a fintech company; the rest of the time I build open-source Flutter packages and Algoistan, a free course that teaches data structures and algorithms in Dart.</p>
  <div class="facts">
    <div class="fact"><b>6M+</b><span>combined downloads of the payment apps I work on</span></div>
    <div class="fact"><b>13</b><span>open-source Flutter and Dart packages on pub.dev</span></div>
    <div class="fact"><b>85</b><span>free animated lessons on Algoistan</span></div>
  </div>
  <h2>What I work on</h2>
  <ul>
    <li><b>Fintech apps in Flutter</b> — recharges, bill payments and rent payments for millions of users: payment flows, KYC, analytics and release pipelines.</li>
    <li><b>Open-source packages</b> — each one fills a gap I hit in a real app: notification images, watch tiles, OS proxy resolution, scroll transitions and more. <a href="/#packages">See all of them</a>.</li>
    <li><b>Algoistan</b> — Dart from your first line to every classic algorithm, plus Flutter interview prep and a problem-solving level. Every code sample is tested. <a href="https://algoistan.flutterdev.in/">Open Algoistan</a>.</li>
  </ul>
  <h2>How I like to build</h2>
  <p>Small, well-tested pieces that solve one real problem, documented so the next developer can use them in minutes — and, where it helps people learn, animated so you can see what the code is actually doing.</p>
  <h2>Find me</h2>
  <div class="links">
    <a class="btn pri" href="https://github.com/Manish1Pandey">GitHub</a>
    <a class="btn sec" href="https://www.linkedin.com/in/manish-flutter">LinkedIn</a>
    <a class="btn sec" href="/#packages">All my packages</a>
  </div>
</main>
{footer}
{theme_js}
</body>
</html>
"""
os.makedirs(os.path.join(ROOT, 'about'), exist_ok=True)
open(os.path.join(ROOT, 'about', 'index.html'), 'w', encoding='utf8').write(page)
print('built about/')
