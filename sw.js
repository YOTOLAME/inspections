const CACHE_NAME = 'inspectare-v1';
const FILES = [
  '/inspections/',
  '/inspections/index.html',
  '/inspections/INSPECTARE-500M-MOBILE.html',
  '/inspections/INSPECTARE-CREWBOAT-MOBILE.html',
  '/inspections/INSPECTARE-PSV-MOBILE.html',
  '/inspections/OVID-DP-OPERATIONS-MOBILE.html'
];

self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(FILES);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(k) { return k !== CACHE_NAME; })
            .map(function(k) { return caches.delete(k); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function(e) {
  e.respondWith(
    caches.match(e.request).then(function(cached) {
      return cached || fetch(e.request);
    })
  );
});
