"""Katman 6 — kara-deniz termal kontrastindan dogan basinc anomalisi.

Referans: docs/05-monsoon.md

Katman 1 kasten zonal simetrikti. Bu katman boylama bagli yapiyi ekler:
Sibirya Yuksek Basinci, Azor/Izlanda merkezleri, ve Hint musonu.

Yeni bir ruzgar kurali YOK. Anomali basinc alanina eklenir, Katman 1'in
`winds()` fonksiyonu hic degismeden muson ruzgarini uretir. Katman 1 bu
yuzden ruzgari basinc gradyanindan turetecek sekilde yazilmisti.
"""

from __future__ import annotations

import numpy as np

from .grid import Grid, World

DEFAULTS = dict(
    monsoon_k_hpa_per_k=1.3,  # hPa / K — termal alcak/yuksek siddeti
    monsoon_smooth_km=700.0,  # anomali yumusatma olcegi
    monsoon_ocean_damp=0.35,  # okyanus anomalisinin zayifligi
    monsoon_max_hpa=25.0,  # guvenlik siniri
)


def params(world: World) -> dict:
    return {**DEFAULTS, **world.params}


def pressure_anomaly(temp, ocean_ref, grid: Grid, p: dict | None = None):
    """(months, ny, nx) hPa — termal basinc anomalisi.

    temp:      (months, ny, nx) deniz seviyesi esdeger sicaklik (lapse ONCESI)
    ocean_ref: (months, ny, nx) ayni enlemdeki okyanus sicakligi (referans)

    Isinan bir hava sutunu genisler, ust seviyede iraksama olur, kutle
    tasinir ve yuzey basinci duser. Olcekleme hidrostatik:

        dP ~ -(rho * g * H / T) * dT ~ -1.3 hPa/K   (H ~ 3 km isinan tabaka)

    Referans olarak AYNI ENLEMDEKI OKYANUS alinir; muson tam olarak kara-deniz
    termal kontrastindan dogar. Sicakligin deniz seviyesine indirgenmis hali
    kullanilir (lapse oncesi), yoksa her dag kendi sahte yuksek basincini
    uretir.

    Anomali yumusatilir: gercek termal alcak/yuksekler 1000+ km olceginde
    yapilardir, hucre olceginde degil.
    """
    p = p or params(grid.world)
    dt = np.asarray(temp) - np.asarray(ocean_ref)
    dp = -p["monsoon_k_hpa_per_k"] * dt
    dp = np.where(grid.land[None, :, :], dp, dp * p["monsoon_ocean_damp"])

    sigma = p["monsoon_smooth_km"] / grid.cell_km
    for m in range(dp.shape[0]):
        dp[m] = grid.smooth(dp[m], sigma)

    # Alan ortalamasi CIKARILMAZ. Referans zaten ayni enlemdeki okyanus oldugu
    # icin okyanus hucreleri kendiliginden ~0 alir. Ortalama cikarmak kara
    # sinyalini okyanusa tasiyordu: Tibet kutusu %73 kara, kisin karadaki (+)
    # anomali ortalamayi yukari cekince Bengal Korfezi -7 hPa cikiyordu.
    # Ruzgar yalnizca gradyana duyarli, sabit ofset zaten zararsiz.
    return np.clip(dp, -p["monsoon_max_hpa"], p["monsoon_max_hpa"])
