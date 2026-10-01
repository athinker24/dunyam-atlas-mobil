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

Varsayılan (geniş, yumuşak): çok kıt %0.0, çok düşük %2.4, düşük %12.0, orta %17.3,
yüksek %13.8, çok yüksek %22.8, uç düzey %29.7, buz %1.9; kara ortalaması
1310 g/m²/yıl. Dar seçenekte uç düzey %28.5, kara ortalaması 1303.

## Nehir ve göl kıyısı (28 Eylül ve 1 Ekim, sahibi: "nehir çevreleri falan ayırdın mı", "tam alamamışsın", sonra "direkt yanları yapmayalım, iki seçenekli, varsayılan geniş ve yumuşak")

İlk sürümde yoktu. İkinci sürüm ham ızgaradaki q >= 50 hücrelerinin 1 hücre
çevresini aldı ama yanlıştı: uygulamada çizilen nehir ham ızgara yolu değil,
ortak kaydırma alanıyla kıvrılmış çizgi (`SU.md`), üstelik küçük kollar (kademe
2-4, 1385 nehirden 1341'i) hiç yoktu. Şimdi `data/su.json`'daki çizilen çizgilerin
kendisi ızgaraya işleniyor (`nehir_sinifi`: 1 < 200 m³/s, 2 < 2000, 3 >= 2000) ve
iki seçenek üretiliyor; uygulamada Yaşanabilirlik görünümünde "Nehir çevresi"
ayarı:

| seçenek | yarıçap (hücre ~9.7 km) | etki | su erişimli alan | kara ort. |
|---|---|---|---|---|
| Geniş, yumuşak (varsayılan, `yasam.png`) | 2.5 / 5 / 8, göl 3 | kosinüsle söner | %26.3 | 1310 |
| Nehrin yanı (`yasam_dar.png`) | 1 / 2 / 3, göl 1 | tam etki, keskin | %18.4 | 1303 |

Etki ağırlığı w (0..1) kadar AET olası buharlaşmaya (PE) yaklaşır: AET + w (PE − AET).
Yani nehre en yakın yerde su tavanı tamamen kalkar, uzaklaştıkça sıcaklık ve gerçek
buharlaşmanın verdiği tavana yumuşakça döner (galeri ormanı, vaha etkisi; sıcaklık
tavanı her zaman geçerli). Kartta w >= 0.25 olan yerde "nehir ya da göl kıyısı: su
erişimi var" satırı çıkar (R'nin 32 bitinde). Legend payları seçeneğe göre
(`pay`, `pay_dar`). Görsel doğrulama: koridor ile çizilen çizgiler üst üste
çizildi, hizalı. Gerçek taşkın ovası genişliği nehirden nehire çok değişir; yarıçaplar
kabaca ölçüdür. `su.json` yeniden üretilirse bu betik de koşulmalı.

## Sınırlar (bilerek kaba)

- Yalnız yıllık ortalama sıcaklık ve gerçek buharlaşma. Işık, büyüme mevsimi
  uzunluğu, toprak besini, eğim, yangın ve otlayıcı hesapta yok.
- Dünya'nın kara ortalaması bu yöntemle ~700 g/m²/yıl; buradaki 1256 iklimin
  ılık ve nemli, büyük sıcak çölün olmamasından. Hata değil, ama mutlak sayıyı
  Dünya'yla karşılaştırırken bunu bil.
- Tarımsal verimlilik ayrı bir soru (yalnız toprak türü belirlemez): toprak,
  eğim ve su erişimi ile ayrı katman olabilir, şimdilik bekletildi.
