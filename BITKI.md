# Bitki örtüsü

Doğal (potansiyel) bitki örtüsü: insan dokunmasaydı iklimin kuracağı biyom.
Üretici `bitki/bitki.py` (~20 s), çıktı `data/bitki.png` + `data/bitki.json`.
Uygulamada Arazi sekmesi → **Bitki örtüsü**; dokununca kartta biyom, ne olduğu,
Dünya'daki örnekleri ve nedeni (en soğuk ay, nem oranı).

**Veri iş akışı (veri.yml) bunu üretmez**: iklim değişirse
`python su/akim.py buzul/_iklim_bugun025.npz` sonrası `python bitki/bitki.py`
elle koşulur (iklim dosyası `buzul/iklim_kos.py` ile, `SU.md`).

## Yöntem (27 Eylül)

BIOME1 (Prentice vd. 1992) biyoiklim sınırlarından uyarlanmış kural tablosu;
eşikler `bitki/bitki.py` başındaki tabloda. Değişkenler kaynak arazi
çözünürlüğünde (~0.088°), su modeliyle aynı yoldan:

- en soğuk ay ve en sıcak ay ortalaması (sıcaklık yükseklikle 5.2 K/km düşer,
  ağaç sınırı kendiliğinden çıkar);
- GDD5 ve GDD0: 5 ve 0 °C üstü gün-derece (aylık ortalamadan);
- alfa = gerçek / olası buharlaşma (su modelinin Oudin PE'si ve 150 mm toprak
  kovası). BIOME1'de Priestley-Taylor alfası; aynı büyüklük.

Hiç erimeyen kar buz sayılır. Göl ve deniz boş.

**Denetlenmesi gereken:** eşikler makalenin Tablo 1'inden alındı, ama bu
oturumdan makaleye ağ kısıtı yüzünden erişilemedi; değerler yeniden
karşılaştırılmalı.

## Sonuç (kara alanına göre)

| biyom | pay |
|---|---|
| Ilık yaprak dökmeyen orman | %27 |
| Bozkır (serin otlak) | %14 |
| Ilıman yaprak döken orman | %10 |
| Maki ve sert yapraklı çalılık | %8 |
| Tropikal kuru orman ve savan | %8 |
| Serin karışık orman | %8 |
| Tayga | %7 |
| Tundra | %7 |
| Tropikal mevsimsel orman | %4 |
| Buz ve kutup çölü | %2 |
| Kurak çalılık ve dikenli savan | %2 |
| Soğuk yaprak döken orman | %2 |
| Kuru ağaçlık ve açık orman | %1 |
| Soğuk çöl ve yarı çöl | %0.4 |

## Köppen'le denetim (27 Eylül, sahibi: "savan çok mu oldu", "tekrar kontrol et, dünyamın bilgilerine uygun")

Biyom, motorun kendi Köppen sınıfıyla (`motor/koppen.py`, aynı ince ızgarada,
aynı aylık sıcaklık ve yağıştan) sınıf sınıf karşılaştırıldı. Bulunan dört
tutarsızlık ve düzeltmesi (`bitki.siniflandir` sonu):

1. **ET'nin yarısı bozkırdı.** BIOME1'in serin otu yalnız GDD0 >= 500 ister;
   Köppen ET'de (en sıcak ay < 10 °C) GDD5 medyanı 62, Tw 6.5 °C iken bozkır
   çıkıyordu. En sıcak ay < 10 °C ya da GDD5 < 350 olan otlak tundra: ET →
   %81 tundra, %10 buz. Kuzey kıyısı artık tundra.
2. **İlk savan düzeltmesi tropikte yanlıştı.** Yazı kurak ölçütü kendi
   hesabımla aranıyordu; tropikte kurak mevsim en sıcak aylara düştüğü için
   Aw'nin yarısı ve BSh'nin %92'si maki olmuştu (güneydeki şeritler de
   buradandı). Düzeltme yalnız Köppen Cs'de uygulanıyor.
3. **Cs dışında maki.** Sert yapraklı çalı (BIOME1) yağışı yazın olan kurak
   yerde (BSh, kurak Cw) Akdeniz makisi değil: yeni ad "Kurak çalılık ve
   dikenli savan" (Sahel, Caatinga benzeri).
4. **Am savan çıkıyordu.** Köppen Am muson ormanı iklimidir; nem oranı
   burada düşük (Am medyan 0.74 < 0.80), çünkü motorun yağışı Dünya'nınkinin
   iki katı mevsimsel (CLAUDE.md §8): yağış birkaç ayda boşalıp akışa
   gidiyor. Am → tropikal mevsimsel orman.

İkinci denetim (sahibi işaretli bölge: "iklim olarak çok az kısmı savan ama
tamamen kurak bitki örtüsü yazmışsın"):

5. **Tropik sınırı 18 °C (Köppen A).** BIOME1 tropik bitkileri en soğuk ay
   15.5 °C'den başlatır; kışı 15.5-18 °C olan C iklimleri (Cwa, Cwb, Cfa)
   tropik sayılıp savan çıkıyordu, atlasın iklim haritası oraya C diyor.
   Köppen'in 18 °C sınırı da sıcak isteyen (megaterm) bitkilerden türetildi.
6. **Kurak çalılık yalnız Köppen B'de.** İklimi kurak olmayan (Cw, Dw) ama
   nem oranı ormana yetmeyen yerde (0.28-0.65) yeni sınıf "kuru ağaçlık ve
   açık orman" (Hindistan'ın kuru yaprak döken ormanı, bushveld); Cf/Df (her
   ay yağışlı) yerde orman. İşaretli bölgede kurak örtü %52 → %12 (yalnız
   BS'de), savan %40 → %22 (bölgenin Aw payı %25). Görsel
   `bitki/bolge_kiyas.png`.

Denetim sonrası eşleşme (Köppen sınıfının kara alanında biyom payı):

| Köppen | pay | biyom |
|---|---|---|
| Am | %2.9 | %100 mevsimsel orman |
| Aw | %9.0 | %88 savan ve kuru orman, %12 mevsimsel orman |
| BSh | %1.5 | %81 kurak çalılık, %19 savan |
| BSk | %11.2 | %85 bozkır (plato), %6 tundra (yüksek) |
| Csa / Csb | %8.2 / %6.8 | %61 / %49 maki, gerisi ılık yaprak dökmeyen (daha nemli Akdeniz: pırnal, defne ormanı) |
| Cwa | %13.5 | %70 ılık yaprak dökmeyen, %21 ılıman yaprak döken, %9 kuru ağaçlık |
| Cwb | %10.9 | %89 ılık yaprak dökmeyen (yayla ormanı, Yunnan benzeri) |
| Dw* | %10.3 | karışık ve yaprak döken orman, tayga; %13 bozkır |
| Df* | %10.6 | yaprak döken, karışık, tayga; %13-21 bozkır (orman-bozkır geçişi) |
| Ds* | %4.4 | tayga ve bozkır (yazı kurak kıta içi) |
| ET | %6.7 | %81 tundra |
| EF | %1.3 | %100 buz |

Dünyam'a özgü kalanlar (hata değil): tropikal yağmur ormanı %0 (`k_itcz`
kararı, Af yok); ılık yaprak dökmeyen ormanın büyük olması Cw'nin baskınlığından
(motor sınırı: yağış çok mevsimsel, Cf azınlık); Dfc'nin %13'ü bozkır (Tc
−26 °C, nem oranı 0.62: permafrostun tuttuğu su hesaba girmiyor, gerçekte
Yakutya karaçam ormanıdır). Karşılaştırma görseli `bitki/denetim_kiyas.png`.

## Sıradaki

- Azonal örtü: büyük nehir boyunca galeri ormanı, delta ve göl kıyısında
  sazlık/bataklık (su katmanından).
- Toprak (sahibinin sırası: bitki → toprak → yaşanabilirlik → sonra kurgu
  etiketli toplumlar).
