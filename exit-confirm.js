/* "Exit <app>?" on Back from the home screen of the installed app — shared by flutterdev.in and DartIsCool.
 * Only when Back would really leave the app (home is the first screen of this session). Chrome ignores history entries
 * added before the user has touched the page, so the guard is armed on the first tap. Stay re-arms it; Exit closes the app.
 *   <script src="exit-confirm.js" data-app="flutterdev.in"></script>   (include on the home page only)
 */
(function () {
  'use strict';
  var me = document.currentScript, APP = (me && me.dataset.app) || document.title;
  if (!(matchMedia('(display-mode: standalone)').matches || navigator.standalone === true) || window.top !== window) return;
  var first = window.navigation && navigation.currentEntry ? navigation.currentEntry.index === 0 : history.length <= 1;
  if (!first) return;   // home was reached from another screen: Back goes there, as normal
  var armed = false;
  function arm() { if (armed) return; armed = true; history.pushState({ exitGuard: 1 }, ''); }
  addEventListener('pointerdown', arm, { once: true, capture: true });
  addEventListener('keydown', arm, { once: true, capture: true });
  addEventListener('popstate', function () {
    if (!armed) return;
    // only when Back reached the very first screen (not e.g. from a #section of the same page back to the guard step)
    var atStart = window.navigation && navigation.currentEntry ? navigation.currentEntry.index === 0 : !(history.state && history.state.exitGuard);
    if (!atStart) return;
    armed = false; ask();
  });

  function ask() {
    if (document.getElementById('exit-sheet')) return;
    var css = document.createElement('style');
    css.textContent = '#exit-sheet{position:fixed;inset:0;z-index:2147483646;display:flex;align-items:flex-end;justify-content:center;background:rgba(0,0,0,.45);opacity:0;transition:opacity .2s}'
      + '#exit-sheet.on{opacity:1}#exit-sheet .card{width:min(460px,100%);box-sizing:border-box;margin:0 10px calc(10px + env(safe-area-inset-bottom));padding:22px 20px 16px;border-radius:22px;background:#111a1e;color:#e8efec;border:1px solid rgba(255,255,255,.1);box-shadow:0 20px 60px rgba(0,0,0,.5);font:15px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;transform:translateY(30px);transition:transform .25s cubic-bezier(.2,.8,.2,1)}'
      + '#exit-sheet.on .card{transform:none}#exit-sheet b{display:block;font-size:18px;margin-bottom:4px}#exit-sheet p{margin:0 0 16px;color:#a9bcb7}'
      + '#exit-sheet .row{display:grid;grid-template-columns:1fr 1fr;gap:10px}#exit-sheet button{font:600 15px/1 inherit;font-family:inherit;padding:14px;border-radius:14px;border:1px solid rgba(255,255,255,.14);background:transparent;color:#e8efec;cursor:pointer}'
      + '#exit-sheet button.stay{background:linear-gradient(180deg,#ffb877,#e3741a);color:#1b0f04;border:0}';
    document.head.appendChild(css);
    var box = document.createElement('div');
    box.id = 'exit-sheet'; box.setAttribute('role', 'alertdialog'); box.setAttribute('aria-label', 'Exit ' + APP + '?');
    box.innerHTML = '<div class="card"><b>Exit ' + APP + '?</b><p>You can come back any time from your home screen.</p>'
      + '<div class="row"><button type="button" class="exit">Exit</button><button type="button" class="stay">Stay</button></div></div>';
    document.body.appendChild(box);
    requestAnimationFrame(function () { box.classList.add('on'); });
    if (navigator.vibrate) navigator.vibrate(8);
    function close() { box.classList.remove('on'); setTimeout(function () { box.remove(); css.remove(); }, 220); }
    box.querySelector('.stay').addEventListener('click', function () { close(); arm(); });
    box.addEventListener('click', function (e) { if (e.target === box) { close(); arm(); } });
    box.querySelector('.exit').addEventListener('click', function () {
      close();
      window.close();                                   // an installed app with a single page in its history may close itself
      setTimeout(function () { history.back(); }, 250); // otherwise hand Back to the system, which leaves the app
    });
  }
})();
