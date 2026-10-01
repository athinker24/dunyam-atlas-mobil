"""Yaşanabilirlik: yerleşik yaşam (bitki, hayvan ve insan) için çok etkenli endeks, 0-100.

    python yasam/yasam.py            # ~1 dk; data/yasam*.png, yasam.json yazar

İlk sürüm yalnız net birincil üretime (Miami/Lieth NPP) bakıyordu; bu dünyada
sıcak ve nemli olduğu için neredeyse her yer tavana yapışıyordu (sahibi 1 Ekim:
"bütün dünya mükemmel ötesi yaşanabilir"). Şimdi dokuz etken, her biri 0-1:

  0 sıcaklık      yıllık ortalama (insan nüfusu ~13 °C çevresinde yoğunlaşır,
                  Xu vd. 2020, PNAS), en soğuk ay ve en sıcak ay uçları
  1 su            AET/PE (nem oranı), nehir ve göl erişimi, aşırı yağış
  2 gıda          Miami NPP ve büyüme sezonu (GDD5), toprak verimliliğiyle çarpılır
  3 mevsimsellik  yıllık sıcaklık aralığı, kurak ay sayısı, yağışın en yağışlı 3 aya yığılması
  4 arazi         eğim (yumuşatılmış) ve yükseklik (kalıcı yerleşim ~5100 m'de biter)
  5 toprak        WRB türünün verimlilik sırası (toprak/toprak.py); ağırlığı 0, gıdanın içinde
  6 deniz         kıyıya uzaklık (balık, ticaret, ılımanlık)
  7 tehlike       çarpışma/dönüşüm levha sınırı (deprem) ve volkan kuşağı
  8 alan          çevredeki ~50 km'de elverişli kara payı: dar bir şerit mi, geniş bir ova mı

Birleşim: ağırlıklı geometrik ortalama (bir etken 0 ise sonuç 0: en zayıf halka
belirleyicidir, ortalama gibi telafi edilemez), alan etkeni çarpan olarak.
Sınıflar mutlak eşiklerle (0-100). Eşikler seçimdir; Dünya örnekleriyle sağlaması
YASAM.md'de. Ağırlıklar (aşağıda) kararıdır, ölçülmüş değil.
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
BURASI = os.path.dirname(os.path.abspath(__file__)); KOK = os.path.dirname(BURASI)
sys.path.insert(0, os.path.join(KOK, "su")); sys.path.insert(0, KOK); sys.path.insert(0, os.path.join(KOK, "toprak"))
import akim
import toprak as tp

# kod: (ad, açıklama, Dünya'da örnek, renk, alt sınır puan)
SINIF = {
    1: ("Yaşanmaz", "Bir ya da birkaç etken tek başına yaşamı engelliyor: ölümcül soğuk ya da sıcak, susuzluk, yüksek dağ.",
        "Sahra'nın içi, Tibet'in yüksek platosu, Antarktika", (96, 62, 62), 0),
    2: ("Çok zor", "Çok seyrek yaşam; geçim zor, insan yerleşimi küçük ve dağınık.",
        "Sahel'in kuzeyi, Yakutya, Patagonya", (176, 92, 64), 25),
    3: ("Zor", "Yaşanır ama bir ya da iki ağır kısıt var: soğuk kış, kuraklık, dik arazi ya da kıtanın içi.",
        "Orta Asya bozkırı, İç Moğolistan, Anadolu platosu", (214, 160, 78), 45),
    4: ("Orta", "Kabul edilebilir koşullar, belirgin zayıf yönlerle; tarım mümkün ama güvenli değil.",
        "Doğu Avrupa, Orta Anadolu, Kuzey Hindistan", (220, 208, 104), 62),
    5: ("Elverişli", "Çoğu etken iyi: ılıman, yeterli su, düz ya da hafif eğimli, verimli toprak.",
        "Batı Avrupa, Kuzey Çin ovası, Kuzeydoğu ABD", (132, 186, 88), 78),
    6: ("Çok elverişli", "Hemen her etken uygun, geniş ve düz alan: dünyanın en yoğun yerleşilen bölgeleri.",
        "Ganj ovası, Yangtze deltası, Po ovası", (40, 142, 84), 90),
    7: ("Buz", "Kalıcı buz örtüsü.", "Antarktika, Grönland", (232, 236, 240), None),
}
ESIKLER = [SINIF[c][4] for c in range(1, 7)]

# etken: (ad, ne ölçer, ağırlık)
ETKEN = [
    ("Sıcaklık", "yıllık ortalama, en soğuk ve en sıcak ay", 3.0),
    ("Su", "nem oranı, nehir ve göl erişimi", 3.0),
    ("Gıda", "bitki üretimi ve büyüme sezonu", 2.0),
    ("Mevsimsellik", "sıcaklık aralığı, kurak ay sayısı ve yağışın yığılması", 1.5),
    ("Arazi", "eğim ve yükseklik", 1.5),
    ("Toprak", "toprak türünün verimliliği (gıdanın içinde)", 0.0),
    ("Deniz", "kıyıya uzaklık", 0.5),
    ("Tehlike", "deprem ve volkan", 1.0),
]
# toprak türü (toprak/toprak.py kodu) → verimlilik 0-1 (WRB türlerinin genel tarımsal sırası; yargı)
TOPRAK_VERIM = {1: 0.40, 2: 0.55, 3: 0.45, 4: 0.80, 5: 0.70, 6: 0.35, 7: 1.00, 8: 0.85,
                9: 0.15, 10: 0.30, 11: 0.20, 12: 0.80, 13: 0.10, 14: 0.95, 15: 0.0}
KM_HUCRE = 9.8          # ~0.088° (enlemde); kıyı uzaklığı için kaba ölçek


def ss(x, a, b):
    """0 (x <= a) .. 1 (x >= b), pürüzsüz; a > b ise ters yönde."""
    t = np.clip((np.asarray(x, float) - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def npp(Tyil, AET):
    nt = 3000.0 / (1 + np.exp(1.315 - 0.119 * Tyil))
    na = 3000.0 * (1 - np.exp(-0.0009695 * np.maximum(AET - 20, 0)))
    return np.minimum(nt, na)


def etkenler(T, Tc, Tw, gdd5, alfa, P, aet, pe, kuru_ay, pay3, egim, z, toprak_f, kiyi_km, tehlike, w):
    """Sekiz etken (0-1), alan etkeni ayrı hesaplanır. w: nehir/göl erişimi 0-1."""
    # nüfus yoğunluğunun yıllık ortalama sıcaklığa dağılımı (Xu vd. 2020): ana tepe ~13 °C,
    # ikinci küçük tepe ~27 °C (musonlu Asya). Düz bir "uygun aralık" yerine kademeli.
    konfor = np.maximum(np.exp(-((T - 13) / 12.0) ** 2), 0.7 * np.exp(-((T - 27) / 5.0) ** 2))
    sic = np.minimum(np.minimum(konfor, ss(Tc, -40, -12)), 1 - ss(Tw, 28, 36))
    alfa_e = alfa + w * (1 - alfa)
    su = ss(alfa_e, 0.10, 0.60) * (1 - 0.5 * ss(P, 2500, 4500))
    aet_e = aet + w * np.maximum(pe - aet, 0)
    # toprak gıdanın içinde çarpan: iklim ne kadar iyi olursa olsun yıkanmış, asidik
    # toprak (Acrisol 0.45) üretimi sınırlar; en fakir toprakta bile %40 kalır
    # (otlatma, ormancılık, teraslı tarım). Ayrı ağırlıkla sayılmaz: çift sayım olurdu.
    gida = np.minimum(ss(npp(T, aet_e), 100, 900), ss(gdd5, 400, 1700)) * (0.4 + 0.6 * toprak_f)
    mev = np.cbrt((1 - ss(Tw - Tc, 25, 60)) * (1 - ss(kuru_ay, 3, 10)) * (1 - ss(pay3, 0.50, 0.95)))
    arazi = (1 - ss(egim, 40, 300)) * (1 - ss(z, 2000, 5000))
    toprak_e = toprak_f
    deniz = 0.6 + 0.4 * np.exp(-kiyi_km / 400.0)
    return [sic, su, gida, mev, arazi, toprak_e, deniz, tehlike]


def birlestir(f):
    """Ağırlıklı geometrik ortalama, çarpı kritik dört etkenin (sıcaklık, su, gıda,
    arazi) en zayıfının karekökü: tek bir ağır kısıt (3600 m yükseklik, kuraklık)
    ortalamada sönmesin, puanı belirgin düşürsün."""
    w = np.array([e[2] for e in ETKEN])
    ln = sum(wi * np.log(np.clip(fi, 1e-3, 1)) for wi, fi in zip(w, f))
    kritik = np.minimum(np.minimum(f[0], f[1]), np.minimum(f[2], f[4]))
    return np.exp(ln / w.sum()) * np.sqrt(np.clip(kritik, 0, 1))


def nehir_sinifi(lat, lon, shape):
    """data/su.json'daki çizilen nehirler (0.01° fark kodlu, tepe başına
    10·log10 debi) ızgaraya işlenir; hücreden geçen en büyük debi sınıfı:
    1 < 200 m³/s, 2 < 2000, 3 >= 2000 (0 = nehir yok)."""
    j = json.load(open(os.path.join(KOK, "data", "su.json"), encoding="utf-8"))
    dl, dn = lat[1] - lat[0], lon[1] - lon[0]
    sinif = np.zeros(shape, np.uint8)
    for n in j["nehirler"]:
        kod = np.asarray(n["p"], float).reshape(-1, 2)
        xy = np.cumsum(kod, axis=0) / 100.0
        Q = 10 ** (np.asarray(n["q"], float) / 10.0)
        for i in range(len(xy) - 1):
            (x0, y0), (x1, y1) = xy[i], xy[i + 1]
            adim = max(2, int(np.hypot(x1 - x0, y1 - y0) / (0.4 * abs(dn))) + 1)
            t = np.linspace(0, 1, adim)
            qa = max(Q[i], Q[min(i + 1, len(Q) - 1)])
            c = 1 if qa < 200 else 2 if qa < 2000 else 3
            r = np.round((lat[0] - (y0 + t * (y1 - y0))) / -dl).astype(int)
            k = np.round(((x0 + t * (x1 - x0)) - lon[0]) / dn).astype(int)
            ok = (r >= 0) & (r < shape[0]) & (k >= 0) & (k < shape[1])
            sinif[r[ok], k[ok]] = np.maximum(sinif[r[ok], k[ok]], c)
    return sinif


# koridor yarıçapı (hücre, ~9.7 km): dar = nehrin hemen yanı, tam etki;
# geniş = debiye göre daha büyük alan, etki kosinüsle yumuşakça söner
DAR_R = {1: 1, 2: 2, 3: 3}
GENIS_R = {1: 2.5, 2: 5, 3: 8}
GOL_DAR, GOL_GENIS = 1, 3


def _profil(dist, r, genis):
    if not genis:
        return (dist <= r).astype(np.float32)
    return np.where(dist < r, 0.5 * (1 + np.cos(np.pi * dist / r)), 0).astype(np.float32)


def su_agirligi(sinif, gol, genis):
    """0..1 su erişimi ağırlığı: nehir ve göl kıyısına uzaklığa göre."""
    R = GENIS_R if genis else DAR_R
    w = np.zeros(sinif.shape, np.float32)
    for c in (1, 2, 3):
        w = np.maximum(w, _profil(ndimage.distance_transform_edt(~(sinif >= c)), R[c], genis))
    dg = ndimage.distance_transform_edt(~gol)
    return np.maximum(w, _profil(dg, GOL_GENIS if genis else GOL_DAR, genis))


def tehlike_alani(lat, lon, shape):
    """Çarpışma, dalma ve dönüşüm sınırlarının ~40 km çevresi (deprem) ve volkan
    kuşakları (toprak/toprak.py maskesi). 1 = tehlikesiz, 0.6'ya kadar iner."""
    t = json.load(open(os.path.join(KOK, "data", "tektonik.json"), encoding="utf-8"))
    dl, dn = lat[1] - lat[0], lon[1] - lon[0]
    sis = np.zeros(shape, bool)
    for s in t["sinirlar"]:
        if s["s"] not in ("SUB", "CCB", "OCB", "OTF", "CTF"):
            continue
        xy = np.cumsum(np.asarray(s["p"], float).reshape(-1, 2), axis=0) / 100.0
        for i in range(len(xy) - 1):
            (x0, y0), (x1, y1) = xy[i], xy[i + 1]
            if abs(x1 - x0) > 20:        # boylam dikişi
                continue
            adim = max(2, int(np.hypot(x1 - x0, y1 - y0) / (0.4 * abs(dn))) + 1)
            u = np.linspace(0, 1, adim)
            r = np.round((lat[0] - (y0 + u * (y1 - y0))) / -dl).astype(int)
            k = np.round(((x0 + u * (x1 - x0)) - lon[0]) / dn).astype(int)
            ok = (r >= 0) & (r < shape[0]) & (k >= 0) & (k < shape[1])
            sis[r[ok], k[ok]] = True
    deprem = ndimage.gaussian_filter(ndimage.binary_dilation(sis, iterations=3).astype(np.float32), 1.5)
    volkan = ndimage.gaussian_filter(tp._volkan_maske(lat, lon, shape).astype(np.float32), 1.5)
    return np.clip(1 - 0.15 * deprem - 0.30 * volkan, 0.6, 1)


def alan_etkeni(S0, kara):
    """Çevredeki ~50 km'de elverişli (>= 0.5) kara payı; dar şerit 0.7, geniş ova 1.0."""
    iyi = ndimage.gaussian_filter(((S0 >= 0.5) & kara).astype(np.float32), 5)
    var = ndimage.gaussian_filter(kara.astype(np.float32), 5)
    pay = np.where(var > 0.05, iyi / np.maximum(var, 0.05), 0)
    return 0.7 + 0.3 * ss(pay, 0.10, 0.60), pay


def dunya_orneklari():
    """Bilinen Dünya yerlerinin yaklaşık iklimiyle kaba sağlama (düz, 50 m, orta toprak,
    kıyıya 100 km, tehlikesiz, nehirsiz). Kaynak: yaklaşık iklim normalleri, ezbere."""
    # ad: T, Tc, Tw, gdd5, alfa, P, aet, pe, kuru_ay, z, pay3 (en yağışlı 3 ayın payı)
    O = {"Paris": (11.5, 4, 20, 2300, 0.85, 640, 520, 610, 0, 50, 0.28),
         "Şangay": (17, 4.5, 28, 3700, 0.9, 1150, 800, 880, 0, 5, 0.45),
         "Moskova": (5.8, -6.5, 18, 1900, 0.8, 700, 450, 560, 0, 150, 0.36),
         "Yakutsk": (-8.8, -38, 19, 1300, 0.6, 240, 150, 250, 3, 100, 0.50),
         "Kahire": (22, 14, 29, 6500, 0.08, 25, 25, 1500, 12, 20, 0.55),
         "Phoenix": (23.5, 12, 34, 6800, 0.1, 190, 190, 1900, 10, 330, 0.40),
         "Singapur": (27, 26, 28, 9500, 1.0, 2300, 1500, 1500, 0, 10, 0.36),
         "Mumbai": (27.5, 24, 30, 9000, 0.6, 2400, 1000, 1700, 7, 10, 0.80),
         "Nairobi": (17.5, 15.5, 19.5, 4900, 0.7, 960, 750, 1100, 3, 1650, 0.55),
         "La Paz": (8.5, 6, 11, 1400, 0.5, 570, 300, 600, 6, 3640, 0.70),
         "Ulan Batur": (-0.4, -22, 17, 1100, 0.45, 270, 210, 480, 6, 1350, 0.75)}
    out = {}
    for ad, (T, Tc, Tw, g5, al, P, ae, pe, dm, z, p3) in O.items():
        f = etkenler(np.array([T]), np.array([Tc]), np.array([Tw]), np.array([g5]), np.array([al]), np.array([P]),
                     np.array([ae]), np.array([pe]), np.array([dm]), np.array([p3]), np.array([30.0]), np.array([z]),
                     np.array([0.8]), np.array([100.0]), np.array([1.0]), np.array([0.0]))
        S = float(birlestir(f)[0] * 100)
        out[ad] = (S, [float(x[0]) for x in f])
    return out


def varyant(ad, genis, G, kutu):
    w = su_agirligi(G["sinif"], G["gol"], genis) * G["kara"]
    f = etkenler(G["T"], G["Tc"], G["Tw"], G["gdd5"], G["alfa"], G["P"], G["aet"], G["pe"], G["kuru_ay"], G["pay3"], G["egim"],
                 G["z"], G["toprak_f"], G["kiyi_km"], G["tehlike"], w)
    S0 = birlestir(f)
    alan, _ = alan_etkeni(S0, G["kara"])
    S = 100 * S0 * alan
    f = f + [alan]
    k = np.clip(np.digitize(S, ESIKLER), 1, 6).astype(np.uint8)
    k[G["buzul"]] = 7
    k[~G["kara"]] = 0
    wgt = G["wgt"]
    pay = {c: float(wgt[k == c].sum() / wgt.sum()) for c in SINIF}
    ort = float((S * wgt).sum() / wgt.sum())
    sulak = (w >= 0.25) & G["kara"]
    print("== nehir çevresi:", "geniş, yumuşak" if genis else "dar")
    for c, (a_, *_r) in SINIF.items():
        print("%d %-14s %%%5.1f" % (c, a_, 100 * pay[c]))
    print("kara ortalaması puan %.1f; su erişimli alan %%%.1f" % (ort, 100 * float((sulak * wgt).sum() / wgt.sum())))
    i0, i1, j0, j1 = kutu
    kc = k[i0:i1, j0:j1]
    F = 2
    en = None; secim = None
    for c in np.unique(kc):
        if c == 0:
            continue
        g = ndimage.gaussian_filter(ndimage.zoom((kc == c).astype(np.float32), F, order=1), 0.9)
        if en is None:
            en = g; secim = np.full(g.shape, c, np.uint8)
        else:
            m = g > en; en[m] = g[m]; secim[m] = c
    zc = ndimage.zoom(G["z"][i0:i1, j0:j1].astype(np.float32), F, order=1)
    gc = ndimage.zoom(G["gol"][i0:i1, j0:j1].astype(np.float32), F, order=1)
    secim[(zc < 0) | (gc >= 0.5)] = 0
    im = Image.fromarray(secim, "P")
    pal = [12, 24, 34] * 256
    for c, (_a, _n, _o, r, _e) in SINIF.items():
        pal[3 * c:3 * c + 3] = list(r)
    im.putpalette(pal)
    im.save(os.path.join(KOK, "data", "yasam%s.png" % ad), optimize=True, transparency=0)
    # kart verisi, dikey 4 bölüm (her biri kaynak çözünürlükte, h yüksekliğinde):
    #   0: R = sınıf + 16 * su erişimli, G = puan * 2.5, B = 0
    #   1-3: dokuz etken (0-1 → 0-255), sırayla RGB, RGB, RGB
    h = i1 - i0
    b0 = np.stack([kc + 16 * sulak[i0:i1, j0:j1], np.clip(np.round(S[i0:i1, j0:j1] * 2.5), 0, 250), np.zeros_like(kc)], -1)
    fb = [np.clip(np.round(x[i0:i1, j0:j1] * 255), 0, 255) for x in f]
    bol = [b0] + [np.stack(fb[3 * m:3 * m + 3], -1) for m in range(3)]
    Image.fromarray(np.concatenate(bol, 0).astype(np.uint8), "RGB").save(os.path.join(KOK, "data", "yasam%s_veri.png" % ad), optimize=True)
    return pay, ort, secim.shape, f


def main():
    ornek = dunya_orneklari()
    print("Dünya örnekleri (düz, 50 m, orta toprak): puan; sıcaklık/su/gıda/mevsim/arazi")
    for ad, (S, f) in ornek.items():
        print("  %-11s %5.1f   %s" % (ad, S, " ".join("%.2f" % x for x in f[:5])))
    d = akim.hesapla(os.path.join(KOK, "buzul", "_iklim_bugun025.npz"))
    z, lat, lon = d["z"], d["lat"], d["lon"]
    su = np.load(os.path.join(KOK, "su", "_su.npz"))
    gol = np.isfinite(su["sev"])
    kara = (z >= 0) & ~gol
    b = np.load(os.path.join(KOK, "bitki", "_bitki.npz"))
    topraklar = np.load(os.path.join(KOK, "toprak", "_toprak.npz"))["k"]
    tv = np.zeros(256, np.float32)
    for c, v in TOPRAK_VERIM.items():
        tv[c] = v
    toprak_f = tv[topraklar]
    T = d["Tay"].mean(0)
    Pa = d["Pay"]
    pay3 = np.max(Pa + np.roll(Pa, 1, axis=0) + np.roll(Pa, 2, axis=0), axis=0) / np.maximum(Pa.sum(0), 1e-6)
    kuru_ay = ((d["Pay"] < 25) & (d["Tay"] > 5)).sum(0).astype(np.float32)
    ocean = ~kara & ~gol
    kiyi_km = ndimage.distance_transform_edt(~ocean, sampling=(KM_HUCRE, KM_HUCRE * 0.8))
    G = dict(T=T, Tc=b["Tc"], Tw=b["Tw"], gdd5=b["gdd5"], alfa=b["alfa"], P=d["P"], aet=d["AET"], pe=d["PE"],
             kuru_ay=kuru_ay, pay3=pay3, egim=tp._egim(z), z=z, toprak_f=toprak_f, kiyi_km=kiyi_km,
             tehlike=tehlike_alani(lat, lon, kara.shape), gol=gol, kara=kara, buzul=d["buzul"],
             sinif=nehir_sinifi(lat, lon, kara.shape), wgt=np.cos(np.radians(lat))[:, None] * kara)
    ii, jj = np.where(kara)
    kutu = (ii.min(), ii.max() + 1, jj.min(), jj.max() + 1)
    i0, i1, j0, j1 = kutu
    pay, ort, sek, f = varyant("", True, G, kutu)
    wgt = G["wgt"]
    print("etken ortalamaları (kara, alan ağırlıklı):", " ".join(
        "%s %.2f" % (n, float((x * wgt).sum() / wgt.sum())) for n, x in zip([e[0] for e in ETKEN] + ["Alan"], f)))
    pay_d, ort_d, _, _ = varyant("_dar", False, G, kutu)
    dl, dn = lat[1] - lat[0], lon[1] - lon[0]
    kesit = [float(lon[j0] - dn / 2), float(lat[i1 - 1] + dl / 2), float(lon[j1 - 1] + dn / 2), float(lat[i0] - dl / 2)]
    veri = dict(ne="Dünyam yaşanabilirlik endeksi (yasam/yasam.py); yöntem YASAM.md",
                kesit=kesit, ortalama=round(ort, 1), ortalama_dar=round(ort_d, 1), yukseklik=int(i1 - i0),
                kodlar="yasam.png (geniş, yumuşak nehir çevresi, varsayılan) ve yasam_dar.png (nehrin yanı); yasam*_veri.png dikey 4 bölüm: 0 = R sınıf + 16 * su erişimli, G puan * 2.5; 1-3 = dokuz etken 0-255 (RGB sırayla)",
                etkenler=[dict(ad=a, ne=n, agirlik=wt) for a, n, wt in ETKEN] + [dict(ad="Alan", ne="çevredeki elverişli kara genişliği", agirlik=0)],
                siniflar={str(c): dict(ad=a, ne=nn, ornek=o, renk=list(rr), alt=e, pay=round(pay[c], 4), pay_dar=round(pay_d[c], 4))
                          for c, (a, nn, o, rr, e) in SINIF.items()})
    with open(os.path.join(KOK, "data", "yasam.json"), "w", encoding="utf-8") as fh:
        json.dump(veri, fh, ensure_ascii=False, indent=1)
    print("yasam.png %dx%d %.0f KB, yasam_veri.png %.0f KB" % (sek[1], sek[0], os.path.getsize(os.path.join(KOK, "data", "yasam.png")) / 1024,
                                                           os.path.getsize(os.path.join(KOK, "data", "yasam_veri.png")) / 1024))


if __name__ == "__main__":
    main()
