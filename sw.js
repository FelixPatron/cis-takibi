// Önce ağ, olmazsa önbellek. Firebase istekleri asla önbelleğe alınmaz.
const CACHE = "cis-takibi-v2";
const DOSYALAR = ["./", "./index.html", "./manifest.json", "./icon-192.png", "./icon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(DOSYALAR)));
  self.skipWaiting();
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;
  e.respondWith(
    fetch(e.request).then(r => {
      const kopya = r.clone();
      caches.open(CACHE).then(c => c.put(e.request, kopya));
      return r;
    }).catch(() => caches.match(e.request))
  );
});
