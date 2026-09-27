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
| göl payı | karanın **%1.25**'i, 92 göl | Dünya %1.8 (HydroLAKES, Messager vd. 2016) |
| nehir | debi ≥ 50 m³/s veri, ≥ 100 m³/s ve ≥ 120 km haritada | kısa yamaç derecikleri kıta ölçeğinde gürültü |

## Su bütçesi (kara, alan ağırlıklı)

Yağış 958 mm/yıl, buharlaşma 652, akış **307** (akış/yağış 0.32; Dünya
karası ~0.35-0.40).

## En büyük nehirler

| debi (m³/s) | boy (km) | havza (km²) | kaynak | ağız |
|---|---|---|---|---|
| 19.510 | 2.064 | 0.56 milyon | 11 (Alt Kıta orta kuşağı) | 3.1°K 18.3°D |
| 14.808 | 2.960 | 2.82 milyon | 10 (Güneybatı platosu) | 18.2°K 20.6°B |
| 13.964 | 1.430 | 0.46 milyon | 10 (Güneybatı platosu) | 2.1°K 28.6°B |
| 13.826 | 3.410 | 2.35 milyon | 7 (Alt Kıta doğu kıyısı sırası) | 26.3°K 4.1°D |
| 12.419 | 1.609 | 0.64 milyon | meseta (İber yaylası) | 37.0°K 11.7°B |
| 11.976 | 4.275 | 2.46 milyon | 5 (İber kuzey sırası) | 26.6°K 32.2°B |
| 10.858 | 1.101 | 0.29 milyon | yarımada (Yarımada omurgası) | 1.6°K 9.7°B |
| 8.375 | 4.271 | 3.84 milyon | 3 (Duvar) | 36.4°K 8.0°B |

Karşılaştırma: Mississippi ~17.000, Ganj-Brahmaputra ~38.000, Kongo ~41.000 m³/s.
Duvar'ın güneyindeki ova kuru bir ova olarak kaldı: Duvar'dan inen sayısız
dere eteğe paralel akan ova nehrinde birleşip iç denize dökülüyor (Ganj
ovası gibi).

## Plato kolu (sahibin isteği, kurgu)

Sahibi haritaya çizdi: "bozkırda platoya büyük bir kol, o kadar dağ var
oralarda". Nehir plato doğusundan (49.4°K 17.5°D) batıya plato boyunca
akar, 1'in güney ucu ile Duvar'ın batı ucu arasındaki ~2.250 m'lik sırtı
bir boğazla keser ve iç denize (35.7°K 8.3°B) dökülür. Yol çizilen hattın
~100 km'lik koridorunda en alçak geçitten geçer (`su/duzelt.py`
`KURGU_NEHIRLER`).

- **Hikâye:** öncül nehir. Sırt yükselmeden önce de oradaydı ve yükselirken
  yatağını kazdı (İndus, Arun, Kolorado gibi); buzul erimesinde taşan plato
  suyu boğazı derinleştirdi. Plato çanağının dibindeki tuz gölü bu yüzden
  yok: çanak artık bu nehre boşalıyor.
- **Debi:** plato kurak (yağış ~300 mm, akış ~0), su çevre dağlardan gelir.
  Boğazda ~600 m³/s (Amu Derya'nın tarihsel debisi ~1.400, Ren 2.300); boğazdan
  sonra nemli kıyı ovasının kollarıyla ağızda **8.400 m³/s**. Kurak bölgeyi
  geçen "yabancı nehir" (Nil, Amu Derya türü).
- Platodaki kapalı tuz gölleri (Duvar'ın kuzey eteği ve 9 boyunca) bu nehre
  bağlı değil; toplam girdileri ~1.470 m³/s. Bağlanırlarsa boğazdaki debi
  ~2.000 m³/s olur, ama o zaman 9 yarığının tuz gölleri tatlanır ya da kurur.

## Göller

- **Köken:** 51 buzul gölü (moren seti; Duvar'ın güney eteğinde dar, uzun,
  Garda/Como türü), 5 yarık gölü, 36 havza gölü. 27'si kapalı ve tuzlu.
- **En büyükler:** Alt Kıta orta kuşağında 78.400 km² tatlı göl (224 m
  derin, 1.370 m'de; Victoria'dan büyük); 9 yarığının güney ucunda
  56.800 km², **557 m derin** yarık gölü (Baykal türü, tatlı); 9 boyunca
  bir dizi kapalı tuz gölü (yarık kurak platoda); 2'nin
  dağlarında 814 m derin bir dağ gölü.
- Buzul çağında buzun kazıdığı yerlere oyulan 84 oluktan 66'sı su tutuyor,
  51'i 100 km² üstünde. Duvar'ın kuzey yüzündekiler (kurak plato) çoğunlukla
  kuru ya da kapalı.

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
