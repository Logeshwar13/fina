// Simple Service Worker for FinA
// Helps prevent unnecessary page reloads and improves performance

const CACHE_NAME = 'fina-v9'; // Updated cache version - AI chat completely disabled
const urlsToCache = [
    '/',
    '/index-new.html',
    '/css/style-new.css'
    // JS files will use network-first strategy
];

// Install event - cache resources
self.addEventListener('install', (event) => {
    // Skip waiting to activate immediately
    self.skipWaiting();
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Opened cache v6');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event - network-first for JS files, cache-first for others
self.addEventListener('fetch', (event) => {
    // Only handle GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Skip API calls
    if (event.request.url.includes('/api/') || event.request.url.includes('localhost:8000')) {
        return;
    }

    // Network-first strategy for JavaScript files to always get latest
    if (event.request.url.endsWith('.js')) {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    // Clone the response before caching
                    const responseToCache = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseToCache);
                    });
                    return response;
                })
                .catch(() => {
                    // Fallback to cache if network fails
                    return caches.match(event.request);
                })
        );
        return;
    }

    // Cache-first for other resources
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            })
    );
});

// Activate event - clean up old caches and take control immediately
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            // Take control of all clients immediately
            return self.clients.claim();
        })
    );
});