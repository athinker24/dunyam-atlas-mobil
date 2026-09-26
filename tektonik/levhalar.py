# -*- coding: utf-8 -*-
"""Dunyam levha modeli: kapali levhalar, Euler vektorleri, siniflanmis sinir adimlari.

Yontem (TEKTONIK.md "Levha modeli"):
- Sinirlar enlem/boylam cizgileri olarak sayisallastirilir; karadakiler
  araziden olculur (dag etekleri, kiyilar), okyanustakiler tasarlanir
  (sirtlar, donusum faylari, cukurlar). Cizgiler 0.1 derecelik kuresel
  gride yakilir, kalan bolgeler 4-komsulukla etiketlenir (boylamda
  sarmal): gezegenin her hucresi tam bir levhaya aittir (GPlates kapali
  levha cokgenleri ilkesi).
- Her levhaya bir hiz verilir (Kuzey levhasi sabit cerceve), buradan Euler
  vektoru (w = r x v / R) turetilir.
- Sinirlar ~0.5 derecelik adimlara bolunur (PB2002'de ort. 44.7 km). Her
  adimin sinifi Bird (2003) olcutuyle hesaptan cikar: goreli hiz sinira
  20 dereceden yakinsa yanal, degilse yaklasma/ayrilma; iki yani da
  denizse okyanusal, degilse kitasal. Yedi sinif: OSR OTF OCB SUB CRB CTF CCB.
"""
import json, os, sys
import numpy as np
from scipy import ndimage

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

# ------------------------------------------------------------------ levhalar
# hiz: (enlem, boylam) noktasinda (dogu, kuzey) cm/yil, Kuzey levhasina gore.
# sira: carpisma ve okyanus-okyanus dalmasinda ust levhayi secer (buyuk ust).
LEVHALAR = {
    "Kuzey":           dict(tohum=(50, 0),    hiz=(0.0, 0.0),   sira=10, renk=(120, 150, 200)),
    "Kuzeydoğu":       dict(tohum=(47, 34),   hiz=(1.5, 0.0),   sira=9,  renk=(170, 120, 210)),
    "İber":            dict(tohum=(38, -28),  hiz=(0.0, 0.5),   sira=6,  renk=(210, 170, 90)),
    "Ege":             dict(tohum=(26, -12),  hiz=(-0.5, -2.0), sira=9,  renk=(90, 200, 200)),
    "Güneybatı":       dict(tohum=(15, -25),  hiz=(0.0, 1.0),   sira=7,  renk=(220, 130, 100)),
    "Yarımada":        dict(tohum=(6, -3),    hiz=(-2.0, 1.0),  sira=8,  renk=(230, 200, 120)),
    "Alt Kıta":        dict(tohum=(12, 12),   hiz=(0.3, 4.0),   sira=5,  renk=(130, 200, 120)),
    "Batı Okyanusu":   dict(tohum=(0, -60),   hiz=(5.0, 1.0),   sira=2,  renk=(80, 120, 170)),
    "Doğu Okyanusu":   dict(tohum=(0, 60),    hiz=(-6.0, 0.0),  sira=2,  renk=(90, 150, 150)),
    "Büyük Okyanus":   dict(tohum=(0, 130),   hiz=(1.0, 1.0),   sira=2,  renk=(100, 110, 170)),
    "Uzak Okyanus":    dict(tohum=(0, -150),  hiz=(-3.0, -0.5), sira=1,  renk=(110, 130, 190)),
    "Kuzey Kutup":     dict(tohum=(84, 0),    hiz=(1.0, 0.0),   sira=3,  renk=(70, 95, 130)),
    "Güney Kutup":     dict(tohum=(-72, 0),   hiz=(1.0, 0.0),   sira=3,  renk=(70, 90, 125)),
}
def birim(la, lo):
    a, b = np.radians(la), np.radians(lo)
    return np.array([np.cos(a) * np.cos(b), np.cos(a) * np.sin(b), np.sin(a)])
def en(la, lo):
    b = np.radians(lo); a = np.radians(la)
    return np.array([-np.sin(b), np.cos(b), 0.0]), np.array([-np.sin(a) * np.cos(b), -np.sin(a) * np.sin(b), np.cos(a)])
for ad, L in LEVHALAR.items():
    la, lo = L["tohum"]; ve, vn = L["hiz"]; E_, N_ = en(la, lo)
    v = (ve * E_ + vn * N_) * 10.0                       # km/My
    L["omega"] = np.cross(birim(la, lo), v) / RKM          # rad/My
def hiz(ad, la, lo):
    """levhanin (enlem, boylam) noktasindaki hizi, (dogu, kuzey) cm/yil"""
    v = np.cross(LEVHALAR[ad]["omega"], birim(la, lo) * RKM) / 10.0; E_, N_ = en(la, lo)
    return np.array([v @ E_, v @ N_])

# ------------------------------------------------------------------ sinirlar
def olculen(ad):
    """araziden olculen kara sinirlari (TEKTONIK.md bolum 1-6)"""
    p = []
    if ad == "duvar":             # Duvar'in guney etegi, boylam 7.6..33
        for lo in np.arange(7.6, 33.2, 0.5):
            x = col(lo); r = np.where(land[row(45):row(25), x] & (es[row(45):row(25), x] > 2500))[0]
            if not len(r): continue
            y = row(45) + r.max()
            while y < row(20) and land[y, x] and es[y, x] > 1200: y += 1
            p.append((LA(y), lo))
    elif ad == "pireneler":       # 5'in guney etegi
        for lo in np.arange(-41, -16, 0.5):
            x = col(lo); r = np.where(land[row(53):row(38), x] & (es[row(53):row(38), x] > 2500))[0]
            if not len(r): continue
            y = row(53) + r.max()
            while y < row(33) and land[y, x] and es[y, x] > 1200: y += 1
            p.append((LA(y), lo))
    elif ad == "alpler":          # 4'un ic (dogu) etegi
        for la in np.arange(19.5, 3.0, -0.5):
            y = row(la); c0, c1 = col(-21), col(-6)
            r = np.where(land[y, c0:c1] & (es[y, c0:c1] > 2500))[0]
            if not len(r): continue
            x = c0 + r.max()
            while x < col(0) and land[y, x] and es[y, x] > 1300: x += 1
            p.append((la, LO(x)))
    elif ad == "bati_cukur":      # guneybati blogunun bati kiyisi acigi
        for la in np.arange(27.5, 5.0, -0.5):
            y = row(la); c0, c1 = col(-50), col(-22); r = np.where(land[y, c0:c1])[0]
            if len(r): p.append((la, LO(c0 + r.min() - 12)))
    elif ad == "alti":            # 6: kucuk kita carpismasi
        for la in np.arange(6.5, -3.0, -0.5):
            y = row(la); c0, c1 = col(-27), col(-12)
            r = np.where(land[y, c0:c1] & (es[y, c0:c1] > 2200))[0]
            if not len(r): continue
            x = c0 + r.min()
            while x > col(-32) and land[y, x] and es[y, x] > 1000: x -= 1
            p.append((la, LO(x)))
    elif ad == "ege_cukur":       # takimadanin guney acigi
        lab, n = ndimage.label(land, np.ones((3, 3))); ana = np.argmax(np.bincount(lab.ravel())[1:]) + 1
        ada = land & (lab != ana) & (lat[:, None] > 17) & (lat[:, None] < 32) & (lon[None, :] > -22) & (lon[None, :] < -3)
        for lo in np.arange(-21, -3.5, 0.5):
            x = col(lo); r = np.where(ada[:, x])[0]
            if len(r): p.append((LA(r.max() + 16), lo))
    elif ad == "dogu_cukur":      # alt kitanin dogusundaki yarimadanin acigi
        for la in np.arange(21.5, -1.0, -0.5):
            y = row(la); c0, c1 = col(14), col(45); r = np.where(land[y, c0:c1])[0]
            if len(r): p.append((la, LO(c0 + r.max() + 14)))
    return yumusat(p)
def yumusat(p, k=5):
    a = np.array(p, float); o = a.copy()
    for i in range(len(a)): o[i] = a[max(0, i - k // 2): i + k // 2 + 1].mean(0)
    o[0], o[-1] = a[0], a[-1]; return [tuple(x) for x in o]
def zikzak(noktalar):
    return [tuple(x) for x in noktalar]
def halka(la0, genlik, adim, faz=0.0):
    return [(la0 + genlik * np.sin(np.radians(lo * 3 + faz)), lo) for lo in np.arange(-180, 180.01, adim)]
def basamak(la_a, la_b, adim=20):
    """guney halkasi: dogu-bati sirt parcalari, aralarinda kuzey-guney donusum faylari"""
    p = []; lo = -180.0; k = 0
    while lo < 180:
        la = la_a if k % 2 == 0 else la_b; p += [(la, lo), (la, min(lo + adim, 180))]; lo += adim; k += 1
    return p + [(la_a, 180)]   # dikiste halkayi kapat

S = {}   # ad -> cizgi [(enlem, boylam), ...]
S["duvar"] = olculen("duvar")
S["pireneler"] = [(38.5, -47.5)] + olculen("pireneler") + [(40, -14.5), (36.5, -14)]
S["alpler"] = [(15.5, -12.5)] + olculen("alpler")
S["bati_cukur"] = [(28, -48)] + olculen("bati_cukur") + [(4, -40), (3.5, -32), (3.5, -25)]
alti = olculen("alti"); S["alti"] = [(3.5, -25)] + alti + [(-10, -22), (-22, -29), (-35, -35), (-47, -38), (-56, -40)]
eg = olculen("ege_cukur"); S["ege_cukur"] = [(24.5, -21)] + eg + [(19, 0.5)]
S["ege_dogu"] = [(19, 0.5), (22, 0), (26, -0.5), (30, -1), (33, 1), (33.3, 6), S["duvar"][0]]
S["ege_kuzey"] = [(33.3, 6), (35.5, 3), (36.5, -3), (37, -9), (36.5, -14)]
S["ege_bati"] = [(36.5, -14), (35, -17.5), (31, -19), (27, -20), (24.5, -21)]
S["bogaz"] = [(24.5, -21), (25.2, -26), (25.2, -32), (26, -40), (27.5, -46), (28, -48)]
S["iber_bati"] = [(38.5, -47.5), (28, -48)]
S["yar_kuzey"] = [S["alpler"][0], (14.5, -8), (13.5, -3), (13, 1), (12.5, 2.5)]
S["yar_dogu"] = [(12.5, 2.5), (8, 4.5), (4, 6.5), (0, 7), (-5, 7)]
S["yar_guney"] = [S["alpler"][-1], (0, -12), (-2, -5), (-4, 1), (-5, 7)]
S["gb_altkita"] = [(19, 0.5), (16, 1.5), (12.5, 2.5)]
S["gb_altkita_guney"] = [(-5, 7), (-15, 5), (-28, 0), (-42, -3), (-56, -5)]
dc = olculen("dogu_cukur")
S["dogu_cukur"] = [(31, 46), (27, 40), (24, 33), (22, 27)] + dc + [(-12, 25), (-25, 31), (-38, 39), (-56, 46)]
S["duvar_dogu"] = [S["duvar"][-1], (29.5, 38), (30.5, 43), (31, 46)]
S["kuzey_dogu"] = [(31, 46), (38.3, 45.5), (46, 45.5), (53, 44.5), (60, 43), (73, 42)]
S["kd_bati"] = [(55.5, 20.5), (50, 23), (45, 25.2), (40.5, 27)]
S["kd_kuzey"] = [(55.5, 20.5), (55.6, 26), (54.4, 32), (53.2, 38.5), (53, 44.5)]
S["kd_guney"] = [(40.5, 27), (39.6, 31), (39.2, 35), (38.6, 40.5), (38.3, 45.5)]
# --- okyanus sinirlari: taban egrisi + goreli hizdan sekil (tasarim)
RNG = np.random.RandomState(7)
def _en(a, b):   # iki nokta arasi (dogu, kuzey) derece-km benzeri fark
    c = np.cos(np.radians((a[0] + b[0]) / 2)); return np.array([(b[1] - a[1]) * c, b[0] - a[0]]), c
def _goreli(A, B, m):
    v = hiz(A, *m) - hiz(B, *m); n = np.hypot(*v); return v / n if n > 1e-6 else np.array([1.0, 0.0]), n
def merdiven(dugum, A, B, alt=(2, 4)):
    """sirt: parcalar goreli harekete dik, donusum faylari paralel. Taban dugumleri
    arasina duzensiz ara dugumler (1-3 derece yana sapma) konur."""
    taban = [dugum[0]]
    for a, b in zip(dugum[:-1], dugum[1:]):
        k = RNG.randint(alt[0], alt[1] + 1)
        for j in range(1, k):
            t = j / k + RNG.uniform(-0.12, 0.12) / k
            taban.append((a[0] + (b[0] - a[0]) * t + RNG.uniform(-1.2, 1.2), a[1] + (b[1] - a[1]) * t + RNG.uniform(-1.6, 1.6)))
        taban.append(b)
    yol = [taban[0]]
    for a, b in zip(taban[:-1], taban[1:]):
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); d, _ = _goreli(A, B, m); p_ = np.array([-d[1], d[0]])
        D, c = _en(a, b); al = D @ p_; ara = np.array(a) + np.array([(al * p_)[1], (al * p_)[0] / c])
        yol += [tuple(ara), b]
    return yol
def yay(dugum, A, B, bombe=0.14):
    """cukur: dugumler arasi dalan levhaya dogru bombeli yaylar (A ust, B dalan)"""
    yol = [dugum[0]]
    for a, b in zip(dugum[:-1], dugum[1:]):
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); v = hiz(B, *m) - hiz(A, *m); n = np.hypot(*v)
        D, c = _en(a, b); L = np.hypot(*D); u = -v / n if n > 1e-6 else np.array([0, 0])
        for t in np.linspace(0, 1, 7)[1:]:
            q = np.array(a) + (np.array(b) - np.array(a)) * t; k = 4 * t * (1 - t) * bombe * L
            yol.append((q[0] + u[1] * k, q[1] + u[0] * k / c))
    return yol
def halka_dugum(la0, gen, adim, faz):
    return [(la0 + gen * np.sin(np.radians(lo * 2 + faz)) + 0.6 * gen * np.sin(np.radians(lo * 5 + 2 * faz)), float(lo))
            for lo in np.arange(-180, 180.01, adim)]
def bolumlu(dugum, dilimler, ust):
    """halka: boylam dilimlerine gore komsu levha; ayrilmada merdiven, yakinlasmada yay"""
    yol = []
    for lo_a, lo_b, komsu in dilimler:
        dd = [p for p in dugum if lo_a - 1e-6 <= p[1] <= lo_b + 1e-6]
        if len(dd) < 2: continue
        m = dd[len(dd) // 2]; v = hiz(komsu, *m) - hiz(ust, *m)
        D, c = _en(dd[0], dd[-1]); t = D / (np.hypot(*D) or 1); nrm = np.array([-t[1], t[0]])
        ortu = (v @ nrm) * (1 if m[0] > 0 else -1)          # + : komsu kutba dogru (yakinlasma)
        if abs(v @ nrm) < 0.35 * np.hypot(*v): parca = dd
        elif ortu > 0: parca = yay(dd, ust, komsu)
        else: parca = merdiven(dd, ust, komsu, alt=(1, 2))
        yol += parca if not yol else parca[1:]
    return yol
KB = [(77, -118), (66, -112), (55, -100), (44, -92), (35, -86), (27, -84)]
GB = [(27, -84), (16, -88), (5, -96), (-7, -102), (-19, -99), (-31, -90), (-42, -82), (-56, -78)]
S["bati_sirt"] = merdiven(KB, "Kuzey", "Uzak Okyanus")[:-1] + merdiven(GB, "Batı Okyanusu", "Uzak Okyanus")
S["kuzey27"] = [(28, -48), (27.8, -56), (27.3, -64), (27.6, -72), (27.2, -79), (27, -84)]
S["dogu_sirt"] = merdiven([(77, 112), (64, 104), (52, 98), (40, 101), (28, 108), (16, 112), (4, 108), (-8, 100), (-20, 96), (-32, 100), (-44, 108), (-56, 112)],
                          "Doğu Okyanusu", "Büyük Okyanus")
S["orta_cukur"] = yay([(77, 158), (62, 163), (48, 170), (34, 174), (20, 172), (6, 166), (-8, 160), (-22, 157), (-36, 158), (-56, 161)],
                      "Büyük Okyanus", "Uzak Okyanus", bombe=0.18)
S["kuzey_halka"] = bolumlu(halka_dugum(69.5, 3.2, 4, 40), [(-180, -114, "Uzak Okyanus"), (-114, 42, "Kuzey"), (42, 106, "Doğu Okyanusu"),
                                                          (106, 160, "Büyük Okyanus"), (160, 180, "Uzak Okyanus")], "Kuzey Kutup")
S["guney_halka"] = bolumlu(halka_dugum(-42, 4.2, 4, 10), [(-180, -80, "Uzak Okyanus"), (-80, -40, "Batı Okyanusu"), (-40, -5, "Güneybatı"),
                                                           (-5, 45, "Alt Kıta"), (45, 110, "Doğu Okyanusu"), (110, 160, "Büyük Okyanus"),
                                                           (160, 180, "Uzak Okyanus")], "Güney Kutup")
AD = {"duvar": "Duvar dikişi", "pireneler": "5 dikişi (Pireneler benzeri)", "alpler": "4 dikişi (Alpler)",
      "bati_cukur": "Batı dalması (And tipi)", "alti": "6 çarpışması ve güney uzantısı", "ege_cukur": "Ege çukuru",
      "ege_dogu": "Ege doğu sınırı", "ege_kuzey": "Ege yay ardı sınırı", "ege_bati": "Ege batı sınırı",
      "bogaz": "İber-Güneybatı boğazı", "iber_bati": "İber batı kıyısı", "yar_kuzey": "Yarımada kuzeyi (Tiren)",
      "yar_dogu": "Yarımada boğazı", "yar_guney": "Yarımada güneyi", "gb_altkita": "Güneybatı-Alt kıta",
      "gb_altkita_guney": "Güneybatı-Alt kıta güney", "dogu_cukur": "Doğu dalması", "duvar_dogu": "Duvar doğu ucu",
      "kuzey_dogu": "Kuzey doğu kıyısı", "kd_bati": "9 (kaçış bloğu batısı)", "kd_kuzey": "2 (kaçış bloğu kuzeyi)",
      "kd_guney": "kaçış bloğu güneyi", "kuzey27": "27°K dönüşüm fayı", "bati_sirt": "Batı sırtı",
      "dogu_sirt": "Doğu sırtı", "orta_cukur": "Uzak okyanus çukuru", "kuzey_halka": "Kuzey kutup sınırı", "guney_halka": "Güney sırtı"}

# ------------------------------------------------------------------ yak, etiketle
def sik(p, adim=0.05):
    o = []
    for (a1, b1), (a2, b2) in zip(p[:-1], p[1:]):
        n = max(2, int(np.hypot(a2 - a1, b2 - b1) / adim)); t = np.linspace(0, 1, n, endpoint=False)
        o += list(zip(a1 + (a2 - a1) * t, b1 + (b2 - b1) * t))
    return o + [p[-1]]
sinir = np.zeros((H, W), bool)
for p in S.values():
    for la, lo in sik(p):
        r = min(max(row(la), 0), H - 1); c = col(((lo + 180) % 360) - 180) % W; sinir[r, c] = True
sinir = ndimage.binary_dilation(sinir, np.ones((2, 2), bool))
etk, n = ndimage.label(~sinir)   # 4-komsu
# boylam sarmali: sol ve sag kenardaki ayni satir etiketlerini birlestir
es_ = {}
def bul(a):
    while es_.get(a, a) != a: a = es_[a]
    return a
for r in range(H):
    a, b = etk[r, 0], etk[r, -1]
    if a and b and bul(a) != bul(b): es_[bul(a)] = bul(b)
etk = np.vectorize(lambda v: bul(v) if v else 0, otypes=[np.int32])(etk) if es_ else etk
ADLAR = list(LEVHALAR); kimlik = np.zeros((H, W), np.uint8)
for i, ad in enumerate(ADLAR, 1):
    la, lo = LEVHALAR[ad]["tohum"]; v = etk[row(la), col(((lo + 180) % 360) - 180) % W]
    if v == 0: raise SystemExit("tohum sinirda: " + ad)
    if (kimlik[etk == v] > 0).any(): raise SystemExit("iki levha ayni bolgede: %s ile %s" % (ad, ADLAR[kimlik[etk == v].max() - 1]))
    kimlik[etk == v] = i
sahipsiz = (kimlik == 0) & ~sinir
if sahipsiz.sum():
    lb, m = ndimage.label(sahipsiz)
    for k in range(1, m + 1):
        mm = lb == k; kom = kimlik[ndimage.binary_dilation(mm, iterations=3) & (kimlik > 0)]
        kimlik[mm] = np.bincount(kom).argmax() if len(kom) else 0
    print("uyari: %d sahipsiz bolge komsuya verildi (en buyugu %d hucre)" % (m, max(np.bincount(lb.ravel())[1:])))
# sinir hucrelerini en yakin levhaya ver
idx = ndimage.distance_transform_edt(kimlik == 0, return_distances=False, return_indices=True)
kimlik = kimlik[idx[0], idx[1]]

# ------------------------------------------------------------------ adimlar ve siniflar
def levha_at(la, lo):
    return ADLAR[kimlik[min(max(row(la), 0), H - 1), col(((lo + 180) % 360) - 180) % W] - 1]
def kara_at(la, lo):
    return bool(land[min(max(row(la), 0), H - 1), col(((lo + 180) % 360) - 180) % W])
ADIMLAR = []
for sad, p in S.items():
    q = sik(p, 0.5)
    for (a1, b1), (a2, b2) in zip(q[:-1], q[1:]):
        m = ((a1 + a2) / 2, (b1 + b2) / 2); c = np.cos(np.radians(m[0]))
        t = np.array([(b2 - b1) * c, a2 - a1]); L = np.hypot(*t)
        if L == 0: continue
        t = t / L; nrm = np.array([-t[1], t[0]])          # sol normal (dogu, kuzey)
        d = 0.35
        sol = (m[0] + nrm[1] * d, m[1] + nrm[0] * d / max(c, 0.2)); sag = (m[0] - nrm[1] * d, m[1] - nrm[0] * d / max(c, 0.2))
        A, B = levha_at(*sol), levha_at(*sag)
        if A == B: continue
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
        ADIMLAR.append(dict(sinir=sad, p=(a1, b1), q=(a2, b2), sol=A, sag=B, sinif=sinif, ust=ust,
                            yaklasma=round(float(yak), 2), yanal=round(float(boy), 2), km=round(float(km), 1)))

SINIF_AD = {"OSR": "okyanus sırtı", "OTF": "okyanus dönüşüm fayı", "OCB": "okyanusal yakınlaşma", "SUB": "dalma",
            "CRB": "kıta yarığı", "CTF": "kıta dönüşüm fayı", "CCB": "kıta çarpışması", "PAS": "hareketsiz"}

def yaz(dizin=os.path.join(KOK, "tektonik")):
    from PIL import Image
    alan = (RKM * np.radians(RES)) ** 2 * np.cos(np.radians(lat))[:, None] * np.ones((1, W))
    out = {"yontem": "TEKTONIK.md 'Levha modeli'; siniflar Bird (2003) olcutu, 20 derece esigi",
           "cerceve": "Kuzey levhasi sabit; hiz cm/yil", "cozunurluk_derece": RES, "levhalar": {}, "sinif_uzunluk_km": {}}
    for i, ad in enumerate(ADLAR, 1):
        L = LEVHALAR[ad]; m = kimlik == i; om = L["omega"]; rt = np.linalg.norm(om)
        kut = (float(np.degrees(np.arcsin(om[2] / rt))), float(np.degrees(np.arctan2(om[1], om[0])))) if rt else None
        out["levhalar"][ad] = {"kimlik": i, "tohum": L["tohum"], "hiz_tohumda_dogu_kuzey": L["hiz"], "sira": L["sira"],
                               "euler_kutbu": [round(kut[0], 2), round(kut[1], 2)] if kut else None,
                               "euler_hizi_derece_My": round(float(np.degrees(rt)), 4),
                               "alan_milyon_km2": round(float(alan[m].sum() / 1e6), 2),
                               "kara_payi": round(float((alan * (m & land)).sum() / alan[m].sum()), 3)}
    for a in ADIMLAR: out["sinif_uzunluk_km"][a["sinif"]] = round(out["sinif_uzunluk_km"].get(a["sinif"], 0) + a["km"], 0)
    out["adim_sayisi"] = len(ADIMLAR)
    json.dump(out, open(os.path.join(dizin, "levhalar.json"), "w"), ensure_ascii=False, indent=1)
    gj = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "LineString", "coordinates": [[a["p"][1], a["p"][0]], [a["q"][1], a["q"][0]]]},
         "properties": {k: a[k] for k in ("sinir", "sol", "sag", "sinif", "ust", "yaklasma", "yanal", "km")}} for a in ADIMLAR]}
    json.dump(gj, open(os.path.join(dizin, "sinirlar.geojson"), "w"), ensure_ascii=False)
    Image.fromarray(kimlik).save(os.path.join(dizin, "levha_kimlik.png"), optimize=True)
    return out

if __name__ == "__main__":
    o = yaz()
    for ad, v in o["levhalar"].items(): print("%-15s %6.2f milyon km2  kara %%%2.0f  kutup %s  %.3f d/My" % (ad, v["alan_milyon_km2"], 100 * v["kara_payi"], v["euler_kutbu"], v["euler_hizi_derece_My"]))
    print("adim", o["adim_sayisi"], "ort km %.1f" % (sum(a["km"] for a in ADIMLAR) / len(ADIMLAR)))
    for s_, km in sorted(o["sinif_uzunluk_km"].items(), key=lambda x: -x[1]): print("  %s %-22s %7.0f km" % (s_, SINIF_AD[s_], km))
    from collections import Counter
    for sad in S:
        c = Counter(a["sinif"] for a in ADIMLAR if a["sinir"] == sad)
        print("  %-18s %s" % (sad, dict(c)))
