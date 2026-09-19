// Ajapaik refoto service worker
const CACHE_NAME = 'ajapaik-refoto-v1';

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
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});
