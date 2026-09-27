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
| Bozkır (serin otlak) | %18 |
| Tropikal kuru orman ve savan | %17 |
| Maki ve sert yapraklı çalılık | %10 |
| Ilıman yaprak döken orman | %10 |
| Serin karışık orman | %8 |
| Tayga | %7 |
| Tropikal mevsimsel orman | %4 |
| Tundra | %2 |
| Buz ve kutup çölü | %2 |
| Soğuk yaprak döken orman | %2 |
| Soğuk çöl ve yarı çöl | %0.4 |

Tropikal yağmur ormanı %0: `k_itcz` 0.6 kararı (CLAUDE.md §2.2) Af'yi bilerek
sıfırlamıştı; bitki örtüsü bunu doğal olarak izliyor. Sıcak çöl ve sıcak
otlak da %0: sıcak yazlı yerlerde nem oranı 0.28'in altına inmiyor. Plato
bozkır (sahibinin isteği).

## Sıradaki

- Azonal örtü: büyük nehir boyunca galeri ormanı, delta ve göl kıyısında
  sazlık/bataklık (su katmanından).
- Toprak (sahibinin sırası: bitki → toprak → yaşanabilirlik → sonra kurgu
  etiketli toplumlar).
