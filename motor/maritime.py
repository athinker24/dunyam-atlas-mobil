"""Katman 5 — denizellik: hava kutlesinin ruzgar yorungesi boyunca degisimi.

Referans: docs/04-maritime.md

Katman 2-3 saf uclari uretir: tam kita ici kara ve acik okyanus. Bu katman
ikisini karistirir. Karisim orani OKLIT kiyi mesafesiyle degil, HAKIM RUZGAR
yonunde yukari-akis izlemeyle belirlenir.

Fark kritik: Lizbon ile Valensiya kiyiya ayni uzaklikta, ama bati ruzgari
altinda Lizbon'un yukari-akisi hemen Atlantik'e cikar, Valensiya'nin
yukari-akisi tum Iberya'yi kat eder. Oklit mesafe ikisini ayni sayar.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage

from .grid import Grid, World

DEFAULTS = dict(
    maritime_efold_km=600.0,  # e-katlama mesafesi
    maritime_max_frac=1.0,  # kiyida ulasilabilecek en yuksek denizellik
    maritime_local_frac=0.60,  # yonden BAGIMSIZ yerel karisim (deniz meltemi)
    maritime_local_km=130.0,  # yerel terimin e-katlama mesafesi
    trace_step_km=25.0,
    trace_max_km=2500.0,
    # Deniz buzu, HAFIF surum (0 = kapali, motorun Dunya'da dogrulanmis hali).
    # Acikken donma noktasindaki (sea_ice_temp) deniz kiyiya -1.8 C'lik
    # deniz havasi degil, buz ustu havasi tasir: o enlemin kita ici taban
    # sicakligi. Buz-albedo geri beslemesi ve buharlasma kesintisi YOK; kendini
    # besleyen dongu kurulmaz. Ayrinti: dunyam.json _deniz_buzu.
    sea_ice_air=0.0,
)


def params(world: World) -> dict:
    return {**DEFAULTS, **world.params}


def trace_upwind(grid: Grid, u: np.ndarray, v: np.ndarray, p: dict):
    """Her kara hucresinden ruzgara karsi yariya kadar iz surer.

    Yari-Lagrange geri izleme: tum hucreler ayni anda, sabit mesafe adimiyla.

    Doner:
        land_km  (ny,nx) — okyanusa ulasana kadar kat edilen kara mesafesi;
                           ulasilamadiysa trace_max_km
        src      (2,ny,nx) — okyanusa ilk deginilen nokta (satir, sutun indeksi)
        found    (ny,nx) bool — menzil icinde okyanus bulundu mu
    """
    ny, nx = grid.shape
    ds = p["trace_step_km"]
    nstep = int(round(p["trace_max_km"] / ds))

    speed = np.maximum(np.hypot(u, v), 1e-6)
    uh, vh = u / speed, v / speed

    ii, jj = np.meshgrid(np.arange(ny, dtype=float), np.arange(nx, dtype=float), indexing="ij")
    land_km = np.zeros((ny, nx))
    # done = iz durdu; found = GERCEKTEN okyanusa deginildi. Ikisi ayri:
    # domain disina cikan iz durur ama okyanus bulmus sayilmaz.
    done = ~grid.land.copy()
    found = ~grid.land.copy()
    src = np.stack([ii.copy(), jj.copy()])

    dy_km = grid.dy_m / 1000.0
    dx_km = grid.dx_m / 1000.0
    land_f = grid.land.astype(float)  # dongu icinde yeniden uretmek bosuna
    satir = np.arange(ny, dtype=float)

    for _ in range(nstep):
        active = ~done
        if not active.any():
            break
        # uh ve vh AYNI konumda orneklenir: bilineer plani paylassinlar.
        # Ucuncu ornekleme (is_land) adimdan SONRAKI konumda ve tek basina,
        # orada plan kurmanin maliyeti kazancindan buyuk.
        ornek = grid.sampler((ii, jj))
        # yukari-akis = ruzgarin tersi. satir indeksi kuzeye dogru AZALIR.
        su = ornek(uh)
        sv = ornek(vh)
        row_dx = np.interp(ii, satir, dx_km)

        ii = np.where(active, ii + sv * ds / dy_km, ii)
        jj = np.where(active, jj - su * ds / row_dx, jj)

        # sarmalanan gridde boylamda "disari cikmak" yoktur, dikisten geceriz
        outside = (ii < 0) | (ii > ny - 1)
        if not grid.wraps:
            outside |= (jj < 0) | (jj > nx - 1)
        ii, jj = np.clip(ii, 0, ny - 1), grid.wrap_j(jj)

        is_land = grid.sample(land_f, np.stack([ii, jj])) > 0.5

        land_km = np.where(active, land_km + ds, land_km)
        hit = active & ~is_land & ~outside
        src[0] = np.where(hit, ii, src[0])
        src[1] = np.where(hit, jj, src[1])
        found = found | hit
        # domain disina cikan iz durur, ama okyanus bulunmadi: kita ici sayilir
        done = done | hit | (active & outside)

    land_km = np.where(found | ~grid.land, land_km, p["trace_max_km"])
    return land_km, src, found & grid.land


def coast_distance_km(grid: Grid) -> np.ndarray:
    """(ny,nx) — en yakin okyanus hucresine oklit uzaklik, km."""
    return ndimage.distance_transform_edt(
        grid.land, sampling=(grid.dy_m / 1000.0, float(grid.dx_m.mean()) / 1000.0)
    )


def trace_months(grid: Grid, u, v, p: dict):
    """Tum aylar icin iz surer ve sonucu paketler.

    Iz YALNIZCA grid ve ruzgar alanina baglidir — denizellik parametrelerine
    degil. Pahali kisim budur (ay basina ~60 adim x 3 interpolasyon), o yuzden
    kalibrasyonda bir kez hesaplanip tekrar tekrar kullanilabilsin diye ayri
    duruyor.
    """
    n = len(u)
    land_km = np.empty((n, *grid.shape))
    src = np.empty((n, 2, *grid.shape))
    found = np.empty((n, *grid.shape), dtype=bool)
    for m in range(n):
        land_km[m], src[m], found[m] = trace_upwind(grid, u[m], v[m], p)
    return dict(land_km=land_km, src=src, found=found, coast_km=coast_distance_km(grid))


def fraction_from_trace(grid: Grid, land_km, found, coast_km, p: dict):
    """Iz sonucundan denizellik orani. Ucuz — kalibrasyon bunu tarar."""
    f = p["maritime_max_frac"] * np.exp(-land_km / p["maritime_efold_km"])
    f = np.where(found, f, 0.0)
    if p["maritime_local_frac"] > 0:
        f = np.maximum(f, p["maritime_local_frac"] * np.exp(-coast_km / p["maritime_local_km"]))
    return np.where(grid.land, f, 1.0)


def maritime_fraction(grid: Grid, u: np.ndarray, v: np.ndarray, p: dict, coast_km=None):
    """(ny,nx) 0..1 denizellik orani ve kaynak okyanus noktasi.

    Iki terimin buyugu alinir:

    1. YUKARI-AKIS: hakim ruzgar yonunde iz surerek bulunan kara mesafesi.
       Asil mekanizma; Lizbon ile Valensiya'yi ayiran budur.

    2. YEREL: yonden bagimsiz, oklit kiyi mesafesine bagli kisa menzilli terim.
       Deniz meltemi dolasimi ve alt-grid kiyi karisimi. Bu olmadan hakim
       ruzgari KARADAN esen kiyilar hic moderasyon almiyor — olculdu: Sili
       kiyisi 25G'de GD alizeleri altinda yukari-akisini Arjantin'den aliyor,
       Pasifik 20 km otede oldugu halde f=0 cikiyordu ve genlik +5C sisiyordu.
    """
    land_km, src, found = trace_upwind(grid, u, v, p)
    d = coast_distance_km(grid) if coast_km is None else coast_km
    return fraction_from_trace(grid, land_km, found, d, p), src


def apply(land_temp, sst, grid: Grid, u, v, p: dict | None = None, trace=None):
    """Kara sicakligini yukari-akis SST'sine dogru karistirir.

    land_temp, sst: (12, ny, nx). u, v: (12, ny, nx).
    Her ay kendi ruzgar alaniyla izlenir — muson bolgelerinde yon mevsimlik
    dondugu icin tek bir yillik iz yanlis olurdu.
    """
    p = p or params(grid.world)
    tr = trace if trace is not None else trace_months(grid, u, v, p)
    out = np.array(land_temp, dtype=float, copy=True)
    frac = np.empty((len(land_temp), *grid.shape))

    for m in range(len(land_temp)):
        f = fraction_from_trace(grid, tr["land_km"][m], tr["found"][m], tr["coast_km"], p)
        frac[m] = f
        src_sst = grid.sample(sst[m], tr["src"][m])
        if p["sea_ice_air"] > 0:
            # kaynak noktada ne kadar buz var (cift dogrusal ornek: buz kenari yumusak)
            ice = grid.world.params.get("sea_ice_temp", -1.8)
            buz = grid.sample((np.abs(sst[m] - ice) < 0.01).astype(float), tr["src"][m])
            buz_hava = np.minimum(src_sst, grid.sample(land_temp[m], tr["src"][m]))
            src_sst = src_sst + p["sea_ice_air"] * buz * (buz_hava - src_sst)
        out[m] = np.where(grid.land, land_temp[m] + f * (src_sst - land_temp[m]), sst[m])
    return out, frac
