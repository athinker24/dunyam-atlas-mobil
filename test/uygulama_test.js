// Uygulamanin tarayici testi. GitHub Actions'ta (uygulama.yml, veri.yml) ve
// elle kosar:
//
//     npm install --no-save playwright && npx playwright install chromium
//     node test/uygulama_test.js [klasor]        # varsayilan: repo koku
//
// Neden var: iki hata (piksel gorunumde okyanusun sinif rengine boyanmasi,
// yumusak gorunumun %28 karanlik olmasi) elle cekilen ekran goruntulerinden
// kacip telefonda bulundu. Buradaki denetimler o ikisini ve temel akisi
// yakalar. Olcumler ekran goruntusunden degil dogrudan WebGL tamponundan.
// Sayilar ASAGIDA; esikler bilerek genis, amac bozulmayi yakalamak.
"use strict";
const http = require("http");
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const KOK = path.resolve(process.argv[2] || path.join(__dirname, ".."));
const TUR = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".json": "application/json",
  ".png": "image/png", ".jpg": "image/jpeg", ".webmanifest": "application/manifest+json" };

function sunucu() {
  const s = http.createServer((q, r) => {
    const yol = path.join(KOK, decodeURIComponent(q.url.split("?")[0]).replace(/\/$/, "/index.html"));
    if (!yol.startsWith(KOK) || !fs.existsSync(yol) || fs.statSync(yol).isDirectory()) { r.writeHead(404); return r.end(); }
    r.writeHead(200, { "Content-Type": TUR[path.extname(yol)] || "application/octet-stream" });
    fs.createReadStream(yol).pipe(r);
  });
  return new Promise(ok => s.listen(0, "127.0.0.1", () => ok(s)));
}

const sonuclar = [];
function denetle(ad, gecti, ayrinti) {
  sonuclar.push({ ad, gecti });
  console.log(`${gecti ? "GECTI " : "DUSTU "} ${ad}${ayrinti ? "  (" + ayrinti + ")" : ""}`);
}

// sayfa icinde: kara/okyanus hucre merkezlerini ekranda ornekle, WebGL
// tamponundan ortalama parlaklik oku
const OLC = () => {
  const A = window.__atlas, D = A.D, s = A.durum(), cv = document.getElementById("gl");
  const gl = cv.getContext("webgl"), dpr = cv.width / cv.getBoundingClientRect().width;
  const ic = (i, r) => { const x = i % D.W, y = (i / D.W) | 0; for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
    const xx = x + dx, yy = y + dy; if (xx < 0 || yy < 0 || xx >= D.W || yy >= D.H) return false;
    if (D.land[yy * D.W + xx] !== D.land[i]) return false; } return true; };
  const ust = document.querySelector(".marka").getBoundingClientRect().bottom, alt = document.getElementById("dok").getBoundingClientRect().top;
  const px = new Uint8Array(4);
  const oku = (i) => { const x = s.ox + ((i % D.W) + 0.5) * s.olcek, y = s.oy + (((i / D.W) | 0) + 0.5) * s.olcek;
    if (x < 2 || x > cv.clientWidth - 2 || y < ust + 4 || y > alt - 4) return null;
    gl.readPixels(Math.round(x * dpr), cv.height - 1 - Math.round(y * dpr), 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
    return 0.299 * px[0] + 0.587 * px[1] + 0.114 * px[2]; };
  const kara = [], deniz = [];
  for (let i = 0; i < D.N && (kara.length < 400 || deniz.length < 400); i += 97) {
    if (D.land[i] ? kara.length >= 400 : deniz.length >= 400) continue;
    if (!ic(i, D.land[i] ? 2 : 6)) continue;
    const v = oku(i); if (v === null) continue; (D.land[i] ? kara : deniz).push(v);
  }
  const ort = a => a.reduce((p, c) => p + c, 0) / Math.max(a.length, 1);
  // karada dokunulacak bir hucrenin ekran noktasi
  let hedef = null;
  for (let i = 0; i < D.N && !hedef; i += 131) if (D.land[i] && ic(i, 3)) {
    const x = s.ox + ((i % D.W) + 0.5) * s.olcek, y = s.oy + (((i / D.W) | 0) + 0.5) * s.olcek;
    if (x > 30 && x < cv.clientWidth - 30 && y > ust + 30 && y < alt - 30) hedef = { x, y, i };
  }
  return { kara: ort(kara), deniz: ort(deniz), nk: kara.length, nd: deniz.length, hedef };
};

(async () => {
  const srv = await sunucu(), port = srv.address().port;
  const tarayici = await chromium.launch({
    executablePath: process.env.CHROMIUM_YOLU || undefined,
    args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  const ctx = await tarayici.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  const hatalar = [];
  p.on("pageerror", e => hatalar.push(e.message));
  p.on("console", m => { if (m.type() === "error") hatalar.push(m.text()); });
  const bekle = ms => p.waitForTimeout(ms);
  try {
    await p.goto(`http://127.0.0.1:${port}/index.html`, { waitUntil: "networkidle" });
    await p.waitForFunction(() => document.querySelector("#yukleniyor").hidden, null, { timeout: 60000 });
    const d0 = await p.evaluate(() => window.__atlas.durum());
    denetle("acilis", true);
    denetle("WebGL ile ciziliyor", d0.webgl);

    await bekle(600);
    const yum = await p.evaluate(OLC);
    await p.evaluate(() => document.querySelector("#ay-piksel").click()); await bekle(600);
    const pik = await p.evaluate(OLC);
    await p.evaluate(() => document.querySelector("#ay-piksel").click()); await bekle(300);
    const f = v => v.toFixed(1);
    denetle("orneklem yeterli", yum.nk > 50 && yum.nd > 50, `kara ${yum.nk}, okyanus ${yum.nd}`);
    // okyanus zemini ~#0b141a..#11232c (parlaklik ~18-30); sinif rengi 90+
    denetle("yumusak: okyanus koyu", yum.deniz < 50, `parlaklik ${f(yum.deniz)}`);
    denetle("piksel: okyanus koyu", pik.deniz < 50, `parlaklik ${f(pik.deniz)}`);
    denetle("kara okyanustan belirgin", yum.kara > yum.deniz + 40, `kara ${f(yum.kara)}`);
    // olculdu: duzeltmeden sonra 127.1 / 127.8; hata varken 91.6 / 127.8
    const oran = yum.kara / Math.max(pik.kara, 1);
    denetle("yumusak ve piksel kara parlakligi esit", oran > 0.9 && oran < 1.1, `${f(yum.kara)} / ${f(pik.kara)}`);

    if (yum.hedef) {
      await p.touchscreen.tap(yum.hedef.x, yum.hedef.y); await bekle(700);
      const kart = await p.evaluate(() => ({ acik: !document.querySelector("#kart").hidden,
        metin: document.querySelector("#kart-icerik").textContent, sec: window.__atlas.durum().sec }));
      denetle("karaya dokununca kart aciliyor", kart.acik && kart.sec === yum.hedef.i && /\d/.test(kart.metin));
      await p.click("#kart-kapat"); await bekle(300);
    } else denetle("karaya dokununca kart aciliyor", false, "ekranda uygun kara hucresi yok");

    for (const k of ["sicaklik", "yagis", "arazi", "iklim"]) {
      await p.evaluate(k => document.querySelector(`[data-k=${k}]`).click(), k); await bekle(250);
      if (k === "sicaklik" || k === "yagis") { await p.evaluate(() => document.querySelectorAll("#donem button")[7].click()); await bekle(250); }
    }
    const kaynak = await p.evaluate(() => document.querySelectorAll("#kabartma-kaynak button").length);
    if (kaynak) { await p.evaluate(() => document.querySelector("[data-kaynak=gri]").click()); await bekle(250);
      await p.evaluate(() => document.querySelector("[data-kaynak=editor]").click()); }
    denetle("katman, ay ve kabartma gecisleri hatasiz", hatalar.length === 0, hatalar.slice(0, 3).join(" | "));

    // cevrimdisi: service worker her seyi onbellege almis olmali
    await p.evaluate(() => navigator.serviceWorker.ready); await bekle(2500);
    await ctx.setOffline(true);
    await p.reload({ waitUntil: "load" }).catch(() => {});
    const cd = await p.waitForFunction(() => document.querySelector("#yukleniyor").hidden, null, { timeout: 20000 }).then(() => true, () => false);
    denetle("internetsiz aciliyor", cd);
    await ctx.setOffline(false);
  } catch (e) {
    denetle("beklenmeyen hata", false, e.message.split("\n")[0]);
  }
  await tarayici.close(); srv.close();
  const dusen = sonuclar.filter(s => !s.gecti).length;
  console.log(dusen ? `\n${dusen} denetim DUSTU` : `\n${sonuclar.length}/${sonuclar.length} gecti`);
  process.exit(dusen ? 1 : 0);
})();
