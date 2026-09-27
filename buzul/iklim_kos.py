"""Buzul hesabi icin iklimi kosar ve aylik T/P'yi npz olarak saklar.

    python buzul/iklim_kos.py --res 0.5 --dT 0 --deniz 0 --cikti buzul/_iklim_bugun.npz

--dT: deniz seviyesi kuresel ortalama sicakligina eklenen fark (buzul cagi icin
eksi). --deniz: deniz seviyesinin metre degisimi (buzul cagi icin eksi); kara
maskesi yeniden hesaplanir, sahanliklar acilir.
"""
import argparse, os, sys
import numpy as np
BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURASI))
import uret
from motor import model

ap = argparse.ArgumentParser()
ap.add_argument("--res", type=float, default=0.5)
ap.add_argument("--dT", type=float, default=0.0)
ap.add_argument("--deniz", type=float, default=0.0)
ap.add_argument("--egiklik", type=float, default=None, help="eksen egikligi (derece); bos = dunyanin kendisi")
ap.add_argument("--cikti", required=True)
a = ap.parse_args()

w = uret.dunya_yukle()
import dataclasses
w = dataclasses.replace(w, global_mean_sealevel_temp_c=w.global_mean_sealevel_temp_c + a.dT,
                        axial_tilt_deg=w.axial_tilt_deg if a.egiklik is None else a.egiklik)
if a.deniz:
    # Deniz a.deniz metre iner: kaynak cozunurlukte butun yukseklikler -a.deniz
    # kadar kalkar, kara maskesi KUCULTMEDEN ONCE yeniden cikar (CLAUDE.md 5).
    from motor import grid as G
    _ds = G.downsample
    G.downsample = lambda elev, block, sl, wraps: _ds(elev - a.deniz, block, sl, wraps)
g = uret.grid_kur(w, a.res)
print("hucre", g.shape, "kara %", 100 * g.land.mean(), flush=True)
r = model.run(g)
np.savez_compressed(a.cikti, T=r["temp"].astype(np.float32), P=r["precip"].astype(np.float32),
                    elev=g.elev.astype(np.float32), land=g.land, lat=g.lat, lon=g.lon,
                    K=r["koppen"])
print("yazildi", a.cikti)
