# CLAUDE.md — Dünyam Atlası (mobil repo)

Bu dosya, bu repoda çalışan Claude Code oturumları içindir. Amacı iki şey:
**dünyanın sahibinin ne istediğini** kaybetmemek, ve **neyin neden öyle
olduğunu** yeniden keşfetmek zorunda kalmamak.

Belgeler ve kod yorumları **Türkçe**. Kullanıcı Türkçe çalışıyor.

---

## 1. Bu repo nedir

Kurgusal bir gezegenin iklim atlası. İki parçası var:

- **Uygulama** (`index.html`, `app.js`, `style.css`, `sw.js`) — telefona
  kurulan bir PWA. Haritayı, sınıf dağılımını, hücre kartını ve iç tutarlılık
  raporunu gösterir. Veriyi tek bir dosyadan okur: `data/atlas.json`.
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
- **Mobil uygulama hızlı güncellenebilir olmalı**, private repo, tünelle
  telefona kurulur. Veri değişince uygulama koduna dokunulmaz.

### 2.2 İklim istekleri (dünyanın nasıl hissettirmesi gerektiği)

Bunların her biri bir şikâyetten doğdu ve ölçülerek karşılandı. Gerekçeler ve
elenen kollar `dunya/dunyam.json` içindeki `_` ile başlayan notlarda.

| istek | nasıl karşılandı | not |
|---|---|---|
| "yağış olayları çok abartı, her yer muson/yağmur ormanı" | `convective_c` 0.42 → 0.12, `rh_ocean` 0.80 → 0.70 | `_yagis_ayari` |
| "gerçek ve büyük bir Akdeniz kuşağı istiyordum, hiç yok" | `k_itcz` 0.20 → 0.60, muson kapatıldı | `_akdeniz` |
| "savan oranını azaltalım, yerine ılıman kuşak, ~%9" | deniz seviyesi sıcaklığı 20 → 14 °C, eksen eğikliği 23.44° → 28° | `_savan` |
| "orta hattında mor ok gibi bir kuşak var" | `moist_crit_soft` 0.10 (yeni parametre), `blocking_spread_km` 1600 | `_ok_seridi` |
| "batıdaki kama da düzelsin" | `blocking_dz_m` 900 → 3600 | `_ok_seridi` |
| "işaretli platoda at göçebesi bozkırı olsun, ortası hardcore çöl olmasın" | gün uzunluğu 15 saat | `_donus` |
| "dünya çok sert, yaşanabilir olsun" | kara 60°K..−7°K'ye taşındı | `_yumusatma` |
| "en üst 60 olsun, orta olsun" | `KUZEY_KARA, GUNEY_KARA = 60, -7` | `_mk_heightmap.py` |
| "sol üstteki bölge çok soğuk" | dünyanın sahibi araziyi kendisi alçalttı | `_bekleyen` |

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
- **Uzun koşu sırasında boş bekleme.** 0.25 derecelik koşu ~40 dakika.
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
| `data/atlas.json` | uygulamanın okuduğu tek veri dosyası |
| `uret.py` | dünyayı koşup `data/atlas.json`'u yazan tek dosya |
| `motor/` | iklim motoru — asıl projedeki `climate/` kopyası |
| `dunya/` | `dunyam.json`, `dunyam.currents.json`, `dunyam_heightmap.png` |
| `requirements.txt` | numpy, scipy, pillow — hepsi bu |
| `.github/workflows/veri.yml` | değişiklikte veriyi GitHub'da yeniden üretir |
| `_senkron_kontrol.py` | kopyalar asıl projeyle aynı mı |
| `baslat.bat` | yalnız bilgisayarda aç (http://localhost:8778) |
| `tunel.bat` | telefona kurmak için geçici HTTPS tünel |

`motor/reference.py` **yoktur ve olmamalı**: o dosya Dünya doğrulamasına
özeldir, `rasterio` ister ve kurgusal dünyada hiç koşmaz.

---

## 4. İklimi değiştirmek

```bash
pip install -r requirements.txt
python uret.py --res 1.0 --ozet     # kaba deneme, ~1 dk
python uret.py --ozet               # gerçek çözünürlük (0.25), ~20-30 dk
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

`dunya/`, `motor/` ya da `uret.py` değişip push edilince
`.github/workflows/veri.yml` `uret.py`'yi koşar ve değişen `data/atlas.json`'u
commit eder. Actions sekmesinden **atlas verisi → Run workflow** ile elle de
başlatılır (çözünürlük orada seçilir). Ölçüldü: 1365×682 hücre, 11/11
tutarlılık, GitHub koşucusunda ~12 dk.

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
| en yüksek nokta | 6700 m | dünyanın sahibi bildirdi |
| `elev_gamma` | 2.0 | **zorunlu**: doğrusal eşlemede karanın %75'i 2000 m üstüne çıkıyor ve bütün kıta tundraya dönüyordu |
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

### 7.4 Palet iki yerde duruyor

`app.js` içindeki `KPAL` (renkler) ve `KREF` (Dünya karşılıkları) blokları
masaüstü şablonuyla birebir aynı olmalı. Asıl projedeki `_atlas.py` ikisini
karşılaştırır ve farklıysa durur. İki kopyanın sessizce ayrışması bu projede
zaten bir kez gerçek bir hataya yol açtı.

### 7.5 Kurulu PWA kurulduğu adrese bağlıdır

Geçici Cloudflare tünelleri her açılışta yeni adres verir. Telefondaki
uygulama hangi adresten kurulduysa ona bağlıdır — tarayıcılar her adresi ayrı
bir site sayar. Dünkü tünelden kurulan uygulama bugünkü tünelden habersizdir:
ölü adrese gider, 4 saniye sonra önbelleğe düşer ve **eski veriyi** gösterir.
Hata değil, tasarım. Kendini güncelleyebilmesi sabit bir adres ister; şimdilik
bilerek kurulmadı.

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
- **Gezici siklon / jet akımı yok.** Bu dünyada Akdeniz'in kış yağışı gerçek
  fırtına yolundan değil, basınç kuşaklarının salınımından geliyor. Bu yüzden
  kuşak tek parça bir kıyı şeridi değil, lekeler hâlinde.
- **60-70° kuşağında mevsim genliği yetersiz** (en soğuk ay fazla ılık).
  `transport_seasonal_lat_deg` bunu düzeltir ama 70° üstünde aşırı büyütür;
  karası 70°'nin altında biten bir dünyada açmaya değer, büyük kutup kıtası
  varsa kapalı bırak. Varsayılan 0 = kapalı.
- **`gravity_ms2` hiçbir şey tarafından okunmuyor.** Bilerek: ait olduğu üç
  yer de Dünya'ya uydurulmuş sabitler taşıyor. `test_gravity_is_inert` yarım
  bağlamayı engelliyor.
- **Su bütçesi Dünya'nınkinin iki katı** ve düzeltmek Köppen skorunu
  düşürüyor — çünkü fazla su başka bir hatayı (yerleşim hatasını) maskeliyor.
  Sıra önemli: yerleşim düzelmeden bütçe düzeltilemez.

---

## 9. Arazi değişince ne yapılır

Dünyanın sahibi araziyi MerakMapMaker'da düzenleyip yeni bir `.glb` verdiğinde
asıl projede şu zincir koşar:

1. `python _mk_heightmap.py` — `.glb`'den gezegen tuvalini üretir. Mesh
   düzgün bir köşe ızgarası; x/y uzanımlarının oranı çizimin **gerçek en/boy
   oranıdır** (köşe ızgarası kare olsa bile). Kıta, `KARA_MERKEZ_LON` ile
   boylamda sabitlenir — yoksa her yeni arazi sürümünde birkaç derece kayar ve
   akıntılar, işaretli bölge, notlardaki bütün boylamlar sessizce yanlış olur.
2. `sea_level_value` ve `max_depth_m` yeniden okunur (betik basar).
3. 0.25 derecelik koşu, `_denetim.py`, atlas, `_repo_senkron.py --yaz`.
4. Bu repoda commit + push; workflow veriyi yeniden üretir.

Kullanıcının kendi PNG çıktısı **kaynak değildir**: okyanus tabanı orada düz
tek bir değer (batimetri yok), tuvali 2:1 değil ve çizim keyfi bir kareye
oturtulmuş oluyor. `.glb`'de z gerçek yüksekliktir.
