# Toprak türleri

WRB (Dünya Referans Temeli, FAO/IUSS 2015) referans grup adlarıyla, **bölgesel
(zonal) toprak** kavramına göre. Üretici `toprak/toprak.py` (~5 s), çıktı
`data/toprak.png` + `data/toprak.json` + `data/toprak_veri.png`. Uygulamada
Arazi sekmesi → **Toprak**; dokununca kartta tür, ne olduğu, Dünya'daki
örneği. Çizim yolu bitki örtüsüyle birebir aynı (`BITKI.md`): paletli PNG,
2× yumuşak argmax büyütme, kabartma "multiply" ile çarpılır.

**Veri iş akışı (veri.yml) bunu üretmez**: iklim ya da bitki örtüsü
değişirse `python toprak/toprak.py` elle koşulur, `bitki/_bitki.npz`,
`su/_akim.npz`, `su/_su.npz`, `su/_disa.pkl` ve `data/tektonik.json`'a bağlı.

## Yöntem (28 Eylül)

Klasik Dokuchaev fikri, WRB'nin ilk düzeyinde hâlâ izi var: her iklim/bitki
kuşağının kendi karakteristik toprağı olur. Taban tablo biyom kodundan
(`bitki/_bitki.npz`) toprak koduna:

| biyom | toprak | neden |
|---|---|---|
| tropik yağmur/mevsimsel orman | Ferralsol | şiddetle yıkanmış, demir/alüminyum oksitli |
| savan, kuru orman, kuru ağaçlık | Lixisol | belirgin kurak mevsim, kilin B ufkunda birikmesi |
| ılık yaprak dökmeyen orman | Acrisol | nemli (sub)tropik, asit, düşük baz doygunluğu |
| ılıman yaprak döken orman, maki | Luvisol | kil birikmeli, yüksek baz doygunluğu (Akdeniz "kırmızı toprağı" ayrı WRB grubu değil) |
| serin karışık orman | Cambisol | genç, az gelişmiş orman toprağı |
| tayga, soğuk yaprak döken orman | Podzol | iğne yapraklı, asit, kül-gri yıkanma ufku |
| bozkır, yıllık yağış ≥ 400 mm | Chernozem | nemli step, derin siyah, humusça zengin |
| bozkır < 400 mm, kurak çalılık | Kastanozem | kurak step, kestane rengi |
| tundra | Cryosol | donmuş katman 100 cm içinde |
| çöl (sıcak/soğuk) | Calcisol | kurak, kireç birikmeli |

Chernozem/Kastanozem 400 mm sınırı Dünya'da ölçülen aralığın (Chernozem
400-550, Kastanozem 200-450 mm/yıl, kaynak: Wikipedia "Kastanozem", FAO
toprak portalı) ortasına yakın; iki tür arada geçiş yapar, keskin bir eşik
gerçekte de böyle keskin değil ama motor kesikli biyom kodundan başlıyor.

Taban tablonun üstüne, sırayla (sonraki önceki geçersiz kılar):

1. **Dağlık → Leptosol.** Eğim eşiği üstü (bkz. kalibrasyon). Sığ, taşlı dağ
   toprağı — her yüksek dağ zincirinde aynı, iklimden bağımsız.
2. **Volkan kuşağı → Andosol.** `data/tektonik.json`'daki yay volkanları ve
   yarık hatlarının etrafı (aynı geometri, tektonik katmanla ortak). Taze
   volkanik külden, hafif ama verimli.
3. **Kapalı havza → Solonchak.** `su/`'nun dışa akışsız göl/çukur maskesinden
   ~55 km (6 hücre) içi, kıyı köpüğü düşük yerler (`alfa < 0.5`, kurumuş
   kıyı). Tuz birikimi.
4. **Taşkın ovası → Fluvisol.** Büyük nehir (debi ≥ 50, `su/disa.py`'deki
   "büyük nehir" eşiğiyle aynı) çevresi, düz (eğim < 25 m/hücre). Genç,
   tortul, her taşkında yenilenir.
5. **Buz/kalıcı kar → toprak yok** (kod 15, "Buz / çıplak kaya"). Motorun
   buzul maskesinden (`su/_akim.npz` → `buzul`).

## Eğim ve çözünürlük tuzağı (CLAUDE.md §7.2)

İlk koşuda ham `np.gradient` doğrudan kullanıldı: Leptosol payı %35.2 çıktı
ve haritada düz platoların içinde bile tuz-biber gibi dağınık benekler vardı
— dağ sırtlarına değil, tek hücrelik gürültüye oturuyordu. Bu tam olarak
§7.2'nin tarif ettiği tuzak: ince ızgarada (~0.088°, adım ~9.5 km) ham eğim
pürüzlü, kaba bir eşik onu ayıklayamıyor.

Düzeltme: `_egim()` artık eğimi 2 hücrelik Gauss ile yumuşatıyor (kodun
başka yerlerinde kabartma ve `KaydirmaAlani` için kullanılan aynı yarıçap).
Yumuşatılmış alanda kara için yüzdelik dilimler: 50. = 42, 70. = 108,
80. = 183, 85. = 250, 90. = 344, 95. = 498 m/hücre. Eşik 85. yüzdelik
dilime (`EGIM_ESIK = 220.0`) kalibre edildi: Leptosol %13.9'a indi ve
benekler dağ sırtlarına, levha sınırlarına ve yüksek platolara oturdu.

%13.9 Dünya'nın gerçek Leptosol payından (~%10-12) biraz yüksek — bilerek:
bu dünyanın karası Dünya'dan bilerek daha dağlık (kara medyanı ~950 m,
Dünya'da 377 m; CLAUDE.md §6), o yüzden daha fazla dağ toprağı beklenir.

## Sonuç (kara alanına göre, 28 Eylül)

| toprak | pay |
|---|---|
| Acrisol | %20.7 |
| Luvisol | %14.3 |
| Leptosol | %13.9 |
| Kastanozem | %9.5 |
| Fluvisol | %9.4 |
| Lixisol | %8.0 |
| Podzol | %5.8 |
| Cambisol | %5.9 |
| Ferralsol | %3.0 |
| Chernozem | %2.8 |
| Cryosol | %2.5 |
| Buz / çıplak kaya | %1.9 |
| Andosol | %1.8 |
| Calcisol | %0.3 |
| Solonchak | %0.3 |

Acrisol'ün büyüklüğü `BITKI.md`'deki gibi Cw'nin (ılık yaprak dökmeyen orman)
baskınlığından geliyor — motorun yağışı çok mevsimsel olduğu için Cf azınlık
kalıyor, biyom haritasında zaten böyleydi. Calcisol ve Solonchak küçük çünkü
bu dünyada gerçek sıcak çöl (BWh) ve kapalı havza azınlıkta.

## Alüvyon ovası (1 Ekim, sahibi: "duvarın güneyinin çok verimli olmasını istiyordum")

Duvar bir çarpışma dağı (Himalaya benzeri). Böyle bir dağın önündeki ova bir önülke
havzasıdır: dağdan inen nehirlerin tortusuyla dolar ve baştan sona alüvyondur (İndus-Ganj,
Po ovası, Mezopotamya). İlk sürümde alüvyon (Fluvisol) yalnız büyük nehrin 2 hücre
yanındaydı, ovanın geri kalanı iklimden Acrisol ya da Luvisol alıyordu; Duvar'ın güney
şeridi bu yüzden toprak 0.64'te kalıyordu.

Yeni kural (dağlık örtüsünden sonra, volkandan önce): yükseklik < 700 m, yumuşatılmış eğim
< 60 m/hücre, 4 hücrelik Gauss içinde nehir hücresi (debi >= 20 m³/s) payı >= 0.06 ve 2000 m
üstü araziye ~490 km (50 hücre) içinde olan kara Fluvisol. Eşikler bu ızgarada ölçülerek
seçildi: karanın %12.7'si, Duvar'ın güney şeridinin %36'sı. Fluvisol %9.4 → %17.4,
Acrisol %20.7 → %18.6. Yaşanabilirlikte Duvar'ın güney kuşağı kesintisiz "elverişli /
çok elverişli" oldu. Orada kalan sınır sıcaklık (yıllık ~20 °C, insan nişinin 13 °C
tepesinden uzak): fizik, değiştirilmedi.

## Sıradaki

Yaşanabilirlik (sahibinin sırası: bitki → toprak → yaşanabilirlik → sonra
kurgu etiketli toplumlar).
