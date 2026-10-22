// Ajapaik refoto service worker
const CACHE_NAME = 'ajapaik-rephoto-v1';

self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
    // Basic network-first pass-through fetch handler required for PWA installation
    if (event.request.method !== 'GET') {
        return;
    }
    const url = new URL(event.request.url);
    // Explicitly bypass Django admin, auth, and API requests so browser handles native retries & bfcache
    if (url.pathname.startsWith('/admin/') || url.pathname.startsWith('/accounts/') || url.pathname.startsWith('/api/')) {
        return;
    }
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        }),
    );
});
