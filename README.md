# Dünyam Atlası — mobil

Kurgusal dünyanın iklim atlasının telefona kurulan (PWA) sürümü. Koyu tema,
WebGL harita (yumuşak ya da piksel görünüm, kabartma gölgesi: birleşik,
editör görseli ya da yükseklik haritası), 12 aylık klimagramlı hücre kartı,
Dolaşım sekmesinde rüzgâr (akış çizgileri ya da hareketli parçacıklar),
deniz yüzeyi sıcaklığı ve akıntılar, Kar sekmesinde kar örtüsü (aylık
sıcaklık ve yağıştan uygulama içinde türetilir). Eylül 2026'dan beri paleti ve veri
biçimi masaüstü atlastan AYRI (bkz CLAUDE.md 7.4).

## Telefona kurmak (sabit adres, Cloudflare)

Cloudflare bu repoyu okur ve her push'ta uygulamayı yayınlar: derleme komutu
`sh yayinla.sh` yalnız uygulama dosyalarını `site/`'ye kopyalar,
`npx wrangler deploy` onu yayınlar (`wrangler.jsonc`). Motor ve dünya tanımı
yayına girmez. Önünde Cloudflare Access durur; site yalnız sahibin
e-postasına gelen kodla açılır.

1. Yayın adresini telefonda tarayıcıda aç, e-postana gelen kodla gir.
2. Tarayıcı menüsünden **Ana ekrana ekle**.
3. Sonrası kendiliğinden: adres sabit olduğu için uygulama her açılışta
   yeni sürümü alır, internet yoksa önbellekten çalışır.

Yayınlanan dal Cloudflare panelinde Settings → Build → Branch control'dan
seçilir. Diğer dalların ayrı önizleme adresi olur
(`<dal>-dunyam-atlas-mobil.<alt alan>.workers.dev`); bunun için
`wrangler.jsonc`'de `"previews": {}` gerekir, yoksa yayın adımı düşer.
Önizleme adresi Access ile korunmuyorsa herkese açıktır.

## Telefona kurmak (eski yol, geçici tünel)

1. `tunel.bat` çalıştır. Pencerede `https://….trycloudflare.com` adresi çıkar.
2. Adresi telefonda aç. Cloudflare ara sayfası çıkarsa devam et.
3. Tarayıcı menüsünden **Ana ekrana ekle**.
4. Uygulama açıldığında her şey telefona indirilir. Tüneli kapatabilirsin;
   uygulama çevrimdışı çalışmaya devam eder.

Tünel adresi her açılışta değişir ve bilgisayar açık, pencere açıkken geçerlidir.

## Güncellemek

Veriyi bu repodaki `uret.py` üretir (`data/atlas.json` + harita dokuları).
Push'tan sonrası kendiliğinden: GitHub gerekirse veriyi yeniden üretir
(aşağıda), Cloudflare yayınlar, telefondaki uygulama bir sonraki açılışta
yeni sürümü alır. Ayarlar → "Güncellemeleri denetle" bunu hemen yaptırır.

`Proje 3`'teki `_atlas.py` artık bu uygulamanın verisini YAZMAMALI: eski
biçimde (12 aylık veri ve dokular olmadan) yazar ve uygulama açılmaz.

`sw.js` içindeki `AD` sürümünü yalnızca önbelleğe alınan dosya listesi
(`KABUK`) değiştiğinde artır; kod ve veri güncellemesi için gerekmez.

## İklimi değiştirmek — yalnız bu repoyla

Bu repo tek başına yeterlidir. Masaüstüne, GeoTIFF'e ya da `rasterio`'ya
bağımlı değildir; `numpy`, `scipy`, `pillow` yeter.

```bash
pip install -r requirements.txt
python uret.py --res 1.0 --ozet     # kaba deneme, ~1 dk
python uret.py --ozet               # gerçek çözünürlük, ~35 dk (GitHub'da ~20)
```

`uret.py` dünyayı `dunya/` klasöründen okur, iklim motorunu (`motor/`) koşar,
iç tutarlılık raporunu basar ve uygulamanın okuduğu `data/atlas.json`
dosyasını yazar.

**İç tutarlılık kontrollerinden biri düşerse veri yazılmaz.** Bu kontroller
modelin kendi fiziğiyle çelişip çelişmediğine bakar (sıcaklık enlemle düşüyor
mu, yüksek yerler soğuk mu, yarıkürelerin mevsimleri ters mi…) ve düşen bir
kontrol neredeyse her zaman **bozuk girdi** demektir: ters çevrilmiş yükseklik
haritası, yanlış `sea_level_value`, saçma bir parametre. Yine de yazdırmak
için `--zorla`.

### Neyi nereden değiştirirsin

| ne | dosya |
|---|---|
| gün uzunluğu, eksen eğikliği, deniz seviyesi sıcaklığı, yıl | `dunya/dunyam.json` üst seviye alanlar |
| yağış, muson, kuşak salınımı, engellenme gibi hesap ayarları | `dunya/dunyam.json` → `params` |
| deniz seviyesi değeri, en yüksek nokta, yükseklik eğrisi | `dunya/dunyam.json` → `heightmap` |
| okyanus akıntıları | `dunya/dunyam.currents.json` |
| arazi | `dunya/dunyam_heightmap.png` (16 bit gri, 4096×2048) |
| hesaplama yöntemi, katmanlar | `motor/` — `moisture.py`, `temperature.py`, `circulation.py`, `koppen.py` … |

`dunyam.json` içindeki `_` ile başlayan alanlar **karar günlüğüdür**: her ayarın
neden o değerde olduğu, hangi seçeneklerin ölçülüp elendiği orada yazılı.
Bir ayarı değiştirirken oradaki notu da güncelle, yoksa altı ay sonra kimse
nedenini bilemez.

### GitHub üzerinden, bilgisayar açmadan

`dunya/`, `motor/`, `uret.py` ya da `doku.py` değişip push edilince
`.github/workflows/veri.yml` kendiliğinden `uret.py`'yi koşar, uygulamayı
yeni veriyle tarayıcıda test eder (`test/uygulama_test.js`) ve test geçerse
değişen veriyi commit eder. Veri değişmediyse commit atmaz. Actions sekmesinden **atlas verisi →
Run workflow** ile elle de başlatabilirsin (çözünürlüğü orada seçebilirsin).

Yani telefondan GitHub'da `dunyam.json` içindeki bir sayıyı değiştirip
commit'lemek, yeni iklimin hesaplanması için yeterli.

### Motorun kopyası olduğunu unutma

`motor/` ve `dunya/`, ana projedeki (`Proje 3`) dosyaların kopyasıdır. Bu
repoda değiştirirsen ana proje geride kalır. Ana projede `_denetim.py` her
koşuda iki tarafı karşılaştırır ve ayrıştıysa hata verir; `python
_repo_senkron.py --yaz` ana projeden bu repoya kopyalar. Karşılaştırmayı bu
repodan da yapabilirsin:

```bash
python _senkron_kontrol.py /ana/projenin/yolu
```

## Dosyalar

| dosya | ne |
|---|---|
| `index.html`, `style.css`, `app.js` | uygulama |
| `data/atlas.json` + dokular (`doku.png`, `yukseklik.png`, `kabartma*.jpg`, `dolasim.png`) | veri — yalnız `uret.py` yazar, elle düzenleme |
| `sw.js`, `manifest.webmanifest`, `icons/` | kurulum ve çevrimdışı çalışma |
| `uret.py`, `doku.py` | veri üreticisi ve harita dokuları |
| `kabartma_kaydet.py` | editör görselini kabartma kaynağı olarak alır ve araziye oturtur |
| `motor/` | iklim motoru (ana projenin `climate/` kopyası) |
| `dunya/` | dünya tanımı, akıntılar, yükseklik haritası, kabartma kaynağı |
| `test/uygulama_test.js` | uygulamanın tarayıcı testi (GitHub'da yayınlanan `site/` kümesinde koşar) |
| `mevsim_olc.py` | yağışın mevsimselliğini ve korunan istekleri ölçer, harita çizer; veri yazmaz |
| `.github/workflows/veri.yml`, `uygulama.yml` | GitHub'da yeniden üretim ve test |
| `yayinla.sh`, `wrangler.jsonc` | Cloudflare yayını |
| `_senkron_kontrol.py` | kopyalar ana projeyle aynı mı |
| `baslat.bat` | yalnız bilgisayarda aç (http://localhost:8778) |
| `tunel.bat` | yedek: geçici HTTPS tünel |

`app.js` içindeki `KPAL` (palet) masaüstü şablondan bilerek ayrıştı (CLAUDE.md
7.4); `_atlas.py`'nin palet karşılaştırması bu yüzden durur.
