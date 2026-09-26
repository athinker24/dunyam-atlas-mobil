# -*- coding: utf-8 -*-
"""Levha haritalari: tum gezegen (levha_dunya.png) ve kita (levha_haritasi.png).

Model tektonik/levhalar.py'den gelir (kapali levhalar, Euler vektorleri,
Bird 2003 olcutuyle siniflanmis sinir adimlari). Bu betik yalniz cizer.
    python tektonik/harita.py
"""
import os, sys
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import levhalar as M  # noqa: E402

KOK = M.KOK; land, lat, lon, e, es, H, W = M.land, M.lat, M.lon, M.e, M.es, M.H, M.W
F = lambda s, b=False: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if b else ""), s)
RENK = {"OSR": (255, 120, 60), "CRB": (255, 150, 70), "OTF": (90, 230, 140), "CTF": (90, 230, 140),
        "SUB": (80, 160, 255), "OCB": (80, 160, 255), "CCB": (240, 60, 60), "PAS": (160, 160, 160)}
AD = {"OSR": "okyanus sırtı (ayrılma)", "CRB": "kıta yarığı (ayrılma)", "OTF": "okyanus dönüşüm fayı (yanal)",
      "CTF": "kıta dönüşüm fayı (yanal)", "SUB": "dalma çukuru (dişler üst levhada)", "OCB": "okyanusal yakınlaşma",
      "CCB": "kıta çarpışması (dişler üst levhada)", "PAS": "hareketsiz"}

_DERIN = None
def derinlik():
    """okyanus tabani derinligi (km), TASARIM: sirttan uzaklik / yari yayilma hizi = yas,
    d = 2.6 + 0.35 sqrt(yas) (Parsons-Sclater benzeri); cukurlarda derinlesme, kiyida sahanlik."""
    global _DERIN
    if _DERIN is not None: return _DERIN
    sirt = np.zeros((H, W), bool); hz = np.zeros((H, W)); cuk = np.zeros((H, W), bool)
    for a in M.ADIMLAR:
        for la, lo in M.sik([a["p"], a["q"]], 0.05):
            r = min(max(M.row(la), 0), H - 1); c = M.col(((lo + 180) % 360) - 180) % W
            if a["sinif"] == "OSR": sirt[r, c] = True; hz[r, c] = max(abs(a["yaklasma"]), 0.5)
            if a["sinif"] in ("SUB", "OCB"): cuk[r, c] = True
    dist, (ir, ic) = ndimage.distance_transform_edt(~sirt, sampling=(1.0, 0.75), return_indices=True)
    yas = dist * 11.1 / (hz[ir, ic] * 10 / 2)
    d = np.minimum(2.6 + 0.35 * np.sqrt(yas), 6.2)
    dc = ndimage.distance_transform_edt(~cuk, sampling=(1.0, 0.75)) * 11.1
    d = d + 2.6 * np.exp(-dc / 45.0)
    dk = ndimage.distance_transform_edt(~land, sampling=(1.0, 0.75)) * 11.1
    d = np.where(dk < 140, 0.15 + (d - 0.15) * np.clip((dk - 20) / 120, 0, 1) ** 1.5, d)
    _DERIN = np.where(land, 0, d); return _DERIN

def zemin(la0, la1, lo0, lo1, olcek):
    """kabartma golgeli zemin, (enlem, boylam) kutusu, olcek = piksel/derece"""
    r0, r1 = M.row(la1), M.row(la0); c0, c1 = M.col(lo0), M.col(lo1)
    E = e[r0:r1, c0:c1]; L = land[r0:r1, c0:c1]
    sh = ndimage.gaussian_filter(E, 1)
    hs = np.clip(0.5 + (ndimage.sobel(sh, 1) - ndimage.sobel(sh, 0)) / 4500, 0, 1); t = np.clip(E / 6500, 0, 1)
    D = derinlik()[r0:r1, c0:c1]; u = np.clip((D - 0.15) / 7.5, 0, 1)[..., None]
    sig, der = np.array([0.20, 0.42, 0.52]), np.array([0.03, 0.07, 0.16])
    img = sig * (1 - u) ** 1.6 + der * (1 - (1 - u) ** 1.6)
    img = img * (0.9 + 0.1 * np.clip(0.5 + (ndimage.sobel(D, 1) - ndimage.sobel(D, 0)) * 2, 0, 1)[..., None])
    b = np.stack([0.36 + 0.45 * t, 0.35 + 0.40 * t, 0.30 + 0.42 * t], -1) * (0.55 + 0.6 * hs[..., None])
    img[L] = np.clip(b[L], 0, 1)
    k = M.kimlik[r0:r1, c0:c1]
    return img, k, (r0, c0)

class Harita:
    def __init__(self, la0, la1, lo0, lo1, olcek, dolgu=0.22):
        self.la1, self.lo0, self.s = la1, lo0, olcek
        img, k, _ = zemin(la0, la1, lo0, lo1, olcek)
        boy = (int((lo1 - lo0) * olcek), int((la1 - la0) * olcek))
        taban = Image.fromarray((img * 255).astype(np.uint8)).resize(boy, Image.BILINEAR)
        renk = np.zeros((len(M.ADLAR) + 1, 3), np.uint8)
        for i, ad in enumerate(M.ADLAR, 1): renk[i] = M.LEVHALAR[ad]["renk"]
        kat = Image.fromarray(renk[k]).resize(boy, Image.NEAREST)
        self.im = Image.blend(taban, kat, dolgu).convert("RGBA")
        # levha kenarlarini ince koyu cizgiyle belirt
        kk = np.array(Image.fromarray(k).resize(boy, Image.NEAREST))
        kenar = (np.diff(kk, axis=0, prepend=kk[:1]) != 0) | (np.diff(kk, axis=1, prepend=kk[:, :1]) != 0)
        a = np.array(self.im); a[kenar] = (a[kenar] * 0.5).astype(np.uint8); self.im = Image.fromarray(a)
        self.kat = Image.new("RGBA", self.im.size, (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.kat)
    def P(self, la, lo): return ((lo - self.lo0) * self.s, (self.la1 - la) * self.s)
    def adimlar(self, kal=4, dis=13, dis_her=3):
        say = {}
        for a in M.ADIMLAR:
            p, q = np.array(self.P(*a["p"])), np.array(self.P(*a["q"])); c = RENK[a["sinif"]]
            if abs(p[0] - q[0]) > self.im.size[0] / 2: continue      # tarih cizgisini asan parca
            if a["sinif"] == "PAS": self.d.line([tuple(p), tuple(q)], fill=c + (160,), width=max(1, kal // 2)); continue
            if a["sinif"] in ("OSR",):
                t = q - p; n = np.array([t[1], -t[0]]) / (np.hypot(*t) or 1) * (kal * 0.6)
                self.d.line([tuple(p + n), tuple(q + n)], fill=c, width=max(2, kal // 2))
                self.d.line([tuple(p - n), tuple(q - n)], fill=c, width=max(2, kal // 2))
            elif a["sinif"] == "CRB":
                self.d.line([tuple(p), tuple(p + (q - p) * 0.6)], fill=c, width=kal)
            else:
                self.d.line([tuple(p), tuple(q)], fill=c, width=kal)
            if a["ust"]:
                k = say.get(a["sinir"], 0); say[a["sinir"]] = k + 1
                if k % dis_her: continue
                t = q - p; L = np.hypot(*t) or 1; t = t / L; sol = np.array([t[1], -t[0]])
                n = sol if a["ust"] == a["sol"] else -sol; m = (p + q) / 2
                self.d.polygon([tuple(m - t * dis * 0.6), tuple(m + t * dis * 0.6), tuple(m + n * dis)], fill=c)
    def hizlar(self, adim, olc, noktalar=None):
        pts = noktalar or [(la, lo) for la in np.arange(-60, 80, adim) for lo in np.arange(-180 + adim / 2, 180, adim)]
        for la, lo in pts:
            x, y = self.P(la, lo)
            if not (0 <= x < self.im.size[0] and 0 <= y < self.im.size[1]): continue
            ad = M.levha_at(la, lo); v = M.hiz(ad, la, lo); L = np.hypot(*v)
            if L < 0.3: self.d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 255, 255, 180)); continue
            b = np.array([x + v[0] * olc, y - v[1] * olc]); a = np.array([x, y]); t = (b - a) / np.hypot(*(b - a))
            self.d.line([tuple(a), tuple(b)], fill=(255, 255, 255, 220), width=3)
            n = np.array([t[1], -t[0]])
            self.d.polygon([tuple(b + t * 9), tuple(b + n * 6), tuple(b - n * 6)], fill=(255, 255, 255, 220))
    def yazi(self, xy, s, font, renk=(255, 255, 255)):
        bb = self.d.textbbox((0, 0), s, font=font); xy = (xy[0] - (bb[2] - bb[0]) / 2, xy[1] - (bb[3] - bb[1]) / 2)
        self.d.text(xy, s, font=font, fill=renk, stroke_width=3, stroke_fill=(0, 0, 0))
    def bitir(self): return Image.alpha_composite(self.im, self.kat)

def aciklama(im, baslik, satirlar, zaman=None, genislik=None):
    PH = 60 + 36 * max(len(satirlar), len(zaman or [])) + 20
    son = Image.new("RGBA", (im.size[0], im.size[1] + PH), (14, 20, 28, 255)); son.paste(im, (0, 0))
    d = ImageDraw.Draw(son); x0, y0 = 30, im.size[1] + 18
    d.text((x0, y0), baslik, font=F(32, True), fill=(255, 255, 255))
    for i, (sn, ad) in enumerate(satirlar):
        yy = y0 + 58 + i * 34; c = RENK.get(sn, (255, 255, 255))
        if sn == "OSR":
            d.line([(x0, yy + 6), (x0 + 50, yy + 6)], fill=c, width=3); d.line([(x0, yy + 14), (x0 + 50, yy + 14)], fill=c, width=3)
        elif sn == "CRB":
            for k in range(0, 50, 16): d.line([(x0 + k, yy + 10), (x0 + k + 9, yy + 10)], fill=c, width=5)
        elif sn in RENK:
            d.line([(x0, yy + 10), (x0 + 50, yy + 10)], fill=c, width=5)
            if sn in ("SUB", "CCB"):
                for xx in (x0 + 12, x0 + 36): d.polygon([(xx - 7, yy + 10), (xx + 7, yy + 10), (xx, yy - 3)], fill=c)
        elif sn == "HIZ":
            d.line([(x0, yy + 10), (x0 + 40, yy + 10)], fill=(255, 255, 255), width=3); d.polygon([(x0 + 40, yy + 4), (x0 + 50, yy + 10), (x0 + 40, yy + 16)], fill=(255, 255, 255))
        elif sn == "VK":
            d.polygon([(x0 + 4, yy + 18), (x0 + 22, yy + 18), (x0 + 13, yy)], fill=(255, 110, 40), outline=(0, 0, 0))
            d.polygon([(x0 + 32, yy + 18), (x0 + 50, yy + 18), (x0 + 41, yy)], fill=(150, 150, 150), outline=(0, 0, 0))
        elif sn == "NAF": d.line([(x0, yy + 10), (x0 + 50, yy + 10)], fill=(90, 230, 140), width=5)
        elif sn == "ESKI": d.line([(x0, yy + 10), (x0 + 50, yy + 10)], fill=(175, 175, 175), width=4)
        elif sn == "TR":
            for k in range(0, 50, 8): d.line([(x0 + k, yy + 20), (x0 + k + 12, yy)], fill=(80, 160, 255), width=2)
        d.text((x0 + 70, yy - 2), ad, font=F(20), fill=(230, 230, 230))
    if zaman:
        for i, s in enumerate(zaman):
            d.text((genislik or 760, y0 + 4 + i * 34), s, font=F(22, True) if i == 0 else F(20), fill=(255, 255, 255) if i == 0 else (225, 225, 225))
    return son

# ============================================================== 1. tum gezegen
def dunya(cikti):
    h = Harita(-90, 90, -180, 180, 8, dolgu=0.18)
    for lo in range(-150, 181, 30):
        x, _ = h.P(0, lo); h.d.line([(x, 0), (x, h.im.size[1])], fill=(255, 255, 255, 30), width=1)
    for la in range(-60, 61, 30):
        _, y = h.P(la, 0); h.d.line([(0, y), (h.im.size[0], y)], fill=(255, 255, 255, 30), width=1)
    h.adimlar(kal=4, dis=13, dis_her=3)
    h.hizlar(20, 9)
    for ad, (la, lo) in {"Kuzey": (60, -20), "Kuzeydoğu": (47, 33), "İber": (37, -30), "Ege": (26, -12),
                         "Güneybatı": (-15, -25), "Yarımada": (6, -3), "Alt Kıta": (-15, 14), "Batı Okyanusu": (0, -62),
                         "Doğu Okyanusu": (-10, 60), "Büyük Okyanus": (5, 132), "Uzak Okyanus": (5, -140),
                         "Kuzey Kutup": (82, 0), "Güney Kutup": (-68, 0)}.items():
        h.yazi(h.P(la, lo), ad.upper(), F(26 if M.LEVHALAR[ad]["sira"] > 3 or "Okyanus" in ad else 24, True))
    im = h.bitir()
    satir = [("OSR", AD["OSR"]), ("OTF", AD["OTF"].replace("okyanus ", "")), ("SUB", AD["SUB"]),
             ("CCB", AD["CCB"]), ("CRB", AD["CRB"]), ("HIZ", "levha hızı, Kuzey levhasına göre (1 cm/yıl ≈ 9 px)")]
    o = M.yaz()
    uz = o["sinif_uzunluk_km"]
    zaman = ["SAYILAR (Bird 2003 sınıfları, ~42 km'lik adımlar)",
             "%d levha, %d sınır adımı, toplam %.0f bin km sınır" % (len(M.ADLAR), o["adim_sayisi"], sum(uz.values()) / 1e3)]
    for s_ in ("OSR", "OTF", "SUB", "CCB", "CTF", "CRB"):
        if s_ in uz: zaman.append("%s  %-28s %6.0f bin km" % (s_, M.SINIF_AD[s_], uz[s_] / 1e3))
    zaman.append("Okyanustaki sınırlar tasarım; karadakiler araziden ölçüldü.")
    aciklama(im, "Dünyam levhaları — tüm gezegen", satir, zaman, genislik=1400).convert("RGB").save(cikti)
    kureler(im, cikti.replace("levha_dunya", "levha_kure"))

# ============================================================== 2. kita
def kita(cikti):
    h = Harita(-9, 62, -50, 46, 21.5, dolgu=0.16)
    h.adimlar(kal=5, dis=15, dis_her=2)
    d = h.d
    # Ege, Tiren, Karadeniz benzeri ve takimada-Duvar arasi gerilme havzalari (tarama)
    deniz = ~land
    kutu = lambda a, b, c, e_: (lat[:, None] > a) & (lat[:, None] < b) & (lon[None, :] > c) & (lon[None, :] < e_)
    for m, alfa in ((deniz & kutu(14, 29, -4.8, -1.0), 200), (deniz & kutu(29.5, 37, -17, 5), 110),
                    (deniz & kutu(8, 14.5, -9, 1), 200), (deniz & kutu(6.5, 15, 13, 20.5), 200)):
        r0, r1, c0, c1 = M.row(62), M.row(-9), M.col(-50), M.col(46)
        mm = Image.fromarray((m[r0:r1, c0:c1] * 255).astype(np.uint8)).resize(h.im.size, Image.NEAREST)
        t = Image.new("RGBA", h.im.size, (0, 0, 0, 0)); td = ImageDraw.Draw(t)
        for k in range(-h.im.size[1], h.im.size[0], 11): td.line([(k, 0), (k + h.im.size[1], h.im.size[1])], fill=(80, 160, 255, alfa), width=2)
        h.kat.paste(t, (0, 0), mm)
    # Kuzey Anadolu benzeri fay (levha ici)
    pts = []
    for lo in np.arange(1.5, 22, 0.5):
        x = M.col(lo); r = np.where(land[M.row(30):M.row(8), x] & (es[M.row(30):M.row(8), x] > 1100))[0]
        if len(r): pts.append(h.P(M.LA(M.row(30) + r.min()), lo))
    pf = M.yumusat([(y, x) for x, y in pts], 9); pf = [(x, y) for y, x in pf]
    d.line(pf, fill=(90, 230, 140), width=6)
    for k in (len(pf) // 3, 2 * len(pf) // 3):
        x, y = pf[k]
        d.line([(x - 28, y - 10), (x + 28, y - 10)], fill=(90, 230, 140), width=3); d.polygon([(x + 28, y - 16), (x + 38, y - 10), (x + 28, y - 4)], fill=(90, 230, 140))
        d.line([(x - 28, y + 10), (x + 28, y + 10)], fill=(90, 230, 140), width=3); d.polygon([(x - 28, y + 4), (x - 38, y + 10), (x - 28, y + 16)], fill=(90, 230, 140))
    # 11: eski kenet
    m11 = land & (es > 1400) & (lat[:, None] > 3) & (lat[:, None] < 21) & (lon[None, :] > 6.5) & (lon[None, :] < 13)
    yy, xx = np.where(m11); X = np.c_[lon[xx], lat[yy]]; mu = X.mean(0); ev, vec = np.linalg.eigh(np.cov((X - mu).T)); v = vec[:, 1] * 2 * np.sqrt(ev[1])
    a, b = h.P(mu[1] - v[1], mu[0] - v[0]), h.P(mu[1] + v[1], mu[0] + v[0]); d.line([a, b], fill=(175, 175, 175), width=5)
    # volkanlar
    def volkan(la, lo, sonuk=False, boy=12):
        x, y = h.P(la, lo); c = (150, 150, 150) if sonuk else (255, 110, 40)
        d.polygon([(x - boy, y + boy * 0.8), (x + boy, y + boy * 0.8), (x, y - boy)], fill=c, outline=(0, 0, 0))
    lab, n = ndimage.label(land, np.ones((3, 3))); ana = np.argmax(np.bincount(lab.ravel())[1:]) + 1
    ada = land & (lab != ana) & (lat[:, None] > 17) & (lat[:, None] < 32) & (lon[None, :] > -22) & (lon[None, :] < -3)
    for lo in np.arange(-19, -4, 2.5):
        r = np.where(ada[:, M.col(lo)])[0]
        if len(r): volkan(M.LA(r.max() - 6), lo)
    yy, xx = np.where(ada); k = np.argmax(e[yy, xx]); volkan(lat[yy[k]], lon[xx[k]], boy=18)
    h.yazi(np.array(h.P(lat[yy[k]], lon[xx[k]])) + [0, 32], "6.443 m", F(17))
    for la in np.arange(2, 13, 3):
        r = np.where(land[M.row(la), M.col(14):M.col(45)])[0]
        if len(r): volkan(la, lon[M.col(14) + r.max() - 12])
    for la in np.arange(26, 5, -3.5):
        r = np.where(land[M.row(la), M.col(-50):M.col(-22)])[0]
        if len(r): volkan(la, lon[M.col(-50) + r.min() + 20], sonuk=la < 12)
    # hiz oklari (levha tohumlarinda)
    h.hizlar(0, 14, noktalar=[(47, 30), (38, -26), (24, -14), (15, -28), (6, -6), (10, 12), (18, -40), (-5, -36), (8, 36), (52, -8)])
    for ad, (la, lo) in {"KUZEY LEVHASI": (57.5, 2), "KUZEYDOĞU": (48.5, 36), "KAÇIŞ BLOĞU": (46.7, 36),
                         "İBER": (38.5, -34), "EGE": (27, -12), "GÜNEYBATI": (19.5, -30), "YARIMADA": (3.6, -2.5),
                         "ALT KITA": (3, 15), "BATI OKYANUSU": (-6, -44), "DOĞU OKYANUSU": (14, 40.5), "KÜÇÜK KITA": (-4.5, -30)}.items():
        h.yazi(h.P(la, lo), ad, F(28, True))
    for (la, lo), s_ in [((47.5, 12), "sert eski blok (Tarım benzeri)"), ((51, -2), "1: köşe düğümü (Pamir benzeri)"),
                         ((31.2, 21), "Duvar: büyük çarpışma"), ((41.8, -28), "5: Pireneler benzeri"),
                         ((9, -16.5), "4: Alpler"), ((17.5, -2.5), "Ege"), ((11.5, -4), "Tiren benzeri"),
                         ((11.2, 16.8), "Karadeniz benzeri"), ((23.3, 14.5), "Kuzey Anadolu benzeri fay"),
                         ((1.5, -25), "6: çarpışma sürüyor"), ((25.5, -41), "And tipi dalma"), ((34.8, 5), "yay ardı gerilmesi"),
                         ((50.5, 25.5), "9: Baykal tipi yarık"), ((57, 30), "2"), ((-1, 26), "doğu dalması"), ((13.5, 9.5), "11 eski kenet")]:
        h.yazi(h.P(la, lo), s_, F(19))
    im = h.bitir()
    satir = [("CCB", AD["CCB"]), ("SUB", AD["SUB"]), ("OSR", AD["OSR"]), ("CRB", AD["CRB"]), ("CTF", "dönüşüm fayı (yanal)"),
             ("NAF", "Kuzey Anadolu benzeri sağ yanal fay (levha içi)"), ("ESKI", "eski kenet (etkin değil)"),
             ("TR", "gerilme havzası (geri çekilen levha arkası)"), ("VK", "etkin / sönmüş volkan"), ("HIZ", "levha hızı (Kuzey'e göre)")]
    zaman = ["ZAMAN ÇİZELGESİ (eskiden yeniye, göreli)",
             "1. Çok eski: İber bloğunun dağları aşındı (Meseta). Alt kıtanın iki parçası kaynaştı, 11 yükseldi.",
             "2. Eski: alt kıtanın doğusunda dalma; 7 yükseldi, sonra Karadeniz benzeri havza açılıp",
             "    doğudaki yarımadayı (volkan yayı) kopardı. Batıda And tipi dalma, 10 kuşağı başladı.",
             "3. Büyük yakınlaşma (Tetis kapanışı): alt kıta Duvar'a çarptı (1, 3, 2, plato); İber bloğu çarptı (5);",
             "    yarımada batıya savrulup 4'ü yükseltti; küçük kıta batıdan geldi, plato 10 kabardı.",
             "4. Kaçış: kuzeydoğu bloğu doğuya itildi; arkasında (9) Baykal tipi yarık açıldı.",
             "5. Bugün: iç deniz levhası geri çekiliyor (takımada, Ege, Tiren gerilir); 6'da çarpışma sürüyor;",
             "    Kuzey Anadolu benzeri fay, doğu ve batı dalmaları etkin; depremler ve volkanlar oralarda."]
    aciklama(im, "Dünyam levhaları — kıta", satir, zaman, genislik=720).convert("RGB").save(cikti)

def kureler(duz, cikti, merkezler=((20, 0), (-20, 180)), cap=1100):
    """esdikdortgen goruntuden ortografik kureler (duz: tum gezegen, 8 px/derece, legend'siz)"""
    A = np.array(duz.convert("RGB")); Hh, Ww = A.shape[:2]; s_ = Ww / 360
    tuval = Image.new("RGB", (cap * len(merkezler) + 60 * (len(merkezler) + 1), cap + 140), (14, 20, 28))
    y, x = np.mgrid[0:cap, 0:cap]; X = (x - cap / 2) / (cap / 2); Y = (cap / 2 - y) / (cap / 2); r2 = X ** 2 + Y ** 2; ic = r2 <= 1
    Zc = np.sqrt(np.clip(1 - r2, 0, 1))
    for k, (f0, l0) in enumerate(merkezler):
        f0r, l0r = np.radians(f0), np.radians(l0)
        la = np.degrees(np.arcsin(np.clip(Zc * np.sin(f0r) + Y * np.cos(f0r), -1, 1)))
        lo = l0 + np.degrees(np.arctan2(X, Zc * np.cos(f0r) - Y * np.sin(f0r)))
        lo = (lo + 180) % 360 - 180
        px = np.clip(((lo + 180) * s_).astype(int), 0, Ww - 1); py = np.clip(((90 - la) * s_).astype(int), 0, Hh - 1)
        img = A[py, px].astype(float) * (0.55 + 0.45 * Zc[..., None]); img[~ic] = (14, 20, 28)
        tuval.paste(Image.fromarray(img.astype(np.uint8)), (60 + k * (cap + 60), 70))
    d = ImageDraw.Draw(tuval)
    d.text((60, 18), "Dünyam levhaları — kıtaya bakan yüz ve arka yüz", font=F(34, True), fill=(255, 255, 255))
    tuval.save(cikti)

if __name__ == "__main__":
    d = os.path.join(KOK, "tektonik")
    dunya(os.path.join(d, "levha_dunya.png")); kita(os.path.join(d, "levha_haritasi.png")); print("yazildi")
