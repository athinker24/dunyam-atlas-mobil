# -*- coding: utf-8 -*-
"""Dunyam levha modeli (23 Kasim, yeni hikaye; tektonik/HIKAYE.md): kapali levhalar,
Euler vektorleri, siniflanmis sinir adimlari.

Yontem (TEKTONIK.md "Yeni hikaye"):
- Kita levhalari (1-7) sahibin levha kimligi goruntusunden gelir
  (kaynak/levha_kimlik_8k.png, 16k ana haritanin yarisi). Goruntu pikseli
  kaynak/kayit.json ile tuvale, oradan enlem ve boylama cevrilir. Goruntu
  yalniz kitanin cevresinde gecerli: 16k cerceve kureden buyuk, 8-10 o
  cercevede duz cizgilerle bolunmus yer tutuculardir.
- Uzak okyanus levhalari atlasin onceki gezegen olcekli modelinden korunur
  (kaynak/uzak_okyanus.png): Bati Okyanusu (8, eski Uzak Okyanus), Kutup (9,
  eski Kuzey Kutup), Guney Okyanusu (10, eski Guney Kutup), Buyuk Okyanus (11).
  Sirtlar, cukur ve kutup sinirlari eski cizimlerle ayni yerde.
- Aradaki okyanus (kita ile uzak sirtlar arasi) en yakin kita levhasina verilir:
  edilgen kiyida kita ile onundeki okyanus ayni levhadir (HIKAYE.md).
- Sinirlar kimlik rasterindan cikarilir (komsu iki levha arasi kenar
  ortalari, zincirlenir, ~0.5 derecelik adimlara bolunur). Her adimin sinifi
  Bird (2003) olcutuyle hesaptan cikar: goreli hiz sinira 20 dereceden
  yakinsa yanal, degilse yaklasma/ayrilma; iki yani da denizse okyanusal.
  Yedi sinif: OSR OTF OCB SUB CRB CTF CCB.
- Hizlar ve yonler kaynak/levhalar_hikaye.json'dan (Kuzey Levhasi sabit).
  Dogu Dil Levhasi donerek ilerler: saat yonunun tersine 0.3 derece/My.
"""
import json, os, sys
from collections import deque, defaultdict
import numpy as np
from scipy import ndimage
from PIL import Image

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAYNAK = os.path.join(KOK, "tektonik", "kaynak")
sys.path.insert(0, KOK)
import uret  # noqa: E402

RES = 0.1
w = uret.dunya_yukle(); g = uret.grid_kur(w, RES)
land = g.land.astype(bool); lat = np.asarray(g.lat); lon = np.asarray(g.lon); H, W = land.shape
e = np.where(land, np.maximum(g.elev, 0), 0).astype(float); es = ndimage.gaussian_filter(e, 3)
RKM = w.radius_km
row = lambda la: int(round(np.interp(-la, -lat, np.arange(H))))
col = lambda lo: int(round(np.interp(lo, lon, np.arange(W))))
LA = lambda r: float(np.interp(r, np.arange(H), lat))
LO = lambda c: float(np.interp(c, np.arange(W), lon))

# ------------------------------------------------------------------ kayit: 16k piksel <-> enlem, boylam
KAYIT = json.load(open(os.path.join(KAYNAK, "kayit.json"), encoding="utf-8"))
def px16_ll(X, Y):
    c = KAYIT["ox"] + KAYIT["sx"] * np.asarray(X, float); r = KAYIT["oy"] + KAYIT["sy"] * np.asarray(Y, float)
    return 90 - (r + 0.5) * 180 / 2048, -180 + (c + 0.5) * 360 / 4096
def ll_px16(la, lo):
    r = (90 - np.asarray(la, float)) * 2048 / 180 - 0.5; c = (np.asarray(lo, float) + 180) * 4096 / 360 - 0.5
    return (c - KAYIT["ox"]) / KAYIT["sx"], (r - KAYIT["oy"]) / KAYIT["sy"]

# ------------------------------------------------------------------ levhalar
HK = json.load(open(os.path.join(KAYNAK, "levhalar_hikaye.json"), encoding="utf-8"))["levhalar"]
LEVHALAR = {}
for ad, v in sorted(HK.items(), key=lambda x: x[1]["kimlik"]):
    la, lo = px16_ll(*v["tohum_16k_px"])
    LEVHALAR[ad] = dict(kimlik=v["kimlik"], tohum=(round(float(la), 2), round(float(lo), 2)),
                        hiz=tuple(float(x) for x in v["hiz_dogu_kuzey_cm_yil"]), sira=v["sira"],
                        renk=tuple(v["renk"]), kapsam=v["kapsam"])
# atlasin kendi okyanus levhasi (hikayede yok; eski modeldeki hizi)
LEVHALAR["Büyük Okyanus Levhası"] = dict(kimlik=11, tohum=(0.0, 135.0), hiz=(1.0, 1.5), sira=2, renk=(100, 110, 170),
                                          kapsam="uzak yarıküre; atlasın gezegen ölçekli okyanus levhası (hikâyede yok)")
DONME = {"Doğu Dil Levhası": 0.3}          # derece/My, saat yonunun tersi (+)
ADLAR = sorted(LEVHALAR, key=lambda a: LEVHALAR[a]["kimlik"])
assert [LEVHALAR[a]["kimlik"] for a in ADLAR] == list(range(1, len(ADLAR) + 1))

def birim(la, lo):
    a, b = np.radians(la), np.radians(lo)
    return np.array([np.cos(a) * np.cos(b), np.cos(a) * np.sin(b), np.sin(a)])
def en(la, lo):
    b = np.radians(lo); a = np.radians(la)
    return np.array([-np.sin(b), np.cos(b), 0.0]), np.array([-np.sin(a) * np.cos(b), -np.sin(a) * np.sin(b), np.cos(a)])

# ------------------------------------------------------------------ kimlik rasteri
uzak = np.array(Image.open(os.path.join(KAYNAK, "uzak_okyanus.png")))
assert uzak.shape == (H, W), "uzak_okyanus.png izgarayla ayni boyda olmali"
k8 = np.array(Image.open(os.path.join(KAYNAK, "levha_kimlik_8k.png")))
LLA, LLO = np.meshgrid(lat, lon, indexing="ij")
X16, Y16 = ll_px16(LLA, LLO)
i8 = np.floor(Y16 / 2).astype(int); j8 = np.floor(X16 / 2).astype(int)
gec = (i8 >= 0) & (i8 < k8.shape[0]) & (j8 >= 0) & (j8 < k8.shape[1])
goruntu = np.zeros((H, W), np.uint8); goruntu[gec] = k8[i8[gec], j8[gec]]
kimlik = uzak.copy()
cekirdek = (kimlik == 0) & (goruntu >= 1) & (goruntu <= 7)
kimlik[cekirdek] = goruntu[cekirdek]
# kalan ic alan: en yakin kita levhasi (boylamda sarmal: uc kopya)
bos = kimlik == 0
uc = np.concatenate([kimlik, kimlik, kimlik], 1); kaynak_m = np.isin(uc, range(1, 8))
_, (ir, ic) = ndimage.distance_transform_edt(~kaynak_m, sampling=(1.0, 0.7), return_indices=True)
dol = uc[ir, ic][:, W:2 * W]
kimlik[bos] = dol[bos]
assert (kimlik > 0).all()

def levha_at(la, lo):
    return ADLAR[kimlik[min(max(row(la), 0), H - 1), col(((lo + 180) % 360) - 180) % W] - 1]
def kara_at(la, lo):
    return bool(land[min(max(row(la), 0), H - 1), col(((lo + 180) % 360) - 180) % W])

# tohum kendi levhasinin disina dustuyse (Dogu Okyanusu'nun tohumu 16k cercevenin
# uzak dogusunda, kurede Buyuk Okyanus'a dusuyor) levhanin en yakin hucresine al;
# hiz o noktada verilmis sayilir. Etiket ve hiz oku da oraya konur.
TASINAN = {}
for ad, L in LEVHALAR.items():
    i = L["kimlik"]; la, lo = L["tohum"]
    if kimlik[row(la), col(lo)] != i:
        # levhanin kenarlarindan en uzak hucresi (etiket ortada dursun)
        dt = ndimage.distance_transform_edt(kimlik == i, sampling=(1.0, 0.7))
        r_, c_ = np.unravel_index(np.argmax(dt), dt.shape)
        TASINAN[ad] = L["tohum"]; L["tohum"] = (round(float(lat[r_]), 2), round(float(lon[c_]), 2))

# ------------------------------------------------------------------ Euler vektorleri
for ad, L in LEVHALAR.items():
    la, lo = L["tohum"]; ve, vn = L["hiz"]; E_, N_ = en(la, lo)
    v = (ve * E_ + vn * N_) * 10.0                         # km/My
    L["omega"] = np.cross(birim(la, lo), v) / RKM + np.radians(DONME.get(ad, 0.0)) * birim(la, lo)   # rad/My
def hiz(ad, la, lo):
    """levhanin (enlem, boylam) noktasindaki hizi, (dogu, kuzey) cm/yil"""
    v = np.cross(LEVHALAR[ad]["omega"], birim(la, lo) * RKM) / 10.0; E_, N_ = en(la, lo)
    return np.array([v @ E_, v @ N_])

# ------------------------------------------------------------------ sinirlar: rasterdan zincir
def yumusat(p, k=5):
    if not p:
        return []
    a = np.array(p, float); o = a.copy()
    for i in range(len(a)): o[i] = a[max(0, i - k // 2): i + k // 2 + 1].mean(0)
    o[0], o[-1] = a[0], a[-1]; return [tuple(x) for x in o]
def sik(p, adim=0.05):
    o = []
    for (a1, b1), (a2, b2) in zip(p[:-1], p[1:]):
        n = max(2, int(np.hypot(a2 - a1, b2 - b1) / adim)); t = np.linspace(0, 1, n, endpoint=False)
        o += list(zip(a1 + (a2 - a1) * t, b1 + (b2 - b1) * t))
    return o + [p[-1]]

def yeniden_ornekle(p, adim):
    """cizgiyi yay uzunlugunca ~adim derecelik (enlem cos'u ile) esit parcalara bol"""
    a = np.array(p, float); c = np.cos(np.radians(a[:, 0]))
    d = np.r_[0, np.cumsum(np.hypot(np.diff(a[:, 0]), np.diff(a[:, 1]) * (c[1:] + c[:-1]) / 2))]
    if d[-1] < adim / 2: return [tuple(a[0]), tuple(a[-1])]
    n = max(1, int(round(d[-1] / adim))); s = np.linspace(0, d[-1], n + 1)
    return list(zip(np.interp(s, d, a[:, 0]), np.interp(s, d, a[:, 1])))

def _kenarlar():
    """komsu iki farkli levha arasindaki kenar ortalari, 2x izgarada (satir2, sutun2) -> cift"""
    k = kimlik.astype(np.int32); out = defaultdict(list)
    a, b = k[:, :-1], k[:, 1:]; r, c = np.nonzero(a != b)          # yatay komsu
    for rr, cc in zip(r, c): out[tuple(sorted((k[rr, cc], k[rr, cc + 1])))].append((2 * rr + 1, 2 * cc + 2))
    a, b = k[:, -1], k[:, 0]; r = np.nonzero(a != b)[0]            # dikis (sarmal)
    for rr in r: out[tuple(sorted((k[rr, -1], k[rr, 0])))].append((2 * rr + 1, 0))
    a, b = k[:-1, :], k[1:, :]; r, c = np.nonzero(a != b)          # dikey komsu
    for rr, cc in zip(r, c): out[tuple(sorted((k[rr, cc], k[rr + 1, cc])))].append((2 * rr + 2, 2 * cc + 1))
    return out

def _zincirler(noktalar, en_az=12):
    """2x izgaradaki noktalari 8-komsu bilesenlere ayir; her bilesende en uzun yol
    (iki kez BFS), kalan buyuk parcalar icin tekrar. Sirali yol listesi doner."""
    S_ = set(noktalar); yollar = []
    def kom(p):
        r, c = p
        for dr in (-2, -1, 0, 1, 2):          # kenar ortalari 2x izgarada 2 aralikli
            for dc in (-2, -1, 0, 1, 2):
                if dr or dc:
                    q = (r + dr, (c + dc) % (2 * W))
                    if q in S_: yield q
    def bfs(bas, izin):
        ata = {bas: None}; d = deque([bas]); son = bas
        while d:
            p = d.popleft(); son = p
            for q in kom(p):
                if q in izin and q not in ata: ata[q] = p; d.append(q)
        return son, ata
    kalan = set(S_)
    while kalan:
        p0 = next(iter(kalan)); _, ata = bfs(p0, kalan); bilesen = set(ata)
        while len(bilesen) >= en_az:
            p1, _ = bfs(next(iter(bilesen)), bilesen); p2, ata2 = bfs(p1, bilesen)
            yol = [p2]
            while ata2[yol[-1]] is not None: yol.append(ata2[yol[-1]])
            if len(yol) < en_az: break
            yollar.append(yol)
            yakin = set()
            for p in yol:                                  # yolun 3 hucre cevresini dus
                for dr in range(-3, 4):
                    for dc in range(-3, 4): yakin.add((p[0] + dr, (p[1] + dc) % (2 * W)))
            bilesen -= yakin
        kalan -= set(ata)
    return yollar

def _ll(p):
    r2, c2 = p; return LA(r2 / 2 - 0.5), LO(c2 / 2 - 0.5)

SLUG = dict(zip(ADLAR, ["kuzey", "dogudil", "orta", "uzunyar", "ada", "doguhavza", "doguok", "batiok", "kutup", "guneyok", "buyukok"]))
S = {}; AD = {}; CIFT = {}
for (i, j), pts in sorted(_kenarlar().items()):
    A_, B_ = ADLAR[i - 1], ADLAR[j - 1]; n = 0
    for yol in sorted(_zincirler(pts), key=len, reverse=True):
        ll = [_ll(p) for p in yol]
        # dikisi gecen yolu boylamda bol
        parcalar = [[ll[0]]]
        for a, b in zip(ll[:-1], ll[1:]):
            if abs(b[1] - a[1]) > 180: parcalar.append([b])
            else: parcalar[-1].append(b)
        for pc in parcalar:
            if len(pc) < 6: continue
            n += 1
            ad = "%s_%s" % (SLUG[A_], SLUG[B_]) + ("" if n == 1 else "_%d" % n)
            S[ad] = yeniden_ornekle(yumusat(pc, 9), 0.5)
            AD[ad] = "%s / %s" % (A_, B_); CIFT[ad] = (A_, B_)

# ------------------------------------------------------------------ adimlar ve siniflar
ADIMLAR = []
for sad, p in S.items():
    for (a1, b1), (a2, b2) in zip(p[:-1], p[1:]):
        m = ((a1 + a2) / 2, (b1 + b2) / 2); c = np.cos(np.radians(m[0]))
        t = np.array([(b2 - b1) * c, a2 - a1]); L = np.hypot(*t)
        if L == 0: continue
        t = t / L; nrm = np.array([-t[1], t[0]])          # sol normal (dogu, kuzey)
        d = 0.35
        sol = (m[0] + nrm[1] * d, m[1] + nrm[0] * d / max(c, 0.2)); sag = (m[0] - nrm[1] * d, m[1] - nrm[0] * d / max(c, 0.2))
        A, B = levha_at(*sol), levha_at(*sag)
        if {A, B} != set(CIFT[sad]):
            # cok dar yerde orneklem uc levhaya dustu: ciftin yonu sol yandan
            A, B = CIFT[sad] if A != CIFT[sad][1] else CIFT[sad][::-1]
        v = hiz(A, *m) - hiz(B, *m)                       # solun saga gore hizi
        yak = -(v @ nrm); boy = v @ t; hz = np.hypot(yak, boy)
        okyanus = not (kara_at(*sol) or kara_at(*sag))
        if hz < 0.2: sinif = "PAS"
        elif np.degrees(np.arctan2(abs(yak), abs(boy))) < 20: sinif = "OTF" if okyanus else "CTF"
        elif yak > 0:
            if okyanus: sinif = "SUB" if LEVHALAR[A]["sira"] != LEVHALAR[B]["sira"] else "OCB"
            else: sinif = "CCB" if (kara_at(*sol) and kara_at(*sag)) else "SUB"
        else: sinif = "OSR" if okyanus else "CRB"
        ust = None
        if sinif in ("SUB", "CCB", "OCB"):
            ka, kb = kara_at(*sol), kara_at(*sag)
            ust = A if (ka and not kb) else B if (kb and not ka) else (A if LEVHALAR[A]["sira"] >= LEVHALAR[B]["sira"] else B)
        km = np.hypot((b2 - b1) * c, a2 - a1) * np.radians(1) * RKM
        # sahibin goruntusunde de bu iki levha mi karsi karsiya (cerceve disi uzantilar ve yer tutucular haric)
        gi = lambda la_, lo_: int(goruntu[min(max(row(la_), 0), H - 1), col(((lo_ + 180) % 360) - 180) % W])
        goruntude = {gi(*sol), gi(*sag)} == {LEVHALAR[A]["kimlik"], LEVHALAR[B]["kimlik"]}
        ADIMLAR.append(dict(sinir=sad, p=(a1, b1), q=(a2, b2), sol=A, sag=B, sinif=sinif, ust=ust,
                            yaklasma=round(float(yak), 2), yanal=round(float(boy), 2), km=round(float(km), 1), goruntude=goruntude))

SINIF_AD = {"OSR": "okyanus sırtı", "OTF": "okyanus dönüşüm fayı", "OCB": "okyanusal yakınlaşma", "SUB": "dalma",
            "CRB": "kıta yarığı", "CTF": "kıta dönüşüm fayı", "CCB": "kıta çarpışması", "PAS": "hareketsiz"}

# ------------------------------------------------------------------ amaclanan turle karsilastirma
TUR_SINIF = {"ayrılma": {"OSR", "CRB"}, "yanal": {"OTF", "CTF"}, "dalma": {"SUB", "OCB"},
             "kıta çarpışması": {"CCB", "SUB"}}
def karsilastir():
    """kaynak/sinirlar_hikaye.json'daki amaclanan tur ile Bird sinifi, levha cifti basina"""
    amac = json.load(open(os.path.join(KAYNAK, "sinirlar_hikaye.json"), encoding="utf-8"))
    km = defaultdict(lambda: defaultdict(float)); dis = defaultdict(float)
    for a in ADIMLAR:
        if a["goruntude"]: km[frozenset((a["sol"], a["sag"]))][a["sinif"]] += a["km"]
        else: dis[frozenset((a["sol"], a["sag"]))] += a["km"]
    out = []
    for s in amac:
        cift = frozenset(s["levhalar"]); tur = s["tur"].split(" (")[0]
        sc = km.get(cift)
        if not sc:
            out.append(dict(levhalar=s["levhalar"], amac=tur, bird=None, uyum=None, km=0, disarida_km=round(dis.get(cift, 0)),
                            paylar={}, aciklama=s["aciklama"])); continue
        top = sum(sc.values()); bas = max(sc, key=sc.get); uy = sum(v for k, v in sc.items() if k in TUR_SINIF[tur]) / top
        out.append(dict(levhalar=s["levhalar"], amac=tur, bird=bas, uyum=round(uy, 2), km=round(top), disarida_km=round(dis.get(cift, 0)),
                        paylar={k: round(v / top, 2) for k, v in sorted(sc.items(), key=lambda x: -x[1])}, aciklama=s["aciklama"]))
    return out

def yaz(dizin=os.path.join(KOK, "tektonik")):
    dla, dlo = 180 / H, 360 / W
    alan = (RKM * np.radians(dla)) * (RKM * np.radians(dlo)) * np.cos(np.radians(lat))[:, None] * np.ones((1, W))
    out = {"yontem": "TEKTONIK.md 'Yeni hikâye (23 Kasım)'; kıta levhaları sahibin kimlik görüntüsünden, sınıflar Bird (2003) ölçütü, 20 derece eşiği",
           "cerceve": "Kuzey Levhası sabit; hız cm/yıl", "cozunurluk_derece": round(dla, 4), "levhalar": {}, "sinif_uzunluk_km": {}}
    for i, ad in enumerate(ADLAR, 1):
        L = LEVHALAR[ad]; m = kimlik == i; om = L["omega"]; rt = np.linalg.norm(om)
        kut = (float(np.degrees(np.arcsin(om[2] / rt))), float(np.degrees(np.arctan2(om[1], om[0])))) if rt else None
        out["levhalar"][ad] = {"kimlik": i, "tohum": L["tohum"], "hiz_tohumda_dogu_kuzey": L["hiz"], "sira": L["sira"],
                               "euler_kutbu": [round(kut[0], 2), round(kut[1], 2)] if kut else None,
                               "euler_hizi_derece_My": round(float(np.degrees(rt)), 4),
                               "alan_milyon_km2": round(float(alan[m].sum() / 1e6), 2),
                               "kara_payi": round(float((alan * (m & land)).sum() / max(alan[m].sum(), 1)), 3)}
    for a in ADIMLAR: out["sinif_uzunluk_km"][a["sinif"]] = round(out["sinif_uzunluk_km"].get(a["sinif"], 0) + a["km"], 0)
    out["adim_sayisi"] = len(ADIMLAR)
    out["amaclanan_tur_karsilastirma"] = karsilastir()
    json.dump(out, open(os.path.join(dizin, "levhalar.json"), "w"), ensure_ascii=False, indent=1)
    gj = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "LineString", "coordinates": [[a["p"][1], a["p"][0]], [a["q"][1], a["q"][0]]]},
         "properties": {k: a[k] for k in ("sinir", "sol", "sag", "sinif", "ust", "yaklasma", "yanal", "km", "goruntude")}} for a in ADIMLAR]}
    json.dump(gj, open(os.path.join(dizin, "sinirlar.geojson"), "w"), ensure_ascii=False)
    Image.fromarray(kimlik).save(os.path.join(dizin, "levha_kimlik.png"), optimize=True)
    return out

if __name__ == "__main__":
    o = yaz()
    for ad, v in o["levhalar"].items(): print("%-24s %6.2f milyon km2  kara %%%2.0f  kutup %s  %.3f d/My" % (ad, v["alan_milyon_km2"], 100 * v["kara_payi"], v["euler_kutbu"], v["euler_hizi_derece_My"]))
    print("adim", o["adim_sayisi"], "ort km %.1f" % (sum(a["km"] for a in ADIMLAR) / len(ADIMLAR)))
    for s_, km in sorted(o["sinif_uzunluk_km"].items(), key=lambda x: -x[1]): print("  %s %-22s %7.0f km" % (s_, SINIF_AD[s_], km))
    print("amaclanan tur ile Bird sinifi:")
    for x in o["amaclanan_tur_karsilastirma"]:
        print("  %-48s amac %-16s bird %-4s uyum %-4s %5s km (+%5s disarida)  %s" % (" / ".join(x["levhalar"]), x["amac"], x["bird"], x["uyum"], x["km"], x["disarida_km"], x["paylar"]))
