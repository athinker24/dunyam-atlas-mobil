# Gece bakımı günlüğü (gece dalı)

Dünyanın sahibi uyurken yapılan denetim. Kurallar: düzeltmeler bu dalda,
`main`'e girmez (her push telefona yayın); iklim sonucunu değiştiren şeyler
yalnız ölçülür ve buraya yazılır, uygulanmaz. Her kalem: bulgu, nasıl
bulundu, ne yapıldı, nasıl doğrulandı.

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
