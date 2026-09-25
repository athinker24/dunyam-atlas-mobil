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
   ekran). Artık ekranın ortası kara kutusundan en fazla görünen alanın
   %35'i kadar dışarı çıkabiliyor. Doğrulama: kıyıdaki en güney hücreye iki
   yakınlıkta dokununca hücre kartın üstünde kalıyor; test 12/12.
2. **İlk açılışta sayfa iki kez yükleniyordu.** Service worker ilk kez
   kontrolü alınca `controllerchange` ateşleniyor; olay anında `controller`
   dolu olduğu için kod bunu güncelleme sanıp sayfayı yeniliyordu. Artık
   yalnız açılışta zaten bir service worker varsa yeniliyor. Doğrulama:
   Playwright'ta açılıştan sonraki `evaluate` "context destroyed" hatası
   vermiyor.
