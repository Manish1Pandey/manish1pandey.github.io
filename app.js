/* flutterdev.in app mode — runs only when opened as the installed app. Adds the top app bar (back + title) on inner
 * pages and a bottom tab bar, edge-to-edge layout on notched phones, back/forward slide direction and a light tap feel. */
(function () {
  'use strict';
  if (!(matchMedia('(display-mode: standalone)').matches || navigator.standalone === true)) return;
  var de = document.documentElement, path = location.pathname.replace(/index\.html$/, '');
  de.classList.add('app'); if (path === '/learn/') de.classList.add('learn'); else if (path !== '/') de.classList.add('inner');
  // links to the course stay inside the app: they open the Learn screen instead of a separate browser sheet
  // Never leave the app in place (that shows the browser's "outside this app" bar):
  //  • links to the course open the Learn screen inside the app;
  //  • any other website (pub.dev, GitHub, LinkedIn…) opens in the phone's browser, like a native app would.
  addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]'); if (!a || e.defaultPrevented) return;
    var u; try { u = new URL(a.href, location.href); } catch (err) { return; }
    if (!/^https?:$/.test(u.protocol) || u.origin === location.origin) return;   // mailto:, tel:, and this site's own pages behave normally
    e.preventDefault();
    if (u.hostname === 'dartiscool.flutterdev.in') location.href = '/learn/?to=' + encodeURIComponent(u.pathname + u.search + u.hash);
    else window.open(u.href, '_blank', 'noopener');
  });
  var vp = document.querySelector('meta[name="viewport"]'); if (vp && !/viewport-fit/.test(vp.content)) vp.content += ',viewport-fit=cover';
  addEventListener('pagereveal', function (e) {
    var a = window.navigation && navigation.activation;
    if (e.viewTransition && a && a.navigationType === 'traverse' && a.from && a.entry && a.entry.index < a.from.index) e.viewTransition.types.add('back');
  });
  addEventListener('click', function (e) { if (e.target.closest('button, a, [role="button"]') && navigator.vibrate) navigator.vibrate(6); }, true);
  var I = {
    home: '<path d="M3 11.5 12 4l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',
    pkg: '<path d="M21 8 12 3 3 8v8l9 5 9-5zM3 8l9 5 9-5M12 13v8"/>',
    play: '<rect x="3" y="4" width="18" height="16" rx="3"/><path d="m10 9 5 3-5 3z"/>',
    art: '<path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5M9 13h7M9 17h5"/>',
    learn: '<path d="M2 9 12 4l10 5-10 5z"/><path d="M6 11v5c2 2 4 3 6 3s4-1 6-3v-5M22 9v6"/>',
    me: '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/>'
  };
  function icon(d) { return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + d + '</svg>'; }
  document.addEventListener('DOMContentLoaded', function () {
    var nav = document.querySelector('body > nav .nav-in');
    if (nav && path !== '/') {
      var h1 = document.querySelector('main h1, header h1, h1');
      var back = document.createElement('button'); back.type = 'button'; back.className = 'app-back'; back.setAttribute('aria-label', 'Back');
      back.innerHTML = icon('<path d="m15 5-7 7 7 7"/>');
      back.addEventListener('click', function () { if (history.length > 1) history.back(); else location.href = '/'; });
      var title = document.createElement('span'); title.className = 'app-title'; var SECTIONS = { '/demos/': 'Demos', '/articles/': 'Articles', '/about/': 'About' };   // section screens get a short title
      title.textContent = SECTIONS[path] || (h1 ? h1.innerText.replace(/\s+/g, ' ').trim() : document.title.split(/\s[—·|]\s/)[0]);
      nav.prepend(title); nav.prepend(back);
    }
    var tabs = [['/', 'Home', 'home'], ['/#packages', 'Packages', 'pkg'], ['/learn/', 'Learn', 'learn'], ['/demos/', 'Demos', 'play'], ['/about/', 'About', 'me']];
    var bar = document.createElement('div'); bar.className = 'app-tabs'; bar.setAttribute('role', 'navigation'); bar.setAttribute('aria-label', 'App');
    tabs.forEach(function (t) {
      var a = document.createElement('a'); a.href = t[0]; a.innerHTML = icon(I[t[2]]) + t[1];
      var on = t[0] === '/' ? path === '/' : t[0] !== '/#packages' && path.indexOf(t[0]) === 0;
      if (t[0] === '/#packages' && path.indexOf('/packages/') === 0) on = true;
      if (on) { a.className = 'on'; a.setAttribute('aria-current', 'page'); }
      bar.appendChild(a);
    });
    document.body.appendChild(bar);
  });
})();
