const CACHE_NAME = 'cp-report-v1';
const OFFLINE_URL = '/static/offline.html';

const ASSETS_TO_CACHE = [
  '/',
  '/static/css/style.css',
  '/static/manifest.json',
  '/static/icons/icon-192.svg',
  '/static/icons/icon-512.svg',
  OFFLINE_URL
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Network-first for API requests, cache-first for navigation and static
  const request = event.request;
  const url = new URL(request.url);

  // For same-origin navigation requests, try network then fallback to cache/offline
  if (request.mode === 'navigate' || (request.method === 'GET' && request.headers.get('accept') && request.headers.get('accept').includes('text/html'))) {
    event.respondWith(
      fetch(request).then((response) => {
        // put a copy in cache
        const copy = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
        return response;
      }).catch(() => caches.match(request).then(r => r || caches.match(OFFLINE_URL)))
    );
    return;
  }

  // For other GET requests, try cache then network
  if (request.method === 'GET') {
    event.respondWith(
      caches.match(request).then((cached) => {
        return cached || fetch(request).then((response) => {
          // update cache for future
          const respClone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, respClone));
          return response;
        }).catch(() => {
          // if requested a resource and not cached, try manifest or icons
          return caches.match('/static/manifest.json');
        });
      })
    );
  }
});
