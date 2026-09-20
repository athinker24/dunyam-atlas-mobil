"""Katman 2-3 — isinim, enerji denge modeli, SST ve taban kara sicakligi.

Referans: docs/02-temperature.md

Iki katman tek modulde: SST ile kara sicakligi ayni cozucunun farkli isi
kapasitesiyle calistirilmis halidir. Mevsimsel genlik ve faz gecikmesi
elle verilmez, isi kapasitesinden turer.
"""

from __future__ import annotations

import json
import math

import numpy as np

from .circulation import subsolar_lat
from .grid import Grid, World

DEFAULTS = dict(
    olr_a=None,  # W/m2 — global ortalama sicakliktan turetilir, elle verilmez
    olr_b=2.09,  # W/m2/K — OLR = A + B*T
    transport_c=3.81,  # W/m2/K — meridyonel tasima, YILLIK ORTALAMA bileseni
    transport_c_seasonal=3.2,  # W/m2/K — mevsimsel sapma bileseni (<= transport_c)
    coalbedo_a0=0.7395,  # ko-albedo = a0 + a2*x^2 + a4*x^4, x = sin(lat)
    coalbedo_a2=0.1756,
    coalbedo_a4=-0.5199,
    heat_cap_land=1.5e7,  # J/m2/K — atmosfer sutunu + ~2 m nemli toprak
    heat_cap_ocean=2.0e8,  # J/m2/K — ~50 m karisim tabakasi
    wtg_k=6.0,  # W/m2/K — tropik WTG baglasim siddeti
    wtg_lat_deg=40.0,  # WTG'nin bozuldugu enlem olcegi
    # [K] Mevsimsel tasinim sonumunun ENLEMLE zayiflamasi.
    #   C_trs(phi) = C_trs / (1 + (|phi| / lat_deg)^n)
    # Gerekce: yuksek enlem kisinda yuzey kararli sinir tabakasi ve kar
    # ortusuyle atmosferden KOPAR; iyi karisan bir EBM'in izin verdiginden
    # cok daha asagi soguyabilir. Olculdu — mevsimsel genlik orani 60
    # enleme kadar 0.94-0.99, 60-70'te 0.76; ve gozlenen genlik o kusakta
    # YUKSELIRKEN modelinki dusuyor. Isi kapasitesi kaldirac degil (4 kat
    # azaltmak +0.03 aliyor), sonum kaldirac ama kuresel sabit oldugu icin
    # dusurmek 0-60'i patlatiyordu. Bkz docs/02 2.4.
    # lat_deg = 0 -> devre disi, C_trs sabit kalir (eski davranis birebir).
    transport_seasonal_lat_deg=0.0,
    transport_seasonal_pow=8.0,
    sea_ice_temp=-1.8,  # C — deniz suyu donma noktasi (35 psu)
    lapse_k_per_km=5.2,  # K/km — ETKIN YUZEY lapse rate, serbest atmosfer 6.5 DEGIL
    spinup_years=5,
    dt_days=1.0,
)


def params(world: World) -> dict:
    return {**DEFAULTS, **world.params}


# --- 2.1 Isinim geometrisi -------------------------------------------------

def daily_insolation(lat_deg, day, world: World) -> np.ndarray:
    """Gunluk ortalama atmosfer ustu isinim, W/m2. Tam ifade, yaklasim degil.

    lat_deg (nlat,) ve day (nday,) verilirse (nday, nlat) doner.
    """
    phi = np.radians(np.asarray(lat_deg, dtype=float))[None, :]
    dec = np.radians(subsolar_lat(np.asarray(day, dtype=float), world))[:, None]

    # yarim gun acisi; kutup gunu -> h0=pi, kutup gecesi -> h0=0
    h0 = np.arccos(np.clip(-np.tan(phi) * np.tan(dec), -1.0, 1.0))
    s = world.solar_constant_wm2 / np.pi
    return s * (h0 * np.sin(phi) * np.sin(dec) + np.cos(phi) * np.cos(dec) * np.sin(h0))


def coalbedo(lat_deg, p: dict) -> np.ndarray:
    """Ko-albedo (emilen kesir), gozlenen zonal gezegen albedosuna uyum.

    Klasik North (1975) tek terimli formu (a0 + a2*x^2) iki yapiyi kaciriyor:
    subtropiklerdeki acik-gokyuzu albedo minimumu ve kutuptaki buz kenari.
    x^4 terimi ikisini de yakaliyor. Bkz docs/02-temperature.md 2.2.
    """
    x = np.sin(np.radians(np.asarray(lat_deg, dtype=float)))
    return p["coalbedo_a0"] + p["coalbedo_a2"] * x**2 + p["coalbedo_a4"] * x**4


# --- 2.2 Enerji denge modeli ----------------------------------------------

def _area_weight(lat_deg) -> np.ndarray:
    w = np.cos(np.radians(np.asarray(lat_deg, dtype=float)))
    return w / w.sum()


def global_lat(dlat: float) -> np.ndarray:
    n = int(round(180.0 / dlat))
    return 90.0 - (np.arange(n) + 0.5) * dlat


def wtg_coupling(lat, p: dict) -> np.ndarray:
    """Zayif sicaklik gradyani (WTG) baglasim katsayisi, W/m2/K.

    Tropik troposfer yatayda neredeyse es sicakliktir: yercekimi dalgalari
    buoyancy gradyanini olusabileceginden hizli siler. Kara yuzey sicakligi
    bu yuzden okyanusun belirledigi troposfer sicakligina baglanir ve mevsimsel
    genligi bastirilir. Kongo ve Amazon ic bolgelerinin yillik genligi 1-3 C
    olmasinin sebebi budur, kiyiya yakinlik degil.

    Coriolis onem kazandikca (~30 derece) WTG bozulur; ^4 dusus bunu temsil eder.
    Bkz Sobel & Bretherton (2000) ve docs/02-temperature.md 2.3.
    """
    x = np.abs(np.asarray(lat, dtype=float)) / p["wtg_lat_deg"]
    return p["wtg_k"] / (1.0 + x**4)


def solve(lat, world: World, p: dict, heat_capacity: float, floor=None,
          months: int = 12, couple_to=None):
    """Zamana bagli 1B enerji dengesini periyodik rejime kadar entegre eder.

        C dT/dt = (1-alpha)S(t) - A - B*T - C_tr*(T - Tbar) - K(lat)*(T - T_ref(t))

    Denge cozumu degil, zamana bagli cozum: faz gecikmesi ve genlik sonumlemesi
    isi kapasitesinden kendiliginden cikar, elle verilmez.

    couple_to: (nday, nlat) referans sicaklik serisi (okyanus). Verilirse WTG
    baglasim terimi devreye girer; kara cozumu icin kullanilir.

    Doner (months, nlat); ayrica gunluk seriyi (nday, nlat) doner.
    """
    lat = np.asarray(lat, dtype=float)
    B, Ctr = p["olr_b"], p["transport_c"]
    tbar = world.global_mean_sealevel_temp_c

    dt = p["dt_days"]
    days = np.arange(0.0, world.year_length_days, dt)
    absorbed = coalbedo(lat, p)[None, :] * daily_insolation(lat, days, world)

    # A, global ortalamanin hedefe oturmasi icin turetilir (sera etkisi siddeti)
    a = p["olr_a"]
    if a is None:
        a = float((absorbed.mean(axis=0) * _area_weight(lat)).sum()) - B * tbar

    K = wtg_coupling(lat, p) if couple_to is not None else None
    Ctrs = p["transport_c_seasonal"]
    lat_s = p["transport_seasonal_lat_deg"]
    if lat_s and lat_s > 0:
        # kutba dogru zayiflayan sonum; ekvatorda carpan 1
        Ctrs = Ctrs / (1.0 + (np.abs(lat) / lat_s) ** p["transport_seasonal_pow"])

    dt_s = dt * 86400.0
    T = np.full(lat.size, tbar, dtype=float)
    month_of = np.minimum((days / world.year_length_days * months).astype(int), months - 1)

    acc = np.zeros((months, lat.size))
    cnt = np.zeros(months)
    daily = np.zeros((days.size, lat.size))
    t_ann = np.full(lat.size, tbar)  # onceki yilin ortalamasi
    for year in range(p["spinup_years"]):
        record = year == p["spinup_years"] - 1
        ysum = np.zeros(lat.size)
        for i in range(days.size):
            net = (absorbed[i] - a - B * T
                   - Ctr * (t_ann - tbar) - Ctrs * (T - t_ann))
            if K is not None:
                net = net - K * (T - couple_to[i])
            T = T + net * dt_s / heat_capacity
            if floor is not None:
                T = np.maximum(T, floor)
            ysum += T
            if record:
                acc[month_of[i]] += T
                cnt[month_of[i]] += 1
                daily[i] = T
        t_ann = ysum / days.size
    return acc / cnt[:, None], daily


def ocean_profile(lat, world: World, p: dict, months: int = 12):
    """Okyanus cozumu — kara cozumu buna baglanacagi icin ayri fonksiyon."""
    return solve(lat, world, p, p["heat_cap_ocean"], floor=p["sea_ice_temp"], months=months)


# --- 2.3 Okyanus akintilari -----------------------------------------------

def load_currents(world: World, path: str | None = None) -> list:
    path = path or getattr(world, "currents_file", None)
    if not path:
        return []
    with open(path, encoding="utf-8") as fh:
        akintilar = [c for c in json.load(fh)["currents"] if not c.get("disabled")]
    # Bu dosya kurgusal dunyada TAMAMEN elle yazilir; yazim hatasi sessizce
    # yutulmamali. Olculdu: tek noktali yol ve width_km=0 hicbir uyari
    # vermeden akintiyi tamamen yok ediyordu, negatif width ise pozitifmis
    # gibi calisiyordu (exp(-(d/w)^2) w'de cift).
    for c in akintilar:
        ad = c.get("name", "<isimsiz>")
        if len(c.get("path", [])) < 2:
            raise ValueError(f"akinti '{ad}': path en az 2 nokta icermeli "
                             f"({len(c.get('path', []))} verildi)")
        if float(c["width_km"]) <= 0:
            raise ValueError(f"akinti '{ad}': width_km pozitif olmali "
                             f"({c['width_km']} verildi)")
    return akintilar


def _segment_distance_km(lon, lat, a, b, wrap=False):
    """Hucrelerin bir dogru parcasina uzakligi (km) ve parca uzerindeki konumu.

    wrap=True (kuresel grid) ise boylam farklari parcanin BASLANGICINA gore
    +-180'e indirgenir. Sarmalamadan: antimeridyeni gecen bir yol 340 derece
    uzunlugunda bir dogru sanilir, ve dikisin obur yanindaki hucreler 359
    derece uzakta cikar. Olculdu: Kuroshio'nun sicak kuyrugu dikiste
    +0.156 C'den 0'a duserek kesiliyordu.
    """
    latref = math.radians((a[1] + b[1]) / 2.0)
    kx = 111.32 * math.cos(latref)
    if wrap:
        lon = (np.asarray(lon) - a[0] + 180.0) % 360.0 - 180.0
        bl = (b[0] - a[0] + 180.0) % 360.0 - 180.0
        al = 0.0
    else:
        al, bl = a[0], b[0]
    px, py = lon * kx, lat * 110.57
    ax, ay, bx, by = al * kx, a[1] * 110.57, bl * kx, b[1] * 110.57
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = np.clip(((px - ax) * dx + (py - ay) * dy) / max(L2, 1e-9), 0.0, 1.0)
    return np.hypot(px - (ax + t * dx), py - (ay + t * dy)), t, math.sqrt(L2)


def current_anomaly(grid: Grid, currents: list, months: int = 12) -> np.ndarray:
    """(months, ny, nx) C — akintilarin SST anomalisi. Yalnizca okyanus hucrelerinde.

    anomaly_c skaler ya da aylik dizi olabilir. Mevsimsel biçim, yari-kapali
    havzalar (Akdeniz) ve mevsimlik yukselim (Somali) icin gerekli.
    """
    lon2 = np.repeat(grid.lon[None, :], grid.lat.size, axis=0)
    lat2 = grid.lat2d
    total = np.zeros((months, *grid.shape))

    for cur in currents:
        pts = cur["path"]
        taper = np.asarray(cur.get("taper", [1.0, 1.0]), dtype=float)
        width = float(cur["width_km"])
        amp = np.asarray(cur["anomaly_c"], dtype=float)
        if amp.ndim == 0:
            amp = np.full(months, float(amp))
        elif amp.size != months:
            # Mevsimsel dizi yilin PERIYODIK bir fonksiyonudur; kac ornekle
            # yazildigiyla motorun kac ornek istedigi ayni olmak zorunda degil.
            # Dongusel interpolasyonla yeniden orneklenir.
            src = (np.arange(amp.size) + 0.5) / amp.size
            dst = (np.arange(months) + 0.5) / months
            amp = np.interp(dst, np.concatenate([src - 1, src, src + 1]),
                            np.concatenate([amp, amp, amp]))

        sar = grid.wraps
        lens = [_segment_distance_km(lon2[:1, :1], lat2[:1, :1], pts[i], pts[i + 1], sar)[2]
                for i in range(len(pts) - 1)]
        cum = np.concatenate([[0.0], np.cumsum(lens)])
        total_len = max(cum[-1], 1e-9)

        shape = np.zeros(grid.shape)  # birim genlikli mekansal desen
        for i in range(len(pts) - 1):
            d, t, _ = _segment_distance_km(lon2, lat2, pts[i], pts[i + 1], sar)
            pos = (cum[i] + t * lens[i]) / total_len
            scale = np.interp(pos, np.linspace(0, 1, taper.size), taper)
            shape = np.maximum(shape, scale * np.exp(-((d / width) ** 2)))
        total += amp[:, None, None] * shape[None, :, :]

    return np.where(grid.land[None, :, :], 0.0, total)


# --- Katman ciktilari ------------------------------------------------------

def sst(grid: Grid, currents: list | None = None, months: int = 12):
    """(12, ny, nx) C — deniz yuzey sicakligi."""
    world = grid.world
    p = params(world)
    gl = global_lat(grid.dlat)
    prof, _ = ocean_profile(gl, world, p, months)

    out = np.empty((months, *grid.shape))
    for m in range(months):
        out[m] = np.interp(grid.lat, gl[::-1], prof[m][::-1])[:, None]
    if currents:
        out += current_anomaly(grid, currents, months)
    return np.maximum(out, p["sea_ice_temp"])


def apply_lapse(temp, grid: Grid, p: dict | None = None):
    """Katman 4 — yukseklik duzeltmesi. (months, ny, nx) -> (months, ny, nx).

    Etkin YUZEY lapse rate'i kullanir (5.2 K/km), ICAO serbest atmosfer
    degerini (6.5) degil. Fark onemli: 4500 m Tibet'te 5.9 C. Dag yuzeyleri
    kendi sinir tabakalarini isitir, vadilerde soguk hava birikir; yuzey ile
    terrain arasindaki iliski serbest atmosferinkinden sigdir. Deger 235 bin
    hucrede yerel pencere regresyonuyla olculdu, bkz docs/03-elevation.md.
    """
    p = p or params(grid.world)
    dz = np.maximum(grid.elev - grid.world.sea_level_m, 0.0)
    return temp - p["lapse_k_per_km"] * dz / 1000.0


def base_temperature(grid: Grid, months: int = 12):
    """(12, ny, nx) C — deniz seviyesine indirgenmis kara sicakligi.

    Yukseklik duzeltmesi Katman 4'te, denizellik karisimi Katman 5'te.
    Bu haliyle KITA ICI davranisi temsil eder; kiyida asiri genlikli olmasi
    beklenir, duzeltmesi Katman 5'in isi.
    """
    world = grid.world
    p = params(world)
    gl = global_lat(grid.dlat)
    _, ocean_daily = ocean_profile(gl, world, p, months)
    prof, _ = solve(gl, world, p, p["heat_cap_land"], months=months, couple_to=ocean_daily)

    out = np.empty((months, *grid.shape))
    for m in range(months):
        out[m] = np.interp(grid.lat, gl[::-1], prof[m][::-1])[:, None]
    return out
