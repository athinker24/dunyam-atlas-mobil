# DURUM — aktif durum (her oturumun başında oku)

Son güncelleme: 26 Eylül 2026, bulut oturumu (masaüstü sonuçları dahil). Bu dosya "şu an
neredeyiz" sorusunun cevabıdır; kalıcı bilgi `CLAUDE.md`'de, gece bakımının
ayrıntısı `GECE.md`'de. Oturumu bitirirken bu dosyayı güncelle.

## Çalışma biçimi (26 Eylül'den beri)

Sahibi bu proje için artık bilgisayar kullanmayacak: iş **yalnız GitHub ve
mobil Claude Code** (bulut oturumu) üzerinden yürür. Sonuçları:

- **Tek kaynak bu repo.** `motor/` ve `dunya/` artık kopya değil, asıl
  hâldir. Asıl proje ("Proje 3") 26 Eylül itibarıyla bu repoyla aynı ve
  arşiv olarak kalır; `_senkron_kontrol.py` yalnız bir gün oraya dönülürse
  işe yarar.
- **Dünya doğrulaması artık koşulamaz.** `test_climate.py` ve Dünya
  referans verisi (`rasterio` ister) masaüstünde. Motor değişikliği burada
  yalnız iç tutarlılık kontrolleri (12 madde) ve uygulama testiyle
  sınanır. Motorun fiziğine dokunan bir değişiklikte bunu sahibine söyle.
- **Arazi değişikliği şu an bilgisayar ister.** `.glb`'den gezegen tuvalini
  üreten `_mk_heightmap.py` ve akıntıları kıyıdan türeten `_akinti_kur.py`
  yalnız masaüstünde. Sahibi yeni arazi verirse önce bu ikisinin repoya
  taşınması gerekir (kanal ve üç kıyı girintisi `_heightmap_kaynak`'ta
  yazılı; taşınan sürüm onları korumalı). Kabartma görseli zaten repoda
  (`kabartma_kaydet.py`).
- `baslat.bat` ve `tunel.bat` yalnız Windows içindir; yayın Cloudflare'den.

## Sıradaki iş: eksikleri repoya taşımak (27 Eylül planı)

Bu dosyalar yalnız bilgisayarda; bulut oturumu onlara ulaşamaz. Bir kez
bilgisayardan (GitHub web arayüzünden yükleyerek ya da masaüstü Claude
Code'la) bir dala konmaları gerekir, sonrası bulutta yürür:

1. `_mk_heightmap.py` ve `worldinfo/` içindeki en yeni arazi kaynağı
   (`.glb` ya da 16 bit PNG). Repoya alınırken kanal ve üç kıyı girintisi
   (`_heightmap_kaynak`) korunmalı; bulut oturumu bunu yeniden üretip
   bugünkü `dunya/dunyam_heightmap.png` ile karşılaştırarak doğrular.
2. `_akinti_kur.py` (yalnız kıyı değişirse gerekir).
3. İsteğe bağlı: `test_climate.py` ve Dünya referans verisi. Referans
   `rasterio` istiyor ve büyük; repoya girip girmeyeceği boyutuna bakılarak
   karar verilir.

## Şu an yayında olan

- `main`: `yalniz-repo` ve `tektonik` dalları birleşti (26 Eylül). Uygulama
  dosyaları 60a4674'ten beri aynı; telefonda değişen yok. Veri sürümü
  `f773654851` (üretim 26 Eylül 05:57 UTC). İklim sayıları 25 Eylül'den beri
  aynı (`dunyam.json` → `_guncel_durum`).
- Son eklenenler, telefonda görüldü:
  - Günlük sıcaklık: gündüz/gece, ayın tipik tepesi/dibi, 30 yılda bir rekor
    (Sıcaklık sekmesinde Ortalama/Gündüz/Gece/Tepe/Dip; kartta bant ve satır).
  - Deniz dokusu: sığ/derin tonu, eşderinlik çizgileri, kıyı köpüğü. Yalnız
    görünüş; "derinlik" kıyıya uzaklıktır, batimetri değil. Ayarlarda
    "Deniz dokusu" anahtarı.
  - Deniz kartı: her sekmede denize dokununca su sıcaklığı, aylık rüzgâr ve
    Beaufort şeridi, buz ayları, tropikal fırtına koşulu (yalnız eşik),
    yakındaki akıntı, yağış, en yakın kara.
- Açık kalan karar yok. Doğu kıyı savanı bilerek bırakıldı (`_dogu_kiyi_savan`).

## Tektonik hikâye (26 Eylül, `main`'de)

Arazideki dağ, plato ve havzalardan geriye dönük kurulan levha hikâyesi.
Başka bir oturum ya da yapay zekâ için giriş noktası **`tektonik/OZET.md`**
(makine için `tektonik/ozet.json`); ikisi `tektonik/ozet.py` ile modelden
üretilir, elle düzenlenmez. Bölge bölge kararların gerekçesi `TEKTONIK.md`.
Model `tektonik/levhalar.py` (13 kapalı levha, Bird 2003 sınır sınıfları),
haritalar `tektonik/harita.py` (Equal Earth ve küreler). Okyanus içindeki
sırt, hendek ve üçlü kavşaklar **tasarımdır**, araziden ölçülmedi.

Açık karar yok: kaçış bloğunun ve 9'daki Baykal tipi yarığın ayrıntısını
sahibi Claude'a bıraktı ("sen belirlersin"), ikisi kesin. Buzul geçmişi `BUZUL.md`'de.

## Buzul geçmişi (27 Eylül, `buzul` dalında)

Giriş noktası **`BUZUL.md`**. Karar: buzul çağı −6 °C, eğiklik 22°,
deniz −120 m; ovalarda kıta buz örtüsü yok (kurak, kar çizgisi yüksek).
Sonuç dağ buzulu: doruğunda karanın %6.7'si buz, bugün %2.2. İzler: 172
moren seti gölü adayı (26 büyük, çoğu Duvar'da), 12 fiyort (kuzey kıyısı),
~3.000 sirk. Göller ve nehirler `SU.md`'de.

## Göller ve nehirler (27 Eylül, yayında)

Giriş noktası **`SU.md`**. Karar: fırça izleri yumuşatıldı, eşik aşınması
200 m, 300 km² altı göl yok. Göller karanın %1.68'i (95 göl). Sahibin
isteğiyle (kurgu) plato kolu boğazla iç denize, boğaz ağzında 10.066 km²
tatlı göl, kuzey kolunun ucunda 4.050 km² tuz gölü. Uygulamada su katmanı
(27 Eylül): ana kollar / bütün kollar, dokununca göl ve
nehir bilgisi. Deltalar (160 delta, uygulamada çatallı ağızlar). Su deniz renkleriyle çizilir. Nehir çizgisi bütün ağa ortak kaydırma alanıyla kıvrılır, düz arazide (plato) 200-900 km'lik büyük kıvrım (sahibi: "çok düz"). Paralel dere tarakları birleştirildi (~35 km, sahibi: "olabildiğince az"). Adalarda ayrı eşik (3 m³/s, ≥ 60 km): takımadada 175 kol (sahibi: "adalarda su yok"). Aylık akış rejimi 2 Ekim'de eklendi (`su/rejim.py`, SU.md). Sıradaki: göl/nehir adları (sahibi verirse).

## Ansiklopedi yönü (27 Eylül, sahibi)

Uygulama bir ansiklopediye büyüyecek: iklim, dağlar, nehirler, toprak,
bitki örtüsü, ileride hayvanlar ve canlılar. Karar: özellikler şimdilik
mevcut sekmelere yerleştirilir, hepsi bitince gruplar hâlinde yeni iskelet
kurulur. Merak Planet Advisor'dan eksikler sırası: **bitki örtüsü (yapıldı,
`BITKI.md`) → toprak (yapıldı, `TOPRAK.md`) → yaşanabilirlik (1 Ekim'de dokuz etkenli puana baştan yazıldı, 2 Ekim'de hastalık ve taşkın eklendi, `YASAM.md`) → tarım (yapıldı, `TARIM.md`)**;
toplumlar/zincir en sona, "olası okuma, tahmin değil" etiketiyle. Sahibi
yaşanabilirliği insana özgü değil, genel koşullar olarak istedi (28 Eylül);
ilk sürüm yalnız net birincil üretimdi ve her yer "çok elverişli" çıktı, o yüzden
dokuz etkenli puana yazıldı (`YASAM.md`). Tarımsal verimlilik ("yalnız toprak türü
belirlemez") 1 Ekim'de ayrı katman oldu (`TARIM.md`). Toprak, yaşanabilirlik ve tarım
veri.yml ile üretilmez, elle koşulur. Sahibinin sırası (2 Ekim): hastalık ve taşkın (yapıldı) →
nehir akış rejimi (yapıldı) → arayüzün gruplanması (yapıldı: A düzeni, dört bölüm ve
çipler, keskin köşeler) → hayvanlar (yapıldı: topluluklar ve tür zenginliği, `HAYVAN.md`). Dördü üst üste dallarda,
en üstteki `hayvanlar` hepsini taşır; birleştirilmedi. Ansiklopedide kalan: toplumlar/zincir
("olası okuma, tahmin değil" etiketiyle; Toplum bölümü şimdilik pasif).

## Tektonik katman (27 Eylül)

Arazi sekmesinde "Yükseklik / Levhalar". Levhalar, sınırlar ve volkan
kuşakları; kural ve kaynaklar `TEKTONIK.md` sonunda. Veri
`python tektonik/uygulama.py` ile (levha modeli değişirse elle koşulur).
Merak Planet Advisor incelemesi askıda (sahibi: "bu bi dursun").

## Yayın (Cloudflare) — 26 Eylül'de öğrenilen

`main`'e push'lar bir süre üretime gitmedi: Cloudflare'in üretim dalı `main`
değildi, `main` yalnız önizleme olarak derleniyordu. GitHub'daki "Workers
Builds" onay işareti yeşil olsa da yayın olmuyordu. Sahibi Cloudflare'de
Settings → Build → Branch control → üretim dalı = `main` yaptı, düzeldi.
Bir değişiklik telefona gelmiyorsa önce Cloudflare → Deployments'ta yeni kayıt
var mı bak. Telefonda: uygulamayı tamamen kapatıp aç; veri sürümü
değişmediyse "Güncellemeleri denetle" yalnız "Güncel" der, kodu yenilemez.

## Bilgisayarda (masaüstü, asıl proje "Proje 3") — BİTTİ

26 Eylül masaüstü oturumunda 1, 2, 4 ve 5 kapandı; 3'ü sahibi atladı
(`_atlas.py` kullanılmıyor), 6 bırakıldı.

1. **Ayrışmalar asıl projeye taşındı.** `motor/`'dan 6 dosya
   (`circulation`, `grid`, `maritime`, `moisture`, `monsoon`, `sanity`),
   `dunya/`'dan 2 (`dunyam.json`, `dunyam_heightmap.png`); Windows klonundan
   bayt bayt, satır sonlarına dokunulmadan. Projedeki eski hâlleri
   `Proje 3/out/_yedek_oncesi/` altında.
   - Farklar satır sonu gürültüsüyle şişik görünüyordu; normalize edilmiş
     gerçek değişiklik: `monsoon` 3, `maritime` 14, `circulation` 15,
     `sanity` 31, `grid` 32, `moisture` 209 satır.
   - `kabartma_kaynak.jpg` **taşınmadı**: eşleme listesinde yok, projede onu
     okuyan kod yok. İstenirse tek kopyalama.
   - `_senkron_kontrol.py`: fark yok, çıkış 0.
   - `test_climate.py` kopyalamadan önce ve sonra: ikisi de **68/68**, çıkış
     0, test listesi ve sonuçları birebir aynı. Tek fark üç yeni
     `RuntimeWarning` idi (aşağıya bak).
2. **Koşulmadı** ve bundan sonra da koşulmayacak: `_repo_senkron.py --yaz`,
   `_egri_kur.py --yaz`, `_mk_heightmap.py`. Üçü de repodan taşınan işi geri
   alır. Asıl projede bu yasak üç yere yazıldı: `HANDOFF.md` başına ⛔
   uyarısı, `CLAUDE.md`'ye kalıcı not, oturum hafızası.
3. **Atlandı** (sahibi: "`_atlas.py`'yi kullanmıyorum"). Palet karşılaştırması
   hâlâ duracaktır, beklenen.
4. `_atlas.py`'nin yazdığı `atlas.json` bu repoya **kopyalanmadı**.
5. **Windows'ta denendi, GECE 41 ve 22 kapandı.**
   - `baslat.bat`: dinleyen adres `127.0.0.1`. Bu makineden `/` ve
     `/index.html` 200, `/.git/HEAD` 200 (tasarım gereği depo kökü);
     **yerel ağdan bağlantı kurulmuyor.** Geçti.
   - `tunel.bat`: genel adreste `/index.html` ve `/` 200; `/.git/HEAD`,
     `/motor/`, `/motor/sanity.py`, `/dunya/dunyam.json` hepsi **404**;
     `/data/atlas.json` 200 (uygulama verisi). Geçti.
   - Klavye: `+` yakınlaştırdı, `0` kıtaya sığdırdı, `→` kaydırdı, tıklayınca
     kart açıldı, `Esc` kapattı. Dördü de görüntüyle doğrulandı.
   - **Bulunan kusur ve düzeltmesi:** `tunel.bat`'ın yerel sunucusu
     `--bind 127.0.0.1` kullanmıyordu (`baslat.bat` kullanıyor), yani tünel
     açıkken `site/` yerel ağa da açılıyordu. Ölçüldü: dinleyen adres `::`.
     Düzeltme `tunel-yerel-bind` dalındaydı; `yalniz-repo` ile `main`'e girdi.
   - Not: `.bat`'ları otomatik başlatırken `Start-Process` çalışma dizinini
     devralmıyor; tam yol verilirse ikisi de sorunsuz koşuyor. Betiklerde
     kusur değil.
6. **Bırakıldı** (sahibi: "şimdilik"). Nem korunumu (`conserve_moisture`)
   Dünya doğrulamasında hiç denenmedi (§8); asıl projede Dünya'ya karşı bir
   koşu değerli olur.

## Sahibinin kararını bekleyen

- **Servis çalışanı bir kez normal tarayıcıda görülmeli.** Gömülü tarayıcı
  panelinde kaydolmadı: konsolda iki "script alınamadı" hatası, kayıt sayısı
  0. Sunucu tarafı sağlam — `sw.js` 200 dönüyor, bağlam güvenli (localhost),
  `navigator.serviceWorker` var. Panelin kısıtı olması kuvvetle muhtemel
  (telefonda çalışıyor) ama **doğrulanmadı**: `baslat.bat` ile açıp
  konsola bakmak yeter.
- **`durum-duzelt` dalı artık bayat** (yalnız DURUM.md'ye "şunları yap"
  notları; hepsi yapıldı). Birleştirilirse bitmiş işi geri yazar.
  Silinebilir.

### Küçük, eskiden beri bekleyenler

- Akıntı uzaklığındaki Dünya sabiti (111.32 / 110.57 km/derece) giderildi:
  `motor/temperature.py` artık `radius_km × π/180` kullanıyor. Dünyam yarıçapı
  6371 km olduğundan fark çok küçük; veri.yml yeni veriyi üretir. Asıl projeye
  de taşınmalı (§7.6).
- Aylık sıcaklığı 2 baytla saklamak (kartta sınıf/klimagram çelişkisi
  karanın %2.1'inde, en çok 0.16 °C). Öncelik düşük.
- Küresel ortalama 15.1 °C (girdi 14). Öneri: dokunma.
- Birleşmiş eski dallar: `gunluk-sicaklik`, `deniz-deneme`, `deniz-yumusak`,
  `deniz-kart`, `durum`, `sanity-okyanussuz`, `durum-masaustu-bitti`,
  `tunel-yerel-bind`, `yalniz-repo`, `tektonik`, `durum-duzelt` (bayat),
  `buzul`, `su`, `su-katmani`, `delta`, `su-gorunum`, `nehir-kivrim`,
  `nehir-deneme` (boş). Silmek
  sahibinde (bulut oturumunun silme izni yok, 403).

## Kurallar (hatırlatma)

- `main`'e push = telefona yayın. `main`'e yalnız sahibi "Main'e birleştir"
  deyince girilir; iş önce bir dalda, test yeşil olunca ileri sarma.
- İklim parametresi sahibinin kararı olmadan değişmez; seçenekler PNG ile.
- Bulutta `test/uygulama_test.js`'in "güncelleme denetimi yeni veride
  yeniler" maddesi yerelde zaman aşımına düşüyor (değişmemiş `main`'de de);
  GitHub'da geçiyor. Karar GitHub'daki `uygulama testi` sonucudur.

## Genel temizlik (1 Ekim)

Git'te izlenen ama `.gitignore`'da olan `su/_goller*.pkl` önbellekleri (3 MB; yalnız yazılıyor, hiçbir yerde okunmuyor) ve hiçbir belgede ya da kodda adı geçmeyen 11 önizleme PNG'si (~13 MB) silindi. Kullanılmayan değişken ve import'lar temizlendi (`pyflakes` temiz). Katman çıktıları ve 31 tarayıcı testi değişmedi. Not: `toprak/toprak.py` `su/_disa.pkl` ister; bu dosya git'te yok, `su/uret_su.py` üretir.

## Tarımsal verimlilik (1 Ekim, `tarim-verimlilik` dalında)

Arazi → Tarım: ısı, su, toprak, arazi dört etkeni; iki varyant (nehirle sulamalı varsayılan, yalnız yağmur). `tarim/tarim.py`, `TARIM.md`. `veri.yml` üretmez. Çok yüksek payı %23.4, 14.8 puanı Duvar'ın güneyindeki alüvyon ovası (bilerek verimli). Kalıcı donmuş toprak ve toprak eşlemesi düzeltildi (Yakutsk 14, Amazon 54). Birleştirilmedi.

## Arazi denemesi 3 (14 Kasım, `arazi-tarih-3` dalı, YAYINDA DEĞİL)

İkinci denemenin arazisi + işaretli bozkır havzasının batısında sırt (42-49.5°K, 0-5°D,
en yüksek ~2100 m). Önizleme `https://arazi-tarih-3-dunyam-atlas-mobil.qarb0natalha2434.workers.dev`.
12/12 tutarlılık, 36/36 test; ana gruplar deneme 2 ile aynı (A 17.6, B 6.5, C 39.5, D 33.1, E 3.3).
Bozkır amacı TUTMADI: bölge (37-49°K, 5°B-28°D) yağışı 900 → 851 mm, BSk %9 → %10 (0.25°);
elips içinde BS %5 → %6. Sırt kısa ve alçak: 0.5° taramasında 36-51°K boyunca kesintisiz
2500 m sırt %8, 3500 m sırt %29 bozkır vermişti. Tarama araçları: oturumun karalama
dizinindeki tara.py (bölgesel geri dönüşüm ve sırt bellekte denenir).

## Arazi denemesi 4 (14 Kasım, `arazi-tarih-4` dalı, YAYINDA DEĞİL)

Üçüncü denemenin arazisi; batı sırtı kuzeydoğu-güneybatı uzanıyor: 52-44°K arası 3000-3300 m
(6°D'den 3°B'ye), 42-38°K arasında 1100-1350 m'lik GEDİK, 36°K'de 2500 m. Kara piksellerinin
%4.7'si değişti. Önizleme `https://arazi-tarih-4-dunyam-atlas-mobil.qarb0natalha2434.workers.dev`.
12/12 tutarlılık, 36/36 test; ana gruplar A 17.6, B 6.7, C 39.5, D 32.9, E 3.3.
Bozkır amacı YİNE TUTMADI: bölge yağışı 851 → 848 mm, BS %10 → %12. Sırt çalışıyor ama yalnız
arkasında: 5-20°D bandında yağış 48°K 355, 46°K 438, 44°K 756, 42°K 1223, 40°K 1306 mm.
Havzanın güney yarısı nemi 38-42°K gediğinden alıyor; gedik kapanmadan bölge bozkır olmaz.

## Arazi denemesi 5 (14 Kasım, `arazi-tarih-5` dalı, YAYINDA DEĞİL)

Dördüncü denemenin arazisi; batı sırtındaki 38-42°K gediği kapatıldı: 44-36°K arası tepe
3400-3670 m, tepe hattı 2.5-3.8°B, 2000 m üstü genişlik ~1°. 44.5°K kuzeyi aynı (en çok 3 m).
Önizleme `https://arazi-tarih-5-dunyam-atlas-mobil.qarb0natalha2434.workers.dev`.
12/12 tutarlılık, 36/36 test; ana gruplar A 17.6, B 9.8, C 39.4, D 29.8, E 3.4.
Bozkır amacı TUTTU: bölge yağışı 848 → 485 mm, BSk %12 → %41 (atlas), 0.25°'de %41.
5-20°D bandında yağış 350-480 mm (44°K 404, 40°K 482). Bölgenin geri kalanı Dwa %31, Dfa %12:
doğu ve kuzey kenar. Bölge dışında sınıfı değişen kara %2.9. Bölgesel geri dönüşüm denenmedi.

## Arazi denemesi 6 (14 Kasım, `arazi-tarih-6` dalı, YAYINDA DEĞİL)

Beşinci denemenin arazisi + savanı azaltmak için ekvator kuşağında kıyıdan içeri yükselen
kalkan kubbesi (tam genlik 2.5°G-12.5°K, 10°G ve 20°K'ye sönümlü; bantta kara ortancası
236 → 645 m). 20°K kuzeyi aynı. Önizleme
`https://arazi-tarih-6-dunyam-atlas-mobil.qarb0natalha2434.workers.dev`.
12/12 tutarlılık, 36/36 test; ana gruplar A 12.3, B 9.8, C 44.8, D 29.8, E 3.4.
Savan Aw %15.3 → %10.5 (main %8.6), Cwb %5.5 → %11.1 (main %11.2); bozkır bölgesi %41 aynı.
Karada sınıfı değişen %11.1 (0.25°). Yan etki: deneme 3-5'teki 17°K 24.5°B'deki 428 bin km²'lik
tuz gölü (main'de yok) kubbenin kuzey eteğiyle kayboldu; yerine 1229 m'de 80 bin km² tatlı göl.
Göllerin kara payı %2.90 → %1.86.

## Arazi denemesi 7 (14 Kasım, `arazi-tarih-7` dalı, YAYINDA DEĞİL)

Sahibin yeni tektonik değişiklikleri (açıklamasız geldi, ölçüldü): karanın %33'ü değişti.
Batı sırtı doğuya kaydı ve alçaldı (44°K 3029 m 2.1°D'de, 42°K 2464 m), 38-40°K gediği
yeniden açıldı (1350-1370 m); 36-54°K, 8-17°B'de 1670 m'ye kadar yeni yükselti; Büyük Duvar'ın
güneydoğusu (28-43°K, 23-43°D) ortalama 970 m alçaldı; ekvator kubbesi duruyor.
Önizleme `https://arazi-tarih-7-dunyam-atlas-mobil.qarb0natalha2434.workers.dev`.
12/12 tutarlılık, 36/36 test; ana gruplar A 12.0, B 6.4, C 46.6, D 32.4, E 2.6; Aw %10.1.
Bozkır GERİ GİTTİ: bölge yağışı 484 → 743 mm, BSk %41 → %12 (dördüncü denemedeki gedik etkisi;
5-20°D'de 42°K 847, 40°K 1069 mm). Karada sınıfı değişen %18.4 (deneme 6'ya göre).

## Arazi denemesi 8 (14 Kasım, `arazi-tarih-8` dalı, YAYINDA DEĞİL)

Yedinci denemenin arazisi; yalnız batı sırtı yükseltildi (karanın %2.7'si): 0.25° ızgarada
39.5-44°K sırt 2560-3200 m. Gedik daraldı ama kapanmadı: ızgarada 36.75-39°K arası sırt
1040-1420 m. Önizleme `https://arazi-tarih-8-dunyam-atlas-mobil.qarb0natalha2434.workers.dev`.
12/12 tutarlılık, 36/36 test; ana gruplar deneme 7 ile aynı (A 12.0, B 6.4, C 46.6, D 32.4, E 2.6).
Bozkır TUTMADI: bölge yağışı 743 → 681 mm, BSk %12. Nem gedikten girip sırtın arkasında kuzeye
yayılıyor: 39.5°K'de sırtın doğusunda (1-6°D) 1000-1480 mm, 37.5°K'de 280-370 mm.
Bozkır havzasında 761 m'de 434 bin km²'lik tuz gölü (en büyük göl).
Test düzeltmesi: `gole dokununca kartta gol satiri` en büyük gölün kutusunda ilk iç noktayı
seçiyordu; bu gölde nokta kıyıdaydı, dokunuş hücre merkezine oturup gölün dışına düştü.
Artık nokta kıyıdan en az bir hücre içeride seçiliyor. Bu düzeltme main'e de gitmeli.

## Arazi denemesi 9 (15 Kasım, `arazi-tarih-9` dalı, YAYINDA DEĞİL)

Sekizinci denemenin arazisi; batı sırtının 36-41°K kesimi yükseltildi (karanın %1.4'ü), gedik
kapandı: 0.25° ölçeğinde sırt 36.5-41°K boyunca 2370-3200 m.
Önizleme `https://arazi-tarih-9-dunyam-atlas-mobil.qarb0natalha2434.workers.dev`.
12/12 tutarlılık, 36/36 test; ana gruplar A 12.0, B 7.3, C 46.6, D 31.5, E 2.6.
Bozkır KISMEN: bölge yağışı 681 → 591 mm, BSk %12 → %19 (deneme 6: %41). Sırtın arkası (0-10°D)
deneme 6 kadar kuru; havzanın doğu yarısı ıslak. Sebep: yedinci denemede Büyük Duvar'ın
güneydoğu ucu alçaldı, tepe 34-42°D'de 3770-3850 → 3460-720 m (36°D 3091, 38°D 2727,
40°D 1704, 42°D 721). Güney nemi bu yarıktan girip havzanın doğusunu ıslatıyor
(41°K 12-16°D: 410-440 → 700-770 mm).

DÜZELTME (15 Kasım): duvar yarığı açıklaması YANLIŞTI. 0.25° kutu değiştirme denemeleri
(dokuzuncu denemenin arazisinde bir kutuyu altıncı denemeden alarak): Büyük Duvar güneydoğusu
637 mm %19, 43°K kuzeyi 576 mm %20, 8-17°B yükseltisi 590 mm %19, bütün havza 468 mm %40,
yalnız batı sırtı 34-44°K 6.5°B-4°D 470 mm %37. Sebep sırtın 41-43°K'de 4-5° doğuya kayması
ve ~500 m alçalması.

## Arazi denemesi 10 (15 Kasım, `arazi-tarih-10` dalı, YAYINDA DEĞİL)

Dokuzuncu denemenin arazisi; batı sırtının 34-44°K, 6.5°B-4°D kutusu altıncı denemeden geri
alındı (sırt 36-44°K, 2.7-3.5°B, 3330-3660 m), kuzey sırtla 44-46°K'de kavisle birleşir.
Önizleme `https://arazi-tarih-10-dunyam-atlas-mobil.qarb0natalha2434.workers.dev`.
12/12 tutarlılık, 36/36 test; ana gruplar A 12.0, B 8.9, C 46.5, D 30.0, E 2.6, Aw 10.1.
Bozkır: bölge yağışı 591 → 474 mm, BSk %19 → %33 (deneme 6 %41). Göllerin kara payı %0.87.
