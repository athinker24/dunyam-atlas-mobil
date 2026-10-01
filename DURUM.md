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
nehir bilgisi. Deltalar (160 delta, uygulamada çatallı ağızlar). Su deniz renkleriyle çizilir. Nehir çizgisi bütün ağa ortak kaydırma alanıyla kıvrılır, düz arazide (plato) 200-900 km'lik büyük kıvrım (sahibi: "çok düz"). Paralel dere tarakları birleştirildi (~35 km, sahibi: "olabildiğince az"). Adalarda ayrı eşik (3 m³/s, ≥ 60 km): takımadada 175 kol (sahibi: "adalarda su yok"). Sıradaki: aylık akış rejimi, göl/nehir adları (sahibi verirse).

## Ansiklopedi yönü (27 Eylül, sahibi)

Uygulama bir ansiklopediye büyüyecek: iklim, dağlar, nehirler, toprak,
bitki örtüsü, ileride hayvanlar ve canlılar. Karar: özellikler şimdilik
mevcut sekmelere yerleştirilir, hepsi bitince gruplar hâlinde yeni iskelet
kurulur. Merak Planet Advisor'dan eksikler sırası: **bitki örtüsü (yapıldı,
`BITKI.md`) → toprak (yapıldı, `TOPRAK.md`) → yaşanabilirlik (1 Ekim'de dokuz etkenli puana baştan yazıldı, `YASAM.md`)**;
toplumlar/zincir en sona, "olası okuma, tahmin değil" etiketiyle. Sahibi
yaşanabilirliği insana özgü değil, genel koşullar olarak istedi (28 Eylül);
ilk sürüm yalnız net birincil üretimdi ve her yer "çok elverişli" çıktı, o yüzden
dokuz etkenli puana yazıldı (`YASAM.md`). Tarımsal verimlilik sorusu ("yalnız toprak türü
belirlemez") şimdilik bekletildi; toprak + eğim + su erişimi ile ayrı katman
olabilir. Toprak ve yaşanabilirlik veri.yml ile üretilmez, elle koşulur.

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
