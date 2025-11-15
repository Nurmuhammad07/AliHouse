// Service Worker для AliHouse PWA
const CACHE_NAME = 'alihouse-v1';
const RUNTIME_CACHE = 'alihouse-runtime-v1';

// Файлы для кеширования при установке
const STATIC_CACHE_URLS = [
  '/',
  '/static/css/app.css',
  '/static/css/landing.css',
  '/static/js/theme.js',
  '/static/js/landing.js',
  '/static/js/pwa.js',
  '/catalog/',
];

// Установка Service Worker
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Caching static files');
        return cache.addAll(STATIC_CACHE_URLS.map(url => new Request(url, { cache: 'reload' })));
      })
      .catch((error) => {
        console.error('[Service Worker] Cache install failed:', error);
      })
  );
  self.skipWaiting();
});

// Активация Service Worker
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => {
            return cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE;
          })
          .map((cacheName) => {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          })
      );
    })
  );
  return self.clients.claim();
});

// Перехват запросов (стратегия: Network First, затем Cache)
self.addEventListener('fetch', (event) => {
  // Пропускаем запросы не-GET
  if (event.request.method !== 'GET') {
    return;
  }

  // Пропускаем запросы к API (они должны быть свежими)
  if (event.request.url.includes('/api/')) {
    return;
  }

  // Пропускаем запросы к админке
  if (event.request.url.includes('/admin/')) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Клонируем ответ для кеша
        const responseToCache = response.clone();

        // Кешируем успешные ответы
        if (response.status === 200) {
          caches.open(RUNTIME_CACHE).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }

        return response;
      })
      .catch(() => {
        // Если сеть недоступна, пытаемся получить из кеша
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }

          // Если это навигационный запрос и нет кеша, возвращаем офлайн-страницу
          if (event.request.mode === 'navigate') {
            return caches.match('/');
          }

          return new Response('Offline', {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({
              'Content-Type': 'text/plain',
            }),
          });
        });
      })
  );
});

// Обработка сообщений от клиента
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

