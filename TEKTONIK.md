# Tektonik hikâye — karar günlüğü

**Hızlı ve kendi başına anlaşılır özet: `tektonik/OZET.md`** (makine için `tektonik/ozet.json`). Bu dosya kararların tarihçesi; düzeltmeler dahil, sonuç için özete bak.

Dünyanın sahibiyle adım adım kuruluyor. 23 Kasım'dan beri hikâye sahibinin kendi kaynağından
geliyor (aşağıda "YENİ HİKÂYE"); eskiden arazi elle çizilip hikâye araziden geriye doğru okunuyordu. Motor levha bilmez, iklimi etkilemez. Numaralar
26 Eylül dağ ölçümündeki sıradağlar (tepe yüksekliğine göre sıralı).

## YENİ HİKÂYE (23 Kasım, sahibi: "tektonik hikâye değişti; atlastaki tektonik katmanı bu yeni hikâyeye geçir")

**Bu bölüm geçerli olandır. Aşağıdaki 1-8 numaralı bölümler ve "Levha haritası" eski hikâyedir, GEÇERSİZ;
karar tarihçesi olarak duruyor.** Eski adlar (Duvar, Alt Kıta, İber, Ege, Yarımada, Güneybatı, And tipi batı
çarpışması) artık kullanılmaz.

**Kaynak.** Sahibin Merakproject deposundaki `tarih/olaylar.py` (tek kaynak); atlasa paket olarak geldi:
`tektonik/HIKAYE.md` (hikâyenin tamamı, kendi başına okunur), `tektonik/kaynak/levha_kimlik_8k.png` (her piksel
levha kimliği, 16k ana haritanın yarısı), `kaynak/levhalar_hikaye.json` (hızlar, yönler, Kuzey sabit),
`kaynak/sinirlar_hikaye.json` (amaçlanan sınır türleri). Yeni ana arazi `worldinfo/dunyam_ana_16k.png`.

**Özet.** Kıta yedi parçadır; bugün iki çarpışma etkin: 3, 2'nin altına (Mor Sıradağları, 50 MYÖ'den beri);
5, 4'ün altına (Sarı Sıradağları, 8 MYÖ'den beri). Doğu Okyanusu Doğu Hendeği'nde 3'ün altına dalar; iç
denizdeki ada (6) yay ardı gerilmesiyle güneye çekilir (Ada Hendeği); Güneydoğu Kanalı açılan yarık; 7 Kanal
Fayı boyunca kuzeybatıya kayar. 3 MYÖ'de Köprü Kıstağı 1 ile 4 arasındaki boğazı kapattı.

**Arazi (Köprü Kıstağı).** `_mk_heightmap.py`, `_egri_kur.py` ve `_akinti_kur.py` bu repoda yok (DURUM.md
"Çalışma biçimi"), o yüzden aynı ilkeyle elle girildi: 16k harita tuvale kara maskesi IoU'su en büyük
ölçek+kayma ile kaydedildi (`tektonik/kaynak/kayit.json`, IoU 0.951; 16k'da kara > 13996, 13996 sığ deniz).
Yalnız kıstak değişti: 25.2°K 27.7°B, 164 tuval pikseli, 80-400 m, mevcut `elev_curve`'ün tersiyle griye.
Eğri değişmedi, `_egri_kur.py --yaz` koşulmadı (CLAUDE.md §9). Tuvalde körfez ile iç deniz zaten bağlı
değildi (aradaki en dar kara ~35 km) ve hiçbir akıntı yolu boğazdan geçmiyor: akıntılar değişmedi.
Ayrıntı `dunya/dunyam.json` → `_heightmap_kaynak`.

**Levha modeli (`tektonik/levhalar.py`, yeniden yazıldı).**
- Kıta levhaları 1-7 sahibin görüntüsünden, `kayit.json` ile enlem ve boylama (piksel ×2 ile 16k).
- 16k çerçeve küreden büyük (kayıtla 108°K..110°G, 227°B..225°D'ye düşer); 8, 9, 10 o çerçevede düz
  çizgilerle bölünmüş yer tutucu. Bu yüzden uzak okyanus levhaları atlasın eski gezegen ölçekli modelinden
  korundu (`kaynak/uzak_okyanus.png`): Batı Okyanusu Levhası = eski Uzak Okyanus, Kutup Levhası = eski Kuzey
  Kutup, Güney Okyanusu Levhası = eski Güney Kutup, Büyük Okyanus Levhası (11) yalnız atlasta. Sırtlar ve
  çukur eskisiyle aynı yerde.
- Kıta ile uzak sırtlar arasındaki okyanus en yakın kıta levhasına verildi (edilgen kenar: kıta ile
  önündeki okyanus aynı levha). Sonuç: çerçevenin dışında Orta Blok ve Uzun Yarımada güneye uzanan şeritler,
  Kuzey Levhası batı ve kuzey okyanusunu kaplar (123.6 milyon km²).
- Hızlar sahibin tablosundan; Euler vektörü tohum noktasındaki hızdan. Doğu Dil Levhası dönerek ilerler:
  Euler vektörüne saat yönünün tersine 0,3°/My eklendi. Doğu Okyanusu'nun tohumu kayıtla Büyük Okyanus'a
  düşüyordu; levhanın ortasına (7.8°K 65.3°D) alındı.
- Sınırlar kimlik rasterından çıkarılır (komşu levhalar arası kenar, zincir, ~55 km'lik adımlar); sınıf
  Bird (2003) ölçütüyle hesaptan. Uzunluklar sahibin tablosundakinden ~%15-25 uzun: raster kenarı basamaklı.
- Volkan yayları (`uygulama.py`) hikâye tablosunu esas alır: amaçlanan türü dalma olmayan çiftte yay
  çizilmez (Bird orada dalma bulsa bile). Eski "sönmüş batı kuşağı" kuralı kalktı.

**Bird sınıfı ile amaçlanan tür (madde 4).** Yalnız sahibin görüntüsünde çizili kesimler sayıldı; uyum =
amaçlanan türe uyan sınıfların uzunluk payı. Hikâyenin kuralı: ayrılırsa tablo esas.

| levhalar | amaçlanan | Bird baskın | uyum | görüntüde km | sınıf payları |
|---|---|---|---|---|---|
| Kuzey Levhası / Doğu Okyanusu Levhası | yanal | dalma | %4 | 5734 | SUB %78, CCB %12, CRB %6, CTF %4 |
| Doğu Dil Levhası / Doğu Okyanusu Levhası | dalma | dalma | %100 | 4484 | SUB %100 |
| Kuzey Levhası / Ada Bloğu | ayrılma | okyanus sırtı | %49 | 3565 | OSR %45, SUB %29, OTF %19, CRB %5, CCB %3 |
| Doğu Dil Levhası / Uzun Yarımada Bloğu | ayrılma | okyanus sırtı | %71 | 3620 | OSR %68, OTF %24, SUB %3, CRB %3, CTF %2 |
| Doğu Okyanusu Levhası / Kutup Levhası | yanal | okyanusal yakınlaşma | %0 | 109 | OCB %100 |
| Kuzey Levhası / Doğu Dil Levhası | kıta çarpışması | kıta çarpışması | %81 | 3445 | CCB %79, OTF %18, SUB %2, CTF %2 |
| Kuzey Levhası / Orta Blok | kıta çarpışması | kıta çarpışması | %100 | 3738 | CCB %51, SUB %49 |
| Kuzey Levhası / Doğu Havza Levhası | yanal | dalma | %21 | 2570 | SUB %49, CRB %22, CTF %15, OTF %7, CCB %6, OSR %2 |
| Doğu Dil Levhası / Doğu Havza Levhası | yanal | dalma | %25 | 3009 | SUB %49, CTF %22, OSR %11, CCB %11, CRB %4, OTF %4 |
| Orta Blok / Uzun Yarımada Bloğu | yanal | okyanus dönüşüm fayı | %63 | 3419 | OTF %52, SUB %13, CTF %11, OSR %10, CRB %10, CCB %5 |
| Ada Bloğu / Doğu Havza Levhası | dalma | dalma | %74 | 1900 | SUB %74, OTF %26 |
| Orta Blok / Doğu Havza Levhası | yanal | kıta yarığı | %18 | 1284 | CRB %74, OTF %13, CCB %8, CTF %4 |
| Doğu Dil Levhası / Orta Blok | ayrılma | okyanus sırtı | %100 | 55 | OSR %100 |

Ayrılanlar (uyum %50'nin altı):
- **Kuzey / Doğu Okyanusu (2'nin doğu açığı):** amaçlanan yanal, Bird %79 dalma. Doğu Okyanusu batıya
  6,5 cm/yıl gidiyor, sınır ise kuzey-güney uzanıyor: hareket sınıra dik, yakınlaşma ~3,9 cm/yıl. Yanal olması
  için ya Doğu Okyanusu'nun bu kesimde kuzey ya da güneye gitmesi ya da sınırın doğu-batı uzanması gerekir.
- **Doğu Havza'nın üç sınırı** (Kuzey, Doğu Dil, Orta Blok ile): amaçlanan yanal, Bird karışık (dalma,
  yarık, yanal). Doğu Havza yavaş (0,8 cm/yıl kuzeybatı) ve sınırları kıvrımlı: yönün küçük değişimi sınıfı
  değiştiriyor. Orta Blok / Doğu Havza'da Bird %74 kıta yarığı (Orta Blok batıya, Doğu Havza kuzeybatıya,
  aradaki sınır onları ayırıyor).
- **Kuzey / Ada Bloğu:** amaçlanan ayrılma, Bird %45 sırt + %5 yarık, %29 dalma. Ada güneye 0,7 cm/yıl
  gidiyor; adanın kuzeyi ayrılıyor ama güneybatı kesimde Kuzey Levhası adanın güneyinde kaldığı için
  aynı hareket yakınlaşma oluyor.
- Uyanlar: Mor Sıradağları (%81), Sarı Sıradağları (%100, kıyı kesimi dalma), Doğu Hendeği (%100), Ada Hendeği
  (%74), Güneydoğu Kanalı (%71), Kanal fayı (%63).
- Yer tutucu sınırlar (8, 9, 10 ile) görüntüde çizgi olarak var ama çerçeve kenarında; kürede yerleri eski
  modelden, karşılaştırılmadı.

## 1. Büyük Çarpışma (KARARLAŞTI, 26 Eylül) — GEÇERSİZ (23 Kasım, yeni hikâye)

**Karar (sahip):** Duvar (3) ve çevresindeki dağlar, platolar, havzalar
(1, 2, 9 dahil) tek bir çarpışmanın ürünü: güneydoğudaki blok (sahibin
çizdiği alan; boylam ~0..33, enlem ~−2..33) kuzeydeki ana karaya çarptı.
Himalaya-Tibet benzeri, ama kuşak daha uzun.

**Ölçüler (0.1 derece):**
- Blok ~8,9 milyon km² (Hindistan'ın ~2 katı); ana kara ~37 milyon km².
- Blok Duvar'a boylam 7,6..33,1 arasında değiyor (~2.200 km).
- Duvar'ın 3000 m üstü kuşağı boylam −36,8..39,7 (~6.500 km).

**Seçilen yol A: tek sınır, iki davranış.**
- Doğuda (7,6..33) kıta çarpışması: dikiş hattı Duvar'ın güney eteğinde.
- Batıda (−37..7,6) okyanus tabanı hâlâ Duvar'ın altına dalıyor; Duvar'ın
  batı bölümü dalmayla yükselmiş (And tipi). İç deniz o okyanusun kalıntısı
  ve daralıyor; batı Duvar'ın güney yamacında volkan ve deprem beklenir.
  Asya benzeri: Hindistan ortada çarptı, Sumatra/Cava'da dalma sürüyor.
- Uzak etki (Tanrı Dağları/Altay benzeri): 9 (~900 km kuzey), 2 (~1.800 km).
- 1: bloğun kuzeybatı köşesinin kıvrım düğümü (Pamir benzeri); kuzey-güney
  uzanımı ve dünyanın en yüksek noktası (7.000 m) bununla açıklanır.
- Plato çanağı: kıvrılmamış sert eski blok (Tarım benzeri), çevresinde
  dağlar yükseldi; ortasının düz kalması bozkır isteğiyle uyumlu.
- Duvar'ın dibindeki alçak ova (bloğun kuzeyi): önülke havzası (Ganj ovası
  benzeri); Duvar'dan inen nehirler buraya döküldü.
- İç denizdeki takımadalar: dalma zonuna taşınan küçük kıta parçaları,
  "sıradaki çarpışma" (henüz karar değil, yalnız okuma).
- Elenen yol B (blok batıdan doğuya sürtünerek geldi, iç deniz arkasında
  açıldı): bloğun batı kıyısı iç denizin karşı kıyısına oturmuyor.

**Bu olayın DIŞINDA:** 5 (kuzeybatı yayı), güneybatı bloğu (4, 6, 10),
bloğun kendi dağları (7, 8, 11) ayrı ele alınacak.

**Küçük uyumsuzluk:** Duvar'ın iki yamacı eşit dik (asimetri 1,0);
Himalaya'da çarpan kıtaya bakan güney yamaç diktir. Arazinin elle
çizilmesinden; istenirse güney yamaç dikleştirilir.

## 2. Alt kıta: Anadolu benzeri kolaj (KARARLAŞTI, 26 Eylül) — GEÇERSİZ (23 Kasım, yeni hikâye)

**Sahibin tasarımı:** blok Anadolu örnek alınarak çizildi; doğu ve batı
kıyısına paralel sıralar, arada platolar, havzalar, vadiler.
**Adlandırma (sahip):** 7 = doğu kıyısı sırası (ölçümdeki 7 ve 8 aynı
sıra), 8 = batı kıyısı sıraları, 11 = ortadaki eski kuşak.

**Ölçüler (1400 m eşik):**
- 7: ~2.370 km, 5.892 m, pürüz 502 (genç, etkin).
- 8: 160-430 km'lik kısa dik parçalar, pürüz 700-1000, en yüksek 5.594 m;
  aralarında denize açılan vadiler.
- 11 ve çevresi: 1.555 km, yalnız 3.488 m, pürüz 227 (eski, aşınmış).
- Bloğun %56'sı 900 m altında (ova ve havza).

**Hikâye (dört aşama):**
1. Eski kaynaşma: blok iki küçük kıtaydı; aradaki okyanus kapandı, 11 o
   dikişte yükseldi (Kırşehir kütlesi / İzmir-Ankara kenedi benzeri).
2. Doğu kenarı: blok kuzeye yürürken doğu kenarının altına okyanus daldı,
   7 yükseldi. 7'nin doğusundaki kapalı körfez **Karadeniz benzeri** yay
   ardı havzası: dalmanın arkasında kabuk gerilip açıldı (sahip seçti).
3. Batı kenarı gerilmesi (sahip onayladı): iç denizin Duvar altına dalan
   levhası geri çekildikçe bloğun batı kıyısı gerildi; 8 kısa dağlara ve
   denize açılan çöküntü vadilerine bölündü (Ege / Batı Anadolu benzeri).
   Sonuç: verimli vadiler, sıcak su kaynakları, depremler. İç denizdeki
   takımadalar Ege adaları karşılığı.
4. Büyük Çarpışma: blok Duvar'a dayandı; kuzeyi önülke havzası, iç kısım
   sıkışıp kabardı; kapalı havzalar tuzlu göl adayı (Tuz Gölü benzeri).

**Büyük yanal fay (sahip ekledi):** Kuzey Anadolu Fayı benzeri. Bloğun
yaylalarının kuzey kenarı boyunca, önülke ovasıyla yayla arasında,
doğudaki körfezden batı kıyısına kabaca doğu-batı uzanır. Sağ yönlü:
fayın güneyi batıya, serbest kenara (geri çekilen iç deniz levhasına)
kaçar; kuzeyi Duvar'a bağlı kalır. Büyük deprem hattı.

## 3. Yarımada ve 4: İtalya-Alpler benzeri (KARARLAŞTI, 26 Eylül) — GEÇERSİZ (23 Kasım, yeni hikâye)

Sahibin tasarımı: güneybatı bloğunun doğusundaki yarımada İtalya'dan
esinli, omurgasında Apenin benzeri sıra; batıdaki kıtaya (güneybatı
bloğu) çarparak 4'ü (Alpler benzeri yay, arası vadili) yükseltti; ikisinin
arasında Po ovası benzeri ova.

**Ölçüler:** yarımada 1,58 milyon km² (İtalya'nın ~5 katı), omurga ~1.560 km,
en yüksek 5.143 m, karanın %3'ü 1.500 m üstü (ince omurga). Ova 0,53 milyon
km², ort. 640 m, 4'ün iç bükeyinde. 4: 1,07 milyon km², 6.706 m; ovaya bakan
iç yamaç dış yamaçtan biraz dik (0,91° / 0,83°), gerçek Alpler gibi.

**Seçilen yol (a):** yarımada alt kıtanın batıya uzanan çıkıntısıydı
(Adriyatik levhasının Afrika çıkıntısı olması gibi). Alt kıta kuzeye
yürürken saat yönünün tersine biraz döndü, çıkıntı batıya savrulup
güneybatı bloğuna çarptı ve 4'ü yükseltti. Yarımadanın doğu ucu alt
kıtanın güneybatı köşesine dar bir boğazla hâlâ değiyor.

**Dünyam'ın Akdeniz'i:** iç denizin güneyi genel yakınlaşma içinde geri
çekilen levhaların açtığı gerilme havzalarıdır: alt kıtanın batı kıyısı
(Ege), yarımadanın kuzeyindeki iç bükey körfez (Tiren benzeri).

**Sonraya:** Alp tipi büyük buzul gölleri için buzul çağı geçmişi gerekir
(4 ~11°K'de); tektonikten sonra ayrı karar.

## 4. 10 ve 6: batıdan gelen devasa çarpışma (KARARLAŞTI, 26 Eylül) — GEÇERSİZ (23 Kasım, yeni hikâye)

Sahibin tasarımı: çizdiği güneybatı kıyı kuşağının tamamı tek bir devasa
çarpışma; içindeki düzlük onun platosu; çarpan batıdaki okyanus levhası,
güneybatıdaki düz yarımada o levhanın su üstündeki kısmı. Örnek And Dağları.

**Ölçüler:** kuşak 5,19 milyon km², en yüksek 5.924 m (6). Plato 10: 0,59
milyon km², ort. 2.278 m, eğim 0,12° (Altiplano benzeri, daha alçak ve
büyük). Güneybatı düz yarımada: 1,13 milyon km², ort. 156 m, en yüksek
712 m. 6: küçük ama en dik ve keskin yer (eğim 1,24°), genç ve etkin.

**Düzeltme (kabul edildi):** okyanus kabuğu 1,1 milyon km²'lik düz kara
olarak su üstüne çıkmaz; yarımada okyanus levhasının taşıdığı hafif bir
küçük kıta (Zelandia benzeri).

**Hikâye:**
1. And dönemi: batı okyanus levhası güneybatı bloğunun altına daldı,
   kıyıda volkanlı dağ kuşağı yükseldi.
2. Küçük kıta dalma hattına geldi, batamadı; ön kısmı bloğun altına
   sokulup kabuğu iki kat kalınlaştırdı, plato 10 kabardı (Tibet
   mekanizması). And gibi başlayıp Himalaya gibi biten çarpışma.
3. Bugün: batmayan artık güneybatı düz yarımada; çarpışma en son 6'da
   sürüyor; kuşağın geri kalanında volkanlar sönmüş.

Güneybatı bloğu doğudan (4) ve batıdan (bu çarpışma) sıkışan bir kıta.
Tuz düzlüğü / Titikaka benzeri göl istenirse plato ortasına sığ çanak
açmak gerekir (plato yüzeyi şu an dışarı akıyor); arazi kararı, sonraya.

## 5. 5 ve daire içi: İber Yarımadası benzeri (KARARLAŞTI, 26 Eylül) — GEÇERSİZ (23 Kasım, yeni hikâye)

Sahibin tasarımı: 5 klasik alt kıta / üst kıta çarpışması; güneyindeki
yükseltiler eski çarpışmaların kalıntısı; bölge İber Yarımadası'ndan esinli.

**Ölçüler:** daire içi 3,24 milyon km² (İber ~0,58), ort. 535 m, %16'sı
700 m üstü, eğim 0,10°, pürüz 43: geniş, düz, eski yayla (Meseta
benzeri). 900 m'yi geçen tek grup 5'in eteği; eski dağlar aşınıp alçak
kabartılara dönmüş (Varisken kalıntısı benzeri). 5: 6.563 m, pürüz 626,
eğim 1,26°, yamaçlar eşit; genç (Pireneler benzeri, ~2.390 km).

**Hikâye:** daire içi çok eski dağlarıyla ayrı bir kıta parçasıydı; dağları
aşındı. Blok kuzeye yürüyüp ana karaya çarptı, 5 dikişte yükseldi.
Biskay Körfezi benzeri dönme EKLENMEDİ: iç denizin batı ucu okyanus
kalıntısı olarak kalıyor (bölüm 1, yol A).

**Omurga:** 5, Duvar, 4 ve 6 genç; güneydeki bütün parçalar (İber benzeri
blok, alt kıta, İtalya benzeri yarımada, batıdaki küçük kıta) aynı kuzeye
yakınlaşmanın içinde. Tetis kapanışının Dünyam karşılığı.

## 6. İç denizdeki takımadalar: Yunanistan-Ege benzeri (KARARLAŞTI, 26 Eylül) — GEÇERSİZ (23 Kasım, yeni hikâye)

Sahibin tasarımı: Yunanistan'dan esinli, dağlık, iç denizin batıya yakın
ortasında.

**Ölçüler:** 1,17 milyon km², 8 ada, en büyüğü karanın %87'si (ana ada ve
küçükler). Boylam −20..−4, enlem 19..30. Kuzey kenarı kuzeye yay çiziyor,
güneye parmaklar uzanıyor (Mora, Halkidiki benzeri). Ort. 501 m, %12'si
1.000 m üstü; en yüksek 6.443 m (büyük volkan). Doğu ucu ile alt kıtanın
batı kıyısı arası ~260 km deniz.

**Hikâye:** iç deniz levhası geri çekildikçe dalma hattı güneye kaydı;
kenardan koparılan kabuk şeridi güneye çekilip gerildi, adalara bölündü.
Dalma hattı takımadanın güney açığında; adaların güneyinde volkan yayı
(Santorini benzeri), en büyüğü 6.443 m. Takımada ile alt kıtanın batı
kıyısı arasındaki deniz Ege'nin karşılığı; bölüm 2'deki batı kıyısı
gerilmesiyle birlikte iki yanlı Ege.

**Bölüm 1, yol A'ya düzeltme:** batıda okyanus Duvar'ın altına değil,
takımadanın altına dalar; takımada ile Duvar arasındaki deniz, geri
çekilmenin arkasında açılan gerilme havzasıdır.

## 7. Kuzeydoğu kaçış bloğu (sahip ekledi, 26 Eylül) — GEÇERSİZ (23 Kasım, yeni hikâye)

**Sahip:** 9, 3 ve 2 arasına bir levha daha; ayrıntıyı Claude belirler.
**Ölçüler:** ~5,1 milyon km², ort. 1.567 m, %43'ü 1.500 m üstü, %42'si
700-1.500 m arası yayla; en yüksek 6.760 m (2).
**Hikâye (Claude; sahip ayrıntıyı bıraktı, kesin):** büyük çarpışmanın basıncı
kuzeydoğu bloğunu doğuya, açık okyanusa doğru sıkıştırıp itti (Hindistan
çarpışmasının Güney Çin ve Çinhindi'ni doğuya itmesi gibi, kaçış
tektoniği). Batı sınırı 9: plato bloğunun ittiği bindirme kuşağı. Kuzey
sınırı 2 boyunca sol yanal, güney sınırı Duvar'ın kuzey eteği boyunca
sağ yanal faylar. Dağlık ve yüksek olması sınırlarının hepsinin etkin
olmasından.

## 8. Bölüm 2'ye geometri düzeltmesi (Claude, 26 Eylül) — GEÇERSİZ (23 Kasım, yeni hikâye)

Bölüm 2'de "7'nin doğusundaki körfez dalmanın arkasında açıldı" yazıyordu;
bu sıra ters: yay ardı havzası çukurun öbür tarafında açılır. Doğru sıra
(doğudan batıya): doğu dalma çukuru (doğudaki yarımadanın açığında) →
doğudaki yarımada (etkin volkan yayı) → Karadeniz benzeri körfez (yay ardı
havzası) → 7 (aynı dalmanın körfez açılmadan önce yükselttiği eski kenar).
Körfez açılırken yarımadayı 7'den kopardı (Japon Denizi'nin Japonya'yı
Asya'dan koparması gibi; Batı Karadeniz de benzer biçimde açıldı).

## Levha haritası (ilk sürüm, yerini aşağıdaki modele bıraktı) — GEÇERSİZ (23 Kasım, yeni hikâye)

`tektonik/levha_haritasi.png`, üreten betik `tektonik/harita.py` (çizgiler
araziden ölçülür, adlar elle). Levhalar: Kuzey, Kuzeydoğu kaçış bloğu,
İber bloğu, Güneybatı bloğu, Yarımada, Alt kıta, Ege, Küçük kıta (batı
okyanusu levhasının üstünde), Batı okyanusu, Doğu okyanusu, İç deniz.
Okyanus ortası sırtları çizilmedi: okyanus tabanı verisi yok, karar sahibin.

## Levha modeli (26 Eylül, sahip istedi: bütün gezegeni saran, sınırları tam) — GEOMETRİSİ GEÇERSİZ (23 Kasım); Bird yöntemi ve uzak okyanus sınırları geçerli

**Yöntem** (gerçek dünyadaki sayısallaştırmanın iki standardı birleştirildi):
- *GPlates kapalı levha çokgenleri* (Gurnis vd. 2012): levhalar sınır
  parçalarının kesişmesinden çıkan kapalı alanlar; gezegenin her noktası
  tam bir levhaya ait. Burada sınır çizgileri 0,1 derecelik küresel gride
  yakılıp kalan bölgeler etiketleniyor (boylamda sarmal).
- *Bird 2003, PB2002*: sınırlar kısa adımlara bölünür (PB2002'de ort. 44,7 km, burada ~27 km), her adım
  levhaların Euler vektörlerinden hesaplanan göreli hızla yedi sınıftan
  birine atanır: göreli hız sınıra 20°'den yakınsa yanal (OTF/CTF), değilse
  yaklaşma (SUB/OCB/CCB) ya da ayrılma (OSR/CRB); iki yanı denizse okyanusal.
  Dalma ve çarpışmada üst levha: kıta tarafı, değilse levha sırası.
- Levha hızları hikâyeden seçildi (Kuzey levhası sabit çerçeve); sınıflar
  hesaptan çıkar, elle yazılmaz. Böylece harita kendi içinde tutarsız olamaz.
- Karadaki sınırlar araziden ölçülür (dağ etekleri, kıyılar). Okyanustakiler
  TASARIM: sırtlar göreli harekete dik parçalar ve ona paralel dönüşüm
  faylarıyla (düzensiz aralıklı) üretilir, dalma çukurları dalan levhaya
  doğru bombeli yaylar. Okyanus tabanı derinliği de tasarım: sırttan uzaklık /
  yarı yayılma hızı = yaş, derinlik = 2,6 + 0,35 √yaş km.

**Levhalar** (13 levha, 6119 adım, toplam 164 bin km sınır):

| levha | alan (milyon km²) | kara payı | Euler hızı (°/My) |
|---|---|---|---|
| Kuzey | 55.8 | %28 | 0.00 |
| Kuzeydoğu | 3.4 | %77 | 0.13 |
| İber | 6.7 | %75 | 0.04 |
| Ege | 4.5 | %32 | 0.19 |
| Güneybatı | 23.4 | %38 | 0.09 |
| Yarımada | 4.6 | %49 | 0.20 |
| Alt Kıta | 20.6 | %41 | 0.36 |
| Batı Okyanusu | 77.1 | %2 | 0.41 |
| Doğu Okyanusu | 97.5 | %0 | 0.47 |
| Büyük Okyanus | 110.1 | %0 | 0.16 |
| Uzak Okyanus | 131.3 | %0 | 0.28 |
| Kuzey Kutup | 15.0 | %0 | 0.09 |
| Güney Kutup | 110.4 | %0 | 0.09 |

**Sınıf uzunlukları (bin km):** OSR 54, SUB 49, OTF 38, CCB 11, CRB 6, CTF 5, OCB 1.

**Şekil (sahip: "çok karemsi", 26 Eylül):** okyanus düzeni gerçek Dünya'ya
benzetildi: sırtlar gezegeni çapraz ve kıvrılarak dolaşıyor, üç üçlü kavşakta
(sırt-sırt-sırt ve sırt-sırt-çukur) buluşuyor; Güney Kutup levhası üç sırtın
kuşattığı düzensiz bir alan. Tasarlanan bütün çizgiler orta nokta kaydırmayla
(fraktal) çok ölçekli kırıklık aldı; sırtlar yalnız yayılma sınıra dikse
basamaklı, yanalsa kırıklı eğri. 9 artık araziden: sıranın doğu eteği (yarık
vadisi). Gezegen haritası Equal Earth izdüşümünde (Šavrič vd. 2018); enlem-
boylam ızgarası kutupları yatay şeride çevirip levhaları dikdörtgen
gösteriyordu.

**Hikâyeye etkisi (hesaptan çıkan, Claude):**
- 9 hesapta *kıta yarığı* çıktı: kaçış bloğu doğuya giderken arkası açılıyor.
  Bölüm 7'deki "9 bindirme" yerine: 9 önce sıkışmayla yükselmiş eski bir
  kuşak, bugün eteğinde Baykal tipi bir yarık açılıyor (Amur levhasının batı
  sınırı Baykal yarığıdır). Derin bir yarık gölü için aday.
- Yarımada ile alt kıta arasındaki boğaz *yarık* çıktı: çıkıntı alt kıtadan
  kopuyor, bölüm 3'teki (a) ile uyumlu.
- Ege ile Kuzey arası *yay ardı yarık*, Ege çukuru *dalma*, alt kıtanın
  batı kıyısı boyunca *yanal fay*: bölüm 1, 2 ve 6 ile uyumlu.
- Okyanus levhaları (Batı, Doğu, Büyük, Uzak, iki kutup) tamamen tasarım;
  okyanus tabanı verisi yok, sahibin kararına açık.

**Dosyalar:** `tektonik/levhalar.py` (model), `tektonik/harita.py` (çizim),
`levhalar.json` (levhalar, Euler kutupları, alanlar), `sinirlar.geojson`
(sınıflanmış adımlar, PB2002 `steps` karşılığı), `levha_kimlik.png` (0,1°
levha kimliği rasterı), `levha_dunya.png`, `levha_kure.png`, `levha_haritasi.png`.


## Uygulamada (27 Eylül, sahibi: "tektonik haritasını uygulamaya yükle, volkan kuşakları ile birlikte") — geçerli; sönmüş batı kuşağı kuralı GEÇERSİZ (23 Kasım)

Arazi sekmesi → **Levhalar**. Veri `tektonik/uygulama.py`'den (`data/tektonik.json`,
`data/levha.png`); levha modeli yeniden koşulmaz, bu klasörün çıktıları okunur.

- Levha renkleri (denizde soluk), adları, Kuzey'e göre hızı ve yön oku.
- Sınırlar `sinirlar.geojson` adımlarından: yakınsak (dalma, okyanusal
  yakınlaşma, kıta çarpışması) kırmızı ve üst levha tarafında dişli; ıraksak
  (sırt, kıta yarığı kesik) yeşil; dönüşüm turuncu. Dişlerin tarafı
  geometriden: çizginin iki yanında levha kimliğine bakılır.
- **Volkan kuşakları (kural, ölçütle):** yay volkanları dalma ve okyanusal
  yakınlaşma adımlarında, üst levhada; cephe hendekten 150 km, kuşak
  150-280 km. Kaynak: volkan cephesi dalan levhanın ~100-130 km derinliğe
  indiği yerin üstünde (Syracuse ve Abers 2006), hendek-yay uzaklığı
  çoğunlukla 100-300 km (Dickinson 1973). Yakınlaşma 1 cm/yıl altındaysa yay
  yok. Baskın sınıfı kıta çarpışması olan sınırda yay yok (Duvar dikişi;
  Himalaya'da etkin yay volkanı yok). Kıta yarıklarında seyrek yarık
  volkanları (sarı). Sönmüş: güneybatı bloğunun batı kıyısında 12°K güneyi
  (bölüm 4, `harita.py`'deki işaretlerle aynı). Okyanus sırtları da
  volkaniktir, su altında; ayrı kuşak çizilmez. Sıcak nokta tanımlı değil.
- Sonuç: 35 yay kuşağı parçası (4'ü sönmüş), 7 yarık. Okyanustaki sınırlar
  ve onların yayları [tasarım]; kart bunu belirtir.
