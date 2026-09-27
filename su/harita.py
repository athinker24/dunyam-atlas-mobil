"""Göl + nehir seçeneklerini yan yana çizer. python su/harita.py 0 50 150 300"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw
BURASI = os.path.dirname(os.path.abspath(__file__)); KOK = os.path.dirname(BURASI)
sys.path.insert(0, BURASI); sys.path.insert(0, os.path.join(KOK, "buzul"))
import gol, nehir
from ciz import golge, font

k = np.load(os.path.join(BURASI, "_akim.npz"))
z, lat, lon = k["z"].astype(np.float64), k["lat"], k["lon"]
dy = 6371e3 * np.radians(abs(lat[1] - lat[0]))
dx = (6371e3 * np.radians(lon[1] - lon[0]) * np.cos(np.radians(lat)))[:, None]
alan = dx * dy * np.ones_like(z)
deniz = z < 0
kara = ~deniz
h = golge(z, dx, dy)
wk = alan[kara].sum()


def cozum(asinma):
    seviye, goller, A = gol.coz(z, deniz, k["R"], k["P"], k["Egol"], alan, asinma)
    kapali = np.zeros(z.size, bool)
    for g in goller:
        if not g["cikisli"]:
            kapali[g["hucreler"]] = True
    kapali = kapali.reshape(z.shape)
    alici, sira = nehir.yonlendir(z, deniz, seviye, kapali)
    gol_m = np.isfinite(seviye)
    kaynak = np.where(gol_m, (k["P"] - k["Egol"]), k["R"]) * alan / 1000
    kaynak[deniz] = 0
    q = nehir.debi(alici, sira, kaynak).reshape(z.shape) / nehir.SANIYE_YIL
    return seviye, goller, kapali, q, alici


ESIK_Q = 100.0   # m3/s, haritada nehir sayılan en küçük debi


def panel(asinma, seviye, goller, kapali, q, kutu):
    t = np.clip(z / 5000, 0, 1)[..., None]
    img = (np.array([118, 120, 98]) * (1 - t) + np.array([165, 150, 125]) * t) / 255 * (0.5 + 0.6 * h[..., None])
    img = np.where(deniz[..., None], np.array([20, 32, 46]) / 255, img)
    gm = np.isfinite(seviye)
    img[gm & ~kapali] = np.array([60, 130, 210]) / 255
    img[kapali] = np.array([80, 175, 170]) / 255
    r0, r1, c0, c1 = kutu
    im = Image.fromarray((np.clip(img[r0:r1, c0:c1], 0, 1) * 255).astype(np.uint8))
    S = 2
    im = im.resize((im.width * S, im.height * S), Image.NEAREST)
    dr = ImageDraw.Draw(im)
    # nehirler: debi >= 30 m3/s, kalınlık log
    alici = panel.alici
    ny, nx = z.shape
    for i, j in zip(*np.where((q >= ESIK_Q) & kara & ~gm)):
        if not (r0 <= i < r1 and c0 <= j < c1):
            continue
        r = alici[i * nx + j]
        if r < 0:
            continue
        a, b = divmod(int(r), nx)
        w = int(np.clip(np.log10(q[i, j] / ESIK_Q) * 2.6 + 1, 1, 8))
        dr.line([((j - c0 + .5) * S, (i - r0 + .5) * S), ((b - c0 + .5) * S, (a - r0 + .5) * S)], fill=(95, 170, 240), width=w)
    toplam = sum(g["alan_km2"] for g in goller) * 1e6
    yazi = "eşik aşınması %d m: göller karanın %%%.1f'i, %d göl" % (asinma, 100 * toplam / wk, len(goller))
    dr.text((10, 8), yazi, fill=(255, 255, 255), font=font(24), stroke_width=3, stroke_fill=(0, 0, 0))
    return im


if __name__ == "__main__":
    secenek = [float(a) for a in sys.argv[1:]] or [0, 50, 150, 300]
    r, c = np.where(kara)
    kutu = (r.min() - 6, r.max() + 6, c.min() - 6, c.max() + 6)
    pan = []
    for a in secenek:
        seviye, goller, kapali, q, alici = cozum(a)
        panel.alici = alici
        pan.append(panel(a, seviye, goller, kapali, q, kutu))
        np.savez_compressed(os.path.join(BURASI, "_su_%d.npz" % a), seviye=seviye, kapali=kapali, q=q.astype(np.float32), alici=alici)
        print(a, "bitti", flush=True)
    W, H = pan[0].size
    kol = 2 if len(pan) > 1 else 1; sat = (len(pan) + kol - 1) // kol
    out = Image.new("RGB", (W * kol + 8 * (kol - 1), H * sat + 8 * (sat - 1)), (8, 8, 10))
    for i, im in enumerate(pan):
        out.paste(im, ((i % kol) * (W + 8), (i // kol) * (H + 8)))
    out = out.resize((out.width // 2, out.height // 2), Image.LANCZOS) if out.width > 3000 else out
    out.save(os.path.join(BURASI, "secenekler.png")); print(out.size)
