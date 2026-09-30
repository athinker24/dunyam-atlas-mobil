# Genel yaşanabilirlik

İnsana özgü değil (sahibi 28 Eylül: "direkt insan için değil, genel şartlar"):
ölçü, iklimin bitki ve hayvan yaşamına verdiği üretim tavanı, yani **net birincil
üretim (NPP)**: bir yerin bir yılda bitki kütlesine çevirebileceği enerji. Besin
zincirinin tamamı buna yaslanır. Üretici `yasam/yasam.py` (~40 s), çıktı
`data/yasam.png` + `yasam_veri.png` + `yasam.json`. Uygulamada Arazi sekmesi →
**Yaşanabilirlik**; kartta sınıf, g/m²/yıl, yıllık ortalama sıcaklık ve sınırlayan
etken. Çizim yolu bitki örtüsü ve toprakla aynı (`BITKI.md`).

**Veri iş akışı (veri.yml) bunu üretmez**: iklim değişirse `python yasam/yasam.py`
elle koşulur (`buzul/_iklim_bugun025.npz`'yi okur, `su/akim.py` üzerinden).

## Yöntem

Miami modeli (Lieth 1975): iki bağımsız tavan, gerçek üretim küçük olanı
(Liebig'in en az etken yasası).

- sıcaklık tavanı: NPP_T = 3000 / (1 + exp(1.315 − 0.119 T)), T yıllık ortalama °C
- su tavanı: NPP_A = 3000 (1 − exp(−0.0009695 (AET − 20))), AET yıllık gerçek buharlaşma mm

Su tavanında Miami'nin yağış sürümü yerine Lieth'in buharlaşma sürümü var: motorun
yağışı Dünya'nınkinden fazla ve mevsimsel (CLAUDE.md §8), yağış formülü şişerdi.
AET, su modelinin toprak kovasından geçmiş buharlaşmasıdır (`bitki/` ile aynı).

Sınıflar mutlak NPP eşikleriyle (g kuru madde/m²/yıl): <50, 50-250, 250-600,
600-1000, 1000-1400, 1400-1750, >1750; kalıcı buz ayrı. İlk denemede üst sınıf
%44.7 çıktı (eşikler Dünya'ya göre, bu dünya ılık ve nemli); üst sınıf ikiye
bölünerek okunur hâle getirildi.

## Sonuç (kara alanına göre, 28 Eylül)

Çok kıt %0.0, çok düşük %2.4, düşük %12.0, orta %17.7, yüksek %14.6, çok yüksek
%25.1, uç düzey %26.3, buz %1.9. Kara ortalaması 1281 g/m²/yıl; alanın %29'unda
sıcaklık, geri kalanında su sınırlayıcı.

## Nehir ve göl kıyısı (28 Eylül, sahibi sordu: "nehir çevreleri falan ayırdın mı")

İlk sürümde yoktu; yalnız yıllık sıcaklık ve AET vardı. Şimdi büyük nehrin
(debi >= 50) 1 hücre (~9 km) çevresi ve göl kıyısı su erişimli sayılır: AET,
olası buharlaşma (PE) düzeyine çıkar, yani su tavanı kalkar, sıcaklık tavanı
kalır. Karanın %10.6'sı bu bölgede, ortalama artış 240 g/m²/yıl. Kartta
"nehir ya da göl kıyısı: su erişimi var" satırı çıkar (R'nin 32 bitinde).
Gerçek taşkın ovası genişliği bundan çok daha değişken; 1 hücre kabaca ölçüdür.

## Sınırlar (bilerek kaba)

- Yalnız yıllık ortalama sıcaklık ve gerçek buharlaşma. Işık, büyüme mevsimi
  uzunluğu, toprak besini, eğim, yangın ve otlayıcı hesapta yok.
- Dünya'nın kara ortalaması bu yöntemle ~700 g/m²/yıl; buradaki 1256 iklimin
  ılık ve nemli, büyük sıcak çölün olmamasından. Hata değil, ama mutlak sayıyı
  Dünya'yla karşılaştırırken bunu bil.
- Tarımsal verimlilik ayrı bir soru (yalnız toprak türü belirlemez): toprak,
  eğim ve su erişimi ile ayrı katman olabilir, şimdilik bekletildi.
