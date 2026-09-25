# CLAUDE.md — Dünyam Atlası (mobil repo)

Bu dosya, bu repoda çalışan Claude Code oturumları içindir. Amacı iki şey:
**dünyanın sahibinin ne istediğini** kaybetmemek, ve **neyin neden öyle
olduğunu** yeniden keşfetmek zorunda kalmamak.

Belgeler ve kod yorumları **Türkçe**. Kullanıcı Türkçe çalışıyor.

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
  ince örtü. Hiç erimeyen hücreler kartta "kalıcı (buzul)". Veriyi `data/atlas.json`'dan,
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
  makinesinde ~35 dakika (nem korunumu açıkken ölçüldü, 25 Eylül; kapalıyken
  ~14 dk idi, eski masaüstünde ~40 dk). Yavaşlığın yarısından fazlası
  `grid.smooth`: korunum her adımda bir Gauss yumuşatması daha ekliyor.
  Arka plana al, o sırada bağımsız işi yap. Çıktıyı dosyaya yönlendirdiğinde
  tamponlanır — koşu bitene kadar dosya boş görünebilir, bu normal.
- **Yüzdeler alan ağırlıklı olacak.** Kullanıcıya gösterilen her oran.
  Gerekçe aşağıda (§7.1).

---

## 3. Repo düzeni

| yol | ne |
|---|---|
| `index.html`, `style.css`, `app.js` | uygulama (dokunmatik pan/pinch, hücre kartı, alt panel) |
| `sw.js`, `manifest.webmanifest`, `icons/` | kurulum ve çevrimdışı çalışma |
| `data/atlas.json` | uygulamanın veri dosyası (yıllık alanlar, 12 aylık kara verisi, sınıflar) |
| `data/doku.png`, `yukseklik.png`, `kabartma.jpg`, `kabartma_gri.jpg`, `kabartma_bir.jpg` | harita dokuları, ~0.066° (kıyı + okyanus uzaklığı + yumuşak sınıf; yükseklik; üç kabartma: editör görselinden, gri tonlu yükseklik haritasından ve ikisinin birleşimi — büyük biçim griden, ince doku editörden; uygulamada varsayılan birleşik). Editör görseli sahibin KONTURSUZ çıktısı olmalı: konturlu görselde tırtık gölgeye geçiyor |
| `data/dolasim.png` | Dolaşım sekmesi: 12 ay alt alta, R/G = yüzey rüzgârı u/v, B = deniz yüzeyi sıcaklığı; ~0.75° bloklar. Akıntı yolları `atlas.json`'da, motora giren dosyadan olduğu gibi |
| `uret.py` | dünyayı koşup `data/`'yı yazan tek giriş noktası |
| `doku.py` | harita dokularını üretir (`uret.py` çağırır) |
| `kabartma_kaydet.py` | sahibin editör görselini kabartma kaynağı olarak repoya alır ve araziye oturtur |
| `motor/` | iklim motoru — asıl projedeki `climate/` kopyası |
| `dunya/` | `dunyam.json`, `dunyam.currents.json`, `dunyam_heightmap.png`, `kabartma_kaynak.jpg` |
| `requirements.txt` | numpy, scipy, pillow — hepsi bu |
| `.github/workflows/veri.yml` | değişiklikte veriyi GitHub'da yeniden üretir |
| `test/uygulama_test.js`, `.github/workflows/uygulama.yml` | tarayıcı testi: açılış (tek yükleme), iki görünümde okyanus koyu, yumuşak/piksel parlaklık eşit, kart (kar satırı dahil), Kar katmanı, Dolaşım (çizgiler, akıntılar, parçacıklar), katman/ay/kabartma geçişleri, yakınken pan sınırı, çevrimdışı. `veri.yml` yeni veriyi bu test geçmeden commit etmez |
| `mevsim_olc.py` | yağışın mevsimselliğini ölçer (kara min/max ay oranı, 36°K kuzeyinde f/s/w payları, korunan istekler) ve harita çizer; `--p` ile params denemesi, `--kod`/`--kiyas` ile sınıfı değişen kara payı. Veri yazmaz |
| `_senkron_kontrol.py` | kopyalar asıl projeyle aynı mı |
| `yayinla.sh`, `wrangler.jsonc` | Cloudflare derleme komutu ve yayın ayarı: yalnız uygulama dosyalarını `site/`'ye kopyalar (motor ve dünya tanımı yayınlanmaz) |
| `baslat.bat` | yalnız bilgisayarda aç (http://localhost:8778) |
| `tunel.bat` | telefona kurmak için geçici HTTPS tünel |

`motor/reference.py` **yoktur ve olmamalı**: o dosya Dünya doğrulamasına
özeldir, `rasterio` ister ve kurgusal dünyada hiç koşmaz.

---

## 4. İklimi değiştirmek

```bash
pip install -r requirements.txt
python uret.py --res 1.0 --ozet     # kaba deneme, ~1 dk
python uret.py --ozet               # gerçek çözünürlük (0.25), ~35 dk (GitHub'da ~20)
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
tutarlılık, GitHub koşucusunda ~20 dk (nem korunumundan önce ~12). Koşu sırasında dala başka commit
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
  eskiden sessizce yutuluyordu.
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
| deniz seviyesi ort. sıcaklık | 14 °C | savan payını %19'dan ~%9'a indirmek için |
| kara kuşağı | 60°K .. −7°K | 40-70°K'de dünya çok sertti; tek işleyen kol karayı güneye taşımaktı |
| en yüksek nokta | 7000 m | dünyanın sahibi bildirdi (önce 6700) |
| yükseklik eğrisi | sahibin çapaları | ova 250-300 m, plato çanağı 800-1000 m, Büyük Duvar zirveleri 6000 m, en yüksek 7000 m; aralar PCHIP. Kıta **bilerek** Dünya'dan yüksek (kara medyanı ~950 m, Dünya 377). Ayrıntı `_elev_curve` |
| kara payı | ~%6.8 (alan) | hücre sayarak %5.3 — ikisi aynı şey değil (§7.1) |

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
dalların ayrı önizleme adresi olur. Önünde Cloudflare Access durur (yalnız
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
(`sea_ice_air`), `motor/moisture.py` nem korunumu (`conserve_moisture`) yalnız bu repoda. Asıl projeye
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
- **Yağış hâlâ çok mevsimsel.** Kara min/max ay oranı 0.078 (Dünya gözlemi
  0.249); ılıman kuşakta Cf azınlık, Cw baskın. Yaz tepesini indirmek
  (`convective_c`, muson) karanın %13-16'sının sınıfını değiştirip bozkır
  üretiyor, o yüzden seçilmedi. Ölçmek için `mevsim_olc.py`.
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
