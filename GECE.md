# Gece bakımı günlüğü (gece dalı)

Dünyanın sahibi uyurken yapılan denetim (25-26 Eylül). Kurallar: düzeltmeler
bu dalda, `main`'e girmez (her push telefona yayın); iklim sonucunu
değiştiren şeyler yalnız ölçülür ve buraya yazılır, uygulanmaz. Her kalem:
bulgu, nasıl bulundu, ne yapıldı, nasıl doğrulandı. Uygulama testi her
adımda koştu (şimdi 15 denetim, hepsi geçiyor; GitHub'da da yeşil).

## Özet

- **Telefonda bakman gerekenler:** Dolaşım sekmesinde kaydırma akıcılığı
  (madde 16), çok yakınken kaydırma sınırı (1), dar ekranda lejant (7),
  ayar çekmecesi açıkken kart (8), Kar sekmesi ve kart (11, 18), deniz
  kartı (15).
- **Karar bekleyenler:** "Yalnız raporlanan" bölümü.
- `main`'e almak için `gece` dalını birleştirmek yeter (ileri sarma).

## Düzeltilenler

1. **Yakınken harita boşluğa kayabiliyordu.** `sinirla` pan sınırını bütün
   veri kutusuna göre koyuyordu; veride karanın çevresinde 22° okyanus payı
   olduğu için çok yakınken ekran tamamen boş okyanusa ya da verinin dışına
   kayabiliyordu (keşif betiği: tuvalde 2 renk, ekran görüntüsünde boş
   ekran). Artık dikeyde ekranın ortası kara kutusundan, yatayda o satırdaki
   karanın batı/doğu ucundan en fazla görünen alanın %35'i kadar dışarı
   çıkabiliyor. İlk sürüm yalnız dikdörtgen kutuya bağlıydı; yeni test
   kutunun köşesinin açık deniz olduğunu yakaladı, satır satır sınıra
   geçildi. Doğrulama: çok yakınken altı yöne aşırı sürüklemede ekranda
   hep kara var (%20 ile %100); kıyıdaki en güney hücreye iki yakınlıkta
   dokununca hücre kartın üstünde kalıyor.
2. **İlk açılışta sayfa iki kez yükleniyordu.** Service worker ilk kez
   kontrolü alınca `controllerchange` ateşleniyor; olay anında `controller`
   dolu olduğu için kod bunu güncelleme sanıp sayfayı yeniliyordu. Artık
   yalnız açılışta zaten bir service worker varsa yeniliyor. Doğrulama:
   Playwright'ta açılıştan sonraki `evaluate` "context destroyed" hatası
   vermiyor.
3. **Açılışta veri hazırlığı yavaştı.** CPU 4 kat yavaşlatılmış (orta sınıf
   telefon yaklaşığı) ölçümde `veriHazirla` 989 ms sürüyordu. İki sebep:
   - Kar alanı açılışta hesaplanıyordu (~360 ms), ilk ekran kar göstermediği
     halde. Artık ilk kareden sonra boşta hesaplanıyor; Kar sekmesi ya da
     kart daha önce isterse o an (`karAl`).
   - Yüzdelik renk ölçeği için ~650 bin değer sıralanıyordu. Değerler bayt
     kodlarından geldiği için (kodlama başına en fazla 256 değer) havuz
     artık kodlardan sayılarak kuruluyor.

   Sonuç: `veriHazirla` 989 → 239 ms.
   Yan düzeltme: eski havuz Float32'ye yuvarlanmış değer tutup tam hassas
   değerle sorgulandığı için eşit değerler "ortadan" değil bir yandan
   sayılabiliyordu. Renk tablosu farkı en fazla 6/255 (görünmez); lejant
   etiketleri birebir aynı; yalnız bantlı yıllık yağışta bant sınırındaki
   3 kod komşu banda geçti. Test 12/12.
4. **Test bu gecenin düzeltmelerini kapsamıyordu.** Üç denetim eklendi:
   ilk açılışta tek yükleme, kar katmanının çizilmesi (tuval tek renk
   değil, lejant doğru), çok yakınken aşırı sürüklemede karanın ekranda
   kalması. Test 15/15.
5. **Karar notlarında okuma tuzağı.** `_su_butcesi` notunun başı "DEGISIKLIKLER:
   evap_max_mm_month=106" diye başlıyordu; sonradan kaldırılan tavan şu anki
   ayar gibi okunuyordu. "İLK DENEME (sonra değişti)" olarak düzeltildi.
   Eski notlardaki "NIHAI" sınıf payları (örn. `_akdeniz` Cs %10.8) kendi
   tarihlerinin ölçümü; bugün Cs %14.9. Tek yerde güncel durum için
   `_guncel_durum` notu eklendi (veri sürümü 65cf9d017d'nin ölçümleri).
6. **Belgelerdeki koşu süreleri eskimişti.** Nem korunumu motoru yavaşlattı:
   0.25° bu makinede ~14 → ~35 dk, GitHub'da ~12 → ~20 dk (ölçüldü).
   CLAUDE.md ve README güncellendi. Test satırı da yeni denetimleri anıyor.
7. **Dar ekranda lejant etiketleri üst üste biniyordu.** 360 px'te yıllık
   yağışta "1.164" ile "5.610 mm/yıl" birleşip "1.1645.610" okunuyordu
   (yüzdelik ölçekte değerler uçta birbirine yakın). Artık komşusuyla
   çakışan ara etiket gizleniyor, uçlar hep görünüyor; ekran dönünce yeniden
   hesaplanıyor. Doğrulama: 320/360/390/1024 px × 5 katman × 2 dönem,
   çakışma ve taşma yok.
8. **Ayar çekmecesi açıkken hücre kartı haritayı örtüyordu.** Çekmece yarıda
   durur ki ayar değişikliği haritada görülsün; kart tam o alanı kapatıyordu.
   Çekmece açıkken kart gizleniyor (kapanmıyor), çekmece kapanınca geri
   geliyor. Doğrulama: 360×640'ta aç/kapa.
9. **Hareketli rüzgâr yüksek yenileme hızlı ekranda hızlı akıyordu.**
   Parçacık hızı ve iz sönümü kare başına tanımlıydı; 90/120 Hz ekranda
   parçacıklar 1.5-2 kat hızlı akıp izleri kısalıyordu. Adım artık geçen
   süreyle ölçekleniyor (60 Hz'de davranış aynı), arka plandan dönüşte
   sıçrama olmasın diye en fazla 3 kare. Test 15/15.
10. **`_senkron_kontrol.py` yanlış yolda anlaşılmaz çıktı veriyordu.** Proje
    yolu yoksa ya da yanlışsa her dosya için ayrı "projede yok" yazıyordu.
    Artık yol kontrol ediliyor (`climate/` var mı) ve tek satırlık açık hata
    ile 2 kodu dönüyor.
11. **Buzul hücrelerinde kar kalınlığı anlamsızdı.** 1076 kara hücresinde
    yıllık kar yağışı yıllık erime kapasitesini aşıyor, kar hiç erimeden
    birikiyor. Kart burada "en kalın ..., X mm su" yazıyordu ama X yalnız kar
    hesabının kaç yıl döndürüldüğüne bağlı. Artık bu hücreler "kalıcı,
    erimiyor (buzul)" gösteriyor. Kontrol: 784'ü EF (buz örtüsü), 289'u ET,
    3'ü BSk; tutarlı. Test 15/15.
12. **GitHub testi yayınlanan dosyaları değil repo kökünü test ediyordu.**
    Cloudflare yalnız `yayinla.sh`'nin `site/`'ye kopyaladıklarını yayınlıyor;
    oraya eklenmesi unutulan bir dosya telefonda eksik kalır ama kökte test
    geçerdi. `uygulama.yml` ve `veri.yml` artık `sh yayinla.sh && node
    test/uygulama_test.js site` koşuyor; `yayinla.sh` değişince de test
    tetikleniyor. `yayinla.sh` yorumu "Pages" yerine Workers'ı anlatıyor.
    Doğrulama: yerelde `site/` üzerinde 15/15.
13. **README eksikleri.** Dosya tablosuna `mevsim_olc.py` eklendi; test
    satırı `site/` kümesini anıyor; dal önizlemesinin adres biçimi,
    `"previews": {}` gereği ve Access uyarısı yazıldı.
14. **Dolaşım sekmesinde deniz sıcaklığı alanı dikdörtgen kenarla
    kesiliyordu** (veri karanın ~22° ötesinde biter). Son %4'te koyu zemine
    yumuşak geçiş eklendi; diğer katmanlarda uzak okyanus zaten zemine
    karışıyordu. Test 15/15.
15. **Metin düzeltmeleri.** Deniz kartı her okyanus hücresine "Açık deniz"
    yazıyordu (kıyı suları ve iç deniz dahil); artık "Deniz" ve en yakın
    kıyıya yaklaşık uzaklık ("kıyıya ~250 km", 30 km altı "kıyıya yakın").
    Yükleme hatası "İlk kurulum için sunucu açık olmalı" diyordu (eski tünel
    dönemi); artık "İlk açılış için internet bağlantısı gerekli".
16. **Dolaşım sekmesinde kaydırma takılıyordu.** 40 adımlık sürükleme
    (CPU 4 kat yavaş) İklim'de 3.8 s, Dolaşım'da 18.9 s sürdü. Profil: JS
    değil, büyük SVG kaplamasının her karede yeniden kurulup boyanması
    (kaplama gizlenince 3.7 s). Artık hareket sürerken son çizim CSS
    dönüşümüyle kaydırılıp ölçekleniyor, parmak kalkınca / tekerlek durunca
    bir kez yeniden kuruluyor (sayıldı: sürüklemede 0 yeniden kurma, 20
    dönüşüm; bırakınca 1 kurma). Dürüst not: bu test ortamı GPU'yu yazılımla
    taklit ediyor ve orada kazanç yalnız %22 (9.2 → 7.1 s); gerçek telefon
    GPU'sunda katman kaydırmak çok daha ucuz olmalı ama buradan ölçemedim.
    Telefonda Dolaşım'da kaydırmanın akıcılığına bakman gerekiyor. Test 15/15.
17. **CLAUDE.md'ye tuzak eklendi (§7.7):** bulut makinesinde çizim
    performansı yanıltır (yazılım GPU); JS maliyeti CPU ×4 ile ve profille
    ölçülür, çizim telefonda doğrulanır.
18. **Kar örtüsü süresi fazla hesaplanıyordu.** Eşikleri Dünya istasyonlarıyla
    kaba sınadım (Moskova ve Ulan Batur aylık normalleri, uygulamanın kendi
    `karHesapla`'sı). Moskova 6 ay örtü veriyordu (gerçekte kabaca Kasım
    sonu–Nisan başı, ~4.5 ay); Nisan ortasında 109 mm su görünüyordu. Sebep
    tanım: "ay ortası" ayın başı ile sonunun ortalamasıydı; kar ayın başında
    eriyip bitse de başlangıç büyükse ay örtülü sayılıyordu. Artık ay içi
    yağış ve erime doğrusal kabul edilip ayın ortasındaki durum hesaplanıyor.
    Moskova 5 ay (Kas–Mar), Ulan Batur 4 ay ince örtü. Dünyam: örtülü kara
    payı aynı (%41.9), ortalama örtü süresi 2.55 → 2.23 ay. Test 15/15.
    CLAUDE.md §1'deki kar tanımı güncellendi.

## Yalnız raporlanan (senin kararın)

- **Motor yavaşlığı.** Profil (0.5°, bir ay): 18.3 s'nin 10 s'si Gauss
  yumuşatması; korunum her adımda bir yumuşatma daha ekliyor. Adım içindeki
  iki yumuşatmadan birini yeniden kullanmak hızı ~%30-40 artırır ama sonucu
  çok az değiştirir (veri sürümü değişir). Bit bit aynı kalan bir hızlandırma
  bulamadım. GitHub'da 20 dk kabul edilebilir göründüğü için dokunmadım.
- **Kartta sınıf ile klimagram %2.1 karada çelişiyor.** Kaydedilen Köppen
  sınıfı, uygulamanın gösterdiği aylık değerlerden yeniden hesaplanınca
  karanın %2.1'inde (alan ağırlıklı, 1059 hücre) farklı çıkıyor; en sık
  Cwa/Cwb, Csa/Csb, Dfa/Dfb (hepsi 22 °C sıcak ay eşiği). Sebep: veri
  dosyasında aylık sıcaklık 0.32 °C adımla saklanıyor. Motorun sınıfı
  doğru; eşiğin hemen yanındaki hücrelerde gösterilen değer yuvarlanmış.
  Düzeltme: sıcaklığı 2 baytla saklamak (atlas.json ~0.8 MB büyür).
  Öncelik DÜŞÜK: fark en fazla 0.16 °C, kart sıcaklığı tam dereceye yuvarlıyor;
  gözle görülebilir bir çelişki değil. Açılışı yavaşlatmaya değmez bence.

## Temiz çıkan denetimler (sorun bulunmadı)

- Rastgele etkileşim taraması: 3 tohum, 1100 eylem (dokunma, çift dokunma,
  sekme/ay, çekmece, anahtarlar, sınıf izolasyonu, döndürme, yakınlaştırma,
  sürükleme): 0 JS hatası.
- WebGL'siz yedek çizim (Canvas2D): 6 sekme hatasız.
- 360×640 ve 1024×768'de taşan öğe yok.
- `index.html` ve `manifest.webmanifest`: eksik yok.
- Python dosyalarında statik tarama (pyflakes): temiz.
- `yayinla.sh` 17 dosya kopyalıyor, eksik yok; `site/` git'te izlenmiyor.
- Tutarlılık kontrolü metinleri güncel veriyle uyumlu (12/12).
- Ham yağış alanında 57-59°K satır sıçraması: kıyı geçişinden, artefakt değil.
