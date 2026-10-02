# CLAUDE.md — Dünyam Atlası (mobil repo)

Bu dosya, bu repoda çalışan Claude Code oturumları içindir. Amacı iki şey:
**dünyanın sahibinin ne istediğini** kaybetmemek, ve **neyin neden öyle
olduğunu** yeniden keşfetmek zorunda kalmamak.

Belgeler ve kod yorumları **Türkçe**. Kullanıcı Türkçe çalışıyor.

**Oturuma başlarken önce `DURUM.md`'yi oku**: şu an yayında olan, açık
kararlar ve bilgisayarda (asıl projede) yapılacaklar orada. Oturumu
bitirirken onu güncelle; kalıcı bilgi buraya, anlık durum oraya.

**26 Eylül'den beri iş yalnız GitHub + mobil Claude Code ile yürür;** bu
repo tek kaynaktır, asıl proje arşivdir. Aşağıda "asıl projede koşar"
diye geçen adımlar (Dünya doğrulaması, `_mk_heightmap.py`, `_akinti_kur.py`,
senkron) artık erişilemez; ne anlama geldiği `DURUM.md` → "Çalışma biçimi".

---

## 1. Bu repo nedir

Kurgusal bir gezegenin iklim atlası. İki parçası var:

- **Uygulama** (`index.html`, `app.js`, `style.css`, `sw.js`) — telefona
  kurulan bir PWA, koyu tema. Haritayı WebGL ile çizer (yumuşak ya da piksel
  görünüm, kabartma gölgesi), sınıf dağılımını, 12 aylık klimagramlı hücre
  kartını, Dolaşım sekmesinde aylık rüzgârı (akış çizgileri ya da hareketli
  parçacıklar), zemin olarak deniz yüzeyi sıcaklığını ya da rüzgâr hızını ve
  akıntı yollarını, Kar sekmesinde kar örtüsünü, bir de iç tutarlılık
  raporunu gösterir. Kar motordan gelmez: `app.js` `karHesapla` aylık
  sıcaklık ve yağıştan bir kar kovası döndürür (kar payı −2..+4 °C arası
  doğrusal, erime 75 mm/°C/ay, örtü eşiği ay ortasında 10 mm su; ay ortası
  ay içi doğrusal yağış/erimeyle hesaplanır). Eşikler seçimdir; kaba bir
  sınama: Moskova normalleriyle 5 ay örtü (gerçekte ~4.5), Ulan Batur 4 ay
  ince örtü. Hiç erimeyen hücreler kartta "kalıcı (buzul)". Gündüz/gece
  sıcaklığı, ayın tipik tepesi/dibi ve ~30 yılda bir rekor da motordan gelmez:
  `app.js` `gunlukHazirla` aylık sıcaklık, yağış, yükseklik, kıyıya uzaklık,
  güneş ışınımı (gezegenin eksen eğikliği ve yılından; veride `gezegen`) ve
  yıllık genlikten istatistiksel tahmin eder. Katsayılar 209 ABD istasyonunun
  1991-2019 günlük verisinden (CMU/GHCN-D); istasyon dışarıda bırakılarak
  hata: gündüz-gece farkı 1.9, tepe 1.7, dip 1.35 °C. Gündüz-gece farkı
  √(gün/24) ile ölçeklenir (Dünyam 15 saat: %21 küçük). Kalibrasyon 25-48°K;
  tropikte ve çok yüksekte kaba. Sıcaklık sekmesinde Ortalama/Gündüz/Gece/
  Tepe/Dip seçimi, kartta klimagram bandı ve satırı. Denize dokununca (her sekmede) deniz kartı: su sıcaklığı, aylık rüzgâr yönü ve Beaufort şeridi, en sert/sakin ay, deniz buzu ayları, tropikal fırtına koşulu (su ≥ 26,5 °C, enlem 5-30°; motor siklon çözmez, yalnız eşik), yakındaki akıntı (`dunyam.currents.json`'dan; "mevsimsel genlik" girdisi akıntı sayılmaz), yağış, en yakın karanın yönü ve sınıfı. Derinlik, gelgit, dalga verisi yok; deniz dokusundaki sığ/derin tonu kıyıya uzaklıktır, batimetri değil. Göller ve nehirler her sekmede kaplama (`data/su.json`, `su/` üretir; ayarlarda aç/kapa, "Ana kollar / Bütün kollar"): uzaktan yalnız 1. kademe büyük ana kollar, yakınlaştıkça 2-4. kademe yumuşakça belirir; göle ya da nehre dokununca kartta Göl/Nehir satırı. Kaydırırken su tuvali yeniden boyanmaz, CSS ile kayar. Su, shader'daki `deniz()` renkleriyle (sığ ton, kıyı köpüğü, kıyı ışıltısı) çizilir; ayrı parlak mavi katman haritaya yapıştırma gibi duruyordu. Dolaşım sekmesinde su çizilmez. Arazi sekmesinde "Yükseklik / Levhalar" seçimi: Levhalar'da levha renkleri, adları ve hızları, sınırlar (yakınsak kırmızı ve dişli, ıraksak yeşil, dönüşüm turuncu) ve volkan kuşakları (`data/tektonik.json`, `data/levha.png`; `tektonik/uygulama.py` üretir); dokununca kartta Levha/Sınır/Volkan satırı. Arazi'de üçüncü seçim "Bitki örtüsü": iklimden doğal biyom haritası (`data/bitki.png`, `bitki_veri.png`, `bitki.json`; `bitki/bitki.py`, BIOME1 eşikleri, `BITKI.md`), kabartmayla gölgeli; kartta biyom ve nedeni. Dördüncü seçim "Toprak": bölgesel (zonal) WRB toprak türleri, biyom + eğim + önülke alüvyon ovası + volkan kuşağı + kapalı havza + nehir taşkın ovasından (`data/toprak.png`, `toprak_veri.png`, `toprak.json`; `toprak/toprak.py`, `TOPRAK.md`), aynı yoldan kabartmayla gölgeli; kartta toprak türü ve Dünya'daki örneği. Beşinci seçim "Yaşanabilirlik": on bir etkenli 0-100 puan (sıcaklık, su, gıda (toprak verimliliğiyle çarpılır), mevsimsellik, arazi, deniz erişimi, tehlike, hastalık (MARA sıtma mevsimi), taşkın, alan genişliği; ağırlıklı geometrik ortalama, tek ağır kısıt puanı düşürür; `data/yasam.png`, `yasam_veri.png`, `yasam.json`; `yasam/yasam.py`, `YASAM.md`); kartta sınıf, puan, zayıf ve iyi yönler. Altıncı seçim "Tarım": dört etkenli (ısı, su, toprak, arazi) tarımsal verimlilik puanı, en zayıf halka belirleyici; iki varyant, "Nehirle sulamalı" (varsayılan) ve "Yalnız yağmur" (`data/tarim*.png`, `tarim_veri.png`, `tarim.json`; `tarim/tarim.py`, `TARIM.md`); kartta sınıf, puan, etkenler ve sınırlayan etken. Nehir çevresi iki seçenekli ayar: "Geniş, yumuşak" (varsayılan, debiye göre 2.5-8 hücre kosinüsle söner) ve "Nehrin yanı"; ikisi için ayrı PNG (`yasam.png`, `yasam_dar.png`, `*_veri.png`). Veriyi `data/atlas.json`'dan,
  harita dokularını `data/doku.png`, `yukseklik.png`, `kabartma*.jpg`,
  `dolasim.png`'den okur.
- **Üretici** (`uret.py` + `motor/` + `dunya/`) — iklim motorunun ve dünya
  tanımının kopyası. O `data/atlas.json`'u üretir.

Motor bir GCM değil: akışkanlar dinamiği yok. Katmanlı, belirlenimci bir
hesap. Girdi bir yükseklik haritası ve gezegen parametreleri; çıktı 12 aylık
sıcaklık ve yağış alanları ile hücre başına bir Köppen-Geiger sınıfı.

Asıl proje ayrı bir klasörde (`Proje 3`, git'te değil). Orada motor Dünya
verisine karşı doğrulanıyor. **Bu repo o projeye bağımlı değildir** — burada
`numpy`, `scipy`, `pillow` yeter.

---

## 2. Dünyanın sahibinin istekleri

Bunlar oturumlar boyunca tekrarlanmış, kalıcı istekler. Bir değişiklik
önerirken bunlara çarpıyor mu diye bak.

### 2.1 Mimarî istekler

- **Hiçbir şey Dünya'ya özel sabitlenmeyecek.** Gezegen özellikleri
  `dunya/dunyam.json`'da, okyanus akıntıları `dunya/dunyam.currents.json`'da.
  Motorun içine "Dünya'da şöyledir" diye bir sayı gömmek yasak. Dünya, motorun
  *birinci test dünyası*; yerleşik değil.
- **Okyanus akıntıları elle tanımlanır.** Motor akıntı türetmez; dosyadaki
  yollar, genişlikler ve sıcaklık anomalileri kullanılır. Bu bir eksiklik
  değil, seçim: akıntı yerleşimi dünyanın sahibinin kurgusal kararı.
- **Repo tek başına yetmeli.** Kullanıcının kendi sözleriyle: *"sadece
  github reposundaki dosyaları kullanarak sistemde hesap gibi değişiklikler
  yapmak… şu an masaüstüne bağımlı, bunu istemiyorum."* Bu yüzden `motor/`
  ve `dunya/` burada kopya olarak duruyor ve GitHub Actions veriyi kendisi
  üretebiliyor.
- **Mobil uygulama hızlı güncellenebilir olmalı**, private repo. Cloudflare
  her push'ta yayınlar (sabit adres, önünde Access), telefondaki uygulama
  kendini günceller (§7.5). Veri değişince uygulama koduna dokunulmaz.

### 2.2 İklim istekleri (dünyanın nasıl hissettirmesi gerektiği)

Bunların her biri bir şikâyetten doğdu ve ölçülerek karşılandı. Gerekçeler ve
elenen kollar `dunya/dunyam.json` içindeki `_` ile başlayan notlarda.

| istek | nasıl karşılandı | not |
|---|---|---|
| "yağış olayları çok abartı, her yer muson/yağmur ormanı" | önce `convective_c` 0.42 → 0.12, `rh_ocean` 0.80 → 0.70; bayat eğriyle ayarlandığı anlaşılınca **şimdi 0.27 / 0.75** (yarı yol) | `_yagis_ayari`, `_params_notu` |
| "gerçek ve büyük bir Akdeniz kuşağı istiyordum, hiç yok" | `k_itcz` 0.20 → 0.60; muson o zaman kapatıldı, sonra **yeniden açıldı** (`monsoon_k_hpa_per_k` 1.3) | `_akdeniz`, `_muson` |
| "savan oranını azaltalım, yerine ılıman kuşak, ~%9" | deniz seviyesi sıcaklığı 20 → 14 °C, eksen eğikliği 23.44° → 28° | `_savan` |
| "orta hattında mor ok gibi bir kuşak var" | önce `moist_crit_soft` 0.10, `blocking_spread_km` 1600; arazi değişince ok geri gelmedi, **şimdi 0 / 1200** | `_ok_seridi` |
| "batıdaki kama da düzelsin" | önce `blocking_dz_m` 900 → 3600; **şimdi 900** (motor varsayılanı) | `_ok_seridi`, `_yagis_ayari` |
| "işaretli platoda at göçebesi bozkırı olsun, ortası hardcore çöl olmasın" | gün uzunluğu 15 saat | `_donus` |
| "dünya çok sert, yaşanabilir olsun" | kara 60°K..−7°K'ye taşındı | `_yumusatma` |
| "en üst 60 olsun, orta olsun" | `KUZEY_KARA, GUNEY_KARA = 60, -7` | `_mk_heightmap.py` |
| "sol üstteki bölge çok soğuk" | dünyanın sahibi araziyi kendisi alçalttı | `_bekleyen` |
| "kış yağışı dünya genelinde çok az, kar da" | fırtına yolu terimi, `storm_c` 60 (yeni parametre) | `_firtina` |
| "kendi içinde tutarlı olsun" (su bütçesi Dünya'nın 2 katıydı) | nem korunumu (`conserve_moisture` 1, yeni anahtar), `land_recycle` 0.25 → 0.65, `eddy_blend` 0.005 → 0.02 (etkin difüzivite motor notundaki ~1e6 m²/s); sabit buharlaşma tavanı denenip **reddedildi** | `_su_butcesi` |

### 2.3 Çalışma biçimi istekleri

- **Ölçüt neyse o.** Bir keresinde sıcaklık yoluyla düzeltme önerildi ve
  cevap *"yağış oranı ile benim sorunum, sıcaklıkla değil ki"* oldu. Hangi
  eksende şikâyet varsa orada çalış; başka eksende kazanç sunma.
- **Kurgu fizikten önce gelir — istendiğinde.** Bir şey motorun kuralları
  içinde imkânsızsa "imkânsız" deyip durma: kuralı değiştirmeyi ve bedelini
  sun. `k_itcz`'yi Dünya-doğrulanmış 0.20'den 0.60'a çıkarmak böyle bir
  karardı; bedeli Af yağmur ormanının sıfırlanması oldu ve bilerek verildi.
- **Görselle sor, tabloyla değil.** Bir seçenek listesi sunarken haritayı
  PNG olarak karşılaştır. Bir kez sınıf tablosunda görünen kazanç haritada
  görünmedi: atlas paletinde Af/Am/Aw aynı turkuazın üç tonuydu (ton farkı
  8 derece). Karar yanlış ölçütle verilmişti.
- **Uzun koşu sırasında boş bekleme.** 0.25 derecelik koşu 4 çekirdekli bulut
  makinesinde ~16 dakika (25 Eylül, nem korunumu açık, aylar paralel;
  sıralıyken ~35 dk). Nem çözücüsü 12 ayı `fork` ile paralel çözer, sonuç bit
  bit aynı (`surum` doğrulandı); Windows'ta ya da `DUNYAM_ISCI=1` ile sıralı.
  Tek bir ayın yarıdan fazlası `grid.smooth`: korunum her adımda bir Gauss
  yumuşatması daha ekliyor.
  Arka plana al, o sırada bağımsız işi yap. Çıktıyı dosyaya yönlendirdiğinde
  tamponlanır — koşu bitene kadar dosya boş görünebilir, bu normal.
- **Yüzdeler alan ağırlıklı olacak.** Kullanıcıya gösterilen her oran.
  Gerekçe aşağıda (§7.1).

---

## 3. Repo düzeni

| yol | ne |
|---|---|
| `index.html`, `style.css`, `app.js` | uygulama (dokunmatik pan/pinch, hücre kartı, alt panel; yatay kısa ekranda panel ve ayarlar sağ sütunda, görünür harita alanını yalnız `gorunen()` hesaplar) |
| `sw.js`, `manifest.webmanifest`, `icons/` | kurulum ve çevrimdışı çalışma |
| `data/atlas.json` | uygulamanın veri dosyası (yıllık alanlar, 12 aylık kara verisi, sınıflar) |
| `data/doku.png`, `yukseklik.png`, `kabartma.jpg`, `kabartma_gri.jpg`, `kabartma_bir.jpg` | harita dokuları, ~0.066° (kıyı + okyanus uzaklığı + yumuşak sınıf; yükseklik; üç kabartma: editör görselinden, gri tonlu yükseklik haritasından ve ikisinin birleşimi — büyük biçim griden, ince doku editörden; uygulamada varsayılan birleşik). Editör görseli sahibin KONTURSUZ çıktısı olmalı: konturlu görselde tırtık gölgeye geçiyor |
| `data/dolasim.png` | Dolaşım sekmesi: 12 ay alt alta, R/G = yüzey rüzgârı u/v, B = deniz yüzeyi sıcaklığı; ~0.75° bloklar. Akıntı yolları `atlas.json`'da, motora giren dosyadan olduğu gibi |
| `data/su.json` | su katmanı: nehir kolları (kademe 1-4, debi, fark kodlu 0.01° koordinat) ve göl kıyıları; `su/uret_su.py` yazar (veri.yml ÜRETMEZ; iklim değişirse elle yeniden koşulur, `SU.md`) |
| `uret.py` | dünyayı koşup `data/`'yı yazan tek giriş noktası |
| `doku.py` | harita dokularını üretir (`uret.py` çağırır) |
| `kabartma_kaydet.py` | sahibin editör görselini kabartma kaynağı olarak repoya alır ve araziye oturtur |
| `data/tektonik.json`, `data/levha.png` | tektonik katman: levhalar, sınır çizgileri, volkan kuşakları; harita kutusuna kırpılmış levha kimliği. `tektonik/uygulama.py` yazar (veri.yml üretmez) |
| `data/bitki.png`, `data/bitki_veri.png`, `data/bitki.json` | bitki örtüsü: paletli biyom haritası (~0.044°); kart için kaynak çözünürlükte R = biyom kodu, G = nem oranı, B = en soğuk ay; biyom adları, açıklamaları, renkleri, payları. `bitki/bitki.py` yazar (veri.yml üretmez) |
| `data/toprak.png`, `data/toprak_veri.png`, `data/toprak.json` | toprak türleri: paletli WRB haritası (~0.044°, bitki ile aynı büyütme); kart için kaynak çözünürlükte R = toprak kodu; toprak adları, açıklamaları, renkleri, payları. `toprak/toprak.py` yazar (veri.yml üretmez) |
| `data/yasam.png`, `data/yasam_veri.png`, `data/yasam.json` | yaşanabilirlik: paletli puan sınıfları (~0.044°); kart için kaynak çözünürlükte dikey 5 bölümlü veri PNG'si (0: R = sınıf + 16 × su erişimli, G = puan × 2.5; 1-4: on bir etken 0-255, uygulama bölüm sayısını `etkenler` uzunluğundan alır). `yasam/yasam.py` yazar (veri.yml üretmez) |
| `tektonik/`, `buzul/`, `su/`, `bitki/`, `toprak/`, `yasam/`, `tarim/` | levha modeli, buzul geçmişi, göl ve nehirler, bitki örtüsü, toprak türleri, yaşanabilirlik, tarımsal verimlilik; giriş belgeleri `TEKTONIK.md` (özet `tektonik/OZET.md`), `BUZUL.md`, `SU.md`, `BITKI.md`, `TOPRAK.md`, `YASAM.md`, `TARIM.md` |
| `motor/` | iklim motoru — asıl projedeki `climate/` kopyası |
| `dunya/` | `dunyam.json`, `dunyam.currents.json`, `dunyam_heightmap.png`, `kabartma_kaynak.jpg` |
| `requirements.txt` | numpy, scipy, pillow — hepsi bu |
| `.github/workflows/veri.yml` | değişiklikte veriyi GitHub'da yeniden üretir |
| `test/uygulama_test.js`, `.github/workflows/uygulama.yml` | tarayıcı testi: açılış (tek yükleme), su katmanı (ana/bütün kollar, kapatınca boş, göle dokununca kart), tektonik katman (Levhalar'da çizim ve kartta Levha satırı, Yükseklik'te boş), bitki örtüsü (çizim, kartta Bitki satırı, Yükseklik'te boş), WebGL yokken Canvas2D yedeği, ay şeridinde parmakla tarama, yatay ekranda yan dok, gündüz sıcaklığı katmanı ve kartta gündüz-gece bandı (veride `gezegen` varsa), iki görünümde okyanus koyu, yumuşak/piksel parlaklık eşit, kart (kar satırı dahil), denize dokununca deniz kartı, Kar katmanı, Dolaşım (çizgiler, akıntılar, parçacıklar), katman/ay/kabartma geçişleri, yakınken pan sınırı, geri tuşu, güncelleme denetimi (yeni veride yenileyip bildirir), çevrimdışı (sunucu kapatılarak) ve çevrimdışı güncelleme denetimi. `veri.yml` yeni veriyi bu test geçmeden commit etmez |
| `mevsim_olc.py` | yağışın mevsimselliğini ölçer (kara min/max ay oranı, 36°K kuzeyinde f/s/w payları, korunan istekler, yılda ≥3 kez dönen rüzgâr payı) ve harita çizer; `--p` ile params denemesi, `--kod`/`--kiyas` ile sınıfı değişen kara payı. Veri yazmaz |
| `_senkron_kontrol.py` | kopyalar asıl projeyle aynı mı |
| `yayinla.sh`, `wrangler.jsonc` | Cloudflare derleme komutu ve yayın ayarı: yalnız uygulama dosyalarını `site/`'ye kopyalar (motor ve dünya tanımı yayınlanmaz) |
| `baslat.bat` | yalnız bilgisayarda aç (http://localhost:8778) |
| `tunel.bat` | telefona kurmak için geçici HTTPS tünel (yedek yol; yalnız `yayinla.sh` kümesini `site/`den sunar, liste iki dosyada aynı olmalı) |

`motor/reference.py` **yoktur ve olmamalı**: o dosya Dünya doğrulamasına
özeldir, `rasterio` ister ve kurgusal dünyada hiç koşmaz.

---

## 4. İklimi değiştirmek

```bash
pip install -r requirements.txt
python uret.py --res 1.0 --ozet     # kaba deneme, ~1 dk
python uret.py --ozet               # gerçek çözünürlük (0.25), ~16 dk (GitHub'da ~12)
```

`uret.py` dünyayı `dunya/`'dan okur, motoru koşar, iç tutarlılık raporunu
basar, `data/atlas.json`'u yazar.

**İç tutarlılık kontrollerinden biri düşerse veri YAZILMAZ** (`--zorla` ile
geçilir). Bu kontroller modelin kendi fiziğiyle çelişip çelişmediğine bakar:
sıcaklık enlemle düşüyor mu, yükseklik sabitken yüksek yerler soğuk mu,
yarıkürelerin mevsimleri ters mi, okyanusun mevsim genliği karadan küçük mü,
sınıf dağılımı dejenere mi. Düşen bir kontrol neredeyse her zaman **bozuk
girdi** demektir — ters çevrilmiş yükseklik haritası, yanlış
`sea_level_value`, saçma bir parametre — model hatası değil.

### Neyi nereden değiştirirsin

| ne | yer |
|---|---|
| gün uzunluğu, eksen eğikliği, deniz seviyesi sıcaklığı, yıl | `dunya/dunyam.json` üst seviye |
| yağış, muson, kuşak salınımı, engellenme | `dunya/dunyam.json` → `params` |
| deniz seviyesi değeri, en yüksek nokta, yükseklik eğrisi | `dunya/dunyam.json` → `heightmap` |
| okyanus akıntıları | `dunya/dunyam.currents.json` |
| arazi | `dunya/dunyam_heightmap.png` (16 bit gri, 2:1 equirectangular) |
| hesaplama yöntemi | `motor/` — `moisture.py`, `temperature.py`, `circulation.py`, `koppen.py` … |

`dunyam.json`'daki `_` ile başlayan alanlar **karar günlüğüdür**: her ayarın
neden o değerde olduğu, hangi seçeneklerin ölçülüp elendiği orada yazılı.
Bir ayarı değiştirirken oradaki notu da güncelle — bu proje boyunca en çok
işe yarayan alışkanlık bu oldu. Notla veri çelişiyorsa bu bir hatadır.

### GitHub üzerinden, bilgisayar açmadan

`dunya/`, `motor/`, `uret.py` ya da `doku.py` değişip push edilince
`.github/workflows/veri.yml` `uret.py`'yi koşar, yeni veriyle uygulama testini
koşar ve test geçerse değişen `data/`'yı commit eder. Motor belirlenimci:
girdi aynıysa `surum` aynı çıkar ve commit atılmaz; test adımı da yalnız veri
değiştiğinde koşar (ilk kez 24 Eylül'de, rapor metni değişikliğinde koştu ve
geçti). Actions sekmesinden **atlas verisi → Run workflow** ile elle de
başlatılır (çözünürlük orada seçilir). Ölçüldü: 1365×682 hücre, 12/12
tutarlılık, GitHub koşucusunda ~12 dk (aylar paralel; sıralıyken ~20). Koşu sırasında dala başka commit
gelirse iş akışı push'tan önce `git pull --rebase` yapar.

---

## 5. Motorun yapısı

Katman numaraları özgün plandan gelir; **koşma sırası bağımlılıklara göredir
ve bilerek farklıdır.** Gerçek sırayı bilen tek yer `motor/model.py`:

```
dolasim -> SST -> taban kara sicakligi -> denizellik -> muson
                                            ^             |
                                            +-------------+   (TEK dongu)
                                  -> lapse -> nem -> koppen
```

### Kırılması kolay sıra kısıtları

- **Okyanus karadan önce çözülür.** Kara enerji dengesi okyanus çözümüne
  zayıf-sıcaklık-eğimi terimiyle bağlanır.
- **Denizellik lapse'ten önce koşar.** Hava kütlesi deniz seviyesinde
  değiştirilir, sonra kaldırılır. `apply_lapse` son sıcaklık adımıdır.
- **Denizellik rüzgâr ister, muson sıcaklık ister.** Bu yüzden tek geri
  besleme geçişi var: zonal rüzgâr → sıcaklık → basınç anomalisi →
  düzeltilmiş rüzgâr → yine sıcaklık. Sabit geçiş sayısı belirlenimciliği
  korur.
- **Küresel koşular boylamda sarmalanır.** Her katman `Grid.ddx` / `smooth` /
  `sample` / `wrap_j` üzerinden gider. Yeni bir katman eklemek bu yardımcıları
  kullanmak demektir, ham `np.gradient(..., axis=1)` değil.
- **Kara maskesi kaynak çözünürlüğünde, küçültmeden ÖNCE hesaplanır.**
  Tersi dar boğazları kapatır.

### Değişmezler

- `Grid.lat` **kuzeyden güneye, azalan.** Bütün meridyenel eğim işaretleri
  buna bağlı.
- `grid.elev` okyanus hücrelerinde **deniz tabanıdır.** Havanın üzerinde
  aktığı yüzeyi düşünen her şey kelepçelemeli:
  `np.maximum(elev, sea_level_m)`. Unutulduğunda her kıyıda sahte 3100 m'lik
  bir tırmanış çıkmıştı.
- **Rüzgâr hiçbir zaman kuralla dayatılmaz**, her zaman basınç eğiminden
  türetilir. `monsoon.py`'nin yalnızca bir basınç anomalisi eklemesi ve aynı
  fonksiyonun muson rüzgârını üretmesi bu yüzden.
- **Elle yazılan dünya dosyaları bir güven sınırıdır.** `load_currents` her
  akıntıyı doğrular (yol ≥ 2 nokta, `width_km` > 0), çünkü bir yazım hatası
  eskiden sessizce yutuluyordu. Aynı sebeple `uret.py` ve `mevsim_olc.py`
  motorun okumadığı `params` adında durur (`bilinmeyen_params`; `heightmap` anahtarlarında da; yeni bir
  parametre katmanın `DEFAULTS`'una ya da `params.get("..")` ile eklenmeli).
- Motor çekirdeği **saf numpy + scipy**. `grid.from_heightmap` bir zamanlar
  koşulsuz `import rasterio` yapıyordu ve bu repo GitHub Actions'ta tam o
  satırda düştü; artık `_heightmap_oku` Pillow'a düşüyor ve iki okuyucu
  birebir aynı diziyi veriyor.

---

## 6. Dünyanın kimliği

Bu sayılar dünyanın kendisidir; değiştirmek başka bir gezegen yapar.

| ne | değer | neden |
|---|---|---|
| gün uzunluğu | 15 saat | işaretli platoda bozkır isteniyordu; 24 saatlik günde orası %0 bozkırdı. Hızlı dönüş Hadley hücresini daraltır, iç kesimlere nem taşınımını zayıflatır |
| eksen eğikliği | 28° | soğutmanın tundra bedelini ödüyor (yazları ısıtır) |
| deniz seviyesi ort. sıcaklık | 14 °C (girdi; modelin çıkan küresel ortalaması 15.1) | savan payını %19'dan ~%9'a indirmek için. Fark akıntı ve denizellikten, 24 Eylül'den beri aynı; tutarlılık kontrolü ±3 °C ile geçer |
| kara kuşağı | 60°K .. −7°K | 40-70°K'de dünya çok sertti; tek işleyen kol karayı güneye taşımaktı |
| en yüksek nokta | 7000 m | dünyanın sahibi bildirdi (önce 6700) |
| yükseklik eğrisi | sahibin çapaları | ova 250-300 m, plato çanağı 800-1000 m, Büyük Duvar zirveleri 6000 m, en yüksek 7000 m; aralar PCHIP. Kıta **bilerek** Dünya'dan yüksek (kara medyanı ~950 m, Dünya 377). Ayrıntı `_elev_curve` |
| kara payı | ~%6.9 (alan) | hücre sayarak %5.4 — ikisi aynı şey değil (§7.1) |

Akıntılar: 15 saatlik gün gezegeni çok hücreli yapıyor (ölçülen kuşak
sınırları 17°K/37°K/57°K), o yüzden Dünya'daki tek subtropikal jir yerine
burada **üç jir** üst üste diziliyor.

---

## 7. Tuzaklar

### 7.1 Sınıf payları hücre sayısıdır, alan değil

Equirectangular gridde hücre alanı cos(enlem) ile küçülür; hücre saymak
yüksek enlemleri şişirir. Beck'in gözlem rasterinde ölçüldü: E sınıfı hücre
sayarak %30.0, alan ağırlıklı %11.6 (yayınlanan değer %12.8). Fark 37.5
puanken alan ağırlıklı fark 8.6 puana düşüyor.

**Kullanıcıya gösterilen her oran alan ağırlıklı olmalı.** `uret.py`'nin
künye ve özet fonksiyonları öyle. Bu bir kez atlanmıştı ve atlas kara
yağışını 1375 gösteriyordu; doğrusu 1492 idi.

### 7.2 Engellenme çözünürlüğe bağlı ve kaba tarama yanıltır

Akış engellenmesi **ilerletme adımı başına** (25 km) kazanılan yüksekliğe
bakar. Arazi ince gridde daha pürüzlüdür: ölçüldü, 25 km'lik adımda ortalama
tırmanış 0.5 derecede 152 m, 0.26 derecede **189 m**; eşiği aşan hücre payı
%14 → %20. Yani aynı `blocking_dz_m` ince çözünürlükte daha sert engeller.
0.5 derecelik bir tarama 1800 m demişti; 0.26'da o ayar hiçbir şeyi
düzeltmedi (kama payı %4.4 yerine %25).

**Engellenme ayarını koşacağın çözünürlükte seç.**

### 7.3 `uretim` damgası dosyayı her koşuda değiştirir

`data/atlas.json` bir zaman damgası taşır. `git diff` ile "değişti mi" diye
bakmak bu yüzden her zaman "evet" der ve 2 MB'lık boş commit'ler birikir.
İçerik özeti olan **`surum`** alanı karşılaştırılır. Workflow öyle yapıyor.

İki bağımsız üretici aynı sonucu veriyor: masaüstündeki `_atlas.py`
(viewer.json'dan) ve buradaki `uret.py` (kendi koşusundan) aynı içerik özetini
üretti, yalnız zaman damgası farklıydı.

### 7.4 Palet iki yerde duruyor — ŞU AN AYRIŞIK

`app.js` içindeki `KPAL` (renkler) ve `KREF` (Dünya karşılıkları) blokları
masaüstü şablonuyla birebir aynı olmalıydı; asıl projedeki `_atlas.py` ikisini
karşılaştırır ve farklıysa durur. İki kopyanın sessizce ayrışması bu projede
zaten bir kez gerçek bir hataya yol açtı.

**Eylül 2026'da bilerek ayrıştırıldı:** yeni koyu arayüz için `KPAL` yeniden
kuruldu (düşük doygunluk, kabartmayla okunur; ana grup ton aileleri aynı).
`KREF` değişmedi. Masaüstü şablonu yeni palete taşınana kadar `_atlas.py`'nin
palet karşılaştırması DURACAK; bu beklenen bir sonuç, hata değil. Karar:
dünyanın sahibi onayladı.

### 7.5 Kurulu PWA kurulduğu adrese bağlıdır

Geçici Cloudflare tünelleri her açılışta yeni adres verir. Telefondaki
uygulama hangi adresten kurulduysa ona bağlıdır — tarayıcılar her adresi ayrı
bir site sayar. Dünkü tünelden kurulan uygulama bugünkü tünelden habersizdir:
ölü adrese gider, 4 saniye sonra önbelleğe düşer ve **eski veriyi** gösterir.
Hata değil, tasarım. Kendini güncelleyebilmesi sabit bir adres ister.

**Eylül 2026: sabit adres Cloudflare ile KURULDU** (Workers, yalnız statik
dosya; `wrangler.jsonc`). Cloudflare private repoyu okur, her push'ta
`sh yayinla.sh` koşar ve `npx wrangler deploy` `site/`'yi yayınlar; diğer
dalların ayrı önizleme adresi olur. **Üretim dalı Cloudflare ayarıdır** (Settings → Build → Branch control): 26 Eylül'de `main` değildi ve `main` push'ları yalnız önizleme olarak derleniyordu; GitHub'daki "Workers Builds" onayı yine yeşildi. Telefona gelmeyen bir değişiklikte önce Cloudflare → Deployments'a bak. Önünde Cloudflare Access durur (yalnız
sahibin e-postası). Access'in çerezi manifest isteğine gitsin diye
`index.html`'de manifest bağlantısı `crossorigin="use-credentials"` taşır;
kaldırılırsa telefona kurulum sessizce bozulur. Access oturumu dolunca `sw.js`
sayfa isteğindeki yönlendirmeyi tarayıcıya bırakır (giriş sayfası açılır);
önbellekten eski sayfayı verseydi uygulama sessizce eski veride kalırdı.
İnternet yoksa önbellekten açılır. Tünel ve Termux yolu yedek
olarak duruyor.

### 7.6 Kopyalar ayrışabilir

`motor/` ve `dunya/` asıl projedeki dosyaların kopyasıdır. Kopyalama **tek
yönlüdür** (proje → repo, `_repo_senkron.py --yaz`) ve asıl projedeki
`_denetim.py` her koşuda farkı kontrol eder. Buradan da bakılabilir:

```bash
python _senkron_kontrol.py /asil/projenin/yolu
```

Bu repoda `motor/` ya da `dunya/` içinde değişiklik yaparsan asıl proje geride
kalır. Küçük bir düzeltme için sorun değil; kalıcı bir değişiklikse asıl
projeye de taşı.

**Şu an böyle bir ayrışma VAR** (motor tarafı): `motor/moisture.py` fırtına
yolu terimi (`storm_c`) ve karşıtlığın ay içi dağılımı (`storm_contrast_sigma_k`), `motor/grid.py` bölünmeyen kaynağı yeniden örnekleme
ve dikişte su kütlesi birleştirme, `motor/sanity.py` donmuş okyanus oranı ve
alan ağırlıklı kara yağışı / sınıf payı, `motor/maritime.py` hafif deniz buzu
(`sea_ice_air`), `motor/moisture.py` nem korunumu (`conserve_moisture`) ve ayların paralel
çözümü (`run`, sonucu değiştirmez) ve ay süresinin gezegen yılından alınması (`_saniye_ay`, Dünyam'da etkisiz), `motor/circulation.py` `belt_shift_decay` (kapalı) ve `motor/temperature.py` akıntı uzaklığında gezegen yarıçapı (111.32/110.57 sabiti kalktı) yalnız bu repoda. Asıl projeye
taşınmalı.

**Arazi tarafında da ayrışma VAR:** `dunya/dunyam_heightmap.png` (kara pikselleri
sahibin kendi PNG'sinden, kayıtla aktarıldı) ve `elev_curve` (sahibin çapaları)
yalnız bu repoda; 24 Eylül'de açılan kanal ve üç kıyı girintisi de
(`_heightmap_kaynak`), kontursuz editör görseli `kabartma_kaynak.jpg` ve
`heightmap.kabartma` kaydı da. Asıl projede `_repo_senkron.py --yaz`
koşulursa hepsini eski hâline döndürür; `_egri_kur.py --yaz` koşulursa eğriyi yeniden Dünya
hipsometrisine zorlar. Önce bu iki dosyayı asıl projeye taşı. Ayrıntı
`dunyam.json` → `_heightmap_kaynak`, `_elev_curve`.

### 7.7 Bulut makinesinde uygulama performansı yanıltır

Playwright'ın Chromium'u burada GPU'yu yazılımla taklit ediyor (SwiftShader).
Büyük bir SVG ya da tuval katmanını birleştirmek bu yüzden telefondakinden
çok pahalı görünür: Dolaşım'da sürükleme Iklim'in ~5 katı sürdü, ama JS
profili neredeyse boştu. Ölçerken ayır: JS maliyeti için CPU'yu 4 kat
yavaşlat (`Emulation.setCPUThrottlingRate`, orta sınıf telefon yaklaşığı) ve
CDP profilini oku; çizim maliyetini telefonda gözle doğrula. Açılış ölçümü
(25 Eylül, CPU ×4): `veriHazirla` 239 ms, toplam açılış ~2.3 s.

Aynı ortamda **çevrimdışı taklidi (`context.setOffline`) yeniden başlayan
service worker'a uygulanmıyor**: sayfa yeniden yüklenince SW sunucuya ulaşır.
Çevrimdışını sınarken sunucuyu da kapat; testte öyle (`uygulama_test.js`).

---

## 8. Motorun bilinen sınırları

Bunlar kurgusal dünyada da geçerli; bir sonucu "hata" diye kovalamadan önce
buraya bak.

- **Yağış zayıf katman.** Uzamsal korelasyon Dünya doğrulamasında 0.47.
  Yağışın yeri (hangi hücrenin ıslak olduğu) rüzgâr alanı ve nem taşınımıyla
  belirlenir; bir katsayıyla düzeltilemez.
- **Yağış zaman ekseninde iki kat fazla mevsimsel.** Şema `p ~ W^a · conv^b`
  olduğu için ulaşılabilecek en iyi mevsimsel oran çarpanların kendi
  oranlarının çarpımıdır. Yakınsama çekilince modelde devreye girecek başka
  bir mekanizma yok, o yüzden mevsim dışı yağış sıfıra çöküyor.
- **Gezici siklon / jet akımı yok — yalnız bir yaklaşığı var.** `storm_c`
  (motor/moisture.py) siklonları tek tek çözmez: kara-okyanus sıcaklık
  karşıtlığından bir kış yağışı kuşağı kurar ve okyanus havasını termal
  rüzgârdan türetilen üst seviye akışla, sırtlarda engellenerek taşır. Kıyı
  ve iç deniz çevresinin kışını ıslatır; kıta içini pek ıslatamaz (40-50°K
  kış ayı ~19 mm, Moskova 55). Varsayılan 0 = kapalı. Terim olmadan Akdeniz'in
  kış yağışı yalnız basınç kuşaklarının salınımından gelir ve kuşak lekeler
  hâlinde kalır. Ayrıntı ve elenen dört kol: `_firtina`.
  Karşıtlık aylık ortalamaya değil ay içi dağılıma uygulanır
  (`storm_contrast_sigma_k`, Dünyam'da 10 K, motor 0): ilkbaharda ortalama
  sıfıra inince terim tamamen sönüyordu ve 36°K kuzeyinde en kurak ay Mart
  çıkıyordu. Yalnız geçiş aylarına yağış ekler. Kıta içine yine ulaşmaz:
  orada darboğaz sırtlardaki engellenme.
- **Yağış hâlâ çok mevsimsel.** Kara min/max ay oranı 0.076 (Dünya gözlemi
  0.249); ılıman kuşakta Cf azınlık, Cw baskın. Yaz tepesini indirmek
  (`convective_c`, muson) karanın %13-16'sının sınıfını değiştirip bozkır
  üretiyor, o yüzden seçilmedi. Ölçmek için `mevsim_olc.py`. Önemli bir
  kaynak kuşak salınımı (aşağıda): 1 derecede `k_itcz` 0.2 ile oran 0.138,
  ama Akdeniz bandında Cs %47 → %7 ve B %9 → %22 (26 Eylül).
- **Basınç kuşakları ITCZ ile katı kayar.** `circulation._belt_nodes` bütün
  kuşakları (kutup yüksekleri dahil) ITCZ kadar kaydırır. Dünyam'da kuşak
  aralığı φ_H 18.8° (15 saatlik gün), ITCZ salınımı `k_itcz` 0.6 × 28° =
  ±16.8°: her enlem yılda neredeyse bir kuşak ileri geri geçer, okyanusun
  %77'sinde yüzey rüzgârı yılda 3-4 kez yön değiştirir (0.2 ile %0.1;
  26 Eylül ölçümü, `gece_resim/zonal_ruzgar.png`). Akdeniz kuşağı bu
  salınımdan gelir. Yıllık ortalama rüzgâr vektörü bu yüzden zayıftır;
  uygulama yıllık hız için aylık hızların ortalamasını kullanır.
  Deneme düğmesi `belt_shift_decay` (motor 0 = katı kayma, bit bit eski;
  Dünyam'da kapalı): 0.25'te dönüş %20 ama karanın %38'i sınıf değiştirir
  (`gece_resim/kusak_kaymasi.png`).
- **60-70° kuşağında mevsim genliği yetersiz** (en soğuk ay fazla ılık).
  `transport_seasonal_lat_deg` bunu düzeltir ama 70° üstünde aşırı büyütür;
  karası 70°'nin altında biten bir dünyada açmaya değer, büyük kutup kıtası
  varsa kapalı bırak. Varsayılan 0 = kapalı.
- **Deniz buzu yalnız hafif sürümde var.** Okyanus sıcaklığı donma noktasında
  kelepçelenir (okyanus-ayların ~%15'i; eşik %35). `sea_ice_air` (Dünyam'da
  1, motor varsayılanı 0) donmuş denizin kıyıya buz üstü havası taşımasını
  sağlar: kuzey kıyı şeridinin kışı soğur (en çok −18.6 °C), sınıflar
  neredeyse değişmez. Buz-albedo ve buharlaşma kesintisi **bilerek yok**
  (kendini besleyen döngü, Dünya doğrulaması). Ayrıntı: `_deniz_buzu`.
- **`gravity_ms2` hiçbir şey tarafından okunmuyor.** Bilerek: ait olduğu üç
  yer de Dünya'ya uydurulmuş sabitler taşıyor. `test_gravity_is_inert` yarım
  bağlamayı engelliyor.
- **Su bütçesi Dünya'nınkinin iki katıydı; Dünyam'da yarı yolda düzeltildi.**
  Yakınsama, girdap ve fırtına yağışı nemden düşülmüyordu (yağışın ~%30'u
  yoktan). `conserve_moisture` (motor 0, Dünyam 1) bunu düşer. Tek başına
  açmak dünyayı kurutur (B %6 → %43): nem karaya ulaşmıyordu. O yüzden
  birlikte `land_recycle` 0.65 ve `eddy_blend` 0.02. Sabit `evap_max`
  tavanı YANLIŞ: ortalama akışı her yerde üst sınır yapıyor, kuru havanın
  iç denizlerde nemlenmesini kesiyor. Küresel yağış hâlâ ~1540 mm (Dünya
  ~1015); kalan fazla `rh_ocean`'dan. Dünya doğrulamasında korunum açık
  denenmedi. Ayrıntı `_su_butcesi`.

---

## 9. Arazi değişince ne yapılır

Dünyanın sahibi araziyi MerakMapMaker'da düzenleyip yeni bir `.glb` verdiğinde
asıl projede şu zincir koşar:

1. `python _mk_heightmap.py` — `worldinfo/` içindeki **en yeni** arazi
   dosyasından (`.glb` varsa o, yoksa 16 bit PNG) gezegen tuvalini üretir ve
   `data/work/` altına yazar. Kıta, `KARA_MERKEZ_LON` ile boylamda sabitlenir
   — yoksa her yeni arazi sürümünde birkaç derece kayar ve akıntılar,
   işaretli bölge, notlardaki bütün boylamlar sessizce yanlış olur. Betik
   `file` / `sea_level_value` / `max_depth_m` alanlarını **kendi** yazar;
   bunlar elle taşınmaz.
2. **ŞU AN KOŞMA** (§6, §7.6): `elev_curve` artık sahibin çapalarıyla kurulu
   ve bu betik onu siler. Aşağıdaki yöntem eski yoldur, çapalar asıl projeye
   taşınmadan kullanılmaz.
   `python _egri_kur.py --yaz` — `elev_curve`'ü kurar. Yöntem: karanın alan
   ağırlıklı gri ton dağılımı, ETOPO'dan **ölçülmüş** gerçek Dünya buzsuz kara
   hipsometrisine nicelik eşlemesiyle oturtulur (`f = Q(F(v))`). Çizimin kendi
   biçimi korunur, yalnız ölçek gerçeğe oturur. Bölge kutusu yoktur ve elle
   taşınacak çapa yoktur.
3. `python _akinti_kur.py` — **yalnız kıyı değiştiyse**; akıntı yollarını
   gerçek kıyı çizgisinden yeniden türetir.
3b. **Kabartma görseli:** editörden aynı çerçevede yeni bir renkli görsel al
   (**konturlar kapalı**; konturlu görselde tırtık gölgeye geçer) ve
   bu repoda `python kabartma_kaydet.py <görsel>` koş. Görsel yenilenmezse
   uygulamadaki gölge eski dağları gösterir; `uret.py` görselin karaya
   oturmasını her koşuda ölçer ve %95'in altındaysa uyarır.
4. 0.26 derecelik koşu, `export_viewer.py --res 0.26`, `_atlas.py`,
   `_denetim.py`, `node _atlas_test.js`, `_repo_senkron.py --yaz`.
   **DİKKAT:** `_atlas.py` mobil `data/atlas.json`'u eski biçimde yazar (aylık
   veri ve dokular yok) ve yeni uygulama açılmaz. Mobil veri yalnız bu
   repodaki `uret.py`'den üretilir.
5. Bu repoda commit + push; workflow veriyi yeniden üretir.

**Sıra kuralı (sert):** eğri düzelmeden nem düğmesi (`convective_c`,
`rh_ocean`, `blocking_*`) ayarlanmaz. Bayat bir eşlemeyle ayarlanan düğme,
eğri düzelince yanlış kalır ve yanlışlığı *arazi kusuru gibi* görünür — bu bir
kez oldu, aynı çizim `convective_c`'ye göre kurak payını %42 ya da %8
veriyordu ve arada geçen sürede arazi suçlandı. Ayrıntı: `docs/08` 4.5.

Kaynak tercihen `.glb`'dir: orada z gerçek yüksekliktir. Sahibinin PNG çıktısı
da **desteklenir ve kullanıldı** — kıyı sahanlığı eğimleri vardır, ama derin
okyanus tabanı düz tek bir değerdir. Modelde neredeyse etkisiz (hava akışı
okyanus üzerinde deniz seviyesine kelepçelenir).
