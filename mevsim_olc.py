"""Yagisin mevsimselligini olcer: mevsim disi yagis isinin olcum tezgahi.

    python mevsim_olc.py                           # 0.5 derece, dunyam.json aynen
    python mevsim_olc.py --p eddy_blend=0.01       # params ustune deneme
    python mevsim_olc.py --res 0.25 --harita m.png --json m.json

Neden var: motorun yagisi Dunya'ya gore ~4 kat fazla mevsimsel (kara min/max
ay orani 0.067, Dunya gozlemi 0.249; motor/moisture.py conv_w_pow notu).
Sonucu iliman kusakta Cf'nin neredeyse yok olmasi (%1.6, Cw %24.4). Bir
duzeltme denemesi yalniz OLCUTU degil, dunyanin sahibinin onceki isteklerini
de (Akdeniz kusagi, plato bozkiri, savan payi) bozabilir; bu betik ikisini
birlikte basar. Butun oranlar alan agirlikli (CLAUDE.md 7.1).

Cozunurluk: plato kis yagisi 1 derecede 5-10 mm/ay, 0.25'te 0-2 mm/ay cikti
(engellenme, CLAUDE.md 7.2). Tarama en az 0.5'te, karar 0.25'te.
Veri YAZMAZ; data/'ya dokunmaz.
"""
import argparse
import json
import sys
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import uret
from motor import koppen, model

# Dunya gozlemi: kara hucrelerinde en kurak ay / en yagisli ay (motor notu)
DUNYA_MINMAX = 0.249
# karsiz kalan plato canagi (kar katmaninda gri oval), derece
PLATO = dict(lat=(43.0, 49.0), lon=(6.0, 18.0))
# Akdeniz istegi "mavi cizgiler arasi" kusakta olculmustu (_akdeniz)
AKDENIZ_BANT = (19.0, 36.0)
KIS_AYLARI_K = [10, 11, 0, 1, 2]    # Kasim..Mart (kuzey yarimkure)
YAZ_AYLARI_K = [4, 5, 6, 7, 8]      # Mayis..Eylul
KUZEY_ALT = 36.0

# Harita: kurak mevsimin tipi. Koppen'in ikinci harfi (f/s/w, A'da f/m/w).
TIP_RENK = {
    "f": (84, 150, 104),    # yil boyu yagisli: Af, Cf, Df
    "w": (70, 118, 178),    # kisi kurak: Aw, Cw, Dw
    "s": (214, 150, 72),    # yazi kurak: Cs, Ds
    "m": (96, 170, 170),    # muson (kisa kurak mevsim): Am
    "B": (150, 138, 118),   # kurak iklim
    "E": (200, 204, 206),   # kutup
}
TIP_AD = {"f": "yıl boyu yağışlı (Cf, Df, Af)", "w": "kışı kurak (Cw, Dw, Aw)",
          "s": "yazı kurak (Cs, Ds)", "m": "muson (Am)", "B": "kurak iklim (B)", "E": "kutup (E)"}
OKYANUS = (14, 22, 28)


def tip(kod: str) -> str:
    if kod[0] in "BE":
        return kod[0]
    return {"f": "f", "s": "s", "w": "w", "m": "m"}[kod[1]]


def olc(g, r):
    lat, lon = np.asarray(g.lat), np.asarray(g.lon)
    LA, LO = np.meshgrid(lat, lon, indexing="ij")
    wt = np.cos(np.radians(LA))
    kara = np.asarray(g.land)
    P, K = r["precip"], r["koppen"]

    def ort(a, m):
        return float((a * wt)[m].sum() / wt[m].sum())

    oran = P.min(0) / np.maximum(P.max(0), 1e-6)
    kodlar = np.vectorize(lambda k: koppen.CODES.get(int(k), "?"))(np.where(kara, K, 1))
    tipler = np.vectorize(tip)(kodlar)

    def pay(m_alt, m_ust=kara):
        return round(100 * ort(m_alt.astype(float), m_ust), 1)

    plato = kara & (LA >= PLATO["lat"][0]) & (LA <= PLATO["lat"][1]) \
        & (LO >= PLATO["lon"][0]) & (LO <= PLATO["lon"][1])
    bant = kara & (LA >= AKDENIZ_BANT[0]) & (LA <= AKDENIZ_BANT[1])
    ilik = kara & np.isin(np.vectorize(lambda s: s[0])(kodlar), ["C"])
    soguk = kara & np.isin(np.vectorize(lambda s: s[0])(kodlar), ["D"])
    k2 = np.vectorize(lambda s: s[:2])(kodlar)
    # asil hedef: 36K kuzeyi (Akdeniz bandinin ve tropiklerin disi)
    kuzey = kara & (LA >= KUZEY_ALT)

    s = {
        "olcut": {
            "kara_minmax_ort": round(ort(oran, kara), 3),
            "dunya_minmax": DUNYA_MINMAX,
            "kara_ay_payi_10mm_alti": round(100 * ort((P < 10).mean(0), kara), 1),
            "kara_yillik_yagis_mm": round(ort(P.sum(0), kara)),
            "C_icinde_f_s_w": [pay(k2 == "Cf", ilik), pay(k2 == "Cs", ilik), pay(k2 == "Cw", ilik)],
            "D_icinde_f_s_w": [pay(k2 == "Df", soguk), pay(k2 == "Ds", soguk), pay(k2 == "Dw", soguk)],
            "kara_tip_payi": {t: pay(tipler == t) for t in TIP_RENK},
        },
        "kuzey36": {
            "minmax_ort": round(ort(oran, kuzey), 3),
            "kis_yagisi_mm": round(sum(ort(P[m], kuzey) for m in KIS_AYLARI_K), 1),
            "yaz_yagisi_mm": round(sum(ort(P[m], kuzey) for m in YAZ_AYLARI_K), 1),
            "C_icinde_f_s_w": [pay(k2 == "Cf", ilik & kuzey), pay(k2 == "Cs", ilik & kuzey), pay(k2 == "Cw", ilik & kuzey)],
            "D_icinde_f_s_w": [pay(k2 == "Df", soguk & kuzey), pay(k2 == "Ds", soguk & kuzey), pay(k2 == "Dw", soguk & kuzey)],
            "tip_payi": {t: pay(tipler == t, kuzey) for t in TIP_RENK},
        },
        "korunan": {
            "Cs_kara": pay(k2 == "Cs"),
            "Cs_akdeniz_bandi": pay(k2 == "Cs", bant),
            "Aw_savan": pay(kodlar == "Aw"),
            "plato_BSk": pay(kodlar == "BSk", plato),
            "plato_BW_col": pay(np.isin(kodlar, ["BWk", "BWh"]), plato),
            "plato_kis_yagisi_mm": round(sum(ort(P[m], plato) for m in KIS_AYLARI_K), 1),
            "plato_yillik_mm": round(ort(P.sum(0), plato)),
        },
        "grup": {gr: pay(np.vectorize(lambda s: s[0])(kodlar) == gr) for gr in "ABCDE"},
    }
    return s, dict(tipler=tipler, oran=oran, kara=kara, lat=lat, lon=lon)


def harita(h, yol, baslik):
    kara, lat, lon = h["kara"], h["lat"], h["lon"]
    ys, xs = np.where(kara)
    pay = int(round(4.0 / abs(lat[0] - lat[1])))
    y0, y1 = max(0, ys.min() - pay), min(kara.shape[0], ys.max() + pay + 1)
    x0, x1 = max(0, xs.min() - pay), min(kara.shape[1], xs.max() + pay + 1)
    k = kara[y0:y1, x0:x1]
    hh, ww = k.shape
    olcek = max(1, int(900 / ww))

    def panel(renk_fn):
        a = np.empty((hh, ww, 3), np.uint8)
        a[:] = OKYANUS
        a[k] = renk_fn(y0, y1, x0, x1)[k]
        im = Image.fromarray(a).resize((ww * olcek, hh * olcek), Image.NEAREST)
        d = ImageDraw.Draw(im)
        dy = abs(lat[0] - lat[1])
        ylat = lambda la: (lat[0] - la) / dy * olcek - y0 * olcek
        xlon = lambda lo: (lo - lon[0]) / dy * olcek - x0 * olcek
        for la in AKDENIZ_BANT:
            d.line([(0, ylat(la)), (im.width, ylat(la))], fill=(120, 170, 230), width=2)
        d.rectangle([xlon(PLATO["lon"][0]), ylat(PLATO["lat"][1]), xlon(PLATO["lon"][1]), ylat(PLATO["lat"][0])],
                    outline=(240, 240, 240), width=2)
        return im

    def tip_renk(a0, a1, b0, b1):
        t = h["tipler"][a0:a1, b0:b1]
        o = np.zeros((*t.shape, 3), np.uint8)
        for kk, rr in TIP_RENK.items():
            o[t == kk] = rr
        return o

    def oran_renk(a0, a1, b0, b1):
        # 0 (koyu kahve) -> Dunya ortalamasi 0.249 (acik) -> 0.5+ (yesil)
        v = np.clip(h["oran"][a0:a1, b0:b1] / 0.5, 0, 1)[..., None]
        a, b, c = np.array([74, 44, 30]), np.array([226, 214, 176]), np.array([60, 140, 90])
        return np.where(v < 0.498, a + (b - a) * (v / 0.498), b + (c - b) * ((v - 0.498) / 0.502)).astype(np.uint8)

    p1, p2 = panel(tip_renk), panel(oran_renk)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    kucuk = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    W = p1.width
    lej1 = 44 + 30 * 3
    lej2 = 110
    out = Image.new("RGB", (W, 50 + p1.height + lej1 + 40 + p2.height + lej2), (11, 17, 22))
    d = ImageDraw.Draw(out)
    bf = font
    while d.textlength(baslik, font=bf) > W - 32 and bf.size > 12:
        bf = ImageFont.truetype(bf.path, bf.size - 1)
    d.text((16, 12), baslik, font=bf, fill=(230, 226, 216))
    y = 50
    out.paste(p1, (0, y)); y += p1.height + 12
    d.text((16, y), "Kurak mevsimin tipi", font=font, fill=(230, 226, 216)); y += 32
    for i, (kk, rr) in enumerate(TIP_RENK.items()):
        cx, cy = 16 + (i % 2) * (W // 2), y + (i // 2) * 30
        d.rectangle([cx, cy + 3, cx + 18, cy + 21], fill=rr)
        d.text((cx + 28, cy), TIP_AD[kk], font=kucuk, fill=(210, 206, 196))
    y += 3 * 30 + 28
    out.paste(p2, (0, y)); y += p2.height + 12
    d.text((16, y), "En kurak ay / en yağışlı ay", font=font, fill=(230, 226, 216)); y += 32
    bw = W - 32
    for i in range(bw):
        v = i / bw
        a, b, cc = np.array([74, 44, 30]), np.array([226, 214, 176]), np.array([60, 140, 90])
        col = a + (b - a) * (v / 0.498) if v < 0.498 else b + (cc - b) * ((v - 0.498) / 0.502)
        d.line([(16 + i, y), (16 + i, y + 14)], fill=tuple(int(x) for x in col))
    for v, t in [(0, "0"), (0.249, "0.25 Dünya"), (0.5, "0.5+")]:
        x = 16 + v / 0.5 * bw
        d.text((min(x, W - 70) - (0 if v == 0 else 30), y + 18), t, font=kucuk, fill=(210, 206, 196))
    d.text((16, out.height - 24), "mavi çizgiler: 19-36°K Akdeniz bandı · beyaz kutu: karsız plato çanağı",
           font=kucuk, fill=(150, 150, 150))
    out.save(yol)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--res", type=float, default=0.5)
    ap.add_argument("--p", action="append", default=[], metavar="AD=DEGER",
                    help="params ustune yazilir (tekrarlanabilir)")
    ap.add_argument("--harita", help="PNG yolu")
    ap.add_argument("--json", help="olcumleri JSON olarak yaz")
    ap.add_argument("--etiket", default="")
    a = ap.parse_args()

    w = uret.dunya_yukle()
    for kv in a.p:
        ad, deger = kv.split("=", 1)
        w.params[ad] = float(deger)
    g = uret.grid_kur(w, a.res)
    t0 = time.time()
    r = model.run(g)
    s, h = olc(g, r)
    s["kosu"] = {"res": a.res, "params": {kv.split("=")[0]: float(kv.split("=")[1]) for kv in a.p},
                 "sure_s": round(time.time() - t0)}
    print(json.dumps(s, ensure_ascii=False, indent=1))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(s, fh, ensure_ascii=False, indent=1)
    if a.harita:
        o = s["olcut"]
        k = s["kuzey36"]
        baslik = "%s%.2f° · min/max %.3f (Dünya %.3f) · 36°K+ kış %.0f mm, f payı C %.0f / D %.0f" % (
            (a.etiket + " · ") if a.etiket else "", a.res, o["kara_minmax_ort"], DUNYA_MINMAX,
            k["kis_yagisi_mm"], k["C_icinde_f_s_w"][0], k["D_icinde_f_s_w"][0])
        harita(h, a.harita, baslik)
        print("harita:", a.harita)


if __name__ == "__main__":
    sys.exit(main())
