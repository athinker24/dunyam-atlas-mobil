"""Uygulama için su verisi: data/su.json (uret_su.py çağırır).

Nehirler kol kol: her ağızdan ana kol (kaynağa en uzak yol) kaynağa kadar
izlenir, ona katılan her kol ayrı bir kol olarak aynı şekilde. Her kolun bir
KADEMESİ var; uygulama genel görünümde yalnız 1. kademeyi (büyük ve uzun ana
kollar) çizer, yakınlaştıkça 2-3'ü açar, "tüm kollar" seçilince hepsini.
Gerçek atlaslarda da böyle: nehir ağacı ölçeğe göre seyreltilir.

Kademe (kolun ağzındaki/katıldığı yerdeki debi Q ve kolun boyu L):
    1: Q >= 2000 m³/s ya da L >= 1500 km
    2: Q >=  600          ya da L >=  600
    3: Q >=  200          ya da L >=  250
    4: geri kalan (Q >= 50)
Bir kol, katıldığı koldan daha önemli sayılmaz (kademesi en az onunki).

Çizgi: D8 basamakları Ramer-Douglas-Peucker ile silinir, iki düzey orta nokta
kaydırmayla kıvrım verilir; birleşme noktaları sabit tepe olarak kalır ki
kollar ana kola tam otursun. Uygulama noktalardan geçen eğriyle çizer.
Kodlama: koordinatlar 0.01° tamsayı, fark kodlu; debi 10·log10(Q).

Göller: her gölün hücre maskesi 3 kat büyütülüp yumuşatılır, 0.5 eş değer
eğrisi (marching squares) kıyı çizgisi olur.
"""
import json, os
import numpy as np
from scipy import ndimage

BURASI = os.path.dirname(os.path.abspath(__file__)); KOK = os.path.dirname(BURASI)
NEHIR_Q = 50.0


def kademe(q, L):
    if q >= 2000 or L >= 1500:
        return 1
    if q >= 600 or L >= 600:
        return 2
    if q >= 200 or L >= 250:
        return 3
    return 4


def rdp(p, tol):
    if len(p) < 3:
        return p
    a, b = p[0], p[-1]; d = b - a; L = np.hypot(*d)
    u = np.hypot(*(p - a).T) if L == 0 else np.abs(d[0] * (p[:, 1] - a[1]) - d[1] * (p[:, 0] - a[0])) / L
    i = int(np.argmax(u))
    if u[i] <= tol:
        return np.array([a, b])
    return np.vstack([rdp(p[:i + 1], tol)[:-1], rdp(p[i:], tol)])


def kivir(p, rng, duzey=2, oran=0.16):
    for _ in range(duzey):
        yeni = [p[0]]
        for a, b in zip(p[:-1], p[1:]):
            d = b - a; L = np.hypot(*d)
            if L < 1.2:
                yeni.append(b); continue
            n = np.array([-d[1], d[0]]) / L
            yeni += [(a + b) / 2 + n * L * rng.normal(0, oran), b]
        p = np.array(yeni)
    return p


def nehirler(alici, q, boy, gm, deniz, lat, lon):
    ny, nx = q.shape
    qf, bf = q.ravel(), boy.ravel()
    nm = (qf >= NEHIR_Q) & ~gm.ravel() & ~deniz.ravel()
    idx = np.where(nm)[0]
    # nehir içi çocuk listeleri
    g = nm[np.maximum(alici, 0)] & (alici >= 0) & nm
    cc = np.where(g)[0]; o = np.argsort(alici[cc], kind="stable"); cc = cc[o]; ust = alici[cc]
    bas = np.searchsorted(ust, np.arange(ny * nx)); son = np.searchsorted(ust, np.arange(ny * nx), side="right")
    cocuk = lambda c: cc[bas[c]:son[c]]
    agizlar = [c for c in idx if alici[c] < 0 or not nm[alici[c]]]
    agizlar.sort(key=lambda c: -qf[c])
    kollar = []
    yig = [(c, 1, None) for c in agizlar]      # (ağız hücresi, üst kademe, katıldığı hücre)
    while yig:
        c, ust_k, katilim = yig.pop()
        stem = [c]; x = c
        while True:
            ch = cocuk(x)
            if len(ch) == 0:
                break
            x = int(ch[np.argmax(bf[ch])]); stem.append(x)
        L = bf[c]
        k = max(ust_k if katilim is not None else 1, kademe(qf[c], L))
        stem = stem[::-1]                       # kaynaktan ağıza
        # ağız: denize/göle giren ya da katıldığı hücre sona eklenir
        uc = katilim if katilim is not None else (alici[c] if alici[c] >= 0 else None)
        if uc is not None:
            stem.append(int(uc))
        kollar.append(dict(k=k, hucre=stem, katilim=katilim))
        # yan kollar: stem üzerindeki her hücrenin ana yol dışındaki çocukları
        ana = set(stem)
        # eklenen uç hücre (katıldığı kol ya da göl/deniz) bu kolun değil:
        # onun çocukları (bu kolun kardeşleri) yeniden eklenmesin
        for s in (stem[:-1] if uc is not None else stem):
            if not nm[s]:
                continue
            for ch in cocuk(s):
                if ch not in ana:
                    yig.append((int(ch), k, int(s)))
    # birleşme noktaları: her kolun katıldığı hücre, ana kolda sabit tepe
    sabit = set(kol["katilim"] for kol in kollar if kol["katilim"] is not None)
    rng = np.random.default_rng(1492)
    cikis = []
    for kol in kollar:
        h = np.array(kol["hucre"])
        p = np.column_stack([h % nx, h // nx]).astype(float)       # (sütun, satır)
        qq = qf[h]
        # sabit noktalardan böl, parça parça sadeleştir ve kıvır
        kes = [0] + [i for i in range(1, len(h) - 1) if int(h[i]) in sabit] + [len(h) - 1]
        pts, qs = [p[0]], [qq[0]]
        for a, b in zip(kes[:-1], kes[1:]):
            parca = rdp(p[a:b + 1], 0.75)
            parca = kivir(parca, rng)
            # her yeni noktanın debisi: özgün yoldaki en yakın hücreden
            for v in parca[1:]:
                j = a + int(np.argmin(np.hypot(*(p[a:b + 1] - v).T)))
                pts.append(v); qs.append(qq[j])
        pts = np.array(pts)
        lo = lon[0] + pts[:, 0] * (lon[1] - lon[0]); la = lat[0] + pts[:, 1] * (lat[1] - lat[0])
        X = np.round(lo * 100).astype(int); Y = np.round(la * 100).astype(int)
        kod = [int(X[0]), int(Y[0])]
        for i in range(1, len(X)):
            kod += [int(X[i] - X[i - 1]), int(Y[i] - Y[i - 1])]
        cikis.append(dict(k=kol["k"], p=kod, q=[int(round(10 * np.log10(max(v, 1)))) for v in qs],
                          L=int(bf[h[-2] if len(h) > 1 else h[-1]]), Q=int(qf[h[-2] if len(h) > 1 else h[-1]])))
    return cikis


def es_egri(f, seviye=0.5):
    """Marching squares: f'in 'seviye' eş değer eğrileri, kapalı halkalar (satır, sütun)."""
    ny, nx = f.shape
    b = f >= seviye
    kenar = {}
    def nokta(i1, j1, i2, j2):
        a, c = f[i1, j1], f[i2, j2]
        t = (seviye - a) / (c - a) if c != a else 0.5
        return (i1 + t * (i2 - i1), j1 + t * (j2 - j1))
    parcalar = []
    for i in range(ny - 1):
        for j in range(nx - 1):
            k = (b[i, j] << 3) | (b[i, j + 1] << 2) | (b[i + 1, j + 1] << 1) | b[i + 1, j]
            if k in (0, 15):
                continue
            U = nokta(i, j, i, j + 1); R = nokta(i, j + 1, i + 1, j + 1)
            D = nokta(i + 1, j, i + 1, j + 1); L = nokta(i, j, i + 1, j)
            tablo = {1: [(L, D)], 2: [(D, R)], 3: [(L, R)], 4: [(U, R)], 5: [(L, U), (D, R)], 6: [(U, D)],
                     7: [(L, U)], 8: [(U, L)], 9: [(U, D)], 10: [(U, R), (L, D)], 11: [(U, R)],
                     12: [(L, R)], 13: [(D, R)], 14: [(L, D)]}
            parcalar += tablo[k]
    # parçaları uç uca bağla (yön gözetmeden: her uç noktanın iki komşusu var)
    yuv = lambda p: (round(p[0], 6), round(p[1], 6))
    komsu, nokta_ = {}, {}
    for a, c in parcalar:
        ka, kc = yuv(a), yuv(c)
        if ka == kc:
            continue
        komsu.setdefault(ka, []).append(kc); komsu.setdefault(kc, []).append(ka)
        nokta_[ka] = a; nokta_[kc] = c
    gezildi = set(); halkalar = []
    for bas in list(komsu):
        if bas in gezildi:
            continue
        halka = [bas]; gezildi.add(bas); onceki, x = None, bas
        while True:
            aday = [n for n in komsu[x] if n != onceki and n not in gezildi]
            if not aday:
                break
            onceki, x = x, aday[0]; halka.append(x); gezildi.add(x)
        if len(halka) > 3:
            halkalar.append(np.array([nokta_[k] for k in halka]))
    return halkalar


def goller_kiyi(goller, shape, lat, lon, S=3):
    ny, nx = shape
    out = []
    for g in goller:
        m = np.zeros(ny * nx, bool); m[g["hucreler"]] = True; m = m.reshape(ny, nx)
        r, c = np.where(m); r0, r1, c0, c1 = r.min() - 2, r.max() + 3, c.min() - 2, c.max() + 3
        sub = m[max(r0, 0):r1, max(c0, 0):c1].astype(float)
        f = ndimage.zoom(sub, S, order=1)
        f = ndimage.gaussian_filter(f, S * 0.45)
        halkalar = [h for h in es_egri(f, 0.42) if len(h) >= 6]
        cokgen = []
        for h in halkalar:
            h = rdp(h, 0.35)
            if len(h) < 4:
                continue
            satir = max(r0, 0) + (h[:, 0] + 0.5) / S - 0.5; sutun = max(c0, 0) + (h[:, 1] + 0.5) / S - 0.5
            la = lat[0] + satir * (lat[1] - lat[0]); lo = lon[0] + sutun * (lon[1] - lon[0])
            X = np.round(lo * 100).astype(int); Y = np.round(la * 100).astype(int)
            kod = [int(X[0]), int(Y[0])]
            for i in range(1, len(X)):
                kod += [int(X[i] - X[i - 1]), int(Y[i] - Y[i - 1])]
            cokgen.append(kod)
        if cokgen:
            out.append(dict(c=cokgen, tuz=not g["cikisli"], alan=int(g["alan_km2"]), derin=int(g["derin_m"]),
                            sev=int(g["seviye"]), koken=g.get("koken", ""), giren=round(g["giren_km3_yil"], 2)))
    return out


def yaz(goller, alici, q, boy, gm, deniz, lat, lon):
    n = nehirler(alici, q, boy, gm, deniz, lat, lon)
    l = goller_kiyi(goller, q.shape, lat, lon)
    veri = dict(ne="Dünyam gölleri ve nehirleri (su/uret_su.py, su/disa.py)", kademe_esikleri=dict(
        k1="Q>=2000 m3/s ya da boy>=1500 km", k2="Q>=600 ya da >=600 km", k3="Q>=200 ya da >=250 km", k4="Q>=50"),
        nehirler=n, goller=l)
    yol = os.path.join(KOK, "data", "su.json")
    with open(yol, "w", encoding="utf-8") as fh:
        json.dump(veri, fh, ensure_ascii=False, separators=(",", ":"))
    from collections import Counter
    print("su.json: %d kol %s, %d göl, %.0f KB" % (len(n), dict(sorted(Counter(x["k"] for x in n).items())), len(l),
                                                 os.path.getsize(yol) / 1024))


if __name__ == "__main__":
    import pickle
    d = pickle.load(open(os.path.join(BURASI, "_disa.pkl"), "rb"))
    yaz(**d)
