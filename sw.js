/* Ag-once, onbellek-yedek + kurulumda TAM on-bellekleme.
   Desen Goc ve Evrim Simulasyonu'ndan (Proje 2) alindi, orada telefonda sinandi.

   - Kod ve veri her zaman taze: sunucu (gecici tunel) aciksa her istek
     sunucuyla dogrulanir, 304 ise ucuz.
   - Sunucu yoksa onbellekten. Kurulumda her sey bir kere indirildigi icin
     telefona eklendikten sonra PC ve internet gerekmez.
   - Olu tunel adresine giden istek ne hata verir ne doner, asili kalir.
     Proje 2'de sayfa sonsuza dek "yukleniyor"da kaldi; bu yuzden ag istegi
     4 saniyede iptal edilip onbellege dusulur.

   AD'yi yalnizca KABUK listesi degistiginde artir. Kod ve veri guncellemesi
   icin gerekmez: ag-once zaten tazesini getirir. */
const AD = 'dunyam-atlas-v9';   // v9: bitki örtüsü paletli + bitki_veri.png
const KABUK = [
  './', 'index.html', 'app.js', 'style.css', 'manifest.webmanifest', 'data/atlas.json',
  'data/doku.png', 'data/yukseklik.png', 'data/kabartma.jpg', 'data/kabartma_gri.jpg', 'data/kabartma_bir.jpg', 'data/dolasim.png', 'data/su.json', 'data/tektonik.json', 'data/levha.png', 'data/bitki.json', 'data/bitki.png', 'data/bitki_veri.png',
  'icons/icon-192.png', 'icons/icon-512.png',
  'icons/icon-maskable-192.png', 'icons/icon-maskable-512.png', 'icons/apple-touch-icon.png',
];
const AG_ZAMAN_ASIMI_MS = 4000;

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(AD).then(c =>
    Promise.allSettled(KABUK.map(u => fetch(u, { cache: 'no-cache' }).then(r => r.ok && c.put(u, r))))));
});

self.addEventListener('activate', e => e.waitUntil(
  caches.keys()
    .then(k => Promise.all(k.filter(x => x !== AD).map(x => caches.delete(x))))
    .then(() => self.clients.claim())
));

function zamanAsimliFetch(istek, ms) {
  const denetci = new AbortController();
  const zt = setTimeout(() => denetci.abort(), ms);
  return fetch(istek, { signal: denetci.signal, cache: 'no-cache' }).finally(() => clearTimeout(zt));
}

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== location.origin) return;
  // X-Taze: uygulamanin "Guncellemeleri denetle" istegi; onbellege dusulmez,
  // yoksa cevrimdisiyken de "Guncel" deniyordu (gece denetimi).
  const taze = e.request.headers.get('X-Taze') === '1';
  e.respondWith(caches.open(AD).then(async c => {
    // ?v=... gibi sorgu parametreleri ayni dosyayi farkli anahtara bolmesin
    const hit = taze ? undefined : await c.match(e.request, { ignoreSearch: true });
    try {
      const r = await zamanAsimliFetch(e.request, AG_ZAMAN_ASIMI_MS);
      if (r.ok) { c.put(e.request, r.clone()); return r; }
      // Cloudflare Access oturumu dolunca sayfa istegi giris sayfasina
      // yonlendirilir. Onbellekten eski sayfayi vermek yerine yonlendirmeyi
      // tarayiciya birak: yoksa uygulama sessizce eski veride kalir.
      if (r.type === 'opaqueredirect') return r;
      return hit || r;   // sunucu hata dondu (or. olu tunel 502) ama onbellek varsa ondan
    } catch (err) {
      if (hit) return hit;
      throw err;
    }
  }));
});
