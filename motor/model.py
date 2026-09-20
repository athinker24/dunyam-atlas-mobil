"""Zincirin calistiricisi — katmanlari sirayla ve dogru bagimliliklarla kosar.

Yurutme sirasi (modul numaralariyla ayni degil, bilerek):

    1. circulation  — zonal basinc kusaklari, ITCZ, ruzgar
    2. temperature  — SST (okyanus once: kara cozumu ona baglanir)
    3. temperature  — taban kara sicakligi (WTG ile SST'ye bagli)
    5. maritime     — yukari-akis karisimi          <-- ruzgara ihtiyac duyar
    6. monsoon      — termal basinc anomalisi       <-- sicakliga ihtiyac duyar
       ...ve ruzgar yeniden hesaplanir, 5 tekrarlanir (TEK iterasyon)
    4. temperature  — lapse rate                    <-- en son: hava kutlesi
                                                        once degisir, sonra yukselir
    7. moisture     — nem tasinimi ve yagis         <-- sicaklik + ruzgar
    8. koppen       — iklim siniflandirmasi          <-- nihai katman

Katman 6 zincire geri besleme sokar: sicaklik -> basinc -> ruzgar -> sicaklik.
Tam iterasyon gereksiz, tek gecis yeter ve determinizmi bozmaz.
"""

from __future__ import annotations

import numpy as np

from . import circulation, koppen, maritime, moisture, monsoon, temperature
from .grid import Grid


def run(grid: Grid, months: int = 12, monsoon_feedback: bool = True) -> dict:
    world = grid.world
    currents = temperature.load_currents(world)

    sst = temperature.sst(grid, currents, months)
    ocean_ref = temperature.sst(grid, None, months)  # akintisiz zonal referans
    base = temperature.base_temperature(grid, months)

    pressure, u, v, itcz = circulation.run(grid, months)
    cp = circulation.params(world)
    dp = np.zeros_like(pressure)

    npass = 2 if monsoon_feedback else 1
    for i in range(npass):
        sealevel, frac = maritime.apply(base, sst, grid, u, v)
        if i < npass - 1:
            dp = monsoon.pressure_anomaly(sealevel, ocean_ref, grid)
            pressure = pressure + dp
            for m in range(months):
                u[m], v[m] = circulation.winds(grid, pressure[m], cp)

    temp = temperature.apply_lapse(sealevel, grid)
    precip, cwv = moisture.run(grid, temp, sst, ocean_ref, u, v)

    # Koppen 12 aylik iklimatoloji uzerinde TANIMLIDIR (en soguk/sicak ay,
    # yaz/kis yarilari, 10 C ustu ay sayisi). Baska bir ornekleme sayisi
    # hata degil, hizli deneme icin gecerli bir secim — ama o durumda sinif
    # uretilemez, sessizce yanlis uretmek yerine atlanir.
    climate_class = koppen.classify(temp, precip) if months == 12 else None

    return dict(
        temp=temp,
        precip=precip,
        koppen=climate_class,  # months != 12 ise None
        cwv=cwv,
        sealevel_temp=sealevel,
        sst=sst,
        pressure=pressure,
        pressure_anomaly=dp,
        u=u,
        v=v,
        itcz=itcz,
        maritime_frac=frac,
    )
