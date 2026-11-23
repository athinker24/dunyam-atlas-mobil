"""Bölgeyi bozkır yapacak düğme taraması. python tara.py ad '{"param": deger}' [res]"""
import sys, os, json, time
import numpy as np
K = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, K); os.chdir(K)
import uret
from motor import model, koppen
ad, ek = sys.argv[1], json.loads(sys.argv[2]); res = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
ozel = {k: ek.pop(k) for k in list(ek) if k in ("bolge_recycle", "sirt_m", "trop_taban_m", "akinti")}
w = uret.dunya_yukle()
import dataclasses as _dc
gz = {k: ek.pop(k) for k in list(ek) if k in [f.name for f in _dc.fields(w)]}
if gz: w = _dc.replace(w, **gz)
ozel.update(gz)
w.params.update(ek)
if "akinti" in ozel:
    # {"ad oneki": {"anomaly_c": x, "width_km": y, "olcek": k}}: akinti dosyasinin gecici kopyasi
    _c = json.load(open(os.path.join(K, "dunya", "dunyam.currents.json"), encoding="utf-8"))
    for _a in _c["currents"]:
        for _on, _d in ozel["akinti"].items():
            if _a["name"].startswith(_on):
                for _k, _v in _d.items():
                    if _k == "olcek": _a["anomaly_c"] = [x * _v for x in _a["anomaly_c"]] if isinstance(_a["anomaly_c"], list) else _a["anomaly_c"] * _v
                    else: _a[_k] = _v
    _yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), "akinti_%s.json" % ad)
    json.dump(_c, open(_yol, "w"), ensure_ascii=False)
    w = _dc.replace(w, currents_file=_yol)
assert not uret.bilinmeyen_params(w.params)
g = uret.grid_kur(w, res)
LA2, LO2 = np.asarray(g.lat)[:, None], np.asarray(g.lon)[None, :]
if "bolge_recycle" in ozel:
    # bölge elipsi (merkez 43K 11.5D, yarı eksen 6° x 17°), kenar 0.3 içinde yumuşak
    e = np.sqrt(((LA2 - 43) / 6.0) ** 2 + ((LO2 - 11.5) / 17.0) ** 2)
    mask = np.clip((1.3 - e) / 0.3, 0, 1)
    lr0 = w.params.get("land_recycle", 0.65)
    w.params["land_recycle"] = (lr0 - (lr0 - ozel["bolge_recycle"]) * mask).astype(np.float32)
if "sirt_m" in ozel:
    # batı kenarında K-G sırt: boylam -6..-2, enlem 36..51, kosinüs profilli
    prof = np.clip(1 - np.abs(LO2 + 4) / 2.0, 0, 1) * ((LA2 >= 36) & (LA2 <= 51))
    import dataclasses
    g = dataclasses.replace(g, elev=np.where(g.land, np.maximum(g.elev, ozel["sirt_m"] * np.sin(np.pi / 2 * prof)), g.elev))
if "trop_taban_m" in ozel:
    import dataclasses
    bant = np.clip(1 - np.abs(LA2 - 5) / 15.0, 0, 1)
    g = dataclasses.replace(g, elev=np.where(g.land, np.maximum(g.elev, ozel["trop_taban_m"] * np.minimum(1, 2 * bant)), g.elev))
t0 = time.time(); r = model.run(g)
T, P, Kp = r["temp"], r["precip"], r["koppen"]; land = g.land.astype(bool); lat = np.asarray(g.lat); lon = np.asarray(g.lon)
wt = np.cos(np.radians(lat))[:, None] * np.ones(land.shape)
m = land & (lat[:, None] >= 37) & (lat[:, None] <= 49) & (lon[None, :] >= -5) & (lon[None, :] <= 28)
Py = P.sum(0); Ty = T.mean(0); yaz = P[3:9].sum(0)
esik = 20 * Ty + np.where(yaz >= 0.7 * Py, 280, np.where(Py - yaz >= 0.7 * Py, 0, 140))
ort = lambda a, mm: float((a * wt)[mm].sum() / wt[mm].sum())
br = np.vectorize(lambda c: koppen.BROAD.get(int(c), "?"))(Kp)
pay = lambda mm, ust: 100 * float(wt[mm].sum() / wt[ust].sum())
out = dict(ad=ad, params={**ek, **ozel}, res=res, sure_s=round(time.time() - t0),
           bolge_yagis=round(ort(Py, m)), bolge_BSk=round(pay(m & (Kp == 7), m), 1), bolge_oran=round(ort(Py / np.maximum(esik, 1), m), 2),
           bolge_B=round(pay(m & (br == "B"), m), 1), bolge_BS=round(pay(m & np.isin(Kp, [6, 7]), m), 1),
           grup={x: round(pay(land & (br == x), land), 1) for x in "ABCDE"},
           Aw=round(pay(land & (Kp == 3), land), 1), BS=round(pay(land & np.isin(Kp, [6, 7]), land), 1),
           Cs=round(pay(land & np.isin(Kp, [8, 9, 10]), land), 1), kara_yagis=round(ort(Py, land)))
np.savez_compressed(os.path.join(os.path.dirname(__file__), "k_%s_%s.npz" % (ad, res)), K=Kp)
taban = os.path.join(os.path.dirname(__file__), "k_taban_%s.npz" % res)
if ad != "taban" and os.path.exists(taban):
    out["sinif_degisen"] = round(pay(land & (np.load(taban)["K"] != Kp), land), 1)
    out["bolge_disi_degisen"] = round(pay(land & ~m & (np.load(taban)["K"] != Kp), land & ~m), 1)
print(json.dumps(out, ensure_ascii=False))
with open(os.path.join(os.path.dirname(__file__), "sonuc.jsonl"), "a") as fh:
    fh.write(json.dumps(out, ensure_ascii=False) + "\n")
