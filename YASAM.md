# Yaşanabilirlik

Yerleşik yaşam (bitki, hayvan ve insan) için çok etkenli endeks, 0-100. Üretici
`yasam/yasam.py` (~1 dk), çıktı `data/yasam.png` (geniş, yumuşak nehir çevresi,
varsayılan) ve `yasam_dar.png` (nehrin hemen yanı), her ikisi için `*_veri.png`,
`yasam.json`. Uygulamada Arazi sekmesi → **Yaşanabilirlik**; kartta sınıf, puan,
zayıf ve iyi yönler. Çizim yolu bitki örtüsü ve toprakla aynı (`BITKI.md`).

**Veri iş akışı (veri.yml) bunu üretmez.** Bağımlılıklar: `bitki/_bitki.npz`,
`toprak/_toprak.npz` (`toprak/toprak.py` yazar), `su/_akim.npz`, `su/_su.npz`,
`data/su.json`, `data/tektonik.json`. İklim değişirse sıra: bitki, toprak, yasam.

## Neden baştan (1 Ekim, sahibi)

İlk sürüm yalnız net birincil üretime (Miami/Lieth NPP) bakıyordu. Bu dünya
ılık ve nemli olduğu için NPP tavana yapışıyor, ilk sürümde karanın %52'si en
üst iki sınıftaydı: "sanki bütün dünya mükemmel ötesi yaşanabilir". Sahibi
etken listesini verdi (arazi, iklim, yağış, sıcaklık, suya ve denize erişim,
mevsimsel değişim, insan yaşamı için alan); NPP artık yalnız gıda etkeninin bir
parçası.

## Etkenler (her biri 0-1)

| # | etken | ağırlık | ne bakıyor |
|---|---|---|---|
| 0 | Sıcaklık | 3 | yıllık ortalama (nüfus yoğunluğu ~13 °C'de tepe, ikinci küçük tepe ~27 °C: Xu vd. 2020, PNAS; Gauss, σ 12 ve 5), en soğuk ay (0 at −40 °C, 1 at −12 °C), en sıcak ay (1 at 33 °C, 0 at 40 °C); üçünün en zayıfı |
| 1 | Su | 3 | nem oranı AET/PE (0.10 → 0, 0.60 → 1), nehir ve göl erişimi (aşağıda), aşırı yağış (> 2500 mm/yıl yarıya kadar ceza) |
| 2 | Gıda | 2 | Miami NPP (100 → 0, 900 g/m²/yıl → 1) ve büyüme sezonu GDD5 (400 → 0, 1700 → 1); küçük olan, çarpı (0.4 + 0.6 × toprak) |
| 3 | Mevsimsellik | 1.5 | yıllık sıcaklık aralığı (25 K → 1, 60 K → 0), kurak ay sayısı (P < 25 mm ve T > 5 °C; 3 → 1, 10 → 0), yağışın en yağışlı 3 aya yığılması (pay 0.50 → 1, 0.95 → 0, musonu cezalandırır); üçünün geometrik ortalaması. Kurak ay ve yığılma cezası nehir erişimiyle (w) azalır: sulanan yerde yağışın zamanı önemsiz |
| 4 | Arazi | 1.5 | yumuşatılmış eğim (40 m/hücre → 1, 300 → 0, `toprak/toprak.py` ile aynı yöntem) × yükseklik (2000 m → 1, 5000 m → 0; kalıcı yerleşim ~5100 m'de biter, 5400 m üstünde oksijen yetmez) |
| 5 | Toprak | 0 (gıdanın içinde) | WRB türünün tarımsal verimlilik sırası (Chernozem 1.0, Fluvisol 0.95, Kastanozem 0.85, Luvisol ve Andosol 0.8, Cambisol 0.7, Lixisol 0.55, Acrisol 0.45, Ferralsol 0.4, Podzol 0.35, Calcisol 0.3, Leptosol 0.2, Cryosol 0.15, Solonchak 0.1); yargıdır, ölçüm değil |
| 6 | Deniz | 0.5 | kıyıya uzaklık: 0.6 + 0.4 exp(−d/400 km) (balık, ticaret, ılımanlık; zorunlu değil, bonus) |
| 7 | Tehlike | 1 | çarpışma, dalma ve dönüşüm levha sınırı çevresi ~40 km (deprem, −0.15) ve volkan kuşağı (−0.30); en çok 0.6'ya iner |
| 8 | Alan | çarpan | çevredeki ~50 km'de elverişli (≥ 0.5) kara payı: dar bir şerit ya da vadi 0.7, geniş ova 1.0 ("insan yaşamı için yeterli alan var mı") |

**Birleşim:** etkenlerin ağırlıklı geometrik ortalaması (bir etken 0 ise sonuç 0:
telafi edilemez), çarpı kritik dört etkenin (sıcaklık, su, gıda, arazi) en
zayıfının karekökü, çarpı alan etkeni. Kritik terim eklendi çünkü ortalama tek
ağır kısıtı söndürüyordu: 3640 m'deki La Paz ilk denemede 82 puan çıkıyordu.

**Sınıflar** (mutlak puan): Yaşanmaz < 25, Çok zor 25-45, Zor 45-62, Orta 62-78,
Elverişli 78-90, Çok elverişli >= 90; kalıcı buz ayrı. Eşikler ve ağırlıklar
seçimdir; aşağıdaki Dünya örnekleriyle sağlandı.

## Nehir ve göl kıyısı

Su etkeninde nem oranı, nehre yakınlık ağırlığı w (0..1) kadar 1'e yaklaşır
(alfa + w (1 − alfa)); gıda etkeninde AET olası buharlaşmaya (PE) yaklaşır.
Nehirler uygulamada çizilen gerçek çizgilerdir (`data/su.json`, bütün kademeler,
ham ızgara yolu değil). İki seçenek (uygulamada "Nehir çevresi" ayarı):
**Geniş, yumuşak** (varsayılan, debiye göre 2.5 / 5 / 8 hücre, ~9.7 km/hücre,
kosinüsle söner, göl kıyısı 3) ve **Nehrin yanı** (1 / 2 / 3 hücre, keskin). Yeni
modelde seçeneğin etkisi küçük (kara ortalaması 55.4 ve 55.3), çünkü yaşanabilir
bölgelerde su zaten sınırlayıcı değil; asıl fark kurak yerlerde.

## Gerçek dünya bölgeleriyle sağlama (1 Ekim, sahibi: "gerçek dünyadan bazı bölgelere de uygula")

Aynı etkenler, bölgelerin yaklaşık iklim normalleri ve arazisiyle (ezbere, kaba; toprak,
kıyı uzaklığı, nehir erişimi, alan elle). `python yasam/yasam.py` her koşuda basar.
Ölçüt: puan sırası gerçek nüfus yoğunluğu sırasına benziyor mu.

| bölge | puan | sınıf | zayıf yön | gerçek yoğunluk (kişi/km², kaba) |
|---|---|---|---|---|
| Po ovası | 96 | Çok elverişli | | ~250 |
| Kuzey Çin ovası | 96 | Çok elverişli | deniz | ~700 |
| Paris havzası | 91 | Çok elverişli | | ~200 |
| Ukrayna bozkırı | 85 | Elverişli | deniz | ~60 |
| Etiyopya yaylası | 80 | Elverişli | tehlike (yarık), deniz | ~150 |
| Ganj ovası | 73 | Orta | sıcaklık | ~1000+ |
| Yunnan yaylası | 72 | Orta | toprak (Acrisol) | ~120 |
| Amazon ormanı | 67 | Orta | toprak, deniz | ~2 |
| Nil vadisi | 65 | Orta | sıcaklık | ~1500 (vadide) |
| Mezopotamya | 58 | Zor | sıcaklık | ~150 (nehirde) |
| Kanada kalkanı | 21 | Yaşanmaz | sıcaklık, gıda | ~0.5 |
| Sibirya taygası | 2 | Yaşanmaz | sıcaklık | ~0.3 |
| Sahra içi | 0 | Yaşanmaz | su | ~0 |
| Tibet platosu (4500 m) | 0 | Yaşanmaz | gıda, arazi | ~2 |

**Sağlamanın bulduğu iki kusur, düzeltildi:**
1. Nil vadisi önce 28 ("çok zor") çıktı: 12 kurak ay cezalanıyordu, oysa nehirden
   sulanan yerde yağışın zamanı önemsiz. Kurak ay ve yığılma cezası artık nehir
   erişimiyle (w) azalıyor.
2. Ganj ovası 56 ("zor"), Mezopotamya 9 ("yaşanmaz") çıktı: en sıcak ay sınırı (28-36
   °C) fazla sertti; ikisi de binlerce yıllık yoğun tarım merkezi ve Xu vd.'nin ikinci
   nüfus tepesi tam bu sıcak ovalarda. Sınır 33-40 °C'ye çekildi.

**Kalan bilinen sapmalar (düzeltilmedi):** Amazon "orta" ama neredeyse boş: model
tropik hastalığı, sık ormanı açmanın zorluğunu ve tarihsel nedenleri görmüyor. Ganj ve
Nil gerçekte dünyanın en yoğun yerleri, burada "orta": sıcaklık nişi yoğunluğun
yüksek olduğu sıcak ovaları hâlâ biraz cezalandırıyor. Ukrayna çok elverişliye yakın
ama yoğunluğu düşük: yoğunluk tarih ve siyasetle de belirlenir, endeks yalnız doğal
koşullara bakar.

## Toprak gıdanın içinde (1 Ekim, sahibi: "bayağı verimli işaretlenmiş, öyle mi gerçekte de")

İlk dokuz etkenli sürümde toprak ayrı etkendi, ağırlığı 14.5'te 1.5. Güneybatıdaki
1500-2000 m Cwb yaylası (alanın %72'si Acrisol, toprak 0.51) bu yüzden 90 puanla
"çok elverişli" çıkıyordu: toprak puanı toplamı yalnız ~%6 düşürüyordu. Dünya'daki
subtropikal yaylalardan verimli olanlar (Kenya, Etiyopya) volkanik ya da besince
zengin topraklı; Acrisol'lü olanlar (Yunnan'ın kırmızı toprakları) teraslama ve
gübreyle ayakta. Şimdi toprak gıda etkeninin çarpanı: gıda × (0.4 + 0.6 × toprak);
en fakir toprakta bile %40 kalır (otlatma, ormancılık). Ayrı ağırlığı 0 (çift sayım
olmasın), kartta yine görünür. Gıda kritik dört etkenden biri olduğu için etkisi
belirgin. O yaylada medyan puan 90 → 76 ("orta"); içinden geçen nehir vadileri
(Fluvisol) 96 ile öne çıkıyor.

## Sonuç (kara alanına göre, 1 Ekim, alüvyon ovası kuralından sonra)

Yaşanmaz %23.4, çok zor %4.6, zor %15.2, orta %33.0, elverişli %13.8, çok elverişli
%8.1, buz %1.9. Kara ortalaması 53.9 puan. Toprak modeline önülke alüvyon ovası
eklendi (`TOPRAK.md`): Duvar'ın güney kuşağı "elverişli / çok elverişli". Etken
ortalamaları: sıcaklık 0.64, su 0.97, gıda 0.65, mevsimsellik 0.93, arazi 0.78, toprak 0.60, deniz 0.79, tehlike 0.99,
alan 0.92. En iyi bölge ~13 °C ılıman ova kuşağı (batı ve kuzey-orta) ile doğu kıyısı
ve nehir vadileri; sıcak güney ovaları "orta" (sıcaklık ve toprak), kurak plato "zor",
dağlar ve kuzey yaşanmaz. Dünya örnekleri (orta toprak 0.8): Paris 91, Şangay 89,
Nairobi 88, Singapur 75, Moskova 75, Mumbai 68, La Paz 51, Ulan Batur 31.

## Sınırlar ve eksikler

- Yağış bu motorda iki kat fazla mevsimsel (CLAUDE.md §8); kurak ay ve yığılma
  cezaları bunu Dünya'dan fazla vurur.
- Su etkeni neredeyse hiçbir yerde sınırlayıcı değil (0.97): motorun yağışı Dünya'dan
  fazla. Gerçek kurak kuşak az.
- Eksik: hastalık yükü (tropik), sel (nehir ovasının tehlikesi), deniz ve kıyı
  fırtınası, kış yağışının kar olarak düşmesi, rüzgâr ve yangın, mineral kaynaklar.
  Sel ve tropik hastalık sonraki aday etkenler.
- Kıyıya uzaklık ızgara hücresiyle (~9.8 km, boylam yönünde 0.8 çarpanı) hesaplanıyor,
  yüksek enlemde kaba.
- Tarımsal verimlilik ayrı bir soru olarak bekliyor (yalnız toprak türü belirlemez);
  bu endeks gıda ve toprağı zaten içeriyor ama tarım katmanı ayrı olabilir.
