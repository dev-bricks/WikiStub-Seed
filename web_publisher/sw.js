const CACHE_NAME = "wikistub-seed-v2";

const ASSETS = [
  "./index.html",
  "./app.js",
  "./manifest.webmanifest",
  "./data/wikistub_seed.json",
  "./data/search-index.json",
  "./icons/Icon-192.png",
  "./icons/Icon-512.png",
  "./icons/Icon-maskable-192.png",
  "./icons/Icon-maskable-512.png",
  "./icons/apple-touch-icon-180.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) =>
        Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
      )
      .then(() => self.clients.claim())
  );
});

async function networkFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  try {
    const response = await fetch(request);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    await cache.put(request, response.clone());
    return response;
  } catch (error) {
    const cached = await caches.match(request, { ignoreSearch: true });
    if (cached) return cached;
    throw error;
  }
}

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  const isProjectData =
    url.origin === self.location.origin && url.pathname.includes("/data/");

  if (isProjectData) {
    event.respondWith(networkFirst(event.request));
    return;
  }

  event.respondWith(
    caches.match(event.request, { ignoreSearch: true }).then((cached) => cached || fetch(event.request))
  );
});
