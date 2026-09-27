"""izler.json + _izler.npz -> buzul_haritasi.png (kıta) ve buzul_kuzey.png (yakın)."""
import json, os
import numpy as np
from PIL import Image, ImageDraw
from ciz import golge, font
BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURASI)

def ciz(d, oz, kutu, olcek, ad, baslik):
    z, lat, lon = d["z"], d["lat"], d["lon"]
    dy = 6371e3 * np.radians(abs(lat[1] - lat[0]))
    dx = (6371e3 * np.radians(lon[1] - lon[0]) * np.cos(np.radians(lat)))[:, None]
    h = golge(z, dx, dy)
    bugun_kara = z - 120 >= 0; lgm_kara = z >= 0
    t = np.clip((z - 120) / 5000, 0, 1)[..., None]
    arazi = (np.array([112, 118, 92]) * (1 - t) + np.array([170, 150, 120]) * t) / 255 * (0.45 + 0.75 * h[..., None])
    img = np.where(bugun_kara[..., None], arazi, np.array([22, 34, 48]) / 255)
    sah = lgm_kara & ~bugun_kara
    img[sah] = np.array([40, 58, 70]) / 255
    lg = d["ortu"] & ~d["bugun"]
    img[lg] = img[lg] * 0.35 + np.array([150, 200, 235]) / 255 * 0.65 * (0.75 + 0.3 * h[lg])[:, None]
    img[d["bugun"]] = np.array([245, 250, 255]) / 255 * (0.75 + 0.3 * h[d["bugun"]])[:, None]
    n, s, w, e = kutu
    r0, r1 = int((lat[0] - n) / (lat[0] - lat[1])), int((lat[0] - s) / (lat[0] - lat[1]))
    c0, c1 = int((w - lon[0]) / (lon[1] - lon[0])), int((e - lon[0]) / (lon[1] - lon[0]))
    im = Image.fromarray((np.clip(img[r0:r1, c0:c1], 0, 1) * 255).astype(np.uint8))
    im = im.resize((im.width * olcek, im.height * olcek), Image.LANCZOS)
    dr = ImageDraw.Draw(im)
    def xy(la, lo):
        return ((lo - lon[0]) / (lon[1] - lon[0]) - c0 + 0.5) * olcek, ((lat[0] - la) / (lat[0] - lat[1]) - r0 + 0.5) * olcek
    # sirkler
    for i, j in zip(*np.where(d["sirk"][r0:r1, c0:c1])):
        x, y = (j + 0.5) * olcek, (i + 0.5) * olcek
        dr.point((x, y), fill=(60, 60, 80))
    # buzul dilleri / cephe morenleri
    for i, j in zip(*np.where(d["buyuk_dil"][r0:r1, c0:c1] & (d["z"][r0:r1, c0:c1] - 120 >= 0))):
        x, y = (j + 0.5) * olcek, (i + 0.5) * olcek
        dr.ellipse((x - 2.5, y - 2.5, x + 2.5, y + 2.5), fill=(190, 110, 50), outline=(40, 20, 10))
    fk = font(12 if olcek < 2 else 15)
    for g in oz["goller"]:
        if g["boy"] == "küçük":
            continue
        x, y = xy(*g["enlem_boylam"])
        rr = {"büyük": 6, "orta": 4, "küçük": 2.5}[g["boy"]] * (1 if olcek < 2 else 1.4)
        dr.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(60, 150, 230), outline=(10, 20, 40))
        if g["boy"] == "büyük":
            dr.text((x + rr + 2, y - 7), "G%d" % g["no"], fill=(170, 215, 255), font=fk, stroke_width=2, stroke_fill=(0, 0, 0))
    for f in oz["fiyortlar"]:
        x, y = xy(*f["enlem_boylam"])
        dr.polygon([(x, y - 7), (x - 6, y + 5), (x + 6, y + 5)], fill=(40, 230, 220), outline=(0, 0, 0))
        dr.text((x + 7, y - 4), "F%d" % f["no"], fill=(140, 255, 245), font=fk, stroke_width=2, stroke_fill=(0, 0, 0))
    dag = json.load(open(os.path.join(KOK, "tektonik", "ozet.json"), encoding="utf-8"))["dag_ve_yer_sekilleri"]
    fd = font(18 if olcek < 2 else 22)
    for m in dag:
        x, y = xy(*m["enlem_boylam"])
        if 0 <= x < im.width and 0 <= y < im.height:
            dr.text((x - 6, y - 10), m["no"], fill=(255, 210, 90), font=fd, stroke_width=3, stroke_fill=(0, 0, 0))
    # açıklama haritanın altında ayrı şeritte
    fa = font(16)
    kalem = (((245, 250, 255), "bugünkü buzul"), ((150, 200, 235), "buzul çağı doruğunda buz"),
             ((40, 58, 70), "o zaman kara olan sahanlık (deniz −120 m)"),
             ((190, 110, 50), "büyük buzulun dili: cephe moreni"), ((60, 150, 230), "moren seti gölü adayı (G: büyük, adsız: orta)"),
             ((40, 230, 220), "fiyort (F)"), ((60, 60, 80), "sirk (koyu nokta)"))
    ser = Image.new("RGB", (im.width, 44 + 24 * ((len(kalem) + 1) // 2)), (14, 16, 20))
    ds = ImageDraw.Draw(ser)
    ds.text((12, 8), baslik, fill=(255, 255, 255), font=font(20))
    for k, (renk, yazi) in enumerate(kalem):
        x0, y0 = 12 + (k % 2) * (im.width // 2), 40 + (k // 2) * 24
        ds.rectangle((x0, y0 + 2, x0 + 16, y0 + 16), fill=renk, outline=(90, 90, 90))
        ds.text((x0 + 24, y0), yazi, fill=(225, 225, 225), font=fa)
    tam = Image.new("RGB", (im.width, im.height + ser.height)); tam.paste(im, (0, 0)); tam.paste(ser, (0, im.height))
    im = tam
    im.save(os.path.join(BURASI, ad)); print(ad, im.size)

if __name__ == "__main__":
    d = dict(np.load(os.path.join(BURASI, "_izler.npz")))
    oz = json.load(open(os.path.join(BURASI, "izler.json"), encoding="utf-8"))
    ciz(d, oz, (61.5, -8.5, -46, 45), 1, "buzul_haritasi.png", "Buzul çağı doruğu: −6 °C, eğiklik 22°")
    ciz(d, oz, (61.5, 26, -18, 42), 2, "buzul_kuzey.png", "Kuzey: Duvar, 1, 2, 3, 9, plato")
