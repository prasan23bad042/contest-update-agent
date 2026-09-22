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
  const request = event.request;
  const url = new URL(request.url);

  // For same-origin navigation requests (HTML), try network then fallback to cache/offline
  if (request.mode === 'navigate' || (request.method === 'GET' && request.headers.get('accept') && request.headers.get('accept').includes('text/html'))) {
    event.respondWith(
      fetch(request).then((response) => {
        // put a copy in cache for offline navigations
        try {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
        } catch (e) { /* ignore clone/cache errors */ }
        return response;
      }).catch(() => caches.match(request).then(r => r || caches.match(OFFLINE_URL)))
    );
    return;
  }

  // Exclude API or dynamic endpoints from cache-first behavior.
  // Use network-first for API calls (e.g., /generate, /api/*)
  const isSameOrigin = url.origin === self.location.origin;
  const isApiCall = isSameOrigin && (url.pathname.startsWith('/generate') || url.pathname.startsWith('/api'));

  if (request.method === 'GET' && isApiCall) {
    event.respondWith(
      fetch(request).then((response) => {
        // do not cache API responses (or you could cache selectively)
        return response;
      }).catch(() => {
        // fallback to offline page when network unavailable
        return caches.match(OFFLINE_URL);
      })
    );
    return;
  }

  // For other GET requests (static assets), try cache then network
  if (request.method === 'GET') {
    event.respondWith(
      caches.match(request).then((cached) => {
        if (cached) return cached;
        return fetch(request).then((response) => {
          // update cache for future
          try {
            const respClone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(request, respClone));
          } catch (e) { /* ignore */ }
          return response;
        }).catch(() => caches.match('/static/manifest.json'));
      })
    );
  }
});
