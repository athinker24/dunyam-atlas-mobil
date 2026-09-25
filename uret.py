# -*- coding: utf-8 -*-
"""Dunyam Atlasi — veri ureticisi. Bu repo TEK BASINA yeterlidir.

    python uret.py                 # 0.25 derece (olculdu ~13-15 dk, 4 cekirdek)
    python uret.py --res 1.0       # kaba ve hizli deneme (~1 dk)
    python uret.py --ozet          # bitince sinif paylarini da yazar

Ne yapar: dunya/dunyam.json + dunyam.currents.json + dunyam_heightmap.png
dosyalarini okur, iklim motorunu (motor/) kosar ve uygulamanin okudugu
data/atlas.json dosyasini yazar. Masaustune, GeoTIFF'e ya da rasterio'ya
bagimli DEGILDIR; numpy + scipy + pillow yeter.

Iklimi degistirmek icin dunya/dunyam.json duzenlenir (params blogu, donus,
egiklik, isi...), sonra bu betik kosulur. Nedenler ayni dosyadaki "_" ile
baslayan notlarda yazili — degisiklik yaparken oraya da yaz.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import tempfile
import time

import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)

from motor import grid as G, model, sanity, temperature   # noqa: E402
import doku                                           # noqa: E402

DUNYA = os.path.join(BURASI, "dunya")
CIKTI = os.path.join(BURASI, "data", "atlas.json")

# Sinif kodu -> (kisa ad, yedek RGB, tanim). Haritanin gercek renkleri
# uygulamanin kendi paletinden (app.js icindeki KPAL) gelir; buradaki RGB
# yalnizca palet bulunamazsa kullanilir.
LEG = {
    1: ("Af", (0, 0, 255), "Tropikal, yağmur ormanı"),
    2: ("Am", (0, 120, 255), "Tropikal, muson"),
    3: ("Aw", (70, 170, 250), "Tropikal, savan"),
    4: ("BWh", (255, 0, 0), "Kurak, çöl, sıcak"),
    5: ("BWk", (255, 150, 150), "Kurak, çöl, soğuk"),
    6: ("BSh", (245, 165, 0), "Kurak, bozkır, sıcak"),
    7: ("BSk", (255, 220, 100), "Kurak, bozkır, soğuk"),
    8: ("Csa", (255, 255, 0), "Ilıman, kurak yaz, sıcak yaz"),
    9: ("Csb", (200, 200, 0), "Ilıman, kurak yaz, ılık yaz"),
    10: ("Csc", (150, 150, 0), "Ilıman, kurak yaz, serin yaz"),
    11: ("Cwa", (150, 255, 150), "Ilıman, kurak kış, sıcak yaz"),
    12: ("Cwb", (100, 200, 100), "Ilıman, kurak kış, ılık yaz"),
    13: ("Cwc", (50, 150, 50), "Ilıman, kurak kış, serin yaz"),
    14: ("Cfa", (200, 255, 80), "Ilıman, kuraksız, sıcak yaz"),
    15: ("Cfb", (100, 255, 80), "Ilıman, kuraksız, ılık yaz"),
    16: ("Cfc", (50, 200, 0), "Ilıman, kuraksız, serin yaz"),
    17: ("Dsa", (255, 0, 255), "Soğuk, kurak yaz, sıcak yaz"),
    18: ("Dsb", (200, 0, 200), "Soğuk, kurak yaz, ılık yaz"),
    19: ("Dsc", (150, 50, 150), "Soğuk, kurak yaz, serin yaz"),
    20: ("Dsd", (150, 100, 150), "Soğuk, kurak yaz, çok soğuk kış"),
    21: ("Dwa", (170, 175, 255), "Soğuk, kurak kış, sıcak yaz"),
    22: ("Dwb", (90, 120, 220), "Soğuk, kurak kış, ılık yaz"),
    23: ("Dwc", (75, 80, 180), "Soğuk, kurak kış, serin yaz"),
    24: ("Dwd", (50, 0, 135), "Soğuk, kurak kış, çok soğuk kış"),
    25: ("Dfa", (0, 255, 255), "Soğuk, kuraksız, sıcak yaz"),
    26: ("Dfb", (55, 200, 255), "Soğuk, kuraksız, ılık yaz"),
    27: ("Dfc", (0, 125, 125), "Soğuk, kuraksız, serin yaz"),
    28: ("Dfd", (0, 70, 95), "Soğuk, kuraksız, çok soğuk kış"),
    29: ("ET", (178, 178, 178), "Kutup, tundra"),
    30: ("EF", (102, 102, 102), "Kutup, buzul"),
}

# Kullanicinin isaretledigi bozkir bolgesi. Poligon 2000x1000'lik gorselden
# okundu; cevrim yukseklik haritasini ureten betikle AYNI sayilari kullanir.
POLI = [(1180, 62), (1310, 68), (1420, 130), (1470, 210), (1475, 218),
        (1400, 265), (1395, 290), (1330, 330), (1245, 372), (1215, 372),
        (1100, 330), (1010, 315), (955, 300), (940, 290), (955, 200),
        (1010, 120), (1060, 90), (1120, 68)]
GOR_W, GOR_H, CIZ_NX, CIZ_NY = 2000, 1000, 2048, 1024
KUZEY, DLAT, LON_SPAN = 61.473, 0.070157, 94.830


def enlemboylam(x, y):
    c = x * CIZ_NX / GOR_W
    r = y * CIZ_NY / GOR_H
    return (KUZEY - r * DLAT, -LON_SPAN / 2 + c * LON_SPAN / CIZ_NX)


def dunya_yukle():
    """dunya/dunyam.json'u okur, dosya yollarini bu repoya gore duzeltir.

    Kaynak JSON projedeki haliyle AYNEN duruyor (senkron denetimi bozulmasin
    diye); icindeki 'worlds/...' ve 'worldinfo/...' yollari burada bellekte
    duzeltilip gecici bir dosyaya yaziliyor, sonra siliniyor.
    """
    with open(os.path.join(DUNYA, "dunyam.json"), encoding="utf-8") as fh:
        ham = json.load(fh)
    ham["currents_file"] = os.path.join(DUNYA, "dunyam.currents.json")
    ham["heightmap"] = dict(ham["heightmap"])
    ham["heightmap"]["file"] = os.path.join(DUNYA, "dunyam_heightmap.png")
    # Her koşu KENDİ geçici dosyasını alır: sabit bir ad (.dunya_gecici.json)
    # aynı anda koşan iki üreticide birinin dosyasını ötekine sildiriyordu
    # (FileNotFoundError, ölçüldü).
    fd, gecici = tempfile.mkstemp(prefix="dunya_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(ham, fh, ensure_ascii=False)
        return G.World.load(gecici)
    finally:
        os.remove(gecici)


def grid_kur(w, res):
    hm = w.heightmap
    return G.from_heightmap(
        hm["file"], w,
        sea_level_value=hm["sea_level_value"],
        max_elev_m=hm["max_elev_m"],
        max_depth_m=hm["max_depth_m"],
        bounds=tuple(hm.get("bounds", (-180.0, -90.0, 180.0, 90.0))),
        res_deg=res,
        band=hm.get("band", 1),
        elev_gamma=hm.get("elev_gamma", 1.0),
        elev_curve=hm.get("elev_curve"),
    )


def kodla(a, lo, hi, olcek="lin"):
    """1..255 bayta kodlar; uygulama val() ile ayni formulle geri acar.

    olcek="kok": x = ((v-lo)/(hi-lo))**0.5 kodlanir, acarken karesi alinir.
    Yagista kullanilir: aralik 0..7000 mm'ye uzaninca dogrusal bir basamak
    28 mm olur ve kurak hucreler birbirinden ayrilamaz; kok olcekte dusuk
    ucta basamak ~0.1 mm, yuksek ucta ~55 mm.
    """
    x = np.clip((np.nan_to_num(a, nan=lo) - lo) / max(hi - lo, 1e-9), 0.0, 1.0)
    if olcek == "kok":
        x = np.sqrt(x)
    q = np.clip(np.round(x * 254) + 1, 1, 255)
    return base64.b64encode(q.astype(np.uint8).tobytes()).decode()


# Motorun rapor metinleri ASCII (motor/ asil projeyle ortak, orada boyle).
# Uygulamada gosterilirken Turkce karakterlerle yazilir; yalniz bu gosterim.
_TURKCE = [
    ("sayisal saglik", "sayısal sağlık"), ("negatif degil", "negatif değil"), ("en dusuk", "en düşük"),
    ("buyuk olcude donmus degil", "büyük ölçüde donmuş değil"), ("okyanus-aylarin", "okyanus-ayların"),
    ("donma noktasinda", "donma noktasında"), ("buz yuzeyi", "buz yüzeyi"), ("ust siniri", "üst sınırı"),
    ("en yuksek", "en yüksek"), ("kuresel", "küresel"), ("sicaklik", "sıcaklık"), ("dusuyor", "düşüyor"),
    ("ARTIYOR", "ARTIYOR"), ("asiri egiklik", "aşırı eğiklik"), ("yukseklikle sogume", "yükseklikle soğuma"),
    ("yukseklik", "yükseklik"), ("esdogrusalligi", "eşdoğrusallığı"), ("esdogrusallik", "eşdoğrusallık"),
    ("iyi kosullu dunyada", "iyi koşullu dünyada"), ("genligi", "genliği"), ("kucuk", "küçük"),
    ("yagis aliyor", "yağış alıyor"), ("yagis", "yağış"), ("alan agirlikli", "alan ağırlıklı"),
    ("mm/yil", "mm/yıl"), ("sinifi dagilimi", "sınıfı dağılımı"), ("degil", "değil"), ("sinif", "sınıf"),
    ("yaygin", "yaygın"), ("basinci kelepceye dayanmiyor", "basıncı kelepçeye dayanmıyor"),
    ("kelepce", "kelepçe"), ("hucre", "hücre"), ("buyuk", "büyük"), ("isinim", "ışınım"), ("egiklik", "eğiklik"),
]


def turkce(metin: str) -> str:
    for a, b in _TURKCE:
        metin = metin.replace(a, b)
    return re.sub(r"(\d) C\b", r"\1 °C", metin)


def kirp(r, pay_deg=22.0):
    """Yuku karanin cevresine kirpar.

    Gezegenin %93'u okyanus; tam gridi telefona gondermek bosuna, uzaktaki
    acik okyanusun tek bilgisi 'derin'. Kara sinir kutusu + pay kadari kalir.
    """
    w, h = r["w"], r["h"]
    B, D, Dg, Y = r["bounds"]
    land = np.unpackbits(np.frombuffer(base64.b64decode(r["land"]), np.uint8))[:w * h].reshape(h, w)
    ys, xs = np.where(land)
    px, py = int(pay_deg / ((Dg - B) / w)), int(pay_deg / ((Y - D) / h))
    x0, x1 = max(0, xs.min() - px), min(w, xs.max() + px + 1)
    y0, y1 = max(0, ys.min() - py), min(h, ys.max() + py + 1)

    def kes(b64):
        a = np.frombuffer(base64.b64decode(b64), np.uint8).reshape(h, w)
        return base64.b64encode(a[y0:y1, x0:x1].tobytes()).decode()

    r["land"] = base64.b64encode(np.packbits(land[y0:y1, x0:x1]).tobytes()).decode()
    r["elev"]["data"] = kes(r["elev"]["data"])
    for f in r["fields"].values():
        f["model"] = kes(f["model"])
    dlon, dlat = (Dg - B) / w, (Y - D) / h
    r["bounds"] = [round(B + x0 * dlon, 4), round(Y - y1 * dlat, 4),
                   round(B + x1 * dlon, 4), round(Y - y0 * dlat, 4)]
    r["w"], r["h"] = int(x1 - x0), int(y1 - y0)
    return r, (w, h), (y0, y1, x0, x1)


def dolasim(r, g, w, pencere, cikti_dir):
    """Ruzgar, deniz yuzeyi sicakligi ve akinti yollari: uygulamanin Dolasim
    sekmesi icin.

    data/dolasim.png, RGB, 12 ay alt alta (ay m = satir m*h .. (m+1)*h):
        R, G = yuzey ruzgari u (dogu+), v (kuzey+): 128 + deger/ust*127
        B    = deniz yuzeyi sicakligi, 1..255 dogrusal [lo, hi]; kara
               hucreleri en yakin okyanusun degeriyle dolu (kiyida cift
               dogrusal aradegerleme karanin sicakligini denize sizdirmasin)
    Alanlar puruzsuz: ~0.75 derecelik bloklara ortalanir (0.25'te 3x3). Tam
    cozunurlukte 12 ay x 3 alan 7.5 MB'lik PNG olurdu, bu ~150 KB.

    Akinti yollari motora giren dosyadan (dunya/dunyam.currents.json)
    oldugu gibi gecer: uygulama motorun kullandigi yolu cizer, turetilmis
    bir sey degil.
    """
    from PIL import Image
    from scipy import ndimage
    y0, y1, x0, x1 = pencere
    hucre = (g.bounds[2] - g.bounds[0]) / g.shape[1]
    f = max(1, int(round(0.75 / hucre)))
    h, wd = (y1 - y0) // f, (x1 - x0) // f

    def blok(a):
        a = a[..., y0:y0 + h * f, x0:x0 + wd * f]
        return a.reshape(a.shape[:-2] + (h, f, wd, f)).mean(axis=(-3, -1))

    u, v, sst = blok(r["u"]), blok(r["v"]), blok(r["sst"])
    kara = blok(g.land.astype(float)) > 0.5
    ust = float(np.ceil(max(np.abs(u).max(), np.abs(v).max())))
    deniz_sst = sst[:, ~kara]
    slo, shi = float(np.floor(deniz_sst.min())), float(np.ceil(deniz_sst.max()))
    _, (iy, ix) = ndimage.distance_transform_edt(kara, return_indices=True)
    sst = sst[:, iy, ix]
    bayt = lambda a: np.clip(np.round(128 + a / ust * 127), 1, 255).astype(np.uint8)
    sb = np.clip(np.round(1 + (sst - slo) / (shi - slo) * 254), 1, 255).astype(np.uint8)
    img = np.stack([bayt(u), bayt(v), sb], axis=-1).reshape(12 * h, wd, 3)
    Image.fromarray(img).save(os.path.join(cikti_dir, "dolasim.png"), optimize=True)

    akintilar = []
    for c in temperature.load_currents(w):
        a = np.asarray(c["anomaly_c"], dtype=float)
        akintilar.append({"ad": c.get("name", ""), "yol": [[round(x, 2), round(y, 2)] for x, y in c["path"]],
                          "anomali": round(float(a.mean()), 2), "genislik_km": float(c["width_km"]),
                          "taper": c.get("taper", [1.0, 1.0])})
    return {"w": int(wd), "h": int(h), "blok": int(f), "ruzgar_ust": ust, "sst_lo": slo, "sst_hi": shi}, akintilar


def kunye(w, g, yillik_yagis):
    """Kunye paylari ALAN agirlikli olmali.

    Equirectangular gridde hucre alani cos(enlem) ile kuculur; hucre saymak
    yuksek enlemleri sisirir. Bu bir kere atlanmisti ve kara yagisini 1375
    gosteriyordu, dogrusu 1492 idi.
    """
    kara = g.land
    alan = np.cos(np.radians(np.broadcast_to(g.lat[:, None], g.shape)))
    agir = float((yillik_yagis[kara] * alan[kara]).sum() / alan[kara].sum())
    lat = np.broadcast_to(g.lat[:, None], g.shape)[kara]
    yon = lambda a: "%.0f°%s" % (abs(a), "K" if a >= 0 else "G")
    return [
        ["gün", ("%.1f" % w.rotation_period_h).rstrip("0").rstrip(".") + " saat"],
        ["eksen eğikliği", "%.1f°" % w.axial_tilt_deg],
        ["yıl", "%.0f gün" % w.year_length_days],
        ["kara payı", "%%%.1f" % (100 * alan[kara].sum() / alan.sum())],
        ["kara kuşağı", "%s – %s" % (yon(lat.max()), yon(lat.min()))],
        ["en yüksek nokta", "%.0f m (hücre ortalamasında %.0f m)"
         % (w.heightmap["max_elev_m"], float(g.elev[kara].max()))],
        ["kara yağışı", "%.0f mm/yıl" % agir],
    ]


def ozet_yaz(g, K, yillik_yagis):
    """Sinif paylari, ALAN agirlikli. Kiyas sutunu Beck 2018 rasterinden."""
    kara = g.land
    alan = np.cos(np.radians(np.broadcast_to(g.lat[:, None], g.shape)))
    pay = lambda l: 100 * alan[np.isin(K, list(l)) & kara].sum() / alan[kara].sum()
    print()
    print("  %-22s %8s %12s" % ("", "Dunyam", "gercek Dunya"))
    for ad, kodlar, dunya in (("gercek col (BW)", [4, 5], 21.0),
                              ("tundra + buz (E)", [29, 30], 11.6),
                              ("sik orman (Af)", [1], 5.0),
                              ("bozkir (BS)", [6, 7], 12.0)):
        print("  %-22s %7.1f%% %11.1f%%" % (ad, pay(kodlar), dunya))
    for ad, r, dunya in (("A", range(1, 4), 20.6), ("B", range(4, 8), 33.0),
                         ("C", range(8, 17), 11.3), ("D", range(17, 29), 23.6),
                         ("E", range(29, 31), 11.6)):
        print("  ana grup %-13s %7.1f%% %11.1f%%" % (ad, pay(r), dunya))
    print("  kara yagisi %.0f mm/yil (alan agirlikli)"
          % float((yillik_yagis[kara] * alan[kara]).sum() / alan[kara].sum()))


def main():
    ap = argparse.ArgumentParser(description="Dunyam Atlasi veri ureticisi")
    ap.add_argument("--res", type=float, default=0.25, help="derece/hucre (varsayilan 0.25)")
    ap.add_argument("--cikti", default=CIKTI, help="atlas.json yolu ya da klasor (dokular yanina yazilir)")
    ap.add_argument("--ozet", action="store_true", help="sinif paylarini da yaz")
    ap.add_argument("--zorla", action="store_true",
                    help="ic tutarlilik dusse de veriyi yine de yaz")
    a = ap.parse_args()
    # klasor verilirse icine atlas.json (once dosya yolu bekleniyordu ve
    # hesap bittikten sonra yazarken IsADirectoryError ile dusuyordu)
    if os.path.isdir(a.cikti):
        a.cikti = os.path.join(a.cikti, "atlas.json")

    t0 = time.time()
    w = dunya_yukle()
    g = grid_kur(w, a.res)
    print("%s: %dx%d hucre, kara %%%.0f, hucre %.3f derece"
          % (w.name, g.shape[1], g.shape[0], 100 * g.land.mean(),
             (g.bounds[2] - g.bounds[0]) / g.shape[1]))
    r = model.run(g)
    K, T, P = r["koppen"], r["temp"], r["precip"]

    rapor = sanity.check(g, r)
    dusen = [(ad, aciklama) for ad, ok, aciklama in rapor if not ok]
    print("ic tutarlilik: %d/%d gecti" % (len(rapor) - len(dusen), len(rapor)))
    for ad, aciklama in dusen:
        print("   DUSTU: %s — %s" % (ad, aciklama))
    # Dusen bir kontrol neredeyse her zaman BOZUK GIRDI demek (ters cevrilmis
    # yukseklik haritasi, yanlis deniz seviyesi degeri, sacma bir parametre).
    # GitHub Actions bunu yalnizca yazdirsaydi bozuk dunyayi sessizce commit
    # eder, telefonda ancak gozle fark edilirdi. O yuzden hata veriyoruz.
    if dusen and not a.zorla:
        raise SystemExit(
            "%d ic tutarlilik kontrolu dustu, veri YAZILMADI. Once girdiyi "
            "kontrol et (yukseklik haritasi, sea_level_value, params). "
            "Yine de yazmak icin: --zorla" % len(dusen))

    os.makedirs(os.path.dirname(os.path.abspath(a.cikti)), exist_ok=True)
    land = g.land
    alanlar = {}
    # TAM kara araligi kodlanir. Onceden %1-%99 yuzdelikleri kullaniliyordu ve
    # karanin ~%2'si sinira kirpiliyordu: hucre karti Temmuz'un en soguk
    # hucresini -24.7 yerine -3.1 C, en yagisli hucreyi 2221 yerine 758 mm
    # gosteriyordu (olculdu). Renk dagilimi uygulamada yuzdelik esitlemeyle
    # kuruldugu icin uc degerler rengi bozmaz.
    # Ocak/Temmuz ayri alan olarak TASINMAZ: 12 ayin tamami asagida "aylik"
    # blokta, yalniz kara hucreleri icin paketli geliyor.
    for ad, mo in (("temp_yil", T.mean(0)), ("prec_yil", P.sum(0))):
        v = mo[land]
        lo, hi = float(np.floor(v.min() * 10) / 10), float(np.ceil(v.max() * 10) / 10)
        olcek = "kok" if ad.startswith("prec") else "lin"
        alanlar[ad] = {"lo": lo, "hi": hi, "olcek": olcek,
                       "model": kodla(mo, lo, hi, olcek), "obs": None}
    alanlar["koppen"] = {"model": base64.b64encode(K.astype(np.uint8).tobytes()).decode(),
                         "obs": None}
    # Alt sinir karanin EN DUSUK noktasi: kapali havza deniz seviyesinin
    # altinda (-673 m); 0'dan kodlanirken hucre kartinda 0 m gorunuyordu.
    e = g.elev.copy()
    e[~land] = np.nan
    ust = float(np.nanmax(e)) if np.isfinite(e).any() else 1.0
    alt = min(0.0, float(np.floor(np.nanmin(e)))) if np.isfinite(e).any() else 0.0
    bolge = {
        "title": "global", "why": w.name, "w": g.shape[1], "h": g.shape[0],
        "bounds": [round(x, 3) for x in g.bounds],
        "land": base64.b64encode(np.packbits(land).tobytes()).decode(),
        "elev": {"lo": alt, "hi": ust, "data": kodla(np.nan_to_num(e, nan=alt), alt, ust)},
        "fields": alanlar, "stats": None,
        "sanity": [{"ad": turkce(ad), "gecti": bool(ok), "aciklama": turkce(d)} for ad, ok, d in rapor],
    }
    bolge, ham, (y0, y1, x0, x1) = kirp(bolge)
    print("kirpildi: %dx%d -> %dx%d" % (ham[0], ham[1], bolge["w"], bolge["h"]))

    # 12 AYLIK sicaklik ve yagis, yalniz KARA hucreleri, satir sirasiyla
    # (kirpilmis gridde land bitlerinin sirasi). Klimagram ve ay kaydiricisi
    # icin. Tam grid 24 x 209 bin bayt (6.7 MB base64) olurdu; kara ~%24'u.
    kl = land[y0:y1, x0:x1]
    Tk = T[:, y0:y1, x0:x1][:, kl]
    Pk = P[:, y0:y1, x0:x1][:, kl]
    tlo, thi = float(np.floor(Tk.min() * 10) / 10), float(np.ceil(Tk.max() * 10) / 10)
    phi = float(np.ceil(Pk.max() * 10) / 10)
    bolge["aylik"] = {
        "n": int(kl.sum()),
        "T": {"lo": tlo, "hi": thi, "olcek": "lin", "data": kodla(Tk, tlo, thi)},
        "P": {"lo": 0.0, "hi": phi, "olcek": "kok", "data": kodla(Pk, 0.0, phi, "kok")},
    }
    # doku cozunurlugu veri cozunurlugunden bagimsiz ~0.066 derece: kaba
    # denemede (--res 1.0) de harita kiyisi ayni incelikte cizilir
    hucre = (g.bounds[2] - g.bounds[0]) / g.shape[1]
    dokubilgi = doku.uret(w, bolge, K[y0:y1, x0:x1], (y0, y1, x0, x1),
                          os.path.dirname(os.path.abspath(a.cikti)),
                          olcek=max(1, int(round(hucre / 0.066))))
    if dokubilgi["kabartma_ortusme"] is not None and dokubilgi["kabartma_ortusme"] < 0.95:
        print("UYARI: kabartma gorseli karaya %.1f%% oturuyor (<%%95). Arazi degistiyse "
              "editor gorselini yeniden al: python kabartma_kaydet.py <gorsel>"
              % (100 * dokubilgi["kabartma_ortusme"]))
    print("dokular: %dx%d, kabartma kaynagi %s, ortusme %s"
          % (dokubilgi["w"], dokubilgi["h"], dokubilgi["kabartma"], dokubilgi["kabartma_ortusme"]))
    bolge["doku"] = dokubilgi
    bolge["dolasim"], bolge["akintilar"] = dolasim(r, g, w, (y0, y1, x0, x1),
                                                   os.path.dirname(os.path.abspath(a.cikti)))

    veri = {"world": w.name, "fictional": True, "regions": {"global": bolge},
            "koppen_colors": {v[0]: "#%02x%02x%02x" % v[1] for v in LEG.values()},
            "koppen_names": {v[0]: v[2] for v in LEG.values()},
            "koppen_code": {str(k): v[0] for k, v in LEG.items()}}
    facts = kunye(w, g, P.sum(0))

    govde = json.dumps(veri, separators=(",", ":"))
    ozet_h = hashlib.sha1((govde + json.dumps(facts, ensure_ascii=False)).encode("utf-8"))
    # dokular JSON'da degil ayri dosyada; icerikleri de surume girer, yoksa
    # yalniz kabartma degistiginde is akisi "ayni" deyip commit etmezdi
    for ad in ("doku.png", "yukseklik.png", "kabartma.jpg", "kabartma_gri.jpg", "kabartma_bir.jpg", "dolasim.png"):
        with open(os.path.join(os.path.dirname(os.path.abspath(a.cikti)), ad), "rb") as fh:
            ozet_h.update(fh.read())
    surum = ozet_h.hexdigest()[:10]
    with open(a.cikti, "w", encoding="utf-8") as fh:
        fh.write('{"surum":%s,"uretim":%s,"facts":%s,"data":%s}'
                 % (json.dumps(surum), json.dumps(time.strftime("%Y-%m-%d %H:%M")),
                    json.dumps(facts, ensure_ascii=False), govde))
    print("-> %s  surum %s  %.2f MB  (%.0f sn)"
          % (a.cikti, surum, os.path.getsize(a.cikti) / 1e6, time.time() - t0))
    print("kunye: " + ", ".join("%s %s" % (x, y) for x, y in facts))
    if a.ozet:
        ozet_yaz(g, K, P.sum(0))


if __name__ == "__main__":
    main()
