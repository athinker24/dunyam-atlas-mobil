"""Katman 1 — basinc kusaklari, ITCZ kaymasi, hakim ruzgarlar.

Referans: docs/01-pressure-winds.md
Girdisi yok: sadece enlem geometrisi + gezegen parametreleri.
Kasten zonal simetrik; kara-deniz kaynakli yapilar Katman 6'da eklenecek.
"""

from __future__ import annotations

import math

import numpy as np
from scipy import ndimage

from .grid import Grid, World

# Model ayar katsayilari. Dunya ozelligi degil, parametrizasyon sabiti.
# world.params ile ezilebilir. Her degerin gerekcesi docs/01-pressure-winds.md.
DEFAULTS = dict(
    hadley_const=13939.0,  # derece*m/s; Dunya'da phi_H=30 verecek sekilde capalandi
    p_itcz=1010.0,  # hPa
    p_high=1019.0,
    p_low=1000.0,
    p_polar=1013.0,
    k_itcz=0.20,  # ITCZ salinim sonumlemesi
    itcz_lag_days=30.0,  # termal atalet gecikmesi
    drag_ocean_h=10.0,  # sinir tabakasi surtunme zaman olcegi
    drag_land_h=4.5,  # (45 derecede 15/30 kestirme acisini verir)
    c_eddy=2.0,  # cozulmeyen eddy tasiniminin toptan vekili
    eddy_scale_deg=25.0,  # eddy'lerin devreye girdigi enlem olcegi
    v_min=1.5,  # m/s taban
    smooth_deg=3.0,  # basinc profili yumusatmasi
    drag_blend_km=60.0,  # kiyida surtunme gecisinin yumusatma olcegi
    # ITCZ'den k. kusak dugumu ITCZ kaymasinin max(0, 1 - k*belt_shift_decay)
    # kadarini izler. 0 = KAPALI: butun kusaklar ITCZ ile kati kayar (bit bit
    # eski). Kati kayma 15 saatlik gunde (phi_H 18.8) ve k_itcz 0.6'da okyanusun
    # ~%77'sinde ruzgari yilda 3-4 kez donduruyor (CLAUDE.md 8, gece denetimi).
    belt_shift_decay=0.0,
)


def params(world: World) -> dict:
    return {**DEFAULTS, **world.params}


def subsolar_lat(day, world: World) -> np.ndarray:
    """Altgunes enlemi, derece. Dairesel yorunge icin tam ifade."""
    L = 2.0 * np.pi * (np.asarray(day, dtype=float) - world.northward_equinox_doy) / world.year_length_days
    return np.degrees(np.arcsin(math.sin(math.radians(world.axial_tilt_deg)) * np.sin(L)))


def hadley_edge_deg(world: World, p: dict) -> float:
    """Held-Hou olceklemesi: phi_H = C / (Omega * a)."""
    return float(np.clip(p["hadley_const"] / (world.omega * world.radius_m), 1.0, 90.0))


def itcz_lat(day, world: World, p: dict) -> np.ndarray:
    return p["k_itcz"] * subsolar_lat(np.asarray(day, dtype=float) - p["itcz_lag_days"], world)


def _belt_nodes(itcz: float, phi_h: float, p: dict):
    """ITCZ'den disariya alcak/yuksek donusumlu kusak dugumleri."""
    nodes, vals = [itcz], [p["p_itcz"]]
    d = float(p.get("belt_shift_decay", 0.0))
    for s in (1, -1):
        hemi = []
        k, phi = 1, (s * phi_h + itcz * max(0.0, 1.0 - d)) if d > 0 else itcz + s * phi_h
        while abs(phi) <= 90.0 + phi_h:
            hemi.append((phi, p["p_high"] if k % 2 else p["p_low"], k % 2 == 1))
            k += 1
            if d > 0:
                phi = s * k * phi_h + itcz * max(0.0, 1.0 - k * d)
            else:
                phi += s * phi_h
        # her yarimkurede en distaki YUKSEK kusak kutup yuksegidir
        for i in range(len(hemi) - 1, -1, -1):
            if hemi[i][2]:
                hemi[i] = (hemi[i][0], p["p_polar"], True)
                break
        nodes += [h[0] for h in hemi]
        vals += [h[1] for h in hemi]
    order = np.argsort(nodes)
    return np.asarray(nodes)[order], np.asarray(vals)[order]


def pressure_profile(lat: np.ndarray, itcz: float, world: World, p: dict) -> np.ndarray:
    """(ny,) hPa — zonal basinc profili."""
    phi_h = hadley_edge_deg(world, p)
    nodes, vals = _belt_nodes(itcz, phi_h, p)
    prof = np.interp(lat, nodes, vals)
    dlat = abs(float(lat[1] - lat[0]))
    sigma = p["smooth_deg"] / dlat
    if sigma > 0.5:
        prof = ndimage.gaussian_filter1d(prof, sigma, mode="nearest")
    return prof


def winds(grid: Grid, pressure: np.ndarray, p: dict):
    """Basinc alanindan yuzey ruzgari. (u, v) m/s, dogu ve kuzey pozitif.

    Ayri bir 'ruzgar kurali' yok: her sey gradyandan turer. Katman 6 muson
    anomalisini basinc alanina ekledinde bu kod degismeden muson ruzgarini
    da uretir.

    Denge: dogrusal surtunmeli momentum denklemi
        -f*v + k*u = -(1/rho) dP/dx
         f*u + k*v = -(1/rho) dP/dy
    cozumu hem hizi hem sapma acisini birlikte verir:
        |V|   = |gradP| / (rho * sqrt(f^2 + k^2))
        alpha = atan2(f, k)   (asagi-gradyan yonunden donme)
    Ekvatorda f=0 -> alpha=0 (saf asagi-gradyan akis), yuksek enlemde
    f>>k -> alpha->90 (jeostrofik). Ayri bir Coriolis tabanina gerek yok.
    """
    world = grid.world
    P = np.asarray(pressure, dtype=float) * 100.0  # hPa -> Pa

    # isaret ve sarmalama grid yardimcilarinda; bkz Grid.ddx / Grid.ddy
    dPdy = grid.ddy(P)
    dPdx = grid.ddx(P)

    mag = np.hypot(dPdx, dPdy)
    safe = np.maximum(mag, 1e-12)
    gx, gy = -dPdx / safe, -dPdy / safe  # yuksekten alcaga birim vektor

    lat2 = grid.lat2d
    # Surtunme kiyida SERT BASAMAK yapmamali. Gercek gecis ~50 km'de olur;
    # basamak birakmak ruzgari tek hucrede sicratir ve sahte yakinsama uretir
    # (olculdu: Kaskad kiyisinda konvektif yagis 3574 mm/ay, ortalamanin 26 kati).
    k = np.where(grid.land, 1.0 / (p["drag_land_h"] * 3600.0), 1.0 / (p["drag_ocean_h"] * 3600.0))
    k = grid.smooth(k, p["drag_blend_km"] / grid.cell_km)
    f = 2.0 * world.omega * np.sin(np.radians(lat2))

    a = np.arctan2(f, k) * world.rotation_sign
    ca, sa = np.cos(a), np.sin(a)
    ux, vy = gx * ca + gy * sa, -gx * sa + gy * ca  # saat yonunde dondurme (KY)

    # eddy takviyesi yalnizca orta/yuksek enlemlerde: gezici siklonlar
    # firtina yollarinda yasar, tropiklerde zonal ortalama akis zaten
    # akisin kendisidir. Uniform C_eddy tropikleri sisirir.
    c = 1.0 + (p["c_eddy"] - 1.0) * np.tanh(np.abs(lat2) / p["eddy_scale_deg"])
    speed = c * mag / (world.air_density_kgm3 * np.hypot(f, k))
    speed = np.maximum(speed, p["v_min"])
    return ux * speed, vy * speed


def run(grid: Grid, months: int = 12):
    """12 aylik basinc ve ruzgar alanlari.

    Doner: pressure (12,ny,nx) hPa, u (12,ny,nx), v (12,ny,nx), itcz (12,) derece.
    """
    world = grid.world
    p = params(world)
    ny, nx = grid.shape
    days = (np.arange(months) + 0.5) * world.year_length_days / months

    pres = np.empty((months, ny, nx))
    u = np.empty((months, ny, nx))
    v = np.empty((months, ny, nx))
    itcz = itcz_lat(days, world, p)

    for m in range(months):
        prof = pressure_profile(grid.lat, float(itcz[m]), world, p)
        pres[m] = prof[:, None]
        u[m], v[m] = winds(grid, pres[m], p)
    return pres, u, v, itcz
