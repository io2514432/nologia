/* 체스놀로지아 서비스 워커 — 오프라인 우선(캐시 우선 + 백그라운드 갱신) */
const CACHE = 'chessnologia-v16';
const ASSETS = ['./', './index.html', './config.js', './manifest.json', './icons/icon-192.png', './icons/icon-512.png', './icons/icon-512-maskable.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const isNav = e.request.mode === 'navigate';
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then(hit => {
      const net = fetch(e.request).then(res => {
        if (res && res.ok && new URL(e.request.url).origin === self.location.origin) {
          const cp = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, cp));
        }
        return res;
      }).catch(async () => {
        if (isNav) return (await caches.match('./index.html')) || (await caches.match('./')) || Response.error();
        return hit || Response.error();
      });
      return hit || net;
    })
  );
});
