/* flutterdev.in quick search: ⌘K / Ctrl+K (or the Search button in the nav) opens a palette over packages, demos,
 * articles, pages and courses from /search.json. Arrow keys move, Enter opens, Esc closes. No dependencies. */
(function () {
  'use strict';
  var data = null, dlg, input, list, items = [], sel = 0, lastFocus = null;
  var mac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);

  var css = ''
    + '.qk-btn{display:inline-flex;align-items:center;gap:8px;height:36px;padding:0 10px 0 11px;margin-left:6px;border-radius:10px;cursor:pointer;'
    + 'border:1px solid var(--line);background:var(--surf);color:var(--mute);font:500 13px var(--f-b,inherit);transition:color .18s,border-color .18s}'
    + '.qk-btn:hover{color:var(--ink);border-color:var(--line2,var(--line))}'
    + '.qk-btn svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:1.9}'
    + '.qk-btn kbd{font:500 11px var(--f-m,monospace);border:1px solid var(--line);border-radius:6px;padding:2px 6px;background:var(--surf2)}'
    + '@media (max-width:1180px){.qk-btn{padding:0;width:36px;justify-content:center}.qk-btn span,.qk-btn kbd{display:none}}'
    + '.qk{position:fixed;inset:0;z-index:100;display:none;align-items:flex-start;justify-content:center;padding:12vh 16px 16px;'
    + 'background:rgba(3,5,9,.62)}'
    + ':root[data-t="light"] .qk{background:rgba(11,16,32,.32)}'
    + '.qk.open{display:flex;animation:qk-in .16s cubic-bezier(.2,.9,.25,1)}'
    + '@keyframes qk-in{from{opacity:0}}'
    + '.qk-box{width:min(640px,100%);max-height:70vh;display:flex;flex-direction:column;border-radius:16px;overflow:hidden;'
    + 'background:var(--surf);border:1px solid var(--line2,var(--line));box-shadow:0 30px 80px -20px rgba(0,0,0,.6);'
    + 'animation:qk-up .18s cubic-bezier(.2,.9,.25,1)}'
    + '@keyframes qk-up{from{transform:translateY(8px) scale(.985);opacity:0}}'
    + '.qk-in{display:flex;align-items:center;gap:10px;padding:14px 16px;border-bottom:1px solid var(--line)}'
    + '.qk-in svg{width:18px;height:18px;flex:none;fill:none;stroke:var(--mute);stroke-width:1.9}'
    + '.qk-in input{flex:1;min-width:0;border:0;outline:0;background:none;color:var(--ink);font:16px var(--f-b,inherit)}'
    + '.qk-in input::placeholder{color:var(--faint,var(--mute))}'
    + '.qk-in kbd{font:500 11px var(--f-m,monospace);color:var(--mute);border:1px solid var(--line);border-radius:6px;padding:3px 7px}'
    + '.qk-list{overflow-y:auto;padding:8px;margin:0;list-style:none}'
    + '.qk-g{font:600 11px var(--f-m,monospace);letter-spacing:.1em;text-transform:uppercase;color:var(--faint,var(--mute));padding:10px 10px 6px}'
    + '.qk-it a{display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:10px;text-decoration:none;color:var(--ink)}'
    + '.qk-it.on a{background:color-mix(in srgb,var(--brand) 12%,transparent);box-shadow:inset 2px 0 0 var(--brand)}'
    + '.qk-ic{flex:none;width:30px;height:30px;border-radius:8px;display:grid;place-items:center;font:600 12px var(--f-m,monospace);'
    + 'background:var(--surf2);color:var(--brand);border:1px solid var(--line)}'
    + '.qk-tx{min-width:0;flex:1}'
    + '.qk-t{display:block;font:600 14.5px var(--f-b,inherit);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'
    + '.qk-t mark{background:none;color:var(--brand)}'
    + '.qk-d{display:block;font-size:12.5px;color:var(--mute);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'
    + '.qk-go{flex:none;color:var(--faint,var(--mute));font-size:13px;opacity:0}.qk-it.on .qk-go{opacity:1}'
    + '.qk-empty{padding:28px 16px;text-align:center;color:var(--mute);font-size:14px}'
    + '.qk-ft{display:flex;gap:16px;padding:10px 16px;border-top:1px solid var(--line);font-size:12px;color:var(--faint,var(--mute))}'
    + '.qk-ft kbd{font:500 11px var(--f-m,monospace);border:1px solid var(--line);border-radius:5px;padding:1px 5px;margin-right:4px}'
    + '@media (prefers-reduced-motion:reduce){.qk.open,.qk-box{animation:none}}';

  var ICON = { Package: 'pk', Demo: '▶', Article: 'Aa', Page: '#', Course: '◎', Tool: '⌁', Link: '↗' };
  var SEARCH_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>';

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* subsequence match with bonuses for word starts and contiguous runs; returns score and matched indexes */
  function match(q, s) {
    if (!q) return { s: 1, m: [] };
    var t = s.toLowerCase(), qi = 0, score = 0, run = 0, m = [], i;
    var exact = t.indexOf(q);
    if (exact !== -1) { for (i = 0; i < q.length; i++) m.push(exact + i); return { s: 100 - exact + (exact === 0 ? 50 : 0), m: m }; }
    for (i = 0; i < t.length && qi < q.length; i++) {
      if (t[i] === q[qi]) { run++; score += 1 + run * 2 + (i === 0 || /[\s_\-.]/.test(t[i - 1]) ? 6 : 0); m.push(i); qi++; }
      else run = 0;
    }
    return qi === q.length ? { s: score, m: m } : null;
  }
  function mark(s, m) {
    if (!m.length) return esc(s);
    var out = '', set = {}; m.forEach(function (i) { set[i] = 1; });
    for (var i = 0; i < s.length; i++) out += set[i] ? '<mark>' + esc(s[i]) + '</mark>' : esc(s[i]);
    return out;
  }

  var styled = false;
  function style() { if (styled) return; styled = true; var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st); }
  function build() {
    style();
    dlg = document.createElement('div'); dlg.className = 'qk'; dlg.setAttribute('role', 'dialog'); dlg.setAttribute('aria-modal', 'true'); dlg.setAttribute('aria-label', 'Search flutterdev.in');
    dlg.innerHTML = '<div class="qk-box"><label class="qk-in">' + SEARCH_SVG
      + '<input type="text" placeholder="Search packages, demos, articles…" aria-label="Search" aria-controls="qk-list" aria-autocomplete="list" autocomplete="off" spellcheck="false">'
      + '<kbd>Esc</kbd></label><ul class="qk-list" id="qk-list" role="listbox"></ul>'
      + '<div class="qk-ft"><span><kbd>↑</kbd><kbd>↓</kbd>move</span><span><kbd>↵</kbd>open</span><span><kbd>esc</kbd>close</span></div></div>';
    document.body.appendChild(dlg);
    input = dlg.querySelector('input'); list = dlg.querySelector('.qk-list');
    dlg.addEventListener('mousedown', function (e) { if (e.target === dlg) close(); });
    input.addEventListener('input', render);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
      else if (e.key === 'Enter') { e.preventDefault(); var a = list.querySelector('.qk-it.on a'); if (a) go(a, e.metaKey || e.ctrlKey); }
      else if (e.key === 'Escape') { e.preventDefault(); close(); }
      else if (e.key === 'Tab') { e.preventDefault(); move(e.shiftKey ? -1 : 1); }
    });
    list.addEventListener('mousemove', function (e) { var li = e.target.closest('.qk-it'); if (li) setSel(+li.dataset.i, false); });
  }

  function go(a, newTab) { close(); if (newTab) window.open(a.href, '_blank', 'noopener'); else location.href = a.href; }

  function render() {
    var q = input.value.trim().toLowerCase();
    var res = [];
    (data || []).forEach(function (it, idx) {
      var a = match(q, it.t), b = q ? match(q, it.d) : null;
      var s = a ? a.s * 2 : b ? b.s * .5 : -1;
      if (s >= 0) res.push({ it: it, s: s, m: a ? a.m : [], o: idx });
    });
    if (q) res.sort(function (x, y) { return y.s - x.s || x.o - y.o; });
    items = res.slice(0, 40);
    if (!data) { list.innerHTML = '<li class="qk-empty">Loading…</li>'; return; }
    if (!items.length) { list.innerHTML = '<li class="qk-empty">No results for “' + esc(input.value) + '”</li>'; return; }
    var html = '', group = null;
    items.forEach(function (r, i) {
      var g = q ? (i === 0 ? 'Best matches' : null) : r.it.k + 's';
      if (g && g !== group) { html += '<li class="qk-g" role="presentation">' + esc(g) + '</li>'; group = g; }
      var ext = /^https?:/.test(r.it.u);
      html += '<li class="qk-it" role="option" data-i="' + i + '" id="qk-o' + i + '"><a href="' + esc(r.it.u) + '"' + (ext ? ' rel="noopener"' : '') + '>'
        + '<span class="qk-ic" aria-hidden="true">' + (ICON[r.it.k] || '•') + '</span>'
        + '<span class="qk-tx"><span class="qk-t">' + mark(r.it.t, r.m) + '</span><span class="qk-d">' + esc(r.it.k) + ' · ' + esc(r.it.d) + '</span></span>'
        + '<span class="qk-go" aria-hidden="true">' + (ext ? '↗' : '↵') + '</span></a></li>';
    });
    list.innerHTML = html;
    setSel(0, true);
  }
  function setSel(i, scroll) {
    sel = Math.max(0, Math.min(items.length - 1, i));
    [].forEach.call(list.querySelectorAll('.qk-it'), function (li) { var on = +li.dataset.i === sel; li.classList.toggle('on', on); li.setAttribute('aria-selected', on); if (on && scroll) li.scrollIntoView({ block: 'nearest' }); });
    input.setAttribute('aria-activedescendant', 'qk-o' + sel);
  }
  function move(d) { if (items.length) setSel((sel + d + items.length) % items.length, true); }

  function load() {
    if (data) return;
    fetch('/search.json').then(function (r) { return r.json(); }).then(function (d) { data = d; if (dlg.classList.contains('open')) render(); })
      .catch(function () { data = []; if (dlg.classList.contains('open')) list.innerHTML = '<li class="qk-empty">Search is unavailable offline.</li>'; });
  }
  function open() {
    if (!dlg) build();
    load(); lastFocus = document.activeElement;
    dlg.classList.add('open'); document.documentElement.style.overflow = 'hidden';
    input.value = ''; render(); input.focus();
  }
  function close() {
    if (!dlg) return;
    dlg.classList.remove('open'); document.documentElement.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  document.addEventListener('keydown', function (e) {
    if ((e.metaKey || e.ctrlKey) && (e.key === 'k' || e.key === 'K')) { e.preventDefault(); dlg && dlg.classList.contains('open') ? close() : open(); }
  });

  /* nav button, placed before the theme toggle on every page */
  function addButton() {
    var tt = document.getElementById('tt'); if (!tt || document.querySelector('.qk-btn')) return;
    style();
    var b = document.createElement('button'); b.type = 'button'; b.className = 'qk-btn'; b.setAttribute('aria-label', 'Search the site');
    b.innerHTML = SEARCH_SVG + '<span>Search</span><kbd>' + (mac ? '⌘' : 'Ctrl ') + 'K</kbd>';
    b.addEventListener('click', open); b.addEventListener('pointerenter', function () { if (!dlg) build(); load(); }, { once: true });
    tt.parentNode.insertBefore(b, tt);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', addButton); else addButton();
})();
