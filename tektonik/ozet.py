# -*- coding: utf-8 -*-
"""Levha modelinin kendi basina anlasilir ozeti: OZET.md (insan / baska yapay zeka) ve
ozet.json (makine). Modelden uretilir; harita ya da hikaye degisince yeniden kos:
    python tektonik/ozet.py
Hikayenin tamami (donemler, olaylar) tektonik/HIKAYE.md'de; bu ozet levhalari,
sinirlari ve Bird siniflarini modelden yazar.
"""
import json, os, sys
from collections import defaultdict
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import levhalar as M  # noqa: E402

D = os.path.join(M.KOK, "tektonik")
YON = ["kuzeye", "kuzeydoğuya", "doğuya", "güneydoğuya", "güneye", "güneybatıya", "batıya", "kuzeybatıya"]
def yon(v):
    return YON[int(round((np.degrees(np.arctan2(v[0], v[1])) % 360) / 45)) % 8]
AMAC = {frozenset(s["levhalar"]): s for s in json.load(open(os.path.join(M.KAYNAK, "sinirlar_hikaye.json"), encoding="utf-8"))}
YER_TUTUCU = {"Batı Okyanusu Levhası", "Kutup Levhası", "Güney Okyanusu Levhası", "Büyük Okyanus Levhası"}

def tur(ad):
    k = M.LEVHALAR[ad]["kimlik"]
    if k == 11: return "okyanus (atlasın kendi levhası)"
    if k >= 7: return "okyanus"
    return "kıta + okyanus" if M.levhalar_json_kara(ad) > 0.02 else "okyanus"

OLAYLAR = [
    ("3400-2500 MYÖ", "Kalkanların doğuşu: Ak Kalkan (1'in kuzeyi), Boz Kalkan (2'nin doğusu), Kır Çekirdeği (2'nin batısı), Kızıl Kalkan (3'ün ortası)."),
    ("2100-1700 MYÖ", "Kaynak orojenleri: Kır Çekirdeği ile Boz Kalkan birleşir; 2'nin içi tek parça olur."),
    ("1150-750 MYÖ", "İlk Birlik süper kıtası; 1'in batısında Ulu Dağlar. Parçalanınca 1 ile 2 arasında Ata Okyanusu açılır."),
    ("750-520 MYÖ", "İki büyük buzullaşma; Ata Okyanusu kıyılarında kalın çökeller."),
    ("520-400 MYÖ", "Mavi orojeni: Ata Okyanusu kapanır, 430 MYÖ'de 1 ile 2 çarpışır (Mavi Dağlar, Kaledonya benzeri)."),
    ("400-290 MYÖ", "Köz orojeni: Güney Kıtası çarpar, 4'ün temeli kıvrılır; Büyük Birlik. Doğuda Mor Okyanusu kaması açık kalır."),
    ("290-200 MYÖ", "İnce Şerit Güney Kıtası'ndan kopup 210 MYÖ'de 2'nin güneyine yapışır; 252 MYÖ Kuzey Tuzakları."),
    ("200-130 MYÖ", "Büyük Birlik parçalanır: Batı ve Güney okyanusları açılır; 3, 5 ve 7'yi taşıyan Doğu Parça kuzeye yola çıkar."),
    ("130-85 MYÖ", "Makas açılması: 4 ve 6, 1'den ayrılıp ~29° saat yönünde döner; iç denizin batısı açılır, Köprü Dağları başlar."),
    ("85-50 MYÖ", "Kuzeye koşu: Doğu Parça yılda ~6,5 cm ilerler; 66 MYÖ Kızıl Basamaklar; Doğu Okyanusu 3'ün altına dalmaya başlar."),
    ("50-25 MYÖ", "Mor çarpışması: 3, 2'nin altına girer (Mor Sıradağları, Şerit Yaylası); Tuzak Çanağı kalkar; doğu iç deniz kuşatılır."),
    ("25-2,6 MYÖ", "İç deniz evresi: Ada Hendeği, 6 güneye çekilir; 5 kopar ve 8 MYÖ'de 4'e çarpar (Sarı Sıradağları); 7 Kanal Fayı boyunca kayar; 3 MYÖ Köprü Kıstağı kapanır."),
    ("2,6-0 MYÖ", "Buzul çağları; bugün iki etkin çarpışma (3 ile 2, 5 ile 4), bir yanal fay, bir yay ardı gerilmesi, bir yarık."),
]

def _sinir_maske(a, b):
    i, j = M.LEVHALAR[a]["kimlik"], M.LEVHALAR[b]["kimlik"]
    A = M.kimlik == i; B = M.kimlik == j
    return (A & ndimage.binary_dilation(B)) | (B & ndimage.binary_dilation(A))

def daglar():
    """adlandirilmis yer sekilleri: en yuksek nokta arazide olculur"""
    out = []
    km_hucre = M.RKM * np.radians(180 / M.H)
    def tepe(maske, ad, benzer, koken):
        if not maske.any(): return
        z = np.where(maske, M.e, -1); r, c = np.unravel_index(np.argmax(z), z.shape)
        out.append((ad, (round(float(M.lat[r]), 1), round(float(M.lon[c]), 1)), int(round(z[r, c])), benzer, koken))
    yakin = lambda a, b, km: ndimage.distance_transform_edt(~_sinir_maske(a, b)) * km_hucre < km
    lv = lambda ad: M.kimlik == M.LEVHALAR[ad]["kimlik"]
    tepe(M.land & yakin("Kuzey Levhası", "Doğu Dil Levhası", 400) & lv("Kuzey Levhası"), "Mor Sıradağları", "Kafkas ölçeğinde Himalaya benzeri",
         "3, 2'nin altına giriyor (50 MYÖ'den beri); arkasında ~1 km'lik Şerit Yaylası.")
    tepe(M.land & yakin("Kuzey Levhası", "Orta Blok", 300), "Sarı Sıradağları", "Zagros / Tayvan benzeri",
         "5, 4'ün altına giriyor (8 MYÖ'den beri); genç, dik, en yüksek güney orta kesim.")
    tepe(M.land & yakin("Doğu Dil Levhası", "Doğu Okyanusu Levhası", 450) & lv("Doğu Dil Levhası"), "Doğu Yay Dağları", "And benzeri yay",
         "Doğu Okyanusu, Doğu Hendeği'nde 3'ün altına dalıyor.")
    tepe(M.land & lv("Uzun Yarımada Bloğu"), "Uzun Yarımada sırtı", "Ölü Deniz fayı kıyısı",
         "7, 5'e bastırarak kuzeybatıya kayıyor; dar, dik sırt.")
    tepe(M.land & lv("Ada Bloğu"), "İç denizdeki ada (6)", "Ege / Tiren benzeri",
         "Yay ardı gerilmesi: parmak biçimli horst ve grabenler; Ada Hendeği güneyinde.")
    out.append(("Köprü Kıstağı", (25.2, -27.7), 400, "Panama benzeri", "3 MYÖ'de 1 ile 4 arasındaki boğazı kapattı; 80-400 m."))
    return out

def cumle(sinif, cift, ust, yak):
    a, b = cift; r = abs(yak)
    if sinif in ("SUB", "OCB"):
        alt = b if ust == a else a; return "%s, %s altına dalıyor (%.1f cm/yıl)." % (alt, ust, r)
    if sinif == "CCB":
        alt = b if ust == a else a; return "%s, %s levhasına çarpıyor, altına giriyor (%.1f cm/yıl)." % (alt, ust, r)
    if sinif in ("OSR", "CRB"): return "%s ile %s birbirinden ayrılıyor (%.1f cm/yıl)." % (a, b, r)
    if sinif in ("OTF", "CTF"): return "%s ile %s yan yana kayıyor." % (a, b)
    return "hareket yok denecek kadar az."

def uret():
    o = M.yaz()
    M.levhalar_json_kara = lambda ad: o["levhalar"][ad]["kara_payi"]
    kom = defaultdict(float)
    for a in M.ADIMLAR: kom[tuple(sorted((a["sol"], a["sag"])))] += a["km"]
    lev = []
    for ad in M.ADLAR:
        L = M.LEVHALAR[ad]; v = np.array(L["hiz"]); j = o["levhalar"][ad]
        komsu = sorted({b for (a, b) in kom if a == ad} | {a for (a, b) in kom if b == ad})
        lev.append({"kimlik": L["kimlik"], "ad": ad, "tur": tur(ad), "kapsam": L["kapsam"], "alan_milyon_km2": j["alan_milyon_km2"],
                    "kara_payi": j["kara_payi"], "tohum_enlem_boylam": L["tohum"], "hiz_cm_yil": round(float(np.hypot(*v)), 2),
                    "yon": (yon(v) if np.hypot(*v) > 0.05 else "sabit (çerçeve)") + (" (dönerek)" if ad in M.DONME else ""),
                    "euler_kutbu": j["euler_kutbu"], "euler_hizi_derece_My": j["euler_hizi_derece_My"], "komsular": komsu,
                    "yer_tutucu": ad in YER_TUTUCU})
    grup = defaultdict(list)
    for a in M.ADIMLAR: grup[(a["sinir"], tuple(sorted((a["sol"], a["sag"]))))].append(a)
    sin = []
    for (ad, cift), ad_ in sorted(grup.items(), key=lambda x: -sum(a["km"] for a in x[1])):
        km = sum(a["km"] for a in ad_); sc = defaultdict(float)
        for a in ad_: sc[a["sinif"]] += a["km"]
        bas = max(sc, key=sc.get); yak = sum(a["yaklasma"] * a["km"] for a in ad_) / km
        ust = defaultdict(float)
        for a in ad_:
            if a["ust"]: ust[a["ust"]] += a["km"]
        pts = [ad_[0]["p"]] + [a["q"] for a in ad_]; nk = pts[::max(1, len(pts) // 12)] + [pts[-1]]
        u_ = max(ust, key=ust.get) if (ust and bas in ("SUB", "OCB", "CCB")) else None
        goruntu_km = sum(a["km"] for a in ad_ if a["goruntude"])
        am = AMAC.get(frozenset(cift))
        tasarim = goruntu_km < 0.5 * km
        ad_uzun = (am["aciklama"].split(":")[0] if (am and am["aciklama"]) else " / ".join(cift))
        not_ = ("[tasarım] " if tasarim else "") + cumle(bas, cift, u_, yak) + \
               (" Hikâyede: %s, %s." % (am["tur"], am["aciklama"]) if (am and not tasarim and am["aciklama"]) else
                (" Hikâyede: %s." % am["tur"] if (am and not tasarim) else ""))
        sin.append({"sinir": ad, "ad": ad_uzun, "levhalar": list(cift), "uzunluk_km": round(km), "hikayede_cizili_km": round(goruntu_km),
                    "baskin_sinif": bas, "sinif_paylari": {k: round(v / km, 2) for k, v in sorted(sc.items(), key=lambda x: -x[1])},
                    "ort_yaklasma_cm_yil": round(yak, 2), "ust_levha": u_, "amaclanan_tur": am["tur"] if am else None,
                    "anlam": not_, "kaba_iz_enlem_boylam": [[round(p[0], 1), round(p[1], 1)] for p in nk]})
    DG = daglar()
    J = {"ne": "Dünyam (kurgusal gezegen) levha tektoniği özeti, 23 Kasım hikâyesi (tektonik/HIKAYE.md). "
               "Kıta levhaları sahibin levha kimliği görüntüsünden; uzak okyanus levhaları atlasın gezegen ölçekli modelinden.",
         "gezegen": {"yaricap_km": M.RKM, "gun_saat": M.w.rotation_period_h, "eksen_egikligi_derece": M.w.axial_tilt_deg,
                     "kara": "tek kıta, yaklaşık 60°K..7°G ve 47°B..43°D; karanın ~%7'si, gerisi okyanus"},
         "kurallar": {"koordinat": "enlem kuzey +, boylam doğu + (−180..180), derece",
                      "hiz": "cm/yıl, Kuzey Levhası sabit kabul edilir (göreli çerçeve)",
                      "sinif_olcutu": "Bird (2003) PB2002: göreli hız sınıra 20°'den yakınsa yanal, değilse yaklaşma/ayrılma; iki yanı denizse okyanusal",
                      "ust_levha": "dalma/çarpışmada: kıta tarafı; ikisi de aynıysa levha sırası"},
         "siniflar": M.SINIF_AD, "levhalar": lev, "sinirlar": sin, "amaclanan_tur_karsilastirma": o["amaclanan_tur_karsilastirma"],
         "dag_ve_yer_sekilleri": [{"ad": a, "enlem_boylam": p, "yukseklik_m": h, "gercek_benzeri": g, "koken": k} for a, p, h, g, k in DG],
         "tarih_eskiden_yeniye": [{"donem": d, "olay": t} for d, t in OLAYLAR],
         "dosyalar": {"HIKAYE.md": "hikâyenin tamamı: dönemler, olaylar (sahibin)",
                      "levha_dunya.png": "tüm gezegen, Equal Earth", "levha_kure.png": "iki küre görünümü",
                      "levha_haritasi.png": "kıta ayrıntısı, zaman çizelgesi",
                      "sinirlar.geojson": "her sınır adımı bir LineString; özellikler: sinir, sol, sag, sinif, ust, yaklasma, yanal, km, goruntude",
                      "levha_kimlik.png": "kaynak çözünürlüğünde ızgara (4096×2048, satır 0 = 90°K), değer = levha kimliği",
                      "levhalar.json": "levha alanları, Euler kutupları, amaçlanan türle karşılaştırma",
                      "kaynak/": "sahibin girdileri (levha_kimlik_8k.png, levhalar_hikaye.json, sinirlar_hikaye.json), 16k kaydı, uzak okyanus levhaları",
                      "TEKTONIK.md": "kararların tarihçesi (eski hikâye geçersiz işaretli)"}}
    json.dump(J, open(os.path.join(D, "ozet.json"), "w"), ensure_ascii=False, indent=1)
    # ---------------- OZET.md
    L = []
    L += ["# Dünyam levha tektoniği — özet", "",
          "Bu belge kendi başına okunacak biçimde yazıldı (başka bir kişi ya da yapay zekâ sohbeti için). "
          "Aynı bilgi makine için `ozet.json`'da. Hikâyenin tamamı `HIKAYE.md`'de, kararların tarihçesi `../TEKTONIK.md`'de. "
          "Belge `tektonik/ozet.py` ile modelden üretilir; elle düzenleme, betiği koş.", "",
          "## 1. Kısaca", "",
          "Dünyam kurgusal bir gezegen: yarıçap %.0f km, gün %g saat, eksen eğikliği %g°. Tek bir kıtası var "
          "(yaklaşık 60°K ile 7°G, 47°B ile 43°D arası); gerisi okyanus. Kıta yedi parçadan oluşur ve bugün iki çarpışma etkindir: "
          "3, 2'nin altına giriyor (Mor Sıradağları); 5, 4'ün altına giriyor (Sarı Sıradağları). 3 milyon yıl önce 1 ile 4 arasındaki "
          "boğaz Köprü Kıstağı ile kapandı. Eski hikâyenin adları (Duvar, Alt Kıta, İber, Ege, Yarımada, Güneybatı, And tipi batı çarpışması) "
          "geçersizdir." % (M.RKM, M.w.rotation_period_h, M.w.axial_tilt_deg), "",
          "![tüm gezegen](levha_dunya.png)", "",
          "## 2. Okuma kuralları", "",
          "- Koordinat: enlem kuzey +, boylam doğu + (−180..180), derece.",
          "- Hız: cm/yıl, **Kuzey Levhası sabit** kabul edilir; diğer hızlar ona göredir (sahibin `kaynak/levhalar_hikaye.json`'u).",
          "- Kıta levhaları (1-7) sahibin levha kimliği görüntüsünden kayıtla enlem ve boylama çevrildi. Kıta ile uzak sırtlar arasındaki "
          "okyanus en yakın kıta levhasına verildi (edilgen kenar). Batı Okyanusu, Kutup ve Güney Okyanusu levhaları hikâyede yer tutucu; "
          "yerleri atlasın eski gezegen ölçekli modelinden (sırtlar aynı), Büyük Okyanus Levhası yalnız atlasta var.",
          "- Sınır türü elle yazılmadı: her ~55 km'lik sınır adımında iki levhanın göreli hızından hesaplandı "
          "(Bird 2003, PB2002 ölçütü): göreli hız sınıra 20°'den yakınsa **yanal**, değilse **yaklaşma** ya da **ayrılma**; "
          "iki yanı denizse okyanusal, değilse kıtasal. Hikâyedeki amaçlanan türle karşılaştırma bölüm 5'te.",
          "- [tasarım] işaretli sınırlar sahibin görüntüsünde yok: görüntü çerçevesinin dışındaki uzantılar ya da uzak okyanus sınırları.", "",
          "| kısaltma | anlamı |", "|---|---|"]
    L += ["| %s | %s |" % (k, v) for k, v in M.SINIF_AD.items()]
    L += ["", "## 3. Levhalar", "", "| no | levha | tür | kapsam | alan (milyon km²) | kara payı | hareket (Kuzey'e göre) | komşular |", "|---|---|---|---|---|---|---|---|"]
    for x in lev:
        L.append("| %d | %s%s | %s | %s | %.1f | %%%d | %s | %s |" % (x["kimlik"], x["ad"], " (yer tutucu)" if x["yer_tutucu"] else "", x["tur"], x["kapsam"],
                 x["alan_milyon_km2"], round(100 * x["kara_payi"]), ("%s %.1f cm/yıl" % (x["yon"], x["hiz_cm_yil"])) if x["hiz_cm_yil"] > 0.05 else x["yon"],
                 ", ".join(x["komsular"])))
    L += ["", "## 4. Sınırlar", "", "Uzunluğa göre sıralı; 150 km'den kısa parçalar tabloda yok (hepsi `ozet.json`'da). 'yaklaşma' artıysa levhalar "
          "birbirine yaklaşıyor, eksiyse ayrılıyor. Aynı levha çifti birden çok parçaya bölünmüşse her parça ayrı satır.", "",
          "| sınır | arasındaki levhalar | baskın tür (Bird) | uzunluk (km) | yaklaşma (cm/yıl) | üst levha | anlamı |", "|---|---|---|---|---|---|---|"]
    for x in sin:
        if x["uzunluk_km"] < 150: continue
        L.append("| %s | %s | %s (%%%d) | %d | %+.1f | %s | %s |" % (x["ad"], " / ".join(x["levhalar"]), M.SINIF_AD[x["baskin_sinif"]],
                 round(100 * x["sinif_paylari"][x["baskin_sinif"]]), x["uzunluk_km"], x["ort_yaklasma_cm_yil"], x["ust_levha"] or "—", x["anlam"]))
    L += ["", "## 5. Amaçlanan tür ile Bird sınıfı", "",
          "Sahibin `sinirlar_hikaye.json`'undaki tür ile yeni hızlardan hesaplanan Bird sınıfı, levha çifti başına; yalnız sahibin görüntüsünde "
          "çizili kesimler sayıldı ('görüntüde km'), görüntü dışındaki uzantı ayrı. 'uyum' = amaçlanan türe uyan sınıfların uzunluk payı "
          "(kıta çarpışmasında CCB ve kıyı kesimindeki SUB uyar). Hikâyenin kuralı: ayrılırsa **tablo esas alınır**, fark not edilir.", "",
          "| levhalar | amaçlanan | Bird baskın | uyum | görüntüde km | dışarıda km | sınıf payları |", "|---|---|---|---|---|---|---|"]
    for x in o["amaclanan_tur_karsilastirma"]:
        L.append("| %s | %s | %s | %s | %d | %d | %s |" % (" / ".join(x["levhalar"]), x["amac"], M.SINIF_AD.get(x["bird"], "—") if x["bird"] else "— (yer tutucu, çizilmedi)",
                 ("%%%d" % round(100 * x["uyum"])) if x["uyum"] is not None else "—", x["km"], x["disarida_km"],
                 ", ".join("%s %%%d" % (k, round(100 * v)) for k, v in x["paylar"].items()) or "—"))
    L += ["", "## 6. Dağlar ve yer şekilleri (kıta)", "", "![kıta](levha_haritasi.png)", "",
          "En yüksek noktalar araziden ölçüldü (sınırın 300-450 km'si içinde ya da levhanın karasında).", "",
          "| ad | yer (enlem, boylam) | yükseklik (m) | gerçek benzeri | kökeni |", "|---|---|---|---|---|"]
    for a, p, h, g, k in DG:
        L.append("| %s | %.1f, %.1f | %d | %s | %s |" % (a, p[0], p[1], h, g, k))
    L += ["", "## 7. Tarih (eskiden yeniye)", "", "Ayrıntı ve tek tek olaylar `HIKAYE.md`'de.", ""]
    L += ["%d. **%s**: %s" % (i + 1, d, t) for i, (d, t) in enumerate(OLAYLAR)]
    L += ["", "## 8. Açık kararlar", "",
          "- Uzak okyanus levhalarının (8-11) yeri ve Büyük Okyanus'un hızı tasarım; hikâyede yer tutucu.",
          "- Kaçış Bloğu (2'nin güneydoğu köşesi, doğuya 1,2 cm/yıl) çok küçük olduğu için levha haritasında yok (hikâye kararı).",
          "- Doğu Dil Levhası dönerek ilerliyor (doğu ucu ~2,4, batı ucu ~1,2 cm/yıl); modelde Euler vektörüne 0,3°/My dönme eklendi.", "",
          "## 9. Dosyalar", ""]
    L += ["- `%s`: %s" % (k, v) for k, v in J["dosyalar"].items()]
    open(os.path.join(D, "OZET.md"), "w").write("\n".join(L) + "\n")
    print("yazildi: OZET.md, ozet.json;", len(sin), "sinir grubu")

if __name__ == "__main__":
    uret()
