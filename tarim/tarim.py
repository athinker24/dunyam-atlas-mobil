"""Tarımsal verimlilik: bir hücrede ekin yetiştirmenin ne kadar kolay ve verimli olduğu, 0-100.

    python tarim/tarim.py            # ~1 dk; data/tarim*.png, tarim.json yazar

Yaşanabilirlikteki "gıda" etkeninin tek başına bir katmanı değil; orada toprak yalnız
bir çarpandı. Burada sahibinin sorusu cevaplanıyor ("verimliliği yalnız toprak türü
belirlemez"): dört etken, her biri 0-1, en zayıf halka belirleyici (Liebig):

  0 ısı     büyüme derece günü (GDD5) ve en sıcak ay (ekinler 34-41 °C arasında söner)
  1 su      yağmurdan gelen nem oranı (AET/PE), kurak ay sayısı, aşırı yağışta toprak yıkanması;
            sulamalı varyantta nehir ve göl kıyısında su eksiği kapanır
  2 toprak  WRB türünün tarımsal sırası (yasam.TOPRAK_VERIM, toprak/toprak.py)
  3 arazi   eğim (sürülebilirlik) ve yükseklik (ekin sınırı)

Birleşim: karekök(en zayıf etken × dört etkenin geometrik ortalaması). Yalnız ortalama
telafi eder (verimli toprak kuraklığı kapatmaz); yalnız minimum tek bir iyi etkeni
yok sayar. Sınıflar mutlak eşiklerle; eşikler seçimdir (YASAM.md ve TARIM.md'de Dünya
örnekleriyle sağlama). Ekin türü ayrımı, gübre, makine ve mülkiyet yok: yalnız doğal
elverişlilik. İki varyant: sulamalı (varsayılan; nehir ve göl kıyısı) ve yalnız yağmur.
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

# kod: (ad, açıklama, Dünya'da örnek, renk, alt sınır puan)
SINIF = {
    1: ("Elverişsiz", "Ekin yetişmez: don, çöl, buz ya da çok dik ve yüksek arazi.",
        "Sahra'nın içi, Tibet platosu, Sibirya'nın kuzeyi", (110, 84, 70), 0),
    2: ("Çok düşük", "Ancak otlatma ya da kıt, riskli ekim; verim çoğu yıl yetersiz.",
        "Sahel'in kuzeyi, İç Asya kurak bozkırı", (190, 128, 78), 15),
    3: ("Düşük", "Bir ağır kısıt var: kısa sezon, kuraklık, fakir toprak ya da eğim.",
        "Kanada kalkanı'nın güneyi, Patagonya", (214, 176, 92), 35),
    4: ("Orta", "Ekim yapılır; belirgin bir kısıt verimi sınırlar.",
        "Orta Anadolu, Sahel, Amazon'un yıkanmış toprakları", (196, 206, 100), 55),
    5: ("Yüksek", "Sezon, su ve toprak büyük ölçüde uygun; hafif kısıtlar.",
        "Ukrayna, Paris havzası, Kuzeydoğu ABD", (120, 184, 90), 78),
    6: ("Çok yüksek", "Dört etken de uygun: derin toprak, yeterli su, uzun sezon, düz arazi.",
        "Po ovası, Kuzey Çin ovası, Ganj ovası", (38, 138, 82), 92),
    7: ("Buz", "Kalıcı buz örtüsü.", "Antarktika, Grönland", (232, 236, 240), None),
}
ESIKLER = [SINIF[c][4] for c in range(1, 7)]

ETKEN = [
    ("Isı", "büyüme sezonunun sıcaklığı ve sıcak ay"),
    ("Su", "yağmur ve (sulamalıda) nehir erişimi, kurak ay"),
    ("Toprak", "toprak türünün tarımsal sırası"),
    ("Arazi", "eğim ve yükseklik"),
]


def etkenler(T, Tw, gdd5, alfa, P, kuru_ay, egim, z, toprak_f, w):
    """Dört etken (0-1). w: nehir/göl erişimi 0-1 (yağmur varyantında 0)."""
    # kalıcı donmuş toprak: yıllık ortalama -1 °C altında başlar, -9 °C'de sürekli olur
    # (Yakutsk -8.8 °C; yaz sıcak olsa da kök bölgesi ve drenaj sınırlı). Yoksa Yakutsk 32 çıkıyordu.
    isi = ss(gdd5, 800, 2600) * (1 - ss(Tw, 34, 41)) * (1 - 0.7 * ss(T, -1, -9))
    alfa_e = alfa + w * (1 - alfa)
    kuru_e = kuru_ay * (1 - w)
    su = ss(alfa_e, 0.25, 0.70) * (1 - 0.5 * ss(kuru_e, 4, 9)) * (1 - 0.3 * ss(P, 2500, 4500))
    # toprak sırası 0.05-0.9 arasında 0-1'e açılır: Acrisol (0.45) ~0.45, Podzol (0.3) ~0.24, Çernozem 1.
    # İlk sürüm 0-0.8 idi; Amazon'un yıkanmış toprağı 65 ile "orta" çıkıyordu (1 Ekim).
    toprak = ss(toprak_f, 0.05, 0.90)
    arazi = (1 - ss(egim, 60, 300)) * (1 - ss(z, 2500, 4500))
    return [isi, su, toprak, arazi]


def birlestir(f):
    a = np.stack([np.clip(x, 1e-3, 1) for x in f])
    return np.sqrt(a.min(0) * np.exp(np.log(a).mean(0)))


def orneklerden():
    """Yaşanabilirliğin Dünya bölgeleri (yasam.DUNYA_ORNEKLERI) üzerinde aynı etkenler,
    hem sulamalı hem yalnız yağmur. Girdiler kaba normallerdir (ezbere)."""
    out = {}
    for ad, v in ys.DUNYA_ORNEKLERI.items():
        T, Tc, Tw, g5, al, P, ae, pe, dm, p3, eg, z, tf, kk, th, w, alan = [np.array([float(x)]) for x in v]
        r = []
        for ww in (w, np.zeros(1)):
            r.append(float(birlestir(etkenler(T, Tw, g5, al, P, dm, eg, z, tf, ww))[0] * 100))
        out[ad] = tuple(r)
    return out


def varyant(ad, sulamali, G, kutu):
    w = ys.su_agirligi(G["sinif"], G["gol"], True) * G["kara"] if sulamali else np.zeros(G["z"].shape, np.float32)
    f = etkenler(G["T"], G["Tw"], G["gdd5"], G["alfa"], G["P"], G["kuru_ay"], G["egim"], G["z"], G["toprak_f"], w)
    S = 100 * birlestir(f)
    sinir = np.argmin(np.stack(f), axis=0).astype(np.uint8)
    k = np.clip(np.digitize(S, ESIKLER), 1, 6).astype(np.uint8)
    k[G["buzul"]] = 7
    k[~G["kara"]] = 0
    wgt = G["wgt"]
    pay = {c: float(wgt[k == c].sum() / wgt.sum()) for c in SINIF}
    ort = float((S * wgt).sum() / wgt.sum())
    sulanan = (w >= 0.25) & G["kara"]
    print("== su:", "sulamalı (nehir ve göl kıyısı)" if sulamali else "yalnız yağmur")
    for c, (a_, *_r) in SINIF.items():
        print("%d %-12s %%%5.1f" % (c, a_, 100 * pay[c]))
    print("kara ortalaması puan %.1f" % ort)
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
    im.save(os.path.join(KOK, "data", "tarim%s.png" % ad), optimize=True, transparency=0)
    # kart verisi, dikey 3 bölüm (kaynak çözünürlükte, h yüksekliğinde):
    #   0: R = sınıf + 16 * sulanan, G = puan * 2.5, B = en zayıf etken (0-3)
    #   1: RGB = ısı, su, toprak (0-1 → 0-255);  2: R = arazi
    b0 = np.stack([kc + 16 * sulanan[i0:i1, j0:j1], np.clip(np.round(S[i0:i1, j0:j1] * 2.5), 0, 250), sinir[i0:i1, j0:j1]], -1)
    fb = [np.clip(np.round(x[i0:i1, j0:j1] * 255), 0, 255) for x in f]
    b1 = np.stack(fb[0:3], -1)
    b2 = np.stack([fb[3], np.zeros_like(fb[3]), np.zeros_like(fb[3])], -1)
    Image.fromarray(np.concatenate([b0, b1, b2], 0).astype(np.uint8), "RGB").save(
        os.path.join(KOK, "data", "tarim%s_veri.png" % ad), optimize=True)
    return pay, ort, secim.shape, f, S


def main():
    print("Dünya bölgeleri: puan (sulamalı / yalnız yağmur)")
    for ad, (a, b) in orneklerden().items():
        print("  %-31s %5.1f / %5.1f" % (ad, a, b))
    d = akim.hesapla(os.path.join(KOK, "buzul", "_iklim_bugun025.npz"))
    z, lat, lon = d["z"], d["lat"], d["lon"]
    su = np.load(os.path.join(KOK, "su", "_su.npz"))
    gol = np.isfinite(su["sev"])
    kara = (z >= 0) & ~gol
    b = np.load(os.path.join(KOK, "bitki", "_bitki.npz"))
    topraklar = np.load(os.path.join(KOK, "toprak", "_toprak.npz"))["k"]
    tv = np.zeros(256, np.float32)
    for c, v in ys.TOPRAK_VERIM.items():
        tv[c] = v
    kuru_ay = ((d["Pay"] < 25) & (d["Tay"] > 5)).sum(0).astype(np.float32)
    G = dict(T=d["Tay"].mean(0), Tw=b["Tw"], gdd5=b["gdd5"], alfa=b["alfa"], P=d["P"], kuru_ay=kuru_ay, egim=tp._egim(z), z=z,
             toprak_f=tv[topraklar], gol=gol, kara=kara, buzul=d["buzul"],
             sinif=ys.nehir_sinifi(lat, lon, kara.shape), wgt=np.cos(np.radians(lat))[:, None] * kara)
    ii, jj = np.where(kara)
    kutu = (ii.min(), ii.max() + 1, jj.min(), jj.max() + 1)
    i0, i1, j0, j1 = kutu
    pay, ort, sek, f, S = varyant("", True, G, kutu)
    wgt = G["wgt"]
    print("etken ortalamaları (kara, alan ağırlıklı):", " ".join(
        "%s %.2f" % (n, float((x * wgt).sum() / wgt.sum())) for n, x in zip([e[0] for e in ETKEN], f)))
    # kara payına göre sınırlayıcı etken (ekilebilir olmayan yerler dahil)
    sn = np.argmin(np.stack(f), axis=0)
    print("sınırlayıcı etken payı:", " ".join("%s %%%.0f" % (e[0], 100 * float(wgt[sn == i].sum() / wgt.sum())) for i, e in enumerate(ETKEN)))
    pay_y, ort_y, _, _, _ = varyant("_yagmur", False, G, kutu)
    dl, dn = lat[1] - lat[0], lon[1] - lon[0]
    kesit = [float(lon[j0] - dn / 2), float(lat[i1 - 1] + dl / 2), float(lon[j1 - 1] + dn / 2), float(lat[i0] - dl / 2)]
    veri = dict(ne="Dünyam tarımsal verimlilik endeksi (tarim/tarim.py); yöntem TARIM.md",
                kesit=kesit, ortalama=round(ort, 1), ortalama_yagmur=round(ort_y, 1), yukseklik=int(i1 - i0),
                kodlar="tarim.png (sulamalı, varsayılan) ve tarim_yagmur.png (yalnız yağmur); tarim*_veri.png dikey 3 bölüm: 0 = R sınıf + 16 * sulanan, G puan * 2.5, B en zayıf etken (0-3); 1 = RGB ısı, su, toprak 0-255; 2 = R arazi",
                etkenler=[dict(ad=a, ne=n) for a, n in ETKEN],
                siniflar={str(c): dict(ad=a, ne=nn, ornek=o, renk=list(rr), alt=e, pay=round(pay[c], 4), pay_yagmur=round(pay_y[c], 4))
                          for c, (a, nn, o, rr, e) in SINIF.items()})
    with open(os.path.join(KOK, "data", "tarim.json"), "w", encoding="utf-8") as fh:
        json.dump(veri, fh, ensure_ascii=False, indent=1)
    print("tarim.png %dx%d %.0f KB, tarim_veri.png %.0f KB" % (sek[1], sek[0], os.path.getsize(os.path.join(KOK, "data", "tarim.png")) / 1024,
                                                          os.path.getsize(os.path.join(KOK, "data", "tarim_veri.png")) / 1024))


if __name__ == "__main__":
    main()
