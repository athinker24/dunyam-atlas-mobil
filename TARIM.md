# Tarımsal verimlilik

Arazi sekmesi → **Tarım**. `tarim/tarim.py` üretir (`data/tarim*.png`, `tarim.json`); `veri.yml`
ÜRETMEZ, elle koşulur (`python tarim/tarim.py`, ~1 dk; `bitki/_bitki.npz`, `toprak/_toprak.npz`,
`su/_su.npz` ve `buzul/_iklim_bugun025.npz` hazır olmalı).

Sahibinin sorusu ("verimlilik yalnız toprak türüyle belirlenmez") buradan cevaplanır. Yaşanabilirlikteki
gıda etkeninde toprak yalnız bir çarpandı; burada tarımın kendi dört etkeni var. Alan ağırlıklı yüzdeler.

## Etkenler (her biri 0-1)

| etken | ne ölçer | formül |
|---|---|---|
| Isı | büyüme sezonu ve sıcak ay | `ss(GDD5, 800, 2600) × (1 − ss(en sıcak ay, 34, 41))` |
| Su | yağmurdan nem oranı, kurak ay, yıkanma | `ss(AET/PE, 0.25, 0.70) × (1 − 0.5·ss(kurak ay, 4, 9)) × (1 − 0.3·ss(yağış, 2500, 4500))` |
| Toprak | WRB türünün tarımsal sırası | `ss(verim, 0, 0.8)`; verim `yasam.TOPRAK_VERIM` (Çernozem 1, Acrisol 0.45) |
| Arazi | sürülebilirlik ve ekin sınırı | `(1 − ss(eğim, 60, 300)) × (1 − ss(yükseklik, 2500, 4500))` |

`ss` pürüzsüz basamak. Birleşim **karekök(en zayıf etken × dört etkenin geometrik ortalaması)**: ortalama
telafi etmez (derin toprak kuraklığı kapatmaz), saf minimum ise tek iyi etkeni yok sayardı. Kartta en
zayıf etken "Sınırlayan" diye yazılır.

İki varyant, ayarlarda iki seçenekli:
- **Nehirle sulamalı** (varsayılan): nehir ve göl kıyısında su eksiği kapanır (nehir erişimi
  `yasam.su_agirligi`, geniş ve yumuşak profil; kurak ay cezası da orada azalır).
- **Yalnız yağmur**: sulama yok. Nil ve Mezopotamya burada çöle düşer.

Sınıflar (puan): Elverişsiz 0, Çok düşük 15, Düşük 35, Orta 55, Yüksek 78, Çok yüksek 92, Buz. Eşikler seçimdir.

## Dağılım (kara, alan ağırlıklı)

| sınıf | sulamalı | yalnız yağmur |
|---|---|---|
| Elverişsiz | 20.7 | 20.7 |
| Çok düşük | 4.1 | 4.1 |
| Düşük | 6.0 | 6.4 |
| Orta | 29.5 | 31.0 |
| Yüksek | 12.5 | 13.4 |
| Çok yüksek | 25.4 | 22.5 |
| Buz | 1.9 | 1.9 |

Kara ortalaması 60.4 / 59.5. En zayıf halka payı: Isı %43, Toprak %27, Su %19, Arazi %11.
Çok yüksek payı büyük çünkü Büyük Duvar'ın güneyindeki geniş alüvyon ovası bilerek verimli
(sahibi isteği, `TOPRAK.md`); Dünya'da "çok uygun" kara payı ~%10-15.

## Dünya sağlaması

Kaba normallerle (ezbere; `yasam.DUNYA_ORNEKLERI`), sulamalı / yalnız yağmur:

| bölge | puan | beklenen |
|---|---|---|
| Po, Kuzey Çin, Paris | 100 / 100, 100 / 83, 95 / 95 | çok verimli: doğru |
| Ukrayna (Çernozem) | 91 / 82 | çok verimli: doğru |
| Ganj ovası | 100 / 81 | iki ürün, verimli: doğru |
| Nil, Mezopotamya | 100 / 1, 97 / 1 | yalnız nehirle: doğru (çıkış noktası) |
| Etiyopya yaylası | 93 | teff ve tahıl yaylası: doğru |
| Yunnan | 71 | teraslı pirinç: makul |
| Amazon (Oksisol) | 65 | fakir toprak, ama yağmurla ekin yetişir; fazla yüksek olabilir |
| Kanada kalkanı | 18 | az tarım: doğru |
| Yakutsk | 32 | gerçekte daha düşük (kalıcı donmuş toprak modellenmiyor) |
| Sahra, Tibet | 1, 0 | doğru |

Bilinen sapmalar bilerek bırakıldı: kalıcı donmuş toprak (permafrost) ve gübre, makine, ekin türü,
ürün sayısı modelde yok. Burada yalnız doğal elverişlilik var, gerçek verim değil.
