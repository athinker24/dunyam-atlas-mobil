"use strict";
/* Dunyam Atlasi — mobil.

   Veri data/atlas.json'dan, harita dokulari data/doku.png, yukseklik.png,
   kabartma.jpg'den gelir; hepsini uret.py yazar. Dunya yeniden kosuldugunda
   uygulama koduna dokunmak gerekmez.

   Cizim WebGL: harita her kareye ekran cozunurlugunde yeniden cizilir,
   yakinlasinca bulaniklasmaz. Yumusak gorunumde kiyi ve sinif sinirlari
   ince dokulardan, sicaklik/yagis alanlari GPU'da cift dogrusal
   aradegerlenerek gelir; renk aradegerlemeden SONRA verilir (ara renk
   uydurulmaz). Piksel gorunumu modelin hucrelerini oldugu gibi cizer.
   WebGL yoksa Canvas2D ile piksel gorunumune duser. */

const $ = s => document.querySelector(s);
const AYLAR = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"];
const AY_HARF = ["O","Ş","M","N","M","H","T","A","E","E","K","A"];

/* ---- renkler ----
   Koppen paleti KOYU ZEMIN icin yeniden kuruldu (Eylul 2026). Ana gruplar ton
   ailesi olarak korunur: A yesil-turkuaz, B toprak/kum, C zeytin-yesil,
   D arduvaz-mavi (Ds morumsu, Dw mavi, Df camgobegi), E gri. Doygunluk dusuk,
   parlaklik dengeli: kabartma golgesiyle birlikte okunur. Aw bilerek ayri
   ton (tozlu gul): savan turkuazda Af/Am'den secilmiyor, sari-kahvede bozkirla
   karisiyordu. MASAUSTU SABLONUNDAN AYRISTI, bkz CLAUDE.md 7.4. */
const KPAL = {
  Af:"#2e7466", Am:"#3f8c7c", Aw:"#a97d8c",
  BWh:"#c47552", BWk:"#b59584", BSh:"#cf9a57", BSk:"#c9ae7b",
  Csa:"#b4a44c", Csb:"#9f9b55", Csc:"#88885f",
  Cwa:"#71994c", Cwb:"#618752", Cwc:"#5a7658",
  Cfa:"#428b58", Cfb:"#3b7852", Cfc:"#4d6c58",
  Dsa:"#7b6b9c", Dsb:"#6e6692", Dsc:"#646083", Dsd:"#5b5b74",
  Dwa:"#5c80b6", Dwb:"#52709f", Dwc:"#4b6389", Dwd:"#465771",
  Dfa:"#5294a9", Dfb:"#4b8297", Dfc:"#4b7183", Dfd:"#47606e",
  ET:"#99a2a5", EF:"#d5d9da",
};
// Dunya'da ayni sinifin dustugu yerler: "BSk" degil, "Mogolistan bozkiri".
const KREF = {
  Af:"Amazon, Kongo Havzası", Am:"Batı Hindistan kıyısı, Miami",
  Aw:"Serengeti, Kuzey Avustralya", BWh:"Sahra, Arabistan",
  BWk:"Gobi, Taklamakan", BSh:"Sahel, Kalahari kenarı",
  BSk:"Moğolistan ve Kazakistan bozkırı", Csa:"Akdeniz kıyıları, Kaliforniya",
  Csb:"Portekiz, orta Şili", Csc:"Yüksek And ve Kaskad yamaçları",
  Cwa:"Kuzey Hindistan, Güney Çin", Cwb:"Meksika ve Etiyopya yaylaları",
  Cwc:"And yüksek yaylaları", Cfa:"Karadeniz kıyısı, güneydoğu ABD",
  Cfb:"Batı Avrupa, Yeni Zelanda", Cfc:"İzlanda ve Faroe kıyıları",
  Dsa:"Doğu Anadolu havzaları, İran yaylası", Dsb:"Great Basin dağları",
  Dsc:"Yüksek Sierra Nevada", Dsd:"Doğu Sibirya yükseltileri (çok nadir)",
  Dwa:"Pekin, Kuzey Çin ovası", Dwb:"Vladivostok, Kuzey Kore dağları",
  Dwc:"Transbaykal, kuzey Moğolistan taygası", Dwd:"Oymyakon, Verhoyansk",
  Dfa:"Ukrayna, Chicago", Dfb:"Moskova, Toronto",
  Dfc:"Sibirya ve Finlandiya taygası", Dfd:"Yakutistan",
  ET:"Kutup tundrası, İzlanda yaylası", EF:"Grönland ve Antarktika buzulu",
};
const GRUP = {A:"Tropikal", B:"Kurak", C:"Ilıman", D:"Soğuk", E:"Kutup"};
const GRUP_RENK = {A:"#3f8c7c", B:"#c9ae7b", C:"#6e9650", D:"#5780ad", E:"#b8bec0"};
// Gokkusagi degil; koyu zeminde iki ucu da secilir kalir.
const RAMPA = {
  sicaklik:["#2b3a6e","#34599a","#4c84ae","#83aec0","#c3d3cb","#e3d4a3","#e0ab67","#cf7c46","#b0503a","#852d33"],
  // ruzgar hizi: sakin koyu mavi -> ruzgarli sicak tonlar; koyu zeminde okunur
  ruzgar:["#28345a","#2c5f86","#2f8a93","#5aa77f","#a2b865","#d7b957","#dc8b47","#c75a44","#99405d"],
  // kar: soluk mavi -> beyaz; karsiz kara ayrica notr gri
  kar:["#3e5572","#56718f","#7892ad","#a0b6c9","#c9d6e1","#eef2f5"],
  yagis:["#5f5139","#86724a","#a3955a","#8aa86a","#5d9f79","#3f8d83","#2f7489","#2b5a86","#2d4478","#2a3163"],
};
// Arazi: yuzdelik degil MUTLAK metre duraklari (hipsometrik renk)
const ARAZI_DURAK = [[0,"#3c6446"],[200,"#557a4a"],[500,"#7d8a52"],[900,"#9c9160"],[1500,"#a3815c"],
                     [2500,"#8a6a55"],[3500,"#827a74"],[4500,"#aeb0b0"],[6000,"#e6e8e8"]];
const OKYANUS_KIYI = "#11232c", OKYANUS_DERIN = "#0b141a";

const hex = h => [parseInt(h.slice(1,3),16), parseInt(h.slice(3,5),16), parseInt(h.slice(5,7),16)];
function rampa(dur, t){ t = Math.max(0, Math.min(1, t));
  const x = t*(dur.length-1), i = Math.min(dur.length-2, Math.floor(x)), f = x-i, a = hex(dur[i]), b = hex(dur[i+1]);
  return [a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f, a[2]+(b[2]-a[2])*f]; }
function araziRenk(m){ const d = ARAZI_DURAK;
  if(m <= d[0][0]) return hex(d[0][1]);
  for(let i=1;i<d.length;i++) if(m <= d[i][0]){ const f=(m-d[i-1][0])/(d[i][0]-d[i-1][0]), a=hex(d[i-1][1]), b=hex(d[i][1]);
    return [a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f, a[2]+(b[2]-a[2])*f]; }
  return hex(d[d.length-1][1]); }
const css = c => `rgb(${c[0]|0},${c[1]|0},${c[2]|0})`;
const eksi = v => String(v).replace("-", "\u2212");   // tipografik eksi
// uretim damgasi: yeni veride UTC ("...T19:24Z"), telefonun saatine cevrilir.
// Once makinenin yerel saatiydi: GitHub'da UTC, masaustunde TSI, ayirt
// edilemiyordu (gece denetimi). Eski bicim oldugu gibi gosterilir.
const tarih = u => { const d = /T\d\d:\d\dZ$/.test(u||"") ? new Date(u) : null;
  return d && !isNaN(d) ? d.toLocaleString("tr-TR", {day:"numeric", month:"long", year:"numeric", hour:"2-digit", minute:"2-digit"}) : u; };
// Turkce ondalik virgul. Lejant ve deniz karti virgul, sinif paylari,
// koordinatlar ve uret.py'den gelen metinler nokta yaziyordu (gece denetimi).
const virgul = v => String(v).replace(/(\d)\.(?=\d)/g, "$1,");
const cssRampa = dur => `linear-gradient(90deg,${dur.join(",")})`;

function b64(s){ const bin = atob(s), o = new Uint8Array(bin.length);
  for(let i=0;i<bin.length;i++) o[i] = bin.charCodeAt(i); return o; }
function bitAc(by, n){ const o = new Uint8Array(n);
  for(let i=0;i<n;i++) o[i] = (by[i>>3] >> (7-(i&7))) & 1; return o; }
// uret.py kodla() ile ayni: bayt 1..255, olcek "kok" ise karesi alinir
const kodCoz = (k, b) => { const x = (b-1)/254; return k.lo + (k.kok ? x*x : x)*(k.hi-k.lo); };

function bildir(msg, ms=3200){ const t=$("#bildirim"); t.textContent=msg; t.hidden=false;
  clearTimeout(bildir._z); bildir._z=setTimeout(()=>{ t.hidden=true; }, ms); }

const AYAR_ANAHTAR = "dunyam-ayar";
const ayar = Object.assign({kabartma:true, kabartmaKaynak:"bir", piksel:false, izgara:true, bant:false,
  dolZemin:"sst", parcacik:false, sicMod:"ort", deniz:true, su:true, suKol:"ana", araziMod:"yukseklik", yasamKiyi:"genis"},
  (()=>{ try{ return JSON.parse(localStorage.getItem(AYAR_ANAHTAR)) || {}; }catch(_){ return {}; } })());
// Eylul 2026: birlesik kabartma varsayilan oldu. Eski surumde "editor"
// kaydedilmis telefonlar bir kez birlesige gecer; sonra secim kullanicinin.
if(ayar.kabSurum !== 2){ if(ayar.kabartmaKaynak === "editor") ayar.kabartmaKaynak = "bir"; ayar.kabSurum = 2; }
const ayarYaz = () => { try{ localStorage.setItem(AYAR_ANAHTAR, JSON.stringify(ayar)); }catch(_){} };

function resimYukle(src){
  return new Promise((ok, hata) => { const im = new Image(); im.onload = () => ok(im);
    im.onerror = () => hata(new Error(src+" okunamadı")); im.src = src; });
}

/* ================================================================ veri */
function veriHazirla(J){
  const R = J.data.regions.global, W = R.w, H = R.h, N = W*H;
  const land = bitAc(b64(R.land), N);
  const kop = b64(R.fields.koppen.model);
  const alan = k => ({lo:R.fields[k].lo, hi:R.fields[k].hi, kok:R.fields[k].olcek==="kok", a:b64(R.fields[k].model)});
  const tyil = alan("temp_yil"), pyil = alan("prec_yil");
  const ek = {lo:R.elev.lo, hi:R.elev.hi, kok:false};
  const eb = b64(R.elev.data), elev = new Float32Array(N);
  for(let i=0;i<N;i++) elev[i] = kodCoz(ek, eb[i]);

  // kara sirasi: uret.py aylik veriyi kara hucrelerini satir sirasiyla paketler
  const karaSira = new Int32Array(N).fill(-1); let n = 0;
  for(let i=0;i<N;i++) if(land[i]) karaSira[i] = n++;
  const A = R.aylik;
  if(!A || A.n !== n) throw new Error("aylık veri eksik ya da kara sayısıyla uyuşmuyor");
  const Tk = {lo:A.T.lo, hi:A.T.hi, kok:A.T.olcek==="kok"}, Pk = {lo:A.P.lo, hi:A.P.hi, kok:A.P.olcek==="kok"};
  const Tm = b64(A.T.data), Pm = b64(A.P.data);

  // okyanus hucresine en yakin kara hucresi (cok kaynakli BFS). Alanlar kiyida
  // cift dogrusal aradegerlenirken okyanus degeri karaya sizmasin diye
  // okyanus hucreleri en yakin karanin degeriyle doldurulur.
  const yakin = new Int32Array(N).fill(-1), kuyruk = new Int32Array(N); let bas=0, son=0;
  for(let i=0;i<N;i++) if(land[i]){ yakin[i]=i; kuyruk[son++]=i; }
  while(bas<son){ const i=kuyruk[bas++], x=i%W, y=(i/W)|0;
    if(x>0 && yakin[i-1]<0){ yakin[i-1]=yakin[i]; kuyruk[son++]=i-1; }
    if(x<W-1 && yakin[i+1]<0){ yakin[i+1]=yakin[i]; kuyruk[son++]=i+1; }
    if(y>0 && yakin[i-W]<0){ yakin[i-W]=yakin[i]; kuyruk[son++]=i-W; }
    if(y<H-1 && yakin[i+W]<0){ yakin[i+W]=yakin[i]; kuyruk[son++]=i+W; } }

  const enlem = y => R.bounds[3] - (y+0.5)*(R.bounds[3]-R.bounds[1])/H;
  const agirlik = new Float32Array(H); for(let y=0;y<H;y++) agirlik[y] = Math.cos(enlem(y)*Math.PI/180);

  // ortak olcek havuzlari (yalniz kara): 12 ay + yillik sicaklik birlikte,
  // 12 aylik yagis birlikte, yillik yagis kendi basina (mm/yil ile mm/ay
  // ayni aralikta olamaz)
  // Havuz, bayt KODLARINDAN sayilarak kurulur: her kodlamada en fazla 256
  // deger var. Once 650 bin Float32 deger siralaniyordu (orta sinif telefonda
  // ~yarim saniye) ve Float32'ye yuvarlanan havuz tam hassas sorguyla
  // karsilastirildigi icin esit degerler "ortadan" degil bir yandan
  // sayilabiliyordu (gece denetimi). parcalar: [kodlama, kod dizisi] ciftleri.
  const havuz = parcalar => { const say = new Map(); let t = 0;
    for(const [enc, kodlar] of parcalar){ const h = new Float64Array(256);
      for(let j=0;j<kodlar.length;j++) h[kodlar[j]]++;
      for(let b=0;b<256;b++) if(h[b]){ const v = kodCoz(enc, b); say.set(v, (say.get(v)||0) + h[b]); t += h[b]; } }
    const vals = Float64Array.from(say.keys()).sort(), cum = new Float64Array(vals.length + 1);
    for(let i=0;i<vals.length;i++) cum[i+1] = cum[i] + say.get(vals[i]);
    return {n: t, vals, cum}; };
  const karaKod = f => { const a = new Uint8Array(n); for(let i=0;i<N;i++) if(land[i]) a[karaSira[i]] = f.a[i]; return a; };
  const ayDegerleri = (enc, ham) => { const o=[]; for(let m=0;m<12;m++){ const a=new Float32Array(n);
      for(let j=0;j<n;j++) a[j]=kodCoz(enc, ham[m*n+j]); o.push(a); } return o; };
  const tAy = ayDegerleri(Tk, Tm), pAy = ayDegerleri(Pk, Pm);
  const karaDeger = f => { const a=new Float32Array(n); for(let i=0;i<N;i++) if(land[i]) a[karaSira[i]]=kodCoz(f, f.a[i]); return a; };
  const tYil = karaDeger(tyil), pYil = karaDeger(pyil);

  return { kar: null, J, R, W, H, N, B:R.bounds, land, kop, tyil, pyil, elev, karaSira, n, Tk, Pk, Tm, Pm, tAy, pAy, tYil, pYil,
    dol: null, akintilar: R.akintilar || [],
    yakin, agirlik, enlem,
    havuzT: havuz([[Tk, Tm], [tyil, karaKod(tyil)]]), havuzP: havuz([[Pk, Pm]]), havuzPY: havuz([[pyil, karaKod(pyil)]]),
    doku: R.doku, KCODE: J.data.koppen_code, KNAME: J.data.koppen_names };
}

/* Dolasim: uret.py dolasim.png'si (12 ay alt alta; R,G = ruzgar u,v; B = deniz
   yuzeyi sicakligi) kaba bir gridde. Buradan m/s ve C olarak acilir; "yil"
   (-1) 12 ayin ortalamasi. */
function dolasimHazirla(D, resim){
  const k = D.R.dolasim; if(!k || !resim) return null;
  const cv = document.createElement("canvas"); cv.width = k.w; cv.height = k.h*12;
  const c = cv.getContext("2d"); c.drawImage(resim, 0, 0);
  const px = c.getImageData(0, 0, k.w, k.h*12).data, n = k.w*k.h;
  const ay = (kanal, f) => { const o = []; for(let m=0;m<13;m++) o.push(new Float32Array(n));
    for(let m=0;m<12;m++) for(let j=0;j<n;j++){ const v = f(px[(m*n + j)*4 + kanal]); o[m][j] = v; o[12][j] += v/12; }
    return o; };
  const ruz = b => (b-128)/127*k.ruzgar_ust, sic = b => k.sst_lo + (b-1)/254*(k.sst_hi-k.sst_lo);
  const u = ay(0, ruz), v = ay(1, ruz);
  // hiz: aylik vektorlerin buyuklugu (yillik: 12 ayin hizlarinin ortalamasi,
  // ortalama vektorun boyu degil; zit mevsimler birbirini silmesin)
  const hiz = []; for(let m=0;m<13;m++) hiz.push(new Float32Array(n));
  for(let m=0;m<12;m++) for(let j=0;j<n;j++){ const h = Math.hypot(u[m][j], v[m][j]); hiz[m][j] = h; hiz[12][j] += h/12; }
  let hizUst = 0; for(let m=0;m<12;m++) for(let j=0;j<n;j++) hizUst = Math.max(hizUst, hiz[m][j]);
  return {...k, u, v, hiz, hizUst: Math.ceil(hizUst), sst: ay(2, sic)};
}
// kaba griddeki alani ince hucre koordinatinda (x, y: hucre birimi) cift dogrusal oku
function dolOrnek(D, a, x, y){
  const k = D.dol, f = k.blok, gx = Math.max(0, Math.min(k.w-1.001, (x+0.5)/f - 0.5)),
        gy = Math.max(0, Math.min(k.h-1.001, (y+0.5)/f - 0.5)), x0 = gx|0, y0 = gy|0, fx = gx-x0, fy = gy-y0, i = y0*k.w + x0;
  return (a[i]*(1-fx) + a[i+1]*fx)*(1-fy) + (a[i+k.w]*(1-fx) + a[i+k.w+1]*fx)*fy;
}
/* Su: data/su.json (su/disa.py). Koordinatlar 0.01° tamsayı, fark kodlu;
   debi 10·log10(Q). Kol kademesi 1 (büyük ana kollar) .. 4 (küçük dereler). */
function suHazirla(S){
  if(!S || !S.nehirler) return null;
  const coz = kod => { const n = kod.length/2, a = new Float32Array(kod.length); let x = 0, y = 0;
    for(let i=0;i<n;i++){ x += kod[2*i]; y += kod[2*i+1]; a[2*i] = x/100; a[2*i+1] = y/100; } return a; };
  const kutu = a => { let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;
    for(let i=0;i<a.length;i+=2){ x0=Math.min(x0,a[i]); x1=Math.max(x1,a[i]); y0=Math.min(y0,a[i+1]); y1=Math.max(y1,a[i+1]); }
    return [x0,y0,x1,y1]; };
  // Egriler bir kez, boylam/enlem uzayinda Path2D olarak kurulur; her karede
  // yalniz donusumle cizilir (her karede kurmak "butun kollar"da kaydirmayi
  // telefonda kare basina ~250 ms yavaslatiyordu, CPU x4 olcumu). Kol,
  // taban kalinligi ayni kalan parcalara bolunur (kalinlik debiyle artar).
  // kalinlik debinin logaritmasiyla: kaynak ~0.5 px, 20.000 m3/s ~2.2 px
  const tabanK = q => Math.max(0.5, 0.3 + 0.62*Math.log10(Math.max(q, 50)/50));
  const nehirler = S.nehirler.map(n => { const p = coz(n.p), m = p.length/2;
    const q = Float32Array.from(n.q, v => Math.pow(10, v/10)), parcalar = [];
    const x = i => p[2*i], y = i => p[2*i+1];
    let yol = null, gen = -1;
    for(let i=0;i<m-1;i++){ const g = Math.round(tabanK(q[Math.min(i+1, m-1)])*4)/4;
      if(g !== gen){ yol = new Path2D(); yol.moveTo(x(i), y(i)); gen = g; parcalar.push([g, yol]); }
      const i0 = Math.max(0, i-1), i3 = Math.min(m-1, i+2);
      yol.bezierCurveTo(x(i) + (x(i+1)-x(i0))/6, y(i) + (y(i+1)-y(i0))/6,
        x(i+1) - (x(i3)-x(i))/6, y(i+1) - (y(i3)-y(i))/6, x(i+1), y(i+1)); }
    return {k:n.k, p, q, parcalar, kutu:kutu(p), Q:n.Q, L:n.L}; });
  // kalın kollar üstte kalsın: önce küçük kademeler çizilir
  nehirler.sort((a, b) => b.k - a.k || a.Q - b.Q);
  const golYolu = a => { const n = a.length/2, yol = new Path2D();
    yol.moveTo((a[0]+a[2*(n-1)])/2, (a[1]+a[2*(n-1)+1])/2);
    for(let i=0;i<n;i++){ const j = (i+1)%n; yol.quadraticCurveTo(a[2*i], a[2*i+1], (a[2*i]+a[2*j])/2, (a[2*i+1]+a[2*j+1])/2); }
    yol.closePath(); return yol; };
  const goller = S.goller.map(g => { const c = g.c.map(coz), yol = new Path2D();
    for(const a of c) yol.addPath(golYolu(a));
    return {...g, c, yol, kutu: kutu(Float32Array.from(c.flatMap(a => [...a])))}; });
  // deltalar: ağızda yelpaze gibi açılan kollar (su/delta.py). Kademe:
  // nehir baskın 1, yay biçimli 2, küçük 3 (ana kollarla aynı seyreltme)
  const deltalar = (S.deltalar || []).map(d => { const c = d.c.map(coz);
    const yollar = c.map(p => { const m = p.length/2, yol = new Path2D(), x = i => p[2*i], y = i => p[2*i+1];
      yol.moveTo(x(0), y(0));
      for(let i=0;i<m-1;i++){ const i0 = Math.max(0, i-1), i3 = Math.min(m-1, i+2);
        yol.bezierCurveTo(x(i) + (x(i+1)-x(i0))/6, y(i) + (y(i+1)-y(i0))/6, x(i+1) - (x(i3)-x(i))/6, y(i+1) - (y(i3)-y(i))/6, x(i+1), y(i+1)); }
      return yol; });
    const k = /^nehir/.test(d.tur) ? 1 : /^yay/.test(d.tur) ? 2 : 3;
    return {...d, k, yollar, g: tabanK(d.q / Math.pow(c.length, 0.8)), kutu: kutu(Float32Array.from(c.flatMap(a => [...a])))}; });
  return {nehirler, goller, deltalar};
}

/* Tektonik: data/tektonik.json ve data/levha.png (tektonik/uygulama.py).
   Sınırlar ve volkan kuşakları 0.01° fark kodlu; levha.png harita kutusuna
   kırpılmış levha kimliği (gri ton = kimlik). */
const LEVHA_RENK = {1:[201,166,107], 2:[217,140,95], 3:[181,138,216], 4:[224,192,96], 5:[111,179,160], 6:[224,122,138],
  7:[143,191,90], 8:[91,143,214], 9:[79,176,198], 10:[122,127,208], 11:[76,120,168], 12:[154,184,200], 13:[138,160,184]};
function tektHazirla(T, im){
  if(!T || !im) return null;
  const coz = kod => { const n = kod.length/2, a = new Float32Array(kod.length); let x = 0, y = 0;
    for(let i=0;i<n;i++){ x += kod[2*i]; y += kod[2*i+1]; a[2*i] = x/100; a[2*i+1] = y/100; } return a; };
  const kutu = a => { let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;
    for(let i=0;i<a.length;i+=2){ x0=Math.min(x0,a[i]); x1=Math.max(x1,a[i]); y0=Math.min(y0,a[i+1]); y1=Math.max(y1,a[i+1]); }
    return [x0,y0,x1,y1]; };
  const yolKur = (a, kapat) => { const y = new Path2D(); y.moveTo(a[0], a[1]);
    for(let i=2;i<a.length;i+=2) y.lineTo(a[i], a[i+1]); if(kapat) y.closePath(); return y; };
  const sinirlar = T.sinirlar.map(s => { const p = coz(s.p); return {...s, p, yol: yolKur(p), kutu: kutu(p)}; });
  const kusaklar = T.kusaklar.map(k => { const on = coz(k.on), arka = coz(k.arka), n = on.length/2;
    // kuşak alanı: cephe boyunca git, arka çizgiden geri dön
    const alan = new Float32Array(on.length*2); alan.set(on);
    for(let i=0;i<n;i++){ alan[on.length + 2*i] = arka[2*(n-1-i)]; alan[on.length + 2*i+1] = arka[2*(n-1-i)+1]; }
    return {...k, on, alanYol: yolKur(alan, true), onYol: yolKur(on), kutu: kutu(alan)}; });
  const yariklar = T.yariklar.map(r => { const p = coz(r.p); return {...r, p, kutu: kutu(p)}; });
  // levha kimliği ve boyalı levha tuvali (bir kez)
  const w = im.naturalWidth, h = im.naturalHeight, cv = document.createElement("canvas");
  cv.width = w; cv.height = h; const c = cv.getContext("2d", {willReadFrequently:true}); c.drawImage(im, 0, 0);
  const px = c.getImageData(0, 0, w, h), kim = new Uint8Array(w*h);
  for(let i=0;i<w*h;i++){ const k = px.data[4*i]; kim[i] = k;
    const r = LEVHA_RENK[k]; if(r){ px.data[4*i] = r[0]; px.data[4*i+1] = r[1]; px.data[4*i+2] = r[2]; px.data[4*i+3] = 255; } else px.data[4*i+3] = 0; }
  c.putImageData(px, 0, 0);
  const K = T.kesit;
  const levhaAt = (lon, lat) => { const x = Math.floor((lon-K[0])/(K[2]-K[0])*w), y = Math.floor((K[3]-lat)/(K[3]-K[1])*h);
    return x < 0 || y < 0 || x >= w || y >= h ? 0 : kim[y*w + x]; };
  return {levhalar: T.levhalar, siniflar: T.siniflar, sinirlar, kusaklar, yariklar, tuval: cv, kesit: K, levhaAt};
}

const PUSULA = ["kuzeyden","kuzeydoğudan","doğudan","güneydoğudan","güneyden","güneybatıdan","batıdan","kuzeybatıdan"];
// ruzgar geldigi yonle adlandirilir: akis guneye ise "kuzeyden"
const nereden = (u, v) => PUSULA[Math.round(((Math.atan2(-u, -v)*180/Math.PI) + 360) % 360 / 45) % 8];
const YONE = ["kuzeye","kuzeydoğuya","doğuya","güneydoğuya","güneye","güneybatıya","batıya","kuzeybatıya"];
// Beaufort olcegi (m/s alt sinirlari, WMO)
const BFT = [0.5, 1.6, 3.4, 5.5, 8.0, 10.8, 13.9, 17.2, 20.8, 24.5, 28.5, 32.7];
const beaufort = v => BFT.filter(e => v >= e).length;
const BFT_AD = ["sakin","esinti","hafif rüzgâr","tatlı rüzgâr","mutedil rüzgâr","sert rüzgâr","kuvvetli","fırtınamsı","fırtına","kuvvetli fırtına","tam fırtına","şiddetli fırtına","kasırga"];
// isaretli aylari ardisik araliklar olarak yaz ("Ara–Şub, Tem"), yil sonundan basa sarar
function aySirasi(b){ if(b.every(Boolean)) return "yıl boyu";
  let bas = b.findIndex(v => !v); const ara = [];
  for(let k=1;k<=12;k++){ const j = (bas+k)%12; if(b[j] && !b[(j+11)%12]) ara.push([j, j]); else if(b[j]) ara[ara.length-1][1] = j; }
  return ara.map(([a, z]) => a===z ? AYLAR[a] : `${AYLAR[a]}–${AYLAR[z]}`).join(", "); }

// yuzdelik: havuzdaki orta sira (esit degerler ortadan)
function yuzdelik(h, x){ if(!h.n) return 0.5; const v = h.vals;
  let a=0,b=v.length; while(a<b){ const m=(a+b)>>1; if(v[m]<x) a=m+1; else b=m; } const alt=h.cum[a];
  b=v.length; while(a<b){ const m=(a+b)>>1; if(v[m]<=x) a=m+1; else b=m; }
  return (alt+h.cum[a])/2/h.n; }
// kantil: sirasi round(q*(n-1)) olan deger (lejant etiketleri)
function kantil(h, q){ const r = Math.round(q*(h.n-1)); let a=0, b=h.vals.length-1;
  while(a<b){ const m=(a+b)>>1; if(h.cum[m+1] > r) b=m; else a=m+1; } return h.vals[a]; }

/* Kar: motor kar hesaplamaz; burada aylik ortalama sicaklik ve yagistan
   turetilir (aylik su dengesi modellerindeki kar kovasi). Yagisin kar payi
   KAR_ALT'ta 1, KAR_UST'te 0, arada dogrusal (aylik ORTALAMA sicaklik: +2
   derecelik bir ayda da karli gunler olur). Erime derece-gun: ayda
   ERIME mm su esdegeri / derece. Denge icin uc yil dondurulur. Sonuc su
   esdegeri mm; ORTU_ESIK (~3-5 cm kar) ay ortasinda asilirsa "ortu var". */
const KAR_ALT = -2, KAR_UST = 4, ERIME = 75, ORTU_ESIK = 10, YAGAR_ESIK = 5;
function karHesapla(tAy, pAy, n){
  const swe = [], kar = [];   // ay ortasi kar ortusu, ayda yagan kar (mm su)
  for(let m=0;m<12;m++){ swe.push(new Float32Array(n)); kar.push(new Float32Array(n)); }
  // kalici: kar hic erimiyor, yildan yila birikiyor (buzul). Orada kalinlik
  // yalniz dondurulen yil sayisina bagli, anlamsiz; kart "kalici" yazar.
  const ortu = new Uint8Array(n), yagar = new Uint16Array(n), ortuAy = new Uint16Array(n), kalici = new Uint8Array(n);
  for(let j=0;j<n;j++){ let s = 0, gecen = 0;
    for(let tur=0;tur<3;tur++){ for(let m=0;m<12;m++){ const T = tAy[m][j];
      const k = pAy[m][j]*Math.max(0, Math.min(1, (KAR_UST-T)/(KAR_UST-KAR_ALT)));
      const bas = s, M = ERIME*Math.max(0, T); s += k; s -= Math.min(s, M);
      // Ay ortasi: ay icinde yagis ve erime dogrusal. Once (bas+son)/2
      // aliniyordu; kar ayin basinda eriyip bitse de (son=0) bas buyukse ay
      // "ortulu" sayiliyordu: Moskova normallerinde 6 ay (gercekte ~4.5),
      // Nisan ortasinda 109 mm. Simdi Moskova 5 ay (gece denetimi).
      if(tur===2){ kar[m][j] = k; swe[m][j] = Math.max(0, bas + (k - M)/2); } }
      if(tur===1) gecen = s; }
    if(s > gecen + 1) kalici[j] = 1;
    for(let m=0;m<12;m++){
      if(swe[m][j] >= ORTU_ESIK){ ortu[j]++; ortuAy[j] |= 1<<m; }
      if(kar[m][j] >= YAGAR_ESIK) yagar[j] |= 1<<m; } }
  return {swe, kar, ortu, yagar, ortuAy, kalici};
}
// Kar alani ilk ihtiyacta kurulur. Acilista hesaplamak orta sinif telefonda
// (CPU 4 kat yavas) ~360 ms ekliyordu ve ilk ekran kar gostermiyor; baslat
// ilk kareden sonra bos zamanda cagirir, sekme ya da kart daha once isterse
// o an hesaplanir (gece denetimi).
function karAl(D){ return D.kar || (D.kar = karHesapla(D.tAy, D.pAy, D.n)); }
/* Gunluk sicaklik: gunduz (ortalama gunluk en yuksek), gece (ortalama gunluk
   en dusuk), ayin tipik tepesi ve dibi (her yil o ay gorulen en yuksek/en
   dusuk) ve ~30 yilda bir rekor. Motor yalniz aylik ortalama verir; bunlar
   ondan istatistiksel olarak turetilir (kar gibi, veri dosyasina girmez).
   Katsayilar 209 ABD istasyonunun 1991-2019 gunluk verisinden (CMU/GHCN-D)
   en kucuk karelerle; istasyon disarida birakilarak olculen hata: gunduz-gece
   farki 1.9, tepe 1.7, dip 1.35, rekor ~2 C. Girdiler motorun bildigi
   seyler: aylik yagis (kuru hava gece hizli sogur), yukseklik, kiyiya
   uzaklik, ayin gunes isinimi (gezegenin eksen egikligi ve yilindan), yillik
   sicaklik genligi (karasallik) ve ayin yillik ortalamadan sapmasi.
   Gezegenin gunu Dunya'dan farkliysa gunduz-gece farki sqrt(gun/24) ile
   olceklenir: yuzey sicakliginin gunluk salinimi donemin karekokuyle buyur
   (isinin toprakta yayilmasi). Dunyam'da 15 saat: fark %21 kucuk. Kalibrasyon
   ABD'nin 25-48K araligindan; tropikte ve cok yuksekte kaba bir tahmindir. */
/* Deniz dokusu (yalniz gorunus): okyanus hucrelerinde en yakin karaya
   uzaklik, iki gecisli pah (chamfer) donusumu, dogu-bati adimi cos(enlem)
   ile. 0..255 = 1 - exp(-km/700); kara 0. */
function denizUzak(D){
  const {W, H, N, B, land} = D, km = (B[3]-B[1])/H * (D.J.data.radius_km || 6371) * Math.PI/180;
  const d = new Float32Array(N).fill(1e9);
  for(let i=0;i<N;i++) if(land[i]) d[i] = 0;
  const cx = y => Math.max(0.05, Math.cos(D.enlem(y)*Math.PI/180));
  for(let y=0;y<H;y++){ const ax = cx(y), ac = Math.hypot(ax, 1);
    for(let x=0;x<W;x++){ const i = y*W+x; let v = d[i];
      if(x>0) v = Math.min(v, d[i-1]+ax);
      if(y>0){ v = Math.min(v, d[i-W]+1); if(x>0) v = Math.min(v, d[i-W-1]+ac); if(x<W-1) v = Math.min(v, d[i-W+1]+ac); }
      d[i] = v; } }
  for(let y=H-1;y>=0;y--){ const ax = cx(y), ac = Math.hypot(ax, 1);
    for(let x=W-1;x>=0;x--){ const i = y*W+x; let v = d[i];
      if(x<W-1) v = Math.min(v, d[i+1]+ax);
      if(y<H-1){ v = Math.min(v, d[i+W]+1); if(x<W-1) v = Math.min(v, d[i+W+1]+ac); if(x>0) v = Math.min(v, d[i+W-1]+ac); }
      d[i] = v; } }
  const o = new Uint8Array(N);
  for(let i=0;i<N;i++) o[i] = Math.round(255*(1 - Math.exp(-d[i]*km/700)));
  return o;
}

const GS = {dtr: [11.942, -1.117, 2.417, 1.071, 0.833], ehi: [0.848, 0.292, -0.246, -0.207, 0.228],
  elo: [2.832, 0.195, -0.198, 0.622, 0.015], rekS: [2.12, 0.34], rekC: [0.09, 0.73]};
function gunlukHazirla(D){
  const g = D.J.data.gezegen; if(!g) return null;
  const {W, H, N, n, land, karaSira, elev, tAy, pAy, B} = D;
  // kiyiya uzaklik (km): okyanustan kara hucrelerine 4 komsulu BFS
  const adim = (B[2]-B[0])/W * (D.J.data.radius_km || 6371) * Math.PI/180;
  const uz = new Float32Array(N).fill(-1), q = new Int32Array(N); let bas = 0, son = 0;
  for(let i=0;i<N;i++) if(!land[i]){ uz[i] = 0; q[son++] = i; }
  while(bas < son){ const i = q[bas++], x = i%W;
    for(const k of [x>0 ? i-1 : -1, x<W-1 ? i+1 : -1, i-W, i+W]) if(k >= 0 && k < N && uz[k] < 0){ uz[k] = uz[i] + 1; q[son++] = k; } }
  // ayin ortasinda gunluk ortalama atmosfer ustu gunes isinimi (W/m2), satir basina
  const Q = new Float32Array(H*12), egik = g.eksen_deg*Math.PI/180;
  for(let y=0;y<H;y++){ const f = D.enlem(y)*Math.PI/180;
    for(let m=0;m<12;m++){ const dec = egik*Math.sin(2*Math.PI*((m+0.5)*g.yil_gun/12 - g.ekinoks_gun)/g.yil_gun);
      const h0 = Math.acos(Math.max(-1, Math.min(1, -Math.tan(f)*Math.tan(dec))));
      Q[y*12+m] = 1361/Math.PI*(h0*Math.sin(f)*Math.sin(dec) + Math.cos(f)*Math.cos(dec)*Math.sin(h0)); } }
  const kk = new Float32Array(n), z = new Float32Array(n), A = new Float32Array(n), Tm = new Float32Array(n), satir = new Int32Array(n);
  for(let i=0;i<N;i++){ if(!land[i]) continue; const j = karaSira[i];
    kk[j] = 1 - Math.exp(-uz[i]*adim/150); z[j] = Math.max(0, elev[i])/1000; satir[j] = (i/W)|0;
    let lo = 1e9, hi = -1e9, t = 0; for(let m=0;m<12;m++){ const v = tAy[m][j]; lo = Math.min(lo, v); hi = Math.max(hi, v); t += v/12; }
    A[j] = hi - lo; Tm[j] = t; }
  const don = Math.sqrt(g.gun_saat/24), c = (v, a, b) => Math.max(a, Math.min(b, v));
  // j hucresi, m ayi: {gunduz, gece, tepe, dip, rekS, rekC}
  function ay(j, m){ const T = tAy[m][j], q2 = Q[satir[j]*12+m]/100, dT = T - Tm[j], k = GS;
    const dtr = c(k.dtr[0] + k.dtr[1]*Math.log(pAy[m][j]+5) + k.dtr[2]*z[j] + k.dtr[3]*kk[j] + k.dtr[4]*q2, 3, 22)*don;
    const ehi = c(k.ehi[0] + k.ehi[1]*A[j] + k.ehi[2]*dT + k.ehi[3]*kk[j] + k.ehi[4]*q2, 1, 14);
    const elo = c(k.elo[0] + k.elo[1]*A[j] + k.elo[2]*dT + k.elo[3]*kk[j] + k.elo[4]*q2, 1, 20);
    const gunduz = T + dtr/2, gece = T - dtr/2, tepe = gunduz + ehi, dip = gece - elo;
    return {gunduz, gece, tepe, dip, rekS: tepe + k.rekS[0] + k.rekS[1]*ehi, rekC: dip - k.rekC[0] - k.rekC[1]*elo}; }
  return {ay, don};
}
function gunlukAl(D){ return D.gunluk !== undefined ? D.gunluk : (D.gunluk = gunlukHazirla(D)); }
// ay maskesinden "Kasım–Mart" gibi bir aralik (yil donumunu asan dahil)
function ayAraligi(mask){
  if(!mask) return null; if(mask === 0xfff) return "bütün yıl";
  const var_ = m => (mask >> ((m+12)%12)) & 1, par = [];
  for(let m=0;m<12;m++) if(var_(m) && !var_(m-1)){ let e = m; while(var_(e+1)) e++; par.push([m, e%12, e-m+1]); }
  par.sort((a,b)=>b[2]-a[2]);
  return par.map(([a,b,u]) => u===1 ? AYLAR[a] : AYLAR[a]+"–"+AYLAR[b]).join(", ");
}

/* Gosterilen alan: tam grid bayt dizisi + 256'lik renk tablosu + lejant. */
function gorunumKur(D, katman, donem, bant){
  const {N, yakin, karaSira, n} = D, a = new Uint8Array(N), lut = new Uint8Array(256*3);
  if(katman==="dolasim"){
    // deniz yuzeyi sicakligi; ince gride aradegerlenir, renk dogrusal
    // zemin: deniz yuzeyi sicakligi (yalniz okyanus) ya da ruzgar hizi (her yer)
    const k = D.dol, m = donem<0 ? 12 : donem, hizZ = ayar.dolZemin==="hiz";
    const alanD = hizZ ? k.hiz[m] : k.sst[m], lo = hizZ ? 0 : k.sst_lo, hi = hizZ ? k.hizUst : k.sst_hi, dur = RAMPA[hizZ ? "ruzgar" : "sicaklik"];
    for(let i=0;i<N;i++) a[i] = Math.round(Math.max(0, Math.min(1, (dolOrnek(D, alanD, i%D.W, (i/D.W)|0)-lo)/(hi-lo)))*255);
    for(let b=0;b<256;b++) lut.set(rampa(dur, b/255).map(v=>(v*0.82)|0), b*3);
    const adim = [lo, lo+(hi-lo)/4, lo+(hi-lo)/2, lo+(hi-lo)*3/4, hi];
    return {a, lut, olcek:{serit: cssRampa(dur), birim: hizZ ? "m/s" : "°C",
      etiket: adim.map((v,k2)=>({x:k2/4, t:eksi(Math.round(v))}))}};
  }
  if(katman==="kar"){
    // yil: kar ortusunun kac ay yerde kaldigi; ay: o ayin ortasinda yerdeki
    // kar (mm su esdegeri, kok olcek). Karsiz kara notr gri.
    const K = karAl(D), yil = donem<0, UST = 300;
    for(let i=0;i<N;i++){ const j = karaSira[yakin[i]];
      a[i] = yil ? Math.round(K.ortu[j]/12*255) : Math.round(Math.sqrt(Math.min(1, K.swe[donem][j]/UST))*255); }
    const esik = yil ? 255/24 : Math.sqrt(ORTU_ESIK/UST)*255;
    for(let b=0;b<256;b++) lut.set(b < esik ? [94,92,86] : rampa(RAMPA.kar, b/255).map(v=>v|0), b*3);
    const etiket = yil ? [0,3,6,9,12].map(m=>({x:m/12, t:String(m)}))
      : [0,10,50,150,300].map(v=>({x:Math.sqrt(v/UST), t:String(v)}));
    return {a, lut, olcek:{serit:`linear-gradient(90deg,#5e5c56 0% ${(esik/2.55).toFixed(1)}%,${RAMPA.kar.join(",")})`,
      birim: yil ? "ay örtü" : "mm su", etiket}};
  }
  if(katman==="arazi"){
    const ust = D.doku.yukseklik_ust;
    for(let i=0;i<N;i++){ const e=D.elev[yakin[i]]; a[i] = Math.round(Math.sqrt(Math.max(e,0)/ust)*255); }
    for(let b=0;b<256;b++){ const c=araziRenk((b/255)**2*ust); lut.set(c.map(v=>v|0), b*3); }
    const etiket=[0,500,1500,3000,6000].filter(m=>m<=ust*1.02);
    return {a, lut, olcek:{serit:`linear-gradient(90deg,${Array.from({length:24},(_,k)=>css(araziRenk((k/23)**2*ust))).join(",")})`,
      etiket: etiket.map(m=>({x:Math.sqrt(m/ust), t:m.toLocaleString("tr-TR")})), birim:"m"}};
  }
  if(katman==="sicaklik" && ayar.sicMod && ayar.sicMod!=="ort" && gunlukAl(D)) return gunlukGorunum(D, donem, bant, a, lut);
  const sic = katman==="sicaklik";
  const enc = donem<0 ? (sic ? D.tyil : D.pyil) : (sic ? D.Tk : D.Pk);
  const ham = donem<0 ? null : (sic ? D.Tm : D.Pm);
  for(let i=0;i<N;i++){ const j=yakin[i]; a[i] = ham ? ham[donem*n + karaSira[j]] : enc.a[j]; }
  const hv = sic ? D.havuzT : (donem<0 ? D.havuzPY : D.havuzP);
  const dur = RAMPA[sic ? "sicaklik" : "yagis"], BANT = 6;
  for(let b=1;b<256;b++){ let q=yuzdelik(hv, kodCoz(enc, b));
    if(bant) q = Math.min(BANT-1, Math.floor(q*BANT))/(BANT-1);
    lut.set(rampa(dur, q).map(v=>v|0), b*3); }
  lut.set(lut.slice(3,6), 0);
  const birim = sic ? "°C" : (donem<0 ? "mm/yıl" : "mm");
  const fmt = v => eksi((Math.abs(v)>=100 ? Math.round(v) : Math.round(v*10)/10).toLocaleString("tr-TR"));
  const serit = bant
    ? `linear-gradient(90deg,${Array.from({length:BANT},(_,k)=>{ const c=css(rampa(dur,k/(BANT-1))); return `${c} ${(k/BANT*100).toFixed(2)}% ${((k+1)/BANT*100).toFixed(2)}%`; }).join(",")})`
    : cssRampa(dur);
  return {a, lut, olcek:{serit, birim,
    // bantliyken etiketler bant sinirlarinda; ceyreklikler bantlarin ortasina
    // dusuyor ve hangi degerin bandi boldugu okunmuyordu (gece denetimi)
    etiket:(bant ? Array.from({length:BANT+1}, (_,k)=>k/BANT) : [0,.25,.5,.75,1]).map(q=>({x:q, t:fmt(kantil(hv, q))}))}};
}

// Sicaklik sekmesinde gunduz / gece / tepe / dip. Yillikta gunduz ve gece 12
// ayin ortalamasi; tepe yilin en sicak ayinin tepesi, dip en soguk ayin dibi.
// Renk olcegi ortalama katmaniyla ayni mantik: bu alanin 12 ayindaki dagilima
// gore esit alanli (yuzdelik) rampa, ay degisince renkler karsilastirilabilir.
const SIC_MOD = {gunduz: "gündüz", gece: "gece", tepe: "ayın tipik tepesi", dip: "ayın tipik dibi"};
function gunlukGorunum(D, donem, bant, a, lut){
  const G = gunlukAl(D), mod = ayar.sicMod, {n, N, yakin, karaSira} = D;
  const hv = D.gunlukHavuz || (D.gunlukHavuz = {});
  if(!hv[mod]){ const ay = [], yl = new Float32Array(n); let lo = 1e9, hi = -1e9;
    for(let m=0;m<12;m++){ const f = new Float32Array(n); for(let j=0;j<n;j++){ const v = G.ay(j, m)[mod]; f[j] = v; lo = Math.min(lo, v); hi = Math.max(hi, v); } ay.push(f); }
    for(let j=0;j<n;j++){ let t = mod==="tepe" ? -1e9 : mod==="dip" ? 1e9 : 0;
      for(let m=0;m<12;m++){ const v = ay[m][j]; t = mod==="tepe" ? Math.max(t, v) : mod==="dip" ? Math.min(t, v) : t + v/12; } yl[j] = t; }
    const enc = {lo, hi, kok: false}, kod = v => 1 + Math.round((v-lo)/(hi-lo||1)*254), say = new Float64Array(256);
    for(const f of ay) for(let j=0;j<n;j++) say[kod(f[j])]++;
    const vals = [], cum = [0]; let t = 0; for(let b=1;b<256;b++) if(say[b]){ vals.push(kodCoz(enc, b)); t += say[b]; cum.push(t); }
    hv[mod] = {ay, yl, enc, kod, havuz: {n: t, vals: Float64Array.from(vals), cum: Float64Array.from(cum)}}; }
  const h = hv[mod], f = donem<0 ? h.yl : h.ay[donem], dur = RAMPA.sicaklik, BANT = 6;
  for(let i=0;i<N;i++) a[i] = h.kod(f[karaSira[yakin[i]]]);
  for(let b=1;b<256;b++){ let q = yuzdelik(h.havuz, kodCoz(h.enc, b)); if(bant) q = Math.min(BANT-1, Math.floor(q*BANT))/(BANT-1);
    lut.set(rampa(dur, q).map(v=>v|0), b*3); }
  lut.set(lut.slice(3,6), 0);
  const fmt = v => eksi(Math.round(v));
  const serit = bant ? `linear-gradient(90deg,${Array.from({length:BANT},(_,k)=>{ const c=css(rampa(dur,k/(BANT-1))); return `${c} ${(k/BANT*100).toFixed(2)}% ${((k+1)/BANT*100).toFixed(2)}%`; }).join(",")})` : cssRampa(dur);
  return {a, lut, olcek:{serit, birim: "°C", etiket:(bant ? Array.from({length:BANT+1}, (_,k)=>k/BANT) : [0,.25,.5,.75,1]).map(q=>({x:q, t:fmt(kantil(h.havuz, q))}))}};
}

/* ================================================================ cizim */
const VS = `attribute vec2 p; void main(){ gl_Position = vec4(p, 0.0, 1.0); }`;
const vec3s = h => hex(h).map(v=>(v/255).toFixed(4)).join(",");
const FS = `
precision highp float;
uniform vec2 uRes; uniform float uDpr; uniform vec3 uView; uniform vec2 uGrid; uniform vec4 uBounds;
uniform sampler2D tAlan, tLut, tKop, tPal, tDoku, tDokuN, tYuk, tKab;
uniform int uMod; uniform float uPiksel, uKabartma, uIzgara, uIzole, uOlcek, uZemin, uDeniz;
const vec3 DERIN = vec3(${vec3s(OKYANUS_DERIN)});
const vec3 KIYI = vec3(${vec3s(OKYANUS_KIYI)});
// deniz dokusu (yalniz gorunus, veri degil): kiyiya uzakliktan sig/derin
// tonu, esderinlik cizgileri, kiyi kopugu, enleme gore hafif ton ve durgun
// su grenli. Derinlik gercek batimetri degil, kiyiya uzakliktir.
float hs(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float gurultu(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.0 - 2.0*f);
  return mix(mix(hs(i), hs(i + vec2(1.0, 0.0)), f.x), mix(hs(i + vec2(0.0, 1.0)), hs(i + vec2(1.0, 1.0)), f.x), f.y); }
// kaba derinlik tKop alfasinda, en yakin ornekleme: elle cift dogrusal
float kabaDerin(vec2 uv){ vec2 p = uv * uGrid - 0.5, i = floor(p), f = p - i;
  float a = texture2D(tKop, (i + vec2(0.5, 0.5)) / uGrid).a, b = texture2D(tKop, (i + vec2(1.5, 0.5)) / uGrid).a;
  float c = texture2D(tKop, (i + vec2(0.5, 1.5)) / uGrid).a, d = texture2D(tKop, (i + vec2(1.5, 1.5)) / uGrid).a;
  return mix(mix(a, b, f.x), mix(c, d, f.x), f.y); }
// t: 0 kiyi .. 1 acik okyanus
float denizT(vec2 uv, vec2 derece){
  if(uv.x < 0.0 || uv.y < 0.0 || uv.x >= 1.0 || uv.y >= 1.0) return 1.0;
  // doku.png G = karekok(uzaklik/60 teksel): karesi dogrusal, ~450 km'de doyar
  float g = texture2D(tDoku, uv).g;
  // ince alan ~450 km'de doyar; doyma noktasinda kirilmasin diye egimi
  // sifira yumusakca iner (yoksa kiyiya paralel bir ton siniri gorunuyordu)
  float f = g * g; f = f * (2.0 - f);
  float t = 0.5 * f + 0.5 * kabaDerin(uv);
  // havzalar ve sirtlar: derinde buyuk olcekli dalgalanma
  float n = gurultu(derece / 9.0) - 0.5;
  return clamp(t + n * 0.16 * smoothstep(0.3, 0.9, t), 0.0, 1.0); }
vec3 deniz(float t, vec2 derece, float grad){
  vec3 sig = vec3(0.135, 0.300, 0.320), orta = vec3(0.060, 0.145, 0.185), derin = vec3(0.028, 0.058, 0.085);
  // sahanliktan derine tek surekli gecis (iki basamak degil): sig -> orta
  // genis bir aralikta, orta -> derin daha da genis, ikisi ust uste biner
  vec3 c = mix(sig, orta, smoothstep(0.0, 0.45, t));
  c = mix(c, derin, smoothstep(0.2, 1.0, t));
  // tropik sular biraz turkuaz, yuksek enlem griye
  float e = clamp(abs(derece.y) / 60.0, 0.0, 1.0);
  c = mix(c * vec3(0.90, 1.07, 1.05), c * vec3(1.03, 0.98, 0.95), e);
  // durgun su greni, +-%4
  float n = gurultu(derece * 1.3) * 0.5 + gurultu(derece * 5.1) * 0.5;
  c *= 0.96 + 0.08 * n;
  // esderinlik cizgileri, ekranda ~1 piksel
  if(grad > 1e-6){ float k = t * 6.0, d = abs(fract(k + 0.5) - 0.5) / (grad * 6.0);
    c += vec3(0.35, 0.50, 0.52) * 0.04 * (1.0 - smoothstep(0.3, 1.6, d)) * smoothstep(0.03, 0.12, t) * (1.0 - smoothstep(0.85, 0.98, t)); }
  // kiyi kopugu
  c += vec3(0.07, 0.12, 0.13) * (1.0 - smoothstep(0.0, 0.12, t));
  return c;
}
void main(){
  vec2 ekran = vec2(gl_FragCoord.x, uRes.y - gl_FragCoord.y) / uDpr;
  vec2 hucre = (ekran - uView.xy) / uView.z;
  vec2 uv = hucre / uGrid;
  vec2 muv = (floor(hucre) + 0.5) / uGrid;
  bool icinde = uv.x >= 0.0 && uv.y >= 0.0 && uv.x < 1.0 && uv.y < 1.0;
  vec4 dk = texture2D(tDoku, uv);
  vec3 renk = icinde ? mix(KIYI, DERIN, dk.g) : DERIN;
  if(uDeniz > 0.5){
    float dlon = (uBounds.z - uBounds.x) / uGrid.x, dlat = (uBounds.w - uBounds.y) / uGrid.y;
    vec2 derece = vec2(uBounds.x + hucre.x * dlon, uBounds.w - hucre.y * dlat);
    vec2 o = 1.0 / uView.z / uGrid, od = vec2(dlon, dlat) / uView.z;
    float t = denizT(uv, derece);
    float grad = length(vec2(denizT(uv + vec2(o.x, 0.0), derece + vec2(od.x, 0.0)) - t, denizT(uv + vec2(0.0, o.y), derece - vec2(0.0, od.y)) - t));
    renk = deniz(t, derece, grad);
  }
  if(uMod == 3 && icinde){   // dolasim: okyanus deniz yuzeyi sicakligiyla
    float sv = uPiksel > 0.5 ? texture2D(tAlan, muv).r : texture2D(tAlan, uv).r;
    // veri karanin ~22 derece otesinde biter; alan orada dikdortgen bir
    // kenarla kesiliyordu, son %4'te zemine karisir (gece denetimi)
    float kenar = smoothstep(0.0, 0.04, min(min(uv.x, 1.0 - uv.x), min(uv.y, 1.0 - uv.y)));
    renk = mix(DERIN, texture2D(tLut, vec2((sv * 255.0 + 0.5) / 256.0, 0.5)).rgb, kenar); }
  // kiyi kenarinin genisligi: ekranda ~1 piksel, yakinlik ne olursa olsun keskin
  float w = clamp(0.5 * uOlcek / uView.z, 0.015, 0.5);
  float a = 0.0, kod = 0.0;
  if(uPiksel > 0.5){ kod = texture2D(tKop, muv).r * 255.0; a = (icinde && kod > 0.5) ? 1.0 : 0.0; }
  else if(icinde){ a = smoothstep(0.5 - w, 0.5 + w, dk.r);
    kod = texture2D(tDokuN, uv).b * 255.0; if(kod < 0.5) kod = texture2D(tKop, muv).r * 255.0; }
  if(a > 0.0){
    vec3 c;
    if(uMod == 0){
      kod = floor(kod + 0.5);
      c = texture2D(tPal, vec2((kod + 0.5) / 32.0, 0.5)).rgb;
      if(uIzole > 0.5 && abs(kod - uIzole) > 0.5){ float g = dot(c, vec3(0.299, 0.587, 0.114));
        c = mix(vec3(g), vec3(0.13, 0.16, 0.18), 0.62); }
    } else if(uMod == 3){
      // dolasim: deniz sicakliginda kara notr (yalniz kabartma); ruzgar
      // hizinda alan karayi da kaplar
      if(uZemin > 0.5){ float hv = uPiksel > 0.5 ? texture2D(tAlan, muv).r : texture2D(tAlan, uv).r;
        c = texture2D(tLut, vec2((hv * 255.0 + 0.5) / 256.0, 0.5)).rgb; }
      else c = vec3(0.37, 0.36, 0.33);
    } else {
      float v = uPiksel > 0.5 ? texture2D(tAlan, muv).r : (uMod == 2 ? texture2D(tYuk, uv).r : texture2D(tAlan, uv).r);
      c = texture2D(tLut, vec2((v * 255.0 + 0.5) / 256.0, 0.5)).rgb;
    }
    if(uKabartma > 0.0){ float s = (texture2D(tKab, uv).r - 0.5) * 2.0;
      c = s < 0.0 ? c * (1.0 + uKabartma * s * 0.85) : c + (1.0 - c) * uKabartma * s * 0.45; }
    // kiyi seridi: yalniz kara oraninin 1'den kucuk oldugu kenar teksellerinde.
    // Ust sinir 1'i gecerse (uzak yakinlastirmada w buyur) ic kara da
    // koyulasiyordu: yumusak gorunum piksel gorunumden ~%28 karanlikti.
    if(uPiksel < 0.5){ float e = 1.0 - smoothstep(0.5, min(0.5 + 7.0 * w, 1.0), dk.r); c *= 1.0 - 0.3 * e; }
    renk = mix(renk, c, a);
  }
  if(uIzgara > 0.5){
    float lon = uBounds.x + hucre.x / uGrid.x * (uBounds.z - uBounds.x);
    float lat = uBounds.w - hucre.y / uGrid.y * (uBounds.w - uBounds.y);
    float dpp = (uBounds.z - uBounds.x) / uGrid.x / uView.z;
    float adim = dpp < 0.03 ? 10.0 : 30.0;
    float dx = abs(mod(lon + adim * 0.5, adim) - adim * 0.5) / dpp;
    float dy = abs(mod(lat + adim * 0.5, adim) - adim * 0.5) / dpp;
    float cz = 1.0 - smoothstep(0.35, 1.1, min(dx, dy));
    float ek = 1.0 - smoothstep(0.35, 1.3, abs(lat) / dpp);
    renk = mix(renk, vec3(0.9, 0.88, 0.83), 0.075 * cz + 0.11 * ek);
  }
  gl_FragColor = vec4(renk, 1.0);
}`;

function glKur(canvas){
  const gl = canvas.getContext("webgl", {antialias:false, alpha:false, depth:false, stencil:false,
    premultipliedAlpha:false, preserveDrawingBuffer:true});
  if(!gl) return null;
  const sh = (t, s) => { const o=gl.createShader(t); gl.shaderSource(o,s); gl.compileShader(o);
    if(!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
  const pr = gl.createProgram();
  gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS));
  gl.linkProgram(pr); if(!gl.getProgramParameter(pr, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(pr));
  gl.useProgram(pr);
  const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 3,-1, -1,3]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(pr, "p"); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  gl.pixelStorei(gl.UNPACK_ALIGNMENT, 1);
  // sinif kodu B kanalinda: renk profili donusumu kodu bozmasin
  gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL, gl.NONE);
  gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
  const U = {}; for(const ad of ["uRes","uDpr","uView","uGrid","uBounds","tAlan","tLut","tKop","tPal","tDoku","tDokuN","tYuk","tKab",
    "uMod","uPiksel","uKabartma","uIzgara","uIzole","uOlcek","uZemin","uDeniz"]) U[ad] = gl.getUniformLocation(pr, ad);
  const birimler = {tAlan:0, tLut:1, tKop:2, tPal:3, tDoku:4, tDokuN:5, tYuk:6, tKab:7};
  const doku = {};
  function kur(ad, veri, w, h, bicim, suz){
    let t = doku[ad]; if(!t) t = doku[ad] = gl.createTexture();
    gl.activeTexture(gl.TEXTURE0 + birimler[ad]); gl.bindTexture(gl.TEXTURE_2D, t);
    const f = bicim==="L" ? gl.LUMINANCE : bicim==="LA" ? gl.LUMINANCE_ALPHA : (bicim==="RGBA" ? gl.RGBA : gl.RGB);
    if(veri instanceof Uint8Array) gl.texImage2D(gl.TEXTURE_2D, 0, f, w, h, 0, f, gl.UNSIGNED_BYTE, veri);
    else gl.texImage2D(gl.TEXTURE_2D, 0, f, f, gl.UNSIGNED_BYTE, veri);
    const m = suz ? gl.LINEAR : gl.NEAREST;
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, m); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, m);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.uniform1i(U[ad], birimler[ad]);
  }
  return {gl, U, kur, enBuyuk: gl.getParameter(gl.MAX_TEXTURE_SIZE)};
}

/* ================================================================ uygulama */
function baslat(J, resimler){
  const D = veriHazirla(J), {W, H, N, B} = D;
  D.dol = dolasimHazirla(D, resimler.dolasim);
  D.su = suHazirla(resimler.su);
  D.tk = tektHazirla(resimler.tekt, resimler.levha);
  // kabartma kaynaklari (kabartmaKur GL kurulurken cagrilir, once tanimli olmali)
  const KAB = {bir: resimler.kabartmaBir, editor: resimler.kabartma, gri: resimler.kabartmaGri};
  if(!KAB[ayar.kabartmaKaynak]) ayar.kabartmaKaynak = KAB.bir ? "bir" : "editor";
  if(!D.dol) $("[data-k=dolasim]").hidden = true;   // eski veride dolasim yok
  const canvas = $("#gl"), kaplama = $("#kaplama");
  let G = null;
  try { G = glKur(canvas); if(G && G.enBuyuk < Math.max(D.doku.w, D.doku.h)) G = null; }
  catch(e){ console.error(e); G = null; }
  const yedek = G ? null : canvas.getContext("2d");
  // Android arka plandaki sekmenin GPU bagini koparabilir (context lost);
  // o zaman dokular gider ve harita siyah kalir. Geri gelince sayfa yeniden
  // kurulur: veri ve dokular onbellekte, acilis kisa.
  canvas.addEventListener("webglcontextlost", e => e.preventDefault());
  canvas.addEventListener("webglcontextrestored", () => location.reload());

  const palet = new Uint8Array(32*4);
  for(const [kod, ad] of Object.entries(D.KCODE)){ const c = hex(KPAL[ad] || D.J.data.koppen_colors[ad]);
    palet.set([c[0],c[1],c[2],255], (+kod)*4); }
  // gezegenin yaricapi veriden (eski veride yok: Dunyam'inki 6371)
  const YARICAP = D.J.data.radius_km || 6371, KM_DERECE = YARICAP*Math.PI/180;
  const kodNo = {}; for(const [kod, ad] of Object.entries(D.KCODE)) kodNo[ad] = +kod;

  if(G){
    // model okyanus hucrelerine de sinif yazar; piksel gorunumu karayi
    // "kod > 0" diye ayirdigi icin dokuda okyanus 0 olmali
    // L = kara sinif kodu, A = deniz dokusu icin kaba "derinlik" (kiyiya
    // uzakliktan; gercek batimetri degil, yalniz gorunus)
    const kopKara = new Uint8Array(N*2), dz = denizUzak(D);
    for(let i=0;i<N;i++){ if(D.land[i]) kopKara[2*i] = D.kop[i]; kopKara[2*i+1] = dz[i]; }
    G.kur("tKop", kopKara, W, H, "LA", false);
    G.kur("tPal", palet, 32, 1, "RGBA", false);
    G.kur("tDoku", resimler.doku, 0, 0, "RGB", true);
    G.kur("tDokuN", resimler.doku, 0, 0, "RGB", false);
    G.kur("tYuk", resimler.yukseklik, 0, 0, "L", true);
    kabartmaKur();
    // WebGL1 her ornekleyicinin bir dokusu olmasini ister; alan dokulari
    // katman secilince dolar, o zamana kadar bos durur
    G.kur("tAlan", new Uint8Array(W*H), W, H, "L", true);
    G.kur("tLut", new Uint8Array(256*3), 256, 1, "RGB", true);
  }

  let katman = "iklim", donem = -1, izole = null, sec = null, gor = null;
  let olcek = 1, ox = 0, oy = 0, sigOlcek = 1, dpr = 1, kirli = true;

  const KUTU = (()=>{ let x0=W,x1=0,y0=H,y1=0; for(let i=0;i<N;i++) if(D.land[i]){ const x=i%W, y=(i/W)|0;
    if(x<x0)x0=x; if(x>x1)x1=x; if(y<y0)y0=y; if(y>y1)y1=y; } return {x0, y0, w:x1-x0+1, h:y1-y0+1}; })();
  // her satirdaki karanin bati/dogu ucu (karasiz satirlar en yakin karali
  // satirdan): pan siniri kutunun kosesindeki acik denize degil karaya baglanir
  const SATIR = (()=>{ const a = new Float64Array(H).fill(NaN), b = new Float64Array(H).fill(NaN);
    for(let i=0;i<N;i++) if(D.land[i]){ const x=i%W, y=(i/W)|0;
      if(isNaN(a[y]) || x < a[y]) a[y] = x; if(isNaN(b[y]) || x+1 > b[y]) b[y] = x+1; }
    for(let y=0, son=-1; y<H; y++){ if(!isNaN(a[y])) son=y; else if(son>=0){ a[y]=a[son]; b[y]=b[son]; } }
    for(let y=H-1, son=-1; y>=0; y--){ if(!isNaN(a[y])) son=y; else if(son>=0){ a[y]=a[son]; b[y]=b[son]; } }
    return {a, b}; })();

  function gorunen(){
    const r = canvas.getBoundingClientRect(), d = $("#dok").getBoundingClientRect();
    const ust = $(".marka").getBoundingClientRect().bottom + 8;
    // yatay kisa ekranda dok sag sutunda (style.css): harita solda kalan alan
    const yan = d.top < 1 && d.left > 1;
    const alt = yan ? r.height - 8 : d.top - 8;
    return {w: yan ? d.left : r.width, h:r.height, ust, alt};
  }
  function sigdir(){
    const g = gorunen(), vh = Math.max(80, g.alt - g.ust), pay = 0.94;
    olcek = Math.min(g.w/KUTU.w, vh/KUTU.h) * pay; sigOlcek = olcek;
    ox = g.w/2 - (KUTU.x0 + KUTU.w/2)*olcek; oy = g.ust + vh/2 - (KUTU.y0 + KUTU.h/2)*olcek;
    ciz();
  }
  function sinirla(){
    const g = gorunen();
    olcek = Math.max(sigOlcek*0.7, Math.min(sigOlcek*48, olcek));
    // Ekranin ortasi kara kutusundan en fazla gorunen alanin %35'i kadar
    // disari cikabilir. Once butun VERI kutusuna gore sinirlaniyordu; veride
    // karanin cevresinde 22 derecelik okyanus payi oldugu icin yakinken ekran
    // tamamen bos okyanusa (ya da verinin disina) kayabiliyordu (gece
    // denetimi, olculdu). Pay, kiyidaki secili hucrenin kartin ustune
    // kaydirilabilmesi icin (gorunurYap).
    // Yatay sinir, ekranin ortasindaki SATIRDA karanin bati/dogu ucuna gore:
    // dikdortgen kutu yetmedi, kosesi kiyidan uzak acik deniz (test yakaladi).
    const cx = g.w/2, cy = (g.ust + g.alt)/2, pw = 0.35*g.w, ph = 0.35*(g.alt - g.ust);
    oy = Math.min(cy + ph - KUTU.y0*olcek, Math.max(cy - ph - (KUTU.y0 + KUTU.h)*olcek, oy));
    const sy = Math.max(0, Math.min(H-1, Math.floor((cy - oy)/olcek)));
    ox = Math.min(cx + pw - SATIR.a[sy]*olcek, Math.max(cx - pw - SATIR.b[sy]*olcek, ox));
  }
  function boyut(){
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    const r = canvas.getBoundingClientRect();
    canvas.width = Math.round(r.width*dpr); canvas.height = Math.round(r.height*dpr);
    document.documentElement.style.setProperty("--dok-h", $("#dok").getBoundingClientRect().height+"px");
    ciz();
  }
  function ciz(){ kirli = true; }

  /* --- yedek (WebGL yok): hucre cozunurlugunde, piksel gorunumu --- */
  const yedekTuval = document.createElement("canvas");
  function yedekBoya(){
    yedekTuval.width = W; yedekTuval.height = H;
    const c2 = yedekTuval.getContext("2d"), img = c2.createImageData(W, H), px = img.data, dz = hex(OKYANUS_DERIN);
    for(let i=0;i<N;i++){ let c = dz;
      if(katman==="dolasim"){ const b = gor.a[i]; c = D.land[i] && ayar.dolZemin!=="hiz" ? [94,92,84] : [gor.lut[b*3], gor.lut[b*3+1], gor.lut[b*3+2]]; }
      else if(D.land[i]){ if(katman==="iklim"){ c = [palet[D.kop[i]*4], palet[D.kop[i]*4+1], palet[D.kop[i]*4+2]];
          // yalitilmis sinif: shader'daki gibi otekiler gri-koyu (gece denetimi:
          // yedekte yalitma hic yoktu, butun siniflar gorunuyordu)
          if(izole && D.kop[i] !== kodNo[izole]){ const g = 0.299*c[0] + 0.587*c[1] + 0.114*c[2];
            c = [g*0.38 + 33*0.62, g*0.38 + 41*0.62, g*0.38 + 46*0.62]; } }
        else { const b = gor.a[i]; c = [gor.lut[b*3], gor.lut[b*3+1], gor.lut[b*3+2]]; } }
      px[i*4]=c[0]; px[i*4+1]=c[1]; px[i*4+2]=c[2]; px[i*4+3]=255; }
    c2.putImageData(img, 0, 0);
  }

  function kare(){
    if(kirli){ kirli = false; sinirla();
      if(G){ const gl = G.gl, U = G.U;
        gl.viewport(0, 0, canvas.width, canvas.height);
        gl.uniform2f(U.uRes, canvas.width, canvas.height); gl.uniform1f(U.uDpr, dpr);
        gl.uniform3f(U.uView, ox, oy, olcek); gl.uniform2f(U.uGrid, W, H);
        gl.uniform4f(U.uBounds, B[0], B[1], B[2], B[3]);
        gl.uniform1i(U.uMod, {iklim:0, arazi:2, dolasim:3}[katman] ?? 1);
        gl.uniform1f(U.uPiksel, ayar.piksel ? 1 : 0);
        gl.uniform1f(U.uKabartma, ayar.kabartma ? (katman==="arazi" || katman==="dolasim" ? 0.8 : 0.5) : 0);
        gl.uniform1f(U.uIzgara, ayar.izgara ? 1 : 0);
        gl.uniform1f(U.uDeniz, ayar.deniz ? 1 : 0);
        gl.uniform1f(U.uIzole, izole ? kodNo[izole] : 0);
        gl.uniform1f(U.uOlcek, D.doku.olcek);
        gl.uniform1f(U.uZemin, ayar.dolZemin==="hiz" ? 1 : 0);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
      } else {
        const c = yedek; c.setTransform(1,0,0,1,0,0); c.fillStyle = OKYANUS_DERIN; c.fillRect(0,0,canvas.width,canvas.height);
        c.imageSmoothingEnabled = false; c.setTransform(dpr*olcek,0,0,dpr*olcek,dpr*ox,dpr*oy); c.drawImage(yedekTuval, 0, 0);
      }
      suCiz();
      if(TK) tektCiz();
      if(BI) bitkiCiz();
      if(TP) toprakCiz();
      if(YS) yasamCiz();
      parcacik.gorunumDegisti();   // once: kaplama parcacik acikken akis cizgisi cizmesin
      kaplamaCiz();
    }
    parcacik.adim();
    requestAnimationFrame(kare);
  }

  // Dolasim kaplamasi (akis cizgileri) her karede bastan kurulup boyaniyordu;
  // Dolasim'da surukleme Iklim'in ~5 kati surdu (yazilim GPU'lu test
  // ortami, gece denetimi). Maliyet JS degil buyuk SVG'nin boyanmasi. Hareket
  // surerken son cizim oldugu gibi kaydirilip olceklenir; hareket bitince
  // (parmak kalkinca / tekerlek durunca) bir kez yeniden kurulur.
  let cizilen = null, sonTeker = 0;
  const harekette = () => ptr.size > 0 || performance.now() - sonTeker < 150;
  function kaplamaCiz(){
    const r = canvas.getBoundingClientRect(); kaplama.setAttribute("viewBox", `0 0 ${r.width} ${r.height}`);
    // Donusum SVG'nin icine degil ogenin kendisine (CSS) verilir: tarayici onu
    // katman olarak kaydirir, yeniden boyamaz. SVG donusumu de her karede
    // boyatiyordu: maliyet JS degil boyamaydi (kaplamasiz 3.7 s, olculdu).
    if(katman==="dolasim" && D.dol && !ayar.parcacik && cizilen && cizilen.katman === katman && cizilen.donem === donem && harekette()){
      const k = olcek/cizilen.olcek;
      kaplama.style.transform = `translate(${(ox - cizilen.ox*k).toFixed(2)}px,${(oy - cizilen.oy*k).toFixed(2)}px) scale(${k.toFixed(5)})`;
      return; }
    kaplama.style.transform = "";
    cizilen = {ox, oy, olcek, katman, donem};
    let s = "";
    if(ayar.izgara){ const g = gorunen();
      // etiket adimi cizgiyle ayni (shader: dpp < 0.03 ise 10°); yakinken
      // 30'un katlari ekrandan cikinca hic enlem etiketi kalmiyordu (gece denetimi)
      const adim = (B[2]-B[0])/W/olcek < 0.03 ? 10 : 30, enler = [];
      for(let la = Math.ceil(B[1]/adim)*adim; la <= B[3]; la += adim) enler.push(la);
      for(const la of enler){ const y = oy + (B[3]-la)/(B[3]-B[1])*H*olcek;
        if(y > g.ust + 10 && y < g.alt - 4) s += `<text x="10" y="${(y-4).toFixed(1)}">${la===0 ? "EKVATOR" : Math.abs(la)+"°"+(la>0?"K":"G")}</text>`; } }
    if(katman==="dolasim" && D.dol) s += dolasimCiz();
    if(sec !== null){ const x = ox + (sec%W)*olcek, y = oy + ((sec/W)|0)*olcek, k = Math.max(olcek, 6), d = (k-olcek)/2;
      s += `<rect x="${(x-d-1).toFixed(1)}" y="${(y-d-1).toFixed(1)}" width="${(k+2).toFixed(1)}" height="${(k+2).toFixed(1)}" fill="none" stroke="#0b1116" stroke-width="3" stroke-opacity=".7"/>`
        + `<rect x="${(x-d).toFixed(1)}" y="${(y-d).toFixed(1)}" width="${k.toFixed(1)}" height="${k.toFixed(1)}" fill="none" stroke="#d2a45c" stroke-width="1.5"/>`; }
    kaplama.innerHTML = s;
  }

  /* --- dolasim kaplamasi: akinti yollari ve ruzgar oklari (SVG) --- */
  const ekranX = lon => ox + (lon-B[0])/(B[2]-B[0])*W*olcek, ekranY = lat => oy + (B[3]-lat)/(B[3]-B[1])*H*olcek;
  function dolasimCiz(){
    const r = canvas.getBoundingClientRect(), g = gorunen(), km = olcek/((B[2]-B[0])/W*KM_DERECE);   // ekran px / km
    let s = "";
    // akintilar: genisligi kadar soluk bir serit + yonunu gosteren cekirdek cizgi
    for(const a of D.akintilar){
      const p = a.yol.map(([lo,la]) => [ekranX(lo), ekranY(la)]);
      let d = `M${p[0][0].toFixed(1)},${p[0][1].toFixed(1)}`;
      for(let i=0;i<p.length-1;i++){ const a0=p[Math.max(0,i-1)], a1=p[i], a2=p[i+1], a3=p[Math.min(p.length-1,i+2)];
        d += `C${(a1[0]+(a2[0]-a0[0])/6).toFixed(1)},${(a1[1]+(a2[1]-a0[1])/6).toFixed(1)} ${(a2[0]-(a3[0]-a1[0])/6).toFixed(1)},${(a2[1]-(a3[1]-a1[1])/6).toFixed(1)} ${a2[0].toFixed(1)},${a2[1].toFixed(1)}`; }
      const sicak = a.anomali >= 0, renk = sicak ? "#e39a63" : "#86b9d8";
      s += `<path d="${d}" fill="none" stroke="${renk}" stroke-opacity=".13" stroke-linecap="round" stroke-width="${Math.max(6, a.genislik_km*km*1.6).toFixed(1)}"/>`
        + `<path d="${d}" fill="none" stroke="#0b1116" stroke-opacity=".55" stroke-width="4" stroke-linecap="round"/>`
        + `<path d="${d}" fill="none" stroke="${renk}" stroke-width="2" stroke-linecap="round" stroke-dasharray="10 7" marker-end="url(#ak-${sicak?"s":"k"})"><title>${a.ad}</title></path>`;
    }
    if(!(ayar.parcacik && parcacik.calisiyor)) s += ruzgarCiz(r, g);
    return `<defs>${["s","k"].map(t=>`<marker id="ak-${t}" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="${t==="s"?"#e39a63":"#86b9d8"}"/></marker>`).join("")}</defs>` + s;
  }

  /* --- su katmani: goller ve nehirler (Canvas2D) ---
     Atlaslardaki gibi ölçeğe göre seyreltilir: uzaktan yalnız 1. kademe
     (büyük ve uzun ana kollar), yakınlaştıkça 2, 3, 4. kademe yumuşakça
     belirir; "Bütün kollar" seçilince hepsi. Çizgi noktalardan geçen
     Catmull-Rom eğrisi (kollar ana kola tam oturur), kalınlık debiyle
     akış yönünde artar. Önce koyu bir kılıf, üstünde su rengi: renkli
     iklim zemininde de seçilir. */
  const SU = D.su, suCv = $("#su"), suC = suCv.getContext("2d");
  // Su, denizin kendi malzemesiyle çizilir (shader'daki deniz(): sığ
  // sahanlık tonu, orta, derin, kıyı köpüğü). Ayrı parlak mavi bir katman
  // haritanın üstünde yapıştırma gibi duruyordu. Göl: kıyıda sığ ton +
  // köpük, içe doğru denizin orta/derin tonu (kıyı ışıltısı denizdekiyle
  // aynı). Nehir: sığ-köpük tonu, altında aynı tonda yumuşak bir ışıltı
  // (kıta kıyısındaki ışıltının küçüğü); büyük kollar biraz daha açık.
  const DZ = {sig:[34,77,82], orta:[15,37,47], derin:[7,15,22], kopuk:[52,107,115], isik:[74,138,146]};
  const rgb = (c, a=1) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;
  const karis = (x, y, t) => x.map((v, i) => Math.round(v + (y[i]-v)*t));
  const COKEL = "150,140,100";   // delta ovasi ve denizdeki cokel bulutu (koyu zemine gore bastirilmis)
  const yumusak = (a, b, x) => { const t = Math.max(0, Math.min(1, (x-a)/(b-a))); return t*t*(3-2*t); };
  function suGorunurluk(k){
    if(ayar.suKol === "tum" || k === 1) return 1;
    const z = olcek/sigOlcek;
    return k === 2 ? yumusak(1.7, 2.6, z) : k === 3 ? yumusak(3.4, 5, z) : yumusak(7, 10, z);
  }
  // Kaydirma/yakinlastirma surerken yeniden boyanmaz: son cizim CSS ile
  // kaydirilip olceklenir (Dolasim kaplamasi gibi); hareket bitince bir kez
  // cizilir. "Butun kollar"da boyama kare basina ~250 ms tutuyordu (bulut
  // makinesi, yazilim GPU, CPU x4); bekleyen hesap degil boyamaydi.
  let suCizilen = null;
  function suCiz(){
    const imza = `${ayar.su}|${ayar.suKol}|${katman}`;
    if(suCizilen && suCizilen.imza === imza && harekette()){
      const k = olcek/suCizilen.olcek;
      suCv.style.transform = `translate(${(ox - suCizilen.ox*k).toFixed(2)}px,${(oy - suCizilen.oy*k).toFixed(2)}px) scale(${k.toFixed(5)})`;
      return; }
    suCv.style.transform = ""; suCizilen = {ox, oy, olcek, imza};
    const w = Math.round(suCv.getBoundingClientRect().width*dpr), h = Math.round(suCv.getBoundingClientRect().height*dpr);
    if(suCv.width !== w || suCv.height !== h){ suCv.width = w; suCv.height = h; }
    suC.setTransform(1,0,0,1,0,0); suC.clearRect(0, 0, w, h);
    // Dolasim'da su cizilmez: ruzgar ve akinti okunurlugu; o sekmede
    // ayrica boyama maliyeti (yazilim GPU'da ~0.5 s) katmanin gecikmesine yol aciyordu
    if(!SU || !ayar.su || katman === "dolasim") return;
    suC.setTransform(dpr,0,0,dpr,0,0);
    const g = gorunen(), sx = (B[2]-B[0])/W, sy = (B[3]-B[1])/H;
    // gorunen alanin enlem/boylam kutusu (payli)
    const lo0 = B[0] + (-ox/olcek - 4)*sx, lo1 = B[0] + ((g.w - ox)/olcek + 4)*sx;
    const la1 = B[3] - (-oy/olcek - 4)*sy, la0 = B[3] - ((h/dpr - oy)/olcek + 4)*sy;
    const icinde = k => !(k[2] < lo0 || k[0] > lo1 || k[3] < la0 || k[1] > la1);
    const zf = Math.max(1, Math.min(3.2, Math.sqrt(olcek/sigOlcek)));
    const soluk = 1;
    // boylam/enlem -> ekran (dogrusal); cizgi kalinligi yol birimine cevrilir
    const kx = olcek/sx, ky = olcek/sy, birim = 1/Math.sqrt(kx*ky);
    suC.setTransform(dpr*kx, 0, 0, -dpr*ky, dpr*(ox - B[0]*kx), dpr*(oy + B[3]*ky));
    // delta: agizda cokel bulutu (yarisi delta ovasi, yarisi denizde bulanik su)
    for(const d of SU.deltalar){ if(suGorunurluk(d.k) < 0.02 || !icinde(d.kutu)) continue;
      const r = d.r/111.2*1.1, x = d.agiz[1], y = d.agiz[0];
      const g = suC.createRadialGradient(x, y, 0, x, y, r);
      const a0 = Math.min(0.28, 0.08 + 0.04*Math.log10(1 + d.Qs)) * suGorunurluk(d.k) * soluk;
      g.addColorStop(0, `rgba(${COKEL},${a0.toFixed(3)})`); g.addColorStop(1, `rgba(${COKEL},0)`);
      suC.globalAlpha = 1; suC.fillStyle = g; suC.beginPath(); suC.arc(x, y, r, 0, Math.PI*2); suC.fill(); }
    // goller: denizle ayni malzeme. Dolgu derin/orta ton; icten kiyiya dogru
    // sig ton ve kopuk (genisten dara ust uste bindirilmis cizgiler)
    for(const L of SU.goller){ if(!icinde(L.kutu)) continue;
      suC.globalAlpha = soluk;
      suC.fillStyle = rgb(L.tuz ? karis(DZ.sig, [150,142,112], 0.5) : (L.alan > 20000 ? DZ.orta : karis(DZ.orta, DZ.sig, 0.35))); suC.fill(L.yol, "evenodd");
      suC.save(); suC.clip(L.yol, "evenodd");
      const kiyi = L.tuz ? [176,168,136] : DZ.sig;   // tuz golu: kurumus kiyi tuz/kum rengi
      for(const [gen, al] of [[10, 0.25], [4, 0.45]]){ suC.globalAlpha = al*soluk; suC.strokeStyle = rgb(kiyi); suC.lineWidth = gen*zf*birim; suC.stroke(L.yol); }
      suC.globalAlpha = (L.tuz ? 0.55 : 0.8)*soluk; suC.strokeStyle = rgb(L.tuz ? [196,188,154] : DZ.kopuk); suC.lineWidth = 1.6*zf*birim; suC.stroke(L.yol);
      suC.restore(); }
    suC.lineCap = "round"; suC.lineJoin = "round";
    const parlak = g => Math.max(0, Math.min(1, (g - 0.5)/1.6));
    const cizilecek = [];
    for(const n of SU.nehirler){ const a = suGorunurluk(n.k); if(a > 0.02 && icinde(n.kutu)) cizilecek.push([n, a]); }
    const kollar = [];
    for(const d of SU.deltalar){ const a = suGorunurluk(d.k); if(a > 0.02 && icinde(d.kutu)) for(const yol of d.yollar) kollar.push([d.g, yol, a]); }
    for(const [n, a] of cizilecek) for(const [g, yol] of n.parcalar) kollar.push([g, yol, a]);
    // once isilti (genis, soluk), sonra su
    for(const isilti of [true, false]) for(const [g, yol, a] of kollar){
      if(isilti && g < 1) continue;     // isilti yalniz buyuk kollarda: kucuklerde gorunmuyor, maliyeti iki katti
      const t = parlak(g), w = g*zf;
      if(isilti){ suC.globalAlpha = a*soluk*0.16; suC.strokeStyle = rgb(DZ.isik); suC.lineWidth = (w*2.6 + 1.5)*birim; }
      else { suC.globalAlpha = a*soluk*(0.75 + 0.25*t); suC.strokeStyle = rgb(karis(DZ.kopuk, DZ.isik, 0.35 + 0.65*t)); suC.lineWidth = w*birim; }
      suC.stroke(yol); }
    suC.globalAlpha = 1;
  }

  /* --- bitki örtüsü (Arazi > Bitki): bitki/bitki.py'nin biyom haritası.
     data/bitki.png paletli (renkler dosyada, ~0.044°); kabartma tuvalin
     kendi "multiply" birleştirmesiyle çarpılır, piksel döngüsü yok (eski
     yol ilk açılışta CPU x4'te ~0.9 s sürüyordu). Kartın değerleri
     data/bitki_veri.png'den (R = kod, G = alfa*200, B = en soğuk ay + 100),
     dokunulan nokta için tek piksel okunur. Kaydırırken CSS ile kayar. */
  const BJ = resimler.bitkiJ, BI = BJ && resimler.bitki ? resimler.bitki : null, BV = resimler.bitkiVeri;
  const bkCv = $("#bitki"), bkC = bkCv.getContext("2d");
  let BK = null;     // {tuval, veri (okuma tuvali)}
  function bitkiKur(){
    if(BK || !BI) return BK;
    const w = BI.naturalWidth, h = BI.naturalHeight, K = BJ.kesit, cv = document.createElement("canvas"); cv.width = w; cv.height = h;
    const c = cv.getContext("2d"); c.drawImage(BI, 0, 0);
    // gölge kapalıysa ya da kaynak yoksa çarpma adımı atlanır (düz renkler)
    const kab = ayar.kabartma ? (KAB[ayar.kabartmaKaynak] || KAB.bir || KAB.editor) : null;
    if(kab){
      // kabartma harita kutusu B'yi kaplar: bitki kesitine göre yerleştir
      const kx = w/(K[2]-K[0]), ky = h/(K[3]-K[1]);
      c.globalCompositeOperation = "multiply"; c.imageSmoothingEnabled = true; c.imageSmoothingQuality = "high";
      c.drawImage(kab, (B[0]-K[0])*kx, (K[3]-B[3])*ky, (B[2]-B[0])*kx, (B[3]-B[1])*ky);
      // kabartma ortası ~128: çarpım yarıya indirir, kendisiyle toplayıp 2 katına çıkar
      c.globalCompositeOperation = "lighter"; c.drawImage(cv, 0, 0);
      // multiply saydam denize de boyadı: kara maskesi yeniden uygulanır
      c.globalCompositeOperation = "destination-in"; c.drawImage(BI, 0, 0);
      c.globalCompositeOperation = "source-over"; }
    let veri = null;
    if(BV){ const v = document.createElement("canvas"); v.width = BV.naturalWidth; v.height = BV.naturalHeight;
      veri = v.getContext("2d", {willReadFrequently:true}); veri.drawImage(BV, 0, 0); }
    return BK = {tuval: cv, veri};
  }
  const bitkiModu = () => !!BI && katman === "arazi" && ayar.araziMod === "bitki";
  let bkCizilen = null;
  function bitkiCiz(){
    const imza = `${bitkiModu()}|${katman}`;
    if(bkCizilen && bkCizilen.imza === imza && harekette()){
      const k = olcek/bkCizilen.olcek;
      bkCv.style.transform = `translate(${(ox - bkCizilen.ox*k).toFixed(2)}px,${(oy - bkCizilen.oy*k).toFixed(2)}px) scale(${k.toFixed(5)})`;
      return; }
    bkCv.style.transform = ""; bkCizilen = {ox, oy, olcek, imza};
    // kapalıyken sıfırlanıp gizlenir (tektonik katmanındaki headless okuma sorunu)
    if(!bitkiModu()){ if(!bkCv.hidden){ bkCv.width = bkCv.width; bkCv.hidden = true; } return; }
    bkCv.hidden = false; bitkiKur();
    const r = bkCv.getBoundingClientRect(), w = Math.round(r.width*dpr), h = Math.round(r.height*dpr);
    if(bkCv.width !== w || bkCv.height !== h){ bkCv.width = w; bkCv.height = h; }
    bkC.setTransform(1,0,0,1,0,0); bkC.clearRect(0, 0, w, h);
    const sx = (B[2]-B[0])/W, sy = (B[3]-B[1])/H, kx = olcek/sx, ky = olcek/sy, K = BJ.kesit;
    bkC.setTransform(dpr*kx, 0, 0, dpr*ky, dpr*(ox - B[0]*kx), dpr*(oy + B[3]*ky));
    bkC.imageSmoothingEnabled = true; bkC.imageSmoothingQuality = "high";
    bkC.drawImage(BK.tuval, K[0], -K[3], K[2]-K[0], K[3]-K[1]);
  }
  function bitkiSatiri(lon, lat){
    if(!bitkiModu() || !bitkiKur() || !BK.veri) return "";
    const K = BJ.kesit, W2 = BV.naturalWidth, H2 = BV.naturalHeight;
    const x = Math.floor((lon-K[0])/(K[2]-K[0])*W2), y = Math.floor((K[3]-lat)/(K[3]-K[1])*H2);
    if(x < 0 || y < 0 || x >= W2 || y >= H2) return "";
    const p = BK.veri.getImageData(x, y, 1, 1).data, b = BJ.biyomlar[p[0]]; if(!b) return "";
    return `<div class="k-bk"><b>Bitki örtüsü</b> ${b.ad} · ${b.ne} <small>Dünya'da: ${b.ornek}</small></div>`
      + `<div class="k-bk"><b>Neden</b> en soğuk ay ${eksi(p[2] - 100)} °C · nem oranı (gerçek / olası buharlaşma) ${virgul((p[1]/200).toFixed(2))}</div>`;
  }

  /* --- toprak türleri (Arazi > Toprak): toprak/toprak.py'nin WRB sınıfları.
     Bitki örtüsüyle birebir aynı çizim yolu: data/toprak.png paletli, kabartma
     "multiply" ile çarpılır, kart data/toprak_veri.png'den (R = kod) okunur. */
  const TPJ = resimler.toprakJ, TP = TPJ && resimler.toprak ? resimler.toprak : null, TPV = resimler.toprakVeri;
  const tpCv = $("#toprak"), tpC = tpCv.getContext("2d");
  let TPK = null;     // {tuval, veri (okuma tuvali)}
  function toprakKur(){
    if(TPK || !TP) return TPK;
    const w = TP.naturalWidth, h = TP.naturalHeight, K = TPJ.kesit, cv = document.createElement("canvas"); cv.width = w; cv.height = h;
    const c = cv.getContext("2d"); c.drawImage(TP, 0, 0);
    const kab = ayar.kabartma ? (KAB[ayar.kabartmaKaynak] || KAB.bir || KAB.editor) : null;
    if(kab){
      const kx = w/(K[2]-K[0]), ky = h/(K[3]-K[1]);
      c.globalCompositeOperation = "multiply"; c.imageSmoothingEnabled = true; c.imageSmoothingQuality = "high";
      c.drawImage(kab, (B[0]-K[0])*kx, (K[3]-B[3])*ky, (B[2]-B[0])*kx, (B[3]-B[1])*ky);
      c.globalCompositeOperation = "lighter"; c.drawImage(cv, 0, 0);
      c.globalCompositeOperation = "destination-in"; c.drawImage(TP, 0, 0);
      c.globalCompositeOperation = "source-over"; }
    let veri = null;
    if(TPV){ const v = document.createElement("canvas"); v.width = TPV.naturalWidth; v.height = TPV.naturalHeight;
      veri = v.getContext("2d", {willReadFrequently:true}); veri.drawImage(TPV, 0, 0); }
    return TPK = {tuval: cv, veri};
  }
  const toprakModu = () => !!TP && katman === "arazi" && ayar.araziMod === "toprak";
  let tpCizilen = null;
  function toprakCiz(){
    const imza = `${toprakModu()}|${katman}`;
    if(tpCizilen && tpCizilen.imza === imza && harekette()){
      const k = olcek/tpCizilen.olcek;
      tpCv.style.transform = `translate(${(ox - tpCizilen.ox*k).toFixed(2)}px,${(oy - tpCizilen.oy*k).toFixed(2)}px) scale(${k.toFixed(5)})`;
      return; }
    tpCv.style.transform = ""; tpCizilen = {ox, oy, olcek, imza};
    if(!toprakModu()){ if(!tpCv.hidden){ tpCv.width = tpCv.width; tpCv.hidden = true; } return; }
    tpCv.hidden = false; toprakKur();
    const r = tpCv.getBoundingClientRect(), w = Math.round(r.width*dpr), h = Math.round(r.height*dpr);
    if(tpCv.width !== w || tpCv.height !== h){ tpCv.width = w; tpCv.height = h; }
    tpC.setTransform(1,0,0,1,0,0); tpC.clearRect(0, 0, w, h);
    const sx = (B[2]-B[0])/W, sy = (B[3]-B[1])/H, kx = olcek/sx, ky = olcek/sy, K = TPJ.kesit;
    tpC.setTransform(dpr*kx, 0, 0, dpr*ky, dpr*(ox - B[0]*kx), dpr*(oy + B[3]*ky));
    tpC.imageSmoothingEnabled = true; tpC.imageSmoothingQuality = "high";
    tpC.drawImage(TPK.tuval, K[0], -K[3], K[2]-K[0], K[3]-K[1]);
  }
  function toprakSatiri(lon, lat){
    if(!toprakModu() || !toprakKur() || !TPK.veri) return "";
    const K = TPJ.kesit, W2 = TPV.naturalWidth, H2 = TPV.naturalHeight;
    const x = Math.floor((lon-K[0])/(K[2]-K[0])*W2), y = Math.floor((K[3]-lat)/(K[3]-K[1])*H2);
    if(x < 0 || y < 0 || x >= W2 || y >= H2) return "";
    const p = TPK.veri.getImageData(x, y, 1, 1).data, t = TPJ.topraklar[p[0]]; if(!t) return "";
    return `<div class="k-bk"><b>Toprak</b> ${t.ad} · ${t.ne} <small>Dünya'da: ${t.ornek}</small></div>`;
  }

  /* --- genel yaşanabilirlik (Arazi > Yaşanabilirlik): yasam/yasam.py'nin net birincil üretim sınıfları.
     Bitki örtüsüyle birebir aynı çizim yolu: data/yasam.png paletli, kabartma
     "multiply" ile çarpılır, kart data/yasam_veri.png'den okunur (R = sınıf + 16 × sınırlayıcı + 32 × kıyı, G = NPP/12, B = sıcaklık + 100). */
  const YJ = resimler.yasamJ, YS = YJ && resimler.yasam ? resimler.yasam : null, YV = resimler.yasamVeri;
  const ysCv = $("#yasam"), ysC = ysCv.getContext("2d");
  let YK = null;     // {tuval, veri (okuma tuvali)}
  // nehir çevresi seçeneği: geniş ve yumuşak (varsayılan) ya da nehrin hemen yanı
  const yasamRes = () => ayar.yasamKiyi === "dar" && resimler.yasamDar && resimler.yasamDarVeri ? [resimler.yasamDar, resimler.yasamDarVeri] : [YS, YV];
  function yasamKur(){
    if(YK || !YS) return YK;
    const [Y, V] = yasamRes();
    const w = Y.naturalWidth, h = Y.naturalHeight, K = YJ.kesit, cv = document.createElement("canvas"); cv.width = w; cv.height = h;
    const c = cv.getContext("2d"); c.drawImage(Y, 0, 0);
    const kab = ayar.kabartma ? (KAB[ayar.kabartmaKaynak] || KAB.bir || KAB.editor) : null;
    if(kab){
      const kx = w/(K[2]-K[0]), ky = h/(K[3]-K[1]);
      c.globalCompositeOperation = "multiply"; c.imageSmoothingEnabled = true; c.imageSmoothingQuality = "high";
      c.drawImage(kab, (B[0]-K[0])*kx, (K[3]-B[3])*ky, (B[2]-B[0])*kx, (B[3]-B[1])*ky);
      c.globalCompositeOperation = "lighter"; c.drawImage(cv, 0, 0);
      c.globalCompositeOperation = "destination-in"; c.drawImage(Y, 0, 0);
      c.globalCompositeOperation = "source-over"; }
    let veri = null;
    if(V){ const v = document.createElement("canvas"); v.width = V.naturalWidth; v.height = V.naturalHeight;
      veri = v.getContext("2d", {willReadFrequently:true}); veri.drawImage(V, 0, 0); }
    return YK = {tuval: cv, veri};
  }
  const yasamModu = () => !!YS && katman === "arazi" && ayar.araziMod === "yasam";
  let ysCizilen = null;
  function yasamCiz(){
    const imza = `${yasamModu()}|${katman}`;
    if(ysCizilen && ysCizilen.imza === imza && harekette()){
      const k = olcek/ysCizilen.olcek;
      ysCv.style.transform = `translate(${(ox - ysCizilen.ox*k).toFixed(2)}px,${(oy - ysCizilen.oy*k).toFixed(2)}px) scale(${k.toFixed(5)})`;
      return; }
    ysCv.style.transform = ""; ysCizilen = {ox, oy, olcek, imza};
    if(!yasamModu()){ if(!ysCv.hidden){ ysCv.width = ysCv.width; ysCv.hidden = true; } return; }
    ysCv.hidden = false; yasamKur();
    const r = ysCv.getBoundingClientRect(), w = Math.round(r.width*dpr), h = Math.round(r.height*dpr);
    if(ysCv.width !== w || ysCv.height !== h){ ysCv.width = w; ysCv.height = h; }
    ysC.setTransform(1,0,0,1,0,0); ysC.clearRect(0, 0, w, h);
    const sx = (B[2]-B[0])/W, sy = (B[3]-B[1])/H, kx = olcek/sx, ky = olcek/sy, K = YJ.kesit;
    ysC.setTransform(dpr*kx, 0, 0, dpr*ky, dpr*(ox - B[0]*kx), dpr*(oy + B[3]*ky));
    ysC.imageSmoothingEnabled = true; ysC.imageSmoothingQuality = "high";
    ysC.drawImage(YK.tuval, K[0], -K[3], K[2]-K[0], K[3]-K[1]);
  }
  function yasamSatiri(lon, lat){
    if(!yasamModu() || !yasamKur() || !YK.veri) return "";
    const K = YJ.kesit, V = yasamRes()[1], W2 = V.naturalWidth, H2 = V.naturalHeight;
    const x = Math.floor((lon-K[0])/(K[2]-K[0])*W2), y = Math.floor((K[3]-lat)/(K[3]-K[1])*H2);
    if(x < 0 || y < 0 || x >= W2 || y >= H2) return "";
    const p = YK.veri.getImageData(x, y, 1, 1).data, c = YJ.siniflar[p[0] & 15]; if(!c) return "";
    const npp = p[1]*12, buz = (p[0] & 15) === 8;
    return `<div class="k-bk"><b>Yaşanabilirlik</b> ${c.ad} · ${c.ne} <small>Dünya'da: ${c.ornek}</small></div>`
      + (buz ? "" : `<div class="k-bk"><b>Üretim</b> ~${npp.toLocaleString("tr-TR")} g/m²/yıl · yıllık ortalama ${eksi(p[2] - 100)} °C · ${(p[0] >> 4) & 1 ? "sıcaklık sınırlıyor" : "su sınırlıyor"}${p[0] & 32 ? " · nehir ya da göl kıyısı: su erişimi var" : ""}</div>`);
  }

  /* --- tektonik katman (Arazi > Levhalar): levha renkleri, sınırlar,
     volkan kuşakları. Su katmanı gibi Canvas2D; kaydırırken CSS ile kayar.
     Sınır renkleri yaygın levha haritası geleneği: yakınsak kırmızı (dişler
     üst levhanın tarafında), ıraksak yeşil (kıta yarığı kesik), dönüşüm
     turuncu. Yay volkanları: dalma hattına paralel, üst levhada 150-280 km
     içeride bir kuşak ve cephede üçgenler; sönmüşler gri. */
  const TK = D.tk, tkCv = $("#tekt"), tkC = tkCv.getContext("2d");
  // denizde levha rengi daha soluk: koyu deniz bulanık görünmesin
  if(TK){ const c = TK.tuval.getContext("2d"), tw = TK.tuval.width, th = TK.tuval.height, im = c.getImageData(0, 0, tw, th), K = TK.kesit;
    for(let y=0;y<th;y++){ const la = K[3] - (y+0.5)*(K[3]-K[1])/th, gy = Math.floor((B[3]-la)/(B[3]-B[1])*H);
      for(let x=0;x<tw;x++){ const q = 4*(y*tw + x); if(!im.data[q+3]) continue;
        const lo = K[0] + (x+0.5)*(K[2]-K[0])/tw, gx = Math.floor((lo-B[0])/(B[2]-B[0])*W);
        const kara = gx >= 0 && gy >= 0 && gx < W && gy < H && D.land[gy*W + gx];
        im.data[q+3] = kara ? 255 : 120; } }
    c.putImageData(im, 0, 0); }
  const TK_RENK = {yak:"#e0563f", ira:"#3fbf8a", don:"#f0a23c", pas:"#9a9a9a"};
  const tkTur = s => /^(SUB|OCB|CCB)$/.test(s) ? "yak" : /^(OSR|CRB)$/.test(s) ? "ira" : /^(OTF|CTF)$/.test(s) ? "don" : "pas";
  const levhaModu = () => !!TK && katman === "arazi" && ayar.araziMod === "levha";
  let tkCizilen = null;
  // çizgi boyunca eşit aralıklı noktalar (derece uzayında), yön ile
  function boyunca(p, aralik, f){
    let kalan = aralik/2;
    for(let i=0;i<p.length/2-1;i++){ const x0 = p[2*i], y0 = p[2*i+1], dx = p[2*i+2]-x0, dy = p[2*i+3]-y0, L = Math.hypot(dx, dy);
      if(L === 0 || L > 20) continue;          // boylam dikişi
      let t = kalan;
      while(t <= L){ f(x0 + dx*t/L, y0 + dy*t/L, dx/L, dy/L); t += aralik; }
      kalan = t - L; } }
  function tektCiz(){
    const imza = `${levhaModu()}|${katman}`;
    if(tkCizilen && tkCizilen.imza === imza && harekette()){
      const k = olcek/tkCizilen.olcek;
      tkCv.style.transform = `translate(${(ox - tkCizilen.ox*k).toFixed(2)}px,${(oy - tkCizilen.oy*k).toFixed(2)}px) scale(${k.toFixed(5)})`;
      return; }
    tkCv.style.transform = ""; tkCizilen = {ox, oy, olcek, imza};
    // Kapalıyken tuval sıfırlanıp gizlenir (boyut yeniden atanır): tam tuval
    // clearRect, headless Chromium'da (GitHub testi) sonraki okumada eski
    // pikselleri döndürüyordu; gizli tuval birleştirmeye de girmez.
    if(!levhaModu()){ if(!tkCv.hidden){ tkCv.width = tkCv.width; tkCv.hidden = true; } return; }
    tkCv.hidden = false;
    const r = tkCv.getBoundingClientRect(), w = Math.round(r.width*dpr), h = Math.round(r.height*dpr);
    if(tkCv.width !== w || tkCv.height !== h){ tkCv.width = w; tkCv.height = h; }
    tkC.setTransform(1,0,0,1,0,0); tkC.clearRect(0, 0, w, h);
    const g = gorunen(), sx = (B[2]-B[0])/W, sy = (B[3]-B[1])/H;
    const lo0 = B[0] + (-ox/olcek - 4)*sx, lo1 = B[0] + ((g.w - ox)/olcek + 4)*sx;
    const la1 = B[3] - (-oy/olcek - 4)*sy, la0 = B[3] - ((h/dpr - oy)/olcek + 4)*sy;
    const icinde = k => !(k[2] < lo0 || k[0] > lo1 || k[3] < la0 || k[1] > la1);
    const kx = olcek/sx, ky = olcek/sy, birim = 1/Math.sqrt(kx*ky);
    // levha renkleri: y ekseni -enlem (resim kuzeyden güneye)
    tkC.setTransform(dpr*kx, 0, 0, dpr*ky, dpr*(ox - B[0]*kx), dpr*(oy + B[3]*ky));
    const K = TK.kesit; tkC.globalAlpha = 0.34; tkC.imageSmoothingEnabled = false;
    tkC.drawImage(TK.tuval, K[0], -K[3], K[2]-K[0], K[3]-K[1]); tkC.globalAlpha = 1;
    tkC.setTransform(dpr*kx, 0, 0, -dpr*ky, dpr*(ox - B[0]*kx), dpr*(oy + B[3]*ky));
    tkC.save(); tkC.beginPath(); tkC.rect(B[0], B[1], B[2]-B[0], B[3]-B[1]); tkC.clip();   // harita kutusunun dışı boş
    tkC.lineCap = "round"; tkC.lineJoin = "round";
    // volkan kuşakları (alan), sonra sınırlar, en üstte volkan üçgenleri
    for(const k of TK.kusaklar){ if(!icinde(k.kutu)) continue;
      tkC.fillStyle = k.sonuk ? "rgba(150,142,132,.28)" : "rgba(255,112,56,.26)"; tkC.fill(k.alanYol); }
    for(const s of TK.sinirlar){ if(!icinde(s.kutu)) continue;
      const tur = tkTur(s.s);
      tkC.strokeStyle = "rgba(11,17,22,.55)"; tkC.lineWidth = 3.4*birim; tkC.setLineDash([]); tkC.stroke(s.yol);
      tkC.strokeStyle = TK_RENK[tur]; tkC.lineWidth = 1.8*birim;
      tkC.setLineDash(s.s === "CRB" ? [5*birim, 3.5*birim] : []); tkC.stroke(s.yol); }
    tkC.setLineDash([]);
    // dişler: yakınsak sınırda üst levha tarafında üçgenler
    tkC.fillStyle = TK_RENK.yak;
    for(const s of TK.sinirlar){ if(!s.u || tkTur(s.s) !== "yak" || !icinde(s.kutu)) continue;
      const b = 4.2*birim, yol = new Path2D();
      boyunca(s.p, 16*birim, (x, y, tx, ty) => { const nx = -ty*s.u, ny = tx*s.u;
        yol.moveTo(x - tx*b*0.7, y - ty*b*0.7); yol.lineTo(x + nx*b*1.2, y + ny*b*1.2); yol.lineTo(x + tx*b*0.7, y + ty*b*0.7); yol.closePath(); });
      tkC.fill(yol); }
    // volkanlar: yay cephesinde ve yarıklarda üçgen (ekranda yukarı bakar)
    const ucgen = (yol, x, y, b) => { yol.moveTo(x - b, y - b*0.75); yol.lineTo(x + b, y - b*0.75); yol.lineTo(x, y + b); yol.closePath(); };
    for(const [liste, anahtar, aralik] of [[TK.kusaklar, "on", 30], [TK.yariklar, "p", 46]]){
      for(const k of liste){ if(!icinde(k.kutu)) continue;
        const yol = new Path2D(), b = 3.6*birim;
        boyunca(k[anahtar], aralik*birim, (x, y) => ucgen(yol, x, y, b));
        tkC.fillStyle = anahtar === "p" ? "#f2c14e" : k.sonuk ? "#8f887e" : "#ff6a3d";
        tkC.strokeStyle = "rgba(11,17,22,.7)"; tkC.lineWidth = 0.9*birim; tkC.fill(yol); tkC.stroke(yol); } }
    tkC.restore();
    // levha adları ve hızları: tohum noktasında, ekran uzayında
    tkC.setTransform(dpr, 0, 0, dpr, 0, 0);
    tkC.font = `600 11px system-ui, sans-serif`; tkC.textAlign = "center"; tkC.textBaseline = "middle";
    for(const L of Object.values(TK.levhalar)){ const [la, lo] = L.tohum;
      const X = ox + (lo-B[0])/sx*olcek, Y = oy + (B[3]-la)/sy*olcek;
      if(X < 30 || X > g.w - 30 || Y < g.ust + 20 || Y > g.alt - 20 || la > B[3] - 1 || la < B[1] + 1 || lo < B[0] + 1 || lo > B[2] - 1) continue;
      const hiz = L.hiz ? `${virgul(L.hiz.toFixed(1))} cm/yıl` : "sabit";
      tkC.lineWidth = 3; tkC.strokeStyle = "rgba(11,17,22,.8)"; tkC.fillStyle = "#f1ece2";
      tkC.strokeText(L.ad, X, Y - 7); tkC.fillText(L.ad, X, Y - 7);
      tkC.font = `11px system-ui, sans-serif`; tkC.fillStyle = "#cfc8bb"; tkC.strokeText(hiz, X, Y + 7); tkC.fillText(hiz, X, Y + 7);
      tkC.font = `600 11px system-ui, sans-serif`;
      if(L.hiz){ const [ve, vn] = L.v, m = Math.hypot(ve, vn) || 1, ux = ve/m, uy = -vn/m, ax = X, ay = Y + 30, u = 6 + 1.5*Math.min(4, m);
        tkC.strokeStyle = "rgba(11,17,22,.8)"; tkC.lineWidth = 4; tkC.beginPath(); tkC.moveTo(ax - ux*u, ay - uy*u); tkC.lineTo(ax + ux*u, ay + uy*u); tkC.stroke();
        tkC.strokeStyle = "#f1ece2"; tkC.lineWidth = 1.6; tkC.beginPath(); tkC.moveTo(ax - ux*u, ay - uy*u); tkC.lineTo(ax + ux*u, ay + uy*u);
        tkC.moveTo(ax + ux*u - ux*5 - uy*4, ay + uy*u - uy*5 + ux*4); tkC.lineTo(ax + ux*u, ay + uy*u); tkC.lineTo(ax + ux*u - ux*5 + uy*4, ay + uy*u - uy*5 - ux*4); tkC.stroke(); } }
  }
  // kart: levha, en yakın sınır (~250 km içinde), volkan kuşağı
  function tektSatiri(lon, lat){
    if(!levhaModu()) return "";
    const out = [], cz = Math.cos(lat*Math.PI/180), km = (a, b) => Math.hypot((a-lon)*cz, b-lat)*111.2;
    const L = TK.levhalar[TK.levhaAt(lon, lat)];
    if(L) out.push(`<b>Levha</b> ${L.ad} (${L.tur}) · ${L.hiz ? `${L.yon} ${virgul(L.hiz.toFixed(1))} cm/yıl` : "hızlar buna göre ölçülür"}`);
    let en = null, ed = 250;
    for(const s of TK.sinirlar){ const k = s.kutu; if(lon < k[0]-3 || lon > k[2]+3 || lat < k[1]-3 || lat > k[3]+3) continue;
      for(let i=0;i<s.p.length/2;i++){ const d = km(s.p[2*i], s.p[2*i+1]); if(d < ed){ ed = d; en = s; } } }
    if(en) out.push(`<b>Sınır</b> ${en.ad}, ~${Math.max(10, Math.round(ed/10)*10)} km · ${TK.siniflar[en.s] || en.s}${en.n ? " · " + en.n.replace(/^\[tasarım\]\s*/, "") : ""}${/^\[tasarım\]/.test(en.n) ? " <small>(okyanusta, tasarım)</small>" : ""}`);
    tkC.setTransform(1,0,0,1,0,0);
    const kus = TK.kusaklar.find(k => lon >= k.kutu[0] && lon <= k.kutu[2] && lat >= k.kutu[1] && lat <= k.kutu[3] && tkC.isPointInPath(k.alanYol, lon, lat));
    if(kus) out.push(`<b>Volkan</b> ${kus.sonuk ? "sönmüş yay kuşağı" : "etkin yay kuşağı"} · ${kus.ad}, bu kesimde yakınlaşma ~${virgul(kus.y.toFixed(1))} cm/yıl`);
    else { const yr = TK.yariklar.find(r => { for(let i=0;i<r.p.length/2;i++) if(km(r.p[2*i], r.p[2*i+1]) < 60) return true; return false; });
      if(yr) out.push(`<b>Volkan</b> yarık volkanizması, seyrek · ${yr.ad}`); }
    return out.map(t => `<div class="k-tk">${t}</div>`).join("");
  }

  /* Hareketli ruzgar: Windy/earth.nullschool usulu parcaciklar. Her parcacik
     hucre koordinatinda durur, her karede bulundugu yerdeki ruzgar kadar
     ilerler ve kisa bir iz birakir; iz her karede biraz soner. Parcaciklar
     60-110 karelik omurden sonra gorunen alanda rastgele yeniden dogar.
     Canvas2D ve CPU: en fazla 2000 parcacik telefonda rahat; hesap yalniz Dolasim
     sekmesi acik ve anahtar aciksa, sayfa gorunurken (rAF) doner. Harita
     kaydirilinca izler silinir, yoksa eski yerlerinde bulasik kalirlar. */
  const parcacik = (() => {
    const cv = $("#parcacik"), c = cv.getContext("2d");
    let P = null, sayi = 0, calisiyor = false, son = null, sonZaman = 0;
    const ac = () => katman==="dolasim" && ayar.parcacik && D.dol;
    // yalniz gorunen haritada dogar (yatay duzende dokun altina harcanmasin)
    function dogur(i){ const g = gorunen();
      const sx = Math.random()*g.w, sy = g.ust + Math.random()*(g.alt-g.ust);
      P[i*4] = (sx-ox)/olcek - 0.5; P[i*4+1] = (sy-oy)/olcek - 0.5; P[i*4+2] = 0; P[i*4+3] = 60 + Math.random()*50; }
    function kur(){ const r = cv.getBoundingClientRect();
      cv.width = Math.round(r.width*dpr); cv.height = Math.round(r.height*dpr);
      // dikeyde sayi eskisi gibi; yatayda yan dokun kapladigi pay dusulur
      sayi = Math.min(2000, Math.round(gorunen().w*r.height/300)); P = new Float32Array(sayi*4);
      for(let i=0;i<sayi;i++){ dogur(i); P[i*4+2] = Math.random()*P[i*4+3]; } c.clearRect(0, 0, cv.width, cv.height); }
    return {
      get calisiyor(){ return calisiyor; },
      gorunumDegisti(){ const g = ac();
        if(!g){ if(calisiyor){ calisiyor = false; c.clearRect(0, 0, cv.width, cv.height); cv.hidden = true; } return; }
        const imza = `${ox.toFixed(1)},${oy.toFixed(1)},${olcek.toFixed(4)},${canvas.width},${donem}`;
        if(!calisiyor){ calisiyor = true; cv.hidden = false; sonZaman = 0; kur(); }
        else if(imza !== son){ if(cv.width !== canvas.width) kur(); else c.clearRect(0, 0, cv.width, cv.height);
          for(let i=0;i<sayi;i++) dogur(i); }
        son = imza; },
      adim(){ if(!calisiyor) return;
        // Hiz ve iz uzunlugu 60 Hz'lik kareye gore tanimli; 90/120 Hz ekranda
        // parcaciklar 1.5-2 kat hizli akip izleri kisaliyordu (gece denetimi).
        // Adim gecen sureyle olceklenir; arka plandan donuste sicrama olmasin
        // diye 3 kareyle sinirli.
        const simdi = performance.now(), f = sonZaman ? Math.min(3, Math.max(0.25, (simdi - sonZaman)/16.67)) : 1; sonZaman = simdi;
        const m = donem<0 ? 12 : donem, U = D.dol.u[m], V = D.dol.v[m], ust = D.dol.ruzgar_ust, k = 0.38*f/olcek;
        // eski izleri sondur (hedef-icinde: yalniz alfa azalir, renk karismaz)
        c.globalCompositeOperation = "destination-in"; c.fillStyle = `rgba(0,0,0,${Math.pow(0.86, f).toFixed(3)})`; c.fillRect(0, 0, cv.width, cv.height);
        c.globalCompositeOperation = "source-over"; c.lineWidth = 1.1*dpr; c.lineCap = "round";
        const kova = [[], [], []];   // hiza gore uc parlaklik; ayni stille toplu cizim hizli
        for(let i=0;i<sayi;i++){ const j = i*4, x = P[j], y = P[j+1];
          if((P[j+2] += f) > P[j+3] || x < 0 || y < 0 || x > W-1 || y > H-1){ dogur(i); continue; }
          const u = dolOrnek(D, U, x, y), v = dolOrnek(D, V, x, y), h = Math.hypot(u, v);
          const nx = x + u*k, ny = y - v*k;   // ekranda ~0.38 px/kare her m/s icin
          kova[h < ust*0.25 ? 0 : h < ust*0.5 ? 1 : 2].push(ox + (x+0.5)*olcek, oy + (y+0.5)*olcek, ox + (nx+0.5)*olcek, oy + (ny+0.5)*olcek);
          P[j] = nx; P[j+1] = ny; }
        const g = gorunen();
        kova.forEach((a, t) => { c.strokeStyle = `rgba(240,236,226,${[0.4, 0.62, 0.85][t]})`; c.beginPath();
          for(let q=0;q<a.length;q+=4){ if(a[q+1] < g.ust || a[q+1] > g.alt) continue;
            c.moveTo(a[q]*dpr, a[q+1]*dpr); c.lineTo(a[q+2]*dpr, a[q+3]*dpr); }
          c.stroke(); });
      },
    };
  })();

  /* Ruzgar: akis cizgileri. Ekranda esit aralikli tohumlardan akis yonunde
     ileri-geri izlenir; bir cizgi baskasina ~d px yaklasinca durur (Jobard-
     Lefer'in sade hali), boylece cizgiler ust uste binmez ve alani esit
     doldurur. Hiz, cizginin kalinligi ve parlakligiyla okunur; yon, ucundaki
     kucuk okla. */
  function ruzgarCiz(r, g){
    const bicim = window.__ruzgarBicim || "cizgi";
    const m = donem<0 ? 12 : donem, U = D.dol.u[m], V = D.dol.v[m], ust = D.dol.ruzgar_ust;
    const hiz = (x, y) => { const hx = (x-ox)/olcek - 0.5, hy = (y-oy)/olcek - 0.5;
      if(hx < 0 || hy < 0 || hx > W-1 || hy > H-1 || y < g.ust || y > g.alt || x < 0 || x > r.width) return null;
      return [dolOrnek(D, U, hx, hy), -dolOrnek(D, V, hx, hy)]; };   // ekranda y asagi
    if(bicim === "ok"){
      const adim = 34; let ok = "";
      for(let y=g.ust+adim/2; y<g.alt; y+=adim) for(let x=adim/2; x<r.width; x+=adim){
        const w = hiz(x, y); if(!w) continue; const h = Math.hypot(w[0], w[1]); if(h < 0.3) continue;
        const L = Math.min(1, 0.35 + h/ust*1.3)*adim*0.78, dx = w[0]/h*L/2, dy = w[1]/h*L/2;
        const x2 = x+dx, y2 = y+dy, bx = -dx/L*2*5, by = -dy/L*2*5;
        ok += `M${(x-dx).toFixed(1)},${(y-dy).toFixed(1)}L${x2.toFixed(1)},${y2.toFixed(1)}`
          + `M${(x2+bx-by*0.6).toFixed(1)},${(y2+by+bx*0.6).toFixed(1)}L${x2.toFixed(1)},${y2.toFixed(1)}L${(x2+bx+by*0.6).toFixed(1)},${(y2+by-bx*0.6).toFixed(1)}`;
      }
      return `<path d="${ok}" fill="none" stroke="#0b1116" stroke-opacity=".6" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>`
        + `<path class="ruzgar" d="${ok}" fill="none" stroke="#ebe6dc" stroke-opacity=".9" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>`;
    }
    const d = 15, ADIM = 2.5, EN = 90, gw = Math.ceil(r.width/d)+1, gh = Math.ceil(r.height/d)+1;
    const dolu = new Uint8Array(gw*gh), hucre = (x, y) => ((y/d)|0)*gw + ((x/d)|0);
    const bos = (x, y, sahip) => { const cx = (x/d)|0, cy = (y/d)|0;
      for(let j=-1;j<=1;j++) for(let i=-1;i<=1;i++){ const k = (cy+j)*gw + cx+i;
        if(cy+j<0 || cx+i<0 || cy+j>=gh || cx+i>=gw) continue;
        if(dolu[k] && dolu[k] !== sahip){ const dx = (cx+i+0.5)*d - x, dy = (cy+j+0.5)*d - y; if(dx*dx+dy*dy < d*d*0.55) return false; } }
      return true; };
    const kademe = [[], [], [], []];   // hiza gore 4 kalinlik
    let no = 1;
    for(let sy = g.ust + d/2; sy < g.alt; sy += d*1.3) for(let sx = d/2 + ((sy/d)|0)%2*d*0.6; sx < r.width; sx += d*1.3){
      if(!bos(sx, sy, 0) || !hiz(sx, sy)) continue;
      const sahip = (no = no % 250 + 1), iz = (yon) => { const p = []; let x = sx, y = sy;
        for(let k=0;k<EN/ADIM;k++){ const w = hiz(x, y); if(!w) break; const h = Math.hypot(w[0], w[1]); if(h < 0.2) break;
          const nx = x + yon*w[0]/h*ADIM, ny = y + yon*w[1]/h*ADIM;
          if(!bos(nx, ny, sahip)) break; p.push([nx, ny, h]); x = nx; y = ny; }
        return p; };
      const geri = iz(-1).reverse(), ileri = iz(1), yol = [...geri, [sx, sy, 0], ...ileri];
      if(yol.length*ADIM < 14) continue;
      for(const [x, y] of yol) dolu[hucre(x, y)] = sahip;
      let hs = 0, n = 0; for(const q of yol) if(q[2]){ hs += q[2]; n++; } const hh = n ? hs/n : 0;
      let dd = `M${yol[0][0].toFixed(1)},${yol[0][1].toFixed(1)}`; for(let k=1;k<yol.length;k+=2) dd += `L${yol[k][0].toFixed(1)},${yol[k][1].toFixed(1)}`;
      // ucta ok: son iki noktanin yonunde
      const a = yol[yol.length-1], b = yol[Math.max(0, yol.length-3)], ax = a[0]-b[0], ay = a[1]-b[1], al = Math.hypot(ax, ay) || 1;
      const ux = ax/al*4.5, uy = ay/al*4.5;
      dd += `M${(a[0]-ux-uy*0.7).toFixed(1)},${(a[1]-uy+ux*0.7).toFixed(1)}L${a[0].toFixed(1)},${a[1].toFixed(1)}L${(a[0]-ux+uy*0.7).toFixed(1)},${(a[1]-uy-ux*0.7).toFixed(1)}`;
      kademe[Math.min(3, Math.floor(hh/ust*5))].push(dd);
    }
    let out = "";
    kademe.forEach((yollar, k) => { if(!yollar.length) return; const dd = yollar.join("");
      out += `<path d="${dd}" fill="none" stroke="#0b1116" stroke-opacity=".45" stroke-width="${(2.6+k*0.5).toFixed(1)}" stroke-linecap="round" stroke-linejoin="round"/>`
        + `<path class="ruzgar" d="${dd}" fill="none" stroke="#ebe6dc" stroke-opacity="${(0.55+k*0.13).toFixed(2)}" stroke-width="${(0.9+k*0.35).toFixed(2)}" stroke-linecap="round" stroke-linejoin="round"/>`; });
    return out;
  }

  /* --- katman ve donem --- */
  function katmanSec(k, d){
    katman = k; if(d !== undefined) donem = d;
    if(k==="iklim" || k==="arazi") donem = -1;
    if(k!=="iklim") izole = null;
    for(const b of $("#sekmeler").children) b.setAttribute("aria-selected", String(b.dataset.k===k));
    $("#donem").hidden = !(k==="sicaklik" || k==="yagis" || k==="kar" || k==="dolasim");
    for(const b of $("#donem").children) b.setAttribute("aria-checked", String(+b.dataset.d===donem));
    if(k!=="iklim"){ gor = gorunumKur(D, k, donem, ayar.bant);
      if(G){ G.kur("tAlan", gor.a, W, H, "L", true); G.kur("tLut", gor.lut, 256, 1, "RGB", true); } }
    if(!G) yedekBoya();
    $("#altbaslik").textContent = {iklim:"İklim sınıfları, Köppen-Geiger", arazi: TK && ayar.araziMod==="levha" ? "Levhalar, sınırlar ve volkan kuşakları" : BI && ayar.araziMod==="bitki" ? "Doğal bitki örtüsü, iklimden" : TP && ayar.araziMod==="toprak" ? "Toprak türleri, WRB" : YS && ayar.araziMod==="yasam" ? "Genel yaşanabilirlik, net birincil üretim" : "Arazi, yükseklik",
      sicaklik: ayar.sicMod!=="ort" && gunlukAl(D) ? "Sıcaklık, "+SIC_MOD[ayar.sicMod]+", "+(donem<0 ? (ayar.sicMod==="tepe" ? "yılın en sıcak ayı" : ayar.sicMod==="dip" ? "yılın en soğuk ayı" : "yıllık ortalama") : AYLAR[donem])
        : "Sıcaklık, "+(donem<0 ? "yıllık ortalama" : AYLAR[donem]),
      yagis:"Yağış, "+(donem<0 ? "yıllık toplam" : AYLAR[donem]),
      kar:donem<0 ? "Kar örtüsü, yerde kaldığı ay sayısı" : "Yerdeki kar, "+AYLAR[donem]+" ortası",
      // yillikta oklar 12 ayin bileske (net) ruzgari: yil icinde donen yerlerde
      // zayif kalir, "ortalama" ruzgar hizi sanilmasin (gece denetimi)
      dolasim:"Rüzgâr ve akıntılar, "+(donem<0 ? "yıllık net rüzgâr" : AYLAR[donem])}[k];
    aciklamaYaz(); boyut();
    // ay seridi acilinca dok ve kart yukselir; secili hucre kartin altinda kalmasin
    if(sec!==null && !D.land[sec] && k!=="dolasim"){ sec = null; $("#kart").hidden = true; }
    if(sec!==null){ D.land[sec] ? kartYaz() : denizKartYaz(); gorunurYap(oy + (((sec/W)|0) + 0.5)*olcek); }
  }
  $("#donem").innerHTML = `<button role="radio" data-d="-1" aria-checked="true">Yıl</button>` +
    AY_HARF.map((h,m)=>`<button role="radio" data-d="${m}" aria-checked="false" aria-label="${AYLAR[m]}">${h}</button>`).join("");
  $("#donem").addEventListener("click", e => { const b = e.target.closest("button"); if(b) katmanSec(katman, +b.dataset.d); });
  // parmagi seridin ustunde kaydirarak aylari taramak
  $("#donem").addEventListener("pointermove", e => { if(e.pointerType==="mouse" && e.buttons!==1) return;
    const b = document.elementFromPoint(e.clientX, e.clientY);
    if(b && b.parentNode===$("#donem") && +b.dataset.d!==donem) katmanSec(katman, +b.dataset.d); });
  $("#sekmeler").addEventListener("click", e => { const b = e.target.closest("button"); if(b) katmanSec(b.dataset.k); });

  /* --- lejant / aciklama satiri --- */
  const paylar = (()=>{ const c={}; let t=0;
    for(let i=0;i<N;i++){ if(!D.land[i]) continue; const w=D.agirlik[(i/W)|0], k=D.KCODE[String(D.kop[i])];
      t+=w; if(k) c[k]=(c[k]||0)+w; }
    for(const k in c) c[k]/=t; return c; })();
  const grupPay = {}; for(const k in paylar) grupPay[k[0]] = (grupPay[k[0]]||0) + paylar[k];

  function aciklamaYaz(){
    const el = $("#aciklama");
    if(katman==="iklim"){
      if(izole){ el.innerHTML = `<div class="izole"><span><b>${izole}</b> · ${D.KNAME[izole]||""} · %${virgul((paylar[izole]*100).toFixed(1))}</span><button id="izole-kaldir">Hepsi</button></div>`;
        $("#izole-kaldir").onclick = () => { izole=null; listeYaz(); aciklamaYaz(); if(!G) yedekBoya(); ciz(); }; return; }
      const g = Object.keys(GRUP).filter(g=>grupPay[g]);
      el.innerHTML = `<button class="gruplar" id="siniflar-ac"><span class="cubuk">${g.map(k=>`<i style="width:${grupPay[k]*100}%;background:${GRUP_RENK[k]}"></i>`).join("")}</span><span class="ok">Sınıflar</span></button>`
        + `<div class="gruplar-etiket">${g.map(k=>`<span>${GRUP[k]} <b>%${Math.round(grupPay[k]*100)}</b></span>`).join("")}</div>`;
      $("#siniflar-ac").onclick = () => sayfaAc("siniflar");
      return;
    }
    const o = gor.olcek;
    const dolNot = katman==="dolasim" ? `<div class="dol-ust"><div class="secim kucuk" role="radiogroup" aria-label="Zemin">`
      + `<button role="radio" data-zemin="sst" aria-checked="${ayar.dolZemin!=="hiz"}">Deniz sıcaklığı</button>`
      + `<button role="radio" data-zemin="hiz" aria-checked="${ayar.dolZemin==="hiz"}">Rüzgâr hızı</button></div>`
      + `<button class="canli" id="parcacik-ac" aria-pressed="${ayar.parcacik}">Hareketli</button></div>`
      + `<div class="dol-not"><span><i class="ok-ruzgar"></i>rüzgâr</span><span><i class="ak s"></i>sıcak akıntı</span><span><i class="ak k"></i>soğuk akıntı</span></div>` : "";
    // sicaklik: ortalama / gunduz / gece / ayin tipik tepesi ve dibi (gunlukHazirla)
    const sicNot = katman==="sicaklik" && gunlukAl(D) ? `<div class="dol-ust"><div class="secim kucuk" role="radiogroup" aria-label="Sıcaklık türü">`
      + [["ort","Ortalama"],["gunduz","Gündüz"],["gece","Gece"],["tepe","Tepe"],["dip","Dip"]].map(([k,t]) =>
        `<button role="radio" data-sicmod="${k}" aria-checked="${ayar.sicMod===k}">${t}</button>`).join("") + `</div></div>` : "";
    const araziSec = katman==="arazi" && (TK || BI || TP || YS) ? `<div class="dol-ust"><div class="secim kucuk" role="radiogroup" aria-label="Arazi görünümü">`
      + [["yukseklik","Yükseklik",true], ["levha","Levhalar",!!TK], ["bitki","Bitki örtüsü",!!BI], ["toprak","Toprak",!!TP], ["yasam","Yaşanabilirlik",!!YS]].filter(a => a[2]).map(([k, t]) =>
        `<button role="radio" data-arazimod="${k}" aria-checked="${(ayar.araziMod||"yukseklik")===k}">${t}</button>`).join("") + `</div></div>` : "";
    if(katman==="arazi" && BI && ayar.araziMod==="bitki"){
      const liste = Object.entries(BJ.biyomlar).filter(([, b]) => b.pay >= 0.005).sort((a, b) => b[1].pay - a[1].pay);
      el.innerHTML = araziSec + `<div class="bk-not">` + liste.map(([, b]) =>
        `<span><i style="background:rgb(${b.renk.join(",")})"></i>${b.ad.replace(/ \(.*\)/, "")} <b>%${Math.round(b.pay*100)}</b></span>`).join("") + `</div>`;
      return; }
    if(katman==="arazi" && YS && ayar.araziMod==="yasam"){
      const dar = ayar.yasamKiyi === "dar" && resimler.yasamDar, pk = dar ? "pay_dar" : "pay";
      const kiyiSec = resimler.yasamDar ? `<div class="dol-ust"><div class="secim kucuk" role="radiogroup" aria-label="Nehir çevresi">`
        + [["genis","Geniş, yumuşak"],["dar","Nehrin yanı"]].map(([k, t]) =>
          `<button role="radio" data-yasamkiyi="${k}" aria-checked="${dar ? k==="dar" : k==="genis"}">${t}</button>`).join("") + `</div></div>` : "";
      el.innerHTML = araziSec + kiyiSec + `<div class="bk-not">` + Object.entries(YJ.siniflar).filter(([, c]) => c[pk] >= 0.005).map(([, c]) =>
        `<span><i style="background:rgb(${c.renk.join(",")})"></i>${c.ad} <b>%${Math.round(c[pk]*100)}</b></span>`).join("") + `</div>`;
      return; }
    if(katman==="arazi" && TP && ayar.araziMod==="toprak"){
      const liste = Object.entries(TPJ.topraklar).filter(([, t]) => t.pay >= 0.005).sort((a, b) => b[1].pay - a[1].pay);
      el.innerHTML = araziSec + `<div class="bk-not">` + liste.map(([, t]) =>
        `<span><i style="background:rgb(${t.renk.join(",")})"></i>${t.ad} <b>%${Math.round(t.pay*100)}</b></span>`).join("") + `</div>`;
      return; }
    if(katman==="arazi" && TK && ayar.araziMod==="levha"){
      el.innerHTML = araziSec + `<div class="tk-not"><span><i class="yak"></i>yakınsak</span><span><i class="ira"></i>ıraksak</span>`
        + `<span><i class="don"></i>dönüşüm</span><span><b class="vk"></b>volkan</span><span><b class="vk s"></b>sönmüş</span></div>`;
      return; }
    el.innerHTML = araziSec + dolNot + sicNot + `<div class="olcek"><div class="serit" style="background:${o.serit}"></div><div class="etiketler">`
      + o.etiket.map((e,k)=>`<span style="left:${e.x*100}%">${e.t}${k===o.etiket.length-1?` <span class="birim">${o.birim}</span>`:""}</span>`).join("")
      + `</div></div>`;
    etiketCakismasi();
  }
  // Yuzdelik olcekte degerler uclarda birbirine yakin duser; dar ekranda bir
  // ara etiket komsusunun ustune biniyordu ("1.1645.610 mm/yil", 360 px,
  // gece denetimi). Komsusuyla cakisan ara etiket gizlenir, uclar kalir.
  function etiketCakismasi(){
    const sp = [...document.querySelectorAll("#aciklama .etiketler>span")];
    for(const e of sp) e.style.visibility = "";
    for(let i=sp.length-2;i>=1;i--){ const r = sp[i].getBoundingClientRect(), sag = sp[i+1];
      if(sag.style.visibility !== "hidden" && r.right > sag.getBoundingClientRect().left - 6) sp[i].style.visibility = "hidden"; }
    for(let i=1;i<sp.length-1;i++){ if(sp[i].style.visibility === "hidden") continue;
      const r = sp[i].getBoundingClientRect(), sol = sp.slice(0, i).reverse().find(e => e.style.visibility !== "hidden");
      if(sol && sol.getBoundingClientRect().right > r.left - 6) sp[i].style.visibility = "hidden"; }
  }
  addEventListener("resize", () => etiketCakismasi());

  $("#aciklama").addEventListener("click", e => {
    const z = e.target.closest("[data-zemin]"), p = e.target.closest("#parcacik-ac"), sm = e.target.closest("[data-sicmod]"), am = e.target.closest("[data-arazimod]"), yk = e.target.closest("[data-yasamkiyi]");
    if(yk){ ayar.yasamKiyi = yk.dataset.yasamkiyi; ayarYaz(); YK = null; katmanSec("arazi"); ciz(); }
    if(am){ ayar.araziMod = am.dataset.arazimod; ayarYaz(); katmanSec("arazi"); ciz(); }
    if(sm){ ayar.sicMod = sm.dataset.sicmod; ayarYaz(); katmanSec("sicaklik"); }
    if(z){ ayar.dolZemin = z.dataset.zemin; ayarYaz(); katmanSec("dolasim"); }
    if(p){ ayar.parcacik = !ayar.parcacik; ayarYaz(); aciklamaYaz(); ciz(); }
  });

  function listeYaz(){
    const aile = {}; for(const k of Object.keys(paylar).sort((a,b)=>paylar[b]-paylar[a])) (aile[k[0]] = aile[k[0]]||[]).push(k);
    $("#sinif-listesi").innerHTML = Object.keys(GRUP).filter(g=>aile[g]).map(g =>
      `<div class="grup"><h4>${GRUP[g]}<span>%${virgul((grupPay[g]*100).toFixed(1))}</span></h4>` + aile[g].map(k =>
        `<button class="satir" data-sinif="${k}" aria-pressed="${izole===k}"><i style="background:${KPAL[k]}"></i>`
        + `<span class="kod">${k}</span><span class="ad">${D.KNAME[k]||k}<small>${KREF[k]||""}</small></span>`
        + `<span class="pay">%${virgul((paylar[k]*100).toFixed(paylar[k]<0.01?2:1))}</span></button>`).join("") + `</div>`).join("");
  }
  $("#sinif-listesi").addEventListener("click", e => { const b = e.target.closest("[data-sinif]"); if(!b) return;
    izole = izole===b.dataset.sinif ? null : b.dataset.sinif; listeYaz(); sayfaKapat(); katmanSec("iklim"); });

  /* --- sayfalar --- */
  function sayfaAc(ad){ if(ad === "ayar") return cekmeceAc(); $("#sayfa-"+ad).hidden = false; }
  function sayfaKapat(){ for(const s of document.querySelectorAll(".sayfa")) s.hidden = true; }

  /* Ayarlar asagidan kayan bir cekmece: yarida durur, harita ustte gorunur
     kalir ve ayar degisikligi aninda gorulur. Tutamaktan (ya da basliktan)
     yukari cekilince tam ekrana acilir, asagi itilince kapanir. */
  const cek = $("#sayfa-ayar");
  const cekUst = () => window.innerHeight - ($(".marka").getBoundingClientRect().bottom + 12);
  const cekYari = () => Math.round(window.innerHeight * 0.48);
  function cekYukseklik(h, anim){ cek.style.transition = anim ? "height .22s ease" : "none"; cek.style.height = h + "px"; }
  function cekmeceAc(){ cek.hidden = false; cekYukseklik(0, false); cek.getBoundingClientRect(); cekYukseklik(cekYari(), true); }
  { let bas = null;
    const tut = e => { const b = e.target.closest(".tutamak, #sayfa-ayar > header");
      if(!b || e.target.closest("button")) return; bas = {y: e.clientY, h: cek.getBoundingClientRect().height};
      cek.setPointerCapture(e.pointerId); };
    cek.addEventListener("pointerdown", tut);
    cek.addEventListener("pointermove", e => { if(!bas) return;
      cekYukseklik(Math.max(60, Math.min(cekUst(), bas.h - (e.clientY - bas.y))), false); });
    const birak = e => { if(!bas) return; const h = cek.getBoundingClientRect().height, hiz = bas.h - h; bas = null;
      if(h < cekYari()*0.55){ cekYukseklik(0, true); setTimeout(() => { cek.hidden = true; }, 220); return; }
      // en yakin durak: yari ya da tam
      cekYukseklik(Math.abs(h - cekYari()) < Math.abs(h - cekUst()) ? cekYari() : cekUst(), true); };
    cek.addEventListener("pointerup", birak); cek.addEventListener("pointercancel", birak);
    // ekran donunce cekmece yeni ekrana sigmali: yatayda eski yukseklik ekrani
    // asiyor, tutamak ustte gorunmez kaliyordu (olculdu: 405 px, ekran 390)
    addEventListener("resize", () => { if(cek.hidden) return;
      const h = cek.getBoundingClientRect().height;
      cekYukseklik(h >= cekUst() - 2 ? cekUst() : Math.min(cekYari(), cekUst()), false); }); }
  for(const b of document.querySelectorAll("[data-kapat]")) b.addEventListener("click", sayfaKapat);
  $("#menu").addEventListener("click", () => sayfaAc("ayar"));
  $("#sigdir").addEventListener("click", sigdir);

  // iki kabartma kaynagi: editor gorseli ya da gri tonlu yukseklik haritasi.
  // Gri doku eski veride yoksa secenek kapali kalir.
  // uc kabartma kaynagi: birlesik (varsayilan), editor gorseli, gri yukseklik
  // haritasi. Veride olmayanin dugmesi gizlenir, secim olana duser.
  function kabartmaKur(){ if(!G) return; G.kur("tKab", KAB[ayar.kabartmaKaynak] || resimler.kabartma, 0, 0, "L", true); }
  const kaynakDugme = [...document.querySelectorAll("#kabartma-kaynak button")];
  // golge kapaliyken kaynak secimi etkisiz: soluk ve dokunulmaz (gece denetimi)
  function kaynakYaz(){ for(const b of kaynakDugme){ b.setAttribute("aria-checked", String(b.dataset.kaynak===ayar.kabartmaKaynak)); b.disabled = !ayar.kabartma; }
    $("#kabartma-kaynak").classList.toggle("pasif", !ayar.kabartma); }
  for(const b of kaynakDugme) b.hidden = !KAB[b.dataset.kaynak];
  if(kaynakDugme.filter(b=>!b.hidden).length < 2) $("#kabartma-kaynak").hidden = true;
  for(const b of kaynakDugme) b.addEventListener("click", () => {
    ayar.kabartmaKaynak = b.dataset.kaynak; ayarYaz(); kaynakYaz(); kabartmaKur(); BK = null; TPK = null; YK = null; ciz(); });
  kaynakYaz();
  const suKolDugme = [...document.querySelectorAll("#su-kollar button")];
  function suKolYaz(){ for(const b of suKolDugme){ b.setAttribute("aria-checked", String(b.dataset.sukol===ayar.suKol)); b.disabled = !ayar.su; }
    $("#su-kollar").classList.toggle("pasif", !ayar.su); }
  for(const b of suKolDugme) b.addEventListener("click", () => { ayar.suKol = b.dataset.sukol; ayarYaz(); suKolYaz(); ciz(); });
  if(!D.su){ $("#ay-su").closest("label").hidden = true; $("#su-kollar").hidden = true; }
  suKolYaz();
  for(const [id, k] of [["ay-kabartma","kabartma"],["ay-piksel","piksel"],["ay-izgara","izgara"],["ay-deniz","deniz"],["ay-bant","bant"],["ay-su","su"]]){
    const el = $("#"+id); el.checked = ayar[k];
    el.addEventListener("change", () => { ayar[k] = el.checked; ayarYaz(); kaynakYaz(); suKolYaz(); if(k==="kabartma"){ BK = null; TPK = null; YK = null; } katmanSec(katman); });
  }
  $("#kunye").innerHTML = D.J.facts.map(([b,v])=>`<dt>${b}</dt><dd>${virgul(v)}</dd>`).join("")
    + `<dt>hücre</dt><dd>${virgul(((B[2]-B[0])/W).toFixed(2))}°</dd>`;
  const gecen = D.R.sanity.filter(c=>c.gecti).length;
  $("#tutarlilik-say").textContent = `${gecen}/${D.R.sanity.length}`;
  $("#tutarlilik").innerHTML = D.R.sanity.map(c=>`<div class="denetim${c.gecti?"":" dustu"}"><span>${c.ad}<small>${virgul(c.aciklama).replace(/(^|[\s(])-(?=\d)/g, "$1\u2212")}</small></span></div>`).join("");
  $("#surum").textContent = `Veri sürümü ${D.J.surum} · üretildi ${tarih(D.J.uretim)} · kabartma: ${D.doku.kabartma}`;

  /* --- hucre karti --- */
  function kartYaz(){
    const i = sec, x = i%W, y = (i/W)|0, lat = D.enlem(y), lon = B[0] + (x+0.5)*(B[2]-B[0])/W;
    const konum = virgul(`${Math.abs(lat).toFixed(1)}°${lat>=0?"K":"G"} ${Math.abs(lon).toFixed(1)}°${lon>=0?"D":"B"}`);
    const el = $("#kart-icerik"); $("#kart").hidden = false;
    const j = D.karaSira[i], ad = D.KCODE[String(D.kop[i])];
    const T = D.tAy.map(a=>a[j]), P = D.pAy.map(a=>a[j]);
    const gun = gunlukAl(D) ? AYLAR.map((_, m) => gunlukAl(D).ay(j, m)) : null;
    const sicak = T.indexOf(Math.max(...T)), soguk = T.indexOf(Math.min(...T)), r = v => eksi(Math.round(v));
    el.innerHTML = `<div class="k-ust"><i style="background:${KPAL[ad]||"#888"}"></i><div><h3>${D.KNAME[ad]||"—"}</h3>`
      + `<small><b>${ad||""}</b>${KREF[ad] ? "Dünya'da: "+KREF[ad] : ""}</small></div></div>`
      + `<div class="k-sayilar"><div><em>${r(D.tYil[j])}°</em><span>ortalama</span></div>`
      + `<div><em>${r(T[sicak])}°</em><span>${AYLAR[sicak]}</span></div>`
      + `<div><em>${r(T[soguk])}°</em><span>${AYLAR[soguk]}</span></div>`
      + `<div><em>${Math.round(D.pYil[j]).toLocaleString("tr-TR")}</em><span>mm/yıl</span></div></div>`
      + klimagram(T, P, donem, karAl(D).ortuAy[j], karAl(D).kar.map(a=>a[j]), gun)
      + gunSatiri(gun)
      + karSatiri(j)
      + suSatiri(lon, lat)
      + tektSatiri(lon, lat)
      + bitkiSatiri(lon, lat)
      + toprakSatiri(lon, lat)
      + yasamSatiri(lon, lat)
      + `<div class="k-alt"><span>${konum} · ${eksi(Math.round(D.elev[i]).toLocaleString("tr-TR"))} m</span><span>sıcaklık °C · yağış mm</span></div>`;
  }
  // "Temmuz: gündüz 33°, gece 22° · her yıl ~41° / ~18° · 30 yılda bir ~46°"
  // yillikta: yilin en sicak gunu ve en soguk gecesi (ayi ile)
  function gunSatiri(gun){
    if(!gun) return "";
    const r = v => eksi(Math.round(v)) + "°";
    if(donem >= 0){ const o = gun[donem];
      return `<div class="k-gun"><b>${AYLAR[donem]}</b> gündüz ${r(o.gunduz)}, gece ${r(o.gece)} · ayın tipik tepesi ${r(o.tepe)}, dibi ${r(o.dip)} · 30 yılda bir ${r(o.rekS)} / ${r(o.rekC)}</div>`; }
    const s = gun.reduce((a, o, m) => o.tepe > gun[a].tepe ? m : a, 0), c = gun.reduce((a, o, m) => o.dip < gun[a].dip ? m : a, 0);
    const fark = gun.reduce((t, o) => t + (o.gunduz - o.gece)/12, 0);
    return `<div class="k-gun"><b>Gün</b> gündüz-gece farkı ~${Math.round(fark)}° · yılın en sıcak günü ~${r(gun[s].tepe)} (${AYLAR[s]}), en soğuk gecesi ~${r(gun[c].dip)} (${AYLAR[c]}) · 30 yılda bir ${r(gun[s].rekS)} / ${r(gun[c].rekC)}</div>`;
  }
  // "Göl: tatlı, taşar · 10.066 km², en derin 248 m" ya da
  // "Nehir: burada ~450 m³/s · ana kol, 2.690 km, ağızda 20.250 m³/s".
  // Nehir: noktaya en yakın kol (ekranda ~10 px ya da bir hücre içinde);
  // görünmeyen kademeler de sayılır, kart her zaman bilgi verir.
  const KADEME_AD = ["", "büyük ana kol", "ana kol", "kol", "küçük kol"];
  function suSatiri(lon, lat){
    if(!SU || !ayar.su) return "";
    const bin = n => Math.round(n).toLocaleString("tr-TR");
    suC.setTransform(1,0,0,1,0,0);
    for(const L of SU.goller){ const k = L.kutu;
      if(lon < k[0] || lon > k[2] || lat < k[1] || lat > k[3] || !suC.isPointInPath(L.yol, lon, lat, "evenodd")) continue;
      return `<div class="k-su"><b>Göl</b> ${L.tuz ? "kapalı, tuzlu" : "tatlı, taşar"} · ${bin(L.alan)} km², en derin ${bin(L.derin)} m, yüzey ${bin(L.sev)} m`
        + `${L.koken && L.koken !== "havza" ? " · köken: "+L.koken : ""}</div>`; }
    let delta = "";
    { let en = null, ed = 1e9;
      for(const d of SU.deltalar){ const km = Math.hypot((d.agiz[1]-lon)*Math.cos(lat*Math.PI/180), d.agiz[0]-lat)*111.2;
        if(km < d.r*1.1 && km < ed){ ed = km; en = d; } }
      if(en) delta = `<div class="k-su"><b>Delta</b> ${en.tur} · ${en.hedef === "göl" ? "göle dökülür" : "denize dökülür"} · yılda ~${bin(en.Qs)} milyon ton çökel</div>`; }
    const sx = (B[2]-B[0])/W, tol = Math.max(0.6*sx, 10/olcek*sx), cz = Math.cos(lat*Math.PI/180);
    let en = null, ed = tol*tol;
    for(const n of SU.nehirler){ const k = n.kutu;
      if(lon < k[0]-tol || lon > k[2]+tol || lat < k[1]-tol || lat > k[3]+tol) continue;
      for(let i=0;i<n.p.length/2;i++){ const dx = (n.p[2*i]-lon)*cz, dy = n.p[2*i+1]-lat, d = dx*dx + dy*dy;
        if(d < ed || (en && d === ed && n.Q > en.n.Q)){ ed = d; en = {n, q: n.q[i]}; } } }
    if(!en) return delta;
    const yuv = v => v >= 1000 ? Math.round(v/100)*100 : v >= 100 ? Math.round(v/10)*10 : Math.round(v);
    const parca = [`burada ~${bin(yuv(en.q))} m³/s`, `${KADEME_AD[en.n.k]}, ${bin(en.n.L)} km`];
    if(en.n.Q > en.q*1.05) parca.push(`aşağı ucunda ${bin(yuv(en.n.Q))} m³/s`);
    return `<div class="k-su"><b>Nehir</b> ${parca.join(" · ")}</div>` + delta;
  }
  // "Kar: Kasım–Mart yağar · örtü 4 ay, en çok Şubat'ta 120 mm su"
  function karSatiri(j){
    const K = karAl(D), yag = ayAraligi(K.yagar[j]);
    if(!yag && !K.ortu[j]) return `<div class="k-kar yok">Kar yok</div>`;
    const sw = K.swe.map(a=>a[j]), en = sw.indexOf(Math.max(...sw));
    const ortu = K.kalici[j] ? "kalıcı, erimiyor (buzul)"
      : K.ortu[j] ? `örtü ${K.ortu[j]===12 ? "bütün yıl" : K.ortu[j]+" ay"} · en kalın ${AYLAR[en]}, ${Math.round(sw[en])} mm su` : "yerde tutunmuyor";
    return `<div class="k-kar"><b>Kar</b> ${yag ? yag+" yağar" : "seyrek"} · ${ortu}</div>`;
  }
  // Dolasim sekmesinde okyanusa dokununca: deniz yuzeyi sicakligi ve ruzgar
  // Denize dokununca (her sekmede): denizcilik icin motorun verdigi ne varsa.
  // Derinlik, gelgit ve dalga verisi YOK; gosterilmez. Tropikal firtina satiri
  // bir kosul esigidir (deniz suyu >= 26,5 °C ve enlem 5-30°), motor siklon
  // cozmez.
  function denizKartYaz(){
    const i = sec, x = i%W, y = (i/W)|0, lat = D.enlem(y), lon = B[0] + (x+0.5)*(B[2]-B[0])/W;
    const konum = virgul(`${Math.abs(lat).toFixed(1)}°${lat>=0?"K":"G"} ${Math.abs(lon).toFixed(1)}°${lon>=0?"D":"B"}`);
    const r1 = v => eksi(Math.round(v*10)/10).replace(".", ","), rad = Math.PI/180;
    // en yakin kara: buyuk daire uzakligi ve yonu (gece denetimi: "acik deniz"
    // her okyanus hucresine yaziliyordu)
    const k = D.yakin[i], kx = k%W, kyy = (k/W)|0;
    const klat = D.enlem(kyy)*rad, klon = (B[0] + (kx+0.5)*(B[2]-B[0])/W)*rad, la1 = lat*rad, lo1 = lon*rad;
    const km = YARICAP*Math.acos(Math.min(1, Math.sin(la1)*Math.sin(klat) + Math.cos(la1)*Math.cos(klat)*Math.cos(lo1-klon)));
    const kmYaz = v => (v < 200 ? Math.round(v/10)*10 : Math.round(v/50)*50).toLocaleString("tr-TR");
    const karaYon = YONE[Math.round(((Math.atan2(Math.sin(klon-lo1)*Math.cos(klat), Math.cos(la1)*Math.sin(klat) - Math.sin(la1)*Math.cos(klat)*Math.cos(klon-lo1))/rad) + 360) % 360 / 45) % 8];
    const karaSinif = D.KCODE[String(D.kop[k])], kiyi = km < 30 ? "kıyıya yakın" : `kıyıya ~${kmYaz(km)} km`;
    const satirlar = [];
    let sayilar = "", serit = "";
    if(D.dol){
      const m = donem<0 ? 12 : donem;
      const T = D.dol.sst.slice(0,12).map(a=>dolOrnek(D, a, x, y));
      const U = AYLAR.map((_, a) => dolOrnek(D, D.dol.u[a], x, y)), V = AYLAR.map((_, a) => dolOrnek(D, D.dol.v[a], x, y));
      const HZ = AYLAR.map((_, a) => dolOrnek(D, D.dol.hiz[a], x, y));
      const hiz = dolOrnek(D, D.dol.hiz[m], x, y), u = dolOrnek(D, D.dol.u[m], x, y), v = dolOrnek(D, D.dol.v[m], x, y);
      const bf = beaufort(hiz);
      sayilar = `<div><em>${r1(donem<0 ? T.reduce((p,c)=>p+c,0)/12 : T[donem])}°</em><span>su</span></div>`
        + `<div><em>${r1(Math.min(...T))}..${r1(Math.max(...T))}°</em><span>yıl içinde</span></div>`
        + `<div><em>${r1(hiz)}</em><span>m/s rüzgâr</span></div><div><em>${bf}</em><span>Beaufort</span></div>`;
      // yon: aylik vektor hizin yarisindan kucukse tek bir yon yok (gece denetimi)
      const yon = (a, uu, vv) => Math.hypot(uu, vv) >= 0.5*a ? nereden(uu, vv) : null;
      const buYon = yon(hiz, u, v);
      satirlar.push(`<b>Rüzgâr</b> ${buYon ? buYon + " esiyor" : "yönü mevsimle değişiyor"} · ${BFT_AD[bf]}`);
      const sert = HZ.indexOf(Math.max(...HZ)), sakin = HZ.indexOf(Math.min(...HZ));
      satirlar.push(`<b>En sert</b> ${AYLAR[sert]} ${r1(HZ[sert])} m/s (${beaufort(HZ[sert])} bft) · <b>en sakin</b> ${AYLAR[sakin]} ${r1(HZ[sakin])} m/s`);
      // 12 ay: okun yonu ruzgarin gittigi yon, sayi Beaufort
      serit = `<div class="k-serit">` + AYLAR.map((a, j) => { const tek = yon(HZ[j], U[j], V[j]);
        const aci = Math.atan2(U[j], V[j])/rad;
        return `<div${j===donem ? ' class="sec"' : ""}><span>${a[0]}</span><i style="${tek ? `transform:rotate(${aci.toFixed(0)}deg)` : "opacity:.35"}">${tek ? "↑" : "·"}</i><b>${beaufort(HZ[j])}</b></div>`; }).join("") + `</div>`;
      // buz: motor okyanusu donma noktasinda kelepceler
      const buz = T.map(t => t <= -1.5);
      satirlar.push(`<b>Buz</b> ${buz.some(Boolean) ? `${aySirasi(buz)} (${buz.filter(Boolean).length} ay deniz buzu)` : "yok, yıl boyu açık"}`);
      const tf = T.map(t => t >= 26.5 && Math.abs(lat) >= 5 && Math.abs(lat) <= 30);
      if(tf.some(Boolean)) satirlar.push(`<b>Tropikal fırtına koşulları</b> ${aySirasi(tf)} <small>(su ≥ 26,5 °C; motor siklon çözmez)</small>`);
    }
    // akinti: yola en yakin nokta; genisligin yarisi icindeyse "icinde"
    let ak = null;
    // "Ic Deniz - mevsimsel genlik" bir akinti degil, mevsimsel sicaklik
    // ayari; akis yonu yazilirsa yaniltir
    for(const a of D.akintilar){ if(/genlik/i.test(a.ad)) continue; for(let s = 0; s+1 < a.yol.length; s++){
      const [x1, y1] = a.yol[s], [x2, y2] = a.yol[s+1], c = Math.cos(lat*rad);
      const dx = (x2-x1)*c, dy = y2-y1, px = (lon-x1)*c, py = lat-y1, L = dx*dx+dy*dy || 1e-9;
      const t = Math.max(0, Math.min(1, (px*dx+py*dy)/L)), d = Math.hypot(px-t*dx, py-t*dy)*KM_DERECE;
      if(!ak || d < ak.d) ak = {d, a, dx, dy}; } }
    if(ak && ak.d < ak.a.genislik_km){
      const ad = ak.a.ad.includes(" - ") ? ak.a.ad.split(" - ").slice(1).join(" - ") : ak.a.ad;
      const akYon = YONE[Math.round(((Math.atan2(ak.dx, ak.dy)/rad) + 360) % 360 / 45) % 8];
      satirlar.push(`<b>Akıntı</b> ${ak.a.anomali >= 0 ? "sıcak" : "soğuk"} (${ak.a.anomali >= 0 ? "+" : ""}${r1(ak.a.anomali)} °C), `
        + `${ak.d < ak.a.genislik_km/2 ? "içinde" : `~${kmYaz(ak.d)} km yakında`}, akış ${akYon} · <small>${ad}</small>`);
    } else satirlar.push(`<b>Akıntı</b> yakında tanımlı akıntı yok`);
    if(D.pyil.a[i]) satirlar.push(`<b>Yağış</b> ${Math.round(kodCoz(D.pyil, D.pyil.a[i])).toLocaleString("tr-TR")} mm/yıl, denize düşen`);
    satirlar.push(`<b>En yakın kara</b> ${km < 30 ? "hemen yanında" : `~${kmYaz(km)} km ${karaYon}`} · ${D.KNAME[karaSinif] || karaSinif} (${karaSinif})`);
    $("#kart").hidden = false;
    $("#kart-icerik").innerHTML = `<div class="k-ust"><i style="background:#2b4a5a"></i><div><h3>Deniz</h3>`
      + `<small>${donem<0 ? "yıllık ortalama" : AYLAR[donem]} · ${kiyi}</small></div></div>`
      + (sayilar ? `<div class="k-sayilar">${sayilar}</div>` : "") + serit
      + satirlar.map(t => `<div class="k-gun">${t}</div>`).join("")
      + tektSatiri(lon, lat)
      + `<div class="k-alt"><span>${konum}</span><span>derinlik verisi yok</span></div>`;
  }
  function kartKapat(){ sec = null; $("#kart").hidden = true; ciz(); }
  // secilen hucre acilan kartin altinda kaldiysa haritayi yukari kaydir
  function gorunurYap(y){ const ust = $("#kart").getBoundingClientRect().top - 24, bas = $(".marka").getBoundingClientRect().bottom + 24;
    if(y > ust){ const k = Math.min(y - ust, y - bas); if(k > 0){ oy -= k; ciz(); } } }
  $("#kart-kapat").addEventListener("click", kartKapat);

  /* --- dokunma: tek parmak kaydir, iki parmak yakinlastir, dokun = hucre sec --- */
  const ptr = new Map(); let g0 = null, dokun = null, sonDokun = null;
  const harita = $("#harita");
  const yerel = e => { const r = harita.getBoundingClientRect(); return {x:e.clientX-r.left, y:e.clientY-r.top}; };
  function hareketBasla(){ const p = [...ptr.values()]; g0 = {ox, oy, olcek, p:p.map(q=>({...q}))};
    if(p.length>=2){ g0.orta = {x:(p[0].x+p[1].x)/2, y:(p[0].y+p[1].y)/2}; g0.d = Math.hypot(p[0].x-p[1].x, p[0].y-p[1].y)||1; } }
  function yakinlas(px, py, f){ const once = olcek; olcek *= f; sinirla(); const k = olcek/once;
    ox = px-(px-ox)*k; oy = py-(py-oy)*k; ciz(); }
  harita.addEventListener("pointerdown", e => { harita.setPointerCapture(e.pointerId); ptr.set(e.pointerId, yerel(e)); hareketBasla();
    dokun = ptr.size===1 ? {...yerel(e), t:performance.now()} : null; });
  harita.addEventListener("pointermove", e => { if(!ptr.has(e.pointerId)) return; ptr.set(e.pointerId, yerel(e));
    const p = [...ptr.values()];
    if(dokun && Math.hypot(p[0].x-dokun.x, p[0].y-dokun.y) > 8) dokun = null;
    if(p.length===1 && g0.p.length===1){ ox = g0.ox+(p[0].x-g0.p[0].x); oy = g0.oy+(p[0].y-g0.p[0].y); ciz(); }
    else if(p.length>=2 && g0.orta){ const orta = {x:(p[0].x+p[1].x)/2, y:(p[0].y+p[1].y)/2}, d = Math.hypot(p[0].x-p[1].x, p[0].y-p[1].y);
      olcek = g0.olcek*d/g0.d; sinirla(); const k = olcek/g0.olcek;
      ox = orta.x-(g0.orta.x-g0.ox)*k; oy = orta.y-(g0.orta.y-g0.oy)*k; ciz(); } });
  function birak(e){ if(!ptr.has(e.pointerId)) return; const q = ptr.get(e.pointerId); ptr.delete(e.pointerId); ciz();
    if(dokun && e.type==="pointerup" && performance.now()-dokun.t < 350){ const now = performance.now();
      // Tek dokunma hucreyi HEMEN secer (onceden ikinci dokunusu beklemek icin
      // 290 ms ertelenirdi; kart gec geliyordu). Cift dokunma gelirse ilk
      // dokunusun etkisi (secim, kart, kaydirma) geri alinir ve yakinlastirilir.
      if(sonDokun && now-sonDokun.t < 300 && Math.hypot(q.x-sonDokun.x, q.y-sonDokun.y) < 30){
        const o = sonDokun.once; ox = o.ox; oy = o.oy; sec = o.sec;
        if(sec === null) $("#kart").hidden = true; else (D.land[sec] ? kartYaz() : denizKartYaz());
        yakinlas(q.x, q.y, 2); sonDokun = null; }
      else {
        sonDokun = {...q, t:now, once:{ox, oy, sec}};
        const x = Math.floor((q.x-ox)/olcek), y = Math.floor((q.y-oy)/olcek);
        const i = (x<0||y<0||x>=W||y>=H) ? null : y*W+x;
        if(i===null) kartKapat();
        else { sec = i; D.land[i] ? kartYaz() : denizKartYaz(); gorunurYap(q.y); ciz(); } } }
    dokun = null; hareketBasla(); }
  harita.addEventListener("pointerup", birak); harita.addEventListener("pointercancel", birak);
  // deltaMode 1 = satir (Firefox): piksele cevrilir, yoksa tik basina ~%0.5
  // yakinlasiyordu (gece denetimi)
  harita.addEventListener("wheel", e => { e.preventDefault(); sonTeker = performance.now(); const q = yerel(e);
    yakinlas(q.x, q.y, Math.exp(-e.deltaY*(e.deltaMode===1 ? 16 : e.deltaMode===2 ? 400 : 1)*0.0015));
    clearTimeout(harita.tekerSon); harita.tekerSon = setTimeout(ciz, 170); }, {passive:false});

  // Bilgisayarda (baslat.bat) klavye: Esc acik olani kapatir, oklar kaydirir,
  // +/- yakinlastirir, 0 kitaya sigdirir (gece denetimi: klavye hic yoktu).
  addEventListener("keydown", e => {
    if(e.target.closest && e.target.closest("input, textarea")) return;
    const g = gorunen(), cx = g.w/2, cy = (g.ust + g.alt)/2, adim = 60;
    if(e.key === "Escape"){ if(!cek.hidden || document.querySelector(".sayfa:not([hidden])")) sayfaKapat(), cek.hidden = true; else if(sec !== null) kartKapat(); }
    else if(e.key === "+" || e.key === "=") yakinlas(cx, cy, 1.4);
    else if(e.key === "-") yakinlas(cx, cy, 1/1.4);
    else if(e.key === "0") sigdir();
    else if(e.key.startsWith("Arrow")){ const d = {ArrowLeft:[adim,0], ArrowRight:[-adim,0], ArrowUp:[0,adim], ArrowDown:[0,-adim]}[e.key];
      ox += d[0]; oy += d[1]; ciz(); }
    else return;
    e.preventDefault(); });
  addEventListener("resize", () => { boyut(); sigdir(); });
  listeYaz(); katmanSec("iklim"); sigdir(); requestAnimationFrame(kare);
  $("#yukleniyor").hidden = true;
  (window.requestIdleCallback || (f => setTimeout(f, 300)))(() => karAl(D));
  // Android geri tusu: acik kart, cekmece ya da sayfa once kapanir; once
  // dogrudan uygulamadan cikiliyordu (gece denetimi). Biri acilinca gecmise
  // tek durum itilir; geri gelince hepsi kapanir. Arayuzden kapatilinca itilen
  // durum geri alinir ki gecmis sismesin.
  { const ustler = [$("#kart"), ...document.querySelectorAll(".sayfa")];
    let itildi = false, geriBekle = false;
    new MutationObserver(() => {
      const acik = ustler.some(e => !e.hidden);
      if(acik && !itildi){ history.pushState({atlasUst: 1}, ""); itildi = true; }
      else if(!acik && itildi){ itildi = false; geriBekle = true; history.back(); }
    }).observe(document.body, {subtree: true, attributes: true, attributeFilter: ["hidden"]});
    addEventListener("popstate", () => {
      if(geriBekle){ geriBekle = false; return; }
      if(!itildi) return;
      itildi = false; sayfaKapat(); if(!$("#kart").hidden) kartKapat(); }); }
  window.__atlas = {D, durum:()=>({katman, donem, ox, oy, olcek, sec, webgl:!!G})};   // dogrulama betikleri icin
}

/* 12 aylik iklim grafigi: cubuk yagis, cizgi sicaklik. Secili ay vurgulu. */
function klimagram(T, P, secili, ortuAy = 0, kar = null, gun = null){
  const w = 330, h = 92, sol = 28, sag = 34, ust = 6, alt = 16, iw = w-sol-sag, ih = h-ust-alt;
  const guzel = v => { for(const x of [10,20,25,50,100,150,200,250,300,400,500,750,1000,1500,2000,3000]) if(v <= x) return x;
    return Math.ceil(v/1000)*1000; };
  const pm = guzel(Math.max(40, ...P));
  // gunduz-gece bandi varsa olcek onu da kapsar
  const tAlt = gun ? Math.min(...gun.map(o=>o.gece)) : Math.min(...T), tUst = gun ? Math.max(...gun.map(o=>o.gunduz)) : Math.max(...T);
  const t0 = Math.floor((tAlt-1)/5)*5, t1 = Math.ceil((tUst+1)/5)*5;
  const X = i => sol + (i+0.5)*iw/12, Yt = t => ust + (t1-t)/(t1-t0)*ih, bw = iw/12*0.58;
  let s = `<svg class="klimagram" viewBox="0 0 ${w} ${h}" role="img" aria-label="Aylık sıcaklık ve yağış">`;
  for(const t of [t0, t1]) s += `<line x1="${sol}" x2="${w-sag}" y1="${Yt(t)}" y2="${Yt(t)}" stroke="rgba(214,205,186,.10)"/>`;
  if(t0 < 0 && t1 > 0) s += `<line x1="${sol}" x2="${w-sag}" y1="${Yt(0)}" y2="${Yt(0)}" stroke="rgba(214,205,186,.28)" stroke-dasharray="2 3"/>`;
  P.forEach((p,i) => { const bh = p/pm*ih;
    s += `<rect x="${(X(i)-bw/2).toFixed(1)}" y="${(ust+ih-bh).toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(bh,0.5).toFixed(1)}" fill="#3f7f8c" fill-opacity="${i===secili?1:.72}"${i===secili?' stroke="#d2a45c" stroke-width="1.2"':""}/>`; });
  // yagisin kar olan kismi cubugun ustunde beyaz; kar ortusu aylarin altinda serit
  if(kar) kar.forEach((k,i) => { const kh = Math.min(k, P[i])/pm*ih; if(kh < 0.5) return;
    s += `<rect x="${(X(i)-bw/2).toFixed(1)}" y="${(ust+ih-P[i]/pm*ih).toFixed(1)}" width="${bw.toFixed(1)}" height="${kh.toFixed(1)}" fill="#e8eef3" fill-opacity=".82"/>`; });
  for(let i=0;i<12;i++) if(ortuAy>>i & 1)
    s += `<rect x="${(X(i)-iw/24).toFixed(1)}" y="${ust+ih+1}" width="${(iw/12).toFixed(1)}" height="2" fill="#e8eef3" fill-opacity=".7"/>`;
  // gunduz (ust kenar) ile gece (alt kenar) arasi soluk bant
  if(gun) s += `<polygon points="${[...gun.map((o,i)=>`${X(i).toFixed(1)},${Yt(o.gunduz).toFixed(1)}`), ...gun.map((o,i)=>`${X(i).toFixed(1)},${Yt(o.gece).toFixed(1)}`).reverse()].join(" ")}" fill="#d2a45c" fill-opacity=".16" stroke="#d2a45c" stroke-opacity=".35" stroke-width=".6"/>`;
  s += `<polyline fill="none" stroke="#d2a45c" stroke-width="1.7" stroke-linejoin="round" points="${T.map((t,i)=>`${X(i).toFixed(1)},${Yt(t).toFixed(1)}`).join(" ")}"/>`;
  T.forEach((t,i) => { s += `<circle cx="${X(i).toFixed(1)}" cy="${Yt(t).toFixed(1)}" r="${i===secili?3:1.8}" fill="#d2a45c"/>`; });
  s += `<text x="${sol-5}" y="${Yt(t1)+3}" text-anchor="end">${eksi(t1)}°</text><text x="${sol-5}" y="${Yt(t0)+3}" text-anchor="end">${eksi(t0)}°</text>`;
  s += `<text x="${w-sag+5}" y="${ust+3}">${pm}</text><text x="${w-sag+5}" y="${ust+ih+3}">0</text>`;
  AY_HARF.forEach((a,i) => { s += `<text x="${X(i).toFixed(1)}" y="${h-4}" text-anchor="middle"${i===secili?' style="fill:#e4dfd3"':""}>${a}</text>`; });
  return s + `</svg>`;
}

/* ---- acilis ve guncelleme ---- */
// taze: service worker onbellege dusmesin. Dusunce "Guncellemeleri denetle"
// cevrimdisiyken de "Guncel" diyordu (gece denetimi).
async function veriCek(taze){
  const r = await fetch("data/atlas.json", {cache:"no-cache", headers: taze ? {"X-Taze": "1"} : {}});
  if(!r.ok) throw new Error("data/atlas.json okunamadı ("+r.status+")");
  return r.json();
}
async function acilis(){
  let J, resimler;
  try {
    J = await veriCek();
    const [doku, yukseklik, kabartma, kabartmaGri, kabartmaBir, dolasim, su, tekt, levha, bitkiJ, bitki, bitkiVeri, toprakJ, toprak, toprakVeri, yasamJ, yasam, yasamVeri, yasamDar, yasamDarVeri] = await Promise.all([
      ...["data/doku.png","data/yukseklik.png","data/kabartma.jpg"].map(resimYukle),
      resimYukle("data/kabartma_gri.jpg").catch(() => null),     // eski veride yok
      resimYukle("data/kabartma_bir.jpg").catch(() => null),
      resimYukle("data/dolasim.png").catch(() => null),
      // su katmani istege bagli: dosya yoksa ya da bozuksa harita yine acilir
      fetch("data/su.json", {cache:"no-cache"}).then(r => r.ok ? r.json() : null).catch(() => null),
      // tektonik katman da istege bagli (tektonik/uygulama.py)
      fetch("data/tektonik.json", {cache:"no-cache"}).then(r => r.ok ? r.json() : null).catch(() => null),
      resimYukle("data/levha.png").catch(() => null),
      // bitki örtüsü de isteğe bağlı (bitki/bitki.py)
      fetch("data/bitki.json", {cache:"no-cache"}).then(r => r.ok ? r.json() : null).catch(() => null),
      resimYukle("data/bitki.png").catch(() => null),
      resimYukle("data/bitki_veri.png").catch(() => null),
      // toprak türleri de isteğe bağlı (toprak/toprak.py)
      fetch("data/toprak.json", {cache:"no-cache"}).then(r => r.ok ? r.json() : null).catch(() => null),
      resimYukle("data/toprak.png").catch(() => null),
      resimYukle("data/toprak_veri.png").catch(() => null),
      // genel yaşanabilirlik de isteğe bağlı (yasam/yasam.py)
      fetch("data/yasam.json", {cache:"no-cache"}).then(r => r.ok ? r.json() : null).catch(() => null),
      resimYukle("data/yasam.png").catch(() => null),
      resimYukle("data/yasam_veri.png").catch(() => null),
      resimYukle("data/yasam_dar.png").catch(() => null),
      resimYukle("data/yasam_dar_veri.png").catch(() => null)]);
    resimler = {doku, yukseklik, kabartma, kabartmaGri, kabartmaBir, dolasim, su, tekt, levha, bitkiJ, bitki, bitkiVeri, toprakJ, toprak, toprakVeri, yasamJ, yasam, yasamVeri, yasamDar, yasamDarVeri};
  } catch(e){ $("#yukleniyor").innerHTML = `<span>Atlas yüklenemedi<br><small style="text-transform:none;letter-spacing:0">${e.message}. İlk açılış için internet bağlantısı gerekli; sonra çevrimdışı da açılır.</small></span>`; return; }
  try { const once = localStorage.getItem("veri-surum");
    if(once && once!==J.surum) setTimeout(()=>bildir("Yeni veri yüklendi · "+tarih(J.uretim)), 600);
    localStorage.setItem("veri-surum", J.surum); } catch(_){}
  try { baslat(J, resimler); }
  catch(e){ console.error(e); $("#yukleniyor").innerHTML = `<span>Atlas açılamadı<br><small style="text-transform:none;letter-spacing:0">${e.message}</small></span>`; }
}

if("serviceWorker" in navigator){
  // Yalniz ESKI bir service worker'in yerine yenisi gecince yenile. Ilk
  // kurulumda da controllerchange atesleniyor (clients.claim) ve olay anında
  // controller dolu oldugu icin eski kontrol ilk acilisi da yeniliyordu:
  // sayfa iki kez yukleniyordu (gece denetimi).
  let yenilendi = false;
  const oncekiDenetci = !!navigator.serviceWorker.controller;
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if(yenilendi || !oncekiDenetci) return; yenilendi = true; location.reload(); });
  navigator.serviceWorker.register("sw.js", {updateViaCache:"none"}).then(r=>r.update()).catch(()=>{});
}
document.addEventListener("click", async e => {
  if(e.target.id !== "guncelle") return;
  // service worker guncellemesi beklenmez: cevrimdisiyken uzun asili kalip
  // eski "Guncel" bildirimini ekranda birakiyordu (gece denetimi)
  navigator.serviceWorker?.getRegistration().then(r => r?.update()).catch(() => {});
  bildir("Denetleniyor…");
  try { const J = await veriCek(true);
    // karsilastirma ekrandaki veriyle: yerel kayit engelliyse (gizli sekme)
    // yeni veri "Guncel" diye geciliyordu (gece denetimi). veri-surum burada
    // yazilmaz: acilis farki gorup "Yeni veri yuklendi" desin.
    let once = window.__atlas?.D?.J?.surum ?? null; if(!once) try{ once = localStorage.getItem("veri-surum"); }catch(_){}
    if(once && once!==J.surum) location.reload();
    else bildir("Güncel · veri "+J.surum);
  } catch(err){
    // cevrimiciyken istek dusuyorsa en olasi sebep Cloudflare Access oturumunun
    // dolmasi (giris sayfasina yonlendirme CORS'ta duser); cozum yeniden acmak
    bildir(navigator.onLine === false ? "İnternet yok, önbellekteki sürüm açık"
      : "Sunucuya ulaşılamadı. Oturum dolmuş olabilir: uygulamayı kapatıp yeniden aç", 5000); }
});
acilis();
