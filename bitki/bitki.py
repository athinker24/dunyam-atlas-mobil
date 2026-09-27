"""Bitki örtüsü: iklimden doğal (potansiyel) bitki örtüsü, biyom haritası.

    python bitki/bitki.py            # ~1 dk; data/bitki.png ve bitki/bitki.json yazar

Yöntem: BIOME1 (Prentice vd. 1992, J. Biogeography 19:117-134) biyoiklim
sınırlarından uyarlanmış kural tablosu. Değişkenler:
- Tc: en soğuk ay ortalaması (°C), Tw: en sıcak ay ortalaması
- GDD5, GDD0: 5 ve 0 °C üstü gün-derece toplamı (aylık ortalamadan, ay gün
  sayısı gezegenin yılından)
- alfa: yıllık gerçek buharlaşma / potansiyel buharlaşma (AET/PE). BIOME1'de
  Priestley-Taylor alfası; burada su modelinin (su/akim.py) Oudin PE'si ve
  150 mm toprak kovasıyla bulunan AET. Aynı büyüklük (0 kurak, 1 nemli).
İklim su modeliyle aynı yoldan kaynak araziye (~0.088°) indirilir, yani
dağlarda sıcaklık yükseklikle düşer (5.2 K/km) ve ağaç sınırı kendiliğinden
çıkar.

Eşikler (bitki işlev tipleri, Prentice vd. 1992 Tablo 1):
  tropik yaprak dökmeyen      Tc >= 15.5, alfa >= 0.80   (burada Tc >= 18, Köppen A)
  tropik yağmurla yeşeren     Tc >= 15.5, 0.45 <= alfa <= 0.95   (burada Tc >= 18)
  ılık yaprak dökmeyen        Tc >= 5,    alfa >= 0.65
  ılıman yaz yeşil (yaprak döken) -15 <= Tc <= 15.5, GDD5 >= 1200, alfa >= 0.65
  serin iğne yapraklı         -19 <= Tc <= 5, GDD5 >= 900, alfa >= 0.65
  boreal iğne yapraklı        -35 <= Tc <= -2, GDD5 >= 350, alfa >= 0.75
  boreal yaz yeşil            Tc <= 5, GDD5 >= 350, alfa >= 0.65
  sert yapraklı / sukulent    Tc >= 5, alfa >= 0.28
  sıcak ot/çalı               Tw >= 22, alfa >= 0.18
  serin ot/çalı               GDD0 >= 500, alfa >= 0.33
  soğuk ot/çalı (tundra)      GDD0 >= 100, alfa >= 0.33
  sıcak çöl çalısı            Tw >= 22
  soğuk çöl çalısı            GDD0 >= 100
Ağaçlar otlardan, otlar çöl çalılarından baskındır (BIOME1 baskınlık
sırası); biyom baskın tiplerin birleşiminden adlandırılır.

NOT: eşikler makalenin tablosundan alındı ama bu oturumdan makaleye
erişilemedi (ağ kısıtı); değerler tekrar kontrol edilmeli (BITKI.md).

Kalıcı kar (su modelinde hiç erimeyen kar) buz sayılır. Göl ve deniz
boştur (uygulamada su katmanı çizer).
"""
import json, os, sys
import numpy as np
from PIL import Image
BURASI = os.path.dirname(os.path.abspath(__file__)); KOK = os.path.dirname(BURASI)
sys.path.insert(0, os.path.join(KOK, "su")); sys.path.insert(0, KOK)
import akim

# kod: (ad, açıklama, Dünya'da örnek, renk)
BIYOM = {
    1: ("Tropikal yağmur ormanı", "Yıl boyu sıcak ve nemli; yaprağını dökmeyen, çok katlı sık orman.",
        "Amazon, Kongo, Borneo", (22, 92, 48)),
    2: ("Tropikal mevsimsel orman", "Sıcak, kurak bir mevsimi olan; kurak ayda yaprağının bir kısmını döken orman.",
        "Hindistan'ın batı kıyısı, Güneydoğu Asya muson ormanları", (60, 128, 52)),
    3: ("Tropikal kuru orman ve savan", "Uzun kurak mevsim: seyrek ağaçlı otlak ya da kuru mevsimde yaprak döken orman.",
        "Serengeti, Brezilya Cerrado'su", (176, 170, 62)),
    4: ("Ilık yaprak dökmeyen orman", "Kışı ılık, yağışı bol; defne, meşe, kâfur gibi geniş yapraklı yeşil orman.",
        "Güney Çin, Güney Japonya, Karadeniz'in doğusu", (48, 138, 108)),
    5: ("Ilıman yaprak döken orman", "Kışı soğuk, yazı ılık ve nemli; kayın, meşe, akçaağaç.",
        "Batı ve Orta Avrupa, ABD'nin doğusu", (120, 170, 70)),
    6: ("Serin karışık orman", "Yaprak döken ağaçlarla iğne yapraklıların karışığı; kışı sert.",
        "Güney İskandinavya, Büyük Göller çevresi", (70, 118, 90)),
    7: ("Tayga (iğne yapraklı kuzey ormanı)", "Uzun, çok soğuk kış, kısa yaz; ladin, köknar, çam.",
        "Sibirya, Kanada", (40, 84, 78)),
    8: ("Soğuk yaprak döken orman", "Çok soğuk ve kuru kış; kışın yaprağını döken iğne yapraklı (karaçam).",
        "Doğu Sibirya karaçam ormanları", (112, 132, 112)),
    9: ("Maki ve sert yapraklı çalılık", "Ilık, kurak yaz; kuraklığa dayanıklı sert yapraklı çalı ve seyrek ağaç.",
        "Akdeniz kıyıları, Kaliforniya chaparral'ı", (150, 128, 72)),
    10: ("Kurak çalılık ve dikenli savan", "Sıcak ve yarı kurak, yağışı yazın; kuraklığa dayanıklı dikenli çalı, seyrek ağaç ve ot.",
         "Sahel, Hindistan'ın dikenli çalılıkları, Brezilya Caatinga'sı", (214, 176, 96)),
    11: ("Bozkır (serin otlak)", "Soğuk kışlı, yarı kurak; uzun ya da kısa otlu ağaçsız ova.",
         "Kazak ve Moğol bozkırı, Kuzey Amerika çayırları", (208, 200, 138)),
    12: ("Tundra", "Ağaç yetişemeyecek kadar kısa ve serin yaz; yosun, liken, cüce çalı.",
         "Kuzey Kanada, Sibirya kıyısı; dağlarda ağaç sınırının üstü", (156, 176, 170)),
    13: ("Sıcak çöl", "Çok az yağış, sıcak; seyrek çalı ya da çıplak toprak.",
         "Sahra, Arabistan", (232, 206, 146)),
    14: ("Soğuk çöl ve yarı çöl", "Az yağış, soğuk kış; seyrek çalı (pelin, geven).",
         "Gobi, Tibet'in kuzeyi, Patagonya", (190, 176, 150)),
    16: ("Kuru ağaçlık ve açık orman", "Uzun kurak kışlı, yağışı yazın; kışın yaprağını döken seyrek ağaçlar, altında ot ve çalı. Kurak değil ama orman kapanamaz.",
         "Hindistan'ın kuru yaprak döken ormanları, Güney Afrika bushveld'i", (132, 150, 78)),
    15: ("Buz ve kutup çölü", "Kalıcı kar ve buz ya da bitkinin yaşayamayacağı kadar soğuk.",
         "Antarktika, Grönland; en yüksek zirveler", (238, 242, 246)),
}


def degiskenler(d, w):
    T, P = d["Tay"], d["Pay"]
    _, ay_gun = akim.ay_gunleri(w)
    Tc, Tw = T.min(0), T.max(0)
    gdd5 = (np.maximum(T - 5, 0) * ay_gun).sum(0)
    gdd0 = (np.maximum(T, 0) * ay_gun).sum(0)
    alfa = np.where(d["PE"] > 1, d["AET"] / np.maximum(d["PE"], 1), 1.0)
    return Tc, Tw, gdd5, gdd0, np.clip(alfa, 0, 1)


def siniflandir(Tc, Tw, gdd5, gdd0, alfa, buz, K=None):
    # bitki işlev tipleri (Prentice vd. 1992 Tablo 1)
    # Tropik eşiği BIOME1'de Tc >= 15.5 °C; burada Köppen A sınırı 18 °C
    # (27 Eylül, sahibi işaretli bölge: "iklim olarak çok az kısmı savan").
    # 15.5-18 °C'lik kışı ılık C iklimleri (Cwa, Cwb, Cfa) tropik sayılıp
    # savan çıkıyordu; atlasın iklim haritası oraya C diyor. Köppen'in 18 °C
    # sınırı da bitki örtüsünden türetilmişti (sıcak ister "megaterm" bitkiler).
    TROPIK = 18.0
    te = (Tc >= TROPIK) & (alfa >= 0.80)
    tr = (Tc >= TROPIK) & (alfa >= 0.45) & (alfa <= 0.95)
    wte = (Tc >= 5) & (alfa >= 0.65)
    ts = (Tc >= -15) & (Tc <= 15.5) & (gdd5 >= 1200) & (alfa >= 0.65)
    ctc = (Tc >= -19) & (Tc <= 5) & (gdd5 >= 900) & (alfa >= 0.65)
    bec = (Tc >= -35) & (Tc <= -2) & (gdd5 >= 350) & (alfa >= 0.75)
    bs = (Tc <= 5) & (gdd5 >= 350) & (alfa >= 0.65)
    ss = (Tc >= 5) & (alfa >= 0.28)
    wg = (Tw >= 22) & (alfa >= 0.18)
    cg = (gdd0 >= 500) & (alfa >= 0.33)
    cold = (gdd0 >= 100) & (alfa >= 0.33)
    hd = Tw >= 22
    cd = gdd0 >= 100
    k = np.full(Tc.shape, 15, np.uint8)          # varsayılan: kutup çölü
    # baskınlık sırası: aşağıdan yukarı yazılır, üstteki kural öncekini ezer
    k[cd] = 14
    k[hd] = 13
    k[cold] = 12
    k[cg & ~hd | cg & (Tw < 22)] = 11
    k[wg] = 10
    k[cg & wg & (Tc < 5)] = 11                   # soğuk kışlı sıcak yazlı otlak: bozkır
    k[ss] = 9
    k[bs] = 8
    k[bec] = 7
    k[ctc & ~bec] = 6                            # serin iğne yapraklı (ts'siz): karışık/iğne yapraklı
    # BIOME1: ılıman yaprak döken orman = yaz yeşil (ts) baskın; boreal iğne
    # yapraklı (bec) da yetişiyorsa serin karışık orman
    k[ts & bec] = 6
    k[ts & ~bec] = 5
    k[wte & ~te & ~tr] = 4
    k[wte & ts & (Tc < 5)] = 5
    k[tr & ~te] = 3
    k[tr & te] = 2
    k[te & ~tr] = 1
    # Köppen'le (motorun kendi sınıfı, aynı ızgarada) üç düzeltme, 27 Eylül
    # denetimi (sahibi: "savan çok mu oldu", "dünyamın bilgilerine uygun"):
    # 1) Tundra: BIOME1'in serin otu (GDD0 >= 500) Tw < 10 °C yerleri de
    #    kapsıyordu ve Köppen ET'nin yarısı bozkır çıkıyordu (GDD5 medyan 62,
    #    Tw 6.5 °C). En sıcak ay 10 °C altı ya da GDD5 < 350 ise tundra
    #    (Köppen'in ET sınırı ağaç sınırıdır; 350 BIOME1'in boreal ağaç eşiği).
    k[(k == 11) & ((Tw < 10) | (gdd5 < 350))] = 12
    if K is not None:
        Cs = np.isin(K, (8, 9, 10))
        # 2) BIOME1 yağışın ZAMANINA bakmaz: kışı ılık (Tc >= 15.5) Akdeniz
        #    ikliminde (Köppen Cs) kurak mevsim yaza düşer, sert yapraklılar
        #    baskındır: savan değil maki. Önceki sürüm Cs'yi kendi ölçütüyle
        #    arıyordu ve tropikte kurak mevsim en sıcak aylara denk geldiği
        #    için Aw'nin yarısını da maki yapıyordu; artık yalnız Köppen Cs.
        k[(k == 3) & Cs] = 9
        # 3) Sert yapraklı çalı Cs dışında (yağış yazın; BSh, kurak Cw):
        #    maki değil kurak çalılık ve dikenli savan (BIOME1'in "xerophytic
        #    woods/scrub" biyomu ikisini birlikte tutar).
        k[(k == 9) & ~Cs] = 10
        # 4) Köppen Am (muson iklimi) muson ormanıdır. Burada nem oranı
        #    düşük çıkıyor (Am medyan 0.74 < 0.80) çünkü motorun yağışı
        #    Dünya'nınkinin iki katı mevsimsel (CLAUDE.md §8): yağış birkaç
        #    ayda boşalıp akışa gidiyor. Am'de savan -> mevsimsel orman.
        k[(K == 2) & np.isin(k, (3, 10))] = 2
        # 5) Köppen f (her ay yağışlı: Cfa, Cfb, Df) kurak çalılık olamaz;
        #    nem oranı 0.65'in biraz altında kalan bu yerler ormandır (ılık
        #    kışlıysa yaprak dökmeyen, değilse yaprak döken).
        # 6) Kurak çalılık yalnız Köppen B'de (BS, BW). İklimi kurak olmayan
        #    (Cw, Dw) ama nem oranı ormana yetmeyen yerde (0.28-0.65) örtü
        #    kuru ağaçlık / açık ormandır (sahibi işaretli bölge, 27 Eylül:
        #    "iklim olarak çok az kısmı savan ama tamamen kurak bitki örtüsü").
        B = np.isin(K, (4, 5, 6, 7))
        k[(k == 10) & ~B & ~np.isin(K, (14, 15, 16, 25, 26, 27, 28))] = 16
        f = np.isin(K, (14, 15, 16, 25, 26, 27, 28))
        k[(k == 10) & f & (Tc >= 5)] = 4
        k[(k == 10) & f & (Tc < 5)] = 5
    k[buz] = 15
    return k


def main():
    iklim = os.path.join(KOK, "buzul", "_iklim_bugun025.npz")
    import uret
    w = uret.dunya_yukle()
    d = akim.hesapla(iklim)
    Tc, Tw, gdd5, gdd0, alfa = degiskenler(d, w)
    from motor import koppen
    K = koppen.classify(d["Tay"], d["Pay"])
    k = siniflandir(Tc, Tw, gdd5, gdd0, alfa, d["buzul"], K)
    z, lat, lon = d["z"], d["lat"], d["lon"]
    su = np.load(os.path.join(KOK, "su", "_su.npz"))
    gol = np.isfinite(su["sev"])
    kara = (z >= 0) & ~gol
    k[~kara] = 0
    # alan ağırlıklı paylar
    wgt = np.cos(np.radians(lat))[:, None] * kara
    pay = {int(c): float(wgt[k == c].sum() / wgt.sum()) for c in BIYOM}
    for c, (ad, *_r) in BIYOM.items():
        print("%2d %-38s %%%5.1f" % (c, ad, 100 * pay[c]))
    # uygulama: R = biyom kodu, G = alfa*200, B = Tc+100 (°C), kara kutusuna
    # kırpılmış, kaynak ızgaranın 2 katı çözünürlükte (~0.044°; sahibi 27 Eylül:
    # "piksel piksel, bulanık"). Sınıflar yumuşak argmax ile büyütülür (her
    # sınıfın göstergesi ara değerlenip hafif yumuşatılır, en büyüğü seçilir):
    # merdiven sınırlar yuvarlanır, yeni sınıf uydurulmaz. Kıyı ve göl
    # kıyısı yükseklik ve göl maskesinin ara değerlemesinden.
    from scipy import ndimage
    F = 2
    ii, jj = np.where(kara)
    i0, i1, j0, j1 = ii.min(), ii.max() + 1, jj.min(), jj.max() + 1
    kc = k[i0:i1, j0:j1]
    en = None; secim = None
    for c in np.unique(kc):
        if c == 0:
            continue
        g = ndimage.gaussian_filter(ndimage.zoom((kc == c).astype(np.float32), F, order=1), 0.9)
        if en is None:
            en = g; secim = np.full(g.shape, c, np.uint8)
        else:
            b = g > en; en[b] = g[b]; secim[b] = c
    zc = ndimage.zoom(z[i0:i1, j0:j1].astype(np.float32), F, order=1)
    gc = ndimage.zoom(gol[i0:i1, j0:j1].astype(np.float32), F, order=1)
    secim[(zc < 0) | (gc >= 0.5)] = 0
    # alfa ve Tc: denizi en yakın kara değeriyle doldurup ara değerle
    _, (yi, xi) = ndimage.distance_transform_edt(~kara[i0:i1, j0:j1], return_indices=True)
    doldur = lambda a: ndimage.zoom(a[i0:i1, j0:j1][yi, xi].astype(np.float32), F, order=1)
    # Görüntü paletli PNG (indeks = biyom kodu, palet = biyom rengi): tarayıcı
    # renkleri doğrudan çözer, uygulamada piksel döngüsü gerekmez (ilk açılış
    # CPU x4'te ~0.9 s idi). Kartın okuduğu değerler ayrı, kaynak
    # çözünürlükte bitki_veri.png'de (R = kod, G = alfa*200, B = Tc+100).
    im = Image.fromarray(secim, "P")
    pal = [12, 24, 34] * 256
    for c, (_a, _n, _o, r) in BIYOM.items():
        pal[3 * c:3 * c + 3] = list(r)
    im.putpalette(pal)
    im.save(os.path.join(KOK, "data", "bitki.png"), optimize=True, transparency=0)
    veri_rgb = np.stack([kc, np.round(alfa[i0:i1, j0:j1] * 50) * 4, np.clip(np.round(Tc[i0:i1, j0:j1] + 100), 0, 255)], -1).astype(np.uint8)
    Image.fromarray(veri_rgb, "RGB").save(os.path.join(KOK, "data", "bitki_veri.png"), optimize=True)
    rgb = secim
    dl, dn = lat[1] - lat[0], lon[1] - lon[0]
    kesit = [float(lon[j0] - dn / 2), float(lat[i1 - 1] + dl / 2), float(lon[j1 - 1] + dn / 2), float(lat[i0] - dl / 2)]
    veri = dict(ne="Dünyam doğal bitki örtüsü (bitki/bitki.py); yöntem BITKI.md",
                kesit=kesit, kodlar="bitki.png: paletli, indeks = biyom kodu (0 boş), 2 kat çözünürlük; bitki_veri.png: kaynak çözünürlük, R = biyom kodu, G = alfa*200, B = en soğuk ay + 100 °C (ikisi aynı kesit)",
                biyomlar={str(c): dict(ad=a, ne=n, ornek=o, renk=list(r), pay=round(pay[c], 4)) for c, (a, n, o, r) in BIYOM.items()})
    with open(os.path.join(KOK, "data", "bitki.json"), "w", encoding="utf-8") as fh:
        json.dump(veri, fh, ensure_ascii=False, indent=1)
    np.savez_compressed(os.path.join(BURASI, "_bitki.npz"), k=k, Tc=Tc.astype(np.float32), Tw=Tw.astype(np.float32),
                        gdd5=gdd5.astype(np.float32), gdd0=gdd0.astype(np.float32), alfa=alfa.astype(np.float32), lat=lat, lon=lon)
    print("bitki.png %dx%d %.0f KB, bitki_veri.png %.0f KB" % (rgb.shape[1], rgb.shape[0], os.path.getsize(os.path.join(KOK, "data", "bitki.png")) / 1024,
                                                           os.path.getsize(os.path.join(KOK, "data", "bitki_veri.png")) / 1024))


if __name__ == "__main__":
    main()
