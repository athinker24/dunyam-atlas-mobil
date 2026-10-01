# Tarımsal verimlilik

Arazi sekmesi → **Tarım**. `tarim/tarim.py` üretir (`data/tarim*.png`, `tarim.json`); `veri.yml`
ÜRETMEZ, elle koşulur (`python tarim/tarim.py`, ~1 dk; `bitki/_bitki.npz`, `toprak/_toprak.npz`,
`su/_su.npz` ve `buzul/_iklim_bugun025.npz` hazır olmalı).

Sahibinin sorusu ("verimlilik yalnız toprak türüyle belirlenmez") buradan cevaplanır. Yaşanabilirlikteki
gıda etkeninde toprak yalnız bir çarpandı; burada tarımın kendi dört etkeni var. Alan ağırlıklı yüzdeler.

## Etkenler (her biri 0-1)

| etken | ne ölçer | formül |
|---|---|---|
| Isı | büyüme sezonu, sıcak ay, kalıcı donmuş toprak | `ss(GDD5, 800, 2600) × (1 − ss(en sıcak ay, 34, 41)) × (1 − 0.7·ss(yıllık ort., −1, −9))` |
| Su | yağmurdan nem oranı, kurak ay, yıkanma | `ss(AET/PE, 0.25, 0.70) × (1 − 0.5·ss(kurak ay, 4, 9)) × (1 − 0.3·ss(yağış, 2500, 4500))` |
| Toprak | WRB türünün tarımsal sırası | `ss(verim, 0.05, 0.9)`; verim `yasam.TOPRAK_VERIM` (Çernozem 1, Acrisol 0.45 → 0.45) |
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
| Elverişsiz | 21.2 | 21.2 |
| Çok düşük | 3.7 | 3.7 |
| Düşük | 7.9 | 8.3 |
| Orta | 32.7 | 34.0 |
| Yüksek | 9.4 | 10.5 |
| Çok yüksek | 23.4 | 20.5 |
| Buz | 1.9 | 1.9 |

Kara ortalaması 57.3 / 56.4. En zayıf halka payı: Isı %38, Toprak %35, Su %18, Arazi %9.

**Çok yüksek payı neden büyük:** %23.4'ün 14.8 puanı Fluvisol (alüvyon), yani Büyük Duvar'ın
güneyindeki önülke ovası; bu ova karanın %17.4'ü (Dünya'da Fluvisol ~%3) ve sahibinin isteğiyle
verimli (`TOPRAK.md`). Ovanın dışında çok yüksek payı %8.6; Dünya'da "çok uygun" kara ~%10-15.
Eşikle düşürmek ovayı cezalandırırdı, o yüzden eşik değişmedi.

## Dünya sağlaması

Kaba normallerle (ezbere; `yasam.DUNYA_ORNEKLERI`), sulamalı / yalnız yağmur:

| bölge | puan | beklenen |
|---|---|---|
| Po, Kuzey Çin, Paris | 100 / 100, 100 / 83, 95 / 95 | çok verimli: doğru |
| Ukrayna (Çernozem) | 91 / 82 | çok verimli: doğru |
| Ganj ovası | 100 / 81 | iki ürün, verimli: doğru |
| Nil, Mezopotamya | 100 / 1, 96 / 1 | yalnız nehirle: doğru (çıkış noktası) |
| Etiyopya yaylası | 92 | teff ve tahıl yaylası: doğru |
| Yunnan | 60 | teraslı pirinç, yıkanmış toprak: orta |
| Amazon (Oksisol) | 54 | fakir, yıkanmış toprak: düşük-orta sınırı |
| Kanada kalkanı | 16 | az tarım: doğru |
| Yakutsk | 14 | kalıcı donmuş toprak: çok düşük |
| Sahra, Tibet | 1, 0 | doğru |

## Düzeltmeler (1 Ekim)

- **Yakutsk 32 → 14:** kalıcı donmuş toprak ısı etkenine eklendi (yıllık ortalama −1 °C'de başlar,
  −9 °C'de %70 kesinti). Sıcak yaz GDD'yi doldursa da kök bölgesi ve drenaj kısıtlı.
- **Amazon 65 → 54, Yunnan 71 → 60:** toprak eşlemesi 0-0.8 yerine 0.05-0.9; yıkanmış tropik toprak
  (Acrisol, Ferralsol) daha belirgin sınırlıyor, Çernozem ve Luvisol değişmedi.

Düzeltilemeyen, kapsam dışı: gübre, makine, ekin türü ve yılda ürün sayısı modelde yok. Burada yalnız doğal elverişlilik var, gerçek verim değil.
