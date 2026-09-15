"use strict";
/* Dunyam Atlasi — mobil. Masaustu atlasla (atlas/atlas_tmpl.html) AYNI veri,
   AYNI palet, AYNI on hesaplar; yalnizca etkilesim ve yerlesim telefona gore.

   Veri HTML'e gomulu degil, data/atlas.json'dan gelir: dunya yeniden
   kosuldugunda _atlas.py o dosyayi yazar, uygulama koduna dokunmak gerekmez.

   KPAL ve KREF bloklari masaustu sablonla BIREBIR ayni olmali. _atlas.py
   ikisini karsilastirir ve farkliysa durur — iki kopya sessizce ayrismasin. */

const $ = s => document.querySelector(s);

const RAMPS = {
  temp:["#2c3a7a","#3f6fb0","#79b0d0","#b9dce6","#e8f2ee","#f6e2a6","#eeb463","#dd7a44","#bd4433","#8d1f22"],
  prec:["#f2ead2","#dfe4b4","#bcd79a","#8ec684","#5cb079","#2f9276","#1d7480","#1c5686","#233d78","#161f4a"],
  elev:["#2f5546","#4f7350","#7d8d55","#a89f65","#bd9a6d","#a1785a","#836553","#a9a49c","#e6eae8"],
};
const hex = h => [parseInt(h.slice(1,3),16),parseInt(h.slice(3,5),16),parseInt(h.slice(5,7),16)];
function rampColor(st,t){ t=Math.max(0,Math.min(1,t));
  const x=t*(st.length-1), i=Math.min(st.length-2,Math.floor(x)), f=x-i, a=hex(st[i]), b=hex(st[i+1]);
  return [a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f, a[2]+(b[2]-a[2])*f]; }
const cssRamp = st => `linear-gradient(90deg,${st.join(",")})`;
function b64(s){ const bin=atob(s), o=new Uint8Array(bin.length);
  for(let i=0;i<bin.length;i++) o[i]=bin.charCodeAt(i); return o; }
function unpackBits(by,n){ const o=new Uint8Array(n);
  for(let i=0;i<n;i++) o[i]=(by[i>>3]>>(7-(i&7)))&1; return o; }

// Dunya'da ayni sinifin dustugu yerler. Kurgusal bir iklimi okumanin en hizli
// yolu: "BSk" degil, "Mogolistan bozkiri".
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

function hsl(h,s,l){
  s/=100; l/=100;
  const k = n => (n + h/30) % 12;
  const a = s * Math.min(l, 1-l);
  const f = n => l - a * Math.max(-1, Math.min(k(n)-3, Math.min(9-k(n), 1)));
  return [255*f(0), 255*f(8), 255*f(4)];
}
const KPAL = {
  Af:hsl(178,48,30),  Am:hsl(174,42,40),  Aw:hsl(318,45,62),  // Aw bilerek ayri ton: savan kurak mevsimli, turkuazda Af/Am'den secilmiyordu; sari-kahve bozkirla karisirdi
  BWh:hsl(10,65,50),  BWk:hsl(16,46,67),  BSh:hsl(32,68,57),  BSk:hsl(40,55,72),
  Csa:hsl(50,60,48),  Csb:hsl(52,52,60),  Csc:hsl(54,44,71),
  Cwa:hsl(86,45,42),  Cwb:hsl(88,38,54),  Cwc:hsl(90,32,66),
  Cfa:hsl(128,42,36), Cfb:hsl(130,35,48), Cfc:hsl(132,30,60),
  Dsa:hsl(265,40,38), Dsb:hsl(262,36,48), Dsc:hsl(259,32,58), Dsd:hsl(256,28,68),  // Ds koyu mavi-mor: pastel lavanta soguk iklimi iliman gibi okutuyordu
  Dwa:hsl(232,48,52), Dwb:hsl(230,42,62), Dwc:hsl(228,36,71), Dwd:hsl(226,30,80),
  Dfa:hsl(202,55,42), Dfb:hsl(200,47,53), Dfc:hsl(198,40,64), Dfd:hsl(196,33,74),
  ET:hsl(190,10,72),  EF:hsl(200,6,88),
};
const rgb = c => 'rgb(' + (c[0]|0) + ',' + (c[1]|0) + ',' + (c[2]|0) + ')';
const GRUP = {A:"Tropikal", B:"Kurak", C:"Ilıman", D:"Soğuk", E:"Kutup"};
const cs = n => getComputedStyle(document.body).getPropertyValue(n).trim();
const fmt = (x,u) => (Math.abs(x)>=100 ? Math.round(x) : x.toFixed(1)) + (u?" "+u:"");

function toast(msg, ms=3200){
  const t=$("#toast"); t.textContent=msg; t.hidden=false;
  clearTimeout(toast._z); toast._z=setTimeout(()=>{ t.hidden=true; }, ms);
}

async function veriCek(){
  // no-cache: sunucu varsa her seferinde dogrula (304 ucuz). Sunucu yoksa
  // servis calisani onbellekten verir.
  const r = await fetch("data/atlas.json", {cache:"no-cache"});
  if(!r.ok) throw new Error("data/atlas.json okunamadı ("+r.status+")");
  return r.json();
}

function baslat(J){
  const DATA=J.data, FACTS=J.facts, ROI=J.roi;
  const KCODE=DATA.koppen_code, KCOL=DATA.koppen_colors, KNAME=DATA.koppen_names;
  const R = DATA.regions[Object.keys(DATA.regions)[0]];
  const N = R.w*R.h, B = R.bounds;
  const LAND = unpackBits(b64(R.land), N);
  const F = {};
  for(const [k,v] of Object.entries(R.fields)) F[k] = {lo:v.lo, hi:v.hi, a:b64(v.model)};
  F.elev = {lo:R.elev.lo, hi:R.elev.hi, a:b64(R.elev.data)};
  const val = (f,i) => f.lo + (f.a[i]-1)/254*(f.hi-f.lo);

  const LAYERS = [
    {id:"koppen",   label:"Köppen sınıfı",    chip:"İklim",        kind:"class"},
    {id:"temp_yil", label:"Yıllık sıcaklık",  chip:"Sıcaklık",     kind:"temp", unit:"°C"},
    {id:"prec_yil", label:"Yıllık yağış",     chip:"Yağış",        kind:"prec", unit:"mm"},
    {id:"temp_jan", label:"Ocak sıcaklığı",   chip:"Ocak °C",      kind:"temp", unit:"°C"},
    {id:"temp_jul", label:"Temmuz sıcaklığı", chip:"Temmuz °C",    kind:"temp", unit:"°C"},
    {id:"prec_jan", label:"Ocak yağışı",      chip:"Ocak yağış",   kind:"prec", unit:"mm"},
    {id:"prec_jul", label:"Temmuz yağışı",    chip:"Temmuz yağış", kind:"prec", unit:"mm"},
    {id:"elev",     label:"Yükseklik",        chip:"Yükseklik",    kind:"elev", unit:"m"},
  ].filter(l => l.id==="koppen" || l.id==="elev" || R.fields[l.id]);
  let layerId = "koppen";

  /* ---- bir kereye mahsus on hesaplar (masaustuyle ayni) ---- */
  const DIST = new Float32Array(N);
  (function(){
    const INF=1e9, W=R.w, H=R.h, wx=x=>(x+W)%W;
    for(let i=0;i<N;i++) DIST[i] = LAND[i] ? 0 : INF;
    for(let y=0;y<H;y++) for(let x=0;x<W;x++){
      const i=y*W+x; if(DIST[i]===0) continue; let d=DIST[i];
      if(y>0) d=Math.min(d, DIST[(y-1)*W+x]+1, DIST[(y-1)*W+wx(x-1)]+1.414, DIST[(y-1)*W+wx(x+1)]+1.414);
      DIST[i]=Math.min(d, DIST[y*W+wx(x-1)]+1);
    }
    for(let y=H-1;y>=0;y--) for(let x=W-1;x>=0;x--){
      const i=y*W+x; if(DIST[i]===0) continue; let d=DIST[i];
      if(y<H-1) d=Math.min(d, DIST[(y+1)*W+x]+1, DIST[(y+1)*W+wx(x-1)]+1.414, DIST[(y+1)*W+wx(x+1)]+1.414);
      DIST[i]=Math.min(d, DIST[y*W+wx(x+1)]+1);
    }
  })();
  const SHADE = new Float32Array(N).fill(1);
  (function(){
    const W=R.w, H=R.h, e=F.elev, m=new Float32Array(N), wx=x=>(x+W)%W;
    for(let i=0;i<N;i++) m[i] = LAND[i] ? val(e,i) : 0;
    for(let y=1;y<H-1;y++) for(let x=0;x<W;x++){
      const i=y*W+x; if(!LAND[i]) continue;
      const dzdx=(m[y*W+wx(x+1)]-m[y*W+wx(x-1)])/2, dzdy=(m[(y+1)*W+x]-m[(y-1)*W+x])/2;
      SHADE[i] = Math.max(0.74, Math.min(1.26, 1 + (dzdx+dzdy)/900));
    }
  })();
  const KVIEW = new Uint8Array(F.koppen.a);
  (function(){
    const W=R.w, H=R.h, a=F.koppen.a, wx=x=>(x+W)%W;
    for(let y=1;y<H-1;y++) for(let x=0;x<W;x++){
      const i=y*W+x; if(!LAND[i]) continue; const say={};
      for(let dy=-1;dy<=1;dy++) for(let dx=-1;dx<=1;dx++){
        if(!dx&&!dy) continue; const j=(y+dy)*W+wx(x+dx); if(!LAND[j]) continue;
        say[a[j]]=(say[a[j]]||0)+1;
      }
      let en=0,k=0; for(const c in say) if(say[c]>en){ en=say[c]; k=+c; }
      if(en>=6 && k!==a[i]) KVIEW[i]=k;
    }
  })();
  const EDGE = new Uint8Array(N);
  (function(){
    const W=R.w, H=R.h, wx=x=>(x+W)%W;
    for(let y=0;y<H;y++) for(let x=0;x<W;x++){
      const i=y*W+x; if(!LAND[i]) continue;
      if(!LAND[y*W+wx(x-1)] || !LAND[y*W+wx(x+1)] || (y>0&&!LAND[(y-1)*W+x]) || (y<H-1&&!LAND[(y+1)*W+x])) EDGE[i]=1;
    }
  })();
  const BOX = (function(){
    let x0=R.w,x1=0,y0=R.h,y1=0;
    for(let i=0;i<N;i++) if(LAND[i]){ const x=i%R.w, y=(i/R.w)|0;
      if(x<x0)x0=x; if(x>x1)x1=x; if(y<y0)y0=y; if(y>y1)y1=y; }
    const mx=(x1-x0)*0.03, my=(y1-y0)*0.04;
    return {x0:x0-mx, y0:y0-my, w:(x1-x0+1)+2*mx, h:(y1-y0+1)+2*my};
  })();

  /* ---- gorunum ---- */
  const stage=$("#stage"), cv=$("#cv"), ov=$("#ov"), sheet=$("#sheet");
  let scale=1, ox=0, oy=0, fitScale=1, sec=null, izole=null;

  // Haritanin gorunen kismi: ust serit ile alt panelin arasi. Kita oraya oturur.
  function gorunen(){
    const r = stage.getBoundingClientRect();
    const top = $(".top").getBoundingClientRect().bottom;
    const peek = parseFloat(cs("--peek-h")) || 132;
    return {w:r.width, h:r.height, top, bot:r.height - peek};
  }
  function fit(){
    const g = gorunen(), vh = Math.max(80, g.bot - g.top);
    fitScale = Math.min(g.w/R.w, g.h/R.h);
    scale = Math.min(g.w/BOX.w, vh/BOX.h);
    ox = g.w/2 - (BOX.x0 + BOX.w/2)*scale;
    oy = g.top + vh/2 - (BOX.y0 + BOX.h/2)*scale;
    apply();
  }
  function clampView(){
    const g = gorunen();
    scale = Math.max(fitScale*0.8, Math.min(fitScale*60, scale));
    const w=R.w*scale, h=R.h*scale, pad=g.w*0.5;
    ox = Math.min(pad, Math.max(g.w-w-pad, ox));
    oy = Math.min(g.bot-40, Math.max(g.top+40-h, oy));
  }
  function apply(){
    clampView();
    cv.style.width=R.w+"px"; cv.style.height=R.h+"px";
    cv.style.transform = `translate(${ox}px,${oy}px) scale(${scale})`;
    const L = LAYERS.find(l=>l.id===layerId);
    // Sinif haritasi HER ZAMAN keskin: kategorik veriyi yumusatmak ara renk uydurur.
    cv.classList.toggle("crisp", L.kind==="class" || scale>=6);
    overlay();
  }
  function zoomAt(px,py,factor){
    const before=scale; scale*=factor; clampView();
    const k=scale/before; ox=px-(px-ox)*k; oy=py-(py-oy)*k; apply();
  }

  const mix=(a,b,t)=>[a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t];
  function paint(){
    const L=LAYERS.find(l=>l.id===layerId), f=F[layerId];
    cv.width=R.w; cv.height=R.h;
    const ctx=cv.getContext("2d"), img=ctx.createImageData(R.w,R.h), px=img.data;
    const rim=hex(cs("--sea-rim")), mid=hex(cs("--sea-mid")), deep=hex(cs("--sea-deep"));
    const golge=$("#shade").checked;
    for(let i=0;i<N;i++){
      const p=i*4; let c;
      if(!LAND[i]){ const d=DIST[i];
        c = d<3 ? mix(rim,mid,d/3) : mix(mid,deep,Math.min(1,(d-3)/20)); }
      else {
        let sonuk=false;
        if(L.kind==="class"){ const k=KCODE[String(KVIEW[i])];
          c = k ? (KPAL[k]||hex(KCOL[k])) : mid; if(izole && k!==izole) sonuk=true; }
        else c = rampColor(RAMPS[L.kind], (f.a[i]-1)/254);
        let s = golge ? SHADE[i] : 1; if(EDGE[i]) s*=0.87;
        c=[c[0]*s,c[1]*s,c[2]*s];
        if(sonuk){ const g=0.299*c[0]+0.587*c[1]+0.114*c[2];
          c=[g*0.55+120*0.45, g*0.55+124*0.45, g*0.55+122*0.45]; }
      }
      px[p]=Math.min(255,c[0])|0; px[p+1]=Math.min(255,c[1])|0; px[p+2]=Math.min(255,c[2])|0; px[p+3]=255;
    }
    ctx.putImageData(img,0,0);
  }

  const sx = lon => ox + (lon-B[0])/(B[2]-B[0])*R.w*scale;
  const sy = lat => oy + (B[3]-lat)/(B[3]-B[1])*R.h*scale;
  function overlay(){
    const r=stage.getBoundingClientRect(), ink=cs("--ink");
    ov.setAttribute("viewBox",`0 0 ${r.width} ${r.height}`);
    let s="";
    if($("#grat").checked){
      const g=`stroke="${ink}" stroke-opacity=".2" stroke-width="1" fill="none"`;
      for(let la=-60;la<=60;la+=30) if(la) s+=`<line x1="0" y1="${sy(la)}" x2="${r.width}" y2="${sy(la)}" ${g}/>`;
      for(let lo=-150;lo<=150;lo+=30) s+=`<line x1="${sx(lo)}" y1="0" x2="${sx(lo)}" y2="${r.height}" ${g}/>`;
      s+=`<line x1="0" y1="${sy(0)}" x2="${r.width}" y2="${sy(0)}" stroke="${ink}" stroke-opacity=".42" stroke-width="1.4"/>`;
      for(const la of [60,30,0,-30]){ const y=sy(la);
        if(y>12 && y<r.height-4) s+=`<text x="8" y="${y-5}" fill="${ink}" fill-opacity=".55" font-size="11" font-family="ui-monospace,Menlo,monospace">${la===0?"ekvator":Math.abs(la)+"°"+(la>0?"K":"G")}</text>`; }
    }
    if($("#roi").checked){
      const pts=ROI.map(([la,lo])=>`${sx(lo)},${sy(la)}`).join(" ");
      s+=`<polygon points="${pts}" fill="#e8503f" fill-opacity=".07" stroke="#e8503f" stroke-width="2" stroke-linejoin="round"/>`;
    }
    if(sec!==null){
      const x=ox+(sec%R.w+.5)*scale, y=oy+(((sec/R.w)|0)+.5)*scale, rr=Math.max(9, scale*1.2);
      s+=`<circle cx="${x}" cy="${y}" r="${rr+2}" fill="none" stroke="#000" stroke-opacity=".45" stroke-width="4"/>`
       + `<circle cx="${x}" cy="${y}" r="${rr}" fill="none" stroke="#fff" stroke-width="2.5"/>`;
    }
    ov.innerHTML=s;
  }

  /* ---- hucre karti (panelin gorunen ust kismi) ---- */
  // Kapali panel = tutamac + kart + sekmeler. Sabit yukseklik, kart dolunca
  // sekmeleri ekranin altina itiyordu; yuksekligi icerikten olc.
  function peekOlc(){
    const h = $("#grip").offsetHeight + $("#peek").offsetHeight + $("#tabs").offsetHeight;
    document.documentElement.style.setProperty("--peek-h", h+"px");
  }
  function hucre(){ hucreYaz(); peekOlc(); }
  function hucreYaz(){
    const peek=$("#peek"), i=sec;
    if(i===null){ peek.innerHTML=`<div class="hint">Haritada bir yere dokun, o hücrenin iklimi burada görünür.</div>`; return; }
    const x=i%R.w, y=(i/R.w)|0;
    const lat=B[3]-(y+0.5)*(B[3]-B[1])/R.h, lon=B[0]+(x+0.5)*(B[2]-B[0])/R.w;
    const konum=`${Math.abs(lat).toFixed(1)}°${lat>=0?"K":"G"} ${Math.abs(lon).toFixed(1)}°${lon>=0?"D":"B"}`;
    if(!LAND[i]){ peek.innerHTML=`<div class="cell-top"><i class="cell-sw" style="background:${cs("--sea-mid")}"></i><b>Okyanus</b><span class="code mono">${konum}</span></div>`; return; }
    const k=KCODE[String(KVIEW[i])], L=LAYERS.find(l=>l.id===layerId);
    const jan=F.temp_jan?val(F.temp_jan,i):null, jul=F.temp_jul?val(F.temp_jul,i):null;
    const yaz=lat>=0?jul:jan, kis=lat>=0?jan:jul, n=[];
    if(F.temp_yil) n.push(`<span><em>${val(F.temp_yil,i).toFixed(0)}°C</em> ort</span>`);
    if(yaz!==null) n.push(`<span>yaz <em>${yaz.toFixed(0)}°</em> kış <em>${kis.toFixed(0)}°</em></span>`);
    if(F.prec_yil) n.push(`<span><em>${Math.round(val(F.prec_yil,i))}</em> mm/yıl</span>`);
    if(L.kind!=="class" && layerId!=="elev" && !["temp_yil","prec_yil"].includes(layerId))
      n.push(`<span>${L.label.toLowerCase()} <em>${fmt(val(F[layerId],i),L.unit)}</em></span>`);
    peek.innerHTML =
      `<div class="cell-top"><i class="cell-sw" style="background:${k?rgb(KPAL[k]||hex(KCOL[k])):"#888"}"></i>`
      + `<b>${k?KNAME[k]:"—"}</b><span class="code mono">${k||""}</span></div>`
      + (k&&KREF[k] ? `<div class="cell-ref">Dünya'da: ${KREF[k]}</div>` : "")
      + `<div class="cell-nums mono">${n.join("")}</div>`
      + `<div class="cell-loc mono">${konum} · ${Math.round(val(F.elev,i))} m</div>`;
  }

  /* ---- lejant: ALAN agirlikli (hucre saymak yuksek enlemleri sisirir) ---- */
  function legend(){
    const c={}; let tot=0;
    for(let i=0;i<N;i++){ if(!LAND[i]) continue;
      const lat=B[3]-(((i/R.w)|0)+0.5)*(B[3]-B[1])/R.h, w_=Math.cos(lat*Math.PI/180);
      tot+=w_; const k=KCODE[String(KVIEW[i])]; if(k) c[k]=(c[k]||0)+w_; }
    const ks=Object.keys(c).filter(k=>c[k]/tot>0.004), aile={};
    for(const k of ks) (aile[k[0]]=aile[k[0]]||[]).push(k);
    $("#klist").innerHTML = Object.keys(GRUP).filter(g=>aile[g]).map(g=>{
      const pay=aile[g].reduce((a,k)=>a+c[k],0)/tot;
      return `<div class="kgroup"><h3>${GRUP[g]}<em>%${(100*pay).toFixed(0)}</em></h3>`
        + aile[g].sort((a,b)=>c[b]-c[a]).map(k=>
          `<button class="krow${izole===k?" on":""}" data-k="${k}">
             <i class="ksw" style="background:${rgb(KPAL[k]||hex(KCOL[k]))}"></i>
             <span class="kcode mono">${k}</span>
             <span class="kname">${KREF[k]||KNAME[k]}</span>
             <span class="kpct mono">%${(100*c[k]/tot).toFixed(1)}</span>
           </button>`).join("") + `</div>`;
    }).join("");
  }
  function izoleEt(k){
    izole=k; $("#izole-not").hidden=!izole;
    if(izole && layerId!=="koppen") katmanSec("koppen");
    legend(); paint(); overlay();
  }
  $("#klist").addEventListener("click", e=>{
    const b=e.target.closest("button[data-k]"); if(!b) return;
    izoleEt(izole===b.dataset.k ? null : b.dataset.k);
  });
  $("#izole-kapat").addEventListener("click", ()=>izoleEt(null));

  function katmanSec(id){
    layerId=id; const L=LAYERS.find(l=>l.id===id);
    $("#katman-ad").textContent=L.label;
    for(const b of $("#layers").children) b.setAttribute("aria-pressed", b.dataset.l===id);
    const sinif=L.kind==="class"; $("#rampbox").hidden=sinif;
    if(!sinif){ const f=F[id]; $("#ramp").style.background=cssRamp(RAMPS[L.kind]);
      $("#lo").textContent=fmt(f.lo,L.unit); $("#hi").textContent=fmt(f.hi,L.unit); }
    paint(); apply(); hucre();
  }
  $("#layers").innerHTML = LAYERS.map(l=>`<button data-l="${l.id}" aria-pressed="${l.id===layerId}">${l.chip}</button>`).join("");
  $("#layers").addEventListener("click", e=>{ const b=e.target.closest("button[data-l]"); if(b) katmanSec(b.dataset.l); });

  /* ---- dokunma: tek parmak kaydir, iki parmak yakinlastir, dokun = hucre sec ---- */
  const ptr=new Map(); let g0=null, dokun=null, sonDokun=null;
  function hareketBasla(){
    const p=[...ptr.values()];
    g0={ox,oy,scale,p:p.map(q=>({...q}))};
    if(p.length>=2){ g0.mid={x:(p[0].x+p[1].x)/2, y:(p[0].y+p[1].y)/2}; g0.d=Math.hypot(p[0].x-p[1].x, p[0].y-p[1].y)||1; }
  }
  const yerel = e => { const r=stage.getBoundingClientRect(); return {x:e.clientX-r.left, y:e.clientY-r.top}; };
  stage.addEventListener("pointerdown", e=>{
    stage.setPointerCapture(e.pointerId); ptr.set(e.pointerId, yerel(e)); hareketBasla();
    dokun = ptr.size===1 ? {...yerel(e), t:performance.now()} : null;
  });
  stage.addEventListener("pointermove", e=>{
    if(!ptr.has(e.pointerId)) return;
    ptr.set(e.pointerId, yerel(e));
    const p=[...ptr.values()];
    if(dokun && Math.hypot(p[0].x-dokun.x, p[0].y-dokun.y) > 8) dokun=null;
    if(p.length===1 && g0.p.length===1){
      ox=g0.ox+(p[0].x-g0.p[0].x); oy=g0.oy+(p[0].y-g0.p[0].y); apply();
    } else if(p.length>=2 && g0.mid){
      const mid={x:(p[0].x+p[1].x)/2, y:(p[0].y+p[1].y)/2}, d=Math.hypot(p[0].x-p[1].x, p[0].y-p[1].y);
      scale=g0.scale*d/g0.d; clampView(); const k=scale/g0.scale;
      ox=mid.x-(g0.mid.x-g0.ox)*k; oy=mid.y-(g0.mid.y-g0.oy)*k; apply();
    }
  });
  function birak(e){
    if(!ptr.has(e.pointerId)) return;
    const q=ptr.get(e.pointerId); ptr.delete(e.pointerId);
    if(dokun && e.type==="pointerup" && performance.now()-dokun.t < 350){
      const now=performance.now();
      if(sonDokun && now-sonDokun.t<320 && Math.hypot(q.x-sonDokun.x, q.y-sonDokun.y)<30){
        zoomAt(q.x,q.y,2); sonDokun=null;
      } else {
        const x=Math.floor((q.x-ox)/scale), y=Math.floor((q.y-oy)/scale);
        sec = (x<0||y<0||x>=R.w||y>=R.h) ? null : y*R.w+x;
        hucre(); overlay(); sonDokun={...q, t:now};
      }
    }
    dokun=null; hareketBasla();
  }
  stage.addEventListener("pointerup", birak);
  stage.addEventListener("pointercancel", birak);
  stage.addEventListener("wheel", e=>{ e.preventDefault(); const q=yerel(e); zoomAt(q.x,q.y,Math.exp(-e.deltaY*0.0015)); }, {passive:false});
  $("#fit").addEventListener("click", fit);

  /* ---- alt panel: tut-cek ya da tutamaca dokun ---- */
  const grip=$("#grip"); let cek=null;
  const panelAc = ac => { sheet.dataset.open=String(ac); sheet.style.transform=""; };
  grip.addEventListener("pointerdown", e=>{ grip.setPointerCapture(e.pointerId); cek={y:e.clientY, t:performance.now(), acik:sheet.dataset.open==="true"}; sheet.classList.add("dragging"); });
  grip.addEventListener("pointermove", e=>{
    if(!cek) return;
    const h=sheet.getBoundingClientRect().height, peek=parseFloat(cs("--peek-h"));
    const kapaliY=h-peek, taban=cek.acik?0:kapaliY;
    const y=Math.max(0, Math.min(kapaliY, taban+(e.clientY-cek.y)));
    sheet.style.transform=`translateY(${y}px)`;
  });
  function cekBitir(e){
    if(!cek) return; sheet.classList.remove("dragging");
    const dy=e.clientY-cek.y, hizli=performance.now()-cek.t<250;
    panelAc(Math.abs(dy)<6 ? !cek.acik : (dy<0 ? true : (hizli || dy>60 ? false : cek.acik)));
    cek=null;
  }
  grip.addEventListener("pointerup", cekBitir); grip.addEventListener("pointercancel", cekBitir);
  $("#peek").addEventListener("click", ()=>{ if(sheet.dataset.open!=="true") panelAc(true); });

  $("#tabs").addEventListener("click", e=>{
    const b=e.target.closest("button[data-t]"); if(!b) return;
    for(const t of $("#tabs").children) t.setAttribute("aria-selected", t===b);
    for(const p of document.querySelectorAll(".pane")) p.hidden = p.id!=="p-"+b.dataset.t;
    panelAc(true);
  });

  for(const id of ["grat","roi"]) $("#"+id).addEventListener("change", overlay);
  $("#shade").addEventListener("change", paint);

  $("#facts").innerHTML = FACTS.map(([b,v])=>`<div><b>${b}</b><span>${v}</span></div>`).join("")
    + `<div><b>hücre</b><span>${((B[2]-B[0])/R.w).toFixed(2)}°</span></div>`;
  $("#surum").textContent = `Veri sürümü ${J.surum} · üretildi ${J.uretim}`;
  const gecen=R.sanity.filter(c=>c.gecti).length;
  $("#tally").textContent=`${gecen}/${R.sanity.length}`;
  $("#checks").innerHTML=R.sanity.map(c=>`<div class="check${c.gecti?"":" no"}"><strong>${c.ad}</strong><small>${c.aciklama}</small></div>`).join("");

  const ustH=()=>document.documentElement.style.setProperty("--top-h", $(".top").getBoundingClientRect().bottom+"px");
  // ponytail: dondurunce/boyut degisince kitaya yeniden oturur, yakinlik korunmaz
  addEventListener("resize", ()=>{ ustH(); fit(); });
  matchMedia("(prefers-color-scheme:dark)").addEventListener("change", ()=>{ paint(); overlay(); hucre(); });

  ustH(); legend(); hucre(); katmanSec("koppen"); fit();
  $("#yukleniyor").hidden=true;
}

/* ---- guncelleme: veri surumu degistiyse ve yeni uygulama kodu geldiyse haber ver ---- */
async function acilis(){
  let J;
  try { J = await veriCek(); }
  catch(e){ $("#yukleniyor").textContent = "Atlas yüklenemedi: "+e.message+". İlk kurulum için sunucu açık olmalı."; return; }
  try {
    const onceki = localStorage.getItem("veri-surum");
    if(onceki && onceki!==J.surum) setTimeout(()=>toast("Yeni veri yüklendi · "+J.uretim), 600);
    localStorage.setItem("veri-surum", J.surum);
  } catch(_){}
  baslat(J);
}

if("serviceWorker" in navigator){
  let yenilendi=false;
  navigator.serviceWorker.addEventListener("controllerchange", ()=>{
    // yeni servis calisani devraldi = yeni uygulama kodu. Bir kez yenile.
    if(yenilendi || !navigator.serviceWorker.controller) return;
    yenilendi=true; location.reload();
  });
  navigator.serviceWorker.register("sw.js", {updateViaCache:"none"}).then(r=>r.update()).catch(()=>{});
}
document.addEventListener("click", async e=>{
  if(e.target.id!=="guncelle") return;
  try{
    const r = await navigator.serviceWorker?.getRegistration(); await r?.update();
    const J = await veriCek(); let onceki=null;
    try{ onceki=localStorage.getItem("veri-surum"); }catch(_){}
    if(onceki && onceki!==J.surum){ try{ localStorage.setItem("veri-surum", J.surum); }catch(_){} location.reload(); }
    else toast("Güncel · veri "+J.surum);
  } catch(err){ toast("Sunucuya ulaşılamadı, önbellekteki sürüm açık"); }
});
acilis();
