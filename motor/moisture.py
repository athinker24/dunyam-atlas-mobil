"""Katman 7 — nem tasinimi, orografik yagis, yagmur golgesi, konvektif yagis.

Referans: docs/06-precipitation.md

Yontem: kararli-hal yari-Lagrange nem butcesi. IKI bilesen ruzgar boyunca
tasinir — W = su buhari, C = bulut suyu:

    W, C     = yukari-akis noktasindan ornekle
    engelleme: asilamayan nem C'ye gecer ve YUKARI-AKIS tarafina birakilir
    W       += buharlasma                       (okyanus uzerinde)
    kapasite = W_doygun(T - lapse * altgrid_kaldirma)
    W > kapasite  -> fazlasi C'ye gecer         (yogusma)
    W < kapasite  -> C'den W'ye geri doner      (buharlasma)
    yagan    = verim * C  +  derin_konveksiyon
    C       -= verim * C

Tek bilesenli yazmak calismaz: `verim` hem yagis miktarini hem kuruma hizini
kontrol eder, ikisi ayni anda dogru olamaz. Bkz docs/06-precipitation.md 6.1.

Yagmur golgesi ayri bir kural DEGIL, bu butcenin sonucu. Ama mekanizma
sanildigindan farkli: ruzgar altinda W GERI TOPARLANIR (bulut suyu alcalirken
buharlasir); golgeyi yaratan sey buhar tukenmesi degil, kapasitenin yukselip
YOGUSMANIN DURMASIDIR. Olculdu — sentetik sirt testinde zirvede 76 mm/ay,
ruzgar altinda 0.0 mm/ay, ama W 8.4'ten 11.0'a geri cikiyor.
"""

from __future__ import annotations

import math

import numpy as np
from scipy import ndimage
from scipy.special import erf

from .grid import Grid, World

DEFAULTS = dict(
    cwv_ref_mm=62.0,  # DOYGUN sutun su buhari, referans sicaklikta.
    # 45 yanlisti: 45 mm tropikte GERCEKLESEN degerdir, doygun degil.
    # rh_ocean=0.8 ile 36 mm cikiyordu, Ganj ovasi Temmuz'da gercekte ~55-60.
    cwv_ref_temp_c=27.0,
    cwv_efold_k=15.0,  # Clausius-Clapeyron olcegi (~7%/K)
    rh_ocean=0.80,  # okyanus ustu denge bagil nemi
    evap_length_km=1500.0,  # buharlasmanin e-katlama mesafesi
    # [P] Buharlasma akisinin ust siniri, mm/ay. 0 = KAPALI (Dunya icin
    # bit-birebir eski davranis). Gevseme semasinin eksik parcasi: hava
    # dengeye ne kadar hizli yaklastigi yazili, okyanusun ne kadar
    # verebilecegi yazili degil. Kapali halde kuresel su butcesi Dunya'nin
    # IKI KATI (2061 mm/yil, gercek ~1000). Dunya'da acmak butceyi
    # duzeltirken Koppen'i dusurdugu icin kapali; kurgusal dunyada olcut
    # Koppen degil fizik oldugundan orada acilmali. docs/06 6.5b.
    evap_max_mm_month=0.0,
    # [P] NEM KORUNUMU: yakinsama, girdap ve firtina yagisi tasinan buhardan
    # dusulur (bkz solve_month). Kapaliyken bu uc terim nemden bagimsiz
    # hesaplanir ve yagisin ~%30'u yoktan gelir; evap_max tek basina butceyi
    # duzeltemez (Dunyam 1 der: tavan 60 mm/ay iken okyanusa 1621 mm/yil
    # yagiyor, buharlasmadan fazla). 0 = KAPALI (bit-birebir eski davranis).
    conserve_moisture=0.0,
    land_recycle=0.25,  # kara ustu evapotranspirasyon geri kazanimi
    precip_efficiency=0.060,  # bulut suyunun her adimda yagan kesri
    # [K] Alt-grid sirtlarin etkin kaldirma yuksekligi, relief'in kesri.
    # 1.00 = hava hucreyi vadi tabanindan sirta kat eder; fiziksel TAVAN budur,
    # kaldirma sirtin kendisinden buyuk olamaz. Supuruldu (docs/06 6.6):
    # kuresel Koppen ana grup 0.6388 / 0.6496 / 0.6588 / 0.6404 (frac
    # 0 / 0.5 / 1 / 2) — tepe tam tavanda. 2.0 bes zor bolgede daha iyi
    # gorunuyor ama kuresel olcekte hem ana grubu hem korelasyonu dusuruyor
    # ve fizigi yok. Eski deger 0.50 idi (ortalama -> sirt tirmanisi).
    relief_lift_frac=1.00,
    convective_c=0.42,  # yakinsama katsayisi (us 0.70 ve girdap difuzyonuyla birlikte)
    # [P] SU BUTCESI TAVANI. p_conv = c*W*conv carpimidir ve UST SINIRI YOKTUR;
    # gercekte bir hava sutunu icindeki suyu belli bir devir suresinden hizli
    # yagdiramaz. Kuresel ortalamada bu sure ~9 gun (W ~ 25 mm, P ~ 83 mm/ay).
    # Tavan = W / tau_min * SECONDS_PER_MONTH. Yalnizca UC islak hucreleri
    # kirpar, kuraklara dokunmaz — yani "en kurak / en yagisli" oranini
    # yukseltir, ki 6.6'daki teshis tam bunu istiyor. 0 = tavan yok.
    # [P] 1.5 gun. Olculdu: kuresel yagis orani 1.217 -> 1.118, uzamsal
    # korelasyon 0.375 -> 0.494 (+12 puan, projedeki en buyuk sicrama),
    # Koppen berabere. Fiziksel sabit, Dunya'ya oturtulmus degil.
    conv_tau_min_days=1.5,
    # [P] Esikler aylik ORTALAMAYA uygulaniyordu; Jensen geregi ortalamasi
    # esigin hemen altinda kalan hucreler hak ettiginden az aliyor. Esik
    # dagilima uygulanir: E[max(0,X)] = mu*Phi + sigma*phi, sigma=0'da tam
    # olarak eski hale iner. sigma iraksama alaninin RMS'inin kesri —
    # gezegene ozel sabit yok. Tek basina 0.20'de Koppen grubunu 0.70'e
    # cikariyor ama tam isabeti dusuruyor; tavanla birlikte 0.05 dengeli.
    div_var_frac=0.05,
    # [P] Konvektif yagisin NEM USSU. Sema p_conv ~ W^1 varsayiyor; olculdu
    # ki gozlenen yagisin mevsimsel min/max orani (0.249) W'nin kendi
    # oranindan (0.144) BUYUK, yani gercek yagis nemle dogrusal olcekLENMIYOR:
    # kurak aylarda mevcut neme gore daha verimli yagiyor (firtinalar sutunu
    # daha hizli cevirir). Us 1 -> 0.7 tahmini 0.144^0.7 = 0.26 verir.
    # W_ref = cwv_ref_mm, boylece us degisimi mutlak olcegi kaydirmaz.
    conv_w_pow=0.70,
    # [P] GEZICI GIRDAP NEM DIFUZYONU — kurak mevsim yagisinin ayri sureci.
    #   F = -K grad(W)   (gradyan asagi tasima)
    #   P_eddy = -div(F) = K * laplace(W)      pozitif kisim
    # Neden bu: docs/06'daki imkansizlik argumani, p ~ W^a*conv^b biciminde
    # gozlenen mevsimselligin ULASILAMAZ oldugunu gosteriyor. Gereken sey
    # kurak mevsimde calisan ve KENDI mekansal yapisi olan ayri bir surec.
    # Bu terimin deseni W'nin EGRILIGINDEN gelir (conv'dan bagimsiz), yerel
    # W kuculdugunde sonmez (gradyana baglidir), ve kara-deniz nem karsitligi
    # KISIN en buyuk oldugu icin dogru mevsimde guclenir.
    # Tipik atmosferik girdap difuzivitesi ~1e6 m2/s. 0 = kapali.
    eddy_diff_m2s=1.0e6,
    eddy_smooth_km=600.0,  # laplasyen gurultulu; once yumusatilir
    # [P] Girdap TASIMASI: nem, Gauss yumusatmasina dogru harmanlanarak
    # gradyan asagi tasinir -> W <- (1-a)*W + a*smooth(W). Difuzyona denktir
    # ama KOSULSUZ KARARLIDIR; acik sema kararlilik sayisiyla (0.2) sinirliydi
    # ve K'yi buyutmek hicbir sey degistirmiyordu (olculdu).
    # Bu, on iki denemenin kovaladigi ZAMANSAL kusuru ilk kez asan sey:
    # mevsimsel min/max 0.068 -> 0.105, yani Koppen'in "w" esigi olan 0.10'u
    # geciyor; "kuraksiz" payi %15.7 -> %25.2. Uzamsal korelasyon da yukseliyor
    # (0.470 -> 0.488), yani korukoru su eklemiyor. Bedeli yagis oraninin
    # 1.277 -> 1.381 bozulmasi. Bkz docs/06.
    eddy_blend=0.005,
    moist_crit_frac=0.50,  # derin konveksiyonun basladigi W/kapasite esigi
    # [P] Derin konveksiyon esiginin YUMUSAKLIGI, cap_free'nin kesri olarak.
    # 0 = KAPALI, sert max(0, W - esik): Dunya icin bit-birebir eski davranis.
    # Sert esik kurgusal dunyada (Dunyam) bir dag sirasinin ruzgar ustunde
    # 2-3 derece genisliginde, cevresiyle uyumsuz OK SEKLINDE bir yaz yagisi
    # seridi uretti: engellenen nem W'yi esigin hemen ustune itiyor, iki yani
    # esigin altinda kaliyordu (Temmuz 132 mm, 3 derece otesinde 19). Olculdu,
    # serit ancak engellenme VE derin konveksiyon birlikte acikken var.
    # Esigi dagilima uygulamak (_soft_pos, Jensen) cizgiyi yumusak gecise
    # cevirir. Bedeli: erf ic dongude, ~%14 sure (docs/06, onbirinci deneme).
    moist_crit_soft=0.0,
    moist_rate=0.20,  # esik ustu nemin her adimda yagan kesri
    moist_subsid_scale=1.5e-6,  # cokmenin konveksiyonu bastirma olcegi (1/s)
    convective_smooth_km=350.0,  # konvektif sistemlerin orgutlenme olcegi
    advect_step_km=25.0,
    advect_iters=0,  # 0 = nemin katetmesi gereken mesafeden turet
    reach_factor=3.0,  # yol duz olmadigi icin kiyi mesafesine carpan
    # DIKKAT: bu esik ADIM BASINA metredir (advect_step_km = 25 km), hucre
    # basina degil. Yani engellenmenin devreye girmesi icin EGIM
    # blocking_free_dz_m / advect_step_km = 12 m/km'yi asmali. Olculdu:
    # 2200 m'yi 300 km'de kaldiran bir sirtta (7 m/km) uc engelleme
    # parametresi de TAM ETKISIZ; 4000 m'yi 100 km'de kaldiran duvarda
    # (38 m/km) yagisi 100-760 mm degistiriyorlar. advect_step_km
    # degistirilirse bu esik de degisir — ikisi birbirine baglidir.
    blocking_free_dz_m=300.0,  # bu tirmanisa kadar hic engellenme yok
    blocking_dz_m=900.0,  # esik ustu engellenmenin e-katlama olcegi
    blocking_spread_km=800.0,
 # bariyerin yukari-akis etki mesafesi
    min_wind_ms=1.5,
    # [K] FIRTINA YOLU yagisi — gezici orta enlem siklonlari.
    # Motorda siklon yok; kusak ve muson cekilince orta enlem kisinda yagis
    # uretecek surec kalmiyordu (Dunyam 40-50K kis ayi 16 mm, ayni enlemde
    # Moskova 55). Kis siklonlarini besleyen, soguk kita havasinin ilik
    # okyanusla karsilasmasidir; terim bu KARSITLIKTAN kurulur:
    #   P = storm_c * (f/1e-4 1/s) * max(0, T_okyanus - T_kara)/10 K
    #           * (W_okyanus/W_ref)^conv_w_pow * S
    # T'ler deniz seviyesine indirilmis sicakligin o enlemdeki okyanus ve kara
    # ortalamalari; W_okyanus o enlemdeki okyanusun denge buhari. Takvim YOK:
    # kara okyanustan sicaksa (yaz) terim kendiliginden sifirdir, yarimkureyi
    # ve mevsim gecisini sicaklik alani belirler. f tropikte soner.
    # S = firtina havasi kesri: okyanustan UST SEVIYE akisla (termal ruzgar)
    # tasinir, adim basina exp(-ds/storm_reach_km) soner ve nemle ayni
    # engellenme hesabiyla sirtlarda kesilir. Elenenler (1 derece): oklit kiyi
    # mesafesi platoyu acik ova gibi islatti (plato bozkiri %51 -> %21, c=30);
    # YUZEY ruzgari kisin kitadan denize estigi icin firtina havasi ic kesime
    # giremedi (40-50K Ocak 20 -> 22 mm, c=100).
    # ELENEN IKI SURUM (1 derece, olculdu): yerel egim + yerel W -> terim yazin
    # buyudu; zonal Eady olcegi f*|dT/dy| -> bu dunyada egim kisin buyumuyor
    # (35-60K farki Ocak 13.7, Temmuz 16.6 K; kara %7, ortalamayi okyanus
    # belirliyor), terim yil boyu esit ekledi ve plato bozkirini %51 -> %5'e
    # indirdi. 0 = KAPALI (bit-birebir eski davranis).
    storm_c=0.0,
    storm_smooth_km=1000.0,  # karsitligin enlem boyunca yumusatma olcegi
    storm_reach_km=1500.0,  # firtina havasinin ruzgar boyunca e-katlama mesafesi
    storm_spread_km=400.0,  # firtina yolunun kuzey-guney yalpalamasi (toplam yayilma)
    # [K] Kara-okyanus karsitliginin AY ICI dagilimi, K. Karsitlik aylik
    # ORTALAMAYA uygulaniyordu: ilkbaharda ortalama sifira inince terim
    # tamamen sonuyor, oysa ay icindeki soguk dalgalarda karsitlik yine
    # pozitif ve siklon kaynagi acik. Esik dagilima uygulanir (_soft_pos,
    # div_var_frac ile ayni Jensen argumani): kisin (buyuk karsitlik) ve yazin
    # (kuvvetle negatif) degisiklik yok denecek kadar az, yalniz GECIS
    # aylarinda yagis ekler. Olculdu (Dunyam, 0.5 der, 10 K): 36K kuzeyinde
    # en kurak ay Mart'ti (yakinsama yagisi Mayis'ta basliyor, firtina Mart'ta
    # sonuyor). 0 = KAPALI (bit-birebir eski davranis).
    storm_contrast_sigma_k=0.0,
)

SECONDS_PER_MONTH = 365.25 * 86400.0 / 12.0


def params(world: World) -> dict:
    return {**DEFAULTS, **world.params}


def temperature_lapse(grid: Grid) -> float:
    """Katman 4'un lapse rate'i — alt-grid kaldirmanin sogutmasi icin."""
    from .temperature import params as tparams

    return tparams(grid.world)["lapse_k_per_km"]


def cwv_saturation(temp_c, p: dict) -> np.ndarray:
    """Doygun sutun su buhari (mm). Clausius-Clapeyron olcekli.

    Gozlenen GERCEKLESEN degerler: tropikte ~45-55 mm, orta enlem yazi ~25,
    kisi ~10, kutup ~5. Bu fonksiyon DOYGUNLUGU verir; gerceklesen deger
    bagil nemle carpilmis halidir.
    """
    return p["cwv_ref_mm"] * np.exp((np.asarray(temp_c) - p["cwv_ref_temp_c"]) / p["cwv_efold_k"])


def divergence(grid: Grid, u, v) -> np.ndarray:
    """(ny,nx) 1/s — yatay iraksama. Negatifi yakinsama, yani yukselis."""
    cos = np.cos(np.radians(grid.lat))[:, None]
    return grid.ddx(u) + grid.ddy(v * cos) / cos


def _boxblur(a: np.ndarray, sigma_cells: float) -> np.ndarray:
    """Gauss filtresine yakin, ama sigmadan BAGIMSIZ maliyetli yumusatma.

    scipy'nin gaussian_filter'i cekirdegi sigma ile buyutur; iterasyon
    dongusunun icinde sigma=44 hucreyle cagirmak modeli bir kat yavaslatiyordu
    (Tibet'te 12 ay x 300 iterasyon x buyuk cekirdek). Iki gecisli kutu
    filtresi merkezi limit teoremi geregi Gauss'a yakinsar ve kayan toplamla
    O(N) calisir.
    """
    # n gecisli kutu filtresinin toplam varyansi n*(N^2-1)/12 oldugundan
    # esdeger boyut N = sigma * sqrt(12/n). 3 gecis Gauss'a en yakin sonucu
    # veriyor (olculdu: hata 0.171 std, 2 gecisli 0.263), maliyeti hala
    # gaussian_filter'in 1/10'u.
    n = 3
    size = max(1, int(round(sigma_cells * (12.0 / n) ** 0.5)))
    if size <= 1:
        return a
    for _ in range(n):
        a = ndimage.uniform_filter(a, size, mode="nearest")
    return a


def _upwind_sampler(grid: Grid, u, v, ds_km: float):
    """Yukari-akis noktasinin indeks koordinatlarini bir kez hesaplar."""
    ny, nx = grid.shape
    speed = np.maximum(np.hypot(u, v), 1e-6)
    uh, vh = u / speed, v / speed
    ii, jj = np.meshgrid(np.arange(ny, dtype=float), np.arange(nx, dtype=float), indexing="ij")
    # satir indeksi kuzeye dogru AZALIR
    src_i = np.clip(ii + vh * ds_km / (grid.dy_m / 1000.0), 0, ny - 1)
    src_j = grid.wrap_j(jj - uh * ds_km / (grid.dx_m[:, None] / 1000.0))
    return np.stack([src_i, src_j])


def _soft_pos(mu, sigma):
    """E[max(0, X)], X ~ N(mu, sigma^2). sigma=0 iken tam olarak max(0, mu).

    Esigi aylik ORTALAMAYA degil DAGILIMA uygular; Jensen geregi
    E[max(0,X)] >= max(0,E[X]), yani ortalamasi esigin hemen altinda kalan
    hucreler aksi halde tam sifir alir.

    sigma skaler ya da mu ile ayni sekilde DIZI olabilir — yogusma esiginde
    kapasiteyle olceklendigi icin dizidir. Sonuc matematiksel olarak >= 0
    ama buyuk negatif mu icin mu*Phi ile sigma*phi birbirini goturur ve
    kayan noktada minik negatif cikabilir; kirpiliyor.
    """
    sig = np.asarray(sigma, dtype=float)
    if sig.ndim == 0 and sig <= 0.0:
        return np.maximum(0.0, mu)
    s_ = np.maximum(sig, 1e-30)
    z = mu / s_
    out = (mu * 0.5 * (1.0 + erf(z / math.sqrt(2.0)))
           + s_ * np.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi))
    return np.maximum(0.0, np.where(sig > 0.0, out, np.maximum(0.0, mu)))


def _needed_iters(grid: Grid, p: dict) -> int:
    """Iterasyon sayisi, nemin katetmesi gereken mesafeden turer.

    Her iterasyon bilgiyi bir adim tasir. Sabit sayi calismaz: 100 adim
    (2500 km) Tibet kutusunda yagisi yariya dusuruyordu (oran 0.22 yerine
    0.47).

    Ama domain BOYUTUNU kullanmak da yanlis — kuresel gridde tum boylam
    turunu (25 600 km) istiyor ve 1535 iterasyon cikiyordu. Nem her yerde
    okyanustan besleniyor; bilginin katetmesi gereken mesafe, karanin en ic
    noktasinin okyanusa uzakligidir. Yol duz olmadigi icin paya carpilir.

    Hic okyanus hucresi yoksa iterasyon SIFIRDIR. Su buhari yalniz okyanus
    ustunde uretilir (W okyanusta w_eq, karada 0 baslar) ve kara yalnizca
    dusen yagisin bir kismini geri kazanir; kaynak yoksa W sonsuza kadar 0
    kalir. Domain capina dusen eski hal olculdu: tamami kara bir kuresel
    gridde 3041 iterasyon donup 0 mm uretiyordu, 73 saniye.
    """
    if p["advect_iters"]:
        return int(p["advect_iters"])
    if grid.land.all():
        return 0
    d = ndimage.distance_transform_edt(
        grid.land, sampling=(grid.dy_m / 1000.0, float(grid.dx_m.mean()) / 1000.0))
    reach_km = max(float(d.max()), 500.0)
    return int(np.ceil(p["reach_factor"] * reach_km / p["advect_step_km"]))


def solve_month(grid: Grid, temp, sst, ocean_ref, u, v, p: dict):
    """Bir ay icin (yagis mm/ay, sutun su buhari mm) doner."""
    ds = p["advect_step_km"]
    src = _upwind_sampler(grid, u, v, ds)
    # src dongu boyunca SABIT: bilineer plani bir kez kurup tekrar kullan.
    # Olculdu: ornekleme cagrisi basina 2.96 -> 0.49 ms (6 kat).
    # [P] Dongu float32 calisir. Nem dongusu BANT GENISLIGINE baglidir:
    # 0.5 derecede her alan 2.07 MB ve ~15 alan L3'u asiyor. Olculdu, ayni
    # aritmetik dongu — 1 derecede 2.26 kat, 0.5 derecede 4.37 kat hizli
    # (teorik 2 katin ustunde, cunku float32 calisma kumesi onbellege
    # sigiyor). Hassasiyet: ~300 ardisik islem icin bagil hata ~2e-6;
    # yagis mm olceginde ve Koppen esikleri cok daha kaba.
    F = np.float32
    ornek = grid.sampler(src, dtype=F)
    speed = np.maximum(np.hypot(u, v), p["min_wind_ms"])

    # Etkin yogusma seviyesi hucre ORTALAMA yuksekliginde degil, icindeki
    # SIRTIN uzerindedir. 18 km'lik hucrede ortalama yukseklik sirtlari
    # duzlestirir; hava gercekte sirta tirmanip orada yogusur.
    # Olculdu: gozlenen yagis yukseklikle degil ROLYEFLE korele
    # (Kaskadlar +0.35, Iberya +0.43; yukseklikle -0.36 ve 0.00).
    lift = p["relief_lift_frac"] * np.asarray(grid.relief) / 1000.0
    lapse = temperature_lapse(grid)
    cap = cwv_saturation(np.asarray(temp) - lapse * lift, p)
    w_eq = p["rh_ocean"] * cwv_saturation(sst, p)

    # Derin konveksiyon esigi SERBEST TROPOSFER sicakligina baglidir, yerel
    # kara yuzeyine degil. Tropikte troposfer sicakligini okyanus belirler
    # (Katman 2-3'teki WTG argumaninin aynisi). Yerel yuzeyi kullanmak Ganj
    # ovasinda kapasiteyi 55 mm'ye sisiriyor, esik 38.5 oluyor ve W=32.7 ile
    # esik asilamiyordu: model 0 mm veriyordu, gozlenen 300.
    cap_free = cwv_saturation(np.asarray(ocean_ref), p)

    # Derin konveksiyon COKME ile bastirilir. Subtropikal yuksek basincin
    # alcalan havasi konveksiyonu oldurur — Akdeniz yazinin kuru olmasinin
    # sebebi budur, nem eksikligi degil. Bu terim olmadan Iberya yazin yagis
    # aliyor ve bolge sistematik olarak 1.5 kat islak cikiyordu; ayni anda
    # muson bolgeleri (yakinsama) 0.3 kat kuru kaliyordu.
    div_s = grid.smooth(divergence(grid, u, v), p["convective_smooth_km"] / grid.cell_km)
    subsid_gate = np.exp(-np.maximum(0.0, div_s) / p["moist_subsid_scale"])

    # AKIS ENGELLENMESI (blocking). Alcak Froude sayisinda hava bir bariyeri
    # asamaz, etrafindan dolanir. Model bunu bilmezse nemli muson havasini
    # 5000 m Himalaya'nin uzerinden duz gecirir ve Tibet Platosu'na yagdirir:
    # olculdu, platoda 171 mm/ay (gozlenen 52-79) ve korelasyon NEGATIF.
    # Yol boyunca bir adimda kazanilan yukseklik ne kadar buyukse, o kadar az
    # nem karsiya gecer.
    # DIKKAT: grid.elev okyanusta deniz TABANI derinligidir. Havanin uzerinden
    # aktigi yuzey deniz seviyesinde kirpilmali; yoksa kiyiya gecerken -3000'den
    # +100'e 3100 m'lik sahte tirmanis cikiyor ve TUM nem kiyida engelleniyor
    # (olculdu: yagis her bolgede sifira dustu).
    surf = np.maximum(np.asarray(grid.elev), grid.world.sea_level_m)
    dz = surf - grid.sample(surf, src)
    # ESIK sart: engellenme yalnizca GERCEK bariyerlerde olmali. Esiksiz
    # kullanmak her kucuk tumsekte carpan uyguluyor, yuzlerce adimda birikip
    # nemi yok ediyordu (olculdu: yagis orani 0.02'ye dustu).
    through = np.exp(
        -np.maximum(0.0, dz - p["blocking_free_dz_m"]) / p["blocking_dz_m"])
    # Engellenen nem, bariyerin BULUNDUGU hucreye degil YUKARI-AKIS tarafina
    # birakilir: hava o hucreye zaten varamiyor. Bariyerin etkisi yuzlerce km
    # yukari-akisa uzanir (Ganj ovasinin islakligi Himalaya'nin onunde
    # zorlanmis yukselistendir), o yuzden birakim ayrica yumusatilir.
    si = np.clip(np.round(src[0]).astype(int), 0, grid.shape[0] - 1)
    sj = grid.wrap_j(np.round(src[1]).astype(int))
    # Sacilma-toplama duz indeksle: np.add.at yavastir, bincount 5.2 kat hizli
    # ve BIT BIT ayni sonucu verir (olculdu). Indeksler dongu boyunca sabit.
    _nyx = grid.shape[0] * grid.shape[1]
    _flat = (si * grid.shape[1] + sj).ravel()
    block_sigma = p["blocking_spread_km"] / grid.cell_km
    evap_gain = 1.0 - np.exp(-ds / p["evap_length_km"])
    ocean = ~grid.land

    # [P] Buharlasmanin AKI SINIRI. Yukaridaki gevsemede hava dengeye ne kadar
    # HIZLI yaklastigi yazili ama okyanusun saatte kac mm verebilecegi yazili
    # degil; gercekte yuzey enerji butcesi bunu keser. Sinirsiz hali modelin
    # kuresel su butcesini Dunya'nin iki katina cikariyor (2061 mm/yil, gercek
    # ~1000; docs/06 6.5b). Dunya kalibrasyonunda 0 = KAPALI birakildi: acmak
    # su butcesini duzeltirken Koppen skorunu dusuruyor ve o skor Dunya'da
    # dogrulamanin olcusu. Kurgusal dunyada o gerekce yok — orada olcu fizik.
    # Parsel bir adimi step_seconds'ta gecer, o yuzden aylik tavan adim
    # tavanina cevrilir.
    evap_max = float(p.get("evap_max_mm_month", 0.0))
    if evap_max < 0 or not np.isfinite(evap_max):
        raise ValueError(f"evap_max_mm_month={evap_max} negatif olamaz")
    adim_tavan = (evap_max * (ds * 1000.0 / speed) / SECONDS_PER_MONTH
                  if evap_max > 0 else None)

    # Kararli-hal cozumu. IKI BILESEN ayri tasinir:
    #   W = buhar, C = bulut suyu.
    # Buhar doygunlugu ASAMAZ: fazlasi aninda C'ye gecer. Bulut suyunun
    # `eff` kadari her adimda yagar, gerisi tasinir ve ruzgar altinda
    # kapasite yukselince BUHARA GERI DONER.
    #
    # Tek bilesenli sema (W = adv - eff*cond) calismiyordu: `eff` hem yagis
    # miktarini hem kuruma hizini kontrol ediyordu. Gercekci miktar icin
    # eff=0.03 gerekiyor, o zaman da hava kurumuyor ve YAGMUR GOLGESI
    # OLUSMUYORDU (olculdu: Kaskadlar'i asarken W 12.0'dan ancak 11.8'e
    # dusuyor, zirvenin dogusunda yagis gozlenenin 4 katı cikiyordu).
    through = through.astype(F)
    cap = cap.astype(F)
    w_eq32 = np.asarray(w_eq, dtype=F)
    cap_free = cap_free.astype(F)
    subsid_gate = subsid_gate.astype(F)
    W = np.where(ocean, w_eq32, F(0.0))
    C = np.zeros(grid.shape, dtype=F)
    fall = np.zeros(grid.shape, dtype=F)
    eff = p["precip_efficiency"]
    ed_sig = p["eddy_smooth_km"] / grid.cell_km
    ed_a = p["eddy_blend"]
    _soft = float(p.get("moist_crit_soft", 0.0))
    if _soft < 0 or not np.isfinite(_soft):
        raise ValueError(f"moist_crit_soft={_soft} negatif olamaz")
    crit_sig = _soft * cap_free if _soft > 0 else None   # cap_free dongude sabit
    # Yakinsama, girdap ve firtina yagisi (mm/ay). Anahtar kapaliyken dongu
    # SONRASI son W ile bir kez hesaplanir ve nemden DUSULMEZ (eski davranis:
    # kuresel su butcesi Dunya'nin ~2 kati, bu terimler yagisin ~%30'u).
    # conserve_moisture acikken her adimda hesaplanip tasinan nemden dusulur.
    # konvektif / yakinsama kaynakli yagis: ITCZ'yi ve subtropikal collerin
    # kuruluğunu bu terim uretir (yakinsama vs iraksama)
    # Iraksama BUYUK OLCEKTE degerlendirilir: konvektif sistemler ~300 km
    # olceginde orgutlenir, hucre olcegindeki gurultu yagis uretmez.
    conv = _soft_pos(-div_s, p["div_var_frac"] * float(np.sqrt((div_s ** 2).mean())))
    storm_c = float(p.get("storm_c", 0.0))
    if storm_c < 0 or not np.isfinite(storm_c):
        raise ValueError(f"storm_c={storm_c} negatif olamaz")
    firtina = None
    if storm_c > 0:
        # havanin uzerinden aktigi yuzeye kelepce: okyanusta elev deniz tabani
        z = np.maximum(np.asarray(grid.elev), grid.world.sea_level_m) - grid.world.sea_level_m
        t_ds = np.asarray(temp) + temperature_lapse(grid) * z / 1000.0
        land = grid.land
        n_k, n_o = land.sum(axis=1), ocean.sum(axis=1)
        t_k = np.where(land, t_ds, 0.0).sum(axis=1) / np.maximum(n_k, 1)
        t_o = np.where(ocean, t_ds, 0.0).sum(axis=1) / np.maximum(n_o, 1)
        karsit = np.where((n_k > 0) & (n_o > 0), t_o - t_k, 0.0)
        karsit = ndimage.gaussian_filter1d(karsit, p["storm_smooth_km"] / grid.cell_km, mode="nearest")
        f = 2.0 * grid.world.omega * np.abs(np.sin(np.radians(grid.lat))) / 1.0e-4
        w_ok = np.where(n_o > 0, np.where(ocean, w_eq32, 0.0).sum(axis=1) / np.maximum(n_o, 1),
                        float(w_eq32[ocean].mean()))
        sig_t = float(p.get("storm_contrast_sigma_k", 0.0))
        if sig_t < 0 or not np.isfinite(sig_t):
            raise ValueError(f"storm_contrast_sigma_k={sig_t} negatif olamaz")
        kusak = f * _soft_pos(karsit, sig_t) / 10.0 * np.power(w_ok / p["cwv_ref_mm"], p["conv_w_pow"])
        # YONLENDIRME: siklonlar yuzey ruzgariyla degil ~500 hPa akisiyla
        # tasinir. Kisin kita ustundeki yuksek basinc SIGDIR; yuzeyde ruzgari
        # denize cevirir ama ustteki bati akisini degistirmez. Ust akis termal
        # ruzgardan TURETILIR (basinc koordinatinda, g gerektirmez):
        #   u_500 = <u_yuzey> - (R/f) ln(1000/500) dT/dy
        # <.> zonal ortalama, T deniz seviyesine indirilmis. f ekvatora yakin
        # sifira gittigi icin |f| 10 derecedeki degerle tabanlanir (termal
        # ruzgar orada tanimsiz; kusak zaten f ile sondugu icin etkisiz).
        t_z = ndimage.gaussian_filter1d(t_ds.mean(axis=1), p["storm_smooth_km"] / grid.cell_km, mode="nearest")
        dtdy = -np.gradient(t_z) / grid.dy_m                  # lat kuzeyden guneye azalir
        om2 = 2.0 * grid.world.omega
        f_s = np.sin(np.radians(grid.lat)) * om2 * grid.world.rotation_sign
        f_s = np.where(f_s >= 0, 1.0, -1.0) * np.maximum(np.abs(f_s), om2 * math.sin(math.radians(10.0)))
        u_ust = np.asarray(u).mean(axis=1) - 287.0 / f_s * math.log(2.0) * dtdy
        u_st = np.broadcast_to(u_ust[:, None], grid.shape)
        src2 = _upwind_sampler(grid, u_st, np.zeros(grid.shape), ds)
        ornek2 = grid.sampler(src2, dtype=F)
        dz2 = surf - grid.sample(surf, src2)
        through2 = np.exp(-np.maximum(0.0, dz2 - p["blocking_free_dz_m"]) / p["blocking_dz_m"]).astype(F)
        st_decay = F(math.exp(-ds / p["storm_reach_km"]))
        S = ocean.astype(F)
        # Siklonlar ust akisa tam paralel gitmez, kuzey-guney yalpalar. Bu
        # olmadan zonal yonlendirme her sirtin dogusuna CETVEL GIBI yatay bir
        # golge ciziyordu (olculdu, 1 derece). Her adimda enlem yonunde kucuk
        # bir Gauss yayilmasi: toplam yayilma storm_reach_km yolda
        # storm_spread_km olur (difuzyon: adim sigmasi * sqrt(adim sayisi)).
        sig_adim = p["storm_spread_km"] * math.sqrt(ds / p["storm_reach_km"]) / (grid.dy_m / 1000.0)
        for _ in range(_needed_iters(grid, p)):
            S = np.where(ocean, F(1.0), ornek2(S) * through2 * st_decay)
            if sig_adim > 0.3:
                S = np.where(ocean, F(1.0), ndimage.gaussian_filter1d(S, sig_adim, axis=0, mode="nearest"))
        firtina = storm_c * kusak[:, None] * S

    def konv_orani(W_):
        nw = W_
        if p["conv_w_pow"] != 1.0:
            wr = p["cwv_ref_mm"]
            nw = wr * np.power(np.maximum(W_, 0.0) / wr, p["conv_w_pow"])
        r = p["convective_c"] * nw * conv * SECONDS_PER_MONTH
        if p["eddy_diff_m2s"] > 0:
            Ws = grid.smooth(W_, p["eddy_smooth_km"] / grid.cell_km)
            lap = grid.ddx(grid.ddx(Ws)) + grid.ddy(grid.ddy(Ws))
            r = r + np.maximum(0.0, p["eddy_diff_m2s"] * lap) * SECONDS_PER_MONTH
        if firtina is not None:
            r = r + firtina
        if p["conv_tau_min_days"] > 0:
            p_max = W_ * SECONDS_PER_MONTH / (p["conv_tau_min_days"] * 86400.0)
            r = np.minimum(r, p_max)
        return r

    # [P] NEM KORUNUMU. 0 = KAPALI (bit-birebir eski davranis). Acikken
    # yukaridaki uc terimin yagisi adim basina tasinan buhardan dusulur:
    # parsel hucreyi step_seconds'ta gecer, o surede r*step/ay kadar yagar.
    korunum = float(p.get("conserve_moisture", 0.0)) > 0
    step_seconds = ds * 1000.0 / speed
    adim_ay = (step_seconds / SECONDS_PER_MONTH).astype(F)

    for _ in range(_needed_iters(grid, p)):
        if ed_a > 0:
            W = ((1.0 - ed_a) * W + ed_a * grid.smooth(W, ed_sig)).astype(W.dtype)
        Wa = ornek(W)
        Ca = ornek(C)
        # Engellenen nem YOK OLMAZ, bariyerin ruzgar ustune yagar. Silmek
        # Himalaya'yi kurutuyordu (oran 0.09, katsayilardan bagimsiz); oysa
        # guney yamac dunyanin en yagisli yeridir, sebebi tam da engellenen
        # akisin orada zorunlu yukselmesidir. Bulut suyuna cevriliyor.
        blocked = Wa * (1.0 - through)
        Wa = Wa - blocked
        dep = np.bincount(_flat, weights=blocked.ravel(),
                          minlength=_nyx).reshape(grid.shape).astype(F, copy=False)
        if block_sigma > 0.5:
            dep = _boxblur(dep, block_sigma)
        Ca = Ca + dep
        ekle = (w_eq32 - Wa) * evap_gain
        if adim_tavan is not None:
            # yalniz POZITIF yon kirpilir: negatif taraf buharlasma degil,
            # havanin yuzeye nem birakmasidir ve enerji sinirina tabi degil
            ekle = np.minimum(ekle, adim_tavan)
        Wa = np.where(ocean, Wa + ekle, Wa)

        # doygunlugu asan buhar yogusur; eksik kalirsa bulut suyu buharlasir
        excess = Wa - cap
        cond_now = np.maximum(0.0, excess)
        evap_now = np.minimum(Ca, np.maximum(0.0, -excess))
        W = Wa - cond_now + evap_now
        C = Ca + cond_now - evap_now

        # Derin nemli konveksiyon. Gozlemsel iliski: yagis, sutun su
        # buharinin doygunluga ORANI kritik bir esigi asinca hizla artar
        # (Bretherton 2004). Bu terim olmadan model duz tropik ovalarda
        # SIFIR yagis veriyordu — Ganj ovasinda 0 mm, gozlenen 300-700.
        # Orografik terim yalnizca kaldirma varken calisir; muson yagmuru
        # ise ovada konvektiftir.
        if crit_sig is None:
            deep = np.maximum(0.0, W - p["moist_crit_frac"] * cap_free)
        else:
            deep = _soft_pos(W - p["moist_crit_frac"] * cap_free, crit_sig).astype(F, copy=False)
        conv_fall = p["moist_rate"] * deep * subsid_gate
        W = W - conv_fall

        if korunum:
            sink = np.minimum(W, konv_orani(W) * adim_ay).astype(F, copy=False)
            W = W - sink
            fall = eff * C + conv_fall + sink
        else:
            fall = eff * C + conv_fall
        C = C - eff * C
        # kara ustu evapotranspirasyon: dusen yagisin bir kismi geri doner
        W = np.where(ocean, W, W + p["land_recycle"] * fall)

    # yagan bulut suyu -> mm/ay. Parsel ds yolunu ds/U surede gecer.
    p_oro = fall / step_seconds * SECONDS_PER_MONTH

    if korunum:
        return p_oro, W
    p_conv = konv_orani(W)
    return p_oro + p_conv, W


def run(grid: Grid, temp, sst, ocean_ref, u, v, p: dict | None = None):
    """(12, ny, nx) mm/ay yagis ve sutun su buhari."""
    p = p or params(grid.world)
    n = len(temp)
    precip = np.empty((n, *grid.shape))
    cwv = np.empty((n, *grid.shape))
    for m in range(n):
        precip[m], cwv[m] = solve_month(grid, temp[m], sst[m], ocean_ref[m], u[m], v[m], p)
    return precip, cwv
