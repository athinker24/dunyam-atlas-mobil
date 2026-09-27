"""Deltalar: nehrin çökel akısı ile ağızdaki dalga gücünün dengesi.

    python su/delta.py        # su/_disa.pkl, su/_akim.npz, buzul/ ön hesapları gerekir

1. Çökel akısı (BQART, Syvitski ve Milliman 2007):
       Qs = ω · B · Q^0.31 · A^0.5 · R · T      (T >= 2 °C)
       Qs = 2ω · B · Q^0.31 · A^0.5 · R         (T <  2 °C)
   ω = 0.0006, Qs Mt/yıl; Q km³/yıl, A km², R havzanın en yüksek noktası
   (km), T havzanın alan ağırlıklı yıllık ortalama sıcaklığı (°C).
   B = I · (1 − TE): I = 1 + 0.09·(buzul yüzdesi) buzul aşındırması,
   TE göllerin tuttuğu pay (akışı bir gölden geçen havza alanının payı;
   çökel göle çöker). Kayaç türü ve insan etkisi bilinmiyor: 1.
2. Dalga: ağızdaki yıllık ortalama rüzgâr hızı (uygulamanın dolaşım
   verisinden, aylık hızların ortalaması) ve açık su mesafesi (16 yönde
   karaya çarpana kadar, en çok 2000 km; ortalaması). Dalga yüksekliği
   SPM (1977) derin su bağıntısıyla:
       H = 0.283 U²/g · tanh(0.0125 (gF/U²)^0.42)
3. Delta göstergesi X = Qs / H^2.4 (dalganın kıyı boyu taşıma gücü
   H^(12/5) ile artar; Nienhuis vd. 2015, 2020'de nehir/dalga oranı).
   Eşikler Dünya örnekleriyle kaba ayarlı (doğal hâlleriyle): Mississippi
   ~300 Mt/yıl, Meksika Körfezi H ~1 m -> X ~300 (kuş ayağı); Nil ~120,
   Akdeniz H ~1.5 m -> X ~45 (yay biçimli, dalga baskın); açık kıyıda
   küçük nehir ~5 Mt/yıl, H ~2 m -> X ~1 (delta yok).
       X >= 100  nehir baskın delta (kuş ayağı / loblu)
       15..100   yay biçimli delta (dalga törpüler)
       3..15     küçük, dalga baskın delta
       < 3       delta yok (ağız düz kıyı ya da haliç)
   Gelgit bilinmiyor (Dünyam'ın ayı tanımlı değil): gelgit baskın (Ganj
   türü huni) deltalar değerlendirilemez.
Göllere dökülen nehirler: göl dalgası küçük (H ~0.5 m), kapalı tuz gölüne
dökülen büyük nehir iç delta yapar (Volga-Hazar, Amu Derya-Aral).
"""
import json, os, pickle, sys
import numpy as np
from PIL import Image
BURASI = os.path.dirname(os.path.abspath(__file__)); KOK = os.path.dirname(BURASI)
sys.path.insert(0, BURASI); sys.path.insert(0, os.path.join(KOK, "buzul"))
import nehir

G = 9.81
OMEGA = 0.0006
GOL_H = 0.5
ESIK = [(100, "nehir baskın (kuş ayağı / loblu)"), (15, "yay biçimli (dalga törpüler)"),
        (3, "küçük, dalga baskın"), (0, None)]


def ruzgar_hizi(lat, lon):
    """Uygulamanın dolasim.png'sinden yıllık ortalama rüzgâr hızı (m/s), ince gridde."""
    A = json.load(open(os.path.join(KOK, "data", "atlas.json"), encoding="utf-8"))["data"]["regions"]["global"]
    k = A["dolasim"]; W, H, B = A["w"], A["h"], A["bounds"]
    px = np.asarray(Image.open(os.path.join(KOK, "data", "dolasim.png")).convert("RGB"), dtype=np.float64)
    hiz = np.zeros((k["h"], k["w"]))
    for m in range(12):
        blok = px[m * k["h"]:(m + 1) * k["h"]]
        u = (blok[..., 0] - 128) / 127 * k["ruzgar_ust"]; v = (blok[..., 1] - 128) / 127 * k["ruzgar_ust"]
        hiz += np.hypot(u, v) / 12
    # ince grid -> atlas hücresi -> dolaşım bloğu
    ax = (lon - B[0]) / (B[2] - B[0]) * W; ay = (B[3] - lat) / (B[3] - B[1]) * H
    bx = np.clip((ax / k["blok"]).astype(int), 0, k["w"] - 1); by = np.clip((ay / k["blok"]).astype(int), 0, k["h"] - 1)
    return hiz[by[:, None], bx[None, :]]


def acik_su(i, j, deniz, dyk, dxk, en_cok=2000.0):
    """16 yönde karaya ya da en_cok km'ye kadar açık su mesafesi (km), ortalama."""
    ny, nx = deniz.shape
    t = []
    for a in np.linspace(0, 2 * np.pi, 16, endpoint=False):
        L = 0.0; adim = 8.0
        while L < en_cok:
            L += adim
            ii = int(round(i - np.sin(a) * L / dyk)); jj = int(round(j + np.cos(a) * L / dxk[min(max(ii, 0), ny - 1)]))
            if not (0 <= ii < ny and 0 <= jj < nx) or not deniz[ii, jj]:
                break
        t.append(min(L, en_cok))
    return float(np.mean(t))


def dalga_H(U, F_km):
    if U < 0.5:
        return 0.05
    return 0.283 * U * U / G * np.tanh(0.0125 * (G * F_km * 1000 / (U * U)) ** 0.42)


def main():
    d = pickle.load(open(os.path.join(BURASI, "_disa.pkl"), "rb"))
    alici, q, gm, deniz, lat, lon, goller = d["alici"], d["q"], d["gm"], d["deniz"], d["lat"], d["lon"], d["goller"]
    k = np.load(os.path.join(BURASI, "_akim.npz")); z = k["z"].astype(np.float64)
    ny, nx = z.shape
    dyk = 6371 * np.radians(abs(lat[1] - lat[0])); dxk = 6371 * np.radians(lon[1] - lon[0]) * np.cos(np.radians(lat))
    alan = dyk * dxk[:, None] * np.ones((1, nx))
    # yıllık ortalama sıcaklık (yüzeyde) ve bugünkü buzul
    import buzul as BZ
    T0, _ = BZ.iklim_indir(os.path.join(KOK, "buzul", "_iklim_bugun025.npz"), lat, lon)
    Tyil = T0.mean(0) - BZ.LAPSE * np.maximum(z, 0)
    buz = np.load(os.path.join(KOK, "buzul", "_akis_bugun.npz"))["ortu"]
    U = ruzgar_hizi(lat, lon)
    # havzalar: her hücre, akışı kökte (deniz/kapalı göl) biten ağaçta kökün kimliğini alır
    sira = nehir.sira_kur(alici)
    kok = np.full(ny * nx, -1, dtype=np.int64); gol_ust = np.zeros(ny * nx, bool)
    gmf = gm.ravel()
    for c in sira:
        r = alici[c]
        if r < 0:
            kok[c] = c
        else:
            kok[c] = kok[r]
            gol_ust[c] = gol_ust[r] or gmf[r]      # akış yolu aşağıda bir gölden geçiyor
    # ağızlar: denize dökülen nehir hücresi, ya da göle dökülen (göl kıyısı)
    qf = q.ravel(); df = deniz.ravel(); zf = z.ravel()
    nehir_m = (qf >= 50) & ~gmf & ~df
    agiz = [c for c in np.where(nehir_m)[0] if alici[c] >= 0 and (df[alici[c]] or gmf[alici[c]])]
    # her ağzın havzası: ağızdan yukarı, alici zinciri ağıza varan hücreler
    ust = np.full(ny * nx, -1, dtype=np.int64)
    agiz_set = np.zeros(ny * nx, bool); agiz_set[agiz] = True
    for c in sira:
        r = alici[c]
        ust[c] = c if agiz_set[c] else (ust[r] if r >= 0 else -1)
    gol_ic = np.zeros(ny * nx, bool)     # ağızdan yukarıda yolu bir gölden geçen (ağız ile göl arası değil)
    for c in sira:
        r = alici[c]
        if r >= 0 and not agiz_set[c]:
            gol_ic[c] = gol_ic[r] or (gmf[r] and not agiz_set[r])
    sonuc = []
    af, Tf, bf = alan.ravel(), Tyil.ravel(), buz.ravel()
    uyelik = ust
    sirali = np.argsort(uyelik, kind="stable"); u_sorted = uyelik[sirali]
    for c in agiz:
        a0 = np.searchsorted(u_sorted, c); a1 = np.searchsorted(u_sorted, c, side="right")
        hv = sirali[a0:a1]
        A = af[hv].sum()
        if A < 2000:
            continue
        Qkm3 = qf[c] * 3.156e7 / 1e9
        R = max(zf[hv].max(), 1) / 1000.0
        w = af[hv]
        T = float((Tf[hv] * w).sum() / w.sum())
        Ag = 100 * float((bf[hv] * w).sum() / w.sum())
        TE = float((gol_ic[hv] * w).sum() / w.sum())
        B = (1 + 0.09 * Ag) * (1 - TE)
        Qs = OMEGA * B * Qkm3 ** 0.31 * A ** 0.5 * R * (T if T >= 2 else 2.0)
        i, j = divmod(int(c), nx)
        hedef = "göl" if gmf[alici[c]] else "deniz"
        if hedef == "deniz":
            F = acik_su(i, j, deniz, dyk, dxk); Hs = dalga_H(float(U[i, j]), F)
        else:
            F = 0.0; Hs = GOL_H
        X = Qs / max(Hs, 0.05) ** 2.4
        tur = next(t for e, t in ESIK if X >= e)
        if tur is None:
            continue
        # göl bilgisi
        gol = None
        if hedef == "göl":
            for g in goller:
                if alici[c] in set(g["hucreler"][:0]) or np.isin(alici[c], g["hucreler"]):
                    gol = ("kapalı, tuzlu" if not g["cikisli"] else "tatlı") + ", %d km²" % g["alan_km2"]; break
        sonuc.append(dict(enlem_boylam=[round(float(lat[i]), 2), round(float(lon[j]), 2)], hucre=int(c),
                          hedef=hedef, gol=gol, debi_m3s=int(qf[c]), havza_km2=int(A), en_yuksek_m=int(R * 1000),
                          sicaklik_c=round(T, 1), buzul_yuzde=round(Ag, 1), gol_tutar=round(TE, 2),
                          cokel_mt_yil=round(float(Qs), 1), ruzgar_ms=round(float(U[i, j]), 1) if hedef == "deniz" else None,
                          acik_su_km=int(F), dalga_m=round(float(Hs), 2), gosterge=round(float(X), 1), tur=tur))
    # yakın ağızlar (aynı nehrin kolları) birleşir: 60 km içinde en büyük kalır
    sonuc.sort(key=lambda s: -s["cokel_mt_yil"])
    tut = []
    for s in sonuc:
        la, lo = s["enlem_boylam"]
        if any(np.hypot(la - t["enlem_boylam"][0], (lo - t["enlem_boylam"][1]) * np.cos(np.radians(la))) * 111.2 < 60 for t in tut):
            continue
        tut.append(s)
    json.dump(dict(ne="Delta adayları (su/delta.py)", deltalar=tut), open(os.path.join(BURASI, "deltalar.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    from collections import Counter
    print("delta:", len(tut), Counter(t["tur"] for t in tut), Counter(t["hedef"] for t in tut))
    for t in tut[:25]:
        print("  %6.1f Mt  Q %6d  H %.2f  X %7.1f  %-6s %s %s" % (t["cokel_mt_yil"], t["debi_m3s"], t["dalga_m"], t["gosterge"],
                                                                t["hedef"], t["enlem_boylam"], t["tur"]))




# --- uygulama için çatallanan ağız kolları -----------------------------------
# Delta görünüşü: ağızdan r km yukarıdaki "tepe"den kıyıya yelpaze gibi açılan
# 2-5 kol. r = 12·Qs^0.45 km (Qs Mt/yıl: 700 -> ~230 km, Nil deltası ~160 km;
# 60 -> ~75 km; 10 -> ~35 km). Kol sayısı nehir baskında 3-5, yay biçimlide 2-3,
# küçükte 2. Kolların YERİ tasarımdır: ~10 km'lik arazi dağıtıcı kolları
# çözmez; delta varlığı ve büyüklüğü hesaptan, çatalların biçimi değil.
def catallar(tut, alici, q, deniz, gm, lat, lon):
    import disa
    ny, nx = q.shape; qf = q.ravel()
    g = alici >= 0; o = np.argsort(alici[g], kind="stable"); coc = np.where(g)[0][o]; ust = alici[coc]
    bas = np.searchsorted(ust, np.arange(ny * nx)); son = np.searchsorted(ust, np.arange(ny * nx), side="right")
    dyk = 6371 * np.radians(abs(lat[1] - lat[0])); dxk = 6371 * np.radians(lon[1] - lon[0]) * np.cos(np.radians(lat))
    su_ = deniz | gm
    kara = ~su_
    kiyi = kara & (np.roll(su_, 1, 0) | np.roll(su_, -1, 0) | np.roll(su_, 1, 1) | np.roll(su_, -1, 1))
    ki, kj = np.where(kiyi)
    rng = np.random.default_rng(1492)
    out = []
    for t in tut:
        c = t["hucre"]; i, j = divmod(c, nx)
        r_km = 12 * t["cokel_mt_yil"] ** 0.45
        # tepe: ana koldan r_km yukarı
        x, L = c, 0.0
        while L < r_km and son[x] > bas[x]:
            cc = coc[bas[x]:son[x]]; y = int(cc[np.argmax(qf[cc])])
            i1, j1 = divmod(x, nx); i2, j2 = divmod(y, nx)
            L += np.hypot((i2 - i1) * dyk, (j2 - j1) * dxk[i1]); x = y
        ai, aj = divmod(x, nx)
        if L < 0.4 * r_km:
            continue
        yon = np.array([i - ai, j - aj], float); yon /= max(np.hypot(*yon), 1e-9)
        d = np.hypot((ki - ai) * dyk, (kj - aj) * dxk[ai])
        v = np.column_stack([ki - ai, kj - aj]).astype(float); vn = v / np.maximum(np.hypot(v[:, 0], v[:, 1]), 1e-9)[:, None]
        aci = np.degrees(np.arccos(np.clip(vn @ yon, -1, 1)))
        # hedef kıyı: kolun döküldüğü su (deniz ya da o göl) kıyısı
        aday = np.where((d > 0.6 * r_km) & (d < 1.4 * r_km) & (aci < 70))[0]
        n = {"nehir": 4, "yay": 3, "küçük,": 2}[t["tur"].split()[0]] + (1 if t["cokel_mt_yil"] > 200 else 0)
        if len(aday) < n:
            continue
        s = np.sign(vn[aday] @ np.array([-yon[1], yon[0]])) * aci[aday]      # soldan sağa işaretli açı
        sira = aday[np.argsort(s)]
        hedefler = [sira[int(round(k * (len(sira) - 1) / (n - 1)))] for k in range(n)]
        yollar_ = []
        for h in hedefler:
            p = np.array([[aj, ai], [kj[h], ki[h]]], float)
            p = disa.kivir(np.vstack([p[0], (p[0] + p[1]) / 2 + rng.normal(0, 0.8, 2), p[1]]), rng, duzey=3, oran=0.13)
            lo = lon[0] + p[:, 0] * (lon[1] - lon[0]); la = lat[0] + p[:, 1] * (lat[1] - lat[0])
            X = np.round(lo * 100).astype(int); Y = np.round(la * 100).astype(int)
            kod = [int(X[0]), int(Y[0])]
            for m in range(1, len(X)):
                kod += [int(X[m] - X[m - 1]), int(Y[m] - Y[m - 1])]
            yollar_.append(kod)
        out.append(dict(c=yollar_, tur=t["tur"], Qs=t["cokel_mt_yil"], hedef=t["hedef"], q=t["debi_m3s"],
                        r=int(r_km), agiz=t["enlem_boylam"]))
    return out


def uygulamaya_yaz():
    d = pickle.load(open(os.path.join(BURASI, "_disa.pkl"), "rb"))
    tut = json.load(open(os.path.join(BURASI, "deltalar.json"), encoding="utf-8"))["deltalar"]
    cat = catallar(tut, d["alici"], d["q"], d["deniz"], d["gm"], d["lat"], d["lon"])
    yol = os.path.join(KOK, "data", "su.json")
    S = json.load(open(yol, encoding="utf-8")); S["deltalar"] = cat
    json.dump(S, open(yol, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("su.json: %d delta çatalı, %.0f KB" % (len(cat), os.path.getsize(yol) / 1024))


if __name__ == "__main__":
    main()
    uygulamaya_yaz()
