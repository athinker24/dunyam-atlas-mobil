"""Uygulamanın tektonik katmanı: data/tektonik.json ve data/levha.png.

    python tektonik/uygulama.py

Girdi yalnız bu klasörün çıktıları (levha_kimlik.png, sinirlar.geojson,
ozet.json); levha modeli yeniden koşulmaz.

- levha.png: harita kutusuna kırpılmış levha kimliği (gri ton = kimlik,
  0 = kutu dışı), kaynak çözünürlüğünde (~0.088°).
- tektonik.json: levhalar (ad, tür, hız, yön, komşular), sınır çizgileri
  (aynı sınır ve sınıftaki ardışık adımlar birleşik; 0.01° fark kodlu),
  volkan kuşakları.

Volkan kuşakları (27 Eylül, sahibi: "volkan kuşakları ile birlikte"):
- Yay volkanları: dalan levhanın üstündeki levhada, dalma hattına paralel.
  Volkan cephesi dalan levhanın ~100-130 km derinliğe indiği yerin üstünde
  (Syracuse ve Abers 2006); hendeğe uzaklık çoğunlukla 100-300 km
  (Dickinson 1973). Burada cephe 150 km, kuşak 150-280 km. Yalnız
  yakınlaşma >= 1 cm/yıl olan dalma ve okyanusal yakınlaşma adımlarında:
  daha yavaşında dalan levha cepheye kadar inmemiş sayılır.
- Kıta çarpışmasında yay yok (Himalaya'da etkin yay volkanı yok); baskın
  sınıfı çarpışma olan sınırın dalma parçaları da sayılmaz.
- Yarık volkanları: kıta yarığı adımlarında, sınırın üstünde (Doğu Afrika
  yarığı bol, Baykal seyrek; burada "seyrek" diye gösterilir).
- Sönmüş: güneybatı bloğunun batı kıyısında 12°K güneyi (TEKTONIK.md bölüm
  4: küçük kıta dalma hattına gelince volkanlar sustu; levha haritasındaki
  işaretlerle aynı sınır).
Okyanus sırtları da volkaniktir ama su altındadır; ayrı kuşak çizilmez.
"""
import json, math, os
import numpy as np
from PIL import Image

BURASI = os.path.dirname(os.path.abspath(__file__)); KOK = os.path.dirname(BURASI)
R_KM = 6371.0
CEPHE_KM, KUSAK_KM = 150.0, 280.0
YAY_ESIK = 1.0            # cm/yıl
PAY = 6.0                 # harita kutusunun dışına taşan pay (derece)


def kutu():
    J = json.load(open(os.path.join(KOK, "data", "atlas.json"), encoding="utf-8"))
    return J["data"]["regions"]["global"]["bounds"]      # [lon0, lat0, lon1, lat1]


def kimlik():
    a = np.array(Image.open(os.path.join(BURASI, "levha_kimlik.png")))
    ny, nx = a.shape
    return a, ny, nx


def levha_at(a, la, lo):
    ny, nx = a.shape
    i = int(np.clip((90 - la) / 180 * ny, 0, ny - 1)); j = int(((lo + 180) / 360 * nx) % nx)
    return int(a[i, j])


def kaydir(la, lo, yon_km):
    """(dogu, kuzey) km kadar kaydır (küçük uzaklık yaklaşığı)."""
    de, dn = yon_km
    return la + math.degrees(dn / R_KM), lo + math.degrees(de / (R_KM * max(math.cos(math.radians(la)), 0.05)))


def kodla(p):
    X = [int(round(lo * 100)) for lo, la in p]; Y = [int(round(la * 100)) for lo, la in p]
    kod = [X[0], Y[0]]
    for i in range(1, len(X)):
        kod += [X[i] - X[i - 1], Y[i] - Y[i - 1]]
    return kod


def main():
    B = kutu()
    icinde = lambda lo, la: B[0] - PAY <= lo <= B[2] + PAY and B[1] - PAY <= la <= B[3] + PAY
    a, ny, nx = kimlik()
    oz = json.load(open(os.path.join(BURASI, "ozet.json"), encoding="utf-8"))
    kim = {k: v["kimlik"] for k, v in json.load(open(os.path.join(BURASI, "levhalar.json"), encoding="utf-8"))["levhalar"].items()}
    ad_sinir = {}; anlam = {}
    # baskın sınıfı kıta çarpışması olan sınırda yay yok (Duvar dikişinin
    # denize değen kısa ucu dalma sayılıyor ama cephe Himalaya gibi)
    baskin = {s["sinir"]: s["baskin_sinif"] for s in sorted(oz["sinirlar"], key=lambda s: s["uzunluk_km"])}
    for s in oz["sinirlar"]:
        ad_sinir[s["sinir"]] = s["ad"]
        anlam[(s["sinir"], frozenset(s["levhalar"]))] = s["anlam"]

    # --- levha.png: kutuya kırpılmış kimlik
    i0 = int(np.floor((90 - B[3]) / 180 * ny)); i1 = int(np.ceil((90 - B[1]) / 180 * ny))
    j0 = int(np.floor((B[0] + 180) / 360 * nx)); j1 = int(np.ceil((B[2] + 180) / 360 * nx))
    kes = a[i0:i1, j0:j1]
    Image.fromarray(kes.astype(np.uint8), "L").save(os.path.join(KOK, "data", "levha.png"), optimize=True)
    kesit = [(-180 + j0 * 360 / nx), (90 - i1 * 180 / ny), (-180 + j1 * 360 / nx), (90 - i0 * 180 / ny)]

    # --- sınırlar: ardışık, aynı sınır/sınıf/üst taraf adımları tek çizgi
    F = json.load(open(os.path.join(BURASI, "sinirlar.geojson"), encoding="utf-8"))["features"]
    cizgiler = []; cur = None
    for f in F:
        p = f["properties"]; c = f["geometry"]["coordinates"]
        if not any(icinde(lo, la) for lo, la in c):
            cur = None; continue
        # dişler (dalma/çarpışma) üst levhanın tarafında: sol mu sağ mı
        u = 0
        if p["ust"]:
            u = 1 if p["ust"] == p["sol"] else -1
        anahtar = (p["sinir"], p["sinif"], u, p["sol"], p["sag"])
        if cur is not None and cur["anahtar"] == anahtar and cur["p"][-1] == tuple(c[0]):
            cur["p"].append(tuple(c[-1])); cur["km"] += p["km"]; cur["y"].append((p["yaklasma"], p["km"]))
        else:
            cur = dict(anahtar=anahtar, p=[tuple(c[0]), tuple(c[-1])], km=p["km"], y=[(p["yaklasma"], p["km"])])
            cizgiler.append(cur)
    sinirlar = []
    for s in cizgiler:
        sinir, sinif, u, sol, sag = s["anahtar"]
        yak = sum(y * k for y, k in s["y"]) / max(sum(k for _, k in s["y"]), 1e-9)
        # dişlerin yönü geometriden: çizginin (p0 -> p1 yönüne göre) sol
        # yanındaki levha üst levha mı. u = +1 sol, -1 sağ, 0 diş yok.
        if u:
            ust_id = kim[sol if u == 1 else sag]; oy = {1: 0, -1: 0}
            for (lo1, la1), (lo2, la2) in zip(s["p"][:-1], s["p"][1:]):
                la, lo = (la1 + la2) / 2, (lo1 + lo2) / 2
                te = (lo2 - lo1) * 111.2 * math.cos(math.radians(la)); tn = (la2 - la1) * 111.2
                Lk = math.hypot(te, tn) or 1
                for sgn in (1, -1):
                    q = kaydir(la, lo, (-tn / Lk * 40 * sgn, te / Lk * 40 * sgn))
                    if levha_at(a, *q) == ust_id:
                        oy[sgn] += 1
            u = 1 if oy[1] >= oy[-1] else -1
        sinirlar.append(dict(ad=ad_sinir.get(sinir, sinir), s=sinif, u=u, l=[sol, sag], y=round(yak, 1),
                             km=round(s["km"]), n=anlam.get((sinir, frozenset((sol, sag))), ""), p=kodla(s["p"])))

    # --- volkan kuşakları
    yaylar = []; yariklar = []
    for f in F:
        p = f["properties"]; c = f["geometry"]["coordinates"]
        (lo1, la1), (lo2, la2) = c[0], c[-1]
        lo, la = (lo1 + lo2) / 2, (la1 + la2) / 2
        if not icinde(lo, la):
            continue
        if p["sinif"] == "CRB":
            yariklar.append((p["sinir"], lo, la)); continue
        if p["sinif"] not in ("SUB", "OCB") or p["yaklasma"] < YAY_ESIK or not p["ust"] or baskin.get(p["sinir"]) == "CCB":
            continue
        # sınır doğrultusu (km) ve iki normal; üst levha hangi taraftaysa
        te = (lo2 - lo1) * 111.2 * math.cos(math.radians(la)); tn = (la2 - la1) * 111.2
        L = math.hypot(te, tn) or 1; te, tn = te / L, tn / L
        ust = kim[p["ust"]]; secilen = None
        for sgn in (1, -1):
            nrm = (-tn * sgn, te * sgn)
            q = kaydir(la, lo, (nrm[0] * CEPHE_KM, nrm[1] * CEPHE_KM))
            if levha_at(a, *q) == ust:
                secilen = nrm; break
        if secilen is None:
            continue
        on = kaydir(la, lo, (secilen[0] * CEPHE_KM, secilen[1] * CEPHE_KM))
        arka = kaydir(la, lo, (secilen[0] * KUSAK_KM, secilen[1] * KUSAK_KM))
        sonuk = p["sinir"] == "bati_cukur" and on[0] < 12
        yaylar.append(dict(sinir=p["sinir"], on=on, arka=arka, sonuk=sonuk, y=p["yaklasma"]))
    # ardışık yay noktalarını kuşak çizgilerine bağla (aynı sınır, aynı durum, 60 km'den yakın)
    kusaklar = []; cur = None
    for v in yaylar:
        if cur and cur["sinir"] == v["sinir"] and cur["sonuk"] == v["sonuk"] and \
                math.hypot((v["on"][0] - cur["on"][-1][0]) * 111.2,
                           (v["on"][1] - cur["on"][-1][1]) * 111.2 * math.cos(math.radians(v["on"][0]))) < 90:
            cur["on"].append(v["on"]); cur["arka"].append(v["arka"]); cur["y"].append(v["y"])
        else:
            cur = dict(sinir=v["sinir"], sonuk=v["sonuk"], on=[v["on"]], arka=[v["arka"]], y=[v["y"]]); kusaklar.append(cur)
    kusak_cikis = []
    for k in kusaklar:
        if len(k["on"]) < 3:
            continue
        on = [(lo, la) for la, lo in k["on"]]; arka = [(lo, la) for la, lo in k["arka"]]
        kusak_cikis.append(dict(ad=ad_sinir.get(k["sinir"], k["sinir"]), sonuk=k["sonuk"], y=round(float(np.mean(k["y"])), 1),
                                on=kodla(on), arka=kodla(arka)))
    yarik_cikis = {}
    for s, lo, la in yariklar:
        yarik_cikis.setdefault(s, []).append((lo, la))
    yarik_cikis = [dict(ad=ad_sinir.get(s, s), p=kodla(v)) for s, v in yarik_cikis.items() if len(v) >= 3]

    levhalar = {}
    LJ = json.load(open(os.path.join(BURASI, "levhalar.json"), encoding="utf-8"))["levhalar"]
    for L_ in oz["levhalar"]:
        lj = LJ[L_["ad"]]
        # etiket yeri: tohum (levhanın içinde seçilmiş nokta); hız oku tohumdaki (doğu, kuzey) cm/yıl
        levhalar[str(kim[L_["ad"]])] = dict(ad=L_["ad"], tur=L_["tur"], hiz=L_["hiz_cm_yil"], yon=L_["yon"],
                                            alan=L_["alan_milyon_km2"], kara=L_["kara_payi"], komsu=L_["komsular"],
                                            tohum=lj["tohum"], v=lj["hiz_tohumda_dogu_kuzey"])
    veri = dict(ne="Dünyam levha tektoniği (tektonik/uygulama.py); ayrıntı tektonik/OZET.md",
                siniflar=oz["siniflar"], kesit=[round(v, 4) for v in kesit], levhalar=levhalar,
                sinirlar=sinirlar, kusaklar=kusak_cikis, yariklar=yarik_cikis,
                olcut=dict(cephe_km=CEPHE_KM, kusak_km=KUSAK_KM, yay_esik_cm_yil=YAY_ESIK))
    yol = os.path.join(KOK, "data", "tektonik.json")
    with open(yol, "w", encoding="utf-8") as fh:
        json.dump(veri, fh, ensure_ascii=False, separators=(",", ":"))
    print("tektonik.json: %d sınır çizgisi, %d yay kuşağı (%d sönmüş), %d yarık; %.0f KB; levha.png %dx%d %.0f KB" % (
        len(sinirlar), len(kusak_cikis), sum(k["sonuk"] for k in kusak_cikis), len(yarik_cikis),
        os.path.getsize(yol) / 1024, kes.shape[1], kes.shape[0], os.path.getsize(os.path.join(KOK, "data", "levha.png")) / 1024))
    for k in kusak_cikis:
        print("  yay:", k["ad"], "sönmüş" if k["sonuk"] else "etkin", k["y"], "cm/yıl", len(k["on"]) // 2, "nokta")


if __name__ == "__main__":
    main()
