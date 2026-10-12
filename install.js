/* "Install this site as an app" banner — shared by flutterdev.in and DartIsCool.
 * Android / desktop Chrome & Edge: a one-tap Install button (the browser's own install dialog).
 * iPhone / iPad: browsers there cannot trigger an install, so the banner shows how: Share → Add to Home Screen.
 * Polite: appears only after the visitor has spent a little time on the site, never when already installed,
 * and stays hidden for 30 days after "Not now". Configure with data- attributes on the script tag:
 *   <script src="install.js" data-app="flutterdev.in" data-icon="/icon-192.png" defer></script>
 */
(function () {
  'use strict';
  var me = document.currentScript;
  var APP = (me && me.dataset.app) || document.title;
  var ICON = (me && me.dataset.icon) || '';
  var KEY = 'pwa_install_hidden_until';
  var standalone = matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
  if (standalone) return;
  try { if (Date.now() < +(localStorage.getItem(KEY) || 0)) return; } catch (e) { /* storage unavailable */ }

  var ua = navigator.userAgent;
  var isIOS = /iPhone|iPad|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  var deferred = window.__pwaPrompt || null, shown = false, ready = false;   // a signal caught before this file loaded

  addEventListener('beforeinstallprompt', function (e) { e.preventDefault(); deferred = e; if (ready) show(); });
  addEventListener('appinstalled', function () { hide(3650); });

  // engagement first: 25 s on the page, or a second page in this visit
  var visits = 0;
  try { visits = +(sessionStorage.getItem('pwa_pages') || 0) + 1; sessionStorage.setItem('pwa_pages', visits); } catch (e) {}
  setTimeout(function () { ready = true; show(); }, visits > 1 ? 4000 : 25000);

  function hide(days) {
    try { localStorage.setItem(KEY, String(Date.now() + days * 864e5)); } catch (e) {}
    var b = document.getElementById('pwa-install'); if (b) { b.classList.remove('on'); setTimeout(function () { b.remove(); }, 300); }
  }

  function show() {
    if (shown || (!deferred && !isIOS)) return;   // nothing to offer (e.g. Firefox desktop, or already installed)
    shown = true;
    var css = document.createElement('style');
    css.textContent = '#pwa-install{box-sizing:border-box;position:fixed;left:50%;bottom:16px;z-index:2147483000;width:min(460px,calc(100% - 24px));transform:translate(-50%,140%);transition:transform .35s cubic-bezier(.2,.8,.2,1);display:flex;gap:14px;align-items:center;padding:14px 16px;border-radius:18px;background:rgba(10,17,16,.96);color:#e8efec;border:1px solid rgba(255,255,255,.12);box-shadow:0 18px 50px rgba(0,0,0,.45);font:14px/1.4 -apple-system,"Segoe UI",Roboto,sans-serif;backdrop-filter:blur(10px)}'
      + '#pwa-install.on{transform:translate(-50%,0)}#pwa-install img{width:48px;height:48px;border-radius:12px;flex:none}'
      + '#pwa-install b{display:block;font-size:15px}#pwa-install small{color:#a9bcb7}#pwa-install .acts{display:flex;gap:8px;margin-left:auto;flex:none}'
      + '#pwa-install button{font:600 13px/1 inherit;border-radius:999px;padding:10px 14px;cursor:pointer;border:1px solid rgba(255,255,255,.18);background:transparent;color:#e8efec}'
      + '#pwa-install button.go{background:linear-gradient(180deg,#ffb877,#e3741a);color:#1b0f04;border:0}'
      + '#pwa-install .share{display:inline-block;width:14px;height:14px;vertical-align:-2px;margin:0 2px}'
      + '@media (prefers-reduced-motion:reduce){#pwa-install{transition:none}}';
    document.head.appendChild(css);
    var box = document.createElement('div');
    box.id = 'pwa-install'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-label', 'Install ' + APP);
    var shareIcon = '<svg class="share" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12M8 7l4-4 4 4M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/></svg>';
    var text = deferred
      ? '<b>Install ' + APP + '</b><small>Opens like an app, from your home screen. Works offline.</small>'
      : '<b>Add ' + APP + ' to your Home Screen</b><small>Tap Share ' + shareIcon + ' then <b style="display:inline;font-size:inherit">Add to Home Screen</b>.</small>';
    box.innerHTML = (ICON ? '<img src="' + ICON + '" alt="">' : '') + '<div>' + text + '</div><div class="acts">'
      + (deferred ? '<button class="go" type="button">Install</button>' : '') + '<button class="no" type="button">' + (deferred ? 'Not now' : 'Got it') + '</button></div>';
    document.body.appendChild(box);
    requestAnimationFrame(function () { requestAnimationFrame(function () { box.classList.add('on'); }); });
    box.querySelector('.no').addEventListener('click', function () { hide(30); });
    var go = box.querySelector('.go');
    if (go) go.addEventListener('click', function () {
      deferred.prompt();
      deferred.userChoice.then(function (r) { hide(r.outcome === 'accepted' ? 3650 : 30); deferred = null; });
    });
  }
})();
