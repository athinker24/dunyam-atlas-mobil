# Dünyam levha tektoniği — özet

Bu belge kendi başına okunacak biçimde yazıldı (başka bir kişi ya da yapay zekâ sohbeti için). Aynı bilgi makine için `ozet.json`'da. Hikâyenin tamamı `HIKAYE.md`'de, kararların tarihçesi `../TEKTONIK.md`'de. Belge `tektonik/ozet.py` ile modelden üretilir; elle düzenleme, betiği koş.

## 1. Kısaca

Dünyam kurgusal bir gezegen: yarıçap 6371 km, gün 23.934 saat, eksen eğikliği 23.44°. Tek bir kıtası var (yaklaşık 60°K ile 7°G, 47°B ile 43°D arası); gerisi okyanus. Kıta yedi parçadan oluşur ve bugün iki çarpışma etkindir: 3, 2'nin altına giriyor (Mor Sıradağları); 5, 4'ün altına giriyor (Sarı Sıradağları). 3 milyon yıl önce 1 ile 4 arasındaki boğaz Köprü Kıstağı ile kapandı. Eski hikâyenin adları (Duvar, Alt Kıta, İber, Ege, Yarımada, Güneybatı, And tipi batı çarpışması) geçersizdir.

![tüm gezegen](levha_dunya.png)

## 2. Okuma kuralları

- Koordinat: enlem kuzey +, boylam doğu + (−180..180), derece.
- Hız: cm/yıl, **Kuzey Levhası sabit** kabul edilir; diğer hızlar ona göredir (sahibin `kaynak/levhalar_hikaye.json`'u).
- Kıta levhaları (1-7) sahibin levha kimliği görüntüsünden kayıtla enlem ve boylama çevrildi. Kıta ile uzak sırtlar arasındaki okyanus en yakın kıta levhasına verildi (edilgen kenar). Batı Okyanusu, Kutup ve Güney Okyanusu levhaları hikâyede yer tutucu; yerleri atlasın eski gezegen ölçekli modelinden (sırtlar aynı), Büyük Okyanus Levhası yalnız atlasta var.
- Sınır türü elle yazılmadı: her ~55 km'lik sınır adımında iki levhanın göreli hızından hesaplandı (Bird 2003, PB2002 ölçütü): göreli hız sınıra 20°'den yakınsa **yanal**, değilse **yaklaşma** ya da **ayrılma**; iki yanı denizse okyanusal, değilse kıtasal. Hikâyedeki amaçlanan türle karşılaştırma bölüm 5'te.
- [tasarım] işaretli sınırlar sahibin görüntüsünde yok: görüntü çerçevesinin dışındaki uzantılar ya da uzak okyanus sınırları.

| kısaltma | anlamı |
|---|---|
| OSR | okyanus sırtı |
| OTF | okyanus dönüşüm fayı |
| OCB | okyanusal yakınlaşma |
| SUB | dalma |
| CRB | kıta yarığı |
| CTF | kıta dönüşüm fayı |
| CCB | kıta çarpışması |
| PAS | hareketsiz |

## 3. Levhalar

| no | levha | tür | kapsam | alan (milyon km²) | kara payı | hareket (Kuzey'e göre) | komşular |
|---|---|---|---|---|---|---|---|
| 1 | Kuzey Levhası | kıta + okyanus | 1, 2 (şerit dahil), 4; Köprü Kıstağı; iç denizin batısı; kuzey, batı ve güney sahanlıkları | 113.0 | %19 | sabit (çerçeve) | Ada Bloğu, Batı Okyanusu Levhası, Doğu Dil Levhası, Doğu Havza Levhası, Doğu Okyanusu Levhası, Güney Okyanusu Levhası, Kutup Levhası, Orta Blok |
| 2 | Doğu Dil Levhası | kıta + okyanus | 3 ve doğu kıyısının önü, Doğu Hendeği'ne kadar | 13.3 | %46 | kuzeye (dönerek) 1.8 cm/yıl | Doğu Havza Levhası, Doğu Okyanusu Levhası, Kuzey Levhası, Orta Blok, Uzun Yarımada Bloğu |
| 3 | Orta Blok | kıta + okyanus | 5 (Sarı Sıradağları'nın doğu şeridi, Sarı Ön Havzası) | 5.0 | %27 | batıya 2.8 cm/yıl | Doğu Dil Levhası, Doğu Havza Levhası, Doğu Okyanusu Levhası, Güney Okyanusu Levhası, Kuzey Levhası, Uzun Yarımada Bloğu |
| 4 | Uzun Yarımada Bloğu | kıta + okyanus | 7 (Uzun Yarımada) | 1.9 | %20 | kuzeybatıya 4.6 cm/yıl | Doğu Dil Levhası, Orta Blok |
| 5 | Ada Bloğu | kıta + okyanus | 6 (iç denizdeki ada) | 1.9 | %37 | güneye 0.7 cm/yıl | Doğu Havza Levhası, Kuzey Levhası |
| 6 | Doğu Havza Levhası | okyanus | iç denizin doğusu ve güneyi (eski Mor Okyanusu kalıntısı) | 1.8 | %0 | kuzeybatıya 0.8 cm/yıl | Ada Bloğu, Doğu Dil Levhası, Kuzey Levhası, Orta Blok |
| 7 | Doğu Okyanusu Levhası | okyanus | Doğu Hendeği'nin dışındaki okyanus | 73.7 | %0 | batıya 6.5 cm/yıl | Büyük Okyanus Levhası, Doğu Dil Levhası, Güney Okyanusu Levhası, Kutup Levhası, Kuzey Levhası, Orta Blok |
| 8 | Batı Okyanusu Levhası (yer tutucu) | okyanus | batıda, uzak sırtın ötesi | 95.9 | %0 | batıya 2.4 cm/yıl | Büyük Okyanus Levhası, Güney Okyanusu Levhası, Kutup Levhası, Kuzey Levhası |
| 9 | Kutup Levhası (yer tutucu) | okyanus | kuzeyde, uzak sırtın ötesi | 2.2 | %0 | kuzeye 0.6 cm/yıl | Batı Okyanusu Levhası, Büyük Okyanus Levhası, Doğu Okyanusu Levhası, Kuzey Levhası |
| 10 | Güney Okyanusu Levhası (yer tutucu) | okyanus | güneyde, uzak sırtın ötesi | 120.3 | %0 | güneye 1.5 cm/yıl | Batı Okyanusu Levhası, Büyük Okyanus Levhası, Doğu Okyanusu Levhası, Kuzey Levhası, Orta Blok |
| 11 | Büyük Okyanus Levhası (yer tutucu) | okyanus (atlasın kendi levhası) | uzak yarıküre; atlasın gezegen ölçekli okyanus levhası (hikâyede yok) | 81.0 | %0 | kuzeydoğuya 1.8 cm/yıl | Batı Okyanusu Levhası, Doğu Okyanusu Levhası, Güney Okyanusu Levhası, Kutup Levhası |

## 4. Sınırlar

Uzunluğa göre sıralı; 150 km'den kısa parçalar tabloda yok (hepsi `ozet.json`'da). 'yaklaşma' artıysa levhalar birbirine yaklaşıyor, eksiyse ayrılıyor. Aynı levha çifti birden çok parçaya bölünmüşse her parça ayrı satır.

| sınır | arasındaki levhalar | baskın tür (Bird) | uzunluk (km) | yaklaşma (cm/yıl) | üst levha | anlamı |
|---|---|---|---|---|---|---|
| batı okyanus sırtı (uzak) | Batı Okyanusu Levhası / Kuzey Levhası | okyanus sırtı (%95) | 17003 | -1.6 | — | [tasarım] Batı Okyanusu Levhası ile Kuzey Levhası birbirinden ayrılıyor (1.6 cm/yıl). |
| Büyük Okyanus Levhası / Doğu Okyanusu Levhası | Büyük Okyanus Levhası / Doğu Okyanusu Levhası | okyanus sırtı (%87) | 16156 | -4.5 | — | [tasarım] Büyük Okyanus Levhası ile Doğu Okyanusu Levhası birbirinden ayrılıyor (4.5 cm/yıl). |
| Batı Okyanusu Levhası / Büyük Okyanus Levhası | Batı Okyanusu Levhası / Büyük Okyanus Levhası | okyanusal yakınlaşma (%89) | 14515 | +2.6 | Batı Okyanusu Levhası | [tasarım] Büyük Okyanus Levhası, Batı Okyanusu Levhası altına dalıyor (2.6 cm/yıl). |
| güney okyanus sırtı (uzak) | Güney Okyanusu Levhası / Kuzey Levhası | okyanus sırtı (%90) | 12419 | -1.0 | — | [tasarım] Güney Okyanusu Levhası ile Kuzey Levhası birbirinden ayrılıyor (1.0 cm/yıl). |
| Doğu Okyanusu Levhası / Güney Okyanusu Levhası | Doğu Okyanusu Levhası / Güney Okyanusu Levhası | okyanusal yakınlaşma (%65) | 9422 | +2.4 | Güney Okyanusu Levhası | [tasarım] Doğu Okyanusu Levhası, Güney Okyanusu Levhası altına dalıyor (2.4 cm/yıl). |
| Büyük Okyanus Levhası / Güney Okyanusu Levhası | Büyük Okyanus Levhası / Güney Okyanusu Levhası | okyanus sırtı (%58) | 7955 | -0.7 | — | [tasarım] Büyük Okyanus Levhası ile Güney Okyanusu Levhası birbirinden ayrılıyor (0.7 cm/yıl). |
| Doğu Hendeği | Doğu Dil Levhası / Doğu Okyanusu Levhası | dalma (%66) | 6808 | +4.3 | Doğu Dil Levhası | Doğu Okyanusu Levhası, Doğu Dil Levhası altına dalıyor (4.3 cm/yıl). Hikâyede: dalma (Subduction), Doğu Hendeği: Doğu Okyanusu 3'ün altına dalıyor; Doğu Yay Dağları. |
| 2'nin doğu açığı | Doğu Okyanusu Levhası / Kuzey Levhası | dalma (%92) | 6319 | +3.9 | Kuzey Levhası | Doğu Okyanusu Levhası, Kuzey Levhası altına dalıyor (3.9 cm/yıl). Hikâyede: yanal (Transform), 2'nin doğu açığı. |
| kuzey okyanus sırtı (uzak) | Kutup Levhası / Kuzey Levhası | okyanus sırtı (%49) | 5263 | -0.1 | — | [tasarım] Kutup Levhası ile Kuzey Levhası birbirinden ayrılıyor (0.1 cm/yıl). |
| Sarı Sıradağları | Kuzey Levhası / Orta Blok | dalma (%62) | 5189 | +2.6 | Kuzey Levhası | Orta Blok, Kuzey Levhası altına dalıyor (2.6 cm/yıl). Hikâyede: kıta çarpışması (Continental collision), Sarı Sıradağları: 5, 4'ün altına giriyor (Zagros benzeri, 8 MYÖ'den beri). |
| Batı Okyanusu Levhası / Güney Okyanusu Levhası | Batı Okyanusu Levhası / Güney Okyanusu Levhası | okyanus sırtı (%71) | 5044 | -0.5 | — | [tasarım] Batı Okyanusu Levhası ile Güney Okyanusu Levhası birbirinden ayrılıyor (0.5 cm/yıl). |
| Güneydoğu Kanalı | Doğu Dil Levhası / Uzun Yarımada Bloğu | okyanus sırtı (%66) | 3692 | -2.8 | — | Doğu Dil Levhası ile Uzun Yarımada Bloğu birbirinden ayrılıyor (2.8 cm/yıl). Hikâyede: ayrılma (Divergent), Güneydoğu Kanalı: 22 MYÖ'den beri açılan yarık, kuzeyinde okyanus kabuğu (Kızıldeniz benzeri). |
| Kanal fayı | Orta Blok / Uzun Yarımada Bloğu | okyanus dönüşüm fayı (%52) | 3445 | -0.1 | — | Orta Blok ile Uzun Yarımada Bloğu yan yana kayıyor. Hikâyede: yanal (Transform), Kanal fayı: 7, 5'e göre kuzeybatıya kayıyor (Ölü Deniz fayı benzeri). |
| Mor Sıradağları | Doğu Dil Levhası / Kuzey Levhası | kıta çarpışması (%75) | 3127 | +1.3 | Kuzey Levhası | Doğu Dil Levhası, Kuzey Levhası levhasına çarpıyor, altına giriyor (1.3 cm/yıl). Hikâyede: kıta çarpışması (Continental collision), Mor Sıradağları: 3, 2'nin altına giriyor (Himalaya benzeri, 50 MYÖ'den beri). |
| adanın kuzey ve batısı | Ada Bloğu / Kuzey Levhası | okyanus sırtı (%49) | 2929 | -0.2 | — | Ada Bloğu ile Kuzey Levhası birbirinden ayrılıyor (0.2 cm/yıl). Hikâyede: ayrılma (Divergent), adanın kuzey ve batısı: yay ardı gerilmesi, 6 güneye çekiliyor. |
| Doğu Dil Levhası / Doğu Havza Levhası | Doğu Dil Levhası / Doğu Havza Levhası | dalma (%64) | 2915 | +0.2 | Doğu Dil Levhası | Doğu Havza Levhası, Doğu Dil Levhası altına dalıyor (0.2 cm/yıl). Hikâyede: yanal (Transform). |
| Büyük Okyanus Levhası / Kutup Levhası | Büyük Okyanus Levhası / Kutup Levhası | okyanusal yakınlaşma (%52) | 1935 | +0.5 | Kutup Levhası | [tasarım] Büyük Okyanus Levhası, Kutup Levhası altına dalıyor (0.5 cm/yıl). |
| Ada Hendeği | Ada Bloğu / Doğu Havza Levhası | dalma (%76) | 1840 | +0.7 | Ada Bloğu | Doğu Havza Levhası, Ada Bloğu altına dalıyor (0.7 cm/yıl). Hikâyede: dalma (Subduction), Ada Hendeği: doğu iç deniz tabanı 6'nın altına dalıyor. |
| Güneydoğu Kanalı'nın kuzey ucu | Doğu Dil Levhası / Orta Blok | okyanus sırtı (%100) | 1427 | -4.6 | — | [tasarım] Doğu Dil Levhası ile Orta Blok birbirinden ayrılıyor (4.6 cm/yıl). |
| Doğu Havza Levhası / Orta Blok | Doğu Havza Levhası / Orta Blok | kıta yarığı (%74) | 1240 | -1.3 | — | Doğu Havza Levhası ile Orta Blok birbirinden ayrılıyor (1.3 cm/yıl). Hikâyede: yanal (Transform). |
| Doğu Havza Levhası / Kuzey Levhası | Doğu Havza Levhası / Kuzey Levhası | dalma (%68) | 1127 | +0.4 | Kuzey Levhası | Doğu Havza Levhası, Kuzey Levhası altına dalıyor (0.4 cm/yıl). Hikâyede: yanal (Transform). |
| Batı Okyanusu Levhası / Kutup Levhası | Batı Okyanusu Levhası / Kutup Levhası | okyanusal yakınlaşma (%64) | 1010 | +0.1 | Kutup Levhası | [tasarım] Batı Okyanusu Levhası, Kutup Levhası altına dalıyor (0.1 cm/yıl). |
| Doğu Okyanusu Levhası / Kutup Levhası | Doğu Okyanusu Levhası / Kutup Levhası | okyanusal yakınlaşma (%100) | 1006 | +2.5 | Kutup Levhası | [tasarım] Doğu Okyanusu Levhası, Kutup Levhası altına dalıyor (2.5 cm/yıl). |
| Doğu Havza Levhası / Kuzey Levhası | Doğu Havza Levhası / Kuzey Levhası | kıta yarığı (%49) | 991 | -0.2 | — | Doğu Havza Levhası ile Kuzey Levhası birbirinden ayrılıyor (0.2 cm/yıl). Hikâyede: yanal (Transform). |
| Batı Okyanusu Levhası / Güney Okyanusu Levhası | Batı Okyanusu Levhası / Güney Okyanusu Levhası | okyanusal yakınlaşma (%100) | 984 | +0.5 | Batı Okyanusu Levhası | [tasarım] Güney Okyanusu Levhası, Batı Okyanusu Levhası altına dalıyor (0.5 cm/yıl). |
| Güney Okyanusu Levhası / Orta Blok | Güney Okyanusu Levhası / Orta Blok | okyanus dönüşüm fayı (%100) | 741 | +0.6 | — | [tasarım] Güney Okyanusu Levhası ile Orta Blok yan yana kayıyor. |
| Batı Okyanusu Levhası / Kutup Levhası | Batı Okyanusu Levhası / Kutup Levhası | okyanus dönüşüm fayı (%78) | 714 | -0.2 | — | [tasarım] Batı Okyanusu Levhası ile Kutup Levhası yan yana kayıyor. |
| adanın kuzey ve batısı | Ada Bloğu / Kuzey Levhası | dalma (%90) | 575 | +0.7 | Kuzey Levhası | Ada Bloğu, Kuzey Levhası altına dalıyor (0.6 cm/yıl). Hikâyede: ayrılma (Divergent), adanın kuzey ve batısı: yay ardı gerilmesi, 6 güneye çekiliyor. |
| Doğu Havza Levhası / Kuzey Levhası | Doğu Havza Levhası / Kuzey Levhası | dalma (%90) | 550 | +0.5 | Kuzey Levhası | Doğu Havza Levhası, Kuzey Levhası altına dalıyor (0.5 cm/yıl). Hikâyede: yanal (Transform). |
| Doğu Okyanusu Levhası / Orta Blok | Doğu Okyanusu Levhası / Orta Blok | okyanus dönüşüm fayı (%100) | 237 | +0.7 | — | [tasarım] Doğu Okyanusu Levhası ile Orta Blok yan yana kayıyor. |

## 5. Amaçlanan tür ile Bird sınıfı

Sahibin `sinirlar_hikaye.json`'undaki tür ile yeni hızlardan hesaplanan Bird sınıfı, levha çifti başına; yalnız sahibin görüntüsünde çizili kesimler sayıldı ('görüntüde km'), görüntü dışındaki uzantı ayrı. 'uyum' = amaçlanan türe uyan sınıfların uzunluk payı (kıta çarpışmasında CCB ve kıyı kesimindeki SUB uyar). Hikâyenin kuralı: ayrılırsa **tablo esas alınır**, fark not edilir.

| levhalar | amaçlanan | Bird baskın | uyum | görüntüde km | dışarıda km | sınıf payları |
|---|---|---|---|---|---|---|
| Batı Okyanusu Levhası / Kutup Levhası | yanal | — (yer tutucu, çizilmedi) | — | 0 | 1724 | — |
| Batı Okyanusu Levhası / Güney Okyanusu Levhası | yanal | — (yer tutucu, çizilmedi) | — | 0 | 6028 | — |
| Kuzey Levhası / Kutup Levhası | ayrılma | — (yer tutucu, çizilmedi) | — | 0 | 5263 | — |
| Doğu Okyanusu Levhası / Güney Okyanusu Levhası | yanal | — (yer tutucu, çizilmedi) | — | 0 | 9422 | — |
| Kuzey Levhası / Batı Okyanusu Levhası | ayrılma | — (yer tutucu, çizilmedi) | — | 0 | 17003 | — |
| Kuzey Levhası / Doğu Okyanusu Levhası | yanal | dalma | %3 | 5598 | 721 | SUB %91, CRB %6, CTF %3 |
| Doğu Dil Levhası / Doğu Okyanusu Levhası | dalma | dalma | %100 | 4426 | 2382 | SUB %100 |
| Kuzey Levhası / Ada Bloğu | ayrılma | okyanus sırtı | %47 | 3389 | 115 | OSR %43, SUB %31, OTF %20, CRB %5, CCB %2 |
| Kuzey Levhası / Güney Okyanusu Levhası | ayrılma | — (yer tutucu, çizilmedi) | — | 0 | 12419 | — |
| Doğu Dil Levhası / Uzun Yarımada Bloğu | ayrılma | okyanus sırtı | %69 | 3581 | 112 | OSR %66, OTF %26, SUB %4, CRB %3 |
| Doğu Okyanusu Levhası / Kutup Levhası | yanal | okyanusal yakınlaşma | %0 | 112 | 894 | OCB %100 |
| Kuzey Levhası / Doğu Dil Levhası | kıta çarpışması | kıta çarpışması | %79 | 3127 | 0 | CCB %75, OTF %20, SUB %4, CTF %2 |
| Kuzey Levhası / Orta Blok | kıta çarpışması | kıta çarpışması | %100 | 3736 | 1453 | CCB %52, SUB %48 |
| Kuzey Levhası / Doğu Havza Levhası | yanal | dalma | %22 | 2304 | 363 | SUB %55, CRB %19, OTF %12, CTF %9, OSR %5 |
| Doğu Dil Levhası / Doğu Havza Levhası | yanal | dalma | %19 | 2915 | 0 | SUB %64, CTF %17, OSR %11, CRB %6, OTF %2 |
| Orta Blok / Uzun Yarımada Bloğu | yanal | okyanus dönüşüm fayı | %61 | 3389 | 56 | OTF %51, SUB %15, OSR %13, CTF %10, CRB %8, CCB %3 |
| Ada Bloğu / Doğu Havza Levhası | dalma | dalma | %76 | 1840 | 0 | SUB %76, OTF %24 |
| Orta Blok / Doğu Havza Levhası | yanal | kıta yarığı | %18 | 1240 | 137 | CRB %74, OTF %13, SUB %8, CTF %4 |
| Doğu Dil Levhası / Güney Okyanusu Levhası | ayrılma | — (yer tutucu, çizilmedi) | — | 0 | 0 | — |
| Orta Blok / Güney Okyanusu Levhası | ayrılma | — (yer tutucu, çizilmedi) | — | 0 | 741 | — |
| Doğu Dil Levhası / Orta Blok | ayrılma | okyanus sırtı | %100 | 55 | 1521 | OSR %100 |

## 6. Dağlar ve yer şekilleri (kıta)

![kıta](levha_haritasi.png)

En yüksek noktalar araziden ölçüldü (sınırın 300-450 km'si içinde ya da levhanın karasında).

| ad | yer (enlem, boylam) | yükseklik (m) | gerçek benzeri | kökeni |
|---|---|---|---|---|
| Mor Sıradağları | 42.2, 25.3 | 5490 | Kafkas ölçeğinde Himalaya benzeri | 3, 2'nin altına giriyor (50 MYÖ'den beri); arkasında ~1 km'lik Şerit Yaylası. |
| Sarı Sıradağları | 18.1, -13.0 | 3057 | Zagros / Tayvan benzeri | 5, 4'ün altına giriyor (8 MYÖ'den beri); genç, dik, en yüksek güney orta kesim. |
| Doğu Yay Dağları | 17.4, 22.1 | 1021 | And benzeri yay | Doğu Okyanusu, Doğu Hendeği'nde 3'ün altına dalıyor. |
| Uzun Yarımada sırtı | 18.8, -4.8 | 1539 | Ölü Deniz fayı kıyısı | 7, 5'e bastırarak kuzeybatıya kayıyor; dar, dik sırt. |
| İç denizdeki ada (6) | 38.6, -11.5 | 1708 | Ege / Tiren benzeri | Yay ardı gerilmesi: parmak biçimli horst ve grabenler; Ada Hendeği güneyinde. |
| Köprü Kıstağı | 35.2, -27.7 | 400 | Panama benzeri | 3 MYÖ'de 1 ile 4 arasındaki boğazı kapattı; 80-400 m. |

## 7. Tarih (eskiden yeniye)

Ayrıntı ve tek tek olaylar `HIKAYE.md`'de.

1. **3400-2500 MYÖ**: Kalkanların doğuşu: Ak Kalkan (1'in kuzeyi), Boz Kalkan (2'nin doğusu), Kır Çekirdeği (2'nin batısı), Kızıl Kalkan (3'ün ortası).
2. **2100-1700 MYÖ**: Kaynak orojenleri: Kır Çekirdeği ile Boz Kalkan birleşir; 2'nin içi tek parça olur.
3. **1150-750 MYÖ**: İlk Birlik süper kıtası; 1'in batısında Ulu Dağlar. Parçalanınca 1 ile 2 arasında Ata Okyanusu açılır.
4. **750-520 MYÖ**: İki büyük buzullaşma; Ata Okyanusu kıyılarında kalın çökeller.
5. **520-400 MYÖ**: Mavi orojeni: Ata Okyanusu kapanır, 430 MYÖ'de 1 ile 2 çarpışır (Mavi Dağlar, Kaledonya benzeri).
6. **400-290 MYÖ**: Köz orojeni: Güney Kıtası çarpar, 4'ün temeli kıvrılır; Büyük Birlik. Doğuda Mor Okyanusu kaması açık kalır.
7. **290-200 MYÖ**: İnce Şerit Güney Kıtası'ndan kopup 210 MYÖ'de 2'nin güneyine yapışır; 252 MYÖ Kuzey Tuzakları.
8. **200-130 MYÖ**: Büyük Birlik parçalanır: Batı ve Güney okyanusları açılır; 3, 5 ve 7'yi taşıyan Doğu Parça kuzeye yola çıkar.
9. **130-85 MYÖ**: Makas açılması: 4 ve 6, 1'den ayrılıp ~29° saat yönünde döner; iç denizin batısı açılır, Köprü Dağları başlar.
10. **85-50 MYÖ**: Kuzeye koşu: Doğu Parça yılda ~6,5 cm ilerler; 66 MYÖ Kızıl Basamaklar; Doğu Okyanusu 3'ün altına dalmaya başlar.
11. **50-25 MYÖ**: Mor çarpışması: 3, 2'nin altına girer (Mor Sıradağları, Şerit Yaylası); Tuzak Çanağı kalkar; doğu iç deniz kuşatılır.
12. **25-2,6 MYÖ**: İç deniz evresi: Ada Hendeği, 6 güneye çekilir; 5 kopar ve 8 MYÖ'de 4'e çarpar (Sarı Sıradağları); 7 Kanal Fayı boyunca kayar; 3 MYÖ Köprü Kıstağı kapanır.
13. **2,6-0 MYÖ**: Buzul çağları; bugün iki etkin çarpışma (3 ile 2, 5 ile 4), bir yanal fay, bir yay ardı gerilmesi, bir yarık.

## 8. Açık kararlar

- Uzak okyanus levhalarının (8-11) yeri ve Büyük Okyanus'un hızı tasarım; hikâyede yer tutucu.
- Kaçış Bloğu (2'nin güneydoğu köşesi, doğuya 1,2 cm/yıl) çok küçük olduğu için levha haritasında yok (hikâye kararı).
- Doğu Dil Levhası dönerek ilerliyor (doğu ucu ~2,4, batı ucu ~1,2 cm/yıl); modelde Euler vektörüne 0,3°/My dönme eklendi.

## 9. Dosyalar

- `HIKAYE.md`: hikâyenin tamamı: dönemler, olaylar (sahibin)
- `levha_dunya.png`: tüm gezegen, Equal Earth
- `levha_kure.png`: iki küre görünümü
- `levha_haritasi.png`: kıta ayrıntısı, zaman çizelgesi
- `sinirlar.geojson`: her sınır adımı bir LineString; özellikler: sinir, sol, sag, sinif, ust, yaklasma, yanal, km, goruntude
- `levha_kimlik.png`: kaynak çözünürlüğünde ızgara (4096×2048, satır 0 = 90°K), değer = levha kimliği
- `levhalar.json`: levha alanları, Euler kutupları, amaçlanan türle karşılaştırma
- `kaynak/`: sahibin girdileri (levha_kimlik_8k.png, levhalar_hikaye.json, sinirlar_hikaye.json), 16k kaydı, uzak okyanus levhaları
- `TEKTONIK.md`: kararların tarihçesi (eski hikâye geçersiz işaretli)
