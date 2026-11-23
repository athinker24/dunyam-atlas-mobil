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
