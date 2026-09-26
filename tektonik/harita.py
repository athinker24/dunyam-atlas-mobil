# -*- coding: utf-8 -*-
"""Levha haritasi: TEKTONIK.md'deki kararlari arazi uzerine cizer.

Cizgilerin cogu araziden olculur (dag etekleri, kiyilar); levha adlari ve
bazi alanlar elle yerlestirildi (26 Eylul dag olcumu gorselinin koordinat
sisteminde, 'goruntu' noktalari). Veri yazmaz, yalniz PNG.

    python tektonik/harita.py [cikti.png]
"""
import os, sys
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
import uret  # noqa: E402

CIKTI = sys.argv[1] if len(sys.argv) > 1 else os.path.join(KOK, "tektonik", "levha_haritasi.png")
w = uret.dunya_yukle(); g = uret.grid_kur(w, 0.1)
land = g.land; lat = np.asarray(g.lat); lon = np.asarray(g.lon); H, W = land.shape
e = np.where(land, np.maximum(g.elev, 0), 0).astype(float)
es = ndimage.gaussian_filter(e, 3)
ys, xs = np.where(land); Y0, X0 = ys.min() - 20, xs.min() - 20; Y1, X1 = ys.max() + 20, xs.max() + 20
Z = 2
R = lambda la: float(np.interp(-la, -lat, np.arange(H)))          # enlem -> satir
C = lambda lo: float(np.interp(lo, lon, np.arange(W)))            # boylam -> sutun
P = lambda la, lo: ((C(lo) - X0) * Z, (R(la) - Y0) * Z)           # enlem/boylam -> piksel
G = lambda x, y: (x * 1.036, y * 1.036)                           # olcum gorseli -> piksel

# --- zemin
E = e[Y0:Y1, X0:X1]; L = land[Y0:Y1, X0:X1]
sh = ndimage.gaussian_filter(E, 1)
hs = np.clip(0.5 + (ndimage.sobel(sh, 1) - ndimage.sobel(sh, 0)) / 4500, 0, 1)
t = np.clip(E / 6500, 0, 1)
img = np.zeros(L.shape + (3,)); img[...] = [0.06, 0.09, 0.13]
b = np.stack([0.36 + 0.45 * t, 0.35 + 0.40 * t, 0.30 + 0.42 * t], -1) * (0.55 + 0.6 * hs[..., None])
img[L] = np.clip(b[L], 0, 1)
im = Image.fromarray((img * 255).astype(np.uint8)).resize((L.shape[1] * Z, L.shape[0] * Z), Image.BILINEAR).convert("RGBA")
kat = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(kat)
F = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if s > 0 else ""), abs(s))
f_lev, f_k, f_n, f_bas = F(30), F(-19), F(-17), F(34)

def yumusat(pts, k=7):
    if len(pts) < k: return pts
    a = np.array(pts, float); o = a.copy()
    for i in range(len(a)):
        s = slice(max(0, i - k // 2), i + k // 2 + 1); o[i] = a[s].mean(0)
    return [tuple(p) for p in o]

def cizgi(pts, renk, kal=5, kesik=False):
    if kesik:
        for i in range(0, len(pts) - 1, 2): d.line([pts[i], pts[i + 1]], fill=renk, width=kal)
    else: d.line(pts, fill=renk, width=kal, joint="curve")

def disler(pts, renk, hedef, aralik=34, boy=15, kal=5):
    """cizgi + ucgenler; ucgenler UST levhaya (hedef = (enlem, boylam)) bakar."""
    cizgi(pts, renk, kal); a = np.array(pts, float); hd = np.array(P(*hedef))
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(a, axis=0).T))]
    for s in np.arange(aralik / 2, seg[-1], aralik):
        i = min(max(np.searchsorted(seg, s), 1), len(a) - 1)
        p, q = a[i - 1], a[i]; v = q - p; n = np.hypot(*v) or 1; v = v / n
        c = p + v * (s - seg[i - 1]); nrm = np.array([v[1], -v[0]])
        if np.dot(nrm, hd - c) < 0: nrm = -nrm
        d.polygon([tuple(c - v * boy * 0.6), tuple(c + v * boy * 0.6), tuple(c + nrm * boy)], fill=renk)

def tarama(maske_g, renk, aralik=10):
    """grid maskesini capraz cizgiyle tara"""
    m = maske_g[Y0:Y1, X0:X1]
    mm = Image.fromarray((m * 255).astype(np.uint8)).resize(im.size, Image.NEAREST)
    t = Image.new("RGBA", im.size, (0, 0, 0, 0)); td = ImageDraw.Draw(t)
    for k in range(-im.size[1], im.size[0], aralik): td.line([(k, 0), (k + im.size[1], im.size[1])], fill=renk, width=2)
    kat.paste(t, (0, 0), Image.composite(t, Image.new("RGBA", im.size), mm).split()[3])

def yazi(xy, s, font, renk=(255, 255, 255), kenar=(0, 0, 0), merkez=True):
    if merkez:
        bb = d.textbbox((0, 0), s, font=font); xy = (xy[0] - (bb[2] - bb[0]) / 2, xy[1] - (bb[3] - bb[1]) / 2)
    d.text(xy, s, font=font, fill=renk, stroke_width=3, stroke_fill=kenar)

def volkan(xy, renk=(255, 110, 40), boy=11, sonuk=False):
    x, y = xy; c = (150, 150, 150) if sonuk else renk
    d.polygon([(x - boy, y + boy * 0.8), (x + boy, y + boy * 0.8), (x, y - boy)], fill=c, outline=(0, 0, 0))

KIRMIZI, MAVI, MOR, YESIL, GRI = (230, 60, 50), (70, 150, 255), (190, 110, 255), (80, 220, 140), (175, 175, 175)
col = lambda lo: int(round(C(lo))); row = lambda la: int(round(R(la)))

# --- 1. Buyuk carpisma dikisi: Duvar'in guney etegi, boylam 7.6..33
pts = []
for lo in np.arange(7.6, 33.2, 0.4):
    x = col(lo); r = np.where(land[row(45):row(25), x] & (es[row(45):row(25), x] > 2500))[0]
    if not len(r): continue
    y = row(45) + r.max()
    while y < row(20) and land[y, x] and es[y, x] > 1200: y += 1
    pts.append(((x - X0) * Z, (y - Y0) * Z))
disler(yumusat(pts), KIRMIZI, (45, 20))

# --- 5. Iber blogu dikisi: 5'in guney etegi
pts = []
for lo in np.arange(-41, -16, 0.4):
    x = col(lo); r = np.where(land[row(53):row(38), x] & (es[row(53):row(38), x] > 2500))[0]
    if not len(r): continue
    y = row(53) + r.max()
    while y < row(33) and land[y, x] and es[y, x] > 1200: y += 1
    pts.append(((x - X0) * Z, (y - Y0) * Z))
disler(yumusat(pts), KIRMIZI, (50, -25))

# --- 3. Alpler (4): ic (dogu) etek, yarimada batiya carpti
pts = []
for la in np.arange(19.5, 3.0, -0.4):
    y = row(la); c0, c1 = col(-21), col(-6)
    r = np.where(land[y, c0:c1] & (es[y, c0:c1] > 2500))[0]
    if not len(r): continue
    x = c0 + r.max()
    while x < col(0) and land[y, x] and es[y, x] > 1300: x += 1
    pts.append(((x - X0) * Z, (y - Y0) * Z))
disler(yumusat(pts), KIRMIZI, (7, -3))

# --- 4a. Bati okyanusu dalma cukuru (10 kusagi, kuzey kesim etkin)
pts = []
for la in np.arange(28, 5.5, -0.5):
    y = row(la); c0, c1 = col(-50), col(-22)
    r = np.where(land[y, c0:c1])[0]
    if not len(r): continue
    pts.append(((c0 + r.min() - 12 - X0) * Z, (y - Y0) * Z))
disler(yumusat(pts, 9), MAVI, (16, -25))
# --- 4b. 6: kucuk kita carpismasi (surer)
pts = []
for la in np.arange(6.5, -3.0, -0.4):
    y = row(la); c0, c1 = col(-27), col(-12)
    r = np.where(land[y, c0:c1] & (es[y, c0:c1] > 2200))[0]
    if not len(r): continue
    x = c0 + r.min()
    while x > col(-32) and land[y, x] and es[y, x] > 1000: x -= 1
    pts.append(((x - X0) * Z, (y - Y0) * Z))
if len(pts) > 3: disler(yumusat(pts, 5), KIRMIZI, (8, -15))

# --- 6. Takimada (Ege) dalma cukuru: takimadanin guneyinde, ucgenler kuzeye
lab, n = ndimage.label(land, np.ones((3, 3)))
anakara = np.argmax(np.bincount(lab.ravel())[1:]) + 1
ada = land & (lab != anakara) & (lat[:, None] > 17) & (lat[:, None] < 32) & (lon[None, :] > -22) & (lon[None, :] < -3)
ay, ax_ = np.where(ada)
pts = []
for lo in np.arange(-21, -3.5, 0.5):
    x = col(lo); r = np.where(ada[:, x])[0]
    if not len(r): continue
    pts.append(((x - X0) * Z, (r.max() + 16 - Y0) * Z))
disler(yumusat(pts, 9), MAVI, (26, -12))

# --- 2. Alt kita dogu cukuru: dogudaki yarimadanin acigi, ucgenler batiya
pts = []
for la in np.arange(22, -1, -0.5):
    y = row(la); c0, c1 = col(14), col(45)
    r = np.where(land[y, c0:c1])[0]
    if not len(r): continue
    pts.append(((c0 + r.max() + 14 - X0) * Z, (y - Y0) * Z))
disler(yumusat(pts, 9), MAVI, (10, 20))

# --- 2. Kuzey Anadolu benzeri fay: alt kita yaylasinin kuzey kenari
pts = []
for lo in np.arange(1.5, 22, 0.5):
    x = col(lo); r = np.where(land[row(30):row(8), x] & (es[row(30):row(8), x] > 1100))[0]
    if not len(r): continue
    pts.append(((x - X0) * Z, (row(30) + r.min() - Y0) * Z))
pf = yumusat(pts, 9); cizgi(pf, YESIL, 5)
for k in (len(pf) // 3, 2 * len(pf) // 3):
    x, y = pf[k]; d.line([(x - 26, y - 9), (x + 26, y - 9)], fill=YESIL, width=3); d.polygon([(x + 26, y - 15), (x + 36, y - 9), (x + 26, y - 3)], fill=YESIL)
    d.line([(x - 26, y + 9), (x + 26, y + 9)], fill=YESIL, width=3); d.polygon([(x - 26, y + 3), (x - 36, y + 9), (x - 26, y + 15)], fill=YESIL)

# --- 11: eski kaynasma dikisi (etkin degil)
m11 = land & (es > 1400) & (lat[:, None] > 3) & (lat[:, None] < 21) & (lon[None, :] > 6.5) & (lon[None, :] < 13)
yy, xx = np.where(m11)
X = np.c_[xx, yy].astype(float); mu = X.mean(0); ev, vec = np.linalg.eigh(np.cov((X - mu).T)); v = vec[:, 1] * 2 * np.sqrt(ev[1])
cizgi([tuple((mu - v - [X0, Y0]) * Z), tuple((mu + v - [X0, Y0]) * Z)], GRI, 4)
yazi(tuple((mu + v * 0.2 - [X0, Y0]) * Z + [0, -22]), "11 eski kenet", f_n, GRI)

# --- Kuzeydogu kacis blogu (sahip ekledi): bati sinir 9 (bindirme, blok doguya itilir),
# kuzey sinir 2 (sol yanal), guney sinir Duvar'in kuzey etegi (sag yanal). Elle, dag eksenleri boyunca.
def ok_cifti(p, q, sol_yon):
    """yanal fay oklari: cizginin iki yaninda zit yonlu; sol_yon=+1 ise cizginin
    solundaki (kuzey/bati) taraf cizgi yonunde gider"""
    p, q = np.array(p), np.array(q); v = (q - p) / np.hypot(*(q - p)); nrm = np.array([v[1], -v[0]])
    if nrm[1] > 0: nrm = -nrm          # nrm hep kuzeye (ekranda yukari)
    m = (p + q) / 2
    for taraf, yon in ((1, sol_yon), (-1, -sol_yon)):
        c = m + nrm * 11 * taraf; a, b_ = c - v * 26 * yon, c + v * 26 * yon
        d.line([tuple(a), tuple(b_)], fill=MOR, width=3)
        d.polygon([tuple(b_ + nrm * 6), tuple(b_ + v * 10 * yon), tuple(b_ - nrm * 6)], fill=MOR)
bati = [P(55.5, 20.5), P(50, 23), P(45, 25.2), P(40.5, 27)]
kuzey = [P(55.5, 20.5), P(55.6, 26), P(54.4, 32), P(53.2, 38.5)]
guney = [P(40.5, 27), P(39.6, 31), P(39.2, 35), P(38.6, 40.5)]
disler(bati, MOR, (47, 33), kal=6)
cizgi(kuzey, MOR, 6); ok_cifti(kuzey[1], kuzey[2], -1)
cizgi(guney, MOR, 6); ok_cifti(guney[1], guney[2], -1)

# --- gerilme havzalari (yay ardi / geri cekilme)
deniz = ~land
kutu = lambda a, b_, c, e_: (lat[:, None] > a) & (lat[:, None] < b_) & (lon[None, :] > c) & (lon[None, :] < e_)
tarama(deniz & kutu(14, 29, -4.8, -1.0), (70, 150, 255, 200))       # Ege
tarama(deniz & kutu(29.5, 37, -17, 7) & ~kutu(29.5, 37, 5, 7), (70, 150, 255, 120))  # takimada ile Duvar arasi
tarama(deniz & kutu(8, 14.5, -9, 1), (70, 150, 255, 200))            # Tiren benzeri
tarama(deniz & kutu(6.5, 15, 13, 20.5), (70, 150, 255, 200))         # Karadeniz benzeri

# --- volkanlar
for lo in np.arange(-19, -4, 2.5):                                    # Ege yayi (takimada guneyi)
    x = col(lo); r = np.where(ada[:, x])[0]
    if len(r): volkan(((x - X0) * Z, (r.max() - 6 - Y0) * Z))
yy, xx = np.where(ada); k = np.argmax(e[yy, xx])
volkan(((xx[k] - X0) * Z, (yy[k] - Y0) * Z), boy=17); yazi(((xx[k] - X0) * Z, (yy[k] - Y0) * Z + 30), "6.443 m", f_n)
for la in np.arange(2, 13, 3):                                        # dogu yayi (dogudaki yarimada)
    y = row(la); r = np.where(land[y, col(14):col(45)])[0]
    if len(r): volkan(((col(14) + r.max() - 12 - X0) * Z, (y - Y0) * Z))
for la in np.arange(26, 5, -3.5):                                     # 10 kusagi: kuzeyi etkin, guneyi sonmus
    y = row(la); r = np.where(land[y, col(-50):col(-22)])[0]
    if len(r): volkan(((col(-50) + r.min() + 20 - X0) * Z, (y - Y0) * Z), sonuk=la < 12)

# --- adlar
for (la, lo), s_ in [((57.5, 2), "KUZEY LEVHASI"), ((47.5, 34), "KUZEYDOĞU"), ((45.8, 34), "KAÇIŞ BLOĞU"),
                     ((3, 14), "ALT KITA"), ((6.5, -2.5), "YARIMADA"), ((19, -27), "GÜNEYBATI BLOĞU"),
                     ((38.5, -27), "İBER BLOĞU"), ((26.5, -12), "EGE"), ((-3.5, -30), "KÜÇÜK KITA"),
                     ((-5.5, -43), "BATI"), ((-7.3, -43), "OKYANUSU"), ((12, 41), "DOĞU"), ((10.3, 41), "OKYANUSU"),
                     ((33.5, -8), "İÇ DENİZ")]:
    yazi(P(la, lo), s_, f_lev)
for (la, lo), s_ in [((47.5, 12), "sert eski blok (Tarım benzeri)"), ((51, -2), "1: köşe düğümü (Pamir benzeri)"),
                     ((31.2, 21), "Duvar dikişi: büyük çarpışma"), ((41.8, -28), "5: Pireneler benzeri"),
                     ((9, -16.5), "4: Alpler"), ((17.5, -1.5), "Ege"), ((11.5, -4), "Tiren benzeri"),
                     ((11.2, 16.8), "Karadeniz benzeri"), ((23.2, 14.5), "Kuzey Anadolu benzeri fay"),
                     ((1.5, -24), "6: çarpışma sürüyor"), ((25.5, -41), "And tipi dalma"),
                     ((34.8, 4.5), "gerilme havzası"), ((50, 24.8), "9"), ((57, 30), "2"), ((-1, 25), "doğu dalması")]:
    yazi(P(la, lo), s_, f_k)

im = Image.alpha_composite(im, kat)
# --- alt panel: aciklama ve zaman cizelgesi
PH = 330; son = Image.new("RGBA", (im.size[0], im.size[1] + PH), (14, 20, 28, 255)); son.paste(im, (0, 0))
d = ImageDraw.Draw(son); x0p, y0p = 30, im.size[1] + 22
d.text((x0p, y0p), "Dünyam levha haritası", font=f_bas, fill=(255, 255, 255))
L_ = [("dis", KIRMIZI, "çarpışma dikişi (dişler üst levhada)"), ("dis", MAVI, "dalma çukuru (dişler üst levhada)"),
      ("dis", MOR, "kaçış bloğu sınırı: bindirme"), ("ok", MOR, "kaçış bloğu sınırı: yanal fay"),
      ("cz", YESIL, "Kuzey Anadolu benzeri sağ yanal fay"), ("cz", GRI, "eski kenet (etkin değil)"),
      ("tr", MAVI, "gerilme havzası (geri çekilen levha arkası)"), ("vk", None, "etkin volkan / sönmüş volkan")]
for i, (tip, rk, ad) in enumerate(L_):
    yy_ = y0p + 62 + i * 30; a, b_ = (x0p, yy_ + 10), (x0p + 50, yy_ + 10)
    if tip in ("dis", "cz", "ok"): d.line([a, b_], fill=rk, width=5)
    if tip == "dis":
        for xx_ in (x0p + 12, x0p + 36): d.polygon([(xx_ - 7, yy_ + 10), (xx_ + 7, yy_ + 10), (xx_, yy_ - 3)], fill=rk)
    if tip == "ok": d.polygon([(x0p + 50, yy_ + 4), (x0p + 60, yy_ + 10), (x0p + 50, yy_ + 16)], fill=rk)
    if tip == "tr":
        for k_ in range(0, 50, 8): d.line([(x0p + k_, yy_ + 20), (x0p + k_ + 12, yy_)], fill=rk, width=2)
    if tip == "vk":
        d.polygon([(x0p + 4, yy_ + 18), (x0p + 22, yy_ + 18), (x0p + 13, yy_)], fill=(255, 110, 40), outline=(0, 0, 0))
        d.polygon([(x0p + 32, yy_ + 18), (x0p + 50, yy_ + 18), (x0p + 41, yy_)], fill=(150, 150, 150), outline=(0, 0, 0))
    d.text((x0p + 72, yy_ - 2), ad, font=f_k, fill=(230, 230, 230))
Z_ = ["ZAMAN ÇİZELGESİ (eskiden yeniye, göreli)",
      "1. Çok eski: İber bloğunun dağları aşındı (Meseta). Alt kıtanın iki parçası kaynaştı, 11 yükseldi.",
      "2. Eski: alt kıtanın doğusunda dalma; 7 yükseldi, sonra Karadeniz benzeri havza açılıp",
      "    doğudaki yarımadayı (volkan yayı) kopardı. Batıda And tipi dalma, 10 kuşağı başladı.",
      "3. Büyük yakınlaşma (Tetis kapanışı): alt kıta Duvar'a çarptı (1, 3, 9, 2, plato); İber bloğu",
      "    çarptı (5); yarımada batıya savrulup 4'ü yükseltti; küçük kıta batıdan geldi, plato 10 kabardı.",
      "4. Kaçış: kuzeydoğu bloğu çarpışmanın basıncıyla doğuya, açık okyanusa itildi.",
      "5. Bugün: iç deniz levhası geri çekiliyor (takımada, Ege, Tiren gerilir); 6'da çarpışma sürüyor;",
      "    Kuzey Anadolu benzeri fay, doğu ve batı dalmaları etkin, depremler ve volkanlar oralarda."]
for i, s_ in enumerate(Z_):
    d.text((760, y0p + 4 + i * 33), s_, font=(F(22) if i == 0 else f_k), fill=(255, 255, 255) if i == 0 else (225, 225, 225))
son.convert("RGB").save(CIKTI); print("yazildi", CIKTI, son.size)
