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
# Adalar (ana kıtaya bağlı olmayan kara) (27 Eylül, sahibi: "adalarda su
# yok"): 50 m³/s eşiği adaların bütün nehirlerini siliyordu. Gerçekte büyük
# Akdeniz adalarının en büyük nehirleri bu eşiğin altında: Simeto (Sicilya)
# ~25, Tirso (Sardinya, 152 km) ~17 m³/s. Takımadanın akışı yılda ~90 mm
# (yarı kurak): 10 m³/s eşiği bile ana adada yalnız birkaç kol bırakıyordu.
# Atlaslar adada nehri debiyle değil boyla seçer (kurak adaların mevsimlik
# nehirleri de çizilir). Adada: debi >= 3 m³/s (ağ bağlı kalsın), denize
# dökülen kol en az 60 km, yan kol en az 40 km (yoksa kıyı boyunca kısa
# dere tarağı çıkar). Kademe ada ölçeğinde: ana nehirler orta ölçekte görünür.
ADA_Q, ADA_BOY, ADA_KOL_BOY = 3.0, 60.0, 40.0


def kademe_ada(q, L):
    if q >= 300 or L >= 300:
        return 2
    if q >= 60 or L >= 120:
        return 3
    return 4


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


def yumusak_kivrim(p, rng, egim=None):
    """Uzun dalga boylu yanal kıvrım (hücre birimi). Rastgele beyaz titreme
    el yapımı görünüyordu; onsuz da D8'in düz ışınları cetvel gibi kalıyordu.
    Yol 0.5 hücre aralıkla yeniden örneklenir, yana 7, 13 ve 23 hücre dalga
    boylu üç sinüsün toplamı kadar kaydırılır; zarf sin(πs/L) uçlarda sıfır,
    birleşme noktaları yerinde kalır. Genlik dalga boyuyla orantılı: ovada
    (eğim < 0.6 m/km) 0.11, dağda 0.045 katı. Sonra hafifçe sadeleştirilir."""
    if len(p) < 2:
        return p
    # önce köşeleri yuvarla (Chaikin, iki tur, uçlar sabit): düz ovada su
    # basma yolu dik açılı dönüyordu
    for _ in range(2):
        if len(p) < 3:
            break
        q1 = 0.75 * p[:-1] + 0.25 * p[1:]; q2 = 0.25 * p[:-1] + 0.75 * p[1:]
        p = np.vstack([p[:1], np.column_stack([q1, q2]).reshape(-1, 2)[1:-1], p[-1:]])
    d = np.hypot(*np.diff(p, axis=0).T); s = np.concatenate([[0], np.cumsum(d)]); L = s[-1]
    if L < 2:
        return p
    n = max(int(L / 0.25), 2)
    t = np.linspace(0, L, n + 1)
    x = np.interp(t, s, p[:, 0]); y = np.interp(t, s, p[:, 1])
    dx = np.gradient(x); dy = np.gradient(y); nn = np.hypot(dx, dy) + 1e-9
    nx_, ny_ = -dy / nn, dx / nn
    # genlik dalga boyuyla orantılı (ovada 0.11, dağda 0.045 × dalga boyu;
    # sabit 0.45 hücre yakından bakınca bile görünmüyordu)
    k = 0.2 if (egim is None or egim < 0.6) else 0.11   # 27 Eylül: 0.11/0.045 telefonda "çok düz"
    off = sum(k * lam * w * np.sin(2 * np.pi * t / lam + rng.uniform(0, 2 * np.pi))
              for lam, w in ((2.5, 0.35), (4, 0.45), (7, 0.5), (13, 0.35), (23, 0.25)))
    off = off * np.sin(np.pi * t / L)
    q = np.column_stack([x + nx_ * off, y + ny_ * off])
    return rdp(q, 0.04)


class KaydirmaAlani:
    """Bütün nehir ağına ortak, yumuşak 2B kaydırma alanı (hücre birimi).

    Her kola ayrı kıvrım verilince birleşme noktalarında sıfıra inmesi
    gerekiyordu; çok kol alan ana kollar kısa parçalara bölündüğü için düz
    kalıyordu. Alan konumun işlevi olduğu için ana kol ve ona katılan kol
    birleşme noktasında AYNI kadar kayar: bağ kopmaz, kıvrım kesilmez.
    Yön ve dalga boyu (2.5-24 hücre) rastgele sabit bileşenlerin toplamı.
    Genlik ovada tam, dağda (eğim > 25 m/hücre) yarıya iner.
    """
    def __init__(self, Z, shape, rng, genlik=1.25, su=None):
        self.ny, self.nx = shape
        self.bil = []
        for lam, w in ((1.6, 0.14), (2.5, 0.22), (4, 0.3), (6.5, 0.35), (10, 0.35), (16, 0.3), (24, 0.25)):
            for _ in range(2):
                phi = rng.uniform(0, np.pi); theta = rng.uniform(0, 2 * np.pi)
                self.bil.append((lam, w * genlik / 2 ** 0.5, np.cos(phi), np.sin(phi), np.cos(theta), np.sin(theta), rng.uniform(0, 2 * np.pi)))
        # 27 Eylül, sahibi: plato nehri "çok düz". Hücre ~10 km; en uzun 24
        # hücrelik bileşen 300 km'lik düz ovada kaybolur. Düz arazide (plato
        # tabanı, kıyı ovası) 300-900 km dalga boyunda 2-4.5 hücrelik büyük
        # salınım eklenir. Her bileşenin eğimi ≤ 0.35: alan kendini
        # katlamaz, kollar birbirini kesmez. Göl ve kıyıdan 10 hücre içinde
        # sönümlenir: göl kıyısı ve ağız kaymaz, nehir göle/denize bağlı kalır.
        self.buyuk = []
        for lam, w in ((20, 1.1), (34, 1.9), (55, 3.1), (90, 5.0)):
            for _ in range(2):
                phi = rng.uniform(0, np.pi); theta = rng.uniform(0, 2 * np.pi)
                self.buyuk.append((lam, w / 2 ** 0.5, np.cos(phi), np.sin(phi), np.cos(theta), np.sin(theta), rng.uniform(0, 2 * np.pi)))
        self.carpan = self.duz = None
        if Z is not None:
            z = Z.reshape(shape)
            gy, gx = np.gradient(np.maximum(z, 0))
            e = ndimage.gaussian_filter(np.hypot(gx, gy), 2)
            self.carpan = np.clip(1.0 - 0.5 * np.clip((e - 8) / 25, 0, 1), 0.5, 1.0)
            e6 = ndimage.gaussian_filter(np.hypot(gx, gy), 6)
            duz = np.clip((25 - e6) / 15, 0, 1)
            if su is not None:
                uz = ndimage.distance_transform_edt(~su.reshape(shape))
                duz = duz * np.clip((uz - 1) / 6, 0, 1)
            self.duz = ndimage.gaussian_filter(duz, 4)

    @staticmethod
    def _topla(bil, x, y):
        dx = np.zeros(len(x)); dy = np.zeros(len(x))
        for lam, w, c, s_, dxv, dyv, ps in bil:
            v = w * np.sin(2 * np.pi * (x * c + y * s_) / lam + ps)
            dx += v * dxv; dy += v * dyv
        return dx, dy

    def __call__(self, p):
        x, y = p[:, 0], p[:, 1]
        dx, dy = self._topla(self.bil, x, y)
        if self.carpan is not None:
            i = np.clip(np.round(y).astype(int), 0, self.ny - 1); j = np.clip(np.round(x).astype(int), 0, self.nx - 1)
            k = self.carpan[i, j]; dx *= k; dy *= k
            bx, by = self._topla(self.buyuk, x, y)
            k = ndimage.map_coordinates(self.duz, [y, x], order=1, mode="nearest")
            dx += bx * k; dy += by * k
        return np.column_stack([x + dx, y + dy])


def sik_ornekle(p, adim=0.25):
    """Köşeleri yuvarla (Chaikin, 2 tur, uçlar sabit) ve eşit aralıkla örnekle."""
    for _ in range(2):
        if len(p) < 3:
            break
        q1 = 0.75 * p[:-1] + 0.25 * p[1:]; q2 = 0.25 * p[:-1] + 0.75 * p[1:]
        p = np.vstack([p[:1], np.column_stack([q1, q2]).reshape(-1, 2)[1:-1], p[-1:]])
    d = np.hypot(*np.diff(p, axis=0).T); s = np.concatenate([[0], np.cumsum(d)]); L = s[-1]
    if L < 1e-6:
        return p
    t = np.linspace(0, L, max(int(L / adim), 1) + 1)
    return np.column_stack([np.interp(t, s, p[:, 0]), np.interp(t, s, p[:, 1])])


def nehirler(alici, q, boy, gm, deniz, lat, lon, Z=None):
    ny, nx = q.shape
    qf, bf = q.ravel(), boy.ravel()
    kara_lab, _ = ndimage.label(~deniz, np.ones((3, 3)))
    ana_kita = np.bincount(kara_lab.ravel())[1:].argmax() + 1
    ada = ((kara_lab != ana_kita) & ~deniz).ravel()
    nm = (qf >= np.where(ada, ADA_Q, NEHIR_Q)) & ~gm.ravel() & ~deniz.ravel()
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
        if ada[c]:
            if L < (ADA_BOY if katilim is None else ADA_KOL_BOY):
                continue                            # adada kısa kıyı deresi / kısa yan kol
            k = max(ust_k if katilim is not None else 1, kademe_ada(qf[c], L))
        else:
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
    alan = KaydirmaAlani(Z, (ny, nx), np.random.default_rng(1493), su=(gm | deniz))
    global KAYDIR
    KAYDIR = alan              # delta.py delta kollarını aynı alanla kaydırır
    cikis = []
    for kol in kollar:
        h = np.array(kol["hucre"])
        p = np.column_stack([h % nx, h // nx]).astype(float)       # (sütun, satır)
        qq = qf[h]
        # sabit noktalardan böl, parça parça sadeleştir ve kıvır
        kes = [0] + [i for i in range(1, len(h) - 1) if int(h[i]) in sabit] + [len(h) - 1]
        pts, qs = [p[0]], [qq[0]]
        for a, b in zip(kes[:-1], kes[1:]):
            parca = rdp(alan(sik_ornekle(rdp(p[a:b + 1], 0.3), 0.4)), 0.1)
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
    zp = os.path.join(BURASI, "_akim.npz")
    Z = np.load(zp)["z"].astype(float).ravel() if os.path.exists(zp) else None
    n = nehirler(alici, q, boy, gm, deniz, lat, lon, Z)
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
