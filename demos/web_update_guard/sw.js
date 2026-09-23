// Demo-only service worker. It lets the page simulate a new deploy by serving
// the app a version.json with a different buildId, exactly as a real redeploy
// would. Nothing else is intercepted.
const STATE = 'wug-demo-sim';
const KEY = '/__wug_sim_state';

self.addEventListener('install', (e) => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));

function newBuildId() {
  const hex = '0123456789abcdef';
  let h = '';
  for (let i = 0; i < 16; i++) h += hex[Math.floor(Math.random() * 16)];
  const t = new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d+Z$/, 'Z');
  return h + '-' + t;
}

async function setSim(buildId) {
  const cache = await caches.open(STATE);
  if (buildId === null) return cache.delete(KEY);
  return cache.put(KEY, new Response(buildId));
}

async function getSim() {
  const cache = await caches.open(STATE);
  const hit = await cache.match(KEY);
  return hit ? hit.text() : null;
}

self.addEventListener('message', (event) => {
  const data = event.data || {};
  if (data.type === 'deploy') {
    event.waitUntil(setSim(newBuildId()));
  } else if (data.type === 'reset') {
    event.waitUntil(setSim(null));
  }
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;
  if (!url.pathname.endsWith('/web_update_guard/app/version.json')) return;
  event.respondWith((async () => {
    const response = await fetch(event.request);
    const simulated = await getSim();
    if (!simulated) return response;
    let body;
    try {
      body = await response.clone().json();
    } catch (_) {
      return response;
    }
    body.buildId = simulated;
    body.builtAt = new Date().toISOString();
    return new Response(JSON.stringify(body, null, 2), {
      headers: { 'content-type': 'application/json' },
    });
  })());
});
