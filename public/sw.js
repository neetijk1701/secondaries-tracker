// Keeps an offline copy. Bump VERSION when you publish changes.
const VERSION = "sec-v16";
const FILES = ["./", "index.html", "library.js", "config.js", "manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png", "favicon.png"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  // Site files: try the network first so changes arrive, fall back to the saved copy offline.
  if (url.origin === location.origin) {
    e.respondWith(fetch(e.request, {cache:"no-cache"}).then(r => {
      if (r.ok) { const copy = r.clone(); caches.open(VERSION).then(c => c.put(e.request.mode === "navigate" ? "./" : e.request, copy)); }
      return r;
    }).catch(() => caches.match(e.request.mode === "navigate" ? "./" : e.request).then(r => r || caches.match("index.html"))));
    return;
  }
  // Fonts: saved copy first, then network, saving a copy for offline use.
  if (url.hostname.endsWith("gstatic.com") || url.hostname.endsWith("googleapis.com")) {
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => {
      const copy = r.clone(); caches.open(VERSION).then(c => c.put(e.request, copy)); return r;
    })));
  }
});
