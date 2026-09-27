"""Buzul çağı doruğundaki buzdan geriye kalan izler.

    python buzul/izler.py            # _iklim_6e22.npz ve _iklim_bugun.npz gerekir

Buz, akis.py'nin dengeli hâl akı yönlendirmesinden. İzler:
- sirk: akısı sıfırdan başlayan (yukarısı buzsuz) ve kar çizgisine yakın
  buzul başları;
- U vadisi: akısı büyük buzlu vadi hücreleri;
- buzul dili ve cephe moreni: buzun buzsuz karaya aktığı son hücre;
- fiyort: denize ulaşan buzul ya da bugün deniz altında kalan buzlu oluk;
- moren seti gölü: büyük vadi buzulunun dilinde, oluğun ağzında
  (Garda, Como, Konstanz türü); kazıma hızın karesiyle (Herman vd. 2015)
  ölçeklenen göreli bir indeksle sıralanır;
- sirk gölü (tarn): sirklerin bugün buzsuz kalanları.
Göllerin yalnız YERİ ve TÜRÜ burada; su dengesi ve derinlik nehir/göl
aşamasında.
"""
import json, os, sys
import numpy as np
BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURASI)
sys.path.insert(0, BURASI)
import buzul as B, akis

DENIZ_DUSUS = -120.0


def kos(ad, deniz):
    z, lat, lon = B.arazi(deniz)
    T0, P = B.iklim_indir(os.path.join(BURASI, "_iklim_%s.npz" % ad), lat, lon)
    b, _, _ = B.denge(T0, P, np.maximum(z, 0))
    dy = B.R * np.radians(abs(lat[1] - lat[0]))
    dx = (B.R * np.radians(lon[1] - lon[0]) * np.cos(np.radians(lat)))[:, None]
    r = akis.buz(z, b, dx, dy)
    r.update(z=z, lat=lat, lon=lon, b=b, dx=dx, dy=dy, T0=T0, P=P)
    return r


def ela(T0, P, maske):
    zz = np.linspace(0, 9000, 901)
    Tm = T0[:, maske].mean(1)[:, None]; Pm = P[:, maske].mean(1)[:, None]
    bb, _, _ = B.denge(Tm * np.ones((12, 901)), Pm * np.ones((12, 901)), zz)
    return float(zz[np.argmax(bb > 0)]) if (bb > 0).any() else None


def en_yakin_dag(la, lo, daglar):
    d = [(np.hypot(la - m["enlem_boylam"][0], (lo - m["enlem_boylam"][1]) * np.cos(np.radians(la))), m) for m in daglar]
    d.sort(key=lambda x: x[0])
    return d[0][1]["no"], d[0][1]["ad"], round(float(d[0][0]) * 111.2)


def main():
    L = kos("6e22", DENIZ_DUSUS)
    N = kos("bugun", 0.0)
    z, lat, lon = L["z"], L["lat"], L["lon"]
    ny, nx = z.shape
    ortu, Q, H, ii, jj, gelen = L["ortu"], L["Q"], L["H"], L["ii"], L["jj"], L["gelen"]
    alan = L["dx"] * L["dy"] * np.ones_like(z)
    gen = np.sqrt(alan)
    u = np.where(ortu & (H > 1), Q / (np.maximum(H, 1) * gen), 0.0)     # m/yıl, kesit ortalaması
    kazi = u ** 2
    bugun_deniz = (z + DENIZ_DUSUS) < 0          # bugünkü kıyıya göre
    lgm_deniz = z < 0
    asagi_ortu = ortu[ii, jj]
    asagi_deniz = lgm_deniz[ii, jj]
    dil = ortu & ~asagi_ortu & ~(ii == np.arange(ny)[:, None]) | (ortu & asagi_deniz)
    daglar = json.load(open(os.path.join(KOK, "tektonik", "ozet.json"), encoding="utf-8"))["dag_ve_yer_sekilleri"]

    # buzul havzaları: her hücre, akış yolunun ulaştığı dile bağlanır
    kok_i = np.arange(ny * nx).reshape(ny, nx)
    hedef = np.where(ortu & ~dil, ii * nx + jj, kok_i).ravel()
    for _ in range(40):
        hedef = hedef[hedef]
    hav = hedef.reshape(ny, nx)

    buzullar = []
    for i, j in zip(*np.where(dil)):
        k = i * nx + j
        m = ortu & (hav == k)
        A = float(alan[m].sum()) / 1e6
        if A < 300:           # 300 km2 altı: küçük dağ buzulu, listeye girmez
            continue
        la, lo = float(lat[i]), float(lon[j])
        no, dad, uz = en_yakin_dag(la, lo, daglar)
        denize = bool(asagi_deniz[i, j])
        fiyort = denize or bool((m & bugun_deniz).any())
        buzullar.append(dict(
            enlem_boylam=[round(la, 2), round(lo, 2)], dag=no, dag_ad=dad, dagdan_km=uz,
            alan_km2=round(A), uzunluk_km=None, en_kalin_m=int(H[m].max()),
            aki_km3_yil=round(float(Q[i, j] + max(L["b"][i, j], 0) * alan[i, j]) / 1e9, 3),
            dil_yukseklik_m=int(z[i, j] + DENIZ_DUSUS), bitis="deniz" if denize else "kara",
            fiyort=fiyort, kazi=float(kazi[m].max()), _i=int(i), _j=int(j), _k=k))
    buzullar.sort(key=lambda g: -g["alan_km2"])
    buyuk_dil = np.zeros_like(dil)
    for g in buzullar:
        buyuk_dil[g["_i"], g["_j"]] = True
    kmax = max(g["kazi"] for g in buzullar)
    for g in buzullar:
        g["kazi"] = round(g["kazi"] / kmax, 3)
        # uzunluk: dilden en uzak buzlu hücreye kaba mesafe
        m = ortu & (hav == g["_k"])
        yi, xj = np.where(m)
        g["uzunluk_km"] = int(np.max(np.hypot((yi - g["_i"]) * L["dy"], (xj - g["_j"]) * L["dx"][yi, 0])) / 1e3)

    # sirkler: buzlu, yukarısından buz gelmeyen, kar çizgisinin 500 m yakınında
    sirk = ortu & (gelen <= 0) & (L["b"] > 0)
    # kar çizgisi enlem bandı başına
    kara = z >= 0
    ela_lgm, ela_bugun = {}, {}
    for la in range(-5, 61, 5):
        r = (np.abs(lat - la) < 2.5)[:, None] & kara
        if r.sum() > 50:
            ela_lgm[la] = ela(L["T0"], L["P"], r)
            ela_bugun[la] = ela(N["T0"], N["P"], r)
    E = np.interp(lat, sorted(ela_lgm), [ela_lgm[k] for k in sorted(ela_lgm)])[:, None]
    yuzey = z + L["H"]
    sirk &= np.abs(yuzey - E) < 600
    tarn = sirk & ~N["ortu"]

    # moren seti gölleri: karada biten, büyük (>= 1000 km2) vadi buzullarının
    # dili. D8 bir buz alanını birçok dile böler; 80 km içindeki diller tek
    # göl sayılır (en büyük besleyen kalır).
    aday = [g for g in buzullar if g["bitis"] == "kara" and g["alan_km2"] >= 1000]
    aday.sort(key=lambda g: -g["alan_km2"])
    goller = []
    for g in aday:
        la, lo = g["enlem_boylam"]
        if any(np.hypot(la - x["enlem_boylam"][0], (lo - x["enlem_boylam"][1]) * np.cos(np.radians(la))) * 111.2 < 80
               for x in goller):
            continue
        acik = not N["ortu"][g["_i"], g["_j"]]
        boy = "büyük" if g["alan_km2"] >= 10000 else ("orta" if g["alan_km2"] >= 3000 else "küçük")
        goller.append(dict(no=len(goller) + 1, tur="moren seti gölü (Garda/Como türü)", boy=boy, enlem_boylam=g["enlem_boylam"],
                           dag=g["dag"], dag_ad=g["dag_ad"], besleyen_buzul_km2=g["alan_km2"], kazi=g["kazi"],
                           yukseklik_m=g["dil_yukseklik_m"],
                           bugun="açık su" if acik else "bugün hâlâ buz altında"))
    # fiyortlar: denize ulaşan buzullar, 80 km içindekiler tek fiyort
    fiyortlar = []
    for g in sorted([g for g in buzullar if g["fiyort"]], key=lambda g: -g["alan_km2"]):
        la, lo = g["enlem_boylam"]
        if any(np.hypot(la - x["enlem_boylam"][0], (lo - x["enlem_boylam"][1]) * np.cos(np.radians(la))) * 111.2 < 80
               for x in fiyortlar):
            continue
        fiyortlar.append(dict(no=len(fiyortlar) + 1, enlem_boylam=g["enlem_boylam"], dag=g["dag"], dag_ad=g["dag_ad"],
                              besleyen_buzul_km2=g["alan_km2"]))
    # sirk ve sirk gölleri dağ başına
    sirk_dag = {}
    for i, j in zip(*np.where(sirk)):
        no = en_yakin_dag(float(lat[i]), float(lon[j]), daglar)[0]
        d = sirk_dag.setdefault(no, [0, 0]); d[0] += 1; d[1] += int(tarn[i, j])

    w = np.cos(np.radians(lat))[:, None] * np.ones_like(z)
    kara_bugun = (z + DENIZ_DUSUS) >= 0
    def pay(m, kk):
        return round(100 * float((w * (m & kk)).sum() / (w * kk).sum()), 2)
    ozet = dict(
        senaryo=dict(sogutma_c=-6, egiklik_derece=22, deniz_m=DENIZ_DUSUS,
                     not_="Buzul çağı doruğu. Dünya'nın son buzul maksimumu küresel −6.1 °C (Tierney vd. 2020); eğiklik 28°→22° salınımı yazları serinletir (Milankoviç)."),
        buz_payi_kara=dict(buzul_cagi=pay(ortu, kara), bugun=pay(N["ortu"], kara_bugun)),
        kar_cizgisi_m=dict(buzul_cagi={str(k): v for k, v in ela_lgm.items()}, bugun={str(k): v for k, v in ela_bugun.items()}),
        buzul_sayisi_300km2_ustu=len(buzullar),
        buzullar_en_buyuk_40=[{k: v for k, v in g.items() if not k.startswith("_")} for g in buzullar[:40]],
        goller=goller,
        fiyortlar=fiyortlar,
        sirk_dag_basina={k: dict(sirk=v[0], bugun_buzsuz_sirk_golu_adayi=v[1]) for k, v in sorted(sirk_dag.items())},
        sirk_sayisi=int(sirk.sum()), tarn_sayisi=int(tarn.sum()),
    )
    json.dump(ozet, open(os.path.join(BURASI, "izler.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    np.savez_compressed(os.path.join(BURASI, "_izler.npz"), ortu=ortu, bugun=N["ortu"], H=H, kazi=kazi, dil=dil,
                        sirk=sirk, tarn=tarn, buyuk_dil=buyuk_dil, z=z, lat=lat, lon=lon, hav=hav)
    print("buz: buzul çağı %%%.2f, bugün %%%.2f" % (ozet["buz_payi_kara"]["buzul_cagi"], ozet["buz_payi_kara"]["bugun"]))
    print("büyük buzul", len(buzullar), "fiyort", len(fiyortlar), "göl", len(goller),
          "sirk", ozet["sirk_sayisi"], "tarn", ozet["tarn_sayisi"])
    for g in buzullar[:15]:
        print(" ", g["dag"], g["dag_ad"], g["alan_km2"], "km2", g["uzunluk_km"], "km", g["en_kalin_m"], "m", g["bitis"], "fiyort" if g["fiyort"] else "", g["dil_yukseklik_m"], "kazi", g["kazi"])
    print(ozet["sirk_dag_basina"]); print(fiyortlar)
    from collections import Counter
    print("göller:", len(goller), Counter((x["dag"], x["boy"]) for x in goller))


if __name__ == "__main__":
    main()
