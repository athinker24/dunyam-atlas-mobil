"""Genel yaşanabilirlik: iklimin bitki ve hayvan yaşamına verdiği üretim tavanı.

    python yasam/yasam.py            # ~40 s; data/yasam.png, yasam_veri.png, yasam.json yazar

İnsana özgü değil: ölçü net birincil üretim (NPP), yani bir yerin bir yılda
bitki kütlesine çevirebileceği enerji; besin zincirindeki her şey buna yaslanır.
Miami modeli (Lieth 1975) iki bağımsız tavan verir, gerçek üretim küçük olandır
(Liebig'in en az etken yasası):

  sıcaklık tavanı   NPP_T = 3000 / (1 + exp(1.315 - 0.119 T))          T: yıllık ortalama °C
  su tavanı         NPP_A = 3000 (1 - exp(-0.00096950 (AET - 20)))     AET: yıllık gerçek buharlaşma mm

Su tavanında Miami'nin yağışlı sürümü (NPP_P, yağış girdisi) yerine Lieth'in
buharlaşma sürümü kullanıldı: motorun yağışı Dünya'nınkinden fazla ve mevsimsel
(CLAUDE.md §8); yağış bitkinin tutabildiğinden çok gelince Miami'nin yağış
formülü şişer. AET zaten su modelinin (su/akim.py) toprak kovasından geçmiş
gerçek buharlaşmasıdır. Çıktı g kuru madde / m² / yıl.

Nehir ve göl kıyısı: uygulamada çizilen nehirlerin kendisi (data/su.json, bütün
kademeler, ortak kaydırma alanıyla kıvrılmış gerçek çizgi; ham ızgara yolu
değil) ızgaraya işlenir, çevresinde debiye göre genişleyen bir koridor ve göl
kıyısı yeraltı suyuna ve taşkına erişimlidir: su tavanı kalkar, buharlaşma
olası buharlaşmaya (PE) çıkar (galeri ormanı, vaha etkisi). İki seçenek (uygulamada
ayar): "Geniş, yumuşak" (varsayılan; debiye göre 2.5 / 5 / 8 hücre, etki kosinüsle
sönerek) ve "Dar" (nehrin hemen yanı, debiye göre 1 / 2 / 3 hücre, tam etki).
Sıcaklık tavanı yine geçerli.

Sınırlar (bilerek kaba): ışık, mevsim uzunluğu, toprak besini, eğim, yangın,
otlayıcı hesaba girmez; yalnız yıllık ortalama sıcaklık ve gerçek buharlaşma.
Buzul (hiç erimeyen kar) ayrı sınıf. Dünya'nın kara ortalaması bu yöntemle
~700 g/m²/yıl; Dünyam'ın kara ortalaması bundan yüksek çünkü kara Dünya'dan
ılık ve nemli, büyük sıcak çölü yok (YASAM.md).
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
BURASI = os.path.dirname(os.path.abspath(__file__)); KOK = os.path.dirname(BURASI)
sys.path.insert(0, os.path.join(KOK, "su")); sys.path.insert(0, KOK)
import akim

# kod: (ad, açıklama, Dünya'da örnek, renk, alt sınır g/m²/yıl)
SINIF = {
    1: ("Yaşam çok kıt", "Üretim neredeyse yok: kurak çöl ya da kışı bitmeyen soğuk. Bitki seyrek, hayvan az.",
        "Sahra'nın içi, Antarktika kıyı çölleri", (78, 70, 66), 0),
    2: ("Çok düşük", "Cılız bitki örtüsü; yağmurdan ya da yazdan sonra kısa bir canlanma.",
        "Yarı çöller, yüksek tundra", (146, 116, 74), 50),
    3: ("Düşük", "Otlak ve tundra düzeyi; yılın çoğunda kıt ama yaşam sürer.",
        "Kuru bozkır, kuzey tundrası", (188, 166, 86), 250),
    4: ("Orta", "Otlaklar, açık ormanlar ve tayga.",
        "Büyük Ovalar, Sibirya taygası", (150, 182, 82), 600),
    5: ("Yüksek", "Yoğun orman ve verimli otlak; büyük hayvan topluluklarını taşır.",
        "Orta Avrupa ormanları, Doğu ABD", (100, 166, 80), 1000),
    6: ("Çok yüksek", "Sıcak, nemli, uzun büyüme dönemi; sık orman.",
        "Güney Çin, Güneydoğu ABD, Atlantik Ormanı", (48, 136, 78), 1400),
    7: ("Uç düzey", "Yıl boyu sıcak ve su kısıtı yok: dünyanın en üretken bölgeleri.",
        "Amazon, Kongo, Endonezya", (16, 96, 72), 1750),
    8: ("Buz", "Kalıcı buz örtüsü: üretim yok.", "Antarktika, Grönland", (232, 236, 240), None),
}
ESIKLER = [SINIF[c][4] for c in range(1, 8)]


def npp(Tyil, AET):
    nt = 3000.0 / (1 + np.exp(1.315 - 0.119 * Tyil))
    na = 3000.0 * (1 - np.exp(-0.0009695 * np.maximum(AET - 20, 0)))
    return np.minimum(nt, na), nt, na


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


def su_agirligi(sinif, gol, genis):
    """0..1 su erişimi ağırlığı: nehir ve göl kıyısına uzaklığa göre."""
    R = GENIS_R if genis else DAR_R
    w = np.zeros(sinif.shape, np.float32)
    for c in (1, 2, 3):
        dist = ndimage.distance_transform_edt(~(sinif >= c))
        w = np.maximum(w, _profil(dist, R[c], genis))
    dg = ndimage.distance_transform_edt(~gol)
    return np.maximum(w, _profil(dg, GOL_GENIS if genis else GOL_DAR, genis))


def _profil(dist, r, genis):
    if not genis:
        return (dist <= r).astype(np.float32)
    return np.where(dist < r, 0.5 * (1 + np.cos(np.pi * dist / r)), 0).astype(np.float32)


def varyant(ad, genis, d, T, sinif, gol, kara, buzul, lat, kutu):
    """Bir nehir çevresi varyantını hesaplar; ad: '' (geniş, varsayılan) ya da '_dar'."""
    w = su_agirligi(sinif, gol, genis) * kara
    # su erişimi ağırlığı kadar AET olası buharlaşmaya (PE) yaklaşır
    aet = d["AET"] + w * np.maximum(d["PE"] - d["AET"], 0)
    n, nt, na = npp(T, aet)
    sinir = (nt < na).astype(np.uint8)          # 1 = sıcaklık sınırlıyor, 0 = su
    k = np.clip(np.digitize(n, ESIKLER), 1, 7).astype(np.uint8)
    k[buzul] = 8
    k[~kara] = 0
    wgt = np.cos(np.radians(lat))[:, None] * kara
    pay = {c: float(wgt[k == c].sum() / wgt.sum()) for c in SINIF}
    ort = float((n * wgt).sum() / wgt.sum())
    sulak = (w >= 0.25) & kara
    print("== nehir çevresi:", "geniş, yumuşak" if genis else "dar")
    for c, (a_, *_r) in SINIF.items():
        print("%d %-16s %%%5.1f" % (c, a_, 100 * pay[c]))
    print("su erişimli (w >= 0.25): kara alanının %%%.1f, ortalama NPP artışı %.0f g/m²/yıl; kara ortalaması %.0f" % (
        100 * float((sulak * wgt).sum() / wgt.sum()),
        float(((n - npp(T, d["AET"])[0]) * (w > 0) * wgt).sum() / ((w > 0) * wgt).sum()), ort))
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
    zc = ndimage.zoom(d["z"][i0:i1, j0:j1].astype(np.float32), F, order=1)
    gc = ndimage.zoom(gol[i0:i1, j0:j1].astype(np.float32), F, order=1)
    secim[(zc < 0) | (gc >= 0.5)] = 0
    im = Image.fromarray(secim, "P")
    pal = [12, 24, 34] * 256
    for c, (_a, _n, _o, r, _e) in SINIF.items():
        pal[3 * c:3 * c + 3] = list(r)
    im.putpalette(pal)
    im.save(os.path.join(KOK, "data", "yasam%s.png" % ad), optimize=True, transparency=0)
    # kart: R = sınıf + 16 * sınırlayıcı (1 sıcaklık) + 32 * nehir/göl kıyısı (w >= 0.25), G = NPP / 12, B = yıllık sıcaklık + 100
    r = kc + 16 * sinir[i0:i1, j0:j1] + 32 * sulak[i0:i1, j0:j1]
    g_ = np.clip(np.round(n[i0:i1, j0:j1] / 12), 0, 255)
    b_ = np.clip(np.round(T[i0:i1, j0:j1] + 100), 0, 255)
    Image.fromarray(np.stack([r, g_, b_], -1).astype(np.uint8), "RGB").save(os.path.join(KOK, "data", "yasam%s_veri.png" % ad), optimize=True)
    return pay, ort, secim.shape


def main():
    d = akim.hesapla(os.path.join(KOK, "buzul", "_iklim_bugun025.npz"))
    z, lat, lon = d["z"], d["lat"], d["lon"]
    su = np.load(os.path.join(KOK, "su", "_su.npz"))
    gol = np.isfinite(su["sev"])
    kara = (z >= 0) & ~gol
    T = d["Tay"].mean(0)
    sinif = nehir_sinifi(lat, lon, kara.shape)
    ii, jj = np.where(kara)
    kutu = (ii.min(), ii.max() + 1, jj.min(), jj.max() + 1)
    i0, i1, j0, j1 = kutu
    pay, ort, sek = varyant("", True, d, T, sinif, gol, kara, d["buzul"], lat, kutu)
    pay_d, ort_d, _ = varyant("_dar", False, d, T, sinif, gol, kara, d["buzul"], lat, kutu)
    dl, dn = lat[1] - lat[0], lon[1] - lon[0]
    kesit = [float(lon[j0] - dn / 2), float(lat[i1 - 1] + dl / 2), float(lon[j1 - 1] + dn / 2), float(lat[i0] - dl / 2)]
    veri = dict(ne="Dünyam genel yaşanabilirlik = Miami/Lieth net birincil üretim (yasam/yasam.py); yöntem YASAM.md",
                kesit=kesit, ortalama=round(ort), ortalama_dar=round(ort_d),
                kodlar="yasam.png (geniş, yumuşak nehir çevresi, varsayılan) ve yasam_dar.png (nehrin hemen yanı); yasam*_veri.png: R = sınıf + 16 * sıcaklık sınırlı + 32 * su erişimli, G = NPP/12, B = yıllık sıcaklık + 100",
                siniflar={str(c): dict(ad=a, ne=nn, ornek=o, renk=list(rr), alt=e, pay=round(pay[c], 4), pay_dar=round(pay_d[c], 4))
                          for c, (a, nn, o, rr, e) in SINIF.items()})
    with open(os.path.join(KOK, "data", "yasam.json"), "w", encoding="utf-8") as fh:
        json.dump(veri, fh, ensure_ascii=False, indent=1)
    print("yasam.png %dx%d %.0f KB, yasam_dar.png %.0f KB" % (sek[1], sek[0], os.path.getsize(os.path.join(KOK, "data", "yasam.png")) / 1024,
                                                           os.path.getsize(os.path.join(KOK, "data", "yasam_dar.png")) / 1024))


if __name__ == "__main__":
    main()
