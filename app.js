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
  dolZemin:"sst", parcacik:false},
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
  const havuz = parcalar => { let t=0; for(const p of parcalar) t+=p.length;
    const s = new Float64Array(t); let k=0; for(const p of parcalar) for(let j=0;j<p.length;j++) s[k++]=p[j]; return s.sort(); };
  const ayDegerleri = (enc, ham) => { const o=[]; for(let m=0;m<12;m++){ const a=new Float32Array(n);
      for(let j=0;j<n;j++) a[j]=kodCoz(enc, ham[m*n+j]); o.push(a); } return o; };
  const tAy = ayDegerleri(Tk, Tm), pAy = ayDegerleri(Pk, Pm);
  const karaDeger = f => { const a=new Float32Array(n); for(let i=0;i<N;i++) if(land[i]) a[karaSira[i]]=kodCoz(f, f.a[i]); return a; };
  const tYil = karaDeger(tyil), pYil = karaDeger(pyil);

  return { J, R, W, H, N, B:R.bounds, land, kop, tyil, pyil, elev, karaSira, n, Tk, Pk, Tm, Pm, tAy, pAy, tYil, pYil,
    dol: null, akintilar: R.akintilar || [],
    yakin, agirlik, enlem,
    havuzT: havuz([...tAy, tYil]), havuzP: havuz(pAy), havuzPY: havuz([pYil]),
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
const PUSULA = ["kuzeyden","kuzeydoğudan","doğudan","güneydoğudan","güneyden","güneybatıdan","batıdan","kuzeybatıdan"];
// ruzgar geldigi yonle adlandirilir: akis guneye ise "kuzeyden"
const nereden = (u, v) => PUSULA[Math.round(((Math.atan2(-u, -v)*180/Math.PI) + 360) % 360 / 45) % 8];

// yuzdelik: havuzdaki orta sira (esit degerler ortadan)
function yuzdelik(s, x){ const n=s.length; if(!n) return 0.5;
  let a=0,b=n; while(a<b){ const m=(a+b)>>1; if(s[m]<x) a=m+1; else b=m; } const alt=a;
  b=n; while(a<b){ const m=(a+b)>>1; if(s[m]<=x) a=m+1; else b=m; }
  return (alt+a)/2/n; }

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
  if(katman==="arazi"){
    const ust = D.doku.yukseklik_ust;
    for(let i=0;i<N;i++){ const e=D.elev[yakin[i]]; a[i] = Math.round(Math.sqrt(Math.max(e,0)/ust)*255); }
    for(let b=0;b<256;b++){ const c=araziRenk((b/255)**2*ust); lut.set(c.map(v=>v|0), b*3); }
    const etiket=[0,500,1500,3000,6000].filter(m=>m<=ust*1.02);
    return {a, lut, olcek:{serit:`linear-gradient(90deg,${Array.from({length:24},(_,k)=>css(araziRenk((k/23)**2*ust))).join(",")})`,
      etiket: etiket.map(m=>({x:Math.sqrt(m/ust), t:m.toLocaleString("tr-TR")})), birim:"m"}};
  }
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
    etiket:[0,.25,.5,.75,1].map(q=>({x:q, t:fmt(hv[Math.min(hv.length-1, Math.round(q*(hv.length-1)))])}))}};
}

/* ================================================================ cizim */
const VS = `attribute vec2 p; void main(){ gl_Position = vec4(p, 0.0, 1.0); }`;
const vec3s = h => hex(h).map(v=>(v/255).toFixed(4)).join(",");
const FS = `
precision highp float;
uniform vec2 uRes; uniform float uDpr; uniform vec3 uView; uniform vec2 uGrid; uniform vec4 uBounds;
uniform sampler2D tAlan, tLut, tKop, tPal, tDoku, tDokuN, tYuk, tKab;
uniform int uMod; uniform float uPiksel, uKabartma, uIzgara, uIzole, uOlcek, uZemin;
const vec3 DERIN = vec3(${vec3s(OKYANUS_DERIN)});
const vec3 KIYI = vec3(${vec3s(OKYANUS_KIYI)});
void main(){
  vec2 ekran = vec2(gl_FragCoord.x, uRes.y - gl_FragCoord.y) / uDpr;
  vec2 hucre = (ekran - uView.xy) / uView.z;
  vec2 uv = hucre / uGrid;
  vec2 muv = (floor(hucre) + 0.5) / uGrid;
  bool icinde = uv.x >= 0.0 && uv.y >= 0.0 && uv.x < 1.0 && uv.y < 1.0;
  vec4 dk = texture2D(tDoku, uv);
  vec3 renk = icinde ? mix(KIYI, DERIN, dk.g) : DERIN;
  if(uMod == 3 && icinde){   // dolasim: okyanus deniz yuzeyi sicakligiyla
    float sv = uPiksel > 0.5 ? texture2D(tAlan, muv).r : texture2D(tAlan, uv).r;
    renk = texture2D(tLut, vec2((sv * 255.0 + 0.5) / 256.0, 0.5)).rgb; }
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
    "uMod","uPiksel","uKabartma","uIzgara","uIzole","uOlcek","uZemin"]) U[ad] = gl.getUniformLocation(pr, ad);
  const birimler = {tAlan:0, tLut:1, tKop:2, tPal:3, tDoku:4, tDokuN:5, tYuk:6, tKab:7};
  const doku = {};
  function kur(ad, veri, w, h, bicim, suz){
    let t = doku[ad]; if(!t) t = doku[ad] = gl.createTexture();
    gl.activeTexture(gl.TEXTURE0 + birimler[ad]); gl.bindTexture(gl.TEXTURE_2D, t);
    const f = bicim==="L" ? gl.LUMINANCE : (bicim==="RGBA" ? gl.RGBA : gl.RGB);
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
  // kabartma kaynaklari (kabartmaKur GL kurulurken cagrilir, once tanimli olmali)
  const KAB = {bir: resimler.kabartmaBir, editor: resimler.kabartma, gri: resimler.kabartmaGri};
  if(!KAB[ayar.kabartmaKaynak]) ayar.kabartmaKaynak = KAB.bir ? "bir" : "editor";
  if(!D.dol) $("[data-k=dolasim]").hidden = true;   // eski veride dolasim yok
  const canvas = $("#gl"), kaplama = $("#kaplama");
  let G = null;
  try { G = glKur(canvas); if(G && G.enBuyuk < Math.max(D.doku.w, D.doku.h)) G = null; }
  catch(e){ console.error(e); G = null; }
  const yedek = G ? null : canvas.getContext("2d");

  const palet = new Uint8Array(32*4);
  for(const [kod, ad] of Object.entries(D.KCODE)){ const c = hex(KPAL[ad] || D.J.data.koppen_colors[ad]);
    palet.set([c[0],c[1],c[2],255], (+kod)*4); }
  const kodNo = {}; for(const [kod, ad] of Object.entries(D.KCODE)) kodNo[ad] = +kod;

  if(G){
    // model okyanus hucrelerine de sinif yazar; piksel gorunumu karayi
    // "kod > 0" diye ayirdigi icin dokuda okyanus 0 olmali
    const kopKara = new Uint8Array(N); for(let i=0;i<N;i++) if(D.land[i]) kopKara[i] = D.kop[i];
    G.kur("tKop", kopKara, W, H, "L", false);
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

  function gorunen(){
    const r = canvas.getBoundingClientRect();
    const ust = $(".marka").getBoundingClientRect().bottom + 8;
    const alt = $("#dok").getBoundingClientRect().top - 8;
    return {w:r.width, h:r.height, ust, alt};
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
    const w = W*olcek, h = H*olcek, px = g.w*0.5;
    ox = Math.min(px, Math.max(g.w - w - px, ox)); oy = Math.min(g.alt - 60, Math.max(g.ust + 60 - h, oy));
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
      else if(D.land[i]){ if(katman==="iklim") c = [palet[D.kop[i]*4], palet[D.kop[i]*4+1], palet[D.kop[i]*4+2]];
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
        gl.uniform1f(U.uIzole, izole ? kodNo[izole] : 0);
        gl.uniform1f(U.uOlcek, D.doku.olcek);
        gl.uniform1f(U.uZemin, ayar.dolZemin==="hiz" ? 1 : 0);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
      } else {
        const c = yedek; c.setTransform(1,0,0,1,0,0); c.fillStyle = OKYANUS_DERIN; c.fillRect(0,0,canvas.width,canvas.height);
        c.imageSmoothingEnabled = false; c.setTransform(dpr*olcek,0,0,dpr*olcek,dpr*ox,dpr*oy); c.drawImage(yedekTuval, 0, 0);
      }
      parcacik.gorunumDegisti();   // once: kaplama parcacik acikken akis cizgisi cizmesin
      kaplamaCiz();
    }
    parcacik.adim();
    requestAnimationFrame(kare);
  }

  function kaplamaCiz(){
    const r = canvas.getBoundingClientRect(); kaplama.setAttribute("viewBox", `0 0 ${r.width} ${r.height}`);
    let s = "";
    if(ayar.izgara){ const g = gorunen();
      for(const la of [60,30,0,-30]){ const y = oy + (B[3]-la)/(B[3]-B[1])*H*olcek;
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
    const r = canvas.getBoundingClientRect(), g = gorunen(), km = olcek/((B[2]-B[0])/W*111.2);   // ekran px / km
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

  /* Hareketli ruzgar: Windy/earth.nullschool usulu parcaciklar. Her parcacik
     hucre koordinatinda durur, her karede bulundugu yerdeki ruzgar kadar
     ilerler ve kisa bir iz birakir; iz her karede biraz soner. Parcaciklar
     60-110 karelik omurden sonra gorunen alanda rastgele yeniden dogar.
     Canvas2D ve CPU: en fazla 2000 parcacik telefonda rahat; hesap yalniz Dolasim
     sekmesi acik ve anahtar aciksa, sayfa gorunurken (rAF) doner. Harita
     kaydirilinca izler silinir, yoksa eski yerlerinde bulasik kalirlar. */
  const parcacik = (() => {
    const cv = $("#parcacik"), c = cv.getContext("2d");
    let P = null, sayi = 0, calisiyor = false, son = null;
    const ac = () => katman==="dolasim" && ayar.parcacik && D.dol;
    function dogur(i){ const g = gorunen(), r = cv.getBoundingClientRect();
      const sx = Math.random()*r.width, sy = g.ust + Math.random()*(g.alt-g.ust);
      P[i*4] = (sx-ox)/olcek - 0.5; P[i*4+1] = (sy-oy)/olcek - 0.5; P[i*4+2] = 0; P[i*4+3] = 60 + Math.random()*50; }
    function kur(){ const r = cv.getBoundingClientRect();
      cv.width = Math.round(r.width*dpr); cv.height = Math.round(r.height*dpr);
      sayi = Math.min(2000, Math.round(r.width*r.height/300)); P = new Float32Array(sayi*4);
      for(let i=0;i<sayi;i++){ dogur(i); P[i*4+2] = Math.random()*P[i*4+3]; } c.clearRect(0, 0, cv.width, cv.height); }
    return {
      get calisiyor(){ return calisiyor; },
      gorunumDegisti(){ const g = ac();
        if(!g){ if(calisiyor){ calisiyor = false; c.clearRect(0, 0, cv.width, cv.height); cv.hidden = true; } return; }
        const imza = `${ox.toFixed(1)},${oy.toFixed(1)},${olcek.toFixed(4)},${canvas.width},${donem}`;
        if(!calisiyor){ calisiyor = true; cv.hidden = false; kur(); }
        else if(imza !== son){ if(cv.width !== canvas.width) kur(); else c.clearRect(0, 0, cv.width, cv.height);
          for(let i=0;i<sayi;i++) dogur(i); }
        son = imza; },
      adim(){ if(!calisiyor) return;
        const m = donem<0 ? 12 : donem, U = D.dol.u[m], V = D.dol.v[m], ust = D.dol.ruzgar_ust, k = 0.38/olcek;
        // eski izleri sondur (hedef-icinde: yalniz alfa azalir, renk karismaz)
        c.globalCompositeOperation = "destination-in"; c.fillStyle = "rgba(0,0,0,0.86)"; c.fillRect(0, 0, cv.width, cv.height);
        c.globalCompositeOperation = "source-over"; c.lineWidth = 1.1*dpr; c.lineCap = "round";
        const kova = [[], [], []];   // hiza gore uc parlaklik; ayni stille toplu cizim hizli
        for(let i=0;i<sayi;i++){ const j = i*4, x = P[j], y = P[j+1];
          if(++P[j+2] > P[j+3] || x < 0 || y < 0 || x > W-1 || y > H-1){ dogur(i); continue; }
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
    $("#donem").hidden = !(k==="sicaklik" || k==="yagis" || k==="dolasim");
    for(const b of $("#donem").children) b.setAttribute("aria-checked", String(+b.dataset.d===donem));
    if(k!=="iklim"){ gor = gorunumKur(D, k, donem, ayar.bant);
      if(G){ G.kur("tAlan", gor.a, W, H, "L", true); G.kur("tLut", gor.lut, 256, 1, "RGB", true); } }
    if(!G) yedekBoya();
    $("#altbaslik").textContent = {iklim:"İklim sınıfları, Köppen-Geiger", arazi:"Arazi, yükseklik",
      sicaklik:"Sıcaklık, "+(donem<0 ? "yıllık ortalama" : AYLAR[donem]),
      yagis:"Yağış, "+(donem<0 ? "yıllık toplam" : AYLAR[donem]),
      dolasim:"Rüzgâr ve akıntılar, "+(donem<0 ? "yıllık ortalama" : AYLAR[donem])}[k];
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
      if(izole){ el.innerHTML = `<div class="izole"><span><b>${izole}</b> · ${D.KNAME[izole]||""} · %${(paylar[izole]*100).toFixed(1)}</span><button id="izole-kaldir">Hepsi</button></div>`;
        $("#izole-kaldir").onclick = () => { izole=null; listeYaz(); aciklamaYaz(); ciz(); }; return; }
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
    el.innerHTML = dolNot + `<div class="olcek"><div class="serit" style="background:${o.serit}"></div><div class="etiketler">`
      + o.etiket.map((e,k)=>`<span style="left:${e.x*100}%">${e.t}${k===o.etiket.length-1?` <span class="birim">${o.birim}</span>`:""}</span>`).join("")
      + `</div></div>`;
  }

  $("#aciklama").addEventListener("click", e => {
    const z = e.target.closest("[data-zemin]"), p = e.target.closest("#parcacik-ac");
    if(z){ ayar.dolZemin = z.dataset.zemin; ayarYaz(); katmanSec("dolasim"); }
    if(p){ ayar.parcacik = !ayar.parcacik; ayarYaz(); aciklamaYaz(); ciz(); }
  });

  function listeYaz(){
    const aile = {}; for(const k of Object.keys(paylar).sort((a,b)=>paylar[b]-paylar[a])) (aile[k[0]] = aile[k[0]]||[]).push(k);
    $("#sinif-listesi").innerHTML = Object.keys(GRUP).filter(g=>aile[g]).map(g =>
      `<div class="grup"><h4>${GRUP[g]}<span>%${(grupPay[g]*100).toFixed(1)}</span></h4>` + aile[g].map(k =>
        `<button class="satir" data-sinif="${k}" aria-pressed="${izole===k}"><i style="background:${KPAL[k]}"></i>`
        + `<span class="kod">${k}</span><span class="ad">${D.KNAME[k]||k}<small>${KREF[k]||""}</small></span>`
        + `<span class="pay">%${(paylar[k]*100).toFixed(paylar[k]<0.01?2:1)}</span></button>`).join("") + `</div>`).join("");
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
    cek.addEventListener("pointerup", birak); cek.addEventListener("pointercancel", birak); }
  for(const b of document.querySelectorAll("[data-kapat]")) b.addEventListener("click", sayfaKapat);
  $("#menu").addEventListener("click", () => sayfaAc("ayar"));
  $("#sigdir").addEventListener("click", sigdir);

  // iki kabartma kaynagi: editor gorseli ya da gri tonlu yukseklik haritasi.
  // Gri doku eski veride yoksa secenek kapali kalir.
  // uc kabartma kaynagi: birlesik (varsayilan), editor gorseli, gri yukseklik
  // haritasi. Veride olmayanin dugmesi gizlenir, secim olana duser.
  function kabartmaKur(){ if(!G) return; G.kur("tKab", KAB[ayar.kabartmaKaynak] || resimler.kabartma, 0, 0, "L", true); }
  const kaynakDugme = [...document.querySelectorAll("#kabartma-kaynak button")];
  function kaynakYaz(){ for(const b of kaynakDugme) b.setAttribute("aria-checked", String(b.dataset.kaynak===ayar.kabartmaKaynak)); }
  for(const b of kaynakDugme) b.hidden = !KAB[b.dataset.kaynak];
  if(kaynakDugme.filter(b=>!b.hidden).length < 2) $("#kabartma-kaynak").hidden = true;
  for(const b of kaynakDugme) b.addEventListener("click", () => {
    ayar.kabartmaKaynak = b.dataset.kaynak; ayarYaz(); kaynakYaz(); kabartmaKur(); ciz(); });
  kaynakYaz();
  for(const [id, k] of [["ay-kabartma","kabartma"],["ay-piksel","piksel"],["ay-izgara","izgara"],["ay-bant","bant"]]){
    const el = $("#"+id); el.checked = ayar[k];
    el.addEventListener("change", () => { ayar[k] = el.checked; ayarYaz(); katmanSec(katman); });
  }
  $("#kunye").innerHTML = D.J.facts.map(([b,v])=>`<dt>${b}</dt><dd>${v}</dd>`).join("")
    + `<dt>hücre</dt><dd>${((B[2]-B[0])/W).toFixed(2)}°</dd>`;
  const gecen = D.R.sanity.filter(c=>c.gecti).length;
  $("#tutarlilik-say").textContent = `${gecen}/${D.R.sanity.length}`;
  $("#tutarlilik").innerHTML = D.R.sanity.map(c=>`<div class="denetim${c.gecti?"":" dustu"}"><span>${c.ad}<small>${c.aciklama}</small></span></div>`).join("");
  $("#surum").textContent = `Veri sürümü ${D.J.surum} · üretildi ${D.J.uretim} · kabartma: ${D.doku.kabartma}`;

  /* --- hucre karti --- */
  function kartYaz(){
    const i = sec, x = i%W, y = (i/W)|0, lat = D.enlem(y), lon = B[0] + (x+0.5)*(B[2]-B[0])/W;
    const konum = `${Math.abs(lat).toFixed(1)}°${lat>=0?"K":"G"} ${Math.abs(lon).toFixed(1)}°${lon>=0?"D":"B"}`;
    const el = $("#kart-icerik"); $("#kart").hidden = false;
    const j = D.karaSira[i], ad = D.KCODE[String(D.kop[i])];
    const T = D.tAy.map(a=>a[j]), P = D.pAy.map(a=>a[j]);
    const sicak = T.indexOf(Math.max(...T)), soguk = T.indexOf(Math.min(...T)), r = v => eksi(Math.round(v));
    el.innerHTML = `<div class="k-ust"><i style="background:${KPAL[ad]||"#888"}"></i><div><h3>${D.KNAME[ad]||"—"}</h3>`
      + `<small><b>${ad||""}</b>${KREF[ad] ? "Dünya'da: "+KREF[ad] : ""}</small></div></div>`
      + `<div class="k-sayilar"><div><em>${r(D.tYil[j])}°</em><span>ortalama</span></div>`
      + `<div><em>${r(T[sicak])}°</em><span>${AYLAR[sicak]}</span></div>`
      + `<div><em>${r(T[soguk])}°</em><span>${AYLAR[soguk]}</span></div>`
      + `<div><em>${Math.round(D.pYil[j]).toLocaleString("tr-TR")}</em><span>mm/yıl</span></div></div>`
      + klimagram(T, P, donem)
      + `<div class="k-alt"><span>${konum} · ${eksi(Math.round(D.elev[i]).toLocaleString("tr-TR"))} m</span><span>sıcaklık °C · yağış mm</span></div>`;
  }
  // Dolasim sekmesinde okyanusa dokununca: deniz yuzeyi sicakligi ve ruzgar
  function denizKartYaz(){
    const i = sec, x = i%W, y = (i/W)|0, lat = D.enlem(y), lon = B[0] + (x+0.5)*(B[2]-B[0])/W, m = donem<0 ? 12 : donem;
    const konum = `${Math.abs(lat).toFixed(1)}°${lat>=0?"K":"G"} ${Math.abs(lon).toFixed(1)}°${lon>=0?"D":"B"}`;
    const u = dolOrnek(D, D.dol.u[m], x, y), v = dolOrnek(D, D.dol.v[m], x, y), T = D.dol.sst.slice(0,12).map(a=>dolOrnek(D, a, x, y));
    const r1 = v => eksi(Math.round(v*10)/10).replace(".", ",");
    $("#kart").hidden = false;
    $("#kart-icerik").innerHTML = `<div class="k-ust"><i style="background:#2b4a5a"></i><div><h3>Açık deniz</h3>`
      + `<small>${donem<0 ? "yıllık ortalama" : AYLAR[donem]}</small></div></div>`
      + `<div class="k-sayilar"><div><em>${r1(donem<0 ? T.reduce((p,c)=>p+c,0)/12 : T[donem])}°</em><span>yüzey</span></div>`
      + `<div><em>${r1(Math.max(...T))}°</em><span>en sıcak ay</span></div><div><em>${r1(Math.min(...T))}°</em><span>en soğuk ay</span></div>`
      + `<div><em>${r1(Math.hypot(u,v))}</em><span>m/s rüzgâr</span></div></div>`
      + `<div class="k-alt"><span>${konum}</span><span>rüzgâr ${nereden(u,v)} esiyor</span></div>`;
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
  function birak(e){ if(!ptr.has(e.pointerId)) return; const q = ptr.get(e.pointerId); ptr.delete(e.pointerId);
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
        if(i===null || (!D.land[i] && katman!=="dolasim")) kartKapat();
        else { sec = i; D.land[i] ? kartYaz() : denizKartYaz(); gorunurYap(q.y); ciz(); } } }
    dokun = null; hareketBasla(); }
  harita.addEventListener("pointerup", birak); harita.addEventListener("pointercancel", birak);
  harita.addEventListener("wheel", e => { e.preventDefault(); const q = yerel(e); yakinlas(q.x, q.y, Math.exp(-e.deltaY*0.0015)); }, {passive:false});

  addEventListener("resize", () => { boyut(); sigdir(); });
  listeYaz(); katmanSec("iklim"); sigdir(); requestAnimationFrame(kare);
  $("#yukleniyor").hidden = true;
  window.__atlas = {D, durum:()=>({katman, donem, ox, oy, olcek, sec, webgl:!!G})};   // dogrulama betikleri icin
}

/* 12 aylik iklim grafigi: cubuk yagis, cizgi sicaklik. Secili ay vurgulu. */
function klimagram(T, P, secili){
  const w = 330, h = 92, sol = 28, sag = 34, ust = 6, alt = 16, iw = w-sol-sag, ih = h-ust-alt;
  const guzel = v => { for(const x of [10,20,25,50,100,150,200,250,300,400,500,750,1000,1500,2000,3000]) if(v <= x) return x;
    return Math.ceil(v/1000)*1000; };
  const pm = guzel(Math.max(40, ...P));
  const t0 = Math.floor((Math.min(...T)-1)/5)*5, t1 = Math.ceil((Math.max(...T)+1)/5)*5;
  const X = i => sol + (i+0.5)*iw/12, Yt = t => ust + (t1-t)/(t1-t0)*ih, bw = iw/12*0.58;
  let s = `<svg class="klimagram" viewBox="0 0 ${w} ${h}" role="img" aria-label="Aylık sıcaklık ve yağış">`;
  for(const t of [t0, t1]) s += `<line x1="${sol}" x2="${w-sag}" y1="${Yt(t)}" y2="${Yt(t)}" stroke="rgba(214,205,186,.10)"/>`;
  if(t0 < 0 && t1 > 0) s += `<line x1="${sol}" x2="${w-sag}" y1="${Yt(0)}" y2="${Yt(0)}" stroke="rgba(214,205,186,.28)" stroke-dasharray="2 3"/>`;
  P.forEach((p,i) => { const bh = p/pm*ih;
    s += `<rect x="${(X(i)-bw/2).toFixed(1)}" y="${(ust+ih-bh).toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(bh,0.5).toFixed(1)}" fill="#3f7f8c" fill-opacity="${i===secili?1:.72}"${i===secili?' stroke="#d2a45c" stroke-width="1.2"':""}/>`; });
  s += `<polyline fill="none" stroke="#d2a45c" stroke-width="1.7" stroke-linejoin="round" points="${T.map((t,i)=>`${X(i).toFixed(1)},${Yt(t).toFixed(1)}`).join(" ")}"/>`;
  T.forEach((t,i) => { s += `<circle cx="${X(i).toFixed(1)}" cy="${Yt(t).toFixed(1)}" r="${i===secili?3:1.8}" fill="#d2a45c"/>`; });
  s += `<text x="${sol-5}" y="${Yt(t1)+3}" text-anchor="end">${eksi(t1)}°</text><text x="${sol-5}" y="${Yt(t0)+3}" text-anchor="end">${eksi(t0)}°</text>`;
  s += `<text x="${w-sag+5}" y="${ust+3}">${pm}</text><text x="${w-sag+5}" y="${ust+ih+3}">0</text>`;
  AY_HARF.forEach((a,i) => { s += `<text x="${X(i).toFixed(1)}" y="${h-4}" text-anchor="middle"${i===secili?' style="fill:#e4dfd3"':""}>${a}</text>`; });
  return s + `</svg>`;
}

/* ---- acilis ve guncelleme ---- */
async function veriCek(){
  const r = await fetch("data/atlas.json", {cache:"no-cache"});
  if(!r.ok) throw new Error("data/atlas.json okunamadı ("+r.status+")");
  return r.json();
}
async function acilis(){
  let J, resimler;
  try {
    J = await veriCek();
    const [doku, yukseklik, kabartma, kabartmaGri, kabartmaBir, dolasim] = await Promise.all([
      ...["data/doku.png","data/yukseklik.png","data/kabartma.jpg"].map(resimYukle),
      resimYukle("data/kabartma_gri.jpg").catch(() => null),     // eski veride yok
      resimYukle("data/kabartma_bir.jpg").catch(() => null),
      resimYukle("data/dolasim.png").catch(() => null)]);
    resimler = {doku, yukseklik, kabartma, kabartmaGri, kabartmaBir, dolasim};
  } catch(e){ $("#yukleniyor").innerHTML = `<span>Atlas yüklenemedi<br><small style="text-transform:none;letter-spacing:0">${e.message}. İlk kurulum için sunucu açık olmalı.</small></span>`; return; }
  try { const once = localStorage.getItem("veri-surum");
    if(once && once!==J.surum) setTimeout(()=>bildir("Yeni veri yüklendi · "+J.uretim), 600);
    localStorage.setItem("veri-surum", J.surum); } catch(_){}
  try { baslat(J, resimler); }
  catch(e){ console.error(e); $("#yukleniyor").innerHTML = `<span>Atlas açılamadı<br><small style="text-transform:none;letter-spacing:0">${e.message}</small></span>`; }
}

if("serviceWorker" in navigator){
  let yenilendi = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if(yenilendi || !navigator.serviceWorker.controller) return; yenilendi = true; location.reload(); });
  navigator.serviceWorker.register("sw.js", {updateViaCache:"none"}).then(r=>r.update()).catch(()=>{});
}
document.addEventListener("click", async e => {
  if(e.target.id !== "guncelle") return;
  try { const r = await navigator.serviceWorker?.getRegistration(); await r?.update();
    const J = await veriCek(); let once = null; try{ once = localStorage.getItem("veri-surum"); }catch(_){}
    if(once && once!==J.surum){ try{ localStorage.setItem("veri-surum", J.surum); }catch(_){} location.reload(); }
    else bildir("Güncel · veri "+J.surum);
  } catch(err){ bildir("Sunucuya ulaşılamadı, önbellekteki sürüm açık"); }
});
acilis();
