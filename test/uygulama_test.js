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
  const adim = Math.max(1, Math.floor(D.N / 5000)) | 1;   // kaba veride (--res 1.0) de yeterli orneklem
  for (let i = 0; i < D.N && (kara.length < 400 || deniz.length < 400); i += adim) {
    if (D.land[i] ? kara.length >= 400 : deniz.length >= 400) continue;
    if (!ic(i, D.land[i] ? 2 : 6)) continue;
    const v = oku(i); if (v === null) continue; (D.land[i] ? kara : deniz).push(v);
  }
  const ort = a => a.reduce((p, c) => p + c, 0) / Math.max(a.length, 1);
  // karada dokunulacak bir hucrenin ekran noktasi
  let hedef = null;
  for (let i = 0; i < D.N && !hedef; i += adim) if (D.land[i] && ic(i, 3)) {
    const x = s.ox + ((i % D.W) + 0.5) * s.olcek, y = s.oy + (((i / D.W) | 0) + 0.5) * s.olcek;
    if (x > 30 && x < cv.clientWidth - 30 && y > ust + 30 && y < alt - 30) hedef = { x, y, i };
  }
  return { kara: ort(kara), deniz: ort(deniz), nk: kara.length, nd: deniz.length, hedef };
};

(async () => {
  const srv = await sunucu(), port = srv.address().port; let kapali = false;
  const tarayici = await chromium.launch({
    executablePath: process.env.CHROMIUM_YOLU || undefined,
    args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  const ctx = await tarayici.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  const hatalar = [];
  p.on("pageerror", e => hatalar.push(e.message));
  // 404 konsolda adresiz "Failed to load resource" olarak da duser; onu yanit
  // olayindan adresiyle yakalariz. Eski veride olmayan istege bagli dokular muaf.
  const ISTEGE_BAGLI = /data\/(kabartma_gri\.jpg|kabartma_bir\.jpg|dolasim\.png)$/;
  p.on("console", m => { if (m.type() === "error" && !/^Failed to load resource/.test(m.text())) hatalar.push(m.text()); });
  p.on("response", y => { if (y.status() >= 400 && !ISTEGE_BAGLI.test(y.url())) hatalar.push(`${y.status()} ${y.url()}`); });
  const bekle = ms => p.waitForTimeout(ms);
  // ilk acilista sayfa bir kez yuklenmeli (service worker ilk kurulumda
  // controllerchange ile yeniliyordu; gece denetimi)
  let yukleme = 0; p.on("framenavigated", f => { if (f === p.mainFrame()) yukleme++; });
  try {
    await p.goto(`http://127.0.0.1:${port}/index.html`, { waitUntil: "networkidle" });
    await p.waitForFunction(() => document.querySelector("#yukleniyor").hidden, null, { timeout: 60000 });
    const d0 = await p.evaluate(() => window.__atlas.durum());
    denetle("acilis", true);
    await bekle(1500);
    denetle("ilk acilista tek yukleme", yukleme === 1, `${yukleme} yukleme`);
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
      denetle("karaya dokununca kart aciliyor", kart.acik && kart.sec === yum.hedef.i && /\d/.test(kart.metin) && /Kar/.test(kart.metin));
      // Android geri tusu acik karti kapatmali, uygulamadan cikmamali (gece denetimi)
      await p.goBack({ waitUntil: "commit" }).catch(() => {}); await bekle(400);
      const geri = await p.evaluate(() => ({ kart: !document.querySelector("#kart").hidden, yol: location.pathname, acik: !!window.__atlas }));
      denetle("geri tusu karti kapatir, sayfada kalir", !geri.kart && geri.acik && /index\.html$|\/$/.test(geri.yol), JSON.stringify(geri));
    } else denetle("karaya dokununca kart aciliyor", false, "ekranda uygun kara hucresi yok");

    for (const k of ["sicaklik", "yagis", "kar", "arazi", "iklim"]) {
      await p.evaluate(k => document.querySelector(`[data-k=${k}]`).click(), k); await bekle(250);
      if (k === "sicaklik" || k === "yagis" || k === "kar") { await p.evaluate(() => document.querySelectorAll("#donem button")[7].click()); await bekle(250); }
    }
    // kar katmani: kar hesabi tembel; sekme acilinca cizilmeli, tuval tek renk kalmamali
    await p.evaluate(() => document.querySelector("[data-k=kar]").click()); await bekle(400);
    const kr = await p.evaluate(() => { const c = document.getElementById("gl"), gl = c.getContext("webgl"), px = new Uint8Array(4), r = new Set();
      // sabit 10x8 izgara: rastgele ornek her kosuda baska sonuc verebiliyordu
      for (let i = 0; i < 80; i++) { gl.readPixels(Math.floor(c.width * (0.1 + 0.8 * (i % 10 + 0.5) / 10)), Math.floor(c.height * (0.35 + 0.45 * (((i / 10) | 0) + 0.5) / 8)), 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); r.add(px.join()); }
      return { renk: r.size, lejant: document.querySelector("#aciklama").textContent }; });
    denetle("kar katmani ciziliyor", kr.renk > 5 && /ay örtü/.test(kr.lejant), `${kr.renk} farkli renk`);
    await p.evaluate(() => document.querySelector("[data-k=iklim]").click()); await bekle(250);
    // Dolasim sekmesi (veride varsa): ruzgar oklari ve akinti yollari cizilmeli
    const dol = await p.evaluate(() => !document.querySelector("[data-k=dolasim]").hidden);
    if (dol) {
      await p.evaluate(() => document.querySelector("[data-k=dolasim]").click()); await bekle(400);
      await p.evaluate(() => document.querySelectorAll("#donem button")[1].click()); await bekle(400);
      const d = await p.evaluate(() => ({ cizgi: [...document.querySelectorAll("#kaplama path.ruzgar")].reduce((t, e) => t + e.getAttribute("d").split("M").length - 1, 0),
        akinti: document.querySelectorAll("#kaplama marker").length ? window.__atlas.D.akintilar.length : 0 }));
      denetle("dolasim: ruzgar cizgileri ve akintilar ciziliyor", d.cizgi > 20 && d.akinti > 0, `${d.cizgi} parca, ${d.akinti} akinti`);
      // hareketli ruzgar: parcacik tuvaline bir saniyede bir seyler cizilmeli
      await p.evaluate(() => document.querySelector("#parcacik-ac").click()); await bekle(1200);
      const pc = await p.evaluate(() => { const c = document.querySelector("#parcacik"), x = c.getContext("2d").getImageData(0, 0, c.width, c.height).data;
        let n = 0; for (let i = 3; i < x.length; i += 4) if (x[i] > 40) n++; return { n, gizli: c.hidden }; });
      denetle("dolasim: hareketli ruzgar parcaciklari ciziliyor", !pc.gizli && pc.n > 500, `${pc.n} piksel`);
      await p.evaluate(() => document.querySelector("[data-zemin=hiz]").click()); await bekle(300);
      await p.evaluate(() => document.querySelector("#parcacik-ac").click()); await bekle(200);
      await p.evaluate(() => document.querySelector("[data-zemin=sst]").click()); await bekle(200);
      await p.evaluate(() => document.querySelector("[data-k=iklim]").click()); await bekle(250);
    }
    const kaynak = await p.evaluate(() => document.querySelectorAll("#kabartma-kaynak button").length);
    if (kaynak) { await p.evaluate(() => document.querySelector("[data-kaynak=gri]").click()); await bekle(250);
      await p.evaluate(() => document.querySelector("[data-kaynak=editor]").click()); await bekle(250);
      await p.evaluate(() => document.querySelector("[data-kaynak=bir]")?.click()); }
    denetle("katman, ay ve kabartma gecisleri hatasiz", hatalar.length === 0, hatalar.slice(0, 3).join(" | "));

    // pan siniri: cok yakinken uzaga surukleyince ekran bos okyanusa/verinin
    // disina kaymamali; ekranin ortasi kara kutusuna yakin kalmali (gece denetimi)
    await p.mouse.move(195, 420); for (let i = 0; i < 12; i++) await p.mouse.wheel(0, -400);
    await p.mouse.down(); await p.mouse.move(195 + 5000, 420 - 5000, { steps: 4 }); await p.mouse.up(); await bekle(300);
    const pan = await p.evaluate(() => { const A = window.__atlas, D = A.D, s = A.durum();
      let kara = 0; for (let y = 140; y < 700; y += 10) for (let x = 5; x < 385; x += 10) {
        const gx = Math.floor((x - s.ox) / s.olcek), gy = Math.floor((y - s.oy) / s.olcek);
        if (gx >= 0 && gy >= 0 && gx < D.W && gy < D.H && D.land[gy * D.W + gx]) kara++; }
      return kara; });
    denetle("yakinken surukleyince kara ekranda kaliyor", pan > 0, `${pan} kara ornegi`);
    await p.click("#sigdir"); await bekle(250);

    // WebGL yoksa Canvas2D yedegi: telefonda GPU surucusu reddederse tek yol
    // bu; CI'da hic sinanmiyordu (gece denetimi)
    { const y = await ctx.newPage(), yh = [];
      y.on("pageerror", e => yh.push(e.message));
      await y.addInitScript(() => { const og = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function (t, ...r) { return /webgl/.test(t) ? null : og.call(this, t, ...r); }; });
      await y.goto(`http://127.0.0.1:${port}/index.html`, { waitUntil: "load" });
      const ac = await y.waitForFunction(() => document.querySelector("#yukleniyor").hidden, null, { timeout: 30000 }).then(() => true, () => false);
      const r = ac ? await y.evaluate(() => { const c = document.getElementById("gl"), x = c.getContext("2d"), n = new Set();
        for (let i = 0; i < 80; i++) n.add(x.getImageData(Math.floor(c.width * (0.1 + 0.8 * (i % 10 + 0.5) / 10)), Math.floor(c.height * (0.2 + 0.6 * (((i / 10) | 0) + 0.5) / 8)), 1, 1).data.join());
        return { webgl: window.__atlas.durum().webgl, renk: n.size }; }) : null;
      denetle("WebGL yokken Canvas2D ile ciziliyor", ac && r && !r.webgl && r.renk > 5 && yh.length === 0, r ? `${r.renk} farkli renk ${yh.join(" | ")}` : "acilmadi");
      await y.close(); }

    // cevrimdisi: service worker her seyi onbellege almis olmali
    await p.evaluate(() => navigator.serviceWorker.ready); await bekle(2500);
    // Gercek kesinti: tarayicinin cevrimdisi taklidi yeniden baslayan service
    // worker'a uygulanmiyor (olculdu: reload sonrasi SW sunucuya ulasti, var
    // olmayan dosyaya 404 dondu); bu denetim ag acikken geciyordu. Sunucu da
    // kapatilir.
    await ctx.setOffline(true);
    srv.close(); srv.closeAllConnections?.(); kapali = true;
    await p.reload({ waitUntil: "load" }).catch(() => {});
    const cd = await p.waitForFunction(() => document.querySelector("#yukleniyor").hidden, null, { timeout: 20000 }).then(() => true, () => false);
    const ag = await p.evaluate(async () => { try { await fetch("data/yok_" + Date.now() + ".json"); return "acik"; } catch (_) { return "kapali"; } }).catch(() => "?");
    if (ag !== "kapali") console.log("UYARI: cevrimdisi denetiminde ag hala " + ag);
    denetle("internetsiz aciliyor", cd);
    // internetsizken "Guncellemeleri denetle" onbellekteki surumu "Guncel" diye
    // sunmamali (gece denetimi: service worker sessizce onbellege dusuyordu)
    if (cd) {
      const gm = await p.evaluate(async () => { const b = document.getElementById("bildirim"), g = [];
        new MutationObserver(() => g.push(b.textContent)).observe(b, { childList: true, characterData: true, subtree: true });
        document.getElementById("guncelle").click(); await new Promise(r => setTimeout(r, 2500)); return g; });
      denetle("internetsizken guncelleme denetimi 'Guncel' demiyor", gm.length > 0 && !gm.some(t => /Güncel ·/.test(t)), JSON.stringify(gm));
    }
    await ctx.setOffline(false);
  } catch (e) {
    denetle("beklenmeyen hata", false, e.message.split("\n")[0]);
  }
  await tarayici.close(); if (!kapali) srv.close();
  const dusen = sonuclar.filter(s => !s.gecti).length;
  console.log(dusen ? `\n${dusen} denetim DUSTU` : `\n${sonuclar.length}/${sonuclar.length} gecti`);
  process.exit(dusen ? 1 : 0);
})();
