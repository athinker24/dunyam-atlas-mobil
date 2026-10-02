# Hayvanlar

Yaşam bölümü → **Hayvanlar**. `hayvan/hayvan.py` üretir (`data/hayvan.png`, `hayvan_zengin.png`,
`hayvan_veri.png`, `hayvan.json`); `veri.yml` ÜRETMEZ, elle koşulur (`python hayvan/hayvan.py`, ~1 dk;
`bitki/_bitki.npz`, `su/_su.npz` ve `buzul/_iklim_bugun025.npz` hazır olmalı).

Sahibi 2 Ekim'de iki okumayı birlikte istedi ("İkisi de, iki seçenek"). Kurgu tür yok: harita hangi
**tür topluluğunun** ve ne kadar **çeşitliliğin** bu iklim ve araziyle uyuştuğunu gösterir; kartta
Dünya'dan tipik hayvanlar örnek olarak verilir. Dünyam'ın kendi türleri tanımlanmadı. Yüzdeler alan
ağırlıklı.

## 1. Topluluklar

Taban biyomdur (`bitki/bitki.py`, BIOME1). Üstüne iki yerel yaşam alanı biner:

- **Dağ:** yükseklik ≥ 2200 m ve yumuşatılmış eğim ≥ 120 (`toprak._egim`).
- **Sulak alan, nehir:** debi sınıfı ≥ 2 (≥ 200 m³/s) nehir yatağı bir hücre genişletilmiş ve göl
  kıyısı (1.5 hücre), 1200 m altında ve eğim < 80. Taslakta bütün nehirler alınınca karanın %17'si
  çıkıyordu; şimdi %7.

| topluluk | biyomlar | pay | Dünya'da tipik |
|---|---|---|---|
| Ilıman orman | ılık yaprak dökmeyen, ılıman yaprak döken, serin karışık, soğuk yaprak döken | 39.1 | kızıl geyik, yaban domuzu, boz ayı, kurt |
| Bozkır sürüleri | bozkır | 12.3 | yaban atı, saiga, bizon, step kartalı |
| Savan sürüleri | tropikal kuru orman ve savan, kurak çalılık, kuru ağaçlık | 10.3 | zebra, antilop, fil, aslan |
| Dağ | (yerel) | 9.3 | yaban keçisi, kar leoparı, yak |
| Maki | maki | 8.0 | yaban keçisi, kertenkele, kartal |
| Sulak alan, nehir | (yerel) | 7.2 | balıkçıl, flamingo, su samuru |
| Kuzey ormanı | tayga | 5.4 | sığın, kurt, vaşak, samur |
| Tropik orman | tropikal yağmur ve mevsimsel orman | 3.0 | primatlar, papağan, jaguar |
| Tundra göçmenleri | tundra | 2.8 | ren geyiği, kutup tilkisi, lemming |
| Buz | buz ve kutup çölü, buzul | 2.0 | (kıyıda fok) |
| Çöl | sıcak ve soğuk çöl | 0.4 | deve, çöl tilkisi, jerboa |

## 2. Tür zenginliği

Kaba ölçekte en iyi açıklayıcı su-enerji dengesi: gerçek buharlaşma (AET) ve birincil üretim; sıcak
bölgelerde su, soğukta enerji sınırlar (Hawkins vd. 2003, Ecology). Dağlık, parçalı arazi türleşmeyi
artırır (Rahbek vd. 2019, Science).

    R = ss(AET, 50, 1200)^0.6 × (0.35 + 0.65 ss(T, −8, 18)) × (1 + 0.45 ss(yükseklik std, 50, 700 m)) × (1 + 0.15 sulak) / 1.3

Yükseklik std 7×7 hücrelik pencerede. Sınıflar 0.2 adımla: çok düşük %22.9, düşük %14.4, orta %15.9,
yüksek %37.8, çok yüksek %6.8, buz %2.0.

Dünya sağlaması (kaba normaller, `hayvan.py` → `DUNYA`): Ekvador And yamacı 1.00, Himalaya eteği 1.00,
Amazon 0.83, Kongo 0.82, Serengeti 0.55, Akdeniz 0.48, Orta Avrupa 0.34, Kazak bozkırı 0.15, Yakutsk
0.03, Kuzey Kanada tundrası 0.03, Sahra 0.00. Sıralama gözlenen küresel desene uyuyor (And ve Himalaya
eteği dünyanın sıcak noktaları, Avrupa tropiklerin çok gerisinde).

## Sınırlar

- Topluluklar biyomdan türetildiği için biyom sınırları keskin; gerçekte geçiş kuşakları var.
- Ada etkisi (izole adada az tür, endemizm) ve göç engelleri (Büyük Duvar gibi) yok.
- Tür zenginliği bir göreli endeks, tür sayısı değil.
- Okyanus ve kıyı faunası yok.
