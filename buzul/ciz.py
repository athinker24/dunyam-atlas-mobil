"""Buzul senaryolarını yan yana çizer (kıta ayrıntısı, dağ numaralı)."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURASI)

def font(n):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        if os.path.exists(f): return ImageFont.truetype(f, n)
    return ImageFont.load_default()

def golge(z, dx, dy):
    zz = np.maximum(z, 0)
    gy, gx = np.gradient(zz, dy, axis=0), np.gradient(zz, axis=1) / dx
    az, al = np.radians(315), np.radians(40)
    sl = np.arctan(np.hypot(gx, gy) * 2.0); asp = np.arctan2(-gx, gy)
    return np.clip(np.sin(al) * np.cos(sl) + np.cos(al) * np.sin(sl) * np.cos(az - asp), 0, 1)

def panel(d, baslik, kirp, kopya_bugun=None):
    z, lat, lon = d["z"], d["lat"], d["lon"]
    dy = 6371e3 * np.radians(abs(lat[1] - lat[0]))
    dx = (6371e3 * np.radians(lon[1] - lon[0]) * np.cos(np.radians(lat)))[:, None]
    h = golge(z, dx, dy)
    kara = z >= 0
    img = np.zeros(z.shape + (3,))
    deniz = np.array([22, 34, 48]) / 255
    t = np.clip(z / 5000, 0, 1)[..., None]
    arazi = (np.array([112, 118, 92]) / 255 * (1 - t) + np.array([170, 150, 120]) / 255 * t)
    arazi = arazi * (0.45 + 0.75 * h[..., None])
    img = np.where(kara[..., None], arazi, deniz)
    if kopya_bugun is not None:   # bugünkü kıyı, kalkık sahanlık farklı tonla
        sah = kara & (kopya_bugun < 0)
        img[sah] = img[sah] * 0.6 + np.array([90, 110, 110]) / 255 * 0.4
    o = d["ortu"]
    buz = np.array([235, 244, 255]) / 255 * (0.7 + 0.35 * h[..., None])
    img = np.where(o[..., None], buz, img)
    r0, r1, c0, c1 = kirp
    im = Image.fromarray((np.clip(img[r0:r1, c0:c1], 0, 1) * 255).astype(np.uint8))
    return im

if __name__ == "__main__":
    ad = sys.argv[1:] or ["bugun", "4", "6", "8"]
    etiket = {"bugun": "bugün", "4": "−4 °C", "6": "−6 °C", "8": "−8 °C", "6e22": "−6 °C, eğiklik 22°"}
    dd = {a: dict(np.load(os.path.join(BURASI, "_akis_%s.npz" % a))) for a in ad}
    z0 = dd["bugun"]["z"]
    lat, lon = dd["bugun"]["lat"], dd["bugun"]["lon"]
    kara = z0 >= -130
    r, c = np.where(kara)
    kirp = (max(r.min() - 8, 0), r.max() + 8, max(c.min() - 8, 0), c.max() + 8)
    dag = json.load(open(os.path.join(KOK, "tektonik", "ozet.json"), encoding="utf-8"))["dag_ve_yer_sekilleri"]
    pan = []
    for a in ad:
        d = dd[a]
        im = panel(d, a, kirp, None if a == "bugun" else z0)
        dr = ImageDraw.Draw(im); f = font(22); fk = font(15)
        dy_ = lat[0] - lat[1]; dx_ = lon[1] - lon[0]
        for m in dag:
            la, lo = m["enlem_boylam"]
            y = (lat[0] - la) / dy_ - kirp[0]; x = (lo - lon[0]) / dx_ - kirp[2]
            dr.text((x + 6, y - 8), m["no"], fill=(255, 210, 90), font=fk, stroke_width=2, stroke_fill=(0, 0, 0))
        w = np.cos(np.radians(lat))[:, None] * np.ones_like(d["z"])
        alan = (w * d["ortu"]).sum() / (w * (d["z"] >= 0)).sum() * 100
        dr.text((12, 10), "%s   buz: karanın %%%.1f" % (etiket[a], alan), fill=(255, 255, 255), font=f,
                stroke_width=2, stroke_fill=(0, 0, 0))
        pan.append(im)
    W, H = pan[0].size
    kol = 2 if len(pan) > 1 else 1; sat = (len(pan) + kol - 1) // kol
    out = Image.new("RGB", (W * kol + 6 * (kol - 1), H * sat + 6 * (sat - 1)), (10, 10, 12))
    for i, im in enumerate(pan):
        out.paste(im, ((i % kol) * (W + 6), (i // kol) * (H + 6)))
    out.save(os.path.join(BURASI, os.environ.get("CIKTI", "senaryolar.png")))
    print(out.size)
