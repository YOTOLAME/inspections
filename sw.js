var CACHE_NAME = 'inspectare-v19';
var FILES = [
  '/inspections/',
  '/inspections/index.html',
  '/inspections/capture.html',
  '/inspections/review.html',
  '/inspections/INSPECTARE-500M-ASSET-MOBILE.html',
  '/inspections/INSPECTARE-500M-MOBILE.html',
  '/inspections/INSPECTARE-AHTS-MOBILE.html',
  '/inspections/INSPECTARE-CREWBOAT-MOBILE.html',
  '/inspections/INSPECTARE-PSV-MOBILE.html',
  '/inspections/INSPECTARE-TUG-MOBILE.html',
  '/inspections/OVID-AHTS-TUG-OPERATIONS-MOBILE.html',
  '/inspections/OVID-BARGE-OPERATIONS-MOBILE.html',
  '/inspections/OVID-COMMON-PART1-MOBILE.html',
  '/inspections/OVID-COMMON-PART2-MOBILE.html',
  '/inspections/OVID-COMMON-PART3-MOBILE.html',
  '/inspections/OVID-COMMON-PART4-MOBILE.html',
  '/inspections/OVID-CREWBOAT-PART1-MOBILE.html',
  '/inspections/OVID-CREWBOAT-PART2-MOBILE.html',
  '/inspections/OVID-DP-OPERATIONS-MOBILE.html',
  '/inspections/OVID-MPSV-OPERATIONS-MOBILE.html',
  '/inspections/OVID-PSV-OPERATIONS-MOBILE.html'
];

self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return Promise.all(FILES.map(function(u) {
        return fetch(new Request(u, { cache: 'reload' })).then(function(r) {
          if (r && r.ok) { return cache.put(u, r); }
        });
      }));
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
    }).then(function() { return self.clients.claim(); })
  );
});

/* Network first (always the latest version when online), cache when offline or network too slow. */
self.addEventListener('fetch', function(e) {
  var req = e.request;
  if (req.method !== 'GET' || req.url.indexOf(self.location.origin) !== 0) { return; }
  e.respondWith(new Promise(function(resolve) {
    var done = false;
    function fromCache() {
      return caches.match(req, { ignoreSearch: true }).then(function(c) { return c || caches.match('/inspections/index.html'); });
    }
    var timer = setTimeout(function() {
      fromCache().then(function(c) { if (!done && c) { done = true; resolve(c); } });
    }, 4000);
    fetch(new Request(req, { cache: 'no-cache' })).then(function(r) {
      clearTimeout(timer);
      if (r && r.ok) {
        var copy = r.clone();
        caches.open(CACHE_NAME).then(function(cache) { cache.put(req, copy); });
      }
      if (!done) { done = true; resolve(r); }
    })['catch'](function() {
      clearTimeout(timer);
      fromCache().then(function(c) { if (!done) { done = true; resolve(c || Response.error()); } });
    });
  }));
});
