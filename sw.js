// flutterdev.in offline support: pages are network-first (always fresh online, last copy offline);
// small files are served from cache and refreshed in the background. The Flutter demos (large) are never cached.
const CACHE = 'flutterdev-v3';
const CORE = ['/', '/learn/', '/demos/', '/articles/', '/about/', '/manifest.webmanifest', '/icons/icon-192.png', '/install.js', '/app.css', '/app.js'];
self.addEventListener('install', (e) => { e.waitUntil(caches.open(CACHE).then((c) => Promise.all(CORE.map((u) => c.add(u).catch(() => null))))); self.skipWaiting(); });
self.addEventListener('activate', (e) => e.waitUntil((async () => {
  for (const k of await caches.keys()) if (k !== CACHE) await caches.delete(k);
  await self.clients.claim();
})()));
self.addEventListener('fetch', (e) => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin) return;
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then((res) => { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); return res; })
      .catch(() => caches.match(req).then((hit) => hit || caches.match('/'))));
    return;
  }
  if (url.pathname.startsWith('/demos/')) return;   // demo apps are big: always from the network
  e.respondWith(caches.match(req).then((hit) => {
    const net = fetch(req).then((res) => { if (res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); } return res; }).catch(() => hit);
    return hit || net;
  }));
});
