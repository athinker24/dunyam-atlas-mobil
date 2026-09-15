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

Telefonda: `tunel.bat` açıkken uygulamayı aç (ya da Ayarlar → Güncellemeleri
denetle). Servis çalışanı ağ öncelikli olduğu için kod ve veri tazesi otomatik
gelir; yeni veri geldiğinde üstte bildirim çıkar.

Uygulama koduna dokunmadan yalnız veri değişebilir. `sw.js` içindeki `AD`
sürümünü yalnızca önbelleğe alınan dosya listesi (`KABUK`) değiştiğinde artır.

## Dosyalar

| dosya | ne |
|---|---|
| `index.html`, `style.css`, `app.js` | uygulama |
| `data/atlas.json` | `_atlas.py`'nin ürettiği veri — elle düzenleme |
| `sw.js`, `manifest.webmanifest`, `icons/` | kurulum ve çevrimdışı çalışma |
| `baslat.bat` | yalnız bilgisayarda aç (http://localhost:8778) |
| `tunel.bat` | telefona kurmak/güncellemek için geçici HTTPS tünel |

`app.js` içindeki `KPAL` (palet) ve `KREF` (Dünya karşılıkları) blokları
masaüstü şablonla (`atlas/atlas_tmpl.html`) birebir aynı olmalı. `_atlas.py`
ikisini karşılaştırır ve farklıysa durur.
