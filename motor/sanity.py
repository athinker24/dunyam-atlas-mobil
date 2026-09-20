"""Kurgusal dunya icin ic tutarlilik raporu.

Dunya dogrulamasinda WorldClim'e karsi sayisal hata olcuyoruz. Kurgusal bir
dunyada karsilastiracak gozlem YOKTUR; onun yerine modelin kendi fizigiyle
celismedigini kontrol ederiz.

Buradaki testler "iklim gercekci mi" demez — "motor kendi kurallarini ihlal
ediyor mu" der. Bir kontrol duserse ya girdi verisi bozuktur (yanlis deniz
seviyesi, ters cevrilmis heightmap) ya da bir katmanda hata vardir.

    from climate import model, sanity
    r = model.run(grid)
    print(sanity.format_report(sanity.check(grid, r)))
"""

from __future__ import annotations

import numpy as np

from .grid import Grid
from .temperature import daily_insolation
from .koppen import BROAD, CODES


def check(grid: Grid, r: dict) -> list:
    """(ad, gecti_mi, aciklama) uclulerinden olusan liste."""
    out = []
    land, ocean = grid.land, ~grid.land
    temp, precip, sst = r["temp"], r["precip"], r["sst"]
    world = grid.world

    def add(name, ok, detail):
        out.append((name, bool(ok), detail))

    # --- sayisal saglik ---
    # TUM ciktilar denetlenir, yalnizca temp/precip/sst degil. Sebep olculdu:
    # NaN bir ruzgar alani maritime iz surmesinde SESSIZCE AKLANIYOR — iz
    # anlamsiz ama SONLU bir denizellik orani uretiyor (0.959, yani her yer
    # denizel) ve sicaklik/yagis sonlu kaliyor. u/v denetlenmedigi surece
    # rapor boyle bir kosuyu temiz gosteriyordu.
    bozuk = sorted(ad for ad, a in r.items()
                   if isinstance(a, np.ndarray) and a.dtype.kind == "f"
                   and not np.isfinite(a).all())
    add("sayisal saglik", not bozuk,
        "NaN/sonsuz yok" if not bozuk else f"NaN ya da sonsuz deger var: {bozuk}")
    # Tolerans: gevseme semasi 1e-15 mertebesinde negatif artik birakabilir.
    # Anlamli bir negatiflik mm/ay olceginde gorunur; esik onun cok altinda.
    add("yagis negatif degil", precip.min() > -1e-6,
        f"en dusuk {precip.min():.3g} mm/ay")

    # --- fiziksel sinirlar ---
    # "SST donma noktasinin altina inmiyor" diye bir kontrol vardi ve YAPISAL
    # OLARAK OLUYDU: temperature.sst() son islem olarak np.maximum(out,
    # sea_ice_temp) uyguluyor, yani kosul asilamaz. Kelepcenin hala calistigi
    # iddiasi teste tasindi (test_sea_ice_clamp_and_frozen_fraction).
    #
    # Bilgi veren sey DONMUS ORAN: okyanusun ne kadari kelepcede. Motorda buz
    # yuzeyi ve buz-albedo geri beslemesi yok, dolayisiyla o oran buyudukce
    # sonuclar giderek daha az anlamli olur. Olculdu: gercek Dunya %11.9
    # (Ocak %13.2, Temmuz %13.2); sentetik gezegende hedef +17.5 -> %15.4,
    # +5 -> %31.5, 0 -> %41.7, -10 -> %60.0. Esik %35, Dunya'ya 3 kat pay.
    ice = world.params.get("sea_ice_temp", -1.8)
    donmus = float((np.abs(sst - ice) < 0.01).mean())
    add("okyanus buyuk olcude donmus degil", donmus < 0.35,
        f"okyanus-aylarin %{100 * donmus:.0f}'i donma noktasinda ({ice} C); "
        "buz yuzeyi ve buz-albedo modelde yok")
    # Esik GEZEGENE gore. Sabit 40 C Dunya'ya ozel bir sayidir ve motorun
    # temel kuralini cigner: kasten sicak bir dunyada (ortalama 30 C) SST'nin
    # 40'i asmasi DOGRUDUR, hata degil. Olculdu — modelin en sicak okyanusu
    # hedefin 11.4 C ustunde cikiyor ve bu sapma hedef -15..+45 C arasinda
    # degismiyor; gercek Dunya'da akintilarla +13.9. 25 C paye rahat.
    tavan = world.global_mean_sealevel_temp_c + 25.0
    add("SST ust siniri makul", sst.max() < tavan,
        f"en yuksek SST {sst.max():.1f} C (tavan {tavan:.1f})")

    # --- kuresel ortalama hedefe oturuyor mu ---
    if land.any():
        w = np.repeat(grid.area_m2[:, None], grid.shape[1], axis=1)
        sl = r["sealevel_temp"]
        gm = float((sl.mean(0) * w).sum() / w.sum())
        hedef = world.global_mean_sealevel_temp_c
        # Soguk bir dunyada bu kontrol duserse sebep neredeyse her zaman
        # DENIZ BUZU TABANIDIR, bir katman hatasi degil: okyanus donma
        # noktasinin altina inemez, ama motorda buz YUZEYI yoktur, dolayisiyla
        # ortalama asagi cekilemez. Olculdu — taban devre disi birakilinca
        # (sea_ice_temp: -60) hedef -25 C'de bile 0.05 C icinde tutuluyor;
        # tabanla birlikte ulasilan deger -2.9 C'de tikaniyor.
        tabanda = float((np.abs(sst - ice) < 0.01).mean())
        nicin = (f"; okyanus-aylarin %{100 * tabanda:.0f}'i donma noktasinda "
                 "(buz yuzeyi modellenmiyor)") if tabanda > 0.25 else ""
        add("kuresel ortalama sicaklik hedefte", abs(gm - hedef) < 3.0,
            f"{gm:.1f} C, hedef {hedef:.1f} C{nicin}")

    # --- enlemle ve yukseklikle sogumali ---
    # Ikisi de AYNI regresyondan okunur. Ayri ayri bakmak yaniltir: bir dunyada
    # daglar tropikte, alcak araziler kutupta olabilir; o zaman yukseklik
    # sogumasi enlem isinmasini tam gotururur ve ham korelasyon +0.00 cikar
    # (sentetik 7%-kara dunyada olculdu). Enlem ve yukseklik birlikte
    # cozulunce her ikisinin katsayisi da dogru isareti verir.
    if land.sum() > 50:
        la = np.abs(grid.lat2d)[land]
        ta = temp.mean(0)[land]
        ele = grid.elev[land] / 1000.0
        A = np.column_stack([np.ones(la.size), la, ele])
        coef, *_ = np.linalg.lstsq(A, ta, rcond=None)
        kol = abs(float(np.corrcoef(ele, la)[0, 1])) if np.ptp(ele) > 0 else 0.0

        if np.ptp(la) > 20:
            # Beklenen ISARET gezegenden turetilir, varsayilmaz. Eksen egikligi
            # ~54 dereceyi asinca yillik ortalama isinim kutupta ekvatordan
            # BUYUK olur ve sicaklik enlemle ARTMALIDIR. Sabit "azalmali"
            # kabulu 80 derece egiklikte dogru bir dunyayi hatali gosteriyordu.
            gun = np.arange(0.5, world.year_length_days, world.year_length_days / 48.0)
            s_ann = daily_insolation(grid.lat, gun, world).mean(0)
            ek = float(np.corrcoef(np.abs(grid.lat), s_ann)[0, 1])
            b = 10.0 * float(coef[1])
            if ek < 0:  # normal rejim: isinim kutba dogru azaliyor
                add("sicaklik enlemle dusuyor (yukseklik sabit)", b < -0.5,
                    f"{b:+.1f} C / 10 derece enlem (esdogrusallik {kol:.2f})")
            else:
                add("sicaklik enlemle ARTIYOR (asiri egiklik)", b > 0.5,
                    f"{b:+.1f} C / 10 derece enlem; yillik isinim kutupta "
                    f"daha buyuk (egiklik {world.axial_tilt_deg:.0f} derece)")

        # Esik GEVSEK: bu bir kalibrasyon degil, "isaret dogru mu" testi.
        # Iyi kosullu bir dunyada 4-6 K/km cikar (gercek Dunya'da olculdu:
        # tibet 4.8, cascades 4.6, atacama 5.5, kuresel 4.3). Arazi ile enlem
        # birbirine kilitliyse deger dusuk cikar ama isaret dogru kalir.
        if land.sum() > 100 and np.ptp(grid.elev[land]) > 500:
            lapse = -float(coef[2])
            add("yukseklikle sogume (enlem sabit)", 1.0 < lapse < 9.0,
                f"{lapse:.1f} K/km (iyi kosullu dunyada 4-6; "
                f"yukseklik-enlem esdogrusalligi {kol:.2f})")

    # Mevsimsel kontroller ancak mevsim VARSA anlamli. Sifir eksen egikligi
    # gecerli bir gezegendir; genlik ~0 oldugunda "ters mevsimli" ve
    # "okyanus genligi karadan kucuk" gurultuyu karsilastirir ve bosuna duser.
    genlik = float(np.ptp(temp, axis=0)[land].mean()) if land.any() else 0.0
    mevsimli = genlik > 1.0

    # --- yarimkureler ters mevsimli ---
    kuzey, guney = grid.lat2d > 20, grid.lat2d < -20
    if mevsimli and (land & kuzey).sum() > 20 and (land & guney).sum() > 20:
        dk = float(temp[6][land & kuzey].mean() - temp[0][land & kuzey].mean())
        dg = float(temp[6][land & guney].mean() - temp[0][land & guney].mean())
        add("yarimkureler ters mevsimli", dk > 0 > dg,
            f"kuzey Tem-Oca {dk:+.1f} C, guney {dg:+.1f} C")

    # --- okyanus karadan az mevsimsel ---
    if mevsimli and ocean.sum() > 20 and land.sum() > 20:
        ao = float(np.ptp(sst, axis=0)[ocean].mean())
        al = float(np.ptp(temp, axis=0)[land].mean())
        add("okyanus genligi karadan kucuk", ao < al,
            f"okyanus {ao:.1f} C, kara {al:.1f} C")

    # --- yagis kaynagi var mi ---
    if land.any():
        yillik = precip.sum(0)[land]
        add("kara yagis aliyor", yillik.mean() > 50,
            f"ortalama {yillik.mean():.0f} mm/yil, medyan {np.median(yillik):.0f}")

    # --- sinif dagilimi dejenere degil ---
    if "koppen" in r and land.any():
        kod, adet = np.unique(r["koppen"][land], return_counts=True)
        pay = adet / adet.sum()
        en = pay.max()
        add("iklim sinifi dagilimi dejenere degil", en < 0.6,
            f"{len(kod)} sinif, en yaygin {CODES[int(kod[pay.argmax()])]} %{100 * en:.0f}")
        gruplar = {BROAD[int(k)] for k in kod}
        add("birden fazla ana grup var", len(gruplar) >= 3,
            "gruplar: " + "".join(sorted(gruplar)))

    # --- muson geri beslemesi bir sey yapti mi ---
    # Eski kontrol "|dP| < 60 hPa" idi ve HIC ATESLENEMEZDI: monsoon.py
    # anomaliyi monsoon_max_hpa'da (25) sert kelepceliyor, yani 60'i asmak
    # imkansiz. Anlamli olan sey DOYMA — kelepce fizigin yerine geciyorsa
    # muson artik termal karsitliktan degil bir guvenlik sinirindan
    # belirleniyordur. Olculdu: gercek Dunya kelepceye hic degmiyor
    # (kuresel max 23.68 hPa, doyan hucre %0.000), ama tamami kara bir
    # sentetik dunya doyuyor.
    if "pressure_anomaly" in r and np.abs(r["pressure_anomaly"]).max() > 0:
        dp = np.abs(r["pressure_anomaly"])
        cap = float(world.params.get("monsoon_max_hpa", 25.0))
        pay = float((dp >= cap - 1e-9).mean())
        add("muson basinci kelepceye dayanmiyor", pay < 0.01,
            f"en buyuk |dP| {dp.max():.1f} hPa (kelepce {cap:.0f}); "
            f"doyan hucre-ay %{100 * pay:.2f}")

    return out


def format_report(rows: list) -> str:
    ok = sum(1 for _, g, _ in rows if g)
    lines = [f"IC TUTARLILIK RAPORU — {ok}/{len(rows)} gecti", ""]
    for name, gecti, detail in rows:
        lines.append(f"  {'gecti ' if gecti else 'DUSTU '} {name:38s} {detail}")
    if ok < len(rows):
        lines += ["", "  Dusen bir kontrol ya girdi verisinin bozuk oldugunu",
                  "  (yanlis deniz seviyesi, ters cevrilmis heightmap) ya da",
                  "  bir katmanda hata oldugunu gosterir."]
    return "\n".join(lines)
