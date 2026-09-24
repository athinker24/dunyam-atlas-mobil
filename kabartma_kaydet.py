# -*- coding: utf-8 -*-
"""Sahibin editor goruntusunu kabartma kaynagi olarak kaydeder.

    python kabartma_kaydet.py /yol/editor_goruntusu.png

Uygulamadaki kabartma golgesi, dunyanin sahibinin MerakMapMaker'dan aldigi
renkli gorselden cikarilir (tonu ayrilinca geriye yalnizca golge kalir).
Bu betik gorseli repoya alir ve yukseklik haritasi tuvaline OTURTUR:

  1. Gorsel en uzun kenari 2400 px olacak sekilde kucultulup
     dunya/kabartma_kaynak.jpg olarak yazilir (4428 px'lik PNG 28 MB idi;
     2400 px hala atlas hucresinden ~6 kat ince).
  2. Gorseldeki kara (mavi olmayan) ile tuvaldeki kara maskesi arasindaki
     ortusme (IoU) en buyuk olacak izotropik olcek + kayma aranir.
  3. Sonuc dunya/dunyam.json -> heightmap.kabartma altina yazilir; uret.py
     dokulari uretirken bunu kullanir.

ARAZI DEGISINCE bu gorsel de editorden yeniden alinmali ve bu betik yeniden
kosulmali; yoksa golge eski daglari gosterir. uret.py her kosuda ortusmeyi
olcer ve %95'in altindaysa uyarir.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage, optimize

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)
from motor import grid as G  # noqa: E402

DUNYA_JSON = os.path.join(BURASI, "dunya", "dunyam.json")
HEDEF = os.path.join(BURASI, "dunya", "kabartma_kaynak.jpg")
EN_UZUN = 2400


def gorsel_kara(rgb: np.ndarray) -> np.ndarray:
    """Editor gorselinde deniz mavi baskin; kara geri kalan."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    deniz = (b > r + 15) & (b > g - 5)
    return ndimage.binary_opening(~deniz, iterations=2)


def tuval_kara(hm: dict) -> np.ndarray:
    with Image.open(os.path.join(BURASI, "dunya", "dunyam_heightmap.png")) as im:
        can = np.asarray(im).astype(np.float64)
    return G.land_mask(can, float(hm["sea_level_value"]), wraps=True)


def ortusme(kara_img, tuval, p, pencere):
    sx, sy, ox, oy = p
    r0, r1, c0, c1 = pencere
    rr, cc = np.mgrid[r0:r1, c0:c1].astype(np.float64)
    m = ndimage.map_coordinates(kara_img.astype(np.float32), [(rr - oy) / sy, (cc - ox) / sx],
                                order=1, cval=0.0) > 0.5
    t = tuval[r0:r1, c0:c1]
    return float((m & t).sum() / max((m | t).sum(), 1))


def kaydet(kaynak: str) -> dict:
    with Image.open(kaynak) as im:
        im = im.convert("RGB")
        k = EN_UZUN / max(im.size)
        if k < 1:
            im = im.resize((round(im.size[0] * k), round(im.size[1] * k)), Image.LANCZOS)
        im.save(HEDEF, quality=92)
        rgb = np.asarray(im).astype(np.float64)

    with open(DUNYA_JSON, encoding="utf-8") as fh:
        metin = fh.read()
    d = json.loads(metin)
    tuval = tuval_kara(d["heightmap"])
    kara = gorsel_kara(rgb)

    ys, xs = np.where(kara)
    tr, tc = np.where(tuval.any(1))[0], np.where(tuval.any(0))[0]
    # tuvalde karanin kutusu (dikis yok: kita ortada)
    pencere = (max(tr.min() - 40, 0), tr.max() + 40, max(tc.min() - 40, 0), tc.max() + 40)
    sy = (tr.max() - tr.min()) / (ys.max() - ys.min())
    sx = (tc.max() - tc.min()) / (xs.max() - xs.min())
    p0 = (sx, sy, tc.min() - xs.min() * sx, tr.min() - ys.min() * sy)
    o = optimize.minimize(lambda p: -ortusme(kara, tuval, p, pencere), p0, method="Nelder-Mead",
                          options=dict(xatol=1e-4, fatol=1e-6, maxiter=400))
    sx, sy, ox, oy = (float(v) for v in o.x)
    sonuc = {"file": "dunya/kabartma_kaynak.jpg", "sx": round(sx, 6), "sy": round(sy, 6),
             "ox": round(ox, 3), "oy": round(oy, 3), "iou": round(-float(o.fun), 4),
             "_not": ("Tuval pikseli (satir, sutun) -> gorsel pikseli: ((satir-oy)/sy, "
                      "(sutun-ox)/sx). kabartma_kaydet.py yazar; elle degistirme.")}
    d["heightmap"]["kabartma"] = sonuc
    with open(DUNYA_JSON, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(d, indent=2, ensure_ascii=False) + ("\n" if metin.endswith("\n") else ""))
    return sonuc


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    s = kaydet(sys.argv[1])
    print("kaydedildi: olcek %.4f/%.4f kayma %.1f/%.1f ortusme %.4f -> %s"
          % (s["sx"], s["sy"], s["ox"], s["oy"], s["iou"], HEDEF))
