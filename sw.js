// Atualize este identificador a cada publicação para substituir o cache antigo.
const CACHE = 'louvores-shell-v10-2-ebd-data';
const APP_FILES = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './catalogo.json'];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(APP_FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil(Promise.all([
    caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key)))),
    self.clients.claim()
  ]));
});
self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;
  // Prefere a versão nova quando há conexão. Na falta dela, usa arquivos locais.
  event.respondWith(fetch(req).then(response => {
    if (response.ok && (new URL(req.url).pathname.endsWith('/') || APP_FILES.some(p => new URL(p, self.registration.scope).pathname === new URL(req.url).pathname))) {
      const copy = response.clone();
      event.waitUntil(caches.open(CACHE).then(cache => cache.put(req, copy)));
    }
    return response;
  }).catch(async () => (await caches.match(req)) || (req.mode === 'navigate' ? await caches.match('./index.html') : Response.error())));
});
