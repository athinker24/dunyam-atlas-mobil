"""Göller ve nehirler: tek giriş noktası.

    python buzul/iklim_kos.py --res 0.25 --cikti buzul/_iklim_bugun025.npz   # ~16 dk
    python su/akim.py buzul/_iklim_bugun025.npz
    python su/uret_su.py

Karar (27 Eylül): eşik aşınması 200 m, fırça ölçeği yumuşatılmış arazi
(duzelt.py), 300 km²'den küçük doğal göl yok sayılır (buzul gölleri 100 km²).
Çıktı: su/su.json (göl ve nehir listesi), su/goller.geojson, su/nehirler.geojson,
su/su_haritasi.png.
"""
import json, os, sys
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw
BURASI = os.path.dirname(os.path.abspath(__file__)); KOK = os.path.dirname(BURASI)
sys.path.insert(0, BURASI); sys.path.insert(0, os.path.join(KOK, "buzul"))
import gol, nehir, duzelt
from ciz import golge, font

ASINMA = 200.0
EN_KUCUK_GOL, EN_KUCUK_BUZUL_GOLU = 300.0, 100.0
NEHIR_Q = 50.0          # m3/s: veri olarak nehir sayılan en küçük debi
CIZIM_Q = 100.0         # kıta haritasında çizilen en küçük debi
CIZIM_BOY = 120.0       # km; bundan kısa ve CIZIM_Q*10'dan küçük dere çizilmez (yamaç derecikleri)


def hazirla():
    k = np.load(os.path.join(BURASI, "_akim.npz"))
    z, lat, lon = k["z"].astype(np.float64), k["lat"], k["lon"]
    zr = duzelt.yumusat(z)
    zr, kim = duzelt.buzul_golleri(zr, lat, lon)
    dy = 6371e3 * np.radians(abs(lat[1] - lat[0]))
    dx = (6371e3 * np.radians(lon[1] - lon[0]) * np.cos(np.radians(lat)))[:, None]
    return k, z, zr, kim, lat, lon, dx * dy * np.ones_like(z)


def coz(k, z, zr, kim, alan):
    deniz = z < 0
    seviye, goller, A = gol.coz(zr, deniz, k["R"], k["P"], k["Egol"], alan, ASINMA)
    kimf = kim.ravel()
    tut = []
    for g in goller:
        buz = int(np.bincount(kimf[g["hucreler"]]).argmax()) if (kimf[g["hucreler"]] > 0).any() else 0
        g["buzul_golu"] = buz
        if g["alan_km2"] >= (EN_KUCUK_BUZUL_GOLU if buz else EN_KUCUK_GOL):
            tut.append(g)
    sev = np.full(z.size, np.nan); kapali = np.zeros(z.size, bool)
    for g in tut:
        sev[g["hucreler"]] = g["seviye"]
        if not g["cikisli"]:
            kapali[g["hucreler"]] = True
    sev = sev.reshape(z.shape); kapali = kapali.reshape(z.shape)
    alici, sira = nehir.yonlendir(zr, deniz, sev, kapali)
    gm = np.isfinite(sev)
    kaynak = np.where(gm, k["P"] - k["Egol"], k["R"]) * alan / 1000
    kaynak[deniz] = 0
    q = nehir.debi(alici, sira, kaynak).reshape(z.shape) / nehir.SANIYE_YIL
    yuz = np.where(gm, sev, zr)
    for _ in range(3):
        alici = nehir.yana_katil(alici, q, yuz, z.shape)
        sira = nehir.sira_kur(alici)
        q = nehir.debi(alici, sira, kaynak).reshape(z.shape) / nehir.SANIYE_YIL
    # kaynağa en uzak yol boyu (km): kısa yamaç derelerini ayıklamak için
    ny, nx = z.shape
    dyk = 6371 * np.radians(abs(k["lat"][1] - k["lat"][0]))
    dxk = 6371 * np.radians(k["lon"][1] - k["lon"][0]) * np.cos(np.radians(k["lat"]))
    boy = np.zeros(ny * nx)
    for c in sira[::-1]:
        r = alici[c]
        if r >= 0:
            i1, j1 = divmod(int(c), nx); i2, j2 = divmod(int(r), nx)
            d = np.hypot((i2 - i1) * dyk, (j2 - j1) * dxk[i1])
            if boy[c] + d > boy[r]:
                boy[r] = boy[c] + d
    return tut, sev, kapali, alici, q, boy.reshape(ny, nx)


def yollar(alici, q, gm, deniz, lat, lon):
    """Nehir hücrelerinden parçalı çizgiler (kaynaktan birleşmeye)."""
    ny, nx = q.shape
    qf = q.ravel(); nehir_m = (qf >= NEHIR_Q) & ~gm.ravel() & ~deniz.ravel()
    ust = np.zeros(ny * nx, bool)
    idx = np.where(nehir_m)[0]
    al = alici[idx]
    ust[al[(al >= 0)]] = True
    kaynaklar = idx[~ust[idx]]
    kaynaklar = kaynaklar[np.argsort(-qf[kaynaklar])]
    goruldu = np.zeros(ny * nx, bool); parca = []
    for s in kaynaklar:
        yol = [s]; c = s
        goruldu[s] = True
        while True:
            r = alici[c]
            if r < 0:
                break
            yol.append(r)
            if goruldu[r] or not nehir_m[r]:
                break
            goruldu[r] = True; c = r
        parca.append(yol)
    return parca


def sadelestir(p, tol):
    """Ramer-Douglas-Peucker: D8'in basamaklarını siler, uçlar sabit."""
    if len(p) < 3:
        return p
    a, b = p[0], p[-1]; d = b - a; L = np.hypot(*d)
    if L == 0:
        u = np.hypot(*(p - a).T)
    else:
        u = np.abs(d[0] * (p[:, 1] - a[1]) - d[1] * (p[:, 0] - a[0])) / L
    i = int(np.argmax(u))
    if u[i] <= tol:
        return np.array([a, b])
    return np.vstack([sadelestir(p[:i + 1], tol)[:-1], sadelestir(p[i:], tol)])


def kivrim(nokta, tohum, hucre):
    """Basamaksız çizgiye çok ölçekli kıvrım: orta nokta kaydırma (her
    düzeyde parça boyunun ~%18'i kadar, yana), sonra Chaikin. Uçlar sabit;
    birleşme noktaları kaymaz, kollar ana nehre bağlı kalır."""
    rng = np.random.default_rng(tohum)
    p = sadelestir(np.asarray(nokta, float), 0.8 * hucre)
    for duzey in range(4):
        yeni = [p[0]]
        for a, b in zip(p[:-1], p[1:]):
            d = b - a; L = np.hypot(*d)
            if L < 0.6 * hucre:
                yeni.append(b); continue
            n = np.array([-d[1], d[0]]) / L
            yeni += [(a + b) / 2 + n * L * rng.normal(0, 0.18), b]
        p = np.array(yeni)
    for _ in range(3):
        if len(p) < 3:
            break
        q1 = 0.75 * p[:-1] + 0.25 * p[1:]; q2 = 0.25 * p[:-1] + 0.75 * p[1:]
        p = np.vstack([p[:1], np.column_stack([q1, q2]).reshape(-1, 2), p[-1:]])
    return p


def en_yakin(la, lo, yerler):
    d = min(yerler, key=lambda m: np.hypot(la - m["enlem_boylam"][0], (lo - m["enlem_boylam"][1]) * np.cos(np.radians(la))))
    return d["no"], d["ad"]


def ozet_yaz(k, z, goller, sev, kapali, alici, q, boy, lat, lon, alan):
    ny, nx = z.shape
    yer = json.load(open(os.path.join(KOK, "tektonik", "ozet.json"), encoding="utf-8"))["dag_ve_yer_sekilleri"]
    ll = lambda c: (round(float(lat[c // nx]), 2), round(float(lon[c % nx]), 2))
    # havza alanı: debi gibi biriktir
    sira = nehir.sira_kur(alici)
    havza = nehir.debi(alici, sira, np.where(z < 0, 0, alan) / 1e6)
    qf, bf = q.ravel(), boy.ravel(); zf = z.ravel(); kf = kapali.ravel(); gf = np.isfinite(sev).ravel()
    # ağız: alıcısı deniz ya da kapalı göl olan kara hücresi
    agiz = [c for c in np.where((qf >= NEHIR_Q) & ~gf)[0] if alici[c] >= 0 and (zf[alici[c]] < 0 or kf[alici[c]])]
    # ters komşuluk: ana kolu kaynağa doğru izlemek için
    g = alici >= 0; o = np.argsort(alici[g], kind="stable"); coc = np.where(g)[0][o]; ust = alici[coc]
    bas = np.searchsorted(ust, np.arange(alici.size)); son = np.searchsorted(ust, np.arange(alici.size), side="right")
    nehirler = []
    for c in sorted(agiz, key=lambda c: -qf[c])[:30]:
        x = c; yol = [c]
        while son[x] > bas[x]:
            cc = coc[bas[x]:son[x]]; x = int(cc[np.argmax(bf[cc])]); yol.append(x)
        kaynak = yol[-1]; no, ad = en_yakin(*ll(kaynak), yer)
        hedef = "deniz" if zf[alici[c]] < 0 else "kapalı göl"
        nehirler.append(dict(debi_m3s=int(qf[c]), boy_km=int(bf[c]), havza_km2=int(havza[c]),
                             agiz=ll(c), kaynak=ll(kaynak), kaynak_yakini=f"{no} ({ad})", doker=hedef))
    # kıta yarığı (CRB) sınır noktaları: yakınındaki göl tektonik (Baykal türü)
    sin = json.load(open(os.path.join(KOK, "tektonik", "sinirlar.geojson"), encoding="utf-8"))["features"]
    yarik = np.array([pt for f in sin if f["properties"]["sinif"] == "CRB" for pt in f["geometry"]["coordinates"]])
    def yarikta(la, lo):
        if not len(yarik):
            return False
        d = np.hypot(la - yarik[:, 1], (lo - yarik[:, 0]) * np.cos(np.radians(la))) * 111.2
        return d.min() < 150
    gl = []
    for x in sorted(goller, key=lambda g: -g["alan_km2"]):
        c = x["hucreler"]; la, lo = float(lat[c // nx].mean()), float(lon[c % nx].mean())
        no, ad = en_yakin(la, lo, yer)
        tur = "buzul (moren seti)" if x["buzul_golu"] else ("yarık (tektonik)" if yarikta(la, lo) else "havza")
        gl.append(dict(enlem_boylam=[round(la, 2), round(lo, 2)], yakin=f"{no} ({ad})", koken=tur,
                       alan_km2=int(x["alan_km2"]), derin_m=int(x["derin_m"]), hacim_km3=round(x["hacim_km3"], 1),
                       seviye_m=int(x["seviye"]), cikis="var (tatlı)" if x["cikisli"] else "yok (kapalı, tuzlu)",
                       giren_km3_yil=round(x["giren_km3_yil"], 2)))
    kara = z >= 0
    w = alan * kara
    ort = lambda a: round(float((a * w).sum() / w.sum()))
    oz = dict(
        ne="Dünyam gölleri ve nehirleri; iklim motorunun bugünkü 0.25° iklimi ve su dengesinden.",
        karar=dict(esik_asinmasi_m=ASINMA, en_kucuk_gol_km2=EN_KUCUK_GOL, en_kucuk_buzul_golu_km2=EN_KUCUK_BUZUL_GOLU,
                   nehir_esigi_m3s=NEHIR_Q, arazi="fırça ölçeği yumuşatılmış (su/duzelt.py)"),
        kara_su_butcesi_mm=dict(yagis=ort(k["P"]), buharlasma=ort(k["AET"]), akis=ort(k["R"])),
        gol_payi_kara_yuzde=round(100 * sum(g["alan_km2"] for g in goller) * 1e6 / w.sum(), 2),
        gol_sayisi=len(gl), goller=gl, en_buyuk_30_nehir=nehirler)
    json.dump(oz, open(os.path.join(BURASI, "su.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("su bütçesi", oz["kara_su_butcesi_mm"])
    for n in nehirler[:12]:
        print("  ", n)
    from collections import Counter
    print("göl kökeni", Counter(x["koken"] for x in gl), "kapalı", sum(x["cikis"].startswith("yok") for x in gl))


def main():
    k, z, zr, kim, lat, lon, alan = hazirla()
    goller, sev, kapali, alici, q, boy = coz(k, z, zr, kim, alan)
    deniz = z < 0; gm = np.isfinite(sev); ny, nx = z.shape
    parca = yollar(alici, q, gm, deniz, lat, lon)
    wk = alan[~deniz].sum() / 1e6
    print("göller: %d, karanın %%%.2f; nehir parçası %d" % (len(goller), 100 * sum(g["alan_km2"] for g in goller) / wk, len(parca)))
    np.savez_compressed(os.path.join(BURASI, "_su.npz"), sev=sev, kapali=kapali, q=q.astype(np.float32), alici=alici)
    ozet_yaz(k, z, goller, sev, kapali, alici, q, boy, lat, lon, alan)

    # --- harita
    r, c = np.where(~deniz); r0, r1, c0, c1 = r.min() - 6, r.max() + 6, c.min() - 6, c.max() + 6
    S = 3
    dy = 6371e3 * np.radians(abs(lat[1] - lat[0])); dx = (6371e3 * np.radians(lon[1] - lon[0]) * np.cos(np.radians(lat)))[:, None]
    h = golge(z, dx, dy)
    t = np.clip(z / 5000, 0, 1)[..., None]
    img = (np.array([118, 122, 98]) * (1 - t) + np.array([168, 152, 128]) * t) / 255 * (0.5 + 0.6 * h[..., None])
    img = np.where(deniz[..., None], np.array([20, 32, 46]) / 255, img)[r0:r1, c0:c1]
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize(((c1 - c0) * S, (r1 - r0) * S), Image.BICUBIC)
    arr = np.asarray(im).astype(np.float64) / 255
    # göl kıyıları: maske büyütülüp yumuşatılır
    for maske, renk in ((gm & ~kapali, (58, 128, 205)), (kapali, (86, 170, 160))):
        m = ndimage.zoom(maske[r0:r1, c0:c1].astype(float), S, order=1)
        m = ndimage.gaussian_filter(m, S * 0.35) > 0.33   # dar buzul gölleri (1 hücre) kaybolmasın
        arr[m] = np.array(renk) / 255
    im = Image.fromarray((arr * 255).astype(np.uint8)); dr = ImageDraw.Draw(im)
    qf, bf = q.ravel(), boy.ravel()
    cizilir = lambda c: qf[c] >= CIZIM_Q and (bf[c] >= CIZIM_BOY or qf[c] >= 10 * CIZIM_Q)
    for yol in parca:
        # parçanın çizilen kısmı: ilk çizilir hücreden sona
        bas = next((s_ for s_, c_ in enumerate(yol[:-1]) if cizilir(c_)), None)
        if bas is None:
            continue
        yol = yol[bas:]
        pts = [((p % nx - c0 + 0.5) * S, (p // nx - r0 + 0.5) * S) for p in yol]
        yumus = kivrim(pts, int(yol[0]), S)
        qs = qf[yol[:-1]]
        n = len(yumus)
        for s_ in range(n - 1):
            qq = qs[min(int(s_ / max(n - 1, 1) * len(qs)), len(qs) - 1)]
            w = int(np.clip(1 + 2.4 * np.log10(max(qq, CIZIM_Q) / CIZIM_Q), 1, 8))
            dr.line([tuple(yumus[s_]), tuple(yumus[s_ + 1])], fill=(110, 180, 245), width=w)
    im.save(os.path.join(BURASI, "su_haritasi.png")); print(im.size)


if __name__ == "__main__":
    main()
