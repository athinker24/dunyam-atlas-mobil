"""Hayvanlar: iki okuma, ikisi de iklimden ve araziden türetilir (kurgu tür yok).

    python hayvan/hayvan.py          # ~1 dk; data/hayvan*.png, hayvan.json yazar

1. Topluluklar: bir hücrede hangi hayvan topluluğu yaşar. Taban biyomdur
   (bitki/bitki.py, BIOME1): savan sürüleri, bozkır sürüleri, kuzey ormanı...
   Üstüne iki yerel yaşam alanı biner: dağ (yükseklik >= 2200 m ve dik) ve
   sulak alan (büyük nehir yatağı ve göl kıyısı, alçak ve düz). Kartta Dünya'dan
   tipik hayvanlar örnek olarak verilir; Dünyam'ın türleri tanımlı değil.

2. Tür zenginliği: ne kadar çok tür yaşar, 0-1. Kaba ölçekte en iyi açıklayıcı
   su-enerji dengesidir (Hawkins vd. 2003, Ecology: gerçek buharlaşma AET ve net
   birincil üretim; sıcak bölgelerde su, soğukta enerji sınırlar). Dağlık ve
   parçalı arazi türleşmeyi artırır (Rahbek vd. 2019, Science: dağlar ve
   topoğrafik çeşitlilik). Formül: ss(AET, 50, 1200)^0.6 (azalan getiri) ×
   (0.35 + 0.65 ss(T, -8, 18)) (soğukta enerji) × (1 + 0.45 ss(yerel yükseklik
   std, 50, 700 m)) × (1 + 0.15 sulak), 1.3'e bölünüp 0-1'e kırpılır.
   Sınıflar 0.2 adımlarla. Eşikler seçimdir; Dünya örnekleri HAYVAN.md'de.
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
BURASI = os.path.dirname(os.path.abspath(__file__)); KOK = os.path.dirname(BURASI)
sys.path.insert(0, os.path.join(KOK, "yasam")); sys.path.insert(0, os.path.join(KOK, "su")); sys.path.insert(0, KOK)
sys.path.insert(0, os.path.join(KOK, "toprak"))
import akim
import toprak as tp
import yasam as ys
from yasam import ss

# kod: (ad, açıklama, Dünya'da tipik hayvanlar, Dünya'da örnek yer, renk)
TOPLULUK = {
    1: ("Tropik orman", "Katmanlı, sürekli yeşil orman: ağaçta yaşayan türler baskın, tür sayısı en yüksek.",
        "primatlar, papağan ve tukanlar, ağaç kurbağaları, jaguar ya da leopar", "Amazon, Kongo havzası", (30, 110, 70)),
    2: ("Savan sürüleri", "Otlak ve seyrek ağaç: büyük otobur sürüleri ve onları izleyen yırtıcılar, yağmura göre göç.",
        "zebra ve antiloplar, fil, zürafa, aslan, sırtlan, akbaba", "Serengeti, Sahel'in güneyi, Cerrado", (196, 170, 80)),
    3: ("Ilıman orman", "Mevsimli yaprak döken ya da karışık orman: orta boy memeliler ve ötücü kuşlar.",
        "kızıl geyik, yaban domuzu, boz ayı, kurt, porsuk, ağaçkakan", "Orta Avrupa, Doğu ABD, Kuzeydoğu Çin", (92, 150, 90)),
    4: ("Maki", "Kurak yazlı sert yapraklı çalılık: kuraklığa dayanıklı küçük memeliler ve sürüngenler.",
        "yaban keçisi, tavşan, kertenkele ve yılanlar, kartal", "Akdeniz kıyıları, Kaliforniya", (160, 150, 90)),
    5: ("Bozkır sürüleri", "Ağaçsız serin otlak: hızlı koşan otoburlar, yuvalı kemiriciler, açık alan yırtıcıları.",
        "yaban atı, saiga antilobu, bizon, dağ sıçanı ve yer sincabı, step kartalı", "Kazak bozkırı, Moğolistan, Büyük Ovalar", (214, 196, 120)),
    6: ("Kuzey ormanı", "İğne yapraklı tayga: uzun kış, az tür ama geniş alanlı büyük memeliler.",
        "sığın, kurt, vaşak, samur, boz ayı, orman tavuğu", "Sibirya taygası, Kanada", (52, 96, 92)),
    7: ("Tundra göçmenleri", "Ağaçsız soğuk ova: yazın göçmen kuşlar ve sürüler gelir, kışın çok azı kalır.",
        "ren geyiği, kutup tilkisi, lemming, kar baykuşu, göçmen kazlar", "Kuzey Kanada, Yamal", (150, 170, 170)),
    8: ("Çöl", "Kurak ve seyrek: gece etkin, susuzluğa dayanıklı küçük hayvanlar.",
        "deve, çöl tilkisi, jerboa, akrep, kertenkele", "Sahra, Gobi", (222, 190, 140)),
    9: ("Dağ", "Yüksek ve dik arazi: kayalık uzmanı otoburlar ve geniş alanlı yırtıcılar; yükseklikle kuşak kuşak değişir.",
        "yaban keçisi, dağ koyunu, kar leoparı, yak, akbaba", "Himalaya, Alpler, And dağları", (130, 110, 120)),
    10: ("Sulak alan, nehir", "Büyük nehir yatağı ve göl kıyısı: su kuşları, balık ve suya bağlı memeliler; göç yolları.",
         "balıkçıl ve flamingolar, ördek ve kazlar, su samuru, sıcakta timsah ve su aygırı", "Okavango, Tuna deltası, Pantanal", (70, 140, 190)),
    11: ("Buz", "Kalıcı buz örtüsü: kara hayvanı yok denecek kadar az.", "kıyıda fok ve deniz kuşları", "Antarktika, Grönland'ın içi", (232, 236, 240)),
}
BIYOM_TOPLULUK = {1: (1, 2), 2: (3, 10, 16), 3: (4, 5, 6, 8), 4: (9,), 5: (11,), 6: (7,), 7: (12,), 8: (13, 14), 11: (15,)}
# lejant için kısa ad (dar ekranda üç sütun)
KISA = {2: "Savan", 5: "Bozkır", 7: "Tundra", 10: "Sulak alan"}
ZENGIN = {1: ("Çok düşük", (70, 60, 90)), 2: ("Düşük", (70, 100, 150)), 3: ("Orta", (60, 150, 140)),
          4: ("Yüksek", (120, 190, 90)), 5: ("Çok yüksek", (230, 210, 80)), 6: ("Buz", (232, 236, 240))}
ZENGIN_ESIK = [0.2, 0.4, 0.6, 0.8]


def zenginlik(aet, T, het, sulak):
    r = ss(aet, 50, 1200) ** 0.6 * (0.35 + 0.65 * ss(T, -8, 18)) * (1 + 0.45 * ss(het, 50, 700)) * (1 + 0.15 * sulak)
    return np.clip(r / 1.3, 0, 1)


# Dünya sağlaması: kaba normaller (ezbere): AET mm, yıllık ort. °C, yerel yükseklik std m, sulak 0-1
DUNYA = {
    "Amazon (Manaus)": (1400, 27.5, 30, 0.5), "Kuzey And yamacı (Ekvador)": (1100, 18, 900, 0.2),
    "Kongo havzası": (1250, 25, 60, 0.4), "Serengeti": (650, 21, 150, 0.1), "Orta Avrupa": (500, 9, 120, 0.2),
    "Kazak bozkırı": (300, 5, 60, 0.0), "Sibirya taygası (Yakutsk)": (150, -8.8, 80, 0.1), "Kuzey Kanada tundrası": (150, -12, 40, 0.1),
    "Sahra içi": (15, 24, 100, 0.0), "Himalaya eteği (Nepal)": (900, 16, 1000, 0.1), "Akdeniz (Yunanistan)": (450, 17, 500, 0.0),
}


def main():
    print("Dünya bölgeleri: tür zenginliği (0-1)")
    for ad, (a, t, h, s) in DUNYA.items():
        print("  %-28s %.2f" % (ad, float(zenginlik(np.array(a, float), np.array(t, float), np.array(h, float), np.array(s, float)))))
    d = akim.hesapla(os.path.join(KOK, "buzul", "_iklim_bugun025.npz"))
    z, lat, lon = d["z"], d["lat"], d["lon"]
    su = np.load(os.path.join(KOK, "su", "_su.npz"))
    gol = np.isfinite(su["sev"]); kara = (z >= 0) & ~gol
    bk = np.load(os.path.join(KOK, "bitki", "_bitki.npz"))["k"]
    egim = tp._egim(z)
    T = d["Tay"].mean(0)
    # sulak alan: debi sınıfı >= 2 nehir (>= 200 m³/s) ve göl kıyısı, alçak ve düz
    sinif = ys.nehir_sinifi(lat, lon, kara.shape)
    sulak = (ndimage.binary_dilation(sinif >= 2, iterations=1) | (ndimage.distance_transform_edt(~gol) <= 1.5)) & kara & (z < 1200) & (egim < 80)
    zs = np.where(kara, z, 0).astype(float)
    m1 = ndimage.uniform_filter(zs, 7); m2 = ndimage.uniform_filter(zs * zs, 7)
    het = np.sqrt(np.maximum(m2 - m1 * m1, 0))
    buz = (bk == 15) | d["buzul"]
    R = zenginlik(d["AET"], T, het, ndimage.gaussian_filter(sulak.astype(np.float32), 1.5))
    top = np.zeros(z.shape, np.uint8)
    for c, bs in BIYOM_TOPLULUK.items():
        for b in bs:
            top[bk == b] = c
    top[(z >= 2200) & (egim >= 120) & ~buz] = 9
    top[sulak & ~buz] = 10
    top[buz] = 11
    top[~kara] = 0
    zc = np.clip(np.digitize(R, ZENGIN_ESIK) + 1, 1, 5).astype(np.uint8)
    zc[buz] = 6; zc[~kara] = 0
    wgt = np.cos(np.radians(lat))[:, None] * kara
    pay_t = {c: float(wgt[top == c].sum() / wgt.sum()) for c in TOPLULUK}
    pay_z = {c: float(wgt[zc == c].sum() / wgt.sum()) for c in ZENGIN}
    print("topluluklar:", " ".join("%s %%%.1f" % (TOPLULUK[c][0], 100 * p) for c, p in pay_t.items()))
    print("zenginlik:", " ".join("%s %%%.1f" % (ZENGIN[c][0], 100 * p) for c, p in pay_z.items()))
    ii, jj = np.where(kara)
    i0, i1, j0, j1 = ii.min(), ii.max() + 1, jj.min(), jj.max() + 1
    F = 2
    zc2 = ndimage.zoom(z[i0:i1, j0:j1].astype(np.float32), F, order=1)
    gc2 = ndimage.zoom(gol[i0:i1, j0:j1].astype(np.float32), F, order=1)

    def yaz(k, renkler, ad):
        kc = k[i0:i1, j0:j1]
        en = None; secim = None
        for c in np.unique(kc):
            if c == 0:
                continue
            g = ndimage.gaussian_filter(ndimage.zoom((kc == c).astype(np.float32), F, order=1), 0.9)
            if en is None:
                en = g; secim = np.full(g.shape, c, np.uint8)
            else:
                m = g > en; en[m] = g[m]; secim[m] = c
        secim[(zc2 < 0) | (gc2 >= 0.5)] = 0
        im = Image.fromarray(secim, "P")
        pal = [12, 24, 34] * 256
        for c, r in renkler.items():
            pal[3 * c:3 * c + 3] = list(r)
        im.putpalette(pal)
        im.save(os.path.join(KOK, "data", ad), optimize=True, transparency=0)
        return secim.shape
    sek = yaz(top, {c: v[4] for c, v in TOPLULUK.items()}, "hayvan.png")
    yaz(zc, {c: v[1] for c, v in ZENGIN.items()}, "hayvan_zengin.png")
    # kart verisi (kaynak çözünürlükte): R = topluluk, G = zenginlik sınıfı, B = zenginlik × 250
    v = np.stack([top[i0:i1, j0:j1], zc[i0:i1, j0:j1], np.clip(np.round(R[i0:i1, j0:j1] * 250), 0, 250).astype(np.uint8)], -1)
    Image.fromarray(v.astype(np.uint8), "RGB").save(os.path.join(KOK, "data", "hayvan_veri.png"), optimize=True)
    dl, dn = lat[1] - lat[0], lon[1] - lon[0]
    kesit = [float(lon[j0] - dn / 2), float(lat[i1 - 1] + dl / 2), float(lon[j1 - 1] + dn / 2), float(lat[i0] - dl / 2)]
    veri = dict(ne="Dünyam hayvan toplulukları ve tür zenginliği (hayvan/hayvan.py); yöntem HAYVAN.md",
                kesit=kesit, kodlar="hayvan.png (topluluk), hayvan_zengin.png (zenginlik sınıfı); hayvan_veri.png R topluluk, G zenginlik sınıfı, B zenginlik × 250",
                topluluklar={str(c): dict(ad=a, kisa=KISA.get(c, a), ne=n, hayvanlar=h, ornek=o, renk=list(r), pay=round(pay_t[c], 4))
                             for c, (a, n, h, o, r) in TOPLULUK.items()},
                zenginlik={str(c): dict(ad=a, renk=list(r), pay=round(pay_z[c], 4)) for c, (a, r) in ZENGIN.items()})
    with open(os.path.join(KOK, "data", "hayvan.json"), "w", encoding="utf-8") as fh:
        json.dump(veri, fh, ensure_ascii=False, indent=1)
    print("hayvan.png %dx%d %.0f KB, hayvan_zengin.png %.0f KB, hayvan_veri.png %.0f KB" % (
        sek[1], sek[0], *(os.path.getsize(os.path.join(KOK, "data", f)) / 1024 for f in ("hayvan.png", "hayvan_zengin.png", "hayvan_veri.png"))))


if __name__ == "__main__":
    main()
