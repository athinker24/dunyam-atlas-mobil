"""Seçenekleri yan yana Köppen haritası olarak çizer (Beck paleti, uret.LEG)."""
import sys, os, json, numpy as np
K = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, K)
from PIL import Image, ImageDraw, ImageFont
import uret
S = os.path.dirname(os.path.abspath(__file__))
sec = [s.split("|") for s in sys.argv[1:]]          # ad|başlık
sonuc = {}
for f in ("sonuc.jsonl",):
    p = os.path.join(S, f)
    if os.path.exists(p):
        for l in open(p):
            if l.startswith("{"):
                j = json.loads(l); sonuc[j["ad"]] = j
w = uret.dunya_yukle(); g = uret.grid_kur(w, float(sys.argv[1].split("|")[0].rsplit("_", 1)[1]))
land = g.land.astype(bool); lat = np.asarray(g.lat); lon = np.asarray(g.lon)
ii, jj = np.where(land); i0, i1, j0, j1 = ii.min() - 2, ii.max() + 3, jj.min() - 2, jj.max() + 3
pal = np.zeros((256, 3), np.uint8); pal[:] = (14, 22, 30)
for k, (ad, rgb, _) in uret.LEG.items(): pal[k] = rgb
F = 3 if "0.5" in sys.argv[1] else 2
try:
    fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20); f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
except Exception:
    fb = f = ImageFont.load_default()
pan = []
for ad, bas in sec:
    Kp = np.load(os.path.join(S, "k_%s.npz" % ad))["K"]
    a = pal[np.where(land, Kp, 0)][i0:i1, j0:j1]
    im = Image.fromarray(a).resize(((j1 - j0) * F, (i1 - i0) * F), Image.NEAREST)
    d = ImageDraw.Draw(im)
    # bölge elipsi
    cy = (lat[i0] - 43) / abs(lat[1] - lat[0]) * F; cx = (11.5 - lon[j0]) / abs(lon[1] - lon[0]) * F
    ry = 6 / abs(lat[1] - lat[0]) * F; rx = 17 / abs(lon[1] - lon[0]) * F
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=(255, 255, 255), width=2)
    s = sonuc.get(ad.rsplit("_", 1)[0], {})
    alt = Image.new("RGB", (im.width, 92), (8, 12, 16)); da = ImageDraw.Draw(alt)
    da.text((8, 6), bas, fill=(210, 164, 92), font=fb)
    if s:
        da.text((8, 36), "bölge: yağış %d mm, bozkır %%%d" % (s["bolge_yagis"], round(s["bolge_BS"])), fill=(230, 230, 220), font=f)
        da.text((8, 60), ("bölge dışı sınıf değişen %%%d · kurak B %%%.1f · Akdeniz %%%d" % (round(s.get("bolge_disi_degisen", 0)), s["grup"]["B"], round(s["Cs"]))), fill=(170, 175, 170), font=f)
    p = Image.new("RGB", (im.width, im.height + 92)); p.paste(alt, (0, 0)); p.paste(im, (0, 92)); pan.append(p)
kol = 3; W_ = pan[0].width; H_ = pan[0].height; sat = (len(pan) + kol - 1) // kol
c = Image.new("RGB", (kol * W_ + (kol - 1) * 10, sat * H_ + (sat - 1) * 10 + 44), (0, 0, 0)); dc = ImageDraw.Draw(c)
for k, p in enumerate(pan): c.paste(p, ((k % kol) * (W_ + 10), 44 + (k // kol) * (H_ + 10)))
lx = 8
for k in (7, 6, 21, 22, 25, 26, 3, 8, 11):
    ad, rgb, _ = uret.LEG[k]; dc.rectangle([lx, 12, lx + 18, 30], fill=rgb); dc.text((lx + 24, 12), ad, fill=(220, 220, 210), font=f); lx += 90
c.save(os.path.join(S, os.environ.get("CIKTI", "deney_1.png"))); print(c.size)
