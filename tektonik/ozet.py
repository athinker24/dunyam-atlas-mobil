# -*- coding: utf-8 -*-
"""Levha modelinin kendi basina anlasilir ozeti: OZET.md (insan / baska yapay zeka) ve
ozet.json (makine). Modelden uretilir; harita degisince yeniden kos:
    python tektonik/ozet.py
"""
import json, os, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import levhalar as M  # noqa: E402

D = os.path.join(M.KOK, "tektonik")
YON = ["kuzeye", "kuzeydoğuya", "doğuya", "güneydoğuya", "güneye", "güneybatıya", "batıya", "kuzeybatıya"]
def yon(v):
    return YON[int(round((np.degrees(np.arctan2(v[0], v[1])) % 360) / 45)) % 8]
TUR = {"Kuzey": "kıta + okyanus", "Kuzeydoğu": "kıta (küçük)", "İber": "kıta (küçük)", "Ege": "kıta parçaları + deniz (mikro)",
       "Güneybatı": "kıta + okyanus", "Yarımada": "kıta (mikro)", "Alt Kıta": "kıta + okyanus", "Batı Okyanusu": "okyanus (üstünde küçük kıta)",
       "Doğu Okyanusu": "okyanus", "Büyük Okyanus": "okyanus", "Uzak Okyanus": "okyanus", "Kuzey Kutup": "okyanus", "Güney Kutup": "okyanus"}
ANLAM = {
    "duvar": "Büyük çarpışma cephesi: Alt Kıta kuzeye, Kuzey levhasının altına giriyor (Himalaya benzeri). Duvar dağları (3) bunun ürünü.",
    "pireneler": "İber bloğu kuzeye, Kuzey levhasına çarpmış; 5 dağları (Pireneler benzeri).",
    "alpler": "Yarımada batıya, Güneybatı bloğuna çarpıyor; 4 dağları (Alpler benzeri). Yarımada üst levha.",
    "bati_cukur": "Batı Okyanusu, Güneybatı bloğunun altına dalıyor (And tipi); kıyıda volkanlar.",
    "alti": "Batı Okyanusu'nun taşıdığı küçük kıta Güneybatı bloğuna çarpıyor (6, etkin); güneyinde okyanusal dalma.",
    "ege_cukur": "İç deniz tabanı (Güneybatı levhası) kuzeye, Ege'nin altına dalıyor; adaların güneyinde volkan yayı.",
    "ege_dogu": "Ege ile Alt Kıta arası, çoğunlukla yanal (Alt Kıta kuzeye, Ege güneye).",
    "ege_kuzey": "Ege güneye çekilirken arkasında açılan yay ardı yarığı (iç denizin kuzeyi).",
    "ege_bati": "Ege ile İber arası, çoğunlukla yanal.",
    "bogaz": "İber ile Güneybatı arası boğaz; yavaş yakınlaşma (Cebelitarık benzeri).",
    "iber_bati": "İber bloğunun batı kıyısı, yanal.",
    "yar_kuzey": "Yarımadanın kuzeyi, yanal; kuzeyindeki körfez Tiren benzeri gerilme havzası.",
    "yar_dogu": "Yarımada ile Alt Kıta arası boğaz: açılan yarık (yarımada Alt Kıta'dan kopuyor).",
    "yar_guney": "Yarımadanın güneyi, çoğunlukla yanal.",
    "gb_altkita": "Güneybatı ile Alt Kıta arası, yanal.",
    "gb_altkita_guney": "Güneye uzanan yanal fay: iki levha aynı yönde farklı hızla kuzeye gidiyor.",
    "dogu_cukur": "Doğu Okyanusu batıya, Alt Kıta'nın altına dalıyor; doğudaki yarımada volkan yayı.",
    "duvar_dogu": "Duvar'ın doğu ucu, kıyıya kadar.",
    "kuzey_dogu": "Doğu Okyanusu, Kuzey ve Kuzeydoğu levhalarının altına dalıyor.",
    "kd_bati": "Kuzeydoğu kaçış bloğunun batı sınırı (9): blok doğuya giderken açılan Baykal tipi yarık.",
    "kd_kuzey": "Kaçış bloğunun kuzey sınırı (2 dağları), çoğunlukla yanal.",
    "kd_guney": "Kaçış bloğunun güney sınırı (Duvar'ın kuzey eteği), yanal.",
    "kuzey27": "27°K boyunca uzun dönüşüm fayı: Batı Okyanusu doğuya kayıyor.",
    "bati_sirt": "Batı okyanus ortası sırtı (Atlas ortası sırtı benzeri, S biçimli).",
    "dogu_sirt": "Doğu okyanus ortası sırtı.",
    "orta_cukur": "Uzak Okyanus batıya, Büyük Okyanus'un altına dalıyor (Pasifik batısı benzeri ada yayları).",
    "guney_sirt": "Kıtanın güneyinden geçen sırt (Hint Okyanusu güneyi benzeri).",
    "guney_sirt2": "Güneydoğu sırtı.", "guney_sirt3": "Uzak güney sırtı.", "guney_sirt3b": "Uzak güney sırtı.",
    "kuzey_halka": "Kuzey Kutup levhasının sınırı; çoğu yerde güneydeki okyanus levhaları onun altına dalıyor."}
DAGLAR = [
    ("1", "Kuzey batı kolu", (51.8, -2.2), 7000, "Pamir", "Dünyanın en yüksek noktası. Çarpan Alt Kıta'nın kuzeybatı köşesinde sıkışan düğüm."),
    ("2", "Kuzeydoğu kıyı sırası", (55.2, 30.2), 6760, "Altay", "Kaçış bloğunun kuzey sınırı; çarpışmanın uzak etkisi."),
    ("3", "Duvar", (39.0, 20.0), 6729, "Himalaya", "~11.400 km'lik çarpışma kuşağı; güneyinde önülke ovası (Ganj benzeri)."),
    ("9", "Plato doğusu sırası", (47.3, 26.5), 4683, "Tanrı Dağları + Baykal", "Önce sıkışmayla yükseldi; bugün doğu eteğinde yarık açılıyor."),
    ("plato", "Plato çanağı", (46.4, 10.1), 880, "Tarım / Moğol platosu", "3,8 milyon km², kıvrılmamış sert eski blok; bozkır."),
    ("5", "İber kuzey sırası", (46.5, -26.3), 6563, "Pireneler", "İber bloğunun kuzeye çarpmasıyla."),
    ("meseta", "İber yaylası", (43.0, -22.0), 535, "Meseta (İspanya)", "Çok eski dağların aşınmış kökleri; düz yayla."),
    ("4", "Yay biçimli sıra", (10.9, -13.9), 6706, "Alpler", "Yarımadanın batıya çarpmasıyla; iç bükeyinde Po benzeri ova (8,6°K −10,3°)."),
    ("yarımada", "Yarımada omurgası", (6.8, -4.4), 5143, "Apeninler / İtalya", "Alt Kıta'nın kopan çıkıntısı."),
    ("10", "Güneybatı platosu", (12.3, -32.1), 4621, "Altiplano / And", "Küçük kıtanın altına sokulmasıyla kalınlaşan kabuk; ort. 2.278 m."),
    ("6", "Güney çarpışma noktası", (1.5, -19.2), 5924, "St. Elias (Alaska)", "Küçük kıtanın hâlâ çarptığı yer; en keskin kesim."),
    ("küçük kıta", "Güneybatı düz yarımada", (-2.0, -30.0), 712, "Zelandia", "Batı Okyanusu'nun taşıdığı hafif kıta parçası; 1,13 milyon km², düz."),
    ("7", "Alt Kıta doğu kıyısı sırası", (14.0, 14.6), 5892, "Pontidler", "Doğudaki dalmanın eski kenarı; doğusundaki körfez Karadeniz benzeri."),
    ("8", "Alt Kıta batı kıyısı sıraları", (15.0, 4.0), 5594, "Batı Anadolu / Ege", "Kısa, dik parçalar; aralarında denize açılan çöküntü vadileri (gerilme)."),
    ("11", "Alt Kıta orta kuşağı", (12.3, 10.5), 3488, "Kırşehir / İzmir-Ankara kenedi", "En eski kuşak: Alt Kıta'nın iki parçasının dikişi; aşınmış."),
    ("takımada", "İç deniz takımadası", (25.0, -12.0), 6443, "Yunanistan / Ege adaları", "Güneye çekilip gerilen kabuk; en yüksek nokta büyük bir volkan."),
]
OLAYLAR = [
    ("çok eski", "İber bloğunun eski dağları aşındı (Meseta). Alt Kıta'nın iki parçası kaynaştı, 11 yükseldi."),
    ("eski", "Alt Kıta'nın doğusunda dalma; 7 yükseldi, sonra Karadeniz benzeri körfez açılıp doğudaki yarımadayı kopardı. Batıda And tipi dalma, 10 kuşağı başladı."),
    ("büyük yakınlaşma", "Güneydeki bütün parçalar kuzeye yürüdü (Tetis kapanışı benzeri): Alt Kıta Duvar'a çarptı (1, 2, 3, plato); İber bloğu çarptı (5); yarımada batıya savrulup 4'ü yükseltti; küçük kıta batıdan geldi, plato 10 kabardı."),
    ("kaçış", "Kuzeydoğu bloğu çarpışmanın basıncıyla doğuya itildi; arkasında (9) Baykal tipi yarık açıldı."),
    ("bugün", "İç deniz levhası geri çekiliyor (takımada, Ege, Tiren gerilir); 6'da çarpışma sürüyor; Kuzey Anadolu benzeri fay, doğu ve batı dalmaları etkin."),
]

TASARIM = {"bati_sirt", "dogu_sirt", "orta_cukur", "guney_sirt", "guney_sirt2", "guney_sirt3", "guney_sirt3b", "kuzey_halka", "kuzey27"}
def cumle(sinif, cift, ust, yak):
    a, b = cift; r = abs(yak)
    if sinif in ("SUB", "OCB"):
        alt = b if ust == a else a; return "%s, %s levhasının altına dalıyor (%.1f cm/yıl)." % (alt, ust, r)
    if sinif == "CCB":
        alt = b if ust == a else a; return "%s, %s levhasına çarpıyor, altına giriyor (%.1f cm/yıl)." % (alt, ust, r)
    if sinif in ("OSR", "CRB"): return "%s ile %s birbirinden ayrılıyor (%.1f cm/yıl)." % (a, b, r)
    if sinif in ("OTF", "CTF"): return "%s ile %s yan yana kayıyor." % (a, b)
    return "hareket yok denecek kadar az."

def uret():
    o = M.yaz()
    kom = defaultdict(float)
    for a in M.ADIMLAR: kom[tuple(sorted((a["sol"], a["sag"])))] += a["km"]
    lev = []
    for ad, L in M.LEVHALAR.items():
        v = np.array(L["hiz"]); j = o["levhalar"][ad]
        komsu = sorted({b for (a, b) in kom if a == ad} | {a for (a, b) in kom if b == ad})
        lev.append({"ad": ad, "tur": TUR[ad], "alan_milyon_km2": j["alan_milyon_km2"], "kara_payi": j["kara_payi"],
                    "tohum_enlem_boylam": L["tohum"], "hiz_cm_yil": round(float(np.hypot(*v)), 2),
                    "yon": yon(v) if np.hypot(*v) > 0.05 else "sabit (çerçeve)", "euler_kutbu": j["euler_kutbu"],
                    "euler_hizi_derece_My": j["euler_hizi_derece_My"], "komsular": komsu})
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
        not_ = ("[tasarım] " if ad in TASARIM else "") + cumle(bas, cift, u_, yak) + ("" if ad in TASARIM else " " + ANLAM.get(ad, ""))
        sin.append({"sinir": ad, "ad": M.AD.get(ad, ad), "levhalar": list(cift), "uzunluk_km": round(km), "baskin_sinif": bas,
                    "sinif_paylari": {k: round(v / km, 2) for k, v in sorted(sc.items(), key=lambda x: -x[1])},
                    "ort_yaklasma_cm_yil": round(yak, 2), "ust_levha": u_, "anlam": not_, "kaba_iz_enlem_boylam": [[round(p[0], 1), round(p[1], 1)] for p in nk]})
    J = {"ne": "Dünyam (kurgusal gezegen) levha tektoniği özeti. Hikâye, sahibin elle çizdiği araziden geriye doğru okundu; "
               "karadaki sınırlar araziden ölçüldü, okyanustakiler tasarım.",
         "gezegen": {"yaricap_km": M.RKM, "gun_saat": M.w.rotation_period_h, "eksen_egikligi_derece": M.w.axial_tilt_deg,
                     "kara": "tek kıta, yaklaşık 60°K..7°G ve 47°B..43°D; karanın ~%7'si, gerisi okyanus"},
         "kurallar": {"koordinat": "enlem kuzey +, boylam doğu + (−180..180), derece",
                      "hiz": "cm/yıl, Kuzey levhası sabit kabul edilir (göreli çerçeve)",
                      "sinif_olcutu": "Bird (2003) PB2002: göreli hız sınıra 20°'den yakınsa yanal, değilse yaklaşma/ayrılma; iki yanı denizse okyanusal",
                      "ust_levha": "dalma/çarpışmada: kıta tarafı; ikisi de aynıysa levha sırası"},
         "siniflar": M.SINIF_AD, "levhalar": lev, "sinirlar": sin,
         "dag_ve_yer_sekilleri": [{"no": n, "ad": a, "enlem_boylam": p, "yukseklik_m": h, "gercek_benzeri": g, "koken": k} for n, a, p, h, g, k in DAGLAR],
         "tarih_eskiden_yeniye": [{"donem": d, "olay": t} for d, t in OLAYLAR],
         "dosyalar": {"levha_dunya.png": "tüm gezegen, Equal Earth", "levha_kure.png": "iki küre görünümü",
                      "levha_haritasi.png": "kıta ayrıntısı, dağ numaraları, zaman çizelgesi",
                      "sinirlar.geojson": "her sınır adımı bir LineString; özellikler: sinir, sol, sag, sinif, ust, yaklasma, yanal, km",
                      "levha_kimlik.png": "0,1° ızgara (3600×1800, satır 0 = 90°K), değer = levha kimliği (levhalar.json 'kimlik')",
                      "levhalar.json": "levha alanları, Euler kutupları", "TEKTONIK.md": "kararların tarihçesi (düzeltmeler dahil)"}}
    json.dump(J, open(os.path.join(D, "ozet.json"), "w"), ensure_ascii=False, indent=1)
    # ---------------- OZET.md
    L = []
    L += ["# Dünyam levha tektoniği — özet", "",
          "Bu belge kendi başına okunacak biçimde yazıldı (başka bir kişi ya da yapay zekâ sohbeti için). "
          "Aynı bilgi makine için `ozet.json`'da. Kararların tarihçesi ve düzeltmeler `../TEKTONIK.md`'de. "
          "Belge `tektonik/ozet.py` ile modelden üretilir; elle düzenleme, betiği koş.", "",
          "## 1. Kısaca", "",
          "Dünyam kurgusal bir gezegen: yarıçap %.0f km, gün %g saat, eksen eğikliği %g°. Tek bir kıtası var "
          "(yaklaşık 60°K ile 7°G, 47°B ile 43°D arası); gerisi okyanus. Kıtanın arazisini sahibi elle çizdi; "
          "levha hikâyesi bu araziden geriye doğru okundu: dağların yeri, yüksekliği, keskinliği ve gerçek Dünya'daki "
          "benzerleri. Hikâyenin omurgası: güneydeki bütün parçalar kuzeye yürüyüp kuzeydeki ana karaya çarpıyor "
          "(Afrika ve Hindistan'ın Avrasya'ya çarpması, yani Tetis'in kapanması gibi)." % (M.RKM, M.w.rotation_period_h, M.w.axial_tilt_deg), "",
          "![tüm gezegen](levha_dunya.png)", "",
          "## 2. Okuma kuralları", "",
          "- Koordinat: enlem kuzey +, boylam doğu + (−180..180), derece.",
          "- Hız: cm/yıl, **Kuzey levhası sabit** kabul edilir; diğer hızlar ona göredir.",
          "- Sınır türü elle yazılmadı: her ~27 km'lik sınır adımında iki levhanın göreli hızından hesaplandı "
          "(Bird 2003, PB2002 ölçütü): göreli hız sınıra 20°'den yakınsa **yanal**, değilse **yaklaşma** ya da **ayrılma**; "
          "iki yanı denizse okyanusal, değilse kıtasal.",
          "- **Ölçülen** (güvenilir): karadaki sınırlar, dağların yeri ve yüksekliği. **Tasarım** (değiştirilebilir): "
          "okyanustaki sınırlar, okyanus levhalarının hızları, okyanus tabanı derinliği.", "",
          "| kısaltma | anlamı |", "|---|---|"]
    L += ["| %s | %s |" % (k, v) for k, v in M.SINIF_AD.items()]
    L += ["", "## 3. Levhalar", "", "| levha | tür | alan (milyon km²) | kara payı | hareket (Kuzey'e göre) | komşular |", "|---|---|---|---|---|---|"]
    for x in lev:
        L.append("| %s | %s | %.1f | %%%d | %s | %s |" % (x["ad"], x["tur"], x["alan_milyon_km2"], round(100 * x["kara_payi"]),
                 ("%s %.1f cm/yıl" % (x["yon"], x["hiz_cm_yil"])) if x["hiz_cm_yil"] > 0.05 else x["yon"], ", ".join(x["komsular"])))
    L += ["", "## 4. Sınırlar", "", "Uzunluğa göre sıralı; 150 km'den kısa parçalar tabloda yok (hepsi `ozet.json`'da). 'yaklaşma' artıysa levhalar birbirine yaklaşıyor, eksiyse ayrılıyor. Aynı sınır birden çok levha çiftine değiyorsa her çift ayrı satır. [tasarım] işaretli sınırlar okyanusta, araziyle sınanmadı.", "",
          "| sınır | arasındaki levhalar | baskın tür | uzunluk (km) | yaklaşma (cm/yıl) | üst levha | anlamı |", "|---|---|---|---|---|---|---|"]
    for x in sin:
        if x["uzunluk_km"] < 150: continue
        L.append("| %s | %s | %s (%%%d) | %d | %+.1f | %s | %s |" % (x["ad"], " / ".join(x["levhalar"]), M.SINIF_AD[x["baskin_sinif"]],
                 round(100 * x["sinif_paylari"][x["baskin_sinif"]]), x["uzunluk_km"], x["ort_yaklasma_cm_yil"], x["ust_levha"] or "—", x["anlam"]))
    L += ["", "## 5. Dağlar ve yer şekilleri (kıta)", "", "![kıta](levha_haritasi.png)", "",
          "| no | ad | yer (enlem, boylam) | yükseklik (m) | gerçek benzeri | kökeni |", "|---|---|---|---|---|---|"]
    for n, a, p, h, g, k in DAGLAR:
        L.append("| %s | %s | %.1f, %.1f | %d | %s | %s |" % (n, a, p[0], p[1], h, g, k))
    L += ["", "Levha içi yapılar: Alt Kıta'nın yaylasıyla kuzeyindeki ova arasında, kabaca doğu-batı uzanan **Kuzey Anadolu benzeri "
          "sağ yanal fay**. Gerilme havzaları: iç denizin kuzeyi (yay ardı), takımada ile Alt Kıta arası (**Ege**), yarımadanın "
          "kuzeyindeki körfez (**Tiren benzeri**), Alt Kıta'nın doğusundaki kapalı körfez (**Karadeniz benzeri**).", "",
          "## 6. Tarih (eskiden yeniye, göreli)", ""]
    L += ["%d. **%s**: %s" % (i + 1, d, t) for i, (d, t) in enumerate(OLAYLAR)]
    L += ["", "Rakam (milyon yıl) verilmedi: arazi yalnız göreli sırayı söyler.", "",
          "## 7. Açık kararlar", "",
          "- Okyanus levhalarının sayısı, sırtların yeri ve hızlar tasarım; okyanus tabanı verisi yok.",
          "- Buzul çağı geçmişi (Alp tipi buzul gölleri için) henüz karar verilmedi.",
          "- Göller ve nehirler bu modelden sonra gelecek (yarık gölleri: 9, Alt Kıta'nın kapalı havzaları).", "",
          "## 8. Dosyalar", ""]
    L += ["- `%s`: %s" % (k, v) for k, v in J["dosyalar"].items()]
    open(os.path.join(D, "OZET.md"), "w").write("\n".join(L) + "\n")
    print("yazildi: OZET.md, ozet.json;", len(sin), "sinir grubu")

if __name__ == "__main__":
    uret()
