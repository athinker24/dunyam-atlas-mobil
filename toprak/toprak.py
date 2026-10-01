"""Toprak türleri: iklim, bitki örtüsü, eğim, nehir ve volkan verisinden.

    python toprak/toprak.py          # ~30 s; data/toprak.png ve toprak.json yazar

Yöntem: WRB (Dünya Referans Temeli, FAO/IUSS 2015) referans grup adları,
**bölgesel (zonal) toprak** kavramıyla eşlenmiş — her iklim/bitki kuşağının
kendi karakteristik toprağı olduğu, 19. yy Rus toprak biliminden gelen ve
WRB'nin ilk düzeyinde hâlâ izi olan klasik fikir (Dokuchaev). Kaynak:
FAO toprak sınıflandırma bölümü, WRB özeti (aşağıda). Girdiler `bitki/`
(biyom kodu, nem oranı = AET/PE), `su/` (yıllık yağış, nehir debisi, kapalı
göl/havza), `tektonik/` (volkan kuşakları) — hepsi aynı kaynak ızgarada
(~0.088°, `bitki/_bitki.npz` ile aynı).

**Bölgesel taban (biyom → toprak):**
  tropik yağmur/mevsimsel orman     Ferralsol   — şiddetle yıkanmış, demir/
                                                   alüminyum oksitli, verimsiz
  savan / kuru orman, kuru ağaçlık  Lixisol     — savan, belirgin kurak
                                                   mevsim, kilin B ufkunda
                                                   birikmesi
  ılık yaprak dökmeyen orman        Acrisol     — nemli (sub)tropik orman,
                                                   asit, düşük baz doygunluğu
  ılıman yaprak döken orman         Luvisol     — ılıman orman, kil birikmeli,
                                                   yüksek baz doygunluğu
  serin karışık orman               Cambisol    — genç, az gelişmiş orman
                                                   toprağı
  tayga, soğuk yaprak döken orman   Podzol      — iğne yapraklı, asit,
                                                   kül-gri yıkanma ufku
  maki                              Luvisol     — Akdeniz "kırmızı toprağı"
                                                   ayrı WRB grubu değil,
                                                   çoğu Luvisol/Cambisol
  bozkır (P ≥ 400 mm)               Chernozem   — nemli step, derin siyah,
                                                   humusça zengin
  bozkır (P < 400 mm), kurak çalılık Kastanozem — kurak step, kestane rengi
  tundra                            Cryosol     — donmuş katman 100 cm içinde
  çöl (sıcak/soğuk)                 Calcisol    — kurak, kireç birikmeli

**Örtüler (bölgesel tabanın üstüne, sırayla — sonraki önceki geçersiz kılar):**
  dağlık (eğim eşiği üstü)          Leptosol    — sığ, taşlı, dağ toprağı
  volkan kuşağı (`data/tektonik.json`) Andosol   — taze volkanik külden,
                                                   hafif ama verimli
  kapalı havza (`su` kapalı göl/çukur) Solonchak — tuz birikimi, dışa akışsız
  alüvyon ovası (dağ önü, düz, alçak, nehir ağı yoğun) Fluvisol — önülke havzası
  taşkın ovası (büyük nehir, düz)   Fluvisol    — genç, tortul, her taşkında
                                                   yenilenir
  buz/kalıcı kar                    (toprak yok) — çıplak buz/kaya

Kaynaklar: FAO Toprak Sınıflandırma (fao.org/soils-portal); Kastanozem ve
Chernozem yağış eşiği (200-450 / 400-550 mm, Wikipedia "Kastanozem"); WRB
bölgesel dağılım (ScienceDirect, Distribution patterns of World Reference
Base soil groups). TOPRAK.md'de ayrıntı ve denetim.
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
BURASI = os.path.dirname(os.path.abspath(__file__)); KOK = os.path.dirname(BURASI)
sys.path.insert(0, os.path.join(KOK, "su")); sys.path.insert(0, KOK)

# kod: (ad, açıklama, Dünya'da örnek, renk)
TOPRAK = {
    1: ("Ferralsol", "Şiddetle yıkanmış tropik toprak; demir ve alüminyum oksitleri kalır, besin ağaçta.",
        "Amazon, Kongo havzası", (150, 92, 58)),
    2: ("Lixisol", "Savan toprağı; belirgin kurak mevsimde kil B ufkunda birikir, orta verimli.",
        "Batı Afrika savanı, Hindistan yarımadası", (176, 138, 78)),
    3: ("Acrisol", "Nemli (sub)tropik orman toprağı; asit, düşük baz doygunluğu, yıkanmış.",
        "Güneydoğu Asya, Güney Çin", (140, 100, 66)),
    4: ("Luvisol", "Ilıman orman ya da Akdeniz toprağı; kil B ufkunda birikir, baz doygunluğu yüksek.",
        "Orta Avrupa, Akdeniz kıyıları", (168, 122, 74)),
    5: ("Cambisol", "Genç, az gelişmiş orman toprağı; henüz belirgin bir B ufku kurmamış.",
        "Kuzey Avrupa, dağ eteği ormanları", (150, 130, 92)),
    6: ("Podzol", "İğne yapraklı orman toprağı; asit, kül-gri yıkanma ufku, altında demir birikimi.",
        "Sibirya, Kanada tayga kuşağı", (172, 168, 150)),
    7: ("Chernozem", "Nemli step toprağı; derin, siyah, humusça çok zengin — dünyanın en verimli toprağı.",
        "Ukrayna, Kuzey Amerika prerileri", (58, 46, 38)),
    8: ("Kastanozem", "Kurak step toprağı; kestane rengi, Chernozem'den daha az humus ve daha sığ kireç.",
        "Kazakistan bozkırı, Moğolistan", (120, 84, 54)),
    9: ("Cryosol", "Donmuş toprak; 100 cm içinde permafrost, çözülme yalnız yaz üstünde.",
        "Sibirya ve Kanada tundrası", (140, 156, 158)),
    10: ("Calcisol", "Kurak toprak; buharlaşma kireci yüzeye yakın biriktirir, organik madde çok az.",
         "Sahra, Orta Asya çölleri", (206, 186, 140)),
    11: ("Leptosol", "Sığ, taşlı dağ toprağı; ana kayaya 25 cm içinde ulaşılır, erozyon sürekli yeniler.",
         "Alp ve Himalaya yamaçları, her yüksek dağ", (144, 132, 118)),
    12: ("Andosol", "Taze volkanik külden; hafif, süngerimsi, yüksek su tutar, genelde verimli.",
         "Java, Etiyopya ve Meksika yaylaları", (98, 90, 70)),
    13: ("Solonchak", "Tuzlu toprak; dışa akışsız havzada buharlaşma tuzu yüzeye taşır.",
         "Hazar çevresi, Büyük Tuz Gölü havzası", (196, 192, 176)),
    14: ("Fluvisol", "Taşkın ovası toprağı; genç, katmanlı, her taşkında tazelenir — nehir tarımının temeli.",
         "Nil, Ganj, Mekong deltaları", (108, 88, 62)),
    15: ("Buz / çıplak kaya", "Toprak oluşmamış; kalıcı buz ya da aşınmamış kaya yüzeyi.",
         "Antarktika, yüksek buzullar", (232, 236, 240)),
}

EGIM_ESIK = 220.0    # m/hücre (~9.5 km, 2 hücrelik Gauss yumuşatmalı): bu üstü Leptosol (dağlık). Kalibrasyon 27 Eylül:
                      # karanın 85. yüzdelik dilimi (kara medyanı ~950 m, Dünya'dan bilerek
                      # yüksek — CLAUDE.md §6); 55'te Leptosol %35'e çıkıyordu (7.2'deki gibi
                      # çözünürlüğe duyarlı, bu koşuda ~9.5 km adımda kalibre edildi)
NEHIR_Q = 50.0        # su/disa.py ile aynı: bu debinin üstü "büyük nehir"
TASKIN_EGIM = 25.0    # m/hücre altı düz sayılır
TASKIN_UZAK_HUCRE = 2  # nehirden bu kadar hücre içi taşkın ovası
VOLKAN_KM = 5.0        # yarık volkanizması buffer'ı (km, tektonik/uygulama.py'deki CEPHE_KM'den küçük: nokta veri)
HAVZA_UZAK_HUCRE = 6
# alüvyon ovası (önülke havzası): yüksek dağın önündeki düz, alçak, nehir ağı yoğun
# ova, dağdan inen nehirlerin tortusuyla dolar (İndus-Ganj, Po, Mezopotamya).
# Sahibi 1 Ekim: "duvarın güneyinin çok verimli olmasını istiyordum". Eşikler bu
# ızgarada ölçülerek seçildi: karanın %12.7'si, Duvar'ın güney şeridinin %36'sı.
ALUVYON_Z = 700.0        # m altı
ALUVYON_EGIM = 60.0      # m/hücre altı (yumuşatılmış eğim)
ALUVYON_NEHIR_Q = 20.0   # m³/s: yoğunluğa sayılan dere
ALUVYON_YOGUNLUK = 0.06  # 4 hücrelik Gauss içinde nehir hücresi payı
ALUVYON_DAG_HUCRE = 50   # 2000 m üstü araziye en çok ~490 km   # kapalı gölden bu kadar hücre içi (~55 km) tuzlu toprak etkisi


def _egim(z):
    # ham gradyan tuz-biber gürültülü (§7.2 tuzağı: ince ızgara pürüzlü);
    # tektonik/app.js'teki kabartma yumuşatmasıyla aynı yarıçap (2 hücre)
    gy, gx = np.gradient(np.maximum(z, 0))
    return ndimage.gaussian_filter(np.hypot(gx, gy), 2)


def _poligon_icinde(pts, poly):
    """Ray-casting (tek geçiş, vektörleştirilmiş): pts (N,2), poly [(x,y)..].
    matplotlib yok (CLAUDE.md: numpy/scipy/pillow dışında bağımlılık yasak)."""
    x, y = pts[:, 0], pts[:, 1]
    icinde = np.zeros(len(pts), bool)
    poly = np.asarray(poly)
    x1, y1 = poly[:, 0], poly[:, 1]
    x2, y2 = np.roll(x1, -1), np.roll(y1, -1)
    for a1, b1, a2, b2 in zip(x1, y1, x2, y2):
        kesen = ((b1 > y) != (b2 > y))
        if not kesen.any():
            continue
        xk = a1 + (y[kesen] - b1) * (a2 - a1) / (b2 - b1 + 1e-30)
        icinde[kesen] ^= x[kesen] < xk
    return icinde


def _volkan_maske(lat, lon, shape):
    """tektonik/uygulama.py'nin data/tektonik.json'una yazdığı yay kuşağı
    çokgenlerini (on+arka, fark kodlu) ızgaraya rasterize eder."""
    yol = os.path.join(KOK, "data", "tektonik.json")
    if not os.path.exists(yol):
        return np.zeros(shape, bool)
    T = json.load(open(yol, encoding="utf-8"))
    ny, nx = shape
    maske = np.zeros(shape, bool)
    ii, jj = np.meshgrid(np.arange(ny), np.arange(nx), indexing="ij")

    def coz(kod):
        n = len(kod) // 2; x = 0; y = 0; out = []
        for i in range(n):
            x += kod[2 * i]; y += kod[2 * i + 1]; out.append((x / 100, y / 100))
        return out

    for k in T.get("kusaklar", []):
        on = coz(k["on"]); arka = coz(k["arka"])
        poly = on + arka[::-1]
        lo = [p[0] for p in poly]; la = [p[1] for p in poly]
        lo0, lo1, la0, la1 = min(lo) - 0.1, max(lo) + 0.1, min(la) - 0.1, max(la) + 0.1
        j0 = max(0, int(np.searchsorted(lon, lo0)) - 1); j1 = min(nx, int(np.searchsorted(lon, lo1)) + 1)
        i0 = max(0, int(np.searchsorted(-lat, -la1)) - 1); i1 = min(ny, int(np.searchsorted(-lat, -la0)) + 1)
        if j1 <= j0 or i1 <= i0:
            continue
        sub_i, sub_j = ii[i0:i1, j0:j1], jj[i0:i1, j0:j1]
        pts = np.column_stack([lon[sub_j.ravel()], lat[sub_i.ravel()]])
        icinde = _poligon_icinde(pts, poly).reshape(sub_i.shape)
        maske[i0:i1, j0:j1] |= icinde
    # yarıklar: nokta/çizgi veri, küçük tampon (uzaklık dönüşümüyle)
    for r in T.get("yariklar", []):
        n = len(r["p"]) // 2; x = 0; y = 0
        for i in range(n):
            x += r["p"][2 * i]; y += r["p"][2 * i + 1]
            j = int(np.argmin(np.abs(lon - x / 100))); ii2 = int(np.argmin(np.abs(lat - y / 100)))
            r_hucre = max(1, int(VOLKAN_KM / (111.2 * abs(lat[1] - lat[0]))))
            i0, i1 = max(0, ii2 - r_hucre), min(ny, ii2 + r_hucre + 1)
            j0, j1 = max(0, j - r_hucre), min(nx, j + r_hucre + 1)
            maske[i0:i1, j0:j1] = True
    return maske


def siniflandir(kb, alfa, P, z, q, kapali, lat, lon):
    ny, nx = kb.shape
    # 1) bölgesel taban: biyom kodundan (bitki.BIYOM 1-16)
    BOLGESEL = {1: 1, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 6, 9: 4, 10: 8, 12: 9, 13: 10, 14: 10, 15: 9, 16: 2}
    k = np.full(kb.shape, 10, np.uint8)   # varsayılan çöl (kb==0 deniz/göl sonra elenir)
    for bkod, tkod in BOLGESEL.items():
        k[kb == bkod] = tkod
    # bozkır (11): nemli step Chernozem, kurak step Kastanozem (Wikipedia
    # "Kastanozem": 200-450 mm; "Chernozem": 400-550 mm; eşik 400 mm)
    step = kb == 11
    k[step & (P >= 400)] = 7
    k[step & (P < 400)] = 8
    # 2) örtüler: sırayla, sonraki önceki geçersiz kılar
    egim = _egim(z)
    k[egim >= EGIM_ESIK] = 11                                    # dağlık
    yog = ndimage.gaussian_filter(((q >= ALUVYON_NEHIR_Q) & (z >= 0)).astype(np.float32), 4)
    dag = ndimage.distance_transform_edt(~(z >= 2000))
    aluvyon = (z >= 0) & (z < ALUVYON_Z) & (egim < ALUVYON_EGIM) & (yog >= ALUVYON_YOGUNLUK) & (dag <= ALUVYON_DAG_HUCRE)
    k[aluvyon] = 14                                              # alüvyon ovası (önülke)
    k[_volkan_maske(lat, lon, kb.shape)] = 12                    # volkan kuşağı
    havza = ndimage.distance_transform_edt(~kapali) <= HAVZA_UZAK_HUCRE
    k[havza & (alfa < 0.5)] = 13                                 # kapalı/kurak havza
    nehir = (q >= NEHIR_Q) & ~kapali
    taskin = (ndimage.distance_transform_edt(~nehir) <= TASKIN_UZAK_HUCRE) & (egim < TASKIN_EGIM)
    k[taskin] = 14                                               # taşkın ovası
    return k


def main():
    b = np.load(os.path.join(KOK, "bitki", "_bitki.npz"))
    a = np.load(os.path.join(KOK, "su", "_akim.npz"))
    su = np.load(os.path.join(KOK, "su", "_su.npz"))
    kb, alfa, lat, lon = b["k"], b["alfa"], b["lat"], b["lon"]
    z, P, q, kapali = a["z"], a["P"], su["q"], su["kapali"]
    import pickle
    disa = pickle.load(open(os.path.join(KOK, "su", "_disa.pkl"), "rb"))
    kara = (z >= 0) & ~disa["gm"]
    k = siniflandir(kb, alfa, P, z, q, kapali, lat, lon)
    buzul = a["buzul"]
    k[buzul] = 15
    k[~kara] = 0
    np.savez_compressed(os.path.join(BURASI, "_toprak.npz"), k=k, lat=lat, lon=lon)   # yasam/yasam.py okur
    wgt = np.cos(np.radians(lat))[:, None] * kara
    pay = {int(c): float(wgt[k == c].sum() / wgt.sum()) for c in TOPRAK}
    for c, (ad, *_r) in TOPRAK.items():
        print("%2d %-14s %%%5.1f" % (c, ad, 100 * pay[c]))
    # aynı 2x büyütme ve yumuşak argmax (bitki.py ile aynı yöntem, keskin sınır)
    ii, jj = np.where(kara)
    i0, i1, j0, j1 = ii.min(), ii.max() + 1, jj.min(), jj.max() + 1
    kc = k[i0:i1, j0:j1]
    F = 2
    en = None; secim = None
    for c in np.unique(kc):
        if c == 0:
            continue
        g = ndimage.gaussian_filter(ndimage.zoom((kc == c).astype(np.float32), F, order=1), 0.9)
        if en is None:
            en = g; secim = np.full(g.shape, c, np.uint8)
        else:
            m = g > en; en[m] = g[m]; secim[m] = c
    zc = ndimage.zoom(z[i0:i1, j0:j1].astype(np.float32), F, order=1)
    gc = ndimage.zoom(disa["gm"][i0:i1, j0:j1].astype(np.float32), F, order=1)
    secim[(zc < 0) | (gc >= 0.5)] = 0
    im = Image.fromarray(secim, "P")
    pal = [12, 24, 34] * 256
    for c, (_a, _n, _o, r) in TOPRAK.items():
        pal[3 * c:3 * c + 3] = list(r)
    im.putpalette(pal)
    im.save(os.path.join(KOK, "data", "toprak.png"), optimize=True, transparency=0)
    dl, dn = lat[1] - lat[0], lon[1] - lon[0]
    kesit = [float(lon[j0] - dn / 2), float(lat[i1 - 1] + dl / 2), float(lon[j1 - 1] + dn / 2), float(lat[i0] - dl / 2)]
    veri = dict(ne="Dünyam toprak türleri (toprak/toprak.py); yöntem TOPRAK.md",
                kesit=kesit,
                topraklar={str(c): dict(ad=a_, ne=n, ornek=o, renk=list(r), pay=round(pay[c], 4)) for c, (a_, n, o, r) in TOPRAK.items()})
    with open(os.path.join(KOK, "data", "toprak.json"), "w", encoding="utf-8") as fh:
        json.dump(veri, fh, ensure_ascii=False, indent=1)
    veri_rgb = np.stack([kc, np.zeros_like(kc), np.zeros_like(kc)], -1).astype(np.uint8)
    Image.fromarray(veri_rgb, "RGB").save(os.path.join(KOK, "data", "toprak_veri.png"), optimize=True)
    print("toprak.png %dx%d %.0f KB" % (secim.shape[1], secim.shape[0], os.path.getsize(os.path.join(KOK, "data", "toprak.png")) / 1024))


if __name__ == "__main__":
    main()
