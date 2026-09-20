# Dünyam Atlası — mobil

Kurgusal dünyanın iklim atlasının telefona kurulan (PWA) sürümü. Masaüstü
atlasla aynı veri ve aynı palet; yerleşim ve etkileşim dokunmatik için.

## Telefona kurmak

1. `tunel.bat` çalıştır. Pencerede `https://….trycloudflare.com` adresi çıkar.
2. Adresi telefonda aç. Cloudflare ara sayfası çıkarsa devam et.
3. Tarayıcı menüsünden **Ana ekrana ekle**.
4. Uygulama açıldığında her şey telefona indirilir. Tüneli kapatabilirsin;
   uygulama çevrimdışı çalışmaya devam eder.

Tünel adresi her açılışta değişir ve bilgisayar açık, pencere açıkken geçerlidir.

## Güncellemek

Dünya yeniden koşulduğunda `Proje 3` kökünde:

```
python _atlas.py
```

Bu hem masaüstü atlası hem `mobil/data/atlas.json`'u yazar. Sonra:

```
git add -A && git commit -m "Veri guncellemesi" && git push
```

### DİKKAT: tünel adresi her açılışta değişir

Geçici Cloudflare tünelleri her seferinde yeni bir adres verir. Telefondaki
uygulama **hangi adresten kurulduysa ona bağlıdır** — tarayıcılar her adresi
ayrı bir site sayar. Yani dün kurduğun uygulama bugünkü tünelden habersizdir:
açtığında ölü adrese gider, 4 saniye sonra önbelleğe düşer ve **eski veriyi**
gösterir. Hata değil, tasarım böyle.

Bu yüzden veriyi telefona getirmenin yolu:

1. `tunel.bat` çalıştır, yeni adresi telefonda **tarayıcıda** aç.
2. Ana ekrana ekle.
3. Eski simgeyi sil (yoksa iki uygulama olur, biri eski veriyle).

Kurulu uygulamanın kendini güncelleyebilmesi **sabit bir adres** ister:
ngrok'un ücretsiz sabit alan adı, kendi alan adınla Cloudflare kalıcı tüneli,
ya da uygulamayı claude.ai artıfaktı olarak yayınlamak (o zaman çevrimdışı
çalışmaz). Şimdilik bilerek kurulmadı.

Ayarlar → "Güncellemeleri denetle" yalnızca **aynı adres** ayaktayken işe yarar.

Uygulama koduna dokunmadan yalnız veri değişebilir. `sw.js` içindeki `AD`
sürümünü yalnızca önbelleğe alınan dosya listesi (`KABUK`) değiştiğinde artır.

## İklimi değiştirmek — yalnız bu repoyla

Bu repo tek başına yeterlidir. Masaüstüne, GeoTIFF'e ya da `rasterio`'ya
bağımlı değildir; `numpy`, `scipy`, `pillow` yeter.

```bash
pip install -r requirements.txt
python uret.py --res 1.0 --ozet     # kaba deneme, ~1 dk
python uret.py --ozet               # gerçek çözünürlük, ~20-30 dk
```

`uret.py` dünyayı `dunya/` klasöründen okur, iklim motorunu (`motor/`) koşar,
iç tutarlılık raporunu basar ve uygulamanın okuduğu `data/atlas.json`
dosyasını yazar.

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

`dunya/`, `motor/` ya da `uret.py` değişip push edilince
`.github/workflows/veri.yml` kendiliğinden `uret.py`'yi koşar ve değişen
`data/atlas.json`'u commit eder. Actions sekmesinden **atlas verisi →
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
| `data/atlas.json` | `_atlas.py`'nin ürettiği veri — elle düzenleme |
| `sw.js`, `manifest.webmanifest`, `icons/` | kurulum ve çevrimdışı çalışma |
| `uret.py` | veri üreticisi — iklimi yeniden hesaplar |
| `motor/` | iklim motoru (ana projenin `climate/` kopyası) |
| `dunya/` | dünya tanımı, akıntılar, yükseklik haritası |
| `_senkron_kontrol.py` | kopyalar ana projeyle aynı mı |
| `.github/workflows/veri.yml` | GitHub'da otomatik yeniden üretim |
| `baslat.bat` | yalnız bilgisayarda aç (http://localhost:8778) |
| `tunel.bat` | telefona kurmak/güncellemek için geçici HTTPS tünel |

`app.js` içindeki `KPAL` (palet) ve `KREF` (Dünya karşılıkları) blokları
masaüstü şablonla (`atlas/atlas_tmpl.html`) birebir aynı olmalı. `_atlas.py`
ikisini karşılaştırır ve farklıysa durur.
