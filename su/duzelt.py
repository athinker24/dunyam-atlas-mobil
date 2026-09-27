"""Hidrolojik arazi: fırça izlerini silip suyun göreceği yüzeyi kurar.

Sahibin çizimi 10-30 km ölçeğinde fırça darbeleri taşıyor: dik yamaçlarda
paralel oluklar, ovalarda sığ lekeler. Su bunları izleyince nehirler cetvelle
çizilmiş paralel çizgiler, göller binlerce minik leke oluyordu. Burada:

1. Kara yüksekliği Gauss ile yumuşatılır (sigma 2 hücre ≈ 15-20 km):
   büyük vadiler, havzalar ve eşikler kalır, fırça ölçeği gider. Kıyı
   çizgisi değişmez (kara/deniz maskesi özgün arazinin).
2. Küçük, belirlenimci bir fraktal gürültü eklenir (en çok ±25 m, yamaçta
   eğimle artar): düz yamaçta D8'in paralel ışınları birbirine kavuşup
   ağaç biçimli kollar oluşturur. Tohum sabit, sonuç her koşuda aynı.
3. Buzul gölleri: buzul çağı doruğunda büyük vadi buzullarının dilinin
   arkasında oluk derinleşmesi (overdeepening) oyulur, dilde moren seti
   yükseltilir (buzul/izler.json'daki büyük ve orta adaylar). Garda 346 m,
   Como 410 m derinliğinde; burada taban dilden 250 m aşağıda, oluk boyunca
   buzul akısını geri izleyerek 4-7 hücre (40-70 km).
"""
import json, os, sys
import numpy as np
from scipy import ndimage
BURASI = os.path.dirname(os.path.abspath(__file__)); KOK = os.path.dirname(BURASI)
sys.path.insert(0, os.path.join(KOK, "buzul"))

SIGMA = 2.0
GURULTU_M = 25.0
TOHUM = 1492
OYUK_M, MOREN_M = 250.0, 40.0


def gurultu(shape, tohum=TOHUM):
    rng = np.random.default_rng(tohum)
    out = np.zeros(shape)
    for oktav, genlik in ((24, 1.0), (12, 0.5), (6, 0.25), (3, 0.125)):
        k = rng.standard_normal((shape[0] // oktav + 2, shape[1] // oktav + 2))
        out += genlik * ndimage.zoom(k, oktav, order=3)[:shape[0], :shape[1]]
    return out / np.abs(out).max()


def yumusat(z):
    kara = z >= 0
    # denizi kıyıdaki kara yüksekliğiyle doldurup yumuşat: kıyı dibe çekilmesin
    ic = np.where(kara, z, np.nan)
    idx = ndimage.distance_transform_edt(~kara, return_distances=False, return_indices=True)
    dolgu = z[tuple(idx)]
    ys = ndimage.gaussian_filter(np.where(kara, z, dolgu), SIGMA)
    egim = np.hypot(*np.gradient(ys)) / 100.0            # ~ m/m, hücre ~10 km
    g = gurultu(z.shape) * GURULTU_M * (0.4 + np.clip(egim * 20, 0, 1.6))
    zr = np.where(kara, np.maximum(ys + g, 0.5), z)
    return zr


def buzul_golleri(zr, lat, lon):
    """Moren seti gölü adaylarını oyar. Döner: oyulmuş arazi, göl kimlikleri."""
    import izler
    oz = json.load(open(os.path.join(KOK, "buzul", "izler.json"), encoding="utf-8"))
    L = izler.kos("6e22", izler.DENIZ_DUSUS)
    ii, jj, Q, ortu = L["ii"], L["jj"], L["Q"], L["ortu"]
    ny, nx = zr.shape
    # akış geri izleme: her hücreye akan komşular içinde en büyük akılı
    gelen_en = np.full(ny * nx, -1, dtype=np.int64); gelen_q = np.zeros(ny * nx)
    hedef = (ii * nx + jj).ravel(); qf = Q.ravel(); of = ortu.ravel()
    for c in np.where(of)[0]:
        h = hedef[c]
        if h != c and qf[c] > gelen_q[h]:
            gelen_q[h] = qf[c]; gelen_en[h] = c
    z2 = zr.copy().ravel(); kim = np.zeros(ny * nx, dtype=np.int32)
    for g in oz["goller"]:
        if g["boy"] == "küçük":
            continue
        la, lo = g["enlem_boylam"]
        i = int(np.argmin(np.abs(lat - la))); j = int(np.argmin(np.abs(lon - lo)))
        c = i * nx + j
        dil_z = z2[c]
        uz = 7 if g["boy"] == "büyük" else 4
        yol = []
        k = gelen_en[c]
        while k >= 0 and len(yol) < uz:
            yol.append(k); k = gelen_en[k]
        if len(yol) < 2:
            continue
        for s, k in enumerate(yol):
            # oluk tabanı: dile yakın en derin, yukarı doğru sığlaşır
            d = OYUK_M * (1 - s / (len(yol) + 1)) ** 0.5
            z2[k] = min(z2[k], dil_z - d)
            kim[k] = g["no"]
        z2[c] = max(z2[c], dil_z + MOREN_M)
    return z2.reshape(ny, nx), kim.reshape(ny, nx)
