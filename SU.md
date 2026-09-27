# SU — Dünyam'ın gölleri ve nehirleri

Buzul geçmişinden (`BUZUL.md`) sonraki katman. Sayılar `su/su.json`'da
(makine için), harita `su/su_haritasi.png`. Hepsi iklim motorunun bugünkü
0.25° ikliminden ve su dengesinden türetildi; göl ve nehir elle konmadı.

## Kararlar (27 Eylül, sahibi: "fırça izlerini görmezden gel, gerçekçi bir sayı belirle")

| ne | değer | neden |
|---|---|---|
| arazi | fırça ölçeği (10-30 km) yumuşatıldı (`su/duzelt.py`) | çizimdeki fırça darbeleri paralel cetvel nehirler ve binlerce minik göl üretiyordu |
| eşik aşınması | 200 m | taşan gölün çıkışı eşiği zamanla kazar; eşiği 200 m'den sığ çukur boşalmış sayılır. Aşınmasız hâlde göller karanın %7.3'ü (3.248 göl), Duvar'ın güney ovası Hazar büyüklüğünde tuzlu iç deniz oluyordu (`su/secenekler.png`) |
| en küçük göl | 300 km² (buzul gölü 100 km²) | küçük lekeler fırçadan |
| göl payı | karanın **%1.68**'i, 95 göl | Dünya %1.8 (HydroLAKES, Messager vd. 2016) |
| nehir | debi ≥ 50 m³/s veri, ≥ 100 m³/s ve ≥ 120 km haritada | kısa yamaç derecikleri kıta ölçeğinde gürültü |

## Uygulamada

`data/su.json` (`su/disa.py`, `su/uret_su.py` sonunda yazar; ~210 KB).
Nehirler kol kol: her ağızdan ana kol kaynağa kadar, ona katılan her kol
ayrı. Kademe: 1 = Q ≥ 2000 m³/s ya da ≥ 1500 km (40 kol), 2 = ≥ 600 ya da
≥ 600 km, 3 = ≥ 200 ya da ≥ 250 km, 4 = ≥ 50 m³/s. Uygulama uzaktan yalnız
1'i çizer, yakınlaştıkça (2.6×, 5×, 10×) diğerleri yumuşakça belirir;
"Bütün kollar" hepsini çizer. Kalınlık debiyle akış yönünde artar. Su
denizin kendi renkleriyle çizilir (sığ ton, kıyı köpüğü; büyük kollarda
kıyıdaki gibi hafif ışıltı); tuz gölü kurumuş kum tonu, noktasız ince kıyı.
Nehir çizgisi: basamaklar silinir, köşeler yuvarlanır, uzun dalga boylu
hafif menderes (ovada belirgin, dağda az). Göle ya da nehre dokununca
kartta alan/derinlik/yüzey ya da o noktadaki debi. **Veri iş akışı
(veri.yml) bu dosyayı üretmez**: iklim değişirse yukarıdaki komutlar elle
koşulur.

## Su bütçesi (kara, alan ağırlıklı)

Yağış 958 mm/yıl, buharlaşma 652, akış **307** (akış/yağış 0.32; Dünya
karası ~0.35-0.40).

## En büyük nehirler

| debi (m³/s) | boy (km) | havza (km²) | kaynak | ağız |
|---|---|---|---|---|
| 19.510 | 2.064 | 0.56 milyon | 11 (Alt Kıta orta kuşağı) | 3.1°K 18.3°D |
| 14.938 | 3.507 | 2.63 milyon | 7 (Alt Kıta doğu kıyısı sırası) | 26.3°K 4.1°D |
| 14.808 | 2.960 | 2.82 milyon | 10 (Güneybatı platosu) | 18.2°K 20.6°B |
| 13.964 | 1.430 | 0.46 milyon | 10 (Güneybatı platosu) | 2.1°K 28.6°B |
| 12.419 | 1.609 | 0.64 milyon | meseta (İber yaylası) | 37.0°K 11.7°B |
| 11.976 | 4.275 | 2.46 milyon | 5 (İber kuzey sırası) | 26.6°K 32.2°B |
| 10.858 | 1.101 | 0.29 milyon | yarımada (Yarımada omurgası) | 1.6°K 9.7°B |
| 8.196 | 758 | 0.17 milyon | yarımada (Yarımada omurgası) | 4.4°K 2.6°B |

Karşılaştırma: Mississippi ~17.000, Ganj-Brahmaputra ~38.000, Kongo ~41.000 m³/s.
Duvar'ın güneyindeki ova kuru bir ova olarak kaldı: Duvar'dan inen sayısız
dere eteğe paralel akan ova nehrinde birleşip iç denize dökülüyor (Ganj
ovası gibi).

## Plato kolu, tatlı göl ve tuz gölü (sahibin isteği, kurgu)

Sahibi haritaya çizdi: "bozkırda platoya büyük bir kol, o kadar dağ var
oralarda"; sonra "platoya göl", "ikisi birlikte, tatlı göl 10.000 km²",
"küçük tuz gölü". Tasarımlar `su/duzelt.py`'de (`KURGU_NEHIRLER`,
`TATLI_GOL`, `TUZ_GOLU`); göl seviyeleri ve debiler yine su dengesinden.

- **Plato kolu:** plato doğusundan (49.4°K 17.5°D) batıya plato boyunca
  akar, 1'in güney ucu ile Duvar'ın batı ucu arasındaki ~2.250 m'lik sırtı
  bir boğazla keser, iç denize (36.4°K 8.0°B) dökülür. Yol çizilen hattın
  ~100 km'lik koridorunda en alçak geçitten geçer. Hikâye: öncül nehir;
  sırt yükselirken yatağını kazdı (İndus, Arun, Kolorado gibi), buzul
  erimesinde taşan plato suyu boğazı derinleştirdi.
- **Tatlı göl (10.066 km², 248 m derin, 792 m'de):** boğaz ağzının önünde,
  sert kaya eşiğinin tuttuğu bir çöküntü havzası. Nehir onu besler (yılda
  14.5 km³), yüzeyinden ~6.8 km³ buharlaşır, kalanı eşikten boğaza taşar:
  **~260 m³/s**. Platonun tek büyük tatlı suyu. Balkaş'ın üçte ikisi.
- **Tuz gölü (4.050 km², 102 m derin, 667 m'de, kapalı):** kuzeydeki
  dağlardan (2) inen kolun aşağı ucunda (48.5°K 14.5°D). Kol yılda ~2.6 km³
  getirir, göl bunu buharlaştıracak büyüklükte dengelenir ve taşmaz; kol
  artık plato koluna katılmaz. Büyük Tuz Gölü (Utah) boyutunda.
- **Su bütçesi sınırı:** plato kurak (yağış ~230-290 mm, açık su yılda
  ~970 mm buharlaştırır); nehrin suyu çevre dağlardan. Eski büyük tuz gölü
  (18.500 km²) yılda 12.5 km³ harcardı, tatlı göle yetecek su kalmazdı; bu
  yüzden tuz gölü küçük seçildi. Daha çok su istenirse 9 yarığının kapalı
  tuz gölleri (~46 km³/yıl) plato koluna bağlanabilir; o zaman o göller
  tatlanır ya da kurur.
- Ağızda, boğazdan sonra kıyı ovasının kollarıyla: 8.160 m³/s.

## Göller

- **Köken:** 51 buzul gölü (moren seti; Duvar'ın güney eteğinde dar, uzun,
  Garda/Como türü), 5 yarık gölü, 39 havza gölü. 24 tanesi kapalı ve tuzlu.
- **En büyükler:**
  - Duvar'ın kuzey eteğindeki kapalı havzada (35.7°K 27.4°D, 1.820 m)
    81.900 km², 404 m derin **tuz gölü**: Duvar'ın kuzey yüzünün eriyen
    kar ve buz suyu kurak platoda burada biter (Tarım havzası ve eski Lop
    Nur türü; Aral'ın 1960 öncesi 68.000 km²).
  - Alt Kıta orta kuşağında 78.400 km² tatlı göl (224 m derin, 1.370 m'de;
    Victoria'dan büyük).
  - 9 boyunca 73.800 km² kapalı tuz gölü (44.8°K 28.9°D).
  - 9 yarığının güney ucunda 56.800 km², **557 m derin** yarık gölü (Baykal
    türü, tatlı); kuzey ucunda 42.200 km² kapalı yarık gölü.
  - 2'nin dağlarında 814 m derin bir dağ gölü.
- Buzul çağında buzun kazıdığı yerlere oyulan 84 oluktan 66'sı su tutuyor,
  51'i 100 km² üstünde. Duvar'ın kuzey yüzündekiler (kurak plato) çoğunlukla
  kuru ya da kapalı.

## Deltalar (27 Eylül, `su/delta.py`)

Nehrin çökel akısı ile ağızdaki dalganın dengesi. Çökel BQART'tan
(Syvitski ve Milliman 2007: debi, havza alanı, en yüksek nokta, havza
sıcaklığı, buzul payı, göllerin tuttuğu pay); dalga ağızdaki yıllık rüzgâr
hızı ve açık su mesafesinden (SPM 1977). Gösterge X = çökel / H^2.4
(Nienhuis vd.); eşikler Dünya örnekleriyle kaba ayarlı (Mississippi ~300,
Nil ~45, açık kıyıda küçük nehir ~1). **Gelgit bilinmiyor** (Dünyam'ın ayı
tanımlı değil): Ganj türü gelgit deltası değerlendirilemez.

- 132 delta: 16 nehir baskın (kuş ayağı / loblu), 52 yay biçimli, 64 küçük;
  23'ü göle dökülür. Sayılar `su/deltalar.json`.
- En büyükler: ova nehri (26.3°K 4.1°D, iç deniz) yılda ~730 milyon ton,
  Ganj-Brahmaputra'nın doğal hâli ~1.000; güneybatı platosu nehri
  (18.2°K 20.6°B) ~720, çok korunaklı kıyı (H ~0.5 m); Alt Kıta'nın büyük
  nehri (3.1°K 18.3°D) ~270.
- İç deniz korunaklı (dalga ~0.5-1 m): büyük deltaların çoğu orada.
  1'den gelen en büyük debili nehir (37.1°K 11.7°B) açık, dalgalı kıyıya
  (~3 m) döküldüğü için yalnız küçük, dalga baskın delta yapar.
- Göl deltaları: plato kolunun tatlı göle girdiği yerde (~30 Mt/yıl,
  Selenga-Baykal türü) en büyüğü; kapalı tuz göllerinde iç deltalar.
- Uygulamada: ağızda yelpaze gibi açılan 2-5 kol (96 delta; tepe ağızdan
  12·Qs^0.45 km yukarıda). **Kolların yeri ve biçimi tasarımdır**: ~10 km'lik
  arazi dağıtıcı kolları çözmez; deltanın varlığı ve büyüklüğü hesaptan.
  Nehir baskın 1., yay biçimli 2., küçük 3. kademede görünür. Dokununca
  kartta Delta satırı. Yeniden üretmek: `python su/delta.py` (uret_su.py'den sonra).

## Yöntem ve sınırlar

- **Akış** (`su/akim.py`): aylık kar kovası (uygulamayla aynı eşikler) ve
  toprak kovası (150 mm); buharlaşma gücü Oudin vd. 2005 (gezegenin
  ışınımı ve sıcaklık); göl buharlaşması tamamlayıcı ilişkiyle
  (E_göl = 2·PE − AET, Bouchet 1963 / Morton 1983): kurak havzada ~1000 mm.
- **Göller** (`su/gol.py`): taşma ağacı (Fill-Spill-Merge, Barnes vd.
  2021 benzeri). Göl, yatağındaki Σ(E − P + R) gelen akışa eşitlenince
  dengede; fazla eşikten kardeş çukura ya da denize taşar.
- **Nehirler** (`su/nehir.py`): göllü yüzeyde öncelikli su basma; aşınmış
  çukurda su dibe inip tek kanalla çıkar; yan yana paralel akan küçük dere
  büyüğüne katılır. Çizim: basamaklar Ramer-Douglas-Peucker ile silinir,
  çok ölçekli kıvrım ve Chaikin (belirlenimci tohum). **Kıvrımlar
  tasarımdır**, arazinin ~10 km çözünürlüğünün altındaki ayrıntı ölçülmedi.
- Sınır: aylık akış rejimi (hangi ay taşar) henüz hesaplanmadı; göllerin
  kıyı çizgisi ~10 km hücrelerden.

Yeniden üretmek:

```bash
python buzul/iklim_kos.py --res 0.25 --cikti buzul/_iklim_bugun025.npz   # ~16 dk
python buzul/iklim_kos.py --res 0.5 --dT -6 --deniz -120 --egiklik 22 --cikti buzul/_iklim_6e22.npz
python su/akim.py buzul/_iklim_bugun025.npz
python su/uret_su.py
```
