/**
Handles the install event. We're going to use this event to cache files,
but first we need to declare the cache and specify the files we want cached.
*/
const CACHE_NAME = 'static-cache';

const FILES_TO_CACHE = [
  '/',
];

self.addEventListener('install', (evt) => {
  console.log('[ServiceWorker] Install');
  evt.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[ServiceWorker] Pre-caching offline page');
      return cache.addAll(FILES_TO_CACHE);
    })
  );

  self.skipWaiting();
});

/**
The activate event happens the first time a connection is made to the service worker.
When a new service worker is made available it is installed in the background but not activated
until there are no pages using the old service worker. We'll use this to clean up any old caches.
*/
self.addEventListener('activate', (evt) => {
  console.log('[ServiceWorker] Activate');
  evt.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(keyList.map((key) => {
        if (key !== CACHE_NAME) {
          console.log('[ServiceWorker] Removing old cache', key);
          return caches.delete(key);
        }
      }));
    })
  );
  self.clients.claim();
});

/**
Network only with index acting as offline page.
*/
self.addEventListener('fetch', (evt) => {
  if (evt.request.mode !== 'navigate') {
    return;
  }
  evt.respondWith(fetch(evt.request).catch(() => {
      return caches.open(CACHE_NAME).then((cache) => {
        return cache.match('index.html');
      });
    })
  );
});