# DURUM — aktif durum (her oturumun başında oku)

Son güncelleme: 26 Eylül 2026, bulut oturumu. Bu dosya "şu an neredeyiz"
sorusunun cevabıdır; kalıcı bilgi `CLAUDE.md`'de, gece bakımının ayrıntısı
`GECE.md`'de. Oturumu bitirirken bu dosyayı güncelle.

## Şu an yayında olan

- `main`: `d0c4fce`. Veri sürümü `f773654851` (üretim 26 Eylül 05:57 UTC).
  İklim sayıları 25 Eylül'den beri aynı (`dunyam.json` → `_guncel_durum`).
- Son eklenenler, telefonda görüldü:
  - Günlük sıcaklık: gündüz/gece, ayın tipik tepesi/dibi, 30 yılda bir rekor
    (Sıcaklık sekmesinde Ortalama/Gündüz/Gece/Tepe/Dip; kartta bant ve satır).
  - Deniz dokusu: sığ/derin tonu, eşderinlik çizgileri, kıyı köpüğü. Yalnız
    görünüş; "derinlik" kıyıya uzaklıktır, batimetri değil. Ayarlarda
    "Deniz dokusu" anahtarı.
  - Deniz kartı: her sekmede denize dokununca su sıcaklığı, aylık rüzgâr ve
    Beaufort şeridi, buz ayları, tropikal fırtına koşulu (yalnız eşik),
    yakındaki akıntı, yağış, en yakın kara.
- Açık kalan karar yok. Doğu kıyı savanı bilerek bırakıldı (`_dogu_kiyi_savan`).

## Yayın (Cloudflare) — 26 Eylül'de öğrenilen

`main`'e push'lar bir süre üretime gitmedi: Cloudflare'in üretim dalı `main`
değildi, `main` yalnız önizleme olarak derleniyordu. GitHub'daki "Workers
Builds" onay işareti yeşil olsa da yayın olmuyordu. Sahibi Cloudflare'de
Settings → Build → Branch control → üretim dalı = `main` yaptı, düzeldi.
Bir değişiklik telefona gelmiyorsa önce Cloudflare → Deployments'ta yeni kayıt
var mı bak. Telefonda: uygulamayı tamamen kapatıp aç; veri sürümü
değişmediyse "Güncellemeleri denetle" yalnız "Güncel" der, kodu yenilemez.

## Bilgisayarda (masaüstü, asıl proje "Proje 3") yapılacaklar

Sırası önemli. 1 bitmeden 2'deki betikleri KOŞMA: bu repodaki ayrışmaları
geri alırlar.

1. **Ayrışmaları bu repodan asıl projeye taşı** (normal yönün tersi; ayrıntı
   `CLAUDE.md` §7.6). Taşınacaklar:
   - `motor/`: `moisture.py` (storm_c, storm_contrast_sigma_k,
     conserve_moisture, ayların paralel çözümü, `_saniye_ay`), `grid.py`
     (bölünmeyen kaynak, dikişte su kütlesi), `sanity.py` (donmuş okyanus,
     alan ağırlıklı kara yağışı / sınıf payı), `maritime.py` (sea_ice_air),
     `circulation.py` (belt_shift_decay, kapalı).
   - `dunya/`: `dunyam_heightmap.png`, `dunyam.json` (elev_curve çapaları,
     `heightmap.kabartma` kaydı, bütün `_` notları), `kabartma_kaynak.jpg`.
   - Sonra `python _senkron_kontrol.py <asıl proje yolu>` fark göstermemeli.
2. **1 bitene kadar koşma:** `_repo_senkron.py --yaz` (repoyu eski hâline
   döndürür), `_egri_kur.py --yaz` (sahibin yükseklik çapalarını siler).
3. **Palet:** masaüstü şablonu yeni koyu `KPAL`'a taşınana kadar `_atlas.py`
   palet karşılaştırmasında DURUR; bu beklenen (§7.4). Ya şablonu taşı ya da
   durmayı bil.
4. `_atlas.py`'nin yazdığı `atlas.json`'u bu repoya KOPYALAMA: eski biçim,
   yeni uygulama açılmaz. Mobil veri yalnız bu repodaki `uret.py`'den.
5. Windows'ta bir kez dene: `baslat.bat` ve `tunel.bat` (GECE 41; bulutta
   sınanamadı), klavye (GECE 22).
6. İsteğe bağlı: nem korunumu (`conserve_moisture`) Dünya doğrulamasında hiç
   denenmedi (§8). Asıl projede Dünya'ya karşı bir koşu değerli olur.

## Sahibinin kararını bekleyen, küçük

- Akıntı uzaklığında Dünya sabiti: `motor/temperature.py` 111.32 / 110.57
  km/derece (Dünya elipsoidi). §2.1'e aykırı; düzeltmesi `radius_km × π/180`.
  Dünyam'da etkisi karanın %0.05'i, ama sayı değiştirdiği için beklemede.
- Aylık sıcaklığı 2 baytla saklamak (kartta sınıf/klimagram çelişkisi
  karanın %2.1'inde, en çok 0.16 °C). Öncelik düşük.
- Küresel ortalama 15.1 °C (girdi 14). Öneri: dokunma.
- Birleşmiş eski dallar: `gunluk-sicaklik`, `deniz-deneme`, `deniz-yumusak`,
  `deniz-kart`. Silmek sahibinde (bulut oturumunun silme izni yok, 403).

## Kurallar (hatırlatma)

- `main`'e push = telefona yayın. `main`'e yalnız sahibi "Main'e birleştir"
  deyince girilir; iş önce bir dalda, test yeşil olunca ileri sarma.
- İklim parametresi sahibinin kararı olmadan değişmez; seçenekler PNG ile.
- Bulutta `test/uygulama_test.js`'in "güncelleme denetimi yeni veride
  yeniler" maddesi yerelde zaman aşımına düşüyor (değişmemiş `main`'de de);
  GitHub'da geçiyor. Karar GitHub'daki `uygulama testi` sonucudur.
