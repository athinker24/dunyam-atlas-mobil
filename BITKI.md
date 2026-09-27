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
| Ilık yaprak dökmeyen orman | %20 |
| Maki ve sert yapraklı çalılık | %19 |
| Bozkır (serin otlak) | %18 |
| Ilıman yaprak döken orman | %10 |
| Tropikal kuru orman ve savan | %8 |
| Serin karışık orman | %8 |
| Tayga | %7 |
| Tropikal mevsimsel orman | %4 |
| Tundra | %2 |
| Buz ve kutup çölü | %2 |
| Soğuk yaprak döken orman | %2 |
| Soğuk çöl ve yarı çöl | %0.4 |

**Yazı kurak düzeltmesi (27 Eylül, sahibi: "savan çok mu oldu"):** BIOME1
yağışın zamanına bakmaz; kışı ılık (en soğuk ay >= 15.5 °C) ama yağışı kışın
düşen yerleri de tropik savan sayıyordu. Savanın yarısı (karanın %8.9'u)
böyleydi. Köppen Cs ölçütüyle (sıcak yarının en kurak ayı < 40 mm ve soğuk
yarının en yağışlı ayının üçte birinden az) bu yerler maki oldu: savan
%17 → %8 (Köppen Aw %8.9), maki %10 → %19 (Köppen Cs %15). Güneyde maki ile
savan enlem boyunca şeritler hâlinde değişiyor: basınç kuşaklarının yıllık
salınımından (CLAUDE.md §8), yağış rejimi enlemle ters dönüyor. Karşılaştırma
`bitki/savan_kiyas.png`.

Tropikal yağmur ormanı %0: `k_itcz` 0.6 kararı (CLAUDE.md §2.2) Af'yi bilerek
sıfırlamıştı; bitki örtüsü bunu doğal olarak izliyor. Sıcak çöl ve sıcak
otlak da %0: sıcak yazlı yerlerde nem oranı 0.28'in altına inmiyor. Plato
bozkır (sahibinin isteği).

## Sıradaki

- Azonal örtü: büyük nehir boyunca galeri ormanı, delta ve göl kıyısında
  sazlık/bataklık (su katmanından).
- Toprak (sahibinin sırası: bitki → toprak → yaşanabilirlik → sonra kurgu
  etiketli toplumlar).
