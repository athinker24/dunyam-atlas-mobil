# İklim denemeleri (arazi sabit) — `deney-iklim` dalı

Arazi `arazi-ana-2` (sahibin ana haritası, son sürüm) olduğu gibi; yalnız `dunya/dunyam.json` → `params`
ve `dunya/dunyam.currents.json` bellekte değiştirilir, dosyalar değişmez.

    python deney/tara.py ad '{"convective_c": 0.20}' 0.5            # params
    python deney/tara.py ad '{"akinti": {"Jir 2 dogu": {"anomaly_c": -2}}}' 0.5   # akıntı (ad öneki)
    python deney/ciz.py "taban_0.5|başlık" "ad_0.5|başlık" ...       # deney_1.png gibi panel

Önce `taban` koşulmalı (sınıfı değişen payı ona göre). Sonuçlar `deney/sonuc.jsonl`'a eklenir.
Ölçüt: bozkır bölgesi (37-49°K, 5°B-28°D) bozkır payı; main %43 (0.25°), bu arazide %32 (0.25°), %25.8 (0.5°).
0.5° taraması yönü gösterir; seçilen kol 0.25°'de doğrulanmalı (CLAUDE.md §7.2: engellenme çözünürlüğe bağlı).

## 1. tarama (23 Kasım, 0.5°, tek tek)

| deneme | bölge yağışı | bölge bozkırı | B | bölge dışı sınıf değişen |
|---|---|---|---|---|
| taban | 498 | 25.8 | 7.3 | — |
| convective_c 0.20 | 455 | 48.4 | 13.5 | 9.0 |
| monsoon_k 0.9 | 478 | 37.8 | 9.5 | 13.6 |
| eddy_blend 0.01 | 449 | 33.6 | 10.0 | 13.4 |
| land_recycle 0.5 | 438 | 31.6 | 9.4 | 11.4 |
| blocking_dz_m 600 | 465 | 30.8 | 8.4 | 4.2 |
| blocking_spread_km 2000 | 431 | 30.2 | 8.2 | 5.5 |
| rh_ocean 0.70 | 454 | 30.3 | 9.5 | 7.0 |
| batı kıyı akıntısı −2 °C | 487 | 26.7 | 9.4 | 5.4 |
| batı kıyı akıntısı 0 | 491 | 26.4 | 8.0 | 3.1 |
| jir akıntıları ×0.5 | 496 | 25.7 | 7.4 | 2.4 |
| storm_c 40 | 502 | 25.8 | 9.3 | 6.9 |
| k_itcz 0.5 | 548 | 14.1 | 7.4 | 21.1 |

Akıntılar bölgeye neredeyse etkisiz. En güçlü kol convective_c (bedeli dünya genelinde kurak payı);
bölge dışına en az dokunan engellenme.

## 2. birleşimler (23 Kasım)

0.5°'de: engellenme 600 + yayılım 2000 %36.1 (dışı %8.8); 450 + 2000 %42.3 (%11.1); 600 + 2000 + muson 1.1
%46.9 (%13.6). 0.25°'de engellenme çok daha sert (§7.2), hedefi aştı; daha yumuşakları 0.25°'de doğrudan
denendi (`deney_2.png`):

| deneme (0.25°) | bölge bozkırı | bölge yağışı | B | bölge dışı sınıf değişen |
|---|---|---|---|---|
| şimdiki | 32 | 474 | 10.1 | — |
| blocking_dz_m 700 | 36.8 | 462 | 11.3 | 3.4 |
| blocking_dz_m 750 + blocking_spread_km 1600 | 40.3 | 416 | 12.0 | 6.4 |
| blocking_spread_km 2000 | 40.0 | 410 | 12.5 | 7.6 |
| 600 + 2000 | 52.5 | 396 | 15.4 | 11.4 |
| 600 + 2000 + monsoon 1.1 | 59.0 | 381 | 16.5 | 15.3 |

Hedefe (main %43) en yakın, bedeli en düşük: blocking_dz_m 750 + blocking_spread_km 1600. Bozkır
platonun güneyindeki şeride de yayılıyor (B'nin artışının bir kısmı oradan).

## 3. Akdeniz'i azaltmak (24 Kasım, taban engellenme 700)

Akdeniz (Cs) kuşak salınımından (k_itcz, yazı kurutur) ve kış fırtına yağışından (storm_c, kışı ıslatır) gelir.
0.5°'de (taban Cs %18.8, bölge bozkırı %28.6): storm_c 40 Cs %16.4 (bozkır %29.4, B +2.0, dışı %7.2);
storm_c 25 %14.4 (%29.7, B +3.3, %12.1); storm_contrast_sigma_k 5 %17.0 (%27.7, B +0.8, %6.6).
Bozkırı geri götürenler (elendi): k_itcz 0.55 (bozkır %21), belt_shift_decay 0.1 (%15), convective_c 0.32
(%20), monsoon 1.6 (%22.5). Akdeniz'den çıkan alan çoğunlukla Cwa'ya geçer (kış kurak olur).

0.25° (`deney_3.png`; taban Cs %18.2, bozkır %36.8, B %11.3):

| deneme | Cs | bölge bozkırı | B | bölge dışı değişen |
|---|---|---|---|---|
| storm_c 40 | 16.1 | 37.1 | 13.4 | 6.7 |
| storm_contrast_sigma_k 5 | 16.6 | 35.5 | 12.0 | 5.7 |

İkisinde de kurağa geçen alanın çoğu ~45°K 10°B çevresi (Dsc, Dsb, Dfb, ET: kışı fırtına yağışıyla ıslanan
kuzeybatı). storm_c sahibinin "kış yağışı ve kar çok az" isteğinden (`_firtina`); azaltmak kışı kurutur.
